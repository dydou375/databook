"""
Script pour corriger automatiquement tous les appels check_mongodb
"""
import re

def fix_file(filename):
    print(f"🔧 Correction de {filename}...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer check_mongodb() par await check_mongodb()
    # Mais pas la définition de la fonction
    pattern = r'(\s+)check_mongodb\(\)'
    replacement = r'\1await check_mongodb()'
    
    new_content = re.sub(pattern, replacement, content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ {filename} corrigé")

if __name__ == "__main__":
    files_to_fix = [
        "routes/routes_mongo_extras.py",
        "routes/routes_real_mongo.py"
    ]
    
    for file in files_to_fix:
        try:
            fix_file(file)
        except Exception as e:
            print(f"❌ Erreur avec {file}: {e}") 