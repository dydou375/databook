#!/usr/bin/env python3
"""
Extraction massive complète des livres OpenLibrary
=================================================

Ce script extrait tous les livres disponibles depuis les dumps OpenLibrary
avec optimisation mémoire et gestion des gros volumes.
"""

import gzip
import csv
import json
import os
import time
import re
from typing import Dict, List, Optional, Generator
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class StatistiquesExtraction:
    """Classe pour stocker les statistiques d'extraction"""
    total_lignes_lues: int = 0
    editions_trouvees: int = 0
    editions_extraites: int = 0
    erreurs_parsing: int = 0
    erreurs_ecriture: int = 0
    temps_debut: float = 0
    temps_fin: float = 0
    fichier_source: str = ""
    fichier_sortie: str = ""

class ExtracteurMassif:
    """Extracteur massif optimisé pour les gros fichiers OpenLibrary"""
    
    def __init__(self):
        self.stats = StatistiquesExtraction()
        self.csv_writer = None
        self.fichier_sortie = None
        self.colonnes = [
            'id_livre', 'titre', 'sous_titre', 'auteurs', 'editeurs',
            'date_publication', 'isbn_10', 'isbn_13', 'langues', 'sujets',
            'description', 'nombre_pages', 'format_physique', 'note_moyenne'
        ]
        
    def nettoyer_texte(self, texte: str) -> str:
        """Nettoie le texte des caractères problématiques"""
        if not texte:
            return ""
        
        # Supprimer les caractères de contrôle
        texte = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', str(texte))
        
        # Remplacer les retours à la ligne par des espaces
        texte = re.sub(r'\s+', ' ', texte)
        
        # Limiter la longueur
        if len(texte) > 1000:
            texte = texte[:997] + "..."
        
        return texte.strip()
    
    def extraire_auteurs(self, auteurs_data: List) -> str:
        """Extrait les IDs des auteurs"""
        if not auteurs_data or not isinstance(auteurs_data, list):
            return ""
        
        auteurs_ids = []
        for auteur in auteurs_data[:10]:  # Limiter à 10 auteurs
            if isinstance(auteur, dict) and 'key' in auteur:
                auteurs_ids.append(auteur['key'])
        
        return " | ".join(auteurs_ids)
    
    def extraire_editeurs(self, data: Dict) -> str:
        """Extrait les noms des éditeurs"""
        editeurs = []
        
        # Essayer différents champs
        for champ in ['publishers', 'publisher']:
            if champ in data and isinstance(data[champ], list):
                for editeur in data[champ][:5]:  # Limiter à 5 éditeurs
                    if isinstance(editeur, str):
                        editeur_nettoye = self.nettoyer_texte(editeur)
                        if editeur_nettoye:
                            editeurs.append(editeur_nettoye)
        
        return " | ".join(editeurs)
    
    def extraire_date_publication(self, data: Dict) -> str:
        """Extrait la date de publication"""
        for champ in ['publish_date', 'publication_date', 'date_published']:
            if champ in data:
                date = data[champ]
                if isinstance(date, str):
                    return self.nettoyer_texte(date)
                elif isinstance(date, list) and date:
                    return self.nettoyer_texte(str(date[0]))
        
        return ""
    
    def extraire_isbn(self, data: Dict, type_isbn: str) -> str:
        """Extrait les ISBN (10 ou 13)"""
        champ = f'isbn_{type_isbn}'
        if champ in data and isinstance(data[champ], list) and data[champ]:
            isbn = str(data[champ][0]).strip()
            # Valider le format de base
            if type_isbn == '10' and len(isbn) == 10:
                return isbn
            elif type_isbn == '13' and len(isbn) == 13:
                return isbn
        
        return ""
    
    def extraire_langues(self, data: Dict) -> str:
        """Extrait les codes de langues"""
        if 'languages' not in data or not isinstance(data['languages'], list):
            return ""
        
        langues = []
        for langue in data['languages'][:5]:  # Limiter à 5 langues
            if isinstance(langue, dict) and 'key' in langue:
                # Extraire le code depuis "/languages/eng"
                code = langue['key'].split('/')[-1]
                if code and len(code) <= 3:
                    langues.append(code)
        
        return " | ".join(langues)
    
    def extraire_sujets(self, data: Dict) -> str:
        """Extrait les sujets/mots-clés"""
        sujets = []
        
        # Essayer différents champs
        for champ in ['subjects', 'subject_places', 'subject_people', 'subject_times']:
            if champ in data and isinstance(data[champ], list):
                for sujet in data[champ][:20]:  # Limiter à 20 sujets
                    if isinstance(sujet, str):
                        sujet_nettoye = self.nettoyer_texte(sujet)
                        if sujet_nettoye and len(sujet_nettoye) > 2:
                            sujets.append(sujet_nettoye)
        
        return " | ".join(sujets[:15])  # Limiter finalement à 15
    
    def extraire_description(self, data: Dict) -> str:
        """Extrait la description"""
        for champ in ['description', 'notes', 'note']:
            if champ in data:
                desc = data[champ]
                if isinstance(desc, str):
                    return self.nettoyer_texte(desc)
                elif isinstance(desc, dict) and 'value' in desc:
                    return self.nettoyer_texte(desc['value'])
                elif isinstance(desc, list) and desc:
                    return self.nettoyer_texte(str(desc[0]))
        
        return ""
    
    def extraire_nombre_pages(self, data: Dict) -> str:
        """Extrait le nombre de pages"""
        for champ in ['number_of_pages', 'pagination']:
            if champ in data:
                pages = data[champ]
                if isinstance(pages, (int, float)):
                    return str(int(pages))
                elif isinstance(pages, str):
                    # Extraire les chiffres
                    match = re.search(r'\d+', pages)
                    if match:
                        return match.group()
        
        return ""
    
    def extraire_format_physique(self, data: Dict) -> str:
        """Extrait le format physique"""
        for champ in ['physical_format', 'format']:
            if champ in data and isinstance(data[champ], str):
                return self.nettoyer_texte(data[champ])
        
        return ""
    
    def traiter_edition(self, ol_id: str, donnees: Dict) -> Optional[Dict]:
        """Traite une édition et retourne les données formatées"""
        try:
            # Vérifier que nous avons au minimum un titre
            if 'title' not in donnees or not donnees['title']:
                return None
            
            # Extraire toutes les données
            livre_data = {
                'id_livre': ol_id,
                'titre': self.nettoyer_texte(donnees.get('title', '')),
                'sous_titre': self.nettoyer_texte(donnees.get('subtitle', '')),
                'auteurs': self.extraire_auteurs(donnees.get('authors', [])),
                'editeurs': self.extraire_editeurs(donnees),
                'date_publication': self.extraire_date_publication(donnees),
                'isbn_10': self.extraire_isbn(donnees, '10'),
                'isbn_13': self.extraire_isbn(donnees, '13'),
                'langues': self.extraire_langues(donnees),
                'sujets': self.extraire_sujets(donnees),
                'description': self.extraire_description(donnees),
                'nombre_pages': self.extraire_nombre_pages(donnees),
                'format_physique': self.extraire_format_physique(donnees),
                'note_moyenne': ""  # À implémenter si disponible
            }
            
            return livre_data
            
        except Exception as e:
            print(f"⚠️ Erreur traitement édition {ol_id}: {e}")
            return None
    
    def lire_fichier_openlibrary(self, fichier_path: str) -> Generator[tuple, None, None]:
        """Générateur pour lire le fichier ligne par ligne"""
        print(f"📖 Lecture du fichier: {os.path.basename(fichier_path)}")
        
        # Déterminer le type de fichier
        est_compresse = fichier_path.endswith('.gz')
        open_func = gzip.open if est_compresse else open
        mode = 'rt' if est_compresse else 'r'
        
        try:
            with open_func(fichier_path, mode, encoding='utf-8', errors='replace') as f:
                for numero_ligne, ligne in enumerate(f, 1):
                    self.stats.total_lignes_lues = numero_ligne
                    
                    # Afficher le progrès
                    if numero_ligne % 100000 == 0:
                        temps_ecoule = time.time() - self.stats.temps_debut
                        vitesse = numero_ligne / temps_ecoule if temps_ecoule > 0 else 0
                        print(f"   📊 Ligne {numero_ligne:,} - {vitesse:.0f} lignes/sec - {self.stats.editions_extraites:,} livres extraits")
                    
                    try:
                        # Parser la ligne OpenLibrary (format: type TAB id TAB revision TAB timestamp TAB json)
                        parties = ligne.strip().split('\t')
                        
                        if len(parties) >= 5 and parties[0] == '/type/edition':
                            self.stats.editions_trouvees += 1
                            
                            ol_id = parties[1]  # /books/OL123M
                            donnees_json = json.loads(parties[4])
                            
                            yield ol_id, donnees_json
                    
                    except (json.JSONDecodeError, IndexError, Exception) as e:
                        self.stats.erreurs_parsing += 1
                        continue
        
        except Exception as e:
            print(f"❌ Erreur lecture fichier: {e}")
    
    def creer_fichier_sortie(self, nom_fichier: str):
        """Crée le fichier CSV de sortie"""
        self.fichier_sortie = open(nom_fichier, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.DictWriter(self.fichier_sortie, fieldnames=self.colonnes)
        self.csv_writer.writeheader()
        print(f"📝 Fichier de sortie créé: {nom_fichier}")
    
    def fermer_fichier_sortie(self):
        """Ferme le fichier de sortie"""
        if self.fichier_sortie:
            self.fichier_sortie.close()
            print(f"💾 Fichier fermé: {self.stats.fichier_sortie}")
    
    def extraire_livres(self, fichier_source: str, nom_sortie: str = None, limite_livres: int = None):
        """Extrait les livres du fichier source"""
        print(f"🚀 EXTRACTION MASSIVE DÉMARRÉE")
        print("=" * 60)
        
        # Préparer les statistiques
        self.stats.temps_debut = time.time()
        self.stats.fichier_source = fichier_source
        
        # Nom du fichier de sortie
        if not nom_sortie:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            if limite_livres:
                nom_sortie = f"livres_openlibrary_{limite_livres}_{timestamp}.csv"
            else:
                nom_sortie = f"livres_openlibrary_complet_{timestamp}.csv"
        
        self.stats.fichier_sortie = nom_sortie
        
        try:
            # Créer le fichier de sortie
            self.creer_fichier_sortie(nom_sortie)
            
            # Traiter le fichier
            for ol_id, donnees in self.lire_fichier_openlibrary(fichier_source):
                # Traiter l'édition
                livre_data = self.traiter_edition(ol_id, donnees)
                
                if livre_data:
                    try:
                        self.csv_writer.writerow(livre_data)
                        self.stats.editions_extraites += 1
                        
                        # Vérifier la limite
                        if limite_livres and self.stats.editions_extraites >= limite_livres:
                            print(f"\n🎯 Limite atteinte: {limite_livres:,} livres extraits")
                            break
                    
                    except Exception as e:
                        self.stats.erreurs_ecriture += 1
                        print(f"⚠️ Erreur écriture: {e}")
            
            # Fermer le fichier
            self.fermer_fichier_sortie()
            
            # Calculer les statistiques finales
            self.stats.temps_fin = time.time()
            duree_totale = self.stats.temps_fin - self.stats.temps_debut
            
            # Afficher le résumé
            print(f"\n🎉 EXTRACTION TERMINÉE!")
            print(f"⏱️ Durée totale: {duree_totale/60:.1f} minutes")
            print(f"📊 Lignes lues: {self.stats.total_lignes_lues:,}")
            print(f"📚 Éditions trouvées: {self.stats.editions_trouvees:,}")
            print(f"✅ Livres extraits: {self.stats.editions_extraites:,}")
            print(f"❌ Erreurs parsing: {self.stats.erreurs_parsing:,}")
            print(f"❌ Erreurs écriture: {self.stats.erreurs_ecriture:,}")
            
            if self.stats.editions_trouvees > 0:
                taux_extraction = (self.stats.editions_extraites / self.stats.editions_trouvees) * 100
                print(f"📈 Taux d'extraction: {taux_extraction:.1f}%")
            
            vitesse_moyenne = self.stats.total_lignes_lues / duree_totale if duree_totale > 0 else 0
            print(f"🚀 Vitesse moyenne: {vitesse_moyenne:.0f} lignes/seconde")
            
            taille_sortie = os.path.getsize(nom_sortie) / (1024*1024)
            print(f"💾 Fichier généré: {nom_sortie} ({taille_sortie:.1f} MB)")
            
        except KeyboardInterrupt:
            print(f"\n⏹️ Extraction interrompue par l'utilisateur")
            self.fermer_fichier_sortie()
        except Exception as e:
            print(f"\n❌ Erreur durant l'extraction: {e}")
            self.fermer_fichier_sortie()

def main():
    """Fonction principale"""
    print("🚀 EXTRACTEUR MASSIF OPENLIBRARY")
    print("=" * 60)
    
    # Détecter les fichiers disponibles
    base_paths = [
        r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary",
        r"C:\Users\dd758\Formation_IA_Greta\Projet_possible certif\Livre_analyse\data_book\databook\data\fichier_openlibrary\non_extrait",
        "."  # Répertoire courant
    ]
    
    fichiers_disponibles = []
    
    for base_path in base_paths:
        if os.path.exists(base_path):
            for filename in os.listdir(base_path):
                filepath = os.path.join(base_path, filename)
                if filename.endswith('.gz') or filename.endswith('.txt'):
                    if os.path.getsize(filepath) > 100 * 1024 * 1024:  # > 100MB
                        fichiers_disponibles.append(filepath)
    
    if not fichiers_disponibles:
        print("❌ Aucun fichier OpenLibrary volumineux trouvé")
        return
    
    print("📁 Fichiers disponibles:")
    for i, fichier in enumerate(fichiers_disponibles, 1):
        taille = os.path.getsize(fichier) / (1024**3)
        print(f"   {i}. {os.path.basename(fichier)} ({taille:.1f} GB)")
    
    # Sélection du fichier
    try:
        choix = int(input(f"\nChoisissez un fichier (1-{len(fichiers_disponibles)}): ")) - 1
        fichier_choisi = fichiers_disponibles[choix]
    except (ValueError, IndexError):
        print("❌ Choix invalide")
        return
    
    # Options d'extraction
    print(f"\n📊 OPTIONS D'EXTRACTION:")
    print(f"   1. Extraction limitée (1,000,000 livres)")
    print(f"   2. Extraction importante (5,000,000 livres)")
    print(f"   3. Extraction complète (tous les livres)")
    print(f"   4. Extraction personnalisée (nombre au choix)")
    
    choix_extraction = input("Choisissez une option (1-4): ").strip()
    
    limite_livres = None
    if choix_extraction == '1':
        limite_livres = 1000000
    elif choix_extraction == '2':
        limite_livres = 5000000
    elif choix_extraction == '3':
        limite_livres = None  # Pas de limite
    elif choix_extraction == '4':
        try:
            limite_livres = int(input("Nombre de livres à extraire: "))
        except ValueError:
            print("❌ Nombre invalide, extraction sans limite")
            limite_livres = None
    
    # Nom du fichier de sortie
    nom_sortie = input("Nom du fichier de sortie [auto]: ").strip()
    if not nom_sortie:
        nom_sortie = None
    
    # Confirmation
    print(f"\n📋 RÉCAPITULATIF:")
    print(f"   📁 Fichier source: {os.path.basename(fichier_choisi)}")
    print(f"   🎯 Limite: {limite_livres:,} livres" if limite_livres else "   🎯 Limite: Aucune (extraction complète)")
    print(f"   📝 Fichier sortie: {nom_sortie if nom_sortie else 'Automatique'}")
    
    confirmation = input("\n🚀 Démarrer l'extraction ? (o/N): ").strip().lower()
    if confirmation not in ['o', 'oui', 'y', 'yes']:
        print("❌ Extraction annulée")
        return
    
    # Lancer l'extraction
    extracteur = ExtracteurMassif()
    extracteur.extraire_livres(fichier_choisi, nom_sortie, limite_livres)

if __name__ == "__main__":
    main() 