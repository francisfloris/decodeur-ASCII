# -*- coding: utf-8 -*-
"""
Module de gestion des utilisateurs
"""

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import Optional, Dict, List
from .database import get_mysql_cursor

class User:
    """Classe représentant un utilisateur"""
    
    def __init__(self, id_utilisateur: int, nom: str, email: str, role: str = 'user', date_creation: Optional[datetime] = None, login_attempts: int = 0, locked_until: Optional[datetime] = None):
        self.id_utilisateur = id_utilisateur
        self.nom = nom
        self.email = email
        self.role = role
        self.date_creation = date_creation or datetime.now()
        self.login_attempts = login_attempts
        self.locked_until = locked_until
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crée un utilisateur à partir d'un dictionnaire"""
        return cls(
            id_utilisateur=data.get('id_utilisateur', 0),
            nom=data.get('nom', ''),
            email=data.get('email', ''),
            role=data.get('role', 'user'),
            date_creation=data.get('date_creation', datetime.now()),
            login_attempts=data.get('login_attempts', 0),
            locked_until=data.get('locked_until')
        )
    
    def to_dict(self) -> Dict:
        """Convertit l'utilisateur en dictionnaire"""
        return {
            'id_utilisateur': self.id_utilisateur,
            'nom': self.nom,
            'email': self.email,
            'role': self.role,
            'date_creation': self.date_creation
        }

class UserManager:
    """Gestionnaire des utilisateurs"""
    
    @staticmethod
    def create_user(nom: str, email: str, password: str) -> Optional[User]:
        """Crée un nouvel utilisateur"""
        cursor = get_mysql_cursor(dict_cursor=False)
        if not cursor:
            return None
        
        try:
            # Créer l'utilisateur
            cursor.execute("INSERT INTO utilisateur (nom, email) VALUES (%s, %s)", (nom, email))
            user_id = cursor.lastrowid
            
            # Créer le compte avec le mot de passe hashé et le rôle par défaut
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO compte (id_utilisateur, mot_de_passe, role) VALUES (%s, %s, %s)", 
                         (user_id, hashed_password, 'user'))
            
            cursor.connection.commit()
            
            return User(user_id, nom, email, 'user')
            
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur: {e}")
            cursor.connection.rollback()
            return None
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur avec gestion des tentatives et blocage temporaire"""
        cursor = get_mysql_cursor()
        if not cursor:
            return None
        try:
            cursor.execute("""
                SELECT u.*, c.mot_de_passe, c.role, c.login_attempts, c.locked_until
                FROM utilisateur u
                JOIN compte c ON u.id_utilisateur = c.id_utilisateur 
                WHERE u.email = %s
            """, (email,))
            user_data = cursor.fetchone()
            if not user_data:
                return None
            # Vérifier blocage
            from datetime import datetime
            locked_until = user_data.get('locked_until')
            if locked_until and locked_until > datetime.now():
                return None
            # Vérifier mot de passe
            if check_password_hash(user_data['mot_de_passe'], password):
                # Succès : reset login_attempts et locked_until
                cursor.execute("""
                    UPDATE compte SET login_attempts = 0, locked_until = NULL WHERE id_utilisateur = %s
                """, (user_data['id_utilisateur'],))
                cursor.connection.commit()
                return User.from_dict(user_data)
            else:
                # Échec : incrémenter login_attempts
                attempts = (user_data.get('login_attempts') or 0) + 1
                if attempts >= 3:
                    from datetime import timedelta
                    locked = datetime.now() + timedelta(minutes=15)
                    cursor.execute("""
                        UPDATE compte SET login_attempts = %s, locked_until = %s WHERE id_utilisateur = %s
                    """, (attempts, locked, user_data['id_utilisateur']))
                else:
                    cursor.execute("""
                        UPDATE compte SET login_attempts = %s WHERE id_utilisateur = %s
                    """, (attempts, user_data['id_utilisateur']))
                cursor.connection.commit()
            return None
        except Exception as e:
            print(f"Erreur lors de l'authentification: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Récupère un utilisateur par email"""
        cursor = get_mysql_cursor()
        if not cursor:
            return None
        
        try:
            cursor.execute("""
                SELECT u.*, c.role 
                FROM utilisateur u
                JOIN compte c ON u.id_utilisateur = c.id_utilisateur 
                WHERE u.email = %s
            """, (email,))
            
            user_data = cursor.fetchone()
            return User.from_dict(user_data) if user_data else None
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Récupère un utilisateur par ID"""
        cursor = get_mysql_cursor()
        if not cursor:
            return None
        
        try:
            cursor.execute("""
                SELECT u.*, c.role 
                FROM utilisateur u
                JOIN compte c ON u.id_utilisateur = c.id_utilisateur 
                WHERE u.id_utilisateur = %s
            """, (user_id,))
            
            user_data = cursor.fetchone()
            return User.from_dict(user_data) if user_data else None
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None
    
    @staticmethod
    def update_password(email: str, new_password: str) -> bool:
        """Met à jour le mot de passe d'un utilisateur"""
        cursor = get_mysql_cursor(dict_cursor=False)
        if not cursor:
            return False
        
        try:
            hashed_password = generate_password_hash(new_password)
            cursor.execute("""
                UPDATE compte 
                SET mot_de_passe = %s 
                WHERE id_utilisateur = (
                    SELECT id_utilisateur FROM utilisateur WHERE email = %s
                )
            """, (hashed_password, email))
            
            cursor.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour du mot de passe: {e}")
            cursor.connection.rollback()
            return False
    
    @staticmethod
    def get_all_users(search_query: str = '') -> List[User]:
        """Récupère tous les utilisateurs avec recherche optionnelle"""
        cursor = get_mysql_cursor()
        if not cursor:
            return []
        
        try:
            if search_query:
                cursor.execute("""
                    SELECT u.*, c.role 
                    FROM utilisateur u
                    JOIN compte c ON u.id_utilisateur = c.id_utilisateur
                    WHERE u.nom LIKE %s OR u.email LIKE %s
                    ORDER BY u.date_creation DESC
                """, (f"%{search_query}%", f"%{search_query}%"))
            else:
                cursor.execute("""
                    SELECT u.*, c.role 
                    FROM utilisateur u
                    JOIN compte c ON u.id_utilisateur = c.id_utilisateur
                    ORDER BY u.date_creation DESC
                """)
            
            users_data = cursor.fetchall()
            return [User.from_dict(user_data) for user_data in users_data]
            
        except Exception as e:
            print(f"Erreur lors de la récupération des utilisateurs: {e}")
            return []
    
    @staticmethod
    def update_user_role(user_id: int, new_role: str) -> bool:
        """Met à jour le rôle d'un utilisateur"""
        cursor = get_mysql_cursor(dict_cursor=False)
        if not cursor:
            return False
        
        try:
            cursor.execute("UPDATE compte SET role = %s WHERE id_utilisateur = %s", 
                         (new_role, user_id))
            cursor.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour du rôle: {e}")
            cursor.connection.rollback()
            return False
    
    @staticmethod
    def update_user(user_id: int, nom: str, email: str, role: str, new_password: Optional[str] = None) -> bool:
        """Met à jour les informations d'un utilisateur"""
        cursor = get_mysql_cursor(dict_cursor=False)
        if not cursor:
            return False
        
        try:
            # Mettre à jour les informations de base
            cursor.execute("UPDATE utilisateur SET nom = %s, email = %s WHERE id_utilisateur = %s", 
                         (nom, email, user_id))
            
            # Mettre à jour le rôle
            cursor.execute("UPDATE compte SET role = %s WHERE id_utilisateur = %s", 
                         (role, user_id))
            
            # Mettre à jour le mot de passe si fourni
            if new_password:
                hashed_password = generate_password_hash(new_password)
                cursor.execute("UPDATE compte SET mot_de_passe = %s WHERE id_utilisateur = %s", 
                             (hashed_password, user_id))
            
            cursor.connection.commit()
            return True
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'utilisateur: {e}")
            cursor.connection.rollback()
            return False
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Supprime un utilisateur"""
        cursor = get_mysql_cursor(dict_cursor=False)
        if not cursor:
            return False
        
        try:
            # Supprimer d'abord le compte (contrainte de clé étrangère)
            cursor.execute("DELETE FROM compte WHERE id_utilisateur = %s", (user_id,))
            cursor.execute("DELETE FROM utilisateur WHERE id_utilisateur = %s", (user_id,))
            
            cursor.connection.commit()
            return True
            
        except Exception as e:
            print(f"Erreur lors de la suppression de l'utilisateur: {e}")
            cursor.connection.rollback()
            return False 