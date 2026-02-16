from Models.Employe import Employe
from Models.Carriere import Carriere
from Models.Permanent import Permanent
from Models.Contractuel import Contractuel
from sqlalchemy import or_, and_
from Models.DepartDefinitif import DepartDefinitif 
from Controllers.BaseController import BaseControllerWithHistory

class EmployeeController(BaseControllerWithHistory):
    def __init__(self, session, current_user_account_number=None):
        super().__init__(session, current_user_account_number)

    def get_employees_with_career(self):
        """Get all employees with their career information"""
        return self.session.query(Employe, Carriere).join(Carriere).all()

    def get_employee_by_id(self, employee_id):
        """Get an employee by ID"""
        return self.session.query(Employe).filter(Employe.idemploye == employee_id).first()

    def get_career_by_employee_id(self, employee_id):
        """Get career information for an employee"""
        return self.session.query(Carriere).filter(Carriere.idemploye == employee_id).first()

    def save_employee(self, employee, career):
        """Save an employee and their career information with history logging"""
        try:
            # Add employee to session
            self.session.add(employee)
            self.session.flush()  # Flush to get the employee ID
            
            # Set the employee ID for the career
            career.idemploye = employee.idemploye
            
            # Add career to session
            self.session.add(career)
            
            # Commit the transaction
            self.session.commit()
            
            # Log history
            self.log_history(
                event="إضافة موظف جديد",
                details=f"تم إضافة الموظف: {employee.Prenom} {employee.Nom} - رقم الموظف: {employee.idemploye} - النوع: {employee.type}",
                gestion="إدارة الموظفين",
                employee_id=employee.idemploye
            )
            
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error saving employee: {e}")

            raise e

    def update_employee(self, employee_id, employee_data, career_data=None):
        """Update an employee and optionally their career information with history logging"""
        try:
            # Get the employee
            employee = self.get_employee_by_id(employee_id)


            
            # Store old values for history
            old_name = f"{employee.Prenom} {employee.Nom}"
            changes = []
            
            # Update employee attributes
            for key, value in employee_data.items():
                if hasattr(employee, key):
                    old_value = getattr(employee, key)
                    if old_value != value:
                        # Format dates and special fields for better readability
                        if key == 'Datedenaissance' and old_value and value:
                            old_str = old_value.strftime('%Y-%m-%d') if hasattr(old_value, 'strftime') else str(old_value)
                            new_str = value.strftime('%Y-%m-%d') if hasattr(value, 'strftime') else str(value)
                            changes.append(f"تاريخ الميلاد: {old_str} ← {new_str}")
                        elif key == 'Statut':
                            old_status = "مفعل" if old_value else "غير مفعل"
                            new_status = "مفعل" if value else "غير مفعل"
                            changes.append(f"الحالة: {old_status} ← {new_status}")
                        else:
                            changes.append(f"{key}: {old_value} ← {value}")
                    setattr(employee, key, value)
            
            # Update career if provided
            if career_data and employee.carrieres:
                career = employee.carrieres
                for key, value in career_data.items():
                    if hasattr(career, key):
                        old_value = getattr(career, key)
                        if old_value != value:
                            if key == 'effectiveDate' and old_value and value:
                                old_str = old_value.strftime('%Y-%m-%d') if hasattr(old_value, 'strftime') else str(old_value)
                                new_str = value.strftime('%Y-%m-%d') if hasattr(value, 'strftime') else str(value)
                                changes.append(f"تاريخ المفعول: {old_str} ← {new_str}")
                            else:
                                changes.append(f"المهنة - {key}: {old_value} ← {value}")
                        setattr(career, key, value)
            
            # Commit the changes
            self.session.commit()
            
            self.log_history(
                    event="تحديث بيانات موظف",
                    details=f"تم تحديث بيانات الموظف: {old_name} (رقم: {employee_id}) - التغييرات: {' | '.join(changes)}",
                    gestion=" إدارة الموظفين ",
                    employee_id=employee_id
                )

            
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error updating employee: {e}")
            
      
            return False

    def delete_employee(self, employee_id):
        """Delete an employee and their related records with history logging"""
        try:
            employee = self.get_employee_by_id(employee_id)
            if employee:
                employee_name = f"{employee.Prenom} {employee.Nom}"
                employee_type = employee.type
                
                self.session.delete(employee)
                self.session.commit()
                
                # Log history
                self.log_history(
                    event="حذف موظف",
                    details=f"تم حذف الموظف: {employee_name} - رقم الموظف: {employee_id} - النوع: {employee_type}",
                    gestion=" إدارة الموظفين ",
                    employee_id=employee_id
                )
                
                return True

        except Exception as e:
            self.session.rollback()
            print(f"Error deleting employee: {e}")

            return False

    def filter_employees(self, criteria):
        """Filter employees based on criteria with history logging"""
        try:
            query = self.session.query(Employe, Carriere).join(Carriere)
            
            applied_filters = []
            
            # Apply filters based on criteria
            for field, value in criteria.items():
                if not value:  # Skip empty criteria
                    continue
                    
                applied_filters.append(f"{field}: {value}")
                
                # Map field names to model attributes
                if field == "رقم الموظف" and value:
                    query = query.filter(Employe.idemploye == value)
                elif field == "التفعيل":
                    is_active = value == "مفعل"
                    query = query.filter(Employe.Statut == is_active)
                elif field == "الاسم":
                    query = query.filter(Employe.Prenom.like(f"%{value}%"))
                elif field == "اللقب":
                    query = query.filter(Employe.Nom.like(f"%{value}%"))
                elif field == "لقب الزوج ":
                    query = query.filter(Employe.NomEpoux.like(f"%{value}%"))
                elif field == "تاريخ الميلاد":
                    query = query.filter(Employe.Datedenaissance == value)
                elif field == "ولاية الميلاد":
                    query = query.filter(Employe.Lieudenaissance.like(f"%{value}%"))
                elif field == "الجنس":
                    query = query.filter(Employe.Sexe == value)
                elif field == " الوضعية العائلية":
                    query = query.filter(Employe.Statutfamilial == value)
                elif field == " الوضعية تجاه الخدمة الوطنية":
                    query = query.filter(Employe.Servicesnationale == value)
                elif field == "الشهادة التي تم على أساسهاالتوظيف الأصلي":
                    query = query.filter(Carriere.Dipinitial.like(f"%{value}%"))
                elif field == "الشهادة الحالية ":
                    query = query.filter(Carriere.Dipactuel.like(f"%{value}%"))
                elif field == "رتبة التوظيف الأصلي":
                    query = query.filter(Carriere.GRec.like(f"%{value}%"))
                elif field == "الرتبة أو منصب الشغل الحالي ":
                    query = query.filter(Carriere.Nomposte.like(f"%{value}%"))
                elif field == "الصنف الحالي ":
                    query = query.filter(Carriere.current_class.like(f"%{value}%"))
                elif field == "الدرجة الحالية":
                    query = query.filter(
                        or_(
                            and_(Employe.type == "permanent", Permanent.current_degree == value),
                            and_(Employe.type == "contractuel", Contractuel.percentage.like(f"%{value}%"))
                        )
                    )
                elif field == "تاريخ المفعول ":
                    query = query.filter(Carriere.effectiveDate == value)
                elif field == "التبعية":
                    query = query.filter(Carriere.dependency.like(f"%{value}%"))
                elif field == "المصلحة":
                    query = query.filter(Carriere.service.like(f"%{value}%"))
                elif field == "طبيعة علاقة العمل (موظف عون متعاقد)":
                    emp_type = "permanent" if value == "موظف" else "contractuel"
                    query = query.filter(Employe.type == emp_type)
            
            results = query.all()
            
            
            return results
            
        except Exception as e:
            print(f"Error filtering employees: {e}")

            return []

    def get_final_departures(self):
        """Get final departures with history logging"""
        try:
            departures = self.session.query(DepartDefinitif).all()

            
            return departures
        except Exception as e:
            print(f"Error getting final departures: {e}")

            return []
    
    def getidbynameandlastname(self, name, lastname):
        """Get employee ID by name and lastname with history logging"""
        try:
            employee = self.session.query(Employe).filter(
                
                Employe.Prenom == name,
                Employe.Nom == lastname
            ).first()

            if employee:
                print(f"Employé trouvé! ID: {employee.idemploye}")
                return employee.idemploye
            else:

                return None
        except Exception as e:
            print(f"Error searching employee by name: {e}")
            

            return None

    def get_all_employees(self):
        """Get all employees (excluding departed) with history logging"""
        try:
            # Récupérer les identifiants des employés qui ont quitté définitivement
            departed_ids = set(depart.idemploye for depart in self.get_final_departures())

            # Récupérer tous les employés qui ne sont pas partis définitivement
            employees = (
                self.session.query(Employe)
                .filter(Employe.idemploye.notin_(departed_ids))
                .all()
            )


            # Retourner Nom et Prénom
            return [(emp.Prenom, emp.Nom) for emp in employees]
        except Exception as e:
            print("Failed to fetch employees:", e)

            return []

    def get_all_employee_names(self):
        """Returns a list of all unique first names of employees with history logging"""
        try:
            employees = self.session.query(Employe).all()
            names = [emp.Prenom for emp in employees if emp.Prenom]
            

            
            return names
        except Exception as e:
            print("Error fetching employee names:", e)
  
            return []

    def get_all_employee_lastnames(self):
        """Returns a list of all unique last names of employees with history logging"""
        try:
            employees = self.session.query(Employe).all()
            lastnames = [emp.Nom for emp in employees if emp.Nom]

            return lastnames
        except Exception as e:
            print("Error fetching employee last names:", e)

            return []

    def get_employee_map(self):
        """Returns a dictionary that maps first names to last names with history logging"""
        try:
            employees = self.session.query(Employe).all()
            employee_map = {emp.Prenom: emp.Nom for emp in employees if emp.Prenom and emp.Nom}

            return employee_map
        except Exception as e:
            print("Error creating employee name map:", e)

            return {}