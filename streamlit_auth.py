"""
🔐 Interface Streamlit avec Authentification JWT pour DataBook API
Gestion complète des utilisateurs : inscription, connexion, profil
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import json

# Configuration
st.set_page_config(
    page_title="🔐 DataBook - Authentification",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000"

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .auth-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .user-info {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

def check_api_status():
    """Vérifier l'état de l'API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def make_api_request(endpoint, method="GET", headers=None, data=None, params=None):
    """Faire une requête à l'API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        return response.status_code, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
    except Exception as e:
        return 500, f"Erreur: {str(e)}"

def register_user(email, password, first_name, last_name):
    """Inscription d'un nouvel utilisateur"""
    data = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name
    }
    
    status_code, response = make_api_request("/auth/register", method="POST", data=data)
    return status_code, response

def login_user(email, password):
    """Connexion utilisateur"""
    data = {
        "email": email,  # L'API attend 'email' pour l'endpoint /auth/login
        "password": password
    }
    
    status_code, response = make_api_request("/auth/login", method="POST", data=data)
    return status_code, response

def get_user_profile(token):
    """Récupérer le profil utilisateur"""
    headers = {"Authorization": f"Bearer {token}"}
    status_code, response = make_api_request("/auth/me", headers=headers)
    return status_code, response

def logout_user(token):
    """Déconnexion utilisateur"""
    headers = {"Authorization": f"Bearer {token}"}
    status_code, response = make_api_request("/auth/logout", method="POST", headers=headers)
    return status_code, response

def show_login_page():
    """Page de connexion"""
    st.markdown("""
    <div class="main-header">
        <h1>🔐 Connexion DataBook</h1>
        <p>Connectez-vous pour accéder à vos données</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        # Onglets pour connexion/inscription
        tab1, tab2 = st.tabs(["🔑 Connexion", "✍️ Inscription"])
        
        with tab1:
            st.subheader("Se connecter")
            
            with st.form("login_form"):
                email = st.text_input("📧 Email")
                password = st.text_input("🔒 Mot de passe", type="password")
                submit_login = st.form_submit_button("🚀 Se connecter", use_container_width=True)
                
                if submit_login:
                    if email and password:
                        with st.spinner("Connexion en cours..."):
                            status_code, response = login_user(email, password)
                            
                            if status_code == 200:
                                st.session_state.token = response.get("access_token")
                                st.session_state.user_email = email
                                st.session_state.authenticated = True
                                st.success("✅ Connexion réussie!")
                                st.rerun()
                            else:
                                st.error(f"❌ Erreur de connexion: {response.get('detail', 'Erreur inconnue')}")
                    else:
                        st.error("⚠️ Veuillez remplir tous les champs")
        
        with tab2:
            st.subheader("Créer un compte")
            
            with st.form("register_form"):
                reg_email = st.text_input("📧 Email", key="reg_email")
                reg_first_name = st.text_input("👤 Prénom", key="reg_first_name")
                reg_last_name = st.text_input("👤 Nom", key="reg_last_name")
                reg_password = st.text_input("🔒 Mot de passe", type="password", key="reg_password")
                reg_password_confirm = st.text_input("🔒 Confirmer le mot de passe", type="password", key="reg_password_confirm")
                submit_register = st.form_submit_button("📝 S'inscrire", use_container_width=True)
                
                if submit_register:
                    if reg_email and reg_first_name and reg_last_name and reg_password:
                        if reg_password == reg_password_confirm:
                            with st.spinner("Inscription en cours..."):
                                status_code, response = register_user(reg_email, reg_password, reg_first_name, reg_last_name)
                                
                                if status_code == 200:
                                    st.success("✅ Inscription réussie! Vous pouvez maintenant vous connecter.")
                                    st.balloons()
                                else:
                                    st.error(f"❌ Erreur d'inscription: {response.get('detail', 'Erreur inconnue')}")
                        else:
                            st.error("⚠️ Les mots de passe ne correspondent pas")
                    else:
                        st.error("⚠️ Veuillez remplir tous les champs")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Test de connexion API
        st.markdown("---")
        with st.expander("🔧 Test de l'API"):
            if st.button("Tester la connexion"):
                api_status, health_data = check_api_status()
                if api_status:
                    st.success("✅ API accessible")
                    st.json(health_data)
                else:
                    st.error("❌ API non accessible - Démarrez l'API avec: `python start.py`")

def show_main_app():
    """Application principale (utilisateur connecté)"""
    
    # En-tête avec info utilisateur
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div class="main-header">
            <h1>📚 DataBook - Dashboard</h1>
            <p>Interface complète pour vos données de livres</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Profil utilisateur
        if st.session_state.get("token"):
            status_code, user_data = get_user_profile(st.session_state.token)
            
            if status_code == 200:
                st.markdown(f"""
                <div class="user-info">
                    <h4>👤 {user_data.get('first_name', '')} {user_data.get('last_name', '')}</h4>
                    <p>📧 {user_data.get('email', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🚪 Se déconnecter"):
                    logout_user(st.session_state.token)
                    # Nettoyer la session
                    for key in ['token', 'user_email', 'authenticated']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            else:
                st.error("❌ Impossible de récupérer le profil")
                st.session_state.authenticated = False
                st.rerun()
    
    # Sidebar avec état de l'API
    with st.sidebar:
        st.header("📊 État de l'API")
        
        api_status, health_data = check_api_status()
        if api_status and health_data:
            databases = health_data.get("databases", {})
            
            # PostgreSQL
            if databases.get("postgresql") == "connected":
                st.success("🐘 PostgreSQL OK")
            else:
                st.error("🐘 PostgreSQL KO")
            
            # MongoDB
            mongo_info = databases.get("mongodb", {})
            if isinstance(mongo_info, dict) and mongo_info.get("status") == "connected":
                st.success("🍃 MongoDB OK")
                st.write(f"📚 Livres: {mongo_info.get('livres', 0)}")
                st.write(f"💬 Critiques: {mongo_info.get('critiques', 0)}")
            else:
                st.warning("🍃 MongoDB KO")
        else:
            st.error("❌ API non accessible")
        
        st.divider()
        
        # Navigation
        st.header("🧭 Navigation")
        
        # Utiliser session_state pour la navigation
        if "current_page" not in st.session_state:
            st.session_state.current_page = "🏠 Accueil"
        
        page = st.selectbox(
            "Choisir une page",
            ["🏠 Accueil", "📚 Livres MongoDB", "💬 Critiques", "🎯 Analytics", "🗄️ PostgreSQL", "👤 Mon Profil"],
            index=["🏠 Accueil", "📚 Livres MongoDB", "💬 Critiques", "🎯 Analytics", "🗄️ PostgreSQL", "👤 Mon Profil"].index(st.session_state.current_page),
            key="navigation_selectbox"
        )
        
        # Mettre à jour la page courante
        st.session_state.current_page = page
    
    # Contenu principal selon la page sélectionnée
    if page == "🏠 Accueil":
        show_home_dashboard()
    elif page == "📚 Livres MongoDB":
        show_mongo_books()
    elif page == "💬 Critiques":
        show_critiques()
    elif page == "🎯 Analytics":
        show_analytics()
    elif page == "🗄️ PostgreSQL":
        show_postgres_data()
    elif page == "👤 Mon Profil":
        show_user_profile()

def show_home_dashboard():
    """Dashboard d'accueil"""
    st.header("🏠 Dashboard")
    
    # Métriques générales
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Test rapide des endpoints (sans headers d'abord)
    status_summary, data_summary = make_api_request("/summary")
    
    with col1:
        if status_summary == 200 and isinstance(data_summary, dict):
            livres_count = data_summary.get("data", {}).get("livres_mongodb", "N/A")
            st.metric("📚 Livres MongoDB", livres_count)
        else:
            # Fallback : essayer avec headers
            status_summary_auth, data_summary_auth = make_api_request("/summary", headers=headers)
            if status_summary_auth == 200 and isinstance(data_summary_auth, dict):
                livres_count = data_summary_auth.get("data", {}).get("livres_mongodb", "N/A")
                st.metric("📚 Livres MongoDB", livres_count)
            else:
                st.metric("📚 Livres MongoDB", "🔍")
    
    with col2:
        if status_summary == 200 and isinstance(data_summary, dict):
            critiques_count = data_summary.get("data", {}).get("critiques_babelio", "N/A")
            st.metric("💬 Critiques", critiques_count)
        else:
            # Fallback
            status_summary_auth, data_summary_auth = make_api_request("/summary", headers=headers)
            if status_summary_auth == 200 and isinstance(data_summary_auth, dict):
                critiques_count = data_summary_auth.get("data", {}).get("critiques_babelio", "N/A")
                st.metric("💬 Critiques", critiques_count)
            else:
                st.metric("💬 Critiques", "🔍")
    
    with col3:
        st.metric("🔐 Authentification", "JWT")
    
    with col4:
        st.metric("🎯 Version API", "3.0.0")
    
    # Accès rapide
    st.subheader("🚀 Accès rapide")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📚 Explorer les livres", use_container_width=True):
            st.session_state.current_page = "📚 Livres MongoDB"
            st.rerun()
    
    with col2:
        if st.button("💬 Voir les critiques", use_container_width=True):
            st.session_state.current_page = "💬 Critiques"
            st.rerun()
    
    with col3:
        if st.button("🎯 Voir les analytics", use_container_width=True):
            st.session_state.current_page = "🎯 Analytics"
            st.rerun()
    
    with col4:
        if st.button("🗄️ Données PostgreSQL", use_container_width=True):
            st.session_state.current_page = "🗄️ PostgreSQL"
            st.rerun()

def show_mongo_books():
    """Page des livres MongoDB"""
    st.header("📚 Livres MongoDB")
    
    # Test avec et sans headers pour voir quel endpoint fonctionne
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Test rapide de l'API
    with st.expander("🔧 Test de l'API"):
        status_test, response_test = make_api_request("/mongo-livres/livres", params={"limit": 3})
        if status_test == 200:
            st.success("✅ API MongoDB accessible")
            st.write(f"Exemple: {len(response_test.get('data', []))} livres trouvés")
        else:
            st.error(f"❌ API non accessible: {response_test}")
    
    # Recherche
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Rechercher un livre", placeholder="Titre, auteur...")
    with col2:
        limit = st.selectbox("Nombre de résultats", [10, 20, 50, 100], index=1)
    
    if search_query:
        # Recherche
        params = {"q": search_query, "limit": limit}
        status_code, response = make_api_request("/mongo-livres/livres/search", params=params)
        
        if status_code == 200:
            # L'API retourne les données dans response["data"] pour les recherches
            livres = response.get("data", [])
            st.success(f"✅ {len(livres)} livres trouvés")
            
            for livre in livres:
                # Gérer les auteurs (peut être une liste ou une string)
                auteurs = livre.get('auteurs', ['N/A'])
                if isinstance(auteurs, list):
                    auteurs_str = ', '.join(auteurs) if auteurs else 'N/A'
                else:
                    auteurs_str = str(auteurs)
                
                # Gérer les genres (peut être une liste)
                genres = livre.get('tous_les_genres', [])
                if isinstance(genres, list):
                    genres_str = ', '.join(genres[:3]) if genres else 'N/A'  # Afficher max 3 genres
                else:
                    genres_str = str(genres)
                
                with st.expander(f"📖 {livre.get('titre', 'Sans titre')} - {auteurs_str}"):
                    display_livre_details(livre)
        else:
            st.error(f"❌ Erreur de recherche: {response}")
    else:
        # Liste générale
        params = {"limit": limit}
        status_code, response = make_api_request("/mongo-livres/livres", params=params)
        
        if status_code == 200:
            # L'API retourne les données dans response["data"] pour la liste
            livres = response.get("data", [])
            st.info(f"📚 Affichage de {len(livres)} livres")
            
            # Affichage des livres en cards
            if livres:
                for livre in livres:
                    # Gérer les auteurs
                    auteurs = livre.get('auteurs', ['N/A'])
                    if isinstance(auteurs, list):
                        auteurs_str = ', '.join(auteurs) if auteurs else 'N/A'
                    else:
                        auteurs_str = str(auteurs)
                    
                    with st.expander(f"📖 {livre.get('titre', 'Sans titre')} - {auteurs_str}"):
                        display_livre_details(livre)
                
                # Option pour afficher en tableau aussi
                if st.checkbox("🗂️ Afficher en tableau"):
                    df = pd.DataFrame(livres)
                    st.dataframe(df, use_container_width=True)
            else:
                st.warning("Aucun livre trouvé dans la réponse")
        else:
            st.error(f"❌ Impossible de charger les livres: {response}")

def display_livre_details(livre):
    """Afficher les détails complets d'un livre avec ses critiques"""
    
    # Informations principales du livre
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Titre et auteurs
        st.markdown(f"### 📖 {livre.get('titre', 'Sans titre')}")
        
        # Auteurs
        auteurs = livre.get('auteurs', ['N/A'])
        if isinstance(auteurs, list):
            auteurs_str = ', '.join(auteurs) if auteurs else 'N/A'
        else:
            auteurs_str = str(auteurs)
        st.write(f"**✍️ Auteur(s):** {auteurs_str}")
        
        # Genres
        genres = livre.get('tous_les_genres', [])
        if isinstance(genres, list):
            genres_str = ', '.join(genres[:5]) if genres else 'N/A'
        else:
            genres_str = str(genres)
        st.write(f"**🎭 Genres:** {genres_str}")
        
        # Résumé
        if livre.get('resume'):
            st.write("**📝 Résumé:**")
            resume = livre['resume']
            if len(resume) > 300:
                # Afficher un aperçu avec option pour voir plus
                st.write(resume[:300] + "...")
                if st.button("📖 Lire le résumé complet", key=f"resume_{livre.get('_id', 'unknown')}"):
                    st.write("**Résumé complet:**")
                    st.write(resume)
            else:
                st.write(resume)
    
    with col2:
        # Métriques
        st.metric("⭐ Note", f"{livre.get('note', 'N/A')}/5")
        st.metric("🌍 Langue", livre.get('langue', 'N/A'))
        
        # ISBN si disponible
        if livre.get('isbn'):
            st.write(f"**📚 ISBN:** {livre.get('isbn')}")
        
        # Autres infos
        if livre.get('editeur'):
            st.write(f"**🏢 Éditeur:** {livre.get('editeur')}")
        if livre.get('date_publication'):
            st.write(f"**📅 Publication:** {livre.get('date_publication')}")
    
    with col3:
        # Informations techniques
        if livre.get('nombre_pages'):
            st.metric("📄 Pages", livre.get('nombre_pages'))
        
        # URL Babelio si disponible
        if livre.get('url_babelio'):
            st.markdown(f"🔗 [Voir sur Babelio]({livre.get('url_babelio')})")
        
        # Date d'import
        if livre.get('_import_date'):
            st.write(f"**📥 Importé:** {livre.get('_import_date')}")
    
    # Section critiques
    st.divider()
    st.subheader("💬 Critiques de ce livre")
    
    # Récupérer les critiques pour ce livre
    livre_id = livre.get('_id')
    if livre_id:
        # Essayer de récupérer les critiques par ID du livre
        status_critiques, critiques_response = make_api_request(f"/mongo-livres/critiques/livre/{livre_id}")
        
        if status_critiques == 200:
            critiques = critiques_response.get('data', [])
            if critiques:
                st.success(f"✅ {len(critiques)} critique(s) trouvée(s)")
                
                for i, critique in enumerate(critiques, 1):
                    st.markdown(f"**💬 Critique #{i} - Note: {critique.get('note_babelio', 'N/A')}/5**")
                    display_critique_inline(critique)
                    st.divider()
            else:
                st.info("ℹ️ Aucune critique trouvée pour ce livre")
        else:
            # Fallback : rechercher par titre
            titre = livre.get('titre', '')
            if titre:
                status_search, search_response = make_api_request("/mongo-livres/critiques/search", params={"q": titre, "limit": 5})
                if status_search == 200:
                    critiques = search_response.get('data', [])
                    if critiques:
                        st.info(f"🔍 {len(critiques)} critique(s) trouvée(s) par recherche de titre")
                        for i, critique in enumerate(critiques, 1):
                            st.markdown(f"**💬 Critique #{i} - Note: {critique.get('note_babelio', 'N/A')}/5**")
                            display_critique_inline(critique)
                            st.divider()
                    else:
                        st.info("ℹ️ Aucune critique trouvée pour ce livre")
                else:
                    st.warning("⚠️ Impossible de récupérer les critiques")
    else:
        st.warning("⚠️ ID du livre non disponible pour récupérer les critiques")

def display_critique_inline(critique):
    """Afficher une critique de manière inline"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Texte de la critique
        if critique.get('critique_babelio'):
            st.write("**💬 Critique:**")
            critique_text = critique['critique_babelio']
            if len(critique_text) > 500:
                with st.expander("Lire la critique complète"):
                    st.write(critique_text)
                st.write(critique_text[:500] + "...")
            else:
                st.write(critique_text)
        
        # Tags
        if critique.get('tags_babelio'):
            tags = critique['tags_babelio']
            if isinstance(tags, list) and tags:
                st.write(f"**🏷️ Tags:** {', '.join(tags[:5])}")
    
    with col2:
        # Métriques de la critique
        st.metric("⭐ Note", f"{critique.get('note_babelio', 'N/A')}/5")
        if critique.get('nombre_votes_babelio'):
            st.metric("🗳️ Votes", critique.get('nombre_votes_babelio', 0))
        
        # Date de critique uniquement
        if critique.get('date_critique'):
            st.write(f"📅 **Date:** {critique['date_critique']}")
        
        # Lien Babelio
        if critique.get('url_babelio'):
            st.markdown(f"🔗 [Voir sur Babelio]({critique.get('url_babelio')})")

def show_critiques():
    """Page des critiques de livres"""
    st.header("💬 Critiques de Livres")
    
    # Test avec et sans headers pour voir quel endpoint fonctionne
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Test rapide de l'API
    with st.expander("🔧 Test de l'API Critiques"):
        status_test, response_test = make_api_request("/mongo-livres/critiques", params={"limit": 3})
        if status_test == 200:
            st.success("✅ API Critiques accessible")
            critiques = response_test.get('data', [])
            st.write(f"Exemple: {len(critiques)} critiques trouvées")
            
            # Afficher la structure des données pour debug
            if critiques:
                st.write("**📋 Structure des données de critiques:**")
                exemple_critique = critiques[0]
                st.write("🔍 Champs disponibles:", list(exemple_critique.keys()))
                st.json(exemple_critique)
        else:
            st.error(f"❌ API non accessible: {response_test}")
    
    # Filtres et recherche
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Rechercher par titre de livre", placeholder="Titre du livre...")
    with col2:
        min_note = st.selectbox("Note minimale", [0, 1, 2, 3, 4, 5], index=0)
    with col3:
        limit = st.selectbox("Nombre de résultats", [10, 20, 50, 100], index=1)
    
    # Onglets pour différentes vues
    tab1, tab2, tab3 = st.tabs(["📋 Liste des critiques", "⭐ Mieux notées", "📊 Statistiques"])
    
    with tab1:
        if search_query:
            # Recherche par titre de livre
            st.subheader(f"🔍 Recherche: '{search_query}'")
            params = {"q": search_query, "limit": limit}
            status_code, response = make_api_request("/mongo-livres/critiques/search", params=params)
            
            if status_code == 200:
                critiques = response.get("data", [])
                st.success(f"✅ {len(critiques)} critiques trouvées")
                display_critiques_list(critiques)
            else:
                st.error(f"❌ Erreur de recherche: {response}")
        else:
            # Liste générale des critiques
            params = {"limit": limit}
            if min_note > 0:
                params["min_note"] = min_note
            
            status_code, response = make_api_request("/mongo-livres/critiques", params=params)
            
            if status_code == 200:
                critiques = response.get("data", [])
                st.info(f"💬 Affichage de {len(critiques)} critiques")
                display_critiques_list(critiques)
            else:
                st.error(f"❌ Impossible de charger les critiques: {response}")
    
    with tab2:
        # Critiques les mieux notées
        st.subheader("⭐ Critiques les mieux notées")
        status_code, response = make_api_request("/mongo-extras/critiques/top-notes", params={"limit": limit})
        
        if status_code == 200:
            critiques = response.get("data", [])
            st.success(f"✅ {len(critiques)} critiques trouvées")
            display_critiques_detailed(critiques)
        else:
            st.error(f"❌ Impossible de charger les meilleures critiques: {response}")
    
    with tab3:
        # Statistiques des critiques
        st.subheader("📊 Statistiques des critiques")
        show_critiques_stats()
        
        # Aide pour comprendre la structure des données
        st.divider()
        st.subheader("🔍 Structure des données")
        if st.button("Analyser la structure des critiques"):
            status_sample, sample_response = make_api_request("/mongo-livres/sample")
            if status_sample == 200:
                echantillons = sample_response.get("echantillons", {})
                critiques_data = echantillons.get("critiques", {})
                
                if critiques_data:
                    st.write("**📋 Champs disponibles dans les critiques:**")
                    champs = critiques_data.get("champs_disponibles", [])
                    st.write(champs)
                    
                    sample_critiques = critiques_data.get("sample", [])
                    if sample_critiques:
                        st.write("**📄 Exemple de critique:**")
                        st.json(sample_critiques[0])
            else:
                st.error("Impossible de récupérer l'échantillon")

def display_critiques_list(critiques):
    """Afficher une liste de critiques en format compact"""
    if not critiques:
        st.warning("Aucune critique trouvée")
        return
    
    for i, critique in enumerate(critiques):
        # Gérer les différents champs possibles pour titre et auteur
        titre = critique.get('titre') or critique.get('titre_livre', 'Livre inconnu')
        auteur = critique.get('auteur') or critique.get('auteur_livre', 'Auteur inconnu')
        
        st.markdown(f"**💬 {titre} - Note: {critique.get('note_babelio', 'N/A')}/5**")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**📖 Livre:** {titre}")
            st.write(f"**✍️ Auteur:** {auteur}")
            
            # Critique Babelio - plusieurs champs possibles
            critique_text = None
            if critique.get('critique_babelio'):
                critique_text = critique['critique_babelio']
            elif critique.get('critiques_babelio') and isinstance(critique['critiques_babelio'], list):
                # Si c'est un array de critiques, prendre la première
                if critique['critiques_babelio']:
                    premiere_critique = critique['critiques_babelio'][0]
                    if isinstance(premiere_critique, dict):
                        critique_text = premiere_critique.get('texte')
                    else:
                        critique_text = str(premiere_critique)
            elif critique.get('resume_babelio'):
                critique_text = critique['resume_babelio']
            
            if critique_text:
                if len(critique_text) > 300:
                    critique_text = critique_text[:300] + "..."
                st.write(f"**💬 Critique:** {critique_text}")
            else:
                st.write("**💬 Critique:** Non disponible")
            
            # Tags s'ils existent
            if critique.get('tags_babelio'):
                tags = critique['tags_babelio']
                if isinstance(tags, list):
                    st.write(f"**🏷️ Tags:** {', '.join(tags[:5])}")
            
            # ISBN si disponible
            if critique.get('isbn'):
                st.write(f"**📚 ISBN:** {critique['isbn']}")
        
        with col2:
            # Métriques
            st.metric("⭐ Note Babelio", f"{critique.get('note_babelio', 'N/A')}/5")
            if critique.get('nombre_votes_babelio'):
                st.metric("🗳️ Votes", critique.get('nombre_votes_babelio', 0))
            
            # Date si disponible (uniquement date_critique)
            if critique.get('date_critique'):
                st.write(f"📅 **Date:** {critique['date_critique']}")
            
            # URL Babelio si disponible
            if critique.get('url_babelio'):
                st.markdown(f"🔗 [Voir sur Babelio]({critique['url_babelio']})")
        
        st.divider()  # Séparateur entre chaque critique

def display_critiques_detailed(critiques):
    """Afficher les critiques en format détaillé"""
    if not critiques:
        st.warning("Aucune critique trouvée")
        return
    
    for i, critique in enumerate(critiques, 1):
        # Gérer les différents champs possibles
        titre = critique.get('titre') or critique.get('titre_livre', 'Livre inconnu')
        auteur = critique.get('auteur') or critique.get('auteur_livre', 'Auteur inconnu')
        
        st.markdown(f"### {i}. 📖 {titre}")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**✍️ Auteur:** {auteur}")
            
            # Affichage de la critique complète - plusieurs sources possibles
            critique_text = None
            if critique.get('critique_babelio'):
                critique_text = critique['critique_babelio']
            elif critique.get('critiques_babelio') and isinstance(critique['critiques_babelio'], list):
                if critique['critiques_babelio']:
                    premiere_critique = critique['critiques_babelio'][0]
                    if isinstance(premiere_critique, dict):
                        critique_text = premiere_critique.get('texte')
                    else:
                        critique_text = str(premiere_critique)
            elif critique.get('resume_babelio'):
                critique_text = critique['resume_babelio']
            
            if critique_text:
                st.write("**💬 Critique Babelio:**")
                st.write(critique_text)
            else:
                st.write("**💬 Critique:** Non disponible")
        
        with col2:
            st.metric("⭐ Note", f"{critique.get('note_babelio', 'N/A')}/5")
            st.metric("🗳️ Votes", critique.get('nombre_votes_babelio', 0))
        
        with col3:
            # Date de critique (pas d'extraction)
            if critique.get('date_critique'):
                st.write(f"📅 **Date:** {critique['date_critique']}")
            
            # Tags
            if critique.get('tags_babelio'):
                tags = critique['tags_babelio']
                if isinstance(tags, list) and tags:
                    st.write("**🏷️ Tags:**")
                    for tag in tags[:3]:
                        st.write(f"• {tag}")
        
        st.divider()

def show_critiques_stats():
    """Afficher les statistiques des critiques"""
    # Récupérer les analytics pour les stats
    status_code, response = make_api_request("/mongo-extras/analytics")
    
    if status_code == 200:
        analytics = response.get("analytics", {})
        
        if "stats_critiques_babelio" in analytics:
            stats = analytics["stats_critiques_babelio"]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🔻 Note minimale", f"{stats.get('min_note', 0):.1f}/5")
            with col2:
                st.metric("🔺 Note maximale", f"{stats.get('max_note', 0):.1f}/5")
            with col3:
                st.metric("📊 Note moyenne", f"{stats.get('avg_note', 0):.2f}/5")
            with col4:
                st.metric("🗳️ Total des votes", f"{stats.get('total_votes', 0):,}")
        
        # Graphiques supplémentaires si on a des données de distribution
        st.subheader("📈 Distribution des notes")
        
        # Simuler une distribution des notes (à adapter selon l'API)
        import numpy as np
        notes_sample = np.random.normal(3.5, 1, 1000)  # Simulation temporaire
        notes_sample = np.clip(notes_sample, 0, 5)
        
        fig = px.histogram(x=notes_sample, nbins=20, title="Distribution des notes des critiques")
        fig.update_layout(xaxis_title="Note", yaxis_title="Nombre de critiques")
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("❌ Impossible de récupérer les statistiques")

def show_analytics():
    """Page analytics"""
    st.header("🎯 Analytics")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Analytics complets
    status_code, response = make_api_request("/mongo-extras/analytics")
    
    if status_code == 200:
        analytics = response.get("analytics", {})
        
        if not analytics:
            st.warning("⚠️ Aucune donnée analytics trouvée")
            st.json(response)
            return
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            # Top genres (utiliser la vraie structure)
            if "top_genres" in analytics:
                genres_data = analytics["top_genres"]
                if genres_data:
                    df_genres = pd.DataFrame(genres_data)
                    df_genres.columns = ["Genre", "Nombre"]
                    fig = px.bar(df_genres.head(10), x="Genre", y="Nombre", title="📊 Top 10 des Genres")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Aucune donnée de genres")
            else:
                st.warning("Clé 'top_genres' manquante dans analytics")
        
        with col2:
            # Répartition par langue (à la place des auteurs temporairement)
            if "repartition_langues" in analytics:
                langues_data = analytics["repartition_langues"]
                if langues_data:
                    df_langues = pd.DataFrame(langues_data)
                    df_langues.columns = ["Langue", "Nombre"]
                    fig = px.pie(df_langues.head(8), values="Nombre", names="Langue", title="🌍 Répartition par langue")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Aucune donnée de langues")
            else:
                st.warning("Clé 'repartition_langues' manquante dans analytics")
        
        # Statistiques générales
        if "stats_critiques_babelio" in analytics:
            stats = analytics["stats_critiques_babelio"]
            st.subheader("📈 Statistiques Critiques Babelio")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔻 Note min", f"{stats.get('min_note', 0):.1f}/5")
            with col2:
                st.metric("🔺 Note max", f"{stats.get('max_note', 0):.1f}/5")
            with col3:
                st.metric("📊 Moyenne", f"{stats.get('avg_note', 0):.2f}/5")
            with col4:
                st.metric("🗳️ Total votes", f"{stats.get('total_votes', 0):,}")
        
        # Répartition des notes des livres
        if "repartition_notes_livres" in analytics:
            st.subheader("⭐ Répartition des notes des livres")
            notes_data = analytics["repartition_notes_livres"]
            if notes_data:
                df_notes = pd.DataFrame(notes_data)
                df_notes.columns = ["Note", "Nombre"]
                fig = px.bar(df_notes, x="Note", y="Nombre", title="Distribution des notes")
                st.plotly_chart(fig, use_container_width=True)
        
        # Livres récents
        if "livres_recents" in analytics:
            st.subheader("📅 Livres récemment ajoutés")
            livres_recents = analytics["livres_recents"]
            if livres_recents:
                for livre in livres_recents[:3]:
                    with st.expander(f"📖 {livre.get('titre', 'Sans titre')}"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write(f"**Auteur(s):** {', '.join(livre.get('auteurs', ['N/A']))}")
                            if livre.get('resume'):
                                resume = livre['resume'][:200] + "..." if len(livre.get('resume', '')) > 200 else livre['resume']
                                st.write(f"**Résumé:** {resume}")
                        with col2:
                            st.write(f"**Note:** {livre.get('note', 'N/A')}/5")
                            st.write(f"**Langue:** {livre.get('langue', 'N/A')}")
                            if livre.get('tous_les_genres'):
                                st.write(f"**Genres:** {', '.join(livre['tous_les_genres'][:3])}")
        
        # Ajout d'analytics supplémentaires via d'autres endpoints
        st.divider()
        st.subheader("🔍 Analytics supplémentaires")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top auteurs via endpoint séparé
            status_auteurs, response_auteurs = make_api_request("/mongo-extras/auteurs")
            if status_auteurs == 200 and response_auteurs.get("success"):
                auteurs_data = response_auteurs.get("data", [])[:10]
                if auteurs_data:
                    df_auteurs = pd.DataFrame(auteurs_data)
                    df_auteurs.columns = ["Auteur", "Nombre"]
                    fig = px.bar(df_auteurs, x="Auteur", y="Nombre", title="✍️ Top 10 des Auteurs")
                    fig.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Métriques générales
            status_summary, summary_data = make_api_request("/summary")
            if status_summary == 200:
                data = summary_data.get("data", {})
                st.metric("📚 Total Livres", data.get("livres_mongodb", 0))
                st.metric("💬 Total Critiques", data.get("critiques_babelio", 0))
                st.metric("🔗 Version API", data.get("version_api", "N/A"))
        
    else:
        st.error(f"❌ Impossible de charger les analytics: {response}")

def show_postgres_data():
    """Page données PostgreSQL"""
    st.header("🗄️ Données PostgreSQL - Schéma Test")
    
    # Utilisation de l'authentification JWT
    jwt_headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Ajouter des onglets pour organiser le contenu
    tab1, tab2, tab3 = st.tabs(["📚 Livres", "📊 Analytics & Graphiques", "🔧 Debug"])
    
    with tab1:
        # Livres de la vraie base de données (schéma test)
        st.subheader("📚 Livres PostgreSQL (Schéma Test)")
        
        # Paramètres de recherche
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_query = st.text_input("🔍 Rechercher un livre", placeholder="Titre du livre...")
        with col2:
            limit = st.selectbox("Nombre de résultats", [10, 20, 50, 100], index=1)
        with col3:
            # Bouton pour rafraîchir
            if st.button("🔄 Actualiser"):
                st.rerun()
        
        # Construire les paramètres de recherche
        params = {"limit": limit}
        if search_query:
            params["search"] = search_query
        
        # Appel API pour les livres
        status_code, response = make_api_request("/postgres/livres", params=params)
        
        if status_code == 200:
            livres = response.get("data", response) if isinstance(response, dict) else response
            if livres:
                st.success(f"✅ {len(livres)} livre(s) trouvé(s)")
                
                # Affichage des livres
                for livre in livres:
                    with st.expander(f"📖 {livre.get('titre', 'Titre inconnu')} - {livre.get('auteur_nom', 'Auteur inconnu')}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**📖 Titre:** {livre.get('titre', 'N/A')}")
                            st.write(f"**✍️ Auteur:** {livre.get('auteur_nom', 'N/A')} {livre.get('auteur_prenom', '')}")
                            st.write(f"**📘 Sous-titre:** {livre.get('sous_titre', 'N/A')}")
                            if livre.get('description'):
                                description = livre['description'][:200] + "..." if len(livre.get('description', '')) > 200 else livre['description']
                                st.write(f"**📝 Description:** {description}")
                            st.write(f"**🏢 Éditeur:** {livre.get('editeur_nom', 'N/A')}")
                            st.write(f"**🌍 Pays:** {livre.get('editeur_pays', 'N/A')}")
                        
                        with col2:
                            if livre.get('isbn_10'):
                                st.write(f"**📚 ISBN-10:** {livre['isbn_10']}")
                            if livre.get('isbn_13'):
                                st.write(f"**📚 ISBN-13:** {livre['isbn_13']}")
                            if livre.get('date_publication'):
                                st.write(f"**📅 Publication:** {livre['date_publication']}")
                            if livre.get('annee_publication'):
                                st.write(f"**📅 Année:** {livre['annee_publication']}")
                            if livre.get('nombre_pages'):
                                st.write(f"**📄 Pages:** {livre['nombre_pages']}")
                            if livre.get('format_physique'):
                                st.write(f"**📏 Format:** {livre['format_physique']}")
                            if livre.get('langue_nom'):
                                st.write(f"**🌐 Langue:** {livre['langue_nom']}")
                            if livre.get('sujet_nom'):
                                st.write(f"**🏷️ Sujet:** {livre['sujet_nom']}")
            else:
                st.info("Aucun livre PostgreSQL trouvé dans le schéma test")
        else:
            st.error(f"❌ Erreur lors de la récupération des livres: {response}")
        
        # Statistiques PostgreSQL réelles (nécessite JWT)
        st.subheader("📊 Statistiques PostgreSQL - Vraies Données")
        status_code, response = make_api_request("/postgres/livres/stats/general", headers=jwt_headers)
        
        if status_code == 200:
            stats = response
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📚 Total livres", stats.get("total_livres", 0))
            with col2:
                st.metric("✍️ Total auteurs", stats.get("total_auteurs", 0))
            with col3:
                st.metric("🏢 Total éditeurs", stats.get("total_editeurs", 0))
            with col4:
                st.metric("🌐 Total langues", stats.get("total_langues", 0))
            
            st.info(f"📊 Base: {stats.get('database', 'PostgreSQL (schéma test)')}")
        else:
            st.warning(f"⚠️ Impossible de charger les statistiques: {response}")
    
    with tab2:
        # NOUVELLE SECTION : Analytics PostgreSQL avec graphiques
        st.subheader("📊 Analytics PostgreSQL - Graphiques")
        st.info("🆕 **Nouveau !** Analytics PostgreSQL équivalents à MongoDB")
        
        # Récupérer les analytics PostgreSQL
        status_analytics, analytics_response = make_api_request("/postgres-extras/analytics", headers=jwt_headers)
        
        if status_analytics == 200 and analytics_response.get("success"):
            analytics = analytics_response.get("analytics", {})
            
            # Section 1: Statistiques générales
            st.subheader("🎯 Statistiques Générales")
            stats_gen = analytics.get("statistiques_generales", {})
            if stats_gen:
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("📚 Livres", f"{stats_gen.get('total_livres', 0):,}")
                with col2:
                    st.metric("✍️ Auteurs", f"{stats_gen.get('total_auteurs', 0):,}")
                with col3:
                    st.metric("🏢 Éditeurs", f"{stats_gen.get('total_editeurs', 0):,}")
                with col4:
                    st.metric("🌐 Langues", f"{stats_gen.get('total_langues', 0):,}")
                with col5:
                    st.metric("🏷️ Sujets", f"{stats_gen.get('total_sujets', 0):,}")
            
            # Section 2: Graphiques
            col1, col2 = st.columns(2)
            
            with col1:
                # Top auteurs
                if "top_auteurs" in analytics:
                    st.subheader("✍️ Top 10 des Auteurs")
                    top_auteurs = analytics["top_auteurs"][:10]
                    if top_auteurs:
                        import pandas as pd
                        import plotly.express as px
                        
                        df_auteurs = pd.DataFrame(top_auteurs)
                        df_auteurs.columns = ["Auteur", "Nombre de livres"]
                        fig = px.bar(
                            df_auteurs, 
                            x="Auteur", 
                            y="Nombre de livres",
                            title="Top 10 des auteurs PostgreSQL",
                            color="Nombre de livres",
                            color_continuous_scale="Blues"
                        )
                        fig.update_layout(xaxis_tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Top éditeurs
                if "top_editeurs" in analytics:
                    st.subheader("🏢 Top 10 des Éditeurs")
                    top_editeurs = analytics["top_editeurs"][:10]
                    if top_editeurs:
                        df_editeurs = pd.DataFrame(top_editeurs)
                        df_editeurs["label"] = df_editeurs["editeur"] + " (" + df_editeurs["pays"].fillna("N/A") + ")"
                        fig = px.bar(
                            df_editeurs, 
                            x="label", 
                            y="nb_livres",
                            title="Top 10 des éditeurs PostgreSQL",
                            color="nb_livres",
                            color_continuous_scale="Greens"
                        )
                        fig.update_layout(xaxis_tickangle=45)
                        fig.update_xaxes(title="Éditeur (Pays)")
                        fig.update_yaxes(title="Nombre de livres")
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Répartition par langues
                if "repartition_langues" in analytics:
                    st.subheader("🌍 Répartition par Langues")
                    langues_data = analytics["repartition_langues"][:10]
                    if langues_data:
                        df_langues = pd.DataFrame(langues_data)
                        fig = px.pie(
                            df_langues, 
                            values="nb_livres", 
                            names="langue",
                            title="Répartition des livres par langue"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Top sujets/genres
                if "top_sujets" in analytics:
                    st.subheader("🏷️ Top Sujets/Genres")
                    top_sujets = analytics["top_sujets"][:10]
                    if top_sujets:
                        df_sujets = pd.DataFrame(top_sujets)
                        df_sujets["label"] = df_sujets["sujet"] + " (" + df_sujets["categorie"].fillna("N/A") + ")"
                        fig = px.bar(
                            df_sujets, 
                            x="label", 
                            y="nb_livres",
                            title="Top 10 des sujets PostgreSQL",
                            color="nb_livres",
                            color_continuous_scale="Purples"
                        )
                        fig.update_layout(xaxis_tickangle=45)
                        fig.update_xaxes(title="Sujet (Catégorie)")
                        fig.update_yaxes(title="Nombre de livres")
                        st.plotly_chart(fig, use_container_width=True)
            
            # Section 3: Graphiques d'évolution temporelle
            st.subheader("📅 Évolution Temporelle")
            
            if "repartition_annees" in analytics:
                annees_data = analytics["repartition_annees"]
                if annees_data:
                    df_annees = pd.DataFrame(annees_data)
                    df_annees = df_annees.sort_values("annee")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Graphique en courbe
                        fig_line = px.line(
                            df_annees, 
                            x="annee", 
                            y="nb_livres",
                            title="Évolution du nombre de livres par année",
                            markers=True
                        )
                        fig_line.update_xaxes(title="Année de publication")
                        fig_line.update_yaxes(title="Nombre de livres")
                        st.plotly_chart(fig_line, use_container_width=True)
                    
                    with col2:
                        # Graphique en barres des 10 dernières années
                        df_recent = df_annees.tail(10)
                        fig_bar = px.bar(
                            df_recent, 
                            x="annee", 
                            y="nb_livres",
                            title="10 dernières années (livres publiés)",
                            color="nb_livres",
                            color_continuous_scale="Oranges"
                        )
                        fig_bar.update_xaxes(title="Année")
                        fig_bar.update_yaxes(title="Nombre de livres")
                        st.plotly_chart(fig_bar, use_container_width=True)
            
            # Section 4: Statistiques des pages
            if "statistiques_pages" in analytics:
                stats_pages = analytics["statistiques_pages"]
                if stats_pages and stats_pages.get("total_avec_pages", 0) > 0:
                    st.subheader("📄 Statistiques des Pages")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📖 Pages min", f"{stats_pages.get('min_pages', 0)}")
                    with col2:
                        st.metric("📚 Pages max", f"{stats_pages.get('max_pages', 0)}")
                    with col3:
                        st.metric("📊 Moyenne", f"{stats_pages.get('avg_pages', 0)}")
                    with col4:
                        st.metric("📈 Total avec pages", f"{stats_pages.get('total_avec_pages', 0):,}")
                    
                    # Récupérer la distribution des pages
                    status_pages, pages_response = make_api_request("/postgres-extras/livres/stats-pages", headers=jwt_headers)
                    if status_pages == 200 and pages_response.get("success"):
                        distribution = pages_response.get("distribution", [])
                        if distribution:
                            df_pages = pd.DataFrame(distribution)
                            fig_pages = px.bar(
                                df_pages, 
                                x="tranche", 
                                y="nb_livres",
                                title="Distribution des livres par nombre de pages",
                                color="nb_livres",
                                color_continuous_scale="Reds"
                            )
                            fig_pages.update_xaxes(title="Tranche de pages")
                            fig_pages.update_yaxes(title="Nombre de livres")
                            st.plotly_chart(fig_pages, use_container_width=True)
            
            # Section 5: Formats physiques
            if "repartition_formats" in analytics:
                formats_data = analytics["repartition_formats"]
                if formats_data:
                    st.subheader("📖 Formats Physiques")
                    df_formats = pd.DataFrame(formats_data)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Graphique en secteurs
                        fig_pie = px.pie(
                            df_formats, 
                            values="nb_livres", 
                            names="format",
                            title="Répartition par format physique"
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        # Graphique en barres horizontales
                        fig_bar = px.bar(
                            df_formats.head(10), 
                            x="nb_livres", 
                            y="format",
                            orientation='h',
                            title="Top 10 des formats",
                            color="nb_livres",
                            color_continuous_scale="Viridis"
                        )
                        fig_bar.update_xaxes(title="Nombre de livres")
                        fig_bar.update_yaxes(title="Format physique")
                        st.plotly_chart(fig_bar, use_container_width=True)
            
            # Bouton pour actualiser les analytics
            if st.button("🔄 Actualiser les analytics PostgreSQL"):
                st.rerun()
                
        else:
            st.error(f"❌ Impossible de charger les analytics PostgreSQL: {analytics_response}")
            st.info("💡 Vérifiez que l'API est démarrée et que vous êtes bien authentifié")
    
    with tab3:
        # Section de debug
        st.subheader("🔧 Debug - Informations techniques")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Lister les tables"):
                debug_status, debug_response = make_api_request("/postgres/livres/debug/tables")
                if debug_status == 200:
                    st.success("✅ Tables du schéma test:")
                    tables = debug_response.get("tables", [])
                    counts = debug_response.get("table_counts", {})
                    
                    for table in tables:
                        count = counts.get(table, "?")
                        st.write(f"• **{table}**: {count} enregistrements")
                else:
                    st.error(f"❌ Erreur debug: {debug_response}")
        
        with col2:
            if st.button("📊 Stats détaillées"):
                stats_status, stats_response = make_api_request("/postgres/livres/stats/general", headers=jwt_headers)
                if stats_status == 200:
                    st.success("✅ Statistiques détaillées:")
                    st.json(stats_response)
                else:
                    st.error(f"❌ Erreur stats: {stats_response}")
        
        # Test simple pour voir la structure de base
        st.write("**Test de requête simple:**")
        if st.button("🔍 Tester requête basique"):
            basic_status, basic_response = make_api_request("/postgres/livres?limit=1")
            if basic_status == 200:
                if basic_response:
                    st.success("✅ Requête réussie!")
                    st.json(basic_response[0] if isinstance(basic_response, list) else basic_response)
                else:
                    st.warning("⚠️ Aucun résultat mais pas d'erreur")
            else:
                st.error(f"❌ Erreur: {basic_response}")
        
        # Test des nouveaux endpoints analytics
        st.subheader("🆕 Test des nouveaux endpoints analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Tester analytics complet"):
                test_status, test_response = make_api_request("/postgres-extras/analytics", headers=jwt_headers)
                if test_status == 200:
                    st.success("✅ Analytics PostgreSQL OK!")
                    st.json(test_response)
                else:
                    st.error(f"❌ Erreur analytics: {test_response}")
        
        with col2:
            if st.button("✍️ Tester top auteurs"):
                test_status, test_response = make_api_request("/postgres-extras/auteurs/top?limit=5", headers=jwt_headers)
                if test_status == 200:
                    st.success("✅ Top auteurs OK!")
                    st.json(test_response)
                else:
                    st.error(f"❌ Erreur top auteurs: {test_response}")

def show_user_profile():
    """Page profil utilisateur"""
    st.header("👤 Mon Profil")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    status_code, response = get_user_profile(st.session_state.token)
    
    if status_code == 200:
        st.markdown(f"""
        <div class="user-info">
            <h3>👤 Informations personnelles</h3>
            <p><strong>Nom:</strong> {response.get('first_name', '')} {response.get('last_name', '')}</p>
            <p><strong>Email:</strong> {response.get('email', '')}</p>
            <p><strong>ID:</strong> {response.get('id', '')}</p>
            <p><strong>Actif:</strong> {'✅ Oui' if response.get('is_active', False) else '❌ Non'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🔧 Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Rafraîchir le profil", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🚪 Se déconnecter", use_container_width=True):
                logout_user(st.session_state.token)
                for key in ['token', 'user_email', 'authenticated']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    else:
        st.error(f"❌ Impossible de charger le profil: {response}")

def main():
    """Fonction principale"""
    
    # Vérification API
    api_status, _ = check_api_status()
    if not api_status:
        st.error("❌ **L'API n'est pas accessible**")
        st.info("🚀 Démarrez l'API avec: `cd api && python start.py`")
        st.stop()
    
    # Gestion de l'authentification
    if not st.session_state.get("authenticated", False):
        show_login_page()
    else:
        show_main_app()

if __name__ == "__main__":
    main()