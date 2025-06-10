import json
import os
from collections import defaultdict

def creer_mapping_categories():
    """
    Crée un mapping entre les catégories des APIs et tes fichiers JSON.
    """
    mapping = {
        # Nom du fichier -> Liste des mots-clés qui correspondent à cette catégorie
        "fiction": ["fiction", "novel", "novels", "literature", "literary fiction", "contemporary fiction"],
        "science": ["science", "physics", "chemistry", "biology", "astronomy", "mathematics", "scientific"],
        "computers": ["computers", "technology", "programming", "software", "information technology", "computer science"],
        "history": ["history", "historical", "biography", "biographies", "memoir", "world war"],
        "philosophy": ["philosophy", "ethics", "metaphysics", "logic", "philosophical"],
        "psychology": ["psychology", "mental health", "cognitive science", "behavioral science", "psychotherapy"],
        "religion": ["religion", "theology", "spirituality", "christianity", "islam", "judaism", "buddhism"],
        "art": ["art", "painting", "sculpture", "design", "visual arts", "photography"],
        "music": ["music", "musical", "composers", "instruments", "jazz", "classical"],
        "performing_arts": ["performing arts", "theater", "theatre", "dance", "drama", "acting"],
        "poetry": ["poetry", "poems", "verse", "poets"],
        "drama": ["drama", "plays", "theater", "theatre", "theatrical"],
        "comics": ["comics", "graphic novels", "manga", "comic books", "superhero"],
        "juvenile_fiction": ["juvenile fiction", "children's books", "kids", "young readers", "children's fiction"],
        "juvenile_nonfiction": ["juvenile nonfiction", "children's nonfiction", "educational"],
        "young_adult_fiction": ["young adult fiction", "teen fiction", "ya fiction", "teenage"],
        "education": ["education", "teaching", "pedagogy", "learning", "academic"],
        "linguistics": ["linguistics", "language", "grammar", "phonetics", "etymology"],
        "foreign_language_study": ["foreign language study", "language learning", "esl", "french", "spanish"],
        "literary_criticism": ["literary criticism", "literary theory", "criticism", "literary analysis"],
        "literature": ["literature", "literary", "classics", "world literature", "modern literature"],
        "business_economics": ["business", "economics", "finance", "management", "entrepreneurship", "marketing"],
        "law": ["law", "legal", "jurisprudence", "constitutional law", "criminal law"],
        "political_science": ["political science", "politics", "government", "international relations"],
        "social_science": ["social science", "sociology", "anthropology", "social studies"],
        "health_fitness": ["health", "fitness", "wellness", "exercise", "nutrition", "diet"],
        "medical": ["medical", "medicine", "health", "anatomy", "physiology", "nursing"],
        "self_help": ["self-help", "personal development", "motivation", "self improvement"],
        "cooking": ["cooking", "recipes", "culinary", "food", "gastronomy", "chef"],
        "house_home": ["house & home", "home improvement", "interior design", "architecture"],
        "family_relationships": ["family", "relationships", "parenting", "marriage", "dating"],
        "travel": ["travel", "tourism", "geography", "travel guides", "adventure travel"],
        "sports_recreation": ["sports", "recreation", "games", "athletics", "football", "basketball"],
        "nature": ["nature", "environment", "ecology", "wildlife", "conservation"],
        "pets": ["pets", "animals", "veterinary", "animal care", "dogs", "cats"],
        "gardening": ["gardening", "horticulture", "plants", "landscaping"],
        "crafts_hobbies": ["crafts", "hobbies", "diy", "handicrafts", "knitting"],
        "games": ["games", "gaming", "puzzles", "board games", "chess"],
        "antiques_collectibles": ["antiques", "collectibles", "collecting"],
        "true_crime": ["true crime", "crime", "criminal justice", "murder"],
        "science_fiction": ["science fiction", "sci-fi", "speculative fiction", "space opera"],
        "fantasy": ["fantasy", "magic", "dragons", "epic fantasy", "urban fantasy"],
        "horror": ["horror", "supernatural", "gothic", "scary", "thriller"],
        "mystery": ["mystery", "detective", "crime fiction", "suspense", "murder mystery"],
        "thriller": ["thriller", "suspense", "espionage", "spy"],
        "romance": ["romance", "love story", "romantic fiction", "historical romance"],
        "adventure": ["adventure", "action", "exploration"],
        "reference": ["reference", "encyclopedia", "dictionary", "handbook", "guide"]
    }
    return mapping

def determiner_fichier_cible(categories_livre):
    """
    Détermine dans quel fichier JSON le livre doit aller selon ses catégories.
    """
    if not categories_livre:
        return "reference"
    
    mapping = creer_mapping_categories()
    
    # Normaliser les catégories du livre
    categories_normalisees = [cat.lower().strip() for cat in categories_livre if cat]
    
    # Chercher la meilleure correspondance
    scores = {}
    
    for fichier, mots_cles in mapping.items():
        score = 0
        for categorie in categories_normalisees:
            for mot_cle in mots_cles:
                # Vérifier si le mot-clé est contenu dans la catégorie ou vice versa
                if mot_cle in categorie or categorie in mot_cle:
                    score += 1
        if score > 0:
            scores[fichier] = score
    
    # Retourner le fichier avec le meilleur score
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    else:
        return "reference"  # Fichier par défaut

def lire_tous_les_livres():
    """
    Lit tous les livres depuis les fichiers JSON existants.
    """
    dossier = "livres_json"
    tous_les_livres = []
    
    if not os.path.exists(dossier):
        print(f"❌ Le dossier {dossier} n'existe pas!")
        return []
    
    for fichier in os.listdir(dossier):
        if fichier.endswith('.json'):
            chemin = os.path.join(dossier, fichier)
            
            try:
                with open(chemin, 'r', encoding='utf-8') as f:
                    livres = json.load(f)
                
                # Ajouter l'info du fichier source
                for livre in livres:
                    livre['fichier_source'] = fichier.replace('.json', '')
                
                tous_les_livres.extend(livres)
                print(f"📖 Lu {fichier} : {len(livres)} livres")
                
            except Exception as e:
                print(f"❌ Erreur lors de la lecture de {fichier} : {e}")
    
    return tous_les_livres

def analyser_structure_categories():
    """
    Analyse la structure des catégories dans tes fichiers existants.
    """
    print("🔍 ANALYSE DE LA STRUCTURE DES CATÉGORIES\n")
    
    dossier = "livres_json"
    champs_categories = {}
    
    for fichier in os.listdir(dossier):
        if fichier.endswith('.json'):
            with open(os.path.join(dossier, fichier), 'r', encoding='utf-8') as f:
                livres = json.load(f)
            
            print(f"📁 {fichier} :")
            
            for i, livre in enumerate(livres[:2]):  # Analyser les 2 premiers
                print(f"  📖 Livre {i+1} : '{livre.get('titre', 'N/A')[:40]}...'")
                
                # Chercher tous les champs qui pourraient contenir des catégories
                for cle, valeur in livre.items():
                    if any(mot in cle.lower() for mot in ['genre', 'categ', 'subject', 'class']):
                        if cle not in champs_categories:
                            champs_categories[cle] = 0
                        champs_categories[cle] += 1
                        print(f"    🏷️  {cle} : {valeur}")
            print()
    
    print("📊 RÉSUMÉ DES CHAMPS CATÉGORIES TROUVÉS :")
    for champ, count in champs_categories.items():
        print(f"  • {champ} : trouvé {count} fois")
    
    return champs_categories

def analyser_categories_reelles():
    """
    Analyse TOUTES les catégories réelles présentes dans tes fichiers.
    """
    print("🔍 ANALYSE DES CATÉGORIES RÉELLES DANS TES FICHIERS\n")
    
    dossier = "livres_json"
    toutes_categories = set()
    categories_par_fichier = {}
    
    for fichier in os.listdir(dossier):
        if fichier.endswith('.json'):
            categories_fichier = set()
            
            with open(os.path.join(dossier, fichier), 'r', encoding='utf-8') as f:
                livres = json.load(f)
            
            print(f"📁 {fichier} ({len(livres)} livres):")
            
            for livre in livres:
                # Chercher toutes les catégories
                categories_livre = []
                
                # Chercher dans tous les champs possibles
                for cle, valeur in livre.items():
                    if any(mot in cle.lower() for mot in ['genre', 'categ', 'subject', 'class']):
                        if isinstance(valeur, list):
                            categories_livre.extend([str(v) for v in valeur if v])
                        elif isinstance(valeur, str) and valeur.strip():
                            categories_livre.append(valeur)
                        elif isinstance(valeur, dict):
                            for sous_cle, sous_val in valeur.items():
                                if isinstance(sous_val, list):
                                    categories_livre.extend([str(v) for v in sous_val if v])
                
                # Ajouter les catégories trouvées
                for cat in categories_livre:
                    cat_clean = cat.strip()
                    if cat_clean:
                        categories_fichier.add(cat_clean)
                        toutes_categories.add(cat_clean)
            
            categories_par_fichier[fichier] = categories_fichier
            
            # Afficher quelques exemples
            exemples = list(categories_fichier)[:5]
            print(f"   Exemples de catégories : {exemples}")
            if len(categories_fichier) > 5:
                print(f"   ... et {len(categories_fichier) - 5} autres")
            print(f"   Total unique : {len(categories_fichier)}\n")
    
    print(f"📊 RÉSUMÉ GLOBAL :")
    print(f"Total catégories uniques trouvées : {len(toutes_categories)}")
    print(f"\n🏷️  TOUTES LES CATÉGORIES TROUVÉES :")
    
    # Afficher toutes les catégories triées
    for i, cat in enumerate(sorted(toutes_categories), 1):
        print(f"{i:3d}. {cat}")
    
    return toutes_categories, categories_par_fichier

def creer_mapping_dynamique(toutes_categories):
    """
    Crée un mapping basé sur les vraies catégories trouvées.
    """
    print("\n🎯 CRÉATION DU MAPPING DYNAMIQUE\n")
    
    # Mapping manuel amélioré basé sur ce qu'on trouve vraiment
    mapping_manuel = {
        "fiction": [
            "fiction", "novel", "novels", "literature", "literary fiction", 
            "contemporary fiction", "general fiction", "adult fiction"
        ],
        "science": [
            "science", "physics", "chemistry", "biology", "astronomy", 
            "mathematics", "scientific", "math", "mathematics"
        ],
        "computers": [
            "computers", "technology", "programming", "software", 
            "information technology", "computer science", "computing"
        ],
        "history": [
            "history", "historical", "biography", "biographies", "memoir", 
            "world war", "historical fiction", "biography & autobiography"
        ],
        "philosophy": [
            "philosophy", "ethics", "metaphysics", "logic", "philosophical"
        ],
        "psychology": [
            "psychology", "mental health", "cognitive science", 
            "behavioral science", "psychotherapy"
        ],
        "religion": [
            "religion", "theology", "spirituality", "christianity", 
            "islam", "judaism", "buddhism"
        ],
        "art": [
            "art", "painting", "sculpture", "design", "visual arts", 
            "photography", "arts"
        ],
        "music": [
            "music", "musical", "composers", "instruments", "jazz", "classical"
        ],
        "performing_arts": [
            "performing arts", "theater", "theatre", "dance", "drama", 
            "acting", "performing"
        ],
        "poetry": [
            "poetry", "poems", "verse", "poets"
        ],
        "drama": [
            "drama", "plays", "theater", "theatre", "theatrical"
        ],
        "comics": [
            "comics", "graphic novels", "manga", "comic books", 
            "superhero", "comics & graphic novels"
        ],
        "juvenile_fiction": [
            "juvenile fiction", "children's books", "kids", "young readers", 
            "children's fiction", "children", "juvenile"
        ],
        "juvenile_nonfiction": [
            "juvenile nonfiction", "children's nonfiction", "educational"
        ],
        "young_adult_fiction": [
            "young adult fiction", "teen fiction", "ya fiction", 
            "teenage", "young adult"
        ],
        "education": [
            "education", "teaching", "pedagogy", "learning", "academic", 
            "educational"
        ],
        "science_fiction": [
            "science fiction", "sci-fi", "speculative fiction", 
            "space opera", "science fiction & fantasy"
        ],
        "fantasy": [
            "fantasy", "magic", "dragons", "epic fantasy", "urban fantasy"
        ],
        "horror": [
            "horror", "supernatural", "gothic", "scary"
        ],
        "mystery": [
            "mystery", "detective", "crime fiction", "suspense", 
            "murder mystery", "mystery & detective", "mystery & thrillers"
        ],
        "thriller": [
            "thriller", "suspense", "espionage", "spy", "thrillers"
        ],
        "romance": [
            "romance", "love story", "romantic fiction", "historical romance"
        ],
        "adventure": [
            "adventure", "action", "exploration"
        ],
        "business_economics": [
            "business", "economics", "finance", "management", 
            "entrepreneurship", "marketing", "business & economics"
        ],
        "self_help": [
            "self-help", "personal development", "motivation", 
            "self improvement", "self help"
        ],
        "reference": [
            "reference", "encyclopedia", "dictionary", "handbook", 
            "guide", "general"
        ]
    }
    
    # Analyser quelles catégories réelles correspondent à quoi
    correspondances = {}
    categories_non_mappees = set(toutes_categories)
    
    for fichier_cible, mots_cles in mapping_manuel.items():
        correspondances[fichier_cible] = []
        
        for categorie_reelle in toutes_categories:
            cat_lower = categorie_reelle.lower()
            
            for mot_cle in mots_cles:
                if mot_cle.lower() in cat_lower or cat_lower in mot_cle.lower():
                    correspondances[fichier_cible].append(categorie_reelle)
                    categories_non_mappees.discard(categorie_reelle)
                    break
    
    # Afficher les correspondances trouvées
    for fichier, categories in correspondances.items():
        if categories:
            print(f"📁 {fichier} :")
            for cat in categories[:5]:  # Limiter à 5 pour la lisibilité
                print(f"   ✅ {cat}")
            if len(categories) > 5:
                print(f"   ... et {len(categories) - 5} autres")
            print()
    
    # Afficher les catégories non mappées
    if categories_non_mappees:
        print(f"⚠️  CATÉGORIES NON MAPPÉES ({len(categories_non_mappees)}) :")
        for cat in sorted(categories_non_mappees)[:10]:
            print(f"   ❓ {cat}")
        if len(categories_non_mappees) > 10:
            print(f"   ... et {len(categories_non_mappees) - 10} autres")
    
    return mapping_manuel, correspondances

def determiner_fichier_cible_ameliore(categories_livre, mapping_manuel):
    """
    Version améliorée pour déterminer le fichier cible.
    """
    if not categories_livre:
        return "reference"
    
    # Normaliser les catégories du livre
    categories_normalisees = [cat.lower().strip() for cat in categories_livre if cat and cat.strip()]
    
    # Chercher la meilleure correspondance
    scores = {}
    
    for fichier, mots_cles in mapping_manuel.items():
        score = 0
        correspondances_trouvees = []
        
        for categorie in categories_normalisees:
            for mot_cle in mots_cles:
                mot_cle_lower = mot_cle.lower()
                
                # Correspondance exacte
                if categorie == mot_cle_lower:
                    score += 10
                    correspondances_trouvees.append(f"exact: {categorie}")
                # Contenance
                elif mot_cle_lower in categorie:
                    score += 5
                    correspondances_trouvees.append(f"contient: {mot_cle_lower} dans {categorie}")
                elif categorie in mot_cle_lower:
                    score += 3
                    correspondances_trouvees.append(f"dans: {categorie} dans {mot_cle_lower}")
        
        if score > 0:
            scores[fichier] = {"score": score, "correspondances": correspondances_trouvees}
    
    # Debug pour voir le processus de décision
    if scores:
        meilleur_fichier = max(scores.items(), key=lambda x: x[1]["score"])
        return meilleur_fichier[0]
    else:
        return "reference"

def redistribuer_livres_ameliore():
    """
    Version améliorée de la redistribution.
    """
    print("🚀 REDISTRIBUTION AMÉLIORÉE DES LIVRES\n")
    
    # Étape 1 : Analyser les vraies catégories
    toutes_categories, categories_par_fichier = analyser_categories_reelles()
    
    # Étape 2 : Créer le mapping dynamique
    mapping_manuel, correspondances = creer_mapping_dynamique(toutes_categories)
    
    # Étape 3 : Redistribuer avec le nouveau mapping
    tous_les_livres = lire_tous_les_livres()
    
    if not tous_les_livres:
        print("❌ Aucun livre trouvé!")
        return
    
    print(f"\n📚 REDISTRIBUTION DE {len(tous_les_livres)} LIVRES :\n")
    
    livres_par_categorie = defaultdict(list)
    stats = {"total": len(tous_les_livres), "redistribues": 0, "debug_count": 0}
    
    for livre in tous_les_livres:
        titre = livre.get('titre', 'Titre inconnu')[:40]
        
        # Extraire les catégories
        categories = []
        for cle, valeur in livre.items():
            if any(mot in cle.lower() for mot in ['genre', 'categ', 'subject']):
                if isinstance(valeur, list):
                    categories.extend([str(v) for v in valeur if v])
                elif isinstance(valeur, str) and valeur.strip():
                    categories.append(valeur)
        
        # Nettoyer
        categories = list(set([cat.strip() for cat in categories if cat and cat.strip()]))
        
        # Déterminer le fichier cible
        fichier_cible = determiner_fichier_cible_ameliore(categories, mapping_manuel)
        
        # Debug pour les premiers livres
        if stats["debug_count"] < 5:
            print(f"🔍 DEBUG {stats['debug_count']+1}. '{titre}...'")
            print(f"   Catégories : {categories}")
            print(f"   → Fichier cible : {fichier_cible}")
            stats["debug_count"] += 1
        
        # Préparer le livre
        livre_clean = {k: v for k, v in livre.items() if k not in ['fichier_source', 'categories_trouvees', 'fichier_cible', 'genres_google']}
        livre_clean['tous_les_genres'] = categories
        livres_par_categorie[fichier_cible].append(livre_clean)
        stats["redistribues"] += 1
    
    # Sauvegarder
    dossier_sortie = "livres_json_redistribues"
    os.makedirs(dossier_sortie, exist_ok=True)
    
    print(f"\n💾 SAUVEGARDE :")
    for categorie, livres in livres_par_categorie.items():
        nom_fichier = f"{dossier_sortie}/{categorie}.json"
        
        with open(nom_fichier, 'w', encoding='utf-8') as f:
            json.dump(livres, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {categorie}.json : {len(livres)} livres")
    
    return livres_par_categorie

def verifier_categories_dans_nouveaux_fichiers():
    """
    Vérifie que les catégories sont bien présentes dans les nouveaux fichiers.
    """
    print("\n🔍 VÉRIFICATION DES CATÉGORIES DANS LES NOUVEAUX FICHIERS:\n")
    
    dossier = "livres_json_redistribues"
    
    if not os.path.exists(dossier):
        print(f"❌ Le dossier {dossier} n'existe pas!")
        return False
    
    for fichier in os.listdir(dossier):
        if fichier.endswith('.json'):
            with open(os.path.join(dossier, fichier), 'r', encoding='utf-8') as f:
                livres = json.load(f)
            
            print(f"📁 {fichier} : {len(livres)} livres")
            
            # Vérifier les 2 premiers livres de chaque fichier
            for i, livre in enumerate(livres[:2]):
                titre = livre.get('titre', 'N/A')[:30]
                categories_consolidees = livre.get('categories_consolidees', [])
                champs_source = livre.get('champs_categories_source', [])
                
                print(f"  📖 {i+1}. '{titre}...'")
                print(f"     Catégories consolidées : {categories_consolidees}")
                print(f"     Champs source : {champs_source}")
                
                # Vérifier la présence d'autres champs de catégories
                autres_champs = []
                for cle, valeur in livre.items():
                    if any(mot in cle.lower() for mot in ['genre', 'categ', 'subject']):
                        autres_champs.append(f"{cle}: {valeur}")
                
                if autres_champs:
                    print(f"     Autres champs catégories : {autres_champs}")
                print()

def verifier_coherence():
    """
    Vérifie la cohérence des données redistribuées.
    """
    print("\n🔍 VÉRIFICATION DE COHÉRENCE:\n")
    
    dossier = "livres_json_redistribues"
    
    if not os.path.exists(dossier):
        print(f"❌ Le dossier {dossier} n'existe pas!")
        return False
    
    problemes = []
    stats = {"total_livres": 0, "total_fichiers": 0}
    
    for fichier in os.listdir(dossier):
        if fichier.endswith('.json'):
            stats["total_fichiers"] += 1
            categorie_fichier = fichier.replace('.json', '')
            
            with open(os.path.join(dossier, fichier), 'r', encoding='utf-8') as f:
                livres = json.load(f)
            
            stats["total_livres"] += len(livres)
            print(f"📁 {fichier} : {len(livres)} livres")
            
            # Vérifier quelques livres par fichier
            for i, livre in enumerate(livres[:3]):  # Vérifier les 3 premiers
                titre = livre.get('titre', 'Titre inconnu')[:30]
                
                # Vérifier les champs essentiels
                if not livre.get('titre'):
                    problemes.append(f"{fichier}[{i}] : Titre manquant")
                
                if not livre.get('auteurs'):
                    problemes.append(f"{fichier}[{i}] : Auteurs manquants")
                
                # Vérifier la cohérence des catégories
                categories = []
                if "tous_les_genres" in livre:
                    categories = livre["tous_les_genres"]
                elif "genres_google" in livre:
                    categories = livre["genres_google"]
                
                if categories:
                    fichier_correct = determiner_fichier_cible(categories)
                    if fichier_correct != categorie_fichier:
                        problemes.append(f"{fichier}[{i}] : '{titre}...' devrait être dans {fichier_correct}.json")
    
    # Résultats
    print(f"\n📊 RÉSUMÉ DE LA VÉRIFICATION :")
    print(f"Fichiers vérifiés : {stats['total_fichiers']}")
    print(f"Livres vérifiés : {stats['total_livres']}")
    print(f"Problèmes détectés : {len(problemes)}")
    
    if problemes:
        print(f"\n⚠️  PROBLÈMES DÉTECTÉS :")
        for probleme in problemes[:5]:  # Afficher les 5 premiers
            print(f"  • {probleme}")
        if len(problemes) > 5:
            print(f"  ... et {len(problemes) - 5} autres problèmes")
        return False
    else:
        print(f"\n✅ AUCUN PROBLÈME DÉTECTÉ - Données cohérentes !")
        return True

def main():
    """
    Fonction principale améliorée.
    """
    print("=" * 70)
    print("🎯 REDISTRIBUTION AMÉLIORÉE DES LIVRES POUR MONGODB")
    print("=" * 70)
    
    redistribuer_livres_ameliore()

if __name__ == "__main__":
    main()