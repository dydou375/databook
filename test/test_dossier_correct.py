#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier que le dossier data_extraite se crée au bon endroit
"""

import json
import os
from datetime import datetime

def tester_creation_dossier():
    """
    Teste la création du dossier dans le bon répertoire
    """
    print("=== 🧪 Test de création du dossier au bon endroit ===")
    
    # Obtenir le répertoire du script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Répertoire du script : {script_dir}")
    
    # Créer le dossier data_extraite dans le même répertoire que le script
    dossier = os.path.join(script_dir, "data_extraite")
    print(f"📁 Dossier cible : {dossier}")
    
    if not os.path.exists(dossier):
        os.makedirs(dossier)
        print(f"✅ Dossier créé : {dossier}")
    else:
        print(f"📂 Dossier existe déjà : {dossier}")
    
    # Créer un fichier de test
    test_data = {
        "test": True,
        "message": "Fichier créé au bon endroit !",
        "timestamp": datetime.now().isoformat(),
        "script_directory": script_dir
    }
    
    nom_fichier = f"test_localisation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    chemin_fichier = os.path.join(dossier, nom_fichier)
    
    try:
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Fichier de test créé : {chemin_fichier}")
        
        # Vérifier que le fichier existe
        if os.path.exists(chemin_fichier):
            print(f"✅ Fichier vérifié et accessible")
            
            # Lire le contenu pour vérifier
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                contenu = json.load(f)
            
            print(f"📄 Contenu du fichier :")
            print(f"   Message : {contenu['message']}")
            print(f"   Répertoire : {contenu['script_directory']}")
            
            return True
        else:
            print(f"❌ Fichier non trouvé après création")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier : {e}")
        return False

if __name__ == "__main__":
    success = tester_creation_dossier()
    
    if success:
        print(f"\n🎉 SUCCESS ! Le dossier et les fichiers se créent maintenant au bon endroit !")
        print(f"📍 Tous vos fichiers JSON seront dans : data_extraite/ (à côté du script)")
    else:
        print(f"\n❌ Échec du test") 