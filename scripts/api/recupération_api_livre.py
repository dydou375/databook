import requests
import time
import random
import json
import os
from urllib.parse import quote_plus
from tqdm import tqdm

categories = [
    {"fr": "Fiction", "en": "Fiction"},
    {"fr": "Science", "en": "Science"},
    {"fr": "Mathématiques", "en": "Mathematics"},
    {"fr": "Technologie", "en": "Technology"},
    {"fr": "Informatique", "en": "Computers"},
    {"fr": "Histoire", "en": "History"},
    {"fr": "Biographies", "en": "Biography"},
    {"fr": "Philosophie", "en": "Philosophy"},
    {"fr": "Psychologie", "en": "Psychology"},
    {"fr": "Religion", "en": "Religion"},
    {"fr": "Art", "en": "Art"},
    {"fr": "Musique", "en": "Music"},
    {"fr": "Arts du spectacle", "en": "Performing Arts"},
    {"fr": "Poésie", "en": "Poetry"},
    {"fr": "Théâtre", "en": "Drama"},
    {"fr": "Bandes dessinées", "en": "Comics"},
    {"fr": "Romans jeunesse", "en": "Juvenile Fiction"},
    {"fr": "Documentaires jeunesse", "en": "Juvenile Nonfiction"},
    {"fr": "Littérature", "en": "Literature"},
    {"fr": "Sciences politiques", "en": "Political Science"},
    {"fr": "Sciences sociales", "en": "Social Science"},
    {"fr": "Science-fiction", "en": "Science Fiction"},
    {"fr": "Fantastique", "en": "Fantasy"},
    {"fr": "Horreur", "en": "Horror"},
    {"fr": "Policier", "en": "Mystery"},
    {"fr": "Thriller", "en": "Thriller"},
    {"fr": "Romance", "en": "Romance"},
    {"fr": "Aventure", "en": "Adventure"},
    {"fr": "Référence", "en": "Reference"}
]

max_results = 500  # Nombre total de livres souhaités par catégorie
max_api_results = 40  # Limite de l'API Google Books par requête

# Crée un dossier pour stocker les fichiers JSON
os.makedirs("livres_json", exist_ok=True)

for cat in categories:
    sujet = cat["en"]
    livres_json = []
    print(f"=== Livres pour le sujet : {sujet} (en) ===")

    total_recup = 0
    for start in range(0, max_results, max_api_results):
        url = (
            f"https://www.googleapis.com/books/v1/volumes"
            f"?q=subject:{quote_plus(sujet)}"
            f"&maxResults={min(max_api_results, max_results - total_recup)}"
            f"&startIndex={start}"
        )
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            livres = data.get("items", [])
            if not livres:
                break  # Plus de livres à récupérer
            for livre in tqdm(livres, desc=f"Livres pour {sujet}", unit="livre", leave=False):
                info = livre.get("volumeInfo", {})
                titre = info.get("title", "Titre inconnu")
                auteurs = info.get("authors", ["Auteur inconnu"])
                langue_livre = info.get("language", "non précisée")
                notes = info.get("averageRating", None)
                nbr_vote = info.get("ratingsCount", None)
                resume = info.get("description", "description non présente")
                genres_google = info.get("categories", [])
                identifiers = info.get("industryIdentifiers", [])
                isbn_10 = next((id["identifier"] for id in identifiers if id["type"] == "ISBN_10"), "N/A")
                isbn_13 = next((id["identifier"] for id in identifiers if id["type"] == "ISBN_13"), "N/A")
                isbn = isbn_13 if isbn_13 != "N/A" else (isbn_10 if isbn_10 != "N/A" else "N/A")
                edition_keys = []
                if isbn != "N/A":
                    ol_url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
                    ol_res = requests.get(ol_url)
                    if ol_res.status_code == 200:
                        ol_data = ol_res.json()
                        key = f"ISBN:{isbn}"
                        if key in ol_data:
                            edition_keys = ol_data[key].get("identifiers", {}).get("openlibrary", [])
                elif titre != "Titre inconnu" and auteurs[0] != "Auteur inconnu":
                    q_title = quote_plus(titre)
                    q_author = quote_plus(auteurs[0])
                    ol_url = f"https://openlibrary.org/search.json?title={q_title}&author={q_author}"
                    ol_res = requests.get(ol_url)
                    if ol_res.status_code == 200:
                        ol_data = ol_res.json()
                        docs = ol_data.get("docs", [])
                        if docs:
                            edition_keys = docs[0].get("edition_key", [])
                livres_json.append({
                    "titre": titre,
                    "auteurs": auteurs,
                    "langue": langue_livre,
                    "resume": resume,
                    "isbn_10": isbn_10,
                    "isbn_13": isbn_13,
                    "edition_keys": edition_keys,
                    "note": notes,
                    "nombre_votes": nbr_vote,
                    "genres_google": genres_google,
                    "tous_les_genres": genres_google
                })
                total_recup += 1
                if total_recup >= max_results:
                    break
            if total_recup >= max_results:
                break
        else:
            print(f"Erreur lors de la récupération pour {sujet} (code {response.status_code})")
            break

    nom_fichier = f"livres_json/{sujet.replace(' ', '_').lower()}.json"
    with open(nom_fichier, "w", encoding="utf-8") as f:
        json.dump(livres_json, f, ensure_ascii=False, indent=2)
    print(f"Fichier créé : {nom_fichier} ({len(livres_json)} livres pour la catégorie '{sujet}')\n")
    time.sleep(random.uniform(2, 5))