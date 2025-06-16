# 📚 Import des Critiques de Livres dans MongoDB

Ce dossier contient les scripts pour importer vos données de critiques de livres (extraites de Babelio) dans une base de données MongoDB.

## 🎯 Objectif

Charger les données JSON des critiques de livres dans MongoDB pour permettre :
- Des recherches avancées
- Des analyses de données
- Un stockage structuré et évolutif
- Des requêtes complexes sur les critiques et notes

## 📁 Fichiers Disponibles

- `livre_critique` : Fichier JSON contenant les données (4203 livres)
- `import_simple.py` : **Script principal simplifié** (recommandé)
- `import_mongodb.py` : Script complet avec toutes les fonctionnalités
- `config_mongodb.py` : Configuration MongoDB
- `requirements.txt` : Dépendances Python
- `README.md` : Ce fichier d'instructions

## 🚀 Installation et Utilisation Rapide

### 1. Prérequis

Vous devez avoir installé :
- **Python 3.7+**
- **MongoDB** (local ou distant)

### 2. Installation de MongoDB

#### Sur Windows :
```bash
# Téléchargez MongoDB Community Server depuis le site officiel
# https://www.mongodb.com/try/download/community
```

#### Sur Linux (Ubuntu/Debian) :
```bash
sudo apt update
sudo apt install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

#### Sur macOS :
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### 3. Installation des dépendances Python

```bash
# Dans le dossier du projet
pip install -r requirements.txt

# Ou manuellement :
pip install pymongo
```

### 4. Lancement de l'import

```bash
# Script simple (recommandé pour débuter)
python import_simple.py

# Ou script complet
python import_mongodb.py
```

## 📊 Structure de la Base de Données

### Base de données : `bibliotheque_critiques`
### Collection : `critiques_livres`

### Structure d'un document :

```json
{
  "_id": ObjectId("..."),
  "isbn": "9782266185691",
  "titre": "La vague",
  "auteur": "ToddStrasser",
  "resume_babelio": "Cette histoire est basée sur...",
  "note_babelio": 3.89,
  "nombre_votes_babelio": 4789,
  "repartition_notes_babelio": {
    "5_etoiles": 230,
    "4_etoiles": 222,
    "3_etoiles": 109,
    "2_etoiles": 35,
    "1_etoiles": 23
  },
  "critiques_babelio": [
    {
      "utilisateur": "tiptop92",
      "date": "10 janvier 2020",
      "note_utilisateur": 5.0,
      "texte": "Todd Strasser-La Vague-1981..."
    }
  ],
  "url_babelio": "https://www.babelio.com/livres/...",
  "date_extraction": "2025-06-16T10:19:07.349212",
  "nombre_critiques": 6,
  "import_date": ISODate("2025-01-XX"),
  "import_source": "babelio_extraction"
}
```

## 🔍 Index Créés Automatiquement

- `isbn` (unique) : Pour éviter les doublons
- `titre` : Pour rechercher par titre
- `auteur` : Pour rechercher par auteur
- `note_babelio` : Pour filtrer par note
- `date_extraction` : Pour trier par date

## 📝 Exemples de Requêtes

### Via MongoDB Shell :

```javascript
// Se connecter à la base
use bibliotheque_critiques

// Trouver tous les livres d'un auteur
db.critiques_livres.find({"auteur": "RobinCook"})

// Livres avec note supérieure à 4
db.critiques_livres.find({"note_babelio": {"$gt": 4}})

// Compter les livres par auteur
db.critiques_livres.aggregate([
    {"$group": {"_id": "$auteur", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
])

// Recherche textuelle dans les titres
db.critiques_livres.find({"titre": {"$regex": "vague", "$options": "i"}})

// Livres avec plus de 100 votes
db.critiques_livres.find({"nombre_votes_babelio": {"$gt": 100}})

// Moyenne des notes par auteur
db.critiques_livres.aggregate([
    {"$group": {
        "_id": "$auteur", 
        "moyenne_notes": {"$avg": "$note_babelio"},
        "nb_livres": {"$sum": 1}
    }},
    {"$sort": {"moyenne_notes": -1}}
])
```

### Via Python (pymongo) :

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['bibliotheque_critiques']
collection = db['critiques_livres']

# Trouver un livre par ISBN
livre = collection.find_one({"isbn": "9782266185691"})

# Rechercher par auteur
livres_cook = collection.find({"auteur": "RobinCook"})

# Statistiques
stats = collection.aggregate([
    {"$group": {
        "_id": None,
        "total_livres": {"$sum": 1},
        "note_moyenne": {"$avg": "$note_babelio"}
    }}
])
```

## ⚙️ Configuration Avancée

### MongoDB distant ou Atlas :

Modifiez les paramètres dans `import_simple.py` :

```python
# Pour MongoDB Atlas
MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/"

# Pour MongoDB distant
MONGO_URI = "mongodb://username:password@host:port/"
```

### Personnalisation :

- Nom de la base : Changez `DB_NAME` dans le script
- Nom de la collection : Changez `COLLECTION_NAME`
- Options de connexion : Modifiez dans `config_mongodb.py`

## 🔧 Dépannage

### Erreur de connexion MongoDB :
```
MongoDB ne démarre pas ou n'est pas accessible
```
**Solution :**
- Vérifiez que MongoDB est démarré : `sudo systemctl status mongodb`
- Vérifiez le port (27017 par défaut)
- Testez la connexion : `mongo` ou `mongosh`

### Erreur pymongo :
```
ModuleNotFoundError: No module named 'pymongo'
```
**Solution :**
```bash
pip install pymongo
```

### Fichier JSON introuvable :
```
FileNotFoundError: livre_critique
```
**Solution :**
- Vérifiez que le fichier `livre_critique` est dans le même dossier
- Vérifiez les permissions de lecture

## 📈 Après l'Import

### Outils recommandés :

1. **MongoDB Compass** : Interface graphique
   - Téléchargement : https://www.mongodb.com/products/compass

2. **Studio 3T** : IDE pour MongoDB
   - Téléchargement : https://studio3t.com/

3. **Ligne de commande** : `mongo` ou `mongosh`

### Analyses possibles :

- Analyse des sentiments des critiques
- Corrélation entre nombre de votes et notes
- Évolution des goûts littéraires
- Recommandation de livres
- Détection de spam dans les critiques

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez les prérequis (Python, MongoDB)
2. Consultez les logs d'erreur
3. Testez avec `import_simple.py` d'abord
4. Vérifiez la connectivité MongoDB

---

**Bon import et bonne analyse ! 📊📚** 