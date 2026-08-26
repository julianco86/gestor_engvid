import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

RUTA_SRC = os.path.dirname(os.path.abspath(__file__))
RUTA_PROYECTO = os.path.dirname(RUTA_SRC)
RUTA_DATA = os.path.join(RUTA_PROYECTO, "data")
RUTA_DB = os.path.join(RUTA_DATA, "engvid_database.db")
RUTA_CSV_CRUDO = os.path.join(RUTA_DATA, "engvid_completo.csv")
RUTA_CSV_LIMPIO = os.path.join(RUTA_DATA, "engvid_completo_limpio.csv")

os.makedirs(RUTA_DATA, exist_ok=True)

_engine = None


def obtener_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{RUTA_DB}")

        @event.listens_for(_engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return _engine


def obtener_sesion():
    Session = sessionmaker(bind=obtener_engine())
    return Session()
