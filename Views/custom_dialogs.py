from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from ui_constants import *

class CustomWarningDialog(QDialog):
    def __init__(self, parent=None, title="تحذير", message=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 180)
        self.setStyleSheet(f"background-color: {DARKER_BG};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {YELLOW}; font-size: 18px; font-weight: bold;")

        msg_box = QLabel(message)
        msg_box.setAlignment(Qt.AlignCenter)
        msg_box.setStyleSheet(f"color: {WHITE}; font-size: 16px;")

        ok_btn = QPushButton("موافق")
        ok_btn.setFixedSize(150, 40)
        ok_btn.setStyleSheet(f"""
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
        ok_btn.clicked.connect(self.accept)

        layout.addWidget(title_label)
        layout.addWidget(msg_box)
        layout.addWidget(ok_btn, 0, Qt.AlignCenter)


class CustomInfoDialog(QDialog):
    def __init__(self, parent=None, title="معلومات", message=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 180)
        self.setStyleSheet(f"background-color: {DARKER_BG};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {GREEN}; font-size: 20px; font-weight: bold;")

        msg_box = QLabel(message)
        msg_box.setAlignment(Qt.AlignCenter)
        msg_box.setStyleSheet(f"color: {WHITE}; font-size: 18px;")

        ok_btn = QPushButton("موافق")
        ok_btn.setFixedSize(150, 40)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GREEN};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #3d8b40;
            }}
        """)
        ok_btn.clicked.connect(self.accept)

        layout.addWidget(title_label)
        layout.addWidget(msg_box)
        layout.addWidget(ok_btn, 0, Qt.AlignCenter)


class CustomMessageBox(QDialog):
    def __init__(self, parent=None, title="تأكيد", message="هل أنت متأكد؟"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)
        self.setStyleSheet(f"background-color: {DARKER_BG};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setStyleSheet(f"color: {WHITE}; font-size: 20px;")
        layout.addWidget(msg_label)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.delete_btn = QPushButton("احذف")
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GREEN};
                color: {WHITE};
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #3d8b40;
            }}
        """)
        self.delete_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED};
                color: {WHITE};
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #d32f2f;
            }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.delete_btn)
        
        layout.addLayout(buttons_layout)