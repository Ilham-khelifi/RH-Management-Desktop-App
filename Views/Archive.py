import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QFrame, QToolButton, QComboBox, QDialog, QCheckBox,
                            QScrollArea, QFileDialog, QMessageBox)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QSize

# Importer la classe TablePaginator depuis le fichier fourni
from TablePaginator1 import tablepaginator # Assurez-vous que ce fichier est accessible
from Models.DepartDefinitif import DepartDefinitif
from Models.Employe import Employe
from DatabaseConnection import db

import openpyxl
from weasyprint import HTML, CSS
import html # <-- AJOUTÉ pour html.escape()

# Définition des couleurs (comme avant)
DARK_BG = "#263238"
DARKER_BG = "#26282b"
MEDIUM_BG = "#37474f"
LIGHT_BG = "#455a64"
ORANGE = "#ff6a0e"
YELLOW = "#ffc20e"
YELLOW_BTN = "#e6b800"
WHITE = "#ffffff"

class EmployeeArchiveSystem(QWidget): # Changé en QWidget pour l'intégration
    def __init__(self, session=None, current_user_data=None):
        super().__init__()
        
        self.session = session if session else db.get_session()
        self.current_user_data = current_user_data

        # Layout principal pour le widget du module
        module_layout = QVBoxLayout(self)
        module_layout.setContentsMargins(0,0,0,0)
        module_layout.setSpacing(0)
        self.setStyleSheet(f"background-color: {DARK_BG}; color: {WHITE}; font-size: 14px;")

        self.main_page = QWidget()
        self.main_page_layout = QVBoxLayout(self.main_page)
        self.main_page_layout.setContentsMargins(20, 20, 20, 20)
        self.main_page_layout.setSpacing(15)
        
        module_layout.addWidget(self.main_page)

        self.create_action_bar()
        self.create_table_title()
        self.create_table()
        
        self.filter_dialog = None
        self.selected_filter_columns = [] # Initialisation pour le dialogue de filtre
        self._last_filter_value = "" # Pour mémoriser la dernière valeur de filtre
        
        self.load_archives()

    def create_table_title(self):
        """
        Create a title for the main table
        """
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        # Create title label
        title_label = QLabel("جدول الأرشيف")
        title_label.setStyleSheet(f"""
            color: {WHITE};
            font-size: 18px;
            font-weight: bold;
        """)
        title_label.setLayoutDirection(Qt.RightToLeft)
        title_layout.addWidget(title_label)
        
        self.main_page_layout.addWidget(title_container)

    def create_action_bar(self):
        # ... (Identique à la version précédente, s'assure que les chemins d'icônes sont corrects)
        action_bar = QWidget()
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 0, 0, 10) 
        action_layout.setSpacing(10)

        refresh_btn = QPushButton("⟳")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.setToolTip("تحديث الجدول")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MEDIUM_BG}; 
                border: none;
                border-radius: 20px; 
                color: {WHITE};
                font-weight: bold;
                font-size: 22px; 
            }}
            QPushButton:hover {{
                background-color: {LIGHT_BG};
            }}
        """)
        refresh_btn.clicked.connect(self.load_archives)

        filter_btn = QPushButton("ترشيح") 
        # Assurez-vous que le chemin de l'icône est correct. S'il n'est pas trouvé, le bouton n'aura pas d'icône.
        # Vous pouvez utiliser un chemin absolu ou relatif au script en cours d'exécution.
        icon_path = "pics/filter icon.png" # ou os.path.join(os.path.dirname(__file__), "pics", "filter_icon.png")
        if os.path.exists(icon_path):
            filter_btn.setIcon(QIcon(icon_path))
        else:
            print(f"Avertissement : L'icône de filtre '{icon_path}' n'a pas été trouvée.")
            filter_btn.setText("ترشيح  lọc") # Texte de secours si l'icône manque

        filter_btn.setIconSize(QSize(18,18))
        filter_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MEDIUM_BG};
                border: none;
                border-radius: 8px;
                color: {WHITE};
                font-weight: bold;
                font-size: 14px; 
                padding: 8px 15px;
                min-width: 90px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_BG};
            }}
        """)
        filter_btn.clicked.connect(self.show_filter_dialog)
        
        action_layout.addWidget(refresh_btn)
        action_layout.addWidget(filter_btn)
        action_layout.addStretch() 
        
        self.main_page_layout.addWidget(action_bar)


    def show_filter_dialog(self):
        # ... (Identique à la version précédente, s'assure de la logique de restauration des valeurs)
        if not self.filter_dialog:
            self.filter_dialog = QDialog(self)
            self.filter_dialog.setWindowTitle("ترشيح الأعمدة") 
            self.filter_dialog.setFixedWidth(380) 
            self.filter_dialog.setStyleSheet(f"background-color: {MEDIUM_BG}; color: {WHITE}; font-size: 16px;")
            
            dialog_layout = QVBoxLayout(self.filter_dialog)
            dialog_layout.setContentsMargins(15, 15, 15, 15)
            dialog_layout.setSpacing(10)
            
            title_label = QLabel("اختر الأعمدة للبحث فيها:")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
            dialog_layout.addWidget(title_label)
            
            columns = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            
            self.filter_checkboxes = {}
            
            for column in columns:
                checkbox = QCheckBox(column)
                checkbox.setStyleSheet(f"""
                    QCheckBox {{
                        font-size: 14px;
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
                dialog_layout.addWidget(checkbox)
                self.filter_checkboxes[column] = checkbox
                
             # Entrée de valeur de filtre
            filter_value_layout = QHBoxLayout()
            filter_value_layout.setSpacing(10) 
            
            filter_value_label = QLabel("قيمة الفلترة:")
            filter_value_label.setStyleSheet("font-size: 14px; ")
            
            self.filter_value_input = QLineEdit()
            self.filter_value_input.setPlaceholderText("أدخل قيمة للفلترة...")
            self.filter_value_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {WHITE};
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    color: #000000;
                    font-size: 13px;
                    text-align: right;
                }}
            """)
            
            filter_value_layout.addWidget(filter_value_label)
            filter_value_layout.addWidget(self.filter_value_input)
            
            dialog_layout.addSpacing(15)
            dialog_layout.addLayout(filter_value_layout)
            
            # Boutons
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
                    font-size: 16px;
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
                    font-size: 16px;
                    min-width: 120px;
                }}
                QPushButton:hover {{
                    background-color: {LIGHT_BG};
                }}
            """)
            cancel_btn.clicked.connect(self.filter_dialog.reject)
            
            # Inverser l'ordre pour RTL
            buttons_layout.addWidget(apply_btn)
            buttons_layout.addWidget(cancel_btn)
            
            dialog_layout.addSpacing(15)
            dialog_layout.addLayout(buttons_layout)
        
        # Afficher la boîte de dialogue
        self.filter_dialog.exec_()
        
    def apply_filter(self):
        self.selected_filter_columns = [col for col, cb in self.filter_checkboxes.items() if cb.isChecked()]
        self._last_filter_value = self.filter_value_input.text().strip().lower()

        if not self._last_filter_value or not self.selected_filter_columns:
            self.paginator.reset_filter() # Le paginateur montrera toutes les lignes de self.table, paginées
            if self.filter_dialog: self.filter_dialog.accept()
            return

        column_indices_to_search_in_table_model = [] # Indices des colonnes dans le modèle de la table
        all_headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
        for col_name in self.selected_filter_columns:
            try:
                column_indices_to_search_in_table_model.append(all_headers.index(col_name))
            except ValueError:
                print(f"Avertissement : La colonne de filtre '{col_name}' n'a pas été trouvée.")
        
        if not column_indices_to_search_in_table_model: # Si aucune colonne valide n'est sélectionnée pour le filtre
            self.paginator.reset_filter()
            if self.filter_dialog: self.filter_dialog.accept()
            return

        # Parcourir toutes les lignes ACTUELLEMENT DANS self.table et trouver celles qui correspondent
        # Le QTableWidget (self.table) contient TOUTES les données après load_archives.
        indices_des_lignes_filtrees_dans_la_table = []
        for r in range(self.table.rowCount()):
            matches_filter = False
            for col_idx in column_indices_to_search_in_table_model:
                item = self.table.item(r, col_idx)
                if item and self._last_filter_value in item.text().lower():
                    matches_filter = True
                    break 
            if matches_filter:
                indices_des_lignes_filtrees_dans_la_table.append(r)
        
        # Passer la liste des indices de lignes filtrées au paginateur
        self.paginator.handle_filter_changed(indices_des_lignes_filtrees_dans_la_table)

        if self.filter_dialog: self.filter_dialog.accept()

    def create_table(self):
        # ... (Identique à la version précédente)
        table_container = QWidget()
        table_container.setStyleSheet(f"background-color:{MEDIUM_BG}; border-radius: 8px; margin: 0px;")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(15, 15, 15, 15) 
        
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
        
        columns = [
            "رقم الأرشيف", "رقم الموظف", "لقب الموظف", "اسم الموظف",
            "رقم القرار", "تاريخ القرار", "تاريخ المغادرة", "سبب المغادرة"
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        table_layout.addWidget(self.table)
        
        self.paginator = tablepaginator(self.table, rows_per_page=10)
        table_layout.addWidget(self.paginator)
        self.main_page_layout.addWidget(table_container)

    def load_archives(self):
            # 1. Créer une session locale si aucune n’est fournie
        current_session = self.session if self.session else db.get_session()
        is_new_session = not self.session

        # 2. Réinitialiser le tableau
        self.table.setRowCount(0)

        try:
            # 3. Récupération des archives depuis la base de données
            db_archives = current_session.query(DepartDefinitif).join(DepartDefinitif.employe).all()

            # 4. Remplissage du tableau ligne par ligne
            for archive in db_archives:
                employe = archive.employe
                row_pos = self.table.rowCount()
                self.table.insertRow(row_pos)
                print("ID:", str(archive.iddepartdefinitif), "Numéro décision:", archive.Numerodecision)
                values = [
                    str(archive.iddepartdefinitif),
                    str(employe.idemploye) if employe else "",
                    employe.Nom if employe else "",
                    employe.Prenom if employe else "",
                    str(archive.Numerodecision) if archive.Numerodecision else"", 
                    archive.Datedecision.strftime("%Y-%m-%d") if archive.Datedecision else "",
                    archive.Datedepartdefinitif.strftime("%Y-%m-%d") if archive.Datedepartdefinitif else "",
                    archive.Motif or ""
                ]

                for col, val in enumerate(values):
                    item = QTableWidgetItem(val)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_pos, col, item)

                # 5. Stocker l’ID dans UserRole pour récupération ultérieure
                self.table.item(row_pos, 0).setData(Qt.UserRole, archive.iddepartdefinitif)

            # 6. Mettre à jour le paginateur
            if self.table.rowCount() > 0:
                self.paginator.reset_filter()
            else:
                self.paginator.total_rows = 0
                self.paginator.total_pages = 1
                self.paginator.current_page = 1
                self.paginator.update_page(1)

        except Exception as e:
            QMessageBox.critical(self, "خطأ في التحميل", f"حدث خطأ أثناء تحميل بيانات الأرشيف:\n{e}")
            print(f"[Erreur] Chargement des archives : {e}")

        finally:
            if is_new_session:
                current_session.close()

    # --- MÉTHODES D'EXPORTATION ET D'IMPRESSION (AJUSTÉES) ---
    def update_data(self):
            # Your code to reload or refresh data, e.g.:
            self.load_archives()
    def _get_table_data_as_lists(self):
        """
        Helper function to extract data ONLY from VISIBLE rows in QTableWidget.
        This respects pagination (only current page) and any visual filtering applied
        directly to the QTableWidget's rows visibility.
        """
        if not self.table or self.table.rowCount() == 0:
            return None, None

        headers = [self.table.horizontalHeaderItem(i).text()
                   for i in range(self.table.columnCount())]

        visible_row_data = []
        for row in range(self.table.rowCount()):
            # La condition clé : exporter seulement si la ligne n'est PAS cachée
            if not self.table.isRowHidden(row):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                visible_row_data.append(row_data)
            
        return headers, visible_row_data

    def export_data_to_excel(self):
        print(f"{self.__class__.__name__}: export_data_to_excel (visible rows only) called")
        headers, data = self._get_table_data_as_lists() # Récupère seulement les lignes visibles

        if not data:
            QMessageBox.information(self, "لا بيانات للتصدير", "لا توجد صفوف ظاهرة في الجدول حاليًا للتصدير.")
            return

        # Le reste de la fonction est identique à la version précédente
        filePath, _ = QFileDialog.getSaveFileName(self, "تصدير إلى Excel (الصفحة الحالية)", os.path.expanduser("~/Documents/Archives_Page_Actuelle.xlsx"),
                                                  "Excel Workbook (*.xlsx);;All Files (*)")

        if not filePath:
            return

        try:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "الأرشيف - الصفحة الحالية"
            sheet.sheet_view.rightToLeft = True
            sheet.append(headers)

            for row_values in data:
                sheet.append(row_values)

            for col_idx, column_cells in enumerate(sheet.columns):
                length = max(len(str(cell.value) or "") for cell in column_cells)
                sheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx + 1)].width = length + 5

            workbook.save(filePath)
            QMessageBox.information(self, "نجاح التصدير", f"تم تصدير الصفوف الظاهرة بنجاح إلى:\n{filePath}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ في التصدير", f"حدث خطأ أثناء تصدير الملف: {e}")
            print(f"Error exporting to Excel: {e}")

    def print_data_to_pdf(self):
        print(f"{self.__class__.__name__}: print_data_to_pdf (visible rows only) called")
        headers, data = self._get_table_data_as_lists() # Récupère seulement les lignes visibles

        if not data:
            QMessageBox.information(self, "لا بيانات للطباعة", "لا توجد صفوف ظاهرة في الجدول حاليًا للطباعة.")
            return

        # Le reste de la fonction est identique à la version précédente
        filePath, _ = QFileDialog.getSaveFileName(self, "طباعة إلى PDF (الصفحة الحالية)", os.path.expanduser("~/Documents/Archives_Page_Actuelle.pdf"),
                                                  "PDF Document (*.pdf);;All Files (*)")
        if not filePath:
            return

        html_content = "<html><head><meta charset='UTF-8'>"
        html_content += """
        <style>
            @font-face { font-family: 'DejaVu Sans'; src: url('fonts/DejaVuSans.ttf'); }
            body { direction: rtl; font-family: 'Arial', 'DejaVu Sans', sans-serif; font-size: 9pt; } /* Taille police réduite pour PDF */
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #333; padding: 4px; text-align: right; word-wrap: break-word; }
            th { background-color: #f0f0f0; font-weight: bold; }
            caption { font-size: 1.1em; font-weight: bold; margin-bottom: 8px; text-align: center; }
        </style>
        </head><body>
        """
        html_content += "<table><caption>سجل الأرشيف (الصفحة الحالية)</caption><thead><tr>"
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
            css_style = CSS(string='@page { size: A4 landscape; margin: 1cm; }')
            HTML(string=html_content).write_pdf(filePath, stylesheets=[css_style])
            QMessageBox.information(self, "نجاح الطباعة", f"تم إنشاء ملف PDF للصفوف الظاهرة بنجاح:\n{filePath}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ في الطباعة", f"حدث خطأ أثناء إنشاء ملف PDF: {e}\n"
                                 "تأكد أن WeasyPrint et ses dépendances (Pango, Cairo) sont correctement installés.")
            print(f"Error printing to PDF: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Arial", 11)
    app.setFont(font)
    app.setLayoutDirection(Qt.RightToLeft)
    
    window_module = EmployeeArchiveSystem() # C'est maintenant un QWidget
    
    main_test_window = QMainWindow()
    main_test_window.setWindowTitle("Test du Module d'Archive (QWidget)")
    main_test_window.setGeometry(50, 50, 1100, 700)

    # Container pour le module et les boutons de test
    test_container_widget = QWidget()
    main_test_layout_container = QVBoxLayout(test_container_widget)
    
    main_test_layout_container.addWidget(window_module) # Ajoute le module QWidget

    # Barre de boutons de test en bas
    test_buttons_layout = QHBoxLayout()
    btn_export_excel = QPushButton("Test Export Excel (Page Actuelle)")
    btn_print_pdf = QPushButton("Test Print PDF (Page Actuelle)")
    btn_export_excel.clicked.connect(window_module.export_data_to_excel)
    btn_print_pdf.clicked.connect(window_module.print_data_to_pdf)
    
    bottom_bar = QWidget()
    bottom_bar.setLayout(test_buttons_layout)
    test_buttons_layout.addWidget(btn_export_excel)
    test_buttons_layout.addWidget(btn_print_pdf)
    
    main_test_layout_container.addWidget(bottom_bar)
    
    main_test_window.setCentralWidget(test_container_widget)
    main_test_window.show()
    
    sys.exit(app.exec_())