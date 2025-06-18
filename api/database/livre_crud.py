"""
CRUD Operations pour la base de données Livres
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict

class LivreCRUD:
    def get_livres(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupérer tous les livres"""
        query = text("""
            SELECT 
                id_livre, titre, annee_publication, isbn, description,
                nombre_pages, url_couverture, note_moyenne, nombre_avis,
                statut_acquisition, date_ajout, date_modification
            FROM test.livre 
            ORDER BY date_ajout DESC
            LIMIT :limit OFFSET :skip
        """)
        
        result = db.execute(query, {"skip": skip, "limit": limit})
        return [dict(row._mapping) for row in result]
    
    def get_livre_by_id(self, db: Session, livre_id: int) -> Optional[Dict]:
        """Récupérer un livre par son ID"""
        query = text("""
            SELECT 
                id_livre, titre, annee_publication, isbn, description,
                nombre_pages, url_couverture, url_openlibrary, url_googlebooks,
                url_babelio, url_goodreads, note_moyenne, nombre_avis,
                statut_acquisition, date_ajout, date_modification
            FROM test.livre 
            WHERE id_livre = :livre_id
        """)
        
        result = db.execute(query, {"livre_id": livre_id})
        row = result.fetchone()
        return dict(row._mapping) if row else None
    
    def get_livre_complet(self, db: Session, livre_id: int) -> Optional[Dict]:
        """Récupérer un livre avec ses relations"""
        livre = self.get_livre_by_id(db, livre_id)
        if not livre:
            return None
            
        # Récupérer les auteurs
        auteurs_query = text("""
            SELECT a.id_auteur, a.nom, a.url_openlibrary, a.url_googlebooks,
                   a.url_babelio, a.url_goodreads
            FROM test.auteur a
            JOIN test.livre_auteur la ON a.id_auteur = la.id_auteur
            WHERE la.id_livre = :livre_id
        """)
        auteurs_result = db.execute(auteurs_query, {"livre_id": livre_id})
        livre["auteurs"] = [dict(row._mapping) for row in auteurs_result]
        
        # Récupérer les éditeurs
        editeurs_query = text("""
            SELECT e.id_editeur, e.nom, e.url_openlibrary, e.url_googlebooks,
                   e.url_babelio, e.url_goodreads
            FROM test.editeur e
            JOIN test.livre_editeur le ON e.id_editeur = le.id_editeur
            WHERE le.id_livre = :livre_id
        """)
        editeurs_result = db.execute(editeurs_query, {"livre_id": livre_id})
        livre["editeurs"] = [dict(row._mapping) for row in editeurs_result]
        
        return livre
    
    def rechercher_livres(self, db: Session, query_text: str) -> List[Dict]:
        """Recherche simple de livres"""
        query = text("""
            SELECT DISTINCT l.id_livre, l.titre, l.annee_publication, l.isbn,
                   l.description, l.nombre_pages, l.note_moyenne
            FROM test.livre l
            LEFT JOIN test.livre_auteur la ON l.id_livre = la.id_livre
            LEFT JOIN test.auteur a ON la.id_auteur = a.id_auteur
            WHERE l.titre ILIKE :query 
               OR l.description ILIKE :query 
               OR a.nom ILIKE :query
               OR l.isbn ILIKE :query
            ORDER BY l.date_ajout DESC
            LIMIT 50
        """)
        
        result = db.execute(query, {"query": f"%{query_text}%"})
        return [dict(row._mapping) for row in result]
    
    def get_statistiques(self, db: Session) -> Dict:
        """Statistiques de base"""
        stats_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM test.livre) as total_livres,
                (SELECT COUNT(*) FROM test.auteur) as total_auteurs,
                (SELECT COUNT(*) FROM test.editeur) as total_editeurs,
                (SELECT COUNT(*) FROM test.langue) as total_langues,
                (SELECT COUNT(*) FROM test.sujet) as total_sujets
        """)
        
        result = db.execute(stats_query)
        row = result.fetchone()
        return dict(row._mapping) if row else {}

class AuteurCRUD:
    def get_auteurs(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
        query = text("""
            SELECT id_auteur, nom, url_openlibrary, url_googlebooks,
                   url_babelio, url_goodreads, date_ajout, date_modification
            FROM test.auteur 
            ORDER BY nom
            LIMIT :limit OFFSET :skip
        """)
        
        result = db.execute(query, {"skip": skip, "limit": limit})
        return [dict(row._mapping) for row in result]

class EditeurCRUD:
    def get_editeurs(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
        query = text("""
            SELECT id_editeur, nom, url_openlibrary, url_googlebooks,
                   url_babelio, url_goodreads, date_ajout, date_modification
            FROM test.editeur 
            ORDER BY nom
            LIMIT :limit OFFSET :skip
        """)
        
        result = db.execute(query, {"skip": skip, "limit": limit})
        return [dict(row._mapping) for row in result]

# Instances globales
livre_crud = LivreCRUD()
auteur_crud = AuteurCRUD()
editeur_crud = EditeurCRUD() 