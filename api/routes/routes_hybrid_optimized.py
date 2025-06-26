from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.database import get_db
from auth.auth import require_jwt, optional_jwt

try:
    from database.mongo_crud import mongodb_service
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    mongodb_service = None

# Router optimisé pour éviter les problèmes de mémoire
hybrid_optimized_router = APIRouter(prefix="/hybrid-lite", tags=["🔀 Hybride Optimisé"])

def serialize_mongo_doc(doc):
    """Convertir un document MongoDB en dict JSON-serializable"""
    if doc is None:
        return None
    
    doc_copy = dict(doc)
    
    # Convertir ObjectId en string
    if '_id' in doc_copy:
        doc_copy['_id'] = str(doc_copy['_id'])
    
    # Convertir les dates en ISO string
    for key, value in doc_copy.items():
        if isinstance(value, datetime):
            doc_copy[key] = value.isoformat()
        elif hasattr(value, '__dict__'):  # ObjectId ou autres objets
            doc_copy[key] = str(value)
    
    return doc_copy

async def check_mongodb():
    """Vérifier la disponibilité de MongoDB"""
    if not MONGODB_AVAILABLE:
        return False
    if mongodb_service is None:
        return False
    
    try:
        if mongodb_service.database is None:
            await mongodb_service.connect_async()
        await mongodb_service.database.list_collection_names()
        return True
    except:
        return False

@hybrid_optimized_router.get("/search-lite")
async def recherche_hybride_optimisee(
    query: str = Query(..., min_length=2, description="Terme de recherche dans les deux bases"),
    limit_postgres: int = Query(5, le=10, description="Limite PostgreSQL (max 10 pour éviter surcharge)"),
    limit_mongo: int = Query(5, le=10, description="Limite MongoDB (max 10)"),
    db: Session = Depends(get_db)
):
    """🔍 Recherche hybride OPTIMISÉE pour éviter les problèmes de mémoire"""
    
    results = {
        "query": query,
        "timestamp": datetime.now(),
        "postgresql": {
            "available": True,
            "data": [],
            "total": 0,
            "error": None
        },
        "mongodb": {
            "available": False,
            "data": [],
            "total": 0,
            "error": None
        },
        "aggregated": {
            "total_combined": 0,
            "postgres_count": 0,
            "mongo_count": 0
        }
    }
    
    # === RECHERCHE POSTGRESQL OPTIMISÉE ===
    try:
        # Requête simplifiée pour réduire la charge mémoire
        postgres_query = text("""
            SELECT 
                l.id_livre,
                l.titre,
                l.isbn_13,
                l.annee_publication,
                l.nombre_pages,
                'PostgreSQL' as source_db
                
            FROM livre l
            
            WHERE 
                l.titre ILIKE :query 
            
            ORDER BY l.titre
            LIMIT :limit
        """)
        
        postgres_result = db.execute(postgres_query, {
            "query": f"%{query}%",
            "limit": limit_postgres
        })
        
        postgres_rows = postgres_result.fetchall()
        results["postgresql"]["data"] = [dict(row._mapping) for row in postgres_rows]
        results["postgresql"]["total"] = len(postgres_rows)
        results["aggregated"]["postgres_count"] = len(postgres_rows)
        
    except Exception as e:
        results["postgresql"]["available"] = False
        results["postgresql"]["error"] = f"Erreur PostgreSQL: {str(e)}"
    
    # === RECHERCHE MONGODB ===
    mongo_available = await check_mongodb()
    results["mongodb"]["available"] = mongo_available
    
    if mongo_available:
        try:
            # Recherche simplifiée MongoDB
            search_query = {
                "titre": {"$regex": query, "$options": "i"}
            }
            
            cursor = mongodb_service.database.livres.find(
                search_query,
                {"titre": 1, "auteurs": 1, "note": 1, "annee_publication": 1}  # Projection pour limiter les données
            ).limit(limit_mongo)
            
            mongo_docs = await cursor.to_list(length=limit_mongo)
            
            # Standardiser les données MongoDB
            mongo_standardized = []
            for doc in mongo_docs:
                standardized = {
                    "id_livre": str(doc.get("_id")),
                    "titre": doc.get("titre"),
                    "auteurs": doc.get("auteurs"),
                    "note_moyenne": doc.get("note"),
                    "annee_publication": doc.get("annee_publication"),
                    "source_db": "MongoDB"
                }
                mongo_standardized.append(standardized)
            
            results["mongodb"]["data"] = mongo_standardized
            results["mongodb"]["total"] = len(mongo_standardized)
            results["aggregated"]["mongo_count"] = len(mongo_standardized)
            
        except Exception as e:
            results["mongodb"]["error"] = f"Erreur MongoDB: {str(e)}"
    
    # === AGRÉGATION FINALE ===
    results["aggregated"]["total_combined"] = (
        results["aggregated"]["postgres_count"] + 
        results["aggregated"]["mongo_count"]
    )
    
    # Combiner les résultats de manière sécurisée
    combined_data = []
    if results["postgresql"]["data"]:
        combined_data.extend(results["postgresql"]["data"])
    if results["mongodb"]["data"]:
        combined_data.extend(results["mongodb"]["data"])
    
    results["combined_results"] = combined_data
    results["optimization_note"] = "Requête optimisée pour éviter les problèmes de mémoire PostgreSQL"
    
    return results

@hybrid_optimized_router.get("/stats-lite")
async def statistiques_simplifiees(
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """📊 Statistiques simplifiées pour éviter la surcharge mémoire"""
    
    stats = {
        "timestamp": datetime.now(),
        "postgresql": {
            "available": True,
            "stats": {},
            "error": None
        },
        "mongodb": {
            "available": False,
            "stats": {},
            "error": None
        }
    }
    
    # === STATS POSTGRESQL SIMPLIFIÉES ===
    try:
        # Requêtes simples une par une pour éviter les JOINs complexes
        simple_queries = {
            "total_livres": "SELECT COUNT(*) as count FROM livre",
            "livres_recents": "SELECT COUNT(*) as count FROM livre WHERE annee_publication >= 2020"
        }
        
        postgres_stats = {}
        for stat_name, query in simple_queries.items():
            result = db.execute(text(query))
            postgres_stats[stat_name] = result.fetchone().count
        
        stats["postgresql"]["stats"] = postgres_stats
        
    except Exception as e:
        stats["postgresql"]["available"] = False
        stats["postgresql"]["error"] = f"Erreur PostgreSQL: {str(e)}"
    
    # === STATS MONGODB ===
    mongo_available = await check_mongodb()
    stats["mongodb"]["available"] = mongo_available
    
    if mongo_available:
        try:
            mongo_stats = {}
            
            # Compter simplement
            mongo_stats["total_livres"] = await mongodb_service.database.livres.count_documents({})
            mongo_stats["total_critiques"] = await mongodb_service.database.critiques_livres.count_documents({})
            
            stats["mongodb"]["stats"] = mongo_stats
            
        except Exception as e:
            stats["mongodb"]["error"] = f"Erreur MongoDB: {str(e)}"
    
    return stats

@hybrid_optimized_router.get("/quick-search")
async def recherche_rapide(
    q: str = Query(..., min_length=2, description="Recherche rapide"),
    source: str = Query("auto", description="Source: postgres, mongo, ou auto"),
    db: Session = Depends(get_db)
):
    """🚀 Recherche ultra-rapide avec choix de source"""
    
    if source == "postgres" or source == "auto":
        try:
            # Requête PostgreSQL ultra-simple
            query = text("SELECT titre, annee_publication FROM livre WHERE titre ILIKE :q LIMIT 5")
            result = db.execute(query, {"q": f"%{q}%"})
            postgres_data = [dict(row._mapping) for row in result.fetchall()]
            
            if source == "postgres":
                return {
                    "source": "PostgreSQL",
                    "data": postgres_data,
                    "count": len(postgres_data)
                }
        except Exception as e:
            postgres_data = []
            postgres_error = str(e)
    
    if source == "mongo" or source == "auto":
        mongo_available = await check_mongodb()
        if mongo_available:
            try:
                # Recherche MongoDB simple
                cursor = mongodb_service.database.livres.find(
                    {"titre": {"$regex": q, "$options": "i"}},
                    {"titre": 1, "auteurs": 1}
                ).limit(5)
                
                mongo_docs = await cursor.to_list(length=5)
                mongo_data = [serialize_mongo_doc(doc) for doc in mongo_docs]
                
                if source == "mongo":
                    return {
                        "source": "MongoDB",
                        "data": mongo_data,
                        "count": len(mongo_data)
                    }
            except Exception as e:
                mongo_data = []
                mongo_error = str(e)
    
    # Retour combiné pour source "auto"
    combined = []
    if 'postgres_data' in locals():
        for item in postgres_data:
            item['source'] = 'PostgreSQL'
            combined.append(item)
    if 'mongo_data' in locals():
        for item in mongo_data:
            item['source'] = 'MongoDB'
            combined.append(item)
    
    return {
        "source": "Combiné",
        "data": combined,
        "count": len(combined),
        "note": "Recherche optimisée - limites réduites pour éviter surcharge mémoire"
    }