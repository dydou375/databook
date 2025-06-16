#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier l'extraction avec l'URL directe de Mutation
"""

from babelio_scraper_final import scraper_fiche_babelio
import json

def tester_avec_url_directe():
    """
    Teste l'extraction avec l'URL directe de Mutation
    """
    print("=== 🧪 Test avec URL directe de Mutation ===")
    
    # URL directe de "Mutation" de Robin Cook (de vos captures)
    url_mutation = "https://www.babelio.com/livres/Cook-Mutation/23159"
    
    print(f"🔍 Test avec URL : {url_mutation}")
    
    # Appeler directement la fonction de scraping
    data_livre = scraper_fiche_babelio(url_mutation, "TEST-MUTATION")
    
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
            
            # Comparaison avec votre capture (5★:2, 4★:7, 3★:3, 2★:0, 1★:2)
            attendu = {"5_etoiles": 2, "4_etoiles": 7, "3_etoiles": 3, "2_etoiles": 0, "1_etoiles": 2}
            print(f"\n🎯 Comparaison avec la capture :")
            for i in range(5, 0, -1):
                trouve = repartition.get(f"{i}_etoiles", 0)
                attendu_val = attendu.get(f"{i}_etoiles", 0)
                status = "✅" if trouve == attendu_val else "❌"
                print(f"  {i}★ : trouvé={trouve}, attendu={attendu_val} {status}")
        else:
            print(f"\n❌ Répartition des notes non trouvée")
        
        # Afficher les critiques avec leurs notes
        critiques = data_livre.get('critiques_babelio', [])
        if critiques:
            print(f"\n💬 CRITIQUES AVEC NOTES ({len(critiques)}) :")
            print("=" * 60)
            
            critiques_avec_notes = [c for c in critiques if c.get('note_utilisateur')]
            print(f"📊 Critiques avec note : {len(critiques_avec_notes)}/{len(critiques)}")
            
            for i, critique in enumerate(critiques[:5], 1):  # Afficher les 5 premières
                print(f"\n--- Critique #{i} ---")
                print(f"👤 Utilisateur : {critique.get('utilisateur', 'Anonyme')}")
                print(f"📅 Date : {critique.get('date', 'N/A')}")
                
                note_user = critique.get('note_utilisateur')
                if note_user:
                    try:
                        note_int = int(float(note_user))
                        etoiles_user = "★" * note_int + "☆" * (5-note_int)
                        print(f"⭐ Note utilisateur : {note_user}/5 {etoiles_user}")
                    except (ValueError, TypeError):
                        print(f"⭐ Note utilisateur : {note_user} (format non standard)")
                else:
                    print(f"⭐ Note utilisateur : Non trouvée")
                
                texte = critique.get('texte', '')
                if texte:
                    texte_court = texte[:100] + "..." if len(texte) > 100 else texte
                    print(f"💭 Critique : {texte_court}")
        else:
            print(f"\n💬 Aucune critique trouvée")
        
        # Sauvegarder le résultat pour inspection
        import os
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nom_fichier = f"test_mutation_direct_{timestamp}.json"
        
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
    success = tester_avec_url_directe()
    
    if success:
        print(f"\n🎉 Test réussi ! Vérifiez les nouvelles fonctionnalités !")
    else:
        print(f"\n❌ Test échoué") 