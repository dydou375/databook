import requests
from bs4 import BeautifulSoup
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

def test_extraction_critiques(url):
    """
    Test spécifique pour l'extraction des critiques
    """
    print(f"🧪 Test d'extraction des critiques sur : {url}")
    
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.content, "html.parser")
    
    # Chercher les conteneurs de critiques
    critiques_containers = soup.find_all("div", class_="post_con")
    print(f"📦 {len(critiques_containers)} conteneurs de critiques trouvés")
    
    for i, container in enumerate(critiques_containers[:3], 1):  # Limiter à 3 pour le test
        print(f"\n--- Test Critique #{i} ---")
        
        # Test extraction utilisateur
        print("🔍 Recherche utilisateur...")
        user_link = container.find("a", href=lambda x: x and "/monprofil.php" in x)
        if user_link:
            print(f"✅ Utilisateur trouvé : '{user_link.text.strip()}'")
        else:
            print("❌ Pas d'utilisateur avec /monprofil.php")
            # Test alternative
            author_span = container.find("span", itemprop="author")
            if author_span:
                author_link = author_span.find("a")
                if author_link:
                    print(f"✅ Utilisateur alternatif trouvé : '{author_link.text.strip()}'")
                else:
                    print("❌ Pas de lien dans span author")
            else:
                print("❌ Pas de span avec itemprop='author'")
        
        # Test extraction date
        print("🔍 Recherche date...")
        date_span = container.find("span", style=lambda x: x and "color:grey" in x)
        if date_span:
            print(f"✅ Date trouvée (style) : '{date_span.text.strip()}'")
        else:
            print("❌ Pas de date avec style color:grey")
            # Test avec regex
            text_content = container.get_text()
            date_pattern = r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}'
            date_match = re.search(date_pattern, text_content, re.IGNORECASE)
            if date_match:
                print(f"✅ Date trouvée (regex) : '{date_match.group()}'")
            else:
                print("❌ Pas de date trouvée avec regex")
                # Test classe entete_date
                date_div = container.find("div", class_="entete_date")
                if date_div:
                    print(f"✅ Date trouvée (classe) : '{date_div.text.strip()}'")
                else:
                    print("❌ Pas de date avec classe entete_date")
        
        # Test extraction note
        print("🔍 Recherche note...")
        stars = container.find_all("img", src=lambda x: x and "etoile" in x)
        if stars:
            print(f"✅ Note trouvée : {len(stars)}/5 étoiles")
        else:
            print("❌ Pas d'étoiles trouvées")
        
        # Afficher le HTML pour debug
        print("🔍 HTML du conteneur (premiers 300 caractères) :")
        print(str(container)[:300] + "...")
        print("-" * 50)

if __name__ == "__main__":
    # Test avec l'URL de Divergente
    url_test = "https://www.babelio.com/livres/Roth-Divergente-tome-1/295647"
    test_extraction_critiques(url_test) 