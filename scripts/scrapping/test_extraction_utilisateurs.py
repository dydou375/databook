#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier l'extraction des noms d'utilisateurs des critiques
"""

from babelio_scraper_final import scraper_fiche_babelio
import json

def tester_extraction_utilisateurs():
    """
    Teste spécifiquement l'extraction des noms d'utilisateurs
    """
    print("=== 🧪 Test d'extraction des noms d'utilisateurs ===")
    
    # URL de "Mutation" de Robin Cook (avec la critique de CatF visible)
    url_mutation = "https://www.babelio.com/livres/Cook-Mutation/23159"
    
    print(f"🔍 Test avec URL : {url_mutation}")
    print(f"👤 Utilisateur attendu dans les critiques : 'CatF' (d'après votre capture)")
    
    # Appeler la fonction de scraping
    data_livre = scraper_fiche_babelio(url_mutation, "TEST-UTILISATEURS")
    
    if data_livre:
        critiques = data_livre.get('critiques_babelio', [])
        
        print(f"\n📊 RÉSULTATS :")
        print("=" * 50)
        print(f"📚 Titre : {data_livre.get('titre', 'N/A')}")
        print(f"💬 Nombre de critiques trouvées : {len(critiques)}")
        
        if critiques:
            print(f"\n👥 UTILISATEURS EXTRAITS :")
            print("-" * 30)
            
            utilisateurs_trouves = []
            critiques_avec_utilisateur = 0
            
            for i, critique in enumerate(critiques, 1):
                utilisateur = critique.get('utilisateur')
                date = critique.get('date', 'N/A')
                note = critique.get('note_utilisateur', 'N/A')
                
                if utilisateur:
                    critiques_avec_utilisateur += 1
                    utilisateurs_trouves.append(utilisateur)
                    status = "✅"
                    # Vérifier si c'est CatF comme dans votre capture
                    if utilisateur.lower() == "catf":
                        status += " 🎯 (CatF trouvé !)"
                else:
                    status = "❌"
                    utilisateur = "NON TROUVÉ"
                
                print(f"  {i:2d}. {status} {utilisateur:15} | Date: {date:15} | Note: {note}")
            
            print(f"\n📈 STATISTIQUES :")
            print(f"  ✅ Critiques avec utilisateur : {critiques_avec_utilisateur}/{len(critiques)}")
            print(f"  📋 Utilisateurs uniques : {len(set(utilisateurs_trouves))}")
            
            if "CatF" in utilisateurs_trouves:
                print(f"  🎯 CatF trouvé : ✅ SUCCESS !")
            else:
                print(f"  🎯 CatF trouvé : ❌ Non trouvé")
                print(f"     Utilisateurs trouvés : {list(set(utilisateurs_trouves))}")
            
            # Afficher quelques critiques complètes
            print(f"\n💬 DÉTAIL DES PREMIÈRES CRITIQUES :")
            print("=" * 60)
            
            for i, critique in enumerate(critiques[:3], 1):
                print(f"\n--- Critique #{i} ---")
                print(f"👤 Utilisateur : {critique.get('utilisateur', '❌ NON TROUVÉ')}")
                print(f"📅 Date : {critique.get('date', 'N/A')}")
                print(f"⭐ Note : {critique.get('note_utilisateur', 'N/A')}")
                
                texte = critique.get('texte', '')
                if texte:
                    texte_extrait = texte[:100] + "..." if len(texte) > 100 else texte
                    print(f"💭 Extrait : {texte_extrait}")
                else:
                    print(f"💭 Texte : Non trouvé")
        
        else:
            print(f"\n❌ Aucune critique trouvée")
        
        # Sauvegarder pour inspection
        import os
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nom_fichier = f"test_utilisateurs_{timestamp}.json"
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dossier = os.path.join(script_dir, "data_extraite")
        if not os.path.exists(dossier):
            os.makedirs(dossier)
        
        chemin_fichier = os.path.join(dossier, nom_fichier)
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump(data_livre, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Données complètes sauvegardées : {chemin_fichier}")
        
        return len(critiques) > 0 and critiques_avec_utilisateur > 0
    else:
        print(f"\n❌ Échec de l'extraction des données")
        return False

if __name__ == "__main__":
    success = tester_extraction_utilisateurs()
    
    if success:
        print(f"\n🎉 Test réussi ! L'extraction des utilisateurs fonctionne.")
    else:
        print(f"\n❌ Test échoué - problème d'extraction des utilisateurs.") 