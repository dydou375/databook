#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier l'extraction du titre avec les nouveaux sélecteurs
"""

import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

def tester_extraction_titre(url_babelio):
    """
    Teste l'extraction du titre avec différents sélecteurs
    """
    print(f"🔍 Test d'extraction du titre pour : {url_babelio}")
    
    try:
        res = requests.get(url_babelio, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        
        print(f"\n📝 Tests des différents sélecteurs :")
        print("=" * 50)
        
        # Méthode 1 : h1 avec classe livre_header_con_titre
        titre_tag = soup.find("h1", class_="livre_header_con_titre")
        if titre_tag:
            titre1 = titre_tag.get_text(strip=True)
            print(f"✅ Méthode 1 (h1.livre_header_con_titre) : '{titre1}'")
        else:
            print(f"❌ Méthode 1 (h1.livre_header_con_titre) : Non trouvé")
        
        # Méthode 2 : lien avec itemprop="name"
        titre_tag = soup.find("a", itemprop="name")
        if titre_tag:
            titre2 = titre_tag.get_text(strip=True)
            print(f"✅ Méthode 2 (a[itemprop='name']) : '{titre2}'")
        else:
            print(f"❌ Méthode 2 (a[itemprop='name']) : Non trouvé")
        
        # Méthode 3 : span avec itemprop="name"
        titre_tag = soup.find("span", itemprop="name")
        if titre_tag:
            titre3 = titre_tag.get_text(strip=True)
            print(f"✅ Méthode 3 (span[itemprop='name']) : '{titre3}'")
        else:
            print(f"❌ Méthode 3 (span[itemprop='name']) : Non trouvé")
        
        # Méthode 4 : h1 général
        titre_tag = soup.find("h1")
        if titre_tag:
            titre4 = titre_tag.get_text(strip=True)
            print(f"✅ Méthode 4 (h1 général) : '{titre4}'")
        else:
            print(f"❌ Méthode 4 (h1 général) : Non trouvé")
        
        # Méthode bonus : chercher dans les éléments avec "name" dans les attributs
        print(f"\n🔍 Recherche bonus - éléments avec 'name' :")
        elements_name = soup.find_all(attrs={"itemprop": "name"})
        for i, elem in enumerate(elements_name):
            print(f"  📌 Élément {i+1} ({elem.name}) : '{elem.get_text(strip=True)}'")
        
        # Test de la logique finale (comme dans le script principal)
        print(f"\n🎯 RÉSULTAT FINAL (logique du script) :")
        titre_final = None
        
        # Méthode 1 : h1 avec itemprop="name" (structure principale)
        titre_tag = soup.find("h1", itemprop="name")
        if titre_tag:
            # Chercher le lien à l'intérieur du h1
            lien_titre = titre_tag.find("a")
            if lien_titre:
                titre_final = lien_titre.get_text(strip=True)
            else:
                titre_final = titre_tag.get_text(strip=True)
        
        # Méthode 2 : lien direct avec href contenant le titre
        if not titre_final:
            liens_livre = soup.find_all("a", href=lambda x: x and "/livres/" in x)
            for lien in liens_livre:
                texte_lien = lien.get_text(strip=True)
                # Prendre le premier lien non vide qui semble être un titre (pas trop long)
                if texte_lien and len(texte_lien) < 100 and not any(mot in texte_lien.lower() for mot in ['critique', 'citation', 'forum', 'auteur']):
                    titre_final = texte_lien
                    break
        
        # Méthode 3 : h1 dans la zone livre_header_con
        if not titre_final:
            div_header = soup.find("div", class_="livre_header_con")
            if div_header:
                titre_tag = div_header.find("h1")
                if titre_tag:
                    lien_titre = titre_tag.find("a")
                    if lien_titre:
                        titre_final = lien_titre.get_text(strip=True)
                    else:
                        titre_final = titre_tag.get_text(strip=True)
                
        # Méthode 4 : h1 général comme fallback
        if not titre_final:
            titre_tag = soup.find("h1")
            if titre_tag:
                titre_final = titre_tag.get_text(strip=True)
        
        if titre_final:
            print(f"🎉 TITRE EXTRAIT : '{titre_final}'")
        else:
            print(f"❌ AUCUN TITRE TROUVÉ")
            
        return titre_final
        
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        return None

if __name__ == "__main__":
    print("=== 🧪 Test d'extraction de titre Babelio ===")
    
    # URL de test (celle de votre capture)
    url_test = "https://www.babelio.com/livres/Cook-Mutation/23159"
    
    titre = tester_extraction_titre(url_test)
    
    if titre:
        print(f"\n✅ SUCCESS : Le titre '{titre}' a été extrait avec succès !")
    else:
        print(f"\n❌ ÉCHEC : Impossible d'extraire le titre") 