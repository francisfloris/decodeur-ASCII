"""
Routes de gestion des fichiers
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
import io
from models.file_upload import FileUploadManager
from utils.decorators import login_required, abonnement_requis, admin_required

files_bp = Blueprint('files', __name__)

@files_bp.route('/upload', methods=['GET', 'POST'])
@abonnement_requis
def upload():
    """Upload de fichiers"""
    if request.method == 'POST':
        fichier = request.files.get('fichier')
        
        if not fichier or fichier.filename == '':
            flash("Aucun fichier sélectionné.", "danger")
            return redirect(url_for('files.upload'))
        
        filename = fichier.filename or ''
        if not FileUploadManager.is_valid_extension(filename):
            flash("Extension de fichier non autorisée.", "danger")
            return redirect(url_for('files.upload'))
        
        # Upload du fichier
        if FileUploadManager.upload_file(fichier.read(), filename, session['email']):
            flash(f"Fichier '{filename}' téléversé avec succès.", "success")
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Erreur lors du traitement du fichier.", "danger")
    
    return render_template("upload.html")

@files_bp.route('/list')
@login_required
def fichiers():
    """Liste des fichiers uploadés"""
    page = int(request.args.get('page', 1))
    result = FileUploadManager.get_uploaded_files(page, 10)
    return render_template("fichiers.html", 
                         fichiers=result['files'], 
                         page=result['current_page'], 
                         total_pages=result['total_pages'])

@files_bp.route('/<nom_fichier>/voir')
@login_required
def voir_fichier(nom_fichier):
    """Voir le contenu d'un fichier"""
    lignes = FileUploadManager.get_file_content(nom_fichier)
    return render_template("voir_fichier.html", lignes=lignes, nom_fichier=nom_fichier)

@files_bp.route('/<nom_fichier>/telecharger')
@login_required
def telecharger_fichier(nom_fichier):
    """Télécharger un fichier"""
    contenu = FileUploadManager.export_file_content(nom_fichier)
    return send_file(
        io.BytesIO(contenu.encode('utf-8')),
        mimetype='text/plain',
        download_name=f"{nom_fichier}_export.txt",
        as_attachment=True
    )

@files_bp.route('/<nom_fichier>/supprimer', methods=['POST'])
@login_required
def supprimer_fichier(nom_fichier):
    """Supprimer un fichier"""
    if FileUploadManager.delete_file(nom_fichier):
        flash(f"Fichier '{nom_fichier}' supprimé.", "success")
    else:
        flash("Erreur lors de la suppression.", "danger")
    return redirect(url_for('files.fichiers'))

@files_bp.route('/raw')
@login_required
def raw():
    """Affichage des lignes brutes avec filtres"""
    nom_fichier = request.args.get('nom_fichier', '').strip()
    date_debut = request.args.get('date_debut', '')
    date_fin = request.args.get('date_fin', '')
    page = int(request.args.get('page', 1))
    
    result = FileUploadManager.search_raw_lines(nom_fichier, date_debut, date_fin, page, 20)
    
    return render_template("raw.html", 
                         lignes=result['lines'], 
                         page=result['current_page'], 
                         total=result['total'], 
                         par_page=20,
                         nom_fichier=nom_fichier, 
                         date_debut=date_debut, 
                         date_fin=date_fin)

@files_bp.route('/clear_raw')
@admin_required
def clear_raw_lines():
    """Supprimer toutes les lignes brutes (admin)"""
    if FileUploadManager.clear_all_raw_lines():
        flash("Toutes les lignes brutes ont été supprimées.", "success")
    else:
        flash("Erreur lors du nettoyage.", "danger")
    return redirect(url_for('files.raw'))

@files_bp.route('/decode')
@abonnement_requis
def decode():
    """Lancer le décodage"""
    from models.decoder import DecoderManager
    
    if DecoderManager.decode_msc_lines(session['id_utilisateur']):
        flash("Décodage lancé avec succès.", "success")
    else:
        flash("Erreur lors du lancement du décodage.", "danger")
    
    return redirect(url_for('dashboard.dashboard'))

@files_bp.route('/decodeurs')
@login_required
def decodeurs():
    """Historique des décodages"""
    from models.decoder import DecoderManager
    
    decodeurs = DecoderManager.get_decoder_history()
    
    return render_template("decodeurs.html", 
                         decodeurs=decodeurs) 