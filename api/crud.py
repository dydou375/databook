from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime

from database import UserDB, ItemDB
from models import UserCreate, UserUpdate, ItemCreate, ItemUpdate

# Configuration pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hacher un mot de passe"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)

# CRUD pour les utilisateurs
class UserCRUD:
    def create_user(self, db: Session, user: UserCreate) -> UserDB:
        """Créer un nouvel utilisateur"""
        hashed_password = hash_password(user.password)
        db_user = UserDB(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            hashed_password=hashed_password,
            is_active=user.is_active
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def get_user(self, db: Session, user_id: int) -> Optional[UserDB]:
        """Récupérer un utilisateur par son ID"""
        return db.query(UserDB).filter(UserDB.id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[UserDB]:
        """Récupérer un utilisateur par son email"""
        return db.query(UserDB).filter(UserDB.email == email).first()
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserDB]:
        """Récupérer une liste d'utilisateurs"""
        return db.query(UserDB).offset(skip).limit(limit).all()
    
    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserDB]:
        """Mettre à jour un utilisateur"""
        db_user = self.get_user(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        
        # Hacher le nouveau mot de passe s'il est fourni
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        
        # Mettre à jour les champs
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.now()
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def delete_user(self, db: Session, user_id: int) -> bool:
        """Supprimer un utilisateur"""
        db_user = self.get_user(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[UserDB]:
        """Authentifier un utilisateur"""
        user = self.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    def count_users(self, db: Session) -> int:
        """Compter le nombre total d'utilisateurs"""
        return db.query(UserDB).count()

# CRUD pour les items
class ItemCRUD:
    def create_item(self, db: Session, item: ItemCreate) -> ItemDB:
        """Créer un nouvel item"""
        db_item = ItemDB(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    
    def get_item(self, db: Session, item_id: int) -> Optional[ItemDB]:
        """Récupérer un item par son ID"""
        return db.query(ItemDB).filter(ItemDB.id == item_id).first()
    
    def get_items(self, db: Session, skip: int = 0, limit: int = 100) -> List[ItemDB]:
        """Récupérer une liste d'items"""
        return db.query(ItemDB).offset(skip).limit(limit).all()
    
    def get_items_by_owner(self, db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[ItemDB]:
        """Récupérer les items d'un propriétaire"""
        return (
            db.query(ItemDB)
            .filter(ItemDB.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_items_by_category(self, db: Session, category: str, skip: int = 0, limit: int = 100) -> List[ItemDB]:
        """Récupérer les items par catégorie"""
        return (
            db.query(ItemDB)
            .filter(ItemDB.category == category)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_items(self, db: Session, query: str, category: Optional[str] = None) -> List[ItemDB]:
        """Rechercher des items par titre ou description"""
        db_query = db.query(ItemDB).filter(
            or_(
                ItemDB.title.contains(query),
                ItemDB.description.contains(query)
            )
        )
        
        if category:
            db_query = db_query.filter(ItemDB.category == category)
        
        return db_query.all()
    
    def update_item(self, db: Session, item_id: int, item_update: ItemUpdate) -> Optional[ItemDB]:
        """Mettre à jour un item"""
        db_item = self.get_item(db, item_id)
        if not db_item:
            return None
        
        update_data = item_update.dict(exclude_unset=True)
        
        # Mettre à jour les champs
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db_item.updated_at = datetime.now()
        db.commit()
        db.refresh(db_item)
        return db_item
    
    def delete_item(self, db: Session, item_id: int) -> bool:
        """Supprimer un item"""
        db_item = self.get_item(db, item_id)
        if not db_item:
            return False
        
        db.delete(db_item)
        db.commit()
        return True
    
    def count_items(self, db: Session) -> int:
        """Compter le nombre total d'items"""
        return db.query(ItemDB).count()
    
    def get_items_by_price_range(self, db: Session, min_price: float, max_price: float) -> List[ItemDB]:
        """Récupérer les items dans une fourchette de prix"""
        return (
            db.query(ItemDB)
            .filter(ItemDB.price >= min_price, ItemDB.price <= max_price)
            .all()
        )

# Instances globales des classes CRUD
user_crud = UserCRUD()
item_crud = ItemCRUD() 