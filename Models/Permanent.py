from sqlalchemy import Column, Integer, ForeignKey, String, Date
from Models.Employe import Employe
from Models import Base

class Permanent(Employe):
    __tablename__ = "permanents"
    __table_args__ = {'extend_existing': True}

    idpermanent = Column(Integer, primary_key=True, autoincrement=True , nullable=False)
    idemploye = Column(Integer, ForeignKey("employes.idemploye"), unique=True , nullable=False)


    # Permanent-specific fields (8 total)
    current_degree = Column(Integer)         # الدرجة الحالية
    NBR_A = Column(Integer)                  # الأقدمية - سنة
    NBR_M = Column(Integer)                  # الأقدمية - شهر
    NBR_J = Column(Integer)                  # الأقدمية - يوم

    __mapper_args__ = {
        'polymorphic_identity': 'permanent',
    }

    def __repr__(self):
        return f"<Permanent {self.idemploye}: {self.Nom} {self.Prenom}>"
