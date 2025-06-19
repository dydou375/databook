from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
from bson import ObjectId

try:
    from config.config import settings
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    # Configuration par défaut
    class Settings:
        mongodb_url = "mongodb://localhost:27017"
        mongodb_database = "databook"
    settings = Settings()
from models.models_mongo import BookMongo, BookMongoCreate, BookMongoUpdate, BookAnalytics, BookRecommendation, BookInventory

class MongoDBService:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.async_client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.sync_db = None
        
    def connect(self):
        """Connexion synchrone à MongoDB"""
        try:
            self.client = MongoClient(settings.get_mongodb_url())
            self.sync_db = self.client[settings.mongodb_database]
            print(f"✅ Connexion MongoDB synchrone réussie: {settings.get_mongodb_url()}")
        except Exception as e:
            print(f"❌ Erreur de connexion MongoDB synchrone: {e}")
            raise
    
    async def connect_async(self):
        """Connexion asynchrone à MongoDB"""
        try:
            self.async_client = AsyncIOMotorClient(settings.get_mongodb_url())
            self.database = self.async_client[settings.mongodb_database]
            # Test de connexion
            await self.database.list_collection_names()
            print(f"✅ Connexion MongoDB asynchrone réussie: {settings.get_mongodb_url()}")
        except Exception as e:
            print(f"❌ Erreur de connexion MongoDB asynchrone: {e}")
            raise
    
    def disconnect(self):
        """Fermer les connexions"""
        if self.client:
            self.client.close()
        if self.async_client:
            self.async_client.close()
    
    # CRUD pour les livres
    async def create_book(self, book_data: BookMongoCreate) -> BookMongo:
        """Créer un nouveau livre"""
        book_dict = book_data.dict()
        book_dict["created_at"] = datetime.now()
        
        result = await self.database.books.insert_one(book_dict)
        created_book = await self.database.books.find_one({"_id": result.inserted_id})
        return BookMongo(**created_book)
    
    async def get_book(self, book_id: str) -> Optional[BookMongo]:
        """Récupérer un livre par ID"""
        try:
            book = await self.database.books.find_one({"_id": ObjectId(book_id)})
            return BookMongo(**book) if book else None
        except Exception:
            return None
    
    async def get_books(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[BookMongo]:
        """Récupérer une liste de livres avec filtres optionnels"""
        query = filters or {}
        cursor = self.database.books.find(query).skip(skip).limit(limit)
        books = await cursor.to_list(length=limit)
        return [BookMongo(**book) for book in books]
    
    async def update_book(self, book_id: str, book_update: BookMongoUpdate) -> Optional[BookMongo]:
        """Mettre à jour un livre"""
        try:
            update_data = book_update.dict(exclude_unset=True)
            if update_data:
                update_data["updated_at"] = datetime.now()
                await self.database.books.update_one(
                    {"_id": ObjectId(book_id)},
                    {"$set": update_data}
                )
            return await self.get_book(book_id)
        except Exception:
            return None
    
    async def delete_book(self, book_id: str) -> bool:
        """Supprimer un livre"""
        try:
            result = await self.database.books.delete_one({"_id": ObjectId(book_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def search_books(self, query: str, category: Optional[str] = None) -> List[BookMongo]:
        """Rechercher des livres par texte"""
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"author": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"tags": {"$regex": query, "$options": "i"}}
            ]
        }
        
        if category:
            search_filter["category"] = category
            
        cursor = self.database.books.find(search_filter)
        books = await cursor.to_list(length=100)
        return [BookMongo(**book) for book in books]
    
    async def get_books_by_category(self, category: str, skip: int = 0, limit: int = 50) -> List[BookMongo]:
        """Récupérer les livres par catégorie"""
        cursor = self.database.books.find({"category": category}).skip(skip).limit(limit)
        books = await cursor.to_list(length=limit)
        return [BookMongo(**book) for book in books]
    
    async def get_popular_books(self, limit: int = 10) -> List[BookMongo]:
        """Récupérer les livres populaires (basé sur rating et reviews)"""
        cursor = self.database.books.find({
            "rating": {"$gte": 4.0}
        }).sort("rating", -1).limit(limit)
        books = await cursor.to_list(length=limit)
        return [BookMongo(**book) for book in books]
    
    # Analytics
    async def create_analytics(self, book_id: str, analytics_data: Dict[str, Any]) -> BookAnalytics:
        """Créer des données d'analyse pour un livre"""
        analytics_dict = {
            "book_id": book_id,
            "created_at": datetime.now(),
            **analytics_data
        }
        
        result = await self.database.analytics.insert_one(analytics_dict)
        created_analytics = await self.database.analytics.find_one({"_id": result.inserted_id})
        return BookAnalytics(**created_analytics)
    
    async def get_book_analytics(self, book_id: str) -> Optional[BookAnalytics]:
        """Récupérer les analytics d'un livre"""
        analytics = await self.database.analytics.find_one({"book_id": book_id})
        return BookAnalytics(**analytics) if analytics else None
    
    async def update_analytics(self, book_id: str, update_data: Dict[str, Any]) -> bool:
        """Mettre à jour les analytics d'un livre"""
        try:
            update_data["updated_at"] = datetime.now()
            result = await self.database.analytics.update_one(
                {"book_id": book_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    # Statistiques et agrégations
    async def get_statistics(self) -> Dict[str, Any]:
        """Récupérer les statistiques générales"""
        total_books = await self.database.books.count_documents({})
        avg_rating = await self.database.books.aggregate([
            {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
        ]).to_list(length=1)
        
        categories = await self.database.books.aggregate([
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]).to_list(length=None)
        
        return {
            "total_books": total_books,
            "average_rating": avg_rating[0]["avg_rating"] if avg_rating else 0,
            "categories": categories,
            "timestamp": datetime.now()
        }
    
    async def get_books_by_year(self, year: int) -> List[BookMongo]:
        """Récupérer les livres par année de publication"""
        cursor = self.database.books.find({"publication_year": year})
        books = await cursor.to_list(length=None)
        return [BookMongo(**book) for book in books]
    
    async def get_books_by_price_range(self, min_price: float, max_price: float) -> List[BookMongo]:
        """Récupérer les livres dans une fourchette de prix"""
        cursor = self.database.books.find({
            "price": {"$gte": min_price, "$lte": max_price}
        })
        books = await cursor.to_list(length=None)
        return [BookMongo(**book) for book in books]

# Instance globale du service MongoDB
mongodb_service = MongoDBService() 