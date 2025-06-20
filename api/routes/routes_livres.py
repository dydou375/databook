"""
Routes pour l'API Livres
Adaptées au schéma de base de données réel
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.database import get_db
from database.livre_crud import livre_crud, auteur_crud, editeur_crud
from auth.auth import require_api_key

# Router pour les livres
livres_router = APIRouter(prefix="/livres", tags=["📚 Livres"])

# ================================
# ROUTES PUBLIQUES
# ================================

@livres_router.get("/", summary="Liste des livres")
async def get_livres(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(20, le=100, description="Nombre maximum d'éléments à retourner"),
    db: Session = Depends(get_db)
):
    """
    Récupérer la liste des livres
    
    - **skip**: Pagination - éléments à ignorer (défaut: 0)
    - **limit**: Nombre max de résultats (défaut: 20, max: 100)
    """
    try:
        livres = livre_crud.get_livres(db, skip=skip, limit=limit)
        return {
            "success": True,
            "data": livres,
            "total": len(livres),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des livres: {str(e)}")

@livres_router.get("/{livre_id}", summary="Détails d'un livre")
async def get_livre_detail(
    livre_id: int,
    complet: bool = Query(False, description="Inclure les relations (auteurs, éditeurs)"),
    db: Session = Depends(get_db)
):
    """
    Récupérer les détails d'un livre par son ID
    
    - **livre_id**: ID du livre
    - **complet**: Si true, inclut auteurs et éditeurs
    """
    try:
        if complet:
            livre = livre_crud.get_livre_complet(db, livre_id)
        else:
            livre = livre_crud.get_livre_by_id(db, livre_id)
        
        if not livre:
            raise HTTPException(status_code=404, detail="Livre non trouvé")
        
        return {
            "success": True,
            "data": livre
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du livre: {str(e)}")

@livres_router.get("/search/", summary="Recherche de livres")
async def rechercher_livres(
    q: str = Query(..., min_length=2, description="Terme de recherche (titre, auteur, ISBN...)"),
    db: Session = Depends(get_db)
):
    """
    Rechercher des livres par titre, auteur, ISBN ou description
    
    - **q**: Terme de recherche (minimum 2 caractères)
    """
    try:
        livres = livre_crud.rechercher_livres(db, q)
        return {
            "success": True,
            "data": livres,
            "total": len(livres),
            "query": q
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche: {str(e)}")

# ================================
# ROUTES AUTEURS
# ================================

@livres_router.get("/auteurs/", summary="Liste des auteurs")
async def get_auteurs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Récupérer la liste des auteurs"""
    try:
        auteurs = auteur_crud.get_auteurs(db, skip=skip, limit=limit)
        return {
            "success": True,
            "data": auteurs,
            "total": len(auteurs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ================================
# ROUTES EDITEURS
# ================================

@livres_router.get("/editeurs/", summary="Liste des éditeurs")
async def get_editeurs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Récupérer la liste des éditeurs"""
    try:
        editeurs = editeur_crud.get_editeurs(db, skip=skip, limit=limit)
        return {
            "success": True,
            "data": editeurs,
            "total": len(editeurs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ================================
# ROUTES STATISTIQUES (Protégées)
# ================================

@livres_router.get("/stats/", summary="Statistiques de la base", dependencies=[Depends(require_api_key)])
async def get_statistiques(db: Session = Depends(get_db)):
    """
    Récupérer les statistiques de la base de données
    
    🔒 **Authentification requise** (clé API)
    """
    try:
        stats = livre_crud.get_statistiques(db)
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ================================
# ROUTES AVANCÉES
# ================================

@livres_router.get("/par-annee/{annee}", summary="Livres par année")
async def get_livres_par_annee(
    annee: int,
    db: Session = Depends(get_db)
):
    """Récupérer les livres publiés une année donnée"""
    try:
        from sqlalchemy import text
        query = text("""
            SELECT id_livre, titre, annee_publication, isbn, note_moyenne
            FROM test.livre 
            WHERE annee_publication = :annee
            ORDER BY titre
        """)
        
        result = db.execute(query, {"annee": annee})
        livres = [dict(row._mapping) for row in result]
        
        return {
            "success": True,
            "data": livres,
            "annee": annee,
            "total": len(livres)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@livres_router.get("/top-notes/", summary="Livres les mieux notés")
async def get_top_livres(
    limit: int = Query(10, le=50, description="Nombre de livres à retourner"),
    db: Session = Depends(get_db)
):
    """Récupérer les livres les mieux notés"""
    try:
        from sqlalchemy import text
        query = text("""
            SELECT id_livre, titre, annee_publication, note_moyenne, nombre_avis
            FROM test.livre 
            WHERE note_moyenne IS NOT NULL
            ORDER BY note_moyenne DESC, nombre_avis DESC
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
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ================================
# ROUTE DE TEST RAPIDE
# ================================

@livres_router.get("/test/connection", summary="Test de connexion")
async def test_connection(db: Session = Depends(get_db)):
    """Tester la connexion à la base de données"""
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT COUNT(*) as total FROM test.livre"))
        count = result.fetchone()
        
        return {
            "success": True,
            "message": "Connexion réussie!",
            "total_livres": dict(count._mapping)["total"],
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de connexion: {str(e)}") 