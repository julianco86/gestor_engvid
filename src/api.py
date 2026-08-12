import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.consultas import (
    insights,
    listar_videos,
    marcar_visto,
    obtener_video,
    por_categoria,
    por_nivel,
    racha,
    recomendaciones,
    registrar_nota,
    resumen,
)
from src.conexion import obtener_sesion

RUTA_WEB = Path(__file__).parent / "web"

app = FastAPI(
    title="EngVid Learning Tracker",
    description="Dashboard personal de aprendizaje de inglés.",
    version="1.0.0",
)


class VistoBody(BaseModel):
    completado: bool


class NotaBody(BaseModel):
    nota: float


def get_db():
    sesion = obtener_sesion()
    try:
        yield sesion
    finally:
        sesion.close()


@app.get("/api/resumen")
def api_resumen(sesion=Depends(get_db)):
    return resumen(sesion)


@app.get("/api/por-nivel")
def api_por_nivel(sesion=Depends(get_db)):
    return por_nivel(sesion)


@app.get("/api/por-categoria")
def api_por_categoria(sesion=Depends(get_db)):
    return por_categoria(sesion)


@app.get("/api/racha")
def api_racha(sesion=Depends(get_db)):
    return racha(sesion)


@app.get("/api/insights")
def api_insights(sesion=Depends(get_db)):
    return insights(sesion)


@app.get("/api/recomendaciones")
def api_recomendaciones(
    limite_categorias: int = Query(3, ge=1, le=12),
    videos_por_categoria: int = Query(5, ge=1, le=20),
    sesion=Depends(get_db),
):
    return recomendaciones(sesion, limite_categorias, videos_por_categoria)


@app.get("/api/videos")
def api_videos(
    nivel: str | None = None,
    categoria: str | None = None,
    texto: str | None = None,
    estado: str | None = Query(None, pattern="^(vistos|pendientes)$"),
    limite: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sesion=Depends(get_db),
):
    return listar_videos(
        sesion,
        nivel=nivel,
        categoria=categoria,
        texto=texto,
        estado=estado,
        limite=limite,
        offset=offset,
    )


@app.get("/api/videos/{video_id}")
def api_video(video_id: int, sesion=Depends(get_db)):
    video = obtener_video(sesion, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    return video


@app.post("/api/videos/{video_id}/visto")
def api_marcar_visto(video_id: int, body: VistoBody, sesion=Depends(get_db)):
    try:
        return marcar_visto(sesion, video_id, body.completado)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/videos/{video_id}/nota")
def api_registrar_nota(video_id: int, body: NotaBody, sesion=Depends(get_db)):
    try:
        return registrar_nota(sesion, video_id, body.nota)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


app.mount("/static", StaticFiles(directory=RUTA_WEB), name="static")


@app.get("/")
def raiz():
    return FileResponse(RUTA_WEB / "index.html")
