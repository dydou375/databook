from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
import json

try:
    from database.mongo_crud import mongodb_service
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    mongodb_service = None

from auth.auth import require_api_key

# Router pour les vraies données MongoDB
real_mongo_router = APIRouter(prefix="/mongodb", tags=["Real MongoDB Data"])

async def check_mongodb():
    """Vérifier la disponibilité de MongoDB"""
    if not MONGODB_AVAILABLE:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")
    if mongodb_service is None:
        raise HTTPException(status_code=503, detail="MongoDB service non disponible")
    
    # S'assurer que la connexion async est établie
    if mongodb_service.database is None:
        try:
            await mongodb_service.connect_async()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Impossible de se connecter à MongoDB: {str(e)}")
    
    # Vérifier que la base est accessible
    try:
        await mongodb_service.database.list_collection_names()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB erreur: {str(e)}")

def serialize_mongo_doc(doc):
    """Convertir un document MongoDB en dict JSON-serializable"""
    if doc is None:
        return None
    
    # Convertir ObjectId en string
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    
    # Convertir les dates en ISO string
    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
    
    return doc

@real_mongo_router.get("/health")
async def health_check_mongo():
    """Vérifier l'état de MongoDB"""
    try:
        await check_mongodb()
        
        # Lister les collections
        collections = await mongodb_service.database.list_collection_names()
        
        # Compter les documents dans quelques collections principales
        stats = {}
        for collection_name in collections[:5]:  # Limiter à 5 collections
            count = await mongodb_service.database[collection_name].count_documents({})
            stats[collection_name] = count
        
        return {
            "status": "✅ OK",
            "timestamp": datetime.now(),
            "collections": collections,
            "documents_count": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur MongoDB: {str(e)}")

@real_mongo_router.get("/collections")
async def list_collections():
    """Lister toutes les collections MongoDB"""
    try:
        await check_mongodb()
        collections = await mongodb_service.database.list_collection_names()
        
        collections_info = []
        for collection_name in collections:
            count = await mongodb_service.database[collection_name].count_documents({})
            collections_info.append({
                "name": collection_name,
                "document_count": count
            })
        
        return {
            "success": True,
            "data": collections_info,
            "total": len(collections_info)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@real_mongo_router.get("/collections/{collection_name}")
async def get_collection_data(
    collection_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100)
):
    """Récupérer les données d'une collection spécifique"""
    try:
        await check_mongodb()
        
        collection = mongodb_service.database[collection_name]
        
        # Récupérer les documents
        cursor = collection.find({}).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        # Sérialiser les documents
        serialized_docs = [serialize_mongo_doc(doc) for doc in documents]
        
        # Compter le total
        total_count = await collection.count_documents({})
        
        return {
            "success": True,
            "collection": collection_name,
            "data": serialized_docs,
            "total_in_collection": total_count,
            "returned_count": len(serialized_docs),
            "pagination": {"skip": skip, "limit": limit}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@real_mongo_router.get("/search/{collection_name}")
async def search_in_collection(
    collection_name: str,
    q: str = Query(..., min_length=2),
    field: Optional[str] = Query(None),
    limit: int = Query(20, le=50)
):
    """Rechercher dans une collection MongoDB"""
    try:
        await check_mongodb()
        
        collection = mongodb_service.database[collection_name]
        
        # Construire la requête de recherche
        if field:
            # Recherche dans un champ spécifique
            search_query = {field: {"$regex": q, "$options": "i"}}
        else:
            # Recherche dans tous les champs texte possibles
            search_query = {
                "$or": [
                    {"title": {"$regex": q, "$options": "i"}},
                    {"titre": {"$regex": q, "$options": "i"}},
                    {"name": {"$regex": q, "$options": "i"}},
                    {"nom": {"$regex": q, "$options": "i"}},
                    {"description": {"$regex": q, "$options": "i"}},
                    {"author": {"$regex": q, "$options": "i"}},
                    {"auteur": {"$regex": q, "$options": "i"}},
                    {"text": {"$regex": q, "$options": "i"}},
                    {"content": {"$regex": q, "$options": "i"}}
                ]
            }
        
        cursor = collection.find(search_query).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        # Sérialiser les documents
        serialized_docs = [serialize_mongo_doc(doc) for doc in documents]
        
        return {
            "success": True,
            "collection": collection_name,
            "query": q,
            "field": field,
            "data": serialized_docs,
            "total": len(serialized_docs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@real_mongo_router.get("/document/{collection_name}/{document_id}")
async def get_document(collection_name: str, document_id: str):
    """Récupérer un document spécifique par son ID"""
    try:
        await check_mongodb()
        
        collection = mongodb_service.database[collection_name]
        
        # Essayer de convertir en ObjectId
        try:
            object_id = ObjectId(document_id)
            document = await collection.find_one({"_id": object_id})
        except:
            # Si ce n'est pas un ObjectId valide, chercher par string
            document = await collection.find_one({"_id": document_id})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document non trouvé")
        
        return {
            "success": True,
            "collection": collection_name,
            "data": serialize_mongo_doc(document)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@real_mongo_router.get("/statistics/")
async def get_mongo_real_statistics(api_key: str = Depends(require_api_key)):
    """Statistiques MongoDB des vraies données (nécessite une clé API)"""
    try:
        await check_mongodb()
        
        collections = await mongodb_service.database.list_collection_names()
        
        stats = {
            "total_collections": len(collections),
            "collections_details": {},
            "total_documents": 0
        }
        
        for collection_name in collections:
            count = await mongodb_service.database[collection_name].count_documents({})
            stats["collections_details"][collection_name] = count
            stats["total_documents"] += count
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now(),
            "database": "MongoDB"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@real_mongo_router.get("/sample/{collection_name}")
async def get_collection_sample(
    collection_name: str,
    count: int = Query(3, le=10)
):
    """Récupérer un échantillon de documents pour voir la structure"""
    try:
        await check_mongodb()
        
        collection = mongodb_service.database[collection_name]
        
        # Utiliser aggregate avec $sample pour obtenir des documents aléatoires
        pipeline = [{"$sample": {"size": count}}]
        cursor = collection.aggregate(pipeline)
        documents = await cursor.to_list(length=count)
        
        # Sérialiser les documents
        serialized_docs = [serialize_mongo_doc(doc) for doc in documents]
        
        # Analyser la structure (récupérer les clés)
        all_keys = set()
        for doc in serialized_docs:
            all_keys.update(doc.keys())
        
        return {
            "success": True,
            "collection": collection_name,
            "sample_data": serialized_docs,
            "structure_keys": sorted(list(all_keys)),
            "sample_size": len(serialized_docs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 