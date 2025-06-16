#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier la création de fichiers JSON
"""

import json
import os
from datetime import datetime

def creer_fichier_test():
    """
    Crée un fichier JSON de test pour vérifier que tout fonctionne
    """
    # Créer le dossier s'il n'existe pas
    dossier = "data_extraite"
    if not os.path.exists(dossier):
        os.makedirs(dossier)
        print(f"✅ Dossier '{dossier}' créé")
    else:
        print(f"📁 Dossier '{dossier}' existe déjà")
    
    # Données de test
    donnees_test = [
        {
            "isbn": "978-2-266-23024-3",
            "titre": "Test Livre 1",
            "auteur": "Auteur Test",
            "resume_babelio": "Ceci est un résumé de test pour vérifier que la structure JSON fonctionne correctement.",
            "note_babelio": 4.2,
            "nombre_votes_babelio": 150,
            "critiques_babelio": [
                {
                    "utilisateur": "TestUser1",
                    "date": "15 janvier 2024",
                    "note_utilisateur": 5,
                    "texte": "Excellent livre, je le recommande vivement !"
                },
                {
                    "utilisateur": "TestUser2", 
                    "date": "10 janvier 2024",
                    "note_utilisateur": 4,
                    "texte": "Très bon livre, bien écrit et captivant."
                }
            ],
            "url_babelio": "https://www.babelio.com/livres/test1",
            "date_extraction": datetime.now().isoformat(),
            "nombre_critiques": 2
        },
        {
            "isbn": "978-2-266-23024-4",
            "titre": "Test Livre 2",
            "auteur": "Auteur Test 2",
            "resume_babelio": "Second livre de test avec des données différentes.",
            "note_babelio": 3.8,
            "nombre_votes_babelio": 89,
            "critiques_babelio": [
                {
                    "utilisateur": "TestUser3",
                    "date": "20 janvier 2024", 
                    "note_utilisateur": 3,
                    "texte": "Livre correct mais sans plus."
                }
            ],
            "url_babelio": "https://www.babelio.com/livres/test2",
            "date_extraction": datetime.now().isoformat(),
            "nombre_critiques": 1
        }
    ]
    
    # Nom du fichier avec timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nom_fichier = f"test_babelio_{timestamp}.json"
    chemin_fichier = os.path.join(dossier, nom_fichier)
    
    # Sauvegarde
    try:
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump(donnees_test, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Fichier de test créé : {chemin_fichier}")
        print(f"📊 Contient {len(donnees_test)} livres de test")
        
        # Afficher le contenu pour vérification
        print(f"\n📄 Aperçu du contenu :")
        for livre in donnees_test:
            print(f"  📚 {livre['titre']} par {livre['auteur']}")
            print(f"      ⭐ Note: {livre['note_babelio']}/5")
            print(f"      💬 Critiques: {livre['nombre_critiques']}")
        
        return chemin_fichier
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier : {e}")
        return None

def verifier_structure_json(chemin_fichier):
    """
    Vérifie que le fichier JSON a la bonne structure
    """
    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            donnees = json.load(f)
        
        print(f"\n🔍 VÉRIFICATION DE LA STRUCTURE :")
        print(f"✅ Fichier JSON valide")
        print(f"✅ Nombre d'entrées : {len(donnees)}")
        
        # Vérifier les champs obligatoires
        champs_obligatoires = ['isbn', 'titre', 'auteur', 'date_extraction']
        
        for i, livre in enumerate(donnees):
            print(f"\n📖 Livre {i+1} :")
            for champ in champs_obligatoires:
                if champ in livre:
                    print(f"  ✅ {champ}: {livre[champ]}")
                else:
                    print(f"  ❌ {champ}: MANQUANT")
            
            if 'critiques_babelio' in livre:
                print(f"  💬 Critiques: {len(livre['critiques_babelio'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")
        return False

if __name__ == "__main__":
    print("=== 🧪 Test de création de fichier JSON ===")
    
    # Créer le fichier de test
    fichier_cree = creer_fichier_test()
    
    if fichier_cree:
        # Vérifier la structure
        verifier_structure_json(fichier_cree)
        
        print(f"\n🎉 Test terminé avec succès !")
        print(f"📁 Votre fichier se trouve dans : {os.path.abspath(fichier_cree)}")
    else:
        print(f"\n❌ Le test a échoué") 