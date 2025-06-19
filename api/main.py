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

# Import des nouveaux routers
from routes.routes_postgres import postgres_router
from routes.routes_postgres_livres import postgres_livres_router  # Nouveau : routes pour les vraies données PostgreSQL
from routes.routes_postgres_extras import postgres_extras_router  # Nouveau : analytics PostgreSQL
from routes.routes_mongo import mongo_router
from routes.routes_real_data import real_data_router
from routes.routes_real_mongo import real_mongo_router
from routes.routes_mongo_livres import mongo_livres_router
from routes.routes_mongo_extras import mongo_extras_router
from routes.auth_routes import auth_router  # Nouveau : routes d'authentification
try:
    from routes.routes_livres import livres_router
    LIVRES_ROUTER_AVAILABLE = True
except ImportError:
    LIVRES_ROUTER_AVAILABLE = False

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

# Inclusion des routers
app.include_router(postgres_router)
app.include_router(postgres_livres_router)  # Routes pour les vraies données PostgreSQL (schéma test)
app.include_router(postgres_extras_router)  # Routes analytics PostgreSQL
app.include_router(mongo_router)
app.include_router(real_data_router)  # Nouvelles routes pour les vraies données
app.include_router(real_mongo_router)  # Routes MongoDB pour les vraies collections
app.include_router(mongo_livres_router)  # Routes spécifiques pour livres et critiques MongoDB
app.include_router(mongo_extras_router)  # Routes avancées MongoDB
app.include_router(auth_router)  # Inclure le nouveau router pour les routes d'authentification

# Inclure le nouveau router pour les livres si disponible
if LIVRES_ROUTER_AVAILABLE:
    app.include_router(livres_router)

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
            "postgresql": "/postgres/* (legacy users + stats)",
            "postgresql_livres": "/postgres/livres/* (📚 vraies données schéma test)",
            "postgresql_analytics": "/postgres-extras/* (📊 graphiques PostgreSQL)",
            "mongodb": "/mongo/*",
            "mongodb_real": "/mongodb/* (vos vraies données)",
            "mongo_livres": "/mongo-livres/* (📚 livres et 💬 critiques)",
            "mongo_extras": "/mongo-extras/* (🎯 analytics avancés)",
            "livres": "/livres/*" if LIVRES_ROUTER_AVAILABLE else "❌ Non disponible"
        },
        "authentication": {
            "jwt": {
                "login": "/auth/login",
                "token": "/auth/token", 
                "register": "/auth/register",
                "me": "/auth/me",
                "refresh": "/auth/refresh"
            },
            "info": "🔐 Authentification JWT moderne - Clé API supprimée",
            "migration_status": "✅ Migration complète vers JWT terminée"
        },
        "features": [
            "📚 Gestion des vraies données de livres (PostgreSQL schéma test)",
            "🔍 Recherche avancée avec jointures complètes", 
            "📊 Analytics temps réel MongoDB ET PostgreSQL",
            "📈 Graphiques et visualisations pour les deux BDD",
            "🔐 Authentification JWT moderne (plus de clé API)",
            "🛡️ API sécurisée et nettoyée",
            "🗂️ Structure de base optimisée (auteur, editeur, langue, sujet)"
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

# Routes legacy (maintien de la compatibilité)
@app.post("/users/", response_model=User, tags=["Legacy"])
async def create_user(user: UserCreate, db=Depends(get_db), current_user = Depends(require_jwt)):
    """Créer un nouvel utilisateur (legacy - utilisez /postgres/users/)"""
    return user_crud.create_user(db, user)

@app.get("/users/", response_model=List[User], tags=["Legacy"])
async def get_users(skip: int = 0, limit: int = 100, db=Depends(get_db), current_user = Depends(require_jwt)):
    """Récupérer la liste des utilisateurs (legacy - utilisez /postgres/users/)"""
    return user_crud.get_users(db, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=User, tags=["Legacy"])
async def get_user(user_id: int, db=Depends(get_db), current_user = Depends(require_jwt)):
    """Récupérer un utilisateur par son ID (legacy - utilisez /postgres/users/{user_id})"""
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

# Note: Les routes legacy /books/ ont été supprimées car nous n'utilisons plus
# la table 'books'. Utilisez /postgres/livres/ pour accéder aux vraies données.

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

# Route pour tester la connexion aux bases de données
@app.get("/db-status/", tags=["System"])
async def database_status(db=Depends(get_db), current_user = Depends(require_jwt)):
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