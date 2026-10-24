# -*- coding: utf-8 -*-
"""
Routes d'authentification
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
from models.user import UserManager
from utils.mail import MailManager
from utils.decorators import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion utilisateur"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember')
        
        # Vérifier si le compte est bloqué
        from models.user import UserManager
        from datetime import datetime
        cursor = None
        try:
            from models.database import get_mysql_cursor
            cursor = get_mysql_cursor()
            if cursor:
                cursor.execute("""
                    SELECT c.locked_until FROM utilisateur u JOIN compte c ON u.id_utilisateur = c.id_utilisateur WHERE u.email = %s
                """, (email,))
                row = cursor.fetchone()
                if row and row['locked_until'] and row['locked_until'] > datetime.now():
                    flash("Compte bloqué après 3 tentatives. Réessayez plus tard.", "danger")
                    return render_template("login.html")
        except Exception:
            pass
        finally:
            if cursor:
                cursor.close()

        # Validation des champs obligatoires
        if not email:
            flash("L'email est obligatoire.", "danger")
            return render_template("login.html")
        
        if not password:
            flash("Le mot de passe est obligatoire.", "danger")
            return render_template("login.html")
        
        # Vérification que le checkbox "Se souvenir de moi" est coché
        if not remember:
            flash("Vous devez accepter de vous souvenir de votre connexion.", "danger")
            return render_template("login.html")
        
        # Authentification
        user = UserManager.authenticate_user(email, password)
        if user:
            session.update({
                'loggedin': True,
                'id_utilisateur': user.id_utilisateur,
                'email': user.email,
                'role': user.role,
                'remember_me': True
            })
            
            # Si "Se souvenir de moi" est coché, étendre la durée de session
            if remember:
                session.permanent = True
            
            flash("Connexion réussie", "success")
            return redirect(url_for('dashboard.dashboard'))
        
        flash("Email ou mot de passe incorrect", "danger")
    
    return render_template("login.html")

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Inscription utilisateur"""
    if request.method == 'POST':
        nom = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas", "danger")
            return redirect(url_for('auth.signup'))
        
        # Créer l'utilisateur
        user = UserManager.create_user(nom, email, password)
        if user:
            flash("Inscription réussie. Connectez-vous", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Erreur lors de l'inscription", "danger")
    
    return render_template("signup.html")

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Demande de réinitialisation de mot de passe"""
    if request.method == 'POST':
        email = request.form['email']
        
        # Vérifier que l'utilisateur existe
        user = UserManager.get_user_by_email(email)
        if user:
            # Envoyer l'email de réinitialisation
            try:
                from app import mail_manager_instance
                if mail_manager_instance:
                    if mail_manager_instance.send_reset_password_email(email):
                        flash("Lien envoyé ✔️", "success")
                    else:
                        flash("Erreur lors de l'envoi de l'email", "danger")
                else:
                    flash("Service email non disponible", "danger")
            except Exception as e:
                print(f"Erreur lors de l'initialisation du mail manager: {e}")
                flash("Erreur lors de l'envoi de l'email", "danger")
        else:
            flash("Adresse inconnue", "danger")
    
    return render_template("reset_password.html")

@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_token(token):
    """Réinitialisation de mot de passe avec token"""
    try:
        from app import mail_manager_instance
        if not mail_manager_instance:
            flash("Service email non disponible", "danger")
            return redirect(url_for('auth.reset_password'))
        email = mail_manager_instance.verify_reset_token(token)
    except Exception as e:
        print(f"Erreur lors de l'initialisation du mail manager: {e}")
        flash("Service email non disponible", "danger")
        return redirect(url_for('auth.reset_password'))
    
    if not email:
        flash("Lien expiré ou invalide", "danger")
        return redirect(url_for('auth.reset_password'))
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash("Les mots de passe ne correspondent pas", "danger")
            return redirect(request.url)
        
        # Mettre à jour le mot de passe
        if UserManager.update_password(email, new_password):
            flash("Mot de passe mis à jour ", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Erreur lors de la mise à jour", "danger")
    
    return render_template("new_password.html", token=token)

@auth_bp.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    flash("Déconnecté avec succès", "info")
    return redirect(url_for('auth.login')) 