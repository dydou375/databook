-- Création de la table Livre
CREATE TABLE Livre (
    id_livre SERIAL PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    date_publication DATE,
    isbn VARCHAR(20),
    langue VARCHAR(50),
    description TEXT,
    note_moyenne DECIMAL(3, 2),
    nb_pages INTEGER,
    couverture_url TEXT
);

-- Création de la table Auteur
CREATE TABLE Auteur (
    id_auteur SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    date_naissance DATE,
    biographie TEXT
);

-- Création de la table Genre
CREATE TABLE Genre (
    id_genre SERIAL PRIMARY KEY,
    nom_genre VARCHAR(100) NOT NULL
);

-- Création de la table Critique
CREATE TABLE Critique (
    id_critique SERIAL PRIMARY KEY,
    id_utilisateur INTEGER REFERENCES Utilisateur(id_utilisateur),
    id_livre INTEGER REFERENCES Livre(id_livre),
    note INTEGER CHECK (note >= 0 AND note <= 5),
    commentaire TEXT,
    date_critique DATE
);

-- Création de la table Utilisateur
CREATE TABLE Utilisateur (
    id_utilisateur SERIAL PRIMARY KEY,
    pseudo VARCHAR(100) NOT NULL,
    date_inscription DATE,
    pays VARCHAR(100)
);