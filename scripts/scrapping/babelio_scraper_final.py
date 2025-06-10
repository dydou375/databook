import requests
from bs4 import BeautifulSoup
import json
import time
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

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
        return scraper_fiche_babelio(lien_fiche)
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche : {e}")
        return None

def scraper_fiche_babelio(url):
    """
    Extrait les informations d'une fiche livre Babelio
    """
    print(f"📖 Extraction des données de : {url}")
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")

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

        # Extraction des critiques
        critiques = []
        
        # Chercher les conteneurs de critiques
        critiques_containers = soup.find_all("div", class_="post_con")
        
        print(f"💬 Recherche des critiques... {len(critiques_containers)} trouvées")
        
        for container in critiques_containers:
            try:
                critique_data = {}
                
                # Nom d'utilisateur - plusieurs approches
                user_link = container.find("a", href=lambda x: x and "/monprofil.php" in x)
                if user_link:
                    critique_data["utilisateur"] = user_link.text.strip()
                else:
                    # Alternative : chercher dans les spans avec itemprop="author"
                    author_span = container.find("span", itemprop="author")
                    if author_span:
                        author_link = author_span.find("a")
                        if author_link:
                            critique_data["utilisateur"] = author_link.text.strip()
                
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
                
                # Note de l'utilisateur (nombre d'étoiles)
                # Chercher les étoiles dans les images ou spans
                stars = container.find_all("img", src=lambda x: x and "etoile" in x)
                if stars:
                    critique_data["note_utilisateur"] = len(stars)
                else:
                    # Alternative : chercher dans les spans avec des classes d'étoiles
                    star_spans = container.find_all("span", class_=lambda x: x and "star" in x)
                    if star_spans:
                        critique_data["note_utilisateur"] = len(star_spans)
                
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

        return {
            "resume_babelio": resume,
            "note_babelio": note,
            "nombre_votes_babelio": nombre_votes,
            "critiques_babelio": critiques,
            "url_babelio": url
        }
        
    except Exception as e:
        print(f"❌ Erreur lors du scraping de la fiche : {e}")
        return None

def main():
    """
    Fonction principale
    """
    print("=== Scraper Babelio ===")
    
    # Demander à l'utilisateur de saisir un ISBN
    isbn = input("Veuillez entrer un ISBN : ").strip()
    
    if not isbn:
        print("❌ Aucun ISBN saisi")
        return
    
    # Rechercher l'ISBN saisi par l'utilisateur
    data_babelio = chercher_babelio_par_isbn(isbn)
    
    if data_babelio:
        print(f"\n✅ Informations trouvées pour l'ISBN {isbn} :")
        print("=" * 60)
        
        # Affichage des informations générales
        print(f"📊 URL : {data_babelio.get('url_babelio', 'N/A')}")
        print(f"⭐ Note moyenne : {data_babelio.get('note_babelio', 'N/A')}")
        print(f"🗳️ Nombre de votes : {data_babelio.get('nombre_votes_babelio', 'N/A')}")
        
        # Affichage du résumé
        resume = data_babelio.get('resume_babelio')
        if resume:
            print(f"\n📝 Résumé :")
            print("-" * 40)
            if len(resume) > 300:
                print(f"{resume[:300]}...")
            else:
                print(resume)
        
        # Affichage des critiques
        critiques = data_babelio.get('critiques_babelio', [])
        if critiques:
            print(f"\n💬 Critiques des utilisateurs ({len(critiques)}) :")
            print("=" * 60)
            
            for i, critique in enumerate(critiques, 1):
                print(f"\n--- Critique #{i} ---")
                print(f"👤 Utilisateur : {critique.get('utilisateur', 'Anonyme')}")
                print(f"📅 Date : {critique.get('date', 'N/A')}")
                
                note_user = critique.get('note_utilisateur')
                if note_user:
                    print(f"⭐ Note : {note_user}/5 {'★' * note_user}{'☆' * (5-note_user)}")
                
                texte = critique.get('texte', '')
                if texte:
                    print(f"💭 Critique :")
                    if len(texte) > 200:
                        print(f"   {texte[:200]}...")
                    else:
                        print(f"   {texte}")
                print()
        else:
            print("\n💬 Aucune critique trouvée")
            
    else:
        print(f"⚠️ Aucune information trouvée pour l'ISBN {isbn}")

if __name__ == "__main__":
    main() 