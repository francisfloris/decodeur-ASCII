"""
Routes d'abonnement
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import get_mysql_cursor
from models.subscription import SubscriptionManager
from utils.decorators import login_required

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/paiement', methods=['GET', 'POST'])
@login_required
def paiement():
    """Gestion des paiements et abonnements"""
    # Vérifier s'il existe déjà un abonnement actif (pour GET et POST)
    active_subscription = SubscriptionManager.get_active_subscription(session['id_utilisateur'])
    if active_subscription:
        flash("Vous avez déjà un abonnement actif.", "warning")
        return redirect(url_for('subscription.mes_abonnements'))

    if request.method == 'POST':
        type_id = int(request.form['type'])
        
        # Récupérer les infos du type d'abonnement
        subscription_types = SubscriptionManager.get_subscription_types()
        selected_type = next((t for t in subscription_types if t['ID_td'] == type_id), None)
        
        if not selected_type:
            flash("Type de décodage invalide.", "danger")
            return redirect(url_for('subscription.paiement'))
        
        # Créer l'abonnement
        subscription = SubscriptionManager.create_subscription(
            session['id_utilisateur'], 
            type_id, 
            selected_type['cout']
        )
        
        if subscription:
            flash("Abonnement activé avec succès.", "success")
            return redirect(url_for('subscription.mes_abonnements'))
        else:
            flash("Erreur lors de l'activation de l'abonnement.", "danger")
    
    # GET : charger les formules d'abonnement disponibles
    subscription_types = SubscriptionManager.get_subscription_types()
    return render_template("paiement.html", types=subscription_types)

@subscription_bp.route('/mes_abonnements')
@login_required
def mes_abonnements():
    """Afficher les abonnements de l'utilisateur"""
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))
    subscriptions = SubscriptionManager.get_user_subscriptions(session['id_utilisateur'])
    active_subscription = SubscriptionManager.get_active_subscription(session['id_utilisateur'])
    return render_template("mes_abonnements.html", abonnements=subscriptions, active_subscription=active_subscription)

@subscription_bp.route('/mes-paiements')
@login_required
def mes_paiements():
    """Liste des paiements de l'utilisateur"""
    cursor = get_mysql_cursor()
    if not cursor:
        flash("Erreur de connexion à la base de données.", "danger")
        return redirect(url_for('auth.login'))
    
    cursor.execute("SELECT * FROM Encaissement WHERE id_utilisateur = %s ORDER BY date_e DESC", 
                  (session['id_utilisateur'],))
    paiements = cursor.fetchall()
    return render_template("mes_paiements.html", paiements=paiements) 