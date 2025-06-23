# DataBook API - Gestion des Données de Livres

Une API REST spécialisée pour la gestion et l'analyse des données de livres, construite avec FastAPI. Conçue pour fonctionner avec des bases de données Docker et protégée par clé API.

## 🚀 Fonctionnalités

- **CRUD complet** pour les livres et utilisateurs
- **Protection par clé API** simple et efficace
- **Support multi-bases de données** (PostgreSQL, MySQL, MongoDB)
- **Configuration Docker** prête à l'emploi
- **Validation des données** avec Pydantic
- **Documentation automatique** avec Swagger UI
- **Recherche avancée** de livres
- **Statistiques** et monitoring

## 📦 Installation

### Prérequis
- Python 3.8+
- Docker & Docker Compose
- pip

### Installation des dépendances

```bash
# Installer les dépendances
pip install -r requirements.txt
```

### Configuration

1. Créez un fichier `.env` à la racine du projet :

```env
# Clé API pour protéger vos endpoints
API_KEY=votre-cle-api-secrete-changez-moi

# Base de données principale (PostgreSQL dans Docker)
DATABASE_URL=postgresql://user:password@localhost:5432/databook

# MongoDB (optionnel)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=databook

# Configuration de l'application
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 🐳 Configuration Docker

### Base de données PostgreSQL

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: databook
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Lancement avec Docker

```bash
# Démarrer la base de données
docker-compose up -d

# Lancer l'API
python main.py
```

## 🏃‍♂️ Lancement de l'application

```bash
# Lancement en mode développement
python main.py

# Ou avec uvicorn directement
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible à l'adresse : `http://localhost:8000`

## 📚 Documentation

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

## 🔑 Authentification par Clé API

Pour accéder aux endpoints protégés, ajoutez l'en-tête suivant à vos requêtes :

```
X-API-Key: votre-cle-api-secrete
```

## 🔗 Endpoints

### 📖 Endpoints Publics (sans clé API)

- `GET /` - Page d'accueil de l'API
- `GET /health` - Vérification de santé
- `GET /books/` - Liste des livres
- `GET /books/{id}` - Détails d'un livre
- `GET /search/` - Recherche de livres

### 🔒 Endpoints Protégés (nécessitent une clé API)

#### Gestion des livres
- `POST /books/` - Créer un livre
- `PUT /books/{id}` - Mettre à jour un livre
- `DELETE /books/{id}` - Supprimer un livre

#### Gestion des utilisateurs
- `GET /users/` - Liste des utilisateurs
- `POST /users/` - Créer un utilisateur
- `GET /users/{id}` - Détails d'un utilisateur

#### Système
- `GET /stats/` - Statistiques générales
- `GET /db-status/` - Status de la base de données

## 🔧 Exemples d'utilisation

### Récupérer tous les livres (public)

```bash
curl -X GET "http://localhost:8000/books/"
```

### Créer un livre (protégé)

```bash
curl -X POST "http://localhost:8000/books/" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: votre-cle-api" \
     -d '{
       "title": "1984",
       "author": "George Orwell",
       "isbn": "978-0-452-28423-4",
       "description": "Roman dystopique",
       "category": "fiction",
       "publication_year": 1949,
       "owner_id": 1
     }'
```

### Rechercher des livres

```bash
curl -X GET "http://localhost:8000/search/?query=orwell&category=fiction"
```

### Vérifier les statistiques (protégé)

```bash
curl -X GET "http://localhost:8000/stats/" \
     -H "X-API-Key: votre-cle-api"
```

## 📊 Structure du projet

```
api/
├── main.py              # Point d'entrée de l'application
├── models.py            # Modèles Pydantic
├── database.py          # Configuration bases de données
├── crud.py              # Opérations CRUD
├── auth.py              # Protection par clé API
├── config.py            # Configuration
├── requirements.txt     # Dépendances
└── README.md           # Documentation
```

## 🗄️ Modèle de données

### Livre (Book)
- `id` - Identifiant unique
- `title` - Titre du livre
- `author` - Auteur
- `isbn` - Numéro ISBN
- `description` - Description
- `category` - Catégorie
- `publication_year` - Année de publication
- `publisher` - Éditeur
- `page_count` - Nombre de pages
- `rating` - Note
- `price` - Prix

## 🔒 Sécurité

- **Protection par clé API** pour les endpoints sensibles
- **Validation des données** d'entrée avec Pydantic
- **Protection CORS** configurable
- **Connexions sécurisées** aux bases de données

## 🚀 Déploiement

### Variables d'environnement de production

```env
API_KEY=your-production-api-key-very-secure
DATABASE_URL=postgresql://user:password@db-server:5432/databook
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com
```

### Avec Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📈 Monitoring

L'API inclut plusieurs endpoints pour le monitoring :

- `/health` - Vérification de santé de l'API
- `/db-status/` - Status de la base de données (protégé)
- `/stats/` - Statistiques d'utilisation (protégé)

## 🛠️ Personnalisation

Cette API est conçue pour être facilement personnalisable :

1. **Modifiez les modèles** dans `models.py` pour vos champs spécifiques
2. **Ajoutez de nouveaux endpoints** dans `main.py`
3. **Étendez les opérations CRUD** dans `crud.py`
4. **Configurez vos bases de données** dans `database.py`

## 📄 Licence

Ce projet est sous licence MIT. 