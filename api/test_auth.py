"""
Script de test pour vérifier l'authentification
"""

from config.config import settings
import requests

def test_api_key():
    """Tester la clé API actuelle"""
    print("🔍 Test de la clé API")
    print("=" * 50)
    
    # Afficher la clé configurée
    print(f"🔑 Clé API configurée: '{settings.api_key}'")
    print(f"🔧 Type: {type(settings.api_key)}")
    print(f"📏 Longueur: {len(settings.api_key)}")
    
    # Test sans clé
    print("\n1️⃣ Test sans clé API:")
    try:
        response = requests.get("http://localhost:8000/livres/test/connection", timeout=5)
        print(f"   ✅ Route publique: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test avec clé
    print("\n2️⃣ Test avec clé API:")
    headers = {"X-API-Key": settings.api_key}
    try:
        response = requests.get("http://localhost:8000/livres/stats/", headers=headers, timeout=5)
        print(f"   📊 Route protégée: {response.status_code}")
        if response.status_code != 200:
            print(f"   📄 Réponse: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test avec différentes variantes
    print("\n3️⃣ Test variantes de clé:")
    test_keys = [
        "your-api-key-change-this",
        "your-api-key-change-this ",  # avec espace
        " your-api-key-change-this",  # avec espace au début
        "YOUR-API-KEY-CHANGE-THIS",   # majuscules
    ]
    
    for key in test_keys:
        headers = {"X-API-Key": key}
        try:
            response = requests.get("http://localhost:8000/livres/stats/", headers=headers, timeout=3)
            print(f"   🔑 '{key}' -> {response.status_code}")
        except Exception as e:
            print(f"   ❌ '{key}' -> Erreur: {e}")

if __name__ == "__main__":
    test_api_key() 