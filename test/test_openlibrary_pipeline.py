#!/usr/bin/env python3
"""
Test de l'étape OpenLibrary du Pipeline DataBook
==============================================

Script pour tester spécifiquement l'extraction et le traitement 
des fichiers .txt OpenLibrary dans le pipeline.
"""

import os
import sys
import json
import time
from pathlib import Path

# Ajouter le chemin du pipeline
sys.path.append(str(Path(__file__).parent))
from pipeline_master import PipelineMaster

def tester_detection_fichiers_openlibrary():
    """Teste la détection des fichiers OpenLibrary"""
    print("🔍 TEST 1: Détection des fichiers OpenLibrary")
    print("-" * 50)
    
    dossier_openlibrary = Path("./data/fichier_openlibrary")
    
    if not dossier_openlibrary.exists():
        print(f"❌ Dossier OpenLibrary non trouvé: {dossier_openlibrary}")
        print(f"💡 Créez le dossier et placez-y vos fichiers .txt OpenLibrary")
        return False
    
    # Lister les fichiers disponibles
    fichiers_txt = list(dossier_openlibrary.glob("*.txt"))
    fichiers_gz = list(dossier_openlibrary.glob("*.gz"))
    fichiers_bz2 = list(dossier_openlibrary.glob("*.bz2"))
    
    total_fichiers = len(fichiers_txt) + len(fichiers_gz) + len(fichiers_bz2)
    
    print(f"📁 Dossier OpenLibrary: {dossier_openlibrary}")
    print(f"📄 Fichiers .txt: {len(fichiers_txt)}")
    print(f"📦 Fichiers .gz: {len(fichiers_gz)}")
    print(f"📦 Fichiers .bz2: {len(fichiers_bz2)}")
    print(f"📊 Total: {total_fichiers} fichiers")
    
    if total_fichiers == 0:
        print("⚠️ Aucun fichier OpenLibrary détecté")
        print("💡 Téléchargez des fichiers depuis https://openlibrary.org/data")
        return False
    
    # Afficher les détails des fichiers
    for fichier in fichiers_txt[:3]:  # Max 3 fichiers
        taille_mb = fichier.stat().st_size / (1024 * 1024)
        print(f"   📄 {fichier.name}: {taille_mb:.1f} MB")
    
    for fichier in fichiers_gz[:3]:  # Max 3 fichiers
        taille_mb = fichier.stat().st_size / (1024 * 1024)
        print(f"   📦 {fichier.name}: {taille_mb:.1f} MB (compressé)")
    
    print("✅ Détection des fichiers OK")
    return True

def tester_extracteur_livres():
    """Teste l'extracteur de livres standalone"""
    print("\n🔧 TEST 2: Extracteur de livres OpenLibrary")
    print("-" * 50)
    
    try:
        # Importer l'extracteur
        sys.path.append("./bdd/livres")
        from extracteur_livres import ExtracteurLivres
        
        # Créer l'extracteur
        base_path = "./data/fichier_openlibrary"
        extracteur = ExtracteurLivres(base_path)
        
        print(f"📚 Extracteur initialisé pour: {base_path}")
        
        # Test d'extraction minimale
        print("🔍 Test d'extraction (100 livres max)...")
        
        criteres = {
            'avec_titre': True,
            'avec_isbn': False,  # Permissif pour le test
            'avec_auteur': False,
            'annee_min': None,
            'annee_max': None,
            'langues': None
        }
        
        debut = time.time()
        livres = extracteur.extraire_editions_echantillon(max_livres=100, criteres=criteres)
        duree = time.time() - debut
        
        if livres:
            print(f"✅ Extraction réussie: {len(livres)} livres en {duree:.1f}s")
            
            # Analyser les premiers livres
            if len(livres) > 0:
                premier_livre = livres[0]
                print(f"📖 Exemple de livre:")
                print(f"   • Titre: {premier_livre.get('titre', 'N/A')}")
                print(f"   • Auteurs: {premier_livre.get('auteurs', 'N/A')}")
                print(f"   • ISBN-13: {premier_livre.get('isbn_13', 'N/A')}")
                print(f"   • Année: {premier_livre.get('annee_publication', 'N/A')}")
            
            return True
        else:
            print("❌ Aucun livre extrait")
            return False
            
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Vérifiez que les scripts dans ./bdd/livres/ sont disponibles")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST COMPLET - ÉTAPE OPENLIBRARY PIPELINE")
    print("=" * 60)
    print("Ce script teste l'intégration des fichiers .txt OpenLibrary")
    print("dans le pipeline DataBook complet.")
    print("=" * 60)
    
    tests_reussis = 0
    tests_total = 2
    
    # Exécuter tous les tests
    tests = [
        tester_detection_fichiers_openlibrary,
        tester_extracteur_livres
    ]
    
    for i, test_func in enumerate(tests, 1):
        try:
            print(f"\n[{i}/{tests_total}] ", end="")
            if test_func():
                tests_reussis += 1
            
        except KeyboardInterrupt:
            print("\n🛑 Tests interrompus par l'utilisateur")
            break
        except Exception as e:
            print(f"\n❌ Erreur test {i}: {e}")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"✅ Tests réussis: {tests_reussis}/{tests_total}")
    print(f"📈 Taux de réussite: {(tests_reussis/tests_total)*100:.1f}%")
    
    if tests_reussis == tests_total:
        print("🎉 Tous les tests sont passés ! Le pipeline OpenLibrary est prêt.")
    elif tests_reussis > 0:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
    else:
        print("❌ Tous les tests ont échoué. Vérifiez l'installation.")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 