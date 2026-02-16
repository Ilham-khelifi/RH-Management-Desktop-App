from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

DARK_BG = "#263238"      # Dark background color
DARKER_BG = "#26282b"    # Darker background for contrast
MEDIUM_BG = "#37474f"    # Medium background for containers
LIGHT_BG = "#455a64"     # Light background for hover states
ORANGE = "#ff6a0e"       # Primary accent color
YELLOW = "#ffc20e"       # Secondary accent color
YELLOW_BTN = "#e6b800"   # Button color
WHITE = "#ffffff"        # Text color
BLACK = "#000000"        # Black text color
GRAY = "#8f8f8f"         # Gray for secondary text
GREEN = "#4CAF50"        # Success color
RED = "#f44336"          # Error/Delete color


class StyledMessageDialog(QDialog):
    def __init__(self, parent, title, message, message_type="info"):
        super().__init__(parent)

        # Dialog settings
        self.setWindowTitle(title)
        self.setFixedSize(600, 300)
        self.setStyleSheet(f"background-color: {DARKER_BG};")

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(30)

        # Title label
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {YELLOW}; font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Message label
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet(f"color: {WHITE}; font-size: 16px;")
        layout.addWidget(message_label)

        # Button
        button = QPushButton("موافق")
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {GREEN};
                color: {WHITE};
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: #3d8b40;
            }}
        """)
        button.clicked.connect(self.accept)

        layout.addWidget(button)

        # Depending on message type, change colors or icons (if needed)
        if message_type == "warning":
            self.setStyleSheet(f"background-color: {RED};")  # Red background for warning

        # If you need other customizations based on message type, you can add them here


# Usage:
def show_custom_warning(self):
    dialog = StyledMessageDialog(self, title="تحذير", message="يرجى تحديد صف للتعديل.", message_type="warning")
    dialog.exec_()


def show_custom_info(self):
    dialog = StyledMessageDialog(self, title="تم الحفظ", message="تم حفظ التعديلات بنجاح.", message_type="info")
    dialog.exec_()


