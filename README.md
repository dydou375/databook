# Contexte ;

Le but est de fournir un accès libre et rapide (interfaces etc...), une analyse poussé sur différents sujets (thèmes, pages, etc...) et de fournir une base de données complètes contenant énormément de livres, avec leur itérations (nombres de parutions), les langues éditées, la possibilité de l'acquérir, les avis et notes présents sur différents sites. Nous pouvons aussi contenir les différentes images de couvertures pour avoir un visuel en plus lors de l'affichage.

# Objectif :
- Fournir une base de données complètes contenant énormément de livres, avec leur itérations (nombres de parutions), les langues éditées, la possibilité de l'acquérir, les avis et notes présents sur différents sites. Nous pouvons aussi contenir les différentes images de couvertures pour avoir un visuel en plus lors de l'affichage.

# Schema fonctionnel :

![Schema fonctionnel](schema_fonctionnel.png)
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

![Diagramme ERD](schema/MCD.png)


```mermaid
erDiagram
    LIVRE {
        int id_livre PK
        string titre
        date date_publication
        string isbn
        string langue
        string description
        float note_moyenne
        int nb_pages
        string couverture_url
    }
    AUTEUR {
        int id_auteur PK
        string nom
        date date_naissance
        string biographie
    }
    GENRE {
        int id_genre PK
        string nom_genre
    }
    UTILISATEUR {
        int id_utilisateur PK
        string pseudo
        date date_inscription
        string pays
    }
    CRITIQUE {
        int id_critique PK
        int id_utilisateur FK
        int id_livre FK
        float note
        string commentaire
        date date_critique
    }
    LIVRE_AUTEUR {
        int id_livre PK, FK
        int id_auteur PK, FK
    }
    LIVRE_GENRE {
        int id_livre PK, FK
        int id_genre PK, FK
    }

    LIVRE ||--o{ LIVRE_AUTEUR : ""
    AUTEUR ||--o{ LIVRE_AUTEUR : ""
    LIVRE ||--o{ LIVRE_GENRE : ""
    GENRE ||--o{ LIVRE_GENRE : ""
    UTILISATEUR ||--o{ CRITIQUE : ""
    LIVRE ||--o{ CRITIQUE : ""
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


