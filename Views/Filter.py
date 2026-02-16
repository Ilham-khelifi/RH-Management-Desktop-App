
import warnings

# Suppress the DeprecationWarning about sipPyTypeDict
warnings.filterwarnings("ignore", category=DeprecationWarning, module="PyQt5.sip")

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
                             QPushButton, QScrollArea, QWidget, QGroupBox, QGridLayout,
                             QLineEdit, QComboBox, QDateEdit, QMessageBox)
from PyQt5.QtCore import Qt, QDate


class FilterWindow(QDialog):
    def __init__(self, parent=None, headers=None):
        super().__init__(parent)
        self.parent = parent
        self.headers = headers or []
        self.setWindowTitle("ترشيح البيانات")
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
            QLineEdit, QComboBox, QDateEdit {
                background-color: {MEDIUM_BG};
                color: {WHITE};
                border: 1px solid {LIGHT_BG};
                border-radius: 4px;
                padding: 5px;
            }
            QScrollArea {
                border: none;
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

        title_label = QLabel("ترشيح البيانات")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        description_label = QLabel("حدد المعايير التي تريد ترشيح البيانات على أساسها")
        description_label.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(title_label)
        header_layout.addWidget(description_label)

        main_layout.addWidget(header_section)

        # Create a scroll area for the filter options
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container for filter options
        filter_container = QWidget()
        filter_layout = QVBoxLayout(filter_container)

        # Create filter groups

        scroll_area.setWidget(filter_container)
        main_layout.addWidget(scroll_area)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.apply_btn = QPushButton("تأكيد")
        self.apply_btn.clicked.connect(self.apply_filter)

        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)

        self.reset_btn = QPushButton("إعادة ضبط")
        self.reset_btn.clicked.connect(self.reset_filters)

        buttons_layout.addWidget(self.apply_btn)
        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(buttons_layout)

        # Initialize filter widgets dictionary
        self.filter_widgets = {}

        # Create filter groups
        self.create_filter_groups(filter_layout)

    def create_filter_groups(self, layout):
        """Create filter groups for different types of data"""
        # Personal Information Group
        personal_group = QGroupBox("البيانات الشخصية")
        personal_layout = QGridLayout(personal_group)

        # Add filter options for personal information
        row = 0
        personal_fields = [
            "رقم الموظف", "الاسم", "اللقب", "لقب الزوج ", "تاريخ الميلاد",
            "ولاية الميلاد", "الجنس", " الوضعية العائلية"
        ]

        for field in personal_fields:
            if field in self.headers:
                checkbox = QCheckBox(field)
                personal_layout.addWidget(checkbox, row, 0)

                # Different input types based on field
                if field == "تاريخ الميلاد":
                    date_edit = QDateEdit()
                    date_edit.setCalendarPopup(True)
                    date_edit.setDate(QDate.currentDate())
                    date_edit.setEnabled(False)
                    personal_layout.addWidget(date_edit, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=date_edit: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": date_edit}
                elif field == "الجنس":
                    gender_combo = QComboBox()
                    gender_combo.addItems(["ذكر", "أنثى"])
                    gender_combo.setEnabled(False)
                    personal_layout.addWidget(gender_combo, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=gender_combo: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": gender_combo}
                elif field == " الوضعية العائلية":
                    status_combo = QComboBox()
                    status_combo.addItems(["أعزب", "متزوج", "مطلق", "أرمل"])
                    status_combo.setEnabled(False)
                    personal_layout.addWidget(status_combo, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=status_combo: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": status_combo}
                elif field == "ولاية الميلاد":
                    state_combo = QComboBox()
                    state_combo.addItems([
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
                    ])
                    state_combo.setEnabled(False)
                    state_combo.setEditable(True)
                    personal_layout.addWidget(state_combo, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=state_combo: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": state_combo}
                else:
                    text_edit = QLineEdit()
                    text_edit.setEnabled(False)
                    personal_layout.addWidget(text_edit, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=text_edit: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": text_edit}

                row += 1

        layout.addWidget(personal_group)

        # Employment Group
        employment_group = QGroupBox("بيانات التوظيف")
        employment_layout = QGridLayout(employment_group)

        # Add filter options for employment information
        row = 0
        employment_fields = [
            "التفعيل", " الوضعية تجاه الخدمة الوطنية", "الشهادة التي تم على أساسهاالتوظيف الأصلي",
            "الشهادة الحالية ", "رتبة التوظيف الأصلي", "الرتبة أو منصب الشغل الحالي "
        ]

        for field in employment_fields:
            if field in self.headers:
                checkbox = QCheckBox(field)
                employment_layout.addWidget(checkbox, row, 0)

                # Different input types based on field
                if field == "التفعيل":
                    status_combo = QComboBox()
                    status_combo.addItems(["مفعل", "غير مفعل"])
                    status_combo.setEnabled(False)
                    employment_layout.addWidget(status_combo, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=status_combo: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": status_combo}
                elif field == " الوضعية تجاه الخدمة الوطنية":
                    service_combo = QComboBox()
                    service_combo.addItems([
                        "مؤدى", "مؤهل لا يجند", "معفى", "مسجل في قوائم الإحصاء",
                        "أجرى فحص الانتقاء الطبي وأعلن مؤهلا للخدمة الوطنية",
                        "إثبات مانع مؤقت أو نهائي للتجنيد", "مستفيد من التأجيل بسبب الدراسة أو التكوين",
                        "مستفيد من إرجاء التجنيد", "أودع ملف إعفاء", "معلن غير مؤهل", "غير معني"
                    ])
                    service_combo.setEnabled(False)
                    service_combo.setEditable(True)
                    employment_layout.addWidget(service_combo, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=service_combo: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": service_combo}
                elif field == "الشهادة التي تم على أساسهاالتوظيف الأصلي" or field == "الشهادة الحالية ":
                    education_combo = QComboBox()
                    education_combo.addItems([
                        "رخصة السياقة", "بدون مستوى", "السنة الثالثة ثانوي", "شهادة الباكالوريا",
                        "شهادة الليسانس", "شهادة الماستر", "شهادة الماجستير", "شهادة الدكتوراه"
                    ])
                    education_combo.setEnabled(False)
                    education_combo.setEditable(True)
                    employment_layout.addWidget(education_combo, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=education_combo: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": education_combo}
                else:
                    text_edit = QLineEdit()
                    text_edit.setEnabled(False)
                    employment_layout.addWidget(text_edit, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=text_edit: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": text_edit}

                row += 1

        # Add Employee Type filter to employment group
        emp_type_checkbox = QCheckBox("طبيعة علاقة العمل (موظف / عون متعاقد)")
        employment_layout.addWidget(emp_type_checkbox, row, 0)
        
        emp_type_combo = QComboBox()
        emp_type_combo.addItems(["موظف", "عون متعاقد"])
        emp_type_combo.setEnabled(False)
        employment_layout.addWidget(emp_type_combo, row, 1)
        emp_type_checkbox.stateChanged.connect(
            lambda state, widget=emp_type_combo: widget.setEnabled(state == Qt.Checked))
        self.filter_widgets["طبيعة علاقة العمل (موظف عون متعاقد)"] = {"checkbox": emp_type_checkbox, "widget": emp_type_combo}

        layout.addWidget(employment_group)

        # Classification Group
        classification_group = QGroupBox("التصنيف والدرجة")
        classification_layout = QGridLayout(classification_group)

        # Add filter options for classification information
        row = 0
        classification_fields = [
            "الصنف الحالي ", "الدرجة الحالية", "تاريخ المفعول "
        ]

        for field in classification_fields:
            if field in self.headers:
                checkbox = QCheckBox(field)
                classification_layout.addWidget(checkbox, row, 0)

                # Different input types based on field
                if field == "تاريخ المفعول ":
                    date_edit = QDateEdit()
                    date_edit.setCalendarPopup(True)
                    date_edit.setDate(QDate.currentDate())
                    date_edit.setEnabled(False)
                    classification_layout.addWidget(date_edit, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=date_edit: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": date_edit}
                elif field == "الصنف الحالي ":
                    class_combo = QComboBox()
                    class_combo.addItems([
                        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17",
                        "ق.ف 1", "ق.ف 2", "ق.ف 3", "ق.ف 4", "ق.ف 5", "ق.ف 6", "ق.ف 7"
                    ])
                    class_combo.setEnabled(False)
                    class_combo.setEditable(True)
                    classification_layout.addWidget(class_combo, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=class_combo: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": class_combo}
                elif field == "الدرجة الحالية":
                    degree_combo = QComboBox()
                    degree_combo.addItems([
                        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"
                    ])
                    degree_combo.setEditable(True)
                    degree_combo.setEnabled(False)
                    classification_layout.addWidget(degree_combo, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=degree_combo: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": degree_combo}
                else:
                    text_edit = QLineEdit()
                    text_edit.setEnabled(False)
                    classification_layout.addWidget(text_edit, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=text_edit: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": text_edit}

                row += 1

        layout.addWidget(classification_group)

        # Affiliation Group
        affiliation_group = QGroupBox("الانتماء")
        affiliation_layout = QGridLayout(affiliation_group)

        # Add filter options for affiliation information
        row = 0
        affiliation_fields = ["التبعية", "المصلحة"]

        for field in affiliation_fields:
            if field in self.headers:
                checkbox = QCheckBox(field)
                affiliation_layout.addWidget(checkbox, row, 0)

                if field == "التبعية":
                    dependency_combo = QComboBox()
                    dependency_combo.addItems([
                        "المديرية", "الأمانة العامة", "دائرة الاستشراف والتنبيه",
                        "دائرة الدراسات والتحليل", "دائرة تقويم المناهج ونوعية الأداءات البيداغوجية ",
                        "دائرة التعاون والإحصاء والتوثيق والاتصال", "دائرة الإدارة والوسائل العامة",
                        "الفروع الجهوية"
                    ])
                    dependency_combo.setEnabled(False)
                    dependency_combo.setEditable(True)
                    affiliation_layout.addWidget(dependency_combo, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=dependency_combo: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": dependency_combo}
                elif field == "المصلحة":
                    service_combo = QComboBox()
                    service_combo.addItems([
                        "مصلحة الاستشراف والبحث في تطور المنظومة الوطنية للتربية والتكوين",
                        "مصلحة تكنولوجيات الإعلام والاتصال في المنظومة الوطنية للتربية والتكوين",
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
                    service_combo.setEnabled(False)
                    service_combo.setEditable(True)
                    affiliation_layout.addWidget(service_combo, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=service_combo: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": service_combo}
                else:
                    text_edit = QLineEdit()
                    text_edit.setEnabled(False)
                    affiliation_layout.addWidget(text_edit, row, 1)
                    checkbox.stateChanged.connect(
                        lambda state, widget=text_edit: widget.setEnabled(state == Qt.Checked))
                    self.filter_widgets[field] = {"checkbox": checkbox, "widget": text_edit}

                row += 1

        layout.addWidget(affiliation_group)

    def reset_filters(self):
        """Reset all filter options"""
        for field_data in self.filter_widgets.values():
            checkbox = field_data["checkbox"]
            widget = field_data["widget"]

            checkbox.setChecked(False)
            widget.setEnabled(False)

            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QDateEdit):
                widget.setDate(QDate.currentDate())

    def get_filter_criteria(self):
        """Get the filter criteria from the selected options"""
        criteria = {}

        for field, field_data in self.filter_widgets.items():
            checkbox = field_data["checkbox"]
            widget = field_data["widget"]

            if checkbox.isChecked():
                if isinstance(widget, QLineEdit):
                    criteria[field] = widget.text()
                elif isinstance(widget, QComboBox):
                    criteria[field] = widget.currentText()
                elif isinstance(widget, QDateEdit):
                    criteria[field] = widget.date().toString("yyyy-MM-dd")

        return criteria

    def apply_filter(self):
        """Apply the filter and close the dialog"""
        criteria = self.get_filter_criteria()

        if not criteria:
            QMessageBox.warning(self, "تحذير", "لم يتم تحديد أي معايير للترشيح")
            return

        # Pass the filter criteria to the parent window
        if self.parent and hasattr(self.parent, "apply_filter_criteria"):
            self.parent.apply_filter_criteria(criteria)
            self.accept()
        else:
            QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء تطبيق الترشيح")