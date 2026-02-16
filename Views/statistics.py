from sqlalchemy.orm import Session
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

# Import de vos contrôleurs
from Controllers.stats_controller import (
    repartition_par_sexe,
    repartition_par_wilaya, 
    repartition_par_age,
    repartition_par_statut,
    repartition_par_statut_familial
)

# Couleurs du thème
DARK_BG = "#263238"
DARKER_BG = "#26282b"
MEDIUM_BG = "#37474f"
LIGHT_BG = "#455a64"
ORANGE = "#ff6a0e"
YELLOW = "#ffc20e"
YELLOW_BTN = "#e6b800"
WHITE = "#ffffff"
BLACK = "#000000"
GRAY = "#8f8f8f"
GREEN = "#4CAF50"
RED = "#f44336"

class StatisticsSidebar(QWidget):
    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setup_ui()
        self.load_statistics()
        
        # Timer pour actualisation automatique (optionnel)
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_statistics)
        # Actualiser toutes les 5 minutes (300000 ms)
        # self.auto_refresh_timer.start(300000)

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Titre de la sidebar
        title_label = QLabel("الإحصائيات")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {WHITE};
                padding: 2px;
                border-radius: 5px;
                margin-bottom: 5px;
                margin-top: 10px;
            }}
        """)
        main_layout.addWidget(title_label)
        
        # Zone scrollable pour les statistiques
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                border-color: transparent;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background: {DARK_BG};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {DARK_BG};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {MEDIUM_BG};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # Widget de contenu
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(10)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
        self.setMinimumWidth(280)

    def create_section(self, title: str, data: dict, show_percentage: bool = False):
        """Crée une section de statistiques avec style arabe"""
        # Frame pour la section
        section_frame = QFrame()
        section_frame.setFrameStyle(QFrame.Box)
        section_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {LIGHT_BG};
                border-radius: 8px;
                background-color: {MEDIUM_BG};
                margin: 2px;
            }}
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setContentsMargins(12, 10, 12, 10)
        section_layout.setSpacing(6)
        
        # Titre de la section
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {WHITE};
                background-color: {ORANGE};
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 5px;
                font-size: 16pt;
            }}
        """)
        section_layout.addWidget(title_label)
        
        # Données avec style amélioré
        for key, value in data.items():
            data_frame = QFrame()
            data_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {MEDIUM_BG};
                    border-radius: 4px;
                    margin: 1px;
                    border: 1px solid {LIGHT_BG};
                }}
                
            """)
            
            data_layout = QVBoxLayout(data_frame)
            data_layout.setContentsMargins(8, 6, 8, 6)
            
            # Nom de la statistique
            key_label = QLabel(key)
            key_label.setStyleSheet(f"""
                QLabel {{
                    color: {WHITE};
                    font-size: 16pt;
                    font-weight: normal;
                }}
            """)
            key_label.setAlignment(Qt.AlignCenter)
            
            # Valeur de la statistique
            if show_percentage:
                value_text = f"{value}%"
                if value < 30:
                    color = RED
                elif value < 70:
                    color = YELLOW
                else:
                    color = GREEN
            else:
                value_text = str(value)
                color = ORANGE
            
            value_label = QLabel(value_text)
            value_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: 14pt;
                    font-weight: bold;
                }}
            """)
            value_label.setAlignment(Qt.AlignCenter)
            
            data_layout.addWidget(key_label)
            data_layout.addWidget(value_label)
            section_layout.addWidget(data_frame)
        
        return section_frame

    def load_statistics(self):
        """Charge toutes les statistiques avec gestion d'erreurs améliorée"""
        try:
            # Effacer le contenu existant
            self.clear_content()
            
            # Statistiques par sexe
            try:
                sexe_stats = repartition_par_sexe(self.session)
                if sexe_stats:
                    sexe_section = self.create_section("توزيع حسب الجنس", sexe_stats, show_percentage=True)
                    self.content_layout.addWidget(sexe_section)
            except Exception as e:
                self.add_error_section("خطأ في إحصائيات الجنس", str(e))
            
            # Statistiques par âge
            try:
                age_stats = repartition_par_age(self.session)
                if age_stats:
                    age_section = self.create_section("توزيع حسب العمر", age_stats)
                    self.content_layout.addWidget(age_section)
            except Exception as e:
                self.add_error_section("خطأ في إحصائيات العمر", str(e))
            
            # Statistiques par statut
            try:
                statut_stats = repartition_par_statut(self.session)
                if statut_stats:
                    statut_section = self.create_section("توزيع حسب الحالة", statut_stats, show_percentage=True)
                    self.content_layout.addWidget(statut_section)
            except Exception as e:
                self.add_error_section("خطأ في إحصائيات الحالة", str(e))
            
            # Statistiques par statut familial
            try:
                statut_familial_stats = repartition_par_statut_familial(self.session)
                if statut_familial_stats:
                    statut_familial_section = self.create_section("الحالة العائلية", statut_familial_stats)
                    self.content_layout.addWidget(statut_familial_section)
            except Exception as e:
                self.add_error_section("خطأ في الحالة العائلية", str(e))
            
            # Top 5 Wilayas seulement pour économiser l'espace
            try:
                wilaya_stats = repartition_par_wilaya(self.session)
                if wilaya_stats:
                    top_wilayas = dict(sorted(wilaya_stats.items(), key=lambda x: x[1], reverse=True)[:5])
                    wilaya_section = self.create_section("أعلى 5 ولايات", top_wilayas)
                    self.content_layout.addWidget(wilaya_section)
            except Exception as e:
                self.add_error_section("خطأ في إحصائيات الولايات", str(e))
            
            # Spacer pour pousser le contenu vers le haut
            self.content_layout.addStretch()
            
        except Exception as e:
            self.add_error_section("خطأ عام", f"حدث خطأ عام في تحميل الإحصائيات: {str(e)}")

    def clear_content(self):
        """Efface tout le contenu de la sidebar"""
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

    def add_error_section(self, title: str, error_message: str):
        """Ajoute une section d'erreur"""
        error_frame = QFrame()
        error_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {RED};
                border-radius: 5px;
                background-color: {DARKER_BG};
                margin: 2px;
            }}
        """)
        
        error_layout = QVBoxLayout(error_frame)
        error_layout.setContentsMargins(10, 8, 10, 8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {RED}; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        error_label = QLabel(f"خطأ: {error_message}")
        error_label.setStyleSheet(f"color: {WHITE}; font-size: 8pt;")
        error_label.setWordWrap(True)
        error_label.setAlignment(Qt.AlignRight)
        
        error_layout.addWidget(title_label)
        error_layout.addWidget(error_label)
        
        self.content_layout.addWidget(error_frame)

    def refresh_statistics(self):
        """Actualise les statistiques"""
        try:
            self.load_statistics()
            print("Statistiques actualisées avec succès")
        except Exception as e:
            print(f"Erreur lors de l'actualisation des statistiques: {e}")

    def update_session(self, new_session: Session):
        """Met à jour la session de base de données"""
        self.session = new_session
        self.refresh_statistics()