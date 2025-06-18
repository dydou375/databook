from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.models import Item, ItemCreate, ItemUpdate, User
from database.database import get_db
from database.crud import item_crud, user_crud
from auth.auth import require_api_key

# Router pour les endpoints PostgreSQL
postgres_router = APIRouter(prefix="/postgres", tags=["PostgreSQL"])

# Endpoints publics pour les livres PostgreSQL
@postgres_router.get("/books/", response_model=List[Item])
async def get_postgres_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupérer les livres depuis PostgreSQL (publique)"""
    if category:
        return item_crud.get_items_by_category(db, category, skip=skip, limit=limit)
    return item_crud.get_items(db, skip=skip, limit=limit)

@postgres_router.get("/books/{book_id}", response_model=Item)
async def get_postgres_book(book_id: int, db: Session = Depends(get_db)):
    """Récupérer un livre par ID depuis PostgreSQL (publique)"""
    book = item_crud.get_item(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé dans PostgreSQL")
    return book

@postgres_router.get("/books/category/{category}", response_model=List[Item])
async def get_postgres_books_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db)
):
    """Récupérer les livres par catégorie depuis PostgreSQL (publique)"""
    return item_crud.get_items_by_category(db, category, skip=skip, limit=limit)

@postgres_router.get("/books/price-range/", response_model=List[Item])
async def get_postgres_books_by_price(
    min_price: float = Query(..., ge=0),
    max_price: float = Query(..., ge=0),
    db: Session = Depends(get_db)
):
    """Récupérer les livres par fourchette de prix depuis PostgreSQL (publique)"""
    if min_price > max_price:
        raise HTTPException(status_code=400, detail="Le prix minimum ne peut pas être supérieur au prix maximum")
    return item_crud.get_items_by_price_range(db, min_price, max_price)

@postgres_router.get("/search/", response_model=List[Item])
async def search_postgres_books(
    query: str = Query(..., min_length=2),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Rechercher des livres dans PostgreSQL (publique)"""
    return item_crud.search_items(db, query=query, category=category)

# Endpoints protégés pour la gestion des livres PostgreSQL
@postgres_router.post("/books/", response_model=Item)
async def create_postgres_book(
    book: ItemCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key)
):
    """Créer un nouveau livre dans PostgreSQL (nécessite une clé API)"""
    return item_crud.create_item(db, book)

@postgres_router.put("/books/{book_id}", response_model=Item)
async def update_postgres_book(
    book_id: int,
    book_update: ItemUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key)
):
    """Mettre à jour un livre dans PostgreSQL (nécessite une clé API)"""
    updated_book = item_crud.update_item(db, book_id, book_update)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Livre non trouvé dans PostgreSQL")
    return updated_book

@postgres_router.delete("/books/{book_id}")
async def delete_postgres_book(
    book_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key)
):
    """Supprimer un livre dans PostgreSQL (nécessite une clé API)"""
    success = item_crud.delete_item(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Livre non trouvé dans PostgreSQL")
    return {"message": "Livre supprimé avec succès de PostgreSQL"}

# Endpoints pour les statistiques PostgreSQL
@postgres_router.get("/statistics/")
async def get_postgres_statistics(
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key)
):
    """Récupérer les statistiques PostgreSQL (nécessite une clé API)"""
    return {
        "total_users": user_crud.count_users(db),
        "total_books": item_crud.count_items(db),
        "timestamp": datetime.now(),
        "database": "PostgreSQL"
    }

# Endpoints pour les utilisateurs
@postgres_router.get("/users/", response_model=List[User])
async def get_postgres_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key)
):
    """Récupérer la liste des utilisateurs depuis PostgreSQL (nécessite une clé API)"""
    return user_crud.get_users(db, skip=skip, limit=limit)

@postgres_router.get("/users/{user_id}", response_model=User)
async def get_postgres_user(
    user_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key)
):
    """Récupérer un utilisateur par ID depuis PostgreSQL (nécessite une clé API)"""
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé dans PostgreSQL")
    return user

@postgres_router.get("/users/{user_id}/books/", response_model=List[Item])
async def get_user_books(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key)
):
    """Récupérer les livres d'un utilisateur depuis PostgreSQL (nécessite une clé API)"""
    # Vérifier que l'utilisateur existe
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return item_crud.get_items_by_owner(db, owner_id=user_id, skip=skip, limit=limit) 