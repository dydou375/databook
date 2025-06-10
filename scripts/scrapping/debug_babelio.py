import requests
from bs4 import BeautifulSoup
import time

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

def chercher_babelio_par_isbn_debug(isbn13):
    url = "https://www.babelio.com/recherche.php"
    print(f"🌐 URL de recherche : {url}")
    
    # Données du formulaire POST
    data = {
        'Recherche': isbn13,
        'recherche': ''
    }
    
    print(f"📨 Données POST : {data}")
    
    res = requests.post(url, headers=headers, data=data)
    print(f"📡 Code de statut HTTP : {res.status_code}")
    
    soup = BeautifulSoup(res.content, "html.parser")
    
    # Debug : afficher le titre de la page
    titre_page = soup.find("title")
    if titre_page:
        print(f"📄 Titre de la page : {titre_page.text}")
    
    # Sauvegarder le HTML pour analyse
    with open("debug_recherche.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    print("💾 HTML sauvegardé dans debug_recherche.html")
    
    # Chercher tous les liens <a> avec différentes approches
    print("🔍 Analyse de tous les liens de la page...")
    
    # Tous les liens <a>
    tous_liens = soup.find_all("a")
    print(f"🔗 Nombre total de liens : {len(tous_liens)}")
    
    # Afficher les 10 premiers liens avec leurs classes
    print("📋 Premiers liens trouvés :")
    for i, lien in enumerate(tous_liens[:10]):
        href = lien.get('href', 'Pas de href')
        classe = lien.get('class', 'Pas de classe')
        texte = lien.text.strip()[:30]
        print(f"  {i+1}. href: {href}, class: {classe}, texte: '{texte}'")
    
    # Essayer différents sélecteurs pour trouver le lien
    print("\n🔍 Recherche du lien vers la fiche...")
    
    # Essai 1 : avec class="titre1"
    lien = soup.find("a", class_="titre1")
    if lien:
        print(f"✅ Lien trouvé avec class='titre1' : {lien.get('href')}")
        lien_fiche = "https://www.babelio.com" + lien["href"]
        return scraper_fiche_babelio(lien_fiche)
    else:
        print("❌ Aucun lien avec class='titre1'")
    
    # Essai 2 : avec class="titre_lien"
    lien = soup.find("a", class_="titre_lien")
    if lien:
        print(f"✅ Lien trouvé avec class='titre_lien' : {lien.get('href')}")
        lien_fiche = "https://www.babelio.com" + lien["href"]
        return scraper_fiche_babelio(lien_fiche)
    else:
        print("❌ Aucun lien avec class='titre_lien'")
    
    # Essai 3 : chercher des liens contenant "livres"
    liens_livres = [l for l in tous_liens if l.get('href') and '/livres/' in l.get('href')]
    if liens_livres:
        print(f"🔗 Trouvé {len(liens_livres)} liens vers des livres")
        for i, lien in enumerate(liens_livres[:3]):
            print(f"  Lien {i+1}: {lien.get('href')} - Texte: '{lien.text.strip()[:50]}'")
        
        # Prendre le premier lien trouvé
        premier_lien = liens_livres[0]
        lien_fiche = "https://www.babelio.com" + premier_lien["href"]
        print(f"🎯 Utilisation du premier lien : {lien_fiche}")
        return scraper_fiche_babelio(lien_fiche)
    else:
        print("❌ Aucun lien vers /livres/ trouvé")
    
    # Essai 4 : chercher dans le contenu textuel
    contenu_page = soup.get_text()
    if "Aucun résultat" in contenu_page or "No result" in contenu_page:
        print("⚠️ Aucun résultat trouvé pour cette recherche")
    
    # Si aucun lien n'est trouvé
    print("❌ Aucun lien vers une fiche livre trouvé")
    print("📝 Contenu de la page (premiers 1000 caractères) :")
    print(soup.text[:1000])
    
    return None

def scraper_fiche_babelio(url):
    print(f"📖 Scraping de la fiche : {url}")
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")

    # Debug : afficher le titre de la page
    titre_page = soup.find("title")
    if titre_page:
        print(f"📄 Titre de la fiche : {titre_page.text}")

    # Chercher le résumé avec le bon sélecteur
    resume_tag = soup.find("div", class_="livre_resume")
    resume = resume_tag.get_text(strip=True) if resume_tag else None
    print(f"📝 Résumé trouvé : {'Oui' if resume else 'Non'}")
    if resume:
        print(f"📝 Début du résumé : {resume[:100]}...")

    note_tag = soup.find("span", itemprop="ratingValue")
    note = float(note_tag.text.strip().replace(",", ".")) if note_tag else None
    print(f"⭐ Note trouvée : {note}")

    votes_tag = soup.find("span", itemprop="ratingCount")
    if votes_tag:
        votes_txt = votes_tag.text.strip().split()[0].replace(" ", "")
        nombre_votes = int(votes_txt)
    else:
        nombre_votes = None
    print(f"🗳️ Nombre de votes : {nombre_votes}")

    return {
        "resume_babelio": resume,
        "note_babelio": note,
        "nombre_votes_babelio": nombre_votes,
        "url_babelio": url
    }

# Test avec un ISBN
if __name__ == "__main__":
    # Demander à l'utilisateur de saisir un ISBN
    isbn = input("Veuillez entrer un ISBN : ").strip()
    
    # Rechercher l'ISBN saisi par l'utilisateur
    print(f"🔎 Recherche ISBN {isbn} sur Babelio...")
    data_babelio = chercher_babelio_par_isbn_debug(isbn)
    if data_babelio:
        print(f"✅ Infos Babelio pour ISBN {isbn} :")
        for key, value in data_babelio.items():
            print(f"  {key}: {value}")
    else:
        print(f"⚠️ Livre avec ISBN {isbn} non trouvé sur Babelio.") 