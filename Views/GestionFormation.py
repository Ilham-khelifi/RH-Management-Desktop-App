import os
from datetime import datetime
import sys
# print(sys.executable)
from Models import init_db
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QTableWidget, 
                            QTableWidgetItem, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, 
                            QFrame, QDialog, QMessageBox, QCheckBox, QComboBox, QDateEdit,
                            QScrollArea, QSizePolicy, QStackedWidget, QToolButton, QMenu,
                            QListWidget, QListWidgetItem, QGridLayout, QHeaderView, QCompleter,QFileDialog)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette, QBrush
from PyQt5.QtCore import Qt, QSize, QDate, QTimer, QLocale, pyqtSignal, QStringListModel
from TablePaginator1 import tablepaginator
from ui_constants import *
from custom_dialogs import CustomWarningDialog, CustomInfoDialog, CustomMessageBox
from Controllers.formation_controller import FormationController
from sqlalchemy.orm import sessionmaker
from DatabaseConnection import db
import openpyxl
from weasyprint import HTML, CSS
import html
class EmployeeCompleter(QCompleter):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setModel(QStringListModel([]))
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterMode(Qt.MatchContains)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setMaxVisibleItems(10)
        
        # Store employee data for lookup
        self.employees = []
        
    def update_employees(self, first_name):
        """Update the list of employees from the database based on first name"""
        if not first_name or len(first_name) < 2:
            self.model().setStringList([])
            return
            
        self.employees = self.controller.search_employees_by_first_name(first_name)
        
        # Create a list of first names
        employee_names = [emp.Prenom for emp in self.employees]
        
        # Update the model
        self.model().setStringList(employee_names)
    
    def get_last_name(self, first_name):
        """Get the last name for a given first name"""
        for emp in self.employees:
            if emp.Prenom == first_name:
                return emp.Nom
        return ""

# New class for form windows
class FormationFormWindow(QMainWindow):
    # Signal to send form data back to main window
    formSaved = pyqtSignal(list)
    
    def __init__(self, parent=None, title="Form Window", form_data=None, controller=None):
        """
        Initialize the form window with title and optional data
        """
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 600, 650)  # Reduced height since duration field is removed
        self.setStyleSheet(f"background-color: {DARK_BG}; color: {WHITE};")
        
        # Center the window on screen
        self.center_window()
        
        # Set window flags to have maximize, restore, and close buttons
        self.setWindowFlags(
            Qt.Window |              # Regular window
            Qt.WindowCloseButtonHint 
        )
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create a scroll area for the form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
    
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {DARK_BG};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 0px;  /* Hide scrollbar but keep functionality */
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: transparent;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # Create form content
        form_content = QWidget()
        form_layout = QVBoxLayout(form_content)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px 0;")
        
        # Form container
        form_container = QWidget()
        form_container.setStyleSheet(f"background-color: {LIGHT_BG}; border-radius: 10px;")
        form_container.setFixedWidth(500)  # Reduced width from 600 to 500
        
        container_layout = QVBoxLayout(form_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        
        # Form fields - REMOVED duration field as requested
        fields = [
            {"name": "الإسم", "type": "autocomplete"},
            {"name": "اللقب", "type": "text"},
            {"name": "نوع التكوين", "type": "text"},
            {"name": "تاريخ البدء", "type": "date"},
            {"name": "تاريخ الإنتهاء", "type": "date"},
            {"name": "مؤسسة التكوين", "type": "text"},
            {"name": "محتوى التكوين", "type": "text"}
        ]
        
        self.form_fields = {}
        
        for field in fields:
            field_layout = QVBoxLayout()
            field_layout.setSpacing(5)
            
            label = QLabel(field["name"])
            label.setStyleSheet("font-size: 16px; font-weight: bold;")  # Increased font size to 16px
            label.setLayoutDirection(Qt.RightToLeft)

            
            if field["type"] == "date":
                input_field = QDateEdit()
                input_field.setCalendarPopup(True)
                input_field.setDate(QDate.currentDate())
                
                # Set RTL date format (YYYY/MM/dd) as requested
                input_field.setDisplayFormat("yyyy/MM/dd")
                input_field.setLayoutDirection(Qt.RightToLeft)
                
                input_field.setStyleSheet(f"""
                    QDateEdit {{
                        background-color: {DARKER_BG};
                        border: none;
                        border-radius: 5px;
                        padding: 8px;
                        color: {WHITE};
                        font-size: 16px;
                        text-align: right;
                    }}
                """)
                
                # Remove the restriction for end date > current date as requested
                # No date validation for future dates
                
            elif field["type"] == "combo":
                input_field = QComboBox()
                input_field.addItems(field["options"])
                input_field.setStyleSheet(f"""
                    QComboBox {{
                        background-color: {DARKER_BG};
                        border: none;
                        border-radius: 5px;
                        padding: 8px;
                        color: {WHITE};
                        font-size: 16px;
                        text-align: right;
                    }}
                    QComboBox::drop-down {{
                        border: none;
                    }}
                    QComboBox::down-arrow {{
                        image: url(dropdown.png);
                        width: 12px;
                        height: 12px;
                    }}
                """)
                input_field.setLayoutDirection(Qt.RightToLeft)
            elif field["type"] == "autocomplete":
                input_field = QLineEdit()
            
                input_field.setStyleSheet(f"""
                    QLineEdit {{
                        background-color: {DARKER_BG};
                        border: none;
                        border-radius: 5px;
                        padding: 8px;
                        color: {WHITE};
                        font-size: 16px;
                        text-align: right;
                    }}
                """)
                input_field.setLayoutDirection(Qt.RightToLeft)
                input_field.setAlignment(Qt.AlignRight)  # Text input from right to left
                
                # Add autocomplete for first name
                if field["name"] == "الإسم" and self.controller:
                    self.name_completer = EmployeeCompleter(self.controller, input_field)
                    input_field.setCompleter(self.name_completer)
                    
                    # Connect textChanged to update suggestions and last name
                    input_field.textChanged.connect(self.update_name_suggestions)
                    input_field.editingFinished.connect(self.update_last_name)
            else:
                input_field = QLineEdit()
        
                input_field.setStyleSheet(f"""
                    QLineEdit {{
                        background-color: {DARKER_BG};
                        border: none;
                        border-radius: 5px;
                        padding: 8px;
                        color: {WHITE};
                        font-size: 16px;
                        text-align: right;
                    }}
                """)
                input_field.setLayoutDirection(Qt.RightToLeft)
                input_field.setAlignment(Qt.AlignRight)  # Text input from right to left
                
                if field.get("readonly", False):
                    input_field.setReadOnly(True)
                    input_field.setStyleSheet(input_field.styleSheet() + f"background-color: #3A3D42;")
            
            field_layout.addWidget(label)
            field_layout.addWidget(input_field)
            container_layout.addLayout(field_layout)
            
            self.form_fields[field["name"]] = input_field
        
        # Fill form with data if provided
        if form_data:
            self.fill_form_with_data(form_data)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        save_btn = QPushButton("حفظ")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GREEN};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: #3d8b40;
            }}
        """)
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: #d32f2f;
            }}
        """)
        
        # Connect buttons
        save_btn.clicked.connect(self.save_form)
        cancel_btn.clicked.connect(self.close)

        # Add buttons in right-to-left order for Arabic
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        container_layout.addLayout(buttons_layout)
        
        # Add to form layout
        form_layout.addWidget(title_label)
        form_layout.addWidget(form_container, 0, Qt.AlignCenter)
        
        # Set the form content as the scroll area widget
        scroll_area.setWidget(form_content)
        
        # Add scroll area to the main layout
        main_layout.addWidget(scroll_area)
        
        # Get current date for validation
        self.today = QDate.currentDate()
    
    def center_window(self):
        """Center the window on the screen, even with multiple monitors"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def update_name_suggestions(self):
        """Update employee suggestions as user types in first name field"""
        first_name = self.form_fields["الإسم"].text()
        if len(first_name) >= 2 and self.controller and hasattr(self, 'name_completer'):
            self.name_completer.update_employees(first_name)
    
    def update_last_name(self):
        """Update last name field when first name is selected"""
        first_name = self.form_fields["الإسم"].text()
        if hasattr(self, 'name_completer') and first_name:
            last_name = self.name_completer.get_last_name(first_name)
            if last_name:
                self.form_fields["اللقب"].setText(last_name)
    
    def validate_form(self):
        """
        Validate the form fields
        Checks required fields, numeric values, and date ranges
        """
        # Check required fields (removed duration from required fields)
        required_fields = ["الإسم", "اللقب", "نوع التكوين", "تاريخ البدء", "تاريخ الإنتهاء", "مؤسسة التكوين"]
        
        for field_name in required_fields:
            field = self.form_fields[field_name]
            if isinstance(field, QLineEdit) and not field.text().strip():
                # Use custom dialog instead of QMessageBox
                warning_dialog = CustomWarningDialog(self, "تحذير", f"الرجاء إدخال {field_name}")
                warning_dialog.exec_()
                field.setFocus()
                return False
                
        # Validate employee exists
        first_name = self.form_fields["الإسم"].text().strip()
        last_name = self.form_fields["اللقب"].text().strip()
        
        if self.controller and not self.controller.get_employee_by_name(first_name, last_name):
            warning_dialog = CustomWarningDialog(self, "تحذير", "الموظف غير موجود. الرجاء التأكد من الاسم واللقب")
            warning_dialog.exec_()
            self.form_fields["الإسم"].setFocus()
            return False
            
        # Validate date range
        start_date = self.form_fields["تاريخ البدء"].date()
        end_date = self.form_fields["تاريخ الإنتهاء"].date()
        
        if start_date > end_date:
            warning_dialog = CustomWarningDialog(self, "تحذير", "تاريخ البدء يجب أن يكون قبل تاريخ الإنتهاء")
            warning_dialog.exec_()
            return False
            
        # REMOVED: Validation for end date > today (as requested)
        # Future training dates are now allowed
            
        return True
    
    def save_form(self):
        """Save form data and emit signal with the data"""
        # Validate form data
        if not self.validate_form():
            return
        
        # Get form data (adjusted for removed duration field)
        form_data = []
        
        # Add placeholder for Annee (will be calculated from DateDebut)
        form_data.append("")
        
        # Add placeholder for idemploye (will be looked up from name)
        form_data.append("")
        
        # Add the rest of the form fields
        for field_name, field in self.form_fields.items():
            if isinstance(field, QDateEdit):
                form_data.append(field.date().toString("yyyy-MM-dd"))
            elif isinstance(field, QComboBox):
                form_data.append(field.currentText())
            else:
                form_data.append(field.text())
        
        # Emit signal with form data
        self.formSaved.emit(form_data)
        
        # Close the window
        self.close()

    def fill_form_with_data(self, data):
        """Fill form fields with provided data (adjusted for removed duration field)"""
        # Map data to form fields (updated mapping without duration)
        field_mapping = {
            0: None,  # Skip Annee
            1: None,  # Skip idemploye
            2: "الإسم",  # Prenom
            3: "اللقب",  # Nom
            4: "نوع التكوين",
            5: "تاريخ البدء",
            6: "تاريخ الإنتهاء",
            7: None,  # Skip duration (removed from form)
            8: "مؤسسة التكوين",
            9: "محتوى التكوين"
        }
        
        for i, field_name in field_mapping.items():
            if field_name and i < len(data):
                field = self.form_fields[field_name]
                value = data[i]
                
                if isinstance(field, QDateEdit) and value:
                    date = QDate.fromString(value, "yyyy-MM-dd")
                    field.setDate(date)
                elif isinstance(field, QComboBox) and value:
                    index = field.findText(value)
                    if index >= 0:
                        field.setCurrentIndex(index)
                elif value:
                    field.setText(value)



# New class for filter dialog
class FilterDialog(QDialog):
    filterApplied = pyqtSignal(list, str)
    
    def __init__(self, parent=None, columns=None):
        super().__init__(parent)
        self.setWindowTitle("ترشيح")
        self.setFixedWidth(350)
        self.setStyleSheet(f"background-color: {MEDIUM_BG}; color: {WHITE};")
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("اختر الأعمدة للترشيح:")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 15px;")
        dialog_layout.addWidget(title_label)
        
        # Create checkboxes for each column
        if not columns:
            columns = [
                "السنة", "رقم الموظف", "الإسم", "اللقب", "نوع التكوين", 
                "تاريخ البدء", "تاريخ الإنتهاء", "مدة التكوين", "مؤسسة التكوين"
            ]
        
        # Create a scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {MEDIUM_BG};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 0px;  /* Hide scrollbar but keep functionality */
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: transparent;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # Create a widget to hold checkboxes
        checkbox_widget = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_widget)
        
        self.filter_checkboxes = {}
        
        for column in columns:
            checkbox = QCheckBox(column)
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    font-size: 16px;  /* Increased font size */
                    padding: 8px 0;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {ORANGE};
                    border: 2px solid {WHITE};
                }}
            """)
            checkbox_layout.addWidget(checkbox)
            self.filter_checkboxes[column] = checkbox
        
        # Set the checkbox widget as the scroll area widget
        scroll_area.setWidget(checkbox_widget)
        
        # Filter value input
        filter_value_layout = QHBoxLayout()
        filter_value_layout.setSpacing(10)
        
        filter_value_label = QLabel("قيمة الترشيح:")
        filter_value_label.setStyleSheet("font-size: 16px;")  # Increased font size
        filter_value_label.setAlignment(Qt.AlignRight)  # Right align for Arabic
        
        self.filter_value_input = QLineEdit()
        self.filter_value_input.setPlaceholderText("أدخل قيمة للترشيح...")
        self.filter_value_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 10px;
                color: {BLACK};
                font-size: 16px;  /* Increased font size */
                text-align: right;
            }}
        """)
        self.filter_value_input.setLayoutDirection(Qt.RightToLeft)
        self.filter_value_input.setAlignment(Qt.AlignRight)  # Ensure text is right-aligned
        
        filter_value_layout.addWidget(self.filter_value_input)
        filter_value_layout.addWidget(filter_value_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        apply_btn = QPushButton("تطبيق")
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ORANGE};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;  /* Increased font size */
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #e05d00;
            }}
        """)
        apply_btn.clicked.connect(self.apply_filter)
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MEDIUM_BG};
                color: {WHITE};
                border: 1px solid {LIGHT_BG};
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;  /* Increased font size */
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_BG};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(apply_btn)
        
        # Add widgets to layout
        dialog_layout.addWidget(scroll_area)
        dialog_layout.addSpacing(15)
        dialog_layout.addLayout(filter_value_layout)
        dialog_layout.addSpacing(15)
        dialog_layout.addLayout(buttons_layout)
    
    def apply_filter(self):
        # Get selected columns
        selected_columns = []
        for column, checkbox in self.filter_checkboxes.items():
            if checkbox.isChecked():
                selected_columns.append(column)
        
        # Get filter value
        filter_value = self.filter_value_input.text().strip()
        
        # Emit signal with filter data
        self.filterApplied.emit(selected_columns, filter_value)
        
        # Close the dialog
        self.accept()

class FormationManagementSystem(QMainWindow):
    def __init__(self, current_user_data=None, session=None):
        """
        Initialize the main application window and set up the UI components
        """
        super().__init__()
        self.setWindowTitle("نظام إدارة الموارد البشرية - إدارة التكوين")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(f"background-color: {DARK_BG}; color: {WHITE};")
        self.current_user_data = current_user_data or {}
        current_user_account_number = None
        if self.current_user_data:
            current_user_account_number = self.current_user_data.get('account_number')
            print(f"DEBUG - Utilisateur actuel dans FormationManagement: {current_user_account_number}")
        else:
            print("DEBUG - Aucun utilisateur actuel défini dans FormationManagement")   
        # MODIFICATION: Utiliser la session partagée ou créer une nouvelle si nécessaire
        if session:
            self.session = session
            print("DEBUG - Utilisation de la session partagée dans gestionComptes")
        else:
            print("DEBUG - Création d'une nouvelle session dans gestionComptes")
            self.session = init_db('mysql+pymysql://hr:hr@localhost/HR')
        
        self.controller = FormationController(self.session, current_user_account_number)

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
        
        # Create action bar with Filter button and Refresh button
        self.create_action_bar()

        # Add main title at the top as requested
        self.create_main_title()
        
        # Create table and buttons
        self.create_table()
        self.create_action_buttons()
        
        self.stacked_widget.addWidget(self.main_page)
        
        # Add content to main layout
        self.main_layout.addWidget(self.content_widget)
        
        # Show main page by default
        self.stacked_widget.setCurrentIndex(0)
        
        self.load_data_from_database()
        
        # Initialize filter state
        self.selected_filter_columns = []
        
        # Get current date for validation
        self.today = QDate.currentDate()
        
        # Initialize form windows
        self.add_form_window = None
        self.edit_form_window = None
        self.history_window = None

    def create_main_title(self):
        """Create the main title at the top of the window in Arabic RTL"""
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        main_title = QLabel("جدول تفاصيل إدارة التكوين")
        main_title.setStyleSheet(f"""
            color: {WHITE};
            font-size: 18px;  /* Increased font size */
            font-weight: bold;
        """)
        main_title.setLayoutDirection(Qt.RightToLeft)
        title_layout.addWidget(main_title)
        self.main_page_layout.addWidget(title_container)

    def create_action_bar(self):
        """
        Create the action bar with Filter button and Refresh button (moved Add button to bottom)
        """
        action_bar = QWidget()
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 0, 0, 20)  # Add margin at bottom
        action_layout.setSpacing(10)

# Refresh button as requested
        refresh_btn = QPushButton("⟳")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.setToolTip("تحديث الجدول")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #37474f;
                border: none;
                border-radius: 17px;
                color: #ffffff;
                font-weight: bold;
                font-size: 25px;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)

        # Filter button with integrated icon and text
        filter_btn = QPushButton("ترشيح")
        filter_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MEDIUM_BG};
                border: none;
                border-radius: 8px;
                color: {WHITE};
                font-weight: bold;
                font-size: 16px;  /* Increased font size */
                padding: 8px 15px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_BG};
            }}
        """)
        
        # Load and set filter icon
        filter_icon = QPixmap("pics/filter.png")
        if not filter_icon.isNull():
            filter_icon = filter_icon.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            filter_btn.setIcon(QIcon(filter_icon))
            filter_btn.setIconSize(QSize(16, 16))
        
        filter_btn.setToolTip("ترشيح")
        filter_btn.clicked.connect(self.show_filter_dialog)
        
        
        
        # Add widgets to layout - right to left for Arabic
        action_layout.addWidget(filter_btn, alignment=Qt.AlignLeft)
        action_layout.addStretch()
        action_layout.addWidget(refresh_btn, alignment=Qt.AlignRight)


        
        self.main_page_layout.addWidget(action_bar)

    def refresh_data(self):
        """Refresh the table data from database"""
        self.load_data_from_database()
        # Reset any applied filters
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, False)
        self.selected_filter_columns = []
    def update_data(self):
        self.refresh_data()
    def show_filter_dialog(self):
        """
        Show the filter dialog with checkboxes for column selection
        """
        # Create columns list
        columns = [
            "السنة", "رقم الموظف", "الإسم", "اللقب", "نوع التكوين", 
            "تاريخ البدء", "تاريخ الإنتهاء", "مدة التكوين", "مؤسسة التكوين"
        ]
        
        # Create and show filter dialog
        filter_dialog = FilterDialog(self, columns)
        filter_dialog.filterApplied.connect(self.apply_filter)
        filter_dialog.exec_()

    def apply_filter(self, selected_columns, filter_value):
        """
        Apply the filter to the table based on selected columns and input value
        """
        # Store selected columns
        self.selected_filter_columns = selected_columns
        
        if not filter_value or not selected_columns:
            # Reset filter if no value or no columns selected
            for row in range(self.table.rowCount()):
                self.table.setRowHidden(row, False)
            return
        
        # Get column indices for selected columns
        column_indices = []
        for col_name in selected_columns:
            for col_idx in range(self.table.columnCount()):
                if self.table.horizontalHeaderItem(col_idx).text() == col_name:
                    column_indices.append(col_idx)
        
        # Apply filter
        for row in range(self.table.rowCount()):
            row_visible = False
            
            # Check if any selected column contains the filter value
            for col_idx in column_indices:
                cell_value = self.table.item(row, col_idx).text().lower()
                if filter_value.lower() in cell_value:
                    row_visible = True
                    break
            
            self.table.setRowHidden(row, not row_visible)

    def create_table(self):
        """
        Create the main data table with all columns, ensuring proper header alignment.
        """

        # Table container (styling remains the same)
        table_container = QWidget()
        table_container.setStyleSheet(f"background-color:{MEDIUM_BG}; border-radius: 8px; margin: 0px;")

        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(15, 15, 15, 15)

        # Create table (styling remains the same)
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
            
        """)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set up columns
        columns = [
        "السنة",
        "رقم الموظف",
        "الإسم",
        "اللقب",
        "نوع التكوين",
        "تاريخ البدء",
        "تاريخ الإنتهاء",
        "مدة التكوين",
        "مؤسسة التكوين",
        "محتوى التكوين",
    ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Add table and paginator
        table_layout.addWidget(self.table)
        self.paginator = tablepaginator(self.table, rows_per_page=10)
        table_layout.addWidget(self.paginator)
        self.main_page_layout.addWidget(table_container)


    def create_action_buttons(self):
        """
        Create action buttons including the moved Add button
        All buttons have the same size and are aligned at the bottom
        """
        # Buttons container
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        buttons_layout.setSpacing(25)
        
        # Create buttons - Add button moved here as requested
        add_btn = QPushButton("إضافة")
        edit_btn = QPushButton("تعديل")
        delete_btn = QPushButton("حذف")
        history_btn = QPushButton("سجل الأنشطة")
        
        # Style buttons - all with the same fixed size
        for btn in [add_btn, edit_btn, delete_btn, history_btn]:
            btn.setFixedSize(160, 45)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ORANGE};
                    color: {WHITE};
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;  /* Increased font size */
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #e05d00;
                }}
                QPushButton:pressed {{
                    background-color: #cc5200;
                }}
            """)
        
        # Connect buttons to actions
        add_btn.clicked.connect(self.show_add_formation_form)
        edit_btn.clicked.connect(self.show_edit_form)
        delete_btn.clicked.connect(self.show_delete_dialog)
        history_btn.clicked.connect(self.show_history)
        
        # Add buttons to layout - right to left for Arabic
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addWidget(history_btn)
        
        self.main_page_layout.addWidget(buttons_widget)
    
    def show_add_formation_form(self):
        """
        Show the add formation form in a separate window
        """
        # Create and show add formation form window
        self.add_form_window = FormationFormWindow(self, "إضافة تكوين", controller=self.controller)
        self.add_form_window.formSaved.connect(self.save_new_formation_from_window)
        self.add_form_window.show()

    def save_new_formation_from_window(self, formation_data):
       try:
        # Extract first name and last name
        first_name = formation_data[2]  # Index 2 is now the first name field
        last_name = formation_data[3]   # Index 3 is now the last name field
        
        # Extract other data (adjusted indices for removed duration field)
        type_formation = formation_data[4]
        date_debut = datetime.strptime(formation_data[5], "%Y-%m-%d").date()
        date_fin = datetime.strptime(formation_data[6], "%Y-%m-%d").date()
        etablissement = formation_data[7]  # Adjusted index
        theme = formation_data[8] if len(formation_data) > 8 and formation_data[8] else None  # Adjusted index

        # Create a new formation in DB
        new_formation = self.controller.create_formation(
            first_name=first_name,
            last_name=last_name,
            type_formation=type_formation,
            date_debut=date_debut,
            date_fin=date_fin,
            etablissement=etablissement,
            theme=theme
        )

        # Refresh the table
        self.load_data_from_database()



        info_dialog = CustomInfoDialog(self, "نجاح", "تم إضافة التكوين بنجاح")
        info_dialog.exec_()
       except Exception as e:
        warning_dialog = CustomWarningDialog(self, "خطأ", str(e))
        warning_dialog.exec_()

    def show_edit_form(self):
        """
        Show the edit form in a separate window with selected row data
        """
        # Check if a row is selected
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            warning_dialog = CustomWarningDialog(self, "تحذير", "الرجاء اختيار تكوين للتعديل")
            warning_dialog.exec_()
            return
        
        # Get selected row data
        row = selected_rows[0].row()
        row_data = []
        
        for col in range(self.table.columnCount()):
            row_data.append(self.table.item(row, col).text())
        
        # Create and show edit form window
        self.edit_form_window = FormationFormWindow(self, "تعديل تكوين", row_data, self.controller)
        self.edit_form_window.formSaved.connect(lambda data: self.save_edited_formation(row, data))
        self.edit_form_window.show()

    def save_edited_formation(self, row, formation_data):
        try:
            formation_id = int(self.table.item(row, 0).data(Qt.UserRole))  # Hidden ID
            
            # Extract first name and last name
            first_name = formation_data[2]  # Index 2 is now the first name field
            last_name = formation_data[3]   # Index 3 is now the last name field
            
            # Extract other data (adjusted indices for removed duration field)
            type_formation = formation_data[4]
            date_debut = datetime.strptime(formation_data[5], "%Y-%m-%d").date()
            date_fin = datetime.strptime(formation_data[6], "%Y-%m-%d").date()
            etablissement = formation_data[7]  # Adjusted index
            theme = formation_data[8] if len(formation_data) > 8 and formation_data[8] else None  # Adjusted index

            self.controller.update_formation(
                formation_id=formation_id,
                first_name=first_name,
                last_name=last_name,
                type_formation=type_formation,
                date_debut=date_debut,
                date_fin=date_fin,
                etablissement=etablissement,
                theme=theme
            )

            self.load_data_from_database()

            CustomInfoDialog(self, "نجاح", "تم تعديل التكوين بنجاح").exec_()

        except Exception as e:
            CustomWarningDialog(self, "خطأ", str(e)).exec_()
    
    def show_delete_dialog(self):
        """
        Show confirmation dialog for deleting a formation
        """
        # Check if a row is selected
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            warning_dialog = CustomWarningDialog(self, "تحذير", "الرجاء اختيار تكوين للحذف")
            warning_dialog.exec_()
            return
        
        # Use CustomMessageBox instead of DeleteConfirmationDialog
        delete_dialog = CustomMessageBox(self, "حذف تكوين", "هل أنت متأكد أنك تريد حذف هذه التكوين ؟")
        # Connect the accept signal to delete_formation
        delete_dialog.accepted.connect(lambda: self.delete_formation(selected_rows[0].row()))
        delete_dialog.exec_()

    def delete_formation(self, row):
        try:
            formation_id = int(self.table.item(row, 0).data(Qt.UserRole))
            self.controller.delete_formation(formation_id)
            self.load_data_from_database()

            CustomInfoDialog(self, "نجاح", "تم حذف التكوين بنجاح").exec_()

        except Exception as e:
            CustomWarningDialog(self, "خطأ", str(e)).exec_()

    def show_history(self):
        """Show the activity history using the  history dialog with shared session"""
        try:
            from Views.Historique import HistoryDialog
            
            print(f"DEBUG - Ouverture historique avec user_data: {self.current_user_data}")
            
            self.history_dialog = HistoryDialog(
                parent=self,
                current_user_data=self.current_user_data,
                session=self.session,  # AJOUT: Passer la session partagée
                module_name="إدارة التكوين",  # Module name in Arabic
                gestion_filter="إدارة التكوينات" # Filter for formation management
                
            )
            self.history_dialog.show()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "خطأ",
                f"حدث خطأ غير متوقع:\n{str(e)}"
            )
            print(f"Erreur dans show_history: {e}")   


    def log_action(self, action_type, details):
        """
        Log user actions for auditing purposes
        In a real application, this would save to a database
        """
        # In a real application, this would save to a database
        # For this example, we'll just print to console
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        user = "اسم المستخدم"  # This would come from the logged-in user
        
        print(f"Action logged: {timestamp} | {user} | {action_type} | {details}")

    def load_data_from_database(self):
        self.table.setRowCount(0)
        formations = self.controller.get_all_formations()
        for formation in formations:
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)

            values = [
                str(formation.DateDebut.year),
                str(formation.idemploye),
                formation.employe.Prenom if formation.employe else "",
                formation.employe.Nom if formation.employe else "",
                formation.Type,
                formation.DateDebut.strftime("%Y-%m-%d"),
                formation.DateFin.strftime("%Y-%m-%d"),
                f"{self.controller.calculate_duration(formation.DateDebut, formation.DateFin)} يوم",
                formation.Etablissement,
                formation.Theme or ""
            ]

            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_pos, col, item)

            # Store hidden ID
            self.table.item(row_pos, 0).setData(Qt.UserRole, formation.idFormation)

        self.paginator.update_total_rows()
        self.paginator.update_page(1)


    def _get_table_data_as_lists(self):
        """Helper function to extract data ONLY from VISIBLE rows in self.table."""
        if not hasattr(self, 'table') or not self.table or self.table.rowCount() == 0:
            print(f"Avertissement dans _get_table_data_as_lists pour {self.__class__.__name__}: self.table non disponible ou vide.")
            return None, None

        headers = [self.table.horizontalHeaderItem(i).text()
                   for i in range(self.table.columnCount())]

        visible_row_data = []
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row): # Respecte la pagination
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                visible_row_data.append(row_data)
        return headers, visible_row_data

    def export_data_to_excel(self):
        print(f"{self.__class__.__name__}: export_data_to_excel called")
        headers, data = self._get_table_data_as_lists()

        if not data:
            QMessageBox.information(self, "لا بيانات للتصدير", "لا توجد تكوينات للعرض في الجدول الحالي.")
            return

        filePath, _ = QFileDialog.getSaveFileName(self, "تصدير التكوينات إلى Excel", 
                                                  os.path.expanduser(f"~/Documents/Formations.xlsx"),
                                                  "Excel Workbook (*.xlsx);;All Files (*)")
        if not filePath: return

        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "قائمة التكوينات"
            sheet.sheet_view.rightToLeft = True
            sheet.append(headers)
            for row_values in data: sheet.append(row_values)
            for col_idx, column_cells in enumerate(sheet.columns):
                length = max(len(str(cell.value) or "") for cell in column_cells)
                sheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx + 1)].width = length + 5
            workbook.save(filePath)
            QMessageBox.information(self, "نجاح التصدير", f"تم تصدير البيانات بنجاح إلى:\n{filePath}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ في التصدير", f"حدث خطأ: {e}")
            print(f"Error exporting Formations to Excel: {e}")

    def print_data_to_pdf(self):
        print(f"{self.__class__.__name__}: print_data_to_pdf called")
        headers, data = self._get_table_data_as_lists()

        if not data:
            QMessageBox.information(self, "لا بيانات للطباعة", "لا توجد تكوينات للعرض في الجدول الحالي.")
            return

        filePath, _ = QFileDialog.getSaveFileName(self, "طباعة التكوينات إلى PDF", 
                                                  os.path.expanduser(f"~/Documents/Formations.pdf"),
                                                  "PDF Document (*.pdf);;All Files (*)")
        if not filePath: return

        html_content = "<html><head><meta charset='UTF-8'>"
        html_content += """
        <style>
            @font-face { font-family: 'DejaVu Sans'; }
            body { direction: rtl; font-family: 'Arial', 'DejaVu Sans', sans-serif; font-size: 9pt; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #333; padding: 4px; text-align: right; word-wrap: break-word; }
            th { background-color: #f0f0f0; font-weight: bold; }
            caption { font-size: 1.1em; font-weight: bold; margin-bottom: 8px; text-align: center; }
        </style>
        </head><body>
        """
        html_content += "<table><caption>جدول تفاصيل إدارة التكوين</caption><thead><tr>"
        for header in headers: html_content += f"<th>{header}</th>"
        html_content += "</tr></thead><tbody>"
        for row_values in data:
            html_content += "<tr>"
            for cell_value in row_values: html_content += f"<td>{html.escape(str(cell_value))}</td>"
            html_content += "</tr>"
        html_content += "</tbody></table></body></html>"

        try:
            css_style = CSS(string='@page { size: A3 landscape; margin: 0.7cm; }') # A3 landscape pour plus de colonnes
            HTML(string=html_content).write_pdf(filePath, stylesheets=[css_style])
            QMessageBox.information(self, "نجاح الطباعة", f"تم إنشاء ملف PDF بنجاح:\n{filePath}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ في الطباعة", f"حدث خطأ: {e}\n"
                                 "Vérifiez WeasyPrint et ses dépendances (Pango, Cairo).")
            print(f"Error printing Formations to PDF: {e}")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application-wide font for Arabic support
    font = QFont("Arial", 10)
    app.setFont(font)
    
    # Set right-to-left layout for Arabic
    app.setLayoutDirection(Qt.RightToLeft)
    
    window = FormationManagementSystem()
    window.show()
    
    sys.exit(app.exec_())