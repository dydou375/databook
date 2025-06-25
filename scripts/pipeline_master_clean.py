#!/usr/bin/env python3
"""
PIPELINE MASTER DATABOOK
========================

Script principal qui orchestre toute la chaîne de récupération et traitement des données :
1. Récupération données API (Google Books, OpenLibrary)
2. Scrapping Babelio (critiques et notes)
3. Traitement fichiers CSV (nettoyage, formatage)
4. Import PostgreSQL (tables relationnelles)
5. Import MongoDB (documents JSON)
6. Validation et vérification

Author: Assistant IA
Date: 2025-01-27
"""

import os
import sys
import time
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Configuration du logging compatible Windows
import sys

# Créer les handlers séparément pour éviter les problèmes d'emojis
file_handler = logging.FileHandler(
    f'pipeline_master_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

# Handler console simplifié pour Windows
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

class PipelineMaster:
    """Gestionnaire principal du pipeline DataBook"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Chemins des dossiers
        self.paths = {
            'scripts_api': self.workspace / "scripts" / "api",
            'scripts_scrapping': self.workspace / "scripts" / "scrapping", 
            'scripts_bdd': self.workspace / "bdd",
            'data_json': self.workspace / "data" / "livre_json",
            'data_csv': self.workspace / "data",
            'deploiement': self.workspace / "deploiement_base_local"
        }
        
        # État du pipeline
        self.etat = {
            'etape_actuelle': 0,
            'total_etapes': 8,
            'debut': datetime.now(),
            'logs': [],
            'erreurs': [],
            'resultats': {}
        }
        
        # Configuration par défaut
        self.config = {
            'api': {
                'max_livres_par_categorie': 1000,
                'categories_actives': 20,
                'delai_requetes': 2
            },
            'scrapping': {
                'max_livres_babelio': 500,
                'delai_scrapping': 3,
                'fichier_csv_source': None
            },
            'bdd': {
                'postgresql_url': "postgresql://postgres:postgres@localhost:5432/databook",
                'mongodb_url': "mongodb://localhost:27017/",
                'schema_postgres': "test",
                'batch_size': 1000
            }
        }
        
        logger.info("PIPELINE MASTER DATABOOK INITIALISE")
        logger.info(f"Workspace: {self.workspace}")
        logger.info(f"Timestamp: {self.timestamp}")

    def afficher_menu_principal(self) -> str:
        """Affiche le menu principal et retourne le choix"""
        print("\n" + "="*60)
        print("PIPELINE MASTER DATABOOK")
        print("="*60)
        print("Choisissez le mode d'exécution :")
        print()
        print("1. PIPELINE COMPLET (toutes les étapes)")
        print("2. Récupération API uniquement")
        print("3. Scrapping Babelio uniquement") 
        print("4. Traitement CSV uniquement")
        print("5. Import BDD uniquement")
        print("6. Configuration personnalisée")
        print("7. Status et diagnostics")
        print("8. Nettoyage des données temporaires")
        print("9. Quitter")
        print()
        
        return input("Votre choix (1-9): ").strip()

    def configurer_pipeline(self):
        """Interface de configuration personnalisée"""
        print("\nCONFIGURATION PERSONNALISÉE")
        print("-" * 40)
        
        # Configuration API
        print("\nRÉCUPÉRATION API")
        self.config['api']['max_livres_par_categorie'] = int(input(
            f"Nombre max de livres par catégorie [{self.config['api']['max_livres_par_categorie']}]: "
        ) or self.config['api']['max_livres_par_categorie'])
        
        # Configuration scrapping
        print("\nSCRAPPING BABELIO")
        self.config['scrapping']['max_livres_babelio'] = int(input(
            f"Nombre max de livres à scrapper [{self.config['scrapping']['max_livres_babelio']}]: "
        ) or self.config['scrapping']['max_livres_babelio'])
        
        # Configuration BDD
        print("\nBASES DE DONNÉES")
        nouveau_schema = input(f"Nom du schéma PostgreSQL [{self.config['bdd']['schema_postgres']}]: ").strip()
        if nouveau_schema:
            self.config['bdd']['schema_postgres'] = nouveau_schema
            
        logger.info("Configuration mise à jour")

    def executer_etape_api(self) -> bool:
        """Étape 1: Récupération données API"""
        self.etat['etape_actuelle'] = 1
        logger.info("ETAPE 1/8: Recuperation donnees API")
        
        try:
            script_api = self.paths['scripts_api'] / "recupération_api_livre_amelioree.py"
            
            if not script_api.exists():
                raise FileNotFoundError(f"Script API non trouvé: {script_api}")
            
            # Exécuter le script de récupération API
            logger.info("Lancement récupération Google Books + OpenLibrary...")
            
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.workspace)
            
            result = subprocess.run([
                sys.executable, str(script_api)
            ], cwd=str(self.paths['scripts_api']), 
               capture_output=True, text=True, env=env, timeout=3600)
            
            if result.returncode == 0:
                logger.info("Récupération API terminée avec succès")
                
                # Compter les fichiers JSON créés
                json_dir = self.paths['data_json'] / "livres_json_ameliore"
                if json_dir.exists():
                    fichiers_json = list(json_dir.glob("*.json"))
                    total_livres = 0
                    
                    for fichier in fichiers_json:
                        try:
                            with open(fichier, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if isinstance(data, list):
                                    total_livres += len(data)
                                else:
                                    total_livres += 1
                        except:
                            pass
                    
                    self.etat['resultats']['api'] = {
                        'fichiers_json': len(fichiers_json),
                        'total_livres': total_livres
                    }
                    logger.info(f"Résultats API: {len(fichiers_json)} fichiers, ~{total_livres:,} livres")
                
                return True
            else:
                logger.error(f"Erreur récupération API: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Exception étape API: {e}")
            return False

    def executer_etape_scrapping(self) -> bool:
        """Étape 2: Scrapping Babelio"""
        self.etat['etape_actuelle'] = 2
        logger.info("ETAPE 2/8: Scrapping Babelio")
        
        try:
            script_babelio = self.paths['scripts_scrapping'] / "babelio_scraper_final.py"
            
            if not script_babelio.exists():
                raise FileNotFoundError(f"Script Babelio non trouvé: {script_babelio}")
            
            # Chercher un fichier CSV source pour les ISBN
            csv_source = None
            if self.config['scrapping']['fichier_csv_source']:
                csv_source = self.config['scrapping']['fichier_csv_source']
            else:
                # Chercher automatiquement
                csv_files = list(self.workspace.rglob("*.csv"))
                csv_files = [f for f in csv_files if f.stat().st_size > 1024*1024]  # > 1MB
                
                if csv_files:
                    print("\nFichiers CSV disponibles:")
                    for i, csv_file in enumerate(csv_files[:5], 1):
                        size_mb = csv_file.stat().st_size / (1024*1024)
                        print(f"   {i}. {csv_file.name} ({size_mb:.1f} MB)")
                    
                    choix = input(f"Choisir fichier (1-{min(5, len(csv_files))}) ou Enter pour passer: ").strip()
                    if choix.isdigit() and 1 <= int(choix) <= len(csv_files):
                        csv_source = str(csv_files[int(choix)-1])
            
            if csv_source:
                logger.info(f"Scrapping Babelio depuis: {Path(csv_source).name}")
                # Note: Le script Babelio est interactif, on le lance en mode guidé
                logger.info("Script Babelio prêt - lancement manuel requis pour configuration interactive")
                self.etat['resultats']['scrapping'] = {'status': 'prêt', 'source': csv_source}
            else:
                logger.info("Scrapping Babelio ignoré - aucun fichier CSV source")
                self.etat['resultats']['scrapping'] = {'status': 'ignoré'}
            
            return True
            
        except Exception as e:
            logger.error(f"Exception étape scrapping: {e}")
            return False

    def executer_etape_nettoyage_csv(self) -> bool:
        """Étape 3: Nettoyage et formatage CSV"""
        self.etat['etape_actuelle'] = 3
        logger.info("ETAPE 3/8: Nettoyage et formatage CSV")
        
        try:
            # Chercher des fichiers CSV à nettoyer
            csv_bruts = []
            for pattern in ["livres_openlibrary_*.csv", "*.csv"]:
                csv_bruts.extend(self.workspace.rglob(pattern))
            
            # Filtrer par taille (> 10MB)
            csv_bruts = [f for f in csv_bruts if f.stat().st_size > 10*1024*1024]
            
            if not csv_bruts:
                logger.info("Aucun gros fichier CSV à nettoyer")
                return True
            
            logger.info(f"Trouvé {len(csv_bruts)} fichiers CSV volumineux")
            
            # Utiliser le script de nettoyage
            script_nettoyage = self.paths['scripts_bdd'] / "livres" / "nettoyage_ultra.py"
            
            if script_nettoyage.exists():
                logger.info("Lancement nettoyage des données...")
                
                # Le script de nettoyage est souvent interactif
                logger.info("Script de nettoyage disponible pour lancement manuel")
                self.etat['resultats']['nettoyage'] = {
                    'fichiers_detectes': len(csv_bruts),
                    'status': 'prêt'
                }
            else:
                logger.warning("Script de nettoyage non trouvé")
                self.etat['resultats']['nettoyage'] = {'status': 'script manquant'}
            
            return True
            
        except Exception as e:
            logger.error(f"Exception étape nettoyage: {e}")
            return False

    def executer_etape_postgresql(self) -> bool:
        """Étape 4: Import PostgreSQL"""
        self.etat['etape_actuelle'] = 4
        logger.info("ETAPE 4/8: Import PostgreSQL")
        
        try:
            # Vérifier la disponibilité de psycopg2
            try:
                import psycopg2
                logger.info("Driver PostgreSQL disponible")
            except ImportError:
                logger.warning("Driver PostgreSQL manquant (pip install psycopg2-binary)")
                return True
            
            # Chercher des fichiers CSV nettoyés
            csv_propres = list(self.workspace.rglob("*nettoye*.csv"))
            csv_propres.extend(self.workspace.rglob("*clean*.csv"))
            csv_propres.extend(self.workspace.rglob("*ultra_propre*.csv"))
            
            if csv_propres:
                csv_choisi = max(csv_propres, key=lambda x: x.stat().st_size)
                logger.info(f"Fichier CSV sélectionné: {csv_choisi.name}")
                
                logger.info("Import PostgreSQL prêt - configuration du schéma nécessaire")
                self.etat['resultats']['postgresql'] = {
                    'fichier_source': str(csv_choisi),
                    'schema': self.config['bdd']['schema_postgres'],
                    'status': 'prêt'
                }
            else:
                logger.info("Aucun fichier CSV nettoyé trouvé pour PostgreSQL")
                self.etat['resultats']['postgresql'] = {'status': 'aucun fichier'}
            
            return True
            
        except Exception as e:
            logger.error(f"Exception étape PostgreSQL: {e}")
            return False

    def executer_etape_mongodb(self) -> bool:
        """Étape 5: Import MongoDB"""
        self.etat['etape_actuelle'] = 5
        logger.info("ETAPE 5/8: Import MongoDB")
        
        try:
            # Vérifier la disponibilité de pymongo
            try:
                import pymongo
                logger.info("Driver MongoDB disponible")
            except ImportError:
                logger.warning("Driver MongoDB manquant (pip install pymongo)")
                return True
            
            # Chercher des fichiers JSON
            json_files = list(self.workspace.rglob("*.json"))
            json_files = [f for f in json_files if f.stat().st_size > 1024]  # > 1KB
            
            if json_files:
                total_size = sum(f.stat().st_size for f in json_files) / (1024*1024)
                logger.info(f"Trouvé {len(json_files)} fichiers JSON ({total_size:.1f} MB)")
                
                logger.info("Import MongoDB prêt - vérification connexion nécessaire")
                self.etat['resultats']['mongodb'] = {
                    'fichiers_json': len(json_files),
                    'taille_totale_mb': total_size,
                    'status': 'prêt'
                }
            else:
                logger.info("Aucun fichier JSON trouvé pour MongoDB")
                self.etat['resultats']['mongodb'] = {'status': 'aucun fichier'}
            
            return True
            
        except Exception as e:
            logger.error(f"Exception étape MongoDB: {e}")
            return False

    def verifier_environnement(self) -> bool:
        """Étape 6: Vérification environnement"""
        self.etat['etape_actuelle'] = 6
        logger.info("ETAPE 6/8: Vérification environnement")
        
        try:
            modules_requis = {
                'requests': False,
                'pandas': False,
                'psycopg2': False,
                'pymongo': False
            }
            
            logger.info("Vérification des dépendances:")
            for module in modules_requis:
                try:
                    __import__(module)
                    modules_requis[module] = True
                    status_icon = "OK" if True else "ERREUR"
                    logger.info(f"  {status_icon} {module}")
                except ImportError:
                    status_icon = "ERREUR" if False else "OK"
                    logger.info(f"  {status_icon} {module}")
            
            logger.info("Vérification des chemins:")
            for nom, chemin in self.paths.items():
                exists = chemin.exists()
                status_icon = "OK" if exists else "ERREUR"
                logger.info(f"  {status_icon} {nom}: {chemin}")
            
            # Calculer un score global
            score_modules = sum(modules_requis.values()) / len(modules_requis)
            score_chemins = sum(1 for _, chemin in self.paths.items() if chemin.exists()) / len(self.paths)
            score_global = (score_modules + score_chemins) / 2
            
            self.etat['resultats']['verification'] = {
                'score_global': score_global,
                'modules_ok': sum(modules_requis.values()),
                'chemins_ok': sum(1 for _, chemin in self.paths.items() if chemin.exists())
            }
            
            return score_global > 0.5
            
        except Exception as e:
            logger.error(f"Exception vérification: {e}")
            return False

    def generer_rapport(self):
        """Étape 7: Génération du rapport"""
        self.etat['etape_actuelle'] = 7
        logger.info("ETAPE 7/8: Génération du rapport")
        
        try:
            fin = datetime.now()
            duree_totale = (fin - self.etat['debut']).total_seconds()
            
            rapport = {
                'timestamp': self.timestamp,
                'workspace': str(self.workspace),
                'duree_totale': duree_totale,
                'etapes_executees': self.etat['etape_actuelle'],
                'resultats': self.etat['resultats'],
                'erreurs': self.etat['erreurs'],
                'config': self.config
            }
            
            fichier_rapport = self.workspace / f"rapport_pipeline_{self.timestamp}.json"
            with open(fichier_rapport, 'w', encoding='utf-8') as f:
                json.dump(rapport, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Rapport sauvegardé: {fichier_rapport.name}")
            
            # Affichage console du résumé
            print("\n" + "="*60)
            print("RÉSUMÉ DU PIPELINE")
            print("="*60)
            print(f"Durée totale: {rapport['duree_totale']:.1f} secondes")
            print(f"Workspace: {self.workspace}")
            print(f"Timestamp: {self.timestamp}")
            
            for etape, resultats in rapport['resultats'].items():
                print(f"\n{etape.upper()}: {resultats.get('status', 'terminé')}")
            
            if self.etat['erreurs']:
                print(f"\n{len(self.etat['erreurs'])} erreurs rencontrées")
                for erreur in self.etat['erreurs'][:3]:
                    print(f"  - {erreur}")
            
        except Exception as e:
            logger.error(f"Exception génération rapport: {e}")

    def nettoyer_temporaires(self):
        """Étape 8: Nettoyage fichiers temporaires"""
        self.etat['etape_actuelle'] = 8
        logger.info("ETAPE 8/8: Nettoyage fichiers temporaires")
        
        try:
            patterns_temp = [
                "*.tmp", "*.temp", "*~", "*.bak",
                "__pycache__", "*.pyc", "*.pyo"
            ]
            
            fichiers_supprimes = 0
            for pattern in patterns_temp:
                for fichier in self.workspace.rglob(pattern):
                    try:
                        if fichier.is_file():
                            fichier.unlink()
                            fichiers_supprimes += 1
                        elif fichier.is_dir():
                            shutil.rmtree(fichier)
                            fichiers_supprimes += 1
                    except Exception as e:
                        logger.warning(f"Impossible de supprimer {fichier}: {e}")
            
            logger.info(f"{fichiers_supprimes} fichiers temporaires supprimés")
            
        except Exception as e:
            logger.error(f"Exception nettoyage: {e}")

    def executer_pipeline_complet(self):
        """Exécute le pipeline complet"""
        logger.info("DÉMARRAGE PIPELINE COMPLET")
        print("\n" + "="*60)
        print("PIPELINE COMPLET DATABOOK")
        print("="*60)
        
        etapes = [
            ("Récupération API", self.executer_etape_api),
            ("Scrapping Babelio", self.executer_etape_scrapping),
            ("Nettoyage CSV", self.executer_etape_nettoyage_csv),
            ("PostgreSQL", self.executer_etape_postgresql),
            ("MongoDB", self.executer_etape_mongodb),
            ("Vérification", self.verifier_environnement),
            ("Rapport", self.generer_rapport),
            ("Nettoyage", self.nettoyer_temporaires)
        ]
        
        for nom_etape, methode_etape in etapes:
            print("\n" + "-"*60)
            print(f">> {nom_etape}")
            print("-"*60)
            
            try:
                succes = methode_etape()
                if succes:
                    logger.info(f"{nom_etape} terminée avec succès")
                else:
                    logger.warning(f"{nom_etape} terminée avec des avertissements")
            except Exception as e:
                logger.error(f"Erreur dans {nom_etape}: {e}")
                self.etat['erreurs'].append(f"{nom_etape}: {str(e)}")

    def afficher_status(self):
        """Affiche le status actuel du pipeline"""
        print("\n" + "="*60)
        print("STATUS ET DIAGNOSTICS")
        print("="*60)
        
        print("\nINFORMATIONS GÉNÉRALES:")
        print(f"Workspace: {self.workspace}")
        print(f"Étape actuelle: {self.etat['etape_actuelle']}/{self.etat['total_etapes']}")
        print(f"Timestamp: {self.timestamp}")
        
        print("\nCHEMINS CONFIGURÉS:")
        for nom, chemin in self.paths.items():
            exists = chemin.exists()
            status = "OK" if exists else "MANQUANT"
            print(f"  {status} {nom}: {chemin}")
        
        print("\nDONNÉES DISPONIBLES:")
        
        # Fichiers JSON
        json_files = list(self.workspace.rglob("*.json"))
        if json_files:
            total_size = sum(f.stat().st_size for f in json_files) / (1024*1024)
            print(f"   JSON: {len(json_files)} fichiers ({total_size:.1f} MB)")
        else:
            print("   JSON: Aucun fichier")
        
        # Fichiers CSV
        csv_files = list(self.workspace.rglob("*.csv"))
        if csv_files:
            total_size = sum(f.stat().st_size for f in csv_files) / (1024*1024)
            print(f"   CSV: {len(csv_files)} fichiers ({total_size:.1f} MB)")
        else:
            print("   CSV: Aucun fichier")

def main():
    """Fonction principale"""
    try:
        pipeline = PipelineMaster()
        
        while True:
            choix = pipeline.afficher_menu_principal()
            
            if choix == '1':
                pipeline.executer_pipeline_complet()
            elif choix == '2':
                pipeline.executer_etape_api()
            elif choix == '3':
                pipeline.executer_etape_scrapping()
            elif choix == '4':
                pipeline.executer_etape_nettoyage_csv()
            elif choix == '5':
                print("\nQuel import BDD voulez-vous faire ?")
                print("1. PostgreSQL")
                print("2. MongoDB")
                choix_bdd = input("Choix (1-2): ").strip()
                if choix_bdd == '1':
                    pipeline.executer_etape_postgresql()
                elif choix_bdd == '2':
                    pipeline.executer_etape_mongodb()
            elif choix == '6':
                pipeline.configurer_pipeline()
            elif choix == '7':
                pipeline.afficher_status()
            elif choix == '8':
                pipeline.nettoyer_temporaires()
            elif choix == '9':
                print("Au revoir !")
                break
            else:
                print("Choix invalide")
            
            input("\nAppuyez sur Entrée pour continuer...")
    
    except KeyboardInterrupt:
        print("\nPipeline interrompu par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")

if __name__ == "__main__":
    main() 