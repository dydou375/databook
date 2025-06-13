import gzip
import json
from pymongo import MongoClient
from pathlib import Path
from tqdm import tqdm

def export_books_to_mongodb(
    dump_path,
    mongo_uri="mongodb://localhost:27017/",
    db_name="openlibrary",
    collection_name="books",
    max_books=10000
):
    """
    Extrait les livres du dump OpenLibrary, les met en forme JSON et les insère dans MongoDB.
    """
    print(f"Connexion à MongoDB ({mongo_uri})...")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    print(f"Lecture du dump : {dump_path}")
    books = []
    total_lines = 0
    with gzip.open(dump_path, 'rt', encoding='utf-8') as f:
        for line in tqdm(f, desc="Lecture dump", unit="lignes", total=max_books):
            total_lines += 1
            try:
                data = json.loads(line)
                # On ne garde que les livres (type /type/edition ou /type/work)
                if data.get('type', {}).get('key') in ['/type/edition', '/type/work']:
                    # On extrait les champs principaux
                    book = {
                        'title': data.get('title'),
                        'authors': data.get('authors', []),
                        'publish_date': data.get('publish_date'),
                        'subjects': data.get('subjects', []),
                        'isbn_10': data.get('isbn_10', []),
                        'isbn_13': data.get('isbn_13', []),
                        'key': data.get('key'),
                        'type': data.get('type', {}).get('key'),
                        'languages': data.get('languages', []),
                        'number_of_pages': data.get('number_of_pages'),
                        'publishers': data.get('publishers', []),
                        'covers': data.get('covers', []),
                        'identifiers': data.get('identifiers', {}),
                        'first_sentence': data.get('first_sentence'),
                        'description': data.get('description'),
                    }
                    books.append(book)
            except Exception as e:
                continue
            if len(books) >= max_books:
                break
    print(f"Nombre de livres extraits : {len(books)}")
    if books:
        print(f"Insertion dans MongoDB ({db_name}.{collection_name})...")
        collection.insert_many(books)
        print("✅ Insertion terminée !")
    else:
        print("Aucun livre extrait.")
    client.close()

if __name__ == "__main__":
    # Exemple d'utilisation
    dump_path = Path("../../data/fichier_openlibrary/dump_file")  # À adapter si besoin
    export_books_to_mongodb(dump_path, max_books=10000) 