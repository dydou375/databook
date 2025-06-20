"""
API Simple pour DataBook
- Connexion PostgreSQL et MongoDB
- Sécurité par clé API
- Affichage des données
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import datetime
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Configuration
API_KEY = os.getenv("API_KEY", "databook-api-key-2024")
POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/databook")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DATABASE", "databook")

# Sécurité
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    """Vérifier la clé API"""
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Clé API invalide ou manquante. Utilisez l'en-tête X-API-Key"
        )
    return api_key

# Configuration PostgreSQL
try:
    postgres_engine = create_engine(POSTGRES_URL)
    PostgresSession = sessionmaker(bind=postgres_engine)
    POSTGRES_AVAILABLE = True
    print("✅ PostgreSQL configuré")
except Exception as e:
    print(f"❌ Erreur PostgreSQL: {e}")
    POSTGRES_AVAILABLE = False

# Configuration MongoDB
try:
    from pymongo import MongoClient
    mongo_client = MongoClient(MONGODB_URL)
    mongo_db = mongo_client[MONGODB_DB]
    MONGODB_AVAILABLE = True
    print("✅ MongoDB configuré")
except Exception as e:
    print(f"❌ Erreur MongoDB: {e}")
    MONGODB_AVAILABLE = False
    mongo_db = None

# Application FastAPI
app = FastAPI(
    title="DataBook API Simple",
    description="API simple pour accéder aux données PostgreSQL et MongoDB",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_postgres_db():
    """Obtenir une session PostgreSQL"""
    if not POSTGRES_AVAILABLE:
        raise HTTPException(status_code=503, detail="PostgreSQL non disponible")
    db = PostgresSession()
    try:
        yield db
    finally:
        db.close()

# === ROUTES PUBLIQUES ===

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "🚀 DataBook API Simple",
        "version": "1.0.0",
        "timestamp": datetime.now(),
        "databases": {
            "postgresql": "✅ Disponible" if POSTGRES_AVAILABLE else "❌ Indisponible",
            "mongodb": "✅ Disponible" if MONGODB_AVAILABLE else "❌ Indisponible"
        },
        "documentation": "/docs",
        "endpoints": {
            "postgres": "/postgres/",
            "mongodb": "/mongodb/",
            "auth_required": "Utilisez l'en-tête X-API-Key"
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état de l'API"""
    status = {
        "api": "OK",
        "timestamp": datetime.now(),
        "databases": {}
    }
    
    # Test PostgreSQL
    if POSTGRES_AVAILABLE:
        try:
            with postgres_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            status["databases"]["postgresql"] = "✅ Connecté"
        except Exception as e:
            status["databases"]["postgresql"] = f"❌ Erreur: {str(e)}"
    else:
        status["databases"]["postgresql"] = "❌ Non configuré"
    
    # Test MongoDB
    if MONGODB_AVAILABLE:
        try:
            mongo_db.list_collection_names()
            status["databases"]["mongodb"] = "✅ Connecté"
        except Exception as e:
            status["databases"]["mongodb"] = f"❌ Erreur: {str(e)}"
    else:
        status["databases"]["mongodb"] = "❌ Non configuré"
    
    return status

# === ROUTES POSTGRESQL (PROTÉGÉES) ===

@app.get("/postgres/")
async def postgres_info(api_key: str = Depends(verify_api_key), db: Session = Depends(get_postgres_db)):
    """Informations sur la base PostgreSQL"""
    try:
        # Récupérer la liste des tables
        result = db.execute(text("""
            SELECT table_name, table_schema 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [{"nom": row[0], "schema": row[1]} for row in result]
        
        return {
            "database": "PostgreSQL",
            "timestamp": datetime.now(),
            "tables": tables,
            "nombre_tables": len(tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur PostgreSQL: {str(e)}")

@app.get("/postgres/tables/{table_name}")
async def postgres_table_data(
    table_name: str,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_postgres_db)
):
    """Récupérer les données d'une table PostgreSQL"""
    try:
        # Vérifier que la table existe
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = :table_name
            )
        """), {"table_name": table_name})
        
        if not result.scalar():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' non trouvée")
        
        # Récupérer les données
        result = db.execute(text(f"""
            SELECT * FROM public.{table_name} 
            ORDER BY 1 
            LIMIT :limit OFFSET :offset
        """), {"limit": limit, "offset": offset})
        
        # Convertir en dictionnaire
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result]
        
        # Compter le total
        count_result = db.execute(text(f"SELECT COUNT(*) FROM public.{table_name}"))
        total = count_result.scalar()
        
        return {
            "table": table_name,
            "data": data,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "count": len(data)
            },
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

@app.get("/postgres/livres")
async def postgres_livres(
    limit: int = Query(50, le=500),
    search: Optional[str] = Query(None),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_postgres_db)
):
    """Récupérer les livres depuis PostgreSQL"""
    try:
        # Construire la requête de base
        base_query = """
            SELECT l.*, a.nom as auteur_nom, a.prenom as auteur_prenom, a.nom_complet as auteur_complet
            FROM livre l
            LEFT JOIN livre_auteur la ON l.id_livre = la.id_livre  
            LEFT JOIN auteur a ON la.id_auteur = a.id_auteur
        """
        
        params = {"limit": limit}
        
        if search:
            base_query += " WHERE l.titre ILIKE :search OR l.description ILIKE :search"
            params["search"] = f"%{search}%"
        
        base_query += " ORDER BY l.id_livre LIMIT :limit"
        
        result = db.execute(text(base_query), params)
        columns = result.keys()
        livres = [dict(zip(columns, row)) for row in result]
        
        return {
            "source": "PostgreSQL",
            "livres": livres,
            "count": len(livres),
            "search": search,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur livres PostgreSQL: {str(e)}")

# === ROUTES MONGODB (PROTÉGÉES) ===

@app.get("/mongodb/")
async def mongodb_info(api_key: str = Depends(verify_api_key)):
    """Informations sur la base MongoDB"""
    if not MONGODB_AVAILABLE:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")
    
    try:
        collections = mongo_db.list_collection_names()
        stats = {}
        
        for collection_name in collections:
            count = mongo_db[collection_name].count_documents({})
            stats[collection_name] = count
        
        return {
            "database": "MongoDB",
            "timestamp": datetime.now(),
            "collections": collections,
            "statistics": stats,
            "nombre_collections": len(collections)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur MongoDB: {str(e)}")

@app.get("/mongodb/collections/{collection_name}")
async def mongodb_collection_data(
    collection_name: str,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    api_key: str = Depends(verify_api_key)
):
    """Récupérer les données d'une collection MongoDB"""
    if not MONGODB_AVAILABLE:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")
    
    try:
        collection = mongo_db[collection_name]
        
        # Récupérer les données
        cursor = collection.find({}).skip(skip).limit(limit)
        data = []
        
        for doc in cursor:
            # Convertir ObjectId en string
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            data.append(doc)
        
        # Compter le total
        total = collection.count_documents({})
        
        return {
            "collection": collection_name,
            "data": data,
            "pagination": {
                "total": total,
                "limit": limit,
                "skip": skip,
                "count": len(data)
            },
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur MongoDB: {str(e)}")

@app.get("/mongodb/livres")
async def mongodb_livres(
    limit: int = Query(50, le=500),
    search: Optional[str] = Query(None),
    api_key: str = Depends(verify_api_key)
):
    """Récupérer les livres depuis MongoDB"""
    if not MONGODB_AVAILABLE:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")
    
    try:
        collection = mongo_db.books  # ou le nom de votre collection
        
        # Construire le filtre de recherche
        filter_query = {}
        if search:
            filter_query = {
                "$or": [
                    {"title": {"$regex": search, "$options": "i"}},
                    {"author": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}}
                ]
            }
        
        cursor = collection.find(filter_query).limit(limit)
        livres = []
        
        for doc in cursor:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            livres.append(doc)
        
        return {
            "source": "MongoDB",
            "livres": livres,
            "count": len(livres),
            "search": search,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur livres MongoDB: {str(e)}")

if __name__ == "__main__":
    print(f"""
🚀 Démarrage de l'API DataBook Simple
📊 PostgreSQL: {'✅' if POSTGRES_AVAILABLE else '❌'}
🍃 MongoDB: {'✅' if MONGODB_AVAILABLE else '❌'}
🔐 Clé API: {API_KEY}
📖 Documentation: http://localhost:8000/docs
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 