import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from src.categorias import CATEGORIAS, NIVELES
from src.consultas import (
    listar_videos,
    marcar_visto,
    obtener_video,
    por_nivel,
    registrar_nota,
    resumen,
)
from src.conexion import obtener_sesion

POR_PAGINA = 20


def _pedir_video_id(accion):
    texto = input(f"ID del video a {accion}: ").strip()
    if not texto.isdigit():
        print("ID inválido.")
        return None
    return int(texto)


def _mostrar_resultados(filas, titulo):
    print(f"\n{titulo} ({len(filas)} resultados)\n")
    if not filas:
        print("Sin resultados.")
        return
    for i in range(0, len(filas), POR_PAGINA):
        for r in filas[i:i + POR_PAGINA]:
            estado = "✓" if r["completado"] else "·"
            print(f"  {r['id']:5d} [{estado}] {r['titulo']}")
        if i + POR_PAGINA < len(filas):
            tecla = input("... Enter para continuar, 'q' para salir: ").strip().lower()
            if tecla == "q":
                break


def listar(sesion):
    print("\n--- FILTROS (Enter para 'Todos') ---")
    nivel = input(f"Nivel {NIVELES}: ").strip().capitalize()
    categoria = input(f"Categoría {CATEGORIAS}: ").strip().lower()
    texto = input("Texto en el título: ").strip().lower()
    estado = input("Estado (vistos/pendientes/todos): ").strip().lower()

    data = listar_videos(
        sesion,
        nivel=nivel or None,
        categoria=categoria or None,
        texto=texto or None,
        estado=estado if estado in ("vistos", "pendientes") else None,
    )
    _mostrar_resultados(data["resultados"], "VIDEOS ENCONTRADOS")


def cambiar_estado(sesion, completado):
    video_id = _pedir_video_id("marcar" if completado else "desmarcar")
    if video_id is None:
        return
    try:
        video = marcar_visto(sesion, video_id, completado)
    except ValueError as e:
        print(f"❌ {e}")
        return
    estado = "VISTO" if completado else "PENDIENTE"
    print(f"✅ Video #{video['id']} marcado como {estado}: {video['titulo']}")


def nota(sesion):
    video_id = _pedir_video_id("registrar nota")
    if video_id is None:
        return
    entrada = input("Nota del quiz (0 a 10): ").strip()
    try:
        valor = float(entrada.replace(",", "."))
    except ValueError:
        print("Nota inválida.")
        return
    try:
        video = registrar_nota(sesion, video_id, valor)
    except ValueError as e:
        print(f"❌ {e}")
        return
    print(f"🎯 Nota {video['nota_quiz']} registrada en #{video['id']} (intento {video['intentos']}): {video['titulo']}")


def detalle(sesion):
    video_id = _pedir_video_id("consultar")
    if video_id is None:
        return
    video = obtener_video(sesion, video_id)
    if video is None:
        print("No existe un video con ese ID.")
        return
    print(f"\nID: {video['id']}")
    print(f"Título: {video['titulo']}")
    print(f"Nivel: {video['nivel']}  |  Categorías: {video['categorias'] or '-'}")
    print(f"URL: {video['url']}")
    print(f"Estado: {'Visto' if video['completado'] else 'Pendiente'}")
    print(f"Fecha visto: {video['fecha_visto'] or '-'}")
    print(f"Nota quiz: {video['nota_quiz'] if video['nota_quiz'] is not None else '-'}")
    print(f"Intentos: {video['intentos']}")


def progreso(sesion):
    r = resumen(sesion)
    print("\n=== RESUMEN DE PROGRESO ===")
    print(f"Videos totales:      {r['total']}")
    print(f"Videos vistos:       {r['vistos']} ({r['porcentaje']}%)")
    print(f"Pendientes:          {r['pendientes']}")
    print(f"Quizzes registrados: {r['quizzes']}")
    print(f"Promedio de notas:   {r['promedio'] if r['promedio'] is not None else '-'}")

    filas_nivel = por_nivel(sesion)
    print("\nPor nivel:")
    for fila in filas_nivel:
        print(f"  {fila['nivel']:13s} {fila['vistos']:5d} de {fila['videos']} vistos")


def main():
    sesion = obtener_sesion()
    try:
        while True:
            print("\n" + "=" * 45)
            print("  📚 ENGVID LEARNING TRACKER")
            print("=" * 45)
            print("  1. Listar videos")
            print("  2. Marcar como visto")
            print("  3. Desmarcar como visto")
            print("  4. Registrar nota de quiz")
            print("  5. Ver mi progreso")
            print("  6. Detalle de un video")
            print("  0. Salir")
            print("=" * 45)
            opcion = input("Opción: ").strip()

            if opcion == "1":
                listar(sesion)
            elif opcion == "2":
                cambiar_estado(sesion, completado=True)
            elif opcion == "3":
                cambiar_estado(sesion, completado=False)
            elif opcion == "4":
                nota(sesion)
            elif opcion == "5":
                progreso(sesion)
            elif opcion == "6":
                detalle(sesion)
            elif opcion == "0":
                print("¡Hasta luego! 👋")
                break
            else:
                print("Opción inválida.")
    finally:
        sesion.close()


if __name__ == "__main__":
    main()
