from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from Models import Base

class Tranche(Base):
    __tablename__ = "tranches"
    __table_args__ = {'extend_existing': True}

    idTranche = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key vers la table Conge
    idConge = Column(Integer, ForeignKey("conges.idConge"), nullable=False)

    # Champs de la tranche
    NumeroDecision = Column(Integer, nullable=False)
    DateDecision = Column(Date, nullable=False)
    DateDebut = Column(Date, nullable=False)
    DateFin = Column(Date, nullable=False)

    # Relation inverse vers Conge
    conge = relationship("Conge", back_populates="tranches")
    history_entries = relationship("History", back_populates="tranche")
    def __repr__(self):
        return f"<Tranche {self.idTranche}: Décision {self.NumeroDecision}>"