#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour importer les données de critiques de livres dans MongoDB
Auteur: Assistant IA
Date: Janvier 2025
"""

import json
import os
from pymongo import MongoClient
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CritiquesBooksImporter:
    """Classe pour importer les données de critiques de livres dans MongoDB"""
    
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="livre_critiques_db"):
        """
        Initialise la connexion MongoDB
        
        Args:
            mongo_uri (str): URI de connexion MongoDB
            db_name (str): Nom de la base de données
        """
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.collection = None
        
    def connect_mongodb(self):
        """Établit la connexion à MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db["critiques_livres"]
            
            # Test de la connexion
            self.client.admin.command('ismaster')
            logger.info(f"Connexion réussie à MongoDB: {self.db_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur de connexion à MongoDB: {e}")
            return False
    
    def load_json_data(self, file_path):
        """
        Charge les données JSON depuis le fichier
        
        Args:
            file_path (str): Chemin vers le fichier JSON
            
        Returns:
            list: Liste des données chargées
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            logger.info(f"Données chargées depuis {file_path}: {len(data)} enregistrements")
            return data
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier {file_path}: {e}")
            return None
    
    def preprocess_data(self, data):
        """
        Préprocesse les données avant insertion
        
        Args:
            data (list): Données brutes
            
        Returns:
            list: Données préprocessées
        """
        processed_data = []
        
        for livre in data:
            # Ajout d'un timestamp d'import
            livre['import_date'] = datetime.now()
            
            # Conversion de l'ISBN en string si c'est un nombre
            if 'isbn' in livre and isinstance(livre['isbn'], (int, float)):
                livre['isbn'] = str(int(livre['isbn']))
            
            # Validation des données obligatoires
            if not all(key in livre for key in ['isbn', 'titre', 'auteur']):
                logger.warning(f"Livre ignoré - données incomplètes: {livre.get('titre', 'Titre inconnu')}")
                continue
            
            # Nettoyage des critiques vides
            if 'critiques_babelio' in livre:
                critiques_valides = []
                for critique in livre['critiques_babelio']:
                    if 'texte' in critique and critique['texte'].strip():
                        critiques_valides.append(critique)
                livre['critiques_babelio'] = critiques_valides
                livre['nombre_critiques_valides'] = len(critiques_valides)
            
            processed_data.append(livre)
        
        logger.info(f"Données préprocessées: {len(processed_data)} livres valides")
        return processed_data
    
    def create_indexes(self):
        """Crée les index pour optimiser les performances"""
        try:
            # Index sur ISBN (unique)
            self.collection.create_index("isbn", unique=True)
            
            # Index sur titre et auteur
            self.collection.create_index("titre")
            self.collection.create_index("auteur")
            
            # Index sur la note Babelio
            self.collection.create_index("note_babelio")
            
            # Index composé pour les recherches combinées
            self.collection.create_index([("auteur", 1), ("titre", 1)])
            
            # Index sur la date d'extraction
            self.collection.create_index("date_extraction")
            
            logger.info("Index créés avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création des index: {e}")
    
    def import_data(self, data):
        """
        Importe les données dans MongoDB
        
        Args:
            data (list): Données à importer
            
        Returns:
            dict: Statistiques d'import
        """
        stats = {
            'total': len(data),
            'inserted': 0,
            'updated': 0,
            'errors': 0
        }
        
        for livre in data:
            try:
                # Utilise upsert pour éviter les doublons sur ISBN
                result = self.collection.replace_one(
                    {'isbn': livre['isbn']},
                    livre,
                    upsert=True
                )
                
                if result.upserted_id:
                    stats['inserted'] += 1
                else:
                    stats['updated'] += 1
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'insertion du livre {livre.get('titre', 'Inconnu')}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def get_collection_stats(self):
        """Retourne les statistiques de la collection"""
        try:
            total_docs = self.collection.count_documents({})
            
            # Statistiques par auteur
            pipeline_auteurs = [
                {"$group": {"_id": "$auteur", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            top_auteurs = list(self.collection.aggregate(pipeline_auteurs))
            
            # Moyenne des notes
            pipeline_moyenne = [
                {"$group": {"_id": None, "moyenne_notes": {"$avg": "$note_babelio"}}}
            ]
            moyenne_result = list(self.collection.aggregate(pipeline_moyenne))
            moyenne_notes = moyenne_result[0]['moyenne_notes'] if moyenne_result else 0
            
            return {
                'total_livres': total_docs,
                'moyenne_notes_babelio': round(moyenne_notes, 2),
                'top_auteurs': top_auteurs
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            return None
    
    def close_connection(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Connexion MongoDB fermée")

def main():
    """Fonction principale"""
    # Configuration
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(current_dir, "livre_critique")
    
    # Paramètres MongoDB (à adapter selon votre configuration)
    MONGO_URI = "mongodb://localhost:27017/"  # Changez si nécessaire
    DB_NAME = "databook"
    
    # Initialisation de l'importeur
    importer = CritiquesBooksImporter(MONGO_URI, DB_NAME)
    
    try:
        # Connexion à MongoDB
        if not importer.connect_mongodb():
            logger.error("Impossible de se connecter à MongoDB")
            return
        
        # Chargement des données
        logger.info("Chargement des données JSON...")
        raw_data = importer.load_json_data(json_file)
        
        if raw_data is None:
            logger.error("Impossible de charger les données")
            return
        
        # Préprocessing
        logger.info("Préprocessing des données...")
        processed_data = importer.preprocess_data(raw_data)
        
        # Création des index
        logger.info("Création des index...")
        importer.create_indexes()
        
        # Import des données
        logger.info("Import des données dans MongoDB...")
        stats = importer.import_data(processed_data)
        
        # Affichage des résultats
        logger.info("=== RÉSULTATS D'IMPORT ===")
        logger.info(f"Total traité: {stats['total']}")
        logger.info(f"Nouveaux livres insérés: {stats['inserted']}")
        logger.info(f"Livres mis à jour: {stats['updated']}")
        logger.info(f"Erreurs: {stats['errors']}")
        
        # Statistiques de la collection
        logger.info("\n=== STATISTIQUES DE LA COLLECTION ===")
        collection_stats = importer.get_collection_stats()
        if collection_stats:
            logger.info(f"Total de livres: {collection_stats['total_livres']}")
            logger.info(f"Note moyenne Babelio: {collection_stats['moyenne_notes_babelio']}")
            logger.info("Top 5 auteurs:")
            for auteur in collection_stats['top_auteurs'][:5]:
                logger.info(f"  - {auteur['_id']}: {auteur['count']} livre(s)")
        
        logger.info("\n=== IMPORT TERMINÉ AVEC SUCCÈS ===")
        
    except Exception as e:
        logger.error(f"Erreur générale: {e}")
        
    finally:
        importer.close_connection()

if __name__ == "__main__":
    main() 