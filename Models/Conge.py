from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from Models import Base

class Conge(Base):
    __tablename__ = "conges"
    __table_args__ = {'extend_existing': True}

    idConge = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key vers Employe
    idemploye = Column(Integer, ForeignKey("employes.idemploye"), nullable=False)

    # Champs du congé
    Annee = Column(Integer, nullable=False)  # السنة
    NbrJoursAlloues = Column(Integer, nullable=False)  # عدد الأيام المخصصة
    NbrJoursPris = Column(Integer, nullable=False)  # عدد الأيام المستعملة
    NbrJoursRestants = Column(Integer, nullable=False)  # عدد الأيام المتبقية

    # Relation vers Employe
    employe = relationship("Employe", back_populates="conges")
    tranches = relationship("Tranche", back_populates="conge", cascade="all, delete-orphan")
    history_entries = relationship("History", back_populates="conge")
    @classmethod
    def create(cls, session, idemploye, Annee, NbrJoursAlloues, NbrJoursPris, NbrJoursRestants):
        new_conge = cls(
            idemploye=idemploye,
            Annee=Annee,
            NbrJoursAlloues=NbrJoursAlloues,
            NbrJoursPris=NbrJoursPris,
            NbrJoursRestants=NbrJoursRestants
        )
        session.add(new_conge)
        session.commit()
        return new_conge

    def __repr__(self):
        return f"<Conge {self.idConge} | {self.Annee} - Employé ID: {self.idemploye}>"