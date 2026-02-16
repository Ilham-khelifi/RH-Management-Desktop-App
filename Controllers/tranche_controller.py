from Controllers.BaseController import BaseControllerWithHistory
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from Models.Tranche import Tranche
from Models.Conge import Conge

class TrancheController(BaseControllerWithHistory):
    """
    Controller for managing leave slices (Tranche) with complete history logging
    Handles operations related to leave slices with journalisation
    """
    def __init__(self, db_session, current_user_account_number=None):
        super().__init__(db_session, current_user_account_number)
        self.session = db_session
    
    def get_tranche_by_id(self, tranche_id):
        """
        Get a specific tranche by ID
        
        Args:
            tranche_id (int): The tranche ID
            
        Returns:
            Tranche: The tranche or None if not found
        """
        return self.session.query(Tranche).filter(Tranche.idTranche == tranche_id).first()
    
    def get_tranches_by_conge(self, conge_id):
        """
        Get all tranches for a specific leave record with logging
        
        Args:
            conge_id (int): The leave ID
            
        Returns:
            list: List of Tranche objects
        """
        try:
            tranches = self.session.query(Tranche).filter(Tranche.idConge == conge_id).order_by(Tranche.DateDebut).all()
            
            # Log the consultation
            conge = self.session.query(Conge).filter(Conge.idConge == conge_id).first()

            
            return tranches
            
        except Exception as e:
            self.log_history(
                event="خطأ في استعلام الشطر",
                details=f"خطأ في استعلام شطر الإجازة {conge_id}: {str(e)}",
                gestion="إدارة الإجازات",
                conge_id=conge_id
            )
            raise e
    
    def create_tranche(self, conge_id, numero_decision, date_decision, date_debut, date_fin):
        """
        Create a new tranche for a leave record with enhanced validation and logging
        
        Args:
            conge_id (int): The leave ID
            numero_decision (int): Decision number
            date_decision (date): Decision date
            date_debut (date): Start date
            date_fin (date): End date
            
        Returns:
            dict: Dictionary with created tranche and updated conge
            
        Raises:
            ValueError: If validation fails
            SQLAlchemyError: For database errors
        """
        try:
            # Get the leave record
            conge = self.session.query(Conge).filter(Conge.idConge == conge_id).first()

            
            # Check if employee has fewer than 5 existing tranches
            existing_tranches_count = self.session.query(Tranche).filter(Tranche.idConge == conge_id).count()
            if existing_tranches_count >= 5:

                raise ValueError("Maximum of 5 tranches allowed per leave record")
            
            # Validate dates are within current year
            current_year = datetime.now().year
            if date_debut.year != current_year or date_fin.year != current_year:
                raise ValueError(f"Dates must be within current year ({current_year})")
            
            # Validate date range
            if date_debut > date_fin:

                raise ValueError("Start date must be before end date")
            
            # Check for overlaps with existing tranches
            self.validate_tranche_dates(conge_id, date_debut, date_fin)
            
            # Calculate tranche duration
            tranche_days = (date_fin - date_debut).days + 1
            
            # Check if tranche duration exceeds remaining days
            if tranche_days > conge.NbrJoursRestants:
                raise ValueError(f"Tranche duration ({tranche_days} days) exceeds remaining days ({conge.NbrJoursRestants} days)")
            
            # Create new tranche
            new_tranche = Tranche(
                idConge=conge_id,
                NumeroDecision=numero_decision,
                DateDecision=date_decision,
                DateDebut=date_debut,
                DateFin=date_fin
            )
            
            self.session.add(new_tranche)
            
            # Update days taken and remaining days in conge
            conge.NbrJoursPris += tranche_days
            conge.NbrJoursRestants = conge.NbrJoursAlloues - conge.NbrJoursPris
            
            self.session.commit()
            
            # Log successful creation
            self.log_history(
                event="إضافة شطر جديد",
                details=f"إضافة شطر جديد للموظف {conge.idemploye} للإجازة {conge_id} من {date_debut} إلى {date_fin} ({tranche_days} أيام) - قرار رقم: {numero_decision}",
                gestion="إدارة الإجازات",
                tranche_id=new_tranche.idTranche,
                conge_id=conge_id,
                employee_id=conge.idemploye
            )           
            
            return {
                "tranche": {
                    "id": new_tranche.idTranche,
                    "conge_id": new_tranche.idConge,
                    "decision_id": new_tranche.NumeroDecision,
                    "decision_date": new_tranche.DateDecision.strftime("%Y-%m-%d"),
                    "start_date": new_tranche.DateDebut.strftime("%Y-%m-%d"),
                    "end_date": new_tranche.DateFin.strftime("%Y-%m-%d"),
                    "days": tranche_days
                },
                "conge": {
                    "id": conge.idConge,
                    "days_taken": conge.NbrJoursPris,
                    "days_remaining": conge.NbrJoursRestants
                }
            }
            
        except SQLAlchemyError as e:
            self.session.rollback()
            self.log_history(
                event="خطأ قاعدة البيانات",
                details=f"خطأ في قاعدة البيانات أثناء إنشاء شطر للإجازة {conge_id}: {str(e)}",
                gestion="إدارة الإجازات",
                conge_id=conge_id
            )
            raise e
    
    def update_tranche(self, tranche_id, numero_decision=None, date_decision=None, date_debut=None, date_fin=None):
        """
        Update a tranche with enhanced validation and complete logging
        
        Args:
            tranche_id (int): The tranche ID
            numero_decision (int, optional): New decision number
            date_decision (date, optional): New decision date
            date_debut (date, optional): New start date
            date_fin (date, optional): New end date
            
        Returns:
            dict: Dictionary with updated tranche and conge
            
        Raises:
            ValueError: If validation fails
            SQLAlchemyError: For database errors
        """
        try:
            # Get the tranche
            tranche = self.get_tranche_by_id(tranche_id)
    
            
            # Get the leave record
            conge = self.session.query(Conge).filter(Conge.idConge == tranche.idConge).first()
            if not conge:

                raise ValueError(f"Leave record with ID {tranche.idConge} not found")
            
            # Store original values for logging
            original_values = {
                "numero_decision": tranche.NumeroDecision,
                "date_decision": tranche.DateDecision,
                "date_debut": tranche.DateDebut,
                "date_fin": tranche.DateFin
            }
            
            # Calculate original tranche duration
            original_days = (tranche.DateFin - tranche.DateDebut).days + 1
            
            # Update tranche fields if provided
            changes = []
            if numero_decision is not None and numero_decision != tranche.NumeroDecision:
                tranche.NumeroDecision = numero_decision
                changes.append(f"رقم القرار: {original_values['numero_decision']} → {numero_decision}")
                
            if date_decision is not None and date_decision != tranche.DateDecision:
                tranche.DateDecision = date_decision
                changes.append(f"تاريخ القرار: {original_values['date_decision']} → {date_decision}")
                
            # Calculate new duration if dates are changed
            new_start = date_debut if date_debut is not None else tranche.DateDebut
            new_end = date_fin if date_fin is not None else tranche.DateFin
            
            # Validate new dates
            if new_start > new_end:
                self.log_history(
                    event="خطأ في تحديث الشطر",
                    details=f"تاريخ البداية أكبر من تاريخ النهاية في الشطر {tranche_id} للموظف {conge.idemploye}",
                    gestion="إدارة الإجازات",
                    tranche_id=tranche_id,
                    conge_id=conge.idConge,
                    employee_id=conge.idemploye
                )
                raise ValueError("Start date must be before end date")
            
            # Validate dates are within current year
            current_year = datetime.now().year
            if new_start.year != current_year or new_end.year != current_year:

                raise ValueError(f"Dates must be within current year ({current_year})")
            
            # Check for overlaps with other tranches (excluding this one)
            if date_debut is not None or date_fin is not None:
                self.validate_tranche_dates(tranche.idConge, new_start, new_end, exclude_tranche_id=tranche_id)
                
            # Calculate new duration
            new_days = (new_end - new_start).days + 1
            
            # Check if new duration fits within remaining days
            days_difference = new_days - original_days
            if days_difference > conge.NbrJoursRestants:

                raise ValueError(f"New duration exceeds remaining days (need {days_difference} more days, but only {conge.NbrJoursRestants} available)")
            
            # Update dates if provided
            if date_debut is not None and date_debut != tranche.DateDebut:
                tranche.DateDebut = date_debut
                changes.append(f"تاريخ البداية: {original_values['date_debut']} → {date_debut}")
                
            if date_fin is not None and date_fin != tranche.DateFin:
                tranche.DateFin = date_fin
                changes.append(f"تاريخ النهاية: {original_values['date_fin']} → {date_fin}")
            
            # Update days taken and remaining days in conge
            conge.NbrJoursPris = conge.NbrJoursPris + days_difference
            conge.NbrJoursRestants = conge.NbrJoursAlloues - conge.NbrJoursPris
            
            self.session.commit()
            
            # Log successful update
            if changes:
                changes_text = " | ".join(changes)
                self.log_history(
                    event="تحديث الشطر",
                    details=f"تم تحديث الشطر {tranche_id} للموظف {conge.idemploye} - التغييرات: {changes_text} - المدة الجديدة: {new_days} أيام",
                    gestion="إدارة الإجازات",
                    tranche_id=tranche_id,
                    conge_id=conge.idConge,
                    employee_id=conge.idemploye
                )
            else:
                self.log_history(
                    event="محاولة تحديث الشطر",
                    details=f"محاولة تحديث الشطر {tranche_id} للموظف {conge.idemploye} بدون تغييرات",
                    gestion="إدارة الإجازات",
                    tranche_id=tranche_id,
                    conge_id=conge.idConge,
                    employee_id=conge.idemploye
                )
            
            return {
                "tranche": {
                    "id": tranche.idTranche,
                    "conge_id": tranche.idConge,
                    "decision_id": tranche.NumeroDecision,
                    "decision_date": tranche.DateDecision.strftime("%Y-%m-%d"),
                    "start_date": tranche.DateDebut.strftime("%Y-%m-%d"),
                    "end_date": tranche.DateFin.strftime("%Y-%m-%d"),
                    "days": new_days
                },
                "conge": {
                    "id": conge.idConge,
                    "days_taken": conge.NbrJoursPris,
                    "days_remaining": conge.NbrJoursRestants
                }
            }
            
        except SQLAlchemyError as e:
            self.session.rollback()
            self.log_history(
                event="خطأ قاعدة البيانات",
                details=f"خطأ في قاعدة البيانات أثناء تحديث الشطر {tranche_id}: {str(e)}",
                gestion="إدارة الإجازات",
                tranche_id=tranche_id
            )
            raise e
    
    def delete_tranche(self, tranche_id):
        """
        Delete a tranche by ID with complete logging
        
        Args:
            tranche_id (int): The tranche ID
            
        Returns:
            dict: Dictionary with updated conge info
            
        Raises:
            ValueError: If tranche doesn't exist
            SQLAlchemyError: For database errors
        """
        try:
            # Get the tranche
            tranche = self.get_tranche_by_id(tranche_id)
            if not tranche:
                self.log_history(
                    event="خطأ في حذف الشطر",
                    details=f"محاولة حذف شطر غير موجود: {tranche_id}",
                    gestion="إدارة الإجازات",
                    tranche_id=tranche_id
                )
                raise ValueError(f"Tranche with ID {tranche_id} not found")
            
            # Get the leave record
            conge = self.session.query(Conge).filter(Conge.idConge == tranche.idConge).first()
            if not conge:

                raise ValueError(f"Leave record with ID {tranche.idConge} not found")
            
            # Store tranche info for logging before deletion
            tranche_info = {
                "id": tranche.idTranche,
                "numero_decision": tranche.NumeroDecision,
                "date_debut": tranche.DateDebut,
                "date_fin": tranche.DateFin,
                "conge_id": tranche.idConge,
                "employee_id": conge.idemploye
            }
            
            # Calculate tranche duration
            tranche_days = (tranche.DateFin - tranche.DateDebut).days + 1
            
            # Update days taken and remaining days in conge
            conge.NbrJoursPris -= tranche_days
            conge.NbrJoursRestants = conge.NbrJoursAlloues - conge.NbrJoursPris
            
            # Delete the tranche

            
            # Log successful deletion
            self.log_history(
                event="حذف الشطر",
                details=f"تم حذف الشطر {tranche_info['id']} للموظف {tranche_info['employee_id']} - قرار رقم: {tranche_info['numero_decision']} - من {tranche_info['date_debut']} إلى {tranche_info['date_fin']} ({tranche_days} أيام)",
                gestion="إدارة الإجازات",
                tranche_id=tranche_info['id'],
                conge_id=tranche_info['conge_id'],
                employee_id=tranche_info['employee_id']
            )
            self.session.delete(tranche)
            self.session.commit()            
            return {
                "conge": {
                    "id": conge.idConge,
                    "days_taken": conge.NbrJoursPris,
                    "days_remaining": conge.NbrJoursRestants
                }
            }
            
        except SQLAlchemyError as e:
            self.session.rollback()
            self.log_history(
                event="خطأ قاعدة البيانات",
                details=f"خطأ في قاعدة البيانات أثناء حذف الشطر {tranche_id}: {str(e)}",
                gestion="إدارة الإجازات",
                tranche_id=tranche_id
            )
            raise e
    
    def calculate_tranche_days(self, date_debut, date_fin):
        """
        Calculate the number of days in a tranche
        
        Args:
            date_debut (date): Start date
            date_fin (date): End date
            
        Returns:
            int: Number of days
            
        Raises:
            ValueError: If start date is after end date
        """
        if date_debut > date_fin:
            raise ValueError("Start date must be before end date")
            
        return (date_fin - date_debut).days + 1
    
    def validate_tranche_dates(self, conge_id, date_debut, date_fin, exclude_tranche_id=None):
        """
        Validate that tranche dates don't overlap with existing tranches
        
        Args:
            conge_id (int): The leave ID
            date_debut (date): Start date
            date_fin (date): End date
            exclude_tranche_id (int, optional): Tranche ID to exclude from validation
            
        Returns:
            bool: True if valid
            
        Raises:
            ValueError: If dates overlap with existing tranches
        """
        # Get existing tranches for this leave
        query = self.session.query(Tranche).filter(Tranche.idConge == conge_id)
        
        # Exclude the current tranche if updating
        if exclude_tranche_id:
            query = query.filter(Tranche.idTranche != exclude_tranche_id)
            
        existing_tranches = query.all()
        
        # Check for overlaps
        for tranche in existing_tranches:
            # Check if new tranche overlaps with existing tranche
            if (date_debut <= tranche.DateFin and date_fin >= tranche.DateDebut):
                # Log the overlap attempt
                conge = self.session.query(Conge).filter(Conge.idConge == conge_id).first()

                raise ValueError(f"Tranche dates overlap with existing tranche (Decision: {tranche.NumeroDecision})")
        
        return True
    
    def get_tranche_history(self, tranche_id):
        """
        Get history entries for a specific tranche
        
        Args:
            tranche_id (int): The tranche ID
            
        Returns:
            list: List of history entries for this tranche
        """
        try:
            from Controllers.history_controller import HistoryController
            history_controller = HistoryController(self.session)
            return history_controller.get_history_by_entity('tranche', tranche_id)
        except Exception as e:
            self.log_history(
                event="خطأ في استعلام تاريخ الشطر",
                details=f"خطأ في استعلام تاريخ الشطر {tranche_id}: {str(e)}",
                gestion="إدارة الإجازات",
                tranche_id=tranche_id
            )
            return []