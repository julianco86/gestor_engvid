import sqlite3
import os

# 1. Aseguramos la ruta correcta al archivo .db
ruta_actual = os.path.dirname(__file__)
ruta_db = os.path.join(ruta_actual, 'engvid_database.db')

try:
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    print("--- 📊 RESUMEN DE LA BASE DE DATOS ---")

    # Consulta 1: Total de videos
    cursor.execute("SELECT COUNT(*) FROM videos")
    total = cursor.fetchone()[0]
    print(f"✅ Total de registros: {total}")

    # Consulta 2: Conteo por Niveles (Agrupación)
    print("\n--- 📈 VIDEOS POR NIVEL ---")
    cursor.execute("SELECT nivel, COUNT(*) FROM videos GROUP BY nivel ORDER BY COUNT(*) DESC")
    niveles = cursor.fetchall()
    
    for nivel, cantidad in niveles:
        # Un poco de formato visual
        progreso_visual = "█" * int(cantidad / 100) # Una barra simple
        print(f"{nivel.ljust(15)}: {str(cantidad).ljust(5)} {progreso_visual}")

    # Consulta 3: Muestra de datos con URL
    print("\n--- 🎬 ÚLTIMOS 5 VIDEOS AGREGADOS (Muestra) ---")
    cursor.execute("SELECT id, titulo, nivel, url FROM videos ORDER BY id DESC LIMIT 5")
    ultimos = cursor.fetchall()
    
    for vid in ultimos:
        print(f"ID: {vid[0]} | {vid[2]} | {vid[1]}")
        print(f"   🔗 URL: {vid[3]}")

    conn.close()

except Exception as e:
    print(f"❌ Error al consultar la base de datos: {e}")