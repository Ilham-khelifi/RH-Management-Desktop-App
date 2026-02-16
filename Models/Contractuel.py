from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from Models.Employe import Employe
from Models import Base

class Contractuel(Employe):
    __tablename__ = "contractuels"
    __table_args__ = {'extend_existing': True}

    idcontractuel = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    idemploye = Column(Integer, ForeignKey("employes.idemploye"), unique=True , nullable=False)


    # Contractuel-specific fields (5 total)
    percentage = Column(Float)             # النسبة المئوية

    __mapper_args__ = {
        'polymorphic_identity': 'contractuel',
    }

    def __repr__(self):
        return f"<Contractuel {self.idemploye}: {self.Nom} {self.Prenom}>"
