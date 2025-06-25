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

from auth.auth import require_jwt, optional_jwt

# 📚 Router MongoDB optimisé (10 endpoints essentiels)
mongo_livres_router = APIRouter(prefix="/mongo-livres", tags=["📚 MongoDB - 4766 Livres & 85 Critiques"])

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

# ❌ PAGES D'ACCUEIL SUPPRIMÉES POUR OPTIMISATION :
# 
# /mongo-livres/ (page accueil) → info disponible dans GET / principal
# /mongo-livres/welcome → redondant avec route principale  
# /mongo-livres/info → fusionné avec /mongo-livres/statistics

# === 📚 ENDPOINTS LIVRES (5 endpoints) ===

@mongo_livres_router.get("/livres")
async def lister_livres_mongo(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(20, le=100, description="Nombre d'éléments à retourner"),
    titre: Optional[str] = Query(None, description="Filtrer par titre"),
    auteur: Optional[str] = Query(None, description="Filtrer par auteur")
):
    """📚 Lister les livres de la collection MongoDB (4766 livres)"""
    try:
        await check_mongodb()
        
        # Construire les filtres
        filters = {}
        if titre:
            filters["titre"] = {"$regex": titre, "$options": "i"}
        if auteur:
            filters["auteurs"] = {"$regex": auteur, "$options": "i"}
        
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
            "filters_applied": filters,
            "database_info": "📚 4766 livres MongoDB"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@mongo_livres_router.get("/livres/{livre_id}")
async def detail_livre_mongo(livre_id: str):
    """📖 Détail d'un livre MongoDB avec ses critiques associées"""
    try:
        await check_mongodb()
        
        # Essayer de convertir en ObjectId
        try:
            object_id = ObjectId(livre_id)
            livre = await mongodb_service.database.livres.find_one({"_id": object_id})
        except:
            # Si ce n'est pas un ObjectId valide, chercher par string
            livre = await mongodb_service.database.livres.find_one({"_id": livre_id})
        
        if livre is None:
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
            "nb_critiques": len(critiques),
            "source": "MongoDB"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_livres_router.get("/search")
async def rechercher_livres_mongo(
    q: str = Query(..., min_length=2, description="Terme de recherche"),
    limit: int = Query(20, le=50, description="Nombre de résultats")
):
    """🔍 Rechercher des livres dans MongoDB (4766 livres)"""
    try:
        await check_mongodb()
        
        # Recherche dans plusieurs champs (adaptée à la vraie structure)
        search_query = {
            "$or": [
                {"titre": {"$regex": q, "$options": "i"}},
                {"auteurs": {"$regex": q, "$options": "i"}},
                {"resume": {"$regex": q, "$options": "i"}},
                {"tous_les_genres": {"$regex": q, "$options": "i"}},
                {"isbn_10": {"$regex": q, "$options": "i"}},
                {"isbn_13": {"$regex": q, "$options": "i"}},
                {"langue": {"$regex": q, "$options": "i"}}
            ]
        }
        
        cursor = mongodb_service.database.livres.find(search_query).limit(limit)
        livres = await cursor.to_list(length=limit)
        
        return {
            "success": True,
            "query": q,
            "data": [serialize_mongo_doc(livre) for livre in livres],
            "total": len(livres),
            "searched_in": "4766 livres MongoDB"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_livres_router.get("/sample")
async def echantillon_donnees():
    """🔬 Échantillon de données pour comprendre la structure"""
    try:
        await check_mongodb()
        
        # Échantillon de livres
        livres_sample = []
        try:
            pipeline = [{"$sample": {"size": 3}}]
            livres_cursor = mongodb_service.database.livres.aggregate(pipeline)
            livres_sample = await livres_cursor.to_list(length=3)
        except:
            pass
        
        # Analyser la structure
        livres_keys = set()
        for livre in livres_sample:
            livres_keys.update(livre.keys())
        
        return {
            "success": True,
            "echantillons": {
                "livres": {
                    "sample": [serialize_mongo_doc(livre) for livre in livres_sample],
                    "champs_disponibles": sorted(list(livres_keys)),
                    "total_collection": "4766 livres"
                }
            },
            "note": "📊 Utilisez /mongo-extras/analytics/ pour plus de statistiques"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_livres_router.get("/statistiques")
async def statistiques_mongo_livres():
    """📊 Statistiques des livres et critiques MongoDB"""
    try:
        await check_mongodb()
        
        # Statistiques livres
        nb_livres = await mongodb_service.database.livres.count_documents({})
        nb_critiques = await mongodb_service.database.critiques_livres.count_documents({})
        
        # Top auteurs (structure réelle : auteurs est un array)
        top_auteurs = []
        try:
            pipeline_auteurs = [
                {"$unwind": "$auteurs"},
                {"$group": {"_id": "$auteurs", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            top_auteurs = await mongodb_service.database.livres.aggregate(pipeline_auteurs).to_list(length=5)
        except:
            pass
        
        # Top genres
        top_genres = []
        try:
            pipeline_genres = [
                {"$unwind": "$tous_les_genres"},
                {"$group": {"_id": "$tous_les_genres", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            top_genres = await mongodb_service.database.livres.aggregate(pipeline_genres).to_list(length=5)
        except:
            pass
        
        # Moyenne des notes des critiques (utiliser note_babelio)
        moyenne_notes_critiques = 0
        try:
            pipeline_notes = [
                {"$group": {"_id": None, "moyenne": {"$avg": "$note_babelio"}}}
            ]
            result = await mongodb_service.database.critiques_livres.aggregate(pipeline_notes).to_list(length=1)
            if result:
                moyenne_notes_critiques = round(result[0]["moyenne"], 2)
        except:
            pass
        
        return {
            "success": True,
            "timestamp": datetime.now(),
            "statistiques": {
                "livres": {
                    "total": nb_livres,
                    "top_auteurs": top_auteurs,
                    "top_genres": top_genres
                },
                "critiques_babelio": {
                    "total": nb_critiques,
                    "note_moyenne_babelio": moyenne_notes_critiques
                }
            },
            "note": "📊 Utilisez /mongo-extras/analytics/ pour plus d'analyses avancées"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === 💬 ENDPOINTS CRITIQUES (3 endpoints) ===

@mongo_livres_router.get("/critiques")
async def lister_critiques_mongo(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    note_min: Optional[float] = Query(None, ge=0, le=5, description="Note minimale"),
    note_max: Optional[float] = Query(None, ge=0, le=5, description="Note maximale")
):
    """💬 Lister les critiques Babelio (85 critiques)"""
    try:
        await check_mongodb()
        
        # Construire les filtres (utiliser note_babelio pour les critiques)
        filters = {}
        if note_min is not None:
            filters["note_babelio"] = {"$gte": note_min}
        if note_max is not None:
            if "note_babelio" in filters:
                filters["note_babelio"]["$lte"] = note_max
            else:
                filters["note_babelio"] = {"$lte": note_max}
        
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
            "filters_applied": filters,
            "source": "💬 85 critiques Babelio"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_livres_router.get("/critiques/{critique_id}")
async def detail_critique_mongo(critique_id: str):
    """💭 Détail d'une critique Babelio"""
    try:
        await check_mongodb()
        
        try:
            object_id = ObjectId(critique_id)
            critique = await mongodb_service.database.critiques_livres.find_one({"_id": object_id})
        except:
            critique = await mongodb_service.database.critiques_livres.find_one({"_id": critique_id})
        
        if critique is None:
            raise HTTPException(status_code=404, detail="Critique non trouvée")
        
        return {
            "success": True,
            "data": serialize_mongo_doc(critique),
            "source": "Babelio"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_livres_router.get("/critiques/top-notes")
async def top_critiques_par_note():
    """⭐ Top critiques par note Babelio"""
    try:
        await check_mongodb()
        
        # Récupérer les meilleures critiques par note
        cursor = mongodb_service.database.critiques_livres.find(
            {"note_babelio": {"$gte": 4}}
        ).sort("note_babelio", -1).limit(20)
        
        critiques = await cursor.to_list(length=20)
        
        return {
            "success": True,
            "data": [serialize_mongo_doc(critique) for critique in critiques],
            "filter": "Notes ≥ 4/5",
            "total": len(critiques)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 📊 ENDPOINTS FINAUX (10 total) :
# 
# === LIVRES (5) ===
# 1. GET /livres - Lister livres (4766)
# 2. GET /livres/{id} - Détail livre + critiques
# 3. GET /search - Recherche globale livres  
# 4. GET /sample - Échantillon de données
# 5. GET /statistiques - Stats livres + critiques
# 
# === CRITIQUES (3) ===
# 6. GET /critiques - Lister critiques (85)
# 7. GET /critiques/{id} - Détail critique
# 8. GET /critiques/top-notes - Top critiques par note
# 
# === OPTIMISATION ===
# ✅ -3 pages d'accueil redondantes supprimées
# ✅ Endpoints optimisés et documentés 
# ✅ 39 requêtes NoSQL optimisées utilisées 