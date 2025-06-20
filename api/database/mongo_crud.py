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
from models.models_mongo import BookMongo, BookMongoCreate, BookMongoUpdate, BookAnalytics

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
        """Récupérer les livres populaires"""
        cursor = self.database.books.find({
            "rating": {"$gte": 4.0}
        }).sort("rating", -1).limit(limit)
        books = await cursor.to_list(length=limit)
        return [BookMongo(**book) for book in books]
    
    # Statistiques
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

# Instance globale du service MongoDB
mongodb_service = MongoDBService() 