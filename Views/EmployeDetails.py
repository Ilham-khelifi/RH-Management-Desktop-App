
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QComboBox, QDateEdit, QPushButton, QScrollArea,
                             QWidget, QMessageBox, QTextEdit,
                             QFrame, QInputDialog)
from PyQt5.QtCore import Qt, QDate, QEvent, QRegExp, QSize
from PyQt5.QtGui import QPixmap, QRegExpValidator, QIntValidator, QIcon
from ui_constants import *

from Controllers.EmployeController import EmployeeController
from DatabaseConnection import db
from Models.Employe import Employe
from Models.Carriere import Carriere


class AutoExpandingTextEdit(QTextEdit):
    """A QTextEdit that automatically expands vertically based on content"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.document().contentsChanged.connect(self.sizeChange)
        self.heightMin = 30
        self.heightMax = 300
        self.setMinimumHeight(self.heightMin)
        self.setMaximumHeight(self.heightMax)
        self.setAcceptRichText(False)

    def sizeChange(self):
        docHeight = self.document().size().height()
        newHeight = min(max(docHeight + 10, self.heightMin), self.heightMax)
        if self.height() != newHeight:
            self.setMinimumHeight(int(newHeight))
            self.setMaximumHeight(int(newHeight))


class CustomComboBox(QComboBox):
    """A custom combobox that allows adding new items"""

    def __init__(self, parent=None, allow_add=True):
        super().__init__(parent)
        self.setEditable(True)
        self.addItem_text = "إضافة خيار جديد..."
        self.allow_add = allow_add

    def showPopup(self):
        # Add the "Add new item" option if it's not already there and adding is allowed
        if self.allow_add and self.count() > 0 and self.itemText(self.count() - 1) != self.addItem_text:
            self.addItem(self.addItem_text)
        super().showPopup()

    def add_new_item(self):
        text, ok = QInputDialog.getText(self, "إضافة خيار جديد", "أدخل الخيار الجديد:")

        if ok and text:
            confirm = QMessageBox(self)
            confirm.setWindowTitle("تأكيد")
            confirm.setText(f"هل تريد اختيار '{text}' مؤقتاً؟")
            confirm.setIcon(QMessageBox.Question)

            yes_btn = confirm.addButton("نعم", QMessageBox.YesRole)
            no_btn = confirm.addButton("لا", QMessageBox.NoRole)

            confirm.exec_()

            if confirm.clickedButton() == yes_btn:
                self.setCurrentText(text)  # Use the text temporarily


        # Re-add "add new" option if needed
        if self.allow_add:
            if self.count() == 0 or self.itemText(self.count() - 1) != self.addItem_text:
                self.addItem(self.addItem_text)


class EmployeeDetailsTopBar(QWidget):
    """A top bar for the employee details window with edit, print, and export buttons"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("employeeDetailsTopBar")
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QWidget#employeeDetailsTopBar {{
                background-color: {LIGHT_BG};
                border-radius: 10px;
                margin: 10px;
            }}
            QLabel#headerTitle {{
                color: {WHITE};
                font-size: 28px;
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {ORANGE};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #d35400;
            }}
            QPushButton#deleteBtn {{
                background-color: {RED};
            }}
            QPushButton#deleteBtn:hover {{
                background-color: #d32f2f;
            }}
            QPushButton#editBtn {{
                background-color: {GREEN};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 10px 30px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton#editBtn:hover {{
                background-color: #388E3C;
            }}
            QLabel#avatarLabel {{
                background-color: #FFC107;
                border-radius: 35px;
                min-width: 70px;
                min-height: 70px;
                max-width: 70px;
                max-height: 70px;
            }}
        """)

        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)

        # Left side - buttons (toolbar)
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setSpacing(15)

        self.edit_btn = QPushButton("تعديل الملف")
        self.edit_btn.setObjectName("editBtn")
        self.edit_btn.setFixedSize(150, 50)


        buttons_layout.addWidget(self.edit_btn)
        # Right side - employee info
        employee_info_widget = QWidget()
        employee_info_layout = QHBoxLayout(employee_info_widget)
        employee_info_layout.setContentsMargins(0, 0, 0, 0)

        # Employee avatar
        self.avatar_label = QLabel()
        self.avatar_label.setObjectName("avatarLabel")
        self.avatar_label.setFixedSize(70, 70)

        # Try to load avatar image
        try:
            pixmap = QPixmap("pics/user.png")
            self.avatar_label.setPixmap(pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            # If image not found, use a placeholder
            self.avatar_label.setText("👤")
            self.avatar_label.setAlignment(Qt.AlignCenter)
            self.avatar_label.setStyleSheet("font-size: 30px; color: #333;")

        # Employee name and position
        employee_text_widget = QWidget()
        employee_text_layout = QVBoxLayout(employee_text_widget)
        employee_text_layout.setContentsMargins(0, 0, 0, 0)
        employee_text_layout.setSpacing(5)

        self.employee_name_label = QLabel("بيانات العامل")
        self.employee_name_label.setObjectName("employeeName")
        self.employee_name_label.setAlignment(Qt.AlignRight)

        self.employee_position_label = QLabel("الوظيفة")
        self.employee_position_label.setObjectName("employeePosition")
        self.employee_position_label.setAlignment(Qt.AlignRight)

        employee_text_layout.addWidget(self.employee_name_label)
        employee_text_layout.addWidget(self.employee_position_label)

        # Add arrow image
        arrow_label = QLabel()
        arrow_label.setFixedSize(100, 30)
        try:
            pixmap = QPixmap("pics/arrow.png")
            arrow_label.setPixmap(pixmap.scaled(100, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            # If image not found, use a text arrow
            arrow_label.setText("←")
            arrow_label.setAlignment(Qt.AlignCenter)
            arrow_label.setStyleSheet(f"font-size: 24px; color: {WHITE};")

        employee_info_layout.addWidget(self.avatar_label)
        employee_info_layout.addWidget(arrow_label)
        employee_info_layout.addWidget(employee_text_widget)

        # Add to main layout
        layout.addWidget(employee_info_widget)  # Right side
        layout.addStretch()
        layout.addWidget(buttons_widget)  # Left side



class SaveConfirmationDialog(QDialog):
    """A dialog to confirm saving changes"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("حفظ التغييرات")
        self.setFixedSize(400, 200)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {DARK_BG};
                color: {WHITE};
            }}
            QLabel {{
                color: {WHITE};
                font-size: 16px;
            }}
            QPushButton#saveBtn {{
                background-color: {GREEN};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 10px 30px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton#cancelBtn {{
                background-color: {RED};
                color: {WHITE};
                border: none;
                border-radius: 5px;
                padding: 10px 30px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton#saveBtn:hover {{
                background-color: #388E3C;
            }}
            QPushButton#cancelBtn:hover {{
                background-color: #D32F2F;
            }}
        """)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Confirmation message
        message_label = QLabel("هل تريد حفظ التغييرات؟")
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)

        # Buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(20)

        self.save_btn = QPushButton("حفظ")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setFixedSize(150, 50)

        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setFixedSize(150, 50)

        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addWidget(buttons_widget, 0, Qt.AlignCenter)

        # Connect buttons
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)


class EmployeeDetailsWindow(QDialog):
    def __init__(self, parent=None, employee_data=None, current_user_data=None, session=None):
        super().__init__(parent)
        self.resize(1450, 800)
        self.setWindowTitle("نظام إدارة الموارد البشرية - تفاصيل الموظف")
        self.edit_mode = False
        self.employee_data = employee_data or {}
        self.current_user_data = current_user_data or {}
        # Type mapping for display to database values
        self.type_mapping = {
            "موظف": "permanent",
            "عون متعاقد": "contractuel"
        }
        
        # Get database session and employee data
        self.session = session
        emp_id = employee_data.get("رقم الموظف")
        self.employee = self.session.query(Employe).filter_by(idemploye=emp_id).first()

        if not self.employee:
            QMessageBox.critical(self, "خطأ", "الموظف غير موجود في قاعدة البيانات.")
            return

        self.carriere = self.employee.carrieres  # assuming one-to-one relationship

        # Set the window style to match the main application
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {DARK_BG};
                color: {WHITE};
            }}
            QLabel {{
                color: {WHITE};
            }}
            QLineEdit, QComboBox, QDateEdit, QTextEdit {{
                background-color: {MEDIUM_BG};
                color: {WHITE};
                border: 1px solid {LIGHT_BG};
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }}
            QPushButton {{
                background-color: {ORANGE};
                color: {WHITE};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #d35400;
            }}
            QPushButton#cancelBtn {{
                background-color: {LIGHT_BG};
            }}
            QPushButton#cancelBtn:hover {{
                background-color: #546E7A;
            }}
            QGroupBox {{
                border: 1px solid {LIGHT_BG};
                border-radius: 4px;
                margin-top: 20px;
                font-weight: bold;
                color: {WHITE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QTabWidget::pane {{
                border: 1px solid {LIGHT_BG};
                background-color: {DARK_BG};
            }}
            QTabBar::tab {{
                background-color: {MEDIUM_BG};
                color: {WHITE};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {ORANGE};
            }}
            QFrame#sectionFrame {{
                background-color: {DARKER_BG};
                border-radius: 4px;
                margin: 5px;
                padding: 5px;
            }}
            QLabel#sectionTitle {{
                font-weight: bold;
                color: {ORANGE};
                font-size: 14px;
                padding: 5px;
                background-color: {MEDIUM_BG};
                border-radius: 4px;
                min-height: 30px;
                max-height: 30px;
            }}
            QPushButton#tabButton {{
                background-color: {MEDIUM_BG};
                border-radius: 4px;
                padding: 5px 10px;
                margin: 2px;
            }}
            QPushButton#tabButton:hover {{
                background-color: {LIGHT_BG};
            }}
            QPushButton#tabButtonActive {{
                background-color: {ORANGE};
                border-radius: 4px;
                padding: 5px 10px;
                margin: 2px;
            }}
            QLabel#frenchLabel {{
                color: #90A4AE;
                font-style: italic;
            }}
            QScrollArea {{
                border: none;
            }}
            QFrame#sectionTitleFrame {{
                background-color: {MEDIUM_BG};
                border-radius: 4px;
                padding: 5px;
                margin-top: 10px;
                margin-bottom: 10px;
            }}
            QLabel#smallSectionTitle {{
                color: {ORANGE};
                font-weight: bold;
                font-size: 12px;
            }}
            QFrame#separator {{
                background-color: {LIGHT_BG};
                max-height: 1px;
                min-height: 1px;
            }}
            QPushButton#affiliationBtn {{
                background-color: {LIGHT_BG};
                color: {WHITE};
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 12px;
            }}
        """)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Create the top bar
        self.top_bar = EmployeeDetailsTopBar(self)

        # Set employee name and position if available
        if employee_data:
            name = employee_data.get("الاسم", "")
            surname = employee_data.get("اللقب", "")
            position = employee_data.get("الرتبة أو منصب الشغل الحالي ", "")
            emp_type = employee_data.get("طبيعة علاقة العمل (موظف عون متعاقد)", "موظف")

            if name and surname:
                self.top_bar.employee_name_label.setText(f"{name} {surname}")

            if position:
                self.top_bar.employee_position_label.setText(f"{position} ({emp_type})")

        # Connect top bar buttons
        self.top_bar.edit_btn.clicked.connect(self.toggle_edit_mode)
        # Add the top bar to the main layout
        self.main_layout.addWidget(self.top_bar)

        # Tab buttons
        tab_buttons = QWidget()
        tab_buttons_layout = QHBoxLayout(tab_buttons)
        tab_buttons_layout.setContentsMargins(10, 10, 10, 10)

        personal_tab_btn = QPushButton("البيانات الشخصية")
        personal_tab_btn.setObjectName("tabButtonActive")

        tab_buttons_layout.addWidget(personal_tab_btn)
        tab_buttons_layout.addStretch()

        self.main_layout.addWidget(tab_buttons)

        # Create a scroll area for the form
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Form container
        form_container = QWidget()
        form_layout = QHBoxLayout(form_container)  # Changed to horizontal layout for two columns
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(15, 15, 15, 15)

        # Create two columns
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)

        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Personal Information Section (Right Column)
        personal_info_frame = QFrame()
        personal_info_frame.setObjectName("sectionFrame")
        personal_info_layout = QVBoxLayout(personal_info_frame)

        personal_info_title = QLabel("البيانات الشخصية")
        personal_info_title.setObjectName("sectionTitle")
        personal_info_title.setAlignment(Qt.AlignCenter)
        personal_info_layout.addWidget(personal_info_title)

        # Personal info form
        personal_form = QFormLayout()
        personal_form.setVerticalSpacing(15)
        personal_form.setHorizontalSpacing(10)
        personal_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Create fields in the exact order specified
        self.name = QLineEdit()
        self.surname = QLineEdit()
        self.spouse_surname = QLineEdit()

        # Set current date and prevent future dates
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDisplayFormat("dd/MM/yyyy")
        self.birth_date.setDate(QDate.currentDate())
        self.birth_date.setMaximumDate(QDate.currentDate())

        self.birth_province = CustomComboBox()
        wilayas = [
            "01- أدرار", "02- الشلف", "03- الأغواط", "04- أم البواقي", "05- باتنة", "06- بجاية", "07- بسكرة",
            "08- بشار",
            "09- البليدة", "10- البويرة", "11- تمنراست", "12- تبسة", "13- تلمسان", "14- تيارت", "15- تيزي وزو",
            "16- الجزائر",
            "17- الجلفة", "18- جيجل", "19- سطيف", "20- سعيدة", "21- سكيكدة", "22- سيدي بلعباس", "23- عنابة",
            "24- قالمة",
            "25- قسنطينة", "26- المدية", "27- مستغانم", "28- المسيلة", "29- معسكر", "30- ورقلة", "31- وهران",
            "32- البيض",
            "33- إليزي", "34- برج بوعريريج", "35- بومرداس", "36- الطارف", "37- تندوف", "38- تيسمسيلت", "39- الوادي",
            "40- خنشلة",
            "41- سوق أهراس", "42- تيبازة", "43- ميلة", "44- عين الدفلى", "45- النعامة", "46- عين تموشنت", "47- غرداية",
            "48- غليزان",
            "49- تيميمون", "50- برج باجي مختار", "51- أولاد جلال", "52- بني عباس", "53- عين صالح", "54- عين قزام",
            "55- تقرت",
            "56- جانت", "57- المغير", "58- المنيعة"
        ]

        # Populate combobox
        self.birth_province.addItems(wilayas)
        self.birth_province.activated.connect(self.handle_combobox_activation)

        self.father_name = QLineEdit()
        self.mother_name = QLineEdit()

        # Create comboboxes with allow_add=False for specified ones
        self.gender = CustomComboBox(allow_add=False)
        self.gender.addItems(["ذكر", "أنثى"])

        self.current_address = QLineEdit()

        # Postal Code - only digits, max 5
        self.postal_code = QLineEdit()
        postal_regex = QRegExp("^[0-9]{5}$")
        self.postal_code.setValidator(QRegExpValidator(postal_regex))
        self.postal_code.setPlaceholderText("XXXXX")

        # Phone Number - Algerian format: starts with 05, 06, or 07 + 8 digits
        self.phone_numbers = QLineEdit()
        phone_regex = QRegExp("^(05|06|07)[0-9]{8}$")
        self.phone_numbers.setValidator(QRegExpValidator(phone_regex))
        self.phone_numbers.setPlaceholderText("05XXXXXXXX")

        # Email - Regex will be checked manually (to allow complete strings)
        self.email = QLineEdit()
        self.email.setPlaceholderText("example@domain.com")

        # Social security number - numbers only
        self.social_security_num = QLineEdit()
        self.social_security_num.setValidator(QIntValidator())

        # National ID with validation (numbers only, max 18 digits)
        self.national_id = QLineEdit()
        reg_ex = QRegExp("^[0-9]{1,18}$")
        input_validator = QRegExpValidator(reg_ex, self.national_id)
        self.national_id.setValidator(input_validator)

        self.marital_status = CustomComboBox(allow_add=False)
        self.marital_status.addItems(["أعزب", "متزوج", "مطلق", "أرمل"])

        self.children_count = QLineEdit()
        self.children_count.setValidator(QIntValidator(0, 99))

        self.national_service = CustomComboBox(allow_add=False)
        national_service_options = [
            "مؤدى",
            "مؤهل لا يجند",
            "معفى",
            "مسجل في قوائم الإحصاء",
            "أجرى فحص الانتقاء الطبي وأعلن مؤهلا للخدمة الوطنية",
            "إثبات مانع مؤقت أو نهائي للتجنيد",
            "مستفيد من التأجيل بسبب الدراسة أو التكوين",
            "مستفيد من إرجاء التجنيد",
            "أودع ملف إعفاء",
            "معلن غير مؤهل",
            "غير معني"
        ]

        self.national_service.addItems(national_service_options)

        # Add fields to form in the specified order
        personal_form.addRow("الاسم:", self.name)
        personal_form.addRow("اللقب:", self.surname)
        personal_form.addRow("لقب الزوج بالنسبة للمتزوجات:", self.spouse_surname)
        personal_form.addRow("تاريخ الميلاد:", self.birth_date)
        personal_form.addRow("ولاية الميلاد:", self.birth_province)
        personal_form.addRow("اسم الأب:", self.father_name)
        personal_form.addRow("لقب واسم الأم:", self.mother_name)
        personal_form.addRow("الجنس:", self.gender)
        personal_form.addRow("العنوان الحالي:", self.current_address)
        personal_form.addRow("الرمز البريدي:", self.postal_code)
        personal_form.addRow("أرقام الهاتف:", self.phone_numbers)
        personal_form.addRow("البريد الإلكتروني:", self.email)
        personal_form.addRow("رقم الضمان الاجتماعي:", self.social_security_num)
        personal_form.addRow("رقم التعريف الوطني:", self.national_id)
        personal_form.addRow("الوضعية العائلية:", self.marital_status)
        personal_form.addRow("عدد الأولاد:", self.children_count)
        personal_form.addRow("الوضعية تجاه الخدمة الوطنية:", self.national_service)

        # Education section
        education_label = QLabel("الشهادة التي تم على أساسها التوظيف الأصلي")
        education_label.setAlignment(Qt.AlignRight)
        personal_form.addRow(education_label)

        self.original_education = CustomComboBox()
        education_levels = [
            "رخصة السياقة",
            "بدون مستوى",
            "السنة الثالثة ثانوي",
            "شهادة الباكالوريا",
            "شهادة الليسانس",
            "شهادة الماستر",
            "شهادة الماجستير",
            "شهادة الدكتوراه"
        ]

        self.original_education.addItems(education_levels)
        self.original_education.activated.connect(self.handle_combobox_activation)
        personal_form.addRow("", self.original_education)

        # Current education
        current_education_label = QLabel("الشهادة الحالية")
        current_education_label.setAlignment(Qt.AlignRight)
        personal_form.addRow(current_education_label)

        self.current_education = CustomComboBox()
        self.current_education.addItems(education_levels)
        self.current_education.activated.connect(self.handle_combobox_activation)
        personal_form.addRow("", self.current_education)

        # Other certifications
        other_certs_label = QLabel("شهادات ومؤهلات أخرى")
        other_certs_label.setAlignment(Qt.AlignRight)
        personal_form.addRow(other_certs_label)

        self.other_certifications = AutoExpandingTextEdit()
        personal_form.addRow("", self.other_certifications)

        personal_info_layout.addLayout(personal_form)
        right_layout.addWidget(personal_info_frame)

        # ---- Separator Bar or Label ----
        separator_label = QLabel("------ المعلومات الشخصية (بالفرنسية) ------")
        separator_label.setAlignment(Qt.AlignRight)
        separator_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        personal_form.addRow(separator_label)

        # ---- French Side of Personal Info ----
        self.french_lastname = QLineEdit()
        self.french_name = QLineEdit()
        self.french_lastname_hus = QLineEdit()

        # Set current date and prevent future dates for French birthday
        self.french_birthday = QDateEdit()
        self.french_birthday.setCalendarPopup(True)
        self.french_birthday.setDisplayFormat("yyyy/MM/dd")
        self.french_birthday.setDate(QDate.currentDate())
        self.french_birthday.setMaximumDate(QDate.currentDate())

        # French style: label on right, field on left (reversed from original)
        french_form_widget = QWidget()
        french_form_layout = QFormLayout(french_form_widget)
        french_form_layout.setLabelAlignment(Qt.AlignRight)
        french_form_layout.setFormAlignment(Qt.AlignRight)

        # Reverse the order: field first, then label
        french_form_layout.addRow(self.french_lastname, QLabel("Nom de famille :"))
        french_form_layout.addRow(self.french_name, QLabel("Prénom :"))
        french_form_layout.addRow(self.french_lastname_hus, QLabel("Nom de famille du mari :"))
        french_form_layout.addRow(self.french_birthday, QLabel("Date de naissance :"))

        # Add French birth province
        self.french_birth_province = CustomComboBox()
        self.french_birth_province.addItems([
            "01- Adrar", "02- Chlef", "03- Laghouat", "04- Oum El Bouaghi", "05- Batna", "06- Béjaïa", "07- Biskra",
            "08- Béchar", "09- Blida", "10- Bouïra", "11- Tamanrasset", "12- Tébessa", "13- Tlemcen", "14- Tiaret",
            "15- Tizi Ouzou", "16- Alger", "17- Djelfa", "18- Jijel", "19- Sétif", "20- Saïda", "21- Skikda",
            "22- Sidi Bel Abbès", "23- Annaba", "24- Guelma", "25- Constantine", "26- Médéa", "27- Mostaganem",
            "28- M'Sila", "29- Mascara", "30- Ouargla", "31- Oran", "32- El Bayadh", "33- Illizi",
            "34- Bordj Bou Arréridj",
            "35- Boumerdès", "36- El Taref", "37- Tindouf", "38- Tissemsilt", "39- El Oued", "40- Khenchela",
            "41- Souk Ahras", "42- Tipaza", "43- Mila", "44- Aïn Defla", "45- Naâma", "46- Aïn Témouchent",
            "47- Ghardaïa", "48- Relizane", "49- Timimoun", "50- Bordj Badji Mokhtar", "51- Ouled Djellal",
            "52- Béni Abbès", "53- In Salah", "54- Ain Guezzam", "55- Touggourt", "56- Djanet", "57- El M'Ghair",
            "58- El Menia"
        ])
        self.french_birth_province.activated.connect(self.handle_combobox_activation)

        french_form_layout.addRow(self.french_birth_province, QLabel("Wilaya de naissance :"))

        # Add the French form to the main personal form
        personal_form.addRow("", french_form_widget)

        # -----------------------------------------------------------------------------------------------------------------------

        # Employment Section (Left Column)
        self.employment_frame = QFrame()
        self.employment_frame.setObjectName("sectionFrame")
        employment_layout = QVBoxLayout(self.employment_frame)

        employment_title = QLabel("التفعيل")
        employment_title.setObjectName("sectionTitle")
        employment_title.setAlignment(Qt.AlignCenter)
        employment_layout.addWidget(employment_title)

        # Employment form
        employment_form = QFormLayout()
        employment_form.setVerticalSpacing(15)
        employment_form.setHorizontalSpacing(10)

        self.employment_type = CustomComboBox(allow_add=False)
        self.employment_type.addItems(["مفعل", "غير مفعل"])
        self.employment_type.activated.connect(self.handle_employment_type_change)

        self.employment_status_reason = CustomComboBox()
        self.employment_status_reason.addItems([
            "إحالة على الاستيداع",
            "عطلة غير مدفوعة الراتب",
            "الخدمة الوطنية",
            "عطلة مرضية طويلة المدى"
        ])
        self.employment_status_reason.activated.connect(self.handle_combobox_activation)

        self.decision_number = QLineEdit()
        self.decision_number.setValidator(QIntValidator(0, 999999))

        # Set current date and prevent future dates
        self.decision_date = QDateEdit()
        self.decision_date.setCalendarPopup(True)
        self.decision_date.setDisplayFormat("dd/MM/yyyy")
        self.decision_date.setDate(QDate.currentDate())
        self.decision_date.setMaximumDate(QDate.currentDate())

        employment_form.addRow("مفعل / غير مفعل:", self.employment_type)

        # Create widgets for conditional display
        self.employment_reason_row = QWidget()
        employment_reason_layout = QHBoxLayout(self.employment_reason_row)
        employment_reason_layout.setContentsMargins(0, 0, 0, 0)
        employment_reason_layout.addWidget(QLabel("سبب تغير حالة التفعيل:"))
        employment_reason_layout.addWidget(self.employment_status_reason)

        self.decision_number_row = QWidget()
        decision_number_layout = QHBoxLayout(self.decision_number_row)
        decision_number_layout.setContentsMargins(0, 0, 0, 0)
        decision_number_layout.addWidget(QLabel("رقم القرار:"))
        decision_number_layout.addWidget(self.decision_number)

        self.decision_date_row = QWidget()
        decision_date_layout = QHBoxLayout(self.decision_date_row)
        decision_date_layout.setContentsMargins(0, 0, 0, 0)
        decision_date_layout.addWidget(QLabel("تاريخ القرار:"))
        decision_date_layout.addWidget(self.decision_date)

        # Add rows to form
        employment_form.addRow("", self.employment_reason_row)
        employment_form.addRow("", self.decision_number_row)
        employment_form.addRow("", self.decision_date_row)

        employment_layout.addLayout(employment_form)
        left_layout.addWidget(self.employment_frame)

        # Current Job Section (Left Column)
        self.current_job_frame = QFrame()
        self.current_job_frame.setObjectName("sectionFrame")
        current_job_layout = QVBoxLayout(self.current_job_frame)

        current_job_title = QLabel("الوظيفة و المنصب الحالي")
        current_job_title.setObjectName("sectionTitle")
        current_job_title.setAlignment(Qt.AlignCenter)
        current_job_layout.addWidget(current_job_title)

        # Current job form
        current_job_form = QFormLayout()
        current_job_form.setVerticalSpacing(15)
        current_job_form.setHorizontalSpacing(10)

        # Create fields for the current job section
        self.job_relationship_type = CustomComboBox(allow_add=False)
        self.job_relationship_type.addItems(["موظف", "عون متعاقد"])
        self.job_relationship_type.activated.connect(self.handle_job_relationship_type_change)

        # Initialize basic law combobox
        self.basic_law = CustomComboBox()
        self.basic_law.addItems([
            "الأسلاك المشتركة",
            "أسلاك التربية",
            "الأعوان المتعاقدون"
        ])
        self.basic_law.currentIndexChanged.connect(self.handle_basic_law_selection)

        # Initialize job category combobox
        self.job_category = CustomComboBox()

        # Initialize silk combobox
        self.silk_category = CustomComboBox()
        self.silk_category.currentIndexChanged.connect(self.update_job_rank)

        # Initialize the job rank combobox
        self.job_rank = CustomComboBox()
        self.job_rank.activated.connect(self.handle_combobox_activation)

        # Define data structures for cascading relationships
        self.category_data = {
            "الإدارة العامة": ["المتصرفون", "مساعدو المتصرفين", "ملحقو الإدارة", "أعوان الإدارة", "الكتاب",
                               "المحاسبون الإداريون"],
            "الترجمة - الترجمة الفورية": ["المترجمون - التراجمة"],
            "الإعلام الآلي": ["المهندسون", "مساعدو المهندسين", "التقنيون", "المعاونون التقنيون", "الأعوان التقنيون"],
            "الإحصائيات": ["المهندسون", "مساعدو المهندسين", "التقنيون", "المعاونون التقنيون", "الأعوان التقنيون"],
            "الوثائق والمحفوظات": ["الوثائقيون أمناء المحفوظات", "مساعدو الوثائقيين أمناء المحفوظات",
                                   "الأعوان التقنيون في الوثائق والمحفوظات"],
            "المخبر والصيانة": ["المهندسون", "التقنيون", "المعاونون التقنيون", "الأعوان التقنيون", "أعوان المخبر"]
        }

        self.rank_data = {
            "المتصرفون": ["متصرف", "متصرف رئيسي", "متصرف مستشار", "متصرف  محلل"],
            "مساعدو المتصرفين": ["مساعد متصرف"],
            "ملحقو الإدارة": ["ملحق إدارة", "ملحق رئيسي للإدارة"],
            "أعوان الإدارة": ["عون إدارة", "عون إدارة رئيسي"],
            "الكتاب": ["كاتب", "كاتب مديرية"],
            "المحاسبون الإداريون": ["محاسب إداري", "محاسب إداري رئيسي"],
            "المترجمون - التراجمة": ["مترجم - ترجمان", "مترجم - ترجمان رئيسي", "مترجم - ترجمان متخصص"],
            "المهندسون": ["مهندس دولة", "مهندس رئيسي", "رئيس المهندسين"],
            "مساعدو المهندسين": ["مساعد مهندس مستوى 1", "مساعد مهندس مستوى 2"],
            "التقنيون": ["تقني", "تقني سامي"],
            "المعاونون التقنيون": ["معاون تقني"],
            "الأعوان التقنيون": ["عون تقني"],
            "الوثائقيون أمناء المحفوظات": ["وثائقي أمين محفوظات", "وثائقي أمين محفوظات رئيسي"],
            "مساعدو الوثائقيين أمناء المحفوظات": ["مساعد وثائقي أمين محفوظات"],
            "الأعوان التقنيون في الوثائق والمحفوظات": ["عون تقني في الوثائق والمحفوظات"],
            "أعوان المخبر": ["عون تقني للمخبر", "عون مخبر"]
        }

        # Education data
        self.category_data_2 = {
            "موظفو التعليم": ["معلمو المدرسة الابتدائية", "أستاذ التعليم الابتدائي", "أساتذة التعليم الأساسي",
                              "أساتذة التعليم المتوسط", "أساتذة التعليم الثانوي", ],
            "موظفو التربية": ["النظار", "مستشار و التربية", "مساعدو التربية", "مشرفو التربية",
                              "المربون المتخصصون في الدعم التربوي"],
            "موظفو التوجيه والإرشاد المدرسي والمهني": ["مستشار و التوجيه والإرشاد المدرسي والمهني"],
            "موظفو المخابر": ["الأعوان التقنيون للمخابر", "المعاونون التقنيون للمخابر", "الملحقون بالمخابر"],
            "موظفو التغذية المدرسية": ["مستشارو التغذية المدرسية"],
            "موظفو المصالح الاقتصادية": ["مساعدو المصالح الاقتصادية", "نواب المقتصدين", "المقتصدون"],
            "موظفو إدارة مؤسسات التربية والتعليم": ["مديرو المدارس الابتدائية", "مديرو المتوسطات", "مديرو الثانويات"],
            "موظفو التفتيش": ["مفتشو التعليم الابتدائي", "مفتشو التعليم المتوسط", "مفتشو التعليم الثانوي",
                              "مفتشو التربية الوطني"]
        }

        self.rank_data_2 = {
            "معلمو المدرسة الابتدائية": ["معلم مدرسة ابتدائية"],
            "أستاذ التعليم الابتدائي": ["أساتذة التعليم الابتدائي", "أستاذ التعليم الابتدائي قسم أول",
                                        "أستاذ التعليم الابتدائي قسم ثان", "أستاذ مميز في التعليم الابتدائي"],
            "أساتذة التعليم الأساسي": ["أستاذ التعليم الأساسي"],
            "أساتذة التعليم المتوسط": ["أستاذ التعليم المتوسط", "أستاذ التعليم المتوسط قسم أول",
                                       "أستاذ التعليم المتوسط قسم ثان", "أستاذ مميز في التعليم المتوسط"],
            "أساتذة التعليم الثانوي": ["أستاذ التعليم الثانوي", "أستاذ التعليم الثانوي قسم أول",
                                       "استاذ التعليم الثانوي قسم ثان", "أستاذ مميز في التعليم الثانوي"],
            "النظار": [" ناظر  في التعليم الابتدائي", "ناظر في التعليم المتوسط", "ناظر في التعليم الثانوي"],
            "مستشارو التربية": ["مستشار التربية"],
            "مساعدو التربية": ["مساعد التربية", "مساعد رئيسي للتربية"],
            "مشرفو التربية": ["مشرف التربية", "مشرف رئيسي للتربية", "مشرف رئيس للتربية", "مشرف عام للتربية"],
            "المربون المتخصصون في الدعم التربوي": ["مربي متخصص في الدعم التربوي", "مربي متخصص رئيسي في الدعم التربوي",
                                                   "مربي متخصص رئيس في الدعم التربوي",
                                                   "مربي متخصص عام في الدعم التربوي"],
            "مستشار و التوجيه والإرشاد المدرسي والمهني": ["مستشار التوجيه والإرشاد المدرسي والمهني",
                                                          "مستشار محلل للتوجيه والإرشاد المدرسي والمهني",
                                                          "مستشار رئيسي للتوجيه والإرشاد المدرسي والمهني",
                                                          "مستشار رئيس للتوجيه والإرشاد المدرسي والمهني"],
            "الأعوان التقنيون للمخابر": ["عون تقني للمخابر"],
            "المعاونون التقنيون للمخابر": ["معاون تقني للمخابر"],
            "الملحقون بالمخابر": ["ملحق بالمخابر", "ملحق رئيسي بالمخابر", "ملحق رئيس بالمخابر", "ملحق مشرف بالمخابر"],
            "مستشارو التغذية المدرسية": ["مستشار التغذية المدرسية", "مستشار رئيسي في التغذية المدرسية",
                                         "مستشار رئيس في التغذية المدرسية"],
            "مساعدو المصالح الاقتصادية": ["مساعد المصالح الاقتصادية ", "مساعد رئيسي للمصالح الاقتصادية"],
            "نواب المقتصدين": ["نائب مقتصد ", "نائب مقتصد مسیر"],
            "المقتصدون": ["مقتصد", "مقتصد رئيسي"],
            "مديرو المدارس الابتدائية": ["مدير المدرسة الابتدائية"],
            "مديرو المتوسطات": ["مدير المتوسطة"],
            "مديرو الثانويات": ["مدير الثانوية"],
            "مفتشو التعليم الابتدائي": ["مفتش التعليم الابتدائي تخصص المواد",
                                        "مفتش التعليم الابتدائي تخصص إدارة المدارس الابتدائية",
                                        "مفتش التعليم الابتدائي تخصص التغذية المدرسية"],
            "مفتشو التعليم المتوسط": ["مفتش التعليم المتوسط تخصص المواد", "مفتش التعليم المتوسط تخصص إدارة المتوسطات",
                                      "مفتش التوجيه والإرشاد المدرسي والمهني في المتوسطات",
                                      "مفتش التسيير المالي والمادي في المتوسطات"],
            "مفتشو التعليم الثانوي": ["مفتش التعليم الثانوي تخصص إدارة الثانويات",
                                      "مفتش التوجيه والإرشاد المدرسي والمهني في الثانويات",
                                      "مفتش التسيير المالي والمادي في الثانويات", "مفتش التعليم الثانوي تخصص المواد"],
            "مفتشو التربية الوطني": ["مفتش التربية الوطني"]
        }

        # Only numbers for decision number
        self.appointment_decision_number = QLineEdit()
        self.appointment_decision_number.setValidator(QIntValidator())

        # Set current date and prevent future dates
        self.appointment_decision_date = QDateEdit()
        self.appointment_decision_date.setCalendarPopup(True)
        self.appointment_decision_date.setDisplayFormat("dd/MM/yyyy")
        self.appointment_decision_date.setDate(QDate.currentDate())
        self.appointment_decision_date.setMaximumDate(QDate.currentDate())

        # Only numbers for visa number
        self.visa_number = QLineEdit()
        self.visa_number.setValidator(QIntValidator())

        # Set current date and prevent future dates
        self.visa_date = QDateEdit()
        self.visa_date.setCalendarPopup(True)
        self.visa_date.setDisplayFormat("dd/MM/yyyy")
        self.visa_date.setDate(QDate.currentDate())
        self.visa_date.setMaximumDate(QDate.currentDate())

        # Set current date and prevent future dates
        self.effective_date = QDateEdit()
        self.effective_date.setCalendarPopup(True)
        self.effective_date.setDisplayFormat("dd/MM/yyyy")
        self.effective_date.setDate(QDate.currentDate())
        self.effective_date.setMaximumDate(QDate.currentDate())

        # Only numbers for appointment report number
        self.appointment_report_number = QLineEdit()
        self.appointment_report_number.setValidator(QIntValidator())

        # Set current date and prevent future dates
        self.appointment_report_date = QDateEdit()
        self.appointment_report_date.setCalendarPopup(True)
        self.appointment_report_date.setDisplayFormat("dd/MM/yyyy")
        self.appointment_report_date.setDate(QDate.currentDate())
        self.appointment_report_date.setMaximumDate(QDate.currentDate())

        # Set current date and prevent future dates
        self.appointment_effective_date = QDateEdit()
        self.appointment_effective_date.setCalendarPopup(True)
        self.appointment_effective_date.setDisplayFormat("dd/MM/yyyy")
        self.appointment_effective_date.setDate(QDate.currentDate())
        self.appointment_effective_date.setMaximumDate(QDate.currentDate())

        self.position_status = CustomComboBox()
        self.position_status.addItems(["متربص", "مرسم"])
        self.position_status.activated.connect(self.handle_combobox_activation)

        # Add fields to the form
        current_job_form.addRow("طبيعة علاقة العمل (موظف عون متعاقد):", self.job_relationship_type)
        current_job_form.addRow("القانون الأساسي:", self.basic_law)
        current_job_form.addRow("الشعبة:", self.job_category)
        current_job_form.addRow("الأسلاك:", self.silk_category)
        current_job_form.addRow("الرتبة أو منصب الشغل الحالي:", self.job_rank)
        current_job_form.addRow("رقم المقرر أو العقد:", self.appointment_decision_number)
        current_job_form.addRow("تاريخ المقرر أو العقد:", self.appointment_decision_date)
        current_job_form.addRow("رقم التأشيرة:", self.visa_number)
        current_job_form.addRow("تاريخ التأشيرة:", self.visa_date)
        current_job_form.addRow("تاريخ المفعول:", self.effective_date)
        current_job_form.addRow("رقم محضر التنصيب:", self.appointment_report_number)
        current_job_form.addRow("تاريخ محضر التنصيب:", self.appointment_report_date)
        current_job_form.addRow("تاريخ مفعول التنصيب:", self.appointment_effective_date)
        current_job_form.addRow("الوضعية:", self.position_status)

        # Add French grade section
        # Create a separator
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        current_job_layout.addWidget(separator)

        # French grade form - using French style (label on right, field on left)
        french_grade_widget = QWidget()
        french_grade_layout = QFormLayout(french_grade_widget)
        french_grade_layout.setLabelAlignment(Qt.AlignRight)
        french_grade_layout.setFormAlignment(Qt.AlignRight)

        self.current_grade = CustomComboBox()
        self.current_grade.addItem("سيتم إضافة المعلومات لاحقاً")
        self.current_grade.activated.connect(self.handle_combobox_activation)

        # Set current date and prevent future dates
        self.current_grade_date = QDateEdit()
        self.current_grade_date.setCalendarPopup(True)
        self.current_grade_date.setDisplayFormat("yyyy/MM/dd")
        self.current_grade_date.setDate(QDate.currentDate())
        self.current_grade_date.setMaximumDate(QDate.currentDate())

        # Add French labels with right alignment
        grade_label = QLabel("Grade ou poste actuel")
        grade_label.setObjectName("frenchLabel")

        date_grade_label = QLabel("Date du grade ou poste actuel")
        date_grade_label.setObjectName("frenchLabel")

        french_grade_layout.addRow(self.current_grade, grade_label)
        french_grade_layout.addRow(self.current_grade_date, date_grade_label)

        # Add the French grade form to the layout
        current_job_layout.addLayout(current_job_form)
        current_job_layout.addWidget(french_grade_widget)
        left_layout.addWidget(self.current_job_frame)

        # Classification Section (Left Column)
        self.classification_frame = QFrame()
        self.classification_frame.setObjectName("sectionFrame")
        classification_layout = QVBoxLayout(self.classification_frame)

        classification_title = QLabel("التصنيف")
        classification_title.setObjectName("sectionTitle")
        classification_title.setAlignment(Qt.AlignCenter)
        classification_layout.addWidget(classification_title)

        # Classification form
        classification_form = QFormLayout()
        classification_form.setVerticalSpacing(15)
        classification_form.setHorizontalSpacing(10)

        self.current_class = CustomComboBox()
        self.current_class.addItems([
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17",
            "ق.ف 1", "ق.ف 2", "ق.ف 3", "ق.ف 4", "ق.ف 5", "ق.ف 6", "ق.ف 7"
        ])
        self.current_class.activated.connect(self.handle_combobox_activation)

        self.current_reference_number = QLineEdit()
        self.current_reference_number.setValidator(QIntValidator())

        classification_form.addRow("الصنف الحالي:", self.current_class)
        classification_form.addRow("الرقم الاستدلالي الحالي:", self.current_reference_number)

        classification_layout.addLayout(classification_form)
        left_layout.addWidget(self.classification_frame)

        # Current Grade Section (Left Column)
        self.current_grade_frame = QFrame()
        self.current_grade_frame.setObjectName("sectionFrame")
        current_grade_layout = QVBoxLayout(self.current_grade_frame)

        current_grade_title = QLabel("طبيعة علاقة العمل (موظف)")
        current_grade_title.setObjectName("sectionTitle")
        current_grade_title.setAlignment(Qt.AlignCenter)
        current_grade_layout.addWidget(current_grade_title)

        # Current grade form
        current_grade_form = QFormLayout()
        current_grade_form.setVerticalSpacing(15)
        current_grade_form.setHorizontalSpacing(10)

        self.current_degree = CustomComboBox()
        self.current_degree.addItems([
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"
        ])
        self.current_degree.activated.connect(self.handle_combobox_activation)

        self.decision_number_2 = QLineEdit()
        self.decision_number_2.setValidator(QIntValidator())

        # Set current date and prevent future dates
        self.decision_date_2 = QDateEdit()
        self.decision_date_2.setCalendarPopup(True)
        self.decision_date_2.setDisplayFormat("dd/MM/yyyy")
        self.decision_date_2.setDate(QDate.currentDate())
        self.decision_date_2.setMaximumDate(QDate.currentDate())

        # Set current date and prevent future dates
        self.effective_date_2 = QDateEdit()
        self.effective_date_2.setCalendarPopup(True)
        self.effective_date_2.setDisplayFormat("dd/MM/yyyy")
        self.effective_date_2.setDate(QDate.currentDate())
        self.effective_date_2.setMaximumDate(QDate.currentDate())

        # Seniority fields (year/month/day)
        seniority_widget = QWidget()
        seniority_layout = QHBoxLayout(seniority_widget)
        seniority_layout.setContentsMargins(0, 0, 0, 0)

        self.seniority_year = QLineEdit()
        self.seniority_year.setPlaceholderText("سنة")
        self.seniority_year.setFixedWidth(60)
        self.seniority_year.setValidator(QIntValidator(0, 99))

        self.seniority_month = QLineEdit()
        self.seniority_month.setPlaceholderText("شهر")
        self.seniority_month.setFixedWidth(60)
        self.seniority_month.setValidator(QIntValidator(0, 11))

        self.seniority_day = QLineEdit()
        self.seniority_day.setPlaceholderText("يوم")
        self.seniority_day.setFixedWidth(60)
        self.seniority_day.setValidator(QIntValidator(0, 31))

        seniority_layout.addWidget(self.seniority_year)
        seniority_layout.addWidget(QLabel("/"))
        seniority_layout.addWidget(self.seniority_month)
        seniority_layout.addWidget(QLabel("/"))
        seniority_layout.addWidget(self.seniority_day)
        seniority_layout.addStretch()

        current_grade_form.addRow("الدرجة الحالية:", self.current_degree)
        current_grade_form.addRow("رقم المقرر:", self.decision_number_2)
        current_grade_form.addRow("تاريخ المقرر:", self.decision_date_2)
        current_grade_form.addRow("تاريخ المفعول:", self.effective_date_2)
        current_grade_form.addRow("الأقدمية المحتفظ بها (سنة / شهر / يوم):", seniority_widget)

        current_grade_layout.addLayout(current_grade_form)
        left_layout.addWidget(self.current_grade_frame)

        # Contract Employee Section (Left Column)
        self.contract_employee_frame = QFrame()
        self.contract_employee_frame.setObjectName("sectionFrame")
        contract_employee_layout = QVBoxLayout(self.contract_employee_frame)

        contract_employee_title = QLabel("طبيعة علاقة العمل (عون متعاقد)")
        contract_employee_title.setObjectName("sectionTitle")
        contract_employee_title.setAlignment(Qt.AlignCenter)
        contract_employee_layout.addWidget(contract_employee_title)

        # Contract employee form
        contract_employee_form = QFormLayout()
        contract_employee_form.setVerticalSpacing(15)
        contract_employee_form.setHorizontalSpacing(10)

        self.decision_number_3 = QLineEdit()
        self.decision_number_3.setValidator(QIntValidator())

        # Set current date and prevent future dates
        self.decision_date_3 = QDateEdit()
        self.decision_date_3.setCalendarPopup(True)
        self.decision_date_3.setDisplayFormat("dd/MM/yyyy")
        self.decision_date_3.setDate(QDate.currentDate())
        self.decision_date_3.setMaximumDate(QDate.currentDate())

        # Set current date and prevent future dates
        self.effective_date_3 = QDateEdit()
        self.effective_date_3.setCalendarPopup(True)
        self.effective_date_3.setDisplayFormat("dd/MM/yyyy")
        self.effective_date_3.setDate(QDate.currentDate())
        self.effective_date_3.setMaximumDate(QDate.currentDate())

        self.percentage = QLineEdit()
        self.percentage.setValidator(QIntValidator(0, 100))

        contract_employee_form.addRow("رقم المقرر:", self.decision_number_3)
        contract_employee_form.addRow("تاريخ المقرر:", self.decision_date_3)
        contract_employee_form.addRow("تاريخ المفعول:", self.effective_date_3)
        contract_employee_form.addRow("النسبة المئوية:", self.percentage)

        contract_employee_layout.addLayout(contract_employee_form)
        left_layout.addWidget(self.contract_employee_frame)

        # Original Recruitment Section (Right Column)
        self.original_recruitment_frame = QFrame()
        self.original_recruitment_frame.setObjectName("sectionFrame")
        original_recruitment_layout = QVBoxLayout(self.original_recruitment_frame)

        original_recruitment_title = QLabel("التوظيف الأصلي")
        original_recruitment_title.setObjectName("sectionTitle")
        original_recruitment_title.setAlignment(Qt.AlignCenter)
        original_recruitment_layout.addWidget(original_recruitment_title)

        # Original recruitment form
        original_recruitment_form = QFormLayout()
        original_recruitment_form.setVerticalSpacing(15)
        original_recruitment_form.setHorizontalSpacing(10)

        self.original_recruitment_rank = QLineEdit()
        self.original_recruitment_decision_number = QLineEdit()
        self.original_recruitment_decision_number.setValidator(QIntValidator())

        # Set current date and prevent future dates
        self.original_recruitment_decision_date = QDateEdit()
        self.original_recruitment_decision_date.setCalendarPopup(True)
        self.original_recruitment_decision_date.setDisplayFormat("dd/MM/yyyy")
        self.original_recruitment_decision_date.setDate(QDate.currentDate())
        self.original_recruitment_decision_date.setMaximumDate(QDate.currentDate())

        self.original_recruitment_visa_number = QLineEdit()
        self.original_recruitment_visa_number.setValidator(QIntValidator())

        # Set current date and prevent future dates
        self.original_recruitment_visa_date = QDateEdit()
        self.original_recruitment_visa_date.setCalendarPopup(True)
        self.original_recruitment_visa_date.setDisplayFormat("dd/MM/yyyy")
        self.original_recruitment_visa_date.setDate(QDate.currentDate())
        self.original_recruitment_visa_date.setMaximumDate(QDate.currentDate())

        # Set current date and prevent future dates
        self.original_recruitment_effective_date = QDateEdit()
        self.original_recruitment_effective_date.setCalendarPopup(True)
        self.original_recruitment_effective_date.setDisplayFormat("dd/MM/yyyy")
        self.original_recruitment_effective_date.setDate(QDate.currentDate())
        self.original_recruitment_effective_date.setMaximumDate(QDate.currentDate())

        self.original_recruitment_report_number = QLineEdit()
        self.original_recruitment_report_number.setValidator(QIntValidator())

        # Set current date and prevent future dates
        self.original_recruitment_report_date = QDateEdit()
        self.original_recruitment_report_date.setCalendarPopup(True)
        self.original_recruitment_report_date.setDisplayFormat("dd/MM/yyyy")
        self.original_recruitment_report_date.setDate(QDate.currentDate())
        self.original_recruitment_report_date.setMaximumDate(QDate.currentDate())

        # Set current date and prevent future dates
        self.original_recruitment_report_effective_date = QDateEdit()
        self.original_recruitment_report_effective_date.setCalendarPopup(True)
        self.original_recruitment_report_effective_date.setDisplayFormat("dd/MM/yyyy")
        self.original_recruitment_report_effective_date.setDate(QDate.currentDate())
        self.original_recruitment_report_effective_date.setMaximumDate(QDate.currentDate())

        self.initial_recruitment = QLineEdit()

        original_recruitment_form.addRow("رتبة التوظيف الأصلي:", self.original_recruitment_rank)
        original_recruitment_form.addRow("رقم المقرر:", self.original_recruitment_decision_number)
        original_recruitment_form.addRow("تاريخ المقرر:", self.original_recruitment_decision_date)
        original_recruitment_form.addRow("رقم التأشيرة:", self.original_recruitment_visa_number)
        original_recruitment_form.addRow("تاريخ التأشيرة:", self.original_recruitment_visa_date)
        original_recruitment_form.addRow("تاريخ المفعول:", self.original_recruitment_effective_date)
        original_recruitment_form.addRow("رقم محضر التنصيب:", self.original_recruitment_report_number)
        original_recruitment_form.addRow("تاريخ محضر التنصيب:", self.original_recruitment_report_date)
        original_recruitment_form.addRow("تاريخ مفعول التنصيب:", self.original_recruitment_report_effective_date)
        original_recruitment_form.addRow("التوظيف الأصلي:", self.initial_recruitment)

        # French recruitment section
        # Create a separator
        separator3 = QFrame()
        separator3.setObjectName("separator")
        separator3.setFrameShape(QFrame.HLine)
        original_recruitment_layout.addWidget(separator3)

        # French recruitment form - using French style (label on right, field on left)
        french_original_recruitment_widget = QWidget()
        french_original_recruitment_layout = QFormLayout(french_original_recruitment_widget)
        french_original_recruitment_layout.setLabelAlignment(Qt.AlignRight)
        french_original_recruitment_layout.setFormAlignment(Qt.AlignRight)

        self.french_original_recruitment_grade = QLineEdit()

        # Set current date and prevent future dates
        self.french_original_recruitment_date = QDateEdit()
        self.french_original_recruitment_date.setCalendarPopup(True)
        self.french_original_recruitment_date.setDisplayFormat("yyyy/MM/dd")
        self.french_original_recruitment_date.setDate(QDate.currentDate())
        self.french_original_recruitment_date.setMaximumDate(QDate.currentDate())

        # Add French labels
        french_original_grade_label = QLabel("Grade de recrutement initial")
        french_original_grade_label.setObjectName("frenchLabel")

        french_original_date_label = QLabel("Date de recrutement initial")
        french_original_date_label.setObjectName("frenchLabel")

        french_original_recruitment_layout.addRow(self.french_original_recruitment_grade, french_original_grade_label)
        french_original_recruitment_layout.addRow(self.french_original_recruitment_date, french_original_date_label)

        original_recruitment_layout.addLayout(original_recruitment_form)
        original_recruitment_layout.addWidget(french_original_recruitment_widget)
        right_layout.addWidget(self.original_recruitment_frame)

        # Affiliation Section (Right Column)
        self.affiliation_frame = QFrame()
        self.affiliation_frame.setObjectName("sectionFrame")
        affiliation_layout = QVBoxLayout(self.affiliation_frame)

        affiliation_title = QLabel("الانتماء")
        affiliation_title.setObjectName("sectionTitle")
        affiliation_title.setAlignment(Qt.AlignCenter)
        affiliation_layout.addWidget(affiliation_title)

        # Affiliation form
        affiliation_form = QFormLayout()
        affiliation_form.setVerticalSpacing(15)
        affiliation_form.setHorizontalSpacing(10)

        self.dependency = CustomComboBox()
        self.dependency.addItems([
            "المديرية",
            "الأمانة العامة",
            "دائرة الاستشراف والتنبيه",
            "دائرة الدراسات والتحليل",
            "دائرة تقويم المناهج ونوعية الأداءات البيداغوجية ",
            "دائرة التعاون والإحصاء والتوثيق والاتصال",
            "دائرة الإدارة والوسائل العامة",
            "الفروع الجهوية"
        ])
        self.dependency.activated.connect(self.handle_dependency_change)

        self.service = CustomComboBox()
        self.service.addItems([
            "مصلحة الاستشراف والبحث في تطور المنظومة الوطنية للتربية والتكوين",
            "مصلحة تكنولوجيات الإعلام والاتصال في ا��منظومة الوطنية للتربية والتكوين",
            "مصلحة إنتاج مؤشرات ومعايير مردودية المنظومة الوطنية للتربية والتكوين",
            "مصلحة وضع مقاربات مقارنة للمنظومة الوطنية للتربية والتكوين",
            "مصلحة دراسة تفاعل مكونات المنظومة الوطنية للتربية والتكوين وتناسقها",
            "مصلحة تحصيل المتعلمين",
            "مصلحة أداءات التأطير",
            "مصلحة مردودية المنظومة الوطنية للتربية والتكوين والمحيط التربوي",
            "مصلحة البرامج والكتب والوسائل التعليمية",
            "مصلحة التعاون والاتصال",
            "مصلحة النشر والتوثيق والإحصاء",
            "مصلحة الإعلام الآلي وبنك المعلومات",
            "مصلحة التنشيط والتثمين",
            "مصلحة تسيير الموظفين",
            "مصلحة الميزانية",
            "مصلحة الوسائل العامة",
            "مصالح الفروع الجهوية"
        ])
        self.service.activated.connect(self.handle_combobox_activation)

        affiliation_form.addRow("التبعية:", self.dependency)
        affiliation_form.addRow("المصلحة:", self.service)

        affiliation_layout.addLayout(affiliation_form)
        right_layout.addWidget(self.affiliation_frame)

        # Current Position Section (Right Column)
        self.current_position_frame = QFrame()
        self.current_position_frame.setObjectName("sectionFrame")
        current_position_layout = QVBoxLayout(self.current_position_frame)

        current_position_title = QLabel("الوظيفة أو المنصب العالي")
        current_position_title.setObjectName("sectionTitle")
        current_position_title.setAlignment(Qt.AlignCenter)
        current_position_layout.addWidget(current_position_title)

        # Current position form
        current_position_form = QFormLayout()
        current_position_form.setVerticalSpacing(15)
        current_position_form.setHorizontalSpacing(10)

        self.current_position = CustomComboBox(allow_add=False)
        self.current_position.addItems(["منصب عالي", "وظيفة"])
        self.current_position.activated.connect(self.handle_current_position_change)

        self.position_name = QLineEdit()
        self.high_position_name = QLineEdit()
        self.branch = QLineEdit()
        self.decision_number_4 = QLineEdit()
        self.decision_number_4.setValidator(QIntValidator())

        # Set current date and prevent future dates
        self.decision_date_4 = QDateEdit()
        self.decision_date_4.setCalendarPopup(True)
        self.decision_date_4.setDisplayFormat("dd/MM/yyyy")
        self.decision_date_4.setDate(QDate.currentDate())
        self.decision_date_4.setMaximumDate(QDate.currentDate())

        self.visa_number_2 = QLineEdit()
        self.visa_number_2.setValidator(QIntValidator())

        # Set current date and prevent future dates
        self.visa_date_2 = QDateEdit()
        self.visa_date_2.setCalendarPopup(True)
        self.visa_date_2.setDisplayFormat("dd/MM/yyyy")
        self.visa_date_2.setDate(QDate.currentDate())
        self.visa_date_2.setMaximumDate(QDate.currentDate())

        # Set current date and prevent future dates
        self.effective_date_4 = QDateEdit()
        self.effective_date_4.setCalendarPopup(True)
        self.effective_date_4.setDisplayFormat("dd/MM/yyyy")
        self.effective_date_4.setDate(QDate.currentDate())
        self.effective_date_4.setMaximumDate(QDate.currentDate())

        # Create widgets for position name (for وظيفة)
        self.position_name_row = QWidget()
        position_name_layout = QHBoxLayout(self.position_name_row)
        position_name_layout.setContentsMargins(0, 0, 0, 0)
        position_name_layout.addWidget(QLabel("اسم الوظيفة:"))
        position_name_layout.addWidget(self.position_name)

        # Create widgets for high position name (for منصب عالي)
        self.high_position_name_row = QWidget()
        high_position_name_layout = QHBoxLayout(self.high_position_name_row)
        high_position_name_layout.setContentsMargins(0, 0, 0, 0)
        high_position_name_layout.addWidget(QLabel("اسم المنصب العالي:"))
        high_position_name_layout.addWidget(self.high_position_name)

        # Create widgets for branch (for منصب عالي)
        self.branch_row = QWidget()
        branch_layout = QHBoxLayout(self.branch_row)
        branch_layout.setContentsMargins(0, 0, 0, 0)
        branch_layout.addWidget(QLabel("الفرع:"))
        branch_layout.addWidget(self.branch)

        current_position_form.addRow("الوظيفة أو المنصب العالي:", self.current_position)
        current_position_form.addRow("", self.position_name_row)
        current_position_form.addRow("", self.high_position_name_row)
        current_position_form.addRow("", self.branch_row)
        current_position_form.addRow("رقم المقرر:", self.decision_number_4)
        current_position_form.addRow("تاريخ المقرر:", self.decision_date_4)
        current_position_form.addRow("رقم التأشيرة:", self.visa_number_2)
        current_position_form.addRow("تاريخ التأشيرة:", self.visa_date_2)
        current_position_form.addRow("تاريخ المفعول:", self.effective_date_4)

        current_position_layout.addLayout(current_position_form)
        right_layout.addWidget(self.current_position_frame)

        # Special Status Section
        self.special_status_frame = QFrame()
        self.special_status_frame.setObjectName("sectionFrame")
        special_status_layout = QVBoxLayout(self.special_status_frame)

        special_status_title = QLabel("الوضعيات الخاصة")
        special_status_title.setObjectName("sectionTitle")
        special_status_title.setAlignment(Qt.AlignCenter)
        special_status_layout.addWidget(special_status_title)

        # Special status form
        special_status_form = QFormLayout()
        special_status_form.setVerticalSpacing(15)
        special_status_form.setHorizontalSpacing(10)

        self.special_status = CustomComboBox()
        special_status_options = [
            "منتدب إلى",
            "منتدب من",
            "خارج الإطار",
            "وضع تحت التصرف"
        ]
        self.special_status.addItems(special_status_options)
        self.special_status.activated.connect(self.handle_combobox_activation)

        self.dependency_structure = AutoExpandingTextEdit()

        special_status_form.addRow("الوضعية الخاصة:", self.special_status)
        special_status_form.addRow("معلومات إضافية", self.dependency_structure)

        special_status_layout.addLayout(special_status_form)
        right_layout.addWidget(self.special_status_frame)

        # Add columns to the main form layout
        form_layout.addWidget(right_column, 1)  # 1 is the stretch factor
        form_layout.addWidget(left_column, 1)  # 1 is the stretch factor

        # Set the form container as the scroll area widget
        self.scroll_area.setWidget(form_container)
        self.main_layout.addWidget(self.scroll_area)

        # Install event filter to track scrolling
        self.scroll_area.viewport().installEventFilter(self)

        # Initially hide or show frames based on default selection
        self.handle_job_relationship_type_change(0)

        # Fill form with employee data if available
        if employee_data:
            self.fill_form_with_data(employee_data)

        # Set all fields to read-only initially
        self.set_fields_readonly(True)

        # Initially hide or show based on default selection
        self.handle_employment_type_change(0)
        self.handle_current_position_change(0)

        # Set the job relationship type based on employee type
        if self.employee and hasattr(self.employee, 'type'):
            if self.employee.type == "permanent":
                self.job_relationship_type.setCurrentText("موظف")
            elif self.employee.type == "contractuel":
                self.job_relationship_type.setCurrentText("عون متعاقد")
            self.handle_job_relationship_type_change(self.job_relationship_type.currentIndex())

    def handle_combobox_activation(self, index):
        """Handle adding new items to comboboxes"""
        sender = self.sender()
        if isinstance(sender, CustomComboBox) and sender.allow_add and sender.currentText() == sender.addItem_text:
            sender.add_new_item()

    def handle_employment_type_change(self, index):
        """Show/hide fields based on employment type selection"""
        if self.employment_type.currentText() == "مفعل":
            self.employment_reason_row.hide()
            self.decision_number_row.hide()
            self.decision_date_row.hide()
        else:
            self.employment_reason_row.show()
            self.decision_number_row.show()
            self.decision_date_row.show()

    def handle_job_relationship_type_change(self, index):
        """Show/hide frames based on job relationship type selection"""
        if self.job_relationship_type.currentText() == "موظف":
            # Show employee frame, hide contract employee frame
            self.current_grade_frame.show()
            self.contract_employee_frame.hide()
        else:
            # Show contract employee frame, hide employee frame
            self.current_grade_frame.hide()
            self.contract_employee_frame.show()

    def handle_current_position_change(self, index):
        """Show/hide fields based on current position selection"""
        if self.current_position.currentText() == "وظيفة":
            # Show position name, hide high position name and branch
            self.position_name_row.show()
            self.high_position_name_row.hide()
            self.branch_row.hide()
        else:
            # Show high position name and branch, hide position name
            self.position_name_row.hide()
            self.high_position_name_row.show()
            self.branch_row.show()

    def handle_basic_law_selection(self, index):
        """Handle selection of القانون الأساسي"""
        # Clear dependent ComboBoxes
        self.job_category.clear()
        self.silk_category.clear()
        self.job_rank.clear()

        # Get the selected basic law
        law = self.basic_law.currentText()

        if law == "الأسلاك المشتركة":
            # Populate job categories for الأسلاك المشتركة
            self.job_category.addItems(list(self.category_data.keys()))
            self.job_category.setEnabled(True)

            # Connect job category to update silk category
            self.job_category.currentIndexChanged.connect(self.update_silk_category)

            # Initialize silk category with first job category
            if self.job_category.count() > 0:
                self.update_silk_category(0)
        else:
            # Directly populate job ranks based on basic law
            if law == "أسلاك التربية":
                self.job_category.clear()
                self.job_category.addItems(list(self.category_data_2.keys()))
                self.job_category.setEnabled(True)
                self.job_category.currentIndexChanged.connect(self.update_silk_category)
                if self.job_category.count() > 0:
                    self.update_silk_category(0)
            elif law == "الأعوان المتعاقدون":
                # For other basic laws, disable job category and silk category
                self.job_category.setEnabled(False)
                self.silk_category.setEnabled(False)

                self.job_rank.clear()
                self.job_rank.addItems([
                    "عامل مهني من المستوى الأول",
                    "عون خدمة من المستوى الأول",
                    "حارس",
                    "سائق سيارة من المستوى الأول",
                    "عامل مهني من المستوى الثاني",
                    "سائق سيارة من المستوى الثاني",
                    "عون خدمة من المستوى الثاني",
                    "سائق سيارة من المستوى الثالث ورئيس حظيرة",
                    "عامل مهني من المستوى الثالث",
                    "عون خدمة من المستوى الثالث",
                    "عون وقاية من المستوى الأول",
                    "عامل مهني من المستوى الرابع",
                    "عون وقاية من المستوى الثاني"
                ])
                self.job_rank.setEnabled(True)
            else:
                self.job_rank.setEnabled(False)

    def update_silk_category(self, index):
        """Update silk category based on job category selection and basic law"""
        # Clear dependent ComboBoxes
        self.silk_category.clear()
        self.job_rank.clear()

        law = self.basic_law.currentText()
        job_category = self.job_category.currentText()

        # Determine which category data to use
        if law == "الأسلاك المشتركة":
            silks = self.category_data.get(job_category, [])
        elif law == "أسلاك التربية":
            silks = self.category_data_2.get(job_category, [])
        else:
            silks = []

        # Populate silk category
        if silks:
            self.silk_category.addItems(silks)
            self.silk_category.setEnabled(True)
            self.update_job_rank(0)  # Initialize with first silk
        else:
            self.silk_category.setEnabled(False)
            self.job_rank.setEnabled(False)

    def update_job_rank(self, index):
        """Update job rank based on silk category selection and basic law"""
        self.job_rank.clear()

        law = self.basic_law.currentText()
        silk = self.silk_category.currentText()

        if law == "الأسلاك المشتركة":
            ranks = self.rank_data.get(silk, [])
        elif law == "أسلاك التربية":
            ranks = self.rank_data_2.get(silk, [])
        else:
            ranks = []

        if ranks:
            self.job_rank.addItems(ranks)
            self.job_rank.setEnabled(True)
        else:
            self.job_rank.setEnabled(False)

    def handle_dependency_change(self, index):
        """Update service options based on selected dependency"""
        dependency = self.dependency.currentText()

        # Clear current items
        self.service.clear()

        # Add appropriate service options based on dependency selection
        if dependency == "المديرية" or dependency == "الأمانة العامة":
            # No options for these dependencies
            pass
        elif dependency == "دائرة الاستشراف والتنبيه":
            self.service.addItems([
                "مصلحة الاستشراف والبحث في تطور المنظومة الوطنية للتربية والتكوين",
                "مصلحة تكنولوجيات الإعلام والاتصال في المنظومة الوطنية للتربية والتكوين"
            ])
        elif dependency == "دائرة الدراسات والتحليل":
            self.service.addItems([
                "مصلحة إنتاج مؤشرات ومعايير مردودية المنظومة الوطنية للتربية والتكوين",
                "مصلحة وضع مقاربات مقارنة للمنظومة الوطنية للتربية والتكوين",
                "مصلحة دراسة تفاعل مكونات المنظومة الوطنية للتربية والتكوين وتناسقها"
            ])
        elif dependency == "دائرة تقويم المناهج ونوعية الأداءات البيداغوجية" or dependency == "دائرة تقويم المناهج ونوعية الأداءات البيداغوجية ":
            self.service.addItems([
                "مصلحة تحصيل المتعلمين",
                "مصلحة أداءات التأطير",
                "مصلحة مردودية المنظومة الوطنية للتربية والتكوين والمحيط التربوي",
                "مصلحة البرامج والكتب والوسائل التعليمية"
            ])
        elif dependency == "دائرة التعاون والإحصاء والتوثيق والاتصال":
            self.service.addItems([
                "مصلحة التعاون والاتصال",
                "مصلحة النشر والتوثيق والإحصاء",
                "مصلحة الإعلام الآلي وبنك المعلومات",
                "مصلحة التنشيط والتثمين"
            ])
        elif dependency == "دائرة الإدارة والوسائل العامة":
            self.service.addItems([
                "مصلحة تسيير الموظفين",
                "مصلحة الميزانية",
                "مصلحة الوسائل العامة"
            ])
        elif dependency == "الفروع الجهوية":
            self.service.addItems(["مصالح الفروع الجهوية"])

    def eventFilter(self, obj, event):
        """Event filter to handle scrolling and keep the header visible"""
        if obj == self.scroll_area.viewport() and event.type() == QEvent.Wheel:
            # You could add animation here to show/hide the header based on scroll position
            # For now, we'll just keep it visible all the time
            pass
        return super().eventFilter(obj, event)

    def fill_form_with_data(self, data):
        """Fill the form with employee data"""
        # Personal information
        self.name.setText(data.get("الاسم", ""))
        self.surname.setText(data.get("اللقب", ""))
        self.spouse_surname.setText(data.get("لقب الزوج ", ""))

        # Try to parse birth date
        birth_date_str = data.get("تاريخ الميلاد", "")
        if birth_date_str:
            try:
                # Try different date formats
                for fmt in ["yyyy-MM-dd", "dd/MM/yyyy", "MM/dd/yyyy"]:
                    date = QDate.fromString(birth_date_str, fmt)
                    if date.isValid():
                        self.birth_date.setDate(date)
                        break
            except:
                pass

        # Set combobox values
        birth_province = data.get("ولاية الميلاد", "")
        if birth_province:
            index = self.birth_province.findText(birth_province, Qt.MatchContains)
            if index >= 0:
                self.birth_province.setCurrentIndex(index)

        gender = data.get("الجنس", "")
        if gender:
            index = self.gender.findText(gender, Qt.MatchContains)
            if index >= 0:
                self.gender.setCurrentIndex(index)

        marital_status = data.get(" الوضعية العائلية", "")
        if marital_status:
            index = self.marital_status.findText(marital_status, Qt.MatchContains)
            if index >= 0:
                self.marital_status.setCurrentIndex(index)

        national_service = data.get(" الوضعية تجاه الخدمة الوطنية", "")
        if national_service:
            index = self.national_service.findText(national_service, Qt.MatchContains)
            if index >= 0:
                self.national_service.setCurrentIndex(index)

        # Education
        original_education = data.get("الشهادة التي تم على أساسهاالتوظيف الأصلي", "")
        if original_education:
            index = self.original_education.findText(original_education, Qt.MatchContains)
            if index >= 0:
                self.original_education.setCurrentIndex(index)

        current_education = data.get("الشهادة الحالية ", "")
        if current_education:
            index = self.current_education.findText(current_education, Qt.MatchContains)
            if index >= 0:
                self.current_education.setCurrentIndex(index)

        # Employment
        employment_type = data.get("التفعيل", "")
        if employment_type:
            index = self.employment_type.findText(employment_type, Qt.MatchContains)
            if index >= 0:
                self.employment_type.setCurrentIndex(index)
                self.handle_employment_type_change(index)

        # Job information
        job_relationship_type = data.get("طبيعة علاقة العمل (موظف عون متعاقد)", "")
        if job_relationship_type:
            index = self.job_relationship_type.findText(job_relationship_type, Qt.MatchContains)
            if index >= 0:
                self.job_relationship_type.setCurrentIndex(index)
                self.handle_job_relationship_type_change(index)

        job_rank = data.get("الرتبة أو منصب الشغل الحالي ", "")
        if job_rank:
            self.job_rank.addItem(job_rank)
            self.job_rank.setCurrentText(job_rank)

        # Try to parse effective date
        effective_date_str = data.get("تاريخ المفعول ", "")
        if effective_date_str:
            try:
                # Try different date formats
                for fmt in ["yyyy-MM-dd", "dd/MM/yyyy", "MM/dd/yyyy"]:
                    date = QDate.fromString(effective_date_str, fmt)
                    if date.isValid():
                        self.effective_date.setDate(date)
                        break
            except:
                pass

        # Set service and dependency
        service = data.get("المصلحة", "")
        if service:
            index = self.service.findText(service, Qt.MatchContains)
            if index >= 0:
                self.service.setCurrentIndex(index)
            else:
                self.service.addItem(service)
                self.service.setCurrentText(service)

        dependency = data.get("التبعية", "")
        if dependency:
            index = self.dependency.findText(dependency, Qt.MatchContains)
            if index >= 0:
                self.dependency.setCurrentIndex(index)
            else:
                self.dependency.addItem(dependency)
                self.dependency.setCurrentText(dependency)

        # Load data from database models
        if self.employee:
            # Load data from the employee model
            self.load_data_from_models()

    def load_data_from_models(self):
        """Load data from database models into the form"""
        if not self.employee:
            return

        # Load basic employee data
        self.name.setText(self.employee.Prenom)
        self.surname.setText(self.employee.Nom)
        self.spouse_surname.setText(self.employee.NomEpoux or "")
        
        if self.employee.Datedenaissance:
            self.birth_date.setDate(QDate.fromString(self.employee.Datedenaissance.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        
        if self.employee.Lieudenaissance:
            index = self.birth_province.findText(self.employee.Lieudenaissance, Qt.MatchContains)
            if index >= 0:
                self.birth_province.setCurrentIndex(index)
        
        if self.employee.Sexe:
            index = self.gender.findText(self.employee.Sexe, Qt.MatchContains)
            if index >= 0:
                self.gender.setCurrentIndex(index)
        
        self.current_address.setText(self.employee.Adresseactuelle or "")
        self.postal_code.setText(str(self.employee.code_postal) if self.employee.code_postal else "")
        self.phone_numbers.setText(str(self.employee.phone_numbers) if self.employee.phone_numbers else "")
        self.email.setText(self.employee.email or "")
        self.social_security_num.setText(str(self.employee.social_security_num) if self.employee.social_security_num else "")
        self.national_id.setText(str(self.employee.national_id) if self.employee.national_id else "")
        
        if self.employee.Statutfamilial:
            index = self.marital_status.findText(self.employee.Statutfamilial, Qt.MatchContains)
            if index >= 0:
                self.marital_status.setCurrentIndex(index)
        
        self.children_count.setText(str(self.employee.Nombredenfants) if self.employee.Nombredenfants else "")
        
        if self.employee.Servicesnationale:
            index = self.national_service.findText(self.employee.Servicesnationale, Qt.MatchContains)
            if index >= 0:
                self.national_service.setCurrentIndex(index)
        
        # French information
        self.french_lastname.setText(self.employee.NomFR or "")
        self.french_name.setText(self.employee.PrenomFR or "")
        self.french_lastname_hus.setText(self.employee.NomEpouxFR or "")
        
        if self.employee.WilayenaissanceFR:
            index = self.french_birth_province.findText(self.employee.WilayenaissanceFR, Qt.MatchContains)
            if index >= 0:
                self.french_birth_province.setCurrentIndex(index)

        # Set employment type
        self.employment_type.setCurrentText("مفعل" if self.employee.Statut else "غير مفعل")
        self.handle_employment_type_change(self.employment_type.currentIndex())

        # Set job relationship type based on employee type
        if self.employee.type == "permanent":
            self.job_relationship_type.setCurrentText("موظف")
            
            # Load permanent-specific data
            if hasattr(self.employee, 'current_degree'):
                self.current_degree.setCurrentText(str(self.employee.current_degree) if self.employee.current_degree is not None else "0")
            
            if hasattr(self.employee, 'Cchiff'):
                self.decision_number_2.setText(self.employee.Cchiff or "")
            
            if hasattr(self.employee, 'Cdate_chiff') and self.employee.Cdate_chiff:
                self.decision_date_2.setDate(QDate.fromString(self.employee.Cdate_chiff.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            if hasattr(self.employee, 'Cdate_effet') and self.employee.Cdate_effet:
                self.effective_date_2.setDate(QDate.fromString(self.employee.Cdate_effet.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            if hasattr(self.employee, 'NBR_A'):
                self.seniority_year.setText(str(self.employee.NBR_A) if self.employee.NBR_A is not None else "")
            
            if hasattr(self.employee, 'NBR_M'):
                self.seniority_month.setText(str(self.employee.NBR_M) if self.employee.NBR_M is not None else "")
            
            if hasattr(self.employee, 'NBR_J'):
                self.seniority_day.setText(str(self.employee.NBR_J) if self.employee.NBR_J is not None else "")
            
        elif self.employee.type == "contractuel":
            self.job_relationship_type.setCurrentText("عون متعاقد")
            
            # Load contractuel-specific data
            if hasattr(self.employee, 'Cchiff'):
                self.decision_number_3.setText(self.employee.Cchiff or "")
            
            if hasattr(self.employee, 'Cdate_chiff') and self.employee.Cdate_chiff:
                self.decision_date_3.setDate(QDate.fromString(self.employee.Cdate_chiff.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            if hasattr(self.employee, 'Cdate_effet') and self.employee.Cdate_effet:
                self.effective_date_3.setDate(QDate.fromString(self.employee.Cdate_effet.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            if hasattr(self.employee, 'percentage'):
                self.percentage.setText(str(self.employee.percentage) if self.employee.percentage is not None else "")
        
        self.handle_job_relationship_type_change(self.job_relationship_type.currentIndex())

        # Load career data
        if self.carriere:
            # Education
            if self.carriere.Dipinitial:
                index = self.original_education.findText(self.carriere.Dipinitial, Qt.MatchContains)
                if index >= 0:
                    self.original_education.setCurrentIndex(index)
            
            if self.carriere.Dipactuel:
                index = self.current_education.findText(self.carriere.Dipactuel, Qt.MatchContains)
                if index >= 0:
                    self.current_education.setCurrentIndex(index)
            
            self.other_certifications.setText(self.carriere.DipAutres or "")
            
            # Job information
            if self.carriere.Lb:
                index = self.basic_law.findText(self.carriere.Lb, Qt.MatchContains)
                if index >= 0:
                    self.basic_law.setCurrentIndex(index)
                    self.handle_basic_law_selection(index)
            
            # Try to set job category, silk, and rank
            if self.carriere.cat:
                index = self.job_category.findText(self.carriere.cat, Qt.MatchContains)
                if index >= 0:
                    self.job_category.setCurrentIndex(index)
                    self.update_silk_category(index)
            
            if self.carriere.silk:
                index = self.silk_category.findText(self.carriere.silk, Qt.MatchContains)
                if index >= 0:
                    self.silk_category.setCurrentIndex(index)
                    self.update_job_rank(index)
            
            if self.carriere.Nomposte:
                index = self.job_rank.findText(self.carriere.Nomposte, Qt.MatchContains)
                if index >= 0:
                    self.job_rank.setCurrentIndex(index)
                else:
                    self.job_rank.addItem(self.carriere.Nomposte)
                    self.job_rank.setCurrentText(self.carriere.Nomposte)
            
            # Appointment details
            self.appointment_decision_number.setText(str(self.carriere.NumD) if self.carriere.NumD else "")
            
            if self.carriere.DateD:
                self.appointment_decision_date.setDate(QDate.fromString(self.carriere.DateD.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            self.visa_number.setText(str(self.carriere.visaNUM) if self.carriere.visaNUM else "")
            
            if self.carriere.visaDate:
                self.visa_date.setDate(QDate.fromString(self.carriere.visaDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            if self.carriere.effectiveDate:
                self.effective_date.setDate(QDate.fromString(self.carriere.effectiveDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            self.appointment_report_number.setText(str(self.carriere.pvNUM) if self.carriere.pvNUM else "")
            
            if self.carriere.PvDate:
                self.appointment_report_date.setDate(QDate.fromString(self.carriere.PvDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            if self.carriere.pvEffetDate:
                self.appointment_effective_date.setDate(QDate.fromString(self.carriere.pvEffetDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            if self.carriere.position:
                index = self.position_status.findText(self.carriere.position, Qt.MatchContains)
                if index >= 0:
                    self.position_status.setCurrentIndex(index)
            
            # French grade
            self.current_grade.setCurrentText(self.carriere.FRPoste or "")
            
            if self.carriere.FRDatePoste:
                self.current_grade_date.setDate(QDate.fromString(self.carriere.FRDatePoste.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            # Classification
            if self.carriere.current_class:
                index = self.current_class.findText(self.carriere.current_class, Qt.MatchContains)
                if index >= 0:
                    self.current_class.setCurrentIndex(index)
            
            self.current_reference_number.setText(self.carriere.current_reference_number or "")
            
            # Original recruitment
            self.original_recruitment_rank.setText(self.carriere.GRec or "")
            self.original_recruitment_decision_number.setText(str(self.carriere.RecNUM) if self.carriere.RecNUM else "")
            
            if self.carriere.RecDate:
                self.original_recruitment_decision_date.setDate(QDate.fromString(self.carriere.RecDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            self.original_recruitment_visa_number.setText(str(self.carriere.RecVisaNUM) if self.carriere.RecVisaNUM else "")
            
            if self.carriere.RecVisaDate:
                self.original_recruitment_visa_date.setDate(QDate.fromString(self.carriere.RecVisaDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            if self.carriere.RecEffetDate:
                self.original_recruitment_effective_date.setDate(QDate.fromString(self.carriere.RecEffetDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            self.original_recruitment_report_number.setText(str(self.carriere.RecPvNUM) if self.carriere.RecPvNUM else "")
            
            if self.carriere.RecPVDate:
                self.original_recruitment_report_date.setDate(QDate.fromString(self.carriere.RecPVDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            if self.carriere.RecPVEffetDate:
                self.original_recruitment_report_effective_date.setDate(QDate.fromString(self.carriere.RecPVEffetDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            self.initial_recruitment.setText(self.carriere.RecI or "")
            
            # French recruitment
            self.french_original_recruitment_grade.setText(self.carriere.FRGrade or "")
            
            if self.carriere.FRGradeDate:
                self.french_original_recruitment_date.setDate(QDate.fromString(self.carriere.FRGradeDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            # Affiliation
            if self.carriere.dependency:
                index = self.dependency.findText(self.carriere.dependency, Qt.MatchContains)
                if index >= 0:
                    self.dependency.setCurrentIndex(index)
                    self.handle_dependency_change(index)
            
            if self.carriere.service:
                index = self.service.findText(self.carriere.service, Qt.MatchContains)
                if index >= 0:
                    self.service.setCurrentIndex(index)
                else:
                    self.service.addItem(self.carriere.service)
                    self.service.setCurrentText(self.carriere.service)
            
            # Current position
            if self.carriere.posType:
                index = self.current_position.findText(self.carriere.posType, Qt.MatchContains)
                if index >= 0:
                    self.current_position.setCurrentIndex(index)
                    self.handle_current_position_change(index)
            
            self.position_name.setText(self.carriere.posNomPoste or "")
            self.high_position_name.setText(self.carriere.posNomSup or "")
            self.branch.setText(self.carriere.br or "")
            self.decision_number_4.setText(str(self.carriere.posNUM) if self.carriere.posNUM else "")
            
            if self.carriere.posDate:
                self.decision_date_4.setDate(QDate.fromString(self.carriere.posDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            self.visa_number_2.setText(str(self.carriere.posVisaNUM) if self.carriere.posVisaNUM else "")
            
            if self.carriere.posVisaDate:
                self.visa_date_2.setDate(QDate.fromString(self.carriere.posVisaDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            if self.carriere.posEffetDate:
                self.effective_date_4.setDate(QDate.fromString(self.carriere.posEffetDate.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            
            # Special status
            if self.carriere.spe:
                index = self.special_status.findText(self.carriere.spe, Qt.MatchContains)
                if index >= 0:
                    self.special_status.setCurrentIndex(index)
            
            self.dependency_structure.setText(self.carriere.plusInfo or "")

    def set_fields_readonly(self, readonly=True):
        """Set all form fields to read-only or editable"""
        # Personal information
        self.name.setReadOnly(readonly)
        self.surname.setReadOnly(readonly)
        self.spouse_surname.setReadOnly(readonly)
        self.birth_date.setReadOnly(readonly)
        self.birth_province.setEnabled(not readonly)
        self.father_name.setReadOnly(readonly)
        self.mother_name.setReadOnly(readonly)
        self.gender.setEnabled(not readonly)
        self.current_address.setReadOnly(readonly)
        self.postal_code.setReadOnly(readonly)
        self.phone_numbers.setReadOnly(readonly)
        self.email.setReadOnly(readonly)
        self.social_security_num.setReadOnly(readonly)
        self.national_id.setReadOnly(readonly)
        self.marital_status.setEnabled(not readonly)
        self.children_count.setReadOnly(readonly)
        self.national_service.setEnabled(not readonly)
        self.original_education.setEnabled(not readonly)
        self.current_education.setEnabled(not readonly)
        self.other_certifications.setReadOnly(readonly)

        # French information
        self.french_lastname.setReadOnly(readonly)
        self.french_name.setReadOnly(readonly)
        self.french_lastname_hus.setReadOnly(readonly)
        self.french_birthday.setReadOnly(readonly)
        self.french_birth_province.setEnabled(not readonly)

        # Employment
        self.employment_type.setEnabled(not readonly)
        self.employment_status_reason.setEnabled(not readonly)
        self.decision_number.setReadOnly(readonly)
        self.decision_date.setReadOnly(readonly)

        # Current job
        self.job_relationship_type.setEnabled(not readonly)
        self.basic_law.setEnabled(not readonly)
        self.job_category.setEnabled(not readonly)
        self.silk_category.setEnabled(not readonly)
        self.job_rank.setEnabled(not readonly)
        self.appointment_decision_number.setReadOnly(readonly)
        self.appointment_decision_date.setReadOnly(readonly)
        self.visa_number.setReadOnly(readonly)
        self.visa_date.setReadOnly(readonly)
        self.effective_date.setReadOnly(readonly)
        self.appointment_report_number.setReadOnly(readonly)
        self.appointment_report_date.setReadOnly(readonly)
        self.appointment_effective_date.setReadOnly(readonly)
        self.position_status.setEnabled(not readonly)

        # French grade
        self.current_grade.setEnabled(not readonly)
        self.current_grade_date.setReadOnly(readonly)

        # Classification
        self.current_class.setEnabled(not readonly)
        self.current_reference_number.setReadOnly(readonly)

        # Current grade (employee)
        self.current_degree.setEnabled(not readonly)
        self.decision_number_2.setReadOnly(readonly)
        self.decision_date_2.setReadOnly(readonly)
        self.effective_date_2.setReadOnly(readonly)
        self.seniority_year.setReadOnly(readonly)
        self.seniority_month.setReadOnly(readonly)
        self.seniority_day.setReadOnly(readonly)

        # Contract employee
        self.decision_number_3.setReadOnly(readonly)
        self.decision_date_3.setReadOnly(readonly)
        self.effective_date_3.setReadOnly(readonly)
        self.percentage.setReadOnly(readonly)

        # Original recruitment
        self.original_recruitment_rank.setReadOnly(readonly)
        self.original_recruitment_decision_number.setReadOnly(readonly)
        self.original_recruitment_decision_date.setReadOnly(readonly)
        self.original_recruitment_visa_number.setReadOnly(readonly)
        self.original_recruitment_visa_date.setReadOnly(readonly)
        self.original_recruitment_effective_date.setReadOnly(readonly)
        self.original_recruitment_report_number.setReadOnly(readonly)
        self.original_recruitment_report_date.setReadOnly(readonly)
        self.original_recruitment_report_effective_date.setReadOnly(readonly)
        self.initial_recruitment.setReadOnly(readonly)
        self.french_original_recruitment_grade.setReadOnly(readonly)
        self.french_original_recruitment_date.setReadOnly(readonly)

        # Current position
        self.current_position.setEnabled(not readonly)
        self.position_name.setReadOnly(readonly)
        self.high_position_name.setReadOnly(readonly)
        self.branch.setReadOnly(readonly)
        self.decision_number_4.setReadOnly(readonly)
        self.decision_date_4.setReadOnly(readonly)
        self.visa_number_2.setReadOnly(readonly)
        self.visa_date_2.setReadOnly(readonly)
        self.effective_date_4.setReadOnly(readonly)

        # Special status
        self.special_status.setEnabled(not readonly)
        self.dependency_structure.setReadOnly(readonly)

        # Affiliation
        self.dependency.setEnabled(not readonly)
        self.service.setEnabled(not readonly)

    def toggle_edit_mode(self):
        """Toggle between read-only and edit mode"""
        if not self.edit_mode:
            # Switching to edit mode - save a backup of current data
            self.backup_data = self.get_current_form_data()
            self.edit_mode = True
            self.set_fields_readonly(False)
            self.top_bar.edit_btn.setText("حفظ التغييرات")
        else:
            # Switching from edit mode - confirm save or cancel
            dialog = SaveConfirmationDialog(self)
            result = dialog.exec_()

            if result == QDialog.Accepted:
                # Save changes
                self.save_changes()
            else:
                # Cancel changes - restore from backup
                self.restore_from_backup()

            # Return to read-only mode
            self.edit_mode = False
            self.set_fields_readonly(True)
            self.top_bar.edit_btn.setText("تعديل الملف")

    def get_current_form_data(self):
        """Get all current form data as a dictionary for backup"""
        data = {}

        # Personal information
        data["الاسم"] = self.name.text()
        data["اللقب"] = self.surname.text()
        data["لقب الزوج "] = self.spouse_surname.text()
        data["تاريخ الميلاد"] = self.birth_date.date().toString("yyyy-MM-dd")
        data["ولاية الميلاد"] = self.birth_province.currentText()
        data["الجنس"] = self.gender.currentText()
        data[" الوضعية العائلية"] = self.marital_status.currentText()
        data[" الوضعية تجاه الخدمة الوطنية"] = self.national_service.currentText()
        data["الشهادة التي تم على أساسهاالتوظيف الأصلي"] = self.original_education.currentText()
        data["الشهادة الحالية "] = self.current_education.currentText()
        data["التفعيل"] = self.employment_type.currentText()
        data["طبيعة علاقة العمل (موظف عون متعاقد)"] = self.job_relationship_type.currentText()
        data["الرتبة أو منصب الشغل الحالي "] = self.job_rank.currentText()
        data["تاريخ المفعول "] = self.effective_date.date().toString("yyyy-MM-dd")
        data["المصلحة"] = self.service.currentText()
        data["التبعية"] = self.dependency.currentText()

        # Add all other fields as needed

        return data

    def restore_from_backup(self):
        """Restore form data from backup after canceling edit"""
        if hasattr(self, 'backup_data'):
            self.fill_form_with_data(self.backup_data)

            # Re-apply conditional display logic
            index = self.employment_type.currentIndex()
            self.handle_employment_type_change(index)

            index = self.job_relationship_type.currentIndex()
            self.handle_job_relationship_type_change(index)

            index = self.current_position.currentIndex()
            self.handle_current_position_change(index)

    def save_changes(self):
        """Save changes to employee data"""
        try:
            # Update employee data in database
            if self.employee:
                # Update employee basic info
                self.employee.Nom = self.surname.text()
                self.employee.Prenom = self.name.text()
                self.employee.NomEpoux = self.spouse_surname.text()
                self.employee.Datedenaissance = self.birth_date.date().toPyDate()
                self.employee.Lieudenaissance = self.birth_province.currentText()
                self.employee.Sexe = self.gender.currentText()
                self.employee.Statut = self.employment_type.currentText() == "مفعل"
                self.employee.social_security_num = int(self.social_security_num.text()) if self.social_security_num.text().isdigit() else 0
                self.employee.national_id = int(self.national_id.text()) if self.national_id.text().isdigit() else 0
                self.employee.Adresseactuelle = self.current_address.text()
                self.employee.code_postal = int(self.postal_code.text()) if self.postal_code.text().isdigit() else 0
                self.employee.phone_numbers = int(self.phone_numbers.text()) if self.phone_numbers.text().isdigit() else 0
                self.employee.email = self.email.text()
                self.employee.Nomdupere = self.father_name.text()
                self.employee.Nomdelamere = self.mother_name.text()
                self.employee.Statutfamilial = self.marital_status.currentText()
                self.employee.Nombredenfants = int(self.children_count.text()) if self.children_count.text().isdigit() else 0
                self.employee.Servicesnationale = self.national_service.currentText()
                self.employee.NomFR = self.french_lastname.text()
                self.employee.PrenomFR = self.french_name.text()
                self.employee.NomEpouxFR = self.french_lastname_hus.text()
                self.employee.WilayenaissanceFR = self.french_birth_province.currentText()

                # Update career info
                if self.carriere:
                    self.carriere.Dipinitial = self.original_education.currentText()
                    self.carriere.Dipactuel = self.current_education.currentText()
                    self.carriere.DipAutres = self.other_certifications.toPlainText()
                    self.carriere.Lb = self.basic_law.currentText()
                    self.carriere.cat = self.job_category.currentText()
                    self.carriere.silk = self.silk_category.currentText()
                    self.carriere.Nomposte = self.job_rank.currentText()
                    self.carriere.NumD = int(self.appointment_decision_number.text()) if self.appointment_decision_number.text().isdigit() else 0
                    self.carriere.DateD = self.appointment_decision_date.date().toPyDate()
                    self.carriere.visaNUM = int(self.visa_number.text()) if self.visa_number.text().isdigit() else 0
                    self.carriere.visaDate = self.visa_date.date().toPyDate()
                    self.carriere.effectiveDate = self.effective_date.date().toPyDate()
                    self.carriere.pvNUM = int(self.appointment_report_number.text()) if self.appointment_report_number.text().isdigit() else 0
                    self.carriere.PvDate = self.appointment_report_date.date().toPyDate()
                    self.carriere.pvEffetDate = self.appointment_effective_date.date().toPyDate()
                    self.carriere.position = self.position_status.currentText()
                    self.carriere.FRPoste = self.current_grade.currentText()
                    self.carriere.FRDatePoste = self.current_grade_date.date().toPyDate()
                    self.carriere.activite = self.employment_type.currentText()
                    self.carriere.actR = self.employment_status_reason.currentText()
                    self.carriere.actNUM = int(self.decision_number.text()) if self.decision_number.text().isdigit() else 0
                    self.carriere.actDate = self.decision_date.date().toPyDate()
                    self.carriere.current_class = self.current_class.currentText()
                    self.carriere.current_reference_number = self.current_reference_number.text()
                    self.carriere.GRec = self.original_recruitment_rank.text()
                    self.carriere.RecI = self.initial_recruitment.text()
                    self.carriere.RecNUM = int(self.original_recruitment_decision_number.text()) if self.original_recruitment_decision_number.text().isdigit() else 0
                    self.carriere.RecDate = self.original_recruitment_decision_date.date().toPyDate()
                    self.carriere.RecVisaNUM = int(self.original_recruitment_visa_number.text()) if self.original_recruitment_visa_number.text().isdigit() else 0
                    self.carriere.RecVisaDate = self.original_recruitment_visa_date.date().toPyDate()
                    self.carriere.RecEffetDate = self.original_recruitment_effective_date.date().toPyDate()
                    self.carriere.RecPvNUM = int(self.original_recruitment_report_number.text()) if self.original_recruitment_report_number.text().isdigit() else 0
                    self.carriere.RecPVDate = self.original_recruitment_report_date.date().toPyDate()
                    self.carriere.RecPVEffetDate = self.original_recruitment_report_effective_date.date().toPyDate()
                    self.carriere.FRGrade = self.french_original_recruitment_grade.text()
                    self.carriere.FRGradeDate = self.french_original_recruitment_date.date().toPyDate()
                    self.carriere.dependency = self.dependency.currentText()
                    self.carriere.service = self.service.currentText()
                    self.carriere.posType = self.current_position.currentText()
                    self.carriere.posNomPoste = self.position_name.text()
                    self.carriere.posNomSup = self.high_position_name.text()
                    self.carriere.br = self.branch.text()
                    self.carriere.posNUM = int(self.decision_number_4.text()) if self.decision_number_4.text().isdigit() else 0
                    self.carriere.posDate = self.decision_date_4.date().toPyDate()
                    self.carriere.posVisaNUM = int(self.visa_number_2.text()) if self.visa_number_2.text().isdigit() else 0
                    self.carriere.posVisaDate = self.visa_date_2.date().toPyDate()
                    self.carriere.posEffetDate = self.effective_date_4.date().toPyDate()
                    self.carriere.spe = self.special_status.currentText()
                    self.carriere.plusInfo = self.dependency_structure.toPlainText()

                # Update type-specific data based on employee type
                if self.job_relationship_type.currentText() == "موظف":
                    # Update permanent employee data
                    from Models.Permanent import Permanent
                    
                    # Check if employee is already a permanent
                    if self.employee.type == "permanent":
                        # Update existing permanent data
                        permanent = self.session.query(Permanent).filter_by(idemploye=self.employee.idemploye).first()
                        if permanent:
                            permanent.current_degree = int(self.current_degree.currentText()) if self.current_degree.currentText().isdigit() else 0
                            permanent.Cchiff = self.decision_number_2.text()
                            permanent.Cdate_chiff = self.decision_date_2.date().toPyDate()
                            permanent.Cdate_effet = self.effective_date_2.date().toPyDate()
                            permanent.NBR_A = int(self.seniority_year.text()) if self.seniority_year.text().isdigit() else 0
                            permanent.NBR_M = int(self.seniority_month.text()) if self.seniority_month.text().isdigit() else 0
                            permanent.NBR_J = int(self.seniority_day.text()) if self.seniority_day.text().isdigit() else 0
                    else:
                        # Convert from contractuel to permanent
                        from Models.Contractuel import Contractuel
                        
                        # Delete existing contractuel record
                        contractuel = self.session.query(Contractuel).filter_by(idemploye=self.employee.idemploye).first()
                        if contractuel:
                            self.session.delete(contractuel)
                        
                        # Create new permanent record
                        permanent = Permanent(
                            idemploye=self.employee.idemploye,
                            current_degree=int(self.current_degree.currentText()) if self.current_degree.currentText().isdigit() else 0,
                            Cchiff=self.decision_number_2.text(),
                            Cdate_chiff=self.decision_date_2.date().toPyDate(),
                            Cdate_effet=self.effective_date_2.date().toPyDate(),
                            NBR_A=int(self.seniority_year.text()) if self.seniority_year.text().isdigit() else 0,
                            NBR_M=int(self.seniority_month.text()) if self.seniority_month.text().isdigit() else 0,
                            NBR_J=int(self.seniority_day.text()) if self.seniority_day.text().isdigit() else 0
                        )
                        self.session.add(permanent)
                        
                        # Update employee type
                        self.employee.type = "permanent"
                
                else:
                    # Update contractuel employee data
                    from Models.Contractuel import Contractuel
                    
                    # Check if employee is already a contractuel
                    if self.employee.type == "contractuel":
                        # Update existing contractuel data
                        contractuel = self.session.query(Contractuel).filter_by(idemploye=self.employee.idemploye).first()
                        if contractuel:
                            contractuel.percentage = float(self.percentage.text()) if self.percentage.text().replace('.', '', 1).isdigit() else 0.0
                            contractuel.Cchiff = self.decision_number_3.text()
                            contractuel.Cdate_chiff = self.decision_date_3.date().toPyDate()
                            contractuel.Cdate_effet = self.effective_date_3.date().toPyDate()
                    else:
                        # Convert from permanent to contractuel
                        from Models.Permanent import Permanent
                        
                        # Delete existing permanent record
                        permanent = self.session.query(Permanent).filter_by(idemploye=self.employee.idemploye).first()
                        if permanent:
                            self.session.delete(permanent)
                        
                        # Create new contractuel record
                        contractuel = Contractuel(
                            idemploye=self.employee.idemploye,
                            percentage=float(self.percentage.text()) if self.percentage.text().replace('.', '', 1).isdigit() else 0.0,
                            Cchiff=self.decision_number_3.text(),
                            Cdate_chiff=self.decision_date_3.date().toPyDate(),
                            Cdate_effet=self.effective_date_3.date().toPyDate()
                        )
                        self.session.add(contractuel)
                        
                        # Update employee type
                        self.employee.type = "contractuel"

                # Commit changes to database
                self.session.commit()

                # Update the top bar with the new name and position
                self.top_bar.employee_name_label.setText(f"{self.name.text()} {self.surname.text()}")
                self.top_bar.employee_position_label.setText(f"{self.job_rank.currentText()} ({self.job_relationship_type.currentText()})")

                #Reload data from models to ensure consistency
                self.load_data_from_models()
                if hasattr(self, "controller") and self.controller:
                    self.controller.log_history(
                        event="تعديل بيانات موظف",
                        details=f"تم تعديل بيانات الموظف: {self.name.text()} {self.surname.text()} (رقم: {self.employee.idemploye})",
                        gestion="إدارة الموظفين",
                        employee_id=self.employee.idemploye
                    )
                # Show success message
                QMessageBox.information(self, "نجاح", "تم حفظ التغييرات بنجاح")
            else:
                QMessageBox.critical(self, "خطأ", "لا يمكن العثور على بيانات الموظف")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ البيانات: {str(e)}")
            self.session.rollback()