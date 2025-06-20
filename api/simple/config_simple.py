"""
Configuration simple pour l'API DataBook
"""
import os

# Configuration des bases de données
API_KEY = os.getenv("API_KEY", "databook-api-key-2024")
POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/databook") 
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "databook")

# Configuration serveur
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

print(f"""
📋 Configuration DataBook API
🔐 API Key: {API_KEY}
📊 PostgreSQL: {POSTGRES_URL}
🍃 MongoDB: {MONGODB_URL}/{MONGODB_DATABASE}
🌐 Serveur: {HOST}:{PORT}
🐛 Debug: {DEBUG}
""") 