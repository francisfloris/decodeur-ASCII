"""
Module d'export de données
"""

import csv
import io
from typing import List, Dict
from models.database import get_mysql_cursor

class ExportManager:
    """Gestionnaire des exports de données"""
    
    @staticmethod
    def export_to_csv(table_name: str = 'FS_Appel') -> str:
        """Exporte les données d'une table en CSV"""
        cursor = get_mysql_cursor()
        if not cursor:
            return ""
        
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            
            if not data:
                return ""
            
            # Créer le CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            
            return output.getvalue()
            
        except Exception as e:
            print(f"Erreur lors de l'export CSV: {e}")
            return ""
    
    @staticmethod
    def export_to_txt(table_name: str = 'FS_Appel') -> str:
        """Exporte les données d'une table en texte"""
        cursor = get_mysql_cursor()
        if not cursor:
            return ""
        
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            
            if not data:
                return ""
            
            # Créer le texte
            lines = []
            for row in data:
                line = f"{row['type_evenement']} {row['datelog']} {row['appelant']} {row['appele']}"
                lines.append(line)
            
            return "\n".join(lines)
            
        except Exception as e:
            print(f"Erreur lors de l'export TXT: {e}")
            return ""
    
    @staticmethod
    def export_filtered_data(filters: Dict) -> List[Dict]:
        """Exporte des données filtrées"""
        cursor = get_mysql_cursor()
        if not cursor:
            return []
        
        try:
            # Construire la requête avec filtres
            query = "SELECT * FROM FS_Appel WHERE 1=1"
            params = []
            
            if filters.get('start_date'):
                query += " AND datelog >= %s"
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                query += " AND datelog <= %s"
                params.append(filters['end_date'] + " 23:59:59")
            
            if filters.get('appelant'):
                query += " AND appelant LIKE %s"
                params.append(f"%{filters['appelant']}%")
            
            if filters.get('appele'):
                query += " AND appele LIKE %s"
                params.append(f"%{filters['appele']}%")
            
            if filters.get('msc'):
                query += " AND msc LIKE %s"
                params.append(f"%{filters['msc']}%")
            
            if filters.get('min_duree'):
                query += " AND duree >= %s"
                params.append(int(filters['min_duree']))
            
            query += " ORDER BY date_insertion DESC"
            
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Erreur lors de l'export filtré: {e}")
            return []
    
    @staticmethod
    def get_export_stats() -> Dict:
        """Récupère les statistiques pour l'export"""
        cursor = get_mysql_cursor()
        if not cursor:
            return {}
        
        try:
            stats = {}
            
            # Total des appels
            cursor.execute("SELECT COUNT(*) as total FROM FS_Appel")
            stats['total_appels'] = cursor.fetchone()['total']
            
            # Par type d'événement
            cursor.execute("""
                SELECT type_evenement, COUNT(*) as count 
                FROM FS_Appel 
                GROUP BY type_evenement
            """)
            stats['par_type'] = {row['type_evenement']: row['count'] for row in cursor.fetchall()}
            
            # Par MSC
            cursor.execute("""
                SELECT msc, COUNT(*) as count 
                FROM FS_Appel 
                GROUP BY msc 
                ORDER BY count DESC 
                LIMIT 10
            """)
            stats['top_msc'] = {row['msc']: row['count'] for row in cursor.fetchall()}
            
            return stats
            
        except Exception as e:
            print(f"Erreur lors de la récupération des stats: {e}")
            return {} 