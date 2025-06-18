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
                # Test spécifique pour les collections de livres
                mongo_status, mongo_data = make_api_request("/mongo-livres/")
                if mongo_status and mongo_data.get("status") == "✅ MongoDB connecté":
                    collections = mongo_data.get("collections", {})
                    st.write("📚 Livres:", collections.get("livres", {}).get("count", 0))
                    st.write("💬 Critiques:", collections.get("critiques_livres", {}).get("count", 0))
            else:
                st.warning("🍃 MongoDB KO")
    
    # Onglets principaux
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Accueil", "📚 Livres PostgreSQL", "🍃 Livres MongoDB", "✍️ Auteurs", "📊 Stats"])
    
    with tab1:
        show_home()
    
    with tab2:
        show_livres()
    
    with tab3:
        show_mongo_livres()
    
    with tab4:
        show_auteurs()
    
    with tab5:
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

def show_mongo_livres():
    """Page des livres MongoDB"""
    st.header("🍃 Livres MongoDB")
    
    # Test de connexion MongoDB
    mongo_status, mongo_data = make_api_request("/mongo-livres/")
    
    if not mongo_status:
        st.error("❌ MongoDB non accessible")
        st.info("Vérifiez que MongoDB est démarré et que votre API est connectée")
        return
    
    if mongo_data and mongo_data.get("status") == "✅ MongoDB connecté":
        # Afficher les infos de connexion
        collections = mongo_data.get("collections", {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📚 Livres MongoDB", collections.get("livres", {}).get("count", 0))
        with col2:
            st.metric("💬 Critiques", collections.get("critiques_livres", {}).get("count", 0))
        
        st.success("🍃 MongoDB connecté avec succès !")
        
        # Onglets pour livres et critiques
        tab_livres, tab_critiques, tab_recherche, tab_analytics, tab_sample = st.tabs(["📚 Livres", "💬 Critiques", "🔍 Recherche", "🎯 Analytics", "🔬 Échantillon"])
        
        with tab_livres:
            show_mongo_livres_list()
        
        with tab_critiques:
            show_mongo_critiques()
        
        with tab_recherche:
            show_mongo_search()
        
        with tab_analytics:
            show_mongo_analytics()
        
        with tab_sample:
            show_mongo_sample()
    else:
        st.error("❌ Erreur de connexion MongoDB")
        if mongo_data:
            st.json(mongo_data)

def show_mongo_livres_list():
    """Afficher la liste des livres MongoDB"""
    st.subheader("📚 Liste des livres MongoDB")
    
    # Paramètres
    col1, col2, col3 = st.columns(3)
    with col1:
        limit = st.selectbox("Nombre de livres", [10, 20, 50], index=1, key="mongo_limit")
    with col2:
        skip = st.number_input("Ignorer", min_value=0, value=0, key="mongo_skip")
    with col3:
        if st.button("🔄 Actualiser", key="mongo_refresh"):
            st.rerun()
    
    # Filtres
    with st.expander("🔍 Filtres avancés"):
        col1, col2 = st.columns(2)
        with col1:
            titre_filter = st.text_input("Filtrer par titre", key="mongo_titre_filter")
        with col2:
            auteur_filter = st.text_input("Filtrer par auteur", key="mongo_auteur_filter")
    
    # Paramètres pour l'API
    params = {"limit": limit, "skip": skip}
    if titre_filter:
        params["titre"] = titre_filter
    if auteur_filter:
        params["auteur"] = auteur_filter
    
    # Récupérer les livres
    success, data = make_api_request("/mongo-livres/livres", params=params)
    
    if success and data.get("success") and data["data"]:
        livres = data["data"]
        pagination = data.get("pagination", {})
        
        # Afficher pagination info
        st.info(f"📊 Affichage de {pagination.get('returned', 0)} livres sur {pagination.get('total', 0)} au total")
        
        # Afficher les livres
        for i, livre in enumerate(livres):
            with st.expander(f"📖 {livre.get('titre', livre.get('title', 'Titre non disponible'))} - {livre.get('auteur', livre.get('author', 'Auteur inconnu'))}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Informations du livre:**")
                    for key, value in livre.items():
                        if key != '_id' and value and key not in ['titre', 'title', 'auteur', 'author']:
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                
                with col2:
                    st.write("**Actions:**")
                    livre_id = livre.get('_id', '')
                    if livre_id and st.button(f"📝 Voir détails", key=f"details_{i}_{livre_id}"):
                        show_mongo_livre_detail(livre_id)
        
        # Navigation
        if pagination.get("total", 0) > limit:
            col1, col2, col3 = st.columns(3)
            with col1:
                if skip > 0:
                    if st.button("⬅️ Précédent"):
                        st.session_state.mongo_skip = max(0, skip - limit)
                        st.rerun()
            with col3:
                if skip + limit < pagination.get("total", 0):
                    if st.button("➡️ Suivant"):
                        st.session_state.mongo_skip = skip + limit
                        st.rerun()
    else:
        st.warning("📚 Aucun livre trouvé dans MongoDB")
        if not success:
            st.error(f"Erreur: {data}")

def show_mongo_critiques():
    """Afficher les critiques MongoDB"""
    st.subheader("💬 Critiques de livres")
    
    limit = st.selectbox("Nombre de critiques", [10, 20, 50], index=1, key="critiques_limit")
    
    # Filtres pour les notes
    with st.expander("⭐ Filtrer par note"):
        col1, col2 = st.columns(2)
        with col1:
            note_min = st.slider("Note minimale", 0.0, 5.0, 0.0, 0.5, key="note_min")
        with col2:
            note_max = st.slider("Note maximale", 0.0, 5.0, 5.0, 0.5, key="note_max")
    
    params = {"limit": limit}
    if note_min > 0:
        params["note_min"] = note_min
    if note_max < 5:
        params["note_max"] = note_max
    
    success, data = make_api_request("/mongo-livres/critiques", params=params)
    
    if success and data.get("success") and data["data"]:
        critiques = data["data"]
        
        for i, critique in enumerate(critiques):
            with st.expander(f"💭 Critique #{i+1} - Note: {critique.get('note', 'N/A')}/5", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    for key, value in critique.items():
                        if key != '_id' and value:
                            if key == 'note':
                                st.metric("⭐ Note", f"{value}/5")
                            else:
                                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                
                with col2:
                    critique_id = critique.get('_id', '')
                    if critique_id:
                        st.write(f"**ID:** `{critique_id}`")
    else:
        st.warning("💬 Aucune critique trouvée")

def show_mongo_search():
    """Recherche dans MongoDB"""
    st.subheader("🔍 Recherche dans MongoDB")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Rechercher dans tous les champs", placeholder="Titre, auteur, description...")
    with col2:
        search_limit = st.selectbox("Résultats max", [10, 20, 50], index=1, key="search_limit")
    
    if search_query and len(search_query) >= 2:
        # Recherche dans les livres
        success, data = make_api_request("/mongo-livres/livres/search", params={"q": search_query, "limit": search_limit})
        
        if success and data.get("success") and data["data"]:
            st.success(f"✅ {len(data['data'])} livre(s) trouvé(s)")
            
            for i, livre in enumerate(data["data"]):
                with st.expander(f"📖 {livre.get('titre', livre.get('title', 'Sans titre'))}", expanded=False):
                    # Afficher tous les champs du livre
                    for key, value in livre.items():
                        if key != '_id' and value:
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        else:
            st.warning("📚 Aucun livre trouvé pour cette recherche")
    elif search_query and len(search_query) < 2:
        st.info("🔍 Tapez au moins 2 caractères pour la recherche")

def show_mongo_analytics():
    """Analytics avancés MongoDB"""
    st.subheader("🎯 Analytics MongoDB avancés")
    
    # Récupérer les analytics
    success, data = make_api_request("/mongo-extras/analytics")
    
    if success and data.get("success"):
        analytics = data.get("analytics", {})
        
        # Section genres
        if "top_genres" in analytics:
            st.write("### 📑 Top Genres")
            genres_data = analytics["top_genres"]
            if genres_data:
                col1, col2 = st.columns([2, 1])
                with col1:
                    # Graphique des genres
                    genres_df = pd.DataFrame(genres_data)
                    if not genres_df.empty:
                        fig = px.bar(
                            genres_df, 
                            x='_id', 
                            y='count',
                            title="Top 10 des genres",
                            labels={'_id': 'Genre', 'count': 'Nombre de livres'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.write("**Top 5 genres:**")
                    for i, genre in enumerate(genres_data[:5]):
                        st.write(f"{i+1}. **{genre['_id']}** ({genre['count']} livres)")
        
        # Section langues
        if "repartition_langues" in analytics:
            st.write("### 🌍 Répartition par langue")
            langues_data = analytics["repartition_langues"]
            if langues_data:
                col1, col2 = st.columns([2, 1])
                with col1:
                    langues_df = pd.DataFrame(langues_data)
                    if not langues_df.empty:
                        fig = px.pie(
                            langues_df, 
                            values='count', 
                            names='_id',
                            title="Répartition des livres par langue"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                with col2:
                    for langue in langues_data[:5]:
                        st.metric(f"📚 {langue['_id']}", langue['count'])
        
        # Section critiques Babelio
        if "stats_critiques_babelio" in analytics:
            st.write("### 💬 Statistiques Critiques Babelio")
            stats = analytics["stats_critiques_babelio"]
            if stats:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if "min_note" in stats:
                        st.metric("🔻 Note min", f"{stats['min_note']:.1f}/5")
                with col2:
                    if "max_note" in stats:
                        st.metric("🔺 Note max", f"{stats['max_note']:.1f}/5")
                with col3:
                    if "avg_note" in stats:
                        st.metric("📊 Moyenne", f"{stats['avg_note']:.2f}/5")
                with col4:
                    if "total_votes" in stats:
                        st.metric("🗳️ Total votes", f"{stats['total_votes']:,}")
        
        # Section notes des livres
        if "repartition_notes_livres" in analytics:
            st.write("### ⭐ Répartition des notes des livres")
            notes_data = analytics["repartition_notes_livres"]
            if notes_data:
                notes_df = pd.DataFrame(notes_data)
                if not notes_df.empty:
                    fig = px.bar(
                        notes_df, 
                        x='_id', 
                        y='count',
                        title="Distribution des notes",
                        labels={'_id': 'Note', 'count': 'Nombre de livres'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Section livres récents
        if "livres_recents" in analytics:
            st.write("### 📅 Livres récemment ajoutés")
            livres_recents = analytics["livres_recents"]
            if livres_recents:
                for i, livre in enumerate(livres_recents[:3]):
                    with st.expander(f"📖 {livre.get('titre', 'Sans titre')} - {livre.get('auteurs', ['Auteur inconnu'])[0] if livre.get('auteurs') else 'Auteur inconnu'}"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            if livre.get('resume'):
                                st.write("**Résumé:**", livre['resume'][:200] + "..." if len(livre.get('resume', '')) > 200 else livre['resume'])
                            if livre.get('tous_les_genres'):
                                st.write("**Genres:**", ", ".join(livre['tous_les_genres']))
                        with col2:
                            if livre.get('note'):
                                st.metric("⭐ Note", f"{livre['note']}/5")
                            if livre.get('langue'):
                                st.write(f"🌍 **Langue:** {livre['langue']}")
    else:
        st.error("❌ Impossible de charger les analytics")
    
    # Section recherche par genre/auteur
    st.write("---")
    st.subheader("🔍 Explorer par catégorie")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📑 Parcourir par genre**")
        # Récupérer les genres
        success_genres, genres_data = make_api_request("/mongo-extras/genres")
        if success_genres and genres_data.get("success"):
            genres_list = [g["_id"] for g in genres_data["data"][:20]]  # Top 20
            selected_genre = st.selectbox("Choisir un genre", [""] + genres_list, key="analytics_genre")
            
            if selected_genre:
                # Afficher les livres de ce genre
                success_livres, livres_data = make_api_request(f"/mongo-extras/livres/genre/{selected_genre}", params={"limit": 5})
                if success_livres and livres_data.get("success"):
                    st.write(f"**{livres_data['total_genre']} livres en {selected_genre}**")
                    for livre in livres_data["data"]:
                        st.write(f"📖 {livre.get('titre', 'Sans titre')}")
    
    with col2:
        st.write("**✍️ Parcourir par auteur**")
        # Récupérer les auteurs
        success_auteurs, auteurs_data = make_api_request("/mongo-extras/auteurs")
        if success_auteurs and auteurs_data.get("success"):
            auteurs_list = [a["_id"] for a in auteurs_data["data"][:20]]  # Top 20
            selected_auteur = st.selectbox("Choisir un auteur", [""] + auteurs_list, key="analytics_auteur")
            
            if selected_auteur:
                # Afficher les livres de cet auteur
                success_livres, livres_data = make_api_request(f"/mongo-extras/livres/auteur/{selected_auteur}", params={"limit": 5})
                if success_livres and livres_data.get("success"):
                    st.write(f"**{livres_data['total_auteur']} livres de {selected_auteur}**")
                    for livre in livres_data["data"]:
                        st.write(f"📖 {livre.get('titre', 'Sans titre')}")

def show_mongo_sample():
    """Afficher un échantillon des données pour comprendre la structure"""
    st.subheader("🔬 Échantillon de données MongoDB")
    
    success, data = make_api_request("/mongo-livres/sample")
    
    if success and data.get("success"):
        echantillons = data.get("echantillons", {})
        
        # Livres
        if "livres" in echantillons:
            livres_data = echantillons["livres"]
            st.write("### 📚 Structure des livres")
            st.write("**Champs disponibles:**", ", ".join(livres_data.get("champs_disponibles", [])))
            
            if livres_data.get("sample"):
                st.write("**Exemples:**")
                for i, livre in enumerate(livres_data["sample"][:2]):  # Limiter à 2 exemples
                    with st.expander(f"Exemple {i+1}: {livre.get('titre', livre.get('title', 'Sans titre'))}"):
                        st.json(livre)
        
        # Critiques
        if "critiques" in echantillons:
            critiques_data = echantillons["critiques"]
            st.write("### 💬 Structure des critiques")
            st.write("**Champs disponibles:**", ", ".join(critiques_data.get("champs_disponibles", [])))
            
            if critiques_data.get("sample"):
                st.write("**Exemples:**")
                for i, critique in enumerate(critiques_data["sample"][:2]):
                    with st.expander(f"Critique exemple {i+1}"):
                        st.json(critique)
    else:
        st.error("❌ Impossible de récupérer l'échantillon de données")

def show_mongo_livre_detail(livre_id):
    """Afficher les détails d'un livre MongoDB"""
    success, data = make_api_request(f"/mongo-livres/livres/{livre_id}")
    
    if success and data.get("success"):
        livre = data["livre"]
        critiques = data.get("critiques", [])
        
        st.write("### 📖 Détails du livre")
        st.json(livre)
        
        if critiques:
            st.write(f"### 💬 Critiques associées ({len(critiques)})")
            for critique in critiques:
                st.json(critique)
        else:
            st.info("💬 Aucune critique trouvée pour ce livre")
    else:
        st.error("❌ Impossible de charger les détails du livre")

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