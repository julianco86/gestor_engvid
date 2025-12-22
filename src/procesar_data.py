import pandas as pd
import os

# -----------------------
# Cargar CSV
# -----------------------
ruta_base = os.path.dirname(os.path.abspath(__file__))
ruta_proyecto = os.path.dirname(ruta_base)
ruta_csv = os.path.join(ruta_proyecto, "data", "engvid_completo.csv")

print("Cargando CSV desde:", ruta_csv)
try:
    df = pd.read_csv(ruta_csv)
except UnicodeDecodeError:
    # Intenta con otro encoding si falla UTF-8
    df = pd.read_csv(ruta_csv, encoding='latin-1')

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

# -----------------------
# Procesar Detalles
# -----------------------

# 1. 🔍 Extraer Nivel usando una Expresión Regular
# Busca 'Beginner', 'Intermediate', o 'Advanced' opcionalmente precedido por 'Nivel-', 'Level-' o un número (ej. '2-').
# Se usa '(\d+-)?' para capturar 0 o 1 dígito seguido de un guión, que es opcional.
# Se usa '(Intermediate|Beginner|Advanced)' para capturar el nivel exacto.
# -----------------------
# Procesar Detalles (Versión Corregida para el error)
# -----------------------

# 1. 🔍 Extraer Nivel usando una Expresión Regular
level_regex = r'(\d+-)?(Intermediate|Beginner|Advanced)'

# Corregido: Usamos expand=True para obtener un DataFrame con las dos capturas.
# Luego seleccionamos la columna [1] (que contiene el Nivel) y luego aplicamos .fillna()
df["Nivel"] = df["Detalles"].str.extract(level_regex, expand=True)[1].fillna('Unspecified')
#                                          ^^^^^^^^^^^^^^^^^^^  ^^^

# 2. 🧹 Limpiar la columna Detalles (eliminar el Nivel y sus posibles prefijos)
df["Detalles"] = df["Detalles"].str.replace(level_regex, '', regex=True).str.strip().str.replace(r'\s{2,}', ' ', regex=True)


# -----------------------
# Mostrar resultado (50 primeras filas)
# -----------------------
print(df.head(50))
print(f"\n[{len(df)} filas x {len(df.columns)} columnas]")


# Generate new CSV file with cleaned data
ruta_nuevo_csv = os.path.join(ruta_proyecto, "data", "engvid_completo_limpio.csv")
df.to_csv(ruta_nuevo_csv, index=False)
print(f"CSV limpio guardado en: {ruta_nuevo_csv}")

