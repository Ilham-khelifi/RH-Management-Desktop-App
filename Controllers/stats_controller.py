from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from Models.Employe import Employe


def repartition_par_sexe(session: Session):
    resultats = session.query(Employe.Sexe, func.count()).group_by(Employe.Sexe).all()
    total = sum([r[1] for r in resultats])
    return {
        sexe if sexe else "Non spécifié": round((count / total) * 100, 2)
        for sexe, count in resultats
    }
    
def repartition_par_wilaya(session: Session):
    resultats = session.query(Employe.Lieudenaissance, func.count()).group_by(Employe.Lieudenaissance).all()
    return {
        wilaya if wilaya else "Non spécifiée": count
        for wilaya, count in resultats
    }

def repartition_par_age(session: Session):
    today = date.today()
    tranches = {
        "< 25": 0,
        "25-34": 0,
        "35-44": 0,
        "45-54": 0,
        "55+": 0,
    }
    employes = session.query(Employe.Datedenaissance).filter(Employe.Datedenaissance != None).all()

    for (birthdate,) in employes:
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        if age < 25:
            tranches["< 25"] += 1
        elif age < 35:
            tranches["25-34"] += 1
        elif age < 45:
            tranches["35-44"] += 1
        elif age < 55:
            tranches["45-54"] += 1
        else:
            tranches["55+"] += 1

    return tranches


def repartition_par_statut(session: Session):
    resultats = session.query(Employe.Statut, func.count()).group_by(Employe.Statut).all()
    total = sum([r[1] for r in resultats])
    return {
        "Activé" if statut else "Désactivé": round((count / total) * 100, 2)
        for statut, count in resultats
    }
    
    
def repartition_par_statut_familial(session: Session):
    resultats = session.query(Employe.Statutfamilial, func.count()).group_by(Employe.Statutfamilial).all()
    return {
        statut if statut else "Non spécifié": count
        for statut, count in resultats
    }