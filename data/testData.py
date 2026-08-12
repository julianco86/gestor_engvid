import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conexion import RUTA_DB
from src.modelos import Progreso, Video

try:
    from sqlalchemy import func, select

    from src.conexion import obtener_sesion

    sesion = obtener_sesion()
    total = sesion.scalar(select(func.count()).select_from(Video))
    primer_video = sesion.scalar(select(Video.titulo).order_by(Video.id))
    progresos = sesion.scalar(select(func.count()).select_from(Progreso))

    print(f"Archivo consultado en: {RUTA_DB}")
    print(f"Total de videos en la DB: {total}")
    print(f"Titulo del primer video: {primer_video}")
    print(f"Registros de progreso: {progresos}")

    sesion.close()

except FileNotFoundError:
    print(f"Error: No se encontro la base de datos '{RUTA_DB}'.")
    print("Ejecuta primero: python src/crearBD.py")
except Exception as e:
    print(f"Ocurrio un error: {e}")
