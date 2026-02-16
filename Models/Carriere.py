from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from Models import Base


class Carriere(Base):
    __tablename__ = "carrieres"

    # Primary & Foreign Key
    idcarriere = Column(Integer, primary_key=True, index=True , autoincrement=True , nullable=False)
    idemploye = Column(Integer, ForeignKey("employes.idemploye"), nullable=False)

    # Diplomas
    Dipinitial = Column(String(100))  # الشهادة التي تم التوظيف الأصلي على أساسها
    Dipactuel = Column(String(100))   # الشهادة الحالية
    DipAutres = Column(Text)          # شهادات ومؤهلات أخرى

    # Structure
    Lb = Column(String(100))          # القانون الأساسي
    cat = Column(String(100))         # الشعبة
    silk = Column(String(100))        # الأسلاك

    # Job Position
    Nomposte = Column(String(100))    # الرتبة أو منصب الشغل الحالي
    NumD = Column(Integer)            # رقم المقرر أو العقد
    DateD = Column(Date)              # تاريخ المقرر أو العقد

    # Visa and Appointment
    visaNUM = Column(Integer)         # رقم التأشيرة
    visaDate = Column(Date)           # تاريخ التأشيرة
    effectiveDate = Column(Date)      # تاريخ المفعول
    pvNUM = Column(Integer)           # رقم محضر التنصيب
    PvDate = Column(Date)             # تاريخ محضر التنصيب
    pvEffetDate = Column(Date)        # تاريخ مفعول التنصيب

    # Position Status
    position = Column(String(100))    # الوضعية
    FRPoste = Column(String(100))     # Grade ou poste initial
    FRDatePoste = Column(Date)        # Date du grade ou poste initial

    # Employment Status
    activite = Column(String(50))     # مفعل / غير مفعل
    actR = Column(String(100))        # سبب تغير حالة التفعيل
    actNUM = Column(Integer)          # رقم القرار
    actDate = Column(Date)            # تاريخ القرار

    # Classification
    current_class = Column(String(50))               # الصنف الحالي
    current_reference_number = Column(String(50))    # الرقم الاستدلالي الحالي

    # Original Recruitment
    GRec = Column(String(100))       # رتبة التوظيف الأصلي
    RecI = Column(String(100))       # التوظيف الأصلي
    RecNUM = Column(Integer)         # رقم المقرر
    RecDate = Column(Date)           # تاريخ المقرر
    RecVisaNUM = Column(Integer)     # رقم التأشيرة
    RecVisaDate = Column(Date)       # تاريخ التأشيرة
    RecEffetDate = Column(Date)      # تاريخ المفعول
    RecPvNUM = Column(Integer)       # رقم محضر التنصيب
    RecPVDate = Column(Date)         # تاريخ محضر التنصيب
    RecPVEffetDate = Column(Date)    # تاريخ مفعول التنصيب

    # Current Grade
    FRGrade = Column(String(100))    # Grade ou poste actuel
    FRGradeDate = Column(Date)       # Date du grade ou poste actuel

    # Affiliation
    dependency = Column(String(100))  # التبعية
    service = Column(String(100))     # المصلحة

    # Current High Position
    posType = Column(String(50))         # الوظيفة أو المنصب العالي
    posNomPoste = Column(String(100))    # اسم الوظيفة
    posNomSup = Column(String(100))      # اسم المنصب العالي
    br = Column(String(100))             # الفرع
    posNUM = Column(Integer)             # رقم المقرر
    posDate = Column(Date)               # تاريخ المقرر
    posVisaNUM = Column(Integer)         # رقم التأشيرة
    posVisaDate = Column(Date)           # تاريخ التأشيرة
    posEffetDate = Column(Date)          # تاريخ المفعول

    # Special Status
    spe = Column(String(100))     # الوضعية الخاصة
    plusInfo = Column(Text)       # معلومات إضافية

    # Relationship
    employe = relationship("Employe", back_populates="carrieres")

    def __repr__(self):
        return f"<Carriere {self.idcarriere} - Poste: {self.Nomposte}>"
