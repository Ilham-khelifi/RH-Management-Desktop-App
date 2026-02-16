import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette

# AJOUT: Import des contrôleurs
from Controllers.user_controller import UserController
from Controllers.history_controller import HistoryController


class DeleteAccountDialog(QMainWindow):
    def __init__(self, parent=None, account_data=None, 
                 user_controller=None, history_controller=None, current_user_data=None):
        super().__init__(parent)
        self.parent = parent
        self.account_data = account_data
        
        # AJOUT: Contrôleurs de base de données
        self.user_controller = user_controller
        self.history_controller = history_controller
        self.current_user_data = current_user_data or {}
        
        # Si les contrôleurs ne sont pas fournis, essayer de les récupérer du parent
        if not self.user_controller and parent and hasattr(parent, 'user_controller'):
            self.user_controller = parent.user_controller
        if not self.history_controller and parent and hasattr(parent, 'history_controller'):
            self.history_controller = parent.history_controller
        if not self.current_user_data and parent and hasattr(parent, 'current_user_data'):
            self.current_user_data = parent.current_user_data

        # Set window properties
        self.setWindowTitle("حذف حساب")
        self.setMinimumSize(400, 200)

        # Set dark background color
        self.setStyleSheet("background-color: #26282b;")

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 40)

        # Create header label
        header_label = QLabel("حذف حساب")
        header_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        header_label.setAlignment(Qt.AlignLeading)
        main_layout.addWidget(header_label)
        main_layout.addSpacing(20)

        

        # Create confirmation message
        confirmation_message = QLabel("هل أنت متأكد أنك تريد حذف هذا الحساب ؟")
        confirmation_message.setStyleSheet("color: white ; font-size: 16px bold;")
        confirmation_message.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(confirmation_message)

        # Add account details if available
        if self.account_data:
            account_details = QLabel(f"اسم المستخدم: {self.account_data.get('username', '')}\n"
                                    f"البريد الإلكتروني: {self.account_data.get('email', '')}")
            account_details.setStyleSheet("color: #e0e0e0 bold; font-size: 16px bold; margin-top: 15px;")
            account_details.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(account_details)

       

        # Create buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        # Create delete button
        delete_button = QPushButton("احذف")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: "#4CAF50";
                color: white; 
                border: none; 
                border-radius: 5px; 
                padding: 15px;
                font-size: 15px;
                font-weight: bold;
                min-width: 120px;
            }
        
        """)
        delete_button.clicked.connect(self.delete_account)

        # Create cancel button
        cancel_button = QPushButton("إلغاء")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: "#f44336"; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                padding: 15px;
                font-size: 15px;
                font-weight: bold;
                min-width: 120px;
            }

        """)
        cancel_button.clicked.connect(self.close)

        # Add buttons to layout (in reverse order for RTL)
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.setAlignment(Qt.AlignCenter)

        main_layout.addLayout(buttons_layout)

        # Set layout direction to RTL for Arabic
        self.setLayoutDirection(Qt.RightToLeft)

    def delete_account(self):
        """Delete the account using database controller and log the action"""
        if not self.account_data:
            QMessageBox.warning(self, "خطأ", "لم يتم تحديد حساب للحذف")
            self.close()
            return
            
        # Confirm deletion
        confirmation = QMessageBox.question(
            self,
            "تأكيد الحذف",
            f"هل أنت متأكد من حذف حساب {self.account_data.get('username', '')}؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirmation == QMessageBox.Yes:
            # CORRECTION: Utiliser le contrôleur de base de données directement SANS dupliquer l'historique
            if self.user_controller:
                try:
                    account_number = self.account_data.get('account_number')
                    username = self.account_data.get('username', '')
                    
                    # Delete the account using database controller
                    success, message = self.user_controller.delete_user(account_number)
                    
                    if success:
                        # SUPPRIMÉ: L'enregistrement de l'historique se fait déjà dans le contrôleur
                        
                        # Refresh parent table if available
                        if self.parent and hasattr(self.parent, 'load_data_from_database'):
                            self.parent.load_data_from_database()
                        
                        QMessageBox.information(self, "نجاح", "تم حذف الحساب بنجاح")
                        self.close()
                    else:
                        QMessageBox.warning(self, "خطأ", f"فشل حذف الحساب: {message}")
                        
                except Exception as e:
                    QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حذف الحساب: {str(e)}")
            else:
                # Fallback to parent method if controller not available
                if self.parent and hasattr(self.parent, 'delete_account'):
                    success = self.parent.delete_account(self.account_data)
                    
                    if success:
                        QMessageBox.information(self, "نجاح", "تم حذف الحساب بنجاح")
                        self.close()
                    else:
                        QMessageBox.warning(self, "خطأ", "فشل حذف الحساب")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Arial", 10)
    app.setFont(font)
  
    window = DeleteAccountDialog()
    window.show()
    sys.exit(app.exec_())
