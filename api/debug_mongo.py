"""
Debug MongoDB step by step
"""
import asyncio
from database.mongo_crud import mongodb_service

async def debug_mongo_step_by_step():
    print("🔍 Debug MongoDB étape par étape...")
    
    print(f"1. MONGODB_AVAILABLE: MongoDB service importé")
    print(f"2. mongodb_service exists: {mongodb_service is not None}")
    
    if mongodb_service:
        print(f"3. mongodb_service.async_client: {mongodb_service.async_client}")
        print(f"4. mongodb_service.database: {mongodb_service.database}")
        
        # Test connexion
        try:
            await mongodb_service.connect_async()
            print("5. ✅ connect_async() réussi")
        except Exception as e:
            print(f"5. ❌ connect_async() erreur: {e}")
            return
        
        print(f"6. Après connexion - async_client: {mongodb_service.async_client}")
        print(f"7. Après connexion - database: {mongodb_service.database}")
        
        # Test vérification problématique
        try:
            result = bool(mongodb_service.database)
            print(f"8. ❌ bool(database) causa l'erreur: {result}")
        except Exception as e:
            print(f"8. ❌ bool(database) erreur: {e}")
        
        try:
            result = (mongodb_service.database is None)
            print(f"9. ✅ database is None: {result}")
        except Exception as e:
            print(f"9. ❌ database is None erreur: {e}")
        
        # Test comptage
        try:
            count = await mongodb_service.database.livres.count_documents({})
            print(f"10. ✅ Count livres: {count}")
        except Exception as e:
            print(f"10. ❌ Count erreur: {e}")

if __name__ == "__main__":
    asyncio.run(debug_mongo_step_by_step()) 