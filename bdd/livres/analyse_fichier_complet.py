#!/usr/bin/env python3
"""
Analyseur de fichier OpenLibrary complet
=======================================

Ce script analyse les gros fichiers OpenLibrary pour estimer
le nombre total de livres disponibles et planifier l'extraction.
"""

import gzip
import os
import json
import time
from collections import defaultdict
from typing import Dict, Tuple

def analyser_fichier_openlibrary(fichier_path: str, echantillon_lignes: int = 100000) -> Dict:
    """
    Analyse un fichier OpenLibrary pour obtenir des statistiques
    
    Args:
        fichier_path: Chemin vers le fichier à analyser
        echantillon_lignes: Nombre de lignes à analyser pour l'estimation
        
    Returns:
        Dictionnaire avec les statistiques du fichier
    """
    print(f"🔍 ANALYSE DU FICHIER OPENLIBRARY")
    print(f"📁 Fichier: {os.path.basename(fichier_path)}")
    
    if not os.path.exists(fichier_path):
        print(f"❌ Fichier non trouvé: {fichier_path}")
        return {}
    
    # Informations sur le fichier
    taille_octets = os.path.getsize(fichier_path)
    taille_gb = taille_octets / (1024**3)
    est_compresse = fichier_path.endswith('.gz')
    
    print(f"📊 Taille: {taille_gb:.2f} GB")
    print(f"🗜️ Compressé: {'Oui' if est_compresse else 'Non'}")
    
    stats = {
        'fichier': os.path.basename(fichier_path),
        'taille_gb': taille_gb,
        'est_compresse': est_compresse,
        'lignes_totales_estimees': 0,
        'editions_estimees': 0,
        'works_estimes': 0,
        'authors_estimes': 0,
        'types_entrees': defaultdict(int),
        'langues_populaires': defaultdict(int),
        'annees_range': {'min': 9999, 'max': 0},
        'qualite_donnees': {
            'avec_titre': 0,
            'avec_isbn': 0,
            'avec_auteur': 0,
            'avec_annee': 0
        }
    }
    
    try:
        # Ouvrir le fichier (gzip ou normal)
        open_func = gzip.open if est_compresse else open
        mode = 'rt' if est_compresse else 'r'
        
        print(f"\n📈 Analyse d'un échantillon de {echantillon_lignes:,} lignes...")
        debut = time.time()
        
        with open_func(fichier_path, mode, encoding='utf-8', errors='replace') as f:
            for i, ligne in enumerate(f):
                if i >= echantillon_lignes:
                    break
                
                try:
                    # Parser la ligne OpenLibrary (format: type TAB id TAB revision TAB timestamp TAB json)
                    parties = ligne.strip().split('\t')
                    
                    if len(parties) >= 5:
                        type_entree = parties[0]
                        donnees_json = json.loads(parties[4])
                        
                        # Compter les types
                        stats['types_entrees'][type_entree] += 1
                        
                        # Analyser spécifiquement les éditions
                        if type_entree == '/type/edition':
                            # Titre
                            if donnees_json.get('title'):
                                stats['qualite_donnees']['avec_titre'] += 1
                            
                            # ISBN
                            if donnees_json.get('isbn_10') or donnees_json.get('isbn_13'):
                                stats['qualite_donnees']['avec_isbn'] += 1
                            
                            # Auteurs
                            if donnees_json.get('authors'):
                                stats['qualite_donnees']['avec_auteur'] += 1
                            
                            # Année
                            if donnees_json.get('publish_date'):
                                stats['qualite_donnees']['avec_annee'] += 1
                                # Extraire l'année si possible
                                try:
                                    date_str = str(donnees_json['publish_date'])
                                    # Chercher une année à 4 chiffres
                                    import re
                                    annee_match = re.search(r'\b(19|20)\d{2}\b', date_str)
                                    if annee_match:
                                        annee = int(annee_match.group())
                                        stats['annees_range']['min'] = min(stats['annees_range']['min'], annee)
                                        stats['annees_range']['max'] = max(stats['annees_range']['max'], annee)
                                except:
                                    pass
                            
                            # Langues
                            if donnees_json.get('languages'):
                                langues = donnees_json['languages']
                                if isinstance(langues, list) and langues:
                                    # Extraire le code de langue depuis "/languages/eng"
                                    for langue in langues[:3]:  # Prendre les 3 premières
                                        if isinstance(langue, dict) and 'key' in langue:
                                            code_langue = langue['key'].split('/')[-1]
                                            stats['langues_populaires'][code_langue] += 1
                
                except (json.JSONDecodeError, IndexError, Exception):
                    continue
                
                # Afficher le progrès
                if (i + 1) % 10000 == 0:
                    print(f"   Analysé: {i+1:,} lignes...")
        
        duree = time.time() - debut
        
        # Calculer les estimations totales
        if i > 0:
            # Estimer le nombre total de lignes basé sur la taille du fichier
            taille_echantillon = i + 1
            vitesse_lignes_par_seconde = taille_echantillon / duree
            
            # Estimation basée sur la proportion
            total_editions = stats['types_entrees']['/type/edition']
            if total_editions > 0:
                proportion_editions = total_editions / taille_echantillon
                
                # Estimation grossière du nombre total de lignes
                # (basée sur la taille et la vitesse de lecture)
                if est_compresse:
                    # Les fichiers gzip ont généralement un ratio 10:1
                    lignes_estimees = int(taille_gb * 1000000)  # ~1M lignes par GB décompressé
                else:
                    lignes_estimees = int(taille_gb * 200000)   # ~200K lignes par GB
                
                stats['lignes_totales_estimees'] = lignes_estimees
                stats['editions_estimees'] = int(lignes_estimees * proportion_editions)
                stats['works_estimes'] = stats['types_entrees'].get('/type/work', 0) * (lignes_estimees // taille_echantillon)
                stats['authors_estimes'] = stats['types_entrees'].get('/type/author', 0) * (lignes_estimees // taille_echantillon)
        
        # Afficher les résultats
        print(f"\n📊 RÉSULTATS DE L'ANALYSE")
        print(f"⏱️ Temps d'analyse: {duree:.1f} secondes")
        print(f"🔢 Lignes analysées: {i+1:,}")
        print(f"📈 Vitesse: {vitesse_lignes_par_seconde:.0f} lignes/seconde")
        
        print(f"\n📋 ESTIMATIONS TOTALES:")
        print(f"   • Lignes totales: {stats['lignes_totales_estimees']:,}")
        print(f"   • Éditions: {stats['editions_estimees']:,}")
        print(f"   • Works: {stats['works_estimes']:,}")
        print(f"   • Auteurs: {stats['authors_estimes']:,}")
        
        print(f"\n📈 TYPES D'ENTRÉES (échantillon):")
        for type_entree, count in sorted(stats['types_entrees'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {type_entree}: {count:,}")
        
        print(f"\n📋 QUALITÉ DES DONNÉES (éditions uniquement):")
        total_editions = stats['types_entrees'].get('/type/edition', 1)
        for critere, count in stats['qualite_donnees'].items():
            pourcentage = (count / total_editions) * 100 if total_editions > 0 else 0
            print(f"   • {critere}: {count:,} ({pourcentage:.1f}%)")
        
        if stats['langues_populaires']:
            print(f"\n🌍 TOP 10 LANGUES:")
            langues_triees = sorted(stats['langues_populaires'].items(), key=lambda x: x[1], reverse=True)
            for i, (langue, count) in enumerate(langues_triees[:10]):
                print(f"   {i+1:2d}. {langue}: {count:,}")
        
        if stats['annees_range']['max'] > 0:
            print(f"\n📅 PLAGE D'ANNÉES: {stats['annees_range']['min']} - {stats['annees_range']['max']}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return stats

def main():
    """Fonction principale"""
    print("🔍 ANALYSEUR DE FICHIER OPENLIBRARY COMPLET")
    print("=" * 60)
    
    # Détecter les gros fichiers disponibles
    base_path = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary"
    
    gros_fichiers = []
    
    # Chercher dans le répertoire principal
    if os.path.exists(base_path):
        for filename in os.listdir(base_path):
            filepath = os.path.join(base_path, filename)
            if filename.endswith('.gz') and os.path.getsize(filepath) > 1024**3:  # > 1GB
                gros_fichiers.append(filepath)
    
    # Chercher dans non_extrait
    non_extrait_path = os.path.join(base_path, "non_extrait")
    if os.path.exists(non_extrait_path):
        for filename in os.listdir(non_extrait_path):
            filepath = os.path.join(non_extrait_path, filename)
            if filename.endswith('.gz'):
                gros_fichiers.append(filepath)
    
    if not gros_fichiers:
        print("❌ Aucun gros fichier OpenLibrary trouvé")
        return
    
    print("📁 Gros fichiers détectés:")
    for i, fichier in enumerate(gros_fichiers, 1):
        taille = os.path.getsize(fichier) / (1024**3)
        print(f"   {i}. {os.path.basename(fichier)} ({taille:.1f} GB)")
    
    # Sélection
    try:
        choix = int(input(f"\nChoisissez un fichier à analyser (1-{len(gros_fichiers)}): ")) - 1
        fichier_choisi = gros_fichiers[choix]
    except (ValueError, IndexError):
        print("❌ Choix invalide")
        return
    
    # Options d'analyse
    print(f"\n📊 OPTIONS D'ANALYSE:")
    print(f"   1. Analyse rapide (100,000 lignes)")
    print(f"   2. Analyse moyenne (500,000 lignes)")
    print(f"   3. Analyse approfondie (1,000,000 lignes)")
    
    echantillon_map = {'1': 100000, '2': 500000, '3': 1000000}
    choix_echantillon = input("Choisissez le niveau d'analyse (1-3): ").strip()
    echantillon = echantillon_map.get(choix_echantillon, 100000)
    
    # Lancer l'analyse
    stats = analyser_fichier_openlibrary(fichier_choisi, echantillon)
    
    if stats:
        print(f"\n💡 RECOMMANDATIONS:")
        editions_estimees = stats.get('editions_estimees', 0)
        
        if editions_estimees > 10000000:  # > 10M
            print(f"   🚀 Fichier très volumineux ({editions_estimees/1000000:.1f}M éditions)")
            print(f"   💡 Recommandation: Extraction par lots de 100,000-500,000")
        elif editions_estimees > 1000000:  # > 1M
            print(f"   📚 Fichier volumineux ({editions_estimees/1000000:.1f}M éditions)")
            print(f"   💡 Recommandation: Extraction par lots de 500,000-1,000,000")
        else:
            print(f"   📖 Fichier gérable ({editions_estimees:,} éditions)")
            print(f"   💡 Recommandation: Extraction complète possible")
        
        print(f"\n🔧 PROCHAINES ÉTAPES SUGGÉRÉES:")
        print(f"   1. Utiliser extraction_massive.py avec les estimations ci-dessus")
        print(f"   2. Nettoyer les données avec nettoyage_ultra.py")
        print(f"   3. Formater pour la base de données avec le script de formatage")

if __name__ == "__main__":
    main() 