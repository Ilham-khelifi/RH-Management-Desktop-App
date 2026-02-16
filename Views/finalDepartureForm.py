import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QScrollArea, QDateEdit,QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont,QIntValidator
from Models.DepartDefinitif import DepartDefinitif
from Models.Employe import Employe
class FinalDepartureForm(QWidget):
    def __init__(self, session, employe, refresh_callback=None, employe_view = None):
        super().__init__()
        self.session = session
        self.employe = employe
        self.refresh_callback = refresh_callback
        self.employe_view = employe_view
        self.initUI()

    def initUI(self):
        self.setWindowTitle("الرحيل النهائي")
        self.setFixedSize(580, 800)
        self.setStyleSheet("background-color: #263238;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Scroll area setup (no visible frame)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; }")
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

        # Title
        title_label = QLabel("الرحيل النهائي")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 18px;")
        scroll_layout.addWidget(title_label)

        form_container = QFrame()
        form_container.setStyleSheet("background-color: #455A64; border-radius: 10px;")
        form_container.setFixedWidth(500)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(12)

        def create_label(text):
            label = QLabel(text)
            label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-bottom: 15px;")
            return label

        def create_lineedit():
            field = QLineEdit()
            field.setAlignment(Qt.AlignRight)
            
            field.setLayoutDirection(Qt.RightToLeft)
            field.setStyleSheet("""
        QLineEdit {
            background-color: "#26282b";
            color: white; 
            border: none; 
            border-radius: 5px; 
            padding: 10px;
            text-align: right;
        }
        QLineEdit::placeholder {
            color: #AAAAAA;
        }
    """)
            field.returnPressed.connect(self.focus_next_field)
            return field

        def create_dateedit():
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDate(QDate.currentDate())
            date_edit.setLayoutDirection(Qt.RightToLeft)
            date_edit.setAlignment(Qt.AlignRight)
            date_edit.setStyleSheet("""
                QDateEdit {
                    background-color: "#26282b"; 
                    color: white; 
                    border: none; 
                    border-radius: 5px; 
                    padding: 10px;
                    font-weight: bold;
                }
                QCalendarWidget QWidget {
                    background-color: #455A64; 
                    color: white;
                    font-size: 14px;
                }
                QCalendarWidget QToolButton {
                    background-color: #455A64; 
                    color: white;
                    font-size: 14px;
                }
            """)
            return date_edit

        # Champs du formulaire
        form_layout.addWidget(create_label("رقم الموظف"))
        self.field1 = create_lineedit()
        form_layout.addWidget(self.field1)

        form_layout.addWidget(create_label("اللقب"))
        self.field2 = create_lineedit()
        form_layout.addWidget(self.field2)

        form_layout.addWidget(create_label("الاسم"))
        self.field3 = create_lineedit()
        form_layout.addWidget(self.field3)
        if self.employe:
            self.field1.setText(str(self.employe.idemploye))
            self.field2.setText(self.employe.Nom)
            self.field3.setText(self.employe.Prenom)
            self.field1.setReadOnly(True)
            self.field2.setReadOnly(True)
            self.field3.setReadOnly(True)

        form_layout.addWidget(create_label("تفاصيل الرحيل النهائي"))

        form_layout.addWidget(create_label("رقم القرار"))
        self.field4 = create_lineedit()
        self.field4.setValidator(QIntValidator())
        form_layout.addWidget(self.field4)

        form_layout.addWidget(create_label("تاريخ القرار"))
        self.field5 = create_dateedit()
        form_layout.addWidget(self.field5)

        form_layout.addWidget(create_label("تاريخ الرحيل"))
        self.field6 = create_dateedit()
        form_layout.addWidget(self.field6)

        form_layout.addWidget(create_label("سبب المغادرة"))
        self.field7 = create_lineedit()
        form_layout.addWidget(self.field7)

        scroll_layout.addWidget(form_container)

        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(0, 20, 0, 0)

        cancel_button = QPushButton("إلغاء")
        cancel_button.setFixedHeight(50)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: "#f44336"; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        save_button = QPushButton("حفظ")
        save_button.setFixedHeight(50)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: "#4CAF50"; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        scroll_layout.addLayout(buttons_layout)

        # Connexion des boutons
        save_button.clicked.connect(self.save_form)
        cancel_button.clicked.connect(self.cancel_form)

    def focus_next_field(self):
        # Ordre logique des champs
        fields = [
            self.field1, self.field2, self.field3, self.field4,
            self.date_decision, self.date_departure, self.field5
        ]
        current = self.focusWidget()
        if current in fields:
            idx = fields.index(current)
            if idx + 1 < len(fields):
                fields[idx + 1].setFocus()

    def save_form(self):
        numero_decision = self.field4.text().strip()
        date_decision = self.field5.date().toPyDate()
        date_depart = self.field6.date().toPyDate()
        motif = self.field7.text().strip()

        if not (numero_decision and motif):
            print("Veuillez remplir tous les champs obligatoires.")
            return

        try:
            numero_employe = self.field1.text().strip()
            employe = self.session.query(Employe).filter_by(idemploye=int(numero_employe)).first()
            if not employe:
                print("Employé introuvable.")
                return

            depart_def = DepartDefinitif.create(
                session=self.session,
                numero_decision=numero_decision,
                date_decision=date_decision,
                motif=motif,
                date_depart_definitif=date_depart,
                employe=employe
            )
            
            
            self.session.add(depart_def)
            self.session.commit()

            print("Départ définitif enregistré.")
            if self.refresh_callback:
                self.refresh_callback()
            
            QMessageBox.information(self, "Succès", "تمت أرشفة الموظف بنجاح")
            self.close()
        except Exception as e:
            print("Erreur :", e)
            self.session.rollback()

    def cancel_form(self):
        print("Formulaire annulé")
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    app.setFont(QFont("Inter", 12))
    form = FinalDepartureForm()
    form.show()
    sys.exit(app.exec_())