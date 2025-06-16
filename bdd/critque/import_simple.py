#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplifié pour importer les critiques de livres dans MongoDB
Usage: python import_simple.py
"""

import json
import os
from pymongo import MongoClient
from datetime import datetime

def importer_critiques_livres():
    """
    Fonction principale pour importer les données de critiques de livres
    """
    print("🚀 Démarrage de l'import des critiques de livres dans MongoDB...")
    
    # Configuration MongoDB
    MONGO_URI = "mongodb://localhost:27017/"
    DB_NAME = "databook"
    COLLECTION_NAME = "critiques_livres"
    
    try:
        # 1. Connexion à MongoDB
        print("📝 Connexion à MongoDB...")
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Test de connexion
        client.admin.command('ismaster')
        print("✅ Connexion réussie à MongoDB")
        
        # 2. Chargement du fichier JSON
        print("📖 Chargement des données...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file = os.path.join(current_dir, "livre_critique")
        
        with open(json_file, 'r', encoding='utf-8') as file:
            livres_data = json.load(file)
        
        print(f"✅ {len(livres_data)} livres chargés depuis le fichier JSON")
        
        # 3. Nettoyage de la collection existante (optionnel)
        choix = input("🗑️  Vider la collection existante ? (o/N): ").lower().strip()
        if choix in ['o', 'oui', 'y', 'yes']:
            collection.delete_many({})
            print("🗑️  Collection vidée")
        
        # 4. Préparation des données
        print("🔧 Préparation des données...")
        livres_traites = 0
        livres_inseres = 0
        
        for livre in livres_data:
            try:
                # Ajout de métadonnées
                livre['import_date'] = datetime.now()
                livre['import_source'] = "babelio_extraction"
                
                # Conversion ISBN en string
                if 'isbn' in livre:
                    livre['isbn'] = str(livre['isbn'])
                
                # Validation des données minimales
                if not all(key in livre for key in ['isbn', 'titre', 'auteur']):
                    print(f"⚠️  Livre ignoré (données incomplètes): {livre.get('titre', 'Inconnu')}")
                    continue
                
                # Insert ou update
                result = collection.replace_one(
                    {'isbn': livre['isbn']},
                    livre,
                    upsert=True
                )
                
                livres_traites += 1
                if result.upserted_id:
                    livres_inseres += 1
                
            except Exception as e:
                print(f"❌ Erreur pour le livre {livre.get('titre', 'Inconnu')}: {e}")
        
        # 5. Création d'index basiques
        print("🔍 Création des index...")
        try:
            collection.create_index("isbn", unique=True)
            collection.create_index("titre")
            collection.create_index("auteur")
            collection.create_index("note_babelio")
            print("✅ Index créés")
        except Exception as e:
            print(f"⚠️  Erreur lors de la création des index: {e}")
        
        # 6. Statistiques finales
        print("\n" + "="*50)
        print("📊 RÉSULTATS DE L'IMPORT")
        print("="*50)
        print(f"📚 Livres traités: {livres_traites}")
        print(f"➕ Nouveaux livres: {livres_inseres}")
        print(f"🔄 Livres mis à jour: {livres_traites - livres_inseres}")
        print(f"📖 Total dans la collection: {collection.count_documents({})}")
        
        # Quelques statistiques
        total_critiques = collection.aggregate([
            {"$unwind": "$critiques_babelio"},
            {"$count": "total"}
        ])
        total_critiques = list(total_critiques)
        nb_critiques = total_critiques[0]['total'] if total_critiques else 0
        
        moyenne_notes = collection.aggregate([
            {"$group": {"_id": None, "moyenne": {"$avg": "$note_babelio"}}}
        ])
        moyenne_notes = list(moyenne_notes)
        moyenne = round(moyenne_notes[0]['moyenne'], 2) if moyenne_notes else 0
        
        print(f"💬 Total de critiques: {nb_critiques}")
        print(f"⭐ Note moyenne: {moyenne}/5")
        
        print("\n✅ Import terminé avec succès !")
        print(f"🔗 Base de données: {DB_NAME}")
        print(f"📦 Collection: {COLLECTION_NAME}")
        
        # Fermeture de la connexion
        client.close()
        
    except FileNotFoundError:
        print("❌ Fichier 'livre_critique' introuvable dans le répertoire courant")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

def afficher_exemples_requetes():
    """
    Affiche quelques exemples de requêtes MongoDB
    """
    print("\n" + "="*50)
    print("🔍 EXEMPLES DE REQUÊTES MONGODB")
    print("="*50)
    
    exemples = [
        {
            "description": "Trouver tous les livres d'un auteur",
            "requete": 'db.databook.find({"auteur": "RobinCook"})'
        },
        {
            "description": "Livres avec note supérieure à 4",
            "requete": 'db.databook.find({"note_babelio": {"$gt": 4}})'
        },
        {
            "description": "Compter les livres par auteur",
            "requete": '''db.databook.aggregate([
    {"$group": {"_id": "$auteur", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
])'''
        },
        {
            "description": "Livres avec plus de 100 votes",
            "requete": 'db.databook.find({"nombre_votes_babelio": {"$gt": 100}})'
        }
    ]
    
    for i, exemple in enumerate(exemples, 1):
        print(f"\n{i}. {exemple['description']}:")
        print(f"   {exemple['requete']}")

if __name__ == "__main__":
    print("📚 IMPORTEUR DE CRITIQUES DE LIVRES - MONGODB")
    print("=" * 50)
    
    # Import des données
    importer_critiques_livres()
    
    # Affichage des exemples
    afficher_exemples_requetes()
    
    print("\n🎉 Terminé ! Vous pouvez maintenant utiliser MongoDB Compass ou la ligne de commande pour explorer vos données.") 