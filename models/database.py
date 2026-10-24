"""
Module de gestion des connexions de base de données
"""

import pymysql  # type: ignore
from pymongo import MongoClient
import config

# Configuration MySQL
mysql_connection = None

def init_mysql(app):
    """Initialise la connexion MySQL"""
    global mysql_connection
    try:
        mysql_connection = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"Erreur de connexion MySQL: {e}")
        mysql_connection = None

def get_mysql_connection():
    """Récupère une connexion MySQL sécurisée"""
    return mysql_connection

def get_mysql_cursor(dict_cursor: bool = True):
    """Récupère un curseur MySQL"""
    global mysql_connection
    connection = get_mysql_connection()
    
    # Si pas de connexion ou connexion fermée, reconnecter
    if not connection or not connection.open:
        try:
            mysql_connection = pymysql.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DB,
                cursorclass=pymysql.cursors.DictCursor
            )
            connection = mysql_connection
        except Exception as e:
            print(f"Erreur de reconnexion MySQL: {e}")
            return None
    
    # Vérifier si la connexion est toujours active
    try:
        connection.ping(reconnect=True)
    except Exception:
        try:
            mysql_connection = pymysql.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DB,
                cursorclass=pymysql.cursors.DictCursor
            )
            connection = mysql_connection
        except Exception as e:
            print(f"Erreur de reconnexion MySQL: {e}")
            return None
    
    cursor_class = pymysql.cursors.DictCursor if dict_cursor else pymysql.cursors.Cursor
    return connection.cursor(cursor_class)

# Configuration MongoDB
mongo_client = None
mongo_db = None

def init_mongo():
    """Initialise la connexion MongoDB"""
    global mongo_client, mongo_db
    try:
        mongo_client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        # Tester la connexion
        mongo_client.server_info()
        mongo_db = mongo_client["decodeur_db"]
        print("Connexion MongoDB établie avec succès")
        return True
    except Exception as e:
        print(f"⚠️  MongoDB n'est pas disponible: {e}")
        print("   L'application continuera sans MongoDB. Démarrez MongoDB pour utiliser cette fonctionnalité.")
        mongo_client = None
        mongo_db = None
        return False

def get_mongo_connection():
    """Récupère la connexion MongoDB"""
    return mongo_db

def get_mongo_collection(collection_name: str):
    """Récupère une collection MongoDB"""
    if mongo_db is None:
        return None
    try:
        # Vérifier que la connexion est toujours active
        mongo_client.server_info()
        return mongo_db[collection_name]
    except Exception as e:
        print(f"Erreur d'accès à MongoDB: {e}")
        return None

# Collection principale pour les fichiers bruts
def get_fns_collection():
    """Récupère la collection FNS_LigneBrute"""
    try:
        return get_mongo_collection("FNS_LigneBrute")
    except Exception as e:
        print(f"Erreur lors de la récupération de la collection FNS_LigneBrute: {e}")
        return None 