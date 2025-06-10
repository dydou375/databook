from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager

from models import User, UserCreate, UserUpdate, Item, ItemCreate, ItemUpdate
from database import get_db, init_db
from crud import user_crud, item_crud
from auth import require_api_key
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (si nécessaire)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="DATA BOOK API",
    description="API pour l'analyse et la gestion des données de livres",
    version="1.0.0",
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

# Route de base (publique)
@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API DataBook",
        "description": "API pour l'analyse des données de livres",
        "version": "1.0.0",
        "timestamp": datetime.now(),
        "docs": "/docs"
    }

# Route de santé (publique)
@app.get("/health")
async def health_check():
    return {"status": "OK", "timestamp": datetime.now()}

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

# Routes pour les livres/items (certaines publiques, d'autres protégées)
@app.get("/books/", response_model=List[Item], tags=["Books"])
async def get_books(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    """Récupérer la liste des livres (publique)"""
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

# Route de recherche (publique)
@app.get("/search/", tags=["Search"])
async def search_books(
    query: str,
    category: Optional[str] = None,
    db=Depends(get_db)
):
    """Rechercher des livres par titre ou description"""
    return item_crud.search_items(db, query, category)

# Routes de statistiques (protégées)
@app.get("/stats/", tags=["Statistics"])
async def get_statistics(db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Récupérer les statistiques générales (nécessite une clé API)"""
    return {
        "total_users": user_crud.count_users(db),
        "total_books": item_crud.count_items(db),
        "timestamp": datetime.now()
    }

# Route pour tester la connexion à la base de données (protégée)
@app.get("/db-status/", tags=["System"])
async def database_status(db=Depends(get_db), api_key: str = Depends(require_api_key)):
    """Vérifier le statut de la base de données (nécessite une clé API)"""
    try:
        # Test simple de connexion
        db.execute("SELECT 1")
        return {"database": "connected", "timestamp": datetime.now()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erreur de base de données: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 