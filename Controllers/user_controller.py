from sqlalchemy.exc import IntegrityError
from Models import User, History
import re
from datetime import datetime
from Controllers.history_controller import HistoryController

class UserController:
    """
    Contrôleur pour gérer les opérations CRUD sur les utilisateurs
    """
    def __init__(self, session, current_user_account_number=None):
        """
        Initialise le contrôleur avec une session SQLAlchemy
        
        Args:
            session: Session SQLAlchemy active
            current_user_account_number: Numéro de compte de l'utilisateur actuellement connecté (pour l'historique)
        """
        self.session = session
        self.current_user_account_number = current_user_account_number
        self.history_controller = None
    
    def set_history_controller(self, history_controller):
        """Définit le contrôleur d'historique (injection de dépendance)"""
        self.history_controller = history_controller
    
    def get_all_users(self):
        """Récupère tous les utilisateurs de la base de données"""
        users = self.session.query(User).all()
        return [user.to_dict() for user in users]
    
    def get_user_by_id(self, user_id):
        """Récupère un utilisateur par son ID"""
        user = self.session.query(User).filter(User.id == user_id).first()
        return user.to_dict() if user else None
    
    def get_user_by_account_number(self, account_number):
        """Récupère un utilisateur par son numéro de compte"""
        user = self.session.query(User).filter(User.account_number == account_number).first()
        return user.to_dict() if user else None
    
    def get_user_by_username(self, username):
        """Récupère un utilisateur par son nom d'utilisateur"""
        user = self.session.query(User).filter(User.username == username).first()
        return user.to_dict() if user else None
    
    def is_username_unique(self, username, original_username=None):
        """Vérifie si le nom d'utilisateur est unique"""
        if original_username and username == original_username:
            return True
            
        user = self.session.query(User).filter(User.username == username).first()
        return user is None
    
    def get_next_account_number(self):
        """Obtient le prochain numéro de compte disponible"""
        max_account = self.session.query(User).order_by(User.account_number.desc()).first()
        return (max_account.account_number + 1) if max_account else 1
    
    def add_user(self, user_data):
        """
        Ajoute un nouvel utilisateur
        
        Args:
            user_data: Dictionnaire contenant les données de l'utilisateur
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Validation des données
            if not self.is_username_unique(user_data['username']):
                return False, "اسم المستخدم موجود بالفعل"
                
            if not User.validate_email(user_data['email']):
                return False, "البريد الإلكتروني يجب أن يكون بتنسيق xxx@gmail.com"
                
            is_valid_password, password_error = User.validate_password(user_data['password'])
            if not is_valid_password:
                return False, password_error
            
            # Création du nouvel utilisateur
            new_user = User(
                account_number=user_data.get('account_number', self.get_next_account_number()),
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],  # Dans un système réel, il faudrait hacher le mot de passe
                role=user_data['role'],
                creation_date=datetime.strptime(user_data['creation_date'], '%Y-%m-%d') 
                    if 'creation_date' in user_data else datetime.now()
            )
            
            self.session.add(new_user)
            self.session.commit()
            
            # Enregistrement dans l'historique seulement si current_user_account_number est défini
            if self.current_user_account_number and self.history_controller:
                self.history_controller.add_history_entry(
                    self.current_user_account_number,
                    "إضافة حساب",
                    f"تم إضافة حساب جديد: {new_user.username}",
                    "ادرة الحسابات"
                )
            else:
                print("DEBUG - Pas d'enregistrement d'historique: utilisateur ou contrôleur manquant")
                
            return True, "تم إضافة الحساب بنجاح"
            
        except IntegrityError:
            self.session.rollback()
            return False, "خطأ في قاعدة البيانات: قد يكون البريد الإلكتروني أو رقم الحساب موجودًا بالفعل"
            
        except Exception as e:
            self.session.rollback()
            print(f"Erreur dans add_user: {e}")
            return False, f"خطأ غير متوقع: {str(e)}"
    
    def update_user(self, account_number, user_data):
        """
        Met à jour un utilisateur existant
        
        Args:
            account_number: Numéro de compte de l'utilisateur à mettre à jour
            user_data: Dictionnaire contenant les nouvelles données
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Récupération de l'utilisateur
            user = self.session.query(User).filter(User.account_number == account_number).first()
            if not user:
                return False, "لم يتم العثور على الحساب"
            
            # Validation des données
            if not self.is_username_unique(user_data['username'], user.username):
                return False, "اسم المستخدم موجود بالفعل"
                
            if not User.validate_email(user_data['email']):
                return False, "البريد الإلكتروني يجب أن يكون بتنسيق xxx@gmail.com"
            
            # Vérification du mot de passe uniquement s'il a été modifié
            if user_data['password'] != user.password:
                is_valid_password, password_error = User.validate_password(user_data['password'])
                if not is_valid_password:
                    return False, password_error
            
            # Mise à jour des données
            user.username = user_data['username']
            user.email = user_data['email']
            user.password = user_data['password']  # Dans un système réel, il faudrait hacher le mot de passe
            user.role = user_data['role']
            
            self.session.commit()
            
            # Enregistrement dans l'historique
            if self.current_user_account_number and self.history_controller:
                self.history_controller.add_history_entry(
                    self.current_user_account_number,
                    "تعديل حساب",
                    f"تم تعديل حساب: {user.username}",
                    "ادرة الحسابات"
                )
            
            return True, "تم تحديث الحساب بنجاح"
            
        except IntegrityError:
            self.session.rollback()
            return False, "خطأ في قاعدة البيانات: قد يكون البريد الإلكتروني موجودًا بالفعل"
            
        except Exception as e:
            self.session.rollback()
            return False, f"خطأ غير متوقع: {str(e)}"
    
    def delete_user(self, account_number):
        """
        Supprime un utilisateur
        
        Args:
            account_number: Numéro de compte de l'utilisateur à supprimer
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Récupération de l'utilisateur
            user = self.session.query(User).filter(User.account_number == account_number).first()
            if not user:
                return False, "لم يتم العثور على الحساب"
            
            username = user.username
            
            # Enregistrement dans l'historique AVANT la suppression
            if self.current_user_account_number and self.history_controller:
                self.history_controller.add_history_entry(
                    self.current_user_account_number,
                    "حذف حساب",
                    f"تم حذف حساب: {username}",
                    "ادرة الحسابات"
                )

            # Suppression de l'utilisateur
            self.session.delete(user)
            self.session.commit()
            
            return True, "تم حذف الحساب بنجاح"
            
        except Exception as e:
            self.session.rollback()
            return False, f"خطأ غير متوقع: {str(e)}"
