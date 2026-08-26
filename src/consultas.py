import re
from datetime import date, timedelta

from sqlalchemy import func, select

from src.categorias import CATEGORIAS, NIVELES, NIVELES_TODOS
from src.modelos import Progreso, Video


def _escapar_like(texto):
    return texto.replace("%", "\\%").replace("_", "\\_")


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


def _obtener_progreso(sesion, video_id, user_id):
    return sesion.scalar(
        select(Progreso).where(Progreso.video_id == video_id, Progreso.user_id == user_id)
    )


def _stats_categoria(sesion, cat, user_id):
    ids = select(Video.id).where(Video.categorias.contains(cat))
    total = sesion.scalar(select(func.count()).select_from(Video).where(Video.id.in_(ids)))
    vistos = sesion.scalar(
        select(func.count()).select_from(Progreso).where(
            Progreso.completado, Progreso.user_id == user_id, Progreso.video_id.in_(ids)
        )
    )
    prom = sesion.scalar(
        select(func.avg(Progreso.nota_quiz)).where(
            Progreso.nota_quiz.isnot(None), Progreso.user_id == user_id, Progreso.video_id.in_(ids)
        )
    )
    return total, vistos, prom


def resumen(sesion, user_id):
    total = sesion.scalar(select(func.count()).select_from(Video))
    vistos = sesion.scalar(
        select(func.count()).select_from(Progreso).where(Progreso.completado, Progreso.user_id == user_id)
    )
    con_nota = sesion.scalar(
        select(func.count()).select_from(Progreso).where(
            Progreso.nota_quiz.isnot(None), Progreso.user_id == user_id
        )
    )
    prom = sesion.scalar(
        select(func.avg(Progreso.nota_quiz)).where(
            Progreso.nota_quiz.isnot(None), Progreso.user_id == user_id
        )
    )
    return {
        "total": total,
        "vistos": vistos,
        "pendientes": total - vistos,
        "porcentaje": round(vistos * 100 / total, 1) if total else 0.0,
        "quizzes": con_nota,
        "promedio": round(prom, 2) if prom is not None else None,
    }


def por_nivel(sesion, user_id):
    filas = []
    for nivel in NIVELES_TODOS:
        ids = select(Video.id).where(Video.nivel == nivel)
        total = sesion.scalar(select(func.count()).select_from(Video).where(Video.id.in_(ids)))
        vistos = sesion.scalar(
            select(func.count()).select_from(Progreso).where(
                Progreso.completado, Progreso.user_id == user_id, Progreso.video_id.in_(ids)
            )
        )
        prom = sesion.scalar(
            select(func.avg(Progreso.nota_quiz)).where(
                Progreso.nota_quiz.isnot(None), Progreso.user_id == user_id, Progreso.video_id.in_(ids)
            )
        )
        filas.append({
            "nivel": nivel,
            "videos": total,
            "vistos": vistos,
            "porcentaje": round(vistos * 100 / total, 1) if total else 0.0,
            "promedio": round(prom, 2) if prom is not None else None,
        })
    return filas


def por_categoria(sesion, user_id):
    filas = []
    for cat in CATEGORIAS:
        total, vistos, prom = _stats_categoria(sesion, cat, user_id)
        filas.append({
            "categoria": cat,
            "videos": total,
            "vistos": vistos,
            "porcentaje": round(vistos * 100 / total, 1) if total else 0.0,
            "promedio": round(prom, 2) if prom is not None else None,
        })
    return sorted(filas, key=lambda f: f["videos"], reverse=True)


def listar_videos(sesion, user_id, nivel=None, categoria=None, texto=None, estado=None, limite=None, offset=0):
    q = select(Video)
    if nivel and nivel in NIVELES_TODOS:
        q = q.where(Video.nivel == nivel)
    if categoria:
        q = q.where(Video.categorias.contains(_escapar_like(categoria)))
    if texto:
        q = q.where(Video.titulo.ilike(f"%{_escapar_like(texto)}%"))
    if estado == "vistos":
        ids_vistos = select(Progreso.video_id).where(Progreso.completado, Progreso.user_id == user_id)
        q = q.where(Video.id.in_(ids_vistos))
    elif estado == "pendientes":
        ids_vistos = select(Progreso.video_id).where(Progreso.completado, Progreso.user_id == user_id)
        q = q.where(Video.id.notin_(ids_vistos))

    total = sesion.scalar(select(func.count()).select_from(q.subquery()))
    q = q.order_by(Video.id).offset(offset)
    if limite:
        q = q.limit(limite)

    videos = sesion.scalars(q).all()
    ids = [v.id for v in videos]
    progresos = {}
    if ids:
        for prog in sesion.scalars(
            select(Progreso).where(Progreso.video_id.in_(ids), Progreso.user_id == user_id)
        ):
            progresos[prog.video_id] = prog
    return {
        "total": total,
        "resultados": [_video_a_dict(v, progresos.get(v.id)) for v in videos],
    }


def obtener_video(sesion, video_id, user_id):
    video = sesion.get(Video, video_id)
    if video is None:
        return None
    return _video_a_dict(video, _obtener_progreso(sesion, video_id, user_id))


def marcar_visto(sesion, video_id, completado, user_id):
    video = sesion.get(Video, video_id)
    if video is None:
        raise ValueError("No existe un video con ese ID")
    prog = _obtener_progreso(sesion, video_id, user_id)
    if prog is None:
        prog = Progreso(video_id=video_id, user_id=user_id)
        sesion.add(prog)
    prog.completado = bool(completado)
    if completado:
        prog.fecha_visto = prog.fecha_visto or date.today()
    sesion.commit()
    return _video_a_dict(video, prog)


def registrar_nota(sesion, video_id, nota, user_id):
    video = sesion.get(Video, video_id)
    if video is None:
        raise ValueError("No existe un video con ese ID")
    if not 0 <= nota <= 10:
        raise ValueError("La nota debe estar entre 0 y 10")
    prog = _obtener_progreso(sesion, video_id, user_id)
    if prog is None:
        prog = Progreso(video_id=video_id, user_id=user_id)
        sesion.add(prog)
    prog.nota_quiz = float(nota)
    prog.fecha_nota = date.today()
    prog.intentos = (prog.intentos or 0) + 1
    sesion.commit()
    return _video_a_dict(video, prog)


def recomendaciones(sesion, user_id, limite_categorias=3, videos_por_categoria=5):
    ranking = []
    for cat in CATEGORIAS:
        total, vistos, prom = _stats_categoria(sesion, cat, user_id)
        if not total:
            continue
        ranking.append({
            "categoria": cat,
            "promedio": round(prom, 2) if prom is not None else None,
        })
    ranking.sort(key=lambda r: (r["promedio"] if r["promedio"] is not None else 0.0))

    resultado = []
    ids_vistos = select(Progreso.video_id).where(Progreso.completado, Progreso.user_id == user_id)
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


def racha(sesion, user_id):
    fechas = sesion.scalars(
        select(Progreso.fecha_visto).where(
            Progreso.completado, Progreso.user_id == user_id, Progreso.fecha_visto.isnot(None)
        )
    ).all()
    dias = sorted({d if isinstance(d, date) else date.fromisoformat(str(d)) for d in fechas})
    if not dias:
        return {"actual": 0, "record": 0, "dias_activos": 0}

    dias_set = set(dias)
    hoy = date.today()
    actual = 0
    cursor = hoy if hoy in dias_set else hoy - timedelta(days=1)
    while cursor in dias_set:
        actual += 1
        cursor -= timedelta(days=1)

    record = 0
    seguidos = 0
    previo = None
    for d in dias:
        seguidos = seguidos + 1 if previo is None or (d - previo).days == 1 else 1
        record = max(record, seguidos)
        previo = d

    return {"actual": actual, "record": record, "dias_activos": len(dias)}


def evolucion_notas(sesion, user_id):
    filas = (
        sesion.execute(
            select(Progreso.fecha_nota, func.avg(Progreso.nota_quiz), func.count())
            .where(
                Progreso.nota_quiz.isnot(None),
                Progreso.user_id == user_id,
                Progreso.fecha_nota.isnot(None),
            )
            .group_by(Progreso.fecha_nota)
            .order_by(Progreso.fecha_nota)
        )
        .all()
    )
    return [
        {"fecha": str(f.fecha_nota), "promedio": round(f[1], 2), "cantidad": f[2]}
        for f in filas
    ]


def distribucion_notas(sesion, user_id):
    rangos = [(0, 2), (2, 4), (4, 6), (6, 8), (8, 10.01)]
    etiquetas = ["0-2", "2-4", "4-6", "6-8", "8-10"]
    resultados = []
    for etiqueta, (inf, sup) in zip(etiquetas, rangos):
        cant = sesion.scalar(
            select(func.count()).select_from(Progreso).where(
                Progreso.nota_quiz.isnot(None),
                Progreso.user_id == user_id,
                Progreso.nota_quiz >= inf,
                Progreso.nota_quiz < sup,
            )
        )
        resultados.append({"rango": etiqueta, "cantidad": cant})
    return resultados


def reset_progreso(sesion, user_id):
    sesion.execute(Progreso.__table__.delete().where(Progreso.user_id == user_id))
    sesion.commit()


def insights(sesion, user_id):
    r = resumen(sesion, user_id)
    lineas = []
    if r["vistos"] == 0:
        lineas.append("Todavía no marcaste ningún video como visto. ¡Marcá tu primer video y arrancá la racha!")
        return lineas

    con_promedio = [c for c in por_categoria(sesion, user_id) if c["promedio"] is not None]
    if con_promedio:
        debil = min(con_promedio, key=lambda c: c["promedio"])
        fuerte = max(con_promedio, key=lambda c: c["promedio"])
        lineas.append(f"Área más débil: {debil['categoria']} (promedio {debil['promedio']:.2f})")
        if fuerte["categoria"] != debil["categoria"]:
            lineas.append(f"Tu mejor área: {fuerte['categoria']} (promedio {fuerte['promedio']:.2f})")

    rch = racha(sesion, user_id)
    if rch["actual"] >= 2:
        lineas.append(f"¡Vas {rch['actual']} días seguidos de estudio! Seguí así.")
    elif rch["actual"] == 1:
        lineas.append("Llevás 1 día de racha. ¡Volvé mañana para mantenerla!")

    return lineas
