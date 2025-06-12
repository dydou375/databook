#!/usr/bin/env python3
"""
Extracteur de livres OpenLibrary - Script autonome
==================================================

Ce script extrait les informations des livres depuis les fichiers de données OpenLibrary
et fournit des fonctions de test pour valider le bon fonctionnement.

Basé sur l'analyse du notebook analyse_csv_auteurs.ipynb
"""

import json
import gzip
import os
import pandas as pd
import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Union


class ExtracteurLivres:
    """Classe principale pour extraire les informations des livres depuis OpenLibrary"""
    
    def __init__(self, base_path: str):
        """
        Initialise l'extracteur avec le chemin de base des fichiers OpenLibrary
        
        Args:
            base_path: Chemin vers le dossier contenant les fichiers OpenLibrary
        """
        self.base_path = base_path
        self.fichier_editions = None
        self.fichier_works = None
        self.fichier_auteurs = None
        self._detecter_fichiers()
    
    def _detecter_fichiers(self):
        """Détecte automatiquement les fichiers disponibles dans le répertoire"""
        print("🔍 Détection des fichiers disponibles...")
        
        if not os.path.exists(self.base_path):
            print(f"❌ Le répertoire {self.base_path} n'existe pas")
            return
        
        for filename in os.listdir(self.base_path):
            file_path = os.path.join(self.base_path, filename)
            
            if 'edition' in filename.lower():
                self.fichier_editions = file_path
                print(f"✅ Fichier éditions détecté: {filename}")
            elif 'work' in filename.lower():
                self.fichier_works = file_path
                print(f"✅ Fichier works détecté: {filename}")
            elif 'author' in filename.lower():
                self.fichier_auteurs = file_path
                print(f"✅ Fichier auteurs détecté: {filename}")
    
    def analyser_taille_fichier(self, fichier_path: str) -> Dict:
        """
        Analyse la taille et structure d'un fichier OpenLibrary
        
        Args:
            fichier_path: Chemin vers le fichier à analyser
            
        Returns:
            Dictionnaire avec les informations du fichier
        """
        if not os.path.exists(fichier_path):
            return {'erreur': 'Fichier non trouvé'}
        
        taille_octets = os.path.getsize(fichier_path)
        taille_mb = taille_octets / (1024 * 1024)
        taille_gb = taille_octets / (1024 * 1024 * 1024)
        
        info = {
            'fichier': os.path.basename(fichier_path),
            'taille_octets': taille_octets,
            'taille_mb': round(taille_mb, 2),
            'taille_gb': round(taille_gb, 2),
            'est_compresse': fichier_path.endswith('.gz')
        }
        
        # Si c'est un fichier gzip, essayer de lire la taille décompressée
        if info['est_compresse']:
            try:
                import struct
                with open(fichier_path, 'rb') as f:
                    f.seek(-4, 2)
                    taille_decompresse = struct.unpack('<I', f.read(4))[0]
                    info['taille_decompresse_gb'] = round(taille_decompresse / (1024**3), 2)
            except:
                info['taille_decompresse_gb'] = 'Inconnue'
        
        print(f"📁 {info['fichier']}")
        print(f"   Taille: {info['taille_mb']} MB ({info['taille_gb']} GB)")
        if 'taille_decompresse_gb' in info:
            print(f"   Décompressé: {info['taille_decompresse_gb']} GB")
        
        return info
    
    def extraire_editions_echantillon(self, max_livres: int = 1000, 
                                    criteres: Optional[Dict] = None) -> List[Dict]:
        """
        Extrait un échantillon d'éditions selon des critères spécifiques
        
        Args:
            max_livres: Nombre maximum de livres à extraire
            criteres: Dictionnaire de critères de filtrage
            
        Returns:
            Liste de dictionnaires contenant les informations des livres
        """
        if not self.fichier_editions:
            print("❌ Aucun fichier d'éditions disponible")
            return []
        
        print(f"📚 Extraction de {max_livres:,} éditions depuis {os.path.basename(self.fichier_editions)}")
        
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
        total_traites = 0
        editions_trouvees = 0
        
        try:
            # Ouvrir le fichier (gzip ou normal)
            open_func = gzip.open if self.fichier_editions.endswith('.gz') else open
            mode = 'rt' if self.fichier_editions.endswith('.gz') else 'r'
            
            with open_func(self.fichier_editions, mode, encoding='utf-8') as f:
                for i, ligne in enumerate(f):
                    if len(livres_extraits) >= max_livres:
                        break
                    
                    parties = ligne.strip().split('\t')
                    if len(parties) >= 5 and parties[0] == '/type/edition':
                        editions_trouvees += 1
                        
                        try:
                            donnees_json = json.loads(parties[4])
                            livre = self._extraire_infos_livre(parties, donnees_json)
                            
                            # Appliquer les critères de filtrage
                            if self._respecte_criteres(livre, criteres):
                                livres_extraits.append(livre)
                        
                        except (json.JSONDecodeError, Exception):
                            continue
                    
                    total_traites += 1
                    
                    # Afficher le progrès
                    if total_traites % 10000 == 0:
                        print(f"   Traité: {total_traites:,} - Éditions: {editions_trouvees:,} - Extraits: {len(livres_extraits):,}")
        
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction: {e}")
            return []
        
        print(f"✅ Extraction terminée: {len(livres_extraits):,} livres extraits")
        return livres_extraits
    
    def _extraire_infos_livre(self, parties: List[str], donnees_json: Dict) -> Dict:
        """
        Extrait les informations structurées d'un livre depuis les données JSON
        
        Args:
            parties: Parties de la ligne (type, id, revision, timestamp, json)
            donnees_json: Données JSON parsées du livre
            
        Returns:
            Dictionnaire avec les informations du livre
        """
        livre = {
            'type_entree': parties[0],
            'id_livre': parties[1],
            'revision': parties[2],
            'timestamp': parties[3],
            'titre': donnees_json.get('title', ''),
            'sous_titre': donnees_json.get('subtitle', ''),
            'isbn_10': '',
            'isbn_13': '',
            'editeurs': '',
            'date_publication': donnees_json.get('publish_date', ''),
            'annee_publication': None,
            'nombre_pages': donnees_json.get('number_of_pages', ''),
            'langues': '',
            'auteurs': '',
            'oeuvres': '',
            'format_physique': donnees_json.get('physical_format', ''),
            'nom_edition': donnees_json.get('edition_name', ''),
            'description': '',
            'sujets': '',
            'couvertures': '',
            'poids': donnees_json.get('weight', ''),
            'dimensions': donnees_json.get('dimensions', '')
        }
        
        # Extraire l'année de publication
        if livre['date_publication']:
            match_annee = re.search(r'\b(\d{4})\b', str(livre['date_publication']))
            if match_annee:
                annee = int(match_annee.group(1))
                if 1000 <= annee <= datetime.now().year:
                    livre['annee_publication'] = annee
        
        # Extraire ISBN
        if 'isbn_10' in donnees_json and donnees_json['isbn_10']:
            livre['isbn_10'] = self._extraire_premier_element(donnees_json['isbn_10'])
        
        if 'isbn_13' in donnees_json and donnees_json['isbn_13']:
            livre['isbn_13'] = self._extraire_premier_element(donnees_json['isbn_13'])
        
        # Extraire éditeurs
        if 'publishers' in donnees_json and donnees_json['publishers']:
            if isinstance(donnees_json['publishers'], list):
                livre['editeurs'] = ' | '.join(donnees_json['publishers'])
            else:
                livre['editeurs'] = str(donnees_json['publishers'])
        
        # Extraire langues
        if 'languages' in donnees_json and donnees_json['languages']:
            langues = []
            for lang in donnees_json['languages']:
                if isinstance(lang, dict) and 'key' in lang:
                    code_langue = lang['key'].replace('/languages/', '')
                    langues.append(code_langue)
                else:
                    langues.append(str(lang))
            livre['langues'] = ' | '.join(langues)
        
        # Extraire auteurs
        if 'authors' in donnees_json and donnees_json['authors']:
            auteurs = []
            for auteur in donnees_json['authors']:
                if isinstance(auteur, dict) and 'key' in auteur:
                    auteurs.append(auteur['key'])
                else:
                    auteurs.append(str(auteur))
            livre['auteurs'] = ' | '.join(auteurs)
        
        # Extraire œuvres liées
        if 'works' in donnees_json and donnees_json['works']:
            oeuvres = []
            for oeuvre in donnees_json['works']:
                if isinstance(oeuvre, dict) and 'key' in oeuvre:
                    oeuvres.append(oeuvre['key'])
                else:
                    oeuvres.append(str(oeuvre))
            livre['oeuvres'] = ' | '.join(oeuvres)
        
        # Extraire description
        if 'description' in donnees_json:
            desc = donnees_json['description']
            if isinstance(desc, dict) and 'value' in desc:
                livre['description'] = desc['value']
            elif isinstance(desc, str):
                livre['description'] = desc
        
        # Extraire sujets
        if 'subjects' in donnees_json and donnees_json['subjects']:
            if isinstance(donnees_json['subjects'], list):
                livre['sujets'] = ' | '.join(donnees_json['subjects'])
            else:
                livre['sujets'] = str(donnees_json['subjects'])
        
        # Extraire couvertures
        if 'covers' in donnees_json and donnees_json['covers']:
            if isinstance(donnees_json['covers'], list):
                livre['couvertures'] = ' | '.join([str(c) for c in donnees_json['covers']])
            else:
                livre['couvertures'] = str(donnees_json['covers'])
        
        return livre
    
    def _extraire_premier_element(self, element: Union[str, List]) -> str:
        """Extrait le premier élément d'une liste ou retourne la chaîne"""
        if isinstance(element, list) and element:
            return str(element[0])
        return str(element) if element else ''
    
    def _respecte_criteres(self, livre: Dict, criteres: Dict) -> bool:
        """
        Vérifie si un livre respecte les critères de filtrage
        
        Args:
            livre: Dictionnaire avec les informations du livre
            criteres: Critères de filtrage
            
        Returns:
            True si le livre respecte tous les critères
        """
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
        """
        Analyse les livres extraits et retourne un DataFrame avec des statistiques
        
        Args:
            livres: Liste des livres extraits
            
        Returns:
            DataFrame pandas avec les livres et des statistiques
        """
        if not livres:
            print("❌ Aucun livre à analyser")
            return pd.DataFrame()
        
        print(f"\n📊 ANALYSE DE {len(livres):,} LIVRES EXTRAITS")
        print("=" * 60)
        
        df = pd.DataFrame(livres)
        
        # Statistiques de base
        print(f"📏 Dimensions: {df.shape[0]:,} livres × {df.shape[1]} colonnes")
        
        # Taux de remplissage des métadonnées
        print(f"\n📋 QUALITÉ DES MÉTADONNÉES:")
        champs_importants = ['titre', 'annee_publication', 'isbn_13', 'isbn_10', 
                        'editeurs', 'langues', 'auteurs', 'nombre_pages', 'description']
        
        for champ in champs_importants:
            if champ in df.columns:
                non_vides = df[champ].notna() & (df[champ] != '')
                pourcentage = (non_vides.sum() / len(df)) * 100
                print(f"   • {champ:<20} : {non_vides.sum():>6,} ({pourcentage:>5.1f}%)")
        
        # Analyse des années de publication
        if 'annee_publication' in df.columns:
            annees = df['annee_publication'].dropna()
            if len(annees) > 0:
                print(f"\n📅 ANNÉES DE PUBLICATION:")
                print(f"   • Plage: {annees.min():.0f} - {annees.max():.0f}")
                print(f"   • Moyenne: {annees.mean():.0f}")
                print(f"   • Médiane: {annees.median():.0f}")
                
                # Répartition par décennie
                print(f"\n   Répartition par décennie:")
                for decennie in range(1900, 2030, 10):
                    compte = annees[(annees >= decennie) & (annees < decennie + 10)].count()
                    if compte > 0:
                        pourcentage = (compte / len(annees)) * 100
                        print(f"     - {decennie}s: {compte:,} livres ({pourcentage:.1f}%)")
        
        # Analyse des langues
        if 'langues' in df.columns:
            toutes_langues = []
            for langues in df['langues'].dropna():
                if langues:
                    toutes_langues.extend(langues.split(' | '))
            
            if toutes_langues:
                comptes_langues = pd.Series(toutes_langues).value_counts().head(10)
                print(f"\n🌍 TOP 10 LANGUES:")
                for langue, compte in comptes_langues.items():
                    pourcentage = (compte / len(toutes_langues)) * 100
                    print(f"   • {langue:<12}: {compte:,} ({pourcentage:.1f}%)")
        
        # Analyse des éditeurs
        if 'editeurs' in df.columns:
            tous_editeurs = []
            for editeurs in df['editeurs'].dropna():
                if editeurs:
                    tous_editeurs.extend(editeurs.split(' | '))
            
            if tous_editeurs:
                comptes_editeurs = pd.Series(tous_editeurs).value_counts().head(10)
                print(f"\n🏢 TOP 10 ÉDITEURS:")
                for editeur, compte in comptes_editeurs.items():
                    nom_court = editeur[:30] + "..." if len(editeur) > 30 else editeur
                    print(f"   • {nom_court:<33}: {compte:,}")
        
        # Analyse des pages
        if 'nombre_pages' in df.columns:
            pages_numeriques = pd.to_numeric(df['nombre_pages'], errors='coerce').dropna()
            if len(pages_numeriques) > 0:
                print(f"\n📄 STATISTIQUES DES PAGES:")
                print(f"   • Moyenne: {pages_numeriques.mean():.0f} pages")
                print(f"   • Médiane: {pages_numeriques.median():.0f} pages")
                print(f"   • Min - Max: {pages_numeriques.min():.0f} - {pages_numeriques.max():.0f} pages")
                
                # Répartition par tranches
                print(f"   • Répartition:")
                print(f"     - Moins de 100 pages: {(pages_numeriques < 100).sum():,}")
                print(f"     - 100-300 pages: {((pages_numeriques >= 100) & (pages_numeriques <= 300)).sum():,}")
                print(f"     - Plus de 300 pages: {(pages_numeriques > 300).sum():,}")
        
        # Exemples de livres avec métadonnées riches
        print(f"\n📚 EXEMPLES DE LIVRES AVEC MÉTADONNÉES COMPLÈTES:")
        print("-" * 60)
        
        # Calculer un score de qualité
        score_qualite = 0
        for champ in ['isbn_13', 'editeurs', 'auteurs', 'description', 'sujets']:
            if champ in df.columns:
                score_qualite += (df[champ].notna() & (df[champ] != '')).astype(int)
        
        df['score_qualite'] = score_qualite
        livres_qualite = df[df['score_qualite'] >= 3].head(5)
        
        for i, (_, livre) in enumerate(livres_qualite.iterrows(), 1):
            print(f"{i}. 📖 {livre['titre']}")
            if pd.notna(livre['sous_titre']) and livre['sous_titre']:
                print(f"   Sous-titre: {livre['sous_titre']}")
            if pd.notna(livre['annee_publication']):
                print(f"   Année: {livre['annee_publication']:.0f}")
            if pd.notna(livre['editeurs']) and livre['editeurs']:
                editeurs_courts = livre['editeurs'][:80] + "..." if len(livre['editeurs']) > 80 else livre['editeurs']
                print(f"   Éditeur: {editeurs_courts}")
            if pd.notna(livre['langues']) and livre['langues']:
                print(f"   Langues: {livre['langues']}")
            if pd.notna(livre['isbn_13']) and livre['isbn_13']:
                print(f"   ISBN-13: {livre['isbn_13']}")
            print()
        
        return df
    
    def sauvegarder_livres(self, df: pd.DataFrame, nom_fichier: str = "livres_openlibrary.csv"):
        """
        Sauvegarde le DataFrame des livres en CSV
        
        Args:
            df: DataFrame contenant les livres
            nom_fichier: Nom du fichier de sauvegarde
        """
        try:
            df.to_csv(nom_fichier, index=False, encoding='utf-8')
            print(f"💾 Livres sauvegardés dans: {nom_fichier}")
            print(f"   Nombre de livres: {len(df):,}")
            print(f"   Colonnes: {len(df.columns)}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")


def test_extracteur_basique():
    """Test de base de l'extracteur"""
    print("\n🧪 TEST BASIQUE DE L'EXTRACTEUR")
    print("=" * 50)
    
    # Chemin de base (à adapter selon votre configuration)
    base_path = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary"
    
    if not os.path.exists(base_path):
        print(f"❌ Chemin de test non trouvé: {base_path}")
        print("💡 Modifiez la variable 'base_path' dans test_extracteur_basique()")
        return False
    
    # Créer l'extracteur
    extracteur = ExtracteurLivres(base_path)
    
    # Vérifier qu'au moins un fichier est disponible
    if not extracteur.fichier_editions:
        print("❌ Aucun fichier d'éditions détecté")
        return False
    
    # Analyser la taille du fichier
    info_fichier = extracteur.analyser_taille_fichier(extracteur.fichier_editions)
    print(f"✅ Fichier analysé: {info_fichier}")
    
    # Extraire un petit échantillon
    print("\n📚 Extraction d'un échantillon de 100 livres...")
    livres = extracteur.extraire_editions_echantillon(max_livres=100)
    
    if not livres:
        print("❌ Aucun livre extrait")
        return False
    
    print(f"✅ {len(livres)} livres extraits avec succès")
    
    # Analyser les livres
    df = extracteur.analyser_livres_extraits(livres)
    
    if df.empty:
        print("❌ DataFrame vide")
        return False
    
    print(f"✅ DataFrame créé avec {len(df)} livres")
    return True


def test_extracteur_avance():
    """Test avancé avec critères de filtrage"""
    print("\n🧪 TEST AVANCÉ AVEC CRITÈRES")
    print("=" * 50)
    
    base_path = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary"
    
    if not os.path.exists(base_path):
        print(f"❌ Chemin de test non trouvé: {base_path}")
        return False
    
    extracteur = ExtracteurLivres(base_path)
    
    # Critères de filtrage avancés
    criteres = {
        'avec_titre': True,
        'avec_isbn': True,
        'avec_auteur': True,
        'annee_min': 2000,
        'annee_max': 2024,
        'langues': ['eng', 'fre', 'spa', 'ger']
    }
    
    print("🔍 Critères de filtrage:")
    for cle, valeur in criteres.items():
        print(f"   • {cle}: {valeur}")
    
    livres = extracteur.extraire_editions_echantillon(max_livres=500, criteres=criteres)
    
    if not livres:
        print("❌ Aucun livre correspondant aux critères")
        return False
    
    print(f"✅ {len(livres)} livres extraits selon les critères")
    
    # Analyser et sauvegarder
    df = extracteur.analyser_livres_extraits(livres)
    extracteur.sauvegarder_livres(df, "livres_filtres_test.csv")
    
    return True


def test_performance():
    """Test de performance sur un échantillon plus large"""
    print("\n🧪 TEST DE PERFORMANCE")
    print("=" * 50)
    
    base_path = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary"
    
    if not os.path.exists(base_path):
        print(f"❌ Chemin de test non trouvé: {base_path}")
        return False
    
    extracteur = ExtracteurLivres(base_path)
    
    # Test avec 5000 livres
    import time
    debut = time.time()
    
    livres = extracteur.extraire_editions_echantillon(max_livres=5000)
    
    fin = time.time()
    duree = fin - debut
    
    if livres:
        print(f"✅ Performance: {len(livres)} livres extraits en {duree:.2f} secondes")
        print(f"   Vitesse: {len(livres)/duree:.1f} livres/seconde")
        
        # Analyse rapide
        df = extracteur.analyser_livres_extraits(livres)
        extracteur.sauvegarder_livres(df, "livres_performance_test.csv")
        
        return True
    else:
        print("❌ Échec du test de performance")
        return False


def main():
    """Fonction principale pour exécuter les tests"""
    print("🚀 EXTRACTEUR DE LIVRES OPENLIBRARY")
    print("=" * 60)
    print("Ce script extrait les informations des livres depuis les fichiers OpenLibrary")
    print("Basé sur l'analyse du notebook analyse_csv_auteurs.ipynb")
    print()
    
    # Exécuter les tests
    tests = [
        ("Test basique", test_extracteur_basique),
        ("Test avancé", test_extracteur_avance),
        ("Test performance", test_performance)
    ]
    
    resultats = {}
    
    for nom_test, fonction_test in tests:
        print(f"\n{'='*20} {nom_test.upper()} {'='*20}")
        try:
            resultats[nom_test] = fonction_test()
        except Exception as e:
            print(f"❌ Erreur dans {nom_test}: {e}")
            resultats[nom_test] = False
    
    # Résumé des tests
    print(f"\n{'='*20} RÉSUMÉ DES TESTS {'='*20}")
    for nom_test, succes in resultats.items():
        statut = "✅ RÉUSSI" if succes else "❌ ÉCHEC"
        print(f"{nom_test:<20}: {statut}")
    
    # Instruction d'utilisation
    if any(resultats.values()):
        print(f"\n💡 UTILISATION PERSONNALISÉE:")
        print(f"   # Créer un extracteur")
        print(f"   extracteur = ExtracteurLivres('chemin/vers/dossier/openlibrary')")
        print(f"   ")
        print(f"   # Extraire des livres avec critères")
        print(f"   criteres = {{'avec_isbn': True, 'annee_min': 2000}}")
        print(f"   livres = extracteur.extraire_editions_echantillon(max_livres=1000, criteres=criteres)")
        print(f"   ")
        print(f"   # Analyser et sauvegarder")
        print(f"   df = extracteur.analyser_livres_extraits(livres)")
        print(f"   extracteur.sauvegarder_livres(df, 'mes_livres.csv')")


if __name__ == "__main__":
    main()