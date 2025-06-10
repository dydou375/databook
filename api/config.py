import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Configuration de la clé API
    api_key: str = "your-api-key-change-this"
    
    # Configuration des bases de données Docker
    # Base de données principale (ex: PostgreSQL)
    database_url: str = "postgresql://user:password@localhost:5432/databook"
    
    # MongoDB (si utilisé)
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "databook"
    
    # MySQL (si utilisé)
    mysql_url: str = "mysql+pymysql://user:password@localhost:3306/databook"
    
    # Configuration de l'application
    app_name: str = "DataBook API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Configuration CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"]
    
    # Configuration JWT
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Configuration email (optionnel)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instance globale des paramètres
settings = Settings() 