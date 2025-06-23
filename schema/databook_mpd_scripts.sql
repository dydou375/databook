-- =============================================
-- DATABOOK - Modèle Physique de Données (MPD)
-- Système de Gestion de Base de Données : PostgreSQL
-- =============================================

-- Suppression des tables (ordre inverse des dépendances)
DROP TABLE IF EXISTS livre_sujet CASCADE;
DROP TABLE IF EXISTS livre_langue CASCADE;
DROP TABLE IF EXISTS livre_editeur CASCADE;
DROP TABLE IF EXISTS livre_auteur CASCADE;
DROP TABLE IF EXISTS sujet CASCADE;
DROP TABLE IF EXISTS langue CASCADE;
DROP TABLE IF EXISTS editeur CASCADE;
DROP TABLE IF EXISTS auteur CASCADE;
DROP TABLE IF EXISTS livre CASCADE;

-- =============================================
-- TABLES PRINCIPALES
-- =============================================

-- Table LIVRE (entité centrale)
CREATE TABLE livre (
    id_livre SERIAL PRIMARY KEY,
    titre VARCHAR(500) NOT NULL,
    annee_publication INTEGER CHECK (annee_publication > 0 AND annee_publication <= EXTRACT(YEAR FROM CURRENT_DATE)),
    isbn VARCHAR(20) UNIQUE,
    description TEXT,
    nombre_pages INTEGER CHECK (nombre_pages > 0),
    url_couverture VARCHAR(500),
    url_openlibrary VARCHAR(500),
    url_googlebooks VARCHAR(500),
    url_babelio VARCHAR(500),
    url_goodreads VARCHAR(500),
    note_moyenne DECIMAL(3,1) CHECK (note_moyenne >= 0 AND note_moyenne <= 10),
    nombre_avis INTEGER DEFAULT 0 CHECK (nombre_avis >= 0),
    statut_acquisition VARCHAR(50) DEFAULT 'disponible',
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table AUTEUR
CREATE TABLE auteur (
    id_auteur SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    url_openlibrary VARCHAR(500),
    url_googlebooks VARCHAR(500),
    url_babelio VARCHAR(500),
    url_goodreads VARCHAR(500),
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table EDITEUR
CREATE TABLE editeur (
    id_editeur SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    url_openlibrary VARCHAR(500),
    url_googlebooks VARCHAR(500),
    url_babelio VARCHAR(500),
    url_goodreads VARCHAR(500),
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table LANGUE
CREATE TABLE langue (
    id_langue SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table SUJET
CREATE TABLE sujet (
    id_sujet SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- TABLES DE LIAISON (Relations N-N)
-- =============================================

-- Table LIVRE_AUTEUR
CREATE TABLE livre_auteur (
    id_livre INTEGER NOT NULL,
    id_auteur INTEGER NOT NULL,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_livre, id_auteur),
    FOREIGN KEY (id_livre) REFERENCES livre(id_livre) ON DELETE CASCADE,
    FOREIGN KEY (id_auteur) REFERENCES auteur(id_auteur) ON DELETE CASCADE
);

-- Table LIVRE_EDITEUR
CREATE TABLE livre_editeur (
    id_livre INTEGER NOT NULL,
    id_editeur INTEGER NOT NULL,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_livre, id_editeur),
    FOREIGN KEY (id_livre) REFERENCES livre(id_livre) ON DELETE CASCADE,
    FOREIGN KEY (id_editeur) REFERENCES editeur(id_editeur) ON DELETE CASCADE
);

-- Table LIVRE_LANGUE
CREATE TABLE livre_langue (
    id_livre INTEGER NOT NULL,
    id_langue INTEGER NOT NULL,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_livre, id_langue),
    FOREIGN KEY (id_livre) REFERENCES livre(id_livre) ON DELETE CASCADE,
    FOREIGN KEY (id_langue) REFERENCES langue(id_langue) ON DELETE CASCADE
);

-- Table LIVRE_SUJET
CREATE TABLE livre_sujet (
    id_livre INTEGER NOT NULL,
    id_sujet INTEGER NOT NULL,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_livre, id_sujet),
    FOREIGN KEY (id_livre) REFERENCES livre(id_livre) ON DELETE CASCADE,
    FOREIGN KEY (id_sujet) REFERENCES sujet(id_sujet) ON DELETE CASCADE
);

-- =============================================
-- INDEX POUR OPTIMISATION DES PERFORMANCES
-- =============================================

-- Index sur les champs de recherche fréquents
CREATE INDEX idx_livre_titre ON livre(titre);
CREATE INDEX idx_livre_isbn ON livre(isbn);
CREATE INDEX idx_livre_annee ON livre(annee_publication);
CREATE INDEX idx_livre_note ON livre(note_moyenne);

-- Index sur les noms d'auteurs (recherche textuelle)
CREATE INDEX idx_auteur_nom ON auteur(nom);
CREATE INDEX idx_auteur_nom_gin ON auteur USING gin(to_tsvector('french', nom));

-- Index sur les noms d'éditeurs
CREATE INDEX idx_editeur_nom ON editeur(nom);

-- Index sur les codes et noms de langues
CREATE INDEX idx_langue_code ON langue(code);
CREATE INDEX idx_langue_nom ON langue(nom);

-- Index sur les noms de sujets
CREATE INDEX idx_sujet_nom ON sujet(nom);

-- Index composites pour les tables de liaison (optimisation des jointures)
CREATE INDEX idx_livre_auteur_livre ON livre_auteur(id_livre);
CREATE INDEX idx_livre_auteur_auteur ON livre_auteur(id_auteur);
CREATE INDEX idx_livre_editeur_livre ON livre_editeur(id_livre);
CREATE INDEX idx_livre_editeur_editeur ON livre_editeur(id_editeur);
CREATE INDEX idx_livre_langue_livre ON livre_langue(id_livre);
CREATE INDEX idx_livre_langue_langue ON livre_langue(id_langue);
CREATE INDEX idx_livre_sujet_livre ON livre_sujet(id_livre);
CREATE INDEX idx_livre_sujet_sujet ON livre_sujet(id_sujet);

-- =============================================
-- TRIGGERS POUR MISE À JOUR AUTOMATIQUE
-- =============================================

-- Fonction de mise à jour de date_modification
CREATE OR REPLACE FUNCTION update_date_modification()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_modification = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers sur toutes les tables
CREATE TRIGGER trig_livre_update_date BEFORE UPDATE ON livre 
    FOR EACH ROW EXECUTE FUNCTION update_date_modification();

CREATE TRIGGER trig_auteur_update_date BEFORE UPDATE ON auteur 
    FOR EACH ROW EXECUTE FUNCTION update_date_modification();

CREATE TRIGGER trig_editeur_update_date BEFORE UPDATE ON editeur 
    FOR EACH ROW EXECUTE FUNCTION update_date_modification();

CREATE TRIGGER trig_langue_update_date BEFORE UPDATE ON langue 
    FOR EACH ROW EXECUTE FUNCTION update_date_modification();

CREATE TRIGGER trig_sujet_update_date BEFORE UPDATE ON sujet 
    FOR EACH ROW EXECUTE FUNCTION update_date_modification();

-- =============================================
-- DONNÉES DE RÉFÉRENCE (LANGUES)
-- =============================================

-- Insertion des langues principales
INSERT INTO langue (code, nom) VALUES 
    ('fr', 'Français'),
    ('en', 'Anglais'),
    ('es', 'Espagnol'),
    ('de', 'Allemand'),
    ('it', 'Italien'),
    ('pt', 'Portugais'),
    ('ru', 'Russe'),
    ('ja', 'Japonais'),
    ('zh', 'Chinois'),
    ('ar', 'Arabe')
ON CONFLICT (code) DO NOTHING;

-- =============================================
-- COMMENTAIRES POUR DOCUMENTATION
-- =============================================

COMMENT ON TABLE livre IS 'Table principale contenant les informations des livres';
COMMENT ON COLUMN livre.isbn IS 'ISBN unique du livre (ISBN-10 ou ISBN-13)';
COMMENT ON COLUMN livre.note_moyenne IS 'Note moyenne sur 10 calculée depuis les différentes sources';
COMMENT ON COLUMN livre.statut_acquisition IS 'Statut : disponible, épuisé, à_paraître, etc.';

COMMENT ON TABLE livre_auteur IS 'Table de liaison N-N entre livres et auteurs';
COMMENT ON TABLE livre_editeur IS 'Table de liaison N-N entre livres et éditeurs';
COMMENT ON TABLE livre_langue IS 'Table de liaison N-N entre livres et langues';
COMMENT ON TABLE livre_sujet IS 'Table de liaison N-N entre livres et sujets/genres';

-- =============================================
-- VUES UTILES POUR L'APPLICATION
-- =============================================

-- Vue complète des livres avec leurs auteurs
CREATE OR REPLACE VIEW vue_livres_complets AS
SELECT 
    l.id_livre,
    l.titre,
    l.annee_publication,
    l.isbn,
    l.description,
    l.nombre_pages,
    l.note_moyenne,
    l.nombre_avis,
    STRING_AGG(DISTINCT a.nom, ', ' ORDER BY a.nom) AS auteurs,
    STRING_AGG(DISTINCT e.nom, ', ' ORDER BY e.nom) AS editeurs,
    STRING_AGG(DISTINCT lg.nom, ', ' ORDER BY lg.nom) AS langues,
    STRING_AGG(DISTINCT s.nom, ', ' ORDER BY s.nom) AS sujets
FROM livre l
LEFT JOIN livre_auteur la ON l.id_livre = la.id_livre
LEFT JOIN auteur a ON la.id_auteur = a.id_auteur
LEFT JOIN livre_editeur le ON l.id_livre = le.id_livre
LEFT JOIN editeur e ON le.id_editeur = e.id_editeur
LEFT JOIN livre_langue ll ON l.id_livre = ll.id_livre
LEFT JOIN langue lg ON ll.id_langue = lg.id_langue
LEFT JOIN livre_sujet ls ON l.id_livre = ls.id_livre
LEFT JOIN sujet s ON ls.id_sujet = s.id_sujet
GROUP BY l.id_livre, l.titre, l.annee_publication, l.isbn, l.description, 
         l.nombre_pages, l.note_moyenne, l.nombre_avis;

COMMENT ON VIEW vue_livres_complets IS 'Vue dénormalisée pour affichage rapide des livres avec toutes leurs métadonnées';

-- Fin du script MPD DataBook 