#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration MongoDB pour l'import des critiques de livres
"""

# Configuration MongoDB
MONGODB_CONFIG = {
    # URI de connexion MongoDB (modifiez selon votre installation)
    'uri': 'mongodb://localhost:27017/',
    
    # Nom de la base de données
    'database': 'databook',
    
    # Nom de la collection
    'collection': 'critiques_livres',
    
    # Options de connexion
    'options': {
        'serverSelectionTimeoutMS': 5000,  # Timeout en millisecondes
        'connectTimeoutMS': 10000,
    }
}

# Configuration de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'import_mongodb.log'
}

# Schéma de validation pour la collection (optionnel)
COLLECTION_SCHEMA = {
    "bsonType": "object",
    "required": ["isbn", "titre", "auteur"],
    "properties": {
        "isbn": {
            "bsonType": "string",
            "description": "ISBN du livre (obligatoire)"
        },
        "titre": {
            "bsonType": "string",
            "description": "Titre du livre (obligatoire)"
        },
        "auteur": {
            "bsonType": "string",
            "description": "Auteur du livre (obligatoire)"
        },
        "note_babelio": {
            "bsonType": ["double", "null"],
            "minimum": 0,
            "maximum": 5,
            "description": "Note Babelio entre 0 et 5"
        },
        "nombre_votes_babelio": {
            "bsonType": ["int", "null"],
            "minimum": 0,
            "description": "Nombre de votes sur Babelio"
        },
        "critiques_babelio": {
            "bsonType": "array",
            "items": {
                "bsonType": "object",
                "properties": {
                    "utilisateur": {"bsonType": "string"},
                    "date": {"bsonType": "string"},
                    "note_utilisateur": {"bsonType": ["double", "null"]},
                    "texte": {"bsonType": "string"}
                }
            }
        }
    }
} 