from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

try:
    from database.mongo_crud import mongodb_service
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    mongodb_service = None

# Router pour les fonctionnalités avancées MongoDB
mongo_extras_router = APIRouter(prefix="/mongo-extras", tags=["MongoDB - Fonctionnalités avancées"])

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

# ❌ Page d'accueil supprimée - info incluse dans GET / principal

@mongo_extras_router.get("/genres")
async def lister_genres():
    """📑 Lister tous les genres disponibles avec leur nombre de livres"""
    try:
        await check_mongodb()
        
        pipeline = [
            {"$unwind": "$tous_les_genres"},
            {"$group": {"_id": "$tous_les_genres", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        genres = await mongodb_service.database.livres.aggregate(pipeline).to_list(length=None)
        
        return {
            "success": True,
            "data": genres,
            "total_genres": len(genres)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_extras_router.get("/auteurs")
async def lister_auteurs():
    """✍️ Lister tous les auteurs avec leur nombre de livres"""
    try:
        await check_mongodb()
        
        pipeline = [
            {"$unwind": "$auteurs"},
            {"$group": {"_id": "$auteurs", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        auteurs = await mongodb_service.database.livres.aggregate(pipeline).to_list(length=None)
        
        return {
            "success": True,
            "data": auteurs,
            "total_auteurs": len(auteurs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_extras_router.get("/livres/genre/{genre}")
async def livres_par_genre(
    genre: str,
    limit: int = Query(20, le=100)
):
    """📚 Récupérer les livres d'un genre spécifique"""
    try:
        await check_mongodb()
        
        cursor = mongodb_service.database.livres.find({
            "tous_les_genres": genre
        }).limit(limit)
        
        livres = await cursor.to_list(length=limit)
        total = await mongodb_service.database.livres.count_documents({"tous_les_genres": genre})
        
        return {
            "success": True,
            "genre": genre,
            "data": [serialize_mongo_doc(livre) for livre in livres],
            "total_genre": total,
            "returned": len(livres)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_extras_router.get("/livres/auteur/{auteur}")
async def livres_par_auteur(
    auteur: str,
    limit: int = Query(20, le=100)
):
    """📖 Récupérer les livres d'un auteur spécifique"""
    try:
        await check_mongodb()
        
        cursor = mongodb_service.database.livres.find({
            "auteurs": auteur
        }).limit(limit)
        
        livres = await cursor.to_list(length=limit)
        total = await mongodb_service.database.livres.count_documents({"auteurs": auteur})
        
        return {
            "success": True,
            "auteur": auteur,
            "data": [serialize_mongo_doc(livre) for livre in livres],
            "total_auteur": total,
            "returned": len(livres)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_extras_router.get("/livres/top-notes")
async def livres_mieux_notes(limit: int = Query(10, le=50)):
    """⭐ Récupérer les livres les mieux notés"""
    try:
        await check_mongodb()
        
        cursor = mongodb_service.database.livres.find({
            "note": {"$type": "number", "$gte": 1}
        }).sort("note", -1).limit(limit)
        
        livres = await cursor.to_list(length=limit)
        
        return {
            "success": True,
            "data": [serialize_mongo_doc(livre) for livre in livres],
            "total": len(livres)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_extras_router.get("/critiques/top-notes")
async def critiques_mieux_notees(limit: int = Query(10, le=50)):
    """⭐ Récupérer les critiques avec les meilleures notes Babelio"""
    try:
        await check_mongodb()
        
        cursor = mongodb_service.database.critiques_livres.find({
            "note_babelio": {"$type": "number", "$gte": 1}
        }).sort("note_babelio", -1).limit(limit)
        
        critiques = await cursor.to_list(length=limit)
        
        return {
            "success": True,
            "data": [serialize_mongo_doc(critique) for critique in critiques],
            "total": len(critiques)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_extras_router.get("/analytics")
async def analytics_avances():
    """📊 Analytics avancés de vos données MongoDB"""
    try:
        await check_mongodb()
        
        # Répartition par langue
        pipeline_langues = [
            {"$group": {"_id": "$langue", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        langues = await mongodb_service.database.livres.aggregate(pipeline_langues).to_list(length=None)
        
        # Répartition des notes des livres
        pipeline_notes_livres = [
            {"$match": {"note": {"$type": "number"}}},
            {"$group": {"_id": "$note", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        notes_livres = await mongodb_service.database.livres.aggregate(pipeline_notes_livres).to_list(length=None)
        
        # Statistiques des critiques Babelio
        pipeline_stats_critiques = [
            {"$match": {"note_babelio": {"$type": "number"}}},
            {"$group": {
                "_id": None,
                "min_note": {"$min": "$note_babelio"},
                "max_note": {"$max": "$note_babelio"},
                "avg_note": {"$avg": "$note_babelio"},
                "total_votes": {"$sum": "$nombre_votes_babelio"}
            }}
        ]
        stats_critiques = await mongodb_service.database.critiques_livres.aggregate(pipeline_stats_critiques).to_list(length=1)
        
        # Top genres par nombre de livres
        pipeline_top_genres = [
            {"$unwind": "$tous_les_genres"},
            {"$group": {"_id": "$tous_les_genres", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_genres = await mongodb_service.database.livres.aggregate(pipeline_top_genres).to_list(length=10)
        
        # Livres récents (par date d'import)
        livres_recents = []
        try:
            cursor = mongodb_service.database.livres.find({}).sort("_import_date", -1).limit(5)
            livres_recents = await cursor.to_list(length=5)
        except:
            pass
        
        return {
            "success": True,
            "timestamp": datetime.now(),
            "analytics": {
                "repartition_langues": langues,
                "repartition_notes_livres": notes_livres,
                "stats_critiques_babelio": stats_critiques[0] if stats_critiques else {},
                "top_genres": top_genres,
                "livres_recents": [serialize_mongo_doc(livre) for livre in livres_recents]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mongo_extras_router.get("/recherche-avancee")
async def recherche_avancee(
    titre: Optional[str] = Query(None),
    auteur: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    langue: Optional[str] = Query(None),
    note_min: Optional[float] = Query(None, ge=0, le=5),
    note_max: Optional[float] = Query(None, ge=0, le=5),
    limit: int = Query(20, le=100)
):
    """🔍 Recherche avancée avec filtres multiples"""
    try:
        await check_mongodb()
        
        # Construire la requête
        query = {}
        
        if titre:
            query["titre"] = {"$regex": titre, "$options": "i"}
        if auteur:
            query["auteurs"] = {"$regex": auteur, "$options": "i"}
        if genre:
            query["tous_les_genres"] = genre
        if langue:
            query["langue"] = langue
        if note_min is not None or note_max is not None:
            note_query = {}
            if note_min is not None:
                note_query["$gte"] = note_min
            if note_max is not None:
                note_query["$lte"] = note_max
            query["note"] = note_query
        
        # Exécuter la recherche
        cursor = mongodb_service.database.livres.find(query).limit(limit)
        livres = await cursor.to_list(length=limit)
        total = await mongodb_service.database.livres.count_documents(query)
        
        return {
            "success": True,
            "filtres_appliques": query,
            "data": [serialize_mongo_doc(livre) for livre in livres],
            "total_correspondant": total,
            "returned": len(livres)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 