from datetime import date

from sqlalchemy import func, select

from src.categorias import CATEGORIAS, NIVELES
from src.modelos import Progreso, Video


def _video_a_dict(video, prog=None):
    return {
        "id": video.id,
        "titulo": video.titulo,
        "detalles": video.detalles,
        "url": video.url,
        "nivel": video.nivel,
        "niveles": video.niveles,
        "categorias": video.categorias,
        "completado": bool(prog.completado) if prog else False,
        "fecha_visto": str(prog.fecha_visto) if prog and prog.fecha_visto else None,
        "nota_quiz": prog.nota_quiz if prog and prog.nota_quiz is not None else None,
        "intentos": prog.intentos if prog else 0,
    }


def _obtener_progreso(sesion, video_id):
    return sesion.scalar(select(Progreso).where(Progreso.video_id == video_id))


def _stats_categoria(sesion, cat):
    ids = select(Video.id).where(Video.categorias.contains(cat))
    total = sesion.scalar(select(func.count()).select_from(Video).where(Video.id.in_(ids)))
    vistos = sesion.scalar(
        select(func.count()).select_from(Progreso).where(Progreso.completado, Progreso.video_id.in_(ids))
    )
    prom = sesion.scalar(
        select(func.avg(Progreso.nota_quiz)).where(Progreso.nota_quiz.isnot(None), Progreso.video_id.in_(ids))
    )
    return total, vistos, prom


def resumen(sesion):
    total = sesion.scalar(select(func.count()).select_from(Video))
    vistos = sesion.scalar(select(func.count()).select_from(Progreso).where(Progreso.completado))
    con_nota = sesion.scalar(select(func.count()).select_from(Progreso).where(Progreso.nota_quiz.isnot(None)))
    prom = sesion.scalar(select(func.avg(Progreso.nota_quiz)).where(Progreso.nota_quiz.isnot(None)))
    return {
        "total": total,
        "vistos": vistos,
        "pendientes": total - vistos,
        "porcentaje": round(vistos * 100 / total, 1) if total else 0.0,
        "quizzes": con_nota,
        "promedio": round(prom, 2) if prom else None,
    }


def por_nivel(sesion):
    filas = []
    for nivel in NIVELES + ["Unspecified"]:
        ids = select(Video.id).where(Video.nivel == nivel)
        total = sesion.scalar(select(func.count()).select_from(Video).where(Video.id.in_(ids)))
        vistos = sesion.scalar(
            select(func.count()).select_from(Progreso).where(Progreso.completado, Progreso.video_id.in_(ids))
        )
        prom = sesion.scalar(
            select(func.avg(Progreso.nota_quiz)).where(Progreso.nota_quiz.isnot(None), Progreso.video_id.in_(ids))
        )
        filas.append({
            "nivel": nivel,
            "videos": total,
            "vistos": vistos,
            "porcentaje": round(vistos * 100 / total, 1) if total else 0.0,
            "promedio": round(prom, 2) if prom else None,
        })
    return filas


def por_categoria(sesion):
    filas = []
    for cat in CATEGORIAS:
        total, vistos, prom = _stats_categoria(sesion, cat)
        filas.append({
            "categoria": cat,
            "videos": total,
            "vistos": vistos,
            "porcentaje": round(vistos * 100 / total, 1) if total else 0.0,
            "promedio": round(prom, 2) if prom else None,
        })
    return sorted(filas, key=lambda f: f["videos"], reverse=True)


def listar_videos(sesion, nivel=None, categoria=None, texto=None, estado=None, limite=None, offset=0):
    q = select(Video)
    if nivel and nivel in NIVELES:
        q = q.where(Video.nivel == nivel)
    if categoria:
        q = q.where(Video.categorias.contains(categoria))
    if texto:
        q = q.where(Video.titulo.ilike(f"%{texto}%"))
    if estado in ("vistos", "pendientes"):
        sub = select(Progreso.video_id).where(Progreso.completado == (estado == "vistos"))
        q = q.where(Video.id.in_(sub))

    total = sesion.scalar(select(func.count()).select_from(q.subquery()))
    q = q.order_by(Video.id).offset(offset)
    if limite:
        q = q.limit(limite)

    videos = sesion.scalars(q).all()
    ids = [v.id for v in videos]
    progresos = {}
    if ids:
        for prog in sesion.scalars(select(Progreso).where(Progreso.video_id.in_(ids))):
            progresos[prog.video_id] = prog
    return {
        "total": total,
        "resultados": [_video_a_dict(v, progresos.get(v.id)) for v in videos],
    }


def obtener_video(sesion, video_id):
    video = sesion.get(Video, video_id)
    if video is None:
        return None
    return _video_a_dict(video, _obtener_progreso(sesion, video_id))


def marcar_visto(sesion, video_id, completado):
    video = sesion.get(Video, video_id)
    if video is None:
        raise ValueError("No existe un video con ese ID")
    prog = _obtener_progreso(sesion, video_id)
    if prog is None:
        prog = Progreso(video_id=video_id)
        sesion.add(prog)
    prog.completado = bool(completado)
    if completado:
        prog.fecha_visto = prog.fecha_visto or date.today()
    sesion.commit()
    return _video_a_dict(video, prog)


def registrar_nota(sesion, video_id, nota):
    video = sesion.get(Video, video_id)
    if video is None:
        raise ValueError("No existe un video con ese ID")
    if not 0 <= nota <= 10:
        raise ValueError("La nota debe estar entre 0 y 10")
    prog = _obtener_progreso(sesion, video_id)
    if prog is None:
        prog = Progreso(video_id=video_id)
        sesion.add(prog)
    prog.nota_quiz = float(nota)
    prog.intentos = (prog.intentos or 0) + 1
    sesion.commit()
    return _video_a_dict(video, prog)


def recomendaciones(sesion, limite_categorias=3, videos_por_categoria=5):
    ranking = []
    for cat in CATEGORIAS:
        total, vistos, prom = _stats_categoria(sesion, cat)
        if not total:
            continue
        ranking.append({
            "categoria": cat,
            "promedio": round(prom, 2) if prom else None,
        })
    ranking.sort(key=lambda r: (r["promedio"] if r["promedio"] is not None else 0.0))

    resultado = []
    ids_vistos = select(Progreso.video_id).where(Progreso.completado)
    for item in ranking[:limite_categorias]:
        q = (
            select(Video)
            .where(Video.categorias.contains(item["categoria"]), Video.id.notin_(ids_vistos))
            .order_by(Video.id)
            .limit(videos_por_categoria)
        )
        pendientes = [_video_a_dict(v) for v in sesion.scalars(q).all()]
        resultado.append({**item, "pendientes": pendientes})
    return resultado
