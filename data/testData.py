import sqlite3
import os

# 1. Localizar la base de datos
# Obtenemos la ruta de la carpeta donde está este script
ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
# Unimos esa ruta con el nombre del archivo
ruta_db = os.path.join(ruta_carpeta, 'engvid_database.db')

# 2. Conectar y consultar
try:
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    # Contar cuántas filas hay en la tabla videos
    cursor.execute("SELECT COUNT(*) FROM videos")
    total = cursor.fetchone()[0]

    # Ver el primer video para estar seguros
    cursor.execute("SELECT titulo FROM videos LIMIT 1")
    primer_video = cursor.fetchone()[0]

    print(f"📂 Archivo consultado en: {ruta_db}")
    print(f"📊 Total de videos en la DB: {total}")
    print(f"🎬 Título del primer video: {primer_video}")

    conn.close()

except sqlite3.OperationalError:
    print(f"❌ Error: No se encontró el archivo '{ruta_db}'.")
    print("Asegúrate de que el script y la base de datos estén en la misma carpeta.")
except Exception as e:
    print(f"❌ Ocurrió un error: {e}")