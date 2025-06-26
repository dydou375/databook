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

# Router pour les requêtes hybrides PostgreSQL + MongoDB
hybrid_router = APIRouter(prefix="/hybrid", tags=["🔀 Hybride - PostgreSQL + MongoDB"])

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

@hybrid_router.get("/search")
async def recherche_hybride(
    query: str = Query(..., min_length=2, description="Terme de recherche dans les deux bases"),
    limit_postgres: int = Query(10, le=50, description="Limite résultats PostgreSQL"),
    limit_mongo: int = Query(10, le=50, description="Limite résultats MongoDB"),
    db: Session = Depends(get_db)
):
    """🔍 Rechercher dans les DEUX bases de données et agréger les résultats"""
    
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
    
    # === RECHERCHE POSTGRESQL (VERSION ALLÉGÉE) ===
    try:
        # Requête simplifiée pour éviter les problèmes de mémoire
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
        results["postgresql"]["error"] = str(e)
    
    # === RECHERCHE MONGODB ===
    mongo_available = await check_mongodb()
    results["mongodb"]["available"] = mongo_available
    
    if mongo_available:
        try:
            # Recherche dans plusieurs champs MongoDB
            search_query = {
                "$or": [
                    {"titre": {"$regex": query, "$options": "i"}},
                    {"auteurs": {"$regex": query, "$options": "i"}},
                    {"resume": {"$regex": query, "$options": "i"}},
                    {"tous_les_genres": {"$regex": query, "$options": "i"}},
                    {"editeur": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = mongodb_service.database.livres.find(search_query).limit(limit_mongo)
            mongo_docs = await cursor.to_list(length=limit_mongo)
            
            # Standardiser les données MongoDB pour l'agrégation
            mongo_standardized = []
            for doc in mongo_docs:
                standardized = {
                    "id_livre": str(doc.get("_id")),
                    "titre": doc.get("titre"),
                    "sous_titre": doc.get("sous_titre"),
                    "isbn_10": doc.get("isbn_10"),
                    "isbn_13": doc.get("isbn_13"),
                    "description": doc.get("resume"),
                    "annee_publication": doc.get("annee_publication"),
                    "nombre_pages": doc.get("nb_pages"),
                    "auteur_nom_complet": doc.get("auteurs"),
                    "editeur_nom": doc.get("editeur"),
                    "langue_nom": doc.get("langue"),
                    "source_db": "MongoDB",
                    "genres": doc.get("tous_les_genres"),
                    "note_moyenne": doc.get("note")
                }
                mongo_standardized.append(standardized)
            
            results["mongodb"]["data"] = mongo_standardized
            results["mongodb"]["total"] = len(mongo_standardized)
            results["aggregated"]["mongo_count"] = len(mongo_standardized)
            
        except Exception as e:
            results["mongodb"]["error"] = str(e)
    
    # === AGRÉGATION FINALE ===
    results["aggregated"]["total_combined"] = (
        results["aggregated"]["postgres_count"] + 
        results["aggregated"]["mongo_count"]
    )
    
    # Combiner les résultats pour une vue unifiée
    combined_data = []
    combined_data.extend(results["postgresql"]["data"])
    combined_data.extend(results["mongodb"]["data"])
    
    results["combined_results"] = combined_data
    
    return results

@hybrid_router.get("/stats-aggregees")
async def statistiques_aggregees(
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """📊 Statistiques agrégées des deux bases de données"""
    
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
        },
        "combined_stats": {}
    }
    
    # === STATS POSTGRESQL ===
    try:
        postgres_queries = {
            "total_livres": "SELECT COUNT(*) as count FROM livre",
            "total_auteurs": "SELECT COUNT(DISTINCT id_auteur) as count FROM auteur",
            "total_editeurs": "SELECT COUNT(DISTINCT id_editeur) as count FROM editeur",
            "total_langues": "SELECT COUNT(DISTINCT id_langue) as count FROM langue"
        }
        
        postgres_stats = {}
        for stat_name, query in postgres_queries.items():
            result = db.execute(text(query))
            postgres_stats[stat_name] = result.fetchone().count
        
        stats["postgresql"]["stats"] = postgres_stats
        
    except Exception as e:
        stats["postgresql"]["available"] = False
        stats["postgresql"]["error"] = str(e)
    
    # === STATS MONGODB ===
    mongo_available = await check_mongodb()
    stats["mongodb"]["available"] = mongo_available
    
    if mongo_available:
        try:
            mongo_stats = {}
            
            # Compter les documents
            mongo_stats["total_livres"] = await mongodb_service.database.livres.count_documents({})
            mongo_stats["total_critiques"] = await mongodb_service.database.critiques_livres.count_documents({})
            
            # Statistiques agrégées
            pipeline_auteurs = [
                {"$group": {"_id": "$auteurs"}},
                {"$count": "total"}
            ]
            auteurs_result = await mongodb_service.database.livres.aggregate(pipeline_auteurs).to_list(None)
            mongo_stats["total_auteurs_uniques"] = auteurs_result[0]["total"] if auteurs_result else 0
            
            pipeline_editeurs = [
                {"$group": {"_id": "$editeur"}},
                {"$count": "total"}
            ]
            editeurs_result = await mongodb_service.database.livres.aggregate(pipeline_editeurs).to_list(None)
            mongo_stats["total_editeurs_uniques"] = editeurs_result[0]["total"] if editeurs_result else 0
            
            stats["mongodb"]["stats"] = mongo_stats
            
        except Exception as e:
            stats["mongodb"]["error"] = str(e)
    
    # === AGRÉGATION FINALE ===
    if stats["postgresql"]["available"] and stats["mongodb"]["available"]:
        postgres_livres = stats["postgresql"]["stats"].get("total_livres", 0)
        mongo_livres = stats["mongodb"]["stats"].get("total_livres", 0)
        
        stats["combined_stats"] = {
            "total_livres_global": postgres_livres + mongo_livres,
            "postgresql_livres": postgres_livres,
            "mongodb_livres": mongo_livres,
            "proportion_postgres": f"{(postgres_livres / (postgres_livres + mongo_livres) * 100):.1f}%" if (postgres_livres + mongo_livres) > 0 else "0%",
            "proportion_mongo": f"{(mongo_livres / (postgres_livres + mongo_livres) * 100):.1f}%" if (postgres_livres + mongo_livres) > 0 else "0%"
        }
    
    return stats

@hybrid_router.get("/compare-livre")
async def comparer_livre_entre_bases(
    titre: str = Query(..., description="Titre du livre à comparer"),
    db: Session = Depends(get_db)
):
    """🔍 Comparer un livre entre PostgreSQL et MongoDB"""
    
    comparison = {
        "titre_recherche": titre,
        "timestamp": datetime.now(),
        "postgresql": {
            "found": False,
            "data": None,
            "error": None
        },
        "mongodb": {
            "found": False,
            "data": None,
            "error": None
        },
        "comparison": {
            "differences": [],
            "similarities": [],
            "recommendation": ""
        }
    }
    
    # === RECHERCHE POSTGRESQL ===
    try:
        postgres_query = text("""
            SELECT 
                l.*,
                a.nom_complet as auteur,
                e.nom_editeur as editeur,
                lg.nom_langue as langue
            FROM livre l
            LEFT JOIN livre_auteur la ON l.id_livre = la.id_livre
            LEFT JOIN auteur a ON la.id_auteur = a.id_auteur
            LEFT JOIN livre_editeur le ON l.id_livre = le.id_livre
            LEFT JOIN editeur e ON le.id_editeur = e.id_editeur
            LEFT JOIN livre_langue ll ON l.id_livre = ll.id_livre
            LEFT JOIN langue lg ON ll.id_langue = lg.id_langue
            WHERE l.titre ILIKE :titre
            LIMIT 1
        """)
        
        postgres_result = db.execute(postgres_query, {"titre": f"%{titre}%"})
        postgres_row = postgres_result.fetchone()
        
        if postgres_row:
            comparison["postgresql"]["found"] = True
            comparison["postgresql"]["data"] = dict(postgres_row._mapping)
            
    except Exception as e:
        comparison["postgresql"]["error"] = str(e)
    
    # === RECHERCHE MONGODB ===
    mongo_available = await check_mongodb()
    
    if mongo_available:
        try:
            mongo_doc = await mongodb_service.database.livres.find_one({
                "titre": {"$regex": titre, "$options": "i"}
            })
            
            if mongo_doc:
                comparison["mongodb"]["found"] = True
                comparison["mongodb"]["data"] = serialize_mongo_doc(mongo_doc)
                
        except Exception as e:
            comparison["mongodb"]["error"] = str(e)
    
    # === COMPARAISON ===
    if comparison["postgresql"]["found"] and comparison["mongodb"]["found"]:
        pg_data = comparison["postgresql"]["data"]
        mg_data = comparison["mongodb"]["data"]
        
        # Analyser les différences et similitudes
        if pg_data.get("titre") == mg_data.get("titre"):
            comparison["comparison"]["similarities"].append("Titre identique")
        else:
            comparison["comparison"]["differences"].append(f"Titre différent: PG='{pg_data.get('titre')}' vs MG='{mg_data.get('titre')}'")
        
        if pg_data.get("isbn_13") == mg_data.get("isbn_13"):
            comparison["comparison"]["similarities"].append("ISBN-13 identique")
        
        comparison["comparison"]["recommendation"] = "Livre trouvé dans les deux bases - Vérifiez la cohérence des données"
        
    elif comparison["postgresql"]["found"]:
        comparison["comparison"]["recommendation"] = "Livre uniquement dans PostgreSQL - Considérez l'ajout dans MongoDB"
        
    elif comparison["mongodb"]["found"]:
        comparison["comparison"]["recommendation"] = "Livre uniquement dans MongoDB - Considérez l'ajout dans PostgreSQL"
        
    else:
        comparison["comparison"]["recommendation"] = "Livre non trouvé dans aucune base"
    
    return comparison

@hybrid_router.get("/top-livres-global")
async def top_livres_global(
    limit: int = Query(20, le=100, description="Nombre de livres à retourner"),
    db: Session = Depends(get_db)
):
    """🏆 Top livres agrégés des deux bases de données"""
    
    result = {
        "timestamp": datetime.now(),
        "limit": limit,
        "postgresql_livres": [],
        "mongodb_livres": [],
        "top_combined": []
    }
    
    # === TOP POSTGRESQL (par date récente) ===
    try:
        postgres_query = text("""
            SELECT 
                l.titre,
                l.annee_publication,
                l.nombre_pages,
                a.nom_complet as auteur,
                e.nom_editeur as editeur,
                'PostgreSQL' as source
            FROM livre l
            LEFT JOIN livre_auteur la ON l.id_livre = la.id_livre
            LEFT JOIN auteur a ON la.id_auteur = a.id_auteur
            LEFT JOIN livre_editeur le ON l.id_livre = le.id_livre
            LEFT JOIN editeur e ON le.id_editeur = e.id_editeur
            ORDER BY l.annee_publication DESC NULLS LAST
            LIMIT :limit
        """)
        
        postgres_result = db.execute(postgres_query, {"limit": limit // 2})
        result["postgresql_livres"] = [dict(row._mapping) for row in postgres_result.fetchall()]
        
    except Exception as e:
        result["postgresql_error"] = str(e)
    
    # === TOP MONGODB (par note) ===
    mongo_available = await check_mongodb()
    
    if mongo_available:
        try:
            pipeline = [
                {"$match": {"note": {"$exists": True, "$ne": None}}},
                {"$sort": {"note": -1}},
                {"$limit": limit // 2},
                {"$project": {
                    "titre": 1,
                    "auteurs": 1,
                    "editeur": 1,
                    "note": 1,
                    "annee_publication": 1,
                    "nb_pages": 1,
                    "source": {"$literal": "MongoDB"}
                }}
            ]
            
            cursor = mongodb_service.database.livres.aggregate(pipeline)
            mongo_livres = await cursor.to_list(None)
            result["mongodb_livres"] = [serialize_mongo_doc(livre) for livre in mongo_livres]
            
        except Exception as e:
            result["mongodb_error"] = str(e)
    
    # === AGRÉGATION FINALE ===
    combined = []
    combined.extend(result["postgresql_livres"])
    combined.extend(result["mongodb_livres"])
    
    # Mélanger et limiter
    import random
    random.shuffle(combined)
    result["top_combined"] = combined[:limit]
    
    result["total_returned"] = len(result["top_combined"])
    result["postgres_count"] = len(result["postgresql_livres"])
    result["mongo_count"] = len(result["mongodb_livres"])
    
    return result