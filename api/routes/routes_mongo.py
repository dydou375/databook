from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.models_mongo import BookMongo, BookMongoCreate, BookMongoUpdate
from database.mongo_crud import mongodb_service
from auth.auth import require_api_key

# Router pour les endpoints MongoDB
mongo_router = APIRouter(prefix="/mongo", tags=["MongoDB"])

# Endpoints publics pour les livres MongoDB
@mongo_router.get("/books/", response_model=List[BookMongo])
async def get_mongo_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    category: Optional[str] = None
):
    """Récupérer les livres depuis MongoDB (publique)"""
    filters = {"category": category} if category else None
    return await mongodb_service.get_books(skip=skip, limit=limit, filters=filters)

@mongo_router.get("/books/{book_id}", response_model=BookMongo)
async def get_mongo_book(book_id: str):
    """Récupérer un livre par ID depuis MongoDB (publique)"""
    book = await mongodb_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé dans MongoDB")
    return book

@mongo_router.get("/books/category/{category}", response_model=List[BookMongo])
async def get_mongo_books_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=500)
):
    """Récupérer les livres par catégorie depuis MongoDB (publique)"""
    return await mongodb_service.get_books_by_category(category, skip=skip, limit=limit)

@mongo_router.get("/books/popular/", response_model=List[BookMongo])
async def get_popular_mongo_books(limit: int = Query(10, le=50)):
    """Récupérer les livres populaires depuis MongoDB (publique)"""
    return await mongodb_service.get_popular_books(limit=limit)

@mongo_router.get("/search/", response_model=List[BookMongo])
async def search_mongo_books(
    query: str = Query(..., min_length=2),
    category: Optional[str] = None
):
    """Rechercher des livres dans MongoDB (publique)"""
    return await mongodb_service.search_books(query=query, category=category)

# Endpoints protégés pour la gestion des livres MongoDB
@mongo_router.post("/books/", response_model=BookMongo)
async def create_mongo_book(
    book: BookMongoCreate,
    api_key: str = Depends(require_api_key)
):
    """Créer un nouveau livre dans MongoDB (nécessite une clé API)"""
    return await mongodb_service.create_book(book)

@mongo_router.put("/books/{book_id}", response_model=BookMongo)
async def update_mongo_book(
    book_id: str,
    book_update: BookMongoUpdate,
    api_key: str = Depends(require_api_key)
):
    """Mettre à jour un livre dans MongoDB (nécessite une clé API)"""
    updated_book = await mongodb_service.update_book(book_id, book_update)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Livre non trouvé dans MongoDB")
    return updated_book

@mongo_router.delete("/books/{book_id}")
async def delete_mongo_book(
    book_id: str,
    api_key: str = Depends(require_api_key)
):
    """Supprimer un livre dans MongoDB (nécessite une clé API)"""
    success = await mongodb_service.delete_book(book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Livre non trouvé dans MongoDB")
    return {"message": "Livre supprimé avec succès de MongoDB"}

# Endpoints pour les statistiques MongoDB
@mongo_router.get("/statistics/")
async def get_mongo_statistics(api_key: str = Depends(require_api_key)):
    """Récupérer les statistiques MongoDB (nécessite une clé API)"""
    return await mongodb_service.get_statistics()

# Endpoint de synchronisation entre PostgreSQL et MongoDB
@mongo_router.post("/sync/")
async def sync_data(api_key: str = Depends(require_api_key)):
    """Synchroniser les données entre PostgreSQL et MongoDB (nécessite une clé API)"""
    # Cette fonction pourrait être implémentée pour synchroniser les données
    return {
        "message": "Synchronisation des données déclenchée",
        "timestamp": datetime.now(),
        "status": "en cours"
    } 