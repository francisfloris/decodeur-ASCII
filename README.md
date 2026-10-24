# 📡 Décodeur MSC - Trafic Mobile

Un projet complet basé sur Flask pour transformer, analyser et visualiser des fichiers bruts ASCII issus du Mobile Switching Center (MSC) en données structurées, avec gestion avancée des utilisateurs, abonnements, paiements, et interface moderne responsive.

![Décodeur MSC](static/images/logo.png)

## 📝 Sommaire
- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Structure du Projet](#-structure-du-projet)
- [Sécurité](#-sécurité)
- [Personnalisation & Dark Mode](#-personnalisation--dark-mode)
- [API REST](#-api-rest-intégrée)
- [Tests](#-tests)
- [Nettoyage & Optimisation](#-nettoyage-et-optimisation)
- [Contribution](#-contribution)
- [Support](#-support)
- [FAQ](#-faq)
- [Licence](#-licence)

## ✨ Fonctionnalités

### 🔐 Authentification & Sécurité
- ✅ Authentification sécurisée des utilisateurs
- 📧 Réinitialisation de mot de passe par email
- 🔒 Gestion des sessions sécurisées
- 👥 Système de rôles (utilisateur/admin)
- 🛡️ Protection CSRF et validation des données

### 📊 Traitement des Données
- 📤 Téléversement de fichiers bruts (.txt, .csv, .log, .avro, .parquet)
- 🧠 Parsing automatique des lignes MSC vers base MySQL
- 📊 Visualisation des appels décodés via dashboard interactif
- 🧾 Filtrage dynamique : date, appelant, MSC, durée, type d'appel
- 📥 Export CSV compatible Power BI / Tableau
- 📋 Visualisation des données brutes avec coloration syntaxique

### 💳 Système de Paiement
- 💳 Gestion des abonnements et paiements
- 📈 Suivi des quotas d'utilisation
- 🔄 Renouvellement automatique des abonnements
- 📊 Historique des transactions

### 🛠️ Administration
- 👨‍💼 Panel d'administration complet
- 👥 **Gestion avancée des utilisateurs** ✨
  - ✅ Modification des informations utilisateur (nom, email, rôle)
  - ✅ Changement de mot de passe sécurisé
  - ✅ Suppression d'utilisateurs avec confirmation
  - 🛡️ Protection contre l'auto-suppression
  - 🔒 Protection des privilèges administrateur
- 📊 Statistiques d'utilisation en temps réel
- 🔧 Configuration système centralisée
- 📈 Tableau de bord analytique

### 🌐 API REST intégrée
- 🔑 Authentification JWT sécurisée
- 👤 Gestion des utilisateurs (CRUD, admin)
- 📊 Accès aux données MSC filtrées
- 📈 Statistiques et export CSV/JSON
- 📖 Documentation interactive sur `/api/v1/docs`

## 🎨 Design Moderne

L'interface utilisateur a été entièrement modernisée avec :
- 🎨 Design futuriste avec gradients bleu ciel/bleu foncé
- ✨ Animations fluides et transitions
- 📱 Interface responsive (mobile-first)
- 🔤 Typographie moderne (Poppins)
- 🎯 Icônes Font Awesome
- 🌈 Palette de couleurs cohérente
- 🎭 **Nouveaux templates** : Formulaire de modification utilisateur

## 🧰 Technologies

### Backend
- **Framework** : Flask (Python)
- **Base de données** : MongoDB (données brutes) + MySQL (données structurées)
- **Email** : Flask-Mail
- **Sécurité** : itsdangerous, werkzeug
- **Traitement** : pandas, pymongo
- **Validation** : Validation côté client et serveur
- **API REST** : Flask-RESTful, PyJWT

### Frontend
- **Design** : CSS3 personnalisé avec gradients et animations
- **Typographie** : Google Fonts (Poppins)
- **Icônes** : Font Awesome 6
- **Responsive** : CSS Grid et Flexbox
- **Animations** : CSS Transitions et Transforms
- **JavaScript** : Validation formulaires et interactions

## ⚙️ Installation

### 1. Cloner le projet
```bash
git clone <lien-du-projet>
cd décodeur
```

### 2. Créer et activer l'environnement virtuel
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration
- Copier `config.py` et configurer vos paramètres
- Configurer les variables d'environnement pour la base de données
- Configurer les paramètres SMTP pour l'envoi d'emails

### 5. Initialiser la base de données
```bash
# Créer les tables MySQL
mysql -u username -p database_name < database.sql

# Initialiser les données de test (optionnel)
python scripts/init_dummy_data.py
```

### 6. Lancer l'application
```bash
python app.py
```

L'application sera accessible sur `http://localhost:5000`

## 📂 Structure du Projet

```
décodeur/
├── app.py                          # Application principale Flask
├── config.py                       # Configuration de l'application
├── database.sql                    # Schéma de base de données MySQL
├── requirements.txt                # Dépendances Python
├── README.md                       # Documentation
│
├── models/                         # Modèles de données
│   ├── __init__.py
│   ├── database.py                 # Connexions base de données
│   ├── user.py                     # Gestion des utilisateurs
│   ├── decoder.py                  # Décodage MSC
│   ├── file_upload.py              # Gestion des fichiers
│   └── subscription.py             # Gestion des abonnements
│
├── routes/                         # Routes de l'application
│   ├── __init__.py
│   ├── auth.py                     # Authentification
│   ├── admin.py                    # Administration
│   ├── dashboard.py                # Tableau de bord
│   ├── files.py                    # Gestion des fichiers
│   └── subscription.py             # Abonnements
│
├── templates/                      # Templates HTML
│   ├── accueil.html               # Page d'accueil
│   ├── login.html                 # Connexion
│   ├── signup.html                # Inscription
│   ├── reset_password.html        # Réinitialisation mot de passe
│   ├── new_password.html          # Nouveau mot de passe
│   ├── dashboard.html             # Tableau de bord principal
│   ├── fichiers.html              # Gestion des fichiers
│   ├── upload.html                # Téléversement de fichiers
│   ├── raw.html                   # Visualisation données brutes
│   ├── decodeurs.html             # Décodage des données
│   ├── voir_fichier.html          # Détails d'un fichier
│   ├── admin_utilisateurs.html    # Gestion des utilisateurs
│   ├── modifier_utilisateur.html  # ✨ Modification utilisateur
│   ├── admin_panel.html           # Panel d'administration
│   ├── mes_abonnements.html       # Gestion des abonnements
│   ├── paiement.html              # Page de paiement
│   ├── mes_paiements.html         # Historique des paiements
│   ├── 403.html                   # Page d'erreur 403
│   ├── 404.html                   # Page d'erreur 404
│   └── 500.html                   # Page d'erreur 500
│
├── utils/                          # Utilitaires
│   ├── __init__.py
│   ├── decorators.py              # Décorateurs de sécurité
│   ├── mail.py                    # Gestion des emails
│   └── export.py                  # Export de données
│
├── static/                         # Ressources statiques
│   ├── enhanced_style.css         # Styles CSS modernes
│   ├── ui_enhancements.js         # Améliorations JavaScript
│   └── images/                    # Images et logos
│       ├── logo.png               # Logo principal
│       └── background*.jpg        # Images de fond
│
├── tests/                          # Tests unitaires et API
│   └── run_tests.py              # Script pour exécuter tous les tests
│
└── venv/                           # Environnement virtuel Python
```

## 📦 Classes et Méthodes

| Classe | Méthodes | Description |
|--------|----------|-------------|
| **User** | | |
| | `__init__(id_utilisateur, nom, email, role, date_creation)` | Constructeur de la classe User |
| | `from_dict(data: Dict) -> User` | Crée un utilisateur à partir d'un dictionnaire |
| | `to_dict() -> Dict` | Convertit l'utilisateur en dictionnaire |
| **UserManager** | | |
| | `create_user(nom: str, email: str, password: str) -> Optional[User]` | Crée un nouvel utilisateur |
| | `authenticate_user(email: str, password: str) -> Optional[User]` | Authentifie un utilisateur |
| | `get_user_by_email(email: str) -> Optional[User]` | Récupère un utilisateur par email |
| | `get_user_by_id(user_id: int) -> Optional[User]` | Récupère un utilisateur par ID |
| | `update_password(email: str, new_password: str) -> bool` | Met à jour le mot de passe |
| | `get_all_users(search_query: str = '') -> List[User]` | Récupère tous les utilisateurs avec recherche |
| | `update_user_role(user_id: int, new_role: str) -> bool` | Met à jour le rôle d'un utilisateur |
| | `update_user(user_id: int, nom: str, email: str, role: str, new_password: Optional[str]) -> bool` | Met à jour les informations d'un utilisateur |
| | `delete_user(user_id: int) -> bool` | Supprime un utilisateur |
| **FileUpload** | | |
| | `__init__(nom_fichier, utilisateur, horodatage, total_lignes)` | Constructeur de la classe FileUpload |
| | `from_dict(data: Dict) -> FileUpload` | Crée un fichier uploadé à partir d'un dictionnaire |
| **FileUploadManager** | | |
| | `is_valid_extension(filename: Optional[str]) -> bool` | Vérifie si l'extension du fichier est autorisée |
| | `upload_file(file_content: bytes, filename: str, user_email: str) -> bool` | Upload un fichier dans MongoDB |
| | `get_uploaded_files(page: int = 1, per_page: int = 10) -> Dict` | Récupère la liste des fichiers uploadés avec pagination |
| | `get_file_content(filename: str) -> List[Dict]` | Récupère le contenu d'un fichier |
| | `delete_file(filename: str) -> bool` | Supprime un fichier et toutes ses lignes |
| | `search_raw_lines(filename_filter: str, date_debut: str, date_fin: str, page: int, per_page: int) -> Dict` | Recherche dans les lignes brutes avec filtres |
| | `clear_all_raw_lines() -> bool` | Supprime toutes les lignes brutes (admin seulement) |
| | `export_file_content(filename: str) -> str` | Exporte le contenu d'un fichier en texte |
| **Decoder** | | |
| | `__init__(id_decodeur, id_utilisateur, statut, horodatage_execution, nom_utilisateur)` | Constructeur de la classe Decoder |
| | `from_dict(data: Dict) -> Decoder` | Crée un décodeur à partir d'un dictionnaire |
| **DecoderManager** | | |
| | `create_decoder(user_id: int) -> Optional[Decoder]` | Crée un nouveau processus de décodage |
| | `update_decoder_status(decoder_id: int, status: str) -> bool` | Met à jour le statut d'un décodeur |
| | `get_decoder_history() -> List[Decoder]` | Récupère l'historique des décodages |
| | `decode_msc_lines(user_id: int) -> bool` | Décode les lignes MSC non encore traitées |
| **MSCParser** | | |
| | `parse_line(line_content: str) -> Optional[Dict[str, Any]]` | Parse une ligne MSC selon le format attendu |
| | `validate_line(line_content: str) -> bool` | Valide une ligne MSC |
| **Subscription** | | |
| | `__init__(id_ab, id_utilisateur, id_type, date_debut, date_fin, statut, libelle)` | Constructeur de la classe Subscription |
| | `from_dict(data: Dict) -> Subscription` | Crée un abonnement à partir d'un dictionnaire |
| | `is_active() -> bool` | Vérifie si l'abonnement est actif |
| | `days_remaining() -> int` | Calcule le nombre de jours restants |
| **SubscriptionManager** | | |
| | `get_active_subscription(user_id: int) -> Optional[Subscription]` | Récupère l'abonnement actif d'un utilisateur |
| | `create_subscription(user_id: int, type_id: int, montant: float) -> Optional[Subscription]` | Crée un nouvel abonnement |
| | `get_subscription_by_id(abonnement_id: int) -> Optional[Subscription]` | Récupère un abonnement par son ID |
| | `get_user_subscriptions(user_id: int) -> List[Subscription]` | Récupère tous les abonnements d'un utilisateur |
| | `get_subscription_types() -> List[Dict]` | Récupère tous les types d'abonnements disponibles |
| | `check_quota(user_id: int) -> Dict` | Vérifie le quota d'un utilisateur |
| **DatabaseManager** | | |
| | `init_mysql(app) -> None` | Initialise la connexion MySQL |
| | `get_mysql_connection() -> Optional[Connection]` | Récupère une connexion MySQL sécurisée |
| | `get_mysql_cursor(dict_cursor: bool = True) -> Optional[Cursor]` | Récupère un curseur MySQL |
| | `init_mongo() -> bool` | Initialise la connexion MongoDB |
| | `get_mongo_connection() -> Optional[Database]` | Récupère la connexion MongoDB |
| | `get_mongo_collection(collection_name: str) -> Optional[Collection]` | Récupère une collection MongoDB |
| | `get_fns_collection() -> Optional[Collection]` | Récupère la collection FNS_LigneBrute |

## 🚀 Utilisation

### Première connexion
1. Accédez à `http://localhost:5000`
2. Créez un compte utilisateur
3. Vérifiez votre email pour activer le compte
4. Connectez-vous à l'application

### Téléversement et décodage
1. Allez dans "Fichiers" → "Téléverser"
2. Sélectionnez vos fichiers MSC (.txt, .csv, .log, etc.)
3. Les fichiers sont automatiquement décodés
4. Visualisez les résultats dans le dashboard

### Gestion des utilisateurs (Admin)
1. Accédez au panel d'administration
2. **Modifier un utilisateur** : Cliquez sur "Modifier" → Formulaire complet
3. **Supprimer un utilisateur** : Cliquez sur "Supprimer" → Confirmation

### API REST (intégration tierce)

- **Base URL** : `http://localhost:5000/api/v1`
- **Documentation interactive** : [http://localhost:5000/api/v1/docs](http://localhost:5000/api/v1/docs)

#### Exemple d'authentification
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

#### Exemple d'accès protégé
```bash
curl -X GET http://localhost:5000/api/v1/data \
  -H "Authorization: Bearer <token>"
```

#### Export CSV
```bash
curl -X GET "http://localhost:5000/api/v1/export?format=csv" \
  -H "Authorization: Bearer <token>" \
  -o export.csv
```

Pour plus d'exemples, voir la documentation interactive ou le code source.

## 🧪 Tests

- Tous les tests unitaires et API sont dans le dossier `tests/`.
- Pour exécuter tous les tests :
```bash
python tests/run_tests.py
```

## 🧹 Nettoyage et optimisation

- Suppression des fichiers et dossiers inutiles :
  - Dossiers et fichiers __pycache__, .pyc, scripts/ (vide), api/ (vestige), tests/ (si non utilisé)
  - Fichiers d'initialisation __init__.py inutiles dans les sous-dossiers
- Seuls les fichiers essentiels au fonctionnement et à la maintenance du projet sont conservés.
- Structure du projet simplifiée pour une meilleure lisibilité et maintenance.

## 📝 Licence

Ce projet est développé dans le cadre d'un décodeur MSC orienté Business Intelligence.

---

*Style : Futuriste | Palette : Bleu ciel, bleu foncé et blanc | Icône : DATA (format PNG)*

## 📈 Statistiques du Projet

- **Lignes de code** : ~5000+
- **Templates** : 20+
- **Routes** : 30+
- **Modèles** : 5+
- **Tests** : En cours de développement
- **Documentation** : Complète

## 🛡️ Sécurité

- Authentification sécurisée (hashing, sessions, JWT pour l'API)
- Protection CSRF sur tous les formulaires
- Validation stricte côté client et serveur
- Gestion des rôles (utilisateur/admin) avec restrictions d'accès
- Logs d'activité et alertes sur actions sensibles
- Protection contre l'auto-suppression et l'élévation de privilèges

## 🎨 Personnalisation & Dark Mode

- Interface claire/sombre avec palette personnalisée (noir, bleu foncé, jaune)
- Toggle dark/light mode persistant (localStorage, synchro multi-onglets)
- CSS et JS facilement modifiables pour adapter le style à vos besoins
- Responsive design pour tous supports (mobile, tablette, desktop)

## 🤝 Contribution

Les contributions sont les bienvenues !
- Forkez le repo, créez une branche, proposez une Pull Request
- Respectez la structure du projet et les conventions de nommage
- Ajoutez des tests pour toute nouvelle fonctionnalité
- Décrivez clairement vos changements dans la PR

## 📬 Support

Pour toute question, bug ou suggestion :
- Ouvrez une issue sur le repo
- Contactez l'auteur par email (voir en-tête du projet)

## ❓ FAQ

**Q : Comment activer le mode sombre par défaut ?**
R : Modifiez la valeur par défaut dans le JS du toggle dark mode.

**Q : Comment ajouter un nouveau type d'abonnement ?**
R : Ajoutez-le dans la base de données et adaptez le formulaire de paiement.

**Q : Comment déployer en production ?**
R : Utilisez un serveur WSGI (gunicorn, uwsgi), configurez les variables d'environnement, sécurisez les clés et SMTP.