import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
import os

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

def extraire_repartition_notes(soup):
    """
    Extrait la répartition des notes (histogramme des étoiles)
    """
    repartition = {}
    
    try:
        # Méthode 1 : Chercher le texte complet de la page et analyser les patterns
        page_text = soup.get_text()
        
        # Patterns pour trouver la répartition (ex: "5★ 2 avis", "4★ 7 avis")
        star_patterns = [
            r'5★\s*(\d+)\s*avis',
            r'4★\s*(\d+)\s*avis', 
            r'3★\s*(\d+)\s*avis',
            r'2★\s*(\d+)\s*avis',
            r'1★\s*(\d+)\s*avis'
        ]
        
        for i, pattern in enumerate(star_patterns):
            nb_etoiles = 5 - i  # 5, 4, 3, 2, 1
            match = re.search(pattern, page_text)
            if match:
                repartition[f"{nb_etoiles}_etoiles"] = int(match.group(1))
        
        # Méthode 2 : Chercher dans les éléments spécifiques
        # Analyser les lignes qui contiennent "avis" et des étoiles
        all_text_elements = soup.find_all(text=re.compile(r'\d+\s*avis'))
        
        for text_elem in all_text_elements:
            parent = text_elem.parent
            if parent:
                # Chercher le contexte autour de ce texte
                context = parent.get_text()
                
                # Pour chaque nombre d'étoiles, voir si on trouve un pattern
                for nb_etoiles in range(1, 6):
                    patterns = [
                        rf'{nb_etoiles}★.*?(\d+)\s*avis',
                        rf'{nb_etoiles}\*.*?(\d+)\s*avis',
                        rf'{nb_etoiles}\s*étoiles?.*?(\d+)\s*avis'
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, context)
                        if match and f"{nb_etoiles}_etoiles" not in repartition:
                            repartition[f"{nb_etoiles}_etoiles"] = int(match.group(1))
        
        # Méthode 3 : Analyse spécifique de la structure Babelio
        # Chercher dans les divs/spans qui pourraient contenir l'histogramme
        possible_containers = soup.find_all(['div', 'section', 'ul'], 
                                          class_=lambda x: x and any(keyword in x.lower() 
                                          for keyword in ['rating', 'note', 'avis', 'review', 'histogram']))
        
        for container in possible_containers:
            container_text = container.get_text()
            if 'avis' in container_text and any(f'{i}★' in container_text for i in range(1, 6)):
                # Extraire tous les patterns d'avis dans ce conteneur
                avis_matches = re.findall(r'(\d+)★.*?(\d+)\s*avis', container_text)
                for nb_etoiles, nb_avis in avis_matches:
                    if f"{nb_etoiles}_etoiles" not in repartition:
                        repartition[f"{nb_etoiles}_etoiles"] = int(nb_avis)
        
        # Méthode 4 : Recherche dans les éléments avec attributs data
        data_elements = soup.find_all(attrs={"data-rating": True})
        for elem in data_elements:
            rating = elem.get('data-rating')
            # Chercher le nombre d'avis associé
            elem_text = elem.get_text()
            avis_match = re.search(r'(\d+)\s*avis', elem_text)
            if avis_match and rating:
                try:
                    rating_num = int(float(rating))
                    if 1 <= rating_num <= 5:
                        repartition[f"{rating_num}_etoiles"] = int(avis_match.group(1))
                except ValueError:
                    pass
        
        # S'assurer que toutes les étoiles sont présentes (avec 0 si pas trouvé)
        if repartition:
            for i in range(1, 6):
                if f"{i}_etoiles" not in repartition:
                    repartition[f"{i}_etoiles"] = 0
            
            print(f"📊 Répartition trouvée : 5★:{repartition.get('5_etoiles',0)}, 4★:{repartition.get('4_etoiles',0)}, 3★:{repartition.get('3_etoiles',0)}, 2★:{repartition.get('2_etoiles',0)}, 1★:{repartition.get('1_etoiles',0)}")
        
        return repartition if repartition else None
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction de la répartition : {e}")
        return None

def extraire_note_critique(container):
    """
    Extrait la note d'une critique individuelle de manière plus robuste
    """
    note_utilisateur = None
    
    try:
        # Méthode 1 : Compter les images d'étoiles
        stars_img = container.find_all("img", src=lambda x: x and ("etoile" in x or "star" in x))
        if stars_img:
            note_utilisateur = len(stars_img)
        
        # Méthode 2 : Chercher dans les divs avec rateit
        if not note_utilisateur:
            rateit_div = container.find("div", class_=lambda x: x and "rateit" in x)
            if rateit_div:
                # Analyser les attributs data-rateit-value ou similaires
                data_value = rateit_div.get("data-rateit-value")
                if data_value:
                    try:
                        note_utilisateur = float(data_value)
                    except ValueError:
                        pass
                
                # Ou analyser la classe pour déterminer le nombre d'étoiles
                if not note_utilisateur:
                    class_attr = rateit_div.get("class", [])
                    for cls in class_attr:
                        if "rateit-range" in cls:
                            # Extraire le nombre d'étoiles de la classe
                            match = re.search(r'(\d+)', cls)
                            if match:
                                note_utilisateur = int(match.group(1))
        
        # Méthode 3 : Chercher les spans avec classes d'étoiles
        if not note_utilisateur:
            star_spans = container.find_all("span", class_=lambda x: x and ("star" in x or "etoile" in x))
            if star_spans:
                note_utilisateur = len(star_spans)
        
        # Méthode 4 : Analyser le texte pour des patterns d'étoiles
        if not note_utilisateur:
            text_content = container.get_text()
            star_patterns = [r'★{1,5}', r'\*{1,5}', r'(\d+)/5', r'(\d+)\s*étoiles?']
            for pattern in star_patterns:
                match = re.search(pattern, text_content)
                if match:
                    if pattern == r'(\d+)/5' or pattern == r'(\d+)\s*étoiles?':
                        note_utilisateur = int(match.group(1))
                    else:
                        note_utilisateur = len(match.group())
                    break
        
        return note_utilisateur
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction de la note de critique : {e}")
        return None

def extraire_isbn_13_by_csv(fichier_csv):
    """
    Extrait les ISBN 13 d'un fichier CSV
    """
    df = pd.read_csv(fichier_csv, 
                    encoding='latin-1',
                    sep=';',
                    on_bad_lines='skip',
                    engine='python'
                    )
    
    list_isbn = df['ISBN'].tolist()
    return list_isbn

def chercher_babelio_par_isbn(isbn13):
    """
    Recherche un livre sur Babelio à partir de son ISBN
    """
    url = "https://www.babelio.com/recherche.php"
    
    # Données du formulaire POST (comme observé dans les DevTools)
    data = {
        'Recherche': isbn13,
        'recherche': ''
    }
    
    print(f"🔎 Recherche de l'ISBN {isbn13} sur Babelio...")
    
    try:
        res = requests.post(url, headers=headers, data=data, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")

        # Chercher le lien vers la fiche du livre
        lien = soup.find("a", class_="titre1")
        if not lien:
            # Essayer d'autres sélecteurs
            liens_livres = soup.find_all("a", href=lambda x: x and "/livres/" in x)
            if liens_livres:
                lien = liens_livres[0]
                print("✅ Lien trouvé avec sélecteur alternatif")
            else:
                print("❌ Aucun lien vers une fiche livre trouvé")
                return None
        else:
            print("✅ Lien trouvé avec class='titre1'")

        lien_fiche = "https://www.babelio.com" + lien["href"]
        return scraper_fiche_babelio(lien_fiche, isbn13)
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche : {e}")
        return None

def scraper_fiche_babelio(url, isbn=None):
    """
    Extrait les informations d'une fiche livre Babelio
    """
    print(f"📖 Extraction des données de : {url}")
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")

        # Titre du livre - cibler précisément la structure HTML
        titre = None
        
        # Méthode 1 : h1 avec itemprop="name" (structure principale)
        titre_tag = soup.find("h1", itemprop="name")
        if titre_tag:
            # Chercher le lien à l'intérieur du h1
            lien_titre = titre_tag.find("a")
            if lien_titre:
                titre = lien_titre.get_text(strip=True)
            else:
                titre = titre_tag.get_text(strip=True)
        
        # Méthode 2 : lien direct avec href contenant le titre
        if not titre:
            liens_livre = soup.find_all("a", href=lambda x: x and "/livres/" in x)
            for lien in liens_livre:
                texte_lien = lien.get_text(strip=True)
                # Prendre le premier lien non vide qui semble être un titre (pas trop long)
                if texte_lien and len(texte_lien) < 100 and not any(mot in texte_lien.lower() for mot in ['critique', 'citation', 'forum', 'auteur']):
                    titre = texte_lien
                    break
        
        # Méthode 3 : h1 dans la zone livre_header_con
        if not titre:
            div_header = soup.find("div", class_="livre_header_con")
            if div_header:
                titre_tag = div_header.find("h1")
                if titre_tag:
                    lien_titre = titre_tag.find("a")
                    if lien_titre:
                        titre = lien_titre.get_text(strip=True)
                    else:
                        titre = titre_tag.get_text(strip=True)
                
        # Méthode 4 : h1 général comme fallback
        if not titre:
            titre_tag = soup.find("h1")
            if titre_tag:
                titre = titre_tag.get_text(strip=True)
        
        print(f"📚 Titre : {'✅ Trouvé' if titre else '❌ Non trouvé'} - {titre if titre else 'N/A'}")

        # Auteur
        auteur_tag = soup.find("a", href=lambda x: x and "/auteur/" in x)
        auteur = auteur_tag.get_text(strip=True) if auteur_tag else None
        print(f"✍️ Auteur : {'✅ Trouvé' if auteur else '❌ Non trouvé'}")

        # Résumé avec le bon sélecteur
        resume_tag = soup.find("div", class_="livre_resume")
        resume = resume_tag.get_text(strip=True) if resume_tag else None
        print(f"📝 Résumé : {'✅ Trouvé' if resume else '❌ Non trouvé'}")

        # Note
        note_tag = soup.find("span", itemprop="ratingValue")
        note = float(note_tag.text.strip().replace(",", ".")) if note_tag else None
        print(f"⭐ Note : {note if note else '❌ Non trouvée'}")

        # Nombre de votes
        votes_tag = soup.find("span", itemprop="ratingCount")
        if votes_tag:
            votes_txt = votes_tag.text.strip().split()[0].replace(" ", "")
            nombre_votes = int(votes_txt)
        else:
            nombre_votes = None
        print(f"🗳️ Nombre de votes : {nombre_votes if nombre_votes else '❌ Non trouvé'}")

        # Répartition des notes (histogramme)
        repartition_notes = extraire_repartition_notes(soup)
        print(f"📊 Répartition des notes : {'✅ Trouvée' if repartition_notes else '❌ Non trouvée'}")

        # Extraction des critiques
        critiques = []
        
        # Chercher les conteneurs de critiques
        critiques_containers = soup.find_all("div", class_="post_con")
        
        print(f"💬 Recherche des critiques... {len(critiques_containers)} trouvées")
        
        for container in critiques_containers:
            try:
                critique_data = {}
                
                # Nom d'utilisateur - plusieurs approches améliorées
                utilisateur = None
                
                # Méthode 1 : lien vers monprofil.php
                user_link = container.find("a", href=lambda x: x and "/monprofil.php" in x)
                if user_link:
                    utilisateur = user_link.text.strip()
                
                # Méthode 2 : span avec itemprop="name" dans le contexte d'une critique
                if not utilisateur:
                    # Chercher spécifiquement dans la zone de l'auteur de la critique
                    name_spans = container.find_all("span", itemprop="name")
                    for span in name_spans:
                        # Vérifier que c'est bien dans le contexte d'un utilisateur (pas le titre du livre)
                        parent_context = span.parent
                        if parent_context:
                            # Si le span est dans un lien ou près d'un lien vers un profil
                            nearby_link = parent_context.find("a", href=lambda x: x and ("/monprofil.php" in x or "/membre/" in x))
                            if nearby_link or "user" in parent_context.get("class", []):
                                utilisateur = span.text.strip()
                                break
                            
                            # Ou si c'est dans une zone avec classe contenant "user", "auteur", "membre"
                            parent_classes = " ".join(parent_context.get("class", []))
                            if any(keyword in parent_classes.lower() for keyword in ["user", "auteur", "membre", "critique"]):
                                text_content = span.text.strip()
                                # Éviter les noms trop longs (probablement des titres)
                                if text_content and len(text_content) < 50:
                                    utilisateur = text_content
                                    break
                
                # Méthode 3 : chercher dans les liens avec des classes spécifiques
                if not utilisateur:
                    user_links = container.find_all("a", class_=lambda x: x and any(keyword in " ".join(x).lower() for keyword in ["user", "membre", "auteur", "lien", "croco"]))
                    for link in user_links:
                        text = link.text.strip()
                        if text and len(text) < 50:  # Nom d'utilisateur raisonnable
                            utilisateur = text
                            break
                
                # Méthode 4 : analyser les éléments avec attribut itemprop="author" 
                # (structure visible dans votre capture : <span itemprop="author"><span itemprop="name">CatF</span></span>)
                if not utilisateur:
                    author_spans = container.find_all("span", itemprop="author")
                    for span in author_spans:
                        # Chercher d'abord un span avec itemprop="name" à l'intérieur
                        name_span = span.find("span", itemprop="name")
                        if name_span:
                            utilisateur = name_span.text.strip()
                            break
                        
                        # Sinon chercher un lien
                        author_link = span.find("a")
                        if author_link:
                            utilisateur = author_link.text.strip()
                            break
                        else:
                            # Parfois le nom est directement dans le span
                            text = span.text.strip()
                            if text and len(text) < 50:
                                utilisateur = text
                                break
                
                if utilisateur:
                    critique_data["utilisateur"] = utilisateur
                
                # Date de la critique - plusieurs approches
                # Approche 1 : span avec style color:grey
                date_span = container.find("span", style=lambda x: x and "color:grey" in x)
                if date_span:
                    critique_data["date"] = date_span.text.strip()
                else:
                    # Approche 2 : chercher une date dans le texte (format français)
                    text_content = container.get_text()
                    date_pattern = r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}'
                    date_match = re.search(date_pattern, text_content, re.IGNORECASE)
                    if date_match:
                        critique_data["date"] = date_match.group()
                    else:
                        # Approche 3 : chercher dans les divs avec classe "entete_date"
                        date_div = container.find("div", class_="entete_date")
                        if date_div:
                            critique_data["date"] = date_div.text.strip()
                
                # Note de l'utilisateur (nombre d'étoiles) - utilisation de la fonction améliorée
                note_utilisateur = extraire_note_critique(container)
                if note_utilisateur:
                    critique_data["note_utilisateur"] = note_utilisateur
                
                # Texte de la critique
                # Chercher d'abord dans les divs spécifiques
                texte_critique = ""
                
                # Méthode 1 : chercher dans les divs sans classe ou avec certaines classes
                content_divs = container.find_all("div")
                for div in content_divs:
                    div_text = div.get_text(strip=True)
                    # Ignorer les divs qui contiennent des infos de métadonnées
                    if (div_text and len(div_text) > 50 and 
                        not any(word in div_text.lower() for word in ['profil', 'critique', 'note', 'étoile', 'commentaire'])):
                        if len(div_text) > len(texte_critique):
                            texte_critique = div_text
                
                # Méthode 2 : si pas trouvé, prendre le texte principal du container
                if not texte_critique:
                    full_text = container.get_text(separator=' ', strip=True)
                    # Nettoyer le texte en supprimant les métadonnées
                    lines = full_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if len(line) > 100:  # Prendre une ligne suffisamment longue
                            texte_critique = line
                            break
                
                if texte_critique:
                    critique_data["texte"] = texte_critique
                
                # Ajouter la critique si elle contient au moins un utilisateur
                if "utilisateur" in critique_data:
                    critiques.append(critique_data)
                    print(f"✅ Critique trouvée : {critique_data.get('utilisateur', 'Anonyme')} - {critique_data.get('date', 'Sans date')}")
                    
            except Exception as e:
                print(f"⚠️ Erreur lors de l'extraction d'une critique : {e}")
                continue
        
        print(f"💬 {len(critiques)} critiques extraites avec succès")

        # Structure des données complète
        data_livre = {
            "isbn": isbn,
            "titre": titre,
            "auteur": auteur,
            "resume_babelio": resume,
            "note_babelio": note,
            "nombre_votes_babelio": nombre_votes,
            "repartition_notes_babelio": repartition_notes,
            "critiques_babelio": critiques,
            "url_babelio": url,
            "date_extraction": datetime.now().isoformat(),
            "nombre_critiques": len(critiques)
        }

        return data_livre
        
    except Exception as e:
        print(f"❌ Erreur lors du scraping de la fiche : {e}")
        return None

def sauvegarder_json(donnees, nom_fichier="babelio_data.json"):
    """
    Sauvegarde les données extraites dans un fichier JSON
    """
    try:
        # Créer le dossier dans le même répertoire que le script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dossier = os.path.join(script_dir, "data_extraite")
        if not os.path.exists(dossier):
            os.makedirs(dossier)
        
        chemin_fichier = os.path.join(dossier, nom_fichier)
        
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Données sauvegardées dans : {chemin_fichier}")
        return chemin_fichier
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
        return None

def charger_json_existant(nom_fichier="babelio_data.json"):
    """
    Charge un fichier JSON existant ou retourne une liste vide
    """
    try:
        # Chercher le fichier dans le même répertoire que le script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        chemin_fichier = os.path.join(script_dir, "data_extraite", nom_fichier)
        if os.path.exists(chemin_fichier):
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"⚠️ Erreur lors du chargement du fichier existant : {e}")
        return []

def traiter_liste_isbn(liste_isbn, nom_fichier="babelio_data.json", delai=2):
    """
    Traite une liste d'ISBN et sauvegarde les résultats en JSON
    """
    print(f"🚀 Traitement de {len(liste_isbn)} ISBN...")
    
    # Charger les données existantes
    donnees_existantes = charger_json_existant(nom_fichier)
    isbn_deja_traites = {livre.get('isbn') for livre in donnees_existantes if isinstance(livre, dict)}
    
    resultats = donnees_existantes.copy()
    
    for i, isbn in enumerate(liste_isbn, 1):
        print(f"\n--- Traitement {i}/{len(liste_isbn)} : ISBN {isbn} ---")
        
        # Vérifier si l'ISBN a déjà été traité
        if isbn in isbn_deja_traites:
            print(f"⏭️ ISBN {isbn} déjà traité, passage au suivant")
            continue
        
        data_livre = chercher_babelio_par_isbn(isbn)
        
        if data_livre:
            resultats.append(data_livre)
            print(f"✅ Données ajoutées pour {data_livre.get('titre', 'Titre inconnu')}")
            
            # Sauvegarde intermédiaire toutes les 5 extractions
            if i % 5 == 0:
                sauvegarder_json(resultats, nom_fichier)
                print(f"💾 Sauvegarde intermédiaire effectuée ({i} livres traités)")
        else:
            # Ajouter une entrée pour signaler l'échec
            resultats.append({
                "isbn": isbn,
                "erreur": "Données non trouvées sur Babelio",
                "date_extraction": datetime.now().isoformat()
            })
            print(f"❌ Aucune donnée trouvée pour l'ISBN {isbn}")
        
        # Délai entre les requêtes pour éviter de surcharger le serveur
        if i < len(liste_isbn):
            print(f"⏳ Pause de {delai} secondes...")
            time.sleep(delai)
    
    # Sauvegarde finale
    chemin_final = sauvegarder_json(resultats, nom_fichier)
    
    # Statistiques finales
    livres_avec_donnees = sum(1 for livre in resultats if isinstance(livre, dict) and 'titre' in livre)
    livres_avec_erreur = sum(1 for livre in resultats if isinstance(livre, dict) and 'erreur' in livre)
    
    print(f"\n📊 RÉSUMÉ FINAL :")
    print(f"📚 Livres avec données complètes : {livres_avec_donnees}")
    print(f"❌ Livres avec erreurs : {livres_avec_erreur}")
    print(f"📁 Fichier de sauvegarde : {chemin_final}")
    
    return resultats

def afficher_statistiques_json(nom_fichier="babelio_data.json"):
    """
    Affiche des statistiques sur les données JSON
    """
    donnees = charger_json_existant(nom_fichier)
    
    if not donnees:
        print("❌ Aucune donnée trouvée")
        return
    
    print(f"\n📊 STATISTIQUES DU FICHIER {nom_fichier} :")
    print("=" * 60)
    
    total_livres = len(donnees)
    livres_avec_donnees = sum(1 for livre in donnees if isinstance(livre, dict) and 'titre' in livre)
    livres_avec_erreur = sum(1 for livre in donnees if isinstance(livre, dict) and 'erreur' in livre)
    
    print(f"📚 Total d'entrées : {total_livres}")
    print(f"✅ Livres avec données : {livres_avec_donnees}")
    print(f"❌ Livres avec erreurs : {livres_avec_erreur}")
    
    if livres_avec_donnees > 0:
        # Statistiques sur les notes
        notes = [livre.get('note_babelio') for livre in donnees if isinstance(livre, dict) and livre.get('note_babelio')]
        if notes:
            note_moyenne = sum(notes) / len(notes)
            print(f"⭐ Note moyenne : {note_moyenne:.2f}")
            print(f"⭐ Note min/max : {min(notes):.1f} / {max(notes):.1f}")
        
        # Statistiques sur les critiques
        total_critiques = sum(livre.get('nombre_critiques', 0) for livre in donnees if isinstance(livre, dict))
        print(f"💬 Total de critiques extraites : {total_critiques}")
        
        if livres_avec_donnees > 0:
            moyenne_critiques = total_critiques / livres_avec_donnees
            print(f"💬 Moyenne de critiques par livre : {moyenne_critiques:.1f}")

def main():
    """
    Fonction principale avec menu interactif
    """
    print("=== 🔍 Scraper Babelio - Version JSON ===")
    print("1. Rechercher un ISBN unique")
    print("2. Traiter un fichier CSV d'ISBN")
    print("3. Afficher les statistiques du fichier JSON")
    print("4. Quitter")
    
    while True:
        choix = input("\nChoisissez une option (1-4) : ").strip()
        
        if choix == "1":
            # Recherche d'un ISBN unique
            isbn = input("Veuillez entrer un ISBN : ").strip()
            
            if not isbn:
                print("❌ Aucun ISBN saisi")
                continue
            
            data_livre = chercher_babelio_par_isbn(isbn)
            
            if data_livre:
                print(f"\n✅ Informations trouvées pour l'ISBN {isbn}")
                
                # Sauvegarder en JSON
                nom_fichier = f"livre_{isbn}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                sauvegarder_json([data_livre], nom_fichier)
                
                # Affichage résumé
                print(f"📚 Titre : {data_livre.get('titre', 'N/A')}")
                print(f"✍️ Auteur : {data_livre.get('auteur', 'N/A')}")
                print(f"⭐ Note : {data_livre.get('note_babelio', 'N/A')}")
                print(f"💬 Critiques : {data_livre.get('nombre_critiques', 0)}")
                
            else:
                print(f"⚠️ Aucune information trouvée pour l'ISBN {isbn}")
        
        elif choix == "2":
            # Traitement d'un fichier CSV
            fichier_csv = input("Chemin vers le fichier CSV : ").strip()
            
            if not os.path.exists(fichier_csv):
                print("❌ Fichier introuvable")
                continue
            
            try:
                liste_isbn = extraire_isbn_13_by_csv(fichier_csv)
                print(f"📋 {len(liste_isbn)} ISBN trouvés dans le fichier")
                
                nom_fichier = input("Nom du fichier JSON de sortie (par défaut: babelio_data.json) : ").strip()
                if not nom_fichier:
                    nom_fichier = "babelio_data.json"
                
                delai = input("Délai entre les requêtes en secondes (par défaut: 2) : ").strip()
                try:
                    delai = int(delai) if delai else 2
                except ValueError:
                    delai = 2
                
                traiter_liste_isbn(liste_isbn, nom_fichier, delai)
                
            except Exception as e:
                print(f"❌ Erreur lors du traitement du fichier CSV : {e}")
        
        elif choix == "3":
            # Affichage des statistiques
            nom_fichier = input("Nom du fichier JSON (par défaut: babelio_data.json) : ").strip()
            if not nom_fichier:
                nom_fichier = "babelio_data.json"
            
            afficher_statistiques_json(nom_fichier)
        
        elif choix == "4":
            print("👋 Au revoir !")
            break
        
        else:
            print("❌ Option invalide, veuillez choisir entre 1 et 4")

if __name__ == "__main__":
    main()