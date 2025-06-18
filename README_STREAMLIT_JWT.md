# 🔐 Interface Streamlit DataBook avec Authentification JWT

## 📋 Vue d'ensemble

Interface utilisateur moderne pour votre API DataBook avec **authentification JWT complète**, permettant aux utilisateurs de s'inscrire, se connecter et accéder à vos données de manière sécurisée.

## ✨ Fonctionnalités

### 🔐 **Authentification sécurisée**
- ✍️ **Inscription** : Création de nouveaux comptes utilisateur
- 🔑 **Connexion** : Authentification par email/mot de passe
- 👤 **Profil** : Gestion du profil utilisateur
- 🚪 **Déconnexion** : Sécurisation des sessions

### 📚 **Exploration des données**
- **4766 livres MongoDB** : Navigation et recherche complète
- **85 critiques Babelio** : Accès aux critiques détaillées
- **PostgreSQL** : Gestion des données relationnelles
- **Analytics avancés** : Graphiques et statistiques

### 🎯 **Interface moderne**
- Design responsive et intuitif
- Navigation par onglets
- Graphiques interactifs avec Plotly
- Indicateurs de statut en temps réel

## 🚀 Démarrage rapide

### 1. **Démarrer l'API** (requis)
```bash
cd api
python start.py
```
> L'API doit tourner sur http://localhost:8000

### 2. **Démarrer l'interface Streamlit**
```bash
python start_streamlit_auth.py
```
> Interface accessible sur http://localhost:8501

### 3. **Créer votre compte**
1. Ouvrez http://localhost:8501
2. Cliquez sur l'onglet "✍️ Inscription"
3. Remplissez vos informations
4. Connectez-vous avec vos identifiants

## 📖 Guide d'utilisation

### 🔑 **Page de connexion**

**Première utilisation :**
1. **Inscription** : Créez votre compte avec email/mot de passe
2. **Connexion** : Utilisez vos identifiants pour accéder

**Fonctionnalités :**
- Validation des mots de passe
- Messages d'erreur explicites
- Test de connexion API intégré

### 🏠 **Dashboard principal**

Une fois connecté, vous accédez au dashboard avec :

**Métriques en temps réel :**
- 📚 Nombre de livres MongoDB
- 💬 Critiques disponibles  
- 🔐 État de l'authentification
- 🎯 Version de l'API

**Navigation rapide :**
- Explorer les livres
- Voir les analytics
- Accéder aux données PostgreSQL

### 📚 **Livres MongoDB**

**Fonctionnalités :**
- **Liste complète** : Affichage paginé des 4766 livres
- **Recherche avancée** : Par titre, auteur, genre
- **Filtres** : Nombre de résultats personnalisable
- **Détails** : Informations complètes par livre

**Exemple de recherche :**
```
🔍 "Victor Hugo" → Tous ses livres
🔍 "roman" → Livres contenant "roman"
```

### 🎯 **Analytics**

**Graphiques disponibles :**
- 📊 **Top 10 des genres** (graphique en barres)
- ✍️ **Top 10 des auteurs** (graphique en barres)
- 📈 **Statistiques générales** (métriques)

**Données analysées :**
- Distribution par genres
- Productivité des auteurs
- Notes moyennes
- Tendances temporelles

### 🗄️ **PostgreSQL**

**Données accessibles :**
- 👥 **Utilisateurs** : Liste des utilisateurs inscrits
- 📚 **Livres** : Livres en base relationnelle
- 🔧 **CRUD** : Opérations de gestion

### 👤 **Mon Profil**

**Informations affichées :**
- Nom et prénom
- Email
- ID utilisateur
- Statut du compte

**Actions disponibles :**
- Rafraîchir le profil
- Se déconnecter

## 🔧 Configuration technique

### **Prérequis**
```python
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.0
plotly>=5.15.0
```

### **Architecture**
```
streamlit_auth.py          # Interface principale
start_streamlit_auth.py    # Script de démarrage
```

### **Endpoints utilisés**
```
POST /auth/register        # Inscription
POST /auth/login          # Connexion
GET  /auth/me             # Profil utilisateur
POST /auth/logout         # Déconnexion
GET  /mongo-livres/*      # Données MongoDB
GET  /mongo-extras/*      # Analytics
GET  /postgres/*          # Données PostgreSQL
```

## 🛡️ Sécurité

### **JWT Tokens**
- **Stockage** : Session Streamlit sécurisée
- **Expiration** : Gestion automatique
- **Headers** : `Authorization: Bearer {token}`

### **Protection des routes**
- Vérification automatique des tokens
- Redirection vers connexion si non authentifié
- Gestion des erreurs 401/403

### **Validation**
- Validation des mots de passe côté client
- Vérification des emails
- Messages d'erreur sécurisés

## 🎨 Personnalisation

### **CSS personnalisé**
L'interface utilise des styles CSS intégrés pour :
- En-têtes avec dégradés
- Containers d'authentification
- Boîtes d'information utilisateur
- Messages de succès/erreur

### **Couleurs**
- 🔵 Bleu : Informations utilisateur
- 🟢 Vert : Succès et états OK
- 🔴 Rouge : Erreurs
- 🟡 Jaune : Avertissements

## 📊 Monitoring

### **État de l'API**
La sidebar affiche en temps réel :
- ✅ PostgreSQL connecté/déconnecté
- ✅ MongoDB connecté + nombre de livres/critiques
- ❌ Erreurs de connexion

### **Debugging**
- Expandeur "Test de l'API" sur la page de connexion
- Affichage des codes de réponse HTTP
- Messages d'erreur détaillés

## 🚨 Dépannage

### **API non accessible**
```
❌ L'API n'est pas accessible
🚀 Démarrez l'API avec: cd api && python start.py
```

### **Erreur de connexion**
```
❌ Erreur de connexion: Invalid credentials
→ Vérifiez votre email/mot de passe
```

### **Token expiré**
```
❌ Impossible de récupérer le profil
→ Reconnectez-vous
```

### **MongoDB non connecté**
```
🍃 MongoDB KO
→ Vérifiez la configuration MongoDB dans l'API
```

## 📈 Évolutions possibles

### **Court terme**
- 🔄 Refresh automatique des tokens
- 📱 Interface mobile optimisée  
- 🌙 Mode sombre/clair

### **Moyen terme**
- 👥 Gestion des rôles utilisateur
- 📊 Dashboards personnalisés
- 🔍 Recherche élastique

### **Long terme**
- 🤖 Recommandations IA
- 📈 Analytics prédictifs
- 🔗 Intégrations externes

---

## 🎯 Résumé

Votre interface Streamlit avec authentification JWT est maintenant **prête** ! 

**Pour commencer :**
1. `python start.py` (API)
2. `python start_streamlit_auth.py` (Interface)
3. Créez votre compte sur http://localhost:8501
4. Explorez vos 4766 livres ! 📚

**Support :** L'interface gère automatiquement les erreurs et vous guide à chaque étape. 