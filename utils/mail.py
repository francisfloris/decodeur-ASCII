"""
Module de gestion des emails
"""

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import url_for
import os
from dotenv import load_dotenv
from typing import Optional
import config

class MailManager:
    """Gestionnaire des emails"""
    
    def __init__(self, app):
        self.app = app
        self.mail = None
        self.serializer = None
        self._init_mail(app)
    
    def _init_mail(self, app):
        """Initialise la configuration email"""
        load_dotenv()
        
        # Utiliser les variables d'environnement ou config.py en fallback
        mail_username = os.getenv("MAIL_USERNAME") or getattr(config, 'MAIL_USERNAME', None)
        mail_password = os.getenv("MAIL_PASSWORD") or getattr(config, 'MAIL_PASSWORD', None)
        
        app.config.update(
            MAIL_SERVER='smtp.gmail.com',
            MAIL_PORT=587,
            MAIL_USE_TLS=True,
            MAIL_USERNAME=mail_username,
            MAIL_PASSWORD=mail_password,
            MAIL_DEFAULT_SENDER=mail_username
        )
        
        self.mail = Mail(app)
        self.serializer = URLSafeTimedSerializer(app.secret_key or 'default-secret-key-for-development')
    
    def send_reset_password_email(self, email: str) -> bool:
        """Envoie un email de réinitialisation de mot de passe"""
        if not self.mail or not self.serializer:
            return False
            
        try:
            token = self.serializer.dumps(email, salt='reset-mdp')
            reset_url = url_for('reset_token', token=token, _external=True)
            
            msg = Message(
                "Réinitialisation de mot de passe",
                recipients=[email],
                body=f"Pour réinitialiser votre mot de passe, cliquez sur ce lien : {reset_url}"
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    def send_welcome_email(self, email: str, username: str) -> bool:
        """Envoie un email de bienvenue"""
        if not self.mail:
            return False
            
        try:
            msg = Message(
                "Bienvenue sur le Décodeur MSC",
                recipients=[email],
                body=f"""
                Bonjour {username},
                
                Bienvenue sur notre plateforme de décodage MSC !
                
                Vous pouvez maintenant :
                - Télécharger vos fichiers MSC
                - Décoder vos données
                - Consulter vos résultats
                
                Merci de votre confiance.
                """
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email de bienvenue: {e}")
            return False
    
    def send_subscription_confirmation(self, email: str, subscription_type: str) -> bool:
        """Envoie un email de confirmation d'abonnement"""
        if not self.mail:
            return False
            
        try:
            msg = Message(
                "Confirmation d'abonnement",
                recipients=[email],
                body=f"""
                Votre abonnement {subscription_type} a été activé avec succès !
                
                Vous pouvez maintenant utiliser toutes les fonctionnalités de décodage.
                
                Merci pour votre confiance.
                """
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email de confirmation: {e}")
            return False

    def send_admin_promotion_email(self, email: str, username: str) -> bool:
        """Envoie un email de notification de promotion au rôle d'administrateur"""
        if not self.mail:
            return False
            
        try:
            admin_panel_url = url_for('admin.admin_panel', _external=True)
            users_management_url = url_for('admin.admin_utilisateurs', _external=True)
            
            msg = Message(
                "🎉 Promotion au rôle d'administrateur - Décodeur MSC",
                recipients=[email],
                body=f"""
                Bonjour {username},

                🎊 Félicitations ! Vous avez été promu(e) au rôle d'administrateur sur la plateforme Décodeur MSC.

                🔐 Nouvelles fonctionnalités disponibles :

                📊 Panel d'administration :
                - {admin_panel_url}
                - Statistiques globales de la plateforme
                - Vue d'ensemble des utilisateurs et décodages

                👥 Gestion des utilisateurs :
                - {users_management_url}
                - Promouvoir/rétrograder des utilisateurs
                - Supprimer des comptes
                - Gérer les rôles

                🛠️ Fonctionnalités administratives :
                - Nettoyage des données de décodage
                - Gestion des types d'abonnement
                - Surveillance des quotas
                - Maintenance de la base de données

                🔒 Sécurité et responsabilités :
                - Accès complet à toutes les données
                - Possibilité de modifier les paramètres système
                - Responsabilité de la confidentialité des données
                - Recommandation : changer régulièrement votre mot de passe

                📞 Support :
                En cas de question ou de problème, contactez l'équipe technique.

                Merci pour votre confiance et votre engagement dans notre plateforme !

                Cordialement,
                L'équipe Décodeur MSC
                """
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email de promotion admin: {e}")
            return False

    def verify_reset_token(self, token: str, max_age: int = 1800) -> Optional[str]:
        """Vérifie un token de réinitialisation"""
        if not self.serializer:
            return None
            
        try:
            return self.serializer.loads(token, salt='reset-mdp', max_age=max_age)
        except Exception:
            return None
    
    def send_contact_message(self, name: str, email: str, subject: str, message: str, company: str = None, phone: str = None, contact_preference: str = 'email') -> bool:
        """Envoie un message de contact par email"""
        if not self.mail:
            return False
            
        try:
            # Formatage du sujet
            subject_map = {
                'support': 'Support technique',
                'sales': 'Commercial',
                'partnership': 'Partenariat',
                'billing': 'Facturation',
                'other': 'Autre'
            }
            subject_text = subject_map.get(subject, 'Contact')
            
            # Formatage de la préférence de contact
            preference_text = "Par email" if contact_preference == 'email' else "Par téléphone"
            preference_icon = "📧" if contact_preference == 'email' else "📱"
            
            # Corps du message
            company_text = f"\nEntreprise: {company}" if company else ""
            phone_text = f"\nTéléphone: {phone}" if phone else ""
            email_text = f"\nEmail: {email}" if email else ""
            body = f"""
Nouveau message de contact reçu depuis le site Décodeur MSC

Nom: {name}{email_text}{phone_text}{company_text}
Sujet: {subject_text}

{preference_icon} Préférence de contact: {preference_text}

Message:
{message}

---
Ce message a été envoyé depuis le formulaire de contact du site.
            """
            
            msg = Message(
                f"[Contact] {subject_text} - {name}",
                recipients=['doryanmougs@gmail.com'],
                body=body,
                reply_to=email if email else None
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de contact: {e}")
            return False 