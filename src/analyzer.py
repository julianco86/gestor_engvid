import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd

from src.consultas import por_categoria, por_nivel, recomendaciones, resumen
from src.conexion import obtener_sesion

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)


def _formatear(tabla):
    for fila in tabla:
        fila = dict(fila)
        fila["porcentaje"] = f"{fila['porcentaje']}%"
        fila["promedio"] = f"{fila['promedio']:.2f}" if fila["promedio"] is not None else "-"
        yield fila


def mostrar_global(sesion):
    r = resumen(sesion)
    print("\n=== RESUMEN GLOBAL ===")
    print(f"Videos totales:      {r['total']}")
    print(f"Videos vistos:       {r['vistos']} ({r['porcentaje']}%)")
    print(f"Pendientes:          {r['pendientes']}")
    print(f"Quizzes realizados:  {r['quizzes']}")
    print(f"Promedio general:    {r['promedio'] if r['promedio'] is not None else '-'}")


def mostrar_por_nivel(sesion):
    print("\n=== RENDIMIENTO POR NIVEL ===")
    df = pd.DataFrame(_formatear(por_nivel(sesion)))
    df = df.rename(columns={"videos": "Videos", "vistos": "Vistos", "porcentaje": "% Completado", "promedio": "Prom. quiz"})
    print(df.to_string(index=False))


def mostrar_por_categoria(sesion):
    print("\n=== RENDIMIENTO POR CATEGORÍA ===")
    df = pd.DataFrame(_formatear(por_categoria(sesion)))
    df = df.rename(columns={"categoria": "Categoría", "videos": "Videos", "vistos": "Vistos", "porcentaje": "% Completado", "promedio": "Prom. quiz"})
    print(df.to_string(index=False))


def mostrar_recomendaciones(sesion):
    print("\n=== RECOMENDACIONES (áreas más débiles) ===")
    for item in recomendaciones(sesion):
        etiqueta = f"{item['promedio']:.2f}" if item["promedio"] is not None else "sin quizzes aún"
        print(f"\n💡 {item['categoria']} (promedio {etiqueta}):")
        if not item["pendientes"]:
            print("   Todos los videos de esta categoría ya fueron vistos. ¡Bien! 🎉")
        for v in item["pendientes"]:
            print(f"   • {v['titulo']} [{v['nivel']}]")
            print(f"     {v['url']}")


def main():
    sesion = obtener_sesion()
    try:
        if "--recomendar" in sys.argv:
            mostrar_recomendaciones(sesion)
        else:
            mostrar_global(sesion)
            mostrar_por_nivel(sesion)
            mostrar_por_categoria(sesion)
            mostrar_recomendaciones(sesion)
    finally:
        sesion.close()


if __name__ == "__main__":
    main()
