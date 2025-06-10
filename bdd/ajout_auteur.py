#!/usr/bin/env python3
"""
Script pour extraire uniquement les clés d'auteurs depuis le fichier OpenLibrary
et les adapter à la structure de la table auteur (id_auteur, nom, date_naissance, biographie).
"""

import csv
import gzip
from pathlib import Path

def extract_author_keys():
    """
    Extrait uniquement les clés d'auteurs (2 premiers champs) depuis le fichier dump.
    Génère un CSV avec id_auteur pour insertion en base.
    """
    
    # Chemins des fichiers
    input_file = Path("../../data/fichier_openlibrary/ol_dump_authors_2025-05-31.txt.gz")
    output_csv = Path("../../data/fichier_openlibrary/authors_keys.csv")
    output_sql = Path("../../data/fichier_openlibrary/insert_authors_keys.sql")
    
    print(f"Lecture du fichier : {input_file}")
    print(f"Extraction des 2 premiers champs uniquement...")
    
    # Compteurs
    total_lines = 0
    author_keys_found = 0
    
    # Liste pour stocker les clés d'auteurs
    author_keys = []
    
    try:
        # Ouvrir le fichier compressé
        with gzip.open(input_file, 'rt', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                total_lines += 1
                
                # Afficher le progrès
                if line_num % 25000 == 0:
                    print(f"Ligne {line_num:,} - {author_keys_found:,} clés d'auteurs trouvées")
                
                try:
                    # Séparer par tabulations et prendre les 2 premiers champs
                    parts = line.strip().split('\t')
                    
                    if len(parts) >= 2:
                        type_field = parts[0]
                        author_key = parts[1]
                        
                        # Vérifier que c'est bien un auteur
                        if type_field == "/type/author" and author_key.startswith("/authors/"):
                            # Nettoyer la clé (enlever "/authors/")
                            clean_key = author_key.replace("/authors/", "")
                            
                            # Ajouter à la liste (éviter les doublons)
                            if clean_key not in [a['id_auteur'] for a in author_keys]:
                                author_keys.append({
                                    'id_auteur': clean_key,
                                    'nom': None,  # À remplir plus tard si besoin
                                    'date_naissance': None,
                                    'biographie': None
                                })
                                author_keys_found += 1
                                
                except Exception:
                    continue
                    
                # Limite pour test (commenter pour traitement complet)
                if line_num >= 100000:  # Test sur 100k lignes
                    print("Mode test - arrêt après 100k lignes")
                    break
        
        # Sauvegarder en CSV
        print(f"\nSauvegarde de {len(author_keys)} clés d'auteurs...")
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id_auteur', 'nom', 'date_naissance', 'biographie']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for author in author_keys:
                writer.writerow(author)
        
        # Créer le fichier SQL
        with open(output_sql, 'w', encoding='utf-8') as sqlfile:
            sqlfile.write("-- Insertion des clés d'auteurs dans la table auteur\n")
            sqlfile.write("-- Structure: auteur(id_auteur VARCHAR, nom VARCHAR, date_naissance DATE, biographie TEXT)\n\n")
            
            for author in author_keys:
                sql = f"INSERT INTO auteur (id_auteur, nom, date_naissance, biographie) VALUES ('{author['id_auteur']}', NULL, NULL, NULL);\n"
                sqlfile.write(sql)
        
        # Résultats
        print(f"\n{'='*60}")
        print(f"RÉSULTATS DE L'EXTRACTION")
        print(f"{'='*60}")
        print(f"Lignes totales traitées    : {total_lines:,}")
        print(f"Clés d'auteurs extraites   : {author_keys_found:,}")
        print(f"Fichier CSV créé           : {output_csv}")
        print(f"Fichier SQL créé           : {output_sql}")
        
        # Exemples
        print(f"\n{'='*60}")
        print(f"EXEMPLES DE CLÉS D'AUTEURS EXTRAITES")
        print(f"{'='*60}")
        for i, author in enumerate(author_keys[:20], 1):
            print(f"{i:2d}. {author['id_auteur']}")
        
        if len(author_keys) > 20:
            print(f"... et {len(author_keys) - 20:,} autres clés")
            
    except Exception as e:
        print(f"Erreur lors du traitement : {e}")

def extract_from_uncompressed():
    """
    Version pour fichier décompressé ol_dump_authors_2025-05-31.txt
    """
    input_file = Path("../../data/fichier_openlibrary/ol_dump_authors_2025-05-31.txt")
    
    if not input_file.exists():
        print(f"Le fichier {input_file} n'existe pas.")
        print("Utilisez la fonction extract_author_keys() pour le fichier .gz")
        return
    
    output_csv = Path("../../data/fichier_openlibrary/authors_keys.csv")
    output_sql = Path("../../data/fichier_openlibrary/insert_authors_keys.sql")
    
    print(f"Lecture du fichier décompressé : {input_file}")
    
    total_lines = 0
    author_keys_found = 0
    author_keys = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                total_lines += 1
                
                if line_num % 50000 == 0:
                    print(f"Ligne {line_num:,} - {author_keys_found:,} clés trouvées")
                
                try:
                    parts = line.strip().split('\t')
                    
                    if len(parts) >= 2:
                        type_field = parts[0]
                        author_key = parts[1]
                        
                        if type_field == "/type/author" and author_key.startswith("/authors/"):
                            clean_key = author_key.replace("/authors/", "")
                            
                            if clean_key not in [a['id_auteur'] for a in author_keys]:
                                author_keys.append({
                                    'id_auteur': clean_key,
                                    'nom': None,
                                    'date_naissance': None,
                                    'biographie': None
                                })
                                author_keys_found += 1
                                
                except Exception:
                    continue
        
        # Sauvegarde identique à la fonction précédente
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id_auteur', 'nom', 'date_naissance', 'biographie']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for author in author_keys:
                writer.writerow(author)
        
        with open(output_sql, 'w', encoding='utf-8') as sqlfile:
            sqlfile.write("-- Insertion des clés d'auteurs\n\n")
            for author in author_keys:
                sql = f"INSERT INTO auteur (id_auteur, nom, date_naissance, biographie) VALUES ('{author['id_auteur']}', NULL, NULL, NULL);\n"
                sqlfile.write(sql)
        
        print(f"\nRésultats : {author_keys_found:,} clés extraites sur {total_lines:,} lignes")
        print(f"Fichiers créés : {output_csv} et {output_sql}")
        
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    print("=== EXTRACTION DES CLÉS D'AUTEURS ===")
    print("Choisissez votre méthode :")
    print("1. Fichier compressé (.gz)")
    print("2. Fichier décompressé (.txt)")
    
    choice = input("Votre choix (1 ou 2) : ").strip()
    
    if choice == "1":
        extract_author_keys()
    elif choice == "2":
        extract_from_uncompressed()
    else:
        print("Exécution par défaut avec fichier compressé...")
        extract_author_keys()
