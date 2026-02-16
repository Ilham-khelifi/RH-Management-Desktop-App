from PyQt5.QtWidgets import QMessageBox
from datetime import datetime, timedelta
from typing import List, Optional, Dict

import csv
import os
from Models import User
from sqlalchemy import desc
from sqlalchemy import func
from Models import History, User
from datetime import datetime
from sqlalchemy import desc

class HistoryController:
    """
    Contrôleur fusionné pour gérer les opérations sur l'historique
    """
    def __init__(self, session):
        self.session = session
    
    # ========== MÉTHODES EXISTANTES (gardées telles quelles) ==========
    def get_all_history(self):
        """Récupère tout l'historique, trié par date décroissante"""
        entries = self.session.query(History).order_by(desc(History.timestamp)).all()
        return [entry.to_dict() for entry in entries]
    
    def add_history_entry(self, user_account_number, event, details, gestion="النظام"):
        """Méthode existante - LÉGÈREMENT MODIFIÉE pour supporter la gestion"""
        try:
            user = self.session.query(User).filter(User.account_number == user_account_number).first()
            if not user:
                print(f"Erreur: Utilisateur avec account_number {user_account_number} non trouvé")
                return False
            
            entry = History(
                user_id=user.id,
                event=event,
                details=details,
                gestion=gestion,  # AJOUT : Support de la gestion
                timestamp=datetime.now()
            )
            
            self.session.add(entry)
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de l'ajout dans l'historique: {str(e)}")
            return False
    
    def check_admin_access(self, user_account_number):
        """Méthode existante - gardée telle quelle"""
        try:
            user = self.session.query(User).filter(User.account_number == user_account_number).first()
            if user:
                user_data = user.to_dict()
                is_admin = user_data.get('role', '').lower() == 'admin'
                return is_admin, user_data
            else:
                return False, None
        except Exception as e:
            print(f"Erreur lors de la vérification des droits: {str(e)}")
            return False, None
    
    def get_history_with_access_control(self, user_account_number, username=None, gestion_filter=None):
        """Méthode existante - LÉGÈREMENT MODIFIÉE pour supporter le filtrage par gestion"""
        try:
            is_admin, user_data = self.check_admin_access(user_account_number)
            
            if not user_data:
                return False, None, "المستخدم غير موجود"
            
            current_username = username or user_data.get('username', 'مستخدم غير معروف')
            
            if not is_admin:
                self.add_history_entry(
                    user_account_number,
                    "محاولة وصول غير مصرح",
                    f"محاولة وصول إلى سجل الأنشطة من قبل المستخدم: {current_username}",
                    gestion="النظام"  # AJOUT : Spécifier la gestion
                )
                return False, None, "عذراً، هذه الميزة متاحة للمديرين فقط."
            
            # MODIFICATION : Déterminer les détails d'accès selon le filtre
            access_details = f"تم الوصول إلى سجل الأنشطة بنجاح من قبل المدير: {current_username}"
            access_gestion = "النظام"
            
            if gestion_filter:
                access_details += f" - مرشح حسب: {gestion_filter}"
                access_gestion = gestion_filter
            
            self.add_history_entry(
                user_account_number,
                "عرض سجل الأنشطة",
                access_details,
                gestion=access_gestion  # AJOUT : Spécifier la gestion
            )
            
            # MODIFICATION : Récupérer l'historique avec ou sans filtre de gestion
            if gestion_filter:
                history_data = self.get_history_by_gestion(gestion_filter)
            else:
                history_data = self.get_all_history()
            
            return True, history_data, "تم تحميل سجل الأنشطة بنجاح"
            
        except Exception as e:
            error_msg = f"حدث خطأ أثناء تحميل سجل الأنشطة: {str(e)}"
            return False, None, error_msg
    
    def filter_history_with_access_control(self, user_account_number, username=None, date=None, event=None, requesting_username=None, gestion_filter=None):
        """Méthode existante - LÉGÈREMENT MODIFIÉE pour supporter le filtrage par gestion"""
        try:
            is_admin, user_data = self.check_admin_access(user_account_number)
            
            if not user_data:
                return False, None, "المستخدم غير موجود"
            
            current_username = requesting_username or user_data.get('username', 'مستخدم غير معروف')
            
            if not is_admin:
                self.add_history_entry(
                    user_account_number,
                    "محاولة وصول غير مصرح",
                    f"محاولة تصفية سجل الأنشطة من قبل المستخدم: {current_username}",
                    gestion="النظام"  # AJOUT : Spécifier la gestion
                )
                return False, None, "عذراً، هذه الميزة متاحة للمديرين فقط."
            
            filtered_data = self.filter_history(username, date, event, gestion_filter)  # MODIFICATION : Ajouter gestion_filter
            
            filter_details = []
            if username:
                filter_details.append(f"اسم المستخدم: {username}")
            if date:
                filter_details.append(f"التاريخ: {date}")
            if event:
                filter_details.append(f"الحدث: {event}")
            if gestion_filter:  # AJOUT : Inclure la gestion dans les détails du filtre
                filter_details.append(f"الإدارة: {gestion_filter}")
            
            filter_text = ", ".join(filter_details) if filter_details else "بدون فلاتر"
            
            self.add_history_entry(
                user_account_number,
                "تصفية سجل الأنشطة",
                f"تم تصفية سجل الأنشطة من قبل المدير: {current_username} - المعايير: {filter_text}",
                gestion=gestion_filter if gestion_filter else "النظام"  # AJOUT : Spécifier la gestion
            )
            
            return True, filtered_data, "تم تطبيق الفلتر بنجاح"
            
        except Exception as e:
            error_msg = f"حدث خطأ أثناء تصفية سجل الأنشطة: {str(e)}"
            return False, None, error_msg
    
    def filter_history(self, username=None, date=None, event=None, gestion=None):
        """Méthode existante - LÉGÈREMENT MODIFIÉE pour supporter le filtrage par gestion"""
        query = self.session.query(History)
        
        if username:
            query = query.join(User).filter(User.username.like(f'%{username}%'))
        
        if date:
            filter_date = datetime.strptime(date, '%Y-%m-%d')
            next_day = datetime(filter_date.year, filter_date.month, filter_date.day + 1)
            query = query.filter(History.timestamp >= filter_date, History.timestamp < next_day)
        
        if event:
            query = query.filter(History.event == event)
        
        if gestion:  # AJOUT : Filtrage par gestion
            query = query.filter(History.gestion == gestion)
        
        query = query.order_by(desc(History.timestamp))
        entries = query.all()
        return [entry.to_dict() for entry in entries]
    
    # ========== NOUVELLES MÉTHODES AJOUTÉES ==========
    def add_history_entry_with_relations(self, user_account_number, event, details, gestion="النظام",
                                       employee_id=None, formation_id=None, conge_id=None,
                                       tranche_id=None, evaluation_id=None, absence_id=None):
        """
        NOUVELLE: Ajoute une entrée dans l'historique avec relations vers les entités et gestion
        """
        try:
            user = self.session.query(User).filter(User.account_number == user_account_number).first()
            if not user:
                print(f"Erreur: Utilisateur avec account_number {user_account_number} non trouvé")
                return False
            
            entry = History(
                user_id=user.id,
                event=event,
                details=details,
                gestion=gestion,  # AJOUT : Support de la gestion
                timestamp=datetime.now(),
                idemploye=employee_id,
                idFormation=formation_id,
                idConge=conge_id,
                idTranche=tranche_id,
                idEvaluation=evaluation_id,
                idAbsence=absence_id
            )
            
            self.session.add(entry)
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de l'ajout dans l'historique: {str(e)}")
            return False
    
    def get_history_by_entity(self, entity_type, entity_id):
        """
        NOUVELLE: Récupère l'historique pour une entité spécifique
        """
        query = self.session.query(History)
        
        if entity_type == 'employee':
            query = query.filter(History.idemploye == entity_id)
        elif entity_type == 'formation':
            query = query.filter(History.idFormation == entity_id)
        elif entity_type == 'conge':
            query = query.filter(History.idConge == entity_id)
        elif entity_type == 'tranche':
            query = query.filter(History.idTranche == entity_id)
        elif entity_type == 'evaluation':
            query = query.filter(History.idEvaluation == entity_id)
        elif entity_type == 'absence':
            query = query.filter(History.idAbsence == entity_id)
        
        entries = query.order_by(desc(History.timestamp)).all()
        return [entry.to_dict() for entry in entries]
    
    def get_history_by_gestion(self, gestion, limit=None):
        """
        NOUVELLE: Récupère l'historique filtré par module de gestion
        """
        query = self.session.query(History).filter(History.gestion == gestion)
        query = query.order_by(desc(History.timestamp))
        
        if limit:
            query = query.limit(limit)
        
        entries = query.all()
        return [entry.to_dict() for entry in entries]
    
    def get_gestion_statistics(self):
        """
        NOUVELLE: Récupère les statistiques par module de gestion
        """
        try:
            from sqlalchemy import func
            
            stats = self.session.query(
                History.gestion,
                func.count(History.id).label('count')
            ).group_by(History.gestion).all()
            
            return {gestion: count for gestion, count in stats}
        except Exception as e:
            print(f"Erreur lors du calcul des statistiques: {e}")
            return {}
