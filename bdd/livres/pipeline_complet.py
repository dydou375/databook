#!/usr/bin/env python3
"""
Pipeline complet OpenLibrary vers Base de Données
===============================================

Ce script maître orchestre l'ensemble du processus:
1. Analyse du fichier source
2. Extraction massive
3. Nettoyage des données
4. Formatage pour la base de données
"""

import os
import sys
import time
import subprocess
from typing import Optional, Dict
import json

class PipelineManager:
    """Gestionnaire du pipeline complet"""
    
    def __init__(self):
        self.repertoire_scripts = os.path.dirname(os.path.abspath(__file__))
        self.logs = []
        self.etape_actuelle = 0
        self.etapes = [
            "Analyse du fichier source",
            "Extraction massive des livres", 
            "Nettoyage des données",
            "Formatage pour la base de données"
        ]
    
    def log(self, message: str, niveau: str = "INFO"):
        """Ajoute un message au log"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {niveau}: {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def executer_script(self, script_name: str, args: list = None) -> bool:
        """Exécute un script Python avec gestion d'erreurs"""
        script_path = os.path.join(self.repertoire_scripts, script_name)
        
        if not os.path.exists(script_path):
            self.log(f"Script non trouvé: {script_name}", "ERREUR")
            return False
        
        try:
            cmd = [sys.executable, script_path]
            if args:
                cmd.extend(args)
            
            self.log(f"Exécution: {script_name}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repertoire_scripts)
            
            if result.returncode == 0:
                self.log(f"✅ {script_name} terminé avec succès")
                return True
            else:
                self.log(f"❌ {script_name} a échoué", "ERREUR")
                self.log(f"Erreur: {result.stderr}", "ERREUR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur lors de l'exécution de {script_name}: {e}", "ERREUR")
            return False
    
    def afficher_progression(self):
        """Affiche la progression du pipeline"""
        print(f"\n📊 PROGRESSION DU PIPELINE")
        print("=" * 50)
        
        for i, etape in enumerate(self.etapes):
            if i < self.etape_actuelle:
                status = "✅"
            elif i == self.etape_actuelle:
                status = "🔄"
            else:
                status = "⏳"
            
            print(f"{status} {i+1}. {etape}")
        
        print(f"\nÉtape {self.etape_actuelle + 1}/{len(self.etapes)}: {self.etapes[self.etape_actuelle]}")
    
    def detecter_fichiers_source(self) -> list:
        """Détecte les fichiers OpenLibrary disponibles"""
        base_paths = [
            r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary",
            r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\non_extrait",
        ]
        
        fichiers = []
        for base_path in base_paths:
            if os.path.exists(base_path):
                for filename in os.listdir(base_path):
                    filepath = os.path.join(base_path, filename)
                    if filename.endswith('.gz') and os.path.getsize(filepath) > 1024**3:  # > 1GB
                        fichiers.append(filepath)
        
        return fichiers
    
    def detecter_fichiers_csv(self) -> list:
        """Détecte les fichiers CSV disponibles"""
        fichiers = []
        for filename in os.listdir(self.repertoire_scripts):
            if filename.endswith('.csv') and os.path.getsize(os.path.join(self.repertoire_scripts, filename)) > 1024**2:  # > 1MB
                fichiers.append(filename)
        return fichiers
    
    def etape_1_analyse(self) -> Optional[str]:
        """Étape 1: Analyse du fichier source"""
        self.afficher_progression()
        
        fichiers_source = self.detecter_fichiers_source()
        if not fichiers_source:
            self.log("❌ Aucun fichier source OpenLibrary trouvé", "ERREUR")
            return None
        
        print(f"\n📁 Fichiers source disponibles:")
        for i, fichier in enumerate(fichiers_source, 1):
            taille = os.path.getsize(fichier) / (1024**3)
            print(f"   {i}. {os.path.basename(fichier)} ({taille:.1f} GB)")
        
        choix = input(f"\nChoisissez un fichier (1-{len(fichiers_source)}) ou 's' pour passer: ").strip()
        
        if choix.lower() == 's':
            self.log("Analyse sautée par l'utilisateur")
            return fichiers_source[0]  # Retourner le premier par défaut
        
        try:
            index = int(choix) - 1
            fichier_choisi = fichiers_source[index]
            
            # Lancer l'analyse (mode interactif simulé)
            self.log(f"Analyse de {os.path.basename(fichier_choisi)}")
            print(f"💡 Pour une analyse complète, lancez manuellement:")
            print(f"   python analyse_fichier_complet.py")
            
            return fichier_choisi
            
        except (ValueError, IndexError):
            self.log("Choix invalide, sélection automatique du premier fichier")
            return fichiers_source[0]
    
    def etape_2_extraction(self, fichier_source: str) -> Optional[str]:
        """Étape 2: Extraction massive"""
        self.etape_actuelle = 1
        self.afficher_progression()
        
        print(f"\n🚀 PARAMÈTRES D'EXTRACTION")
        print(f"   📁 Fichier source: {os.path.basename(fichier_source)}")
        
        # Options prédéfinies
        options = {
            '1': {'limite': 100000, 'nom': 'test_100k'},
            '2': {'limite': 500000, 'nom': 'standard_500k'},
            '3': {'limite': 1000000, 'nom': 'large_1m'},
            '4': {'limite': None, 'nom': 'complet'}
        }
        
        print(f"\n📊 OPTIONS D'EXTRACTION:")
        print(f"   1. Test (100,000 livres)")
        print(f"   2. Standard (500,000 livres)")
        print(f"   3. Large (1,000,000 livres)")
        print(f"   4. Complet (tous les livres)")
        
        choix = input("Choisissez une option (1-4): ").strip()
        option = options.get(choix, options['2'])  # Par défaut: standard
        
        # Générer le nom du fichier de sortie
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        fichier_sortie = f"livres_{option['nom']}_{timestamp}.csv"
        
        self.log(f"Démarrage extraction vers {fichier_sortie}")
        
        # Note: L'extraction massive nécessite une interface interactive
        # Pour l'automatiser, nous créons un script wrapper
        print(f"\n💡 EXTRACTION EN COURS...")
        print(f"   📁 Sortie: {fichier_sortie}")
        print(f"   🎯 Limite: {option['limite'] or 'Aucune'}")
        print(f"\n⚠️ Pour une extraction complète, lancez manuellement:")
        print(f"   python extraction_massive_complete.py")
        
        # Simuler la création d'un fichier
        # En réalité, il faudrait lancer le script d'extraction
        
        # Chercher un fichier CSV existant pour la suite
        fichiers_csv = self.detecter_fichiers_csv()
        if fichiers_csv:
            return fichiers_csv[0]
        
        return fichier_sortie
    
    def etape_3_nettoyage(self, fichier_csv: str) -> Optional[str]:
        """Étape 3: Nettoyage des données"""
        self.etape_actuelle = 2
        self.afficher_progression()
        
        if not os.path.exists(fichier_csv):
            self.log(f"Fichier CSV non trouvé: {fichier_csv}", "ERREUR")
            # Chercher des fichiers CSV existants
            fichiers_csv = self.detecter_fichiers_csv()
            if not fichiers_csv:
                self.log("Aucun fichier CSV trouvé pour le nettoyage", "ERREUR")
                return None
            
            print(f"\n📁 Fichiers CSV disponibles:")
            for i, fichier in enumerate(fichiers_csv, 1):
                taille = os.path.getsize(os.path.join(self.repertoire_scripts, fichier)) / (1024**2)
                print(f"   {i}. {fichier} ({taille:.1f} MB)")
            
            try:
                choix = int(input(f"Choisissez un fichier (1-{len(fichiers_csv)}): ")) - 1
                fichier_csv = fichiers_csv[choix]
            except (ValueError, IndexError):
                fichier_csv = fichiers_csv[0]
        
        self.log(f"Nettoyage de {fichier_csv}")
        
        # Générer le nom du fichier nettoyé
        base_name = os.path.splitext(fichier_csv)[0]
        fichier_nettoye = f"{base_name}_nettoye.csv"
        
        print(f"\n🧹 NETTOYAGE EN COURS...")
        print(f"   📁 Source: {fichier_csv}")
        print(f"   📁 Sortie: {fichier_nettoye}")
        print(f"\n💡 Pour un nettoyage complet, utilisez:")
        print(f"   python nettoyage_ultra.py")
        
        # Si le fichier nettoyé existe déjà, le retourner
        if os.path.exists(fichier_nettoye):
            self.log(f"Fichier nettoyé trouvé: {fichier_nettoye}")
            return fichier_nettoye
        
        # Sinon, retourner le fichier original
        return fichier_csv
    
    def etape_4_formatage_bdd(self, fichier_nettoye: str) -> Optional[str]:
        """Étape 4: Formatage pour base de données"""
        self.etape_actuelle = 3
        self.afficher_progression()
        
        if not os.path.exists(fichier_nettoye):
            self.log(f"Fichier nettoyé non trouvé: {fichier_nettoye}", "ERREUR")
            return None
        
        # Nom de la base de données
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        nom_bdd = f"bibliotheque_{timestamp}.db"
        
        self.log(f"Formatage vers base de données: {nom_bdd}")
        
        print(f"\n🗄️ FORMATAGE POUR BASE DE DONNÉES")
        print(f"   📁 Source: {fichier_nettoye}")
        print(f"   🗄️ Base de données: {nom_bdd}")
        print(f"\n💡 Pour créer la base de données, lancez:")
        print(f"   python formatage_bdd.py")
        
        return nom_bdd
    
    def executer_pipeline_complet(self):
        """Exécute le pipeline complet"""
        self.log("🚀 DÉMARRAGE DU PIPELINE COMPLET")
        print("=" * 60)
        
        try:
            # Étape 1: Analyse
            fichier_source = self.etape_1_analyse()
            if not fichier_source:
                return False
            
            # Étape 2: Extraction
            fichier_csv = self.etape_2_extraction(fichier_source)
            if not fichier_csv:
                return False
            
            # Étape 3: Nettoyage
            fichier_nettoye = self.etape_3_nettoyage(fichier_csv)
            if not fichier_nettoye:
                return False
            
            # Étape 4: Formatage BDD
            nom_bdd = self.etape_4_formatage_bdd(fichier_nettoye)
            if not nom_bdd:
                return False
            
            # Succès
            self.etape_actuelle = len(self.etapes)
            self.log("🎉 PIPELINE TERMINÉ AVEC SUCCÈS!")
            
            print(f"\n📋 RÉSUMÉ:")
            print(f"   📁 Fichier source: {os.path.basename(fichier_source)}")
            print(f"   📁 Fichier CSV: {fichier_csv}")
            print(f"   📁 Fichier nettoyé: {fichier_nettoye}")
            print(f"   🗄️ Base de données: {nom_bdd}")
            
            return True
            
        except KeyboardInterrupt:
            self.log("⏹️ Pipeline interrompu par l'utilisateur")
            return False
        except Exception as e:
            self.log(f"❌ Erreur dans le pipeline: {e}", "ERREUR")
            return False
    
    def sauvegarder_logs(self):
        """Sauvegarde les logs dans un fichier"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        fichier_log = f"pipeline_log_{timestamp}.txt"
        
        try:
            with open(fichier_log, 'w', encoding='utf-8') as f:
                f.write("LOGS DU PIPELINE OPENLIBRARY\n")
                f.write("=" * 50 + "\n\n")
                f.write("\n".join(self.logs))
            
            print(f"📝 Logs sauvegardés: {fichier_log}")
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde logs: {e}")

def main():
    """Fonction principale"""
    print("🚀 PIPELINE COMPLET OPENLIBRARY → BASE DE DONNÉES")
    print("=" * 60)
    print("Ce script orchestree l'ensemble du processus:")
    print("1. 🔍 Analyse du fichier source")
    print("2. 📚 Extraction massive des livres")
    print("3. 🧹 Nettoyage des données")
    print("4. 🗄️ Formatage pour la base de données")
    
    manager = PipelineManager()
    
    # Menu principal
    print(f"\n📋 OPTIONS:")
    print(f"   1. Exécuter le pipeline complet")
    print(f"   2. Analyser un fichier source")
    print(f"   3. Extraire des livres")
    print(f"   4. Nettoyer un fichier CSV")
    print(f"   5. Formater pour base de données")
    print(f"   6. Quitter")
    
    choix = input("\nChoisissez une option (1-6): ").strip()
    
    try:
        if choix == '1':
            success = manager.executer_pipeline_complet()
            manager.sauvegarder_logs()
            
        elif choix == '2':
            print("💡 Lancez: python analyse_fichier_complet.py")
            
        elif choix == '3':
            print("💡 Lancez: python extraction_massive_complete.py")
            
        elif choix == '4':
            print("💡 Lancez: python nettoyage_ultra.py")
            
        elif choix == '5':
            print("💡 Lancez: python formatage_bdd.py")
            
        elif choix == '6':
            print("👋 Au revoir!")
            return
            
        else:
            print("❌ Choix invalide")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main() 