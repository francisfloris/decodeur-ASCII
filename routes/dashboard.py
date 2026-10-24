"""
Routes du dashboard
"""

from flask import Blueprint, render_template, request, session
from datetime import datetime
from models.database import get_mysql_cursor
from models.subscription import SubscriptionManager
from utils.decorators import login_required, abonnement_requis
from utils.export import ExportManager
from math import ceil

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    id_utilisateur = session['id_utilisateur']
    
    # Récupérer l'abonnement actif
    subscription = SubscriptionManager.get_active_subscription(id_utilisateur)
    quota_info = None
    nb_decodages = 0
    
    if subscription:
        # Calcul du quota utilisé
        quota_info = SubscriptionManager.check_quota(id_utilisateur)
        
        # Nombre total de décodages dans la période
        cursor = get_mysql_cursor()
        if cursor:
            cursor.execute("""
                SELECT COUNT(*) AS total FROM Decodeur
                WHERE id_utilisateur = %s AND horodatage_execution BETWEEN %s AND %s
            """, (id_utilisateur, subscription.date_debut, subscription.date_fin))
            nb_decodages = cursor.fetchone()['total']
    
    # Filtrage des données
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'appelant': request.args.get('appelant'),
        'appele': request.args.get('appele'),
        'msc': request.args.get('msc'),
        'min_duree': request.args.get('min_duree')
    }
    
    # Récupérer les données filtrées
    appels = ExportManager.export_filtered_data(filters)
    
    # Pagination
    page = int(request.args.get('page', 1))
    par_page = 10
    total = len(appels)
    total_pages = ceil(total / par_page) if total else 1
    
    # Paginer les résultats
    start_idx = (page - 1) * par_page
    end_idx = start_idx + par_page
    appels_pagines = appels[start_idx:end_idx]
    
    has_next = page < total_pages
    
    return render_template("dashboard.html",
                         email=session['email'],
                         appels=appels_pagines,
                         abonnement=subscription,
                         quota_info=quota_info,
                         nb_decodages=nb_decodages,
                         page=page,
                         total_pages=total_pages,
                         has_next=has_next)

@dashboard_bp.route('/export_csv')
@abonnement_requis
def export_csv():
    """Export des données en CSV"""
    from flask import send_file
    import io
    
    # Récupérer les filtres
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'appelant': request.args.get('appelant'),
        'appele': request.args.get('appele'),
        'msc': request.args.get('msc'),
        'min_duree': request.args.get('min_duree')
    }
    
    # Récupérer les données filtrées
    data = ExportManager.export_filtered_data(filters)
    
    # Créer le CSV
    import csv
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    csv_content = output.getvalue()
    
    return send_file(
        io.BytesIO(csv_content.encode('utf-8')),
        mimetype='text/csv',
        download_name=f'export_msc_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        as_attachment=True
    )

@dashboard_bp.route('/export_txt')
@abonnement_requis
def export_txt():
    """Export des données en TXT"""
    from flask import send_file
    import io
    
    # Récupérer les filtres
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'appelant': request.args.get('appelant'),
        'appele': request.args.get('appele'),
        'msc': request.args.get('msc'),
        'min_duree': request.args.get('min_duree')
    }
    
    # Récupérer les données filtrées
    data = ExportManager.export_filtered_data(filters)
    
    # Créer le TXT
    lines = []
    for row in data:
        line = f"{row['type_evenement']} {row['datelog']} {row['appelant']} {row['appele']} {row.get('duree', '')} {row.get('cellule_origine', '')} {row.get('cellule_destination', '')} {row.get('msc', '')}"
        lines.append(line)
    txt_content = "\n".join(lines)
    
    return send_file(
        io.BytesIO(txt_content.encode('utf-8')),
        mimetype='text/plain',
        download_name=f'export_msc_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
        as_attachment=True
    ) 