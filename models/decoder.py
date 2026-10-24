"""
Module de gestion du décodage MSC
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from .database import get_mysql_cursor, get_fns_collection

class Decoder:
    """Classe représentant un processus de décodage"""
    
    def __init__(self, id_decodeur: int, id_utilisateur: int, statut: str, 
                 horodatage_execution: datetime, nom_utilisateur: str = ''):
        self.id_decodeur = id_decodeur
        self.id_utilisateur = id_utilisateur
        self.statut = statut
        self.horodatage_execution = horodatage_execution
        self.nom_utilisateur = nom_utilisateur
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crée un décodeur à partir d'un dictionnaire"""
        return cls(
            id_decodeur=data.get('id_decodeur', 0),
            id_utilisateur=data.get('id_utilisateur', 0),
            statut=data.get('statut', 'en cours'),
            horodatage_execution=data.get('horodatage_execution', datetime.now()),
            nom_utilisateur=data.get('nom', '')
        )

class DecoderManager:
    """Gestionnaire du décodage MSC"""
    
    @staticmethod
    def create_decoder(user_id: int) -> Optional[Decoder]:
        """Crée un nouveau processus de décodage"""
        cursor = get_mysql_cursor(dict_cursor=False)
        if not cursor:
            return None
        
        try:
            cursor.execute("""
                INSERT INTO Decodeur (id_utilisateur, statut, horodatage_execution) 
                VALUES (%s, %s, %s)
            """, (user_id, "en cours", datetime.now()))
            
            decoder_id = cursor.lastrowid
            cursor.connection.commit()
            
            return Decoder(decoder_id, user_id, "en cours", datetime.now())
            
        except Exception as e:
            print(f"Erreur lors de la création du décodeur: {e}")
            cursor.connection.rollback()
            return None
    
    @staticmethod
    def update_decoder_status(decoder_id: int, status: str) -> bool:
        """Met à jour le statut d'un décodeur"""
        cursor = get_mysql_cursor(dict_cursor=False)
        if not cursor:
            return False
        
        try:
            cursor.execute("""
                UPDATE Decodeur 
                SET statut = %s 
                WHERE id_decodeur = %s
            """, (status, decoder_id))
            
            cursor.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour du statut: {e}")
            cursor.connection.rollback()
            return False
    
    @staticmethod
    def get_decoder_history() -> List[Decoder]:
        """Récupère l'historique des décodages"""
        cursor = get_mysql_cursor()
        if not cursor:
            return []
        
        try:
            cursor.execute("""
                SELECT d.*, u.nom 
                FROM Decodeur d 
                JOIN utilisateur u ON d.id_utilisateur = u.id_utilisateur
                ORDER BY d.horodatage_execution DESC
            """)
            
            decoders_data = cursor.fetchall()
            return [Decoder.from_dict(decoder_data) for decoder_data in decoders_data]
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'historique: {e}")
            return []
    
    @staticmethod
    def decode_msc_lines(user_id: int) -> bool:
        """Décode les lignes MSC non encore traitées"""
        # Créer un nouveau décodeur
        decoder = DecoderManager.create_decoder(user_id)
        if not decoder:
            return False
        
        try:
            # Récupérer les lignes non décodées
            collection = get_fns_collection()
            if collection is None:
                DecoderManager.update_decoder_status(decoder.id_decodeur, "erreur")
                return False
            
            try:
                undecoded_lines = list(collection.find({"id_decodeur": {"$exists": False}}))
            except Exception as mongo_error:
                print(f"Erreur MongoDB lors de la récupération des lignes: {mongo_error}")
                DecoderManager.update_decoder_status(decoder.id_decodeur, "erreur")
                return False
            
            if not undecoded_lines:
                DecoderManager.update_decoder_status(decoder.id_decodeur, "terminé")
                return True
            
            # Traiter chaque ligne
            cursor = get_mysql_cursor(dict_cursor=False)
            if not cursor:
                DecoderManager.update_decoder_status(decoder.id_decodeur, "erreur")
                return False
            
            processed_count = 0
            
            for line in undecoded_lines:
                try:
                    decoded_data = MSCParser.parse_line(line["contenu_ligne"])
                    if decoded_data:
                        # Insérer dans MySQL
                        cursor.execute("""
                            INSERT INTO FS_Appel (
                                type_evenement, datelog, appelant, appele, duree,
                                cellule_origine, cellule_destination, msc, fichier_source, date_insertion
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            decoded_data['type_evenement'],
                            decoded_data['datelog'],
                            decoded_data['appelant'],
                            decoded_data['appele'],
                            decoded_data['duree'],
                            decoded_data['cellule_origine'],
                            decoded_data['cellule_destination'],
                            decoded_data['msc'],
                            line.get('nom_fichier', 'inconnu'),
                            datetime.now()
                        ))
                        
                        # Marquer la ligne comme décodée
                        try:
                            collection.update_one(
                                {'_id': line['_id']}, 
                                {'$set': {'id_decodeur': decoder.id_decodeur}}
                            )
                        except Exception as mongo_update_error:
                            print(f"Erreur MongoDB lors de la mise à jour: {mongo_update_error}")
                            # Continuer quand même le traitement
                        
                        processed_count += 1
                        
                except Exception as e:
                    print(f"Erreur lors du décodage de la ligne: {e}")
                    continue
            
            cursor.connection.commit()
            DecoderManager.update_decoder_status(decoder.id_decodeur, "terminé")
            
            print(f"Décodage terminé: {processed_count} lignes traitées")
            return True
            
        except Exception as e:
            print(f"Erreur globale du décodeur: {e}")
            DecoderManager.update_decoder_status(decoder.id_decodeur, "erreur")
            return False

class MSCParser:
    """Parser pour les lignes MSC"""
    
    @staticmethod
    def parse_line(line_content: str) -> Optional[Dict[str, Any]]:
        """Parse une ligne MSC selon le format attendu"""
        try:
            # Nettoyer la ligne
            line_content = line_content.strip()
            if not line_content or line_content.startswith('#'):
                return None
            
            # Diviser la ligne en parties
            parts = line_content.split()
            if len(parts) < 8:
                return None
            
            # Extraire les informations
            type_evt = parts[0]
            datelog_str = parts[1]
            appelant = parts[2]
            appele = parts[3]
            duree_str = parts[4]
            origine = parts[5]
            destination = parts[6]
            msc = parts[7]
            
            # Valider le type d'événement
            if type_evt not in ['CALL', 'SMS', 'DATA']:
                return None
            
            # Parser la date
            try:
                datelog = datetime.strptime(datelog_str, "%Y%m%d%H%M")
            except ValueError:
                return None
            
            # Valider la durée
            try:
                duree = int(duree_str) if duree_str.isdigit() else None
            except ValueError:
                return None
            
            # Extraire les cellules et MSC
            try:
                origine_cell = origine.split(":")[1] if ":" in origine else origine
                dest_cell = destination.split(":")[1] if ":" in destination else destination
                msc_id = msc.split(":")[1] if ":" in msc else msc
            except IndexError:
                return None
            
            return {
                'type_evenement': type_evt,
                'datelog': datelog,
                'appelant': appelant,
                'appele': appele,
                'duree': duree,
                'cellule_origine': origine_cell,
                'cellule_destination': dest_cell,
                'msc': msc_id
            }
            
        except Exception as e:
            print(f"Erreur lors du parsing: {e}")
            return None
    
    @staticmethod
    def validate_line(line_content: str) -> bool:
        """Valide une ligne MSC"""
        return MSCParser.parse_line(line_content) is not None 