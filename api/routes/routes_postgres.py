from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.models import Item, ItemCreate, ItemUpdate, User
from database.database import get_db
from database.crud import item_crud, user_crud
from auth.auth import require_jwt, optional_jwt

# Router pour les endpoints PostgreSQL
postgres_router = APIRouter(prefix="/postgres", tags=["PostgreSQL"])

# Note: Les anciens endpoints books/ ont été supprimés car nous utilisons maintenant
# la vraie structure de base de données avec /livres (voir routes_postgres_livres.py)

# Endpoints pour les statistiques PostgreSQL (anciennes tables génériques)
@postgres_router.get("/statistics/")
async def get_postgres_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """Récupérer les statistiques PostgreSQL des anciennes tables génériques (legacy)"""
    try:
        total_users = user_crud.count_users(db)
    except:
        total_users = 0  # Table users n'existe peut-être plus
    
    try:
        total_books = item_crud.count_items(db)
    except:
        total_books = 0  # Table books n'existe peut-être plus
    
    return {
        "total_users": total_users,
        "total_books": total_books,
        "timestamp": datetime.now(),
        "database": "PostgreSQL (tables legacy)",
        "note": "Utilisez /postgres/livres/stats/general pour les vraies statistiques"
    }

# Endpoints pour les utilisateurs (conservés pour l'authentification)
@postgres_router.get("/users/", response_model=List[User])
async def get_postgres_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """Récupérer la liste des utilisateurs depuis PostgreSQL (table auth uniquement)"""
    try:
        return user_crud.get_users(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur accès table users: {str(e)}")

@postgres_router.get("/users/{user_id}", response_model=User)
async def get_postgres_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_jwt)
):
    """Récupérer un utilisateur par ID depuis PostgreSQL (table auth uniquement)"""
    try:
        user = user_crud.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé dans PostgreSQL")
        return user
    except Exception as e:
        if "404" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Erreur accès table users: {str(e)}")

# Note: L'endpoint /users/{user_id}/books/ a été supprimé car il n'y a plus de liaison
# entre users et books. Utilisez /postgres/livres/ pour accéder aux livres directement.