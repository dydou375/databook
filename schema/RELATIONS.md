# Relations de la Base de Données Databook

## 📚 Structure des Relations

### 1. Relations Livre-Auteur
- **Table de liaison** : `LIVRE_AUTEUR`
- **Type de relation** : Many-to-Many (Plusieurs-à-Plusieurs)
- **Description** : 
  - Un livre peut avoir plusieurs auteurs
  - Un auteur peut avoir écrit plusieurs livres
- **Clés** :
  - `id_livre` : Référence à la table LIVRE
  - `id_auteur` : Référence à la table AUTEUR

### 2. Relations Livre-Éditeur
- **Table de liaison** : `LIVRE_EDITEUR`
- **Type de relation** : Many-to-Many
- **Description** :
  - Un livre peut être publié par plusieurs éditeurs
  - Un éditeur peut publier plusieurs livres
- **Clés** :
  - `id_livre` : Référence à la table LIVRE
  - `id_editeur` : Référence à la table EDITEUR

### 3. Relations Livre-Langue
- **Table de liaison** : `LIVRE_LANGUE`
- **Type de relation** : Many-to-Many
- **Description** :
  - Un livre peut être disponible en plusieurs langues
  - Une langue peut être utilisée dans plusieurs livres
- **Clés** :
  - `id_livre` : Référence à la table LIVRE
  - `id_langue` : Référence à la table LANGUE

### 4. Relations Livre-Sujet
- **Table de liaison** : `LIVRE_SUJET`
- **Type de relation** : Many-to-Many
- **Description** :
  - Un livre peut traiter de plusieurs sujets
  - Un sujet peut apparaître dans plusieurs livres
- **Clés** :
  - `id_livre` : Référence à la table LIVRE
  - `id_sujet` : Référence à la table SUJET

## 🔄 Exemple de Requêtes SQL

### Trouver tous les auteurs d'un livre
```sql
SELECT a.nom
FROM AUTEUR a
JOIN LIVRE_AUTEUR la ON a.id_auteur = la.id_auteur
JOIN LIVRE l ON l.id_livre = la.id_livre
WHERE l.titre = 'Titre du livre';
```

### Trouver tous les livres d'un auteur
```sql
SELECT l.titre, l.annee_publication
FROM LIVRE l
JOIN LIVRE_AUTEUR la ON l.id_livre = la.id_livre
JOIN AUTEUR a ON a.id_auteur = la.id_auteur
WHERE a.nom = 'Nom de l''auteur';
```

### Trouver les livres par langue
```sql
SELECT l.titre, l.annee_publication
FROM LIVRE l
JOIN LIVRE_LANGUE ll ON l.id_livre = ll.id_livre
JOIN LANGUE lang ON lang.id_langue = ll.id_langue
WHERE lang.code = 'fre';
```

### Trouver les livres par sujet
```sql
SELECT l.titre, l.annee_publication
FROM LIVRE l
JOIN LIVRE_SUJET ls ON l.id_livre = ls.id_livre
JOIN SUJET s ON s.id_sujet = ls.id_sujet
WHERE s.nom = 'Science-fiction';
```

## 📊 Avantages de cette Structure

1. **Flexibilité** :
   - Permet d'ajouter facilement de nouveaux auteurs, éditeurs, langues ou sujets
   - Supporte les relations multiples (ex: un livre avec plusieurs auteurs)

2. **Intégrité des données** :
   - Les clés étrangères garantissent la cohérence des données
   - Évite les doublons grâce aux tables de liaison

3. **Performance** :
   - Indexation optimisée sur les clés primaires et étrangères
   - Requêtes efficaces grâce à la normalisation

4. **Maintenance** :
   - Structure modulaire facile à maintenir
   - Possibilité d'ajouter de nouvelles relations sans modifier la structure existante 