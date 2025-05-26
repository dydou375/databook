-- Table Livre
CREATE TABLE Livre (
    id_livre INT PRIMARY KEY AUTO_INCREMENT,
    titre VARCHAR(255) NOT NULL,
    date_publication DATE,
    isbn VARCHAR(20),
    langue VARCHAR(50),
    description TEXT,
    note_moyenne FLOAT,
    nb_pages INT,
    couverture_url VARCHAR(255)
);

-- Table Auteur
CREATE TABLE Auteur (
    id_auteur INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255) NOT NULL,
    date_naissance DATE,
    biographie TEXT
);

-- Table Genre
CREATE TABLE Genre (
    id_genre INT PRIMARY KEY AUTO_INCREMENT,
    nom_genre VARCHAR(100) NOT NULL
);

-- Table Utilisateur
CREATE TABLE Utilisateur (
    id_utilisateur INT PRIMARY KEY AUTO_INCREMENT,
    pseudo VARCHAR(100) NOT NULL,
    mail VARCHAR(100) NOT NULL,
    mot_de_passe VARCHAR(100) NOT NULL,
    date_inscription DATE,
    pays VARCHAR(100)
);

-- Table Critique
CREATE TABLE Critique (
    id_critique INT PRIMARY KEY AUTO_INCREMENT,
    id_utilisateur INT,
    id_livre INT,
    note FLOAT,
    commentaire TEXT,
    date_critique DATE,
    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur),
    FOREIGN KEY (id_livre) REFERENCES Livre(id_livre)
);

-- Table d'association Livre_Auteur (N-N)
CREATE TABLE Livre_Auteur (
    id_livre INT,
    id_auteur INT,
    PRIMARY KEY (id_livre, id_auteur),
    FOREIGN KEY (id_livre) REFERENCES Livre(id_livre),
    FOREIGN KEY (id_auteur) REFERENCES Auteur(id_auteur)
);

-- Table d'association Livre_Genre (N-N)
CREATE TABLE Livre_Genre (
    id_livre INT,
    id_genre INT,
    PRIMARY KEY (id_livre, id_genre),
    FOREIGN KEY (id_livre) REFERENCES Livre(id_livre),
    FOREIGN KEY (id_genre) REFERENCES Genre(id_genre)
);