import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QComboBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor, QPalette

# AJOUT: Import des contrôleurs
from Controllers.user_controller import UserController
from Controllers.history_controller import HistoryController


class AddAccountForm(QWidget):
    def __init__(self, parent=None, edit_mode=False, account_data=None, 
                 user_controller=None, history_controller=None, current_user_data=None):
        super().__init__()
        self.parent = parent
        self.edit_mode = edit_mode
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
            
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle('إضافة حساب جديد' if not self.edit_mode else 'تعديل الحساب')
        self.setFixedSize(600, 800)

        # Set background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#263238'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Create title
        title_label = QLabel('إضافة حساب جديد' if not self.edit_mode else 'تعديل الحساب')
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setStyleSheet('color: white;')
        title_label.setAlignment(Qt.AlignLeading)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)

        # Create form container
        form_container = QWidget()
        form_container.setStyleSheet('''
            background-color: #455a64;
            border-radius: 10px;
            padding: 20px;
        ''')
        form_layout = QVBoxLayout(form_container)
       
        # Account number field
        field_layout = QVBoxLayout()
        field_layout.setSpacing(2)
        label = QLabel('رقم الحساب')
        label.setFont(QFont('Arial', 14, QFont.Bold))
        label.setStyleSheet('color: white;')
        label.setAlignment(Qt.AlignLeft)
        label.setMinimumHeight(70)
        field_layout.addWidget(label)
        
        self.account_number = QLineEdit()
        self.account_number.setObjectName('accountNumber')
        self.account_number.setFixedHeight(40)
        self.account_number.setAlignment(Qt.AlignRight)
        self.account_number.setStyleSheet('''
            background-color: #26282b;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            color: white;
            font-size: 14px;
        ''')
        self.account_number.setReadOnly(True)
        field_layout.addWidget(self.account_number)
        form_layout.addLayout(field_layout)

        # Username field with validation
        field_layout = QVBoxLayout()
        field_layout.setSpacing(2)
        label = QLabel('اسم المستخدم')
        label.setFont(QFont('Arial', 14, QFont.Bold))
        label.setStyleSheet('color: white;')
        label.setAlignment(Qt.AlignLeft)
        label.setMinimumHeight(70)
        field_layout.addWidget(label)

        self.username = QLineEdit()
        self.username.setObjectName('username')
        self.username.setFixedHeight(40)
        self.username.setAlignment(Qt.AlignRight)
        self.username.setStyleSheet('''
            background-color: #26282b;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            color: white;
            font-size: 14px;
        ''')
        self.username.setMaxLength(25)
        field_layout.addWidget(self.username)
        form_layout.addLayout(field_layout)

        # Email field with validation
        field_layout = QVBoxLayout()
        field_layout.setSpacing(2)
        label = QLabel('البريد الالكتروني')
        label.setFont(QFont('Arial', 14, QFont.Bold))
        label.setStyleSheet('color: white;')
        label.setMinimumHeight(70)
        label.setAlignment(Qt.AlignLeft)
        label.setMinimumHeight(70)
        field_layout.addWidget(label)

        self.email = QLineEdit()
        self.email.setObjectName('email')
        self.email.setFixedHeight(40)
        self.email.setAlignment(Qt.AlignRight)
        self.email.setStyleSheet('''
            background-color: #26282b;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            color: white;
            font-size: 14px;
        ''')
        field_layout.addWidget(self.email)
        form_layout.addLayout(field_layout)

        # Password field with validation
        field_layout = QVBoxLayout()
        field_layout.setSpacing(2)
        label = QLabel('كلمة السر')
        label.setFont(QFont('Arial', 14, QFont.Bold))
        label.setStyleSheet('color: white;')
        label.setAlignment(Qt.AlignLeft)
        label.setMinimumHeight(70)
        field_layout.addWidget(label)

        self.password = QLineEdit()
        self.password.setObjectName('password')
        self.password.setFixedHeight(40)
        self.password.setAlignment(Qt.AlignRight)
        self.password.setStyleSheet('''
            background-color: #26282b;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            color: white;
            font-size: 14px;
        ''')
        field_layout.addWidget(self.password)
        form_layout.addLayout(field_layout)

        # Role field as dropdown
        field_layout = QVBoxLayout()
        field_layout.setSpacing(2)
        label = QLabel('الدور')
        label.setFont(QFont('Arial', 14, QFont.Bold))
        label.setStyleSheet('color: white;')
        label.setAlignment(Qt.AlignLeft)
        label.setMinimumHeight(70)
        field_layout.addWidget(label)

        self.role = QComboBox()
        self.role.setObjectName('role')
        self.role.setFixedHeight(40)
        self.role.addItems(['admin', 'user'])
        self.role.setStyleSheet('''
            background-color: #26282b;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            color: white;
            font-size: 14px;
        ''')
        field_layout.addWidget(self.role)
        form_layout.addLayout(field_layout)

        # Creation date field (auto-filled)
        field_layout = QVBoxLayout()
        field_layout.setSpacing(2)
        label = QLabel('تاريخ الإنشاء')
        label.setFont(QFont('Arial', 14, QFont.Bold))
        label.setStyleSheet('color: white;')
        label.setAlignment(Qt.AlignLeft)
        label.setMinimumHeight(70)
        field_layout.addWidget(label)

        self.creation_date = QDateEdit()
        self.creation_date.setObjectName('creationDate')
        self.creation_date.setFixedHeight(40)
        self.creation_date.setAlignment(Qt.AlignRight)
        self.creation_date.setDate(QDate.currentDate())
        self.creation_date.setReadOnly(True)
        self.creation_date.setStyleSheet('''
            background-color: #26282b;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            color: white;
            font-size: 14px;
        ''')
        field_layout.addWidget(self.creation_date)
        form_layout.addLayout(field_layout)

        # Create buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        # Save button
        save_button = QPushButton('حفظ')
        save_button.setMinimumHeight(45)
        save_button.setStyleSheet("""
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

        # Cancel button
        cancel_button = QPushButton('إلغاء')
        cancel_button.setMinimumHeight(45)
     
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
        
        # Add buttons to layout (in the order needed for RTL)
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        # Add form container to main layout
        main_layout.addWidget(form_container)
        main_layout.addSpacing(15)
        main_layout.addLayout(buttons_layout)

        # Set layout
        self.setLayout(main_layout)

        # Connect signals
        save_button.clicked.connect(self.save_form)
        cancel_button.clicked.connect(self.close)

        # If in edit mode, populate fields with existing data
        if self.edit_mode and self.account_data:
            self.populate_form()

    def populate_form(self):
        """Populate form fields with existing account data"""
        if not self.account_data:
            return
            
        self.account_number.setText(str(self.account_data.get('account_number', '')))
        self.username.setText(self.account_data.get('username', ''))
        self.email.setText(self.account_data.get('email', ''))
        self.password.setText(self.account_data.get('password', ''))
        
        # Set role
        role_index = 0  # Default to admin
        if self.account_data.get('role') == 'user':
            role_index = 1
        self.role.setCurrentIndex(role_index)
        
        # Set creation date if available
        if 'creation_date' in self.account_data:
            try:
                date_parts = self.account_data['creation_date'].split('-')
                if len(date_parts) == 3:
                    year, month, day = map(int, date_parts)
                    self.creation_date.setDate(QDate(year, month, day))
            except:
                self.creation_date.setDate(QDate.currentDate())

    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
        return re.match(pattern, email) is not None

    def validate_password(self, password):
        """Validate password security"""
        if len(password) < 8:
            return False, "كلمة السر يجب أن تكون 8 أحرف على الأقل"
            
        if not re.search(r'[A-Z]', password):
            return False, "كلمة السر يجب أن تحتوي على حرف كبير واحد على الأقل"
            
        if not re.search(r'[a-z]', password):
            return False, "كلمة السر يجب أن تحتوي على حرف صغير واحد على الأقل"
            
        if not re.search(r'[0-9]', password):
            return False, "كلمة السر يجب أن تحتوي على رقم واحد على الأقل"
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "كلمة السر يجب أن تحتوي على رمز خاص واحد على الأقل"
            
        return True, ""

    def check_username_unique(self, username):
        """Check if username is unique using database controller"""
        if self.user_controller:
            original_username = self.account_data.get('username') if self.edit_mode else None
            return self.user_controller.is_username_unique(username, original_username)
        return True

    def get_next_account_number(self):
        """Get the next sequential account number from database"""
        if self.user_controller:
            return self.user_controller.get_next_account_number()
        return 1

    def save_form(self):
        # Get form data
        username = self.username.text()
        email = self.email.text()
        password = self.password.text()
        role = self.role.currentText()
        creation_date = self.creation_date.date().toString('yyyy-MM-dd')
        
        # Validate username
        if not username:
            QMessageBox.warning(self, "خطأ", "اسم المستخدم مطلوب")
            return
            
        if not self.check_username_unique(username):
            QMessageBox.warning(self, "خطأ", "اسم المستخدم موجود بالفعل")
            return
            
        # Validate email
        if not email:
            QMessageBox.warning(self, "خطأ", "البريد الإلكتروني مطلوب")
            return
            
        if not self.validate_email(email):
            QMessageBox.warning(self, "خطأ", "البريد الإلكتروني يجب أن يكون بتنسيق xxx@gmail.com")
            return
            
        # Validate password
        if not password:
            QMessageBox.warning(self, "خطأ", "كلمة السر مطلوبة")
            return
            
        is_valid, password_error = self.validate_password(password)
        if not is_valid:
            QMessageBox.warning(self, "خطأ", password_error)
            return
            
        # Get account number
        account_number = self.account_number.text()
        if not account_number and not self.edit_mode:
            account_number = str(self.get_next_account_number())
            
        # Create account data dictionary
        account_data = {
            'account_number': account_number,
            'username': username,
            'email': email,
            'password': password,
            'role': role,
            'creation_date': creation_date
        }
        
        # CORRECTION: Utiliser les contrôleurs de base de données directement SANS dupliquer l'historique
        if self.user_controller:
            try:
                if self.edit_mode:
                    # Update existing account
                    success, message = self.user_controller.update_user(account_number, account_data)
                    if success:
                        # SUPPRIMÉ: L'enregistrement de l'historique se fait déjà dans le contrôleur
                        # Refresh parent table if available
                        if self.parent and hasattr(self.parent, 'load_data_from_database'):
                            self.parent.load_data_from_database()
                        
                        QMessageBox.information(self, "نجاح", "تم تحديث الحساب بنجاح")
                        self.close()
                    else:
                        QMessageBox.warning(self, "خطأ", f"فشل تحديث الحساب: {message}")
                else:
                    # Add new account
                    success, message = self.user_controller.add_user(account_data)
                    if success:
                        # SUPPRIMÉ: L'enregistrement de l'historique se fait déjà dans le contrôleur
                        # Refresh parent table if available
                        if self.parent and hasattr(self.parent, 'load_data_from_database'):
                            self.parent.load_data_from_database()
                        
                        QMessageBox.information(self, "نجاح", "تم إضافة الحساب بنجاح")
                        self.close()
                    else:
                        QMessageBox.warning(self, "خطأ", f"فشل إضافة الحساب: {message}")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")
        else:
            # Fallback to parent methods if controllers not available
            if self.parent:
                if self.edit_mode:
                    if hasattr(self.parent, 'update_account'):
                        success = self.parent.update_account(account_data)
                        if success:
                            QMessageBox.information(self, "نجاح", "تم تحديث الحساب بنجاح")
                            self.close()
                        else:
                            QMessageBox.warning(self, "خطأ", "فشل تحديث الحساب")
                else:
                    if hasattr(self.parent, 'add_account'):
                        success = self.parent.add_account(account_data)
                        if success:
                            QMessageBox.information(self, "نجاح", "تم إضافة الحساب بنجاح")
                            self.close()
                        else:
                            QMessageBox.warning(self, "خطأ", "فشل إضافة الحساب")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    form = AddAccountForm()
    form.show()
    sys.exit(app.exec_())
