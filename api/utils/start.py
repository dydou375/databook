#!/usr/bin/env python3
"""
Script de démarrage pour l'API DataBook
Ce script configure et lance l'API avec toutes ses dépendances
"""

import os
import sys
import asyncio
import uvicorn
from pathlib import Path

# Ajouter le répertoire parent au path Python
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from config.config import settings
from database.database import init_db, check_db_connection
from database.mongo_crud import mongodb_service

def print_banner():
    """Afficher la bannière de démarrage"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    📚 DataBook API v2.0                     ║
    ║                                                              ║
    ║    API pour l'analyse et la gestion des données de livres   ║
    ║                                                              ║
    ║    🔗 PostgreSQL + MongoDB                                   ║
    ║    🚀 FastAPI + Uvicorn                                      ║
    ║    🔐 Authentification par clé API                          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_environment():
    """Vérifier la configuration de l'environnement"""
    print("🔍 Vérification de la configuration...")
    
    # Vérifier les variables essentielles
    if not settings.api_key or settings.api_key == "your-api-key-change-this":
        print("⚠️  AVERTISSEMENT: Clé API par défaut détectée. Changez-la en production!")
    
    if not settings.secret_key or settings.secret_key == "your-super-secret-key-change-this-in-production":
        print("⚠️  AVERTISSEMENT: Clé secrète par défaut détectée. Changez-la en production!")
    
    print(f"📊 PostgreSQL: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    print(f"🍃 MongoDB: {settings.mongodb_host}:{settings.mongodb_port}/{settings.mongodb_database}")
    print(f"🌐 CORS: {settings.allowed_origins}")
    print(f"🐛 Debug: {settings.debug}")

def init_databases():
    """Initialiser les bases de données"""
    print("\n📊 Initialisation de PostgreSQL...")
    try:
        init_db()
        check_db_connection()
        print("✅ PostgreSQL initialisé avec succès")
    except Exception as e:
        print(f"❌ Erreur PostgreSQL: {e}")
        if not settings.debug:
            sys.exit(1)
    
    print("\n🍃 Test de connexion MongoDB...")
    try:
        mongodb_service.connect()
        print("✅ MongoDB connecté avec succès")
    except Exception as e:
        print(f"⚠️  MongoDB non disponible: {e}")
        print("   L'API fonctionnera sans MongoDB")

def create_sample_data():
    """Créer des données d'exemple (optionnel)"""
    print("\n📝 Création de données d'exemple...")
    # Cette fonction pourrait être implémentée pour ajouter des données de test
    print("   (Pas de données d'exemple créées)")

def print_endpoints():
    """Afficher les endpoints disponibles"""
    print("\n🛣️  Endpoints principaux:")
    print("   📖 Documentation: http://localhost:8000/docs")
    print("   🏠 Accueil: http://localhost:8000/")
    print("   ❤️  Santé: http://localhost:8000/health")
    print("\n📊 PostgreSQL:")
    print("   📚 Livres: http://localhost:8000/postgres/books/")
    print("   👥 Utilisateurs: http://localhost:8000/postgres/users/")
    print("   📈 Stats: http://localhost:8000/postgres/statistics/")
    print("\n🍃 MongoDB:")
    print("   📚 Livres: http://localhost:8000/mongo/books/")
    print("   🔍 Recherche: http://localhost:8000/mongo/search/")
    print("   📈 Analytics: http://localhost:8000/mongo/statistics/")

def main():
    """Fonction principale"""
    print_banner()
    check_environment()
    init_databases()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--sample-data":
        create_sample_data()
    
    print_endpoints()
    
    print(f"\n🚀 Démarrage du serveur sur http://localhost:8000")
    print("   Appuyez sur Ctrl+C pour arrêter")
    
    # Configuration Uvicorn
    config = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": settings.debug,
        "log_level": "info" if not settings.debug else "debug",
        "access_log": True,
    }
    
    # Lancement du serveur
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du serveur demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 