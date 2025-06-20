"""
Modèles pour la base de données Livres
Basés sur le schéma MCD complet de l'utilisateur
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

# ================================
# AUTEUR
# ================================
class AuteurBase(BaseModel):
    nom: str
    url_openlibrary: Optional[str] = None
    url_googlebooks: Optional[str] = None
    url_babelio: Optional[str] = None
    url_goodreads: Optional[str] = None

class Auteur(AuteurBase):
    id_auteur: int
    date_ajout: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ================================
# EDITEUR
# ================================
class EditeurBase(BaseModel):
    nom: str
    url_openlibrary: Optional[str] = None
    url_googlebooks: Optional[str] = None
    url_babelio: Optional[str] = None
    url_goodreads: Optional[str] = None

class Editeur(EditeurBase):
    id_editeur: int
    date_ajout: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ================================
# LANGUE
# ================================
class LangueBase(BaseModel):
    code: str
    nom: str

class Langue(LangueBase):
    id_langue: int
    date_ajout: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ================================
# SUJET
# ================================
class SujetBase(BaseModel):
    nom: str

class Sujet(SujetBase):
    id_sujet: int
    date_ajout: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ================================
# LIVRE (Table principale)
# ================================
class LivreBase(BaseModel):
    titre: str
    annee_publication: Optional[int] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    nombre_pages: Optional[int] = None
    url_couverture: Optional[str] = None
    url_openlibrary: Optional[str] = None
    url_googlebooks: Optional[str] = None
    url_babelio: Optional[str] = None
    url_goodreads: Optional[str] = None
    note_moyenne: Optional[float] = None
    nombre_avis: Optional[int] = None
    statut_acquisition: Optional[str] = None

class Livre(LivreBase):
    id_livre: int
    date_ajout: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ================================
# LIVRE COMPLET AVEC RELATIONS
# ================================
class LivreComplet(Livre):
    """Livre avec toutes ses relations"""
    auteurs: List[Auteur] = []
    editeurs: List[Editeur] = []
    langues: List[Langue] = []
    sujets: List[Sujet] = []

# ================================
# MODÈLES DE RECHERCHE
# ================================
class RechercheParams(BaseModel):
    titre: Optional[str] = None
    auteur: Optional[str] = None
    editeur: Optional[str] = None
    annee_min: Optional[int] = None
    annee_max: Optional[int] = None
    langue: Optional[str] = None
    sujet: Optional[str] = None
    isbn: Optional[str] = None

# ================================
# STATISTIQUES
# ================================
class StatistiquesDB(BaseModel):
    total_livres: int
    total_auteurs: int
    total_editeurs: int
    total_langues: int
    total_sujets: int
    livre_plus_recent: Optional[int] = None
    livre_plus_ancien: Optional[int] = None 