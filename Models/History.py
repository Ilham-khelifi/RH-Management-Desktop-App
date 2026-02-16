from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import re
from Models import Base



class History(Base):
    """
    Modèle SQLAlchemy pour la table d'historique
    Correspond aux données affichées dans la fenêtre d'historique
    """
    __tablename__ = 'history'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey('users.id'))
    event = Column(String(100), nullable=False)
    details = Column(String(255), nullable=False)
    
    # Relations avec les autres entités (optionnelles)
    idemploye = Column(Integer, ForeignKey('employes.idemploye'), nullable=True)
    idFormation = Column(Integer, ForeignKey('formations.idFormation'), nullable=True)
    idConge= Column(Integer, ForeignKey('conges.idConge'), nullable=True)
    idTranche = Column(Integer, ForeignKey('tranches.idTranche'), nullable=True)
    idEvaluation = Column(Integer, ForeignKey('evaluations.idEvaluation'), nullable=True)
    idAbsence = Column(Integer, ForeignKey('absences.idAbsence'), nullable=True)
    gestion = Column(String(50), nullable=False, default="النظام")   
    # Relations
    user = relationship("User", back_populates="history_entries")
    employee = relationship("Employe", back_populates="history_entries")
    formation = relationship("Formation", back_populates="history_entries")
    conge = relationship("Conge", back_populates="history_entries")
    tranche = relationship("Tranche", back_populates="history_entries")
    evaluation = relationship("Evaluation", back_populates="history_entries")
    absence = relationship("Absence", back_populates="history_entries")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'مستخدم محذوف',
            'event': self.event,
            'details': self.details,
            'gestion': self.gestion, 
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else '',
            'idemploye': self.idemploye,
            'idFormation': self.idFormation,
            'idConge': self.idConge,
            'idTranche': self.idTranche,
            'idEvaluation': self.idEvaluation,
            'idAbsence': self.idAbsence
        }

class GestionModules:
    """Constantes pour les différents modules de gestion"""
    EMPLOYES = "إدارة الموظفين"
    CONGES = "إدارة الإجازات"
    ABSENCES = "إدارة الغياب"
    FORMATIONS = "إدارة التكوين"
    EVALUATIONS = "إدارة التقييمات"
    TRANCHES = "إدارة الشرائح"
    COMPTES = "إدارة الحسابات"
    SYSTEME = "النظام"
  


