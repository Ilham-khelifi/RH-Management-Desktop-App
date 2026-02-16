from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from Models import Base

class Database:
    def __init__(self, user, password, host, db_name, port=3306):
        if not all([user, password, host, db_name]):
            raise ValueError("Missing database configuration.")
        

        self.engine = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4",
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
            future=True
        )
        self.Session = scoped_session(sessionmaker(bind=self.engine))
    def drop_all_tables(self):
        """Supprime toutes les tables de la base, désactivant temporairement les contraintes FK."""
        with self.engine.connect() as conn:
            # Désactive les contraintes FK pour éviter les erreurs
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            
            meta = MetaData()
            meta.reflect(bind=self.engine)
            
            # Drop toutes les tables (ordre inverse des dépendances)
            for table in reversed(meta.sorted_tables):
                print(f"Suppression de la table {table.name}")
                table.drop(self.engine)
            
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def close(self):
        self.Session.remove()




db = Database(
    user="hr",
    password="hr",
    host="localhost",
    db_name="HR",
    port=3306
)

