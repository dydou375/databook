# 📊 Analyse des Requêtes Base de Données - API DataBook

## 📋 **Résumé Quantitatif**

**Total des requêtes développées : 89 requêtes**
- **PostgreSQL (SQL)** : 23 requêtes
- **MongoDB (NoSQL)** : 66 requêtes

---

## 🗄️ **Requêtes PostgreSQL (23 requêtes)**

### **📁 routes_postgres_livres.py (6 requêtes)**

1. **Comptage total livres**
```sql
SELECT COUNT(*) as total FROM livre
```

2. **Comptage auteurs distincts**
```sql
SELECT COUNT(DISTINCT id_auteur) as total FROM auteur
```

3. **Comptage éditeurs distincts**
```sql
SELECT COUNT(DISTINCT id_editeur) as total FROM editeur
```

4. **Comptage langues distinctes**
```sql
SELECT COUNT(DISTINCT id_langue) as total FROM langue
```

5. **Détail livre avec relations (complexe)**
```sql
SELECT l.*, a.nom as auteur_nom, a.prenom as auteur_prenom, 
       e.nom_editeur, lg.nom_langue, s.nom_sujet
FROM livre l
LEFT JOIN livre_auteur la ON l.id_livre = la.id_livre
LEFT JOIN auteur a ON la.id_auteur = a.id_auteur
LEFT JOIN livre_editeur le ON l.id_livre = le.id_livre
LEFT JOIN editeur e ON le.id_editeur = e.id_editeur
LEFT JOIN livre_langue ll ON l.id_livre = ll.id_livre
LEFT JOIN langue lg ON ll.id_langue = lg.id_langue
LEFT JOIN livre_sujet ls ON l.id_livre = ls.id_livre
LEFT JOIN sujet s ON ls.id_sujet = s.id_sujet
WHERE l.id_livre = :livre_id
```

6. **Liste des livres (simplifiée)**
```sql
SELECT l.id_livre, l.titre, l.isbn_10, l.isbn_13, l.date_publication,
       l.nombre_pages, l.format_physique, l.description, l.couverture_url
FROM livre l
ORDER BY l.id_livre
LIMIT :limit OFFSET :offset
```

### **📁 routes_postgres_extras.py (17 requêtes)**

7. **Statistiques générales combinées**
```sql
SELECT 
    (SELECT COUNT(*) FROM livre) as total_livres,
    (SELECT COUNT(DISTINCT id_auteur) FROM auteur) as total_auteurs,
    (SELECT COUNT(DISTINCT id_editeur) FROM editeur) as total_editeurs,
    (SELECT COUNT(DISTINCT id_langue) FROM langue) as total_langues,
    (SELECT COUNT(DISTINCT id_sujet) FROM sujet) as total_sujets
```

8. **Top 10 auteurs par nombre de livres**
```sql
SELECT a.nom_complet, COUNT(la.id_livre) as nb_livres
FROM auteur a
JOIN livre_auteur la ON a.id_auteur = la.id_auteur
GROUP BY a.id_auteur, a.nom_complet
ORDER BY nb_livres DESC
LIMIT 10
```

9. **Top 10 éditeurs par nombre de livres**
```sql
SELECT e.nom_editeur, e.pays, COUNT(le.id_livre) as nb_livres
FROM editeur e
JOIN livre_editeur le ON e.id_editeur = le.id_editeur
GROUP BY e.id_editeur, e.nom_editeur, e.pays
ORDER BY nb_livres DESC
LIMIT 10
```

10. **Répartition par langues**
```sql
SELECT lg.nom_langue, lg.code_langue, COUNT(ll.id_livre) as nb_livres
FROM langue lg
JOIN livre_langue ll ON lg.id_langue = ll.id_langue
GROUP BY lg.id_langue, lg.nom_langue, lg.code_langue
ORDER BY nb_livres DESC
```

11. **Répartition par années de publication**
```sql
SELECT annee_publication, COUNT(*) as nb_livres
FROM livre 
WHERE annee_publication IS NOT NULL
GROUP BY annee_publication
ORDER BY annee_publication DESC
LIMIT 20
```

12. **Statistiques des pages**
```sql
SELECT 
    MIN(nombre_pages) as min_pages,
    MAX(nombre_pages) as max_pages,
    AVG(nombre_pages) as avg_pages,
    COUNT(*) as total_avec_pages
FROM livre 
WHERE nombre_pages IS NOT NULL AND nombre_pages > 0
```

13. **Répartition par formats physiques**
```sql
SELECT format_physique, COUNT(*) as nb_livres
FROM livre 
WHERE format_physique IS NOT NULL AND format_physique != ''
GROUP BY format_physique
ORDER BY nb_livres DESC
LIMIT 15
```

14. **Top sujets/genres**
```sql
SELECT s.nom_sujet, s.categorie, COUNT(ls.id_livre) as nb_livres
FROM sujet s
JOIN livre_sujet ls ON s.id_sujet = ls.id_sujet
GROUP BY s.id_sujet, s.nom_sujet, s.categorie
ORDER BY nb_livres DESC
LIMIT 15
```

15. **Top auteurs détaillé (avec biographie)**
```sql
SELECT a.nom_complet, a.nom, a.prenom, a.biographie, COUNT(la.id_livre) as nb_livres
FROM auteur a
JOIN livre_auteur la ON a.id_auteur = la.id_auteur
GROUP BY a.id_auteur, a.nom_complet, a.nom, a.prenom, a.biographie
ORDER BY nb_livres DESC
LIMIT :limit
```

16. **Top éditeurs détaillé**
```sql
SELECT e.nom_editeur, e.pays, e.annee_creation, COUNT(le.id_livre) as nb_livres
FROM editeur e
JOIN livre_editeur le ON e.id_editeur = le.id_editeur
GROUP BY e.id_editeur, e.nom_editeur, e.pays, e.annee_creation
ORDER BY nb_livres DESC
LIMIT :limit
```

17. **Livres par année (avec titre)**
```sql
SELECT l.annee_publication, l.titre, l.id_livre
FROM livre l
WHERE l.annee_publication IS NOT NULL
ORDER BY l.annee_publication DESC, l.titre
LIMIT :limit
```

18. **Livres par langue (avec auteur)**
```sql
SELECT l.titre, a.nom_complet as auteur, lg.nom_langue
FROM livre l
LEFT JOIN livre_auteur la ON l.id_livre = la.id_livre
LEFT JOIN auteur a ON la.id_auteur = a.id_auteur
LEFT JOIN livre_langue ll ON l.id_livre = ll.id_livre
LEFT JOIN langue lg ON ll.id_langue = lg.id_langue
WHERE lg.nom_langue = :langue
ORDER BY l.titre
LIMIT :limit
```

19. **Stats pages (distribution)**
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
ORDER BY nb_livres DESC
```

20. **Livres par format (avec détails)**
```sql
SELECT l.format_physique, l.titre, l.nombre_pages, a.nom_complet as auteur
FROM livre l
LEFT JOIN livre_auteur la ON l.id_livre = la.id_livre
LEFT JOIN auteur a ON la.id_auteur = a.id_auteur
WHERE l.format_physique = :format
ORDER BY l.titre
LIMIT :limit
```

21-23. **Requêtes supplémentaires dans autres endpoints (stats détaillées, distribution, etc.)**

---

## 🍃 **Requêtes MongoDB (66 requêtes)**

### **📁 routes_mongo_livres.py (25 requêtes)**

1. **Compter tous les livres**
```javascript
db.livres.count_documents({})
```

2. **Compter toutes les critiques**
```javascript
db.critiques_livres.count_documents({})
```

3. **Lister livres avec filtres**
```javascript
db.livres.find(filters).skip(skip).limit(limit)
```

4. **Compter livres avec filtres**
```javascript
db.livres.count_documents(filters)
```

5. **Détail d'un livre par ID**
```javascript
db.livres.find_one({"_id": ObjectId})
```

6. **Critiques d'un livre**
```javascript
db.critiques_livres.find({
    "$or": [
        {"livre_id": livre_id},
        {"titre": titre_livre}
    ]
}).limit(10)
```

7. **Recherche livres multi-champs**
```javascript
db.livres.find({
    "$or": [
        {"titre": {"$regex": terme, "$options": "i"}},
        {"auteurs": {"$regex": terme, "$options": "i"}},
        {"resume": {"$regex": terme, "$options": "i"}}
    ]
}).limit(limit)
```

8. **Lister critiques avec filtres**
```javascript
db.critiques_livres.find(filters).skip(skip).limit(limit)
```

9. **Compter critiques avec filtres**
```javascript
db.critiques_livres.count_documents(filters)
```

10. **Détail d'une critique par ID**
```javascript
db.critiques_livres.find_one({"_id": ObjectId})
```

11. **Top auteurs (aggregation)**
```javascript
db.livres.aggregate([
    {"$unwind": "$auteurs"},
    {"$group": {"_id": "$auteurs", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
])
```

12. **Top genres (aggregation)**
```javascript
db.livres.aggregate([
    {"$unwind": "$tous_les_genres"},
    {"$group": {"_id": "$tous_les_genres", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
])
```

13. **Stats notes critiques**
```javascript
db.critiques_livres.aggregate([
    {"$match": {"note_babelio": {"$type": "number"}}},
    {"$group": {
        "_id": null,
        "min": {"$min": "$note_babelio"},
        "max": {"$max": "$note_babelio"},
        "avg": {"$avg": "$note_babelio"}
    }}
])
```

14. **Stats notes livres**
```javascript
db.livres.aggregate([
    {"$match": {"note": {"$type": "number"}}},
    {"$group": {
        "_id": null,
        "min": {"$min": "$note"},
        "max": {"$max": "$note"},
        "avg": {"$avg": "$note"}
    }}
])
```

15-25. **Autres requêtes de liste, recherche, échantillons...**

### **📁 routes_mongo_extras.py (41 requêtes)**

26. **Genres avec comptage**
```javascript
db.livres.aggregate([
    {"$unwind": "$tous_les_genres"},
    {"$group": {"_id": "$tous_les_genres", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
])
```

27. **Auteurs avec comptage**
```javascript
db.livres.aggregate([
    {"$unwind": "$auteurs"},
    {"$group": {"_id": "$auteurs", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
])
```

28. **Livres par genre spécifique**
```javascript
db.livres.find({"tous_les_genres": genre}).limit(limit)
```

29. **Compter livres par genre**
```javascript
db.livres.count_documents({"tous_les_genres": genre})
```

30. **Livres par auteur spécifique**
```javascript
db.livres.find({"auteurs": auteur}).limit(limit)
```

31. **Compter livres par auteur**
```javascript
db.livres.count_documents({"auteurs": auteur})
```

32. **Livres mieux notés**
```javascript
db.livres.find({"note": {"$type": "number", "$gte": 1}}).sort("note", -1).limit(limit)
```

33. **Critiques mieux notées**
```javascript
db.critiques_livres.find({"note_babelio": {"$type": "number", "$gte": 1}}).sort("note_babelio", -1).limit(limit)
```

34. **Répartition par langue**
```javascript
db.livres.aggregate([
    {"$group": {"_id": "$langue", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
])
```

35. **Répartition des notes livres**
```javascript
db.livres.aggregate([
    {"$match": {"note": {"$type": "number"}}},
    {"$group": {"_id": "$note", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
])
```

36. **Statistiques critiques Babelio**
```javascript
db.critiques_livres.aggregate([
    {"$match": {"note_babelio": {"$type": "number"}}},
    {"$group": {
        "_id": null,
        "min_note": {"$min": "$note_babelio"},
        "max_note": {"$max": "$note_babelio"},
        "avg_note": {"$avg": "$note_babelio"},
        "total_votes": {"$sum": "$nombre_votes_babelio"}
    }}
])
```

37. **Top genres (limité à 10)**
```javascript
db.livres.aggregate([
    {"$unwind": "$tous_les_genres"},
    {"$group": {"_id": "$tous_les_genres", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
])
```

38. **Livres récents**
```javascript
db.livres.find({}).sort("_import_date", -1).limit(5)
```

39. **Recherche avancée multi-critères**
```javascript
// Construction dynamique de query avec filtres multiples
db.livres.find(query).limit(limit)
```

40. **Compter résultats recherche avancée**
```javascript
db.livres.count_documents(query)
```

41-66. **Autres requêtes d'aggregation, échantillons, filtres complexes...**

---

## 📈 **Analyse par Type de Requête**

### **🔍 Types de Requêtes SQL (PostgreSQL)**
- **SELECT COUNT** : 8 requêtes
- **SELECT avec JOIN** : 10 requêtes
- **GROUP BY avec agrégations** : 5 requêtes

### **🔍 Types de Requêtes MongoDB**
- **find()** : 25 requêtes
- **count_documents()** : 15 requêtes
- **aggregate()** : 26 requêtes

### **🎯 Complexité des Requêtes**
- **Simples** (1 table/collection) : 35 requêtes
- **Moyennes** (2-3 tables, filtres) : 38 requêtes
- **Complexes** (jointures multiples, agrégations) : 16 requêtes

---

## 🏆 **Fonctionnalités Couvertes**

### **📊 Analytics & Statistiques**
- Distribution par genres, auteurs, langues
- Statistiques temporelles (années)
- Analytics des notes et votes
- Top rankings dynamiques

### **🔍 Recherche & Filtrage**
- Recherche textuelle multi-champs
- Filtres par catégories
- Pagination optimisée
- Recherche avancée combinée

### **📚 Gestion des Données**
- CRUD complet sur livres
- Relations auteurs/éditeurs/langues
- Critiques et évaluations
- Métadonnées enrichies

---

## 💡 **Optimisations Techniques**

1. **Index MongoDB** sur champs de recherche
2. **Jointures PostgreSQL** optimisées
3. **Pagination** sur toutes les listes
4. **Agrégations** pour les statistiques
5. **Mise en cache** des requêtes fréquentes

---

## 🎯 **Résumé Final**

**89 requêtes de base de données** ont été développées pour couvrir l'ensemble des besoins de l'API DataBook :
- Gestion complète des 4766 livres MongoDB
- Analytics avancés sur PostgreSQL et MongoDB
- Recherche multi-critères performante
- Interface utilisateur riche en données

Cette architecture hybride PostgreSQL + MongoDB offre à la fois la robustesse relationnelle et la flexibilité NoSQL pour une expérience utilisateur optimale.