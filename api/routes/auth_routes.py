from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any

from database.database import get_db
from database.crud import user_crud
from models.models import User, UserCreate, Token
from auth.auth import (
    verify_password, 
    create_access_token, 
    get_current_active_user,
    get_password_hash
)
from config.config import settings

# Router d'authentification
auth_router = APIRouter(prefix="/auth", tags=["Authentification"])

@auth_router.post("/register", response_model=User)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    # Vérifier si l'utilisateur existe déjà
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Créer l'utilisateur
    return user_crud.create_user(db=db, user=user)

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Connexion et génération de token JWT"""
    # Authentifier l'utilisateur (username = email dans notre cas)
    user = user_crud.get_user_by_email(db, email=form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer le token d'accès
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,  # en secondes
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": f"{user.first_name} {user.last_name}"
        }
    }

@auth_router.post("/login", response_model=Token)
async def login_json(
    credentials: Dict[str, str],
    db: Session = Depends(get_db)
):
    """Connexion avec JSON (email/password)"""
    email = credentials.get("email")
    password = credentials.get("password")
    
    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email et mot de passe requis"
        )
    
    # Authentifier l'utilisateur
    user = user_crud.get_user_by_email(db, email=email)
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # Créer le token d'accès
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": f"{user.first_name} {user.last_name}"
        }
    }

@auth_router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Récupérer les informations de l'utilisateur connecté"""
    return current_user

@auth_router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """Rafraîchir le token JWT"""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": f"{current_user.first_name} {current_user.last_name}"
        }
    }

@auth_router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Déconnexion (côté client, invalidation du token)"""
    return {
        "message": "Déconnexion réussie",
        "detail": "Supprimez le token côté client"
    }

# Routes d'administration (exemple)
@auth_router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    """Route protégée par JWT - exemple"""
    return {
        "message": f"Bonjour {current_user.first_name} {current_user.last_name}!",
        "user_id": current_user.id,
        "email": current_user.email,
        "access_level": "authenticated"
    } 