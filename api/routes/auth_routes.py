from datetime import timedelta, datetime
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

# 🔐 Router d'authentification complet (7 endpoints)
auth_router = APIRouter(prefix="/auth", tags=["🔐 Authentification JWT & OAuth2"])

@auth_router.post("/register", response_model=User)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """📝 Inscription d'un nouvel utilisateur"""
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
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """🔐 Connexion OAuth2 (avec form-data username/password)"""
    # OAuth2 utilise 'username' mais nous utilisons l'email
    email = form_data.username
    password = form_data.password
    
    # Authentifier l'utilisateur
    user = user_crud.get_user_by_email(db, email=email)
    
    if not user or not verify_password(password, user.hashed_password):
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
        "expires_in": settings.access_token_expire_minutes * 60,
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
    """🔐 Connexion JSON (avec email/password en JSON)"""
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
    """👤 Récupérer les informations de l'utilisateur connecté"""
    return current_user

@auth_router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """🔄 Rafraîchir le token JWT"""
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
    """🚪 Déconnexion (côté client, invalidation du token)"""
    return {
        "message": "✅ Déconnexion réussie",
        "detail": "Supprimez le token côté client",
        "user_email": current_user.email
    }

@auth_router.delete("/delete-account")
async def delete_account(
    password_confirmation: Dict[str, str],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """🗑️ Supprimer définitivement le compte utilisateur"""
    
    # Vérifier le mot de passe pour sécuriser la suppression
    password = password_confirmation.get("password")
    if not password:
        raise HTTPException(
            status_code=400,
            detail="Mot de passe requis pour confirmer la suppression"
        )
    
    # Vérifier le mot de passe actuel
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect"
        )
    
    try:
        # Supprimer l'utilisateur de la base de données
        user_crud.delete_user(db, user_id=current_user.id)
        
        return {
            "message": "✅ Compte supprimé avec succès",
            "detail": "Votre compte et toutes vos données ont été définitivement supprimés",
            "deleted_user": {
                "id": current_user.id,
                "email": current_user.email,
                "deleted_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression du compte: {str(e)}"
        )

# ✅ AUTHENTIFICATION COMPLÈTE :
# 
# 🔐 OAuth2 + JWT + JSON - Support complet pour différents clients
# ✅ Garde OAuth2 /auth/token (important pour l'intégration)
# ✅ Ajoute JSON /auth/login (pratique pour les tests)
# ✅ Suppression de compte sécurisée
# ✅ Gestion complète des utilisateurs

# 📊 ENDPOINTS FINAUX (7 total) :
# 1. POST /auth/register - Inscription
# 2. POST /auth/token - Connexion OAuth2 (form-data)
# 3. POST /auth/login - Connexion JSON (email/password)
# 4. GET /auth/me - Profil utilisateur
# 5. POST /auth/refresh - Rafraîchir token
# 6. POST /auth/logout - Déconnexion
# 7. DELETE /auth/delete-account - Suppression compte 