#!/usr/bin/env python3
"""
Script de sauvegarde du schéma test avant import pipeline
========================================================

Usage:
    python backup_schema_test.py
    python backup_schema_test.py --complet
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path
import argparse

def backup_avec_pg_dump():
    """Sauvegarde complète avec pg_dump"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_schema_test_{timestamp}.sql"
    
    print("📦 Sauvegarde complète avec pg_dump...")
    
    try:
        # Commande pg_dump pour sauvegarder le schéma test
        cmd = [
            "pg_dump",
            "-h", "localhost",
            "-U", "postgres", 
            "-n", "test",  # Schéma test uniquement
            "--no-password",  # Éviter prompt mot de passe
            "databook"
        ]
        
        print(f"🔄 Exécution: {' '.join(cmd)}")
        print(f"📄 Fichier de sortie: {backup_file}")
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            size = Path(backup_file).stat().st_size / 1024
            print(f"✅ Sauvegarde réussie: {backup_file} ({size:.1f} KB)")
            return backup_file
        else:
            print(f"❌ Erreur pg_dump: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("❌ pg_dump non trouvé. Installer PostgreSQL client tools.")
        return None
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return None

def backup_avec_python():
    """Sauvegarde avec Python/SQLAlchemy"""
    print("🐍 Sauvegarde avec Python...")
    
    try:
        from sqlalchemy import create_engine, text
        import pandas as pd
        
        # Connexion à la base
        engine = create_engine("postgresql://postgres:postgres@localhost:5432/databook")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f"backup_test_{timestamp}")
        backup_dir.mkdir(exist_ok=True)
        
        # Tables à sauvegarder
        tables = [
            'livre', 'auteur', 'editeur', 'langue', 'sujet',
            'livre_auteur', 'livre_editeur', 'livre_langue', 'livre_sujet',
            'books', 'users', 'extraction_log'
        ]
        
        total_rows = 0
        
        with engine.connect() as conn:
            for table in tables:
                try:
                    # Vérifier si la table existe
                    result = conn.execute(text(f"""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_schema = 'test' AND table_name = '{table}'
                    """))
                    
                    if result.fetchone()[0] == 0:
                        print(f"⚠️ Table test.{table} n'existe pas - ignorée")
                        continue
                    
                    # Exporter la table
                    df = pd.read_sql(f"SELECT * FROM test.{table}", conn)
                    rows = len(df)
                    total_rows += rows
                    
                    # Sauvegarder en CSV
                    csv_file = backup_dir / f"{table}.csv"
                    df.to_csv(csv_file, index=False, encoding='utf-8')
                    
                    print(f"✅ {table}: {rows} lignes → {csv_file.name}")
                    
                except Exception as e:
                    print(f"⚠️ Erreur table {table}: {e}")
        
        print(f"✅ Sauvegarde Python terminée: {total_rows} lignes total dans {backup_dir}")
        return str(backup_dir)
        
    except ImportError as e:
        print(f"❌ Modules manquants: {e}")
        print("💡 Installer: pip install sqlalchemy pandas psycopg2-binary")
        return None
    except Exception as e:
        print(f"❌ Erreur sauvegarde Python: {e}")
        return None

def compter_donnees_schema_test():
    """Compte les données dans le schéma test"""
    print("📊 Analyse du schéma test...")
    
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine("postgresql://postgres:postgres@localhost:5432/databook")
        
        with engine.connect() as conn:
            # Lister les tables du schéma test
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'test'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if not tables:
                print("⚠️ Aucune table trouvée dans le schéma test")
                return 0
            
            total_rows = 0
            print(f"📋 Tables dans le schéma test:")
            
            for table in tables:
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM test.{table}"))
                    count = count_result.fetchone()[0]
                    total_rows += count
                    print(f"   • {table}: {count:,} lignes")
                except Exception as e:
                    print(f"   • {table}: erreur comptage ({e})")
            
            print(f"\n📊 Total: {total_rows:,} lignes dans {len(tables)} tables")
            return total_rows
            
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description="Sauvegarde schéma test")
    parser.add_argument('--complet', action='store_true', 
                       help='Sauvegarde complète (pg_dump + Python)')
    parser.add_argument('--count-only', action='store_true', 
                       help='Compter les données seulement')
    
    args = parser.parse_args()
    
    print("🔒 SAUVEGARDE SCHÉMA TEST")
    print("=" * 40)
    
    # Compter les données existantes
    total_rows = compter_donnees_schema_test()
    
    if args.count_only:
        return 0
    
    if total_rows == 0:
        print("💡 Schéma test vide - pas besoin de sauvegarde")
        return 0
    
    print(f"\n🎯 Données à sauvegarder: {total_rows:,} lignes")
    
    if not args.complet:
        # Demander confirmation
        reponse = input("\nContinuer la sauvegarde? (o/N): ").strip().lower()
        if reponse != 'o':
            print("⏭️ Sauvegarde annulée")
            return 0
    
    # Tenter pg_dump d'abord
    backup_pg = backup_avec_pg_dump()
    
    if args.complet or not backup_pg:
        # Sauvegarde Python si demandée ou si pg_dump a échoué
        backup_py = backup_avec_python()
        
        if backup_py and not backup_pg:
            print(f"✅ Sauvegarde Python réussie: {backup_py}")
    
    if backup_pg:
        print(f"\n🎉 Sauvegarde terminée: {backup_pg}")
        print("💡 Pour restaurer: psql -h localhost -U postgres databook < backup_file.sql")
    elif args.complet:
        print("\n🎉 Sauvegarde Python terminée")
    else:
        print("\n❌ Échec de la sauvegarde")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 