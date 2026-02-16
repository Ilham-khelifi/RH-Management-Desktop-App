from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Models import Base

class Evaluation(Base):
    __tablename__ = "evaluations"
    __table_args__ = {'extend_existing': True}

    idEvaluation = Column(Integer, primary_key=True, autoincrement=True)

    #foreign key
    idemploye = Column(Integer, ForeignKey("employes.idemploye"), nullable=False)

    # Notes
    Annee = Column(String(10), nullable=False)
    NoteAnnuelle = Column(String(10) , nullable=False)
    Note1 = Column(String(10))
    Note2 = Column(String(10))
    Note3 = Column(String(10))
    Note4 = Column(String(10))

    # Relationship to Employe
    employe = relationship("Employe", back_populates="evaluations")
    history_entries = relationship("History", back_populates="evaluation")

    @classmethod
    def create(cls, session, idemploye, Annee, NoteAnnuelle, Note1=None, Note2=None, Note3=None, Note4=None):
        new_evaluation = cls(
            idemploye=idemploye,
            Annee=Annee.strip(),
            NoteAnnuelle=NoteAnnuelle.strip(),
            Note1=Note1.strip() if Note1 else None,
            Note2=Note2.strip() if Note2 else None,
            Note3=Note3.strip() if Note3 else None,
            Note4=Note4.strip() if Note4 else None,
        )
        session.add(new_evaluation)
        session.commit()
        return new_evaluation


    def __repr__(self):
        return f"<Evaluation {self.idEvaluation}: {self.Annee}, Employe ID: {self.idemploye}>"
