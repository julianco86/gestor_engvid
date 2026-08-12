import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

RUTA_SRC = os.path.dirname(os.path.abspath(__file__))
RUTA_PROYECTO = os.path.dirname(RUTA_SRC)
RUTA_DATA = os.path.join(RUTA_PROYECTO, "data")
RUTA_DB = os.path.join(RUTA_DATA, "engvid_database.db")
RUTA_CSV_CRUDO = os.path.join(RUTA_DATA, "engvid_completo.csv")
RUTA_CSV_LIMPIO = os.path.join(RUTA_DATA, "engvid_completo_limpio.csv")


def obtener_engine():
    return create_engine(f"sqlite:///{RUTA_DB}")


def obtener_sesion():
    Session = sessionmaker(bind=obtener_engine())
    return Session()
