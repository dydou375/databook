#!/usr/bin/env python3
"""
Script de nettoyage CSV pour les livres OpenLibrary
==================================================

Ce script nettoie le fichier CSV en supprimant les lignes mal formatées,
les caractères d'encodage problématiques, et les données incomplètes.
"""

import pandas as pd
import csv
import re
import os
from typing import List, Tuple

def analyser_problemes_csv(fichier_csv: str) -> dict:
    """
    Analyse les problèmes dans le fichier CSV
    
    Args:
        fichier_csv: Chemin vers le fichier CSV à analyser
        
    Returns:
        Dictionnaire avec les statistiques des problèmes trouvés
    """
    print(f"🔍 Analyse des problèmes dans: {fichier_csv}")
    
    problemes = {
        'lignes_totales': 0,
        'lignes_malformees': 0,
        'problemes_encodage': 0,
        'colonnes_incorrectes': 0,
        'titres_vides': 0,
        'caracteres_speciaux': 0,
        'exemples_problemes': []
    }
    
    # Lire le fichier ligne par ligne pour détecter les problèmes
    try:
        with open(fichier_csv, 'r', encoding='utf-8', errors='replace') as f:
            # Lire la première ligne pour connaître le nombre de colonnes attendu
            header = next(f).strip()
            colonnes_attendues = len(header.split(','))
            print(f"📊 Nombre de colonnes attendues: {colonnes_attendues}")
            
            for num_ligne, ligne in enumerate(f, 2):  # Commence à 2 car header = ligne 1
                problemes['lignes_totales'] += 1
                
                # Vérifier les problèmes d'encodage
                if '�' in ligne or '\ufffd' in ligne:
                    problemes['problemes_encodage'] += 1
                    if len(problemes['exemples_problemes']) < 5:
                        problemes['exemples_problemes'].append(f"Ligne {num_ligne}: Problème encodage")
                
                # Vérifier le nombre de colonnes
                try:
                    colonnes_actuelles = len(ligne.split(','))
                    if colonnes_actuelles != colonnes_attendues:
                        problemes['colonnes_incorrectes'] += 1
                        if len(problemes['exemples_problemes']) < 10:
                            problemes['exemples_problemes'].append(f"Ligne {num_ligne}: {colonnes_actuelles} colonnes au lieu de {colonnes_attendues}")
                except:
                    problemes['lignes_malformees'] += 1
                
                # Vérifier les caractères spéciaux problématiques
                if re.search(r'[^\x00-\x7F\u00C0-\u024F\u1E00-\u1EFF]', ligne):
                    problemes['caracteres_speciaux'] += 1
                
                # Afficher le progrès
                if problemes['lignes_totales'] % 50000 == 0:
                    print(f"   Analysé: {problemes['lignes_totales']:,} lignes...")
    
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return problemes
    
    # Afficher le résumé
    print(f"\n📋 RÉSUMÉ DES PROBLÈMES:")
    print(f"   • Lignes totales: {problemes['lignes_totales']:,}")
    print(f"   • Lignes malformées: {problemes['lignes_malformees']:,}")
    print(f"   • Problèmes d'encodage: {problemes['problemes_encodage']:,}")
    print(f"   • Colonnes incorrectes: {problemes['colonnes_incorrectes']:,}")
    print(f"   • Caractères spéciaux: {problemes['caracteres_speciaux']:,}")
    
    if problemes['exemples_problemes']:
        print(f"\n🔍 EXEMPLES DE PROBLÈMES:")
        for exemple in problemes['exemples_problemes'][:10]:
            print(f"   - {exemple}")
    
    return problemes

def nettoyer_csv(fichier_source: str, fichier_destination: str, criteres_strict: bool = True) -> bool:
    """
    Nettoie le fichier CSV en supprimant les lignes problématiques
    
    Args:
        fichier_source: Fichier CSV source
        fichier_destination: Fichier CSV nettoyé
        criteres_strict: Si True, applique des critères stricts de nettoyage
        
    Returns:
        True si le nettoyage a réussi
    """
    print(f"\n🧹 NETTOYAGE DU FICHIER CSV")
    print(f"📁 Source: {fichier_source}")
    print(f"📁 Destination: {fichier_destination}")
    print(f"⚙️ Critères stricts: {criteres_strict}")
    
    lignes_gardees = 0
    lignes_supprimees = 0
    
    try:
        with open(fichier_source, 'r', encoding='utf-8', errors='replace') as source, \
             open(fichier_destination, 'w', encoding='utf-8', newline='') as dest:
            
            # Copier l'en-tête
            header = next(source).strip()
            dest.write(header + '\n')
            colonnes_attendues = len(header.split(','))
            
            for num_ligne, ligne in enumerate(source, 2):
                ligne = ligne.strip()
                
                # Critères de suppression
                doit_supprimer = False
                
                # 1. Problèmes d'encodage
                if '�' in ligne or '\ufffd' in ligne:
                    doit_supprimer = True
                
                # 2. Nombre de colonnes incorrect
                try:
                    colonnes_actuelles = len(ligne.split(','))
                    if colonnes_actuelles != colonnes_attendues:
                        doit_supprimer = True
                except:
                    doit_supprimer = True
                
                # 3. Ligne trop courte ou vide
                if len(ligne) < 50:  # Une ligne de livre doit avoir une taille minimum
                    doit_supprimer = True
                
                # 4. Critères stricts supplémentaires
                if criteres_strict:
                    # Supprimer les lignes avec trop de caractères spéciaux
                    if len(re.findall(r'[^\x00-\x7F\u00C0-\u024F\u1E00-\u1EFF]', ligne)) > 10:
                        doit_supprimer = True
                    
                    # Supprimer les lignes qui ne commencent pas par le bon format
                    if not ligne.startswith(('edition,/type/edition', '/type/edition')):
                        doit_supprimer = True
                
                # Garder ou supprimer la ligne
                if doit_supprimer:
                    lignes_supprimees += 1
                else:
                    dest.write(ligne + '\n')
                    lignes_gardees += 1
                
                # Afficher le progrès
                if (lignes_gardees + lignes_supprimees) % 25000 == 0:
                    print(f"   Traité: {lignes_gardees + lignes_supprimees:,} - Gardées: {lignes_gardees:,} - Supprimées: {lignes_supprimees:,}")
    
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return False
    
    print(f"\n✅ NETTOYAGE TERMINÉ!")
    print(f"   📊 Lignes gardées: {lignes_gardees:,}")
    print(f"   🗑️ Lignes supprimées: {lignes_supprimees:,}")
    print(f"   📈 Taux de conservation: {(lignes_gardees/(lignes_gardees+lignes_supprimees)*100):.1f}%")
    
    return True

def verifier_csv_nettoye(fichier_csv: str) -> bool:
    """
    Vérifie que le fichier CSV nettoyé est correct
    
    Args:
        fichier_csv: Chemin vers le fichier CSV à vérifier
        
    Returns:
        True si le fichier est correct
    """
    print(f"\n✅ VÉRIFICATION DU FICHIER NETTOYÉ")
    
    try:
        # Essayer de lire avec pandas
        df = pd.read_csv(fichier_csv)
        
        print(f"📊 Dimensions: {len(df):,} lignes × {len(df.columns)} colonnes")
        print(f"📋 Colonnes: {list(df.columns)}")
        
        # Vérifier la qualité des données
        print(f"\n📈 QUALITÉ DES DONNÉES:")
        for col in df.columns[:10]:  # Premiers 10 colonnes
            non_null = df[col].notna().sum()
            pourcentage = (non_null / len(df)) * 100
            print(f"   • {col:<20}: {non_null:,} ({pourcentage:.1f}%)")
        
        # Exemples de livres
        print(f"\n📚 EXEMPLES DE LIVRES APRÈS NETTOYAGE:")
        for i, livre in df.head(3).iterrows():
            print(f"   {i+1}. {livre.get('titre', 'Sans titre')[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def menu_nettoyage():
    """Menu interactif pour le nettoyage"""
    
    print("🧹 NETTOYAGE DES DONNÉES OPENLIBRARY")
    print("=" * 50)
    
    # Détecter les fichiers CSV disponibles
    fichiers_csv = [f for f in os.listdir('.') if f.endswith('.csv') and 'openlibrary' in f]
    
    if not fichiers_csv:
        print("❌ Aucun fichier OpenLibrary CSV trouvé dans le répertoire actuel")
        return
    
    print("📁 Fichiers CSV disponibles:")
    for i, fichier in enumerate(fichiers_csv, 1):
        taille = os.path.getsize(fichier) / (1024*1024)  # MB
        print(f"   {i}. {fichier} ({taille:.1f} MB)")
    
    # Sélection du fichier
    try:
        choix = int(input(f"\nChoisissez un fichier (1-{len(fichiers_csv)}): ")) - 1
        fichier_source = fichiers_csv[choix]
    except (ValueError, IndexError):
        print("❌ Choix invalide")
        return
    
    print(f"\n📋 MENU DE NETTOYAGE pour {fichier_source}:")
    print("   1. Analyser les problèmes seulement")
    print("   2. Nettoyage rapide (critères modérés)")
    print("   3. Nettoyage strict (critères stricts)")
    print("   4. Nettoyage personnalisé")
    
    choix_action = input("\nChoisissez une action (1-4): ").strip()
    
    if choix_action == '1':
        # Analyse seulement
        analyser_problemes_csv(fichier_source)
    
    elif choix_action in ['2', '3']:
        # Nettoyage automatique
        criteres_strict = (choix_action == '3')
        nom_base = fichier_source.replace('.csv', '')
        suffixe = '_nettoye_strict' if criteres_strict else '_nettoye'
        fichier_destination = f"{nom_base}{suffixe}.csv"
        
        # Analyser d'abord
        analyser_problemes_csv(fichier_source)
        
        # Confirmer le nettoyage
        confirmer = input(f"\nProcéder au nettoyage ? [o/N]: ").strip().lower()
        if confirmer in ['o', 'oui', 'y', 'yes']:
            if nettoyer_csv(fichier_source, fichier_destination, criteres_strict):
                verifier_csv_nettoye(fichier_destination)
        
    elif choix_action == '4':
        print("🔧 Configuration personnalisée pas encore implémentée")
        print("💡 Utilisez les options 2 ou 3 pour l'instant")
    
    else:
        print("❌ Option invalide")

def main():
    """Fonction principale"""
    print("🧹 NETTOYEUR DE FICHIERS CSV OPENLIBRARY")
    print("=" * 60)
    print("Ce script détecte et supprime les lignes mal formatées")
    print("dans vos fichiers CSV d'extraction OpenLibrary.")
    print()
    
    menu_nettoyage()

if __name__ == "__main__":
    main() 