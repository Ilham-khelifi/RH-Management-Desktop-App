import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QApplication,  QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QFrame
)
from PyQt5.QtGui import QPixmap,  QIcon
from PyQt5.QtCore import Qt, QSize

# Import constants (colors, theme)
from ui_constants import *

try:
    from login_integrated import DatabaseIntegratedLoginWindow
except ImportError:
    print("Erreur: Impossible d'importer LoginWindow depuis login.py")
    print("Assurez-vous que login.py est dans le même répertoire que ce script")

# 🔧 Sidebar Function Exportable with Role-Based Access Control
def create_sidebar(parent, main_layout, active_module=None, on_module_change=None, on_logout=None, current_user_data=None):
    print("Sidebar function imported and running!")
    
    # DEBUG: Afficher les données utilisateur reçues
    print(f"DEBUG - current_user_data reçu: {current_user_data}")
    
    sidebar = QWidget()
    sidebar.setFixedWidth(220)
    sidebar.setStyleSheet(f"background-color: {MEDIUM_BG}; color: {WHITE}; border: none;")

    sidebar_layout = QVBoxLayout(sidebar)
    sidebar_layout.setContentsMargins(0, 0, 0, 0)
    sidebar_layout.setSpacing(0)

    # 👤 Profile section
    profile_widget = QWidget()
    profile_layout = QVBoxLayout(profile_widget)

    avatar_label = QLabel()
    avatar_pixmap = QPixmap("pics/user_icon.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    avatar_label.setPixmap(avatar_pixmap)
    avatar_label.setAlignment(Qt.AlignCenter)
    avatar_label.setStyleSheet("border-radius: 25px; margin: 10px auto;")

    # Update user info from current_user_data avec vérifications améliorées
    username = "اسم المستخدم"
    user_role_text = "دور المستخدم"
    
    # Vérifier si current_user_data existe ET n'est pas vide
    if current_user_data and len(current_user_data) > 0:
        username = current_user_data.get('username', 'اسم المستخدم')
        user_role_text = current_user_data.get('role', 'دور المستخدم')
        print(f"DEBUG - Username: {username}, Role: {user_role_text}")
    else:
        print("DEBUG - current_user_data est None ou vide!")
    
    # Convert role to Arabic
    if user_role_text.lower() == 'admin':
        user_role_display = 'مدير'
    elif user_role_text.lower() == 'user':
        user_role_display = 'مستخدم'
    else:
        user_role_display = user_role_text

    user_name = QLabel(username)
    user_name.setObjectName("user_name")
    user_name.setAlignment(Qt.AlignCenter)
    user_name.setStyleSheet("font-weight: bold; font-size: 14px;")

    user_role = QLabel(user_role_display)
    user_role.setObjectName("user_role")
    user_role.setAlignment(Qt.AlignCenter)
    user_role.setStyleSheet("font-size: 12px; color: #d9d9d9;")

    profile_layout.addWidget(avatar_label)
    profile_layout.addWidget(user_name)
    profile_layout.addWidget(user_role)

    # ⛔ Separator
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setStyleSheet(f"background-color: {LIGHT_BG}; max-height: 1px; margin: 10px 15px;")

    # 📚 Menu items
    menu_widget = QWidget()
    menu_layout = QVBoxLayout(menu_widget)
    menu_layout.setContentsMargins(10, 20, 10, 10)
    menu_layout.setSpacing(20)

    header_layout = QHBoxLayout()
    header_icon = QLabel()
    header_pixmap = QPixmap("pics/main.png").scaled(25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    header_icon.setPixmap(header_pixmap)
    header_icon.setFixedWidth(40)
    header_label = QLabel("الوظائف الأساسية")
    header_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 12px;")

    header_layout.addWidget(header_icon)
    header_layout.addWidget(header_label)
    header_layout.addStretch()
    menu_layout.addLayout(header_layout)

    # Check if user is admin avec vérification améliorée
    is_admin = False
    if current_user_data and len(current_user_data) > 0:
        user_role_check = current_user_data.get('role', '')
        print(f"DEBUG - Role brut: '{user_role_check}'")
        print(f"DEBUG - Role en minuscules: '{user_role_check.lower()}'")
        
        # Vérifications multiples pour être sûr
        is_admin = (
            user_role_check.lower() == 'admin' or 
            user_role_check.lower() == 'administrator' or
            user_role_check == 'admin' or
            user_role_check == 'Admin' or
            user_role_check == 'ADMIN'
        )
        print(f"DEBUG - is_admin: {is_admin}")
    else:
        print("DEBUG - current_user_data est None ou vide, is_admin = False")

    # Define menu items
    menu_items = [
        {"text": "إدارة الموظفين", "icon": "pics/employee.png", "admin_only": False},
        {"text": "إدارة الإجازات", "icon": "pics/conge.png", "admin_only": False},
        {"text": "إدارة الغيابات", "icon": "pics/abs.png", "admin_only": False},
        {"text": "إدارة التقييمات", "icon": "pics/note.png", "admin_only": False},
        {"text": "إدارة التكوين", "icon": "pics/form.png", "admin_only": False},
        {"text": "صفحة الأرشيف", "icon": "pics/arch.png", "admin_only": False},
        {"text": "إدارة الحسابات", "icon": "pics/Vector.png", "admin_only": True}
    ]

    sidebar.buttons = {}
    sidebar.button_layouts = {}

    for item in menu_items:
        print(f"DEBUG - Traitement de l'élément: {item['text']}, admin_only: {item['admin_only']}, is_admin: {is_admin}")
        
        # Skip admin-only items if user is not admin
        if item["admin_only"] and not is_admin:
            print(f"DEBUG - Élément {item['text']} ignoré car admin_only=True et is_admin=False")
            continue
        
        print(f"DEBUG - Ajout de l'élément: {item['text']}")

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setAlignment(Qt.AlignLeft)

        icon_label = QLabel()
        pixmap = QPixmap(item["icon"])
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setText("?")
            print(f"Failed to load icon: {item['icon']}")
        icon_label.setFixedWidth(40)

        is_active = (active_module == item["text"])
        btn = QPushButton(item["text"])
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ORANGE if is_active else "transparent"};
                color: {WHITE};
                border: none;
                text-align: right;
                padding: 10px 3px;
                font-size: 18px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {ORANGE if is_active else LIGHT_BG};
            }}
        """)

        if on_module_change:
            btn.clicked.connect(lambda checked, module=item["text"]: on_module_change(module))

        sidebar.buttons[item["text"]] = btn
        sidebar.button_layouts[item["text"]] = btn_layout
        
        btn_layout.addWidget(icon_label)
        btn_layout.addWidget(btn)
        menu_layout.addLayout(btn_layout)

    print(f"DEBUG - Nombre total de boutons créés: {len(sidebar.buttons)}")
    print(f"DEBUG - Boutons créés: {list(sidebar.buttons.keys())}")

    # 🚪 Logout button
    logout_btn = QPushButton("تسجيل الخروج")
    logout_icon = QPixmap("pics/logout_icon.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    logout_btn.setIcon(QIcon(logout_icon))
    logout_btn.setIconSize(QSize(20, 20))
    logout_btn.setLayoutDirection(Qt.RightToLeft)
    logout_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {YELLOW_BTN};
            color: {WHITE};
            border: none;
            text-align: center;
            padding: 14px 20px;
            font-size: 15px;
            border-radius: 20px;
            margin-top: 30px;
        }}
        QPushButton:hover {{
            background-color: #d4af37;
        }}
    """)
   
    if on_logout:
        logout_btn.clicked.connect(on_logout)


    # ✅ Layout
    sidebar_layout.addWidget(profile_widget)
    sidebar_layout.addWidget(separator)
    sidebar_layout.addWidget(menu_widget)
    sidebar_layout.addStretch()
    sidebar_layout.addWidget(logout_btn, 0, Qt.AlignCenter)
    sidebar_layout.addSpacing(20)
    main_layout.addWidget(sidebar)

    # 📌 Toggle button
    sidebar_toggle = QPushButton()
    sidebar_toggle.setFixedSize(30, 30)
    sidebar_toggle.setStyleSheet(f"""
        QPushButton {{
            background-color: {MEDIUM_BG};
            border: none;
            border-radius: 15px;
            color: {WHITE};
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {LIGHT_BG};
        }}
    """)
    toggle_icon = QPixmap("pics/sidebar_icon.png")
    if not toggle_icon.isNull():
        toggle_icon = toggle_icon.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        sidebar_toggle.setIcon(QIcon(toggle_icon))
        sidebar_toggle.setIconSize(QSize(20, 20))
    else:
        sidebar_toggle.setText("≡")
        print("Failed to load sidebar toggle icon: pics/sidebar_icon.png")

    sidebar_visible = True
    def toggle_sidebar():
        nonlocal sidebar_visible
        sidebar.setVisible(not sidebar_visible)
        sidebar_visible = not sidebar_visible
        QApplication.processEvents()

    sidebar_toggle.clicked.connect(toggle_sidebar)

    # Update active module dynamically
    def update_active_module(module_name):
        for name, btn in sidebar.buttons.items():
            is_active = (name == module_name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ORANGE if is_active else 'transparent'};
                    color: {WHITE};
                    border: none;
                    text-align: right;
                    padding: 10px 3px;
                    font-size: 18px;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background-color: {ORANGE if is_active else LIGHT_BG};
                }}
            """)

    # Function to update user info dynamically
    def update_user_info(user_data):
        if user_data:
            username = user_data.get('username', 'اسم المستخدم')
            role = user_data.get('role', 'دور المستخدم')
            
            # Convert role to Arabic
            if role.lower() == 'admin':
                role_display = 'مدير'
            elif role.lower() == 'user':
                role_display = 'مستخدم'
            else:
                role_display = role
            
            user_name.setText(username)
            user_role.setText(role_display)

    sidebar.update_active_module = update_active_module
    sidebar.update_user_info = update_user_info
    sidebar.current_user_data = current_user_data
    sidebar.is_admin = is_admin

    # IMPORTANT: Return the three values expected by the caller
    print("DEBUG - Retour des valeurs: sidebar, sidebar_toggle, logout_btn")
    return sidebar, sidebar_toggle, logout_btn