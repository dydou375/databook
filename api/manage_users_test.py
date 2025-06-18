"""
🔐 Script de gestion des utilisateurs dans le schéma test
Permet de visualiser, créer et gérer les utilisateurs JWT stockés en PostgreSQL
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent))

from database.database import SessionLocal, UserDB, ensure_test_schema, check_test_schema_users
from database.crud import user_crud
from models.models import UserCreate
from sqlalchemy import text
import argparse

def list_users():
    """Lister tous les utilisateurs du schéma test"""
    print("👥 Liste des utilisateurs dans le schéma test")
    print("=" * 50)
    
    try:
        db = SessionLocal()
        
        # Requête directe sur le schéma test
        users = db.execute(text("""
            SELECT id, email, first_name, last_name, is_active, created_at,
                   LEFT(hashed_password, 30) || '...' as password_preview
            FROM test.users 
            ORDER BY created_at DESC
        """)).fetchall()
        
        if not users:
            print("📭 Aucun utilisateur trouvé dans test.users")
            return
        
        for i, user in enumerate(users, 1):
            print(f"\n{i}. 👤 {user.first_name} {user.last_name}")
            print(f"   📧 Email: {user.email}")
            print(f"   🆔 ID: {user.id}")
            print(f"   ✅ Actif: {'Oui' if user.is_active else 'Non'}")
            print(f"   📅 Créé: {user.created_at}")
            print(f"   🔐 Hash: {user.password_preview}")
        
        print(f"\n📊 Total: {len(users)} utilisateurs")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        db.close()

def create_test_user(email: str, password: str, first_name: str, last_name: str):
    """Créer un utilisateur de test"""
    print(f"👤 Création de l'utilisateur: {first_name} {last_name}")
    
    try:
        db = SessionLocal()
        
        # Vérifier si l'email existe déjà
        existing_user = user_crud.get_user_by_email(db, email)
        if existing_user:
            print(f"⚠️ Un utilisateur avec l'email {email} existe déjà!")
            return False
        
        # Créer l'utilisateur
        user_data = UserCreate(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        new_user = user_crud.create_user(db, user_data)
        
        print(f"✅ Utilisateur créé avec succès!")
        print(f"   🆔 ID: {new_user.id}")
        print(f"   📧 Email: {new_user.email}")
        print(f"   👤 Nom: {new_user.first_name} {new_user.last_name}")
        print(f"   🔐 Mot de passe haché: {new_user.hashed_password[:30]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False
    finally:
        db.close()

def verify_schema():
    """Vérifier l'état du schéma test"""
    print("🔍 Vérification du schéma test")
    print("=" * 50)
    
    try:
        db = SessionLocal()
        
        # Vérifier le schéma
        schema_exists = db.execute(text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'test'
        """)).fetchone()
        
        if schema_exists:
            print("✅ Schéma 'test' trouvé")
        else:
            print("❌ Schéma 'test' introuvable")
            print("🔧 Création du schéma...")
            ensure_test_schema()
        
        # Vérifier les tables
        tables = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'test'
            ORDER BY table_name
        """)).fetchall()
        
        print(f"\n📋 Tables dans le schéma test: {len(tables)}")
        for table in tables:
            print(f"   • {table.table_name}")
        
        # Vérifier la table users spécifiquement
        if any(t.table_name == 'users' for t in tables):
            print("\n✅ Table 'users' trouvée dans le schéma test")
            
            # Compter les utilisateurs
            count = db.execute(text("SELECT COUNT(*) as count FROM test.users")).fetchone()
            print(f"👥 Nombre d'utilisateurs: {count.count}")
            
        else:
            print("\n❌ Table 'users' introuvable dans le schéma test")
            print("🔧 Initialisation nécessaire: python -c 'from database.database import init_db; init_db()'")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        db.close()

def delete_user(email: str):
    """Supprimer un utilisateur par email"""
    print(f"🗑️ Suppression de l'utilisateur: {email}")
    
    try:
        db = SessionLocal()
        
        # Trouver l'utilisateur
        user = user_crud.get_user_by_email(db, email)
        if not user:
            print(f"⚠️ Utilisateur {email} introuvable")
            return False
        
        # Supprimer
        success = user_crud.delete_user(db, user.id)
        
        if success:
            print(f"✅ Utilisateur {email} supprimé avec succès")
        else:
            print(f"❌ Erreur lors de la suppression")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        db.close()

def main():
    """Interface en ligne de commande"""
    parser = argparse.ArgumentParser(description="Gestion des utilisateurs JWT dans le schéma test")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    # Commande list
    subparsers.add_parser("list", help="Lister tous les utilisateurs")
    
    # Commande verify
    subparsers.add_parser("verify", help="Vérifier l'état du schéma test")
    
    # Commande create
    create_parser = subparsers.add_parser("create", help="Créer un utilisateur")
    create_parser.add_argument("email", help="Email de l'utilisateur")
    create_parser.add_argument("password", help="Mot de passe")
    create_parser.add_argument("first_name", help="Prénom")
    create_parser.add_argument("last_name", help="Nom")
    
    # Commande delete
    delete_parser = subparsers.add_parser("delete", help="Supprimer un utilisateur")
    delete_parser.add_argument("email", help="Email de l'utilisateur à supprimer")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🔐 Gestionnaire d'utilisateurs JWT - Schéma test")
        print("=" * 50)
        print("Commandes disponibles:")
        print("  python manage_users_test.py list")
        print("  python manage_users_test.py verify")
        print("  python manage_users_test.py create email@test.com motdepasse Prénom Nom")
        print("  python manage_users_test.py delete email@test.com")
        return
    
    if args.command == "list":
        list_users()
    elif args.command == "verify":
        verify_schema()
    elif args.command == "create":
        create_test_user(args.email, args.password, args.first_name, args.last_name)
    elif args.command == "delete":
        delete_user(args.email)

if __name__ == "__main__":
    main() 