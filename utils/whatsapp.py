"""
Module de gestion des messages WhatsApp via Twilio
"""

import os
from typing import Optional
from dotenv import load_dotenv

class WhatsAppManager:
    """Gestionnaire des messages WhatsApp via Twilio"""
    
    def __init__(self):
        load_dotenv()
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")  # Numéro Twilio par défaut
        self.whatsapp_to = os.getenv("WHATSAPP_TO", "+242069295481")  # Votre numéro WhatsApp
        
    def send_message(self, message: str) -> bool:
        """Envoie un message WhatsApp via Twilio"""
        if not self.account_sid or not self.auth_token:
            print("Twilio n'est pas configuré. Veuillez définir TWILIO_ACCOUNT_SID et TWILIO_AUTH_TOKEN dans votre .env")
            return False
        
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            # Formatage du numéro (ajouter whatsapp: si nécessaire)
            to_number = self.whatsapp_to
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            from_number = self.whatsapp_from
            if not from_number.startswith("whatsapp:"):
                from_number = f"whatsapp:{from_number}"
            
            message_obj = client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            
            print(f"Message WhatsApp envoyé avec succès. SID: {message_obj.sid}")
            return True
            
        except ImportError:
            print("Twilio n'est pas installé. Installez-le avec: pip install twilio")
            return False
        except Exception as e:
            print(f"Erreur lors de l'envoi du message WhatsApp: {e}")
            return False
    
    def send_contact_notification(self, name: str, email: str, subject: str, message: str, company: str = None, phone: str = None, contact_preference: str = 'email') -> bool:
        """Envoie une notification de contact par WhatsApp"""
        subject_map = {
            'support': 'Support technique',
            'sales': 'Commercial',
            'partnership': 'Partenariat',
            'billing': 'Facturation',
            'other': 'Autre'
        }
        subject_text = subject_map.get(subject, 'Contact')
        
        # Formatage de la préférence de contact
        preference_text = "Par email 📧" if contact_preference == 'email' else "Par téléphone 📱"
        
        company_text = f"\n🏢 *Entreprise:* {company}" if company else ""
        phone_text = f"\n📱 *Téléphone:* {phone}" if phone else ""
        email_text = f"\n📧 *Email:* {email}" if email else ""
        
        whatsapp_message = f"""📧 *Nouveau message de contact*

👤 *Nom:* {name}{email_text}{phone_text}{company_text}
📌 *Sujet:* {subject_text}

{preference_text}

💬 *Message:*
{message}

---
Envoyé depuis le site Décodeur MSC"""
        
        return self.send_message(whatsapp_message)

