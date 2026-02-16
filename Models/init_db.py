from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import re
from Models import Base





def init_db(db_url='mysql+pymysql://username:password@localhost/hrms'):
    """Initialise la connexion à la base de données et crée les tables si elles n'existent pas"""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# Exemple d'utilisation:
# session = init_db('mysql+pymysql://root:password@localhost/hrms')