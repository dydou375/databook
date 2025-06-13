#!/usr/bin/env python3
"""
Formatage des données OpenLibrary pour insertion en base PostgreSQL
==================================================================

Ce script transforme les données CSV nettoyées en format compatible
avec PostgreSQL en utilisant SQLAlchemy.
"""

import pandas as pd
import json
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid

class FormateurPostgreSQL:
    """Classe pour formater les données vers PostgreSQL"""
    
    def __init__(self, database_url: str = "postgresql://postgres:postgres@localhost:5432/databook", prefixe_schema: str = "test"):
        """
        Initialise le formateur PostgreSQL
        
        Args:
            database_url: URL de connexion PostgreSQL
            prefixe_schema: Nom du schéma PostgreSQL (ex: "test", "openlibrary")
        """
        self.database_url = database_url
        self.schema_name = prefixe_schema
        self.engine = None
        self.Session = None
        self.metadata = MetaData()
        self.tables_creees = False
        
        # Noms des tables dans le schéma
        self.table_names = {
            'livre': 'livre',
            'auteur': 'auteur', 
            'editeur': 'editeur',
            'langue': 'langue',
            'sujet': 'sujet',
            'livre_auteur': 'livre_auteur',
            'livre_editeur': 'livre_editeur',
            'livre_langue': 'livre_langue',
            'livre_sujet': 'livre_sujet',
            'extraction_log': 'extraction_log'
        }
        
    def connecter_bdd(self):
        """Établit la connexion à PostgreSQL"""
        try:
            self.engine = create_engine(self.database_url, echo=False)
            
            # Tester la connexion
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ Connexion PostgreSQL établie")
                print(f"   📊 Version: {version.split(',')[0]}")
            
            self.Session = sessionmaker(bind=self.engine)
            return True
            
        except Exception as e:
            print(f"❌ Erreur de connexion PostgreSQL: {e}")
            return False
    
    def creer_schema(self):
        """Crée le schéma PostgreSQL s'il n'existe pas"""
        try:
            with self.engine.connect() as conn:
                # Vérifier si le schéma existe
                result = conn.execute(text("""
                    SELECT schema_name FROM information_schema.schemata 
                    WHERE schema_name = :schema_name
                """), {"schema_name": self.schema_name})
                
                if not result.fetchone():
                    # Créer le schéma
                    conn.execute(text(f'CREATE SCHEMA "{self.schema_name}"'))
                    conn.commit()
                    print(f"✅ Schéma '{self.schema_name}' créé")
                else:
                    print(f"📋 Schéma '{self.schema_name}' existe déjà")
                    
        except Exception as e:
            print(f"❌ Erreur création schéma: {e}")
    
    def lister_tables_existantes(self):
        """Liste les tables existantes dans le schéma"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_name, 
                           (SELECT count(*) FROM information_schema.columns 
                            WHERE table_schema = :schema_name 
                            AND table_name = t.table_name) as nb_colonnes
                    FROM information_schema.tables t
                    WHERE table_schema = :schema_name
                    ORDER BY table_name
                """), {"schema_name": self.schema_name})
                
                tables = result.fetchall()
                
                if tables:
                    print(f"📋 Tables existantes dans le schéma '{self.schema_name}':")
                    for table_name, nb_colonnes in tables:
                        # Compter les lignes
                        try:
                            count_result = conn.execute(text(f'SELECT COUNT(*) FROM "{self.schema_name}"."{table_name}"'))
                            count = count_result.fetchone()[0]
                            print(f"   • {table_name}: {count:,} lignes ({nb_colonnes} colonnes)")
                        except Exception as e:
                            print(f"   • {table_name}: erreur comptage ({nb_colonnes} colonnes)")
                else:
                    print(f"📋 Aucune table dans le schéma '{self.schema_name}'")
                    
        except Exception as e:
            print(f"⚠️ Erreur listing tables: {e}")
    
    def creer_tables(self):
        """Crée les tables dans le schéma PostgreSQL"""
        print(f"🗄️ Création des tables dans le schéma '{self.schema_name}'...")
        
        try:
            # Table LIVRE
            self.livre_table = Table(
                self.table_names['livre'], self.metadata,
                Column('id_livre', Integer, primary_key=True),
                Column('ol_id', String(50), unique=True, nullable=False),
                Column('titre', String(1000), nullable=False),
                Column('sous_titre', String(1000)),
                Column('isbn_10', String(20)),
                Column('isbn_13', String(20)),
                Column('date_publication', String(100)),
                Column('annee_publication', Integer),
                Column('nombre_pages', Integer),
                Column('format_physique', String(100)),
                Column('description', Text),
                Column('couverture_url', String(500)),
                Column('created_at', DateTime, default=datetime.utcnow),
                Column('updated_at', DateTime, default=datetime.utcnow),
                schema=self.schema_name
            )
            
            # Table AUTEUR
            self.auteur_table = Table(
                self.table_names['auteur'], self.metadata,
                Column('id_auteur', Integer, primary_key=True),
                Column('ol_id', String(50), unique=True),
                Column('nom', String(200)),
                Column('prenom', String(200)),
                Column('nom_complet', String(400)),
                Column('date_naissance', String(50)),
                Column('date_deces', String(50)),
                Column('biographie', Text),
                Column('created_at', DateTime, default=datetime.utcnow),
                schema=self.schema_name
            )
            
            # Table EDITEUR
            self.editeur_table = Table(
                self.table_names['editeur'], self.metadata,
                Column('id_editeur', Integer, primary_key=True),
                Column('nom_editeur', String(300), unique=True, nullable=False),
                Column('pays', String(100)),
                Column('annee_creation', Integer),
                Column('created_at', DateTime, default=datetime.utcnow),
                schema=self.schema_name
            )
            
            # Table LANGUE
            self.langue_table = Table(
                self.table_names['langue'], self.metadata,
                Column('id_langue', Integer, primary_key=True),
                Column('code_langue', String(10), unique=True, nullable=False),
                Column('nom_langue', String(100)),
                schema=self.schema_name
            )
            
            # Table SUJET
            self.sujet_table = Table(
                self.table_names['sujet'], self.metadata,
                Column('id_sujet', Integer, primary_key=True),
                Column('nom_sujet', String(200), unique=True, nullable=False),
                Column('categorie', String(100)),
                schema=self.schema_name
            )
            
            # Table LIVRE_AUTEUR
            self.livre_auteur_table = Table(
                self.table_names['livre_auteur'], self.metadata,
                Column('id_livre', Integer, ForeignKey(f'{self.schema_name}.{self.table_names["livre"]}.id_livre')),
                Column('id_auteur', Integer, ForeignKey(f'{self.schema_name}.{self.table_names["auteur"]}.id_auteur')),
                Column('role', String(50), default='author'),
                Column('ordre', Integer, default=1),
                schema=self.schema_name
            )
            
            # Table LIVRE_EDITEUR
            self.livre_editeur_table = Table(
                self.table_names['livre_editeur'], self.metadata,
                Column('id_livre', Integer, ForeignKey(f'{self.schema_name}.{self.table_names["livre"]}.id_livre')),
                Column('id_editeur', Integer, ForeignKey(f'{self.schema_name}.{self.table_names["editeur"]}.id_editeur')),
                Column('ordre', Integer, default=1),
                schema=self.schema_name
            )
            
            # Table LIVRE_LANGUE
            self.livre_langue_table = Table(
                self.table_names['livre_langue'], self.metadata,
                Column('id_livre', Integer, ForeignKey(f'{self.schema_name}.{self.table_names["livre"]}.id_livre')),
                Column('id_langue', Integer, ForeignKey(f'{self.schema_name}.{self.table_names["langue"]}.id_langue')),
                Column('langue_principale', Boolean, default=False),
                schema=self.schema_name
            )
            
            # Table LIVRE_SUJET
            self.livre_sujet_table = Table(
                self.table_names['livre_sujet'], self.metadata,
                Column('id_livre', Integer, ForeignKey(f'{self.schema_name}.{self.table_names["livre"]}.id_livre')),
                Column('id_sujet', Integer, ForeignKey(f'{self.schema_name}.{self.table_names["sujet"]}.id_sujet')),
                Column('pertinence', Float, default=1.0),
                schema=self.schema_name
            )
            
            # Table EXTRACTION_LOG
            self.extraction_log_table = Table(
                self.table_names['extraction_log'], self.metadata,
                Column('id_log', Integer, primary_key=True),
                Column('fichier_source', String(500)),
                Column('date_extraction', DateTime, default=datetime.utcnow),
                Column('nb_livres_extraits', Integer),
                Column('nb_erreurs', Integer),
                Column('statistiques_json', Text),
                schema=self.schema_name
            )
            
            # Créer toutes les tables
            self.metadata.create_all(self.engine)
            
            print("✅ Tables créées avec succès:")
            for nom_logique, nom_table in self.table_names.items():
                print(f"   • {self.schema_name}.{nom_table}")
            
            self.tables_creees = True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables: {e}")
    
    def nettoyer_texte(self, texte: str) -> str:
        """Nettoie le texte des caractères problématiques"""
        if pd.isna(texte) or not texte:
            return ""
        
        # Supprimer les caractères de contrôle
        texte = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', str(texte))
        
        # Remplacer les retours à la ligne par des espaces
        texte = re.sub(r'\s+', ' ', texte)
        
        # Limiter la longueur
        if len(texte) > 1000:
            texte = texte[:997] + "..."
        
        return texte.strip()
    
    def extraire_annee(self, date_str: str) -> Optional[int]:
        """Extrait l'année d'une chaîne de date"""
        if pd.isna(date_str) or not date_str:
            return None
        
        # Chercher une année à 4 chiffres
        match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
        if match:
            annee = int(match.group())
            if 1000 <= annee <= 2030:
                return annee
        
        return None
    
    def parser_auteurs(self, auteurs_str: str) -> List[str]:
        """Parse la chaîne d'auteurs et retourne une liste d'IDs OpenLibrary"""
        if pd.isna(auteurs_str) or not auteurs_str:
            return []
        
        # Les auteurs sont stockés comme "/authors/OL123A | /authors/OL456A"
        auteurs = str(auteurs_str).split(' | ')
        ol_ids = []
        
        for auteur in auteurs:
            # Extraire l'ID OpenLibrary
            match = re.search(r'/authors/(OL\w+)', auteur)
            if match:
                ol_ids.append(match.group(1))
        
        return ol_ids[:10]  # Limiter à 10 auteurs
    
    def parser_editeurs(self, editeurs_str: str) -> List[str]:
        """Parse la chaîne d'éditeurs"""
        if pd.isna(editeurs_str) or not editeurs_str:
            return []
        
        # Les éditeurs sont séparés par " | "
        editeurs = str(editeurs_str).split(' | ')
        editeurs_nettoyes = []
        
        for editeur in editeurs:
            editeur = editeur.strip()
            if editeur and len(editeur) < 300:  # Limiter la longueur pour PostgreSQL
                editeurs_nettoyes.append(editeur)
        
        return editeurs_nettoyes[:5]  # Limiter à 5 éditeurs
    
    def parser_langues(self, langues_str: str) -> List[str]:
        """Parse la chaîne de langues"""
        if pd.isna(langues_str) or not langues_str:
            return []
        
        # Les langues sont séparées par " | "
        langues = str(langues_str).split(' | ')
        langues_nettoyees = []
        
        for langue in langues:
            langue = langue.strip()
            # Garder seulement les codes de 2-3 caractères
            if langue and 2 <= len(langue) <= 3 and langue.isalpha():
                langues_nettoyees.append(langue.lower())
        
        return langues_nettoyees[:5]  # Limiter à 5 langues
    
    def parser_sujets(self, sujets_str: str) -> List[str]:
        """Parse la chaîne de sujets"""
        if pd.isna(sujets_str) or not sujets_str:
            return []
        
        # Les sujets sont séparés par " | " ou " . " ou " ; "
        sujets = re.split(r'\s*[|.;]\s*', str(sujets_str))
        sujets_nettoyes = []
        
        for sujet in sujets:
            sujet = sujet.strip()
            if sujet and 3 <= len(sujet) <= 200:  # Longueur raisonnable pour PostgreSQL
                sujets_nettoyes.append(sujet)
        
        return sujets_nettoyes[:10]  # Limiter à 10 sujets
    
    def inserer_ou_recuperer_auteur(self, session, ol_id: str) -> Optional[int]:
        """Insère ou récupère un auteur par son ID OpenLibrary"""
        try:
            # Vérifier si l'auteur existe déjà
            result = session.execute(
                text(f'SELECT id_auteur FROM "{self.schema_name}"."{self.table_names["auteur"]}" WHERE ol_id = :ol_id'),
                {"ol_id": ol_id}
            )
            row = result.fetchone()
            
            if row:
                return row[0]
            
            # Insérer un nouvel auteur
            result = session.execute(
                text(f'''INSERT INTO "{self.schema_name}"."{self.table_names["auteur"]}" 
                        (ol_id, nom_complet) VALUES (:ol_id, :nom_complet) RETURNING id_auteur'''),
                {"ol_id": ol_id, "nom_complet": f"Auteur {ol_id}"}
            )
            return result.fetchone()[0]
            
        except Exception as e:
            print(f"⚠️ Erreur insertion auteur {ol_id}: {e}")
            return None
    
    def inserer_ou_recuperer_editeur(self, session, nom_editeur: str) -> Optional[int]:
        """Insère ou récupère un éditeur par son nom"""
        try:
            # Vérifier si l'éditeur existe déjà
            result = session.execute(
                text(f'SELECT id_editeur FROM "{self.schema_name}"."{self.table_names["editeur"]}" WHERE nom_editeur = :nom_editeur'),
                {"nom_editeur": nom_editeur}
            )
            row = result.fetchone()
            
            if row:
                return row[0]
            
            # Insérer un nouvel éditeur
            result = session.execute(
                text(f'''INSERT INTO "{self.schema_name}"."{self.table_names["editeur"]}" 
                        (nom_editeur) VALUES (:nom_editeur) RETURNING id_editeur'''),
                {"nom_editeur": nom_editeur}
            )
            return result.fetchone()[0]
            
        except Exception as e:
            print(f"⚠️ Erreur insertion éditeur {nom_editeur}: {e}")
            return None
    
    def inserer_ou_recuperer_langue(self, session, code_langue: str) -> Optional[int]:
        """Insère ou récupère une langue par son code"""
        try:
            # Mapping des codes vers les noms
            noms_langues = {
                'eng': 'English',
                'fre': 'Français',
                'spa': 'Español',
                'ger': 'Deutsch',
                'ita': 'Italiano',
                'por': 'Português',
                'rus': 'Русский',
                'jpn': '日本語',
                'chi': '中文',
                'ara': 'العربية'
            }
            
            # Vérifier si la langue existe déjà
            result = session.execute(
                text(f'SELECT id_langue FROM "{self.schema_name}"."{self.table_names["langue"]}" WHERE code_langue = :code_langue'),
                {"code_langue": code_langue}
            )
            row = result.fetchone()
            
            if row:
                return row[0]
            
            # Insérer une nouvelle langue
            nom_langue = noms_langues.get(code_langue, code_langue.upper())
            result = session.execute(
                text(f'''INSERT INTO "{self.schema_name}"."{self.table_names["langue"]}" 
                        (code_langue, nom_langue) VALUES (:code_langue, :nom_langue) RETURNING id_langue'''),
                {"code_langue": code_langue, "nom_langue": nom_langue}
            )
            return result.fetchone()[0]
            
        except Exception as e:
            print(f"⚠️ Erreur insertion langue {code_langue}: {e}")
            return None
    
    def inserer_ou_recuperer_sujet(self, session, nom_sujet: str) -> Optional[int]:
        """Insère ou récupère un sujet par son nom"""
        try:
            # Vérifier si le sujet existe déjà
            result = session.execute(
                text(f'SELECT id_sujet FROM "{self.schema_name}"."{self.table_names["sujet"]}" WHERE nom_sujet = :nom_sujet'),
                {"nom_sujet": nom_sujet}
            )
            row = result.fetchone()
            
            if row:
                return row[0]
            
            # Insérer un nouveau sujet
            result = session.execute(
                text(f'''INSERT INTO "{self.schema_name}"."{self.table_names["sujet"]}" 
                        (nom_sujet) VALUES (:nom_sujet) RETURNING id_sujet'''),
                {"nom_sujet": nom_sujet}
            )
            return result.fetchone()[0]
            
        except Exception as e:
            print(f"⚠️ Erreur insertion sujet {nom_sujet}: {e}")
            return None
    
    def formater_livre(self, session, livre_data: Dict) -> Optional[int]:
        """Formate et insère un livre dans la base de données"""
        try:
            # Données principales du livre
            ol_id = livre_data.get('id_livre', '').replace('/books/', '')
            titre = self.nettoyer_texte(livre_data.get('titre', ''))
            
            if not ol_id or not titre:
                return None
            
            # Vérifier si le livre existe déjà
            result = session.execute(
                text(f'SELECT id_livre FROM "{self.schema_name}"."{self.table_names["livre"]}" WHERE ol_id = :ol_id'),
                {"ol_id": ol_id}
            )
            if result.fetchone():
                return None  # Livre déjà existant
            
            # Préparer les données
            sous_titre = self.nettoyer_texte(livre_data.get('sous_titre', ''))
            isbn_10 = livre_data.get('isbn_10', '') if pd.notna(livre_data.get('isbn_10')) else None
            isbn_13 = livre_data.get('isbn_13', '') if pd.notna(livre_data.get('isbn_13')) else None
            date_publication = livre_data.get('date_publication', '') if pd.notna(livre_data.get('date_publication')) else None
            annee_publication = self.extraire_annee(livre_data.get('date_publication', ''))
            
            # Convertir nombre_pages en entier
            nombre_pages = None
            if pd.notna(livre_data.get('nombre_pages')):
                try:
                    nombre_pages = int(float(livre_data.get('nombre_pages')))
                    if nombre_pages <= 0 or nombre_pages > 10000:
                        nombre_pages = None
                except:
                    pass
            
            format_physique = livre_data.get('format_physique', '') if pd.notna(livre_data.get('format_physique')) else None
            description = livre_data.get('description', '') if pd.notna(livre_data.get('description')) else None
            
            # Insérer le livre principal
            result = session.execute(
                text(f'''INSERT INTO "{self.schema_name}"."{self.table_names["livre"]}" 
                        (ol_id, titre, sous_titre, isbn_10, isbn_13, 
                         date_publication, annee_publication, nombre_pages, 
                         format_physique, description) 
                        VALUES (:ol_id, :titre, :sous_titre, :isbn_10, :isbn_13,
                                :date_publication, :annee_publication, :nombre_pages,
                                :format_physique, :description) RETURNING id_livre'''),
                {
                    "ol_id": ol_id,
                    "titre": titre,
                    "sous_titre": sous_titre or None,
                    "isbn_10": isbn_10,
                    "isbn_13": isbn_13,
                    "date_publication": date_publication,
                    "annee_publication": annee_publication,
                    "nombre_pages": nombre_pages,
                    "format_physique": format_physique,
                    "description": description
                }
            )
            
            id_livre = result.fetchone()[0]
            
            # Insérer les relations
            
            # Auteurs
            auteurs_ol_ids = self.parser_auteurs(livre_data.get('auteurs', ''))
            for i, auteur_ol_id in enumerate(auteurs_ol_ids):
                id_auteur = self.inserer_ou_recuperer_auteur(session, auteur_ol_id)
                if id_auteur:
                    session.execute(
                        text(f'''INSERT INTO "{self.schema_name}"."{self.table_names["livre_auteur"]}" 
                                (id_livre, id_auteur, ordre) VALUES (:id_livre, :id_auteur, :ordre)
                                ON CONFLICT DO NOTHING'''),
                        {"id_livre": id_livre, "id_auteur": id_auteur, "ordre": i + 1}
                    )
            
            # Éditeurs
            editeurs = self.parser_editeurs(livre_data.get('editeurs', ''))
            for i, nom_editeur in enumerate(editeurs):
                id_editeur = self.inserer_ou_recuperer_editeur(session, nom_editeur)
                if id_editeur:
                    session.execute(
                        text(f'''INSERT INTO "{self.schema_name}"."{self.table_names["livre_editeur"]}" 
                                (id_livre, id_editeur, ordre) VALUES (:id_livre, :id_editeur, :ordre)
                                ON CONFLICT DO NOTHING'''),
                        {"id_livre": id_livre, "id_editeur": id_editeur, "ordre": i + 1}
                    )
            
            # Langues
            langues = self.parser_langues(livre_data.get('langues', ''))
            for i, code_langue in enumerate(langues):
                id_langue = self.inserer_ou_recuperer_langue(session, code_langue)
                if id_langue:
                    session.execute(
                        text(f'''INSERT INTO "{self.schema_name}"."{self.table_names["livre_langue"]}" 
                                (id_livre, id_langue, langue_principale) VALUES (:id_livre, :id_langue, :langue_principale)
                                ON CONFLICT DO NOTHING'''),
                        {"id_livre": id_livre, "id_langue": id_langue, "langue_principale": i == 0}
                    )
            
            # Sujets
            sujets = self.parser_sujets(livre_data.get('sujets', ''))
            for nom_sujet in sujets:
                id_sujet = self.inserer_ou_recuperer_sujet(session, nom_sujet)
                if id_sujet:
                    session.execute(
                        text(f'''INSERT INTO "{self.schema_name}"."{self.table_names["livre_sujet"]}" 
                                (id_livre, id_sujet) VALUES (:id_livre, :id_sujet)
                                ON CONFLICT DO NOTHING'''),
                        {"id_livre": id_livre, "id_sujet": id_sujet}
                    )
            
            return id_livre
            
        except Exception as e:
            print(f"❌ Erreur formatage livre {livre_data.get('id_livre', 'unknown')}: {e}")
            return None
    
    def traiter_fichier_csv(self, fichier_csv: str, batch_size: int = 1000):
        """Traite un fichier CSV et l'insère dans PostgreSQL"""
        print(f"📚 Traitement du fichier: {fichier_csv}")
        
        if not os.path.exists(fichier_csv):
            print(f"❌ Fichier non trouvé: {fichier_csv}")
            return
        
        try:
            session = self.Session()
            
            # Lire le CSV par chunks pour économiser la mémoire
            chunk_iter = pd.read_csv(fichier_csv, chunksize=batch_size)
            
            total_traites = 0
            total_inseres = 0
            total_erreurs = 0
            
            for chunk_num, chunk in enumerate(chunk_iter):
                print(f"📦 Traitement du lot {chunk_num + 1} ({len(chunk)} livres)...")
                
                for index, row in chunk.iterrows():
                    try:
                        id_livre = self.formater_livre(session, row.to_dict())
                        if id_livre:
                            total_inseres += 1
                        else:
                            total_erreurs += 1
                    except Exception as e:
                        total_erreurs += 1
                    
                    total_traites += 1
                    
                    # Afficher le progrès
                    if total_traites % 100 == 0:
                        print(f"   Traités: {total_traites} - Insérés: {total_inseres} - Erreurs: {total_erreurs}")
                
                # Commit régulier
                session.commit()
            
            # Log de l'extraction
            session.execute(
                text(f'''INSERT INTO "{self.schema_name}"."{self.table_names["extraction_log"]}" 
                        (fichier_source, nb_livres_extraits, nb_erreurs, statistiques_json) 
                        VALUES (:fichier_source, :nb_livres_extraits, :nb_erreurs, :statistiques_json)'''),
                {
                    "fichier_source": fichier_csv,
                    "nb_livres_extraits": total_inseres,
                    "nb_erreurs": total_erreurs,
                    "statistiques_json": json.dumps({
                        'total_traites': total_traites,
                        'total_inseres': total_inseres,
                        'total_erreurs': total_erreurs,
                        'taux_succes': (total_inseres / total_traites * 100) if total_traites > 0 else 0
                    })
                }
            )
            
            session.commit()
            session.close()
            
            print(f"\n✅ TRAITEMENT TERMINÉ!")
            print(f"   📊 Total traité: {total_traites}")
            print(f"   ✅ Livres insérés: {total_inseres}")
            print(f"   ❌ Erreurs: {total_erreurs}")
            print(f"   📈 Taux de succès: {(total_inseres/total_traites*100):.1f}%")
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")

def main():
    """Fonction principale"""
    print("🗄️ FORMATAGE POUR POSTGRESQL OPENLIBRARY")
    print("=" * 60)
    
    # Détecter les fichiers CSV nettoyés
    fichiers_csv = [f for f in os.listdir('.') if f.endswith('.csv') and os.path.getsize(f) > 1024*1024]  # > 1MB
    
    if not fichiers_csv:
        print("❌ Aucun fichier CSV trouvé")
        return
    
    print("📁 Fichiers CSV disponibles:")
    for i, fichier in enumerate(fichiers_csv, 1):
        taille = os.path.getsize(fichier) / (1024*1024)
        print(f"   {i}. {fichier} ({taille:.1f} MB)")
    
    # Sélection du fichier
    try:
        choix = int(input(f"\nChoisissez un fichier (1-{len(fichiers_csv)}): ")) - 1
        fichier_csv = fichiers_csv[choix]
    except (ValueError, IndexError):
        print("❌ Choix invalide")
        return
    
    # Configuration PostgreSQL
    print(f"\n🗄️ CONFIGURATION POSTGRESQL:")
    
    # URL de connexion
    database_url = input("URL de connexion [postgresql://postgres:postgres@localhost:5432/databook]: ").strip()
    if not database_url:
        database_url = "postgresql://postgres:postgres@localhost:5432/databook"
    
    # Nom du schéma
    print(f"\n📋 SCHÉMA POSTGRESQL:")
    print(f"   1. test (recommandé)")
    print(f"   2. openlibrary")
    print(f"   3. livres")
    print(f"   4. Personnalisé")
    
    choix_schema = input("Choisissez un schéma (1-4): ").strip()
    
    schemas = {'1': 'test', '2': 'openlibrary', '3': 'livres'}
    schema_name = schemas.get(choix_schema, 'test')
    
    if choix_schema == '4':
        schema_name = input("Entrez le nom du schéma: ").strip()
    
    print(f"\n📋 RÉCAPITULATIF:")
    print(f"   📁 Fichier CSV: {fichier_csv}")
    print(f"   🗄️ Base PostgreSQL: {database_url.split('/')[-1]}")
    print(f"   📋 Schéma: {schema_name}")
    print(f"   📝 Tables créées: {schema_name}.livre, {schema_name}.auteur, etc.")
    
    confirmation = input("\n🚀 Démarrer le formatage ? (o/N): ").strip().lower()
    if confirmation not in ['o', 'oui', 'y', 'yes']:
        print("❌ Formatage annulé")
        return
    
    # Traitement
    formateur = FormateurPostgreSQL(database_url, schema_name)
    
    if formateur.connecter_bdd():
        # Créer le schéma
        formateur.creer_schema()
        
        # Afficher les tables existantes
        formateur.lister_tables_existantes()
        
        # Créer les nouvelles tables
        formateur.creer_tables()
        
        if formateur.tables_creees:
            formateur.traiter_fichier_csv(fichier_csv)
        
        print(f"\n🎉 FORMATAGE TERMINÉ!")
        print(f"   🗄️ Base PostgreSQL: {database_url}")
        print(f"   📋 Schéma: {schema_name}")
        print(f"   💡 Connectez-vous avec pgAdmin ou psql pour explorer!")

if __name__ == "__main__":
    main() 