"""
Routes d'administration
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import get_mysql_cursor, get_fns_collection
from models.user import UserManager
from utils.decorators import admin_required
from utils.mail import MailManager

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@admin_required
def admin_panel():
    """Panel d'administration"""
    cursor = get_mysql_cursor()
    if not cursor:
        flash("Erreur de connexion à la base de données.", "danger")
        return redirect(url_for('auth.login'))
    
    # Statistiques
    cursor.execute("SELECT COUNT(*) AS total FROM utilisateur")
    total_users = cursor.fetchone()['total']
    
    cursor.execute("SELECT SUM(montant_paye) AS total FROM Encaissement")
    result = cursor.fetchone()
    total_paiements = result['total'] if result['total'] is not None else 0
    
    cursor.execute("SELECT COUNT(*) AS total FROM Decodeur")
    total_decodeurs = cursor.fetchone()['total']
    
    # Récupérer le nombre de fichiers depuis MongoDB (si disponible)
    total_fichiers = 0
    try:
        collection = get_fns_collection()
        if collection is not None:
            total_fichiers = collection.count_documents({})
    except Exception as e:
        print(f"MongoDB non disponible pour le comptage des fichiers: {e}")
        total_fichiers = 0
    
    return render_template("admin_panel.html",
                         total_users=total_users,
                         total_paiements=total_paiements,
                         total_fichiers=total_fichiers,
                         total_decodeurs=total_decodeurs)

@admin_bp.route('/utilisateurs')
@admin_required
def admin_utilisateurs():
    """Gestion des utilisateurs (admin)"""
    search = request.args.get('search', '').strip()
    users = UserManager.get_all_users(search)
    
    # Create a dummy pagination object to avoid template errors
    class DummyPagination:
        def __init__(self):
            self.pages = 1
            self.has_prev = False
            self.has_next = False
            self.prev_num = None
            self.next_num = None
            self.page = 1
        
        def iter_pages(self):
            return []
    
    pagination = DummyPagination()
    
    return render_template("admin_utilisateurs.html", users=users, pagination=pagination)

@admin_bp.route('/modifier_utilisateur/<int:id_utilisateur>', methods=['GET', 'POST'])
@admin_required
def modifier_utilisateur(id_utilisateur):
    """Modifier un utilisateur (admin)"""
    cursor = get_mysql_cursor()
    if not cursor:
        flash("Erreur de connexion à la base de données.", "danger")
        return redirect(url_for('admin.admin_utilisateurs'))
    
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'user')
        nouveau_mot_de_passe = request.form.get('nouveau_mot_de_passe', '').strip()
        
        if not nom or not email:
            flash("Le nom et l'email sont obligatoires", "danger")
            return redirect(url_for('admin.modifier_utilisateur', id_utilisateur=id_utilisateur))
        
        # Empêcher la modification de son propre rôle en admin
        if id_utilisateur == session.get('id_utilisateur') and role != 'admin':
            flash("Vous ne pouvez pas retirer vos propres privilèges d'administrateur", "danger")
            return redirect(url_for('admin.modifier_utilisateur', id_utilisateur=id_utilisateur))
        
        # Utiliser la méthode du modèle pour la mise à jour
        if UserManager.update_user(id_utilisateur, nom, email, role, nouveau_mot_de_passe if nouveau_mot_de_passe else None):
            flash("Utilisateur modifié avec succès", "success")
            return redirect(url_for('admin.admin_utilisateurs'))
        else:
            flash("Erreur lors de la modification", "danger")
            return redirect(url_for('admin.modifier_utilisateur', id_utilisateur=id_utilisateur))
    
    # GET: Afficher le formulaire de modification
    cursor.execute("""
        SELECT u.*, c.role 
        FROM utilisateur u
        JOIN compte c ON u.id_utilisateur = c.id_utilisateur 
        WHERE u.id_utilisateur = %s
    """, (id_utilisateur,))
    
    user_data = cursor.fetchone()
    if not user_data:
        flash("Utilisateur non trouvé", "danger")
        return redirect(url_for('admin.admin_utilisateurs'))
    
    return render_template('modifier_utilisateur.html', user=user_data)

@admin_bp.route('/supprimer_utilisateur/<int:id_utilisateur>', methods=['GET'])
@admin_required
def supprimer_utilisateur(id_utilisateur):
    """Supprimer un utilisateur (admin)"""
    # Empêcher la suppression de son propre compte
    if id_utilisateur == session.get('id_utilisateur'):
        flash("Vous ne pouvez pas supprimer votre propre compte", "danger")
        return redirect(url_for('admin.admin_utilisateurs'))
    
    # Vérifier que l'utilisateur existe
    user = UserManager.get_user_by_id(id_utilisateur)
    if not user:
        flash("Utilisateur non trouvé", "danger")
        return redirect(url_for('admin.admin_utilisateurs'))
    
    if UserManager.delete_user(id_utilisateur):
        flash("Utilisateur supprimé avec succès", "success")
    else:
        flash("Erreur lors de la suppression", "danger")
    return redirect(url_for('admin.admin_utilisateurs'))

@admin_bp.route('/promouvoir/<int:id_utilisateur>')
@admin_required
def promouvoir_admin(id_utilisateur):
    """Promouvoir un utilisateur admin (admin)"""
    if UserManager.update_user_role(id_utilisateur, 'admin'):
        # Récupérer les informations de l'utilisateur pour l'email
        cursor = get_mysql_cursor()
        if cursor:
            cursor.execute("SELECT nom, email FROM utilisateur WHERE id_utilisateur = %s", (id_utilisateur,))
            user_data = cursor.fetchone()
            
            if user_data:
                # Envoyer l'email de notification
                try:
                    from app import mail_manager_instance
                    if mail_manager_instance:
                        mail_manager_instance.send_admin_promotion_email(user_data['email'], user_data['nom'])
                except Exception as e:
                    print(f"Erreur lors de l'envoi de l'email de promotion: {e}")
                    # L'email n'est pas critique, on continue
        
        flash("Utilisateur promu au rôle d'administrateur", "success")
    else:
        flash("Erreur lors de la promotion", "danger")
    return redirect(url_for('admin.admin_utilisateurs'))

@admin_bp.route("/changer-role/<int:id_utilisateur>/<nouveau_role>")
@admin_required
def changer_role(id_utilisateur, nouveau_role):
    """Changer le rôle d'un utilisateur (admin)"""
    if nouveau_role not in ['admin', 'user']:
        flash("Rôle invalide.", "warning")
        return redirect(url_for('admin.admin_utilisateurs'))
    
    if UserManager.update_user_role(id_utilisateur, nouveau_role):
        # Si promotion en admin, envoyer un email de notification
        if nouveau_role == 'admin':
            cursor = get_mysql_cursor()
            if cursor:
                cursor.execute("SELECT nom, email FROM utilisateur WHERE id_utilisateur = %s", (id_utilisateur,))
                user_data = cursor.fetchone()
                
                if user_data:
                    try:
                        from app import mail_manager_instance
                        if mail_manager_instance:
                            mail_manager_instance.send_admin_promotion_email(user_data['email'], user_data['nom'])
                    except Exception as e:
                        print(f"Erreur lors de l'envoi de l'email de promotion: {e}")
                        # L'email n'est pas critique, on continue
        
        flash(f"Rôle mis à jour en : {nouveau_role}", "success")
    else:
        flash("Erreur lors de la mise à jour", "danger")
    return redirect(url_for('admin.admin_utilisateurs'))

@admin_bp.route('/nettoyer_type_decodage')
@admin_required
def nettoyer_type_decodage():
    """Nettoyer les doublons dans Type_Decodage (admin)"""
    cursor = get_mysql_cursor(dict_cursor=False)
    if not cursor:
        flash("Erreur de connexion à la base de données.", "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    try:
        cursor.execute("""
            DELETE FROM Type_Decodage
            WHERE ID_td NOT IN (
                SELECT * FROM (
                    SELECT MIN(ID_td)
                    FROM Type_Decodage
                    GROUP BY libelle, cout, validite
                ) AS keep_ids
            )
        """)
        cursor.connection.commit()
        flash("Nettoyage des doublons terminé ", "success")
    except Exception as e:
        cursor.connection.rollback()
        flash(f"Erreur lors du nettoyage: {e}", "danger")
    
    return redirect(url_for('dashboard.dashboard'))

@admin_bp.route('/vider-tableau', methods=['POST'])
@admin_required
def vider_tableau():
    """Vider le tableau FS_Appel (admin)"""
    cursor = get_mysql_cursor(dict_cursor=False)
    if not cursor:
        flash("Erreur de connexion à la base de données.", "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    try:
        cursor.execute("DELETE FROM FS_Appel")
        cursor.connection.commit()
        flash("Tableau vidé avec succès", "success")
    except Exception as e:
        cursor.connection.rollback()
        flash(f"Erreur lors du vidage: {e}", "danger")
    
    return redirect(url_for('dashboard.dashboard')) 