#!/usr/bin/env python3
"""
Script simple pour extraire les clés uniques et noms d'auteurs depuis le fichier 
ol_dump_authors_2025-05-31.txt (version décompressée).
"""

import json
import csv
from pathlib import Path

def extract_authors_simple():
    """
    Version simple pour extraire les auteurs depuis le fichier texte décompressé.
    """
    
    # Chemins des fichiers
    input_file = Path("../data/fichier_openlibrary/ol_dump_authors_2025-05-31.txt")
    output_csv = Path("../data/fichier_openlibrary/extracted_authors.csv")
    output_sql = Path("../data/fichier_openlibrary/insert_authors.sql")
    
    print(f"Lecture du fichier : {input_file}")
    
    # Vérifier que le fichier existe
    if not input_file.exists():
        print(f"ERREUR: Le fichier {input_file} n'existe pas.")
        print("Vous devez d'abord décompresser le fichier .gz ou utiliser extract_authors.py")
        return
    
    # Compteurs
    total_lines = 0
    extracted_authors = 0
    errors = 0
    
    # Liste pour stocker les auteurs
    authors_data = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                total_lines += 1
                
                # Afficher le progrès
                if line_num % 50000 == 0:
                    print(f"Traité {line_num:,} lignes - {extracted_authors:,} auteurs extraits")
                
                try:
                    # Diviser la ligne par tabulations
                    columns = line.strip().split('\t')
                    
                    if len(columns) >= 5:
                        type_col = columns[0]
                        author_key = columns[1]
                        json_data = columns[4]
                        
                        # Vérifier que c'est un auteur
                        if type_col == "/type/author" and author_key.startswith("/authors/"):
                            try:
                                # Parser le JSON
                                data = json.loads(json_data)
                                
                                # Extraire le nom
                                if "name" in data:
                                    name = data["name"]
                                    
                                    # Nettoyer les données
                                    clean_key = author_key.replace("/authors/", "")
                                    clean_name = str(name).strip()
                                    
                                    # Ajouter aux résultats
                                    authors_data.append({
                                        'key': clean_key,
                                        'name': clean_name,
                                        'full_key': author_key
                                    })
                                    
                                    extracted_authors += 1
                                    
                            except json.JSONDecodeError:
                                errors += 1
                                
                except Exception:
                    errors += 1
                    
                # Limite pour test (commenter pour traitement complet)
                # if line_num >= 200000:
                #     print("Mode test - arrêt après 200k lignes")
                #     break
        
        # Sauvegarder en CSV
        print(f"\nSauvegarde de {len(authors_data)} auteurs...")
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['author_key', 'author_name', 'full_key'])
            
            for author in authors_data:
                writer.writerow([author['key'], author['name'], author['full_key']])
        
        # Créer le fichier SQL
        with open(output_sql, 'w', encoding='utf-8') as sqlfile:
            sqlfile.write("-- Insertion des auteurs dans la table auteurs\n")
            sqlfile.write("-- Structure supposée: auteurs(id_auteur VARCHAR, nom_auteur TEXT)\n\n")
            
            for author in authors_data:
                key_escaped = author['key'].replace("'", "''")
                name_escaped = author['name'].replace("'", "''")
                
                sql_line = f"INSERT INTO auteurs (id_auteur, nom_auteur) VALUES ('{key_escaped}', '{name_escaped}');\n"
                sqlfile.write(sql_line)
        
        # Résultats
        print(f"\n{'='*50}")
        print(f"RÉSULTATS DE L'EXTRACTION")
        print(f"{'='*50}")
        print(f"Lignes totales traitées : {total_lines:,}")
        print(f"Auteurs extraits        : {extracted_authors:,}")
        print(f"Erreurs rencontrées     : {errors:,}")
        print(f"Fichier CSV créé        : {output_csv}")
        print(f"Fichier SQL créé        : {output_sql}")
        
        # Exemples
        print(f"\n{'='*50}")
        print(f"EXEMPLES D'AUTEURS EXTRAITS")
        print(f"{'='*50}")
        for i, author in enumerate(authors_data[:15], 1):
            print(f"{i:2d}. {author['key']:15s} | {author['name']}")
        
        if len(authors_data) > 15:
            print(f"... et {len(authors_data) - 15:,} autres auteurs")
            
    except Exception as e:
        print(f"Erreur lors du traitement : {e}")

if __name__ == "__main__":
    print("=== EXTRACTION SIMPLE DES AUTEURS ===")
    extract_authors_simple() 