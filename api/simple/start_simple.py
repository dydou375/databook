#!/usr/bin/env python3
"""
Script de démarrage simple pour l'API DataBook
"""

import uvicorn
import sys
from config_simple import HOST, PORT, DEBUG, API_KEY

def main():
    """Démarrer l'API simple"""
    print("""
    ╔════════════════════════════════════════════╗
    ║            🚀 DataBook API Simple          ║
    ║                                            ║
    ║  API simple et sécurisée pour vos données  ║
    ║                                            ║
    ║  📊 PostgreSQL + 🍃 MongoDB                ║
    ║  🔐 Sécurité par clé API                   ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    """)
    
    print(f"🔑 Clé API: {API_KEY}")
    print(f"📖 Documentation: http://localhost:{PORT}/docs")
    print(f"🏠 Accueil: http://localhost:{PORT}/")
    print(f"❤️ Santé: http://localhost:{PORT}/health")
    print("\n" + "="*50)
    print("Appuyez sur Ctrl+C pour arrêter le serveur")
    print("="*50 + "\n")
    
    try:
        uvicorn.run(
            "main_simple:app",
            host=HOST,
            port=PORT,
            reload=DEBUG,
            log_level="info" if not DEBUG else "debug"
        )
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur demandé")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 