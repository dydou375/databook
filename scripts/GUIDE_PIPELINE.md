# 🚀 GUIDE PIPELINE DATABOOK

## 📋 Vue d'ensemble

Le **Pipeline DataBook** est un système automatisé qui orchestre toute la chaîne de récupération et traitement des données pour votre projet d'analyse de livres. Il combine :

- 📡 **Récupération API** (Google Books, OpenLibrary)
- 🕷️ **Scrapping web** (Babelio pour critiques)
- 📊 **Traitement CSV** (nettoyage, formatage)
- 🗄️ **Import PostgreSQL** (tables relationnelles)
- 🍃 **Import MongoDB** (documents JSON)

## 🎯 Démarrage rapide

### Option 1 : Démarrage automatique
```bash
python demarrage_rapide.py --auto
```

### Option 2 : Démarrage interactif
```bash
python demarrage_rapide.py
```

### Option 3 : Pipeline complet manuel
```bash
python pipeline_master.py
```

## ⚙️ Configurations disponibles

### 🚀 Configuration minimale
- **Usage** : Tests rapides, développement
- **Données** : ~100 livres API, vérifications seulement
- **Durée** : 5-10 minutes
- **Espace** : ~50 MB

### 📊 Configuration standard
- **Usage** : Utilisation normale, démonstrations
- **Données** : ~1000 livres API, imports BDD
- **Durée** : 30-60 minutes
- **Espace** : ~500 MB

### 🎯 Configuration complète
- **Usage** : Production, analyses poussées
- **Données** : ~5000+ livres, scrapping Babelio
- **Durée** : 2-4 heures
- **Espace** : ~2 GB

## 📦 Prérequis

### Modules Python requis
```bash
pip install requests pandas beautifulsoup4 sqlalchemy psycopg2-binary pymongo
```

### Bases de données
- **PostgreSQL** : Pour données relationnelles
- **MongoDB** : Pour documents JSON

### Structure de dossiers attendue
```
databook/
├── scripts/
│   ├── api/              # Scripts récupération API
│   └── scrapping/        # Scripts scrapping web
├── bdd/
│   ├── livres/          # Scripts PostgreSQL
│   └── nosql/           # Scripts MongoDB
└── data/
    ├── livre_json/      # Fichiers JSON générés
    └── fichier_openlibrary/  # Données OpenLibrary
```

## 🔧 Utilisation détaillée

### 1. Pipeline complet automatique

```bash
# Lancement avec détection automatique
python demarrage_rapide.py --auto

# Forcer une configuration spécifique
python demarrage_rapide.py --auto --config standard
```

### 2. Étapes individuelles

```python
from pipeline_master import PipelineMaster

pipeline = PipelineMaster()

# Récupération API uniquement
pipeline.executer_etape_api()

# Scrapping Babelio
pipeline.executer_etape_scrapping()

# Import PostgreSQL + MongoDB
pipeline.executer_etape_postgresql()
pipeline.executer_etape_mongodb()
```

### 3. Menu interactif complet

```bash
python pipeline_master.py
```

**Options disponibles :**
1. 🚀 Pipeline complet (toutes étapes)
2. 📡 Récupération API uniquement
3. 🕷️ Scrapping Babelio uniquement
4. 📊 Traitement CSV uniquement
5. 🗄️ Import BDD uniquement
6. ⚙️ Configuration personnalisée
7. 📋 Status et diagnostics
8. 🧹 Nettoyage données temporaires

## 📊 Étapes du pipeline

### Étape 1 : 📡 Récupération API
- **Sources** : Google Books API, OpenLibrary API
- **Données** : Métadonnées livres (titre, auteur, ISBN, etc.)
- **Format** : Fichiers JSON par catégorie
- **Durée** : 10-30 minutes selon configuration

### Étape 2 : 🕷️ Scrapping Babelio
- **Source** : Site web Babelio.com
- **Données** : Critiques, notes, répartition étoiles
- **Format** : Fichiers JSON
- **Durée** : 20-120 minutes selon nombre de livres

### Étape 3 : 📊 Nettoyage CSV
- **Entrée** : Fichiers CSV bruts (OpenLibrary, exports)
- **Traitement** : Déduplication, validation, formatage
- **Sortie** : CSV nettoyés, prêts pour BDD
- **Durée** : 5-15 minutes

### Étape 4 : 🗄️ Import PostgreSQL
- **Tables créées** : livre, auteur, editeur, langue, sujet + tables de liaison
- **Schéma** : Relationnel normalisé
- **Performance** : ~1000 livres/minute
- **Durée** : 10-60 minutes selon volume

### Étape 5 : 🍃 Import MongoDB
- **Collection** : livres (documents JSON)
- **Structure** : Documents dénormalisés
- **Index** : titre, auteurs
- **Durée** : 5-20 minutes

## 🛠️ Configuration personnalisée

### Fichier de configuration
Créez `config_pipeline.json` :

```json
{
  "api": {
    "max_livres_par_categorie": 1000,
    "categories_actives": 20,
    "delai_requetes": 2
  },
  "scrapping": {
    "max_livres_babelio": 500,
    "delai_scrapping": 3
  },
  "bdd": {
    "postgresql_url": "postgresql://user:pass@localhost:5432/databook",
    "mongodb_url": "mongodb://localhost:27017/",
    "schema_postgres": "mon_schema",
    "batch_size": 1000
  }
}
```

### Variables d'environnement
```bash
export DATABOOK_POSTGRES_URL="postgresql://..."
export DATABOOK_MONGO_URL="mongodb://..."
export DATABOOK_API_MAX_BOOKS=1000
```

## 📋 Monitoring et logs

### Logs automatiques
- **Fichier** : `pipeline_master_YYYYMMDD_HHMMSS.log`
- **Format** : Timestamp, niveau, message
- **Niveaux** : INFO, WARNING, ERROR

### Rapport final
- **Fichier** : `rapport_pipeline_YYYYMMDD_HHMMSS.json`
- **Contenu** : Configuration, résultats, erreurs, durées

### Vérification status
```bash
python demarrage_rapide.py --status
```

## 🚨 Résolution des problèmes

### Erreurs courantes

#### Modules manquants
```bash
pip install requests pandas beautifulsoup4 sqlalchemy psycopg2-binary pymongo
```

#### PostgreSQL inaccessible
- Vérifier que PostgreSQL est démarré
- Contrôler l'URL de connexion
- Tester : `psql -h localhost -U postgres`

#### MongoDB inaccessible
- Vérifier que MongoDB est démarré
- Contrôler l'URL de connexion  
- Tester : `mongo --host localhost:27017`

#### Espace disque insuffisant
- Minimum recommandé : 5 GB libre
- Utiliser configuration "minimale"
- Nettoyer fichiers temporaires

#### Timeouts API
- Réduire `max_livres_par_categorie`
- Augmenter `delai_requetes`
- Relancer étape API individuellement

### Récupération après erreur

```python
# Reprendre à partir d'une étape spécifique
pipeline = PipelineMaster()

# Par exemple, reprendre au nettoyage CSV
pipeline.executer_etape_nettoyage_csv()
pipeline.executer_etape_postgresql()
pipeline.executer_etape_mongodb()
```

### Nettoyage et reset

```bash
# Nettoyer fichiers temporaires
python pipeline_master.py  # Option 8

# Reset complet (supprimer toutes les données)
rm -rf data/livre_json/*
rm -f *.log *.json
```

## 📈 Optimisations

### Performance
- **CPU** : Scripts parallélisés automatiquement
- **Mémoire** : Traitement par lots (batch_size configurable)
- **Réseau** : Délais configurables pour éviter rate limiting

### Espace disque
- Configuration minimale : ~100 MB
- Configuration standard : ~1 GB  
- Configuration complète : ~5 GB

### Personnalisation avancée

#### Modifier les catégories API
Éditez `scripts/api/recupération_api_livre_amelioree.py` :
```python
categories_etendues = [
    {"fr": "Ma catégorie", "en": "My category", "variations": ["keyword1", "keyword2"]}
]
```

#### Ajouter sources de données
1. Créer script dans `scripts/api/`
2. Modifier `pipeline_master.py` pour inclure le script
3. Ajouter configuration correspondante

## 🎓 Exemples d'usage

### Recherche académique
```bash
python demarrage_rapide.py --config standard
# Données équilibrées pour analyses statistiques
```

### Développement d'application
```bash
python demarrage_rapide.py --config minimal
# Tests rapides pendant développement
```

### Production / Analytics
```bash
python demarrage_rapide.py --config complet
# Maximum de données pour ML/BI
```

### Usage ponctuel API
```python
from pipeline_master import PipelineMaster
pipeline = PipelineMaster()
pipeline.config['api']['max_livres_par_categorie'] = 50
pipeline.executer_etape_api()
```

## 📞 Support

### Diagnostics automatiques
```bash
python demarrage_rapide.py --status
```

### Logs détaillés
```bash
tail -f pipeline_master_*.log
```

### Vérification environnement
```python
from pipeline_master import PipelineMaster
pipeline = PipelineMaster()
pipeline.verifier_environnement()
```

---

## 📝 Notes importantes

- ⚠️ **Respect des APIs** : Les délais entre requêtes sont configurés pour respecter les limites des services
- 🔒 **Données personnelles** : Aucune donnée personnelle n'est collectée ni stockée
- 📊 **Usage académique** : Pipeline conçu pour la recherche et l'éducation
- 🔄 **Mises à jour** : Scripts mis à jour régulièrement pour s'adapter aux évolutions des APIs

---

*Guide Pipeline DataBook v1.0 - 2025-01-27* 