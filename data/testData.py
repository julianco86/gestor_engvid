import sqlite3

# Conectar al archivo que creó el script anterior
conn = sqlite3.connect('engvid_database.db')
cursor = conn.cursor()

# Contar cuántas filas hay en la tabla videos
cursor.execute("SELECT COUNT(*) FROM videos")
total = cursor.fetchone()[0]

# Ver el primer video para estar seguros
cursor.execute("SELECT titulo FROM videos LIMIT 1")
primer_video = cursor.fetchone()[0]


print(f"📊 Total de videos en la DB: {total}")
print(f"🎬 Título del primer video: {primer_video}")


# Ver los primeros 10 videos
cursor.execute("SELECT id, titulo FROM videos LIMIT 10")
primeros_10_videos = cursor.fetchall()

for i, video in enumerate(primeros_10_videos, start=1):
    print(f"🎬 Video {i}: {video[1]}")

conn.close()