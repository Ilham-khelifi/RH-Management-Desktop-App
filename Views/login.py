import sys
import re
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QIcon

# Import our main application window



class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("ONEF - تسجيل الدخول")
        self.setMinimumSize(1000, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create right side (login form)
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #263238;")
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(50, 50, 50, 50)
        right_layout.setAlignment(Qt.AlignCenter)

        # Create form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # Create form title
        form_title = QLabel("تسجيل الدخول")
        form_title.setStyleSheet("""
            color: #C25B02;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        form_title.setAlignment(Qt.AlignLeft)
        form_layout.addWidget(form_title)

        # Create subtitle
        form_subtitle = QLabel("تسجيل الدخول إلى حسابك")
        form_subtitle.setStyleSheet("""
            color: #FFFFFF;
            font-size: 16px;
            margin-bottom: 30px;
        """)
        form_subtitle.setAlignment(Qt.AlignLeft)
        form_layout.addWidget(form_subtitle)

        # Username field
        username_layout = QVBoxLayout()
        username_layout.setSpacing(10)

        username_label = QLabel("اسم المستخدم")
        username_label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        username_label.setAlignment(Qt.AlignLeft)
        username_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("أدخل اسم المستخدم")
        self.username_input.setMaxLength(25)  # Limit to 25 characters
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
            }
        """)
        self.username_input.setMinimumHeight(45)
        username_layout.addWidget(self.username_input)

        form_layout.addLayout(username_layout)

        # Password field
        password_layout = QVBoxLayout()
        password_layout.setSpacing(10)

        password_label = QLabel("كلمة المرور")
        password_label.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        password_label.setAlignment(Qt.AlignLeft)
        password_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("أدخل كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
            }
        """)
        self.password_input.setMinimumHeight(45)
        password_layout.addWidget(self.password_input)

        form_layout.addLayout(password_layout)

        # Add spacing
        form_layout.addSpacing(20)

        # Login button
        login_button = QPushButton("الدخول")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #C25B02;
                color: #FFFFFF;
                border: none;
                border-radius: 25px;
                padding: 12px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #A04A00;
            }
        """)
        login_button.setMinimumHeight(50)
        login_button.clicked.connect(self.login)
        form_layout.addWidget(login_button)

        # Add form container to right layout
        right_layout.addWidget(form_container)

        # Create left side (ONEF image)
        left_widget = QLabel()
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Load the ONEF image
        onef_pixmap = QPixmap("pics/onef_bg.png")
        if not onef_pixmap.isNull():
            left_widget.setPixmap(onef_pixmap.scaled(left_widget.width(), left_widget.height(),
                                                     Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            left_widget.setScaledContents(True)
        else:
            # Fallback if image is not found
            left_widget.setStyleSheet("""
                background-color: #333333;
                color: white;
                font-size: 24px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            """)
            left_widget.setText("ONEF\nOBSERVATOIRE NATIONAL DE\nL'EDUCATION ET LA FORMATION")

        # Add widgets to main layout - IMPORTANT: In RTL mode, the order is reversed
        # So we add right_widget first, then left_widget to get left_widget on the right
        # and right_widget on the left when displayed in RTL mode
        main_layout.addWidget(right_widget)
        main_layout.addWidget(left_widget)
        # ======
        left_widget.setPixmap(onef_pixmap.scaled(left_widget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Store accounts for authentication
        self.accounts = [
            {
                'username': 'admin',
                'password': 'Admin@123',
                'role': 'admin'
            },
            {
                'username': 'user1',
                'password': 'User1@123',
                'role': 'user'
            }
        ]

    def validate_password(self, password):
        """Validate password security"""
        # Password should be at least 8 characters with at least one uppercase, one lowercase,
        # one digit and one special character
        if len(password) < 8:
            return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"

        if not re.search(r'[A-Z]', password):
            return False, "كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل"

        if not re.search(r'[a-z]', password):
            return False, "كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل"

        if not re.search(r'[0-9]', password):
            return False, "كلمة المرور يجب أن تحتوي على رقم واحد على الأقل"

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل"

        return True, ""

    def login(self):
        """Handle login attempt"""
        username = self.username_input.text()
        password = self.password_input.text()

        # Validate inputs
        if not username:
            QMessageBox.warning(self, "خطأ", "الرجاء إدخال اسم المستخدم")
            return

        if not password:
            QMessageBox.warning(self, "خطأ", "الرجاء إدخال كلمة المرور")
            return

        # Check credentials
        authenticated = False
        for account in self.accounts:
            if account['username'] == username and account['password'] == password:
                authenticated = True
                user_role = account['role']
                break

        if authenticated:
            # Show success message
            QMessageBox.information(self, "نجاح", f"مرحبًا {username}! تم تسجيل الدخول بنجاح.")

            # Open the main application window
            self.open_main_window(username, user_role)
        else:
            # Show error message
            QMessageBox.warning(self, "خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application-wide font for better Arabic text rendering
    font = QFont("Arial", 10)
    app.setFont(font)

    # Set RTL for the entire application
    app.setLayoutDirection(Qt.RightToLeft)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec_())