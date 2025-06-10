import requests
from bs4 import BeautifulSoup
import json
import time

headers = {"User-Agent": "Mozilla/5.0"}

def chercher_babelio_par_isbn(isbn13):
    url = f"https://www.babelio.com/recherche.php?q={isbn13}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")

    # Cherche un lien vers la fiche du livre
    lien = soup.find("a", class_="titre_lien")
    if not lien:
        return None

    lien_fiche = "https://www.babelio.com" + lien["href"]
    return scraper_fiche_babelio(lien_fiche)

def scraper_fiche_babelio(url):
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")

    # Résumé
    resume_tag = soup.find("div", class_="full-content")
    resume = resume_tag.get_text(strip=True) if resume_tag else None

    # Note moyenne
    note_tag = soup.find("span", itemprop="ratingValue")
    note = float(note_tag.text.strip().replace(",", ".")) if note_tag else None

    # Nombre de votes
    votes_tag = soup.find("span", itemprop="ratingCount")
    nombre_votes = int(votes_tag.text.strip().replace(" notes", "").replace(" ", "")) if votes_tag else None

    return {
        "resume_babelio": resume,
        "note_babelio": note,
        "nombre_votes_babelio": nombre_votes,
        "url_babelio": url
    }

# Exemple d'objet JSON existant
livres = [
    {
        "titre": "Saint Thomas Aquinas: The person and his work",
        "auteurs": ["Jean-Pierre Torrell"],
        "langue": "en",
        "resume": "Highly acclaimed ...",
        "isbn_10": "0813214238",
        "isbn_13": "9780813214238",
        "edition_keys": ["OL19084925M"],
        "note": 5,
        "nombre_votes": 1
    }
]

# Enrichir chaque livre
for livre in livres:
    isbn = livre.get("isbn_13")
    isbn_test = "9782092544396"
    if isbn:
        print(f"Recherche ISBN {isbn_test}...")
        data_babelio = chercher_babelio_par_isbn(isbn_test)
        if data_babelio:
            livre.update(data_babelio)
        else:
            print("→ Livre non trouvé sur Babelio.")
        time.sleep(1.5)  # respect du serveur

# Afficher le résultat enrichi
print(json.dumps(livres, indent=2, ensure_ascii=False))
