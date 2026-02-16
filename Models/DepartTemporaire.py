# models/DepartTemporaires.py
from sqlalchemy import Column, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship
from Models.Depart import Depart

class DepartTemporaire(Depart):
    __tablename__ = 'departs_temporaires'
    __table_args__ = {'extend_existing': True}

    iddeparttemporaire = Column(Integer, ForeignKey('departs.iddepart'), primary_key=True)
    Datedebut = Column(Date, nullable=False)
    Datefin = Column(Date, nullable=False)

    idemploye = Column(Integer, ForeignKey('employes.idemploye'), nullable=False)
    employe = relationship("Employe", back_populates="departs_temporaires")

    __mapper_args__ = {
        'polymorphic_identity': 'depart_temporaire',
    }

    @classmethod
    def create(cls, session, numero_decision, date_decision, motif, date_debut, date_fin, employe):
        depart_temp = cls(
            Numerodecision=numero_decision,
            Datedecision=date_decision,
            Motif=motif,
            Datedebut=date_debut,
            Datefin=date_fin,
            employe=employe
        )
        session.add(depart_temp)
        session.commit()
        return depart_temp

    def __repr__(self):
        return f"<DepartTemporaire {self.iddeparttemporaire}: {self.Datedebut} → {self.Datefin}>"