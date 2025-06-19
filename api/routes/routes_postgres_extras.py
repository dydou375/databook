from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.database import get_db
from auth.auth import require_jwt, optional_jwt

# Router pour les endpoints PostgreSQL d'analytics/visualisation
postgres_extras_router = APIRouter(prefix="/postgres-extras", tags=["PostgreSQL - Analytics & Visualisation"])

@postgres_extras_router.get("/")
async def accueil_postgres_extras():
    """🎯 Fonctionnalités d'analytics PostgreSQL"""
    return {
        "message": "🎯 Analytics PostgreSQL - Graphiques et Visualisations",
        "endpoints": {
            "analytics": "GET /postgres-extras/analytics - Analytics avancés PostgreSQL",
            "top_auteurs": "GET /postgres-extras/auteurs/top - Top des auteurs",
            "top_editeurs": "GET /postgres-extras/editeurs/top - Top des éditeurs", 
            "stats_annees": "GET /postgres-extras/livres/stats-annees - Répartition par années",
            "stats_langues": "GET /postgres-extras/livres/stats-langues - Répartition par langues",
            "stats_pages": "GET /postgres-extras/livres/stats-pages - Statistiques des pages",
            "stats_formats": "GET /postgres-extras/livres/stats-formats - Répartition par formats"
        },
        "note": "Ces endpoints sont équivalents aux analytics MongoDB pour les graphiques"
    }

@postgres_extras_router.get("/analytics")
async def analytics_avances_postgres(
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """📊 Analytics avancés PostgreSQL - Équivalent MongoDB pour graphiques"""
    try:
        # Statistiques générales
        stats_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM livre) as total_livres,
                (SELECT COUNT(DISTINCT id_auteur) FROM auteur) as total_auteurs,
                (SELECT COUNT(DISTINCT id_editeur) FROM editeur) as total_editeurs,
                (SELECT COUNT(DISTINCT id_langue) FROM langue) as total_langues,
                (SELECT COUNT(DISTINCT id_sujet) FROM sujet) as total_sujets
        """)
        stats_result = db.execute(stats_query).fetchone()
        
        # Top 10 auteurs par nombre de livres
        top_auteurs_query = text("""
            SELECT a.nom_complet, COUNT(la.id_livre) as nb_livres
            FROM auteur a
            JOIN livre_auteur la ON a.id_auteur = la.id_auteur
            GROUP BY a.id_auteur, a.nom_complet
            ORDER BY nb_livres DESC
            LIMIT 10
        """)
        top_auteurs = db.execute(top_auteurs_query).fetchall()
        
        # Top 10 éditeurs par nombre de livres
        top_editeurs_query = text("""
            SELECT e.nom_editeur, e.pays, COUNT(le.id_livre) as nb_livres
            FROM editeur e
            JOIN livre_editeur le ON e.id_editeur = le.id_editeur
            GROUP BY e.id_editeur, e.nom_editeur, e.pays
            ORDER BY nb_livres DESC
            LIMIT 10
        """)
        top_editeurs = db.execute(top_editeurs_query).fetchall()
        
        # Répartition par langues
        repartition_langues_query = text("""
            SELECT lg.nom_langue, lg.code_langue, COUNT(ll.id_livre) as nb_livres
            FROM langue lg
            JOIN livre_langue ll ON lg.id_langue = ll.id_langue
            GROUP BY lg.id_langue, lg.nom_langue, lg.code_langue
            ORDER BY nb_livres DESC
        """)
        repartition_langues = db.execute(repartition_langues_query).fetchall()
        
        # Répartition par années de publication
        repartition_annees_query = text("""
            SELECT annee_publication, COUNT(*) as nb_livres
            FROM livre 
            WHERE annee_publication IS NOT NULL
            GROUP BY annee_publication
            ORDER BY annee_publication DESC
            LIMIT 20
        """)
        repartition_annees = db.execute(repartition_annees_query).fetchall()
        
        # Statistiques des pages
        stats_pages_query = text("""
            SELECT 
                MIN(nombre_pages) as min_pages,
                MAX(nombre_pages) as max_pages,
                AVG(nombre_pages) as avg_pages,
                COUNT(*) as total_avec_pages
            FROM livre 
            WHERE nombre_pages IS NOT NULL AND nombre_pages > 0
        """)
        stats_pages = db.execute(stats_pages_query).fetchone()
        
        # Répartition par formats physiques
        repartition_formats_query = text("""
            SELECT format_physique, COUNT(*) as nb_livres
            FROM livre 
            WHERE format_physique IS NOT NULL AND format_physique != ''
            GROUP BY format_physique
            ORDER BY nb_livres DESC
            LIMIT 15
        """)
        repartition_formats = db.execute(repartition_formats_query).fetchall()
        
        # Top sujets/genres
        top_sujets_query = text("""
            SELECT s.nom_sujet, s.categorie, COUNT(ls.id_livre) as nb_livres
            FROM sujet s
            JOIN livre_sujet ls ON s.id_sujet = ls.id_sujet
            GROUP BY s.id_sujet, s.nom_sujet, s.categorie
            ORDER BY nb_livres DESC
            LIMIT 15
        """)
        top_sujets = db.execute(top_sujets_query).fetchall()
        
        return {
            "success": True,
            "timestamp": datetime.now(),
            "database": "PostgreSQL (schéma test)",
            "analytics": {
                "statistiques_generales": {
                    "total_livres": stats_result.total_livres,
                    "total_auteurs": stats_result.total_auteurs,
                    "total_editeurs": stats_result.total_editeurs,
                    "total_langues": stats_result.total_langues,
                    "total_sujets": stats_result.total_sujets
                },
                "top_auteurs": [
                    {"auteur": row.nom_complet, "nb_livres": row.nb_livres} 
                    for row in top_auteurs
                ],
                "top_editeurs": [
                    {
                        "editeur": row.nom_editeur, 
                        "pays": row.pays,
                        "nb_livres": row.nb_livres
                    } 
                    for row in top_editeurs
                ],
                "repartition_langues": [
                    {
                        "langue": row.nom_langue,
                        "code": row.code_langue,
                        "nb_livres": row.nb_livres
                    } 
                    for row in repartition_langues
                ],
                "repartition_annees": [
                    {"annee": row.annee_publication, "nb_livres": row.nb_livres} 
                    for row in repartition_annees
                ],
                "statistiques_pages": {
                    "min_pages": stats_pages.min_pages if stats_pages else None,
                    "max_pages": stats_pages.max_pages if stats_pages else None,
                    "avg_pages": round(stats_pages.avg_pages, 1) if stats_pages and stats_pages.avg_pages else None,
                    "total_avec_pages": stats_pages.total_avec_pages if stats_pages else 0
                },
                "repartition_formats": [
                    {"format": row.format_physique, "nb_livres": row.nb_livres} 
                    for row in repartition_formats
                ],
                "top_sujets": [
                    {
                        "sujet": row.nom_sujet,
                        "categorie": row.categorie,
                        "nb_livres": row.nb_livres
                    } 
                    for row in top_sujets
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analytics PostgreSQL: {str(e)}")

@postgres_extras_router.get("/auteurs/top")
async def top_auteurs_postgres(
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """✍️ Top des auteurs PostgreSQL par nombre de livres"""
    try:
        query = text("""
            SELECT 
                a.nom_complet,
                a.nom,
                a.prenom,
                a.biographie,
                COUNT(la.id_livre) as nb_livres
            FROM auteur a
            JOIN livre_auteur la ON a.id_auteur = la.id_auteur
            GROUP BY a.id_auteur, a.nom_complet, a.nom, a.prenom, a.biographie
            ORDER BY nb_livres DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"limit": limit}).fetchall()
        
        return {
            "success": True,
            "data": [
                {
                    "nom_complet": row.nom_complet,
                    "nom": row.nom,
                    "prenom": row.prenom,
                    "biographie": row.biographie,
                    "nb_livres": row.nb_livres
                }
                for row in result
            ],
            "total": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@postgres_extras_router.get("/editeurs/top")
async def top_editeurs_postgres(
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """🏢 Top des éditeurs PostgreSQL par nombre de livres"""
    try:
        query = text("""
            SELECT 
                e.nom_editeur,
                e.pays,
                e.annee_creation,
                COUNT(le.id_livre) as nb_livres
            FROM editeur e
            JOIN livre_editeur le ON e.id_editeur = le.id_editeur
            GROUP BY e.id_editeur, e.nom_editeur, e.pays, e.annee_creation
            ORDER BY nb_livres DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"limit": limit}).fetchall()
        
        return {
            "success": True,
            "data": [
                {
                    "nom_editeur": row.nom_editeur,
                    "pays": row.pays,
                    "annee_creation": row.annee_creation,
                    "nb_livres": row.nb_livres
                }
                for row in result
            ],
            "total": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@postgres_extras_router.get("/livres/stats-annees")
async def stats_annees_postgres(
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """📅 Statistiques de répartition par années de publication"""
    try:
        # Répartition détaillée par années
        query = text("""
            SELECT 
                annee_publication,
                COUNT(*) as nb_livres
            FROM livre 
            WHERE annee_publication IS NOT NULL
            GROUP BY annee_publication
            ORDER BY annee_publication DESC
        """)
        
        result = db.execute(query).fetchall()
        
        # Statistiques sur les années
        stats_query = text("""
            SELECT 
                MIN(annee_publication) as min_annee,
                MAX(annee_publication) as max_annee,
                COUNT(DISTINCT annee_publication) as nb_annees_distinctes,
                COUNT(*) as total_livres_avec_annee
            FROM livre 
            WHERE annee_publication IS NOT NULL
        """)
        
        stats = db.execute(stats_query).fetchone()
        
        return {
            "success": True,
            "data": [
                {"annee": row.annee_publication, "nb_livres": row.nb_livres}
                for row in result
            ],
            "statistiques": {
                "annee_min": stats.min_annee,
                "annee_max": stats.max_annee,
                "nb_annees_distinctes": stats.nb_annees_distinctes,
                "total_livres_avec_annee": stats.total_livres_avec_annee
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@postgres_extras_router.get("/livres/stats-langues")
async def stats_langues_postgres(
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """🌍 Statistiques de répartition par langues"""
    try:
        query = text("""
            SELECT 
                lg.nom_langue,
                lg.code_langue,
                COUNT(ll.id_livre) as nb_livres
            FROM langue lg
            JOIN livre_langue ll ON lg.id_langue = ll.id_langue
            GROUP BY lg.id_langue, lg.nom_langue, lg.code_langue
            ORDER BY nb_livres DESC
        """)
        
        result = db.execute(query).fetchall()
        
        return {
            "success": True,
            "data": [
                {
                    "langue": row.nom_langue,
                    "code": row.code_langue,
                    "nb_livres": row.nb_livres
                }
                for row in result
            ],
            "total": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@postgres_extras_router.get("/livres/stats-pages")
async def stats_pages_postgres(
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """📄 Statistiques détaillées sur le nombre de pages"""
    try:
        # Statistiques générales
        stats_query = text("""
            SELECT 
                MIN(nombre_pages) as min_pages,
                MAX(nombre_pages) as max_pages,
                AVG(nombre_pages) as avg_pages,
                COUNT(*) as total_avec_pages,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY nombre_pages) as median_pages
            FROM livre 
            WHERE nombre_pages IS NOT NULL AND nombre_pages > 0
        """)
        
        stats = db.execute(stats_query).fetchone()
        
        # Distribution par tranches de pages
        distribution_query = text("""
            SELECT 
                CASE 
                    WHEN nombre_pages < 100 THEN '< 100 pages'
                    WHEN nombre_pages < 200 THEN '100-199 pages'
                    WHEN nombre_pages < 300 THEN '200-299 pages'
                    WHEN nombre_pages < 400 THEN '300-399 pages'
                    WHEN nombre_pages < 500 THEN '400-499 pages'
                    ELSE '500+ pages'
                END as tranche_pages,
                COUNT(*) as nb_livres
            FROM livre 
            WHERE nombre_pages IS NOT NULL AND nombre_pages > 0
            GROUP BY 
                CASE 
                    WHEN nombre_pages < 100 THEN '< 100 pages'
                    WHEN nombre_pages < 200 THEN '100-199 pages'
                    WHEN nombre_pages < 300 THEN '200-299 pages'
                    WHEN nombre_pages < 400 THEN '300-399 pages'
                    WHEN nombre_pages < 500 THEN '400-499 pages'
                    ELSE '500+ pages'
                END
            ORDER BY MIN(nombre_pages)
        """)
        
        distribution = db.execute(distribution_query).fetchall()
        
        return {
            "success": True,
            "statistiques": {
                "min_pages": stats.min_pages,
                "max_pages": stats.max_pages,
                "avg_pages": round(stats.avg_pages, 1) if stats.avg_pages else None,
                "median_pages": round(stats.median_pages, 1) if stats.median_pages else None,
                "total_avec_pages": stats.total_avec_pages
            },
            "distribution": [
                {"tranche": row.tranche_pages, "nb_livres": row.nb_livres}
                for row in distribution
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@postgres_extras_router.get("/livres/stats-formats")
async def stats_formats_postgres(
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """📖 Statistiques sur les formats physiques des livres"""
    try:
        query = text("""
            SELECT 
                format_physique,
                COUNT(*) as nb_livres
            FROM livre 
            WHERE format_physique IS NOT NULL AND format_physique != ''
            GROUP BY format_physique
            ORDER BY nb_livres DESC
        """)
        
        result = db.execute(query).fetchall()
        
        return {
            "success": True,
            "data": [
                {"format": row.format_physique, "nb_livres": row.nb_livres}
                for row in result
            ],
            "total": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))