from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from Models import Base

class Formation(Base):
    __tablename__ = "formations"
    __table_args__ = {'extend_existing': True}

    idFormation = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key
    idemploye = Column(Integer, ForeignKey("employes.idemploye"), nullable=False)

    # Fields
    Type = Column(String(100), nullable=False)  # نوع التكوين
    DateDebut = Column(Date, nullable=False)  # تاريخ البدء
    DateFin = Column(Date, nullable=False)  # تاريخ الانتهاء
    Etablissement = Column(String(150), nullable=False)  # مؤسسة التكوين
    Theme = Column(String(255), nullable=True)  # موضوع التكوين (optionnel)

    # Relationship to Employe
    employe = relationship("Employe", back_populates="formations")
    history_entries = relationship("History", back_populates="formation")
    @classmethod
    def create(cls, session, idemploye, Type, DateDebut, DateFin, Duree=None, Etablissement="", Theme=None):
        new_formation = cls(
            idemploye=idemploye,
            Type=Type.strip(),
            DateDebut=DateDebut,
            DateFin=DateFin,
            Etablissement=Etablissement.strip(),
            Theme=Theme.strip() if Theme else None
        )
        session.add(new_formation)
        session.commit()
        return new_formation

    def __repr__(self):
        return f"<Formation {self.idFormation} - {self.Type} - Employé ID: {self.idemploye}>"
