from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        field_schema.update(type="string")
        return field_schema

# Modèles pour les livres dans MongoDB
class BookMongo(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: str
    status: str = "active"
    publication_year: Optional[int] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    rating: Optional[float] = None
    tags: List[str] = []
    reviews: List[Dict[str, Any]] = []
    stock_quantity: Optional[int] = 0
    language: Optional[str] = "fr"
    format: Optional[str] = "paperback"  # paperback, hardcover, ebook, audiobook
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class BookMongoCreate(BaseModel):
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: str
    status: str = "active"
    publication_year: Optional[int] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    rating: Optional[float] = None
    tags: List[str] = []
    stock_quantity: Optional[int] = 0
    language: Optional[str] = "fr"
    format: Optional[str] = "paperback"

class BookMongoUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    status: Optional[str] = None
    publication_year: Optional[int] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    rating: Optional[float] = None
    tags: Optional[List[str]] = None
    stock_quantity: Optional[int] = None
    language: Optional[str] = None
    format: Optional[str] = None

# Modèles pour les analyses de données
class BookAnalytics(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    book_id: str  # Référence au livre
    views_count: int = 0
    purchases_count: int = 0
    average_rating: Optional[float] = None
    total_reviews: int = 0
    popularity_score: Optional[float] = None
    trends_data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

# Modèles pour les recommandations
class BookRecommendation(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_preferences: Dict[str, Any] = {}
    recommended_books: List[str] = []  # Liste des IDs de livres
    recommendation_type: str = "content_based"  # content_based, collaborative, hybrid
    confidence_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)

# Modèles pour les ventes et inventaire
class BookInventory(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    book_id: str
    stock_quantity: int = 0
    reserved_quantity: int = 0
    min_stock_level: int = 5
    max_stock_level: int = 100
    supplier_info: Dict[str, Any] = {}
    last_restock_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None 