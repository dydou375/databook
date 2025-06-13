#!/usr/bin/env python3
"""
Script de nettoyage ultra-robuste pour CSV OpenLibrary
=====================================================

Ce script utilise pandas pour garantir un nettoyage parfait
des fichiers CSV avec une structure cohérente.
"""

import pandas as pd
import os
import re
from typing import List

def nettoyer_csv_ultra_robuste(fichier_source: str) -> str:
    """
    Nettoyage ultra-robuste avec pandas
    
    Args:
        fichier_source: Fichier CSV source
        
    Returns:
        Nom du fichier nettoyé
    """
    print(f"🛠️ NETTOYAGE ULTRA-ROBUSTE")
    print(f"📁 Fichier source: {fichier_source}")
    
    # Nom du fichier de destination
    nom_base = fichier_source.replace('.csv', '')
    fichier_destination = f"{nom_base}_ultra_propre.csv"
    
    try:
        # Lire le fichier avec pandas en ignorant les erreurs
        print("📚 Lecture du fichier (peut prendre quelques minutes)...")
        
        # Essayer différentes méthodes de lecture
        df = None
        
        # Méthode 1: Lecture standard avec gestion d'erreurs
        try:
            df = pd.read_csv(fichier_source, 
                           encoding='utf-8', 
                           on_bad_lines='skip',  # Ignorer les lignes malformées
                           engine='python')  # Moteur plus robuste
            print(f"✅ Lecture réussie avec méthode standard")
        except Exception as e:
            print(f"⚠️ Méthode standard échouée: {e}")
        
        # Méthode 2: Si échec, lecture ligne par ligne
        if df is None:
            print("🔄 Tentative de lecture ligne par ligne...")
            lignes_valides = []
            
            with open(fichier_source, 'r', encoding='utf-8', errors='replace') as f:
                # Lire l'en-tête
                header = next(f).strip().split(',')
                nb_colonnes = len(header)
                print(f"📊 Colonnes attendues: {nb_colonnes}")
                
                for i, ligne in enumerate(f):
                    try:
                        # Nettoyer la ligne
                        ligne = ligne.strip()
                        if not ligne:
                            continue
                            
                        # Vérifier le nombre de colonnes
                        parties = ligne.split(',')
                        if len(parties) == nb_colonnes:
                            # Vérifier que c'est bien une ligne de livre
                            if parties[0] in ['edition', '/type/edition'] or ligne.startswith('edition,'):
                                lignes_valides.append(parties)
                    except:
                        continue
                    
                    # Afficher le progrès
                    if i % 50000 == 0:
                        print(f"   Traité: {i:,} lignes - Valides: {len(lignes_valides):,}")
            
            # Créer le DataFrame
            if lignes_valides:
                df = pd.DataFrame(lignes_valides, columns=header)
                print(f"✅ Lecture ligne par ligne réussie")
            else:
                print(f"❌ Aucune ligne valide trouvée")
                return None
        
        if df is None or len(df) == 0:
            print(f"❌ Impossible de lire le fichier")
            return None
        
        print(f"📊 Données lues: {len(df):,} lignes × {len(df.columns)} colonnes")
        
        # Nettoyage des données
        print("🧹 Nettoyage des données...")
        
        # 1. Supprimer les lignes entièrement vides
        df = df.dropna(how='all')
        print(f"   Après suppression lignes vides: {len(df):,}")
        
        # 2. Nettoyer les colonnes de base
        colonnes_requises = ['titre', 'type_entree']
        for col in colonnes_requises:
            if col in df.columns:
                # Supprimer les lignes sans titre
                df = df[df[col].notna() & (df[col] != '')]
                print(f"   Après nettoyage {col}: {len(df):,}")
        
        # 3. Nettoyer les caractères problématiques dans le titre
        if 'titre' in df.columns:
            # Supprimer les titres avec trop de caractères spéciaux
            def titre_valide(titre):
                if pd.isna(titre) or titre == '':
                    return False
                # Compter les caractères non-ASCII
                non_ascii = len([c for c in str(titre) if ord(c) > 127])
                return non_ascii < len(str(titre)) * 0.5  # Moins de 50% de caractères spéciaux
            
            df = df[df['titre'].apply(titre_valide)]
            print(f"   Après nettoyage titres: {len(df):,}")
        
        # 4. Nettoyer les années
        if 'annee_publication' in df.columns:
            def annee_valide(annee):
                try:
                    annee_int = int(float(str(annee)))
                    return 1000 <= annee_int <= 2030
                except:
                    return True  # Garder les NaN
            
            df = df[df['annee_publication'].apply(annee_valide)]
            print(f"   Après nettoyage années: {len(df):,}")
        
        # 5. Supprimer les doublons exacts
        nb_avant = len(df)
        df = df.drop_duplicates()
        nb_apres = len(df)
        print(f"   Doublons supprimés: {nb_avant - nb_apres}")
        
        # Sauvegarder le fichier nettoyé
        print(f"💾 Sauvegarde du fichier nettoyé...")
        df.to_csv(fichier_destination, index=False, encoding='utf-8')
        
        # Vérification finale
        print(f"\n✅ NETTOYAGE ULTRA-ROBUSTE TERMINÉ!")
        print(f"📁 Fichier créé: {fichier_destination}")
        print(f"📊 Dimensions finales: {len(df):,} lignes × {len(df.columns)} colonnes")
        
        # Statistiques de qualité
        print(f"\n📈 QUALITÉ DES DONNÉES NETTOYÉES:")
        for col in df.columns[:8]:  # Premières 8 colonnes
            non_null = df[col].notna().sum()
            pourcentage = (non_null / len(df)) * 100
            print(f"   • {col:<20}: {non_null:,} ({pourcentage:.1f}%)")
        
        # Exemples
        print(f"\n📚 EXEMPLES DE LIVRES NETTOYÉS:")
        for i, livre in df.head(3).iterrows():
            titre = livre.get('titre', 'Sans titre')
            print(f"   {i+1}. {str(titre)[:60]}...")
        
        # Test de lecture final
        print(f"\n🔍 TEST DE LECTURE FINAL...")
        try:
            df_test = pd.read_csv(fichier_destination)
            print(f"✅ Fichier nettoyé lu avec succès: {len(df_test):,} lignes")
            return fichier_destination
        except Exception as e:
            print(f"❌ Erreur lors du test final: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return None

def main():
    """Fonction principale"""
    print("🛠️ NETTOYAGE ULTRA-ROBUSTE CSV OPENLIBRARY")
    print("=" * 60)
    
    # Détecter les fichiers CSV
    fichiers_csv = [f for f in os.listdir('.') if f.endswith('.csv') and 'openlibrary' in f]
    
    if not fichiers_csv:
        print("❌ Aucun fichier OpenLibrary CSV trouvé")
        return
    
    print("📁 Fichiers CSV disponibles:")
    for i, fichier in enumerate(fichiers_csv, 1):
        taille = os.path.getsize(fichier) / (1024*1024)  # MB
        print(f"   {i}. {fichier} ({taille:.1f} MB)")
    
    # Sélection
    try:
        choix = int(input(f"\nChoisissez un fichier (1-{len(fichiers_csv)}): ")) - 1
        fichier_source = fichiers_csv[choix]
    except (ValueError, IndexError):
        print("❌ Choix invalide")
        return
    
    # Nettoyage
    fichier_nettoye = nettoyer_csv_ultra_robuste(fichier_source)
    
    if fichier_nettoye:
        print(f"\n🎉 SUCCÈS! Votre fichier nettoyé est prêt:")
        print(f"📄 {fichier_nettoye}")
        print(f"\n💡 Vous pouvez maintenant l'utiliser sans problème dans vos analyses!")
    else:
        print(f"\n❌ Échec du nettoyage. Contactez le support.")

if __name__ == "__main__":
    main() 