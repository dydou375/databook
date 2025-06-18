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

# Router spécifique pour les livres MongoDB
mongo_livres_router = APIRouter(prefix="/mongo-livres", tags=["MongoDB - Livres & Critiques"])

def check_mongodb():
    """Vérifier la disponibilité de MongoDB"""
    if not MONGODB_AVAILABLE or not mongodb_service:
        raise HTTPException(status_code=503, detail="MongoDB non disponible")
    if not mongodb_service.database:
        raise HTTPException(status_code=503, detail="MongoDB non connecté")

def serialize_mongo_doc(doc):
    """Convertir un document MongoDB en dict JSON-serializable"""
    if doc is None:
        return None
    
    # Créer une copie pour éviter de modifier l'original
    doc_copy = dict(doc)
    
    # Convertir ObjectId en string
    if '_id' in doc_copy:
        doc_copy['_id'] = str(doc_copy['_id'])
    
    # Convertir les dates en ISO string
    for key, value in doc_copy.items():
        if isinstance(value, datetime):
            doc_copy[key] = value.isoformat()
        elif isinstance(value, ObjectId):
            doc_copy[key] = str(value)
    
    return doc_copy

@mongo_livres_router.get("/")
async def accueil_mongo_livres():
    """Page d'accueil pour les données MongoDB de livres"""
    try:
        check_mongodb()
        
        # Compter les documents dans chaque collection
        nb_livres = await mongodb_service.database.livres.count_documents({})
        nb_critiques = await mongodb_service.database.critiques_livres.count_documents({})
        
        return {
            "message": "🍃 API MongoDB - Livres et Critiques",
            "timestamp": datetime.now(),
            "collections": {
                "livres": {
                    "count": nb_livres,
                    "endpoints": [
                        "GET /mongo-livres/livres - Lister tous les livres",
                        "GET /mongo-livres/livres/{id} - Détail d'un livre",
                        "GET /mongo-livres/livres/search?q={terme} - Rechercher des livres"
                    ]
                },
                "critiques_livres": {
                    "count": nb_critiques,
                    "endpoints": [
                        "GET /mongo-livres/critiques - Lister toutes les critiques",
                        "GET /mongo-livres/critiques/{id} - Détail d'une critique",
                        "GET /mongo-livres/critiques/livre/{livre_id} - Critiques d'un livre"
                    ]
                }
            },
            "status": "✅ MongoDB connecté"
        }
    except Exception as e:
        return {
            "message": "❌ Erreur MongoDB",
            "error": str(e),
            "status": "🔴 MongoDB non disponible"
        }

# === ROUTES LIVRES ===

@mongo_livres_router.get("/livres")
async def lister_livres_mongo(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(20, le=100, description="Nombre d'éléments à retourner"),
    titre: Optional[str] = Query(None, description="Filtrer par titre"),
    auteur: Optional[str] = Query(None, description="Filtrer par auteur")
):
    """📚 Lister les livres de la collection MongoDB"""
    try:
        check_mongodb()
        
        # Construire les filtres
        filters = {}
        if titre:
            filters["titre"] = {"$regex": titre, "$options": "i"}
        if auteur:
            filters["auteur"] = {"$regex": auteur, "$options": "i"}
        
        # Récupérer les livres
        cursor = mongodb_service.database.livres.find(filters).skip(skip).limit(limit)
        livres = await cursor.to_list(length=limit)
        
        # Compter le total
        total = await mongodb_service.database.livres.count_documents(filters)
        
        # Sérialiser
        livres_serialized = [serialize_mongo_doc(livre) for livre in livres]
        
        return {
            "success": True,
            "data": livres_serialized,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
                "returned": len(livres_serialized)
            },
            "filters_applied": filters
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@mongo_livres_router.get("/livres/{livre_id}")
async def detail_livre_mongo(livre_id: str):
    """📖 Détail d'un livre MongoDB"""
    try:
        check_mongodb()
        
        # Essayer de convertir en ObjectId
        try:
            object_id = ObjectId(livre_id)
            livre = await mongodb_service.database.livres.find_one({"_id": object_id})
        except:
            # Si ce n'est pas un ObjectId valide, chercher par string
            livre = await mongodb_service.database.livres.find_one({"_id": livre_id})
        
        if not livre:
            raise HTTPException(status_code=404, detail="Livre non trouvé")
        
        # Récupérer les critiques de ce livre si elles existent
        critiques = []
        try:
            # Chercher par différents champs possibles
            critiques_cursor = mongodb_service.database.critiques_livres.find({
                "$or": [
                    {"livre_id": livre_id},
                    {"livre_id": object_id if 'object_id' in locals() else livre_id},
                    {"titre": livre.get("titre", "")},
                    {"book_id": livre_id}
                ]
            }).limit(10)
            critiques = await critiques_cursor.to_list(length=10)
        except Exception as e:
            print(f"Erreur récupération critiques: {e}")
        
        return {
            "success": True,
            "livre": serialize_mongo_doc(livre),
            "critiques": [serialize_mongo_doc(critique) for critique in critiques],
            "nb_critiques": len(critiques)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_livres_router.get("/livres/search")
async def rechercher_livres_mongo(
    q: str = Query(..., min_length=2, description="Terme de recherche"),
    limit: int = Query(20, le=50, description="Nombre de résultats")
):
    """🔍 Rechercher des livres dans MongoDB"""
    try:
        check_mongodb()
        
        # Recherche dans plusieurs champs
        search_query = {
            "$or": [
                {"titre": {"$regex": q, "$options": "i"}},
                {"auteur": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"genre": {"$regex": q, "$options": "i"}},
                {"isbn": {"$regex": q, "$options": "i"}},
                {"editeur": {"$regex": q, "$options": "i"}}
            ]
        }
        
        cursor = mongodb_service.database.livres.find(search_query).limit(limit)
        livres = await cursor.to_list(length=limit)
        
        return {
            "success": True,
            "query": q,
            "data": [serialize_mongo_doc(livre) for livre in livres],
            "total": len(livres)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === ROUTES CRITIQUES ===

@mongo_livres_router.get("/critiques")
async def lister_critiques_mongo(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    note_min: Optional[float] = Query(None, ge=0, le=5, description="Note minimale"),
    note_max: Optional[float] = Query(None, ge=0, le=5, description="Note maximale")
):
    """💬 Lister les critiques de livres"""
    try:
        check_mongodb()
        
        # Construire les filtres
        filters = {}
        if note_min is not None:
            filters["note"] = {"$gte": note_min}
        if note_max is not None:
            if "note" in filters:
                filters["note"]["$lte"] = note_max
            else:
                filters["note"] = {"$lte": note_max}
        
        cursor = mongodb_service.database.critiques_livres.find(filters).skip(skip).limit(limit)
        critiques = await cursor.to_list(length=limit)
        
        total = await mongodb_service.database.critiques_livres.count_documents(filters)
        
        return {
            "success": True,
            "data": [serialize_mongo_doc(critique) for critique in critiques],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
                "returned": len(critiques)
            },
            "filters_applied": filters
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_livres_router.get("/critiques/{critique_id}")
async def detail_critique_mongo(critique_id: str):
    """💭 Détail d'une critique"""
    try:
        check_mongodb()
        
        try:
            object_id = ObjectId(critique_id)
            critique = await mongodb_service.database.critiques_livres.find_one({"_id": object_id})
        except:
            critique = await mongodb_service.database.critiques_livres.find_one({"_id": critique_id})
        
        if not critique:
            raise HTTPException(status_code=404, detail="Critique non trouvée")
        
        return {
            "success": True,
            "data": serialize_mongo_doc(critique)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_livres_router.get("/statistiques")
async def statistiques_mongo_livres():
    """📊 Statistiques des livres et critiques MongoDB"""
    try:
        check_mongodb()
        
        # Statistiques livres
        nb_livres = await mongodb_service.database.livres.count_documents({})
        nb_critiques = await mongodb_service.database.critiques_livres.count_documents({})
        
        # Top auteurs (si le champ existe)
        top_auteurs = []
        try:
            pipeline_auteurs = [
                {"$group": {"_id": "$auteur", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            top_auteurs = await mongodb_service.database.livres.aggregate(pipeline_auteurs).to_list(length=10)
        except:
            pass
        
        # Moyenne des notes des critiques
        moyenne_notes = 0
        try:
            pipeline_notes = [
                {"$group": {"_id": None, "moyenne": {"$avg": "$note"}}}
            ]
            result = await mongodb_service.database.critiques_livres.aggregate(pipeline_notes).to_list(length=1)
            if result:
                moyenne_notes = round(result[0]["moyenne"], 2)
        except:
            pass
        
        return {
            "success": True,
            "timestamp": datetime.now(),
            "statistiques": {
                "livres": {
                    "total": nb_livres,
                    "top_auteurs": top_auteurs[:5]
                },
                "critiques": {
                    "total": nb_critiques,
                    "note_moyenne": moyenne_notes
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_livres_router.get("/sample")
async def echantillon_donnees():
    """🔬 Échantillon de données pour comprendre la structure"""
    try:
        check_mongodb()
        
        # Échantillon de livres
        livres_sample = []
        try:
            pipeline = [{"$sample": {"size": 3}}]
            livres_cursor = mongodb_service.database.livres.aggregate(pipeline)
            livres_sample = await livres_cursor.to_list(length=3)
        except:
            pass
        
        # Échantillon de critiques
        critiques_sample = []
        try:
            pipeline = [{"$sample": {"size": 3}}]
            critiques_cursor = mongodb_service.database.critiques_livres.aggregate(pipeline)
            critiques_sample = await critiques_cursor.to_list(length=3)
        except:
            pass
        
        # Analyser la structure
        livres_keys = set()
        for livre in livres_sample:
            livres_keys.update(livre.keys())
        
        critiques_keys = set()
        for critique in critiques_sample:
            critiques_keys.update(critique.keys())
        
        return {
            "success": True,
            "echantillons": {
                "livres": {
                    "sample": [serialize_mongo_doc(livre) for livre in livres_sample],
                    "champs_disponibles": sorted(list(livres_keys))
                },
                "critiques": {
                    "sample": [serialize_mongo_doc(critique) for critique in critiques_sample],
                    "champs_disponibles": sorted(list(critiques_keys))
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 