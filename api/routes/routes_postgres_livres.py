from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.models_livres import LivreComplet, LivresResponse, LivreResponse
from database.database import get_db
from auth.auth import require_jwt, optional_jwt

# Router pour les livres PostgreSQL du schéma test
postgres_livres_router = APIRouter(prefix="/postgres", tags=["PostgreSQL - Livres Réels"])

@postgres_livres_router.get("/livres/stats/general")
async def get_livres_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """Statistiques générales des livres PostgreSQL"""
    
    try:
        # Compter le total de livres
        count_query = text("SELECT COUNT(*) as total FROM livre")
        total_result = db.execute(count_query)
        total_livres = total_result.fetchone().total
        
        # Compter les auteurs
        auteurs_query = text("SELECT COUNT(DISTINCT id_auteur) as total FROM auteur")
        auteurs_result = db.execute(auteurs_query)
        total_auteurs = auteurs_result.fetchone().total
        
        # Compter les éditeurs
        editeurs_query = text("SELECT COUNT(DISTINCT id_editeur) as total FROM editeur")
        editeurs_result = db.execute(editeurs_query)
        total_editeurs = editeurs_result.fetchone().total
        
        # Compter les langues
        langues_query = text("SELECT COUNT(DISTINCT id_langue) as total FROM langue")
        langues_result = db.execute(langues_query)
        total_langues = langues_result.fetchone().total
        
        return {
            "total_livres": total_livres,
            "total_auteurs": total_auteurs,
            "total_editeurs": total_editeurs,
            "total_langues": total_langues,
            "database": "PostgreSQL (schéma test)",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul des statistiques: {str(e)}")

@postgres_livres_router.get("/livres/debug/tables")
async def debug_tables(
    db: Session = Depends(get_db)
):
    """Debug: Lister les tables disponibles dans le schéma test"""
    
    try:
        # Lister les tables du schéma test
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'test'
            ORDER BY table_name
        """)
        
        result = db.execute(tables_query)
        tables = [row.table_name for row in result.fetchall()]
        
        # Compter les enregistrements dans chaque table
        table_counts = {}
        for table in tables:
            try:
                count_query = text(f"SELECT COUNT(*) as count FROM {table}")
                count_result = db.execute(count_query)
                table_counts[table] = count_result.fetchone().count
            except Exception as e:
                table_counts[table] = f"Erreur: {str(e)}"
        
        return {
            "schema": "test",
            "tables": tables,
            "table_counts": table_counts,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur debug: {str(e)}")

@postgres_livres_router.get("/livres/{livre_id}", response_model=LivreComplet)
async def get_livre_by_id(
    livre_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer un livre par son ID avec toutes ses relations"""
    
    query = text("""
        SELECT 
            l.id_livre,
            l.ol_id,
            l.titre,
            l.sous_titre,
            l.isbn_10,
            l.isbn_13,
            l.date_publication,
            l.annee_publication,
            l.nombre_pages,
            l.format_physique,
            l.description,
            l.couverture_url,
            l.created_at,
            l.updated_at,
            
            a.nom as auteur_nom,
            a.prenom as auteur_prenom,
            a.nom_complet as auteur_nom_complet,
            a.biographie as auteur_biographie,
            
            e.nom_editeur as editeur_nom,
            e.pays as editeur_pays,
            e.annee_creation as editeur_annee_creation,
            
            lg.code_langue as langue_code,
            lg.nom_langue as langue_nom,
            
            s.nom_sujet as sujet_nom,
            s.categorie as sujet_categorie
            
        FROM livre l
        LEFT JOIN livre_auteur la ON l.id_livre = la.id_livre
        LEFT JOIN auteur a ON la.id_auteur = a.id_auteur
        LEFT JOIN livre_editeur le ON l.id_livre = le.id_livre
        LEFT JOIN editeur e ON le.id_editeur = e.id_editeur
        LEFT JOIN livre_langue ll ON l.id_livre = ll.id_livre
        LEFT JOIN langue lg ON ll.id_langue = lg.id_langue
        LEFT JOIN livre_sujet ls ON l.id_livre = ls.id_livre
        LEFT JOIN sujet s ON ls.id_sujet = s.id_sujet
        
        WHERE l.id_livre = :livre_id
    """)
    
    try:
        result = db.execute(query, {"livre_id": livre_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Livre avec l'ID {livre_id} non trouvé")
        
        livre_dict = {
            "id_livre": row.id_livre,
            "ol_id": row.ol_id,
            "titre": row.titre,
            "sous_titre": row.sous_titre,
            "isbn_10": row.isbn_10,
            "isbn_13": row.isbn_13,
            "date_publication": row.date_publication,
            "annee_publication": row.annee_publication,
            "nombre_pages": row.nombre_pages,
            "format_physique": row.format_physique,
            "description": row.description,
            "couverture_url": row.couverture_url,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "auteur_nom": row.auteur_nom,
            "auteur_prenom": row.auteur_prenom,
            "auteur_nom_complet": row.auteur_nom_complet,
            "auteur_biographie": row.auteur_biographie,
            "editeur_nom": row.editeur_nom,
            "editeur_pays": row.editeur_pays,
            "editeur_annee_creation": row.editeur_annee_creation,
            "langue_code": row.langue_code,
            "langue_nom": row.langue_nom,
            "sujet_nom": row.sujet_nom,
            "sujet_categorie": row.sujet_categorie
        }
        
        return LivreComplet(**livre_dict)
        
    except Exception as e:
        if "404" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du livre: {str(e)}")

@postgres_livres_router.get("/livres", response_model=List[LivreComplet])
async def get_livres_postgres(
    search: Optional[str] = Query(None, description="Recherche dans le titre ou auteur"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    auteur: Optional[str] = Query(None, description="Filtrer par auteur"),
    editeur: Optional[str] = Query(None, description="Filtrer par éditeur"),
    langue: Optional[str] = Query(None, description="Filtrer par langue"),
    db: Session = Depends(get_db)
):
    """Récupérer les livres depuis PostgreSQL (schéma test) avec toutes les relations"""
    
    try:
        # Version simplifiée pour tester d'abord
        simple_query = text("""
            SELECT 
                l.id_livre,
                l.ol_id,
                l.titre,
                l.sous_titre,
                l.isbn_10,
                l.isbn_13,
                l.date_publication,
                l.annee_publication,
                l.nombre_pages,
                l.format_physique,
                l.description,
                l.couverture_url,
                l.created_at,
                l.updated_at
                
            FROM livre l
            WHERE 1=1
            ORDER BY l.id_livre
            LIMIT :limit OFFSET :offset
        """)
        
        params = {"limit": limit, "offset": offset}
        result = db.execute(simple_query, params)
        rows = result.fetchall()
        
        # Convertir les résultats en modèles Pydantic
        livres = []
        for row in rows:
            livre_dict = {
                "id_livre": row.id_livre,
                "ol_id": row.ol_id,
                "titre": row.titre,
                "sous_titre": row.sous_titre,
                "isbn_10": row.isbn_10,
                "isbn_13": row.isbn_13,
                "date_publication": row.date_publication,
                "annee_publication": row.annee_publication,
                "nombre_pages": row.nombre_pages,
                "format_physique": row.format_physique,
                "description": row.description,
                "couverture_url": row.couverture_url,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                # Valeurs par défaut pour les champs manquants
                "auteur_nom": None,
                "auteur_prenom": None,
                "auteur_nom_complet": None,
                "auteur_biographie": None,
                "editeur_nom": None,
                "editeur_pays": None,
                "editeur_annee_creation": None,
                "langue_code": None,
                "langue_nom": None,
                "sujet_nom": None,
                "sujet_categorie": None
            }
            livres.append(LivreComplet(**livre_dict))
        
        return livres
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des livres: {str(e)}")

@postgres_livres_router.get("/livres/test/simple")
async def test_simple_query(db: Session = Depends(get_db)):
    """Test simple pour debugger la connexion"""
    try:
        # Test ultra simple
        result = db.execute(text("SELECT COUNT(*) as count FROM livre LIMIT 1"))
        row = result.fetchone()
        return {"count": row.count, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

@postgres_livres_router.get("/livres/test/columns")
async def test_columns(db: Session = Depends(get_db)):
    """Test des colonnes de la table livre"""
    try:
        # Vérifier les colonnes disponibles
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'livre' 
            AND table_schema = 'test'
            ORDER BY ordinal_position
        """))
        columns = [{"name": row.column_name, "type": row.data_type} for row in result.fetchall()]
        
        return {"columns": columns, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

@postgres_livres_router.get("/livres/test/sample")
async def test_sample_data(db: Session = Depends(get_db)):
    """Test récupération d'un échantillon"""
    try:
        # Récupérer juste les colonnes de base
        result = db.execute(text("SELECT id_livre, titre FROM livre LIMIT 1"))
        row = result.fetchone()
        
        if row:
            return {"id_livre": row.id_livre, "titre": row.titre, "status": "success"}
        else:
            return {"message": "Aucun livre trouvé", "status": "warning"}
    except Exception as e:
        return {"error": str(e), "status": "error"} 