#!/usr/bin/env python3
"""
Test des imports après réorganisation
"""

def test_imports():
    """Tester tous les imports principaux"""
    try:
        print("🔍 Test des imports...")
        
        # Test models
        from models.models import User, UserCreate, Item, ItemCreate
        print("✅ models.models OK")
        
        from models.models_mongo import BookMongo, BookMongoCreate
        print("✅ models.models_mongo OK")
        
        # Test database
        from database.database import get_db, init_db
        print("✅ database.database OK")
        
        from database.crud import user_crud, item_crud
        print("✅ database.crud OK")
        
        # Test config
        from config.config import settings
        print("✅ config.config OK")
        
        # Test auth
        from auth.auth import require_api_key
        print("✅ auth.auth OK")
        
        # Test routes
        from routes.routes_postgres import postgres_router
        print("✅ routes.routes_postgres OK")
        
        from routes.routes_mongo import mongo_router
        print("✅ routes.routes_mongo OK")
        
        print("🎉 Tous les imports fonctionnent correctement!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports() 