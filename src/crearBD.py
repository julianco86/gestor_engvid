import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import insert

from src.conexion import RUTA_CSV_LIMPIO, RUTA_DB, obtener_engine
from src.modelos import Base, Progreso, Usuario, Video


def _limpiar_valor(valor):
    if isinstance(valor, float) and math.isnan(valor):
        return None
    return valor


def crear_bd():
    engine = obtener_engine()
    Base.metadata.create_all(engine)

    # Migraciones
    with engine.begin() as conn:
        # rol para usuarios
        try:
            conn.exec_driver_sql("ALTER TABLE usuarios ADD COLUMN rol VARCHAR DEFAULT 'usuario'")
        except Exception:
            pass
        conn.exec_driver_sql(
            "UPDATE usuarios SET rol = 'admin' WHERE username = 'admin' AND rol IS NULL"
        )

        # user_id en progreso
        try:
            conn.exec_driver_sql("ALTER TABLE progreso ADD COLUMN user_id INTEGER")
        except Exception:
            pass
        conn.exec_driver_sql(
            "UPDATE progreso SET user_id = 1 WHERE user_id IS NULL"
        )
        try:
            conn.exec_driver_sql("CREATE INDEX idx_progreso_user ON progreso(user_id)")
        except Exception:
            pass

    # Crear usuario admin si no existe
    from src.auth import crear_usuario
    try:
        crear_usuario("admin", "admin123")
        print("Usuario admin creado (admin / admin123)")
    except ValueError:
        pass  # Ya existe

    # Asegurar que admin tenga rol admin
    with engine.begin() as conn:
        conn.exec_driver_sql("UPDATE usuarios SET rol = 'admin' WHERE username = 'admin'")

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
        conn.exec_driver_sql(
            "UPDATE progreso SET fecha_nota = fecha_visto "
            "WHERE nota_quiz IS NOT NULL AND fecha_nota IS NULL"
        )

    print(f"Base de datos creada en: {RUTA_DB}")
    print(f"Se cargaron {len(filas)} videos desde: {RUTA_CSV_LIMPIO}")


if __name__ == "__main__":
    crear_bd()
