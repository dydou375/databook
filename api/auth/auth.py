from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi.security.api_key import APIKeyHeader

from database.database import get_db
from database.crud import user_crud
from models.models import TokenData
from config.config import settings

# Configuration pour l'authentification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)  # auto_error=False pour auth optionnelle

# Configuration pour la clé API
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hacher un mot de passe"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Créer un token d'accès JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Récupérer l'utilisateur actuel à partir du token (optionnel - ne lève pas d'erreur si pas de token)"""
    if token is None:
        return None
        
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
    except JWTError:
        return None
    
    user = user_crud.get_user_by_email(db, email=token_data.email)
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Récupérer l'utilisateur actuel à partir du token (obligatoire)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token is None:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = user_crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Récupérer l'utilisateur actuel actif"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user

async def get_current_active_user_optional(current_user = Depends(get_current_user_optional)):
    """Récupérer l'utilisateur actuel actif (optionnel)"""
    if current_user and not current_user.is_active:
        return None  # Utilisateur inactif = pas d'utilisateur
    return current_user

async def get_api_key(api_key: str = Depends(api_key_header)):
    """Vérifier la clé API"""
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou manquante",
            headers={"WWW-Authenticate": "API-Key"},
        )
    return api_key

def require_api_key(api_key: str = Depends(get_api_key)):
    """Décorateur pour protéger les endpoints avec une clé API"""
    return api_key

# Nouvelles fonctions pour la migration JWT

def require_jwt(current_user = Depends(get_current_active_user)):
    """Exiger un token JWT valide (remplace require_api_key)"""
    return current_user

def optional_jwt(current_user = Depends(get_current_active_user_optional)):
    """JWT optionnel - pour les routes publiques avec fonctionnalités bonus si connecté"""
    return current_user 