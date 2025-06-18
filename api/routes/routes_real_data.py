from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.database import get_db
from auth.auth import require_api_key

# Router pour les vraies données du schéma test
real_data_router = APIRouter(prefix="/data", tags=["Real Data"])

@real_data_router.get("/health")
async def health_check_real_data(db: Session = Depends(get_db)):
    """Vérifier l'accès aux vraies tables"""
    try:
        # Test d'accès aux tables réelles
        result = db.execute(text("SELECT COUNT(*) as count FROM test.livre"))
        livre_count = result.fetchone()
        
        result = db.execute(text("SELECT COUNT(*) as count FROM test.auteur"))
        auteur_count = result.fetchone()
        
        return {
            "status": "✅ OK",
            "timestamp": datetime.now(),
            "tables": {
                "livres": dict(livre_count._mapping)["count"],
                "auteurs": dict(auteur_count._mapping)["count"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'accès aux données: {str(e)}")

@real_data_router.get("/livres/")
async def get_livres(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Récupérer les livres depuis la vraie table"""
    try:
        query = text("""
            SELECT 
                l.id_livre,
                l.titre,
                l.sous_titre,
                l.annee_publication,
                l.isbn_10,
                l.isbn_13,
                l.description,
                l.nombre_pages,
                l.format_physique,
                l.couverture_url,
                l.created_at,
                l.updated_at
            FROM test.livre l
            ORDER BY l.created_at DESC
            LIMIT :limit OFFSET :skip
        """)
        
        result = db.execute(query, {"limit": limit, "skip": skip})
        livres = [dict(row._mapping) for row in result]
        
        return {
            "success": True,
            "data": livres,
            "total": len(livres),
            "pagination": {"skip": skip, "limit": limit}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@real_data_router.get("/livres/{livre_id}")
async def get_livre_details(livre_id: int, db: Session = Depends(get_db)):
    """Récupérer les détails d'un livre avec ses auteurs"""
    try:
        # Récupérer le livre
        livre_query = text("""
            SELECT 
                l.id_livre,
                l.titre,
                l.annee_publication,
                l.isbn,
                l.description,
                l.date_ajout
            FROM test.livre l
            WHERE l.id_livre = :livre_id
        """)
        
        result = db.execute(livre_query, {"livre_id": livre_id})
        livre = result.fetchone()
        
        if not livre:
            raise HTTPException(status_code=404, detail="Livre non trouvé")
        
        livre_data = dict(livre._mapping)
        
        # Récupérer les auteurs
        auteurs_query = text("""
            SELECT a.id_auteur, a.nom
            FROM test.auteur a
            JOIN test.livre_auteur la ON a.id_auteur = la.id_auteur
            WHERE la.id_livre = :livre_id
        """)
        
        result = db.execute(auteurs_query, {"livre_id": livre_id})
        auteurs = [dict(row._mapping) for row in result]
        livre_data["auteurs"] = auteurs
        
        # Récupérer les éditeurs
        editeurs_query = text("""
            SELECT e.id_editeur, e.nom
            FROM test.editeur e
            JOIN test.livre_editeur le ON e.id_editeur = le.id_editeur
            WHERE le.id_livre = :livre_id
        """)
        
        result = db.execute(editeurs_query, {"livre_id": livre_id})
        editeurs = [dict(row._mapping) for row in result]
        livre_data["editeurs"] = editeurs
        
        return {"success": True, "data": livre_data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@real_data_router.get("/search/")
async def search_livres(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db)
):
    """Rechercher des livres dans les vraies données"""
    try:
        query = text("""
            SELECT DISTINCT 
                l.id_livre,
                l.titre,
                l.annee_publication,
                l.isbn,
                l.description,
                a.nom as auteur_nom
            FROM test.livre l
            LEFT JOIN test.livre_auteur la ON l.id_livre = la.id_livre
            LEFT JOIN test.auteur a ON la.id_auteur = a.id_auteur
            WHERE 
                l.titre ILIKE :query 
                OR l.description ILIKE :query 
                OR a.nom ILIKE :query
                OR l.isbn ILIKE :query
            ORDER BY l.date_ajout DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"query": f"%{q}%", "limit": limit})
        livres = [dict(row._mapping) for row in result]
        
        return {
            "success": True,
            "query": q,
            "data": livres,
            "total": len(livres)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@real_data_router.get("/auteurs/")
async def get_auteurs(
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Récupérer les auteurs depuis la vraie table"""
    try:
        query = text("""
            SELECT 
                a.id_auteur,
                a.nom,
                a.url_openlibrary,
                a.url_goodreads,
                a.url_babelio,
                a.date_ajout,
                COUNT(la.id_livre) as nombre_livres
            FROM test.auteur a
            LEFT JOIN test.livre_auteur la ON a.id_auteur = la.id_auteur
            GROUP BY a.id_auteur, a.nom, a.url_openlibrary, a.url_goodreads, a.url_babelio, a.date_ajout
            ORDER BY nombre_livres DESC, a.nom
            LIMIT :limit
        """)
        
        result = db.execute(query, {"limit": limit})
        auteurs = [dict(row._mapping) for row in result]
        
        return {
            "success": True,
            "data": auteurs,
            "total": len(auteurs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@real_data_router.get("/statistics/")
async def get_real_statistics(
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key)
):
    """Statistiques des vraies données (nécessite une clé API)"""
    try:
        # D'abord vérifier la structure de la table livre
        structure_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'test' AND table_name = 'livre'
            ORDER BY ordinal_position
        """)
        
        structure_result = db.execute(structure_query)
        columns = [row.column_name for row in structure_result]
        
        # Statistiques de base
        stats_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM test.livre) as total_livres,
                (SELECT COUNT(*) FROM test.auteur) as total_auteurs,
                (SELECT COUNT(*) FROM test.editeur) as total_editeurs,
                (SELECT COUNT(*) FROM test.langue) as total_langues,
                (SELECT COUNT(*) FROM test.sujet) as total_sujets
        """)
        
        result = db.execute(stats_query)
        stats = dict(result.fetchone()._mapping)
        
        # Ajouter les colonnes disponibles pour debug
        stats["colonnes_disponibles"] = columns
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now(),
            "database": "PostgreSQL - Schema test"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@real_data_router.get("/top-livres/")
async def get_top_livres(
    limit: int = Query(10, le=20),
    db: Session = Depends(get_db)
):
    """Livres récents depuis les vraies données"""
    try:
        query = text("""
            SELECT 
                l.id_livre,
                l.titre,
                l.annee_publication,
                STRING_AGG(a.nom, ', ') as auteurs
            FROM test.livre l
            LEFT JOIN test.livre_auteur la ON l.id_livre = la.id_livre
            LEFT JOIN test.auteur a ON la.id_auteur = a.id_auteur
            GROUP BY l.id_livre, l.titre, l.annee_publication
            ORDER BY l.date_ajout DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"limit": limit})
        livres = [dict(row._mapping) for row in result]
        
        return {
            "success": True,
            "data": livres,
            "total": len(livres)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@real_data_router.get("/editeurs/")
async def get_editeurs(
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Récupérer les éditeurs depuis la vraie table"""
    try:
        query = text("""
            SELECT 
                e.id_editeur,
                e.nom,
                e.url_openlibrary,
                e.url_goodreads,
                COUNT(le.id_livre) as nombre_livres
            FROM test.editeur e
            LEFT JOIN test.livre_editeur le ON e.id_editeur = le.id_editeur
            GROUP BY e.id_editeur, e.nom, e.url_openlibrary, e.url_goodreads
            ORDER BY nombre_livres DESC, e.nom
            LIMIT :limit
        """)
        
        result = db.execute(query, {"limit": limit})
        editeurs = [dict(row._mapping) for row in result]
        
        return {
            "success": True,
            "data": editeurs,
            "total": len(editeurs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 