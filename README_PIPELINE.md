# 🚀 PIPELINE MASTER DATABOOK

Un système automatisé complet pour la récupération et le traitement des données de livres.

## 🎯 Qu'est-ce que c'est ?

Le **Pipeline DataBook** est un système qui automatise entièrement la chaîne de traitement des données de votre projet d'analyse de livres :

1. **📡 Récupération automatique** depuis les APIs (Google Books, OpenLibrary)
2. **🕷️ Scrapping intelligent** des critiques (Babelio)
3. **📊 Nettoyage et formatage** des données CSV
4. **🗄️ Import automatique** vers PostgreSQL et MongoDB
5. **✅ Validation et monitoring** complets

## ⚡ Démarrage ultra-rapide

```bash
# Test et lancement automatique
python test_pipeline.py --rapide
python demarrage_rapide.py --auto

# Ou démarrage interactif
python pipeline_master.py
```

## 📋 Ce qui a été créé

### 🎯 Scripts principaux
- **`pipeline_master.py`** : Script principal avec menu interactif
- **`demarrage_rapide.py`** : Lancement automatique avec détection environnement
- **`test_pipeline.py`** : Tests complets de validation

### ⚙️ Configuration
- **`config_pipeline.json`** : Configuration complète du pipeline
- **`GUIDE_PIPELINE.md`** : Guide détaillé d'utilisation

### 🔧 Fonctionnalités

#### 🤖 Détection automatique
- ✅ Modules Python installés
- ✅ Structure des dossiers
- ✅ Connexions aux bases de données
- ✅ Espace disque disponible
- ✅ Recommandations automatiques

#### 📊 3 configurations prêtes
- **🚀 Minimale** : 100 livres, tests rapides (5-10 min)
- **📊 Standard** : 1000 livres, usage normal (30-60 min)  
- **🎯 Complète** : 5000+ livres, production (2-4h)

#### 🔄 Exécution flexible
- **Pipeline complet** : Toutes les étapes en une fois
- **Étapes individuelles** : API, scrapping, BDD séparément
- **Mode interactif** : Menu avec choix utilisateur
- **Mode automatique** : Zero configuration

#### 📋 Monitoring avancé
- **Logs détaillés** : Timestamp, niveaux, messages
- **Rapports JSON** : Statistiques, erreurs, durées
- **Progression en temps réel** : Affichage étape par étape

## 🚀 Utilisation

### Option 1 : Le plus simple
```bash
python demarrage_rapide.py --auto
```
→ Détection automatique + configuration optimale + lancement

### Option 2 : Avec choix de configuration
```bash
python demarrage_rapide.py --auto --config standard
```

### Option 3 : Menu interactif complet
```bash
python pipeline_master.py
```
→ Menu avec 9 options (pipeline complet, étapes individuelles, diagnostics...)

### Option 4 : Tests avant utilisation
```bash
python test_pipeline.py --complet
```

## 📊 Qu'est-ce que ça fait concrètement ?

### Étape 1 : 📡 Récupération API (10-30 min)
- **Depuis Google Books** : Métadonnées livres par catégories
- **Depuis OpenLibrary** : Données bibliographiques étendues
- **Résultat** : Fichiers JSON organisés par source et catégorie

### Étape 2 : 🕷️ Scrapping Babelio (20-120 min)
- **Recherche par ISBN** depuis vos données existantes
- **Extraction** : Critiques, notes, répartition étoiles
- **Résultat** : Fichiers JSON avec données sociales

### Étape 3 : 📊 Nettoyage CSV (5-15 min)
- **Déduplication** automatique
- **Validation** : ISBN, dates, formats
- **Normalisation** : Encodage, structure
- **Résultat** : CSV propres prêts pour BDD

### Étape 4 : 🗄️ Import PostgreSQL (10-60 min)
- **Tables relationnelles** : livre, auteur, editeur, langue, sujet
- **Relations** : Tables de liaison automatiques
- **Performance** : ~1000 livres/minute
- **Résultat** : Base relationnelle normalisée

### Étape 5 : 🍃 Import MongoDB (5-20 min)
- **Documents JSON** : Structure dénormalisée
- **Index automatiques** : titre, auteurs, ISBN
- **Collections** : livres avec données complètes
- **Résultat** : Base NoSQL pour requêtes rapides

## 🛠️ Configuration automatique

Le système s'adapte automatiquement à votre environnement :

### 🔍 Détection intelligente
- **Modules manquants** → Proposition d'installation automatique
- **Espace disque limité** → Configuration minimale recommandée
- **BDD inaccessibles** → Adaptation du pipeline
- **Erreurs réseau** → Retry automatique avec délais

### ⚙️ 3 niveaux de configuration

| Configuration | Livres API | Scrapping | Durée | Espace | Usage |
|---------------|------------|-----------|-------|--------|-------|
| **🚀 Minimale** | 100 | 50 | 5-10 min | ~50 MB | Tests, développement |
| **📊 Standard** | 1000 | 500 | 30-60 min | ~500 MB | Démos, analyses |
| **🎯 Complète** | 5000+ | 2000+ | 2-4h | ~2 GB | Production, ML |

## 📁 Structure créée

```
databook/
├── 🎯 pipeline_master.py          # Script principal 
├── 🚀 demarrage_rapide.py         # Lancement auto
├── 🧪 test_pipeline.py            # Tests validation
├── ⚙️ config_pipeline.json        # Configuration
├── 📖 GUIDE_PIPELINE.md           # Guide détaillé
├── 📄 README_PIPELINE.md          # Ce fichier
│
├── scripts/                       # Vos scripts existants
│   ├── api/                      # Récupération API
│   └── scrapping/                # Scrapping web
│
├── bdd/                          # Scripts base de données
│   ├── livres/                   # PostgreSQL
│   └── nosql/                    # MongoDB
│
└── data/                         # Données générées
    ├── livre_json/               # Fichiers JSON
    └── *.csv                     # Fichiers CSV
```

## 🔧 Personnalisation

### Modifier les limites
```python
# Dans pipeline_master.py ou config_pipeline.json
config['api']['max_livres_par_categorie'] = 2000
config['scrapping']['max_livres_babelio'] = 1000
```

### Ajouter une source de données
1. Créer script dans `scripts/api/mon_nouveau_script.py`
2. Modifier `pipeline_master.py` pour l'inclure
3. Ajouter configuration dans `config_pipeline.json`

### Changer les bases de données
```json
{
  "bdd": {
    "postgresql": {
      "url": "postgresql://user:pass@server:5432/db"
    },
    "mongodb": {
      "url": "mongodb://server:27017/"
    }
  }
}
```

## 🚨 Résolution des problèmes

### ❌ Modules manquants
```bash
pip install requests pandas beautifulsoup4 sqlalchemy psycopg2-binary pymongo
```

### ❌ Bases de données inaccessibles
- PostgreSQL : Vérifier que le service est démarré
- MongoDB : Vérifier la connexion avec `mongo --host localhost:27017`

### ❌ Timeouts API
- Réduire `max_livres_par_categorie` dans la config
- Augmenter `delai_requetes` pour éviter le rate limiting

### ❌ Espace disque insuffisant
- Utiliser configuration "minimale"
- Nettoyer avec : `python pipeline_master.py` → Option 8

## 📊 Monitoring et rapports

### Logs automatiques
- **Fichier** : `pipeline_master_YYYYMMDD_HHMMSS.log`
- **Contenu** : Progression, erreurs, statistiques

### Rapports JSON
- **Fichier** : `rapport_pipeline_YYYYMMDD_HHMMSS.json`
- **Contenu** : Configuration, résultats, durées, erreurs

### Diagnostics
```bash
python demarrage_rapide.py --status
python test_pipeline.py --rapide
```

## 🎓 Exemples d'usage

### Développement rapide
```bash
python demarrage_rapide.py --config minimal
# 100 livres en 10 minutes pour tests
```

### Démonstration
```bash
python demarrage_rapide.py --config standard  
# 1000 livres en 1 heure pour présentation
```

### Production
```bash
python demarrage_rapide.py --config complet
# 5000+ livres en quelques heures pour analyses
```

### Tests uniquement
```bash
python test_pipeline.py --complet
# Validation complète avant utilisation
```

## 🔄 Workflow recommandé

### 1️⃣ Première utilisation
```bash
# Tests pour validation
python test_pipeline.py --rapide

# Si OK, lancement minimal pour test
python demarrage_rapide.py --config minimal

# Si tout fonctionne, configuration standard
python demarrage_rapide.py --config standard
```

### 2️⃣ Utilisation régulière
```bash
# Lancement automatique optimal
python demarrage_rapide.py --auto
```

### 3️⃣ Maintenance
```bash
# Diagnostics
python demarrage_rapide.py --status

# Tests complets
python test_pipeline.py --complet

# Nettoyage
python pipeline_master.py  # Option 8
```

## 📈 Performances attendues

### Récupération API
- **Google Books** : ~40 livres/requête, 1 requête/2s
- **OpenLibrary** : ~100 livres/requête, 1 requête/3s
- **Débit moyen** : ~1000 livres/heure

### Scrapping Babelio
- **Recherche** : 1 livre/3s avec délais
- **Extraction** : Métadonnées + critiques + notes
- **Débit moyen** : ~500 livres/heure

### Import bases de données
- **PostgreSQL** : ~1000 livres/minute
- **MongoDB** : ~2000 documents/minute

## 🏆 Avantages du pipeline

### ✅ Pour vous
- **Zéro configuration** : Détection automatique
- **Gain de temps énorme** : Heures → Minutes
- **Fiabilité** : Gestion d'erreurs, retry automatique
- **Flexibilité** : Étapes individuelles ou complètes

### ✅ Pour votre projet
- **Données cohérentes** : Format standardisé
- **Volume important** : Milliers de livres facilement
- **Sources multiples** : APIs + scrapping combinés
- **Prêt pour analyse** : BDD relationnelle + NoSQL

### ✅ Pour la maintenance
- **Logs détaillés** : Debugging facile
- **Rapports automatiques** : Monitoring inclus
- **Tests intégrés** : Validation continue
- **Documentation complète** : Guide + exemples

---

## 🚀 Commencez maintenant !

```bash
# 1. Tests rapides (2 minutes)
python test_pipeline.py --rapide

# 2. Premier essai (10 minutes)  
python demarrage_rapide.py --config minimal

# 3. Si satisfait, configuration complète
python demarrage_rapide.py --auto
```

**🎯 Résultat** : Des milliers de livres avec métadonnées, critiques et données structurées, prêts pour vos analyses !

---

*Pipeline DataBook v1.0 - Automatisation complète de la récupération de données* 