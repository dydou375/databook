from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
from config.config import settings

# Configuration de la base de données principale
DATABASE_URL = settings.get_database_url()

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
    __table_args__ = {'schema': 'test'}  # 🎯 Forcer le schéma test
    
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
    __table_args__ = {'schema': 'test'}  # 🎯 Forcer le schéma test
    
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
    owner_id = Column(Integer, ForeignKey("test.users.id"), nullable=False)  # 🎯 Référence au schéma test
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relation avec l'utilisateur
    owner = relationship("UserDB", back_populates="books")

# Alias pour maintenir la compatibilité
ItemDB = BookDB

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour initialiser la base de données
def init_db():
    """Créer toutes les tables"""
    try:
        # S'assurer que le schéma test existe d'abord
        ensure_test_schema()
        
        # Créer toutes les tables dans le schéma test
        Base.metadata.create_all(bind=engine)
        print("✅ Base de données initialisée avec succès!")
        print(f"📍 URL: {DATABASE_URL}")
        print("🎯 Tables créées dans le schéma 'test'")
        
        # Vérifier les utilisateurs existants
        check_test_schema_users()
        
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
        client = MongoClient(settings.get_mongodb_url())
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

# Fonction pour vérifier les utilisateurs dans le schéma test
def check_test_schema_users():
    """Vérifier les utilisateurs dans le schéma test"""
    try:
        db = SessionLocal()
        
        # Vérifier l'existence du schéma test
        schema_exists = db.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'test'")).fetchone()
        
        if not schema_exists:
            print("⚠️ Le schéma 'test' n'existe pas")
            return False
        
        # Vérifier l'existence de la table users dans le schéma test
        table_exists = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'test' AND table_name = 'users'
        """)).fetchone()
        
        if not table_exists:
            print("⚠️ La table 'users' n'existe pas dans le schéma 'test'")
            return False
        
        # Compter les utilisateurs
        result = db.execute(text("SELECT COUNT(*) as count FROM test.users")).fetchone()
        user_count = result.count if result else 0
        
        print(f"✅ Schéma 'test' trouvé")
        print(f"📊 Nombre d'utilisateurs JWT dans test.users: {user_count}")
        
        # Afficher quelques utilisateurs (sans mots de passe en clair)
        if user_count > 0:
            users = db.execute(text("""
                SELECT id, email, first_name, last_name, is_active, created_at,
                       LEFT(hashed_password, 20) || '...' as password_preview
                FROM test.users 
                ORDER BY created_at DESC 
                LIMIT 3
            """)).fetchall()
            
            print("\n👥 Derniers utilisateurs enregistrés:")
            for user in users:
                print(f"  • ID {user.id}: {user.first_name} {user.last_name}")
                print(f"    📧 Email: {user.email}")
                print(f"    🔐 Hash: {user.password_preview}")
                print(f"    📅 Créé: {user.created_at}")
                print(f"    ✅ Actif: {user.is_active}")
                print()
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

# Fonction pour créer le schéma test s'il n'existe pas
def ensure_test_schema():
    """S'assurer que le schéma test existe"""
    try:
        db = SessionLocal()
        
        # Créer le schéma test s'il n'existe pas
        db.execute(text("CREATE SCHEMA IF NOT EXISTS test"))
        db.commit()
        
        print("✅ Schéma 'test' vérifié/créé")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du schéma: {e}")
        return False 