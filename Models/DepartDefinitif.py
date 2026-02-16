# models/DepartDefinitif.py
from sqlalchemy import Column, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship
from Models.Depart import Depart

class DepartDefinitif(Depart):
    __tablename__ = 'departs_definitifs'
    __table_args__ = {'extend_existing': True}

    iddepartdefinitif = Column(Integer, ForeignKey('departs.iddepart'), primary_key=True)
    Datedepartdefinitif = Column(Date, nullable=False)

    idemploye = Column(Integer, ForeignKey('employes.idemploye'), unique=True, nullable=False)
    employe = relationship("Employe", back_populates="depart_definitif")

    __mapper_args__ = {
        'polymorphic_identity': 'depart_definitif',
    }

    @classmethod
    def create(cls, session, numero_decision, date_decision, motif, date_depart_definitif, employe):
        depart_def = cls(
            Numerodecision=numero_decision,
            Datedecision=date_decision,
            Motif=motif,
            Datedepartdefinitif=date_depart_definitif,
            employe=employe
        )
        session.add(depart_def)
        session.commit()
        return depart_def

    def __repr__(self):
        return f"<DepartDefinitif {self.iddepartdefinitif}: {self.Datedepartdefinitif}>"