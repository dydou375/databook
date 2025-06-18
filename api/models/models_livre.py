"""
Modèles Pydantic pour la base de données Livre
Basés sur le schéma MCD_v2.png de l'utilisateur
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, date

# ================================
# MODÈLES DE BASE (Tables principales)
# ================================

class AuteurBase(BaseModel):
    nom: str
    url_openlibrary: Optional[str] = None
    url_googlebooks: Optional[str] = None
    url_babelio: Optional[str] = None
    url_goodreads: Optional[str] = None

class AuteurCreate(AuteurBase):
    pass

class AuteurUpdate(BaseModel):
    nom: Optional[str] = None
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

class EditeurCreate(EditeurBase):
    pass

class EditeurUpdate(BaseModel):
    nom: Optional[str] = None
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

class LangueCreate(LangueBase):
    pass

class LangueUpdate(BaseModel):
    code: Optional[str] = None
    nom: Optional[str] = None

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

class SujetCreate(SujetBase):
    pass

class SujetUpdate(BaseModel):
    nom: Optional[str] = None

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
    
    @validator('annee_publication')
    def validate_annee(cls, v):
        if v is not None and (v < 0 or v > datetime.now().year + 1):
            raise ValueError('Année de publication invalide')
        return v
    
    @validator('nombre_pages')
    def validate_pages(cls, v):
        if v is not None and v < 0:
            raise ValueError('Le nombre de pages ne peut pas être négatif')
        return v
    
    @validator('note_moyenne')
    def validate_note(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError('La note doit être entre 0 et 10')
        return v

class LivreCreate(LivreBase):
    pass

class LivreUpdate(BaseModel):
    titre: Optional[str] = None
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
# MODÈLES AVEC RELATIONS
# ================================

class LivreComplet(Livre):
    """Livre avec toutes ses relations"""
    auteurs: List[Auteur] = []
    editeurs: List[Editeur] = []
    langues: List[Langue] = []
    sujets: List[Sujet] = []

class AuteurAvecLivres(Auteur):
    """Auteur avec ses livres"""
    livres: List[Livre] = []

class EditeurAvecLivres(Editeur):
    """Editeur avec ses livres"""
    livres: List[Livre] = []

# ================================
# MODÈLES DE LIAISON (Tables intermédiaires)
# ================================

class LivreAuteurBase(BaseModel):
    id_livre: int
    id_auteur: int

class LivreAuteur(LivreAuteurBase):
    date_ajout: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LivreEditeurBase(BaseModel):
    id_livre: int
    id_editeur: int

class LivreEditeur(LivreEditeurBase):
    date_ajout: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LivreLangueBase(BaseModel):
    id_livre: int
    id_langue: int

class LivreLangue(LivreLangueBase):
    date_ajout: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LivreSujetBase(BaseModel):
    id_livre: int
    id_sujet: int

class LivreSujet(LivreSujetBase):
    date_ajout: datetime
    date_modification: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ================================
# MODÈLES DE RECHERCHE ET STATISTIQUES
# ================================

class RechercheParams(BaseModel):
    """Paramètres de recherche pour les livres"""
    titre: Optional[str] = None
    auteur: Optional[str] = None
    editeur: Optional[str] = None
    annee_min: Optional[int] = None
    annee_max: Optional[int] = None
    langue: Optional[str] = None
    sujet: Optional[str] = None
    isbn: Optional[str] = None
    note_min: Optional[float] = None

class StatistiquesLivres(BaseModel):
    """Statistiques de la base de données"""
    total_livres: int
    total_auteurs: int
    total_editeurs: int
    total_langues: int
    total_sujets: int
    livre_plus_recent: Optional[int] = None
    livre_plus_ancien: Optional[int] = None
    note_moyenne_globale: Optional[float] = None
    
# ================================
# MODÈLES DE RÉPONSE API
# ================================

class PaginatedLivres(BaseModel):
    """Réponse paginée pour les livres"""
    livres: List[Livre]
    total: int
    page: int
    par_page: int
    total_pages: int

class APIResponse(BaseModel):
    """Réponse API générique"""
    success: bool
    message: str
    data: Optional[dict] = None 