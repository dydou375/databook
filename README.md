# Contexte ;

Le but est de fournir un accès libre et rapide (interfaces etc...), une analyse poussé sur différents sujets (thèmes, pages, etc...) et de fournir une base de données complètes contenant énormément de livres, avec leur itérations (nombres de parutions), les langues éditées, la possibilité de l'acquérir, les avis et notes présents sur différents sites. Nous pouvons aussi contenir les différentes images de couvertures pour avoir un visuel en plus lors de l'affichage.

# Objectif :
- Fournir une base de données complètes contenant énormément de livres, avec leur itérations (nombres de parutions), les langues éditées, la possibilité de l'acquérir, les avis et notes présents sur différents sites. Nous pouvons aussi contenir les différentes images de couvertures pour avoir un visuel en plus lors de l'affichage.

# Schema fonctionnel :

![Schema fonctionnel](schema/schema_fonctionnel.png)

# Sources de données externe :
	- API;
		- Open Library : documenté (dernier mise a jour de l'api : 7 mai 2025) -> infos sur les livres, auteurs…
			liens : https://openlibrary.org
		- Googles book api : documenté -> avis, notes, résumé
			liens : documentation et utilisation : https://developers.google.com/books/docs/v1/using?hl=fr

	- Web scrapping;
		- Babelio : Critiques de lecteurs, notes, listes thématiques (permettre une comparaison de différents sites pour les notes et faire une note globales)
			Liens : https://www.babelio.com
		- Goodreads : APi limité donc web scrapping plus pertinents -> citations etc...
			Liens : https://www.goodreads.com

	- Fichiers CSV, TSV : Recuperer sur différents sites -> a etudier plus en details (kaggles, etc...)

	- Big data :
		- Googles big query : datasets public sur auteurs, critiques, avis, etc...

# Sources de données interne :
- Bases de données relationnels : nettoyer et aplanir les données pour ensuite les agréger en quelque choses d'exploitable et de cohérent pour analyse et requêtes

## MCD (Mermaid)

```mermaid
erDiagram
    LIVRE {
        int id_livre PK
        string titre
        int annee_publication
        string isbn
        string description
        int nombre_pages
        string url_couverture
        string url_openlibrary
        string url_googlebooks
        string url_babelio
        string url_goodreads
        float note_moyenne
        int nombre_avis
        string statut_acquisition
        string date_ajout
        string date_modification
    }
    AUTEUR {
        int id_auteur PK
        string nom
        string url_openlibrary
        string url_googlebooks
        string url_babelio
        string url_goodreads
        string date_ajout
        string date_modification
    }
    EDITEUR {
        int id_editeur PK
        string nom
        string url_openlibrary
        string url_googlebooks
        string url_babelio
        string url_goodreads
        string date_ajout
        string date_modification
    }
    LANGUE {
        int id_langue PK
        string code
        string nom
        string date_ajout
        string date_modification
    }
    SUJET {
        int id_sujet PK
        string nom
        string date_ajout
        string date_modification
    }
    LIVRE_AUTEUR {
        int id_livre PK,FK
        int id_auteur PK,FK
        string date_ajout
        string date_modification
    }
    LIVRE_EDITEUR {
        int id_livre PK,FK
        int id_editeur PK,FK
        string date_ajout
        string date_modification
    }
    LIVRE_LANGUE {
        int id_livre PK,FK
        int id_langue PK,FK
        string date_ajout
        string date_modification
    }
    LIVRE_SUJET {
        int id_livre PK,FK
        int id_sujet PK,FK
        string date_ajout
        string date_modification
    }
    EXTRACTION_LOG {
        int id_log PK
        string nom_fichier
        int nombre_lignes
        string date_extraction
        string statut
        string message
    }

    LIVRE ||--o{ LIVRE_AUTEUR : "a"
    AUTEUR ||--o{ LIVRE_AUTEUR : "écrit"
    LIVRE ||--o{ LIVRE_EDITEUR : "publié par"
    EDITEUR ||--o{ LIVRE_EDITEUR : "publie"
    LIVRE ||--o{ LIVRE_LANGUE : "disponible en"
    LANGUE ||--o{ LIVRE_LANGUE : "utilisée dans"
    LIVRE ||--o{ LIVRE_SUJET : "traite de"
    SUJET ||--o{ LIVRE_SUJET : "apparaît dans"
```

## Architecture logique :

data_book
├───data
│   ├───raw
│   ├───processed
│   └───cleaned
├───src
├───docs
└───README.md


