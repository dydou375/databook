from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from auth.auth import get_current_active_user, get_api_key
from models.models import User
from database.database import get_db

class PermissionLevel:
    """Niveaux de permission pour l'API"""
    PUBLIC = "public"           # Accès libre
    AUTHENTICATED = "auth"      # JWT requis
    API_KEY = "api_key"        # Clé API requise (legacy)
    ADMIN = "admin"            # Admin seulement

def require_auth(current_user: User = Depends(get_current_active_user)):
    """Exiger une authentification JWT valide"""
    return current_user

def require_api_key_legacy(api_key: str = Depends(get_api_key)):
    """Exiger une clé API (système legacy)"""
    return api_key

def optional_auth(current_user: Optional[User] = Depends(get_current_active_user)):
    """Authentification optionnelle (public + fonctionnalités bonus si connecté)"""
    return current_user

async def require_admin(current_user: User = Depends(get_current_active_user)):
    """Exiger les droits administrateur"""
    # Vous pouvez ajouter un champ 'is_admin' dans votre modèle User
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits administrateur requis"
        )
    return current_user

def hybrid_auth(
    current_user: Optional[User] = Depends(get_current_active_user),
    api_key: Optional[str] = Depends(get_api_key)
):
    """Authentification hybride : JWT OU clé API"""
    if current_user:
        return {"type": "jwt", "user": current_user}
    elif api_key:
        return {"type": "api_key", "api_key": api_key}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT token ou clé API requis",
            headers={"WWW-Authenticate": "Bearer"}
        )

# Décorateurs de sécurité par niveau
class SecurityLevel:
    """Classes de sécurité pour différents types de données"""
    
    @staticmethod
    def public():
        """Données publiques - pas d'authentification"""
        return None
    
    @staticmethod
    def read_only():
        """Lecture seule - JWT recommandé mais pas obligatoire"""
        def dependency(current_user: Optional[User] = Depends(optional_auth)):
            return current_user
        return dependency
    
    @staticmethod
    def authenticated():
        """Lecture authentifiée - JWT obligatoire"""
        def dependency(current_user: User = Depends(require_auth)):
            return current_user
        return dependency
    
    @staticmethod
    def admin_only():
        """Administration - droits admin requis"""
        def dependency(current_user: User = Depends(require_admin)):
            return current_user
        return dependency
    
    @staticmethod
    def legacy_api():
        """Système legacy avec clé API"""
        def dependency(api_key: str = Depends(require_api_key_legacy)):
            return api_key
        return dependency

# Exemple d'utilisation des permissions
def check_read_permission(user: Optional[User], resource_type: str) -> bool:
    """Vérifier les permissions de lecture selon le type de ressource"""
    if resource_type == "public":
        return True
    elif resource_type == "books":
        return user is not None  # Connecté pour lire les livres
    elif resource_type == "admin":
        return user is not None and getattr(user, 'is_admin', False)
    return False

def check_write_permission(user: User, resource_type: str) -> bool:
    """Vérifier les permissions d'écriture"""
    if not user:
        return False
    
    if resource_type == "books":
        return True  # Tout utilisateur connecté peut écrire
    elif resource_type == "admin":
        return getattr(user, 'is_admin', False)
    return False 