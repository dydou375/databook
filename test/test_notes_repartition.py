#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier l'extraction de la répartition des notes et des notes des critiques
"""

from babelio_scraper_final import chercher_babelio_par_isbn
import json

def tester_extraction_complète():
    """
    Teste l'extraction complète avec les nouvelles fonctionnalités
    """
    print("=== 🧪 Test d'extraction complète avec répartition des notes ===")
    
    # URL de test pour "Mutation" de Robin Cook
    # D'après vos captures, cela devrait donner :
    # 5★: 2 avis, 4★: 7 avis, 3★: 3 avis, 2★: 0 avis, 1★: 2 avis
    
    # Utiliser un ISBN pour "Mutation" (estimation)
    isbn_test = "9782266151733"  # ISBN possible pour ce livre
    
    print(f"🔍 Test avec ISBN : {isbn_test}")
    
    # Appeler la fonction principale
    data_livre = chercher_babelio_par_isbn(isbn_test)
    
    if data_livre:
        print(f"\n✅ Données extraites avec succès !")
        print("=" * 60)
        
        # Afficher les informations générales
        print(f"📚 Titre : {data_livre.get('titre', 'N/A')}")
        print(f"✍️ Auteur : {data_livre.get('auteur', 'N/A')}")
        print(f"⭐ Note moyenne : {data_livre.get('note_babelio', 'N/A')}")
        print(f"🗳️ Nombre de votes : {data_livre.get('nombre_votes_babelio', 'N/A')}")
        
        # Afficher la répartition des notes
        repartition = data_livre.get('repartition_notes_babelio')
        if repartition:
            print(f"\n📊 RÉPARTITION DES NOTES :")
            print("=" * 40)
            for i in range(5, 0, -1):  # De 5 à 1 étoiles
                nb_avis = repartition.get(f"{i}_etoiles", 0)
                etoiles = "★" * i + "☆" * (5-i)
                print(f"  {etoiles} ({i}★) : {nb_avis} avis")
            
            total_avis = sum(repartition.values())
            print(f"  📈 Total répartition : {total_avis} avis")
        else:
            print(f"\n❌ Répartition des notes non trouvée")
        
        # Afficher les critiques avec leurs notes
        critiques = data_livre.get('critiques_babelio', [])
        if critiques:
            print(f"\n💬 CRITIQUES AVEC NOTES ({len(critiques)}) :")
            print("=" * 60)
            
            for i, critique in enumerate(critiques[:3], 1):  # Afficher les 3 premières
                print(f"\n--- Critique #{i} ---")
                print(f"👤 Utilisateur : {critique.get('utilisateur', 'Anonyme')}")
                print(f"📅 Date : {critique.get('date', 'N/A')}")
                
                note_user = critique.get('note_utilisateur')
                if note_user:
                    etoiles_user = "★" * int(note_user) + "☆" * (5-int(note_user))
                    print(f"⭐ Note utilisateur : {note_user}/5 {etoiles_user}")
                else:
                    print(f"⭐ Note utilisateur : Non trouvée")
                
                texte = critique.get('texte', '')
                if texte:
                    texte_court = texte[:150] + "..." if len(texte) > 150 else texte
                    print(f"💭 Critique : {texte_court}")
        else:
            print(f"\n💬 Aucune critique trouvée")
        
        # Sauvegarder le résultat pour inspection
        timestamp = data_livre.get('date_extraction', '').replace(':', '-').replace('.', '-')
        nom_fichier = f"test_complet_mutation_{timestamp}.json"
        
        # Créer le dossier s'il n'existe pas
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dossier = os.path.join(script_dir, "data_extraite")
        if not os.path.exists(dossier):
            os.makedirs(dossier)
        
        chemin_fichier = os.path.join(dossier, nom_fichier)
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump(data_livre, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Données sauvegardées dans : {chemin_fichier}")
        
        return True
    else:
        print(f"\n❌ Aucune donnée extraite")
        return False

if __name__ == "__main__":
    success = tester_extraction_complète()
    
    if success:
        print(f"\n🎉 Test réussi ! Les nouvelles fonctionnalités fonctionnent !")
    else:
        print(f"\n❌ Test échoué") 