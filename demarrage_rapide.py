#!/usr/bin/env python3
"""
DÉMARRAGE RAPIDE PIPELINE DATABOOK
=================================

Script de démarrage rapide pour lancer le pipeline avec configuration automatique.
Détecte automatiquement l'environnement et propose les meilleures options.

Usage:
    python demarrage_rapide.py
    python demarrage_rapide.py --auto
    python demarrage_rapide.py --config minimal
"""

import sys
import argparse
from pathlib import Path
import subprocess
import json

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from pipeline_master import PipelineMaster
except ImportError:
    print("❌ Impossible d'importer pipeline_master.py")
    print("🔧 Assurez-vous que le fichier pipeline_master.py est présent")
    sys.exit(1)

class DemarrageRapide:
    """Gestionnaire de démarrage rapide"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent
        
        # Configurations prédéfinies
        self.configs = {
            'minimal': {
                'description': '🚀 Configuration minimale - test rapide',
                'api_max_livres': 100,
                'scrapping_max': 50,
                'etapes': ['api', 'verification']
            },
            'standard': {
                'description': '📊 Configuration standard - usage normal',
                'api_max_livres': 1000,
                'scrapping_max': 500,
                'etapes': ['api', 'nettoyage', 'postgresql', 'mongodb', 'verification']
            },
            'complet': {
                'description': '🎯 Configuration complète - toutes les données',
                'api_max_livres': 5000,
                'scrapping_max': 2000,
                'etapes': ['api', 'scrapping', 'nettoyage', 'postgresql', 'mongodb', 'verification']
            }
        }

    def detecter_environnement(self):
        """Détecte automatiquement l'environnement et les capacités"""
        print("🔍 DÉTECTION AUTOMATIQUE DE L'ENVIRONNEMENT")
        print("-" * 50)
        
        environnement = {}
        
        # Vérifier Python
        version_python = sys.version_info
        environnement['python'] = f"{version_python.major}.{version_python.minor}.{version_python.micro}"
        print(f"🐍 Python: {environnement['python']}")
        
        # Vérifier les modules essentiels
        modules_requis = ['requests', 'pandas', 'bs4', 'sqlalchemy', 'psycopg2', 'pymongo']
        modules_ok = []
        modules_manquants = []
        
        for module in modules_requis:
            try:
                __import__(module)
                modules_ok.append(module)
                print(f"✅ {module}")
            except ImportError:
                modules_manquants.append(module)
                print(f"❌ {module}")
        
        environnement['modules_ok'] = modules_ok
        environnement['modules_manquants'] = modules_manquants
        
        # Vérifier l'espace disque
        try:
            import shutil
            espace_libre = shutil.disk_usage(self.workspace).free / (1024**3)
            environnement['espace_libre_gb'] = round(espace_libre, 1)
            print(f"💾 Espace libre: {espace_libre:.1f} GB")
        except:
            environnement['espace_libre_gb'] = 0
            print("💾 Espace libre: Impossible de détecter")
        
        # Vérifier les dossiers existants
        dossiers = ['scripts', 'bdd', 'data']
        dossiers_ok = []
        for dossier in dossiers:
            if (self.workspace / dossier).exists():
                dossiers_ok.append(dossier)
                print(f"📁 {dossier}: ✅")
            else:
                print(f"📁 {dossier}: ❌")
        
        environnement['dossiers_ok'] = dossiers_ok
        
        return environnement

    def recommander_configuration(self, environnement):
        """Recommande une configuration basée sur l'environnement"""
        print("\n🎯 RECOMMANDATION AUTOMATIQUE")
        print("-" * 40)
        
        # Critères de recommandation
        if len(environnement['modules_manquants']) > 3:
            config_recommandee = 'minimal'
            raison = "Plusieurs modules manquants"
        elif environnement['espace_libre_gb'] < 5:
            config_recommandee = 'minimal'
            raison = "Espace disque limité"
        elif len(environnement['dossiers_ok']) < 2:
            config_recommandee = 'minimal'
            raison = "Structure de dossiers incomplète"
        elif environnement['espace_libre_gb'] > 20 and len(environnement['modules_ok']) >= 5:
            config_recommandee = 'complet'
            raison = "Environnement optimal détecté"
        else:
            config_recommandee = 'standard'
            raison = "Configuration équilibrée"
        
        print(f"💡 Configuration recommandée: {config_recommandee}")
        print(f"📋 Raison: {raison}")
        print(f"📝 Description: {self.configs[config_recommandee]['description']}")
        
        return config_recommandee

    def installer_dependances(self, modules_manquants):
        """Propose d'installer les dépendances manquantes"""
        if not modules_manquants:
            return True
            
        print(f"\n📦 MODULES MANQUANTS: {len(modules_manquants)}")
        print("-" * 40)
        
        # Correspondance modules -> packages pip
        pip_packages = {
            'requests': 'requests',
            'pandas': 'pandas',
            'bs4': 'beautifulsoup4',
            'sqlalchemy': 'sqlalchemy',
            'psycopg2': 'psycopg2-binary',
            'pymongo': 'pymongo'
        }
        
        packages_to_install = []
        for module in modules_manquants:
            if module in pip_packages:
                packages_to_install.append(pip_packages[module])
                print(f"📦 {module} -> pip install {pip_packages[module]}")
        
        if packages_to_install:
            print(f"\n💡 Commande d'installation complète:")
            print(f"pip install {' '.join(packages_to_install)}")
            
            reponse = input("\nInstaller automatiquement? (o/N): ").strip().lower()
            if reponse == 'o':
                try:
                    print("📥 Installation en cours...")
                    subprocess.run([
                        sys.executable, '-m', 'pip', 'install'
                    ] + packages_to_install, check=True)
                    print("✅ Installation terminée")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"❌ Erreur d'installation: {e}")
                    return False
        
        return False

    def configurer_pipeline(self, nom_config):
        """Configure le pipeline avec une configuration prédéfinie"""
        config = self.configs[nom_config]
        
        pipeline = PipelineMaster()
        
        # Appliquer la configuration
        pipeline.config['api']['max_livres_par_categorie'] = config['api_max_livres']
        pipeline.config['scrapping']['max_livres_babelio'] = config['scrapping_max']
        
        return pipeline, config

    def executer_etapes_selectionnees(self, pipeline, etapes):
        """Exécute les étapes sélectionnées"""
        print(f"\n🚀 EXÉCUTION DE {len(etapes)} ÉTAPES")
        print("=" * 50)
        
        mapping_etapes = {
            'api': ('📡 Récupération API', pipeline.executer_etape_api),
            'scrapping': ('🕷️ Scrapping Babelio', pipeline.executer_etape_scrapping),
            'nettoyage': ('📊 Nettoyage CSV', pipeline.executer_etape_nettoyage_csv),
            'postgresql': ('🗄️ PostgreSQL', pipeline.executer_etape_postgresql),
            'mongodb': ('🍃 MongoDB', pipeline.executer_etape_mongodb),
            'verification': ('✅ Vérification', pipeline.verifier_environnement)
        }
        
        resultats = {}
        
        for etape in etapes:
            if etape in mapping_etapes:
                nom, fonction = mapping_etapes[etape]
                print(f"\n▶️ {nom}")
                print("-" * 40)
                
                try:
                    succes = fonction()
                    resultats[etape] = 'succès' if succes else 'avertissement'
                    status_icon = "✅" if succes else "⚠️"
                    print(f"{status_icon} {nom} terminé")
                except Exception as e:
                    resultats[etape] = f'erreur: {e}'
                    print(f"❌ Erreur dans {nom}: {e}")
        
        return resultats

    def mode_interactif(self):
        """Mode interactif avec menus"""
        print("\n🎯 MODE INTERACTIF")
        print("=" * 50)
        
        # 1. Détecter l'environnement
        environnement = self.detecter_environnement()
        
        # 2. Recommander une configuration
        config_recommandee = self.recommander_configuration(environnement)
        
        # 3. Proposer l'installation des dépendances
        if environnement['modules_manquants']:
            print(f"\n⚠️ {len(environnement['modules_manquants'])} modules manquants détectés")
            self.installer_dependances(environnement['modules_manquants'])
        
        # 4. Choisir la configuration
        print(f"\n📋 CONFIGURATIONS DISPONIBLES:")
        for nom, config in self.configs.items():
            icone = "👈" if nom == config_recommandee else "  "
            print(f"{icone} {nom}: {config['description']}")
        
        choix_config = input(f"\nChoisir configuration [{config_recommandee}]: ").strip() or config_recommandee
        
        if choix_config not in self.configs:
            print(f"❌ Configuration '{choix_config}' invalide, utilisation de '{config_recommandee}'")
            choix_config = config_recommandee
        
        # 5. Configurer et lancer
        pipeline, config = self.configurer_pipeline(choix_config)
        resultats = self.executer_etapes_selectionnees(pipeline, config['etapes'])
        
        # 6. Résumé final
        print(f"\n📊 RÉSUMÉ - Configuration: {choix_config}")
        print("=" * 50)
        for etape, resultat in resultats.items():
            print(f"• {etape}: {resultat}")

    def mode_auto(self, config_name=None):
        """Mode automatique sans intervention"""
        print("\n🤖 MODE AUTOMATIQUE")
        print("=" * 50)
        
        # Détection automatique
        environnement = self.detecter_environnement()
        
        if not config_name:
            config_name = self.recommander_configuration(environnement)
        
        print(f"\n🚀 Lancement automatique avec configuration: {config_name}")
        
        # Installation automatique des dépendances si nécessaire
        if environnement['modules_manquants']:
            print("📦 Installation automatique des dépendances...")
            if not self.installer_dependances(environnement['modules_manquants']):
                print("⚠️ Installation échouée, poursuite avec modules disponibles")
        
        # Configuration et exécution
        pipeline, config = self.configurer_pipeline(config_name)
        resultats = self.executer_etapes_selectionnees(pipeline, config['etapes'])
        
        return resultats

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Démarrage rapide Pipeline DataBook")
    parser.add_argument('--auto', action='store_true', help='Mode automatique')
    parser.add_argument('--config', choices=['minimal', 'standard', 'complet'], 
                       help='Configuration prédéfinie')
    parser.add_argument('--status', action='store_true', help='Afficher uniquement le status')
    
    args = parser.parse_args()
    
    print("🚀 DÉMARRAGE RAPIDE PIPELINE DATABOOK")
    print("=" * 60)
    
    demarrage = DemarrageRapide()
    
    try:
        if args.status:
            # Mode status uniquement
            pipeline = PipelineMaster()
            pipeline.afficher_status()
        elif args.auto:
            # Mode automatique
            demarrage.mode_auto(args.config)
        else:
            # Mode interactif
            demarrage.mode_interactif()
            
    except KeyboardInterrupt:
        print("\n⚠️ Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return 1
    
    print("\n✅ Démarrage rapide terminé")
    return 0

if __name__ == "__main__":
    sys.exit(main())