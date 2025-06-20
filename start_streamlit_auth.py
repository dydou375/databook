"""
🚀 Script de démarrage pour l'interface Streamlit avec authentification JWT
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Vérifier les dépendances requises"""
    required_packages = [
        "streamlit",
        "requests", 
        "pandas",
        "plotly"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Packages manquants:", ", ".join(missing_packages))
        print("📦 Installation en cours...")
        
        for package in missing_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("✅ Installation terminée!")

def start_streamlit():
    """Démarrer l'interface Streamlit"""
    
    # Vérifier que le fichier streamlit_auth.py existe
    streamlit_file = Path(__file__).parent / "streamlit_auth.py"
    
    if not streamlit_file.exists():
        print("❌ Fichier streamlit_auth.py introuvable!")
        return
    
    print("🔐 Démarrage de l'interface Streamlit avec authentification JWT...")
    print("📍 URL: http://localhost:8501")
    print("🔗 API: http://localhost:8000")
    print()
    print("📚 Interface DataBook avec:")
    print("   • 🔐 Authentification JWT")
    print("   • 📝 Inscription/Connexion")
    print("   • 📚 41000 livres MongoDB")
    print("   • 🎯 Analytics avancés")
    print("   • 🗄️ Données PostgreSQL")
    print()
    print("⚠️  Assurez-vous que l'API est démarrée (python start.py)")
    print("-" * 60)
    
    # Démarrer Streamlit
    try:
        subprocess.run([
            "streamlit", "run", 
            str(streamlit_file),
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Interface Streamlit arrêtée")
    except FileNotFoundError:
        print("❌ Streamlit n'est pas installé!")
        print("📦 Installation: pip install streamlit")

if __name__ == "__main__":
    print("🔐 Interface Streamlit DataBook - Authentification JWT")
    print("=" * 60)
    
    # Vérifier les dépendances
    check_requirements()
    
    # Démarrer l'interface
    start_streamlit() 