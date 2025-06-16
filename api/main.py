from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager

from models import User, UserCreate, UserUpdate, Item, ItemCreate, ItemUpdate
from database import get_db, init_db, check_db_connection
from crud import user_crud, item_crud
from auth import require_api_key
from config import settings

# Import des nouveaux routers
from routes_postgres import postgres_router
from routes_mongo import mongo_router
from mongo_crud import mongodb_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Démarrage de l'application DataBook API...")
    
    # Initialisation PostgreSQL
    print("📊 Initialisation de PostgreSQL...")
    init_db()
    check_db_connection()
    
    # Initialisation MongoDB
    print("🍃 Initialisation de MongoDB...")
    try:
        await mongodb_service.connect_async()
    except Exception as e:
        print(f"⚠️ Avertissement: MongoDB non disponible - {e}")
    
    print("✅ Application prête!")
    yield
    
    # Shutdown
    print("🛑 Arrêt de l'application...")
    mongodb_service.disconnect()

# Initialisation de l'application FastAPI
app = FastAPI(
    title="DATA BOOK API",
    description="""
    API pour l'analyse et la gestion des données de livres
    
    ## Fonctionnalités
    
    * **PostgreSQL** : Base de données relationnelle pour les données structurées
    * **MongoDB** : Base de données NoSQL pour l'analyse et les données flexibles
    * **Authentification** : Clé API pour protéger les endpoints sensibles
    * **Recherche avancée** : Recherche textuelle et par filtres
    * **Statistiques** : Analytics et métriques en temps réel
    
    ## Bases de données
    
    * **PostgreSQL** : `/postgres/*` - Données relationnelles
    * **MongoDB** : `/mongo/*` - Données d'analyse et NoSQL
    
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(postgres_router)
app.include_router(mongo_router)

# Route de base (publique)
@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API DataBook v2.0",
        "description": "API pour l'analyse des données de livres avec PostgreSQL et MongoDB",
        "version": "2.0.0",
        "timestamp": datetime.now(),
        "docs": "/docs",
        "databases": {
            "postgresql": "/postgres/*",
            "mongodb": "/mongo/*"
        },
        "features": [
            "Gestion des livres multi-bases",
            "Recherche avancée",
            "Analytics temps réel",
            "API sécurisée"
        ]
    }

# Route de santé (publique)
@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API et des bases de données"""
    status = {
        "api": "OK",
        "timestamp": datetime.now(),
        "databases": {}
    }
    
    # Test PostgreSQL
    try:
        check_db_connection()
        status["databases"]["postgresql"] = "connected"
    except Exception as e:
        status["databases"]["postgresql"] = f"error: {str(e)}"
    
    # Test MongoDB
    try:
        if mongodb_service.async_client:
            await mongodb_service.database.list_collection_names()
            status["databases"]["mongodb"] = "connected"
        else:
            status["databases"]["mongodb"] = "not initialized"
    except Exception as e:
        status["databases"]["mongodb"] = f"error: {str(e)}"
    
    return status

# Routes legacy (maintien de la compatibilité)
@app.post("/users/", response_model=User, tags=["Legacy"])
async def create_user(user: UserCreate, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Créer un nouvel utilisateur (legacy - utilisez /postgres/users/)"""
    return user_crud.create_user(db, user)

@app.get("/users/", response_model=List[User], tags=["Legacy"])
async def get_users(skip: int = 0, limit: int = 100, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Récupérer la liste des utilisateurs (legacy - utilisez /postgres/users/)"""
    return user_crud.get_users(db, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=User, tags=["Legacy"])
async def get_user(user_id: int, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Récupérer un utilisateur par son ID (legacy - utilisez /postgres/users/{user_id})"""
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

# Routes legacy pour les livres (redirigent vers PostgreSQL)
@app.get("/books/", response_model=List[Item], tags=["Legacy"])
async def get_books(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    """Récupérer la liste des livres (legacy - utilisez /postgres/books/)"""
    return item_crud.get_items(db, skip=skip, limit=limit)

@app.get("/books/{book_id}", response_model=Item, tags=["Legacy"])
async def get_book(book_id: int, db=Depends(get_db)):
    """Récupérer un livre par son ID (legacy - utilisez /postgres/books/{book_id})"""
    book = item_crud.get_item(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return book

@app.post("/books/", response_model=Item, tags=["Legacy"])
async def create_book(book: ItemCreate, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Créer un nouveau livre (legacy - utilisez /postgres/books/)"""
    return item_crud.create_item(db, book)

@app.put("/books/{book_id}", response_model=Item, tags=["Legacy"])
async def update_book(book_id: int, book_update: ItemUpdate, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Mettre à jour un livre (legacy - utilisez /postgres/books/{book_id})"""
    book = item_crud.update_item(db, book_id, book_update)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return book

@app.delete("/books/{book_id}", tags=["Legacy"])
async def delete_book(book_id: int, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Supprimer un livre (legacy - utilisez /postgres/books/{book_id})"""
    success = item_crud.delete_item(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return {"message": "Livre supprimé avec succès"}

# Route de recherche globale
@app.get("/search/", tags=["Search"])
async def search_books(
    query: str,
    category: Optional[str] = None,
    database: str = "postgres",  # postgres ou mongo
    db=Depends(get_db)
):
    """Rechercher des livres dans PostgreSQL ou MongoDB"""
    if database == "postgres":
        return item_crud.search_items(db, query, category)
    elif database == "mongo":
        return await mongodb_service.search_books(query, category)
    else:
        raise HTTPException(status_code=400, detail="Base de données non supportée. Utilisez 'postgres' ou 'mongo'")

# Routes de statistiques globales
@app.get("/stats/", tags=["Statistics"])
async def get_global_statistics(db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Récupérer les statistiques globales des deux bases de données"""
    postgres_stats = {
        "total_users": user_crud.count_users(db),
        "total_books": item_crud.count_items(db),
    }
    
    try:
        mongo_stats = await mongodb_service.get_statistics()
    except Exception:
        mongo_stats = {"error": "MongoDB non disponible"}
    
    return {
        "postgres": postgres_stats,
        "mongodb": mongo_stats,
        "timestamp": datetime.now()
    }

# Route pour tester la connexion aux bases de données
@app.get("/db-status/", tags=["System"])
async def database_status(db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Vérifier le statut des bases de données"""
    status = {"timestamp": datetime.now()}
    
    # Test PostgreSQL
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        status["postgresql"] = "connected"
    except Exception as e:
        status["postgresql"] = f"error: {str(e)}"
    
    # Test MongoDB
    try:
        await mongodb_service.database.list_collection_names()
        status["mongodb"] = "connected"
    except Exception as e:
        status["mongodb"] = f"error: {str(e)}"
    
    return status

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 