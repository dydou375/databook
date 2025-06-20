import json
import os
from pathlib import Path

def compter_livres_total(dossier_path):
    """Compte le nombre total de livres dans tous les fichiers JSON du dossier"""
    
    dossier = Path(dossier_path)
    
    if not dossier.exists():
        print(f"❌ Le dossier {dossier_path} n'existe pas !")
        return
    
    # Initialisation des compteurs
    total_livres = 0
    details_fichiers = []
    
    print(f"📂 Analyse du dossier: {dossier_path}")
    print("=" * 60)
    
    # Parcourir tous les fichiers JSON
    fichiers_json = list(dossier.glob("*.json"))
    
    if not fichiers_json:
        print("❌ Aucun fichier JSON trouvé dans le dossier !")
        return
    
    for fichier_json in sorted(fichiers_json):
        try:
            with open(fichier_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Compter les livres dans ce fichier
                if isinstance(data, list):
                    nb_livres = len(data)
                else:
                    nb_livres = 1 if data else 0
                
                total_livres += nb_livres
                details_fichiers.append({
                    'fichier': fichier_json.name,
                    'nb_livres': nb_livres
                })
                
                print(f"📚 {fichier_json.name:<30} : {nb_livres:>6} livres")
                
        except json.JSONDecodeError:
            print(f"⚠️ Erreur de lecture JSON pour {fichier_json.name}")
        except Exception as e:
            print(f"❌ Erreur pour {fichier_json.name}: {e}")
    
    # Affichage des résultats
    print("=" * 60)
    print(f"📊 RÉSUMÉ:")
    print(f"   • Nombre de fichiers JSON : {len(fichiers_json)}")
    print(f"   • Nombre total de livres  : {total_livres:,}")
    print("=" * 60)
    
    # Top 5 des catégories avec le plus de livres
    if details_fichiers:
        print("\n🏆 TOP 5 des catégories avec le plus de livres:")
        top_categories = sorted(details_fichiers, key=lambda x: x['nb_livres'], reverse=True)[:5]
        for i, cat in enumerate(top_categories, 1):
            print(f"   {i}. {cat['fichier']:<25} : {cat['nb_livres']:>6} livres")
    
    return total_livres, len(fichiers_json)

def main():
    """Fonction principale"""
    # Chemin vers le dossier des livres
    dossier_livres = r"C:\Users\dd758\Formation_IA_Greta\livres_json_ameliore"
    
    print("📖 COMPTEUR DE LIVRES")
    print("=" * 40)
    
    resultat = compter_livres_total(dossier_livres)
    
    if resultat:
        total_livres, nb_fichiers = resultat
        print(f"\n🎉 Vous avez un total de {total_livres:,} livres répartis dans {nb_fichiers} catégories !")
    
    print("\n✨ Analyse terminée !")

if __name__ == "__main__":
    main() 