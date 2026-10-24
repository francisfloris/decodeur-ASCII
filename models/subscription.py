# -*- coding: utf-8 -*-
"""
Module de gestion des abonnements
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from .database import get_mysql_cursor

class Subscription:
    """Classe représentant un abonnement"""
    
    def __init__(self, id_ab: int, id_utilisateur: int, id_type: int, date_debut: datetime, 
                 date_fin: datetime, statut: str = 'actif', libelle: str = ''):
        self.id_ab = id_ab
        self.id_utilisateur = id_utilisateur
        self.id_type = id_type
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.statut = statut
        self.libelle = libelle
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crée un abonnement à partir d'un dictionnaire"""
        return cls(
            id_ab=data.get('ID_ab', 0),
            id_utilisateur=data.get('id_utilisateur', 0),
            id_type=data.get('ID_td', 0),
            date_debut=data.get('date_debut', datetime.now()),
            date_fin=data.get('date_fin', datetime.now()),
            statut=data.get('statut', 'actif'),
            libelle=data.get('libelle', '')
        )
    
    def is_active(self) -> bool:
        """Vérifie si l'abonnement est actif"""
        now = datetime.now().date()
        date_debut = self.date_debut.date() if isinstance(self.date_debut, datetime) else self.date_debut
        date_fin = self.date_fin.date() if isinstance(self.date_fin, datetime) else self.date_fin
        return (self.statut == 'actif' and 
                date_debut <= now <= date_fin)
    
    def days_remaining(self) -> int:
        """Calcule le nombre de jours restants"""
        if not self.is_active():
            return 0
        return (self.date_fin.date() - datetime.now().date()).days

class SubscriptionManager:
    """Gestionnaire des abonnements"""
    
    @staticmethod
    def get_active_subscription(user_id: int) -> Optional[Subscription]:
        """Récupère l'abonnement actif d'un utilisateur"""
        cursor = get_mysql_cursor()
        if not cursor:
            return None
        
        try:
            cursor.execute("""
                SELECT ab.*, td.libelle 
                FROM Abonnement ab
                JOIN Type_Decodage td ON ab.ID_td = td.ID_td
                WHERE ab.id_utilisateur = %s 
                AND ab.statut = 'actif'
                AND CURDATE() BETWEEN ab.date_debut AND ab.date_fin
                ORDER BY ab.date_debut DESC 
                LIMIT 1
            """, (user_id,))
            
            subscription_data = cursor.fetchone()
            return Subscription.from_dict(subscription_data) if subscription_data else None
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'abonnement: {e}")
            return None
    
    @staticmethod
    def create_subscription(user_id: int, type_id: int, montant: float = 0.0) -> Optional[Subscription]:
        """Crée un nouvel abonnement"""
        cursor = get_mysql_cursor(dict_cursor=False)
        if not cursor:
            return None
        
        try:
            # Récupérer les informations du type d'abonnement
            cursor.execute("SELECT * FROM Type_Decodage WHERE ID_td = %s", (type_id,))
            type_data = cursor.fetchone()
            
            if not type_data:
                return None
            
            validite = type_data[3]  # validite en jours
            date_debut = datetime.now().date()
            date_fin = date_debut + timedelta(days=validite)
            
            # Créer l'abonnement
            cursor.execute("""
                INSERT INTO Abonnement (id_utilisateur, ID_td, date_debut, date_fin, statut)
                VALUES (%s, %s, %s, %s, 'actif')
            """, (user_id, type_id, date_debut, date_fin))
            
            abonnement_id = cursor.lastrowid
            
            # Créer l'encaissement
            cursor.execute("""
                INSERT INTO Encaissement (id_utilisateur, ID_ab, date_e, montant_a_payer, montant_paye)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, abonnement_id, datetime.now(), montant, montant))
            
            cursor.connection.commit()
            
            # Récupérer l'abonnement créé
            return SubscriptionManager.get_subscription_by_id(abonnement_id)
            
        except Exception as e:
            print(f"Erreur lors de la création de l'abonnement: {e}")
            cursor.connection.rollback()
            return None
    
    @staticmethod
    def get_subscription_by_id(abonnement_id: int) -> Optional[Subscription]:
        """Récupère un abonnement par son ID"""
        cursor = get_mysql_cursor()
        if not cursor:
            return None
        
        try:
            cursor.execute("""
                SELECT ab.*, td.libelle 
                FROM Abonnement ab
                JOIN Type_Decodage td ON ab.ID_td = td.ID_td
                WHERE ab.ID_ab = %s
            """, (abonnement_id,))
            
            subscription_data = cursor.fetchone()
            return Subscription.from_dict(subscription_data) if subscription_data else None
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'abonnement: {e}")
            return None
    
    @staticmethod
    def get_user_subscriptions(user_id: int) -> List[Subscription]:
        """Récupère tous les abonnements d'un utilisateur"""
        cursor = get_mysql_cursor()
        if not cursor:
            return []
        
        try:
            cursor.execute("""
                SELECT ab.*, td.libelle 
                FROM Abonnement ab
                JOIN Type_Decodage td ON ab.ID_td = td.ID_td
                WHERE ab.id_utilisateur = %s 
                ORDER BY ab.date_debut DESC
            """, (user_id,))
            
            subscriptions_data = cursor.fetchall()
            return [Subscription.from_dict(sub_data) for sub_data in subscriptions_data]
            
        except Exception as e:
            print(f"Erreur lors de la récupération des abonnements: {e}")
            return []
    
    @staticmethod
    def get_subscription_types() -> List[Dict]:
        """Récupère tous les types d'abonnements disponibles"""
        cursor = get_mysql_cursor()
        if not cursor:
            return []
        
        try:
            cursor.execute("SELECT * FROM Type_Decodage ORDER BY cout ASC")
            types_data = cursor.fetchall()
            
            return [
                {
                    'ID_td': row['ID_td'],
                    'libelle': row['libelle'],
                    'cout': row['cout'],
                    'validite': row['validite'],
                    'quota_max': row['quota_max']
                }
                for row in types_data
            ]
            
        except Exception as e:
            print(f"Erreur lors de la récupération des types d'abonnement: {e}")
            return []
    
    @staticmethod
    def check_quota(user_id: int) -> Dict:
        """Vérifie le quota d'un utilisateur"""
        subscription = SubscriptionManager.get_active_subscription(user_id)
        if not subscription:
            return {'has_quota': False, 'used': 0, 'max': 0, 'remaining': 0}
        
        cursor = get_mysql_cursor()
        if not cursor:
            return {'has_quota': False, 'used': 0, 'max': 0, 'remaining': 0}
        
        try:
            # Récupérer le quota max du type d'abonnement
            cursor.execute("SELECT quota_max FROM Type_Decodage WHERE ID_td = %s", (subscription.id_type,))
            type_data = cursor.fetchone()
            
            if not type_data or not type_data['quota_max']:
                return {'has_quota': False, 'used': 0, 'max': 0, 'remaining': 0}
            
            quota_max = type_data['quota_max']
            
            # Compter les décodages utilisés
            cursor.execute("""
                SELECT COUNT(*) as used FROM Decodeur
                WHERE id_utilisateur = %s AND horodatage_execution BETWEEN %s AND %s
            """, (user_id, subscription.date_debut, subscription.date_fin))
            
            used_data = cursor.fetchone()
            used = used_data['used'] if used_data else 0
            
            remaining = max(0, quota_max - used)
            
            return {
                'has_quota': True,
                'used': used,
                'max': quota_max,
                'remaining': remaining,
                'percentage': int((used / quota_max) * 100) if quota_max > 0 else 0
            }
            
        except Exception as e:
            print(f"Erreur lors de la vérification du quota: {e}")
            return {'has_quota': False, 'used': 0, 'max': 0, 'remaining': 0} 