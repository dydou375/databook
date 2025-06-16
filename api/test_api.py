#!/usr/bin/env python3
"""
Script de test pour l'API DataBook
Teste les fonctionnalités principales de l'API
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your-api-key-change-this"  # Changez ceci selon votre configuration

class APITester:
    def __init__(self, base_url=BASE_URL, api_key=API_KEY):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
        self.headers_no_auth = {
            "Content-Type": "application/json"
        }
        
    def test_health(self):
        """Tester l'endpoint de santé"""
        print("🏥 Test de l'endpoint de santé...")
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API: {data.get('api', 'Unknown')}")
                databases = data.get('databases', {})
                for db_name, status in databases.items():
                    emoji = "✅" if status == "connected" else "❌"
                    print(f"{emoji} {db_name}: {status}")
                return True
            else:
                print(f"❌ Erreur: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def test_postgres_books(self):
        """Tester les endpoints PostgreSQL"""
        print("\n📊 Test des endpoints PostgreSQL...")
        
        # Test GET books
        try:
            response = requests.get(f"{self.base_url}/postgres/books/")
            if response.status_code == 200:
                books = response.json()
                print(f"✅ Récupération des livres PostgreSQL: {len(books)} livres")
            else:
                print(f"❌ Erreur GET books: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Test création d'un livre (nécessite auth)
        sample_book = {
            "title": "Test Book API",
            "description": "Livre de test créé par l'API",
            "price": 19.99,
            "category": "books",
            "owner_id": 1
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/postgres/books/", 
                headers=self.headers,
                json=sample_book
            )
            if response.status_code == 200:
                book = response.json()
                print(f"✅ Création livre PostgreSQL: ID {book.get('id')}")
                return book.get('id')
            else:
                print(f"❌ Erreur création livre: {response.status_code}")
                if response.status_code == 401:
                    print("   Vérifiez votre clé API")
                return None
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return None
    
    def test_mongo_books(self):
        """Tester les endpoints MongoDB"""
        print("\n🍃 Test des endpoints MongoDB...")
        
        # Test GET books
        try:
            response = requests.get(f"{self.base_url}/mongo/books/")
            if response.status_code == 200:
                books = response.json()
                print(f"✅ Récupération des livres MongoDB: {len(books)} livres")
            else:
                print(f"❌ Erreur GET books: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Test création d'un livre MongoDB
        sample_book = {
            "title": "Test MongoDB Book",
            "author": "Test Author",
            "description": "Livre de test MongoDB",
            "price": 24.99,
            "category": "tech",
            "tags": ["test", "api"],
            "rating": 4.5
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/mongo/books/", 
                headers=self.headers,
                json=sample_book
            )
            if response.status_code == 200:
                book = response.json()
                print(f"✅ Création livre MongoDB: ID {book.get('id')}")
                return book.get('id')
            else:
                print(f"❌ Erreur création livre MongoDB: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return None
    
    def test_search(self):
        """Tester la recherche"""
        print("\n🔍 Test de la recherche...")
        
        # Test recherche PostgreSQL
        try:
            response = requests.get(f"{self.base_url}/postgres/search/?query=test")
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Recherche PostgreSQL: {len(results)} résultats")
            else:
                print(f"❌ Erreur recherche PostgreSQL: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Test recherche MongoDB
        try:
            response = requests.get(f"{self.base_url}/mongo/search/?query=test")
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Recherche MongoDB: {len(results)} résultats")
            else:
                print(f"❌ Erreur recherche MongoDB: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def test_statistics(self):
        """Tester les statistiques"""
        print("\n📈 Test des statistiques...")
        
        try:
            response = requests.get(f"{self.base_url}/stats/", headers=self.headers)
            if response.status_code == 200:
                stats = response.json()
                print("✅ Statistiques globales:")
                postgres_stats = stats.get('postgres', {})
                mongo_stats = stats.get('mongodb', {})
                
                print(f"   PostgreSQL: {postgres_stats.get('total_books', 0)} livres, {postgres_stats.get('total_users', 0)} utilisateurs")
                if 'error' not in mongo_stats:
                    print(f"   MongoDB: {mongo_stats.get('total_books', 0)} livres")
                else:
                    print(f"   MongoDB: {mongo_stats.get('error', 'Erreur')}")
            else:
                print(f"❌ Erreur statistiques: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def test_authentication(self):
        """Tester l'authentification"""
        print("\n🔐 Test de l'authentification...")
        
        # Test avec clé invalide
        invalid_headers = {
            "Content-Type": "application/json",
            "X-API-Key": "invalid-key"
        }
        
        try:
            response = requests.get(f"{self.base_url}/stats/", headers=invalid_headers)
            if response.status_code == 401:
                print("✅ Authentification: Clé invalide correctement rejetée")
            else:
                print(f"❌ Authentification: Attendu 401, reçu {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Test sans clé
        try:
            response = requests.get(f"{self.base_url}/stats/", headers=self.headers_no_auth)
            if response.status_code == 401:
                print("✅ Authentification: Absence de clé correctement rejetée")
            else:
                print(f"❌ Authentification: Attendu 401, reçu {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🧪 Démarrage des tests de l'API DataBook...")
        print(f"🔗 URL de base: {self.base_url}")
        print(f"🔑 Clé API: {self.api_key}")
        print("="*50)
        
        # Tests de base
        if not self.test_health():
            print("❌ L'API n'est pas accessible. Vérifiez qu'elle est démarrée.")
            return False
        
        # Tests fonctionnels
        self.test_postgres_books()
        self.test_mongo_books()
        self.test_search()
        self.test_statistics()
        self.test_authentication()
        
        print("\n" + "="*50)
        print("✅ Tests terminés!")
        return True

def main():
    """Fonction principale"""
    # Vérifier les arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python test_api.py [--help]")
            print("Test l'API DataBook sur http://localhost:8000")
            return
    
    # Exécuter les tests
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Tous les tests sont terminés!")
        print("📖 Consultez la documentation: http://localhost:8000/docs")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main() 