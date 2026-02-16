from DatabaseConnection import Database
from Models import Employe
from Models import Evaluation
from Models import Absence
from Models import Formation
from Models import User
from Models import Contractuel
from Models import Carriere

if __name__ == "__main__":
    db = Database(user="hr", password="hr", host="localhost", db_name="HR", port=3306)
    # Supprimer toutes les anciennes tables
    db.drop_all_tables()
    # Créer toutes les nouvelles tables
    db.create_tables()

