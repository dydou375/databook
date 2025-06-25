# DATABOOK - DIAGRAMMES MERMAID
*Modèles de données basés sur la structure MongoDB existante*

---

## 1. MCD - MODÈLE CONCEPTUEL DE DONNÉES

```mermaid
erDiagram
    AUTEUR {
        int id "Identifiant unique"
        string nom "Nom de famille"
        string prenom "Prénom"
        string nom_complet "Nom complet formaté"
        date date_naissance "Date de naissance"
        date date_deces "Date de décès"
        text biographie "Biographie"
        timestamp created_at "Date de création"
    }
    
    EDITEUR {
        int id "Identifiant unique"
        string nom_editeur "Nom de l'éditeur"
        string pays "Pays d'origine"
        int annee_creation "Année de création"
        timestamp created_at "Date de création"
    }
    
    LIVRE {
        int id "Identifiant unique"
        string titre "Titre du livre"
        string sous_titre "Sous-titre"
        string isbn_10 "ISBN 10 digits"
        string isbn_13 "ISBN 13 digits"
        date date_publication "Date de publication"
        int annee_publication "Année de publication"
        int nombre_pages "Nombre de pages"
        string format_physique "Format physique"
        text description "Description du livre"
        string couverture_url "URL de la couverture"
        timestamp created_at "Date de création"
        timestamp updated_at "Date de mise à jour"
    }
    
    LANGUE {
        string code_langue "Code ISO langue"
        string nom_langue "Nom de la langue"
    }
    
    SUJET {
        int id "Identifiant unique"
        string nom_sujet "Nom du sujet"
        string categorie "Catégorie du sujet"
    }
    
    USERS {
        int id "Identifiant unique"
        string email "Adresse email"
        string first_name "Prénom"
        string last_name "Nom de famille"
        string hashed_password "Mot de passe hashé"
        boolean is_active "Statut actif"
        timestamp created_at "Date de création"
        timestamp updated_at "Date de mise à jour"
    }
    
    EXTRACTION_LOG {
        int id_log "Identifiant unique"
        string fichier_source "Fichier source"
        timestamp date_extraction "Date d'extraction"
        int nb_livres_extraits "Nombre de livres extraits"
        int nb_erreurs "Nombre d'erreurs"
        json statistiques_json "Statistiques JSON"
    }

    AUTEUR ||--o{ LIVRE : "ECRIRE"
    EDITEUR ||--o{ LIVRE : "PUBLIER"
    LANGUE ||--o{ LIVRE : "TRADUIRE"
    SUJET ||--o{ LIVRE : "TRAITER"
```

---

## 2. MLD - MODÈLE LOGIQUE DE DONNÉES

```mermaid
erDiagram
    AUTEUR {
        int id PK
        varchar nom
        varchar prenom  
        varchar nom_complet
        date date_naissance
        date date_deces
        text biographie
        timestamp created_at
    }
    
    EDITEUR {
        int id PK
        varchar nom_editeur
        varchar pays
        int annee_creation
        timestamp created_at
    }
    
    LIVRE {
        int id PK
        varchar titre
        varchar sous_titre
        varchar isbn_10 UK
        varchar isbn_13 UK
        date date_publication
        int annee_publication
        int nombre_pages
        varchar format_physique
        text description
        varchar couverture_url
        timestamp created_at
        timestamp updated_at
    }
    
    LANGUE {
        varchar code_langue PK
        varchar nom_langue
    }
    
    SUJET {
        int id PK
        varchar nom_sujet
        varchar categorie
    }
    
    USERS {
        int id PK
        varchar email UK
        varchar first_name
        varchar last_name
        varchar hashed_password
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    EXTRACTION_LOG {
        int id_log PK
        varchar fichier_source
        timestamp date_extraction
        int nb_livres_extraits
        int nb_erreurs
        json statistiques_json
    }
    
    LIVRE_AUTEUR {
        int id_livre FK
        int id_auteur FK
        varchar role
        int ordre
    }
    
    LIVRE_EDITEUR {
        int id_livre FK
        int id_editeur FK
        int ordre
    }
    
    LIVRE_LANGUE {
        int id_livre FK
        varchar id_langue FK
        boolean langue_principale
    }
    
    LIVRE_SUJET {
        int id_livre FK
        int id_sujet FK
        decimal pertinence
    }

    LIVRE ||--o{ LIVRE_AUTEUR : "id"
    AUTEUR ||--o{ LIVRE_AUTEUR : "id"
    LIVRE ||--o{ LIVRE_EDITEUR : "id"
    EDITEUR ||--o{ LIVRE_EDITEUR : "id"
    LIVRE ||--o{ LIVRE_LANGUE : "id"
    LANGUE ||--o{ LIVRE_LANGUE : "code_langue"
    LIVRE ||--o{ LIVRE_SUJET : "id"
    SUJET ||--o{ LIVRE_SUJET : "id"
```

---

## 3. MPD - MODÈLE PHYSIQUE DE DONNÉES (PostgreSQL)

```mermaid
erDiagram
    auteur {
        SERIAL id PK
        VARCHAR_255 nom
        VARCHAR_255 prenom
        VARCHAR_511 nom_complet
        DATE date_naissance
        DATE date_deces
        TEXT biographie
        TIMESTAMP created_at
    }
    
    editeur {
        SERIAL id PK
        VARCHAR_255 nom_editeur "NOT NULL"
        VARCHAR_100 pays
        INTEGER annee_creation
        TIMESTAMP created_at "DEFAULT CURRENT_TIMESTAMP"
    }
    
    livre {
        SERIAL id PK
        VARCHAR_500 titre "NOT NULL"
        VARCHAR_500 sous_titre
        VARCHAR_10 isbn_10 "UNIQUE"
        VARCHAR_13 isbn_13 "UNIQUE"
        DATE date_publication
        INTEGER annee_publication "CHECK 1000-2030"
        INTEGER nombre_pages "CHECK > 0"
        VARCHAR_50 format_physique
        TEXT description
        VARCHAR_1000 couverture_url
        TIMESTAMP created_at "DEFAULT CURRENT_TIMESTAMP"
        TIMESTAMP updated_at "DEFAULT CURRENT_TIMESTAMP"
    }
    
    langue {
        VARCHAR_10 code_langue PK
        VARCHAR_100 nom_langue "NOT NULL"
    }
    
    sujet {
        SERIAL id PK
        VARCHAR_255 nom_sujet "NOT NULL"
        VARCHAR_100 categorie
    }
    
    users {
        SERIAL id PK
        VARCHAR_255 email "UNIQUE NOT NULL"
        VARCHAR_100 first_name
        VARCHAR_100 last_name
        VARCHAR_255 hashed_password "NOT NULL"
        BOOLEAN is_active "DEFAULT TRUE"
        TIMESTAMP created_at "DEFAULT CURRENT_TIMESTAMP"
        TIMESTAMP updated_at "DEFAULT CURRENT_TIMESTAMP"
    }
    
    extraction_log {
        SERIAL id_log PK
        VARCHAR_255 fichier_source
        TIMESTAMP date_extraction "DEFAULT CURRENT_TIMESTAMP"
        INTEGER nb_livres_extraits "DEFAULT 0"
        INTEGER nb_erreurs "DEFAULT 0"
        JSONB statistiques_json
    }
    
    livre_auteur {
        INTEGER id_livre FK "NOT NULL"
        INTEGER id_auteur FK "NOT NULL"
        VARCHAR_50 role "DEFAULT 'auteur'"
        INTEGER ordre "DEFAULT 1"
    }
    
    livre_editeur {
        INTEGER id_livre FK "NOT NULL"
        INTEGER id_editeur FK "NOT NULL"
        INTEGER ordre "DEFAULT 1"
    }
    
    livre_langue {
        INTEGER id_livre FK "NOT NULL"
        VARCHAR_10 id_langue FK "NOT NULL"
        BOOLEAN langue_principale "DEFAULT FALSE"
    }
    
    livre_sujet {
        INTEGER id_livre FK "NOT NULL"
        INTEGER id_sujet FK "NOT NULL"
        DECIMAL_3_2 pertinence "DEFAULT 1.00, CHECK 0.00-1.00"
    }

    auteur ||--o{ livre_auteur : "id"
    livre ||--o{ livre_auteur : "id"
    editeur ||--o{ livre_editeur : "id"
    livre ||--o{ livre_editeur : "id"
    langue ||--o{ livre_langue : "code_langue"
    livre ||--o{ livre_langue : "id"
    sujet ||--o{ livre_sujet : "id"
    livre ||--o{ livre_sujet : "id"
```

---

## 4. ARCHITECTURE DES INDEX ET PERFORMANCES

```mermaid
graph TB
    subgraph "INDEX PRINCIPAUX"
        A[idx_livre_titre] --> B[Recherche par titre]
        C[idx_livre_isbn_13] --> D[Recherche par ISBN]
        E[idx_auteur_nom_complet] --> F[Recherche par auteur]
        G[idx_livre_annee_publication] --> H[Filtrage par année]
    end
    
    subgraph "INDEX COMPOSITES"
        I[idx_livre_auteur_composite] --> J[Jointures livre-auteur]
        K[idx_livre_sujet_pertinence] --> L[Tri par pertinence]
        M[idx_extraction_log_date] --> N[Historique extractions]
    end
    
    subgraph "CONTRAINTES MÉTIER"
        O[chk_annee_publication] --> P[Années valides 1000-2030]
        Q[chk_nombre_pages] --> R[Pages > 0]
        S[chk_dates_coherentes] --> T[Décès >= Naissance]
        U[chk_pertinence] --> V[Score 0.00-1.00]
    end
```

---

## 5. VUES ET FONCTIONS UTILITAIRES

```mermaid
graph LR
    subgraph "VUES MÉTIER"
        A[v_livres_detailles] --> B[Livres avec auteurs/éditeurs]
        C[v_stats_auteurs] --> D[Statistiques par auteur]
    end
    
    subgraph "FONCTIONS"
        E[recherche_livres] --> F[Recherche textuelle PostgreSQL]
        G[update_updated_at_column] --> H[Mise à jour automatique]
        I[generate_nom_complet] --> J[Génération nom complet]
    end
    
    subgraph "TRIGGERS"
        K[update_livre_updated_at] --> L[Auto-update livre]
        M[update_users_updated_at] --> N[Auto-update users]
        O[generate_auteur_nom_complet] --> P[Auto-generate nom]
    end
```

---

## 6. CORRESPONDANCE MONGODB ↔ POSTGRESQL

```mermaid
graph LR
    subgraph "COLLECTIONS MONGODB"
        A[Collection livres]
        B[Collection auteurs]
        C[Collection editeurs]
        D[Champ genres]
        E[Champ langues]
    end
    
    subgraph "TABLES POSTGRESQL"
        F[Table livre]
        G[Table auteur]
        H[Table editeur]
        I[Table sujet]
        J[Table langue]
        K[Tables de liaison]
    end
    
    A --> F
    B --> G
    C --> H
    D --> I
    E --> J
    A --> K
```

---

## 📊 STATISTIQUES ET MÉTRIQUES

- **8 tables principales** + **4 tables de liaison**
- **25+ index optimisés** pour performances
- **6 contraintes métier** pour intégrité
- **3 triggers automatiques** pour maintenance
- **2 vues prédéfinies** pour requêtes complexes
- **1 fonction de recherche** textuelle avancée
- **Compatibilité PostgreSQL 12+** avec JSONB
- **Support complet UTF-8** pour international
