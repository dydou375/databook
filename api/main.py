from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager

# Suppression des imports legacy models (User, Item) - remplacés par l'authentification JWT
from database.database import get_db, init_db, check_db_connection
from auth.auth import require_jwt, optional_jwt
from config.config import settings

# 🚀 Import des routers optimisés (40 endpoints essentiels)
from routes.routes_postgres_livres import postgres_livres_router  # PostgreSQL - Livres réels
from routes.routes_postgres_extras import postgres_extras_router  # PostgreSQL - Analytics
from routes.routes_mongo_livres import mongo_livres_router  # MongoDB - Livres & Critiques
from routes.routes_mongo_extras import mongo_extras_router  # MongoDB - Analytics
from routes.auth_routes import auth_router  # Authentification JWT

# ❌ Imports supprimés pour optimisation (33 endpoints supprimés) :
# - models.models User/Item (legacy) - remplacés par auth JWT
# - database.crud user_crud/item_crud (legacy) - dans auth maintenant
# - routes legacy supprimées :
#   * routes_postgres (6 endpoints legacy users/items)  
#   * routes_mongo (redondant avec mongo_livres_router)
#   * routes_real_data (fusionné avec postgres_livres)
#   * routes_real_mongo (fusionné avec mongo_livres)
#   * routes_livres (optionnel, rarement utilisé)

try:
    from database.mongo_crud import mongodb_service
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    mongodb_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Démarrage de l'API DataBook optimisée...")
    
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
    
    print("✅ API optimisée prête! (40 endpoints essentiels)")
    yield
    
    # Shutdown
    print("🛑 Arrêt de l'application...")
    if MONGODB_AVAILABLE and mongodb_service:
        mongodb_service.disconnect()

# Initialisation de l'application FastAPI optimisée
app = FastAPI(
    title="DATA BOOK API - Optimisée",
    description="""
    ## 🚀 API DataBook Optimisée v3.0
    
    **42 endpoints essentiels** pour l'analyse et la gestion des données de livres
    
    ### ✅ Optimisations appliquées :
    * **-45% d'endpoints** (73+ → 40 endpoints)
    * Suppression routes legacy (users/items génériques)
    * Suppression endpoints debug/test  
    * Fusion routes redondantes
    * Authentification JWT unifiée
    
    ### 📊 Bases de données hybrides :
    * **PostgreSQL** : `/postgres/*` - 28 requêtes SQL optimisées
    * **MongoDB** : `/mongo/*` - 39 requêtes NoSQL optimisées
    * **4766 livres MongoDB + 85 critiques Babelio**
    
    ### 🔐 Authentification JWT :
    * Login/Register : `/auth/*`
    * Protection endpoints sensibles
    * Tokens sécurisés avec expiration
    
            ### 🎯 Endpoints disponibles :
        * **Auth** (7) : register, token(OAuth2), login(JSON), me, refresh, logout, delete-account
    * **PostgreSQL Livres** (8) : CRUD livres schéma test
    * **PostgreSQL Analytics** (12) : statistiques avancées
    * **MongoDB Livres** (10) : 4766 livres + critiques
    * **MongoDB Analytics** (5) : métriques NoSQL
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

# 🚀 Inclusion des routers optimisés (42 endpoints essentiels)
app.include_router(auth_router)  # 7 endpoints : register, token, login, me, refresh, logout, delete-account
app.include_router(postgres_livres_router)  # 8 endpoints : livres PostgreSQL + relations
app.include_router(postgres_extras_router)  # 12 endpoints : analytics PostgreSQL
app.include_router(mongo_livres_router)  # 10 endpoints : 4766 livres + critiques MongoDB
app.include_router(mongo_extras_router)  # 5 endpoints : analytics MongoDB

# ❌ ROUTERS SUPPRIMÉS POUR OPTIMISATION (-33 endpoints) :
# 
# Legacy supprimés (6 endpoints) :
# - postgres_router : /users/, /items/, /db-status/ (remplacés par auth + /health)
# 
# Redondants supprimés (15 endpoints) :
# - mongo_router : doublons avec mongo_livres_router
# - real_data_router : fusionné avec postgres_livres_router
# - real_mongo_router : fusionné avec mongo_livres_router
# 
# Debug/Test supprimés (6 endpoints) :
# - routes debug dans routes_postgres_livres.py
# - endpoints test dans routes_mongo_livres.py
# 
# Optionnels supprimés (6 endpoints) :
# - livres_router : rarement utilisé, redondant
# - pages d'accueil multiples

# Route de base optimisée (publique)
@app.get("/")
async def root():
    return {
        "message": "🚀 Bienvenue sur l'API DataBook v3.0 Optimisée",
        "description": "API optimisée pour l'analyse des données de livres",
        "version": "3.0.0",
        "optimization": {
            "endpoints_avant": "73+",
            "endpoints_apres": "42",
            "reduction": "-42%",
            "status": "✅ Optimisation + OAuth2 + suppression compte"
        },
        "timestamp": datetime.now(),
        "docs": "/docs",
        "databases": {
            "postgresql_livres": "/postgres/livres/* (📚 livres schéma test + 28 requêtes SQL)",
            "postgresql_analytics": "/postgres-extras/* (📊 analytics PostgreSQL avancés)",
            "mongo_livres": "/mongo-livres/* (📚 4766 livres + 💬 85 critiques Babelio)",
            "mongo_extras": "/mongo-extras/* (🎯 analytics MongoDB + 39 requêtes NoSQL)"
        },
        "authentication": {
                        "oauth2": "/auth/token (form-data username/password)",
            "json": "/auth/login (JSON email/password)",
            "jwt": {
                "register": "/auth/register",
                "me": "/auth/me",
                "refresh": "/auth/refresh",
                "logout": "/auth/logout",
                "delete": "/auth/delete-account"
            },
            "info": "🔐 OAuth2 + JWT + JSON - Support complet"
        },
        "features": [
            "🚀 API optimisée : 40 endpoints essentiels (-45%)",
            "📚 4766 livres MongoDB + Base PostgreSQL",
            "🔍 Recherche avancée et filtres multiples",
            "📊 67 requêtes BDD optimisées (28 SQL + 39 NoSQL)",
            "📈 Analytics temps réel (2 bases de données)",
            "🔐 Authentification JWT sécurisée",
            "📱 Interface Streamlit moderne",
            "⚡ Performance améliorée"
        ]
    }

# Route de santé optimisée (publique)
@app.get("/health")
async def health_check():
    """🏥 Vérification de l'état de santé de l'API et des bases de données"""
    status = {
        "api": "OK",
        "version": "3.0.0",
        "optimization_status": "✅ 40 endpoints actifs (-45%)",
        "timestamp": datetime.now(),
        "databases": {}
    }
    
    # Test PostgreSQL
    try:
        check_db_connection()
        status["databases"]["postgresql"] = "✅ connected"
    except Exception as e:
        status["databases"]["postgresql"] = f"❌ error: {str(e)}"
    
    # Test MongoDB
    if MONGODB_AVAILABLE and mongodb_service:
        try:
            if mongodb_service.async_client is not None:
                await mongodb_service.database.list_collection_names()
                status["databases"]["mongodb"] = "✅ connected"
            else:
                status["databases"]["mongodb"] = "⚠️ not initialized"
        except Exception as e:
            status["databases"]["mongodb"] = f"❌ error: {str(e)}"
    else:
        status["databases"]["mongodb"] = "⚠️ not configured"
    
    return status

# Route de résumé optimisée (publique)
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
                "optimization": "✅ 40 endpoints essentiels (-45%)",
                "livres_mongodb": mongo_data.get("livres_mongodb", "N/A"),
                "critiques_babelio": mongo_data.get("critiques_babelio", "N/A"),
                "requetes_bdd_total": "67 requêtes optimisées",
                "requetes_sql": "28 requêtes PostgreSQL",
                "requetes_nosql": "39 requêtes MongoDB",
                "authentification": "JWT",
                "bases_donnees": ["PostgreSQL", "MongoDB"]
            },
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ❌ ROUTES LEGACY SUPPRIMÉES POUR OPTIMISATION :
# 
# /users/ (CRUD users legacy) → remplacé par /auth/*
# /items/ (CRUD items legacy) → remplacé par /postgres/livres/*
# /db-status/ → remplacé par /health (même fonctionnalité)

# Route de recherche globale optimisée
@app.get("/search/", tags=["Search"])
async def search_books(
    query: str,
    category: Optional[str] = None,
    database: str = "mongo",  # mongo par défaut (4766 livres vs quelques livres PostgreSQL)
    db=Depends(get_db)
):
    """🔍 Rechercher des livres dans PostgreSQL ou MongoDB (optimisé pour MongoDB)"""
    if database == "mongo":
        if MONGODB_AVAILABLE and mongodb_service:
            return await mongodb_service.search_books(query, category)
        else:
            raise HTTPException(status_code=503, detail="MongoDB non disponible")
    elif database == "postgres":
        # Recherche basique PostgreSQL (peu de données)
        from database.crud import item_crud
        return item_crud.search_items(db, query, category)
    else:
        raise HTTPException(status_code=400, detail="Base de données non supportée. Utilisez 'mongo' (recommandé) ou 'postgres'")

# ❌ Route /stats/ globale supprimée pour simplification
# Utilisez les endpoints spécialisés :
# - /postgres/livres/stats/general (PostgreSQL)
# - /mongo-extras/analytics/general (MongoDB)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 