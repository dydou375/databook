from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager

from models.models import User, UserCreate, UserUpdate, Item, ItemCreate, ItemUpdate
from database.database import get_db, init_db, check_db_connection
from database.crud import user_crud, item_crud
from auth.auth import require_jwt, optional_jwt
from config.config import settings

# 🚀 Import des routers optimisés
from routes.routes_postgres_livres import postgres_livres_router  # PostgreSQL - Livres réels
from routes.routes_postgres_extras import postgres_extras_router  # PostgreSQL - Analytics
from routes.routes_mongo_livres import mongo_livres_router  # MongoDB - Livres & Critiques
from routes.routes_mongo_extras import mongo_extras_router  # MongoDB - Analytics
from routes.auth_routes import auth_router  # Authentification JWT

# ❌ Imports supprimés pour simplification :
# - routes_postgres (legacy)
# - routes_mongo (redondant)
# - routes_real_data (fusionné)
# - routes_real_mongo (fusionné)
# - routes_livres (optionnel)

try:
    from database.mongo_crud import mongodb_service
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    mongodb_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Démarrage de l'application DataBook API...")
    
    # Initialisation PostgreSQL
    print("📊 Initialisation de PostgreSQL...")
    init_db()
    check_db_connection()
    
    # Initialisation MongoDB
    if MONGODB_AVAILABLE and mongodb_service:
        print("🍃 Initialisation de MongoDB...")
        try:
            await mongodb_service.connect_async()
        except Exception as e:
            print(f"⚠️ Avertissement: MongoDB non disponible - {e}")
    else:
        print("⚠️ MongoDB non configuré")
    
    print("✅ Application prête!")
    yield
    
    # Shutdown
    print("🛑 Arrêt de l'application...")
    if MONGODB_AVAILABLE and mongodb_service:
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

# 🚀 Inclusion des routers optimisés
app.include_router(auth_router)  # Authentification JWT
app.include_router(postgres_livres_router)  # PostgreSQL - Livres réels
app.include_router(postgres_extras_router)  # PostgreSQL - Analytics
app.include_router(mongo_livres_router)  # MongoDB - Livres & Critiques
app.include_router(mongo_extras_router)  # MongoDB - Analytics

# ❌ Routers supprimés pour simplification :
# - postgres_router (legacy users - remplacé par auth_router)
# - mongo_router (redondant avec mongo_livres_router) 
# - real_data_router (fusionné avec autres routers)
# - real_mongo_router (fusionné avec mongo_livres_router)
# - livres_router (optionnel - généralement pas utilisé)

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
            "postgresql_livres": "/postgres/livres/* (📚 livres schéma test)",
            "postgresql_analytics": "/postgres-extras/* (📊 analytics PostgreSQL)",
            "mongo_livres": "/mongo-livres/* (📚 4766 livres et 💬 85 critiques)",
            "mongo_extras": "/mongo-extras/* (🎯 analytics MongoDB avancés)"
        },
        "authentication": {
            "jwt": {
                "login": "/auth/login",
                "register": "/auth/register",
                "me": "/auth/me",
                "refresh": "/auth/refresh",
                "logout": "/auth/logout"
            },
            "info": "🔐 Authentification JWT sécurisée",
            "note": "❌ /auth/token supprimé - utilisez /auth/login"
        },
        "features": [
            "📚 4766 livres MongoDB + Base PostgreSQL",
            "🔍 Recherche avancée et filtres multiples", 
            "📊 Analytics temps réel (2 bases de données)",
            "📈 Graphiques interactifs Plotly",
            "🔐 Authentification JWT sécurisée",
            "🚀 API optimisée - 40 endpoints essentiels",
            "📱 Interface Streamlit moderne"
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
    if MONGODB_AVAILABLE and mongodb_service:
        try:
            if mongodb_service.async_client is not None:
                await mongodb_service.database.list_collection_names()
                status["databases"]["mongodb"] = "connected"
            else:
                status["databases"]["mongodb"] = "not initialized"
        except Exception as e:
            status["databases"]["mongodb"] = f"error: {str(e)}"
    else:
        status["databases"]["mongodb"] = "not configured"
    
    return status

# Route de résumé rapide (publique)
@app.get("/summary")
async def summary():
    """📊 Résumé rapide des données disponibles"""
    try:
        # Compter MongoDB si disponible
        mongo_data = {}
        if MONGODB_AVAILABLE and mongodb_service:
            try:
                mongo_data["livres_mongodb"] = await mongodb_service.database.livres.count_documents({})
                mongo_data["critiques_babelio"] = await mongodb_service.database.critiques_livres.count_documents({})
            except:
                mongo_data["livres_mongodb"] = "N/A"
                mongo_data["critiques_babelio"] = "N/A"
        
        return {
            "success": True,
            "data": {
                "version_api": "3.0.0",
                "livres_mongodb": mongo_data.get("livres_mongodb", "N/A"),
                "critiques_babelio": mongo_data.get("critiques_babelio", "N/A"),
                "endpoints_total": "~40 endpoints optimisés",
                "authentification": "JWT",
                "bases_donnees": ["PostgreSQL", "MongoDB"]
            },
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ❌ Routes legacy supprimées pour simplification
# Anciens endpoints /users/ remplacés par l'authentification JWT (/auth/*)
# Utilisez les nouveaux endpoints dans les routers spécialisés

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
        if MONGODB_AVAILABLE and mongodb_service:
            return await mongodb_service.search_books(query, category)
        else:
            raise HTTPException(status_code=503, detail="MongoDB non disponible")
    else:
        raise HTTPException(status_code=400, detail="Base de données non supportée. Utilisez 'postgres' ou 'mongo'")

# Routes de statistiques globales
@app.get("/stats/", tags=["Statistics"])
async def get_global_statistics(db=Depends(get_db), current_user = Depends(require_jwt)):
    """Récupérer les statistiques globales des deux bases de données"""
    
    # Stats PostgreSQL (tables legacy)
    try:
        postgres_stats = {
            "total_users": user_crud.count_users(db),
            "total_books": 0,  # Plus de table books générique
            "note": "Utilisez /postgres/livres/stats/general pour les vraies stats des livres"
        }
    except Exception as e:
        postgres_stats = {"error": f"Erreur PostgreSQL: {str(e)}"}
    
    # Stats MongoDB
    try:
        mongo_stats = await mongodb_service.get_statistics()
    except Exception:
        mongo_stats = {"error": "MongoDB non disponible"}
    
    return {
        "postgres": postgres_stats,
        "mongodb": mongo_stats,
        "timestamp": datetime.now(),
        "recommendation": "Utilisez /postgres/livres/stats/general pour les vraies statistiques des livres"
    }

# ❌ Route /db-status/ supprimée - utilisez /health (même fonctionnalité, public)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 