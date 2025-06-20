from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Modèles simplifiés pour MongoDB (compatibles Pydantic v2)
class BookMongo(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow"
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
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
    tags: List[str] = Field(default_factory=list)
    reviews: List[Dict[str, Any]] = Field(default_factory=list)
    stock_quantity: Optional[int] = 0
    language: Optional[str] = "fr"
    format: Optional[str] = "paperback"  # paperback, hardcover, ebook, audiobook
    created_at: Optional[datetime] = None
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
    tags: List[str] = Field(default_factory=list)
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
        extra="allow"
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    book_id: str  # Référence au livre
    views_count: int = 0
    purchases_count: int = 0
    average_rating: Optional[float] = None
    total_reviews: int = 0
    popularity_score: Optional[float] = None
    trends_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Modèles pour les recommandations
class BookRecommendation(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow"
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    recommended_books: List[str] = Field(default_factory=list)  # Liste des IDs de livres
    recommendation_type: str = "content_based"  # content_based, collaborative, hybrid
    confidence_score: Optional[float] = None
    created_at: Optional[datetime] = None

# Modèles pour les ventes et inventaire
class BookInventory(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow"
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    book_id: str
    stock_quantity: int = 0
    reserved_quantity: int = 0
    min_stock_level: int = 5
    max_stock_level: int = 100
    supplier_info: Dict[str, Any] = Field(default_factory=dict)
    last_restock_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None 