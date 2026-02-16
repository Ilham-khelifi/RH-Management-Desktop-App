# models/Depart.py
from sqlalchemy import Column, Integer, Date, String
from Models import Base

class Depart(Base):
    __tablename__ = 'departs'
    __table_args__ = {'extend_existing': True}

    iddepart = Column(Integer, primary_key=True, autoincrement=True)
    Numerodecision = Column(Integer, nullable=False)
    Datedecision = Column(Date, nullable=False)
    Motif = Column(String(255), nullable=False)
    type = Column(String(50))  # polymorphic

    __mapper_args__ = {
        'polymorphic_identity': 'depart',
        'polymorphic_on': type,
        'with_polymorphic': '*',
    }

    @classmethod
    def create(cls, session, numero_decision, date_decision, motif):
        depart = cls(
            Numerodecision=numero_decision,
            Datedecision=date_decision,
            Motif=motif
        )
        session.add(depart)
        session.commit()
        return depart

    def __repr__(self):
        return f"<Depart {self.iddepart}: Décision {self.Numerodecision} - {self.Motif}>"