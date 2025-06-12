# Extracteur de Livres OpenLibrary

Ce projet contient des scripts Python pour extraire et analyser les informations de livres depuis les fichiers de données OpenLibrary.

## Fichiers

- **`extracteur_livres.py`** : Script principal contenant la classe `ExtracteurLivres`
- **`exemple_utilisation.py`** : Script d'exemple montrant comment utiliser l'extracteur
- **`analyse_csv_auteurs.ipynb`** : Notebook d'analyse original

## Fonctionnalités

### 🔍 Extraction de données
- Lecture des fichiers OpenLibrary (formats .txt et .gz)
- Extraction d'informations complètes sur les livres :
  - Titre, sous-titre
  - ISBN-10 et ISBN-13
  - Éditeurs
  - Date et année de publication
  - Nombre de pages
  - Langues
  - Auteurs
  - Description
  - Sujets
  - Format physique
  - Couvertures

### 📊 Filtrage avancé
- Filtrage par titre (obligatoire/optionnel)
- Filtrage par ISBN
- Filtrage par auteur
- Filtrage par plage d'années
- Filtrage par langues

### 📈 Analyse statistique
- Statistiques de qualité des métadonnées
- Répartition par décennie
- Top des langues et éditeurs
- Analyse des pages
- Score de qualité des livres

## Installation

### Prérequis
```bash
pip install pandas
```

### Configuration
Modifiez le chemin dans les scripts pour pointer vers vos fichiers OpenLibrary :
```python
chemin_openlibrary = r"C:\votre\chemin\vers\fichiers\openlibrary"
```

## Utilisation

### 1. Utilisation de base
```python
from extracteur_livres import ExtracteurLivres

# Créer l'extracteur
extracteur = ExtracteurLivres("chemin/vers/fichiers/openlibrary")

# Extraire 1000 livres
livres = extracteur.extraire_editions_echantillon(max_livres=1000)

# Analyser et sauvegarder
df = extracteur.analyser_livres_extraits(livres)
extracteur.sauvegarder_livres(df, "mes_livres.csv")
```

### 2. Utilisation avec critères
```python
# Définir des critères de filtrage
criteres = {
    'avec_titre': True,
    'avec_isbn': True,        # ISBN obligatoire
    'avec_auteur': True,      # Auteur obligatoire
    'annee_min': 2000,        # Livres depuis 2000
    'annee_max': 2024,        # Jusqu'à 2024
    'langues': ['eng', 'fre'] # Anglais et français seulement
}

# Extraire avec critères
livres = extracteur.extraire_editions_echantillon(
    max_livres=500, 
    criteres=criteres
)
```

### 3. Lancer les tests
```bash
python exemple_utilisation.py
```

## Structure des données extraites

Chaque livre extrait contient les champs suivants :

| Champ | Description |
|-------|-------------|
| `type_entree` | Type d'entrée (/type/edition) |
| `id_livre` | Identifiant unique OpenLibrary |
| `revision` | Numéro de révision |
| `timestamp` | Horodatage de dernière modification |
| `titre` | Titre du livre |
| `sous_titre` | Sous-titre |
| `isbn_10` | ISBN-10 |
| `isbn_13` | ISBN-13 |
| `editeurs` | Éditeurs (séparés par \|) |
| `date_publication` | Date de publication (texte) |
| `annee_publication` | Année de publication (numérique) |
| `nombre_pages` | Nombre de pages |
| `langues` | Langues (séparées par \|) |
| `auteurs` | Auteurs (IDs séparés par \|) |
| `oeuvres` | Œuvres liées (IDs séparés par \|) |
| `format_physique` | Format physique |
| `nom_edition` | Nom de l'édition |
| `description` | Description du livre |
| `sujets` | Sujets (séparés par \|) |
| `couvertures` | IDs des couvertures (séparés par \|) |
| `poids` | Poids du livre |
| `dimensions` | Dimensions |

## Tests inclus

Le script `exemple_utilisation.py` inclut plusieurs tests :

1. **Test basique** : Extraction simple avec critères minimaux
2. **Test avancé** : Extraction avec critères stricts
3. **Test de performance** : Extraction de 5000 livres avec mesure du temps
4. **Analyse personnalisée** : Exemples d'analyses statistiques

## Exemple de résultats

```
📊 ANALYSE DE 500 LIVRES EXTRAITS
============================================================
📏 Dimensions: 500 livres × 23 colonnes

📋 QUALITÉ DES MÉTADONNÉES:
   • titre               :    500 (100.0%)
   • annee_publication   :    484 ( 96.8%)
   • isbn_13             :    443 ( 88.6%)
   • isbn_10             :    485 ( 97.0%)
   • editeurs            :    494 ( 98.8%)
   • langues             :    330 ( 66.0%)
   • auteurs             :    412 ( 82.4%)
   • nombre_pages        :    335 ( 67.0%)
   • description         :     45 (  9.0%)

📅 ANNÉES DE PUBLICATION:
   • Plage: 1657 - 2014
   • Moyenne: 1995
   • Médiane: 1999

🌍 TOP 10 LANGUES:
   • eng         : 299 (90.6%)
   • spa         : 8 (2.4%)
   • fre         : 4 (1.2%)
```

## Dépannage

### Problèmes courants

1. **Fichier non trouvé** : Vérifiez le chemin vers les fichiers OpenLibrary
2. **Aucun livre extrait** : Les critères sont peut-être trop stricts
3. **Erreur de mémoire** : Réduisez le nombre de livres à extraire

### Performance

- **Petits tests** : 100-1000 livres
- **Analyses moyennes** : 5000-10000 livres  
- **Gros datasets** : 50000+ livres (selon votre RAM)

## Basé sur

Ce script est basé sur l'analyse du notebook `analyse_csv_auteurs.ipynb` qui contient l'exploration initiale des données OpenLibrary. 