"""
Modèles pour les tables existantes dans la base de données PostgreSQL
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Modèle pour la table auteur existante
class AuteurExisting(BaseModel):
    """Modèle pour la table auteur existante"""
    id_auteur: int
    nom: Optional[str] = None
    prenom: Optional[str] = None
    nom_complet: Optional[str] = None
    date_naissance: Optional[datetime] = None
    date_deces: Optional[datetime] = None
    biographie: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AuteurCreate(BaseModel):
    """Modèle pour créer un auteur"""
    nom: Optional[str] = None
    prenom: Optional[str] = None
    nom_complet: Optional[str] = None
    date_naissance: Optional[datetime] = None
    date_deces: Optional[datetime] = None
    biographie: Optional[str] = None

class AuteurUpdate(BaseModel):
    """Modèle pour mettre à jour un auteur"""
    nom: Optional[str] = None
    prenom: Optional[str] = None
    nom_complet: Optional[str] = None
    date_naissance: Optional[datetime] = None
    date_deces: Optional[datetime] = None
    biographie: Optional[str] = None

# Modèle pour la table livre existante
class LivreExisting(BaseModel):
    """Modèle pour la table livre existante"""
    id_livre: int
    ol_id: Optional[str] = None  # Open Library ID
    titre: Optional[str] = None
    sous_titre: Optional[str] = None
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    date_publication: Optional[datetime] = None
    annee_publication: Optional[int] = None
    nombre_pages: Optional[int] = None
    format_physique: Optional[str] = None
    description: Optional[str] = None
    couverture_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class LivreCreate(BaseModel):
    """Modèle pour créer un livre"""
    ol_id: Optional[str] = None
    titre: str
    sous_titre: Optional[str] = None
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    date_publication: Optional[datetime] = None
    annee_publication: Optional[int] = None
    nombre_pages: Optional[int] = None
    format_physique: Optional[str] = None
    description: Optional[str] = None
    couverture_url: Optional[str] = None

class LivreUpdate(BaseModel):
    """Modèle pour mettre à jour un livre"""
    ol_id: Optional[str] = None
    titre: Optional[str] = None
    sous_titre: Optional[str] = None
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    date_publication: Optional[datetime] = None
    annee_publication: Optional[int] = None
    nombre_pages: Optional[int] = None
    format_physique: Optional[str] = None
    description: Optional[str] = None
    couverture_url: Optional[str] = None

# Modèle complet avec auteur (pour les jointures)
class LivreAvecAuteur(LivreExisting):
    """Modèle de livre avec information de l'auteur"""
    auteur: Optional[AuteurExisting] = None

class AuteurAvecLivres(AuteurExisting):
    """Modèle d'auteur avec ses livres"""
    livres: List[LivreExisting] = Field(default_factory=list)

# Modèles pour les statistiques
class StatistiquesLivres(BaseModel):
    """Statistiques sur les livres"""
    total_livres: int
    total_auteurs: int
    livres_par_annee: dict
    livres_par_format: dict
    auteurs_les_plus_prolifiques: List[dict]

# Modèles pour la recherche
class ResultatRecherche(BaseModel):
    """Résultat de recherche"""
    livres: List[LivreAvecAuteur] = Field(default_factory=list)
    auteurs: List[AuteurAvecLivres] = Field(default_factory=list)
    total_resultats: int
    page: int = 1
    par_page: int = 20 