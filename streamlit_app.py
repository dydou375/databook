"""
Interface Streamlit pour l'API DataBook
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="📚 DataBook Interface",
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
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
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

def make_api_request(endpoint, headers=None, params=None):
    """Faire une requête à l'API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            return True, response.json()
        elif response.status_code == 401:
            return False, "🔑 Clé API invalide"
        else:
            return False, f"❌ Erreur {response.status_code}"
    except Exception as e:
        return False, f"❌ Erreur: {str(e)}"

def main():
    # En-tête
    st.markdown("""
    <div class="main-header">
        <h1>📚 DataBook Interface</h1>
        <p>Interface pour votre API de gestion de livres</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Vérification API
    api_status, health_data = check_api_status()
    
    if not api_status:
        st.error("❌ **L'API n'est pas accessible**")
        st.info("🚀 Démarrez l'API avec: `python start.py`")
        st.stop()
    
    # Sidebar pour l'authentification
    with st.sidebar:
        st.header("🔐 Authentification")
        
        api_key = st.text_input(
            "Clé API",
            type="password",
            placeholder="databook-api-key-2024"
        )
        
        if st.button("💡 Clé par défaut"):
            st.session_state.api_key = "databook-api-key-2024"
            st.rerun()
        
        # Test simple de l'API
        st.write("---")
        st.subheader("🔧 Test API")
        if st.button("Test simple"):
            success, response = make_api_request("/")
            if success:
                st.success("✅ API accessible")
                st.json(response)
            else:
                st.error(f"❌ API non accessible: {response}")
        
        if 'api_key' in st.session_state:
            api_key = st.session_state.api_key
        
        # Test auth
        if api_key:
            headers = {"X-API-Key": api_key}
            success, response = make_api_request("/data/statistics/", headers)
            
            if success:
                st.success("✅ Connecté!")
                st.session_state.authenticated = True
                st.session_state.headers = headers
            else:
                st.error(f"❌ Clé invalide - Erreur: {response}")
                st.session_state.authenticated = False
        else:
            st.session_state.authenticated = False
        
        st.divider()
        st.header("📊 État API")
        if health_data:
            databases = health_data.get("databases", {})
            if databases.get("postgresql") == "connected":
                st.success("🐘 PostgreSQL OK")
            else:
                st.error("🐘 PostgreSQL KO")
            
            if databases.get("mongodb") == "connected":
                st.success("🍃 MongoDB OK")
            else:
                st.warning("🍃 MongoDB KO")
    
    # Onglets principaux
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Accueil", "📚 Livres", "✍️ Auteurs", "📊 Stats"])
    
    with tab1:
        show_home()
    
    with tab2:
        show_livres()
    
    with tab3:
        show_auteurs()
    
    with tab4:
        show_stats()

def show_home():
    """Page d'accueil"""
    st.header("🏠 Accueil")
    
    # Test connexion aux vraies données
    success_pg, response_pg = make_api_request("/data/health")
    
    if success_pg:
        st.markdown(f"""
        <div class="success-box">
            <h3>✅ Base de données connectée!</h3>
            <p><strong>PostgreSQL (schéma test):</strong> Connecté</p>
            <p><strong>Livres:</strong> {response_pg.get('tables', {}).get('livres', 0)}</p>
            <p><strong>Auteurs:</strong> {response_pg.get('tables', {}).get('auteurs', 0)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Métriques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🐘 PostgreSQL", "✅ OK")
            st.metric("📚 Livres", response_pg.get('tables', {}).get('livres', 0))
        with col2:
            st.metric("🔗 API", "En ligne")
            st.metric("✍️ Auteurs", response_pg.get('tables', {}).get('auteurs', 0))
        with col3:
            st.metric("⏰ Statut", "✅ OK")
    else:
        st.error("❌ Problème de connexion à la base de données")

def show_livres():
    """Page des livres"""
    st.header("📚 Livres")
    
    # Recherche
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Rechercher", placeholder="Titre, auteur, ISBN...")
    with col2:
        if st.button("Rechercher", type="primary"):
            if search:
                success, data = make_api_request("/data/search/", params={"q": search})
                
                if success and data.get("success") and data["data"]:
                    st.success(f"✅ {len(data['data'])} résultat(s)")
                    
                    for livre in data["data"]:
                        with st.expander(f"📖 {livre.get('titre', 'Titre non disponible')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                if livre.get('id_livre'):
                                    st.write(f"**ID:** {livre['id_livre']}")
                                if livre.get('titre'):
                                    st.write(f"**Titre:** {livre['titre']}")
                                if livre.get('isbn'):
                                    st.write(f"**ISBN:** {livre['isbn']}")
                                if livre.get('auteur_nom'):
                                    st.write(f"**Auteur:** {livre['auteur_nom']}")
                            with col2:
                                if livre.get('annee_publication'):
                                    st.metric("Année", livre['annee_publication'])
                else:
                    st.warning("Aucun résultat")
    
    # Liste des livres
    st.subheader("📋 Liste des livres")
    limit = st.selectbox("Nombre", [10, 20, 50], index=1)
    
    success, data = make_api_request("/data/livres/", params={"limit": limit})
    
    if success and data.get("success") and data["data"]:
        df = pd.DataFrame(data["data"])
        
        # Colonnes à afficher
        cols = ['id_livre', 'titre', 'annee_publication', 'nombre_pages']
        available_cols = [col for col in cols if col in df.columns]
        
        if available_cols:
            st.dataframe(df[available_cols], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📚 Aucun livre trouvé")

def show_auteurs():
    """Page des auteurs"""
    st.header("✍️ Auteurs")
    
    success, data = make_api_request("/data/auteurs/")
    
    if success and data.get("success") and data["data"]:
        df = pd.DataFrame(data["data"])
        
        # Affichage en grille
        if not df.empty:
            cols = st.columns(3)
            for idx, (_, auteur) in enumerate(df.iterrows()):
                with cols[idx % 3]:
                    if auteur.get('nom'):
                        st.subheader(auteur['nom'])
                    if auteur.get('id_auteur'):
                        st.write(f"ID: {auteur['id_auteur']}")
                    if auteur.get('nombre_livres'):
                        st.metric("📚 Livres", auteur['nombre_livres'])
                    
                    # Liens externes
                    if auteur.get('url_openlibrary'):
                        st.write("🔗 [OpenLibrary](url)")
                    if auteur.get('url_goodreads'):
                        st.write("📖 [Goodreads](url)")
        else:
            st.info("✍️ Aucun auteur trouvé")
    else:
        st.info("✍️ Aucun auteur trouvé")

def show_stats():
    """Page statistiques"""
    st.header("📊 Statistiques")
    
    # Vérifier auth
    if not st.session_state.get('authenticated', False):
        st.warning("🔑 Authentification requise")
        return
    
    headers = st.session_state.get('headers', {})
    
    # Utiliser l'endpoint de statistiques des vraies données
    success_stats, stats_data = make_api_request("/data/statistics/", headers)
    
    if success_stats and stats_data.get("success"):
        stats = stats_data["data"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📚 Livres", stats.get('total_livres', 0))
        with col2:
            st.metric("✍️ Auteurs", stats.get('total_auteurs', 0))
        with col3:
            st.metric("🏢 Éditeurs", stats.get('total_editeurs', 0))
        
        # Deuxième ligne de métriques
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🗣️ Langues", stats.get('total_langues', 0))
        with col2:
            st.metric("🏷️ Sujets", stats.get('total_sujets', 0))
        with col3:
            st.write("**Structure découverte !**")
            if stats.get('colonnes_disponibles'):
                st.write("📋 Colonnes : " + ", ".join(stats['colonnes_disponibles'][:3]) + "...")
        
        # Graphique
        chart_data = {
            'Catégorie': ['Livres', 'Auteurs', 'Éditeurs', 'Langues', 'Sujets'],
            'Total': [
                stats.get('total_livres', 0),
                stats.get('total_auteurs', 0),
                stats.get('total_editeurs', 0),
                stats.get('total_langues', 0),
                stats.get('total_sujets', 0)
            ]
        }
        
        fig = px.bar(
            chart_data, 
            x='Catégorie', 
            y='Total',
            title="📊 Vue d'ensemble de votre bibliothèque",
            color='Total'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Livres récents
        st.subheader("📚 Livres récents")
        success_top, data_top = make_api_request("/data/top-livres/", params={"limit": 5})
        
        if success_top and data_top.get("success") and data_top["data"]:
            for livre in data_top["data"]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📖 **{livre.get('titre', 'Titre non disponible')}**")
                    if livre.get('auteurs'):
                        st.write(f"_par {livre['auteurs']}_")
                    if livre.get('sous_titre'):
                        st.write(f"_{livre['sous_titre']}_")
                with col2:
                    if livre.get('annee_publication'):
                        st.metric("📅 Année", livre['annee_publication'])
                    if livre.get('nombre_pages'):
                        st.metric("📄 Pages", livre['nombre_pages'])
        else:
            st.info("📚 Aucun livre disponible")
    else:
        st.error("❌ Statistiques non disponibles (clé API requise)")

if __name__ == "__main__":
    main() 