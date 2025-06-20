import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional

from database.database import init_db, check_db_connection
from config.config import settings

# Import des routers essentiels (PostgreSQL + MongoDB + Auth)
from routes.routes_postgres import postgres_router       # 🗄️ PostgreSQL (demandé par l'utilisateur)
from routes.routes_mongo_livres import mongo_livres_router  # 📚 Vos vraies données MongoDB
from routes.routes_mongo_extras import mongo_extras_router  # 🎯 Analytics avancés
from routes.auth_routes import auth_router               # 🔐 Authentification JWT

# MongoDB
try:
    from database.mongo_crud import mongodb_service
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    mongodb_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Démarrage de l'API DataBook (Version nettoyée avec PostgreSQL)...")
    
    # Initialisation PostgreSQL (gardé sur demande)
    print("🗄️ Initialisation de PostgreSQL...")
    init_db()
    check_db_connection()
    
    # Initialisation MongoDB (essentiel)
    if MONGODB_AVAILABLE and mongodb_service:
        print("🍃 Initialisation de MongoDB...")
        try:
            await mongodb_service.connect_async()
            print(f"✅ MongoDB connecté - Base: {settings.mongodb_database}")
        except Exception as e:
            print(f"⚠️ Avertissement: MongoDB non disponible - {e}")
    else:
        print("⚠️ MongoDB non configuré")
    
    print("✅ API DataBook prête!")
    yield
    
    # Shutdown
    print("🛑 Arrêt de l'application...")
    if MONGODB_AVAILABLE and mongodb_service:
        mongodb_service.disconnect()

# Application FastAPI optimisée
app = FastAPI(
    title="📚 DataBook API - Version Optimisée",
    description="""
    ## API DataBook - PostgreSQL + MongoDB + JWT
    
    **Interface optimisée** pour vos données réelles :
    
    ### 🎯 Fonctionnalités essentielles
    * **PostgreSQL** : Base relationnelle via `/postgres/*`
    * **4766 livres MongoDB** disponibles via `/mongo-livres/*`
    * **Analytics avancés** via `/mongo-extras/*` 
    * **Authentification JWT moderne** via `/auth/*`
    * **Interface Streamlit** compatible
    
    ### 🔐 Authentification
    * Inscription : `POST /auth/register`
    * Connexion : `POST /auth/login` 
    * Profil : `GET /auth/me` (avec Bearer token)
    
    ### 🗄️ PostgreSQL
    * **Users** : Gestion des utilisateurs
    * **Books** : Livres en base relationnelle
    * **CRUD complet** avec authentification JWT
    
    ### 📚 MongoDB (vos vraies données)
    * **Livres** : 4766 documents avec titre, auteurs, genres, notes
    * **Critiques** : 85 critiques Babelio avec notes et analyses
    * **Recherche avancée** et filtres multiples
    
    """,
    version="3.0.0",
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

# Inclusion des routers essentiels
app.include_router(postgres_router)     # 🗄️ PostgreSQL (gardé sur demande)
app.include_router(mongo_livres_router) # 📚 Vos livres MongoDB (essentiel)
app.include_router(mongo_extras_router) # 🎯 Analytics (essentiel)
app.include_router(auth_router)         # 🔐 JWT Auth (essentiel)

# Routes de base optimisées
@app.get("/")
async def root():
    """Page d'accueil de l'API DataBook optimisée"""
    return {
        "message": "📚 DataBook API - Version Optimisée v3.0",
        "description": "API PostgreSQL + MongoDB + JWT",
        "version": "3.0.0",
        "timestamp": datetime.now(),
        "docs": "/docs",
        "essential_endpoints": {
            "postgresql": {
                "url": "/postgres/*",
                "description": "Base de données relationnelle avec users et books",
                "examples": [
                    "GET /postgres/users - Liste des utilisateurs",
                    "POST /postgres/users - Créer un utilisateur", 
                    "GET /postgres/books - Liste des livres PostgreSQL",
                    "POST /postgres/books - Créer un livre"
                ]
            },
            "livres_mongodb": {
                "url": "/mongo-livres/*",
                "description": "4766 livres avec recherche, filtres et détails",
                "examples": [
                    "GET /mongo-livres/ - Vue d'ensemble",
                    "GET /mongo-livres/livres?limit=10 - Liste des livres", 
                    "GET /mongo-livres/livres/search?q=roman - Recherche",
                    "GET /mongo-livres/statistiques - Stats complètes"
                ]
            },
            "analytics": {
                "url": "/mongo-extras/*", 
                "description": "Analytics avancés et exploration de données",
                "examples": [
                    "GET /mongo-extras/genres - Top genres",
                    "GET /mongo-extras/auteurs - Top auteurs",
                    "GET /mongo-extras/analytics - Données complètes"
                ]
            },
            "authentication": {
                "url": "/auth/*",
                "description": "Authentification JWT moderne",
                "examples": [
                    "POST /auth/register - Inscription",
                    "POST /auth/login - Connexion",
                    "GET /auth/me - Profil utilisateur"
                ]
            }
        },
        "data_summary": {
            "postgresql": "Users + Books relationnels",
            "livres_mongodb": "4766 livres",
            "critiques_babelio": "85 critiques",
            "interface": "Streamlit compatible",
            "auth": "JWT sécurisé"
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de santé complète"""
    status = {
        "api": "OK",
        "version": "3.0.0",
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
                collections = await mongodb_service.database.list_collection_names()
                livres_count = await mongodb_service.database.livres.count_documents({})
                critiques_count = await mongodb_service.database.critiques_livres.count_documents({})
                
                status["databases"]["mongodb"] = {
                    "status": "connected",
                    "collections": len(collections),
                    "livres": livres_count,
                    "critiques": critiques_count
                }
            else:
                status["databases"]["mongodb"] = "not initialized"
        except Exception as e:
            status["databases"]["mongodb"] = f"error: {str(e)}"
    else:
        status["databases"]["mongodb"] = "not configured"
    
    return status

@app.get("/summary")
async def data_summary():
    """Résumé rapide de vos données"""
    try:
        summary_data = {
            "success": True,
            "data": {
                "endpoints_disponibles": 4,
                "version_api": "3.0.0 (optimisée)",
                "postgresql": "Disponible",
                "mongodb": "Non connecté"
            },
            "quick_access": {
                "postgres_users": "/postgres/users",
                "postgres_books": "/postgres/books",
                "explorer_livres": "/mongo-livres/livres?limit=20",
                "top_genres": "/mongo-extras/genres", 
                "authentification": "/auth/register"
            }
        }
        
        # Enrichir avec les données MongoDB si disponible
        if MONGODB_AVAILABLE and mongodb_service:
            livres_count = await mongodb_service.database.livres.count_documents({})
            critiques_count = await mongodb_service.database.critiques_livres.count_documents({})
            
            summary_data["data"].update({
                "livres_mongodb": livres_count,
                "critiques_babelio": critiques_count,
                "mongodb": "Connecté"
            })
        
        return summary_data
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "main_cleaned:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 