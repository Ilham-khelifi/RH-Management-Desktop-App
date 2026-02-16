import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QPushButton,
                             QHBoxLayout, QVBoxLayout, QLabel, QToolButton)

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import pyqtSignal

# Import constants - assuming ui_constants.py is in the same directory
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



def create_top_bar(parent, content_layout, sidebar_toggle,excel_export_action_callback=None,
                   pdf_print_action_callback=None):
    """
    Create the top bar with action buttons and search functionality

    Parameters:
    - parent: The parent widget that will contain the top bar
    - content_layout: The layout where the top bar will be added
    - sidebar_toggle: The sidebar toggle button to be added to the top bar
    - excel_export_action_callback: Function to call when export button is clicked
    - pdf_print_action_callback: Function to call when print button is clicked
    Returns:
    - top_bar: The top bar widget
    - export_btn: The export button widget
    - print_btn: The print button widget

    """
    print("Topbar function imported and running!")

    top_bar = QWidget()
    top_bar.setFixedHeight(60)
    top_bar.setStyleSheet(f"background-color: {DARK_BG}; border-bottom: 1px solid {LIGHT_BG};")

    top_layout = QHBoxLayout(top_bar)
    top_layout.setContentsMargins(15, 10, 15, 10)

    # Right side - action buttons
    right_widget = QWidget()
    right_layout = QHBoxLayout(right_widget)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(20)  # Increased spacing

    # Export button with icon
    export_btn = QToolButton()
    export_btn.setFixedSize(45, 45)  # Increased size
    export_btn.setStyleSheet(f"""
        QToolButton {{
            background-color: transparent;
            border: none;
            color: {WHITE};
            font-size: 16px;
        }}
        QToolButton:hover {{
            background-color: {LIGHT_BG};
            border-radius: 22px;
        }}
    """)

    # Load export icon from pics folder
    export_icon = QPixmap("pics/export.png")
    if not export_icon.isNull():
        export_icon = export_icon.scaled(25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        export_btn.setIcon(QIcon(export_icon))
        export_btn.setIconSize(QSize(25, 25))
    else:
        export_btn.setText("↓")
        print("Failed to load export icon: pics/export.png")
    
    export_btn.setToolTip("تصدير")
    if excel_export_action_callback:
        export_btn.clicked.connect(excel_export_action_callback)
        
    # Print button with icon
    print_btn = QToolButton()
    print_btn.setFixedSize(45, 45)  # Increased size
    print_btn.setStyleSheet(f"""
        QToolButton {{
            background-color: transparent;
            border: none;
            color: {WHITE};
            font-size: 16px;
        }}
        QToolButton:hover {{
            background-color: {LIGHT_BG};
            border-radius: 22px;
        }}
    """)
    
    # Load print icon from pics folder
    print_icon = QPixmap("pics/imprime.png")
    if not print_icon.isNull():
        print_icon = print_icon.scaled(25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        print_btn.setIcon(QIcon(print_icon))
        print_btn.setIconSize(QSize(25, 25))
    else:
        print_btn.setText("🖨️")
        print("Failed to load print icon: pics/imprime.png")

    print_btn.setToolTip("طباعة")
    if pdf_print_action_callback:
        print_btn.clicked.connect(pdf_print_action_callback)
    
    right_layout.addWidget(export_btn)
    right_layout.addWidget(print_btn)
    
    
    # Add sidebar toggle to top bar (left side)
    top_layout.addWidget(sidebar_toggle)
    top_layout.addStretch()
    top_layout.addStretch()
    top_layout.addWidget(right_widget)  # Now on the right side

    content_layout.addWidget(top_bar)

    return top_bar,export_btn, print_btn


# Helper function to get absolute path to pics folder
def get_pics_path():
    """
    Returns the absolute path to the pics folder
    This is useful if your script is run from different locations
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Join with the pics folder name
    pics_path = os.path.join(script_dir, "pics")
    return pics_path


# Test function to demonstrate the topbar
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set application-wide font for Arabic support
    from PyQt5.QtGui import QFont

    font = QFont("Arial", 10)
    app.setFont(font)

    # Set right-to-left layout for Arabic
    app.setLayoutDirection(Qt.RightToLeft)

    # Create a simple window to test the topbar
    from PyQt5.QtWidgets import QMainWindow

    window = QMainWindow()
    window.setWindowTitle("Topbar Test")
    window.setGeometry(100, 100, 800, 600)

    # Set up the central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    # Main layout
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)

    # Create a dummy sidebar toggle button for testing
    sidebar_toggle = QPushButton()

    sidebar_toggle.setIcon(QIcon("pics/sidebar_icon.png"))
    sidebar_toggle.setIconSize(QSize(20, 20))  # Smaller icon size
    sidebar_toggle.setFixedSize(35, 35)  # Smaller button size
    sidebar_toggle.setToolTip("إظهار/إخفاء القائمة الجانبية")
    sidebar_toggle.setStyleSheet(f"""
            QToolButton {{
                background-color: {LIGHT_BG};  /* Background color like hover */
                border: none;
                color: {WHITE};
                border-radius: 17px;  /* Circular background */
                font-size: 16px;
            }}
            QToolButton:hover {{
                background-color: {DARK_BG};
            }}
        """)
    # Create topbar
    top_bar = create_top_bar(window, main_layout, sidebar_toggle)

    # Add a placeholder for the main content
    placeholder = QLabel("Main Content Area")
    placeholder.setAlignment(Qt.AlignCenter)
    placeholder.setStyleSheet("font-size: 24px;")
    main_layout.addWidget(placeholder)

    window.show()
    sys.exit(app.exec_())