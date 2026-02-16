from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Views.login import LoginWindow
from Models import init_db
from Controllers.auth_controller import AuthController
from Controllers.history_controller import HistoryController
from Views.main import HRMSMainWindow  # Import du main
from Controllers.user_controller import UserController
from Models.init_db import init_db

class DatabaseIntegratedLoginWindow(LoginWindow):
    """
    Version de LoginWindow intégrée avec la base de données
    """
    def __init__(self):
        # Initialisation de l'interface utilisateur
        super().__init__()
        
        # Initialisation de la connexion à la base de données
        self.session = init_db('mysql+pymysql://hr:hr@localhost/HR')
        
        # Initialisation des contrôleurs
        self.auth_controller = AuthController(self.session)
        self.history_controller = HistoryController(self.session)

        # Création automatique du compte admin si aucun utilisateur n'existe
        self.user_controller = UserController(self.session)
        if not self.user_controller.get_all_users():
           admin_data = {
            'account_number': 1,
            'username': 'admin',
            'password': 'Admin@123',
            'email': 'admin@gmail.com',
            'role': 'admin',
            'creation_date': datetime.now().strftime('%Y-%m-%d')
           }
           success, msg = self.user_controller.add_user(admin_data)
           print("Création admin:", success, msg)     

    def login(self):
        """Gère la tentative de connexion avec la base de données"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        # Validation des entrées
        if not username:
            QMessageBox.warning(self, "خطأ", "الرجاء إدخال اسم المستخدم")
            return
            
        if not password:
            QMessageBox.warning(self, "خطأ", "الرجاء إدخال كلمة المرور")
            return
            
        # Authentification
        success, user_data, error_message = self.auth_controller.authenticate(username, password)
        
        if success:
            # Enregistrer la connexion réussie dans l'historique
            self.auth_controller.log_login_attempt(
                username, 
                True, 
                self.history_controller, 
                user_data['account_number']
            )
            
            # Afficher un message de succès
            QMessageBox.information(self, "نجاح", f"مرحبًا {username}! تم تسجيل الدخول بنجاح.")
            
            # Ouvrir la fenêtre principale avec la session
            self.open_main_window(user_data)
        else:
            # Enregistrer la tentative échouée dans l'historique
            self.auth_controller.log_login_attempt(
                username, 
                False, 
                self.history_controller
            )
            
            # Afficher un message d'erreur
            QMessageBox.warning(self, "خطأ", error_message or "اسم المستخدم أو كلمة المرور غير صحيحة")
    
    def open_main_window(self, user_data):
        """
        Ouvre la fenêtre principale de l'application avec la session
        """
        print(f"DEBUG - open_main_window appelé avec user_data: {user_data}")
        
        # Créer la fenêtre principale en passant la session ET les données utilisateur
        self.main_window = HRMSMainWindow(
            session=self.session,  # Passer la session ici
            current_user_data=user_data
        )
        
        # Afficher la fenêtre principale
        self.main_window.show()
        
        # Fermer la fenêtre de connexion
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configuration de l'application pour l'arabe
    font = QFont("Arial", 10)
    app.setFont(font)
    app.setLayoutDirection(Qt.RightToLeft)
    
    # Création et affichage de la fenêtre de connexion
    window = DatabaseIntegratedLoginWindow()
    window.show()
    
    sys.exit(app.exec_())