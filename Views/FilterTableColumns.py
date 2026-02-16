
import warnings
# Suppress the DeprecationWarning about sipPyTypeDict
warnings.filterwarnings("ignore", category=DeprecationWarning, module="PyQt5.sip")

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget, QGroupBox,
                             QMessageBox, QListWidget, QListWidgetItem, QAbstractItemView)
from PyQt5.QtCore import Qt

# UI Constants
DARK_BG = "#263238"
MEDIUM_BG = "#37474F"
LIGHT_BG = "#455A64"
DARKER_BG = "#1e272e"
WHITE = "#ECEFF1"
ORANGE = "#e67e22"

# REMOVED THE PROBLEMATIC LINE: from filter_table_columns import FilterTableColumnsWindow

class FilterTableColumnsWindow(QDialog):
    def __init__(self, parent=None, headers=None):
        super().__init__(parent)
        self.parent = parent
        self.headers = headers or []
        self.selected_columns = list(range(len(self.headers)))  # Initially all columns are selected
        self.setWindowTitle("ترشيح أعمدة الجدول")
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: {DARK_BG};
                color: {WHITE};
            }
            QLabel {
                color: {WHITE};
            }
            QCheckBox {
                color: {WHITE};
            }
            QGroupBox {
                color: {WHITE};
                font-weight: bold;
                border: 1px solid {LIGHT_BG};
                border-radius: 4px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #e67e22;
                color: {WHITE};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton#cancelBtn {
                background-color: {LIGHT_BG};
            }
            QPushButton#cancelBtn:hover {
                background-color: #546E7A;
            }
            QListWidget {
                background-color: {MEDIUM_BG};
                color: {WHITE};
                border: 1px solid {LIGHT_BG};
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid {LIGHT_BG};
            }
            QListWidget::item:selected {
                background-color: #e67e22;
                color: {WHITE};
            }
            QScrollArea {
                border: none;
                background-color: {DARK_BG};
            }
            QScrollBar:vertical {
                background: transparent;
                width: 0px;  /* Hide scrollbar but keep functionality */
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: transparent;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QWidget#headerSection {
                background-color: #1e272e;
                border-radius: 4px;
                margin: 5px;
                padding: 10px;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Header section
        header_section = QWidget()
        header_section.setObjectName("headerSection")
        header_layout = QVBoxLayout(header_section)

        title_label = QLabel("ترشيح أعمدة الجدول")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        description_label = QLabel("حدد الأعمدة التي تريد عرضها في الجدول وترتيبها")
        description_label.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(title_label)
        header_layout.addWidget(description_label)

        main_layout.addWidget(header_section)

        # Create a scroll area for the column options
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container for column options
        column_container = QWidget()
        column_layout = QVBoxLayout(column_container)

        # Create column selection group
        columns_group = QGroupBox("الأعمدة المتاحة")
        columns_layout = QVBoxLayout(columns_group)

        # Instructions
        instructions_label = QLabel("حدد الأعمدة التي تريد عرضها واستخدم الأزرار لتغيير ترتيبها")
        instructions_label.setStyleSheet("color: #bdc3c7; margin-bottom: 10px;")
        columns_layout.addWidget(instructions_label)

        # Create a list widget for column selection with checkboxes
        self.columns_list = QListWidget()
        self.columns_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.columns_list.setDragDropMode(QAbstractItemView.InternalMove)

        # Add columns to the list widget
        for i, header in enumerate(self.headers):
            item = QListWidgetItem(header)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)  # Initially all columns are checked
            self.columns_list.addItem(item)

        columns_layout.addWidget(self.columns_list)

        # Buttons for reordering columns
        reorder_buttons = QHBoxLayout()

        move_up_btn = QPushButton("نقل لأعلى")
        move_up_btn.clicked.connect(self.move_column_up)

        move_down_btn = QPushButton("نقل لأسفل")
        move_down_btn.clicked.connect(self.move_column_down)

        select_all_btn = QPushButton("تحديد الكل")
        select_all_btn.clicked.connect(self.select_all_columns)

        deselect_all_btn = QPushButton("إلغاء تحديد الكل")
        deselect_all_btn.clicked.connect(self.deselect_all_columns)

        reorder_buttons.addWidget(move_up_btn)
        reorder_buttons.addWidget(move_down_btn)
        reorder_buttons.addWidget(select_all_btn)
        reorder_buttons.addWidget(deselect_all_btn)

        columns_layout.addLayout(reorder_buttons)
        column_layout.addWidget(columns_group)

        scroll_area.setWidget(column_container)
        main_layout.addWidget(scroll_area)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.apply_btn = QPushButton("تأكيد")
        self.apply_btn.clicked.connect(self.apply_column_filter)

        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)

        self.reset_btn = QPushButton("إعادة ضبط")
        self.reset_btn.clicked.connect(self.reset_columns)

        buttons_layout.addWidget(self.apply_btn)
        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(buttons_layout)

    def move_column_up(self):
        """Move the selected column up in the list"""
        current_row = self.columns_list.currentRow()
        if current_row > 0:
            item = self.columns_list.takeItem(current_row)
            self.columns_list.insertItem(current_row - 1, item)
            self.columns_list.setCurrentRow(current_row - 1)

    def move_column_down(self):
        """Move the selected column down in the list"""
        current_row = self.columns_list.currentRow()
        if current_row < self.columns_list.count() - 1:
            item = self.columns_list.takeItem(current_row)
            self.columns_list.insertItem(current_row + 1, item)
            self.columns_list.setCurrentRow(current_row + 1)

    def select_all_columns(self):
        """Select all columns"""
        for i in range(self.columns_list.count()):
            item = self.columns_list.item(i)
            item.setCheckState(Qt.Checked)

    def deselect_all_columns(self):
        """Deselect all columns"""
        for i in range(self.columns_list.count()):
            item = self.columns_list.item(i)
            item.setCheckState(Qt.Unchecked)

    def reset_columns(self):
        """Reset column selection and order to default"""
        self.columns_list.clear()

        # Add columns to the list widget in original order
        for i, header in enumerate(self.headers):
            item = QListWidgetItem(header)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)  # Initially all columns are checked
            self.columns_list.addItem(item)

    def get_selected_columns(self):
        """Get the selected columns and their order"""
        selected_columns = []
        column_order = []

        for i in range(self.columns_list.count()):
            item = self.columns_list.item(i)
            header_text = item.text()

            # Find the original index of this header
            original_index = self.headers.index(header_text)

            # If the column is checked, add it to the selected columns
            if item.checkState() == Qt.Checked:
                selected_columns.append(original_index)
                column_order.append(header_text)

        return selected_columns, column_order

    def apply_column_filter(self):
        """Apply the column filter and close the dialog"""
        selected_columns, column_order = self.get_selected_columns()

        if not selected_columns:
            QMessageBox.warning(self, "تحذير", "يجب تحديد عمود واحد على الأقل")
            return

        # Pass the selected columns to the parent window
        if self.parent and hasattr(self.parent, "apply_column_filter"):
            self.parent.apply_column_filter(selected_columns, column_order)
            self.accept()
        else:
            QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء تطبيق ترشيح الأعمدة")
            print("Parent window does not have apply_column_filter method")