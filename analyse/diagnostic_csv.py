#!/usr/bin/env python3
"""
Script de diagnostic pour fichier CSV problématique
"""

import pandas as pd
import chardet
import csv

def diagnostiquer_csv(fichier_path):
    """Diagnostique un fichier CSV problématique"""
    
    print("DIAGNOSTIC CSV")
    print("=" * 50)
    
    # 1. Détecter l'encodage
    print("\n[1] DETECTION ENCODAGE:")
    with open(fichier_path, 'rb') as f:
        raw_data = f.read(10000)
        result = chardet.detect(raw_data)
        print(f"    Encodage détecté: {result['encoding']} (confiance: {result['confidence']:.2%})")
    
    encodages_a_tester = [result['encoding'], 'latin-1', 'cp1252', 'utf-8']
    
    # 2. Analyser la structure
    for encodage in encodages_a_tester:
        if encodage is None:
            continue
            
        try:
            print(f"\n[2] ANALYSE AVEC ENCODAGE: {encodage}")
            
            # Lire les premières lignes
            with open(fichier_path, 'r', encoding=encodage) as f:
                lines = [f.readline().strip() for _ in range(5)]
            
            print("    Premières lignes:")
            for i, ligne in enumerate(lines):
                print(f"      Ligne {i+1}: {ligne[:100]}...")
            
            # Détecter les séparateurs
            print("    Analyse des séparateurs:")
            separateurs = [',', ';', '\t', '|']
            for sep in separateurs:
                count = lines[0].count(sep) if lines else 0
                print(f"      '{sep}': {count} occurrences")
            
            # Essayer de lire avec pandas
            for sep in [',', ';', '\t']:
                try:
                    print(f"\n[3] TEST PANDAS avec sep='{sep}':")
                    df_test = pd.read_csv(
                        fichier_path, 
                        encoding=encodage, 
                        sep=sep,
                        nrows=10,  # Lire seulement 10 lignes
                        on_bad_lines='skip'
                    )
                    print(f"      SUCCESS: {df_test.shape[0]} lignes, {df_test.shape[1]} colonnes")
                    print(f"      Colonnes: {list(df_test.columns)[:5]}...")
                    
                    # Essayer de lire tout le fichier
                    print(f"\n[4] TEST COMPLET:")
                    df_complet = pd.read_csv(
                        fichier_path, 
                        encoding=encodage, 
                        sep=sep,
                        on_bad_lines='skip',
                        engine='python'
                    )
                    print(f"      SUCCESS COMPLET: {df_complet.shape}")
                    
                    print(f"\n[SOLUTION] Code à utiliser:")
                    print(f"df = pd.read_csv(")
                    print(f"    r'{fichier_path}',")
                    print(f"    encoding='{encodage}',")
                    print(f"    sep='{sep}',")
                    print(f"    on_bad_lines='skip',")
                    print(f"    engine='python'")
                    print(f")")
                    
                    return df_complet, encodage, sep
                    
                except Exception as e:
                    print(f"      ERREUR: {str(e)[:100]}...")
                    continue
            
        except Exception as e:
            print(f"    ERREUR avec {encodage}: {str(e)[:100]}...")
            continue
    
    print("\n[ERROR] Impossible de lire le fichier avec les méthodes testées")
    return None, None, None

def solution_alternative(fichier_path):
    """Solution alternative : nettoyer le fichier ligne par ligne"""
    print("\n[ALTERNATIVE] Nettoyage ligne par ligne:")
    
    try:
        lignes_propres = []
        lignes_problematiques = []
        
        with open(fichier_path, 'r', encoding='latin-1', errors='ignore') as f:
            for i, ligne in enumerate(f):
                try:
                    # Compter les séparateurs (supposons que c'est une virgule)
                    nb_colonnes = ligne.count(',') + 1
                    if i == 0:
                        nb_colonnes_attendues = nb_colonnes
                        print(f"    Nombre de colonnes attendues: {nb_colonnes_attendues}")
                    
                    if nb_colonnes == nb_colonnes_attendues:
                        lignes_propres.append(ligne.strip())
                    else:
                        lignes_problematiques.append((i+1, nb_colonnes))
                        
                except:
                    lignes_problematiques.append((i+1, "erreur"))
        
        print(f"    Lignes propres: {len(lignes_propres)}")
        print(f"    Lignes problématiques: {len(lignes_problematiques)}")
        
        if lignes_problematiques:
            print("    Premières lignes problématiques:")
            for ligne_num, nb_col in lignes_problematiques[:5]:
                print(f"      Ligne {ligne_num}: {nb_col} colonnes")
        
        # Écrire le fichier nettoyé
        fichier_propre = fichier_path.replace('.csv', '_nettoye.csv')
        with open(fichier_propre, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lignes_propres))
        
        print(f"    Fichier nettoyé créé: {fichier_propre}")
        
        # Essayer de lire le fichier nettoyé
        df = pd.read_csv(fichier_propre)
        print(f"    SUCCESS: Fichier nettoyé lu ({df.shape})")
        
        return df
        
    except Exception as e:
        print(f"    ERREUR alternative: {e}")
        return None

if __name__ == "__main__":
    fichier_path = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\analyse\Biblio_export2240504.csv"
    
    # Diagnostic principal
    df, encodage, sep = diagnostiquer_csv(fichier_path)
    
    # Solution alternative si échec
    if df is None:
        df = solution_alternative(fichier_path) 