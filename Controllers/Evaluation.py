import datetime
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy import func, cast, Float
from Controllers.EmployeController import EmployeeController
from Controllers.BaseController import BaseControllerWithHistory
from Models import Employe
from Models.Evaluation import Evaluation

class EvaluationController(BaseControllerWithHistory):
    def __init__(self, db_session, current_user_account_number=None):
        super().__init__(db_session, current_user_account_number)
        # CORRECTION: Ajouter cette ligne pour maintenir la compatibilité
        self.db_session = db_session
        print(f"DEBUG - EvaluationController init completed, self.current_user_account_number: {self.current_user_account_number}")

    def save_evaluation_for_employee(self, name, lastname, annee, note_annuelle, note1=None, note2=None, note3=None, note4=None):
        """Save evaluation with comprehensive history logging (Update if exists, Create if not)."""
        employe_controller = EmployeeController(self.db_session, self.current_user_account_number)
        
        try:
            print(f"DEBUG - Starting save_evaluation_for_employee for {name} {lastname}")
            employee_id = employe_controller.getidbynameandlastname(name, lastname)

            if employee_id is None:
                print(f"DEBUG - Employee not found: {name} {lastname}")
                return "not_found"

            # Get employee for logging
            employee = self.db_session.query(Employe).filter(Employe.idemploye == employee_id).first()
            employee_name = f"{employee.Prenom} {employee.Nom}" if employee else f"رقم {employee_id}"

            # Check if evaluation already exists for this employee and year
            existing_evaluation = self.db_session.query(Evaluation).filter_by(
                idemploye=employee_id,
                Annee=annee.strip()
            ).first()

            if existing_evaluation:
                # --- UPDATE EXISTING EVALUATION ---
                print(f"DEBUG - Updating existing evaluation for employee {employee_id}, year {annee}")
                existing_evaluation.NoteAnnuelle = note_annuelle.strip()
                existing_evaluation.Note1 = note1.strip() if note1 else existing_evaluation.Note1
                existing_evaluation.Note2 = note2.strip() if note2 else existing_evaluation.Note2
                existing_evaluation.Note3 = note3.strip() if note3 else existing_evaluation.Note3
                existing_evaluation.Note4 = note4.strip() if note4 else existing_evaluation.Note4
                evaluation = existing_evaluation
                action_type = "تحديث تقييم موجود"
            else:
                # --- CREATE NEW EVALUATION ---
                print(f"DEBUG - Creating new evaluation for employee {employee_id}, year {annee}")
                evaluation = Evaluation(
                    idemploye=employee_id,
                    Annee=annee.strip(),
                    NoteAnnuelle=note_annuelle.strip(),
                    Note1=note1.strip() if note1 else None,
                    Note2=note2.strip() if note2 else None,
                    Note3=note3.strip() if note3 else None,
                    Note4=note4.strip() if note4 else None,
                )
                self.db_session.add(evaluation)
                self.db_session.flush()
                action_type = "إضافة تقييم جديد"

            # --- Commit the changes ---
            self.db_session.commit()

            # --- Log the action ---
            notes_info = []
            if note1: notes_info.append(f"نقطة 1: {note1}")
            if note2: notes_info.append(f"نقطة 2: {note2}")
            if note3: notes_info.append(f"نقطة 3: {note3}")
            if note4: notes_info.append(f"نقطة 4: {note4}")
            notes_text = " - " + " | ".join(notes_info) if notes_info else ""

            self.log_history(
                event=action_type,
                details=f"{action_type} للموظف: {employee_name} - السنة: {annee} - النقطة السنوية: {note_annuelle}{notes_text}",
                gestion="إدارة التقييمات",
                employee_id=employee_id,
                evaluation_id=evaluation.idEvaluation
            )

            print(f"DEBUG - Evaluation saved successfully ({action_type})")
            return "success"

        except Exception as e:
            self.db_session.rollback()
            print(f"Error in save_evaluation_for_employee: {e}")
            return "error"



    @staticmethod
    def safe_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def calculate_average(self, notes):
        """Calculate average with history logging"""
        try:
            valid_notes = []
            for note in notes:
                if note is not None:
                    try:
                        valid_notes.append(float(note))
                    except ValueError:
                        pass
            
            average = round(sum(valid_notes) / len(valid_notes), 2) if valid_notes else None

            return average
        except Exception as e:

            return None

    def load_evaluations_with_employee_names(self):
        """Load all evaluations with employee names and history logging"""
        try:
            results = (
                self.db_session.query(
                    Evaluation.idEvaluation.label("idEvaluation"),
                    Evaluation.Annee.label("Annee"),
                    Evaluation.idemploye.label("idemploye"),
                    Employe.Nom.label("nom"),
                    Employe.Prenom.label("prenom"),
                    Evaluation.NoteAnnuelle.label("NoteAnnuelle"),
                    Evaluation.Note1.label("Note1"),
                    Evaluation.Note2.label("Note2"),
                    Evaluation.Note3.label("Note3"),
                    Evaluation.Note4.label("Note4"),
                )
                .join(Employe, Evaluation.idemploye == Employe.idemploye)
                .all()
            )

            table_data = []
            for row in results:
                notes = [row.NoteAnnuelle, row.Note1, row.Note2, row.Note3, row.Note4]
                moyenne = self.calculate_average(notes)

                table_data.append({
                    "idEvaluation": row.idEvaluation,
                    "Annee": row.Annee,
                    "idemploye": row.idemploye,
                    "nom": row.nom,
                    "prenom": row.prenom,
                    "NoteAnnuelle": row.NoteAnnuelle,
                    "Note1": row.Note1,
                    "Note2": row.Note2,
                    "Note3": row.Note3,
                    "Note4": row.Note4,
                    "Moyenne": moyenne,
                })


            return table_data

        except Exception as e:
            print(f"Error loading evaluations: {e}")

            return []

    def update_evaluation(self, evaluation_id, annee, note_annuelle, note1=None, note2=None, note3=None, note4=None):
        """Update evaluation with comprehensive history logging"""
        try:
            evaluation = self.db_session.query(Evaluation).filter_by(idEvaluation=evaluation_id).first()

            if not evaluation:
             
                return "not_found"

            # Get employee name for logging
            employee = self.db_session.query(Employe).filter(Employe.idemploye == evaluation.idemploye).first()
            employee_name = f"{employee.Prenom} {employee.Nom}" if employee else f"رقم {evaluation.idemploye}"

            # Store old values for history
            old_annee = evaluation.Annee
            old_note_annuelle = evaluation.NoteAnnuelle
            old_note1 = evaluation.Note1
            old_note2 = evaluation.Note2
            old_note3 = evaluation.Note3
            old_note4 = evaluation.Note4

            # Check for duplicate year for the same employee (excluding current evaluation)
            existing = self.db_session.query(Evaluation).filter(
                Evaluation.idemploye == evaluation.idemploye,
                Evaluation.Annee == annee.strip(),
                Evaluation.idEvaluation != evaluation_id
            ).first()

            if existing:

                return "already_exists"

            # Track changes
            changes = []
            if old_annee != annee.strip():
                changes.append(f"السنة: {old_annee} ← {annee.strip()}")
            if old_note_annuelle != note_annuelle.strip():
                changes.append(f"النقطة السنوية: {old_note_annuelle} ← {note_annuelle.strip()}")
            if old_note1 != (note1.strip() if note1 else None):
                old_n1 = old_note1 or "غير محدد"
                new_n1 = note1.strip() if note1 else "غير محدد"
                changes.append(f"نقطة المردودية 1: {old_n1} ← {new_n1}")
            if old_note2 != (note2.strip() if note2 else None):
                old_n2 = old_note2 or "غير محدد"
                new_n2 = note2.strip() if note2 else "غير محدد"
                changes.append(f"نقطة المردودية 2: {old_n2} ← {new_n2}")
            if old_note3 != (note3.strip() if note3 else None):
                old_n3 = old_note3 or "غير محدد"
                new_n3 = note3.strip() if note3 else "غير محدد"
                changes.append(f"نقطة المردودية 3: {old_n3} ← {new_n3}")
            if old_note4 != (note4.strip() if note4 else None):
                old_n4 = old_note4 or "غير محدد"
                new_n4 = note4.strip() if note4 else "غير محدد"
                changes.append(f"نقطة المردودية 4: {old_n4} ← {new_n4}")

            # Proceed with update
            evaluation.Annee = annee.strip() if annee else None
            evaluation.NoteAnnuelle = note_annuelle.strip() if note_annuelle else None
            evaluation.Note1 = note1.strip() if note1 else None
            evaluation.Note2 = note2.strip() if note2 else None
            evaluation.Note3 = note3.strip() if note3 else None
            evaluation.Note4 = note4.strip() if note4 else None

            self.db_session.commit()

            # Log successful update
            if changes:
                self.log_history(
                    event="تحديث تقييم",
                    details=f"تم تحديث التقييم رقم {evaluation_id} للموظف: {employee_name} - التغييرات: {' | '.join(changes)}",
                    gestion="إدارة التقييمات",
                    evaluation_id=evaluation_id,
                    employee_id=evaluation.idemploye
                )
            else:
                self.log_history(
                    event="محاولة تحديث تقييم",
                    details=f"تم محاولة تحديث التقييم رقم {evaluation_id} للموظف: {employee_name} - لا توجد تغييرات",
                    gestion="إدارة التقييمات",
                    evaluation_id=evaluation_id,
                    employee_id=evaluation.idemploye
                )

            return "success"

        except Exception as e:
            self.db_session.rollback()

            return "db_error"

    def load_evaluations_with_employee_names_current_year(self):
        """Load current year evaluations with history logging"""
        try:
            import datetime
            current_year = datetime.datetime.now().year
            employe_controller = EmployeeController(self.db_session, self.current_user_account_number)
            
            # Obtenir les identifiants des employés ayant un départ définitif
            departed_ids = set(depart.idemploye for depart in employe_controller.get_final_departures())

            # Requête avec jointure externe pour inclure tous les employés
            results = (
                self.db_session.query(
                    Evaluation.idEvaluation.label("idEvaluation"),
                    Evaluation.Annee.label("Annee"),
                    Evaluation.idemploye.label("idemploye"),
                    Employe.idemploye.label("idemploye"),
                    Employe.Nom.label("nom"),
                    Employe.Prenom.label("prenom"),
                    Evaluation.NoteAnnuelle.label("NoteAnnuelle"),
                    Evaluation.Note1.label("Note1"),
                    Evaluation.Note2.label("Note2"),
                    Evaluation.Note3.label("Note3"),
                    Evaluation.Note4.label("Note4"),
                )
                .select_from(Employe)
                .outerjoin(
                    Evaluation,
                    (Evaluation.idemploye == Employe.idemploye) & (Evaluation.Annee == current_year)
                )
                .all()
            )

            # Construction des données pour le tableau
            table_data = []
            for row in results:
                # ⚠️ Ignorer les employés qui ont quitté définitivement
                if row.idemploye in departed_ids:
                    continue

                notes = [row.NoteAnnuelle, row.Note1, row.Note2, row.Note3, row.Note4]
                moyenne = self.calculate_average(notes) if any(n is not None for n in notes) else None

                table_data.append({
                    "idEvaluation": row.idEvaluation,
                    "Annee": row.Annee,
                    "idemploye": row.idemploye,
                    "nom": row.nom,
                    "prenom": row.prenom,
                    "NoteAnnuelle": row.NoteAnnuelle,
                    "Note1": row.Note1,
                    "Note2": row.Note2,
                    "Note3": row.Note3,
                    "Note4": row.Note4,
                    "Moyenne": moyenne,
                })


            return table_data

        except Exception as e:
            print(f"Error loading current year evaluations: {e}")

            return []

    def delete_evaluation(self, evaluation_id):
        """Delete evaluation with comprehensive history logging"""
        try:
            evaluation = self.db_session.query(Evaluation).filter_by(idEvaluation=evaluation_id).first()
            if not evaluation:

                raise ValueError("التقييم غير موجود.")

            # Get employee name and evaluation details for logging
            employee = self.db_session.query(Employe).filter(Employe.idemploye == evaluation.idemploye).first()
            employee_name = f"{employee.Prenom} {employee.Nom}" if employee else f"رقم {evaluation.idemploye}"
            evaluation_year = evaluation.Annee
            evaluation_note = evaluation.NoteAnnuelle
            employee_id = evaluation.idemploye

            # Delete the evaluation

            # Log successful deletion
            self.log_history(
                event="حذف تقييم",
                details=f"تم حذف التقييم رقم {evaluation_id} للموظف: {employee_name} - السنة: {evaluation_year} - النقطة السنوية: {evaluation_note}",
                gestion="إدارة التقييمات",
                evaluation_id=evaluation_id,
                employee_id=employee_id
            )
            self.db_session.delete(evaluation)
            self.db_session.commit()

            return True

        except Exception as e:
            self.db_session.rollback()
            

            raise e

    def update_evaluation_past(self, evaluation_id, annee, note_annuelle, note1=None, note2=None, note3=None, note4=None):
        """Update past evaluation with comprehensive history logging"""
        try:
            # Find the evaluation by ID
            evaluation = self.db_session.query(Evaluation).filter_by(idEvaluation=evaluation_id).first()

            if not evaluation:

                return "not_found"

            # Get employee name for logging
            employee = self.db_session.query(Employe).filter(Employe.idemploye == evaluation.idemploye).first()
            employee_name = f"{employee.Prenom} {employee.Nom}" if employee else f"رقم {evaluation.idemploye}"

            # Clean the year input
            annee = annee.strip() if annee else None

            # Check if any other evaluation exists for the same employee and year
            existing_eval = (
                self.db_session.query(Evaluation)
                .filter(
                    Evaluation.Annee == annee,
                    Evaluation.idemploye == evaluation.idemploye,
                    Evaluation.idEvaluation != evaluation_id
                )
                .first()
            )
            if existing_eval:
 
                return "already_exists"

            # Store old values for history
            old_annee = evaluation.Annee
            old_note_annuelle = evaluation.NoteAnnuelle
            old_note1 = evaluation.Note1
            old_note2 = evaluation.Note2
            old_note3 = evaluation.Note3
            old_note4 = evaluation.Note4

            # Track changes
            changes = []
            if old_annee != annee:
                changes.append(f"السنة: {old_annee} ← {annee}")
            if old_note_annuelle != (note_annuelle.strip() if note_annuelle else None):
                changes.append(f"النقطة السنوية: {old_note_annuelle} ← {note_annuelle.strip() if note_annuelle else None}")
            if old_note1 != (note1.strip() if note1 else None):
                old_n1 = old_note1 or "غير محدد"
                new_n1 = note1.strip() if note1 else "غير محدد"
                changes.append(f"نقطة المردودية 1: {old_n1} ← {new_n1}")
            if old_note2 != (note2.strip() if note2 else None):
                old_n2 = old_note2 or "غير محدد"
                new_n2 = note2.strip() if note2 else "غير محدد"
                changes.append(f"نقطة المردودية 2: {old_n2} ← {new_n2}")
            if old_note3 != (note3.strip() if note3 else None):
                old_n3 = old_note3 or "غير محدد"
                new_n3 = note3.strip() if note3 else "غير محدد"
                changes.append(f"نقطة المردودية 3: {old_n3} ← {new_n3}")
            if old_note4 != (note4.strip() if note4 else None):
                old_n4 = old_note4 or "غير محدد"
                new_n4 = note4.strip() if note4 else "غير محدد"
                changes.append(f"نقطة المردودية 4: {old_n4} ← {new_n4}")

            # Update the evaluation fields
            evaluation.Annee = annee
            evaluation.NoteAnnuelle = note_annuelle.strip() if note_annuelle else None
            evaluation.Note1 = note1.strip() if note1 else None
            evaluation.Note2 = note2.strip() if note2 else None
            evaluation.Note3 = note3.strip() if note3 else None
            evaluation.Note4 = note4.strip() if note4 else None

            self.db_session.commit()

            # Log successful update
            if changes:
                self.log_history(
                    event="تحديث تقييم سابق",
                    details=f"تم تحديث التقييم السابق رقم {evaluation_id} للموظف: {employee_name} - التغييرات: {' | '.join(changes)}",
                    gestion="إدارة التقييمات",
                    evaluation_id=evaluation_id,
                    employee_id=evaluation.idemploye
                )
            else:
                self.log_history(
                    event="محاولة تحديث تقييم سابق",
                    details=f"تم محاولة تحديث التقييم السابق رقم {evaluation_id} للموظف: {employee_name} - لا توجد تغييرات",
                    gestion="إدارة التقييمات",
                    evaluation_id=evaluation_id,
                    employee_id=evaluation.idemploye
                )

            return "success"

        except Exception as e:
            self.db_session.rollback()

            return "db_error"