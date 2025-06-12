#!/usr/bin/env python3
"""
Script d'extraction massive de livres OpenLibrary
=================================================

Ce script extrait un grand nombre de livres depuis les fichiers volumineux
d'OpenLibrary pour créer une base de données plus complète.
"""

import os
import sys
from extracteur_livres import ExtracteurLivres

def extraction_massive():
    """Extrait un grand nombre de livres depuis les fichiers OpenLibrary"""
    
    print("🚀 EXTRACTION MASSIVE DE LIVRES OPENLIBRARY")
    print("=" * 60)
    
    # Chemins des fichiers
    base_path = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary"
    
    if not os.path.exists(base_path):
        print(f"❌ Répertoire non trouvé: {base_path}")
        return False
    
    # Créer l'extracteur
    extracteur = ExtracteurLivres(base_path)
    
    # Vérifier les fichiers disponibles
    print(f"\n📁 Fichiers détectés:")
    if extracteur.fichier_editions:
        info = extracteur.analyser_taille_fichier(extracteur.fichier_editions)
        print(f"   Éditions: {info['fichier']} ({info['taille_gb']} GB)")
    
    # Menu d'options
    print(f"\n🎯 OPTIONS D'EXTRACTION:")
    print(f"   1. Extraction rapide    : 10,000 livres")
    print(f"   2. Extraction moyenne   : 50,000 livres")
    print(f"   3. Extraction importante: 100,000 livres")
    print(f"   4. Extraction massive   : 500,000 livres")
    print(f"   5. Personnalisé")
    
    choix = input(f"\nChoisissez une option (1-5): ").strip()
    
    # Définir le nombre de livres selon le choix
    options = {
        '1': 10000,
        '2': 50000,
        '3': 100000,
        '4': 500000
    }
    
    if choix in options:
        max_livres = options[choix]
    elif choix == '5':
        try:
            max_livres = int(input("Nombre de livres à extraire: "))
        except ValueError:
            print("❌ Nombre invalide, utilisation de 10,000 par défaut")
            max_livres = 10000
    else:
        print("❌ Choix invalide, utilisation de 10,000 par défaut")
        max_livres = 10000
    
    print(f"\n📚 Extraction de {max_livres:,} livres...")
    print(f"⚠️  Cela peut prendre plusieurs minutes selon la taille du fichier")
    
    # Critères de base (assez permissifs pour avoir plus de résultats)
    criteres = {
        'avec_titre': True,      # Titre obligatoire
        'avec_isbn': False,      # ISBN optionnel
        'avec_auteur': False,    # Auteur optionnel
        'annee_min': None,       # Pas de limite d'année
        'annee_max': None,
        'langues': None          # Toutes les langues
    }
    
    # Demander si l'utilisateur veut des critères plus stricts
    stricte = input("Voulez-vous des critères stricts ? (ISBN + Auteur obligatoires) [o/N]: ").strip().lower()
    
    if stricte in ['o', 'oui', 'y', 'yes']:
        criteres.update({
            'avec_isbn': True,
            'avec_auteur': True,
            'annee_min': 1950,    # Livres depuis 1950
            'langues': ['eng', 'fre', 'spa', 'ger', 'ita']  # Langues principales
        })
        print("✅ Critères stricts activés")
    else:
        print("✅ Critères permissifs utilisés")
    
    # Extraction
    try:
        livres = extracteur.extraire_editions_echantillon(
            max_livres=max_livres, 
            criteres=criteres
        )
        
        if not livres:
            print("❌ Aucun livre extrait")
            return False
        
        print(f"✅ {len(livres):,} livres extraits avec succès")
        
        # Analyser les données
        print(f"\n📊 Analyse des données...")
        df = extracteur.analyser_livres_extraits(livres)
        
        # Sauvegarder avec un nom descriptif
        nom_fichier = f"livres_openlibrary_{len(livres)}_livres.csv"
        extracteur.sauvegarder_livres(df, nom_fichier)
        
        print(f"\n🎉 EXTRACTION TERMINÉE!")
        print(f"   Fichier créé: {nom_fichier}")
        print(f"   Nombre de livres: {len(df):,}")
        print(f"   Nombre de colonnes: {len(df.columns)}")
        
        # Proposer d'autres extractions
        autre = input(f"\nVoulez-vous faire une autre extraction ? [o/N]: ").strip().lower()
        if autre in ['o', 'oui', 'y', 'yes']:
            return extraction_massive()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        return False

def extraction_par_criteres():
    """Extraction avec critères spécifiques personnalisables"""
    
    print("\n🎯 EXTRACTION PAR CRITÈRES PERSONNALISÉS")
    print("=" * 50)
    
    base_path = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary"
    extracteur = ExtracteurLivres(base_path)
    
    # Interface pour définir les critères
    criteres = {'avec_titre': True}
    
    # ISBN
    isbn = input("ISBN obligatoire ? [o/N]: ").strip().lower()
    criteres['avec_isbn'] = isbn in ['o', 'oui', 'y', 'yes']
    
    # Auteur
    auteur = input("Auteur obligatoire ? [o/N]: ").strip().lower()
    criteres['avec_auteur'] = auteur in ['o', 'oui', 'y', 'yes']
    
    # Années
    try:
        annee_min = input("Année minimum (ou Entrée pour aucune): ").strip()
        criteres['annee_min'] = int(annee_min) if annee_min else None
        
        annee_max = input("Année maximum (ou Entrée pour aucune): ").strip()
        criteres['annee_max'] = int(annee_max) if annee_max else None
    except ValueError:
        print("⚠️  Années invalides, aucune limite appliquée")
        criteres['annee_min'] = None
        criteres['annee_max'] = None
    
    # Langues
    langues_input = input("Langues (séparées par des virgules, ou Entrée pour toutes): ").strip()
    if langues_input:
        criteres['langues'] = [l.strip() for l in langues_input.split(',')]
    else:
        criteres['langues'] = None
    
    # Nombre de livres
    try:
        max_livres = int(input("Nombre maximum de livres à extraire: "))
    except ValueError:
        max_livres = 10000
        print(f"⚠️  Utilisation de {max_livres:,} par défaut")
    
    print(f"\n🔍 Critères définis:")
    for cle, valeur in criteres.items():
        print(f"   • {cle}: {valeur}")
    
    # Extraction
    livres = extracteur.extraire_editions_echantillon(max_livres=max_livres, criteres=criteres)
    
    if livres:
        df = extracteur.analyser_livres_extraits(livres)
        nom_fichier = f"livres_criteres_{len(livres)}.csv"
        extracteur.sauvegarder_livres(df, nom_fichier)
        print(f"✅ Extraction terminée: {nom_fichier}")
    else:
        print("❌ Aucun livre trouvé avec ces critères")

def main():
    """Menu principal"""
    
    print("🔧 EXTRACTEUR MASSIVE DE LIVRES OPENLIBRARY")
    print("=" * 60)
    print("Ce script vous permet d'extraire un grand nombre de livres")
    print("depuis vos fichiers OpenLibrary volumineux.")
    print()
    
    while True:
        print("📋 MENU PRINCIPAL:")
        print("   1. Extraction massive (options prédéfinies)")
        print("   2. Extraction par critères personnalisés")
        print("   3. Informations sur les fichiers disponibles")
        print("   4. Quitter")
        
        choix = input("\nChoisissez une option (1-4): ").strip()
        
        if choix == '1':
            extraction_massive()
        elif choix == '2':
            extraction_par_criteres()
        elif choix == '3':
            # Afficher info sur les fichiers
            base_path = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary"
            extracteur = ExtracteurLivres(base_path)
            if extracteur.fichier_editions:
                extracteur.analyser_taille_fichier(extracteur.fichier_editions)
        elif choix == '4':
            print("👋 Au revoir!")
            break
        else:
            print("❌ Choix invalide")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    main() 