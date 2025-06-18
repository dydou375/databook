# 📚 DataBook - Plateforme Complète d'Analyse de Livres

Une plateforme moderne alliant API REST, interface utilisateur et analytics pour l'exploration de données bibliographiques.

## 🎯 Vision et Objectifs

DataBook vise à créer un écosystème complet pour l'analyse de données de livres :

- **📊 Base de données enrichie** : 4766 livres + 85 critiques Babelio opérationnels
- **🔍 Analyse avancée** : Analytics sur genres, auteurs, tendances
- **🌐 Accès ouvert** : API REST + interface utilisateur moderne
- **🛡️ Sécurité moderne** : Authentification JWT complète

## 🏗️ Architecture Technique

### 📋 Stack Technologique
```
Frontend : Streamlit + Plotly (visualisations)
Backend  : FastAPI + JWT (authentification)
Données  : PostgreSQL (relationnel) + MongoDB (NoSQL)
Sécurité : bcrypt (hash) + JWT tokens
Docker   : Containerisation optionnelle
```

### 🗄️ Modèle de Données
- **PostgreSQL schéma `test`** : Utilisateurs JWT, relations
- **MongoDB `databook`** : 4766 livres, 85 critiques Babelio
- **Sources intégrées** : Babelio, métadonnées enrichies

## 🚀 Fonctionnalités Opérationnelles

### ✅ API DataBook v3.0 (40+ endpoints)
- **🔐 Authentification JWT** : Inscription, connexion, profil
- **📚 MongoDB (4766 livres)** : CRUD, recherche, analytics 
- **🗄️ PostgreSQL** : Gestion relationnelle
- **📊 Analytics** : Top genres/auteurs, statistiques
- **📖 Documentation** : Swagger UI automatique

### ✅ Interface Streamlit Authentifiée
- **🔑 Connexion/Inscription** : Gestion complète des comptes
- **🏠 Dashboard** : Métriques temps réel + accès rapide
- **📚 Exploration** : Recherche dans 4766 livres MongoDB
- **📊 Analytics visuels** : Graphiques Plotly interactifs
- **👤 Profil** : Gestion utilisateur personnalisée

## 📦 Installation Rapide

### Prérequis
- Python 3.8+, PostgreSQL 12+, MongoDB 5.0+
- Docker (optionnel mais recommandé)

### Configuration
```bash
# 1. Environnement
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Bases de données (Docker)
docker-compose up -d postgres mongodb

# 3. Configuration .env (api/)
SECRET_KEY=votre-cle-secrete-jwt
POSTGRES_DB=databook
MONGODB_DATABASE=databook

# 4. Démarrage
cd api && python start.py              # API sur :8000
python start_streamlit_auth.py         # Interface sur :8501
```

## 🎮 Guide d'Utilisation

### Interface Streamlit (http://localhost:8501)
1. **Inscription** : Email, nom, prénom, mot de passe
2. **Connexion** : Authentification JWT sécurisée
3. **Dashboard** : Métriques 4766 livres + 85 critiques
4. **Exploration** : Recherche par titre/auteur/genre
5. **Analytics** : Top 10 genres/auteurs, graphiques
6. **Profil** : Gestion compte et déconnexion

### API REST (http://localhost:8000)
```bash
# Documentation interactive
curl http://localhost:8000/docs

# Santé du système  
curl http://localhost:8000/health

# Inscription
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"motdepasse","first_name":"Test","last_name":"User"}'

# Recherche livres
curl "http://localhost:8000/mongo-livres/livres/search?q=roman&limit=10"

# Analytics (avec token)
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/mongo-extras/analytics
```

## 🔗 Endpoints Principaux

### 🌐 Généraux
- `GET /` - Vue d'ensemble + documentation
- `GET /health` - État PostgreSQL + MongoDB
- `GET /docs` - Documentation Swagger

### 🔐 Authentification JWT
- `POST /auth/register` - Inscription utilisateur
- `POST /auth/login` - Connexion (retourne token)
- `GET /auth/me` - Profil utilisateur (authentifié)

### 📚 MongoDB (4766 livres)
- `GET /mongo-livres/livres` - Liste avec pagination
- `GET /mongo-livres/livres/search` - Recherche avancée
- `GET /mongo-livres/critiques` - 85 critiques Babelio
- `GET /mongo-livres/statistiques` - Stats complètes

### 🎯 Analytics
- `GET /mongo-extras/genres` - Top genres
- `GET /mongo-extras/auteurs` - Top auteurs  
- `GET /mongo-extras/analytics` - Dashboard complet

### 🗄️ PostgreSQL
- `GET /postgres/users/` - Utilisateurs (authentifié)
- `POST /postgres/books/` - Créer livre (authentifié)

## 🛡️ Sécurité

### JWT (JSON Web Tokens)
- **Algorithme** : HS256 sécurisé
- **Expiration** : 30 minutes configurable
- **Stockage** : Session Streamlit sécurisée

### Mots de passe
- **Hachage** : bcrypt + salt automatique
- **Stockage** : PostgreSQL `test.users` (jamais en clair)
- **Validation** : Minimum 6 caractères

### Protection des routes
- **Public** : Exploration, recherche, documentation
- **Authentifié** : Création, modification, profil
- **Gestion d'erreurs** : 401/403 appropriés

## 📈 Données Disponibles

| Source | Type | Quantité | État |
|--------|------|----------|------|
| MongoDB | Livres | **4766** | ✅ Opérationnel |
| MongoDB | Critiques Babelio | **85** | ✅ Opérationnel |
| PostgreSQL | Utilisateurs JWT | Variable | ✅ Opérationnel |
| PostgreSQL | Livres relationnels | Variable | ✅ Opérationnel |

## 🔧 Administration

### Gestion utilisateurs PostgreSQL
```bash
cd api

# Lister utilisateurs schéma test
python manage_users_test.py list

# Créer utilisateur
python manage_users_test.py create admin@test.com password Admin User

# Vérifier schéma
python manage_users_test.py verify
```

### Monitoring
- **API Health** : `/health` (PostgreSQL + MongoDB)
- **Métriques** : Utilisateurs, livres, performance
- **Logs** : Connexions, erreurs, authentification

## 🚀 Roadmap

### Court terme (1-3 mois)
- [ ] Refresh automatique tokens JWT
- [ ] Interface mobile optimisée
- [ ] Export données (CSV, JSON)
- [ ] Mode sombre/clair

### Moyen terme (3-6 mois)  
- [ ] Gestion rôles utilisateur (admin/lecteur)
- [ ] Dashboards personnalisés
- [ ] Recherche élastique (Elasticsearch)
- [ ] Images de couvertures

### Long terme (6-12 mois)
- [ ] IA recommandations
- [ ] Analytics prédictifs
- [ ] API publique documentée
- [ ] Application mobile native

## 🎯 Cas d'Usage

### 👨‍💻 Développeurs
- API REST moderne avec JWT
- Documentation Swagger complète
- Données JSON structurées
- Exemples d'intégration

### 📚 Bibliothécaires
- Interface de recherche intuitive
- Gestion de collections
- Import/Export de données
- Statistiques d'utilisation

### 🔬 Chercheurs
- Analytics littéraires
- Données exportables
- API programmatique
- Tendances par genre/époque

### 👥 Grand Public
- Interface simple et moderne
- Découverte de livres
- Critiques de la communauté
- Recommandations personnalisées

## 🏗️ Structure du Projet

```
databook/
├── api/                              # API FastAPI
│   ├── main_cleaned.py              # Application principale
│   ├── routes/                      # Endpoints organisés
│   │   ├── auth_routes.py          # JWT authentification  
│   │   ├── routes_mongo_livres.py  # 4766 livres MongoDB
│   │   ├── routes_mongo_extras.py  # Analytics avancés
│   │   └── routes_postgres.py      # PostgreSQL
│   ├── database/                   # Configuration bases
│   ├── auth/                       # Système authentification
│   └── manage_users_test.py        # Admin utilisateurs
├── streamlit_auth.py               # Interface utilisateur
├── start_streamlit_auth.py         # Démarrage interface
└── README_UNIFIED.md              # Cette documentation
```

## 🌟 Sources de Données

### Actuellement intégrées
- **Babelio** : 85 critiques avec notes
- **Métadonnées** : Titres, auteurs, genres, années
- **Analytics** : Statistiques calculées

### Prévues (sources externes)
- **Open Library** : Métadonnées complètes
- **Google Books** : Descriptions, images  
- **Goodreads** : Citations, discussions
- **Kaggle** : Datasets spécialisés

## 📞 Support et Contribution

### Signalement de bugs
1. Vérifier logs API + interface
2. Documenter étapes de reproduction  
3. Inclure environnement (OS, versions)

### Suggestions d'amélioration
1. Décrire cas d'usage
2. Justifier bénéfices utilisateurs
3. Évaluer faisabilité technique

### Documentation
- **API** : http://localhost:8000/docs (Swagger)
- **Code** : Commentaires dans le source
- **Guides** : README et sous-documentations

---

## 🎉 Résumé

**DataBook est opérationnel** et offre dès maintenant :

✅ **API moderne** : 40+ endpoints avec JWT  
✅ **4766 livres** : MongoDB accessible via interface  
✅ **Interface complète** : Streamlit avec authentification  
✅ **Analytics avancés** : Graphiques et visualisations  
✅ **Architecture sécurisée** : PostgreSQL + MongoDB + JWT  

**Démarrage immédiat :**
1. `cd api && python start.py` (API)
2. `python start_streamlit_auth.py` (Interface)  
3. Créer compte sur http://localhost:8501
4. Explorer 4766 livres ! 🚀📚 