from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from datetime import datetime
from Models.Formation import Formation
from Models.Employe import Employe
from Controllers.BaseController import BaseControllerWithHistory

class FormationController(BaseControllerWithHistory):
    
    def __init__(self, db_session, current_user_account_number=None):
        super().__init__(db_session, current_user_account_number)
        self.session = db_session
    
    def get_all_formations(self, year=None):
        """Get all formations with history logging"""
        try:
            query = self.session.query(Formation)
            if year:
                # Filter by year from DateDebut
                query = query.filter(Formation.DateDebut.between(f"{year}-01-01", f"{year}-12-31"))
            
            formations = query.all()
            
            # Log access
            filter_text = f" للسنة {year}" if year else ""

            
            return formations
        except Exception as e:
            print(f"Error getting formations: {e}")
            
            # Log error
            self.log_history(
                event="فشل عرض إدارة التكوينات",
                details=f"فشل في الوصول إلى قائمة إدارة التكوينات - الخطأ: {str(e)}",
                gestion="إدارة التكوينات"
                

            )
            return []
    
    def get_formation_by_id(self, formation_id):
        """Get formation by ID with history logging"""
        try:
            formation = self.session.query(Formation).filter(Formation.idFormation == formation_id).first()
            

            return formation
        except Exception as e:
            print(f"Error getting formation by ID: {e}")
            
            # Log error
            self.log_history(
                event="فشل عرض تكوين",
                details=f"فشل في الوصول إلى التكوين رقم {formation_id} - الخطأ: {str(e)}",
                gestion="إدارة التكوينات",
                formation_id=formation_id
            )
            return None
    
    def get_formations_by_employee(self, employee_id, year=None):
        """Get formations by employee with history logging"""
        try:
            query = self.session.query(Formation).filter(Formation.idemploye == employee_id)
            if year:
                # Filter by year from DateDebut
                query = query.filter(Formation.DateDebut.between(f"{year}-01-01", f"{year}-12-31"))
            
            formations = query.all()
            
            # Get employee name for logging
            employee = self.session.query(Employe).filter(Employe.idemploye == employee_id).first()
            employee_name = f"{employee.Prenom} {employee.Nom}" if employee else f"رقم {employee_id}"
            
            # Log access
            filter_text = f" للسنة {year}" if year else ""

            
            return formations
        except Exception as e:
            print(f"Error getting formations by employee: {e}")

            return []
    
    def search_employees_by_first_name(self, first_name):
        """Search for employees by first name with history logging"""
        try:
            if not first_name or len(first_name) < 2:
                return []
                
            search_term = f"%{first_name}%"
            employees = self.session.query(Employe).filter(
                Employe.Prenom.like(search_term)
            ).all()
            
            # Log search
            self.log_history(
                event="البحث عن موظفين بالاسم",
                details=f"تم البحث عن الموظفين بالاسم: {first_name} - النتائج: {len(employees)} موظف",
                gestion="إدارة التكوينات",
            )
            
            return employees
        except Exception as e:
            print(f"Error searching employees: {e}")
            
            # Log error
            self.log_history(
                event="فشل البحث عن موظفين",
                details=f"فشل في البحث عن الموظفين بالاسم: {first_name} - الخطأ: {str(e)}",
                gestion="إدارة التكوينات"
            )
            return []
    
    def get_employee_by_name(self, first_name, last_name):
        """Get employee by first name and last name with history logging"""
        try:
            if not first_name or not last_name:
                return None
                
            employee = self.session.query(Employe).filter(
                Employe.Prenom == first_name.strip(),
                Employe.Nom == last_name.strip()
            ).first()
            
            if employee:
                # Log successful search
                self.log_history(
                    event="البحث عن موظف بالاسم الكامل",
                    details=f"تم العثور على الموظف: {first_name} {last_name} - رقم الموظف: {employee.idemploye}",
                    gestion="إدارة التكوينات",
                    employee_id=employee.idemploye
                )
            else:
                # Log failed search
                self.log_history(
                    event="البحث عن موظف بالاسم الكامل",
                    details=f"لم يتم العثور على الموظف: {first_name} {last_name}",
                    gestion="إدارة التكوينات"
                )
            
            return employee
        except Exception as e:
            print(f"Error getting employee by name: {e}")
            
            # Log error
            self.log_history(
                event="فشل البحث عن موظف",
                details=f"فشل في البحث عن الموظف: {first_name} {last_name} - الخطأ: {str(e)}",
                gestion="إدارة التكوينات"
            )
            return None
    
    def create_formation(self, first_name, last_name, type_formation, date_debut, date_fin, etablissement, theme=None):
        """Create formation with comprehensive history logging"""
        try:
            # Find employee by name
            employee = self.get_employee_by_name(first_name, last_name)

            if not employee:
                # Log failed creation
                self.log_history(
                    event="فشل إضافة تكوين",
                    details=f"فشل في إضافة تكوين - لم يتم العثور على الموظف: {first_name} {last_name}",
                    gestion="إدارة التكوينات"
                )
                raise ValueError("لم يتم العثور على الموظف بهذا الاسم")

            if date_debut > date_fin:

                raise ValueError("تاريخ البدء يجب أن يكون قبل تاريخ الإنتهاء")

            new_formation = Formation.create(
                self.session,
                idemploye=employee.idemploye,
                Type=type_formation,
                DateDebut=date_debut,
                DateFin=date_fin,
                Etablissement=etablissement,
                Theme=theme
            )

            # Calculate duration
            duration = (date_fin - date_debut).days + 1

            # Log successful creation
            self.log_history(
                event="إضافة تكوين جديد",
                details=f"تم إضافة تكوين للموظف: {first_name} {last_name} - النوع: {type_formation} - المؤسسة: {etablissement} - المدة: {duration} يوم - الموضوع: {theme or 'غير محدد'}",
                gestion="إدارة التكوينات",
                employee_id=employee.idemploye,
                formation_id=new_formation.idFormation
            )

            return new_formation

        except SQLAlchemyError as e:
            self.session.rollback()
            
            # Log database error
            self.log_history(
                event="فشل إضافة تكوين",
                details=f"فشل في إضافة تكوين للموظف: {first_name} {last_name} - خطأ في قاعدة البيانات: {str(e)}",
                gestion="إدارة التكوينات",
                employee_id=employee.idemploye if 'employee' in locals() else None
            )
            raise e
        except Exception as e:
            # Log general error
            self.log_history(
                event="فشل إضافة تكوين",
                details=f"فشل في إضافة تكوين للموظف: {first_name} {last_name} - خطأ عام: {str(e)}",
                gestion="إدارة التكوينات",
                employee_id=employee.idemploye if 'employee' in locals() else None
            )
            raise e

    def update_formation(self, formation_id, first_name=None, last_name=None, type_formation=None, 
                        date_debut=None, date_fin=None, etablissement=None, theme=None):
        """Update formation with comprehensive history logging"""
        try:
            formation = self.session.query(Formation).filter(Formation.idFormation == formation_id).first()
            if not formation:

                raise ValueError(f"لم يتم العثور على التكوين برقم {formation_id}")
            
            # Store old values for history
            old_employee = formation.employe
            old_employee_name = f"{old_employee.Prenom} {old_employee.Nom}" if old_employee else "غير محدد"
            old_type = formation.Type
            old_etablissement = formation.Etablissement
            old_theme = formation.Theme
            old_date_debut = formation.DateDebut
            old_date_fin = formation.DateFin
            
            changes = []
            
            # Update employee if provided
            if first_name is not None and last_name is not None:
                employee = self.get_employee_by_name(first_name, last_name)
                if not employee:

                    raise ValueError("لم يتم العثور على الموظف بهذا الاسم")
                if formation.idemploye != employee.idemploye:
                    changes.append(f"الموظف: {old_employee_name} ← {first_name} {last_name}")
                formation.idemploye = employee.idemploye
            
            # Update other fields
            if type_formation is not None and formation.Type != type_formation:
                changes.append(f"النوع: {old_type} ← {type_formation}")
                formation.Type = type_formation
            
            if etablissement is not None and formation.Etablissement != etablissement:
                changes.append(f"المؤسسة: {old_etablissement} ← {etablissement}")
                formation.Etablissement = etablissement
            
            if theme is not None and formation.Theme != theme:
                changes.append(f"الموضوع: {old_theme or 'غير محدد'} ← {theme or 'غير محدد'}")
                formation.Theme = theme
            
            if date_debut is not None:
                if formation.DateDebut != date_debut:
                    changes.append(f"تاريخ البدء: {old_date_debut.strftime('%Y-%m-%d')} ← {date_debut.strftime('%Y-%m-%d')}")
                formation.DateDebut = date_debut
                formation.Annee = date_debut.year
            
            if date_fin is not None:
                if formation.DateFin != date_fin:
                    changes.append(f"تاريخ الانتهاء: {old_date_fin.strftime('%Y-%m-%d')} ← {date_fin.strftime('%Y-%m-%d')}")
                formation.DateFin = date_fin
            
            # Validate dates
            if formation.DateDebut > formation.DateFin:
     
                raise ValueError("تاريخ البدء يجب أن يكون قبل تاريخ الإنتهاء")
            
            self.session.commit()
            
            # Log successful update
            if changes:
                self.log_history(
                    event="تحديث تكوين",
                    details=f"تم تحديث التكوين رقم {formation_id} - التغييرات: {' | '.join(changes)}",
                    gestion="إدارة التكوينات",
                    formation_id=formation_id,
                    employee_id=formation.idemploye
                )
            else:
                self.log_history(
                    event="محاولة تحديث تكوين",
                    details=f"تم محاولة تحديث التكوين رقم {formation_id} - لا توجد تغييرات",
                    gestion="إدارة التكوينات",
                    formation_id=formation_id,
                    employee_id=formation.idemploye
                )
            
            return formation
            
        except SQLAlchemyError as e:
            self.session.rollback()
            
            # Log database error
            self.log_history(
                event="فشل تحديث تكوين",
                details=f"فشل في تحديث التكوين رقم {formation_id} - خطأ في قاعدة البيانات: {str(e)}",
                gestion="إدارة التكوينات",
                formation_id=formation_id
            )
            raise e
        except Exception as e:
            # Log general error
            self.log_history(
                event="فشل تحديث تكوين",
                details=f"فشل في تحديث التكوين رقم {formation_id} - خطأ عام: {str(e)}",
                gestion="إدارة التكوينات",
                formation_id=formation_id
            )
            raise e
    
    def delete_formation(self, formation_id):
        """Delete formation with comprehensive history logging"""
        try:
            formation = self.session.query(Formation).filter(Formation.idFormation == formation_id).first()
            if not formation:
                # Log failed deletion
                self.log_history(
                    event="فشل حذف تكوين",
                    details=f"محاولة حذف تكوين غير موجود - رقم التكوين: {formation_id}",
                    gestion="إدارة التكوينات",
                    formation_id=formation_id
                )
                raise ValueError(f"لم يتم العثور على التكوين برقم {formation_id}")
            
            # Store info for history before deletion
            employee_name = f"{formation.employe.Prenom} {formation.employe.Nom}" if formation.employe else "غير محدد"
            formation_type = formation.Type
            formation_etablissement = formation.Etablissement
            formation_duration = (formation.DateFin - formation.DateDebut).days + 1
            employee_id = formation.idemploye
            
            # Delete the training record
            self.session.delete(formation)
            self.session.commit()
            
            # Log successful deletion
            self.log_history(
                event="حذف تكوين",
                details=f"تم حذف التكوين رقم {formation_id} للموظف: {employee_name} - النوع: {formation_type} - المؤسسة: {formation_etablissement} - المدة: {formation_duration} يوم",
                gestion="إدارة التكوينات",
                formation_id=formation_id,
                employee_id=employee_id
            )
            
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            
            # Log database error
            self.log_history(
                event="فشل حذف تكوين",
                details=f"فشل في حذف التكوين رقم {formation_id} - خطأ في قاعدة البيانات: {str(e)}",

                gestion="إدارة التكوينات",
                
                formation_id=formation_id
            )
            raise e
        except Exception as e:
            # Log general error
            self.log_history(
                event="فشل حذف تكوين",
                details=f"فشل في حذف التكوين رقم {formation_id} - خطأ عام: {str(e)}",
                gestion="إدارة التكوينات",
                formation_id=formation_id
            )
            raise e
    
    def calculate_duration(self, date_debut, date_fin):
        """Calculate duration with validation and history logging"""
        try:
            if date_debut > date_fin:

                return 0
            duration = (date_fin - date_debut).days + 1

            
            return duration
        except Exception as e:
            # Log error
            self.log_history(
                event="فشل حساب مدة التكوين",
                details=f"فشل في حساب مدة التكوين - الخطأ: {str(e)}",
                gestion="إدارة التكوينات"
            )
            return 0
    
    def get_all_employees(self):
        """Get all employees for autocomplete with history logging"""
        try:
            employees = self.session.query(Employe).all()

            
            return employees
        except Exception as e:
            print(f"Error getting all employees: {e}")
            
            # Log error
            self.log_history(
                event="فشل عرض الموظفين للتكوين",
                details=f"فشل في الوصول إلى قائمة الموظفين لأغراض التكوين - الخطأ: {str(e)}",
                gestion="إدارة التكوينات"
            )
            return []