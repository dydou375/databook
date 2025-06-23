# 📚 DataBook API v2.0

API moderne pour l'analyse et la gestion des données de livres avec support PostgreSQL et MongoDB.

## 🌟 Fonctionnalités

- **🔗 Multi-bases de données** : PostgreSQL pour les données relationnelles, MongoDB pour l'analyse
- **🚀 FastAPI** : API moderne et rapide avec documentation automatique
- **🔐 Sécurité** : Authentification par clé API
- **🔍 Recherche avancée** : Recherche textuelle dans les deux bases
- **📈 Analytics** : Statistiques et métriques en temps réel
- **🐳 Docker Ready** : Configuration Docker Compose incluse

## 📋 Prérequis

- Python 3.8+
- PostgreSQL 12+
- MongoDB 5.0+
- Docker et Docker Compose (optionnel)

## 🚀 Installation et Configuration

### 1. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 2. Configuration de l'environnement

Copiez `env_example.txt` vers `.env` et configurez vos variables :

```bash
cp env_example.txt .env
```

Modifiez le fichier `.env` avec vos paramètres :

```env
# Configuration API
API_KEY=votre-cle-api-securisee
SECRET_KEY=votre-cle-secrete-super-secure

# Configuration PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=databook
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# Configuration MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=databook
```

### 3. Lancement avec Docker (Recommandé)

```bash
# Démarrer les bases de données
docker-compose up -d postgres mongodb

# Ou tout démarrer (avec interfaces d'admin)
docker-compose up -d
```

### 4. Lancement manuel

```bash
# Démarrage avec le script personnalisé
python start.py

# Ou démarrage direct
python main.py

# Ou avec uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🛠️ Utilisation

### Endpoints principaux

| Endpoint | Description | Authentification |
|----------|-------------|-----------------|
| `GET /` | Page d'accueil | Non |
| `GET /docs` | Documentation Swagger | Non |
| `GET /health` | État de santé | Non |

### 📊 PostgreSQL Endpoints

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/postgres/books/` | GET | Liste des livres | Non |
| `/postgres/books/{id}` | GET | Livre par ID | Non |
| `/postgres/books/` | POST | Créer un livre | Oui |
| `/postgres/books/{id}` | PUT | Modifier un livre | Oui |
| `/postgres/books/{id}` | DELETE | Supprimer un livre | Oui |
| `/postgres/users/` | GET | Liste des utilisateurs | Oui |
| `/postgres/statistics/` | GET | Statistiques PostgreSQL | Oui |

### 🍃 MongoDB Endpoints

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/mongo/books/` | GET | Liste des livres | Non |
| `/mongo/books/{id}` | GET | Livre par ID | Non |
| `/mongo/books/` | POST | Créer un livre | Oui |
| `/mongo/search/` | GET | Recherche avancée | Non |
| `/mongo/books/popular/` | GET | Livres populaires | Non |
| `/mongo/statistics/` | GET | Analytics MongoDB | Oui |

## 📖 Exemples d'utilisation

### 1. Récupérer tous les livres (PostgreSQL)

```bash
curl -X GET "http://localhost:8000/postgres/books/" \
  -H "accept: application/json"
```

### 2. Rechercher des livres (MongoDB)

```bash
curl -X GET "http://localhost:8000/mongo/search/?query=python&category=tech" \
  -H "accept: application/json"
```

### 3. Créer un livre (avec authentification)

```bash
curl -X POST "http://localhost:8000/postgres/books/" \
  -H "accept: application/json" \
  -H "X-API-Key: votre-cle-api" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Guide Python",
    "description": "Un excellent guide pour apprendre Python",
    "price": 29.99,
    "category": "books",
    "owner_id": 1
  }'
```

### 4. Obtenir les statistiques

```bash
curl -X GET "http://localhost:8000/stats/" \
  -H "accept: application/json" \
  -H "X-API-Key: votre-cle-api"
```

## 🔒 Authentification

L'API utilise une authentification par clé API pour les endpoints protégés. Ajoutez l'en-tête suivant à vos requêtes :

```
X-API-Key: votre-cle-api
```

## 📊 Monitoring et Administration

### Interfaces d'administration (avec Docker)

- **PostgreSQL** : http://localhost:8082 (pgAdmin)
  - Email: admin@databook.com
  - Mot de passe: admin123

- **MongoDB** : http://localhost:8081 (Mongo Express)
  - Utilisateur: admin
  - Mot de passe: admin123

### Endpoints de monitoring

- `GET /health` : État de santé des bases de données
- `GET /db-status/` : Statut détaillé des connexions (authentifié)

## 🗂️ Structure des données

### Modèle PostgreSQL (Book/Item)

```json
{
  "id": 1,
  "title": "Titre du livre",
  "description": "Description",
  "price": 29.99,
  "category": "books",
  "status": "active",
  "owner_id": 1,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": null
}
```

### Modèle MongoDB (BookMongo)

```json
{
  "_id": "ObjectId",
  "title": "Titre du livre",
  "author": "Auteur",
  "isbn": "978-0123456789",
  "description": "Description",
  "price": 29.99,
  "category": "tech",
  "publication_year": 2024,
  "rating": 4.5,
  "tags": ["python", "programming"],
  "language": "fr",
  "format": "paperback"
}
```

## 🛠️ Développement

### Structure du projet

```
api/
├── main.py              # Point d'entrée principal
├── start.py             # Script de démarrage
├── config.py            # Configuration
├── models.py            # Modèles PostgreSQL
├── models_mongo.py      # Modèles MongoDB
├── database.py          # Configuration PostgreSQL
├── mongo_crud.py        # Service MongoDB
├── crud.py              # CRUD PostgreSQL
├── routes_postgres.py   # Routes PostgreSQL
├── routes_mongo.py      # Routes MongoDB
├── auth.py              # Authentification
├── requirements.txt     # Dépendances
├── docker-compose.yml   # Configuration Docker
└── README_API.md        # Documentation
```

### Commandes utiles

```bash
# Démarrage en mode développement
python start.py

# Réinitialiser la base PostgreSQL
python -c "from database import reset_db; reset_db()"

# Tests de connexion
python -c "from database import check_db_connection; check_db_connection()"
python -c "from mongo_crud import mongodb_service; mongodb_service.connect()"
```

## 🐛 Dépannage

### Problèmes courants

1. **Erreur de connexion PostgreSQL**
   - Vérifiez que PostgreSQL est démarré
   - Vérifiez les paramètres de connexion dans `.env`

2. **Erreur de connexion MongoDB**
   - MongoDB est optionnel, l'API fonctionne sans
   - Vérifiez que MongoDB est démarré

3. **Erreur d'authentification**
   - Vérifiez que vous utilisez la bonne clé API
   - L'en-tête doit être `X-API-Key`

### Logs et debugging

```bash
# Activer le mode debug
export DEBUG=true
python start.py

# Voir les logs Docker
docker-compose logs -f
```

## 📚 Documentation API

Une fois l'API démarrée, accédez à :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🤝 Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

🚀 **Bon développement avec DataBook API !** 