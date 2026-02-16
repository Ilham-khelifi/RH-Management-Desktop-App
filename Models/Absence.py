from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from Models import Base

class Absence(Base):
    __tablename__ = "absences"
    __table_args__ = {'extend_existing': True }

    idAbsence = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to Employe
    idemploye = Column(Integer, ForeignKey("employes.idemploye"), nullable=False)

    # Absence fields
    Type = Column(String(50), nullable=False)
    NumeroDecision = Column(String(50), nullable=True)
    DateDecision = Column(Date, nullable=True)
    DateDebut = Column(Date, nullable=False)
    DateFin = Column(Date, nullable=False)
    Raison = Column(String(255), nullable=False)
    Raison2 = Column(String(255), nullable=True)

    # Relationship to Employe
    employe = relationship("Employe", back_populates="absences")
    history_entries = relationship("History", back_populates="absence")

    def __repr__(self):
        return (f"<Absence {self.idAbsence}: {self.Type} | "
                f"{self.DateDebut} to {self.DateFin} | Employe ID: {self.idemploye}>")
