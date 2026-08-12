import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import insert

from src.conexion import RUTA_CSV_LIMPIO, RUTA_DB, obtener_engine
from src.modelos import Base, Video


def _limpiar_valor(valor):
    if isinstance(valor, float) and math.isnan(valor):
        return None
    return valor


def crear_bd():
    engine = obtener_engine()
    Base.metadata.drop_all(engine)
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS usuarios")
    Base.metadata.create_all(engine)

    df = pd.read_csv(RUTA_CSV_LIMPIO)
    df.columns = [c.lower() for c in df.columns]

    columnas = ["titulo", "detalles", "url", "nivel", "niveles", "categorias"]
    filas = [
        {k: _limpiar_valor(v) for k, v in reg.items()}
        for reg in df[columnas].to_dict("records")
    ]

    with engine.begin() as conn:
        conn.execute(Video.__table__.delete())
        conn.execute(insert(Video), filas)

    print(f"Base de datos creada en: {RUTA_DB}")
    print(f"Se cargaron {len(filas)} videos desde: {RUTA_CSV_LIMPIO}")


if __name__ == "__main__":
    crear_bd()
