import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

class Settings(BaseSettings):
    # Configuration de la clé API
    api_key: str = os.getenv("API_KEY", "databook-api-key-2024")
    
    # Configuration des bases de données
    # PostgreSQL
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "databook")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    
    def get_database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}?options=-csearch_path%3Dtest"
    
    # MongoDB
    mongodb_host: str = os.getenv("MONGODB_HOST", "localhost")
    mongodb_port: int = int(os.getenv("MONGODB_PORT", "27017"))
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "databook")
    
    def get_mongodb_url(self) -> str:
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}"
    
    # Configuration de l'application
    app_name: str = os.getenv("APP_NAME", "DataBook API")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Configuration CORS
    allowed_origins: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080,http://localhost:5173").split(",")
    
    # Configuration JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Configuration email (optionnel)
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Permet les attributs supplémentaires pour Pydantic 2

# Instance globale des paramètres
settings = Settings() 