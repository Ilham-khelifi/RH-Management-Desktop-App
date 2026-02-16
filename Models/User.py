from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import re

from Models import Base
class User(Base):
    """
    Modèle SQLAlchemy pour la table des utilisateurs
    Correspond aux données affichées dans la table de gestion des comptes
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    account_number = Column(Integer, unique=True, nullable=False)
    username = Column(String(25), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    creation_date = Column(DateTime, default=datetime.now)
    
    # Relation avec l'historique
    history_entries = relationship("History", back_populates="user")
    
    @staticmethod
    def validate_email(email):
        """Valide le format de l'email (doit être un gmail)"""
        pattern = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """
        Valide la sécurité du mot de passe
        - Au moins 8 caractères
        - Au moins une lettre majuscule
        - Au moins une lettre minuscule
        - Au moins un chiffre
        - Au moins un caractère spécial
        """
        if len(password) < 8:
            return False, "كلمة السر يجب أن تكون 8 أحرف على الأقل"
            
        if not re.search(r'[A-Z]', password):
            return False, "كلمة السر يجب أن تحتوي على حرف كبير واحد على الأقل"
            
        if not re.search(r'[a-z]', password):
            return False, "كلمة السر يجب أن تحتوي على حرف صغير واحد على الأقل"
            
        if not re.search(r'[0-9]', password):
            return False, "كلمة السر يجب أن تحتوي على رقم واحد على الأقل"
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "كلمة السر يجب أن تحتوي على رمز خاص واحد على الأقل"
            
        return True, ""
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour l'affichage dans l'interface"""
        return {
            'account_number': self.account_number,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'role': self.role,
            'creation_date': self.creation_date.strftime('%Y-%m-%d') if self.creation_date else None
        }







