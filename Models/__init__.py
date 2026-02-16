from sqlalchemy.orm import declarative_base

Base = declarative_base()

from  Models.Employe import Employe

from  Models.Permanent import Permanent

from  .Contractuel import  Contractuel

from Models.Absence import  Absence

from Models.Formation import Formation

from Models.User import User

from Models.Evaluation import Evaluation

from Models.Carriere import Carriere

from Models.Depart import Depart

from Models.DepartDefinitif import DepartDefinitif

from Models.DepartTemporaire import DepartTemporaire

from Models.Conge import Conge

from Models.Tranche import Tranche

from Models.History import History



