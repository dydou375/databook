#!/usr/bin/env python3
"""
TESTS PIPELINE DATABOOK
=======================

Script de tests complets pour valider le pipeline DataBook.
Vérifie tous les composants et dépendances avant exécution.

Author: Assistant IA
Date: 2025-01-27
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Configuration du logging pour Windows
import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au path
workspace = Path(__file__).parent
sys.path.insert(0, str(workspace))

class TesteurPipeline:
    """Classe de tests pour le pipeline DataBook"""
    
    def __init__(self, mode_complet=False):
        self.workspace = workspace
        self.mode_complet = mode_complet
        self.resultats = {
            'debut': datetime.now(),
            'tests': {},
            'erreurs': [],
            'avertissements': [],
            'duree': 0
        }
        
        print("TESTS PIPELINE DATABOOK")
        print("="*60)
        print(f"Workspace: {self.workspace}")
        print(f"Mode: {'Complet' if mode_complet else 'Rapide'}")
        print()

    def test_modules_python(self) -> bool:
        """Test 1: Vérification des modules Python"""
        print("TEST 1: Modules Python")
        print("-" * 30)
        
        # Modules essentiels
        modules_essentiels = {
            'requests': 'Requêtes API',
            'pandas': 'Traitement données',
            'bs4': 'Scrapping web',
            'sqlalchemy': 'ORM PostgreSQL',
            'pymongo': 'Driver MongoDB'
        }
        
        # Modules optionnels
        modules_optionnels = {
            'psycopg2': 'Driver PostgreSQL',
            'numpy': 'Calculs numériques',
            'matplotlib': 'Graphiques',
            'jupyter': 'Notebooks'
        }
        
        # Test modules essentiels
        modules_ok = 0
        for module, description in modules_essentiels.items():
            try:
                __import__(module)
                modules_ok += 1
                print(f"OK {module}: {description}")
            except ImportError:
                self.resultats['erreurs'].append(f"Module manquant: {module}")
                print(f"ERREUR {module}: {description} - MANQUANT")
        
        # Test modules optionnels
        print("\nModules optionnels:")
        for module, description in modules_optionnels.items():
            try:
                __import__(module)
                print(f"OK {module}: {description}")
            except ImportError:
                print(f"AVERTISSEMENT {module}: {description} - optionnel")
        
        succes = modules_ok >= 3  # Au moins 3 modules essentiels
        
        self.resultats['tests']['modules_python'] = {
            'succes': succes,
            'modules_ok': modules_ok,
            'total_essentiels': len(modules_essentiels)
        }
        
        return succes

    def test_structure_dossiers(self) -> bool:
        """Test 2: Vérification structure des dossiers"""
        print("\nTEST 2: Structure des dossiers")
        print("-" * 30)
        
        # Dossiers essentiels
        dossiers_essentiels = {
            'scripts': 'Scripts de récupération',
            'scripts/api': 'Scripts API',
            'scripts/scrapping': 'Scripts scrapping',
            'bdd': 'Scripts base de données',
            'bdd/livres': 'Scripts PostgreSQL',
            'bdd/nosql': 'Scripts MongoDB'
        }
        
        # Dossiers optionnels
        dossiers_optionnels = {
            'data': 'Données générées',
            'data/livre_json': 'Fichiers JSON',
            'data/fichier_openlibrary': 'Données OpenLibrary',
            'docs': 'Documentation',
            'test': 'Tests'
        }
        
        # Vérifier dossiers essentiels
        dossiers_ok = 0
        for chemin, description in dossiers_essentiels.items():
            chemin_complet = self.workspace / chemin
            if chemin_complet.exists():
                dossiers_ok += 1
                print(f"OK {chemin}: {description}")
            else:
                self.resultats['erreurs'].append(f"Dossier manquant: {chemin}")
                print(f"ERREUR {chemin}: {description} - MANQUANT")
        
        # Vérifier dossiers optionnels  
        print("\nDossiers optionnels:")
        for chemin, description in dossiers_optionnels.items():
            chemin_complet = self.workspace / chemin
            if chemin_complet.exists():
                print(f"OK {chemin}: {description}")
            else:
                print(f"AVERTISSEMENT {chemin}: {description} - optionnel")
        
        succes = dossiers_ok >= 4  # Au moins 4 dossiers essentiels
        
        self.resultats['tests']['structure_dossiers'] = {
            'succes': succes,
            'dossiers_ok': dossiers_ok,
            'total_essentiels': len(dossiers_essentiels)
        }
        
        return succes

    def test_fichiers_essentiels(self) -> bool:
        """Test 3: Vérification des fichiers essentiels"""
        print("\nTEST 3: Fichiers essentiels")
        print("-" * 30)
        
        # Fichiers principaux
        fichiers_principaux = {
            'pipeline_master.py': 'Script principal',
            'demarrage_rapide.py': 'Script démarrage',
            'config_pipeline.json': 'Configuration'
        }
        
        # Scripts spécialisés
        scripts_specialises = {
            'scripts/api/recupération_api_livre_amelioree.py': 'Récupération API',
            'scripts/scrapping/babelio_scraper_final.py': 'Scrapping Babelio',
            'bdd/livres/formatage_bdd_postgresql.py': 'Import PostgreSQL',
            'bdd/nosql/import_mongodb.py': 'Import MongoDB'
        }
        
        # Test fichiers principaux
        fichiers_ok = 0
        for fichier, description in fichiers_principaux.items():
            chemin_fichier = self.workspace / fichier
            if chemin_fichier.exists():
                fichiers_ok += 1
                taille = chemin_fichier.stat().st_size / 1024
                print(f"OK {fichier}: {description} ({taille:.1f} KB)")
            else:
                self.resultats['erreurs'].append(f"Fichier manquant: {fichier}")
                print(f"ERREUR {fichier}: {description} - MANQUANT")
        
        # Test scripts spécialisés
        print("\nScripts spécialisés:")
        for fichier, description in scripts_specialises.items():
            chemin_fichier = self.workspace / fichier
            if chemin_fichier.exists():
                taille = chemin_fichier.stat().st_size / 1024
                print(f"OK {fichier}: {description} ({taille:.1f} KB)")
            else:
                print(f"AVERTISSEMENT {fichier}: {description} - non trouvé")
        
        succes = fichiers_ok >= 2  # Au moins 2 fichiers principaux
        
        self.resultats['tests']['fichiers_essentiels'] = {
            'succes': succes,
            'fichiers_ok': fichiers_ok,
            'total_principaux': len(fichiers_principaux)
        }
        
        return succes

    def test_configuration(self) -> bool:
        """Test 4: Configuration"""
        print("\nTEST 4: Configuration")
        print("-" * 30)
        
        try:
            config_file = self.workspace / "config_pipeline.json"
            if not config_file.exists():
                self.resultats['erreurs'].append("Fichier config_pipeline.json manquant")
                print("ERREUR Fichier config_pipeline.json manquant")
                return False
            
            # Charger la configuration
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Vérifier les sections essentielles
            sections_requises = ['api', 'scrapping', 'bdd']
            sections_ok = 0
            for section in sections_requises:
                if section in config:
                    sections_ok += 1
                    print(f"OK Section '{section}' présente")
                else:
                    print(f"ERREUR Section '{section}' manquante")
                    self.resultats['erreurs'].append(f"Section config manquante: {section}")
            
            # Vérifier les URLs de base de données
            if 'bdd' in config:
                if 'postgresql_url' in config['bdd']:
                    print(f"OK Configuration PostgreSQL")
                else:
                    print(f"AVERTISSEMENT Configuration PostgreSQL manquante")
                
                if 'mongodb_url' in config['bdd']:
                    print(f"OK Configuration MongoDB")
                else:
                    print(f"AVERTISSEMENT Configuration MongoDB manquante")
            
            succes = sections_ok >= 2
            
            self.resultats['tests']['configuration'] = {
                'succes': succes,
                'sections_ok': sections_ok,
                'total_sections': len(sections_requises),
                'config_valide': True
            }
            
            return succes
            
        except json.JSONDecodeError as e:
            self.resultats['erreurs'].append(f"Erreur JSON: {e}")
            print(f"ERREUR Erreur JSON dans la configuration: {e}")
            return False
            
        except Exception as e:
            self.resultats['erreurs'].append(f"Erreur config: {e}")
            print(f"ERREUR Erreur lecture configuration: {e}")
            return False

    def test_imports_pipeline(self) -> bool:
        """Test 5: Imports du pipeline"""
        print("\nTEST 5: Imports pipeline")
        print("-" * 30)
        
        try:
            # Test import principal
            from pipeline_master import PipelineMaster
            print("OK Import PipelineMaster réussi")
            
            # Test instanciation
            pipeline = PipelineMaster()
            print("OK Instanciation PipelineMaster réussie")
            
            # Test méthodes essentielles
            if hasattr(pipeline, 'executer_etape_api'):
                print("OK Méthode executer_etape_api présente")
            else:
                print("ERREUR Méthode executer_etape_api manquante")
                return False
            
            if hasattr(pipeline, 'verifier_environnement'):
                print("OK Méthode verifier_environnement présente")
            else:
                print("ERREUR Méthode verifier_environnement manquante")
                return False
            
            self.resultats['tests']['imports_pipeline'] = {
                'succes': True,
                'import_ok': True,
                'instanciation_ok': True
            }
            
            return True
            
        except ImportError as e:
            self.resultats['erreurs'].append(f"Erreur import: {e}")
            print(f"ERREUR Erreur import pipeline_master: {e}")
            return False
            
        except Exception as e:
            self.resultats['erreurs'].append(f"Erreur instanciation: {e}")
            print(f"ERREUR Erreur instanciation: {e}")
            return False

    def test_connexions_bdd(self) -> bool:
        """Test 6: Connexions bases de données"""
        print("\nTEST 6: Connexions bases de données")
        print("-" * 30)
        
        # Test PostgreSQL
        try:
            import psycopg2
            print("OK Driver PostgreSQL disponible")
            
            # Test connexion (optionnel)
            if self.mode_complet:
                try:
                    conn = psycopg2.connect(
                        "postgresql://postgres:postgres@localhost:5432/databook"
                    )
                    version = conn.execute("SELECT version()").fetchone()[0]
                    conn.close()
                    print(f"OK PostgreSQL connecté: {version.split(',')[0]}")
                except Exception as e:
                    self.resultats['avertissements'].append(f"PostgreSQL non accessible: {e}")
                    print(f"AVERTISSEMENT PostgreSQL non accessible: {e}")
            
        except ImportError:
            self.resultats['erreurs'].append("Driver PostgreSQL manquant")
            print("ERREUR Driver PostgreSQL manquant")
        
        # Test MongoDB
        try:
            import pymongo
            print("OK Driver MongoDB disponible")
            
            # Test connexion (optionnel)
            if self.mode_complet:
                try:
                    client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
                    info = client.admin.command('ismaster')
                    client.close()
                    print(f"OK MongoDB connecté: version {info['version']}")
                except Exception as e:
                    self.resultats['avertissements'].append(f"MongoDB non accessible: {e}")
                    print(f"AVERTISSEMENT MongoDB non accessible: {e}")
            
        except ImportError:
            self.resultats['erreurs'].append("Driver MongoDB manquant")
            print("ERREUR Driver MongoDB manquant")
        
        # Succès si au moins un driver disponible
        postgres_ok = 'psycopg2' in sys.modules
        mongo_ok = 'pymongo' in sys.modules
        succes = postgres_ok or mongo_ok
        
        self.resultats['tests']['connexions_bdd'] = {
            'succes': succes,
            'postgresql_ok': postgres_ok,
            'mongodb_ok': mongo_ok
        }
        
        return succes

    def test_fonctionnel_minimal(self) -> bool:
        """Test 7: Test fonctionnel minimal"""
        print("\nTEST 7: Test fonctionnel minimal")
        print("-" * 30)
        
        try:
            from pipeline_master import PipelineMaster
            
            # Test instanciation
            pipeline = PipelineMaster()
            
            # Test modification de configuration
            print("Test modification configuration...")
            pipeline.config['api']['max_livres_par_categorie'] = 10
            print("OK Configuration modifiée")
            
            # Test vérification environnement
            print("Test vérification environnement...")
            resultat = pipeline.verifier_environnement()
            if resultat:
                print("OK Vérification environnement réussie")
            else:
                print("AVERTISSEMENT Vérification environnement avec avertissements")
            
            self.resultats['tests']['fonctionnel_minimal'] = {
                'succes': True,
                'config_modifiable': True,
                'verification_ok': resultat
            }
            
            return True
            
        except Exception as e:
            self.resultats['erreurs'].append(f"Test fonctionnel: {e}")
            print(f"ERREUR Erreur test fonctionnel: {e}")
            return False

    def executer_test(self, nom_test: str, methode_test) -> bool:
        """Exécute un test individuel avec gestion d'erreurs"""
        try:
            debut = datetime.now()
            resultat = methode_test()
            duree = (datetime.now() - debut).total_seconds()
            
            self.resultats['tests'][nom_test] = self.resultats['tests'].get(nom_test, {})
            self.resultats['tests'][nom_test]['duree'] = duree
            self.resultats['tests'][nom_test]['succes'] = resultat
            
            return resultat
            
        except Exception as e:
            self.resultats['erreurs'].append(f"ERREUR dans {nom_test}: {e}")
            self.resultats['tests'][nom_test] = {
                'succes': False,
                'erreur': str(e)
            }
            print(f"\nERREUR CRITIQUE dans {nom_test}: {e}")
            return False

    def executer_tous_tests(self) -> bool:
        """Exécute tous les tests"""
        tests = [
            ("modules_python", self.test_modules_python),
            ("structure_dossiers", self.test_structure_dossiers),
            ("fichiers_essentiels", self.test_fichiers_essentiels),
            ("configuration", self.test_configuration),
            ("imports_pipeline", self.test_imports_pipeline),
            ("connexions_bdd", self.test_connexions_bdd),
            ("fonctionnel_minimal", self.test_fonctionnel_minimal)
        ]
        
        resultats_tests = []
        for nom_test, methode_test in tests:
            resultat = self.executer_test(nom_test, methode_test)
            resultats_tests.append(resultat)
        
        return all(resultats_tests)

    def generer_rapport_final(self):
        """Génère le rapport final des tests"""
        fin = datetime.now()
        self.resultats['duree'] = (fin - self.resultats['debut']).total_seconds()
        
        print("\n" + "="*60)
        print("RAPPORT FINAL DES TESTS")
        print("="*60)
        
        print(f"Durée totale: {self.resultats['duree']:.1f} secondes")
        print(f"Tests exécutés: {len(self.resultats['tests'])}")
        
        # Résultats par test
        print("RÉSULTATS PAR TEST:")
        for nom_test, resultat in self.resultats['tests'].items():
            icone = "OK" if resultat.get('succes', False) else "ERREUR"
            duree = resultat.get('duree', 0)
            print(f"   {icone} {nom_test}: {duree:.2f}s")
        
        # Erreurs
        if self.resultats['erreurs']:
            print(f"\nERREURS ({len(self.resultats['erreurs'])}):")
            for erreur in self.resultats['erreurs']:
                print(f"   - {erreur}")
        
        # Avertissements
        if self.resultats['avertissements']:
            print(f"\nAVERTISSEMENTS ({len(self.resultats['avertissements'])}):")
            for avertissement in self.resultats['avertissements']:
                print(f"   - {avertissement}")
        
        # Status final
        print(f"\nSTATUS FINAL:")
        succes_global = len(self.resultats['erreurs']) == 0
        if succes_global:
            print("   TOUS LES TESTS RÉUSSIS - Pipeline prêt à l'utilisation")
        else:
            print("   ÉCHECS DÉTECTÉS - Corriger les erreurs avant utilisation")
        
        # Sauvegarder le rapport
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as rapport_file:
                json.dump(self.resultats, rapport_file, indent=2, default=str)
                print(f"\nRapport sauvegardé: {rapport_file.name}")
        except Exception as e:
            print(f"\nImpossible de sauvegarder le rapport: {e}")
        
        return succes_global

def main():
    """Fonction principale des tests"""
    try:
        # Demander le mode
        print("TESTS PIPELINE DATABOOK")
        print("1. Tests rapides (essentiel)")
        print("2. Tests complets (avec connexions BDD)")
        
        choix = input("\nChoix (1-2): ").strip()
        mode_complet = choix == '2'
        
        # Exécuter les tests
        testeur = TesteurPipeline(mode_complet=mode_complet)
        succes = testeur.executer_tous_tests()
        succes_final = testeur.generer_rapport_final()
        
        # Code de sortie
        sys.exit(0 if succes_final else 1)
        
    except KeyboardInterrupt:
        print("\nTests interrompus par l'utilisateur")
        sys.exit(1)
        
    except Exception as e:
        print(f"\nErreur fatale dans les tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()