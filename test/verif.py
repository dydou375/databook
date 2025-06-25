from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['databook']
collection = db['livres']

count = collection.count_documents({})
print(f'Documents dans la collection: {count}')

if count > 0:
    print('\nPremiers documents:')
    for doc in collection.find().limit(5):
        auteur = doc['auteurs'][0] if doc['auteurs'] else '?'
        print(f'   - {doc["titre"]} par {auteur}')

print(f'\nIndex disponibles:')
for idx in collection.list_indexes():
    print(f'   - {idx["name"]}') 