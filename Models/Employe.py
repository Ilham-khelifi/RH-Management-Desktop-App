# models/employe.py

from sqlalchemy import BigInteger, Column, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship
from Models import Base

class Employe(Base):
    __tablename__ = "employes"
    __table_args__ = {'extend_existing': True}

    idemploye = Column(Integer, primary_key=True, autoincrement=True, nullable=False)  # Identifiant unique

    # Basic Personal Info
    Nom = Column(String(100), nullable=False)          # اللقب
    Prenom = Column(String(100), nullable=False)       # الاسم
    NomEpoux = Column(String(100))                     # لقب الزوج (للمتزوجات)
    Datedenaissance = Column(Date, nullable=False)     # تاريخ الميلاد
    Lieudenaissance = Column(String(100))              # ولاية الميلاد
    Sexe = Column(String(10))                          # الجنس
    Statut = Column(Boolean, default=True)             # التفعيل

    # Identifiers
    social_security_num = Column(Integer)              # رقم الضمان الاجتماعي
    national_id = Column(BigInteger)                      # رقم التعريف الوطني

    # Type for polymorphism
    type = Column(String(50))                          # طبيعة علاقة العمل (contractuel / permanent...)

    # Contact Info
    Adresseactuelle = Column(String(255))              # العنوان الحالي
    code_postal = Column(Integer)                      # الرمز البريدي
    phone_numbers = Column(Integer)                    # أرقام الهاتف
    email = Column(String(100))                        # البريد الإلكتروني

    # Family Info
    Nomdupere = Column(String(100))                    # اسم الأب
    Nomdelamere = Column(String(100))                  # لقب واسم الأم
    Statutfamilial = Column(String(50))                # الوضعية العائلية
    Nombredenfants = Column(Integer)                   # عدد الأولاد
    Servicesnationale = Column(String(100))            # الوضعية تجاه الخدمة الوطنية

    # French fields (duplicate in French for some systems)
    NomFR = Column(String(100))                        # Nom de famille en français
    PrenomFR = Column(String(100))                     # Prénom en français
    NomEpouxFR = Column(String(100))                   # Nom de l’époux(se) en français
    WilayenaissanceFR = Column(String(100))            # Wilaya de naissance en français


    # Other Info for the type
    Cchiff = Column(String(50))              # رقم المقرر
    Cdate_chiff = Column(Date)               # تاريخ المقرر
    Cdate_effet = Column(Date)               # تاريخ المفعول
    # Relationships
    carrieres = relationship("Carriere", back_populates="employe", cascade="all, delete-orphan", uselist=False)
    evaluations = relationship("Evaluation", back_populates="employe", cascade="all, delete-orphan", uselist=False)
    absences = relationship("Absence", back_populates="employe", cascade="all, delete-orphan", uselist=False)
    formations = relationship("Formation",back_populates="employe",cascade="all , delete-orphan", uselist=False)
    conges = relationship("Conge", back_populates="employe", cascade="all, delete-orphan", uselist=False)
    
    
    departs_temporaires = relationship("DepartTemporaire", back_populates="employe", cascade="all, delete-orphan")
    depart_definitif = relationship("DepartDefinitif", back_populates="employe", uselist=False, cascade="all, delete-orphan")
    history_entries = relationship("History", back_populates="employee")

    __mapper_args__ = {
        'polymorphic_identity': 'employe',
        'polymorphic_on': type,
        'with_polymorphic': '*',
    }



    def __repr__(self):
        return f"<Employe {self.idemploye}: {self.Nom} {self.Prenom}>"