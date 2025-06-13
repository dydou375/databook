#!/usr/bin/env python3
"""
Script de test simple pour importer adventure.json dans MongoDB
"""

import json
from pymongo import MongoClient
from datetime import datetime

def main():
    # Connexion MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['databook']
    collection = db['livres']
    
    # Supprimer la collection existante
    collection.drop()
    print("Collection 'livres' supprimée")
    
    # Lire le fichier adventure.json
    fichier = r"data\livre_json\livres_json_redistribues\adventure.json"
    
    with open(fichier, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Fichier chargé: {len(data)} documents")
    
    # Ajouter des métadonnées à chaque document
    for i, doc in enumerate(data):
        doc['_source_file'] = 'adventure.json'
        doc['_import_date'] = datetime.now()
        doc['_id_livre'] = f"ADV_{i+1:03d}"  # ID simple: ADV_001, ADV_002, etc.
    
    # Insérer tous les documents
    try:
        result = collection.insert_many(data)
        print(f"✅ {len(result.inserted_ids)} documents insérés avec succès")
        
        # Vérifier le résultat
        count = collection.count_documents({})
        print(f"📊 Total documents dans la collection: {count}")
        
        # Afficher quelques exemples
        print("\n📖 Premiers titres:")
        for doc in collection.find().limit(5):
            print(f"   - {doc['titre']} ({doc.get('_id_livre', 'pas d ID')})")
            
    except Exception as e:
        print(f"❌ Erreur d'insertion: {e}")

if __name__ == "__main__":
    main() 