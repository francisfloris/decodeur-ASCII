"""
Application principale- Décodeur MSC
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
import config

# Import des modules
from models.database import init_mysql, init_mongo
from utils.mail import MailManager
from utils.whatsapp import WhatsAppManager

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY or 'default-secret-key-for-development'
    
    # Initialisation des bases de données
    init_mysql(app)
    init_mongo()
    
    # Initialisation du gestionnaire d'emails
    mail_manager = MailManager(app)
    # Stocker le mail_manager dans une variable globale ou utiliser un autre pattern
    global mail_manager_instance
    mail_manager_instance = mail_manager
    
    # Configuration de la session
    app.permanent_session_lifetime = timedelta(days=30)
    
    # Enregistrement des blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.dashboard import dashboard_bp
    from routes.files import files_bp
    from routes.subscription import subscription_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(subscription_bp)

    return app

# Création de l'application
app = create_app()

# Routes principales
@app.route('/')
def home():
    """Page d'accueil"""
    return render_template('accueil.html')

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    flash("Déconnecté avec succès", "info")
    return redirect(url_for('auth.login'))

# Routes du footer
@app.route('/api')
def api():
    """Documentation API"""
    return render_template('api.html')

@app.route('/documentation')
def documentation():
    """Documentation générale"""
    return render_template('documentation.html')

@app.route('/centre-aide')
def centre_aide():
    """Centre d'aide"""
    return render_template('centre_aide.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Page de contact"""
    if request.method == 'POST':
        # Récupération des données du formulaire
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        company = request.form.get('company', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        contact_preference = request.form.get('contact_preference', 'email').strip()
        
        # Validation des champs requis
        if not name or not subject or not message:
            flash("Veuillez remplir tous les champs obligatoires.", "danger")
            return render_template('contact.html')
        
        # Validation selon la préférence de contact
        if contact_preference == 'email':
            if not email:
                flash("Veuillez renseigner votre adresse email si vous souhaitez être contacté par email.", "danger")
                return render_template('contact.html')
        elif contact_preference == 'phone':
            if not phone:
                flash("Veuillez renseigner votre numéro de téléphone si vous souhaitez être contacté par téléphone.", "danger")
                return render_template('contact.html')
        
        # Envoi par email
        email_sent = False
        if mail_manager_instance:
            email_sent = mail_manager_instance.send_contact_message(
                name=name,
                email=email,
                subject=subject,
                message=message,
                company=company if company else None,
                phone=phone if phone else None,
                contact_preference=contact_preference
            )
        
        # Envoi par WhatsApp
        whatsapp_sent = False
        try:
            whatsapp_manager = WhatsAppManager()
            whatsapp_sent = whatsapp_manager.send_contact_notification(
                name=name,
                email=email,
                subject=subject,
                message=message,
                company=company if company else None,
                phone=phone if phone else None,
                contact_preference=contact_preference
            )
        except Exception as e:
            print(f"Erreur WhatsApp: {e}")
        
        if email_sent:
            flash("Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.", "success")
        elif whatsapp_sent:
            flash("Votre message a été envoyé via WhatsApp. Nous vous répondrons dans les plus brefs délais.", "success")
        else:
            flash("Une erreur est survenue lors de l'envoi. Veuillez réessayer ou nous contacter directement.", "danger")
        
        return render_template('contact.html')
    
    return render_template('contact.html')

@app.route('/statut')
def statut():
    """Statut des services"""
    return render_template('statut.html')

@app.route('/communaute')
def communaute():
    """Page communauté"""
    return render_template('communaute.html')

@app.route('/conditions-utilisation')
def conditions_utilisation():
    """Conditions d'utilisation"""
    return render_template('conditions_utilisation.html')

@app.route('/politique-confidentialite')
def politique_confidentialite():
    """Politique de confidentialité"""
    return render_template('politique_confidentialite.html')

@app.route('/cookies')
def cookies():
    """Politique des cookies"""
    return render_template('cookies.html')

@app.route('/rgpd')
def rgpd():
    """Page RGPD"""
    return render_template('rgpd.html')

# Gestionnaire d'erreurs
@app.errorhandler(403)
def access_forbidden(e):
    """Page d'erreur 403"""
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(e):
    """Page d'erreur 404"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Page d'erreur 500"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 