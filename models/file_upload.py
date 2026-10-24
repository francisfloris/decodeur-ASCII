"""
Module de gestion des uploads de fichiers
"""

import os
from datetime import datetime
from typing import List, Dict, Optional
from .database import get_fns_collection

class FileUpload:
    """Classe représentant un fichier uploadé"""
    
    def __init__(self, nom_fichier: str, utilisateur: str, horodatage: datetime, total_lignes: int = 0):
        self.nom_fichier = nom_fichier
        self.utilisateur = utilisateur
        self.horodatage = horodatage
        self.total_lignes = total_lignes
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crée un fichier uploadé à partir d'un dictionnaire"""
        return cls(
            nom_fichier=data.get('nom_fichier', ''),
            utilisateur=data.get('utilisateur', ''),
            horodatage=data.get('horodatage', datetime.now()),
            total_lignes=data.get('total', 0)
        )

class FileUploadManager:
    """Gestionnaire des uploads de fichiers"""
    
    # Extensions autorisées
    ALLOWED_EXTENSIONS = {
        '.csv', '.txt', '.tsv', '.ini', '.conf', '.cfg', 
        '.py', '.sh', '.js', '.html', '.css', '.xml', '.json', '.log'
    }
    
    @staticmethod
    def is_valid_extension(filename: Optional[str]) -> bool:
        """Vérifie si l'extension du fichier est autorisée"""
        if not filename:
            return False
        return os.path.splitext(filename)[1].lower() in FileUploadManager.ALLOWED_EXTENSIONS
    
    @staticmethod
    def upload_file(file_content: bytes, filename: str, user_email: str) -> bool:
        """Upload un fichier dans MongoDB"""
        try:
            # Décoder le contenu
            content = file_content.decode('utf-8', errors='ignore')
            lines = content.splitlines()
            
            # Récupérer la collection
            collection = get_fns_collection()
            if collection is None:
                return False
            
            # Insérer chaque ligne
            try:
                for line in lines:
                    if line.strip():  # Ignorer les lignes vides
                        collection.insert_one({
                            'contenu_ligne': line,
                            'nom_fichier': filename,
                            'horodatage_insertion': datetime.utcnow(),
                            'utilisateur': user_email
                        })
                return True
            except Exception as mongo_error:
                print(f"Erreur MongoDB lors de l'insertion: {mongo_error}")
                return False
            
        except Exception as e:
            print(f"Erreur lors de l'upload du fichier: {e}")
            return False
    
    @staticmethod
    def get_uploaded_files(page: int = 1, per_page: int = 10) -> Dict:
        """Récupère la liste des fichiers uploadés avec pagination"""
        try:
            collection = get_fns_collection()
            if collection is None:
                return {'files': [], 'total_pages': 0, 'current_page': page}
            
            # Agrégation pour grouper par fichier
            pipeline = [
                {
                    "$group": {
                        "_id": {
                            "nom_fichier": "$nom_fichier",
                            "utilisateur": "$utilisateur"
                        },
                        "horodatage": {"$min": "$horodatage_insertion"},
                        "total": {"$sum": 1}
                    }
                },
                {"$sort": {"horodatage": -1}},
                {"$skip": (page - 1) * per_page},
                {"$limit": per_page}
            ]
            
            files = list(collection.aggregate(pipeline))
            
            # Compter le total pour la pagination
            total_files = len(collection.distinct("nom_fichier"))
            total_pages = (total_files + per_page - 1) // per_page
            
            return {
                'files': [FileUpload.from_dict({
                    'nom_fichier': file['_id']['nom_fichier'],
                    'utilisateur': file['_id']['utilisateur'],
                    'horodatage': file['horodatage'],
                    'total': file['total']
                }) for file in files],
                'total_pages': total_pages,
                'current_page': page
            }
            
        except Exception as e:
            print(f"Erreur MongoDB lors de la récupération des fichiers: {e}")
            return {'files': [], 'total_pages': 0, 'current_page': page}
    
    @staticmethod
    def get_file_content(filename: str) -> List[Dict]:
        """Récupère le contenu d'un fichier"""
        collection = get_fns_collection()
        if collection is None:
            return []
        
        try:
            lines = collection.find({"nom_fichier": filename}).sort("horodatage_insertion", 1)
            return list(lines)
        except Exception as e:
            print(f"Erreur lors de la récupération du contenu: {e}")
            return []
    
    @staticmethod
    def delete_file(filename: str) -> bool:
        """Supprime un fichier et toutes ses lignes"""
        collection = get_fns_collection()
        if collection is None:
            return False
        
        try:
            result = collection.delete_many({"nom_fichier": filename})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier: {e}")
            return False
    
    @staticmethod
    def search_raw_lines(filename_filter: str = '', date_debut: str = '', 
                        date_fin: str = '', page: int = 1, per_page: int = 20) -> Dict:
        """Recherche dans les lignes brutes avec filtres"""
        collection = get_fns_collection()
        if collection is None:
            return {'lines': [], 'total': 0, 'current_page': page}
        
        try:
            # Construire le filtre
            filter_query = {}
            
            if filename_filter:
                filter_query['nom_fichier'] = {'$regex': filename_filter, '$options': 'i'}
            
            if date_debut or date_fin:
                filter_query['horodatage_insertion'] = {}
                if date_debut:
                    filter_query['horodatage_insertion']['$gte'] = datetime.strptime(date_debut, "%Y-%m-%d")
                if date_fin:
                    filter_query['horodatage_insertion']['$lte'] = datetime.strptime(date_fin, "%Y-%m-%d")
            
            # Compter le total
            total = collection.count_documents(filter_query)
            
            # Récupérer les lignes paginées
            lines = list(collection.find(filter_query)
                        .sort("horodatage_insertion", -1)
                        .skip((page - 1) * per_page)
                        .limit(per_page))
            
            return {
                'lines': lines,
                'total': total,
                'current_page': page,
                'total_pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return {'lines': [], 'total': 0, 'current_page': page}
    
    @staticmethod
    def clear_all_raw_lines() -> bool:
        """Supprime toutes les lignes brutes (admin seulement)"""
        collection = get_fns_collection()
        if collection is None:
            return False
        
        try:
            result = collection.delete_many({})
            return True
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")
            return False
    
    @staticmethod
    def export_file_content(filename: str) -> str:
        """Exporte le contenu d'un fichier en texte"""
        lines = FileUploadManager.get_file_content(filename)
        return "\n".join([line['contenu_ligne'] for line in lines]) 