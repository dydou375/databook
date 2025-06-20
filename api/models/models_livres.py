from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

# Modèles pour la vraie structure de base de données

class Auteur(BaseModel):
    """Modèle pour la table auteur"""
    id_auteur: int
    nom: str
    prenom: Optional[str] = None
    nom_complet: Optional[str] = None
    date_naissance: Optional[str] = None
    date_deces: Optional[str] = None
    biographie: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Editeur(BaseModel):
    """Modèle pour la table editeur"""
    id_editeur: int
    nom_editeur: str
    pays: Optional[str] = None
    annee_creation: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Langue(BaseModel):
    """Modèle pour la table langue"""
    id_langue: int
    code_langue: str
    nom_langue: str
    
    class Config:
        from_attributes = True

class Sujet(BaseModel):
    """Modèle pour la table sujet"""
    id_sujet: int
    nom_sujet: str
    categorie: Optional[str] = None
    
    class Config:
        from_attributes = True

class Livre(BaseModel):
    """Modèle pour la table livre"""
    id_livre: int
    ol_id: Optional[str] = None
    titre: str
    sous_titre: Optional[str] = None
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    date_publication: Optional[str] = None
    annee_publication: Optional[int] = None
    nombre_pages: Optional[int] = None
    format_physique: Optional[str] = None
    description: Optional[str] = None
    couverture_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LivreComplet(BaseModel):
    """Modèle pour un livre avec toutes ses relations"""
    # Informations du livre
    id_livre: int
    ol_id: Optional[str] = None
    titre: str
    sous_titre: Optional[str] = None
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    date_publication: Optional[str] = None
    annee_publication: Optional[int] = None
    nombre_pages: Optional[int] = None
    format_physique: Optional[str] = None
    description: Optional[str] = None
    couverture_url: Optional[str] = None
    
    # Informations de l'auteur
    auteur_nom: Optional[str] = None
    auteur_prenom: Optional[str] = None
    auteur_nom_complet: Optional[str] = None
    auteur_biographie: Optional[str] = None
    
    # Informations de l'éditeur
    editeur_nom: Optional[str] = None
    editeur_pays: Optional[str] = None
    editeur_annee_creation: Optional[int] = None
    
    # Informations de la langue
    langue_code: Optional[str] = None
    langue_nom: Optional[str] = None
    
    # Informations du sujet
    sujet_nom: Optional[str] = None
    sujet_categorie: Optional[str] = None
    
    # Métadonnées
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LivreCreate(BaseModel):
    """Modèle pour créer un nouveau livre"""
    titre: str
    sous_titre: Optional[str] = None
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    date_publication: Optional[str] = None
    annee_publication: Optional[int] = None
    nombre_pages: Optional[int] = None
    format_physique: Optional[str] = None
    description: Optional[str] = None
    couverture_url: Optional[str] = None
    
    # Relations (IDs)
    id_auteur: Optional[int] = None
    id_editeur: Optional[int] = None
    id_langue: Optional[int] = None
    id_sujet: Optional[int] = None

class LivreUpdate(BaseModel):
    """Modèle pour mettre à jour un livre"""
    titre: Optional[str] = None
    sous_titre: Optional[str] = None
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    date_publication: Optional[str] = None
    annee_publication: Optional[int] = None
    nombre_pages: Optional[int] = None
    format_physique: Optional[str] = None
    description: Optional[str] = None
    couverture_url: Optional[str] = None

# Modèles de réponse
class LivresResponse(BaseModel):
    """Réponse pour une liste de livres"""
    data: list[LivreComplet]
    total: int
    page: int = 1
    per_page: int = 20
    has_next: bool = False
    has_prev: bool = False

class LivreResponse(BaseModel):
    """Réponse pour un livre unique"""
    data: LivreComplet
    success: bool = True
    message: str = "Livre récupéré avec succès" 