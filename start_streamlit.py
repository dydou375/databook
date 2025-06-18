"""
Script de démarrage pour l'interface Streamlit DataBook
"""

import subprocess
import sys
import os

def install_requirements():
    """Installer les dépendances si nécessaire"""
    try:
        import streamlit
        import requests
        import pandas
        import plotly
        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("📦 Installation des dépendances...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-r", "requirements_streamlit.txt"
            ])
            print("✅ Dépendances installées avec succès!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erreur lors de l'installation des dépendances")
            return False

def check_api_running():
    """Vérifier si l'API est en marche"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def main():
    print("""
    🚀 Démarrage de l'interface Streamlit DataBook
    ===============================================
    """)
    
    # Vérifier et installer les dépendances
    if not install_requirements():
        print("❌ Impossible de continuer sans les dépendances")
        return
    
    # Vérifier si l'API est accessible
    if not check_api_running():
        print("""
        ⚠️  L'API n'est pas accessible sur http://localhost:8000
        
        🔧 Pour démarrer l'API, ouvrez un autre terminal et tapez:
           cd api
           python start.py
        
        Puis relancez ce script.
        """)
        
        choice = input("Voulez-vous continuer quand même ? (o/n): ")
        if choice.lower() != 'o':
            return
    else:
        print("✅ API accessible sur http://localhost:8000")
    
    # Démarrer Streamlit
    print("\n🌟 Démarrage de l'interface Streamlit...")
    print("📱 L'interface s'ouvrira automatiquement dans votre navigateur")
    print("🔗 URL: http://localhost:8501")
    print("\n" + "="*50)
    
    try:
        # Changer vers le bon répertoire
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Lancer Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Interface fermée par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")

if __name__ == "__main__":
    main() 