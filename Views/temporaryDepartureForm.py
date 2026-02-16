import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QScrollArea, QDateEdit, QSizePolicy,QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont,QIntValidator
from Models import Employe
from Models.DepartTemporaire import DepartTemporaire
from Models.Depart import Depart
class TemporaryDepartureForm(QWidget):
    def __init__(self, session, employe, refresh_callback=None):
        super().__init__()
        self.session = session
        self.employe = employe
        self.refresh_callback = refresh_callback
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("الرحيل المؤقت")
        self.setFixedSize(580, 800)
        self.setStyleSheet("background-color: #263238;")

        # Scroll Area Setup
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
            }
            QScrollArea {
                border: none;
            }
        """)

        content_widget = QWidget()
        scroll.setWidget(content_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(15)

        title_label = QLabel("الرحيل المؤقت")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        content_layout.addWidget(title_label)

        form_container = QFrame()
        form_container.setStyleSheet("background-color: #455A64; border-radius: 10px;")
        form_container.setFixedWidth(500)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(12)

        # Liste des champs pour gestion du passage avec Enter
        self.fields = []

        # Fonction d'ajout d’un champ
        def add_label_field(text, widget):
            label = QLabel(text)
            label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-bottom: 4px;")
            form_layout.addWidget(label)
            form_layout.addWidget(widget)
            self.fields.append(widget)  # Ajouter chaque champ à la liste

        def create_lineedit():
            field = QLineEdit()
            field.setAlignment(Qt.AlignRight)
            field.setLayoutDirection(Qt.RightToLeft)  # Ceci est essentiel pour RTL complet
            field.setStyleSheet("""
                    QLineEdit {
            background-color: "#26282b";
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            text-align: right;  /* aligne le texte */
        }
                    QLineEdit::placeholder {
            color: #AAAAAA;
        }
            """)
            field.setFixedHeight(40)
            return field

        def create_dateedit():
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDate(QDate.currentDate())
            date_edit.setStyleSheet("""
                QDateEdit {
                    background-color: "#26282b" ; color: white; border: none;
                    border-radius: 5px; padding: 10px;
                    font-weight: bold;
                }
                QCalendarWidget QToolButton {
                    background-color: #455A64; color: white;
                    font-size: 14px;
                }
            """)
            date_edit.setFixedHeight(40)
            return date_edit

        # Champs classiques
        self.numero_field = create_lineedit()
        add_label_field("رقم الموظف", self.numero_field)

        self.nom_field = create_lineedit()
        add_label_field("اللقب", self.nom_field)

        self.prenom_field = create_lineedit()
        add_label_field("الاسم", self.prenom_field)
        if self.employe:
            self.numero_field.setText(str(self.employe.idemploye))
            self.nom_field.setText(self.employe.Nom)
            self.prenom_field.setText(self.employe.Prenom)

            self.numero_field.setReadOnly(True)
            self.nom_field.setReadOnly(True)
            self.prenom_field.setReadOnly(True)
        # Titre section

        section_label = QLabel("تفاصيل الرحيل المؤقت")
        section_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; margin-top: 10px;")
        form_layout.addWidget(section_label)

        # Champs décision
        self.numeroD_field = create_lineedit()
        self.numeroD_field.setValidator(QIntValidator())
        add_label_field("رقم القرار", self.numeroD_field)
        self.dateD_field = create_dateedit()
        
        add_label_field("تاريخ القرار ", self.dateD_field)
        

        # Champs date: sur la même ligne
        date_row_layout = QHBoxLayout()

        # بداية الرحيل (à droite)
        start_date_layout = QVBoxLayout()
        start_label = QLabel("تاريخ بداية الرحيل")
        start_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-bottom: 4px;")
        self.dateDe_field = create_dateedit()
        start_date = self.dateDe_field
        start_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        start_date_layout.addWidget(start_label)
        start_date_layout.addWidget(start_date)

        # نهاية الرحيل (à gauche)
        end_date_layout = QVBoxLayout()
        end_label = QLabel("تاريخ نهاية الرحيل")
        end_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-bottom: 4px;")
        self.dateF_field = create_dateedit()
        end_date = self.dateF_field
        end_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        end_date_layout.addWidget(end_label)
        end_date_layout.addWidget(end_date)

        # Ajout dans layout horizontal
        date_row_layout.addLayout(start_date_layout)
        date_row_layout.addSpacing(20)
        date_row_layout.addLayout(end_date_layout)

        form_layout.addLayout(date_row_layout)
        self.motif_field = create_lineedit()
        add_label_field("سبب المغادرة", self.motif_field)

        content_layout.addWidget(form_container)

        # Boutons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(0, 20, 0, 0)

        cancel_button = QPushButton("إلغاء")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: "#f44336"; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                padding: 15px;
                font-size: 15px;
                font-weight: bold;
                min-width: 120px;
            }
        """)

        save_button = QPushButton("حفظ")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: "#4CAF50";
                color: white; 
                border: none; 
                border-radius: 5px; 
                padding: 15px;
                font-size: 15px;
                font-weight: bold;
                min-width: 120px;
            }
        """)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        content_layout.addLayout(button_layout)

        # Connexions
        save_button.clicked.connect(self.save_form)
        cancel_button.clicked.connect(self.cancel_form)

        # Passer au champ suivant en appuyant sur "Enter"
        for i in range(len(self.fields) - 1):
            if isinstance(self.fields[i], QLineEdit):
                self.fields[i].returnPressed.connect(self.fields[i + 1].setFocus)

    
    def save_form(self):
        

        # Récupérer les valeurs des champs
        numero_decision = self.numeroD_field.text().strip()
        date_decision = self.dateD_field.date().toPyDate()
        motif = self.motif_field.text().strip()
        date_debut = self.dateDe_field.date().toPyDate()
        date_fin = self.dateF_field.date().toPyDate()
     
        # Validation simple
        if not motif or not numero_decision:
            QMessageBox.warning(self, "تنبيه", "الرجاء ملء جميع الحقول المطلوبة.")
            return
        if date_debut >= date_fin:
            QMessageBox.warning(self, "خطأ في التواريخ", "تاريخ بداية الرحيل يجب أن يكون قبل تاريخ النهاية.")
            return
        try:
            numero_employe = self.numero_field.text().strip()
            employe = self.session.query(Employe).filter_by(idemploye=int(numero_employe)).first()
            if not employe:
                print("Employé non trouvé.")
                return

            # Créer l'objet DepartTemporaire
            depart = DepartTemporaire.create(
                session=self.session,
                numero_decision=numero_decision,
                date_decision=date_decision,
                date_debut=date_debut,
                date_fin=date_fin,
                motif=motif,
                employe=self.employe
            )

            # Modifier le statut de l’employé
            employe.Statut = False

            self.session.add(depart)
            self.session.commit()

            print("Départ temporaire enregistré avec succès.")

            if self.refresh_callback:
                self.refresh_callback()  # Recharge la table
                QMessageBox.information(self, "Succès", "تم الغاء تفعيل الموظف")
            self.close()

        except Exception as e:
            print("Erreur lors de l’enregistrement :", e)
            self.session.rollback()

    def cancel_form(self):
        print("Formulaire annulé")
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    app.setFont(QFont("Inter", 12))
    form = TemporaryDepartureForm()
    form.show()
    sys.exit(app.exec_())