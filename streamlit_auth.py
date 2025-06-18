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
        "username": email,  # L'API attend 'username' pour l'email
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
        page = st.selectbox(
            "Choisir une page",
            ["🏠 Accueil", "📚 Livres MongoDB", "🎯 Analytics", "🗄️ PostgreSQL", "👤 Mon Profil"]
        )
    
    # Contenu principal selon la page sélectionnée
    if page == "🏠 Accueil":
        show_home_dashboard()
    elif page == "📚 Livres MongoDB":
        show_mongo_books()
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
    
    # Test rapide des endpoints
    status_mongo, data_mongo = make_api_request("/mongo-livres/", headers=headers)
    status_summary, data_summary = make_api_request("/summary", headers=headers)
    
    with col1:
        if status_summary == 200 and isinstance(data_summary, dict):
            livres_count = data_summary.get("data", {}).get("livres_mongodb", "N/A")
            st.metric("📚 Livres MongoDB", livres_count)
        else:
            st.metric("📚 Livres MongoDB", "Error")
    
    with col2:
        if status_summary == 200 and isinstance(data_summary, dict):
            critiques_count = data_summary.get("data", {}).get("critiques_babelio", "N/A")
            st.metric("💬 Critiques", critiques_count)
        else:
            st.metric("💬 Critiques", "Error")
    
    with col3:
        st.metric("🔐 Authentification", "JWT")
    
    with col4:
        st.metric("🎯 Version API", "3.0.0")
    
    # Accès rapide
    st.subheader("🚀 Accès rapide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Explorer les livres", use_container_width=True):
            st.session_state.page = "📚 Livres MongoDB"
            st.rerun()
    
    with col2:
        if st.button("🎯 Voir les analytics", use_container_width=True):
            st.session_state.page = "🎯 Analytics"
            st.rerun()
    
    with col3:
        if st.button("🗄️ Données PostgreSQL", use_container_width=True):
            st.session_state.page = "🗄️ PostgreSQL"
            st.rerun()

def show_mongo_books():
    """Page des livres MongoDB"""
    st.header("📚 Livres MongoDB")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Recherche
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Rechercher un livre", placeholder="Titre, auteur...")
    with col2:
        limit = st.selectbox("Nombre de résultats", [10, 20, 50, 100], index=1)
    
    if search_query:
        # Recherche
        params = {"q": search_query, "limit": limit}
        status_code, response = make_api_request("/mongo-livres/livres/search", headers=headers, params=params)
        
        if status_code == 200:
            livres = response.get("livres", [])
            st.success(f"✅ {len(livres)} livres trouvés")
            
            for livre in livres:
                with st.expander(f"📖 {livre.get('titre', 'Sans titre')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Auteur:** {livre.get('auteur', 'N/A')}")
                        st.write(f"**Genre:** {livre.get('genre', 'N/A')}")
                    with col2:
                        st.write(f"**Note:** {livre.get('note', 'N/A')}/5")
                        st.write(f"**Année:** {livre.get('annee_publication', 'N/A')}")
        else:
            st.error(f"❌ Erreur de recherche: {response}")
    else:
        # Liste générale
        params = {"limit": limit}
        status_code, response = make_api_request("/mongo-livres/livres", headers=headers, params=params)
        
        if status_code == 200:
            livres = response.get("livres", [])
            st.info(f"📚 Affichage de {len(livres)} livres")
            
            # Affichage en tableau
            if livres:
                df = pd.DataFrame(livres)
                st.dataframe(df, use_container_width=True)
        else:
            st.error(f"❌ Impossible de charger les livres: {response}")

def show_analytics():
    """Page analytics"""
    st.header("🎯 Analytics")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Analytics complets
    status_code, response = make_api_request("/mongo-extras/analytics", headers=headers)
    
    if status_code == 200:
        analytics = response.get("analytics", {})
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            # Top genres
            if "genres" in analytics:
                genres_data = analytics["genres"]
                df_genres = pd.DataFrame(list(genres_data.items()), columns=["Genre", "Nombre"])
                fig = px.bar(df_genres.head(10), x="Genre", y="Nombre", title="📊 Top 10 des Genres")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top auteurs
            if "auteurs" in analytics:
                auteurs_data = analytics["auteurs"]
                df_auteurs = pd.DataFrame(list(auteurs_data.items()), columns=["Auteur", "Nombre"])
                fig = px.bar(df_auteurs.head(10), x="Auteur", y="Nombre", title="✍️ Top 10 des Auteurs")
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques générales
        if "general" in analytics:
            general = analytics["general"]
            st.subheader("📈 Statistiques générales")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📚 Total livres", general.get("total_livres", 0))
            with col2:
                st.metric("✍️ Total auteurs", general.get("total_auteurs", 0))
            with col3:
                st.metric("🎭 Total genres", general.get("total_genres", 0))
            with col4:
                st.metric("⭐ Note moyenne", f"{general.get('note_moyenne', 0):.1f}/5")
    else:
        st.error(f"❌ Impossible de charger les analytics: {response}")

def show_postgres_data():
    """Page données PostgreSQL"""
    st.header("🗄️ Données PostgreSQL")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Users
    st.subheader("👥 Utilisateurs")
    status_code, response = make_api_request("/postgres/users/", headers=headers)
    
    if status_code == 200:
        users = response
        if users:
            df_users = pd.DataFrame(users)
            st.dataframe(df_users, use_container_width=True)
        else:
            st.info("Aucun utilisateur PostgreSQL trouvé")
    else:
        st.error(f"❌ Erreur: {response}")
    
    # Books
    st.subheader("📚 Livres PostgreSQL")
    status_code, response = make_api_request("/postgres/books/", headers=headers)
    
    if status_code == 200:
        books = response
        if books:
            df_books = pd.DataFrame(books)
            st.dataframe(df_books, use_container_width=True)
        else:
            st.info("Aucun livre PostgreSQL trouvé")
    else:
        st.error(f"❌ Erreur: {response}")

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