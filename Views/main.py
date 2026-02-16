import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
                             QVBoxLayout, QHBoxLayout )
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Views.Evaluation import Evaluation
from Views.Absence import AbsenceManagementSystem
from Views.Archive import EmployeeArchiveSystem
from Views.GestionConge import LeaveManagementSystem
from Views.GestionFormation import FormationManagementSystem
from ui_constants import *
from Views.MainEmployePage import MainEmployeeWindow
from sidebar import create_sidebar
from topbar import create_top_bar
from gestionComptes import CompteManagementSystem

class HRMSMainWindow(QMainWindow):
    def __init__(self, session, current_user_data=None):
        """
        Initialize the main application window that contains all modules
        """
        super().__init__()
        
        # IMPORTANT: Stocker la session reçue de login_integrated
        self.session = session
        self.current_user_data = current_user_data 
        
        self.setWindowTitle("نظام إدارة الموارد البشرية")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(500, 500)
        self.setStyleSheet(f"background-color: {DARK_BG}; color: {WHITE};")

        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create sidebar with active module tracking
        print("DEBUG - Appel de create_sidebar avec current_user_data")
        self.sidebar, self.sidebar_toggle, self.logout_btn = create_sidebar(
            self,
            self.main_layout,
            active_module="إدارة الموظفين",  # Module par défaut
            on_module_change=self.switch_module,
            on_logout=self.handle_logout,
            current_user_data=current_user_data
        )

        # Create main content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Create top bar
        # Top bar
        self.top_bar, self.top_bar_export_btn, self.top_bar_print_btn = create_top_bar(
            self,
            self.content_layout, 
            self.sidebar_toggle,
            excel_export_action_callback=self.proxy_export_excel_action,
            pdf_print_action_callback=self.proxy_print_pdf_action
        )

        # Create stacked widget to hold different modules
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)
        # Add content to main layout
        self.main_layout.addWidget(self.content_widget)
        # Initialize modules
        self.initialize_modules()



    def handle_logout(self):
        """Log out and return to login screen"""
        from login_integrated import DatabaseIntegratedLoginWindow

        # Create and show the login window
        self.login_window = DatabaseIntegratedLoginWindow()
        self.login_window.show()

        # Close the current window
        self.close()

    def initialize_modules(self):
        """
        Initialize all modules and add them to the stacked widget
        """
        
        # IMPORTANT: Passer la session à MainEmployeeWindow
        
        
        self.employee_module = MainEmployeeWindow(
            session=self.session,  # Passer la session ici
            current_user_data=self.current_user_data,
            external_sidebar=self.sidebar,
            external_sidebar_toggle=self.sidebar_toggle,
            logout_btn=self.logout_btn

        )       
        
        self.formation_module = FormationManagementSystem(current_user_data=self.current_user_data,session=self.session)
        self.leave_module = LeaveManagementSystem(current_user_data=self.current_user_data, session=self.session)
        self.Compte_module = CompteManagementSystem(current_user_data=self.current_user_data)
        self.Archive_module = EmployeeArchiveSystem(session=self.session,current_user_data=self.current_user_data)
        self.Absence_module = AbsenceManagementSystem(current_user_data=self.current_user_data,session=self.session)
        self.Evaluation_module = Evaluation(current_user_data=self.current_user_data,session=self.session)

        # Add modules to stacked widget
        self.stacked_widget.addWidget(self.employee_module)    # index 0
        self.stacked_widget.addWidget(self.formation_module)   # index 1
        self.stacked_widget.addWidget(self.leave_module)       # index 2
        self.stacked_widget.addWidget(self.Compte_module)      # index 3
        self.stacked_widget.addWidget(self.Archive_module)     # index 4
        self.stacked_widget.addWidget(self.Absence_module)     # index 5
        self.stacked_widget.addWidget(self.Evaluation_module)  # index 6
        
        # Show employee module by default
        self.stacked_widget.setCurrentIndex(0)
        self.top_bar.setVisible(False)
        

    def switch_module(self, module_name):
        """
        Switch to the specified module
        """
        # Map module names to (index, module instance)
        module_map = {
            "إدارة الموظفين": (0, self.employee_module),
            "إدارة التكوين": (1, self.formation_module),
            "إدارة الإجازات": (2, self.leave_module),
            "إدارة الحسابات": (3, self.Compte_module),
            "صفحة الأرشيف": (4, self.Archive_module),
            "إدارة الغيابات": (5, self.Absence_module),
            "إدارة التقييمات": (6, self.Evaluation_module),
        }

        # Admin-only check for الحسابات
        if module_name == "إدارة الحسابات":
            user_role = self.current_user_data.get('role', '').lower()
            if user_role != 'admin':
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "غير مصرح",
                    "عذراً، هذه الميزة متاحة للمديرين فقط."
                )
                return

        if module_name in module_map:
            index, module_instance = module_map[module_name]

            # Update module if possible
            if hasattr(module_instance, "update_data"):
                module_instance.update_data()

            # Switch stacked widget
            self.stacked_widget.setCurrentIndex(index)

            # Update sidebar active module
            self.sidebar.update_active_module(module_name)

            # Show or hide top bar based on module
            self.top_bar.setVisible(module_name != "إدارة الموظفين")

    def update_top_bar_button_states(self):
        if not self.top_bar.isVisible():
            self.top_bar_export_btn.setEnabled(False)
            self.top_bar_print_btn.setEnabled(False)
            return

        current_module_widget = self.stacked_widget.currentWidget()
        can_export_excel = hasattr(current_module_widget, 'export_data_to_excel')
        can_print_pdf = hasattr(current_module_widget, 'print_data_to_pdf')

        self.top_bar_export_btn.setEnabled(can_export_excel)
        self.top_bar_export_btn.setToolTip("تصدير إلى Excel" if can_export_excel else "غير متاح")
        self.top_bar_print_btn.setEnabled(can_print_pdf)
        self.top_bar_print_btn.setToolTip("طباعة PDF" if can_print_pdf else "غير متاح")

    def proxy_export_excel_action(self):
        if not self.top_bar.isVisible():
            return
        current_module_widget = self.stacked_widget.currentWidget()
        if hasattr(current_module_widget, 'export_data_to_excel'):
            current_module_widget.export_data_to_excel()

    def proxy_print_pdf_action(self):
        if not self.top_bar.isVisible():
            return
        current_module_widget = self.stacked_widget.currentWidget()
        if hasattr(current_module_widget, 'print_data_to_pdf'):
            current_module_widget.print_data_to_pdf()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set application-wide font for Arabic support
    font = QFont("Arial", 10)
    app.setFont(font)

    # Set right-to-left layout for Arabic
    app.setLayoutDirection(Qt.RightToLeft)

    # Pour les tests, créer une session factice
    window = HRMSMainWindow(session=None)
    window.show()

    sys.exit(app.exec_())