#!/usr/bin/env python3
"""
Script d'importation des fichiers JSON dans MongoDB
================================================

Ce script :
1. Se connecte à MongoDB
2. Crée la base databook
3. Crée une collection unique "livres"
4. Importe tous les documents JSON dans cette collection
"""

import os
import json
from typing import Dict, List, Any
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import BulkWriteError, DuplicateKeyError

class ImportateurMongoDB:
    """Classe pour importer les données JSON dans MongoDB"""
    
    def __init__(self, 
                uri_mongodb: str = "mongodb://localhost:27017/",
                nom_base: str = "databook",
                nom_collection: str = "livres",
                dossier_json: str = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\livre_json\livres_json_redistribues"):
        """
        Initialise l'importateur MongoDB
        
        Args:
            uri_mongodb: URI de connexion MongoDB
            nom_base: Nom de la base de données
            nom_collection: Nom de la collection unique
            dossier_json: Chemin vers le dossier contenant les fichiers JSON
        """
        self.uri_mongodb = uri_mongodb
        self.nom_base = nom_base
        self.nom_collection = nom_collection
        self.dossier_json = os.path.abspath(dossier_json)
        self.client = None
        self.db = None
        self.collection = None
        
    def connecter(self) -> bool:
        """Établit la connexion à MongoDB"""
        try:
            # Connexion à MongoDB
            self.client = MongoClient(self.uri_mongodb)
            
            # Tester la connexion
            self.client.admin.command('ping')
            
            # Sélectionner la base et la collection
            self.db = self.client[self.nom_base]
            self.collection = self.db[self.nom_collection]
            
            print("[SUCCESS] Connexion MongoDB établie")
            print("         Base: {}".format(self.nom_base))
            print("         Collection: {}".format(self.nom_collection))
            print("         URI: {}".format(self.uri_mongodb))
            return True
            
        except Exception as e:
            print("[ERROR] Erreur de connexion MongoDB: {}".format(e))
            return False
    
    def lister_fichiers_json(self) -> List[str]:
        """Liste tous les fichiers JSON dans le dossier"""
        fichiers = []
        
        try:
            for fichier in os.listdir(self.dossier_json):
                if fichier.endswith('.json'):
                    chemin = os.path.join(self.dossier_json, fichier)
                    if os.path.isfile(chemin) and os.path.getsize(chemin) > 0:
                        fichiers.append(chemin)
            
            print("\n[INFO] Fichiers JSON trouvés: {}".format(len(fichiers)))
            for fichier in fichiers:
                taille = os.path.getsize(fichier) / (1024*1024)
                print("       {} ({:.1f} MB)".format(os.path.basename(fichier), taille))
                
        except Exception as e:
            print("[ERROR] Erreur listing fichiers: {}".format(e))
            
        return fichiers
    
    def preparer_collection(self):
        """Prépare la collection et crée les index"""
        try:
            # Supprimer la collection existante
            self.collection.drop()
            print("[INFO] Collection '{}' réinitialisée".format(self.nom_collection))
            
            # Recréer la collection
            self.collection = self.db[self.nom_collection]
            
            # Créer les index (sans id_livre car ce champ n'existe pas)
            self.collection.create_index("titre")
            self.collection.create_index("auteurs")
            
            print("[INFO] Index créés sur: titre, auteurs")
            
        except Exception as e:
            print("[ERROR] Erreur préparation collection: {}".format(e))
    
    def importer_fichier(self, chemin_fichier: str, taille_lot: int = 1000) -> Dict[str, Any]:
        """
        Importe un fichier JSON dans la collection
        Gère les formats JSON Array et JSON Lines
        
        Args:
            chemin_fichier: Chemin vers le fichier JSON
            taille_lot: Nombre de documents à insérer par lot
            
        Returns:
            Dict contenant les statistiques d'import
        """
        stats = {
            'fichier': os.path.basename(chemin_fichier),
            'total_documents': 0,
            'inseres': 0,
            'erreurs': 0,
            'doublons': 0,
            'debut': datetime.now()
        }
        
        try:
            # Détecter le format du fichier
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                premier_char = f.read(1)
                
            if premier_char == '[':
                # Format JSON Array
                print("       Format détecté: JSON Array")
                self._importer_json_array(chemin_fichier, stats, taille_lot)
            else:
                # Format JSON Lines
                print("       Format détecté: JSON Lines")
                self._importer_json_lines(chemin_fichier, stats, taille_lot)
            
            stats['fin'] = datetime.now()
            stats['duree'] = (stats['fin'] - stats['debut']).total_seconds()
            
            print("[SUCCESS] Import terminé: {}".format(os.path.basename(chemin_fichier)))
            print("         Documents traités: {:,}".format(stats['total_documents']))
            print("         Documents insérés: {:,}".format(stats['inseres']))
            print("         Doublons ignorés: {:,}".format(stats['doublons']))
            print("         Erreurs: {:,}".format(stats['erreurs']))
            print("         Durée: {:.1f} secondes".format(stats['duree']))
            
        except Exception as e:
            print("[ERROR] Erreur import {}: {}".format(os.path.basename(chemin_fichier), e))
            stats['erreur_generale'] = str(e)
            
        return stats
    
    def _importer_json_array(self, chemin_fichier: str, stats: Dict, taille_lot: int):
        """Importe un fichier au format JSON Array"""
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    print("[ERROR] Le fichier JSON n'est pas un array")
                    return
                
                documents = []
                for document in data:
                    try:
                        # Ajouter métadonnées
                        document['_source_file'] = os.path.basename(chemin_fichier)
                        document['_import_date'] = datetime.now()
                        
                        documents.append(document)
                        stats['total_documents'] += 1
                        
                        # Insérer par lots
                        if len(documents) >= taille_lot:
                            resultat = self.inserer_lot(documents)
                            stats['inseres'] += resultat['inseres']
                            stats['erreurs'] += resultat['erreurs']
                            stats['doublons'] += resultat['doublons']
                            documents = []
                            
                        # Afficher la progression
                        if stats['total_documents'] % 1000 == 0:
                            print("       {} documents traités...".format(stats['total_documents']))
                            
                    except Exception as e:
                        stats['erreurs'] += 1
                        print("[WARN] Erreur document {}: {}...".format(
                            stats['total_documents'], str(e)[:100]))
                
                # Insérer le dernier lot
                if documents:
                    resultat = self.inserer_lot(documents)
                    stats['inseres'] += resultat['inseres']
                    stats['erreurs'] += resultat['erreurs']
                    stats['doublons'] += resultat['doublons']
                    
            except json.JSONDecodeError as e:
                print("[ERROR] Erreur de format JSON: {}".format(e))
                stats['erreurs'] += 1
    
    def _importer_json_lines(self, chemin_fichier: str, stats: Dict, taille_lot: int):
        """Importe un fichier au format JSON Lines"""
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            documents = []
            for ligne in f:
                try:
                    document = json.loads(ligne)
                    
                    # Ajouter métadonnées
                    document['_source_file'] = os.path.basename(chemin_fichier)
                    document['_import_date'] = datetime.now()
                    
                    documents.append(document)
                    stats['total_documents'] += 1
                    
                    # Insérer par lots
                    if len(documents) >= taille_lot:
                        resultat = self.inserer_lot(documents)
                        stats['inseres'] += resultat['inseres']
                        stats['erreurs'] += resultat['erreurs']
                        stats['doublons'] += resultat['doublons']
                        documents = []
                        
                    # Afficher la progression
                    if stats['total_documents'] % 10000 == 0:
                        print("       {} documents traités...".format(stats['total_documents']))
                        
                except json.JSONDecodeError as e:
                    stats['erreurs'] += 1
                    print("[WARN] Erreur JSON ligne {}: {}...".format(
                        stats['total_documents'], str(e)[:100]))
            
            # Insérer le dernier lot
            if documents:
                resultat = self.inserer_lot(documents)
                stats['inseres'] += resultat['inseres']
                stats['erreurs'] += resultat['erreurs']
                stats['doublons'] += resultat['doublons']
    
    def inserer_lot(self, documents: List[Dict]) -> Dict[str, int]:
        """Insère un lot de documents en gérant les doublons"""
        resultat = {'inseres': 0, 'erreurs': 0, 'doublons': 0}
        
        try:
            # Tentative d'insertion en lot
            self.collection.insert_many(documents, ordered=False)
            resultat['inseres'] = len(documents)
            
        except BulkWriteError as bwe:
            # Analyser les résultats détaillés
            resultat['inseres'] = bwe.details.get('nInserted', 0)
            
            # Compter les doublons (erreur 11000)
            for error in bwe.details.get('writeErrors', []):
                if error.get('code') == 11000:  # Duplicate key
                    resultat['doublons'] += 1
                else:
                    resultat['erreurs'] += 1
                    
        except Exception as e:
            print("[ERROR] Erreur insertion lot: {}".format(e))
            resultat['erreurs'] = len(documents)
            
        return resultat
    
    def importer_tous_fichiers(self) -> Dict[str, Any]:
        """Importe tous les fichiers JSON trouvés dans une seule collection"""
        stats_globales = {
            'fichiers_traites': 0,
            'total_documents': 0,
            'total_inseres': 0,
            'total_doublons': 0,
            'total_erreurs': 0,
            'duree_totale': 0,
            'debut': datetime.now()
        }
        
        # Lister les fichiers
        fichiers = self.lister_fichiers_json()
        if not fichiers:
            print("[ERROR] Aucun fichier JSON trouvé")
            return stats_globales
        
        # Préparer la collection
        self.preparer_collection()
        
        # Importer chaque fichier
        for i, fichier in enumerate(fichiers, 1):
            print("\n[INFO] Import fichier {}/{}: {}".format(
                i, len(fichiers), os.path.basename(fichier)))
            stats = self.importer_fichier(fichier)
            
            stats_globales['fichiers_traites'] += 1
            stats_globales['total_documents'] += stats['total_documents']
            stats_globales['total_inseres'] += stats['inseres']
            stats_globales['total_doublons'] += stats.get('doublons', 0)
            stats_globales['total_erreurs'] += stats['erreurs']
            stats_globales['duree_totale'] += stats.get('duree', 0)
        
        stats_globales['fin'] = datetime.now()
        
        # Afficher le résumé final
        print("\n[SUMMARY] Résumé de l'import:")
        print("          Fichiers traités: {}".format(stats_globales['fichiers_traites']))
        print("          Total documents: {:,}".format(stats_globales['total_documents']))
        print("          Documents insérés: {:,}".format(stats_globales['total_inseres']))
        print("          Doublons ignorés: {:,}".format(stats_globales['total_doublons']))
        print("          Erreurs: {:,}".format(stats_globales['total_erreurs']))
        print("          Durée totale: {:.1f} secondes".format(stats_globales['duree_totale']))
        
        # Statistiques de la collection finale
        count_final = self.collection.count_documents({})
        print("\n[INFO] Collection finale:")
        print("       Nom: {}".format(self.nom_collection))
        print("       Documents: {:,}".format(count_final))
        
        return stats_globales

def main():
    """Fonction principale"""
    print("IMPORT JSON VERS MONGODB - COLLECTION UNIQUE")
    print("=" * 60)
    
    # Paramètres de connexion
    uri_mongodb = input("URI MongoDB [mongodb://localhost:27017/]: ").strip()
    if not uri_mongodb:
        uri_mongodb = "mongodb://localhost:27017/"
    
    nom_base = input("Nom de la base [databook]: ").strip()
    if not nom_base:
        nom_base = "databook"
    
    nom_collection = input("Nom de la collection [livres]: ").strip()
    if not nom_collection:
        nom_collection = "livres"
    
    dossier_json = input("Dossier des fichiers JSON [C:\\Users\\dd758\\Formation_IA_Greta\\Projet_possible certif\\Livre_analyse\\data_book\\databook\\data\\livre_json\\livres_json_redistribues]: ").strip()
    if not dossier_json:
        dossier_json = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\livre_json\livres_json_redistribues"
    
    # Créer l'importateur
    importateur = ImportateurMongoDB(uri_mongodb, nom_base, nom_collection, dossier_json)
    
    # Connexion
    if importateur.connecter():
        # Lancer l'import
        importateur.importer_tous_fichiers()
        print("\n[SUCCESS] Import terminé dans la collection '{}'".format(nom_collection))

if __name__ == "__main__":
    main() 