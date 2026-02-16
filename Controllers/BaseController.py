from Controllers.history_controller import HistoryController

class BaseControllerWithHistory:
    """
    Classe de base pour tous les contrôleurs qui doivent enregistrer l'historique
    """
    def __init__(self, db_session, current_user_account_number=None, gestion_module="النظام"):
        self.session = db_session
        self.current_user_account_number = current_user_account_number
        self.gestion_module = gestion_module  # NOUVEAU : Module de gestion par défaut
        self.history_controller = HistoryController(db_session)
    
    def log_history(self, event, details, gestion=None, **kwargs):
        """
        Enregistre une entrée dans l'historique
       
        Args:
            event: Type d'événement
            details: Détails de l'événement
            gestion: Module de gestion (optionnel, utilise celui par défaut si non fourni)
            **kwargs: IDs optionnels des entités liées (employee_id, formation_id, etc.)
        """
        print(f"DEBUG - log_history appelé: event={event}, user={self.current_user_account_number}")
        if self.current_user_account_number:
            try:
                print(f"DEBUG - Tentative d'enregistrement dans l'historique...")
                # Utiliser la gestion fournie ou celle par défaut
                target_gestion = gestion if gestion else self.gestion_module
                
                # Ajouter les IDs des entités liées si fournis
                result = self.history_controller.add_history_entry_with_relations(
                    user_account_number=self.current_user_account_number,
                    event=event,
                    details=details,
                    gestion=target_gestion,  # NOUVEAU : Inclure la gestion
                    **kwargs
                )
                print(f"DEBUG - Résultat enregistrement: {result}")
            except Exception as e:
                print(f"Erreur lors de l'enregistrement de l'historique: {e}")
        else:
            print("DEBUG - Aucun utilisateur actuel défini, historique non enregistré")
    
    def set_current_user(self, user_account_number):
        """Met à jour l'utilisateur actuel"""
        self.current_user_account_number = user_account_number
    
    def set_gestion_module(self, gestion_module):
        """NOUVEAU : Met à jour le module de gestion"""
        self.gestion_module = gestion_module
    
    def get_module_history(self, limit=None):
        """NOUVEAU : Récupère l'historique du module actuel"""
        return self.history_controller.get_history_by_gestion(self.gestion_module, limit)
