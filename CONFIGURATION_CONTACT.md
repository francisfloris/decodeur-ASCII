# Configuration du système de contact

## 📧 Configuration Email

L'email est déjà configuré dans `config.py` avec votre adresse `doryanmougs@gmail.com`. Les messages de contact seront automatiquement envoyés à cette adresse.

## 📱 Configuration WhatsApp (Twilio)

Pour recevoir les messages de contact sur votre WhatsApp (+242069295481), vous devez configurer Twilio :

### Étapes de configuration :

1. **Créer un compte Twilio**
   - Allez sur https://www.twilio.com
   - Créez un compte gratuit (compte d'essai disponible)
   - Vérifiez votre numéro de téléphone

2. **Obtenir vos identifiants**
   - Dans le dashboard Twilio, récupérez :
     - `Account SID`
     - `Auth Token`

3. **Activer WhatsApp Sandbox**
   - Dans la console Twilio, allez dans "Messaging" > "Try it out" > "Send a WhatsApp message"
   - Suivez les instructions pour activer le WhatsApp Sandbox
   - Le numéro Twilio par défaut est `+14155238886`

4. **Ajouter votre numéro WhatsApp**
   - Dans le WhatsApp Sandbox, ajoutez votre numéro : `+242069295481`
   - Envoyez le code de vérification depuis WhatsApp au numéro Twilio

5. **Configurer les variables d'environnement**
   
   Créez un fichier `.env` à la racine du projet avec :
   ```
   TWILIO_ACCOUNT_SID=votre_account_sid_ici
   TWILIO_AUTH_TOKEN=votre_auth_token_ici
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   WHATSAPP_TO=+242069295481
   ```

### Alternative : Configuration directe dans le code

Si vous préférez ne pas utiliser un fichier `.env`, vous pouvez modifier directement `utils/whatsapp.py` et remplacer les lignes :
```python
self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
```

Par :
```python
self.account_sid = "votre_account_sid_ici"
self.auth_token = "votre_auth_token_ici"
```

### Installation de Twilio

Installez la bibliothèque Twilio :
```bash
pip install twilio
```

Ou installez toutes les dépendances :
```bash
pip install -r requirements.txt
```

## ⚠️ Note importante

- **Email** : Fonctionne immédiatement avec la configuration actuelle
- **WhatsApp** : Nécessite la configuration Twilio pour fonctionner. Si Twilio n'est pas configuré, seul l'email sera envoyé.
- Les messages sont envoyés aux deux canaux (email et WhatsApp) si les deux sont configurés.

## 🧪 Test

Pour tester le système :
1. Allez sur la page `/contact`
2. Remplissez le formulaire
3. Vérifiez votre boîte email (doryanmougs@gmail.com)
4. Vérifiez votre WhatsApp (+242069295481) si Twilio est configuré

