from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from Models.Conge import Conge
from Models.Employe import Employe
from Models.Tranche import Tranche
from Models.Depart import Depart
from Controllers.BaseController import BaseControllerWithHistory

class CongeController(BaseControllerWithHistory):
    """
    Controller for managing leave (Conge) records with comprehensive history logging
    """
    
    def __init__(self, db_session, current_user_account_number=None):
        super().__init__(db_session, current_user_account_number)
    
    def get_all_conges(self, year=None):
        """Get all leave records with history logging"""
        try:
            query = self.session.query(Conge)
            if year:
                query = query.filter(Conge.Annee == year)
            
            conges = query.all()
            
            
            return conges
        except Exception as e:
            print(f"Error getting conges: {e}")

            return []
    
    def get_conge_by_id(self, conge_id):
        """Get a specific leave record by ID with history logging"""
        try:
            conge = self.session.query(Conge).filter(Conge.idConge == conge_id).first()

            return conge
        except Exception as e:
            print(f"Error getting conge by ID: {e}")

            return None
    
    def get_conge_by_employee_year(self, employee_id, year):
        """Get a leave record for a specific employee and year with history logging"""
        try:
            conge = self.session.query(Conge).filter(
                Conge.idemploye == employee_id,
                Conge.Annee == year
            ).first()
            
            # Get employee name for logging
            employee = self.session.query(Employe).filter(Employe.idemploye == employee_id).first()
            employee_name = f"{employee.Prenom} {employee.Nom}" if employee else f"رقم {employee_id}"
            

            
            return conge
        except Exception as e:
            print(f"Error getting conge by employee and year: {e}")
 
            return None
    
    
    def get_previous_years_conges(self, current_year):
        """Get leave records from previous years with history logging"""
        try:
            conges = self.session.query(Conge).filter(Conge.Annee < current_year).order_by(Conge.Annee.desc()).all()

            
            return conges
        except Exception as e:
            print(f"Error getting previous years conges: {e}")
 
            return []

    
    def update_allocated_days(self, conge_id, nbr_jours_alloues):
        """Update allocated days with comprehensive history logging"""
        try:
            conge = self.get_conge_by_id(conge_id)
            
            employee_name = f"{conge.employe.Prenom} {conge.employe.Nom}" if conge.employe else "غير محدد"
            old_allocated = conge.NbrJoursAlloues
            

                
            
            # Update allocated days and remaining days
            conge.NbrJoursAlloues = nbr_jours_alloues
            conge.NbrJoursRestants = nbr_jours_alloues - conge.NbrJoursPris
            
            self.session.commit()
            
            # Log successful update
            self.log_history(
                event="تحديث الأيام المخصصة",
                details=f"تم تحديث الأيام المخصصة للموظف: {employee_name} - من {old_allocated} إلى {nbr_jours_alloues} يوم - الأيام المتبقية: {conge.NbrJoursRestants}",
                gestion= "إدارة الإجازات",

                conge_id=conge_id,
                employee_id=conge.idemploye
            )
            
            return conge
            
        except SQLAlchemyError as e:
            self.session.rollback()

            raise e
        except Exception as e:

            raise e


    
    def create_annual_leaves_for_all_employees(self, year, default_days=30):
        """Create annual leave records for all employees with comprehensive history logging"""
        try:
            # Get all employees
            employees = self.session.query(Employe).all()
            created_conges = []
            skipped_employees = []
            
            for employee in employees:
                # Check if leave record already exists for this employee and year
                existing_conge = self.get_conge_by_employee_year(employee.idemploye, year)
                if not existing_conge:
                    # Create new leave record
                    new_conge = Conge.create(
                        self.session,
                        idemploye=employee.idemploye,
                        Annee=year,
                        NbrJoursAlloues=default_days,
                        NbrJoursPris=0,
                        NbrJoursRestants=default_days
                    )
                    created_conges.append(new_conge)
                else:
                    skipped_employees.append(f"{employee.Prenom} {employee.Nom}")
            

            
            return created_conges
            
        except SQLAlchemyError as e:
            self.session.rollback()

            raise e
        except Exception as e:

            raise e
    
    def get_conge_with_tranches(self, conge_id):
        """Get a leave record with its tranches and comprehensive history logging"""
        try:
            conge = self.get_conge_by_id(conge_id)

            
            # Get tranches for this leave
            tranches = self.session.query(Tranche).filter(Tranche.idConge == conge_id).order_by(Tranche.DateDebut).all()
            
            employee_name = f"{conge.employe.Prenom} {conge.employe.Nom}" if conge.employe else "غير محدد"
            
            # Format data for UI
            result = {
                "conge": {
                    "id": conge.idConge,
                    "employee_id": conge.idemploye,
                    "employee_name": employee_name,
                    "year": conge.Annee,
                    "allocated_days": conge.NbrJoursAlloues,
                    "days_taken": conge.NbrJoursPris,
                    "days_remaining": conge.NbrJoursRestants
                },
                "tranches": []
            }
            
            for tranche in tranches:
                result["tranches"].append({
                    "id": tranche.idTranche,
                    "decision_id": tranche.NumeroDecision,
                    "decision_date": tranche.DateDecision.strftime("%Y-%m-%d"),
                    "start_date": tranche.DateDebut.strftime("%Y-%m-%d"),
                    "end_date": tranche.DateFin.strftime("%Y-%m-%d"),
                    "days": (tranche.DateFin - tranche.DateDebut).days + 1
                })
            
        
            
            return result
        except Exception as e:
            print(f"Error getting conge with tranches: {e}")

            raise e
    

