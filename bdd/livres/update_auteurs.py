#!/usr/bin/env python3
"""
Script pour mettre à jour les noms d'auteurs du schéma test
en utilisant les données du schéma public
"""

from sqlalchemy import create_engine, text
from typing import Dict, List, Optional
import re
import unicodedata

def nettoyer_nom(nom: str, max_length: int = 190) -> str:
    """Nettoie et tronque un nom d'auteur"""
    if not nom:
        return ""
        
    # Convertir les caractères spéciaux en leurs équivalents ASCII
    nom = unicodedata.normalize('NFKD', nom).encode('ASCII', 'ignore').decode('ASCII')
    
    # Supprimer les caractères non désirés
    nom = re.sub(r'[^\w\s\-\',.]', ' ', nom)
    
    # Remplacer les espaces multiples par un seul espace
    nom = re.sub(r'\s+', ' ', nom)
    
    # Tronquer à la longueur maximale en évitant de couper un mot
    if len(nom) > max_length:
        nom = nom[:max_length].rsplit(' ', 1)[0] + '...'
    
    return nom.strip()

def update_auteurs():
    """Met à jour les noms d'auteurs du schéma test"""
    
    # Connexion à la base de données
    database_url = "postgresql://postgres:postgres@localhost:5432/databook"
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # 1. Récupérer les correspondances id_auteur -> nom du schéma public
            print("📚 Récupération des noms d'auteurs du schéma public...")
            result = conn.execute(text("""
                SELECT id_auteur, nom 
                FROM public.auteur 
                WHERE nom IS NOT NULL
            """))
            
            auteurs_public = {row[0]: nettoyer_nom(row[1]) for row in result if row[1]}
            print(f"✅ {len(auteurs_public)} auteurs trouvés dans le schéma public")
            
            # 2. Mettre à jour les auteurs du schéma test
            print("\n🔄 Mise à jour des auteurs dans le schéma test...")
            updated = 0
            skipped = 0
            
            for id_auteur, nom in auteurs_public.items():
                if not nom:  # Ignorer les noms vides après nettoyage
                    skipped += 1
                    continue
                    
                try:
                    result = conn.execute(text("""
                        UPDATE test.auteur 
                        SET nom = :nom,
                            nom_complet = :nom
                        WHERE ol_id = :ol_id
                        AND (nom IS NULL OR nom = '' OR nom_complet LIKE 'Auteur%')
                    """), {
                        "ol_id": id_auteur,
                        "nom": nom
                    })
                    
                    if result.rowcount > 0:
                        updated += 1
                        
                    if updated % 100 == 0 and updated > 0:
                        print(f"   ⏳ {updated} auteurs mis à jour...")
                        
                except Exception as e:
                    print(f"   ⚠️ Erreur pour l'auteur {id_auteur}: {str(e)[:100]}...")
                    skipped += 1
            
            conn.commit()
            print(f"\n✅ Mise à jour terminée!")
            print(f"   📊 {updated} auteurs mis à jour")
            print(f"   ⚠️ {skipped} auteurs ignorés")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🔄 MISE À JOUR DES NOMS D'AUTEURS")
    print("=" * 50)
    update_auteurs() 