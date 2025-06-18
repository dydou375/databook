# 🚀 DataBook API Simple

API simple et sécurisée pour accéder à vos données PostgreSQL et MongoDB.

## 🎯 Fonctionnalités

- ✅ Connexion PostgreSQL et MongoDB
- 🔐 Sécurité par clé API
- 📊 Affichage des données des deux bases
- 📖 Documentation interactive (Swagger)
- 🔍 Recherche dans les données

## 🚀 Démarrage rapide

### 1. Configuration

Modifiez `config_simple.py` ou utilisez des variables d'environnement :

```bash
export API_KEY="votre-cle-api"
export DATABASE_URL="postgresql://user:password@localhost:5432/votre_db"
export MONGODB_URL="mongodb://localhost:27017"
export MONGODB_DATABASE="votre_db_mongo"
```

### 2. Démarrage

```bash
python start_simple.py
```

ou directement :

```bash
python main_simple.py
```

### 3. Accès

- 🏠 **Accueil** : http://localhost:8000/
- 📖 **Documentation** : http://localhost:8000/docs
- ❤️ **Santé** : http://localhost:8000/health

## 🔐 Authentification

Toutes les routes protégées nécessitent l'en-tête `X-API-Key` :

```bash
curl -H "X-API-Key: databook-api-key-2024" http://localhost:8000/postgres/
```

## 📋 Endpoints disponibles

### Routes publiques

- `GET /` - Page d'accueil
- `GET /health` - État de l'API et des bases de données

### Routes PostgreSQL (🔐 protégées)

- `GET /postgres/` - Informations sur la base PostgreSQL
- `GET /postgres/tables/{table_name}` - Données d'une table
- `GET /postgres/livres` - Livres avec recherche

### Routes MongoDB (🔐 protégées)

- `GET /mongodb/` - Informations sur la base MongoDB
- `GET /mongodb/collections/{collection_name}` - Données d'une collection
- `GET /mongodb/livres` - Livres avec recherche

## 🔍 Exemples d'utilisation

### Récupérer vos livres PostgreSQL

```bash
curl -H "X-API-Key: databook-api-key-2024" \
     "http://localhost:8000/postgres/livres?limit=10&search=python"
```

### Voir les tables PostgreSQL

```bash
curl -H "X-API-Key: databook-api-key-2024" \
     "http://localhost:8000/postgres/"
```

### Récupérer une table spécifique

```bash
curl -H "X-API-Key: databook-api-key-2024" \
     "http://localhost:8000/postgres/tables/livre?limit=5"
```

### Voir les collections MongoDB

```bash
curl -H "X-API-Key: databook-api-key-2024" \
     "http://localhost:8000/mongodb/"
```

## 📊 Structure des réponses

Toutes les réponses incluent :
- `timestamp` - Horodatage de la requête
- `count` ou `pagination` - Information sur le nombre de résultats
- `data` ou le contenu spécifique

### Exemple de réponse

```json
{
  "source": "PostgreSQL",
  "livres": [
    {
      "id_livre": 1,
      "titre": "Introduction à Python",
      "auteur_nom": "Dupont",
      "auteur_prenom": "Jean"
    }
  ],
  "count": 1,
  "search": "python",
  "timestamp": "2024-06-18T09:30:00"
}
```

## 🛠️ Dépannage

### PostgreSQL ne se connecte pas

1. Vérifiez l'URL de connexion dans `config_simple.py`
2. Assurez-vous que PostgreSQL est démarré
3. Vérifiez les permissions de l'utilisateur

### MongoDB ne se connecte pas

1. Vérifiez l'URL MongoDB dans `config_simple.py`
2. Assurez-vous que MongoDB est démarré
3. Vérifiez le nom de la base de données

### Erreur 401 - Non autorisé

Vous devez inclure l'en-tête `X-API-Key` avec la bonne clé API.

## 📝 Notes importantes

- La clé API par défaut est `databook-api-key-2024` - **changez-la en production !**
- L'API adapte automatiquement les requêtes à votre structure de tables
- Les routes PostgreSQL utilisent vos tables existantes (`livre`, `auteur`, etc.)
- L'API gère gracieusement les bases de données indisponibles

## 🔧 Personnalisation

Pour adapter l'API à votre structure de données :

1. Modifiez les requêtes dans `main_simple.py`
2. Ajustez les noms de tables/collections selon vos besoins
3. Personnalisez les endpoints selon votre usage

Votre API est maintenant prête à utiliser ! 🎉 