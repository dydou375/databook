#!/usr/bin/env python3
"""
Script pour extraire les clés uniques et noms d'auteurs depuis le fichier OpenLibrary
ol_dump_authors_2025-05-31.txt pour insertion en base de données.
"""

import json
import csv
import gzip
import re
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from tqdm import tqdm

def extract_authors_from_dump():
    """
    Extrait les clés uniques et noms d'auteurs depuis le fichier dump OpenLibrary.
    Sauvegarde les résultats dans un fichier CSV.
    """
    
    # Chemins des fichiers
    input_file = Path(r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\ol_dump_authors_2025-05-31.txt.gz")
    output_file = Path(r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\extracted_authors.csv")
    
    print(f"Lecture du fichier : {input_file}")
    print(f"Sauvegarde vers : {output_file}")
    
    # Compteurs pour le suivi
    total_lines = 0
    extracted_authors = 0
    errors = 0
    
    # Liste pour stocker les auteurs extraits
    authors_data = []
    
    try:
        # Ouvrir le fichier compressé
        with gzip.open(input_file, 'rt', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                total_lines += 1
                
                # Afficher le progrès tous les 10000 lignes
                if line_num % 10000 == 0:
                    print(f"Traitement ligne {line_num:,}...")
                
                try:
                    # Séparer les colonnes (tab-separated)
                    parts = line.strip().split('\t')
                    
                    if len(parts) >= 5:
                        type_field = parts[0]
                        author_key = parts[1]
                        json_data = parts[4]
                        
                        # Vérifier que c'est bien un auteur
                        if type_field == "/type/author" and author_key.startswith("/authors/"):
                            try:
                                # Parser le JSON
                                author_data = json.loads(json_data)
                                
                                # Extraire le nom de l'auteur
                                if "name" in author_data:
                                    author_name = author_data["name"]
                                    
                                    # Nettoyer les données
                                    author_key_clean = author_key.replace("/authors/", "")
                                    author_name_clean = str(author_name).strip()
                                    
                                    # Ajouter à la liste
                                    authors_data.append({
                                        'author_key': author_key_clean,
                                        'author_name': author_name_clean,
                                        'full_key': author_key
                                    })
                                    
                                    extracted_authors += 1
                                    
                            except json.JSONDecodeError:
                                errors += 1
                                continue
                                
                except Exception as e:
                    errors += 1
                    continue
                    
                # Limiter pour les tests (retirer cette condition pour traitement complet)
                #if line_num >= 100000:  # Traiter seulement les 100k premières lignes pour test
                #    print("Mode test : arrêt après 100k lignes")
                #    break
    
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return
    
    # Sauvegarder dans un fichier CSV
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['author_key', 'author_name', 'full_key']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Écrire l'en-tête
            writer.writeheader()
            
            # Écrire les données
            for author in authors_data:
                writer.writerow(author)
        
        print(f"\n=== RÉSULTATS ===")
        print(f"Lignes traitées : {total_lines:,}")
        print(f"Auteurs extraits : {extracted_authors:,}")
        print(f"Erreurs : {errors:,}")
        print(f"Fichier sauvegardé : {output_file}")
        
        # Afficher quelques exemples
        print(f"\n=== EXEMPLES D'AUTEURS EXTRAITS ===")
        for i, author in enumerate(authors_data[:10]):
            print(f"{i+1}. Clé: {author['author_key']} | Nom: {author['author_name']}")
            
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")

def create_sql_insert_file():
    """
    Crée un fichier SQL avec les instructions INSERT pour la table auteurs.
    """
    input_csv = Path(r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\extracted_authors.csv")
    output_sql = Path(r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\insert_authors.sql")
    
    if not input_csv.exists():
        print(f"Le fichier {input_csv} n'existe pas. Exécutez d'abord extract_authors_from_dump()")
        return
    
    try:
        with open(input_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            with open(output_sql, 'w', encoding='utf-8') as sqlfile:
                sqlfile.write("-- Instructions SQL pour insérer les auteurs\n")
                sqlfile.write("-- Table supposée : auteur (id_auteur VARCHAR, nom VARCHAR, date_naissance DATE, biographie TEXT)\n\n")
                
                for row in reader:
                    author_key = row['author_key'].replace("'", "''")  # Échapper les apostrophes
                    author_name = row['author_name'].replace("'", "''")  # Échapper les apostrophes
                    
                    sql = f"INSERT INTO auteur (id_auteur, nom, date_naissance, biographie) VALUES ('{author_key}', '{author_name}', NULL, NULL);\n"
                    sqlfile.write(sql)
        
        print(f"Fichier SQL créé : {output_sql}")
        
    except Exception as e:
        print(f"Erreur lors de la création du fichier SQL : {e}")

def insert_authors_to_database():
    """
    Insère les auteurs du fichier CSV dans la base de données PostgreSQL avec SQLAlchemy.
    """
    csv_file = Path(r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\extracted_authors.csv")
    
    if not csv_file.exists():
        print(f"Le fichier CSV {csv_file} n'existe pas.")
        print("Exécutez d'abord extract_authors_from_dump() pour créer le fichier.")
        return
    
    # Paramètres de connexion à la base de données
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/databook"
    
    print("=== INSERTION DANS LA BASE DE DONNÉES (SQLAlchemy) ===")
    print(f"Lecture du fichier CSV : {csv_file}")
    
    try:
        # Créer l'engine SQLAlchemy
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("Connexion à la base de données...")
        
        # Compter d'abord le nombre total de lignes pour la barre de progression
        print("📊 Comptage des auteurs à traiter...")
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            total_authors = sum(1 for line in csvfile) - 1  # -1 pour l'en-tête
        
        print(f"📈 {total_authors:,} auteurs à traiter")
        
        # Lire le fichier CSV avec barre de progression
        authors_inserted = 0
        authors_skipped = 0
        
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Barre de progression avec tqdm
            with tqdm(total=total_authors, desc="🔄 Insertion auteurs", unit="auteurs", 
                     bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
                
                for row in reader:
                    author_key = row['author_key']
                    author_name = row['author_name']
                    
                    try:
                        # Vérifier si l'auteur existe déjà
                        result = session.execute(
                            text("SELECT COUNT(*) FROM auteur WHERE id_auteur = :id_auteur"),
                            {"id_auteur": author_key}
                        ).scalar()
                        
                        # Insérer l'auteur avec gestion automatique des doublons
                        result = session.execute(
                            text("""
                                INSERT INTO auteur (id_auteur, nom, date_naissance, biographie) 
                                VALUES (:id_auteur, :nom, NULL, NULL)
                                ON CONFLICT (id_auteur) DO NOTHING
                                RETURNING id_auteur
                            """),
                            {
                                "id_auteur": author_key,
                                "nom": author_name
                            }
                        )
                        
                        # Vérifier si l'insertion a réussi (retourne une ligne) ou si c'était un doublon
                        if result.fetchone() is not None:
                            authors_inserted += 1
                        else:
                            authors_skipped += 1
                        
                        pbar.set_postfix({
                            "Insérés": f"{authors_inserted:,}", 
                            "Ignorés": f"{authors_skipped:,}"
                        })
                        
                        # Commit périodique
                        if (authors_inserted + authors_skipped) % 1000 == 0:
                            session.commit()
                            
                    except Exception as e:
                        print(f"\n❌ Erreur lors de l'insertion de {author_key}: {e}")
                        session.rollback()
                    
                    # Mettre à jour la barre de progression
                    pbar.update(1)
        
        # Commit final
        session.commit()
        session.close()
        
        print(f"\n=== RÉSULTATS DE L'INSERTION ===")
        print(f"Auteurs insérés     : {authors_inserted:,}")
        print(f"Auteurs ignorés     : {authors_skipped:,} (déjà existants)")
        print(f"Total traité        : {authors_inserted + authors_skipped:,}")
        print("Insertion terminée avec succès !")
        
    except Exception as e:
        print(f"Erreur : {e}")
        if 'session' in locals():
            session.rollback()
            session.close()

def insert_authors_batch():
    """
    Version optimisée avec insertion par batch pour de meilleures performances avec SQLAlchemy.
    """
    csv_file = Path(r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\extracted_authors.csv")
    
    if not csv_file.exists():
        print(f"Le fichier CSV {csv_file} n'existe pas.")
        return
    
    # Paramètres de connexion
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/databook"
    
    batch_size = 1000  # Insérer par batch de 1000
    
    try:
        # Créer l'engine SQLAlchemy
        engine = create_engine(DATABASE_URL)
        
        # Compter le nombre total d'auteurs
        print("📊 Analyse du fichier...")
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            total_authors = sum(1 for line in csvfile) - 1  # -1 pour l'en-tête
        
        print(f"📈 {total_authors:,} auteurs à traiter par batch de {batch_size}")
        
        batch_data = []
        total_inserted = 0
        
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Barre de progression pour l'insertion par batch
            with tqdm(total=total_authors, desc="⚡ Insertion batch", unit="auteurs",
                     bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
                
                for row in reader:
                    batch_data.append({
                        'id_auteur': row['author_key'],
                        'nom': row['author_name'],
                        'date_naissance': None,
                        'biographie': None
                    })
                    
                    if len(batch_data) >= batch_size:
                        # Insérer le batch avec SQLAlchemy
                        with engine.connect() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO auteur (id_auteur, nom, date_naissance, biographie) 
                                    VALUES (:id_auteur, :nom, :date_naissance, :biographie)
                                    ON CONFLICT (id_auteur) DO NOTHING
                                """),
                                batch_data
                            )
                            conn.commit()
                        
                        total_inserted += len(batch_data)
                        pbar.update(len(batch_data))
                        pbar.set_postfix({
                            "Batch": f"{total_inserted//batch_size:,}",
                            "Traités": f"{total_inserted:,}"
                        })
                        
                        batch_data = []
                
                # Insérer le dernier batch
                if batch_data:
                    with engine.connect() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO auteur (id_auteur, nom, date_naissance, biographie) 
                                VALUES (:id_auteur, :nom, :date_naissance, :biographie)
                                ON CONFLICT (id_auteur) DO NOTHING
                            """),
                            batch_data
                        )
                        conn.commit()
                    total_inserted += len(batch_data)
                    pbar.update(len(batch_data))
                    pbar.set_postfix({
                        "Batch": "Final",
                        "Traités": f"{total_inserted:,}"
                    })
        
        engine.dispose()
        print(f"\nInsertion terminée : {total_inserted:,} auteurs traités")
        
    except Exception as e:
        print(f"Erreur : {e}")

def insert_authors_pandas():
    """
    Version ultra-optimisée avec Pandas et SQLAlchemy pour très gros volumes.
    Avec gestion robuste des doublons.
    """
    csv_file = Path(r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\extracted_authors.csv")
    
    if not csv_file.exists():
        print(f"Le fichier CSV {csv_file} n'existe pas.")
        return
    
    # Paramètres de connexion
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/databook"
    
    try:
        # Créer l'engine SQLAlchemy
        engine = create_engine(DATABASE_URL)
        
        print("=== INSERTION ULTRA-OPTIMISÉE AVEC PANDAS ===")
        print(f"📊 Lecture du fichier CSV : {csv_file}")
        
        # Lire le CSV avec Pandas et nettoyer les données
        print("🔍 Chargement et nettoyage des données...")
        df = pd.read_csv(csv_file)
        df = df.dropna(subset=['author_name'])  # Supprimer les noms vides
        df = df.drop_duplicates(subset=['author_key'])  # Supprimer les doublons dans le CSV
        
        # Préparer les données
        df_insert = pd.DataFrame({
            'id_auteur': df['author_key'],
            'nom': df['author_name'],
            'date_naissance': None,
            'biographie': None
        })
        
        print(f"📈 Données préparées : {len(df_insert):,} auteurs uniques")
        
        # Version avec gestion des doublons - insertion chunk par chunk avec ON CONFLICT
        chunk_size = 1000
        total_chunks = (len(df_insert) + chunk_size - 1) // chunk_size
        authors_inserted = 0
        authors_skipped = 0
        
        print(f"⚡ Insertion par chunks de {chunk_size} avec gestion des doublons...")
        
        with tqdm(total=len(df_insert), desc="🚀 Pandas+SQL", unit="auteurs",
                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
            
            for i in range(0, len(df_insert), chunk_size):
                chunk = df_insert.iloc[i:i+chunk_size]
                
                # Convertir le chunk en liste de dictionnaires
                chunk_data = chunk.to_dict('records')
                
                with engine.connect() as conn:
                    # Insérer avec gestion des doublons
                    for record in chunk_data:
                        try:
                            result = conn.execute(
                                text("""
                                    INSERT INTO auteur (id_auteur, nom, date_naissance, biographie) 
                                    VALUES (:id_auteur, :nom, :date_naissance, :biographie)
                                    ON CONFLICT (id_auteur) DO NOTHING
                                    RETURNING id_auteur
                                """),
                                record
                            )
                            
                            if result.fetchone() is not None:
                                authors_inserted += 1
                            else:
                                authors_skipped += 1
                                
                        except Exception as e:
                            print(f"\n❌ Erreur pour {record['id_auteur']}: {e}")
                            authors_skipped += 1
                    
                    conn.commit()
                
                # Mettre à jour la barre de progression
                pbar.update(len(chunk))
                pbar.set_postfix({
                    "✅ Insérés": f"{authors_inserted:,}",
                    "⚠️ Ignorés": f"{authors_skipped:,}",
                    "Chunk": f"{(i//chunk_size)+1}/{total_chunks}"
                })
        
        engine.dispose()
        
        print(f"\n=== RÉSULTATS PANDAS INSERTION ===")
        print(f"✅ Auteurs insérés     : {authors_inserted:,}")
        print(f"⚠️  Auteurs ignorés     : {authors_skipped:,} (doublons)")
        print(f"📊 Total traité        : {authors_inserted + authors_skipped:,}")
        print(f"🎯 Taux de réussite    : {(authors_inserted/(authors_inserted + authors_skipped)*100):.1f}%")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")

def test_extraction_100k():
    """
    FONCTION DE TEST : Extrait et insère seulement 100 000 lignes pour tester.
    """
    # Chemins des fichiers
    input_file = Path(r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\ol_dump_authors_2025-05-31.txt.gz")
    output_file = Path(r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\test_authors_100k.csv")
    
    print("=== TEST : EXTRACTION DE 100 000 LIGNES ===")
    print(f"Lecture du fichier : {input_file}")
    print(f"Sauvegarde vers : {output_file}")
    
    # Compteurs pour le suivi
    total_lines = 0
    extracted_authors = 0
    errors = 0
    
    # Liste pour stocker les auteurs extraits
    authors_data = []
    
    try:
        # Ouvrir le fichier compressé
        with gzip.open(input_file, 'rt', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                total_lines += 1
                
                # Afficher le progrès tous les 10000 lignes
                if line_num % 10000 == 0:
                    print(f"Traitement ligne {line_num:,}... ({extracted_authors:,} auteurs trouvés)")
                
                try:
                    # Séparer les colonnes (tab-separated)
                    parts = line.strip().split('\t')
                    
                    if len(parts) >= 5:
                        type_field = parts[0]
                        author_key = parts[1]
                        json_data = parts[4]
                        
                        # Vérifier que c'est bien un auteur
                        if type_field == "/type/author" and author_key.startswith("/authors/"):
                            try:
                                # Parser le JSON
                                author_data = json.loads(json_data)
                                
                                # Extraire le nom de l'auteur
                                if "name" in author_data:
                                    author_name = author_data["name"]
                                    
                                    # Nettoyer les données
                                    author_key_clean = author_key.replace("/authors/", "")
                                    author_name_clean = str(author_name).strip()
                                    
                                    # Ajouter à la liste
                                    authors_data.append({
                                        'author_key': author_key_clean,
                                        'author_name': author_name_clean,
                                        'full_key': author_key
                                    })
                                    
                                    extracted_authors += 1
                                    
                            except json.JSONDecodeError:
                                errors += 1
                                continue
                                
                except Exception as e:
                    errors += 1
                    continue
                    
                # LIMITE POUR LE TEST : 100 000 lignes
                if line_num >= 100000:
                    print(f"✅ Test terminé après {line_num:,} lignes")
                    break
    
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return None
    
    # Sauvegarder dans un fichier CSV
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['author_key', 'author_name', 'full_key']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Écrire l'en-tête
            writer.writeheader()
            
            # Écrire les données
            for author in authors_data:
                writer.writerow(author)
        
        print(f"\n=== RÉSULTATS DU TEST ===")
        print(f"Lignes traitées      : {total_lines:,}")
        print(f"Auteurs extraits     : {extracted_authors:,}")
        print(f"Erreurs              : {errors:,}")
        print(f"Taux de réussite     : {(extracted_authors/(total_lines-errors)*100):.2f}%")
        print(f"Fichier test créé    : {output_file}")
        
        # Afficher quelques exemples
        print(f"\n=== EXEMPLES D'AUTEURS EXTRAITS ===")
        for i, author in enumerate(authors_data[:10]):
            print(f"{i+1:2d}. {author['author_key']:15s} | {author['author_name']}")
        
        return output_file
            
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")
        return None

def test_insertion_database():
    """
    FONCTION DE TEST : Insère les auteurs du fichier test dans la base de données.
    """
    csv_file = Path(r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\test_authors_100k.csv")
    
    if not csv_file.exists():
        print(f"❌ Le fichier test {csv_file} n'existe pas.")
        print("Exécutez d'abord test_extraction_100k() pour créer le fichier.")
        return
    
    # Paramètres de connexion
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/databook"
    
    print("=== TEST : INSERTION EN BASE DE DONNÉES ===")
    print(f"Lecture du fichier test : {csv_file}")
    
    try:
        # Créer l'engine SQLAlchemy
        engine = create_engine(DATABASE_URL)
        
        print("✅ Connexion à la base de données...")
        
        # Test de connexion
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            print(f"✅ Test de connexion réussi : {result}")
        
        # Lire le fichier CSV
        authors_inserted = 0
        authors_skipped = 0
        
        # Compter le nombre total d'auteurs pour le test
        print("📊 Comptage des auteurs...")
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            total_authors = sum(1 for line in csvfile) - 1  # -1 pour l'en-tête
        
        print(f"📈 {total_authors:,} auteurs à traiter (test)")
        
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Barre de progression pour le test
            with tqdm(total=total_authors, desc="🧪 Test insertion", unit="auteurs",
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
                
                with engine.connect() as conn:
                    for row in reader:
                        author_key = row['author_key']
                        author_name = row['author_name']
                        
                        try:
                            # Vérifier si l'auteur existe déjà
                            result = conn.execute(
                                text("SELECT COUNT(*) FROM auteur WHERE id_auteur = :id_auteur"),
                                {"id_auteur": author_key}
                            ).scalar()
                            
                            # Insérer l'auteur avec gestion automatique des doublons
                            result = conn.execute(
                                text("""
                                    INSERT INTO auteur (id_auteur, nom, date_naissance, biographie) 
                                    VALUES (:id_auteur, :nom, NULL, NULL)
                                    ON CONFLICT (id_auteur) DO NOTHING
                                    RETURNING id_auteur
                                """),
                                {
                                    "id_auteur": author_key,
                                    "nom": author_name
                                }
                            )
                            
                            # Vérifier si l'insertion a réussi
                            if result.fetchone() is not None:
                                authors_inserted += 1
                            else:
                                authors_skipped += 1
                            
                            pbar.set_postfix({
                                "✅ Insérés": f"{authors_inserted:,}",
                                "⚠️ Ignorés": f"{authors_skipped:,}"
                            })
                            
                            # Commit périodique
                            if (authors_inserted + authors_skipped) % 500 == 0:
                                conn.commit()
                                
                        except Exception as e:
                            print(f"\n❌ Erreur lors de l'insertion de {author_key}: {e}")
                            continue
                        
                        # Mettre à jour la barre
                        pbar.update(1)
                    
                    # Commit final
                    conn.commit()
        
        engine.dispose()
        
        print(f"\n=== RÉSULTATS DE L'INSERTION TEST ===")
        print(f"✅ Auteurs insérés     : {authors_inserted:,}")
        print(f"⚠️  Auteurs ignorés     : {authors_skipped:,} (déjà existants)")
        print(f"📊 Total traité        : {authors_inserted + authors_skipped:,}")
        
        if authors_inserted > 0:
            print("🎉 Test d'insertion réussi ! Le système fonctionne correctement.")
        else:
            print("⚠️  Aucun nouvel auteur inséré. Vérifiez si les données existent déjà.")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        print("💡 Vérifiez que PostgreSQL est démarré et que la base 'databook' existe.")

def run_full_test():
    """
    Exécute le test complet : extraction + insertion.
    """
    print("🚀 DÉMARRAGE DU TEST COMPLET")
    print("=" * 50)
    
    # Étape 1 : Extraction
    print("1️⃣ PHASE 1 : Extraction des auteurs (100k lignes)")
    csv_file = test_extraction_100k()
    
    if csv_file is None:
        print("❌ Échec de l'extraction. Test arrêté.")
        return
    
    print("\n" + "=" * 50)
    
    # Étape 2 : Insertion
    print("2️⃣ PHASE 2 : Insertion en base de données")
    test_insertion_database()
    
    print("\n" + "=" * 50)
    print("🏁 TEST COMPLET TERMINÉ")

def ensure_unique_constraint():
    """
    S'assure que la contrainte UNIQUE existe sur la colonne id_auteur.
    """
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/databook"
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Vérifier si la contrainte unique existe déjà
            result = conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'auteur' 
                AND constraint_type = 'UNIQUE' 
                AND constraint_name LIKE '%id_auteur%'
            """)).fetchall()
            
            if not result:
                print("🔧 Création de la contrainte UNIQUE sur id_auteur...")
                # Créer la contrainte unique si elle n'existe pas
                conn.execute(text("""
                    ALTER TABLE auteur 
                    ADD CONSTRAINT auteur_id_auteur_unique 
                    UNIQUE (id_auteur)
                """))
                conn.commit()
                print("✅ Contrainte UNIQUE créée avec succès")
            else:
                print("✅ Contrainte UNIQUE sur id_auteur déjà existante")
        
        engine.dispose()
        
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification/création de la contrainte : {e}")
        print("💡 La contrainte sera gérée par ON CONFLICT DO NOTHING")

if __name__ == "__main__":
    print("=== EXTRACTION ET INSERTION DES AUTEURS OPENLIBRARY ===")
    print("Choisissez une option :")
    print("1. Extraire les auteurs du fichier dump")
    print("2. Créer le fichier SQL")
    print("3. Insérer dans la base de données (SQLAlchemy standard)")
    print("4. Insérer dans la base de données (SQLAlchemy batch)")
    print("5. Insérer dans la base de données (Pandas ultra-rapide)")
    print("6. Tout faire (extraction + insertion)")
    print("7. 🧪 TEST : Extraction 100k lignes")
    print("8. 🧪 TEST : Insertion en base")
    print("9. 🧪 TEST COMPLET (extraction + insertion)")
    print("10. 🔧 Vérifier/Créer contrainte UNIQUE")
    
    choice = input("Votre choix (1-10) : ").strip()
    
    if choice == "1":
        extract_authors_from_dump()
    elif choice == "2":
        create_sql_insert_file()
    elif choice == "3":
        insert_authors_to_database()
    elif choice == "4":
        insert_authors_batch()
    elif choice == "5":
        insert_authors_pandas()
    elif choice == "6":
        print("1. Extraction des données...")
        extract_authors_from_dump()
        print("\n2. Insertion dans la base...")
        insert_authors_batch()
    elif choice == "7":
        test_extraction_100k()
    elif choice == "8":
        test_insertion_database()
    elif choice == "9":
        run_full_test()
    elif choice == "10":
        ensure_unique_constraint()
    else:
        print("Choix invalide. Exécution de l'extraction par défaut...")
        extract_authors_from_dump() 