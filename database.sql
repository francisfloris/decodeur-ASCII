-- Création de la base de données
CREATE DATABASE IF NOT EXISTS decodeur_db;
USE decodeur_db;

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS utilisateur (
    id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20) DEFAULT 'client'
);

-- Table des comptes (authentification)
CREATE TABLE IF NOT EXISTS compte (
    id_compte INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    dernier_login DATETIME,
    login_attempts INT DEFAULT 0,
    locked_until DATETIME DEFAULT NULL,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur)
);

-- Table des décodeurs
CREATE TABLE IF NOT EXISTS decodeur (
    id_decodeur INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    horodatage_execution DATETIME DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(50),
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur)
);

-- Table des appels décodés
CREATE TABLE IF NOT EXISTS fs_appel (
    id_appel INT AUTO_INCREMENT PRIMARY KEY,
    type_evenement VARCHAR(10),
    datelog DATETIME,
    appelant VARCHAR(20),
    appele VARCHAR(20),
    duree INT,
    cellule_origine VARCHAR(20),
    cellule_destination VARCHAR(20),
    msc VARCHAR(50),
    fichier_source VARCHAR(255),
    date_insertion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table des lignes brutes importées
CREATE TABLE IF NOT EXISTS fns_lignebrute (
    id_ligne INT AUTO_INCREMENT PRIMARY KEY,
    contenu_ligne TEXT NOT NULL,
    nom_fichier VARCHAR(255) NOT NULL,
    horodatage_insertion DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_decodeur INT,
    FOREIGN KEY (id_decodeur) REFERENCES decodeur(id_decodeur)
);

-- Table des sessions utilisateur
CREATE TABLE IF NOT EXISTS session (
    id_session INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    token_session CHAR(36) NOT NULL,
    date_connexion DATETIME,
    date_deconnexion DATETIME,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur)
);

-- Table des types de décodage (abonnements)
CREATE TABLE IF NOT EXISTS type_decodage (
    id_td INT AUTO_INCREMENT PRIMARY KEY,
    libelle VARCHAR(100) NOT NULL,
    cout DECIMAL(10,2) NOT NULL,
    validite INT NOT NULL, -- en jours
    quota_max INT DEFAULT NULL
);

-- Table des abonnements
CREATE TABLE IF NOT EXISTS abonnement (
    id_ab INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    id_td INT NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    statut ENUM('en cours', 'actif', 'expiré') DEFAULT 'actif',
    renouvellement_auto BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    FOREIGN KEY (id_td) REFERENCES type_decodage(id_td) ON DELETE CASCADE
);

-- Table des encaissements (paiements)
CREATE TABLE IF NOT EXISTS encaissement (
    id_e INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    id_ab INT NOT NULL,
    date_e DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    montant_a_payer DECIMAL(10,2),
    montant_paye DECIMAL(10,2),
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    FOREIGN KEY (id_ab) REFERENCES abonnement(id_ab) ON DELETE CASCADE
);

-- Insertion d'utilisateurs
INSERT INTO utilisateur (nom, prenom, email, role) VALUES
('Dupont', 'Jean', 'jean.dupont@email.com', 'client'),
('Martin', 'Sophie', 'sophie.martin@email.com', 'admin');

-- Insertion de comptes
INSERT INTO compte (id_utilisateur, mot_de_passe, role) VALUES
(1, 'hash_mdp_jean', 'user'),
(2, 'hash_mdp_sophie', 'admin');

-- Insertion de décodeurs
INSERT INTO decodeur (id_utilisateur, statut) VALUES
(1, 'actif'),
(2, 'inactif');

-- Insertion d'appels décodés
INSERT INTO fs_appel (type_evenement, datelog, appelant, appele, duree, cellule_origine, cellule_destination, msc, fichier_source) VALUES
('IN', '2024-06-01 10:00:00', '0123456789', '0987654321', 120, 'CellA', 'CellB', 'MSC1', 'fichier1.txt'),
('OUT', '2024-06-01 11:00:00', '0987654321', '0123456789', 60, 'CellB', 'CellA', 'MSC2', 'fichier2.txt');

-- Insertion de lignes brutes importées
INSERT INTO fns_lignebrute (contenu_ligne, nom_fichier, id_decodeur) VALUES
('Ligne brute exemple 1', 'fichier1.txt', 1),
('Ligne brute exemple 2', 'fichier2.txt', 2);

-- Insertion de sessions utilisateur
INSERT INTO session (id_utilisateur, token_session, date_connexion) VALUES
(1, 'uuid-token-1', '2024-06-01 09:00:00'),
(2, 'uuid-token-2', '2024-06-01 09:30:00');

-- Insertion de types de décodage
INSERT INTO type_decodage (libelle, cout, validite, quota_max) VALUES
('Décodage Standard', 10.00, 30, 100),
('Décodage Premium', 25.00, 90, 500);

-- Insertion d'abonnements
INSERT INTO abonnement (id_utilisateur, id_td, date_debut, date_fin, statut, renouvellement_auto) VALUES
(1, 1, '2024-06-01', '2024-07-01', 'actif', TRUE),
(2, 2, '2024-06-01', '2024-09-01', 'en cours', FALSE);

-- Insertion d'encaissements (paiements)
INSERT INTO encaissement (id_utilisateur, id_ab, montant_a_payer, montant_paye) VALUES
(1, 1, 10.00, 10.00),
(2, 2, 25.00, 25.00);
