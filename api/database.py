from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
from config import settings

# Configuration de la base de données principale
DATABASE_URL = settings.database_url

# Création du moteur de base de données
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,  # Vérification de la connexion
    echo=settings.debug  # Log des requêtes SQL en mode debug
)

# Configuration de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Modèles de base de données adaptés pour les livres
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relation avec les livres
    books = relationship("BookDB", back_populates="owner", cascade="all, delete-orphan")

class BookDB(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(255), index=True)
    isbn = Column(String(20), unique=True, index=True)
    description = Column(Text)
    price = Column(Float)
    category = Column(String(100), nullable=False, index=True)
    status = Column(String(50), default="active")
    publication_year = Column(Integer)
    publisher = Column(String(255))
    page_count = Column(Integer)
    rating = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relation avec l'utilisateur
    owner = relationship("UserDB", back_populates="books")

# Alias pour maintenir la compatibilité
ItemDB = BookDB

# Fonction pour obtenir une session de base de données
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour initialiser la base de données
def init_db():
    """Créer toutes les tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Base de données initialisée avec succès!")
        print(f"📍 URL: {DATABASE_URL}")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        raise

# Fonction pour supprimer toutes les tables (utile pour les tests)
def drop_db():
    """Supprimer toutes les tables"""
    Base.metadata.drop_all(bind=engine)
    print("🗑️ Toutes les tables ont été supprimées!")

# Fonction pour recréer la base de données
def reset_db():
    """Supprimer et recréer toutes les tables"""
    drop_db()
    init_db()
    print("🔄 Base de données réinitialisée!")

# Fonction utilitaire pour vérifier la connexion
def check_db_connection():
    """Vérifier la connexion à la base de données"""
    try:
        db = SessionLocal()
        # Test simple de connexion avec text()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Connexion à la base de données réussie!")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False

# Configuration MongoDB (optionnel)
try:
    from pymongo import MongoClient
    
    def get_mongodb():
        """Obtenir une connexion MongoDB"""
        client = MongoClient(settings.mongodb_url)
        db = client[settings.mongodb_database]
        return db
        
    def check_mongodb_connection():
        """Vérifier la connexion MongoDB"""
        try:
            db = get_mongodb()
            db.list_collection_names()
            print("✅ Connexion MongoDB réussie!")
            return True
        except Exception as e:
            print(f"❌ Erreur MongoDB: {e}")
            return False
            
except ImportError:
    print("📦 PyMongo non installé - MongoDB non disponible")
    
    def get_mongodb():
        raise ImportError("PyMongo n'est pas installé")
        
    def check_mongodb_connection():
        return False 