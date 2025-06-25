#!/usr/bin/env python3
"""
TESTS PIPELINE DATABOOK
=======================

Script de tests pour valider le bon fonctionnement du pipeline.
Vérifie tous les composants et dépendances avant exécution.

Usage:
    python test_pipeline.py
    python test_pipeline.py --complet
    python test_pipeline.py --rapide
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
import argparse

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

class TesteurPipeline:
    """Classe de tests pour le pipeline DataBook"""
    
    def __init__(self, mode_complet=False):
        self.workspace = Path(__file__).parent
        self.mode_complet = mode_complet
        self.resultats = {
            'debut': datetime.now(),
            'tests': {},
            'erreurs': [],
            'avertissements': []
        }
        
        print("🧪 TESTS PIPELINE DATABOOK")
        print("=" * 50)
        print(f"📂 Workspace: {self.workspace}")
        print(f"🔧 Mode: {'Complet' if mode_complet else 'Rapide'}")
        print()
    
    def test_modules_python(self):
        """Test 1: Vérification des modules Python"""
        print("🐍 TEST 1: Modules Python")
        print("-" * 30)
        
        modules_requis = {
            'requests': '📡 Requêtes API',
            'pandas': '📊 Traitement données',
            'bs4': '🕷️ Scrapping web',
            'sqlalchemy': '🗄️ ORM PostgreSQL',
            'pymongo': '🍃 Driver MongoDB'
        }
        
        modules_optionnels = {
            'psycopg2': '🔗 Driver PostgreSQL',
            'numpy': '🔢 Calculs numériques',
            'matplotlib': '📈 Graphiques',
            'jupyter': '📓 Notebooks'
        }
        
        modules_ok = []
        modules_manquants = []
        
        # Test modules requis
        for module, description in modules_requis.items():
            try:
                __import__(module)
                modules_ok.append(module)
                print(f"✅ {module}: {description}")
            except ImportError:
                modules_manquants.append(module)
                print(f"❌ {module}: {description} - MANQUANT")
        
        # Test modules optionnels
        print("\n📦 Modules optionnels:")
        for module, description in modules_optionnels.items():
            try:
                __import__(module)
                print(f"✅ {module}: {description}")
            except ImportError:
                print(f"⚠️ {module}: {description} - optionnel")
        
        self.resultats['tests']['modules'] = {
            'requis_ok': modules_ok,
            'requis_manquants': modules_manquants,
            'succes': len(modules_manquants) == 0
        }
        
        if modules_manquants:
            self.resultats['erreurs'].append(f"Modules manquants: {', '.join(modules_manquants)}")
            return False
        
        return True
    
    def test_structure_dossiers(self):
        """Test 2: Vérification structure des dossiers"""
        print("\n📁 TEST 2: Structure des dossiers")
        print("-" * 35)
        
        dossiers_requis = {
            'scripts': '📜 Scripts de récupération',
            'scripts/api': '📡 Scripts API',
            'scripts/scrapping': '🕷️ Scripts scrapping',
            'bdd': '🗄️ Scripts base de données',
            'bdd/livres': '📚 Scripts PostgreSQL',
            'bdd/nosql': '🍃 Scripts MongoDB'
        }
        
        dossiers_optionnels = {
            'data': '📊 Données générées',
            'data/livre_json': '📄 Fichiers JSON',
            'data/fichier_openlibrary': '📚 Données OpenLibrary',
            'docs': '📋 Documentation',
            'test': '🧪 Tests'
        }
        
        dossiers_ok = []
        dossiers_manquants = []
        
        # Test dossiers requis
        for chemin, description in dossiers_requis.items():
            dossier = self.workspace / chemin
            if dossier.exists() and dossier.is_dir():
                dossiers_ok.append(chemin)
                print(f"✅ {chemin}: {description}")
            else:
                dossiers_manquants.append(chemin)
                print(f"❌ {chemin}: {description} - MANQUANT")
        
        # Test dossiers optionnels
        print("\n📂 Dossiers optionnels:")
        for chemin, description in dossiers_optionnels.items():
            dossier = self.workspace / chemin
            if dossier.exists() and dossier.is_dir():
                print(f"✅ {chemin}: {description}")
            else:
                print(f"⚠️ {chemin}: {description} - optionnel")
        
        self.resultats['tests']['dossiers'] = {
            'requis_ok': dossiers_ok,
            'requis_manquants': dossiers_manquants,
            'succes': len(dossiers_manquants) == 0
        }
        
        if dossiers_manquants:
            self.resultats['avertissements'].append(f"Dossiers manquants: {', '.join(dossiers_manquants)}")
            return False
        
        return True
    
    def test_fichiers_essentiels(self):
        """Test 3: Vérification des fichiers essentiels"""
        print("\n📄 TEST 3: Fichiers essentiels")
        print("-" * 30)
        
        fichiers_requis = {
            'pipeline_master.py': '🎯 Script principal',
            'demarrage_rapide.py': '🚀 Script démarrage',
            'config_pipeline.json': '⚙️ Configuration'
        }
        
        fichiers_scripts = {
            'scripts/api/recupération_api_livre_amelioree.py': '📡 Récupération API',
            'scripts/scrapping/babelio_scraper_final.py': '🕷️ Scrapping Babelio',
            'bdd/livres/formatage_bdd_postgresql.py': '🗄️ Import PostgreSQL',
            'bdd/nosql/import_mongodb.py': '🍃 Import MongoDB'
        }
        
        fichiers_ok = []
        fichiers_manquants = []
        
        # Test fichiers requis
        for fichier, description in fichiers_requis.items():
            chemin = self.workspace / fichier
            if chemin.exists() and chemin.is_file():
                fichiers_ok.append(fichier)
                taille = chemin.stat().st_size / 1024
                print(f"✅ {fichier}: {description} ({taille:.1f} KB)")
            else:
                fichiers_manquants.append(fichier)
                print(f"❌ {fichier}: {description} - MANQUANT")
        
        # Test scripts
        print("\n📜 Scripts spécialisés:")
        for fichier, description in fichiers_scripts.items():
            chemin = self.workspace / fichier
            if chemin.exists() and chemin.is_file():
                taille = chemin.stat().st_size / 1024
                print(f"✅ {fichier}: {description} ({taille:.1f} KB)")
            else:
                print(f"⚠️ {fichier}: {description} - non trouvé")
        
        self.resultats['tests']['fichiers'] = {
            'requis_ok': fichiers_ok,
            'requis_manquants': fichiers_manquants,
            'succes': len(fichiers_manquants) == 0
        }
        
        if fichiers_manquants:
            self.resultats['erreurs'].append(f"Fichiers manquants: {', '.join(fichiers_manquants)}")
            return False
        
        return True
    
    def test_configuration(self):
        """Test 4: Validation de la configuration"""
        print("\n⚙️ TEST 4: Configuration")
        print("-" * 25)
        
        try:
            config_file = self.workspace / "config_pipeline.json"
            
            if not config_file.exists():
                print("❌ Fichier config_pipeline.json manquant")
                self.resultats['erreurs'].append("Configuration manquante")
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Vérifier les sections essentielles
            sections_requises = ['pipeline', 'api', 'scrapping', 'bdd']
            for section in sections_requises:
                if section in config:
                    print(f"✅ Section '{section}' présente")
                else:
                    print(f"❌ Section '{section}' manquante")
                    self.resultats['erreurs'].append(f"Section config manquante: {section}")
                    return False
            
            # Vérifier les URLs de base de données
            if 'postgresql' in config['bdd']:
                print(f"✅ Configuration PostgreSQL")
            else:
                print(f"⚠️ Configuration PostgreSQL manquante")
                
            if 'mongodb' in config['bdd']:
                print(f"✅ Configuration MongoDB")
            else:
                print(f"⚠️ Configuration MongoDB manquante")
            
            self.resultats['tests']['configuration'] = {
                'fichier_present': True,
                'sections_ok': sections_requises,
                'succes': True
            }
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON dans la configuration: {e}")
            self.resultats['erreurs'].append(f"JSON invalide: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur lecture configuration: {e}")
            self.resultats['erreurs'].append(f"Erreur config: {e}")
            return False
    
    def test_imports_pipeline(self):
        """Test 5: Import des modules du pipeline"""
        print("\n🔧 TEST 5: Imports pipeline")
        print("-" * 30)
        
        try:
            # Test import pipeline_master
            from pipeline_master import PipelineMaster
            print("✅ Import PipelineMaster réussi")
            
            # Test instanciation
            pipeline = PipelineMaster()
            print("✅ Instanciation PipelineMaster réussie")
            
            # Test méthodes essentielles
            if hasattr(pipeline, 'executer_etape_api'):
                print("✅ Méthode executer_etape_api présente")
            else:
                print("❌ Méthode executer_etape_api manquante")
                return False
            
            if hasattr(pipeline, 'verifier_environnement'):
                print("✅ Méthode verifier_environnement présente")
            else:
                print("❌ Méthode verifier_environnement manquante")
                return False
            
            self.resultats['tests']['imports'] = {
                'pipeline_master': True,
                'instanciation': True,
                'methodes': True,
                'succes': True
            }
            
            return True
            
        except ImportError as e:
            print(f"❌ Erreur import pipeline_master: {e}")
            self.resultats['erreurs'].append(f"Import failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur instanciation: {e}")
            self.resultats['erreurs'].append(f"Instanciation failed: {e}")
            return False
    
    def test_connexions_bdd(self):
        """Test 6: Test des connexions aux bases de données"""
        print("\n🗄️ TEST 6: Connexions bases de données")
        print("-" * 40)
        
        resultats_bdd = {}
        
        # Test PostgreSQL
        try:
            import psycopg2
            print("✅ Driver PostgreSQL disponible")
            
            # Test de connexion (sans bloquer si échec)
            try:
                from sqlalchemy import create_engine
                engine = create_engine("postgresql://postgres:postgres@localhost:5432/databook", 
                                    pool_pre_ping=True)
                with engine.connect() as conn:
                    result = conn.execute("SELECT version()")
                    version = result.fetchone()[0]
                    print(f"✅ PostgreSQL connecté: {version.split(',')[0]}")
                    resultats_bdd['postgresql'] = True
            except Exception as e:
                print(f"⚠️ PostgreSQL non accessible: {e}")
                resultats_bdd['postgresql'] = False
                self.resultats['avertissements'].append("PostgreSQL inaccessible")
                
        except ImportError:
            print("❌ Driver PostgreSQL manquant")
            resultats_bdd['postgresql'] = False
            self.resultats['avertissements'].append("Driver PostgreSQL manquant")
        
        # Test MongoDB
        try:
            import pymongo
            print("✅ Driver MongoDB disponible")
            
            # Test de connexion
            try:
                client = pymongo.MongoClient("mongodb://localhost:27017/", 
                                           serverSelectionTimeoutMS=3000)
                info = client.server_info()
                print(f"✅ MongoDB connecté: version {info['version']}")
                resultats_bdd['mongodb'] = True
                client.close()
            except Exception as e:
                print(f"⚠️ MongoDB non accessible: {e}")
                resultats_bdd['mongodb'] = False
                self.resultats['avertissements'].append("MongoDB inaccessible")
                
        except ImportError:
            print("❌ Driver MongoDB manquant")
            resultats_bdd['mongodb'] = False
            self.resultats['avertissements'].append("Driver MongoDB manquant")
        
        self.resultats['tests']['bdd'] = resultats_bdd
        
        # Au moins une BDD doit être accessible pour les tests complets
        if self.mode_complet:
            return any(resultats_bdd.values())
        else:
            return True  # En mode rapide, on n'exige pas les BDD
    
    def test_fonctionnel_minimal(self):
        """Test 7: Test fonctionnel minimal du pipeline"""
        if not self.mode_complet:
            return True
            
        print("\n🚀 TEST 7: Test fonctionnel minimal")
        print("-" * 35)
        
        try:
            from pipeline_master import PipelineMaster
            
            pipeline = PipelineMaster()
            
            # Test configuration
            print("🔧 Test modification configuration...")
            pipeline.config['api']['max_livres_par_categorie'] = 10  # Très petit pour test
            print("✅ Configuration modifiée")
            
            # Test vérification environnement
            print("🔍 Test vérification environnement...")
            result = pipeline.verifier_environnement()
            if result:
                print("✅ Vérification environnement réussie")
            else:
                print("⚠️ Vérification environnement avec avertissements")
            
            self.resultats['tests']['fonctionnel'] = {
                'configuration': True,
                'verification_env': result,
                'succes': True
            }
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur test fonctionnel: {e}")
            self.resultats['erreurs'].append(f"Test fonctionnel: {e}")
            return False
    
    def executer_tous_tests(self):
        """Exécute tous les tests dans l'ordre"""
        tests = [
            ("Modules Python", self.test_modules_python),
            ("Structure dossiers", self.test_structure_dossiers),
            ("Fichiers essentiels", self.test_fichiers_essentiels),
            ("Configuration", self.test_configuration),
            ("Imports pipeline", self.test_imports_pipeline),
            ("Connexions BDD", self.test_connexions_bdd),
        ]
        
        if self.mode_complet:
            tests.append(("Test fonctionnel", self.test_fonctionnel_minimal))
        
        resultats_tests = {}
        tous_ok = True
        
        for nom_test, fonction_test in tests:
            try:
                resultat = fonction_test()
                resultats_tests[nom_test] = resultat
                if not resultat:
                    tous_ok = False
            except Exception as e:
                print(f"\n❌ ERREUR CRITIQUE dans {nom_test}: {e}")
                resultats_tests[nom_test] = False
                tous_ok = False
                self.resultats['erreurs'].append(f"Erreur critique {nom_test}: {e}")
        
        self.resultats['fin'] = datetime.now()
        self.resultats['duree'] = (self.resultats['fin'] - self.resultats['debut']).total_seconds()
        self.resultats['tests_individuels'] = resultats_tests
        self.resultats['succes_global'] = tous_ok
        
        return tous_ok
    
    def generer_rapport(self):
        """Génère le rapport final des tests"""
        print("\n" + "="*60)
        print("📊 RAPPORT FINAL DES TESTS")
        print("="*60)
        
        print(f"⏱️ Durée totale: {self.resultats['duree']:.1f} secondes")
        print(f"🧪 Mode: {'Complet' if self.mode_complet else 'Rapide'}")
        print()
        
        # Résultats par test
        print("📋 RÉSULTATS PAR TEST:")
        for nom_test, resultat in self.resultats['tests_individuels'].items():
            icone = "✅" if resultat else "❌"
            print(f"   {icone} {nom_test}")
        
        # Erreurs
        if self.resultats['erreurs']:
            print(f"\n❌ ERREURS ({len(self.resultats['erreurs'])}):")
            for erreur in self.resultats['erreurs']:
                print(f"   • {erreur}")
        
        # Avertissements
        if self.resultats['avertissements']:
            print(f"\n⚠️ AVERTISSEMENTS ({len(self.resultats['avertissements'])}):")
            for avertissement in self.resultats['avertissements']:
                print(f"   • {avertissement}")
        
        # Status final
        print(f"\n🎯 STATUS FINAL:")
        if self.resultats['succes_global']:
            print("   ✅ TOUS LES TESTS RÉUSSIS - Pipeline prêt à l'utilisation")
        else:
            print("   ❌ ÉCHECS DÉTECTÉS - Corriger les erreurs avant utilisation")
        
        # Sauvegarder rapport
        rapport_file = self.workspace / f"test_rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(rapport_file, 'w', encoding='utf-8') as f:
                json.dump(self.resultats, f, indent=2, default=str)
            print(f"\n📄 Rapport sauvegardé: {rapport_file.name}")
        except Exception as e:
            print(f"\n⚠️ Impossible de sauvegarder le rapport: {e}")
        
        return self.resultats['succes_global']

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Tests Pipeline DataBook")
    parser.add_argument('--complet', action='store_true', help='Tests complets avec connexions BDD')
    parser.add_argument('--rapide', action='store_true', help='Tests rapides uniquement')
    
    args = parser.parse_args()
    
    # Déterminer le mode
    if args.complet:
        mode_complet = True
    elif args.rapide:
        mode_complet = False
    else:
        # Mode par défaut: demander à l'utilisateur
        reponse = input("Tests complets avec BDD? (o/N): ").strip().lower()
        mode_complet = reponse == 'o'
    
    # Exécuter les tests
    testeur = TesteurPipeline(mode_complet=mode_complet)
    
    try:
        succes = testeur.executer_tous_tests()
        testeur.generer_rapport()
        
        return 0 if succes else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrompus par l'utilisateur")
        return 2
    except Exception as e:
        print(f"\n❌ Erreur fatale dans les tests: {e}")
        return 3

if __name__ == "__main__":
    sys.exit(main())