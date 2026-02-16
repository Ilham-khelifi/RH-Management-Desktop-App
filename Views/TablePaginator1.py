from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from ui_constants import *


class tablepaginator(QWidget):
    """
    A reusable pagination widget for QTableWidget
    Provides navigation controls and handles pagination logic
    """
    pageChanged = pyqtSignal(int)  # Signal emitted when page changes

    def __init__(self, table=None, rows_per_page=10):
        """
        Initialize the paginator

        Parameters:
        - table: The QTableWidget to paginate
        - rows_per_page: Number of rows to display per page (fixed at 10)
        """
        super().__init__()
        self.table = table
        self.rows_per_page = 10  # Fixed at 10 rows per page
        self.current_page = 1
        self.total_pages = 1
        self.total_rows = 0
        self.filtered_rows = []  # For storing filtered row indices
        self.is_filtered = False

        # Set up the UI
        self.setup_ui()

        # Connect to the table if provided
        if self.table:
            self.connect_to_table(self.table)

    def setup_ui(self):
        """Set up the paginator UI"""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Add stretch to center the controls
        layout.addStretch()

        # Previous page button
        self.prev_btn = QPushButton("<")
        self.prev_btn.setToolTip("الصفحة السابقة")
        self.prev_btn.setFixedSize(40, 30)
        self.prev_btn.clicked.connect(self.go_to_prev_page)

        # Page indicator
        self.page_label = QLabel("صفحة 1 من 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setMinimumWidth(120)

        # Next page button
        self.next_btn = QPushButton(">")
        self.next_btn.setToolTip("الصفحة التالية")
        self.next_btn.setFixedSize(40, 30)
        self.next_btn.clicked.connect(self.go_to_next_page)

        # Style the widgets
        self.style_widgets()

        # Add widgets to layout
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.page_label)
        layout.addWidget(self.next_btn)

        # Add stretch to center the controls
        layout.addStretch()

        # Set layout direction to RTL for Arabic
        self.setLayoutDirection(Qt.RightToLeft)

    def style_widgets(self):
        """Apply styling to the paginator widgets"""
        # Common button style
        button_style = f"""
            QPushButton {{
                background-color: {MEDIUM_BG};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_BG};
            }}
            QPushButton:disabled {{
                background-color: #555555;
                color: #888888;
            }}
        """

        # Apply styles
        self.prev_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)

        self.page_label.setStyleSheet(f"color: {WHITE}; font-size: 16px;")

    def connect_to_table(self, table):
        """
        Connect the paginator to a QTableWidget

        Parameters:
        - table: The QTableWidget to paginate
        """
        self.table = table
        self.update_total_rows()
        self.update_page(1)

    def update_total_rows(self):
        """Update the total number of rows and pages"""
        if not self.table:
            return

        if self.is_filtered:
            self.total_rows = len(self.filtered_rows)
        else:
            self.total_rows = self.table.rowCount()

        self.total_pages = max(1, (self.total_rows + self.rows_per_page - 1) // self.rows_per_page)

        # Update page label
        self.page_label.setText(f"صفحة {self.current_page} من {self.total_pages}")

        # Update button states
        self.update_button_states()

    def update_button_states(self):
        """Update the enabled/disabled state of navigation buttons"""
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

    def update_page(self, page):
        """
        Update the current page and show the corresponding rows

        Parameters:
        - page: The page number to display
        """
        if not self.table:
            return

        # Validate page number
        page = max(1, min(page, self.total_pages))
        self.current_page = page

        # Calculate start and end indices
        start_idx = (page - 1) * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, self.total_rows)

        # Hide all rows first
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, True)

        # Show only rows for the current page
        if self.is_filtered:
            for i in range(start_idx, end_idx):
                if i < len(self.filtered_rows):
                    self.table.setRowHidden(self.filtered_rows[i], False)
        else:
            for row in range(start_idx, end_idx):
                self.table.setRowHidden(row, False)

        # Update page label and button states
        self.page_label.setText(f"صفحة {self.current_page} من {self.total_pages}")
        self.update_button_states()

        # Emit signal
        self.pageChanged.emit(self.current_page)

    def go_to_prev_page(self):
        """Go to the previous page"""
        self.update_page(self.current_page - 1)

    def go_to_next_page(self):
        """Go to the next page"""
        self.update_page(self.current_page + 1)

    def handle_filter_changed(self, filtered_rows=None):
        """
        Handle when table filtering changes

        Parameters:
        - filtered_rows: List of row indices that match the filter
        """
        if filtered_rows is not None:
            self.filtered_rows = filtered_rows
            self.is_filtered = True
        else:
            self.is_filtered = False
            self.filtered_rows = []

        self.update_total_rows()
        self.update_page(1)  # Reset to first page

    def reset_filter(self):
        """Reset any applied filters"""
        self.is_filtered = False
        self.filtered_rows = []
        self.update_total_rows()
        self.update_page(1)  # Reset to first page