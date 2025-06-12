#!/usr/bin/env python3
"""
Test et extraction du fichier OpenLibrary complet
==================================================

Ce script utilise directement le fichier ol_cdump_2025-05-31.txt.gz 
qui contient TOUS les types de données OpenLibrary mélangés :
- /type/author (auteurs)
- /type/edition (éditions)
- /type/work (œuvres)
"""

import json
import gzip
import os
import pandas as pd
import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional


class ExtracteurFichierComplet:
    """Extracteur spécialisé pour le fichier OpenLibrary complet"""
    
    def __init__(self, fichier_path: str):
        """
        Initialise l'extracteur avec le chemin du fichier complet
        
        Args:
            fichier_path: Chemin vers le fichier ol_cdump_2025-05-31.txt.gz
        """
        self.fichier_path = fichier_path
        self.stats_types = defaultdict(int)
        
    def analyser_structure_fichier(self, nb_lignes_test: int = 10000):
        """
        Analyse la structure du fichier pour comprendre son contenu
        
        Args:
            nb_lignes_test: Nombre de lignes à analyser pour les statistiques
        """
        print(f"🔍 ANALYSE DE LA STRUCTURE DU FICHIER")
        print(f"Fichier: {os.path.basename(self.fichier_path)}")
        print(f"Échantillon: {nb_lignes_test:,} lignes")
        print("=" * 60)
        
        # Réinitialiser les stats
        self.stats_types = defaultdict(int)
        exemples_par_type = {}
        
        try:
            with gzip.open(self.fichier_path, 'rt', encoding='utf-8') as f:
                for i, ligne in enumerate(f):
                    if i >= nb_lignes_test:
                        break
                    
                    parties = ligne.strip().split('\t')
                    if len(parties) >= 5:
                        type_entree = parties[0]
                        self.stats_types[type_entree] += 1
                        
                        # Garder un exemple pour chaque type (seulement le premier)
                        if type_entree not in exemples_par_type:
                            try:
                                donnees_json = json.loads(parties[4])
                                exemples_par_type[type_entree] = {
                                    'id': parties[1],
                                    'exemple_donnees': donnees_json
                                }
                            except:
                                pass
                    
                    # Progrès
                    if (i + 1) % 2000 == 0:
                        print(f"   Analysé {i+1:,} lignes...")
        
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse: {e}")
            return
        
        # Afficher les résultats
        print(f"\n📊 RÉPARTITION DES TYPES DE DONNÉES:")
        print("-" * 50)
        
        total_lignes = sum(self.stats_types.values())
        for type_entree, compte in sorted(self.stats_types.items()):
            pourcentage = (compte / total_lignes) * 100
            print(f"   • {type_entree:<20} : {compte:>8,} ({pourcentage:>5.1f}%)")
        
        print(f"\n📝 EXEMPLES PAR TYPE:")
        print("-" * 50)
        
        for type_entree, info in exemples_par_type.items():
            print(f"\n🔹 {type_entree}")
            print(f"   ID: {info['id']}")
            
            # Afficher quelques champs importants selon le type
            donnees = info['exemple_donnees']
            
            if type_entree == '/type/author':
                print(f"   Nom: {donnees.get('name', 'N/A')}")
                if 'birth_date' in donnees:
                    print(f"   Naissance: {donnees['birth_date']}")
                if 'bio' in donnees:
                    bio = donnees['bio']
                    bio_text = bio['value'] if isinstance(bio, dict) else str(bio)
                    print(f"   Bio: {bio_text[:100]}...")
            
            elif type_entree == '/type/edition':
                print(f"   Titre: {donnees.get('title', 'N/A')}")
                if 'publish_date' in donnees:
                    print(f"   Date pub: {donnees['publish_date']}")
                if 'publishers' in donnees:
                    print(f"   Éditeur: {donnees['publishers']}")
                if 'isbn_13' in donnees:
                    print(f"   ISBN-13: {donnees['isbn_13']}")
            
            elif type_entree == '/type/work':
                print(f"   Titre: {donnees.get('title', 'N/A')}")
                if 'authors' in donnees:
                    print(f"   Auteurs: {donnees['authors']}")
                if 'subjects' in donnees:
                    sujets = donnees['subjects'][:3] if isinstance(donnees['subjects'], list) else donnees['subjects']
                    print(f"   Sujets: {sujets}")
        
        print(f"\n💡 PROJECTION SUR LE FICHIER COMPLET:")
        print("-" * 50)
        
        # Estimer pour tout le fichier (basé sur les 43GB)
        taille_fichier = os.path.getsize(self.fichier_path)
        print(f"   Taille fichier: {taille_fichier / (1024**3):.1f} GB")
        
        if total_lignes > 0:
            # Estimation grossière du nombre total de lignes
            estimation_totale = (total_lignes / nb_lignes_test) * 1000000  # Estimation très approximative
            print(f"   Estimation nombre total de lignes: ~{estimation_totale:,.0f}")
            
            for type_entree, compte in sorted(self.stats_types.items()):
                pourcentage = (compte / total_lignes) * 100
                estimation_type = estimation_totale * (pourcentage / 100)
                print(f"   • {type_entree:<20} : ~{estimation_type:>10,.0f} entrées")
    
    def extraire_livres_complet(self, max_livres: int = 1000, 
                              criteres: Optional[Dict] = None,
                              inclure_works: bool = False) -> List[Dict]:
        """
        Extrait les livres du fichier complet (éditions et optionnellement œuvres)
        
        Args:
            max_livres: Nombre maximum de livres à extraire
            criteres: Critères de filtrage
            inclure_works: Si True, inclut aussi les œuvres (/type/work)
            
        Returns:
            Liste des livres extraits
        """
        print(f"📚 EXTRACTION DE LIVRES DU FICHIER COMPLET")
        print(f"   Limite: {max_livres:,} livres")
        print(f"   Inclure works: {inclure_works}")
        print("=" * 50)
        
        # Critères par défaut
        if criteres is None:
            criteres = {
                'avec_titre': True,
                'avec_isbn': False,
                'avec_auteur': False,
                'annee_min': None,
                'annee_max': None,
                'langues': None
            }
        
        livres_extraits = []
        stats_traitement = {
            'total_lignes': 0,
            'editions_trouvees': 0,
            'works_trouvees': 0,
            'livres_extraits': 0
        }
        
        try:
            with gzip.open(self.fichier_path, 'rt', encoding='utf-8') as f:
                for i, ligne in enumerate(f):
                    if len(livres_extraits) >= max_livres:
                        break
                    
                    parties = ligne.strip().split('\t')
                    if len(parties) >= 5:
                        type_entree = parties[0]
                        
                        # Traiter les éditions
                        if type_entree == '/type/edition':
                            stats_traitement['editions_trouvees'] += 1
                            
                            try:
                                donnees_json = json.loads(parties[4])
                                livre = self._extraire_infos_edition(parties, donnees_json)
                                
                                if self._respecte_criteres(livre, criteres):
                                    livres_extraits.append(livre)
                                    stats_traitement['livres_extraits'] += 1
                            
                            except (json.JSONDecodeError, Exception):
                                continue
                        
                        # Traiter les œuvres si demandé
                        elif inclure_works and type_entree == '/type/work':
                            stats_traitement['works_trouvees'] += 1
                            
                            try:
                                donnees_json = json.loads(parties[4])
                                livre = self._extraire_infos_work(parties, donnees_json)
                                
                                if self._respecte_criteres(livre, criteres):
                                    livres_extraits.append(livre)
                                    stats_traitement['livres_extraits'] += 1
                            
                            except (json.JSONDecodeError, Exception):
                                continue
                    
                    stats_traitement['total_lignes'] += 1
                    
                    # Afficher le progrès
                    if stats_traitement['total_lignes'] % 50000 == 0:
                        print(f"   Ligne {stats_traitement['total_lignes']:,} - "
                              f"Éditions: {stats_traitement['editions_trouvees']:,} - "
                              f"Works: {stats_traitement['works_trouvees']:,} - "
                              f"Extraits: {stats_traitement['livres_extraits']:,}")
        
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction: {e}")
            return []
        
        print(f"\n✅ EXTRACTION TERMINÉE:")
        for cle, valeur in stats_traitement.items():
            print(f"   • {cle}: {valeur:,}")
        
        return livres_extraits
    
    def _extraire_infos_edition(self, parties: List[str], donnees_json: Dict) -> Dict:
        """Extrait les infos d'une édition"""
        livre = {
            'type_source': 'edition',
            'type_entree': parties[0],
            'id_livre': parties[1],
            'revision': parties[2],
            'timestamp': parties[3],
            'titre': donnees_json.get('title', ''),
            'sous_titre': donnees_json.get('subtitle', ''),
            'isbn_10': self._extraire_premier_element(donnees_json.get('isbn_10', '')),
            'isbn_13': self._extraire_premier_element(donnees_json.get('isbn_13', '')),
            'editeurs': self._extraire_liste_ou_chaine(donnees_json.get('publishers', '')),
            'date_publication': donnees_json.get('publish_date', ''),
            'annee_publication': None,
            'nombre_pages': donnees_json.get('number_of_pages', ''),
            'langues': self._extraire_langues(donnees_json.get('languages', '')),
            'auteurs': self._extraire_cles(donnees_json.get('authors', '')),
            'oeuvres': self._extraire_cles(donnees_json.get('works', '')),
            'format_physique': donnees_json.get('physical_format', ''),
            'description': self._extraire_description(donnees_json.get('description', '')),
            'sujets': self._extraire_liste_ou_chaine(donnees_json.get('subjects', '')),
        }
        
        # Extraire l'année de publication
        if livre['date_publication']:
            match_annee = re.search(r'\b(\d{4})\b', str(livre['date_publication']))
            if match_annee:
                annee = int(match_annee.group(1))
                if 1000 <= annee <= datetime.now().year:
                    livre['annee_publication'] = annee
        
        return livre
    
    def _extraire_infos_work(self, parties: List[str], donnees_json: Dict) -> Dict:
        """Extrait les infos d'une œuvre"""
        livre = {
            'type_source': 'work',
            'type_entree': parties[0],
            'id_livre': parties[1],
            'revision': parties[2],
            'timestamp': parties[3],
            'titre': donnees_json.get('title', ''),
            'sous_titre': '',  # Les works n'ont généralement pas de sous-titre
            'isbn_10': '',     # Les works n'ont pas d'ISBN
            'isbn_13': '',
            'editeurs': '',    # Les works n'ont pas d'éditeurs directs
            'date_publication': '',
            'annee_publication': None,
            'nombre_pages': '',
            'langues': '',
            'auteurs': self._extraire_cles(donnees_json.get('authors', '')),
            'oeuvres': parties[1],  # L'ID de l'œuvre elle-même
            'format_physique': '',
            'description': self._extraire_description(donnees_json.get('description', '')),
            'sujets': self._extraire_liste_ou_chaine(donnees_json.get('subjects', '')),
        }
        
        # Essayer d'extraire une année depuis first_publish_date
        if 'first_publish_date' in donnees_json:
            match_annee = re.search(r'\b(\d{4})\b', str(donnees_json['first_publish_date']))
            if match_annee:
                annee = int(match_annee.group(1))
                if 1000 <= annee <= datetime.now().year:
                    livre['annee_publication'] = annee
        
        return livre
    
    def _extraire_premier_element(self, element):
        """Extrait le premier élément d'une liste ou retourne la chaîne"""
        if isinstance(element, list) and element:
            return str(element[0])
        return str(element) if element else ''
    
    def _extraire_liste_ou_chaine(self, element):
        """Extrait une liste en joignant par | ou retourne la chaîne"""
        if isinstance(element, list):
            return ' | '.join([str(x) for x in element])
        return str(element) if element else ''
    
    def _extraire_langues(self, languages):
        """Extrait les codes de langue"""
        if not languages:
            return ''
        
        codes_langues = []
        if isinstance(languages, list):
            for lang in languages:
                if isinstance(lang, dict) and 'key' in lang:
                    code = lang['key'].replace('/languages/', '')
                    codes_langues.append(code)
                else:
                    codes_langues.append(str(lang))
        
        return ' | '.join(codes_langues)
    
    def _extraire_cles(self, elements):
        """Extrait les clés d'une liste d'objets avec key"""
        if not elements:
            return ''
        
        cles = []
        if isinstance(elements, list):
            for element in elements:
                if isinstance(element, dict) and 'key' in element:
                    cles.append(element['key'])
                else:
                    cles.append(str(element))
        
        return ' | '.join(cles)
    
    def _extraire_description(self, description):
        """Extrait la description (peut être une chaîne ou un objet avec 'value')"""
        if isinstance(description, dict) and 'value' in description:
            return description['value']
        return str(description) if description else ''
    
    def _respecte_criteres(self, livre: Dict, criteres: Dict) -> bool:
        """Vérifie si un livre respecte les critères"""
        # Titre requis
        if criteres.get('avec_titre', True) and not livre['titre']:
            return False
        
        # ISBN requis
        if criteres.get('avec_isbn', False) and not (livre['isbn_10'] or livre['isbn_13']):
            return False
        
        # Auteur requis
        if criteres.get('avec_auteur', False) and not livre['auteurs']:
            return False
        
        # Filtrage par année
        if livre['annee_publication']:
            if criteres.get('annee_min') and livre['annee_publication'] < criteres['annee_min']:
                return False
            if criteres.get('annee_max') and livre['annee_publication'] > criteres['annee_max']:
                return False
        
        # Filtrage par langue
        if criteres.get('langues') and livre['langues']:
            langues_livre = livre['langues'].split(' | ')
            langues_acceptees = criteres['langues']
            if not any(lang in langues_acceptees for lang in langues_livre):
                return False
        
        return True
    
    def analyser_livres_extraits(self, livres: List[Dict]) -> pd.DataFrame:
        """Analyse les livres extraits et retourne un DataFrame"""
        if not livres:
            print("❌ Aucun livre à analyser")
            return pd.DataFrame()
        
        print(f"\n📊 ANALYSE DE {len(livres):,} LIVRES EXTRAITS")
        print("=" * 60)
        
        df = pd.DataFrame(livres)
        
        # Statistiques par type de source
        if 'type_source' in df.columns:
            print(f"📋 RÉPARTITION PAR TYPE:")
            repartition = df['type_source'].value_counts()
            for type_source, compte in repartition.items():
                pourcentage = (compte / len(df)) * 100
                print(f"   • {type_source:<10} : {compte:>6,} ({pourcentage:>5.1f}%)")
        
        # Statistiques de base
        print(f"\n📏 Dimensions: {df.shape[0]:,} livres × {df.shape[1]} colonnes")
        
        # Taux de remplissage
        champs_importants = ['titre', 'annee_publication', 'isbn_13', 'auteurs', 'description', 'sujets']
        print(f"\n📋 QUALITÉ DES MÉTADONNÉES:")
        
        for champ in champs_importants:
            if champ in df.columns:
                non_vides = df[champ].notna() & (df[champ] != '')
                pourcentage = (non_vides.sum() / len(df)) * 100
                print(f"   • {champ:<20} : {non_vides.sum():>6,} ({pourcentage:>5.1f}%)")
        
        # Quelques exemples
        print(f"\n📚 EXEMPLES DE LIVRES EXTRAITS:")
        print("-" * 50)
        
        for i, (_, livre) in enumerate(df.head(3).iterrows(), 1):
            print(f"{i}. 📖 {livre['titre']} [{livre['type_source']}]")
            if livre.get('auteurs'):
                print(f"   Auteurs: {livre['auteurs'][:60]}...")
            if livre.get('annee_publication'):
                print(f"   Année: {livre['annee_publication']}")
            print()
        
        return df


def test_fichier_complet():
    """Test du fichier OpenLibrary complet"""
    print("🧪 TEST DU FICHIER OPENLIBRARY COMPLET")
    print("=" * 60)
    
    # Chemin vers votre fichier complet
    fichier_complet = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\non_extrait\ol_cdump_2025-05-31.txt.gz"
    
    if not os.path.exists(fichier_complet):
        print(f"❌ Fichier non trouvé: {fichier_complet}")
        return False
    
    # Créer l'extracteur
    extracteur = ExtracteurFichierComplet(fichier_complet)
    
    # 1. Analyser la structure
    print("\n1️⃣ ANALYSE DE LA STRUCTURE")
    extracteur.analyser_structure_fichier(nb_lignes_test=5000)
    
    # 2. Extraire quelques livres (éditions seulement)
    print(f"\n2️⃣ EXTRACTION D'ÉDITIONS")
    criteres_editions = {
        'avec_titre': True,
        'avec_isbn': False,
        'avec_auteur': False
    }
    
    livres_editions = extracteur.extraire_livres_complet(
        max_livres=200, 
        criteres=criteres_editions, 
        inclure_works=False
    )
    
    if livres_editions:
        df_editions = extracteur.analyser_livres_extraits(livres_editions)
        
        # Sauvegarder
        df_editions.to_csv("livres_editions_complet.csv", index=False, encoding='utf-8')
        print(f"💾 Éditions sauvegardées: livres_editions_complet.csv")
    
    # 3. Extraire avec œuvres incluses
    print(f"\n3️⃣ EXTRACTION AVEC ŒUVRES")
    livres_tout = extracteur.extraire_livres_complet(
        max_livres=100, 
        criteres=criteres_editions, 
        inclure_works=True
    )
    
    if livres_tout:
        df_tout = extracteur.analyser_livres_extraits(livres_tout)
        
        # Sauvegarder
        df_tout.to_csv("livres_tout_complet.csv", index=False, encoding='utf-8')
        print(f"💾 Tout sauvegardé: livres_tout_complet.csv")
    
    print(f"\n✅ TEST TERMINÉ!")
    return True


def main():
    """Fonction principale"""
    print("🚀 EXTRACTEUR FICHIER OPENLIBRARY COMPLET")
    print("=" * 60)
    print("Ce script utilise directement ol_cdump_2025-05-31.txt.gz")
    print("qui contient TOUS les types de données mélangés")
    print()
    
    # Lancer le test
    succes = test_fichier_complet()
    
    if succes:
        print(f"\n💡 UTILISATION PERSONNALISÉE:")
        print(f"extracteur = ExtracteurFichierComplet('chemin/vers/ol_cdump_2025-05-31.txt.gz')")
        print(f"livres = extracteur.extraire_livres_complet(max_livres=1000)")
        print(f"df = extracteur.analyser_livres_extraits(livres)")
    else:
        print(f"\n❌ Vérifiez le chemin vers le fichier ol_cdump_2025-05-31.txt.gz")


if __name__ == "__main__":
    main()