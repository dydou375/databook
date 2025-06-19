import requests
import time
import random
import json
import os
from urllib.parse import quote_plus
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RecuperateurLivresAmeliore:
    def __init__(self):
        self.max_results_par_categorie = 1000  # Augmenté !
        self.max_api_results = 40
        self.dossier_output = "livres_json_ameliore"
        self.stats = {"total_recuperes": 0, "erreurs": 0}
        
        # Catégories étendues avec plus de variations
        self.categories_etendues = [
            # Littérature et Fiction
            {"fr": "Fiction", "en": "Fiction", "variations": ["fiction", "novel", "novels", "literature"]},
            {"fr": "Fiction contemporaine", "en": "Contemporary Fiction", "variations": ["contemporary", "modern fiction"]},
            {"fr": "Fiction historique", "en": "Historical Fiction", "variations": ["historical novel", "period fiction"]},
            {"fr": "Fiction littéraire", "en": "Literary Fiction", "variations": ["literary", "literature"]},
            
            # Sciences et Technologie
            {"fr": "Science", "en": "Science", "variations": ["science", "scientific", "research"]},
            {"fr": "Physique", "en": "Physics", "variations": ["physics", "quantum", "mechanics"]},
            {"fr": "Chimie", "en": "Chemistry", "variations": ["chemistry", "chemical", "biochemistry"]},
            {"fr": "Biologie", "en": "Biology", "variations": ["biology", "life science", "genetics"]},
            {"fr": "Mathématiques", "en": "Mathematics", "variations": ["mathematics", "math", "algebra", "geometry"]},
            {"fr": "Informatique", "en": "Computers", "variations": ["computers", "programming", "software", "technology"]},
            {"fr": "Intelligence Artificielle", "en": "Artificial Intelligence", "variations": ["AI", "machine learning", "deep learning"]},
            {"fr": "Données", "en": "Data Science", "variations": ["data science", "big data", "analytics"]},
            
            # Histoire et Biographies
            {"fr": "Histoire", "en": "History", "variations": ["history", "historical", "past"]},
            {"fr": "Histoire mondiale", "en": "World History", "variations": ["world history", "global history"]},
            {"fr": "Histoire de France", "en": "French History", "variations": ["france history", "french history"]},
            {"fr": "Biographies", "en": "Biography", "variations": ["biography", "autobiography", "memoir"]},
            {"fr": "Mémoires", "en": "Memoirs", "variations": ["memoirs", "personal narrative"]},
            
            # Philosophie et Psychologie
            {"fr": "Philosophie", "en": "Philosophy", "variations": ["philosophy", "philosophical", "ethics"]},
            {"fr": "Psychologie", "en": "Psychology", "variations": ["psychology", "mental health", "cognitive"]},
            {"fr": "Développement personnel", "en": "Self Help", "variations": ["self help", "personal development", "motivation"]},
            
            # Arts et Culture
            {"fr": "Art", "en": "Art", "variations": ["art", "painting", "sculpture", "visual arts"]},
            {"fr": "Musique", "en": "Music", "variations": ["music", "musical", "composer", "instruments"]},
            {"fr": "Photographie", "en": "Photography", "variations": ["photography", "photo", "camera"]},
            {"fr": "Design", "en": "Design", "variations": ["design", "graphic design", "web design"]},
            
            # Genres populaires
            {"fr": "Science-fiction", "en": "Science Fiction", "variations": ["science fiction", "sci-fi", "space", "future"]},
            {"fr": "Fantasy", "en": "Fantasy", "variations": ["fantasy", "magic", "dragons", "epic fantasy"]},
            {"fr": "Thriller", "en": "Thriller", "variations": ["thriller", "suspense", "mystery"]},
            {"fr": "Policier", "en": "Mystery", "variations": ["mystery", "detective", "crime", "murder"]},
            {"fr": "Romance", "en": "Romance", "variations": ["romance", "love story", "romantic"]},
            {"fr": "Horreur", "en": "Horror", "variations": ["horror", "scary", "supernatural", "gothic"]},
            {"fr": "Aventure", "en": "Adventure", "variations": ["adventure", "action", "exploration"]},
            
            # Jeunesse et Education
            {"fr": "Jeunesse", "en": "Juvenile Fiction", "variations": ["children", "kids", "young readers"]},
            {"fr": "Young Adult", "en": "Young Adult Fiction", "variations": ["young adult", "teen", "teenager"]},
            {"fr": "Education", "en": "Education", "variations": ["education", "teaching", "learning"]},
            
            # Vie pratique
            {"fr": "Cuisine", "en": "Cooking", "variations": ["cooking", "recipes", "food", "chef"]},
            {"fr": "Santé", "en": "Health", "variations": ["health", "wellness", "fitness", "medicine"]},
            {"fr": "Voyage", "en": "Travel", "variations": ["travel", "tourism", "guide", "destination"]},
            {"fr": "Business", "en": "Business", "variations": ["business", "economics", "finance", "management"]},
            {"fr": "Sport", "en": "Sports", "variations": ["sports", "athletics", "fitness", "exercise"]},
            
            # Spécialisés
            {"fr": "Religion", "en": "Religion", "variations": ["religion", "spirituality", "faith"]},
            {"fr": "Politique", "en": "Political Science", "variations": ["politics", "government", "democracy"]},
            {"fr": "Droit", "en": "Law", "variations": ["law", "legal", "justice", "court"]},
            {"fr": "Médecine", "en": "Medical", "variations": ["medical", "medicine", "doctor", "health"]},
            {"fr": "Nature", "en": "Nature", "variations": ["nature", "environment", "ecology", "wildlife"]},
        ]
        
        os.makedirs(self.dossier_output, exist_ok=True)

    def recuperer_google_books(self, terme_recherche, max_results=1000):
        """Récupère des livres via Google Books API avec un terme de recherche"""
        livres = []
        total_recup = 0
        
        for start in range(0, max_results, self.max_api_results):
            if total_recup >= max_results:
                break
                
            url = (
                f"https://www.googleapis.com/books/v1/volumes"
                f"?q={quote_plus(terme_recherche)}"
                f"&maxResults={min(self.max_api_results, max_results - total_recup)}"
                f"&startIndex={start}"
                f"&printType=books"
                f"&langRestrict=fr"  # Priorité au français
            )
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    
                    if not items:
                        logging.info(f"Plus de résultats pour '{terme_recherche}' à partir de {start}")
                        break
                    
                    for livre in items:
                        livre_data = self.extraire_donnees_google(livre, terme_recherche)
                        if livre_data:
                            livres.append(livre_data)
                            total_recup += 1
                    
                    logging.info(f"Récupéré {len(items)} livres pour '{terme_recherche}' (total: {total_recup})")
                    
                else:
                    logging.error(f"Erreur Google Books API: {response.status_code} pour '{terme_recherche}'")
                    self.stats["erreurs"] += 1
                    
            except Exception as e:
                logging.error(f"Exception lors de la récupération Google Books: {e}")
                self.stats["erreurs"] += 1
            
            # Pause pour éviter les limites de taux
            time.sleep(random.uniform(1, 3))
        
        return livres

    def recuperer_open_library(self, terme_recherche, max_results=500):
        """Récupère des livres via Open Library API"""
        livres = []
        limite_par_page = 100
        
        for page in range(1, (max_results // limite_par_page) + 2):
            url = f"https://openlibrary.org/search.json?q={quote_plus(terme_recherche)}&limit={limite_par_page}&page={page}"
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    docs = data.get("docs", [])
                    
                    if not docs:
                        logging.info(f"Plus de résultats OpenLibrary pour '{terme_recherche}' page {page}")
                        break
                    
                    for livre in docs:
                        livre_data = self.extraire_donnees_openlibrary(livre, terme_recherche)
                        if livre_data:
                            livres.append(livre_data)
                    
                    logging.info(f"Récupéré {len(docs)} livres OpenLibrary pour '{terme_recherche}' page {page}")
                    
                    if len(livres) >= max_results:
                        break
                        
                else:
                    logging.error(f"Erreur OpenLibrary API: {response.status_code}")
                    self.stats["erreurs"] += 1
                    
            except Exception as e:
                logging.error(f"Exception OpenLibrary: {e}")
                self.stats["erreurs"] += 1
            
            time.sleep(random.uniform(2, 4))
        
        return livres[:max_results]

    def extraire_donnees_google(self, livre, terme_recherche):
        """Extrait les données d'un livre depuis Google Books"""
        try:
            info = livre.get("volumeInfo", {})
            
            # Filtrer les livres sans titre ou auteur
            titre = info.get("title", "").strip()
            auteurs = info.get("authors", [])
            
            if not titre or not auteurs:
                return None
            
            # Extraire les identifiants
            identifiers = info.get("industryIdentifiers", [])
            isbn_10 = next((id["identifier"] for id in identifiers if id["type"] == "ISBN_10"), "N/A")
            isbn_13 = next((id["identifier"] for id in identifiers if id["type"] == "ISBN_13"), "N/A")
            
            return {
                "titre": titre,
                "auteurs": auteurs,
                "langue": info.get("language", "non précisée"),
                "resume": info.get("description", "")[:1000],  # Limiter la taille
                "isbn_10": isbn_10,
                "isbn_13": isbn_13,
                "note": info.get("averageRating"),
                "nombre_votes": info.get("ratingsCount"),
                "genres_google": info.get("categories", []),
                "date_publication": info.get("publishedDate"),
                "nb_pages": info.get("pageCount"),
                "editeur": info.get("publisher"),
                "terme_recherche": terme_recherche,
                "source_api": "google_books",
                "tous_les_genres": info.get("categories", [])
            }
        except Exception as e:
            logging.error(f"Erreur extraction Google Books: {e}")
            return None

    def extraire_donnees_openlibrary(self, livre, terme_recherche):
        """Extrait les données d'un livre depuis Open Library"""
        try:
            titre = livre.get("title", "").strip()
            auteurs = livre.get("author_name", [])
            
            if not titre or not auteurs:
                return None
            
            return {
                "titre": titre,
                "auteurs": auteurs,
                "langue": livre.get("language", ["non précisée"])[0] if livre.get("language") else "non précisée",
                "resume": "",  # OpenLibrary ne fournit pas toujours la description dans la recherche
                "isbn_10": livre.get("isbn", [None])[0] if livre.get("isbn") else "N/A",
                "isbn_13": livre.get("isbn", [None])[1] if len(livre.get("isbn", [])) > 1 else "N/A",
                "note": None,
                "nombre_votes": None,
                "genres_google": livre.get("subject", [])[:10],  # Limiter le nombre de genres
                "date_publication": str(livre.get("first_publish_year", "")),
                "nb_pages": None,
                "editeur": livre.get("publisher", [None])[0] if livre.get("publisher") else None,
                "terme_recherche": terme_recherche,
                "source_api": "open_library",
                "tous_les_genres": livre.get("subject", [])[:10]
            }
        except Exception as e:
            logging.error(f"Erreur extraction OpenLibrary: {e}")
            return None

    def recuperer_pour_categorie(self, categorie):
        """Récupère des livres pour une catégorie avec toutes ses variations"""
        nom_categorie = categorie["en"].replace(" ", "_").lower()
        tous_livres = []
        
        # Utiliser le terme principal et toutes les variations
        termes_recherche = [categorie["en"]] + categorie.get("variations", [])
        
        for terme in termes_recherche:
            logging.info(f"🔍 Récupération pour terme: '{terme}' (catégorie: {categorie['fr']})")
            
            # Google Books
            livres_google = self.recuperer_google_books(f"subject:{terme}", max_results=300)
            tous_livres.extend(livres_google)
            
            # Open Library  
            livres_ol = self.recuperer_open_library(terme, max_results=200)
            tous_livres.extend(livres_ol)
            
            # Pause entre les termes
            time.sleep(random.uniform(3, 6))
        
        # Déduplication par titre + premier auteur
        livres_uniques = {}
        for livre in tous_livres:
            cle = f"{livre['titre'].lower()}_{livre['auteurs'][0].lower() if livre['auteurs'] else 'unknown'}"
            if cle not in livres_uniques:
                livres_uniques[cle] = livre
        
        livres_finaux = list(livres_uniques.values())
        
        # Sauvegarder
        nom_fichier = f"{self.dossier_output}/{nom_categorie}.json"
        with open(nom_fichier, "w", encoding="utf-8") as f:
            json.dump(livres_finaux, f, ensure_ascii=False, indent=2)
        
        self.stats["total_recuperes"] += len(livres_finaux)
        logging.info(f"✅ Sauvegardé {len(livres_finaux)} livres uniques pour {categorie['fr']} dans {nom_fichier}")
        
        return len(livres_finaux)

    def recuperer_tout(self, categories_a_traiter=None):
        """Récupère des livres pour toutes les catégories ou une sélection"""
        categories = categories_a_traiter or self.categories_etendues
        
        logging.info(f"🚀 Début de la récupération pour {len(categories)} catégories")
        
        for i, categorie in enumerate(categories, 1):
            try:
                logging.info(f"📚 Traitement {i}/{len(categories)}: {categorie['fr']}")
                nb_livres = self.recuperer_pour_categorie(categorie)
                
                # Pause plus longue entre les catégories
                if i < len(categories):
                    pause = random.uniform(10, 20)
                    logging.info(f"⏸️ Pause de {pause:.1f}s avant la prochaine catégorie...")
                    time.sleep(pause)
                    
            except Exception as e:
                logging.error(f"❌ Erreur pour la catégorie {categorie['fr']}: {e}")
                self.stats["erreurs"] += 1
                continue
        
        # Statistiques finales
        logging.info(f"🎉 TERMINÉ ! Total récupéré: {self.stats['total_recuperes']} livres")
        logging.info(f"⚠️ Erreurs rencontrées: {self.stats['erreurs']}")

def main():
    """Fonction principale"""
    print("🚀 RÉCUPÉRATION AMÉLIORÉE DE LIVRES VIA APIS")
    print("=" * 60)
    
    recuperateur = RecuperateurLivresAmeliore()
    
    # Option 1: Récupérer tout
    recuperateur.recuperer_tout()
    
    # Option 2: Récupérer seulement quelques catégories pour tester
    # categories_test = recuperateur.categories_etendues[:5]  # Les 5 premières
    # recuperateur.recuperer_tout(categories_test)
    
    print("\n🎯 Récupération terminée ! Vérifiez le dossier 'livres_json_ameliore'")

if __name__ == "__main__":
    main() 