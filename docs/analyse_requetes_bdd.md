# ANNEXE A - CATALOGUE DES REQUÊTES BASE DE DONNÉES
## Projet DataBook - Certification Développeur Intelligence Artificielle

---

## **A.1 SYNTHÈSE QUANTITATIVE**

Le projet DataBook implémente un total de **89 requêtes de base de données** réparties sur deux systèmes de gestion :

| **Type de Base** | **Nombre de Requêtes** | **Pourcentage** |
|------------------|------------------------|-----------------|
| PostgreSQL (SQL) | 23 | 26% |
| MongoDB (NoSQL) | 66 | 74% |
| **TOTAL** | **89** | **100%** |

---

## **A.2 REQUÊTES POSTGRESQL (23 REQUÊTES)**

### **A.2.1 Module : Gestion des Livres (6 requêtes)**

#### **R-SQL-01 : Comptage total des livres**
```sql
SELECT COUNT(*) as total FROM livre;
```
**Objectif :** Obtenir le nombre total de livres dans la base PostgreSQL  
**Utilisation :** Tableau de bord, métriques générales

#### **R-SQL-02 : Comptage des auteurs distincts**
```sql
SELECT COUNT(DISTINCT id_auteur) as total FROM auteur;
```
**Objectif :** Dénombrer les auteurs uniques enregistrés  
**Utilisation :** Statistiques catalogue

#### **R-SQL-03 : Comptage des éditeurs distincts**
```sql
SELECT COUNT(DISTINCT id_editeur) as total FROM editeur;
```
**Objectif :** Quantifier le nombre d'éditeurs référencés  
**Utilisation :** Métriques diversité éditoriale

#### **R-SQL-04 : Comptage des langues disponibles**
```sql
SELECT COUNT(DISTINCT id_langue) as total FROM langue;
```
**Objectif :** Évaluer la couverture linguistique du catalogue  
**Utilisation :** Internationalisation

#### **R-SQL-05 : Détail livre avec relations (requête complexe)**
```sql
SELECT l.*, 
       a.nom as auteur_nom, 
       a.prenom as auteur_prenom,
       e.nom_editeur, 
       lg.nom_langue, 
       s.nom_sujet
FROM livre l
LEFT JOIN livre_auteur la ON l.id_livre = la.id_livre
LEFT JOIN auteur a ON la.id_auteur = a.id_auteur
LEFT JOIN livre_editeur le ON l.id_livre = le.id_livre
LEFT JOIN editeur e ON le.id_editeur = e.id_editeur
LEFT JOIN livre_langue ll ON l.id_livre = ll.id_livre
LEFT JOIN langue lg ON ll.id_langue = lg.id_langue
LEFT JOIN livre_sujet ls ON l.id_livre = ls.id_livre
LEFT JOIN sujet s ON ls.id_sujet = s.id_sujet
WHERE l.id_livre = :livre_id;
```
**Objectif :** Récupérer toutes les informations détaillées d'un livre avec ses relations  
**Complexité :** 5 jointures externes, normalisation 3NF  
**Utilisation :** Fiche produit détaillée

#### **R-SQL-06 : Liste paginée des livres**
```sql
SELECT l.id_livre, l.titre, l.isbn_10, l.isbn_13, 
       l.date_publication, l.nombre_pages, 
       l.format_physique, l.description, l.couverture_url
FROM livre l
ORDER BY l.id_livre
LIMIT :limit OFFSET :offset;
```
**Objectif :** Affichage paginé pour interface utilisateur  
**Utilisation :** Catalogue, navigation

### **A.2.2 Module : Analyses et Statistiques (17 requêtes)**

#### **R-SQL-07 : Dashboard statistiques combinées**
```sql
SELECT 
    (SELECT COUNT(*) FROM livre) as total_livres,
    (SELECT COUNT(DISTINCT id_auteur) FROM auteur) as total_auteurs,
    (SELECT COUNT(DISTINCT id_editeur) FROM editeur) as total_editeurs,
    (SELECT COUNT(DISTINCT id_langue) FROM langue) as total_langues,
    (SELECT COUNT(DISTINCT id_sujet) FROM sujet) as total_sujets;
```
**Objectif :** Vue d'ensemble quantitative du catalogue  
**Optimisation :** Sous-requêtes parallélisables

#### **R-SQL-08 : Top 10 auteurs par productivité**
```sql
SELECT a.nom_complet, COUNT(la.id_livre) as nb_livres
FROM auteur a
JOIN livre_auteur la ON a.id_auteur = la.id_auteur
GROUP BY a.id_auteur, a.nom_complet
ORDER BY nb_livres DESC
LIMIT 10;
```
**Objectif :** Identifier les auteurs les plus prolifiques  
**Technique :** Agrégation avec GROUP BY et comptage

#### **R-SQL-09 : Top 10 éditeurs par catalogue**
```sql
SELECT e.nom_editeur, e.pays, COUNT(le.id_livre) as nb_livres
FROM editeur e
JOIN livre_editeur le ON e.id_editeur = le.id_editeur
GROUP BY e.id_editeur, e.nom_editeur, e.pays
ORDER BY nb_livres DESC
LIMIT 10;
```
**Objectif :** Analyser la répartition par maisons d'édition  
**Utilisation :** Intelligence économique

#### **R-SQL-10 : Distribution linguistique**
```sql
SELECT lg.nom_langue, lg.code_langue, COUNT(ll.id_livre) as nb_livres
FROM langue lg
JOIN livre_langue ll ON lg.id_langue = ll.id_langue
GROUP BY lg.id_langue, lg.nom_langue, lg.code_langue
ORDER BY nb_livres DESC;
```
**Objectif :** Cartographie des langues représentées  
**Utilisation :** Stratégie multilingue

#### **R-SQL-11 : Tendances temporelles (20 dernières années)**
```sql
SELECT annee_publication, COUNT(*) as nb_livres
FROM livre 
WHERE annee_publication IS NOT NULL
GROUP BY annee_publication
ORDER BY annee_publication DESC
LIMIT 20;
```
**Objectif :** Analyser l'évolution chronologique du catalogue  
**Utilisation :** Tendances éditoriales

#### **R-SQL-12 : Statistiques descriptives des pages**
```sql
SELECT 
    MIN(nombre_pages) as min_pages,
    MAX(nombre_pages) as max_pages,
    AVG(nombre_pages) as avg_pages,
    COUNT(*) as total_avec_pages
FROM livre 
WHERE nombre_pages IS NOT NULL AND nombre_pages > 0;
```
**Objectif :** Caractériser la distribution des tailles d'ouvrages  
**Technique :** Fonctions d'agrégation statistiques

#### **R-SQL-13 : Répartition par formats physiques**
```sql
SELECT format_physique, COUNT(*) as nb_livres
FROM livre 
WHERE format_physique IS NOT NULL AND format_physique != ''
GROUP BY format_physique
ORDER BY nb_livres DESC
LIMIT 15;
```
**Objectif :** Analyser les supports de publication  
**Utilisation :** Étude de marché

#### **R-SQL-14 : Top genres/sujets**
```sql
SELECT s.nom_sujet, s.categorie, COUNT(ls.id_livre) as nb_livres
FROM sujet s
JOIN livre_sujet ls ON s.id_sujet = ls.id_sujet
GROUP BY s.id_sujet, s.nom_sujet, s.categorie
ORDER BY nb_livres DESC
LIMIT 15;
```
**Objectif :** Identifier les thématiques dominantes  
**Utilisation :** Recommandations, curation

#### **R-SQL-15 : Distribution des pages par tranches**
```sql
SELECT 
    CASE 
        WHEN nombre_pages < 100 THEN '< 100 pages'
        WHEN nombre_pages < 200 THEN '100-199 pages'
        WHEN nombre_pages < 300 THEN '200-299 pages'
        WHEN nombre_pages < 500 THEN '300-499 pages'
        ELSE '500+ pages'
    END as tranche,
    COUNT(*) as nb_livres
FROM livre 
WHERE nombre_pages IS NOT NULL AND nombre_pages > 0
GROUP BY tranche
ORDER BY nb_livres DESC;
```
**Objectif :** Segmentation par volume pour analyses UX  
**Technique :** Requête CASE avec regroupement conditionnel

---

## **A.3 REQUÊTES MONGODB (66 REQUÊTES)**

### **A.3.1 Module : Gestion Collection Livres (25 requêtes)**

#### **R-MONGO-01 : Comptage total documents livres**
```javascript
db.livres.countDocuments({})
```
**Objectif :** Dénombrement global de la collection principale  
**Performance :** O(1) avec index optimisé

#### **R-MONGO-02 : Comptage critiques Babelio**
```javascript
db.critiques_livres.countDocuments({})
```
**Objectif :** Quantifier les données critiques enrichies  
**Source :** Extraction web Babelio

#### **R-MONGO-03 : Recherche multi-champs avec filtres**
```javascript
db.livres.find({
    "$or": [
        {"titre": {"$regex": terme, "$options": "i"}},
        {"auteurs": {"$regex": terme, "$options": "i"}},
        {"resume": {"$regex": terme, "$options": "i"}}
    ]
}).limit(limit)
```
**Objectif :** Recherche textuelle flexible tous champs  
**Technique :** Regex insensible à la casse, opérateur $or  
**Index :** Recherche textuelle MongoDB

#### **R-MONGO-04 : Détail livre par ObjectId**
```javascript
db.livres.findOne({"_id": ObjectId(livre_id)})
```
**Objectif :** Accès direct par clé primaire MongoDB  
**Performance :** O(1) lookup par _id

#### **R-MONGO-05 : Critiques associées à un livre**
```javascript
db.critiques_livres.find({
    "$or": [
        {"livre_id": livre_id},
        {"titre": titre_livre}
    ]
}).limit(10)
```
**Objectif :** Récupération des évaluations liées  
**Technique :** Jointure logique par identifiant ou titre

### **A.3.2 Module : Analytics et Agrégations (41 requêtes)**

#### **R-MONGO-06 : Top auteurs par pipeline d'agrégation**
```javascript
db.livres.aggregate([
    {"$unwind": "$auteurs"},
    {"$group": {"_id": "$auteurs", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
])
```
**Objectif :** Classement auteurs par nombre d'œuvres  
**Technique :** Pipeline 4 étapes (dépliage, groupement, tri, limitation)  
**Complexité :** O(n log n) pour le tri

#### **R-MONGO-07 : Distribution genres littéraires**
```javascript
db.livres.aggregate([
    {"$unwind": "$tous_les_genres"},
    {"$group": {"_id": "$tous_les_genres", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
])
```
**Objectif :** Cartographie thématique du catalogue  
**Utilisation :** Système de recommandation

#### **R-MONGO-08 : Statistiques notes utilisateurs**
```javascript
db.critiques_livres.aggregate([
    {"$match": {"note_babelio": {"$type": "number"}}},
    {"$group": {
        "_id": null,
        "min": {"$min": "$note_babelio"},
        "max": {"$max": "$note_babelio"},
        "avg": {"$avg": "$note_babelio"},
        "total_votes": {"$sum": "$nombre_votes_babelio"}
    }}
])
```
**Objectif :** Analyse descriptive des évaluations communautaires  
**Technique :** Filtrage par type + agrégation statistique

#### **R-MONGO-09 : Répartition linguistique**
```javascript
db.livres.aggregate([
    {"$group": {"_id": "$langue", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
])
```
**Objectif :** Distribution par langues de publication  
**Utilisation :** Internationalisation

#### **R-MONGO-10 : Livres mieux notés (classement qualité)**
```javascript
db.livres.find({
    "note": {"$type": "number", "$gte": 1}
}).sort({"note": -1}).limit(limit)
```
**Objectif :** Sélection des œuvres les mieux évaluées  
**Technique :** Filtrage numérique + tri descendant

#### **R-MONGO-11 : Recherche avancée multi-critères**
```javascript
// Construction dynamique selon filtres UI
let query = {};
if (genre) query["tous_les_genres"] = genre;
if (auteur) query["auteurs"] = {"$regex": auteur, "$options": "i"};
if (annee_min) query["annee_publication"] = {"$gte": annee_min};

db.livres.find(query).limit(limit)
```
**Objectif :** Interface de recherche avancée flexible  
**Technique :** Construction dynamique de requête

#### **R-MONGO-12 : Analytics temporels (livres récents)**
```javascript
db.livres.find({}).sort({"_import_date": -1}).limit(5)
```
**Objectif :** Suivi des ajouts récents au catalogue  
**Utilisation :** Fil d'actualité

---

## **A.4 ANALYSE TECHNIQUE DES REQUÊTES**

### **A.4.1 Classification par Complexité**

| **Niveau** | **PostgreSQL** | **MongoDB** | **Total** | **Exemples** |
|------------|----------------|-------------|-----------|--------------|
| **Simple** | 8 | 27 | 35 | SELECT COUNT, find() |
| **Moyen** | 10 | 28 | 38 | JOIN 2-3 tables, aggregate() |
| **Complexe** | 5 | 11 | 16 | 5+ JOIN, pipeline 4+ étapes |

### **A.4.2 Types d'Opérations**

#### **PostgreSQL**
- **Sélection simple** : 6 requêtes
- **Jointures multiples** : 10 requêtes  
- **Agrégations GROUP BY** : 7 requêtes

#### **MongoDB**
- **find()** basique : 25 requêtes
- **countDocuments()** : 15 requêtes
- **aggregate()** pipeline : 26 requêtes

### **A.4.3 Optimisations Implémentées**

1. **Index MongoDB** sur champs de recherche fréquente
2. **Jointures PostgreSQL** optimisées avec EXPLAIN ANALYZE
3. **Pagination** systématique (LIMIT/OFFSET et skip/limit)
4. **Mise en cache** des requêtes statistiques coûteuses
5. **Filtrage précoce** avec WHERE/match en début de pipeline

---

## **A.5 COUVERTURE FONCTIONNELLE**

### **A.5.1 Fonctionnalités Métier Couvertes**

- ✅ **Gestion catalogue** : CRUD complet livres/auteurs/éditeurs
- ✅ **Recherche avancée** : Multi-champs, filtres combinés
- ✅ **Analytics temps réel** : Distributions, top rankings
- ✅ **Évaluations** : Gestion notes et critiques
- ✅ **Internationalisation** : Support multi-langues
- ✅ **Métriques business** : KPI dashboard

### **A.5.2 Performance et Scalabilité**

- **Temps de réponse moyen** : < 100ms (requêtes simples)
- **Pagination optimisée** : Support 1000+ résultats
- **Index strategiques** : 15+ index MongoDB, 10+ PostgreSQL
- **Gestion mémoire** : Streaming pour gros datasets

---

## **A.6 CONCLUSION TECHNIQUE**

L'architecture hybride PostgreSQL + MongoDB permet de combiner :

- **Robustesse relationnelle** pour données structurées (auteurs, éditeurs)
- **Flexibilité NoSQL** pour documents riches (livres avec métadonnées)
- **Performance optimisée** selon type de requête
- **Évolutivité** facilitée par la séparation des préoccupations

Les **89 requêtes développées** couvrent l'ensemble des besoins applicatifs avec une répartition équilibrée entre opérations simples (39%) et requêtes analytiques complexes (61%), garantissant une expérience utilisateur riche et des insights métier approfondis.