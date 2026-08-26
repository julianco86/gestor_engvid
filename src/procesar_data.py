import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

from src.categorias import NIVEL_ORDEN, categorias_como_texto
from src.conexion import RUTA_CSV_CRUDO, RUTA_CSV_LIMPIO

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

nivel_regex = re.compile(r"(\d+-)?(Beginner|Intermediate|Advanced)", re.IGNORECASE)


def extraer_niveles(texto):
    """Devuelve todos los niveles encontrados en el texto (ordenados)."""
    if not isinstance(texto, str):
        return []
    encontrados = []
    for m in nivel_regex.finditer(texto):
        nivel = m.group(2).capitalize()
        if nivel not in encontrados:
            encontrados.append(nivel)
    return encontrados


def nivel_principal(texto):
    """Devuelve el nivel más alto del texto (o 'Unspecified')."""
    niveles = extraer_niveles(texto)
    if not niveles:
        return "Unspecified"
    return max(niveles, key=lambda n: NIVEL_ORDEN[n])


def procesar():
    print("Cargando CSV desde:", RUTA_CSV_CRUDO)
    try:
        df = pd.read_csv(RUTA_CSV_CRUDO)
    except UnicodeDecodeError:
        df = pd.read_csv(RUTA_CSV_CRUDO, encoding="latin-1")

    df["Niveles"] = df["Detalles"].apply(extraer_niveles).apply(lambda ls: ", ".join(ls))
    df["Nivel"] = df["Detalles"].apply(nivel_principal)

    df["Detalles"] = (
        df["Detalles"]
        .str.replace(r"\d+-?(Beginner|Intermediate|Advanced)", "", regex=True)
        .str.replace(r"[\s|]+", " ", regex=True)
        .str.strip()
    )

    df["Categorias"] = df["Detalles"].apply(categorias_como_texto)

    df.to_csv(RUTA_CSV_LIMPIO, index=False)

    print(df[["ID", "Titulo", "Nivel", "Categorias"]].head(50).to_string(index=False))
    print(f"\n[{len(df)} filas x {len(df.columns)} columnas]")
    print("Distribución por nivel:")
    print(df["Nivel"].value_counts().to_string())
    print(f"\nCSV limpio guardado en: {RUTA_CSV_LIMPIO}")


if __name__ == "__main__":
    procesar()
