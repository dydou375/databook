from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager

from models.models import User, UserCreate, UserUpdate, Item, ItemCreate, ItemUpdate
from database.database import get_db, init_db, check_db_connection
from database.crud import user_crud, item_crud
from auth.auth import require_api_key

# Configuration simplifiée
try:
    from config.config import settings
    ALLOWED_ORIGINS = settings.allowed_origins
    API_KEY = settings.api_key
except:
    # Configuration par défaut si config.py a des problèmes
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"]
    API_KEY = "your-api-key-change-this"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Démarrage de l'API DataBook (PostgreSQL uniquement)...")
    print("📊 Initialisation de PostgreSQL...")
    init_db()
    check_db_connection()
    print("✅ Application prête!")
    yield
    
    # Shutdown
    print("🛑 Arrêt de l'application...")

# Initialisation de l'application FastAPI
app = FastAPI(
    title="DATA BOOK API - PostgreSQL",
    description="""
    API pour l'analyse et la gestion des données de livres (PostgreSQL uniquement)
    
    ## Fonctionnalités
    
    * **PostgreSQL** : Base de données relationnelle pour les données structurées
    * **Authentification** : Clé API pour protéger les endpoints sensibles
    * **Recherche** : Recherche textuelle dans PostgreSQL
    * **CRUD complet** : Création, lecture, mise à jour, suppression
    
    """,
    version="1.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de base (publique)
@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API DataBook (PostgreSQL)",
        "description": "API pour l'analyse des données de livres avec PostgreSQL",
        "version": "1.5.0",
        "timestamp": datetime.now(),
        "docs": "/docs",
        "endpoints": {
            "books": "/books/",
            "users": "/users/",
            "search": "/search/",
            "stats": "/stats/"
        },
        "features": [
            "Gestion des livres PostgreSQL",
            "Gestion des utilisateurs",
            "Recherche textuelle",
            "API sécurisée",
            "Documentation interactive"
        ]
    }

# Route de santé (publique)
@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API et de PostgreSQL"""
    status = {
        "api": "OK",
        "timestamp": datetime.now(),
        "databases": {}
    }
    
    # Test PostgreSQL
    try:
        check_db_connection()
        status["databases"]["postgresql"] = "connected"
        status["status"] = "healthy"
    except Exception as e:
        status["databases"]["postgresql"] = f"error: {str(e)}"
        status["status"] = "unhealthy"
    
    return status

# Routes pour les utilisateurs (protégées par clé API)
@app.post("/users/", response_model=User, tags=["Users"])
async def create_user(user: UserCreate, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Créer un nouvel utilisateur (nécessite une clé API)"""
    return user_crud.create_user(db, user)

@app.get("/users/", response_model=List[User], tags=["Users"])
async def get_users(skip: int = 0, limit: int = 100, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Récupérer la liste des utilisateurs (nécessite une clé API)"""
    return user_crud.get_users(db, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: int, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Récupérer un utilisateur par son ID (nécessite une clé API)"""
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@app.put("/users/{user_id}", response_model=User, tags=["Users"])
async def update_user(user_id: int, user_update: UserUpdate, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Mettre à jour un utilisateur (nécessite une clé API)"""
    user = user_crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@app.delete("/users/{user_id}", tags=["Users"])
async def delete_user(user_id: int, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Supprimer un utilisateur (nécessite une clé API)"""
    success = user_crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"message": "Utilisateur supprimé avec succès"}

# Routes pour les livres/items
@app.get("/books/", response_model=List[Item], tags=["Books"])
async def get_books(skip: int = 0, limit: int = 100, category: Optional[str] = None, db=Depends(get_db)):
    """Récupérer la liste des livres (publique)"""
    if category:
        return item_crud.get_items_by_category(db, category, skip=skip, limit=limit)
    return item_crud.get_items(db, skip=skip, limit=limit)

@app.get("/books/{book_id}", response_model=Item, tags=["Books"])
async def get_book(book_id: int, db=Depends(get_db)):
    """Récupérer un livre par son ID (publique)"""
    book = item_crud.get_item(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return book

@app.post("/books/", response_model=Item, tags=["Books"])
async def create_book(book: ItemCreate, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Créer un nouveau livre (nécessite une clé API)"""
    return item_crud.create_item(db, book)

@app.put("/books/{book_id}", response_model=Item, tags=["Books"])
async def update_book(book_id: int, book_update: ItemUpdate, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Mettre à jour un livre (nécessite une clé API)"""
    book = item_crud.update_item(db, book_id, book_update)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return book

@app.delete("/books/{book_id}", tags=["Books"])
async def delete_book(book_id: int, db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Supprimer un livre (nécessite une clé API)"""
    success = item_crud.delete_item(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return {"message": "Livre supprimé avec succès"}

# Routes de recherche et filtrage
@app.get("/search/", response_model=List[Item], tags=["Search"])
async def search_books(
    query: str,
    category: Optional[str] = None,
    db=Depends(get_db)
):
    """Rechercher des livres par titre ou description"""
    return item_crud.search_items(db, query, category)

@app.get("/books/category/{category}", response_model=List[Item], tags=["Books"])
async def get_books_by_category(
    category: str,
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_db)
):
    """Récupérer les livres par catégorie"""
    return item_crud.get_items_by_category(db, category, skip=skip, limit=limit)

@app.get("/books/price-range/", response_model=List[Item], tags=["Books"])
async def get_books_by_price_range(
    min_price: float,
    max_price: float,
    db=Depends(get_db)
):
    """Récupérer les livres dans une fourchette de prix"""
    if min_price > max_price:
        raise HTTPException(status_code=400, detail="Prix minimum supérieur au prix maximum")
    return item_crud.get_items_by_price_range(db, min_price, max_price)

@app.get("/users/{user_id}/books/", response_model=List[Item], tags=["Users"])
async def get_user_books(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_db),
    api_key: str = Depends(require_api_key)
):
    """Récupérer les livres d'un utilisateur"""
    return item_crud.get_items_by_owner(db, owner_id=user_id, skip=skip, limit=limit)

# Routes de statistiques (protégées)
@app.get("/stats/", tags=["Statistics"])
async def get_statistics(db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Récupérer les statistiques générales (nécessite une clé API)"""
    return {
        "total_users": user_crud.count_users(db),
        "total_books": item_crud.count_items(db),
        "timestamp": datetime.now(),
        "database": "PostgreSQL"
    }

# Route pour tester la connexion à la base de données (protégée)
@app.get("/db-status/", tags=["System"])
async def database_status(db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Vérifier le statut de la base de données (nécessite une clé API)"""
    try:
        # Test simple de connexion
        db.execute("SELECT 1")
        return {"database": "PostgreSQL", "status": "connected", "timestamp": datetime.now()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erreur de base de données: {str(e)}")

if __name__ == "__main__":
    print("🚀 Lancement de l'API DataBook (PostgreSQL)")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🏥 Santé: http://localhost:8000/health")
    print("📚 Livres: http://localhost:8000/books/")
    uvicorn.run(
        "main_no_mongo:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 