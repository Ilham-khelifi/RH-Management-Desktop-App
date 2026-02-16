import datetime
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy import and_, extract, func, case
from Controllers.EmployeController import EmployeeController
from Models import Employe
from Models.Absence import Absence
from Controllers.BaseController import BaseControllerWithHistory

class AbsenceController(BaseControllerWithHistory):
    def __init__(self, db_session, current_user_account_number=None):
        super().__init__(db_session, current_user_account_number)
        self.session = db_session
    def save_absence_for_employee(self, Type, DateDebut, DateFin, Raison,
                              NumeroDecision=None, DateDecision=None, Raison2=None,
                              idemploye=None, name=None, lastname=None):

        employe_controller = EmployeeController(self.session, self.current_user_account_number)

    # Get employee name for logging
        employee = self.session.query(Employe).filter(Employe.idemploye == idemploye).first()
        employee_name = f"{employee.Prenom} {employee.Nom}" if employee else f"رقم {idemploye}"

    # Clean input data
        Type = Type.strip() if Type else ''
        Raison = Raison.strip() if Raison else ''
        NumeroDecision = NumeroDecision.strip() if NumeroDecision else None
        Raison2 = Raison2.strip() if Raison2 else None

    # Check for overlapping absences
        overlapping_absence = self.session.query(Absence).filter(
          Absence.idemploye == idemploye,
          and_(Absence.DateDebut <= DateFin, Absence.DateFin >= DateDebut)
        ).first()

    # Calculate absence duration
        duration = (DateFin - DateDebut).days + 1

    # Create absence record
        absence = Absence(
           idemploye=idemploye,
           Type=Type,
           NumeroDecision=NumeroDecision,
           DateDecision=DateDecision,
           DateDebut=DateDebut,
           DateFin=DateFin,
           Raison=Raison,
           Raison2=Raison2
       )

        self.session.add(absence)
        self.session.commit()

    # Log successful creation
        decision_info = f" - قرار رقم: {NumeroDecision}" if NumeroDecision else ""
        decision_date_info = f" - تاريخ القرار: {DateDecision.strftime('%Y-%m-%d')}" if DateDecision else ""
        reason2_info = f" - السبب الثاني: {Raison2}" if Raison2 else ""
    
        self.log_history(
           event="إضافة غياب جديد",
           details=f"تم إضافة غياب للموظف: {employee_name} - النوع: {Type} - من {DateDebut.strftime('%Y-%m-%d')} إلى {DateFin.strftime('%Y-%m-%d')} - المدة: {duration} يوم - السبب: {Raison}{decision_info}{decision_date_info}{reason2_info}",
           gestion="إدارة الغيابات",
           employee_id=idemploye,
           absence_id=absence.idAbsence
      )

        return "success"

    def load_absences_with_employee_names(self):
        """Load all absences with employee names and history logging"""
        try:
            results = (
                self.session.query(
                    Absence.idAbsence.label("idAbsence"),
                    Absence.Type.label("Type"),
                    Absence.NumeroDecision.label("NumeroDecision"),
                    Absence.DateDecision.label("DateDecision"),
                    Absence.DateDebut.label("DateDebut"),
                    Absence.DateFin.label("DateFin"),
                    Absence.Raison.label("Raison"),
                    Absence.Raison2.label("Raison2"),
                    Employe.idemploye.label("idemploye"),
                    Employe.Nom.label("nom"),
                    Employe.Prenom.label("prenom"),
                )
                .join(Employe, Absence.idemploye == Employe.idemploye)
                .all()
            )

            table_data = []
            for row in results:
                table_data.append({
                    "idAbsence": row.idAbsence,
                    "Type": row.Type,
                    "NumeroDecision": row.NumeroDecision,
                    "DateDecision": row.DateDecision,
                    "DateDebut": row.DateDebut,
                    "DateFin": row.DateFin,
                    "Raison": row.Raison,
                    "Raison2": row.Raison2,
                    "idemploye": row.idemploye,
                    "nom": row.nom,
                    "prenom": row.prenom,
                })


            return table_data

        except Exception as e:
            print(f"Error loading absences: {e}")
            return []

    def update_absence(self, absence_id, Type, DateDebut, DateFin, Raison,
                       NumeroDecision=None, DateDecision=None, Raison2=None):
        """Update absence with comprehensive history logging"""
        try:
            absence = self.session.query(Absence).filter_by(idAbsence=absence_id).first()

 

            # Get employee name for logging
            employee = self.session.query(Employe).filter(Employe.idemploye == absence.idemploye).first()
            employee_name = f"{employee.Prenom} {employee.Nom}" if employee else f"رقم {absence.idemploye}"

            # Store old values for history
            old_type = absence.Type
            old_start = absence.DateDebut
            old_end = absence.DateFin
            old_reason = absence.Raison
            old_decision = absence.NumeroDecision
            old_decision_date = absence.DateDecision
            old_reason2 = absence.Raison2
            old_duration = (old_end - old_start).days + 1

            # Check overlapping absences for this employee, excluding current record
            overlapping_absence = self.session.query(Absence).filter(
                Absence.idemploye == absence.idemploye,
                Absence.idAbsence != absence_id,
                Absence.DateDebut <= DateFin,
                Absence.DateFin >= DateDebut
            ).first()



            # Track changes
            changes = []
            new_duration = (DateFin - DateDebut).days + 1

            if old_type != Type.strip():
                changes.append(f"النوع: {old_type} ← {Type.strip()}")
            if old_start != DateDebut:
                changes.append(f"تاريخ البدء: {old_start.strftime('%Y-%m-%d')} ← {DateDebut.strftime('%Y-%m-%d')}")
            if old_end != DateFin:
                changes.append(f"تاريخ الانتهاء: {old_end.strftime('%Y-%m-%d')} ← {DateFin.strftime('%Y-%m-%d')}")
            if old_duration != new_duration:
                changes.append(f"المدة: {old_duration} يوم ← {new_duration} يوم")
            if old_reason != Raison.strip():
                changes.append(f"السبب: {old_reason} ← {Raison.strip()}")
            if old_decision != (NumeroDecision.strip() if NumeroDecision else None):
                old_dec = old_decision or "غير محدد"
                new_dec = NumeroDecision.strip() if NumeroDecision else "غير محدد"
                changes.append(f"رقم القرار: {old_dec} ← {new_dec}")
            if old_decision_date != DateDecision:
                old_date = old_decision_date.strftime('%Y-%m-%d') if old_decision_date else "غير محدد"
                new_date = DateDecision.strftime('%Y-%m-%d') if DateDecision else "غير محدد"
                changes.append(f"تاريخ القرار: {old_date} ← {new_date}")
            if old_reason2 != (Raison2.strip() if Raison2 else None):
                old_r2 = old_reason2 or "غير محدد"
                new_r2 = Raison2.strip() if Raison2 else "غير محدد"
                changes.append(f"السبب الثاني: {old_r2} ← {new_r2}")

            # Update absence data
            absence.Type = Type.strip() if Type else None
            absence.NumeroDecision = NumeroDecision.strip() if NumeroDecision else None
            absence.DateDecision = DateDecision
            absence.DateDebut = DateDebut
            absence.DateFin = DateFin
            absence.Raison = Raison.strip() if Raison else None
            absence.Raison2 = Raison2.strip() if Raison2 else None

            self.session.commit()

            # Log successful update
            if changes:
                self.log_history(
                    event="تحديث غياب",
                    details=f"تم تحديث الغياب رقم {absence_id} للموظف: {employee_name} - التغييرات: {' | '.join(changes)}",
                    gestion="إدارة الغيابات",
                    absence_id=absence_id,
                    employee_id=absence.idemploye
                )


            return "success"

        except Exception as e:
            self.session.rollback()
            return "db_error"

    def delete_absence(self, absence_id):
        """Delete absence with comprehensive history logging"""
        try:
            absence = self.session.query(Absence).filter_by(idAbsence=absence_id).first()
            


            # Get employee name and absence details for logging
            employee = self.session.query(Employe).filter(Employe.idemploye == absence.idemploye).first()
            employee_name = f"{employee.Prenom} {employee.Nom}" if employee else f"رقم {absence.idemploye}"
            absence_type = absence.Type
            start_date = absence.DateDebut.strftime('%Y-%m-%d')
            end_date = absence.DateFin.strftime('%Y-%m-%d')
            duration = (absence.DateFin - absence.DateDebut).days + 1
            reason = absence.Raison
            employee_id = absence.idemploye

            # Delete the absence
            self.session.delete(absence)
            self.session.commit()

            # Log successful deletion
            self.log_history(
                event="حذف غياب",
                details=f"تم حذف الغياب رقم {absence_id} للموظف: {employee_name} - النوع: {absence_type} - من {start_date} إلى {end_date} - المدة: {duration} يوم - السبب: {reason}",
                gestion="إدارة الغيابات",
                absence_id=absence_id,
                employee_id=employee_id
            )

            return True

        except Exception as e:
            self.session.rollback()

            raise e

    def load_table(self):
        """Load monthly absence statistics with history logging"""
        try:
            today = datetime.date.today()
            current_year = today.year
            current_month = today.month

            results = (
                self.session.query(
                    Employe.idemploye.label("idemploye"),
                    Employe.Nom.label("nom"),
                    Employe.Prenom.label("prenom"),
                    func.count(Absence.idAbsence).label("total"),
                    func.sum(case((Absence.Type == "مبرر", 1), else_=0)).label("justifiees"),
                    func.sum(case((Absence.Type == "غير مبرر", 1), else_=0)).label("non_justifiees"),
                    func.sum(case((Absence.Type == "إجازة مرضية", 1), else_=0)).label("maladies")
                )
                .join(Absence, Employe.idemploye == Absence.idemploye)
                .filter(
                    extract('year', Absence.DateDebut) == current_year,
                    extract('month', Absence.DateDebut) == current_month
                )
                .group_by(Employe.idemploye, Employe.Nom, Employe.Prenom)
                .order_by(Employe.Nom, Employe.Prenom)
                .all()
            )

            table_data = []
            for row in results:
                table_data.append({
                    "annee": current_year,
                    "mois": current_month,
                    "idemploye": row.idemploye,
                    "nom": row.nom,
                    "prenom": row.prenom,
                    "justifiees": row.justifiees or 0,
                    "non_justifiees": row.non_justifiees or 0,
                    "maladies": row.maladies or 0,
                    "total": row.total or 0,
                })

            # Log statistics access
            month_names = {
                1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
                7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
            }
            month_name = month_names.get(current_month, str(current_month))


            return table_data

        except Exception as e:
            print(f"Error loading absence statistics: {e}")

            return []