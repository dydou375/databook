# 📊 DataBook - Diagrammes Mermaid

Ce fichier contient tous les diagrammes Mermaid pour le projet DataBook : MLD et MPD.

## 📋 MLD (Modèle Logique de Données)

### Description
Le MLD représente la structure logique des données avec les relations entre les entités, indépendamment du SGBD.

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
        datetime date_ajout
        datetime date_modification
    }
    
    AUTEUR {
        int id_auteur PK
        string nom
        string url_openlibrary
        string url_googlebooks
        string url_babelio
        string url_goodreads
        datetime date_ajout
        datetime date_modification
    }
    
    EDITEUR {
        int id_editeur PK
        string nom
        string url_openlibrary
        string url_googlebooks
        string url_babelio
        string url_goodreads
        datetime date_ajout
        datetime date_modification
    }
    
    LANGUE {
        int id_langue PK
        string code
        string nom
        datetime date_ajout
        datetime date_modification
    }
    
    SUJET {
        int id_sujet PK
        string nom
        datetime date_ajout
        datetime date_modification
    }
    
    LIVRE_AUTEUR {
        int id_livre PK,FK
        int id_auteur PK,FK
        datetime date_ajout
        datetime date_modification
    }
    
    LIVRE_EDITEUR {
        int id_livre PK,FK
        int id_editeur PK,FK
        datetime date_ajout
        datetime date_modification
    }
    
    LIVRE_LANGUE {
        int id_livre PK,FK
        int id_langue PK,FK
        datetime date_ajout
        datetime date_modification
    }
    
    LIVRE_SUJET {
        int id_livre PK,FK
        int id_sujet PK,FK
        datetime date_ajout
        datetime date_modification
    }

    LIVRE ||--o{ LIVRE_AUTEUR : "id_livre"
    AUTEUR ||--o{ LIVRE_AUTEUR : "id_auteur"
    LIVRE ||--o{ LIVRE_EDITEUR : "id_livre"
    EDITEUR ||--o{ LIVRE_EDITEUR : "id_editeur"
    LIVRE ||--o{ LIVRE_LANGUE : "id_livre"
    LANGUE ||--o{ LIVRE_LANGUE : "id_langue"
    LIVRE ||--o{ LIVRE_SUJET : "id_livre"
    SUJET ||--o{ LIVRE_SUJET : "id_sujet"
```

## 🗄️ MPD (Modèle Physique de Données) - PostgreSQL

### Description
Le MPD représente l'implémentation physique avec les types de données PostgreSQL, contraintes et optimisations.

```mermaid
erDiagram
    LIVRE {
        SERIAL id_livre PK "PRIMARY KEY"
        VARCHAR_500 titre "NOT NULL"
        INTEGER annee_publication "CHECK (annee_publication > 0)"
        VARCHAR_20 isbn "UNIQUE INDEX"
        TEXT description
        INTEGER nombre_pages "CHECK (nombre_pages > 0)"
        VARCHAR_500 url_couverture
        VARCHAR_500 url_openlibrary
        VARCHAR_500 url_googlebooks
        VARCHAR_500 url_babelio
        VARCHAR_500 url_goodreads
        DECIMAL_3_1 note_moyenne "CHECK (note_moyenne >= 0 AND note_moyenne <= 10)"
        INTEGER nombre_avis "DEFAULT 0"
        VARCHAR_50 statut_acquisition "DEFAULT 'disponible'"
        TIMESTAMP date_ajout "DEFAULT CURRENT_TIMESTAMP"
        TIMESTAMP date_modification "DEFAULT CURRENT_TIMESTAMP"
    }
    
    AUTEUR {
        SERIAL id_auteur PK "PRIMARY KEY"
        VARCHAR_200 nom "NOT NULL INDEX"
        VARCHAR_500 url_openlibrary
        VARCHAR_500 url_googlebooks
        VARCHAR_500 url_babelio
        VARCHAR_500 url_goodreads
        TIMESTAMP date_ajout "DEFAULT CURRENT_TIMESTAMP"
        TIMESTAMP date_modification "DEFAULT CURRENT_TIMESTAMP"
    }
    
    EDITEUR {
        SERIAL id_editeur PK "PRIMARY KEY"
        VARCHAR_200 nom "NOT NULL INDEX"
        VARCHAR_500 url_openlibrary
        VARCHAR_500 url_googlebooks
        VARCHAR_500 url_babelio
        VARCHAR_500 url_goodreads
        TIMESTAMP date_ajout "DEFAULT CURRENT_TIMESTAMP"
        TIMESTAMP date_modification "DEFAULT CURRENT_TIMESTAMP"
    }
    
    LANGUE {
        SERIAL id_langue PK "PRIMARY KEY"
        VARCHAR_10 code "NOT NULL UNIQUE"
        VARCHAR_100 nom "NOT NULL"
        TIMESTAMP date_ajout "DEFAULT CURRENT_TIMESTAMP"
        TIMESTAMP date_modification "DEFAULT CURRENT_TIMESTAMP"
    }
    
    SUJET {
        SERIAL id_sujet PK "PRIMARY KEY"
        VARCHAR_200 nom "NOT NULL INDEX"
        TIMESTAMP date_ajout "DEFAULT CURRENT_TIMESTAMP"
        TIMESTAMP date_modification "DEFAULT CURRENT_TIMESTAMP"
    }
    
    LIVRE_AUTEUR {
        INTEGER id_livre PK,FK "REFERENCES LIVRE(id_livre) ON DELETE CASCADE"
        INTEGER id_auteur PK,FK "REFERENCES AUTEUR(id_auteur) ON DELETE CASCADE"
        TIMESTAMP date_ajout "DEFAULT CURRENT_TIMESTAMP"
        TIMESTAMP date_modification "DEFAULT CURRENT_TIMESTAMP"
    }
    
    LIVRE_EDITEUR {
        INTEGER id_livre PK,FK "REFERENCES LIVRE(id_livre) ON DELETE CASCADE"
        INTEGER id_editeur PK,FK "REFERENCES EDITEUR(id_editeur) ON DELETE CASCADE"
        TIMESTAMP date_ajout "DEFAULT CURRENT_TIMESTAMP"
        TIMESTAMP date_modification "DEFAULT CURRENT_TIMESTAMP"
    }
    
    LIVRE_LANGUE {
        INTEGER id_livre PK,FK "REFERENCES LIVRE(id_livre) ON DELETE CASCADE"
        INTEGER id_langue PK,FK "REFERENCES LANGUE(id_langue) ON DELETE CASCADE"
        TIMESTAMP date_ajout "DEFAULT CURRENT_TIMESTAMP"
        TIMESTAMP date_modification "DEFAULT CURRENT_TIMESTAMP"
    }
    
    LIVRE_SUJET {
        INTEGER id_livre PK,FK "REFERENCES LIVRE(id_livre) ON DELETE CASCADE"
        INTEGER id_sujet PK,FK "REFERENCES SUJET(id_sujet) ON DELETE CASCADE"
        TIMESTAMP date_ajout "DEFAULT CURRENT_TIMESTAMP"
        TIMESTAMP date_modification "DEFAULT CURRENT_TIMESTAMP"
    }

    LIVRE ||--o{ LIVRE_AUTEUR : "FK CASCADE"
    AUTEUR ||--o{ LIVRE_AUTEUR : "FK CASCADE"
    LIVRE ||--o{ LIVRE_EDITEUR : "FK CASCADE"
    EDITEUR ||--o{ LIVRE_EDITEUR : "FK CASCADE"
    LIVRE ||--o{ LIVRE_LANGUE : "FK CASCADE"
    LANGUE ||--o{ LIVRE_LANGUE : "FK CASCADE"
    LIVRE ||--o{ LIVRE_SUJET : "FK CASCADE"
    SUJET ||--o{ LIVRE_SUJET : "FK CASCADE"
```

## 🏗️ Architecture système (Vue d'ensemble)

### Description
Diagramme de l'architecture générale du système DataBook avec les sources de données et les APIs.

```mermaid
graph TB
    subgraph "Sources Externes"
        A[Google Books API]
        B[Open Library API]
        C[Babelio Scraping]
        D[Fichiers CSV/Dumps]
    end
    
    subgraph "ETL Pipeline"
        E[Scripts Python]
        F[Validation & Nettoyage]
        G[Agrégation]
    end
    
    subgraph "Stockage"
        H[(PostgreSQL<br/>Données relationnelles)]
        I[(MongoDB<br/>41,100 livres)]
    end
    
    subgraph "API Layer"
        J[FastAPI<br/>40+ endpoints]
        K[Authentification JWT]
    end
    
    subgraph "Applications"
        L[Interface Streamlit]
        M[Documentation Swagger]
        N[Applications tierces]
    end
    
    A --> E
    B --> E
    C --> E
    D --> E
    
    E --> F
    F --> G
    
    G --> H
    G --> I
    
    H --> J
    I --> J
    
    J --> K
    K --> L
    K --> M
    K --> N
    
    style H fill:#e1f5fe
    style I fill:#f3e5f5
    style J fill:#e8f5e8
    style L fill:#fff3e0
```

## 📱 Flow des données (Flux principal)

### Description
Diagramme du flux de données depuis l'extraction jusqu'à l'utilisation finale.

```mermaid
flowchart TD
    Start([Démarrage ETL]) --> Extract{Extraction}
    
    Extract -->|APIs| ExtractAPI[Google Books<br/>Open Library]
    Extract -->|Scraping| ExtractWeb[Babelio<br/>Critiques]
    Extract -->|Fichiers| ExtractFiles[Dumps JSON<br/>CSV Kaggle]
    
    ExtractAPI --> Transform[Transformation<br/>& Validation]
    ExtractWeb --> Transform
    ExtractFiles --> Transform
    
    Transform --> Clean[Nettoyage<br/>Déduplication]
    Clean --> Normalize[Normalisation<br/>Homogénéisation]
    
    Normalize --> LoadDecision{Choix stockage}
    LoadDecision -->|Structuré| LoadPG[(PostgreSQL<br/>Relations)]
    LoadDecision -->|Documents| LoadMongo[(MongoDB<br/>41,100 livres)]
    
    LoadPG --> API[FastAPI<br/>Endpoints]
    LoadMongo --> API
    
    API --> Auth[Authentification<br/>JWT]
    Auth --> Apps[Applications<br/>Interface]
    
    Apps --> End([Utilisation finale])
    
    style Extract fill:#ffeb3b
    style Transform fill:#ff9800
    style LoadPG fill:#2196f3
    style LoadMongo fill:#9c27b0
    style API fill:#4caf50
    style Apps fill:#f44336
```

## 🔧 Index et Optimisations

### Description
Diagramme des index et optimisations appliquées sur la base PostgreSQL.

```mermaid
graph LR
    subgraph "Table LIVRE"
        L1[idx_livre_titre<br/>B-Tree]
        L2[idx_livre_isbn<br/>Unique]
        L3[idx_livre_annee<br/>B-Tree]
        L4[idx_livre_note<br/>B-Tree]
    end
    
    subgraph "Table AUTEUR"
        A1[idx_auteur_nom<br/>B-Tree]
        A2[idx_auteur_nom_gin<br/>Full-text French]
    end
    
    subgraph "Tables de liaison"
        LA1[idx_livre_auteur_livre]
        LA2[idx_livre_auteur_auteur]
        LE1[idx_livre_editeur_livre]
        LE2[idx_livre_editeur_editeur]
        LL1[idx_livre_langue_livre]
        LL2[idx_livre_langue_langue]
        LS1[idx_livre_sujet_livre]
        LS2[idx_livre_sujet_sujet]
    end
    
    subgraph "Performance"
        P1[Recherche rapide<br/>par titre/ISBN]
        P2[Recherche textuelle<br/>auteurs français]
        P3[Jointures optimisées<br/>relations N-N]
    end
    
    L1 --> P1
    L2 --> P1
    A2 --> P2
    LA1 --> P3
    LA2 --> P3
    LE1 --> P3
    LE2 --> P3
    
    style P1 fill:#c8e6c9
    style P2 fill:#dcedc8
    style P3 fill:#f8bbd9
```

## 📝 Utilisation

### Comment utiliser ces diagrammes

1. **Copier le code Mermaid** de la section souhaitée
2. **Coller dans un éditeur Mermaid** (GitLab, GitHub, VS Code avec extension, etc.)
3. **Ou utiliser les outils en ligne** comme [Mermaid Live Editor](https://mermaid.live/)

### Intégration dans la documentation

Ces diagrammes peuvent être intégrés dans :
- **README.md** du projet
- **Documentation technique**
- **Rapports** (comme votre rapport de formation)
- **Présentations** techniques

### Modification

Pour modifier les diagrammes :
1. Éditer le code Mermaid correspondant
2. Tester avec Mermaid Live Editor
3. Mettre à jour ce fichier

---

**Projet DataBook** - Diagrammes générés pour 41,100 livres et architecture PostgreSQL + MongoDB 