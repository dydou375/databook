from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from enum import Enum

# Énumérations
class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class CategoryEnum(str, Enum):
    ELECTRONICS = "electronics"
    BOOKS = "books"
    CLOTHING = "clothing"
    HOME = "home"
    SPORTS = "sports"
    OTHER = "other"

# Modèles pour les utilisateurs
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Le mot de passe doit contenir au moins 6 caractères')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if v and len(v) < 6:
            raise ValueError('Le mot de passe doit contenir au moins 6 caractères')
        return v

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Modèles pour les items
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: CategoryEnum
    status: StatusEnum = StatusEnum.ACTIVE
    
    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Le prix ne peut pas être négatif')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Le titre doit contenir au moins 3 caractères')
        return v.strip()

class ItemCreate(ItemBase):
    owner_id: int

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[CategoryEnum] = None
    status: Optional[StatusEnum] = None
    
    @validator('price')
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('Le prix ne peut pas être négatif')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError('Le titre doit contenir au moins 3 caractères')
        return v.strip() if v else v

class Item(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Modèles de réponse pour les relations
class UserWithItems(User):
    items: list[Item] = []

class ItemWithOwner(Item):
    owner: User

# Modèles pour l'authentification
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Modèles pour les réponses API
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    per_page: int
    pages: int 