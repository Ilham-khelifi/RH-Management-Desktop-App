import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                             QPushButton, QHeaderView, QDialog, QFormLayout,
                             QLineEdit, QDateEdit, QComboBox, QCheckBox, QToolButton,
                             QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
from Views.ui_constants import *

# Import du contrôleur d'historique
from Controllers.history_controller import HistoryController
from Models import init_db


class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Set window properties
        self.setWindowTitle("تصفية السجل")
        self.setMinimumWidth(400)
        self.setStyleSheet(f"background-color: {DARK_BG}; color: {WHITE};")

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Username filter
        self.username_filter = QLineEdit()
        self.username_filter.setStyleSheet(f"""
            QLineEdit {{
                background-color: {MEDIUM_BG};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }}
        """)
        form_layout.addRow("اسم المستخدم:", self.username_filter)

        # Date filter
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setStyleSheet(f"""
            QDateEdit {{
                background-color: {MEDIUM_BG};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }}
        """)
        self.use_date = QCheckBox("تفعيل تصفية التاريخ")
        self.use_date.setStyleSheet(f"color: {WHITE}; font-size: 14px;")

        date_layout = QHBoxLayout()
        date_layout.addWidget(self.date_filter)
        date_layout.addWidget(self.use_date)
        form_layout.addRow("التاريخ:", date_layout)

        # Event filter - Dynamique selon le module
        self.event_filter = QComboBox()
        self.populate_event_filter()
        self.event_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: {MEDIUM_BG};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {MEDIUM_BG};
                color: {WHITE};
                selection-background-color: {ORANGE};
            }}
        """)
        form_layout.addRow("الحدث:", self.event_filter)

        # NOUVEAU : Gestion filter
        self.gestion_filter = QComboBox()
        self.populate_gestion_filter()
        self.gestion_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: {MEDIUM_BG};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {MEDIUM_BG};
                color: {WHITE};
                selection-background-color: {ORANGE};
            }}
        """)
        form_layout.addRow("الإدارة:", self.gestion_filter)

        layout.addLayout(form_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        apply_button = QPushButton("تطبيق")
        apply_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ORANGE};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e05d00;
            }}
        """)
        apply_button.clicked.connect(self.apply_filter)

        reset_button = QPushButton("إعادة ضبط")
        reset_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {WHITE};
                border: 1px solid {ORANGE};
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 106, 14, 0.1);
            }}
        """)
        reset_button.clicked.connect(self.reset_filter)

        buttons_layout.addWidget(reset_button)
        buttons_layout.addWidget(apply_button)

        layout.addSpacing(20)
        layout.addLayout(buttons_layout)

        # Set layout direction to RTL for Arabic
        self.setLayoutDirection(Qt.RightToLeft)
    
    def populate_event_filter(self):
        """Populate event filter with common events"""
        self.event_filter.addItem("الكل")
        
        # Événements communs pour tous les modules
        common_events = [
            "إضافة حساب", "تعديل حساب", "حذف حساب",
            "إضافة موظف", "تعديل موظف", "حذف موظف",
            "إضافة إجازة", "تعديل إجازة", "حذف إجازة", "موافقة على إجازة", "رفض إجازة",
            "إضافة تكوين", "تعديل تكوين", "حذف تكوين",
            "إضافة غياب", "تعديل غياب", "حذف غياب",
            "إضافة تقييم", "تعديل تقييم", "حذف تقييم",
            "تسجيل الدخول", "تسجيل الخروج",
            "عرض سجل الأنشطة", "تصفية سجل الأنشطة",
            "محاولة وصول غير مصرح"
        ]
        
        for event in common_events:
            self.event_filter.addItem(event)

    def populate_gestion_filter(self):
        """NOUVEAU : Populate gestion filter with management modules"""
        self.gestion_filter.addItem("الكل")
        
        # Modules de gestion disponibles
        gestion_modules = [
            "إدارة الموظفين",
            "إدارة الإجازات", 
            "إدارة الغياب",
            "إدارة التكوين",
            "إدارة التقييمات",
            "إدارة الشرائح",
            "إدارة الحسابات",
            "النظام",
            
            
        ]
        
        for module in gestion_modules:
            self.gestion_filter.addItem(module)

    def apply_filter(self):
        """Apply the filter to the history table"""
        if self.parent:
            username = self.username_filter.text()
            event = self.event_filter.currentText() if self.event_filter.currentIndex() > 0 else ""
            date = self.date_filter.date().toString("yyyy-MM-dd") if self.use_date.isChecked() else ""
            gestion = self.gestion_filter.currentText() if self.gestion_filter.currentIndex() > 0 else ""  # NOUVEAU
            self.current_page = 0

            self.parent.apply_filter(username, date, event, gestion)  # NOUVEAU : Passer la gestion
            self.accept()

    def reset_filter(self):
        """Reset the filter fields"""
        self.username_filter.clear()
        self.date_filter.setDate(QDate.currentDate())
        self.use_date.setChecked(False)
        self.event_filter.setCurrentIndex(0)
        self.gestion_filter.setCurrentIndex(0)  # NOUVEAU : Reset gestion filter
        self.current_page = 0

        if self.parent:
            self.parent.reset_filter()
            self.accept()


class HistoryDialog(QMainWindow):
    """
    Vue d'historique standard réutilisable pour tous les modules
    """
    def __init__(self, parent=None, current_user_data=None, session=None, module_name="النظام", gestion_filter=None):
        super().__init__(parent)
        self.parent = parent
        self.current_user_data = current_user_data or {}
        self.module_name = module_name
        self.gestion_filter = gestion_filter  # NOUVEAU : Filtre par gestion
        
        # Initialiser la session et le contrôleur
        if session:
            self.session = session
        else:
            # Créer une nouvelle session si aucune n'est fournie
            self.session = init_db('mysql+pymysql://hr:hr@localhost/HR')
        
        self.history_controller = HistoryController(self.session)
        
        # Données d'historique
        self.history_data = []
        self.filtered_data = []
        self.rows_per_page = 10
        self.current_page = 0

        # Set window properties
        title = f"سجل الأنشطة - {self.module_name}"
        if self.gestion_filter:
            title += f" ({self.gestion_filter})"
        self.setWindowTitle(title)
        self.setMinimumSize(1200, 700)  # Augmenté pour la nouvelle colonne

        # Set dark background color
        self.setStyleSheet(f"background-color: {DARK_BG};")

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 40)

        # Create header with title and filter button
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Create header label
        header_text = f"سجل الأنشطة - {self.module_name}"
        if self.gestion_filter:
            header_text += f" (مرشح حسب: {self.gestion_filter})"
        
        header_label = QLabel(header_text)
        header_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        header_label.setAlignment(Qt.AlignLeading)

        # Create refresh button
        refresh_button = QToolButton()
        refresh_button.setText("⟳")
        refresh_button.setToolTip("تحديث السجل")
        refresh_button.setStyleSheet(f"""
            QToolButton {{
                background-color: {ORANGE};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 18px;
                min-width: 40px;
                min-height: 40px;
                margin-right: 10px;
                
            }}
            QToolButton:hover {{
                background-color: #e05d00;
            }}
        """)
        refresh_button.clicked.connect(self.refresh_history)

        # Create filter button
        filter_dropdown = QWidget()
        filter_dropdown_layout = QHBoxLayout(filter_dropdown)
        filter_dropdown_layout.setContentsMargins(10, 5, 10, 5)
        

        filter_text = QPushButton()
        filter_text.setText("ترشيح")
        filter_text.setToolTip("تصفية السجل")
        filter_text.setStyleSheet(f"""
            QPushButton {{
                background-color: {MEDIUM_BG};
                border: none;
                border-radius: 8px;
                color: {WHITE};
                font-weight: bold;
                font-size: 16px;
                padding: 8px 15px;
                min-width: 80px;
                
            }}
            QPushButton:hover {{
                background-color: #e05d00;
            }}
        """)
        filter_text.setIcon(QIcon("pics/filter icon.png"))
        filter_text.clicked.connect(self.show_filter_dialog)

        filter_dropdown_layout.addWidget(filter_text)
        filter_dropdown_layout.addStretch()

        header_layout.addWidget(filter_dropdown)
        header_layout.addStretch()
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        header_layout.addWidget(refresh_button)

        main_layout.addWidget(header_widget)
        main_layout.addSpacing(20)

        # Create table container
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
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {LIGHT_BG};
            }}
            QTableWidget::item:selected {{
                background-color: {ORANGE};
                color: {WHITE};
            }}
            QHeaderView::section {{
                background-color: {DARKER_BG};
                color: {WHITE};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
            QScrollBar:vertical {{
                background: {MEDIUM_BG};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {LIGHT_BG};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        # Set up columns - NOUVEAU : Ajouter la colonne "الإدارة"
        columns = ["التاريخ", "الوقت", "اسم المستخدم", "الحدث", "الإدارة", "التفاصيل"]

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Set column widths - NOUVEAU : Ajuster pour la nouvelle colonne
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Time
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Username
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Event
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Gestion - NOUVEAU
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Details

        # Add table to layout
        table_layout.addWidget(self.table)
        main_layout.addWidget(table_container)

         # Pagination controls
        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("← السابق")
        self.next_button = QPushButton("التالي →")
        self.page_label = QLabel()

        for btn in [self.prev_button, self.next_button]:
            btn.setStyleSheet(f"""
               QPushButton {{
                background-color: {ORANGE};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
              }}
              QPushButton:hover {{
                 background-color: #e05d00;
            }}
    """)

        self.prev_button.clicked.connect(self.go_to_previous_page)
        self.next_button.clicked.connect(self.go_to_next_page)

        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addStretch()

        main_layout.addLayout(pagination_layout)

        # Create buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        # Close button
        close_btn = QPushButton("إغلاق")
        close_btn.setFixedSize(160, 45)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ORANGE};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e05d00;
            }}
            QPushButton:pressed {{
                background-color: #cc5200;
            }}
        """)
        close_btn.clicked.connect(self.close)

        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)

        main_layout.addSpacing(20)
        main_layout.addLayout(buttons_layout)

        # Set layout direction to RTL for Arabic
        self.setLayoutDirection(Qt.RightToLeft)

        # Load history data
        self.load_history()

    def load_history(self):
        """Load history data using the controller with access control"""
        try:
            print(f"DEBUG - current_user_data reçu: {self.current_user_data}")
            user_id = self.current_user_data.get('account_number')
            username = self.current_user_data.get('username')
            print(f"DEBUG - user_id extrait: {user_id}")
            print(f"DEBUG - username extrait: {username}")           
            if not user_id:
                print("DEBUG - user_id est None ou vide")
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على معرف المستخدم")
                return
            
            # Use the controller's access control method with gestion filter
            success, data, message = self.history_controller.get_history_with_access_control(
                user_id, username, self.gestion_filter  # NOUVEAU : Passer le filtre de gestion
            )
            
            if success:
                self.history_data = data
                self.filtered_data = self.history_data.copy()
                self.populate_table()
                
                # Log successful access - NOUVEAU : Inclure la gestion
                access_details = f"تم الوصول إلى سجل الأنشطة من {self.module_name} بنجاح من قبل المدير: {username}"
                if self.gestion_filter:
                    access_details += f" - مرشح حسب: {self.gestion_filter}"

            else:
                QMessageBox.warning(self, "غير مصرح", message)
                self.close()
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل السجل:\n{str(e)}")
            print(f"Error loading history: {e}")

    def refresh_history(self):
        """Refresh the history data"""
        self.load_history()

    def show_filter_dialog(self):
        """Show the filter dialog"""
        dialog = FilterDialog(self)
        dialog.exec_()

    def apply_filter(self, username, date, event, gestion=""):
        """Apply filter to the history data using the controller - NOUVEAU : Inclure gestion"""
        try:
            user_id = self.current_user_data.get('account_number')
            requesting_username = self.current_user_data.get('username')
            
            success, data, message = self.history_controller.filter_history_with_access_control(
                user_id, username, date, event, requesting_username, gestion  # NOUVEAU : Passer gestion
            )
            
            if success:
                self.filtered_data = data
                self.populate_table()
            else:
                QMessageBox.warning(self, "خطأ", message)
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء التصفية:\n{str(e)}")

    def reset_filter(self):
        """Reset the filter and show all data"""
        self.filtered_data = self.history_data.copy()
        self.populate_table()

    def go_to_next_page(self):
     if (self.current_page + 1) * self.rows_per_page < len(self.filtered_data):
        self.current_page += 1
        self.populate_table()

    def go_to_previous_page(self):
     if self.current_page > 0:
        self.current_page -= 1
        self.populate_table()

    def populate_table(self):
        self.table.setRowCount(0)

        start_index = self.current_page * self.rows_per_page
        end_index = start_index + self.rows_per_page
        page_data = self.filtered_data[start_index:end_index]

        for entry in page_data:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            timestamp_str = entry.get('timestamp', '')
            if isinstance(timestamp_str, str):
                timestamp_parts = timestamp_str.split()
                date = timestamp_parts[0] if len(timestamp_parts) > 0 else ""
                time = timestamp_parts[1] if len(timestamp_parts) > 1 else ""
            else:
                date = timestamp_str.strftime('%Y-%m-%d') if timestamp_str else ""
                time = timestamp_str.strftime('%H:%M:%S') if timestamp_str else ""

            self.table.setItem(row_position, 0, QTableWidgetItem(date))
            self.table.setItem(row_position, 1, QTableWidgetItem(time))
            self.table.setItem(row_position, 2, QTableWidgetItem(entry.get('username', 'غير معروف')))
            self.table.setItem(row_position, 3, QTableWidgetItem(entry.get('event', '')))
            self.table.setItem(row_position, 4, QTableWidgetItem(entry.get('gestion', 'غير محدد')))  # NOUVEAU : Colonne gestion
            self.table.setItem(row_position, 5, QTableWidgetItem(entry.get('details', '')))

        # Mettre à jour l'état des boutons
        total_pages = max(1, (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page)
        self.page_label.setText(f"الصفحة {self.current_page + 1} من {total_pages}")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled((self.current_page + 1) * self.rows_per_page < len(self.filtered_data))

        # NOUVEAU : Titre mis à jour avec info de filtrage
        title = f"سجل الأنشطة - {self.module_name}"
        if self.gestion_filter:
            title += f" ({self.gestion_filter})"
        title += f" ({len(self.filtered_data)} عنصر)"
        self.setWindowTitle(title)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application-wide font for better Arabic text rendering
    font = QFont("Arial", 10)
    app.setFont(font)

    # Set right-to-left layout for Arabic
    app.setLayoutDirection(Qt.RightToLeft)

    # Test data
    test_user_data = {
        'account_number': 1,
        'username': 'admin',
        'role': 'admin'
    }

    window = HistoryDialog()
    window.show()

    sys.exit(app.exec_())
