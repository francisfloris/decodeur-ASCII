"""
Module des décorateurs pour la gestion des permissions
"""

from functools import wraps
from flask import session, flash, redirect, url_for, abort
from models.database import get_mysql_cursor
from models.subscription import SubscriptionManager

def abonnement_requis(view_func):
    """Décorateur pour vérifier qu'un utilisateur a un abonnement actif"""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'loggedin' not in session:
            flash("Veuillez vous connecter.", "warning")
            return redirect(url_for('auth.login'))
        
        # Vérifier l'abonnement actif
        subscription = SubscriptionManager.get_active_subscription(session['id_utilisateur'])
        if not subscription:
            flash("Aucun abonnement actif. Merci de vous abonner.", "danger")
            return redirect(url_for('subscription.paiement'))
        
        return view_func(*args, **kwargs)
    return wrapper

def admin_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est admin"""
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'loggedin' not in session or session.get('role') != 'admin':
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped_view

def login_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est connecté"""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'loggedin' not in session:
            flash("Veuillez vous connecter.", "warning")
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapper 