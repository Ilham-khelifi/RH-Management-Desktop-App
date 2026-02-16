from sqlalchemy.orm import Session
from Models import User
import re
from datetime import datetime

class AuthController:
    """
    Contrôleur pour gérer l'authentification des utilisateurs
    """
    def __init__(self, session):
        """
        Initialise le contrôleur avec une session SQLAlchemy
        
        Args:
            session: Session SQLAlchemy active
        """
        self.session = session
    
    def authenticate(self, username, password):
        """
        Authentifie un utilisateur avec son nom d'utilisateur et son mot de passe
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            
        Returns:
            Tuple (success, user_data, message)
            - success: Booléen indiquant si l'authentification a réussi
            - user_data: Dictionnaire contenant les données de l'utilisateur si l'authentification a réussi, None sinon
            - message: Message d'erreur si l'authentification a échoué, None sinon
        """
        try:
            # Vérifier si l'utilisateur existe
            user = self.session.query(User).filter(User.username == username).first()
            
            if not user:
                return False, None,  "اسم المستخدم او كلمة المرور غير صحيحة"
            
            # Vérifier le mot de passe
            # Note: Dans un système réel, vous devriez comparer des mots de passe hachés
            if user.password != password:
                return False, None,  "اسم المستخدم او كلمة المرور غير صحيحة"

            
            # Authentification réussie
            return True, user.to_dict(), None
            
        except Exception as e:
            return False, None, f"خطأ في الاتصال بقاعدة البيانات: {str(e)}"
    
    def validate_password(self, password):
        """
        Valide la sécurité du mot de passe
        
        Args:
            password: Mot de passe à valider
            
        Returns:
            Tuple (is_valid, message)
            - is_valid: Booléen indiquant si le mot de passe est valide
            - message: Message d'erreur si le mot de passe n'est pas valide, chaîne vide sinon
        """
        # Réutilisation de la méthode statique du modèle User
        return User.validate_password(password)
    
    def log_login_attempt(self, username, success, history_controller, user_id=None):
        """
        Enregistre une tentative de connexion dans l'historique
        
        Args:
            username: Nom d'utilisateur qui a tenté de se connecter
            success: Booléen indiquant si la tentative a réussi
            history_controller: Contrôleur d'historique pour enregistrer l'événement
            user_id: ID de l'utilisateur si la tentative a réussi, None sinon
            
        Returns:
            Booléen indiquant si l'enregistrement a réussi
        """
        event = "تسجيل الدخول" if success else "محاولة تسجيل دخول فاشلة"
        details = f"تم تسجيل الدخول بنجاح: {username}" if success else f"محاولة تسجيل دخول فاشلة: {username}"
        
        return history_controller.add_history_entry(user_id, event, details)