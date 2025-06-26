#!/usr/bin/env python3
"""
Script pour diagnostiquer et résoudre les problèmes de mémoire PostgreSQL
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, shell=True):
    """Exécuter une commande système"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_postgresql_status():
    """Vérifier le statut de PostgreSQL"""
    print("🔍 Vérification du statut PostgreSQL...")
    
    # Vérifier les processus PostgreSQL
    success, stdout, stderr = run_command("tasklist | findstr postgres")
    if success and stdout:
        print("✅ PostgreSQL semble être en cours d'exécution")
        print(f"Processus trouvés:\n{stdout}")
    else:
        print("⚠️ Aucun processus PostgreSQL trouvé")
    
    return success

def check_shared_memory():
    """Vérifier la mémoire partagée"""
    print("\n🧠 Vérification de la mémoire partagée...")
    
    # Sur Windows, vérifier les segments de mémoire partagée
    success, stdout, stderr = run_command('wmic process where "name=\'postgres.exe\'" get ProcessId,PageFileUsage,WorkingSetSize /format:table')
    
    if success:
        print("📊 Utilisation mémoire PostgreSQL:")
        print(stdout)
    else:
        print("❌ Impossible de vérifier la mémoire partagée")

def cleanup_postgresql():
    """Nettoyer PostgreSQL"""
    print("\n🧹 Nettoyage PostgreSQL...")
    
    # Commandes de nettoyage
    cleanup_commands = [
        "echo Arrêt forcé des processus PostgreSQL...",
        "taskkill /F /IM postgres.exe /T 2>nul || echo Aucun processus PostgreSQL à arrêter",
        "taskkill /F /IM pg_ctl.exe /T 2>nul || echo Aucun pg_ctl à arrêter",
        "echo Nettoyage des fichiers temporaires...",
        "del /Q /S %TEMP%\\postgresql* 2>nul || echo Aucun fichier temp PostgreSQL"
    ]
    
    for cmd in cleanup_commands:
        print(f"Exécution: {cmd}")
        success, stdout, stderr = run_command(cmd)
        if stdout:
            print(f"  Sortie: {stdout.strip()}")
        if stderr and "echo" not in cmd:
            print(f"  Erreur: {stderr.strip()}")

def suggest_postgresql_config():
    """Suggérer une configuration PostgreSQL optimisée"""
    print("\n⚙️ Configuration PostgreSQL suggérée:")
    
    config_suggestions = """
# postgresql.conf - Configuration optimisée pour éviter les problèmes mémoire

# Mémoire partagée réduite
shared_buffers = 128MB                 # Au lieu de valeurs plus élevées
effective_cache_size = 1GB             # Ajuster selon votre RAM
work_mem = 4MB                         # Réduit pour éviter la surcharge
maintenance_work_mem = 64MB            # Réduit

# Connexions limitées
max_connections = 20                   # Réduit drastiquement

# Mémoire partagée système
shared_preload_libraries = ''          # Désactiver pour réduire l'utilisation

# Logging pour diagnostiquer
log_min_messages = warning
log_min_error_statement = error
log_min_duration_statement = 1000     # Log requêtes > 1s

# Checkpoints plus fréquents mais plus petits
checkpoint_segments = 3               # Réduit
checkpoint_completion_target = 0.5

# Désactiver certaines fonctionnalités pour économiser la mémoire
autovacuum = off                      # Temporairement
fsync = off                           # DANGER: uniquement pour dev/test
synchronous_commit = off              # DANGER: uniquement pour dev/test
"""
    
    print(config_suggestions)
    
    print("\n💡 Instructions pour appliquer cette configuration:")
    print("1. Trouvez votre fichier postgresql.conf")
    print("2. Sauvegardez-le avant modification")
    print("3. Modifiez les paramètres ci-dessus")
    print("4. Redémarrez PostgreSQL")
    print("\n⚠️ ATTENTION: fsync=off et synchronous_commit=off sont DANGEREUX en production!")

def restart_postgresql_service():
    """Redémarrer le service PostgreSQL"""
    print("\n🔄 Tentative de redémarrage PostgreSQL...")
    
    # Chercher les services PostgreSQL
    success, stdout, stderr = run_command('sc query type= service | findstr /i "postgresql"')
    
    if success and stdout:
        print("Services PostgreSQL trouvés:")
        print(stdout)
        
        # Essayer de redémarrer
        restart_commands = [
            'net stop "postgresql-x64-14" 2>nul || echo Service non trouvé avec ce nom',
            'timeout /t 5',
            'net start "postgresql-x64-14" 2>nul || echo Impossible de démarrer avec ce nom'
        ]
        
        for cmd in restart_commands:
            print(f"Exécution: {cmd}")
            success, stdout, stderr = run_command(cmd)
            if stdout:
                print(f"  Sortie: {stdout.strip()}")
    else:
        print("❌ Aucun service PostgreSQL trouvé")

def create_lightweight_test():
    """Créer un test léger pour PostgreSQL"""
    test_script = """
import psycopg2
import os

# Configuration allégée pour test
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")

def test_light_connection():
    try:
        # Connexion avec paramètres optimisés
        conn = psycopg2.connect(
            DATABASE_URL,
            options="-c default_transaction_isolation=autocommit"
        )
        
        cursor = conn.cursor()
        
        # Requête ultra-simple
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        
        print(f"✅ Test PostgreSQL réussi: {result}")
        
        # Test de la table livre (simple)
        cursor.execute("SELECT COUNT(*) FROM livre LIMIT 1")
        count = cursor.fetchone()[0]
        print(f"📚 Nombre de livres: {count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    test_light_connection()
"""
    
    with open("test_postgresql_light.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("\n📝 Script de test léger créé: test_postgresql_light.py")
    print("Utilisez ce script pour tester PostgreSQL avec une charge minimale")

def main():
    """Fonction principale"""
    print("🚑 Script de diagnostic et réparation PostgreSQL")
    print("=" * 50)
    
    # 1. Vérifier le statut
    check_postgresql_status()
    
    # 2. Vérifier la mémoire
    check_shared_memory()
    
    # 3. Proposer le nettoyage
    response = input("\n🧹 Voulez-vous nettoyer PostgreSQL ? (y/n): ")
    if response.lower() in ['y', 'yes', 'o', 'oui']:
        cleanup_postgresql()
    
    # 4. Proposer le redémarrage
    response = input("\n🔄 Voulez-vous redémarrer PostgreSQL ? (y/n): ")
    if response.lower() in ['y', 'yes', 'o', 'oui']:
        restart_postgresql_service()
    
    # 5. Afficher la configuration suggérée
    suggest_postgresql_config()
    
    # 6. Créer le test léger
    create_lightweight_test()
    
    print("\n✅ Diagnostic terminé!")
    print("\n💡 Solutions recommandées:")
    print("1. Utilisez les endpoints /hybrid-lite/* pour des requêtes optimisées")
    print("2. Limitez les résultats à 5-10 par requête")
    print("3. Évitez les JOINs complexes")
    print("4. Redémarrez votre système si le problème persiste")

if __name__ == "__main__":
    main() 