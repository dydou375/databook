#!/usr/bin/env python3
"""
Exemple d'utilisation de l'extracteur de livres OpenLibrary
===========================================================

Ce script montre comment utiliser la classe ExtracteurLivres 
pour extraire et analyser les informations des livres.
"""

from extracteur_livres import ExtracteurLivres
import os


def exemple_extraction_simple():
    """Exemple d'extraction simple avec critères de base"""
    print("📚 EXEMPLE D'EXTRACTION SIMPLE")
    print("=" * 50)
    
    # Chemin vers vos fichiers OpenLibrary (à modifier selon votre configuration)
    chemin_openlibrary = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary"
    
    # Vérifier que le chemin existe
    if not os.path.exists(chemin_openlibrary):
        print(f"❌ Chemin non trouvé: {chemin_openlibrary}")
        print("💡 Modifiez la variable 'chemin_openlibrary' avec le bon chemin")
        return
    
    # Créer l'extracteur
    extracteur = ExtracteurLivres(chemin_openlibrary)
    
    # Définir des critères simples
    criteres_simples = {
        'avec_titre': True,      # Livres avec titre
        'avec_isbn': False,      # ISBN pas obligatoire
        'avec_auteur': False,    # Auteur pas obligatoire
    }
    
    # Extraire 500 livres
    print("\n🔍 Extraction de 500 livres avec critères simples...")
    livres = extracteur.extraire_editions_echantillon(
        max_livres=500, 
        criteres=criteres_simples
    )
    
    if livres:
        print(f"✅ {len(livres)} livres extraits")
        
        # Analyser les livres
        df = extracteur.analyser_livres_extraits(livres)
        
        # Sauvegarder
        extracteur.sauvegarder_livres(df, "exemple_livres_simples.csv")
        
        return df
    else:
        print("❌ Aucun livre extrait")
        return None


def exemple_extraction_avancee():
    """Exemple d'extraction avec critères avancés"""
    print("\n📚 EXEMPLE D'EXTRACTION AVANCÉE")
    print("=" * 50)
    
    chemin_openlibrary = r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary"
    
    if not os.path.exists(chemin_openlibrary):
        print(f"❌ Chemin non trouvé: {chemin_openlibrary}")
        return
    
    extracteur = ExtracteurLivres(chemin_openlibrary)
    
    # Critères plus stricts
    criteres_avances = {
        'avec_titre': True,
        'avec_isbn': True,        # ISBN obligatoire
        'avec_auteur': True,      # Auteur obligatoire
        'annee_min': 1990,        # Livres depuis 1990
        'annee_max': 2024,        # Jusqu'à 2024
        'langues': ['eng', 'fre'] # Seulement anglais et français
    }
    
    print("🔍 Critères avancés:")
    for cle, valeur in criteres_avances.items():
        print(f"   • {cle}: {valeur}")
    
    # Extraire 1000 livres
    print(f"\n🔍 Extraction avec critères avancés...")
    livres = extracteur.extraire_editions_echantillon(
        max_livres=1000, 
        criteres=criteres_avances
    )
    
    if livres:
        print(f"✅ {len(livres)} livres extraits selon les critères")
        
        # Analyser
        df = extracteur.analyser_livres_extraits(livres)
        
        # Sauvegarder
        extracteur.sauvegarder_livres(df, "exemple_livres_avances.csv")
        
        return df
    else:
        print("❌ Aucun livre correspondant aux critères")
        return None


def exemple_analyse_personnalisee(df):
    """Exemple d'analyse personnalisée du DataFrame"""
    print("\n📊 EXEMPLE D'ANALYSE PERSONNALISÉE")
    print("=" * 50)
    
    if df is None or df.empty:
        print("❌ Aucun DataFrame à analyser")
        return
    
    print(f"📏 Dataset: {len(df)} livres")
    
    # Livres avec ISBN-13
    if 'isbn_13' in df.columns:
        avec_isbn13 = df[df['isbn_13'].notna() & (df['isbn_13'] != '')]
        print(f"📖 Livres avec ISBN-13: {len(avec_isbn13)} ({len(avec_isbn13)/len(df)*100:.1f}%)")
    
    # Livres récents (après 2000)
    if 'annee_publication' in df.columns:
        livres_recents = df[df['annee_publication'] >= 2000]
        print(f"🆕 Livres récents (≥2000): {len(livres_recents)} ({len(livres_recents)/len(df)*100:.1f}%)")
    
    # Livres avec description
    if 'description' in df.columns:
        avec_description = df[df['description'].notna() & (df['description'] != '')]
        print(f"📝 Livres avec description: {len(avec_description)} ({len(avec_description)/len(df)*100:.1f}%)")
    
    # Top 5 des éditeurs
    if 'editeurs' in df.columns:
        tous_editeurs = []
        for editeurs in df['editeurs'].dropna():
            if editeurs:
                tous_editeurs.extend(editeurs.split(' | '))
        
        if tous_editeurs:
            import pandas as pd
            top_editeurs = pd.Series(tous_editeurs).value_counts().head(5)
            print(f"\n🏢 TOP 5 ÉDITEURS:")
            for i, (editeur, compte) in enumerate(top_editeurs.items(), 1):
                print(f"   {i}. {editeur[:40]}: {compte} livres")
    
    # Livres de qualité (avec beaucoup de métadonnées)
    if 'score_qualite' in df.columns:
        livres_qualite = df[df['score_qualite'] >= 4]
        print(f"\n⭐ Livres de qualité (score ≥4): {len(livres_qualite)} ({len(livres_qualite)/len(df)*100:.1f}%)")
        
        if len(livres_qualite) > 0:
            print(f"📚 Exemple de livre de qualité:")
            livre_exemple = livres_qualite.iloc[0]
            print(f"   Titre: {livre_exemple['titre']}")
            if livre_exemple.get('editeurs'):
                print(f"   Éditeur: {livre_exemple['editeurs'][:50]}")
            if livre_exemple.get('annee_publication'):
                print(f"   Année: {livre_exemple['annee_publication']}")


def fonction_test_complete():
    """Fonction de test complète pour valider le bon fonctionnement"""
    print("🧪 FONCTION DE TEST COMPLÈTE")
    print("=" * 60)
    
    try:
        # Test 1: Extraction simple
        print("\n1️⃣ Test d'extraction simple...")
        df_simple = exemple_extraction_simple()
        
        if df_simple is not None and not df_simple.empty:
            print("✅ Test extraction simple: RÉUSSI")
        else:
            print("❌ Test extraction simple: ÉCHEC")
            return False
        
        # Test 2: Extraction avancée
        print("\n2️⃣ Test d'extraction avancée...")
        df_avance = exemple_extraction_avancee()
        
        if df_avance is not None and not df_avance.empty:
            print("✅ Test extraction avancée: RÉUSSI")
        else:
            print("⚠️ Test extraction avancée: Aucun résultat (critères trop stricts)")
        
        # Test 3: Analyse personnalisée
        print("\n3️⃣ Test d'analyse personnalisée...")
        exemple_analyse_personnalisee(df_simple)
        print("✅ Test analyse personnalisée: RÉUSSI")
        
        # Test 4: Vérification des fichiers créés
        print("\n4️⃣ Test de sauvegarde...")
        fichiers_attendus = ["exemple_livres_simples.csv"]
        if df_avance is not None:
            fichiers_attendus.append("exemple_livres_avances.csv")
        
        for fichier in fichiers_attendus:
            if os.path.exists(fichier):
                taille = os.path.getsize(fichier)
                print(f"✅ Fichier créé: {fichier} ({taille:,} octets)")
            else:
                print(f"❌ Fichier manquant: {fichier}")
        
        print("\n🎉 TOUS LES TESTS SONT TERMINÉS!")
        print("📁 Vérifiez les fichiers CSV créés dans le répertoire courant")
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur durant les tests: {e}")
        return False


def main():
    """Fonction principale"""
    print("🚀 EXEMPLE D'UTILISATION - EXTRACTEUR DE LIVRES")
    print("=" * 60)
    print("Ce script démontre l'utilisation de l'extracteur de livres OpenLibrary")
    print()
    
    # Lancer la fonction de test complète
    succes = fonction_test_complete()
    
    if succes:
        print("\n💡 UTILISATION PERSONNALISÉE:")
        print("Vous pouvez maintenant utiliser l'extracteur ainsi:")
        print()
        print("from extracteur_livres import ExtracteurLivres")
        print("extracteur = ExtracteurLivres('chemin/vers/vos/fichiers')")
        print("livres = extracteur.extraire_editions_echantillon(max_livres=1000)")
        print("df = extracteur.analyser_livres_extraits(livres)")
        print("extracteur.sauvegarder_livres(df, 'mes_livres.csv')")
    else:
        print("\n❌ Certains tests ont échoué. Vérifiez:")
        print("   • Le chemin vers les fichiers OpenLibrary")
        print("   • La présence des fichiers d'éditions")
        print("   • Les permissions d'écriture dans le répertoire")


if __name__ == "__main__":
    main() 