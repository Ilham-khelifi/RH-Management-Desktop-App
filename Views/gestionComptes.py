import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
                             QFrame, QDialog, QMessageBox, QCheckBox, QComboBox, QDateEdit,
                             QScrollArea, QSizePolicy, QStackedWidget, QToolButton, QMenu,
                             QListWidget, QListWidgetItem, QGridLayout, QHeaderView,QFileDialog)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette, QBrush
from PyQt5.QtCore import Qt, QSize, QDate, QTimer

# Import our custom modules
from Views.Historique import HistoryDialog
from ui_constants import *
from AjouterCompte import AddAccountForm
from SuppCompte import DeleteAccountDialog

# AJOUT: Import du UserController qui manquait
from Controllers.auth_controller import AuthController
from Controllers.history_controller import HistoryController
from Controllers.user_controller import UserController  # IMPORTANT: Celui-ci manquait !
from Models.init_db import init_db
import openpyxl
from weasyprint import HTML, CSS
import html

class CompteManagementSystem(QMainWindow):
    def __init__(self, current_user_data=None, session=None):
        """
        Initialize the main application window and set up the UI components
        """
        super().__init__()
        self.setWindowTitle("نظام إدارة الموارد البشرية - إدارة الحسابات")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(QSize(500, 500))
        self.setStyleSheet(f"background-color: {DARK_BG}; color: {WHITE};")
        
        # MODIFICATION: Stocker les données de l'utilisateur connecté
        self.current_user_data = current_user_data or {}
        
        # MODIFICATION: Utiliser la session partagée ou créer une nouvelle si nécessaire
        if session:
            self.session = session
            print("DEBUG - Utilisation de la session partagée dans gestionComptes")
        else:
            print("DEBUG - Création d'une nouvelle session dans gestionComptes")
            self.session = init_db('mysql+pymysql://hr:hr@localhost/HR')
        
        # MODIFICATION: Initialisation des contrôleurs avec la bonne logique
        self.history_controller = HistoryController(self.session)
        self.user_controller = UserController(
            self.session, 
            self.current_user_data.get('account_number')  # Passer account_number, pas id
        )
        
        # CORRECTION: Injection du history_controller dans user_controller
        self.user_controller.set_history_controller(self.history_controller)
        
        self.auth_controller = AuthController(self.session)

        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create main content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)

        # Create main page
        self.main_page = QWidget()
        self.main_page_layout = QVBoxLayout(self.main_page)
        self.main_page_layout.setContentsMargins(15, 15, 15, 15)

        # Create action bar with Filter button
        self.create_action_bar()

        # Create table and buttons
        self.create_table()
        self.create_action_buttons()

        self.stacked_widget.addWidget(self.main_page)

        # Add content to main layout
        self.main_layout.addWidget(self.content_widget)

        # Show main page by default
        self.stacked_widget.setCurrentIndex(0)

        # Initialize filter state
        self.filter_dialog = None
        self.selected_filter_columns = []

        self.accounts = []
        self.history = []
        self.load_data_from_database()

    # NOUVELLE MÉTHODE: Charger les données depuis la base de données
    def load_data_from_database(self):
        """Charge les données depuis la base de données"""
        try:
            # Charger les comptes depuis la base de données
            self.accounts = self.user_controller.get_all_users()
            
            # Charger l'historique depuis la base de données
            self.history = self.history_controller.get_all_history()
            
            # Actualiser l'affichage
            self.refresh_table()
            
            print(f"DEBUG - Données chargées: {len(self.accounts)} comptes, {len(self.history)} entrées d'historique")
            
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            # En cas d'erreur, utiliser des listes vides
            self.accounts = []
            self.history = []

    def create_action_bar(self):
        """Create the action bar with Add button"""
        action_bar = QWidget()
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 0, 0, 15)

        # Add button
        add_btn = QPushButton("إضافة")
        add_btn.setFixedSize(100, 35)
        add_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ORANGE};
                    color: {WHITE};
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #e05d00;
                }}
            """)
        
        add_btn.clicked.connect(self.open_add_account_form)

        action_layout.addStretch()
        action_layout.addWidget(add_btn)
        self.main_page_layout.addWidget(action_bar)

    def create_table(self):
        """Create the main data table with all columns"""
        # Table container
        table_container = QWidget()
        table_container.setStyleSheet(f"background-color: {MEDIUM_BG}; border-radius: 10px;")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(15, 15, 15, 15)

        # Create table
        self.table = QTableWidget()
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {MEDIUM_BG};
                color: {WHITE};
                border: none;
                gridline-color: {LIGHT_BG};
                font-size: 16px;
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {LIGHT_BG};
                color: {WHITE};
                border: none;
                font-weight: bold;
                font-size: 16px;
                text-align: right;
            }}
            QTableWidget::item:selected {{
                background-color: {ORANGE};
                color: {WHITE};
            }}
            QHeaderView::section {{
                background-color: {DARKER_BG};
                color: {WHITE};
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 16px;
                text-align: right;
            }}
            QScrollBar:vertical {{
                background: {MEDIUM_BG};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {LIGHT_BG};
                min-height: 20px;
                border-radius: 7px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        # Set up columns
        columns = ["رقم الحساب", "اسم المستخدم", "البريد الإلكتروني", "الدور", "تاريخ الإنشاء"]

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        table_layout.addWidget(self.table)
        
        self.main_page_layout.addWidget(table_container)

    def create_action_buttons(self):
        """Create action buttons for edit, delete, and history"""
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        buttons_layout.setSpacing(25)

        # Create buttons
        edit_btn = QPushButton("تعديل")
        delete_btn = QPushButton("حذف")
        history_btn = QPushButton("سجل الأنشطة")

        # Style buttons
        for btn in [edit_btn, delete_btn, history_btn]:
            btn.setFixedSize(160, 45)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ORANGE};
                    color: {WHITE};
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #e05d00;
                }}
            """)
        

        # Connect button signals
        edit_btn.clicked.connect(self.edit_selected_account)
        delete_btn.clicked.connect(self.delete_selected_account)
        history_btn.clicked.connect(self.show_history)

        # Add buttons to layout
        buttons_layout.addWidget(history_btn)
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addWidget(edit_btn)

        self.main_page_layout.addWidget(buttons_widget)

    # MODIFICATION COMPLÈTE: Utiliser les contrôleurs de base de données
    def get_next_account_number(self):
        """Get the next sequential account number from database"""
        return self.user_controller.get_next_account_number()

    def is_username_unique(self, username, original_username=None):
        """Check if username is unique using database"""
        return self.user_controller.is_username_unique(username, original_username)

    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
        return re.match(pattern, email) is not None

    def add_account(self, account_data):
        """Add a new account using database controller"""
        try:
            success, message = self.user_controller.add_user(account_data)
            if success:
                # Recharger les données depuis la base de données
                self.load_data_from_database()
                return True
            else:
                print(f"Erreur lors de l'ajout: {message}")
                return False
        except Exception as e:
            print(f"Error adding account: {e}")
            return False

    def update_account(self, account_data):
        """Update an existing account using database controller"""
        try:
            account_number = account_data['account_number']
            success, message = self.user_controller.update_user(account_number, account_data)
            if success:
                # Recharger les données depuis la base de données
                self.load_data_from_database()
                return True
            else:
                print(f"Erreur lors de la mise à jour: {message}")
                return False
        except Exception as e:
            print(f"Error updating account: {e}")
            return False

    def delete_account(self, account_data):
        """Delete an account using database controller"""
        try:
            account_number = account_data['account_number']
            success, message = self.user_controller.delete_user(account_number)
            if success:
                # Recharger les données depuis la base de données
                self.load_data_from_database()
                return True
            else:
                print(f"Erreur lors de la suppression: {message}")
                return False
        except Exception as e:
            print(f"Error deleting account: {e}")
            return False

   
    def refresh_table(self):
        """Refresh the accounts table"""
        self.table.setRowCount(0)

        for account in self.accounts:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Add data to cells
            self.table.setItem(row_position, 0, QTableWidgetItem(str(account['account_number'])))
            self.table.setItem(row_position, 1, QTableWidgetItem(account['username']))
            self.table.setItem(row_position, 2, QTableWidgetItem(account['email']))
            self.table.setItem(row_position, 3, QTableWidgetItem(account['role']))
            self.table.setItem(row_position, 4, QTableWidgetItem(account['creation_date']))

    
    def update_data(self):
        self.refresh_table()
    def search_accounts(self, search_text):
        """Search accounts by username or email"""
        search_text = search_text.lower()
        self.table.setRowCount(0)

        for account in self.accounts:
            if (search_text in account['username'].lower() or
                    search_text in account['email'].lower()):
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                self.table.setItem(row_position, 0, QTableWidgetItem(str(account['account_number'])))
                self.table.setItem(row_position, 1, QTableWidgetItem(account['username']))
                self.table.setItem(row_position, 2, QTableWidgetItem(account['email']))
                self.table.setItem(row_position, 3, QTableWidgetItem(account['role']))
                self.table.setItem(row_position, 4, QTableWidgetItem(account['creation_date']))

    # UI Action Functions
    def open_add_account_form(self):
        """Open the add account form with database controllers"""
        from AjouterCompte import AddAccountForm
        
        self.add_form = AddAccountForm(
            parent=self,
            user_controller=self.user_controller,
            history_controller=self.history_controller,
            current_user_data=self.current_user_data,
            
        )
        
        # Set the account number
        self.add_form.account_number.setText(str(self.get_next_account_number()))
        self.add_form.show()

    def edit_selected_account(self):
        """Edit the selected account with database controllers"""
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "تحذير", "الرجاء تحديد حساب للتعديل")
            return

        row = selected_rows[0].row()
        account_number = self.table.item(row, 0).text()

        # Find the account data
        account_data = None
        for account in self.accounts:
            if str(account['account_number']) == account_number:
                account_data = account
                break

        if not account_data:
            QMessageBox.warning(self, "خطأ", "لم يتم العثور على الحساب")
            return

        from AjouterCompte import AddAccountForm
        
        self.edit_form = AddAccountForm(
            parent=self,
            edit_mode=True,
            account_data=account_data,
            user_controller=self.user_controller,
            history_controller=self.history_controller,
            current_user_data=self.current_user_data,
            
        )
        self.edit_form.show()

    def delete_selected_account(self):
        """Delete the selected account with database controllers"""
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "تحذير", "الرجاء تحديد حساب للحذف")
            return

        row = selected_rows[0].row()
        account_number = self.table.item(row, 0).text()

        # Find the account data
        account_data = None
        for account in self.accounts:
            if str(account['account_number']) == account_number:
                account_data = account
                break

        if not account_data:
            QMessageBox.warning(self, "خطأ", "لم يتم العثور على الحساب")
            return

        from SuppCompte import DeleteAccountDialog
        
        self.delete_dialog = DeleteAccountDialog(
            parent=self,
            account_data=account_data,
            user_controller=self.user_controller,
            history_controller=self.history_controller,
            current_user_data=self.current_user_data,
            
        )
        self.delete_dialog.show()

    def show_history(self):
        """Show the activity history using the  history dialog with shared session"""
        try:
            from Views.Historique import HistoryDialog
            
            print(f"DEBUG - Ouverture historique avec user_data: {self.current_user_data}")
            
            self.history_dialog = HistoryDialog(
                parent=self,
                current_user_data=self.current_user_data,
                session=self.session,  # AJOUT: Passer la session partagée
                module_name="إدارة الحسابات",
                gestion_filter="ادرة الحسابات" # AJOUT: Activer le filtre de gestion
            )
            self.history_dialog.show()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "خطأ",
                f"حدث خطأ غير متوقع:\n{str(e)}"
            )
            print(f"Erreur dans show_history: {e}")   
    
    
    
    def _get_table_data_as_lists(self):
        """
        Helper function to extract data from QTableWidget.
        Si un paginateur est utilisé et cache des lignes, seules les lignes visibles seront prises.
        Si pas de paginateur, toutes les lignes de la table sont prises.
        """
        if not hasattr(self, 'table') or not self.table or self.table.rowCount() == 0:
            print(f"Avertissement dans _get_table_data_as_lists pour {self.__class__.__name__}: self.table non disponible ou vide.")
            return None, None

        headers = [self.table.horizontalHeaderItem(i).text()
                   for i in range(self.table.columnCount())]

        data_rows = []
        for row in range(self.table.rowCount()):
            # Si un paginateur est actif et utilise isRowHidden:
            if hasattr(self, 'paginator') and self.paginator and self.table.isRowHidden(row):
                continue # Ignorer les lignes cachées par le paginateur
            
            # Si pas de paginateur, ou si la ligne n'est pas cachée :
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data_rows.append(row_data)
            
        return headers, data_rows

    def export_data_to_excel(self):
        print(f"{self.__class__.__name__}: export_data_to_excel called")
        headers, data = self._get_table_data_as_lists()

        if not data:
            QMessageBox.information(self, "لا بيانات للتصدير", "الجدول فارغ أو لا توجد بيانات للعرض.")
            return

        filePath, _ = QFileDialog.getSaveFileName(self, "تصدير إلى Excel", 
                                                  os.path.expanduser("~/Documents/Comptes_Utilisateurs.xlsx"), # Nom de fichier adapté
                                                  "Excel Workbook (*.xlsx);;All Files (*)")
        if not filePath:
            return

        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "قائمة الحسابات" # Titre de feuille adapté
            sheet.sheet_view.rightToLeft = True
            sheet.append(headers)

            for row_values in data:
                sheet.append(row_values)

            for col_idx, column_cells in enumerate(sheet.columns):
                length = max(len(str(cell.value) or "") for cell in column_cells)
                sheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx + 1)].width = length + 5

            workbook.save(filePath)
            QMessageBox.information(self, "نجاح التصدير", f"تم تصدير البيانات بنجاح إلى:\n{filePath}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ في التصدير", f"حدث خطأ أثناء تصدير الملف: {e}")
            print(f"Error exporting CompteManagementSystem to Excel: {e}")

    def print_data_to_pdf(self):
        print(f"{self.__class__.__name__}: print_data_to_pdf called")
        headers, data = self._get_table_data_as_lists()

        if not data:
            QMessageBox.information(self, "لا بيانات للطباعة", "الجدول فارغ أو لا توجد بيانات للعرض.")
            return

        filePath, _ = QFileDialog.getSaveFileName(self, "طباعة إلى PDF", 
                                                  os.path.expanduser("~/Documents/Comptes_Utilisateurs.pdf"), # Nom de fichier adapté
                                                  "PDF Document (*.pdf);;All Files (*)")
        if not filePath:
            return

        html_content = "<html><head><meta charset='UTF-8'>"
        html_content += """
        <style>
            @font-face { font-family: 'DejaVu Sans'; } /* Weasyprint essaiera de trouver cette police ou un substitut */
            body { direction: rtl; font-family: 'Arial', 'DejaVu Sans', sans-serif; font-size: 10pt; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #333; padding: 5px; text-align: right; word-wrap: break-word; }
            th { background-color: #f0f0f0; font-weight: bold; }
            caption { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; text-align: center; }
        </style>
        </head><body>
        """
        html_content += "<table><caption>قائمة حسابات المستخدمين</caption><thead><tr>" # Titre adapté
        for header in headers:
            html_content += f"<th>{header}</th>"
        html_content += "</tr></thead><tbody>"

        for row_values in data:
            html_content += "<tr>"
            for cell_value in row_values:
                html_content += f"<td>{html.escape(str(cell_value))}</td>"
            html_content += "</tr>"
        html_content += "</tbody></table></body></html>"

        try:
            # A4 portrait devrait suffire pour ces colonnes
            css_style = CSS(string='@page { size: A4 portrait; margin: 1cm; }') 
            HTML(string=html_content).write_pdf(filePath, stylesheets=[css_style])
            QMessageBox.information(self, "نجاح الطباعة", f"تم إنشاء ملف PDF بنجاح:\n{filePath}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ في الطباعة", f"حدث خطأ أثناء إنشاء ملف PDF: {e}\n"
                                 "تأكد أن WeasyPrint et ses dépendances (Pango, Cairo) sont correctement installés.")
            print(f"Error printing CompteManagementSystem to PDF: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set application-wide font for Arabic support
    font = QFont("Arial", 10)
    app.setFont(font)

    # Set right-to-left layout for Arabic
    app.setLayoutDirection(Qt.RightToLeft)

    # Test avec des données utilisateur
    test_user_data = {
        'account_number': 1,
        'username': 'admin',
        'role': 'admin'  # CORRECTION: Mettre admin pour les tests
    }

    window = CompteManagementSystem(current_user_data=test_user_data)
    window.show()

    sys.exit(app.exec_())
