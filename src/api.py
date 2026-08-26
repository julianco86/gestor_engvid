import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from src.auth import (
    autenticar_usuario,
    crear_token,
    crear_usuario,
    eliminar_usuario,
    es_admin,
    listar_usuarios,
    obtener_rol,
    verificar_token,
)
from src.consultas import (
    distribucion_notas,
    evolucion_notas,
    insights,
    listar_videos,
    marcar_visto,
    obtener_video,
    por_categoria,
    por_nivel,
    racha,
    recomendaciones,
    registrar_nota,
    reset_progreso,
    resumen,
)
from src.conexion import obtener_sesion

RUTA_WEB = Path(__file__).parent / "web"

app = FastAPI(
    title="EngVid Learning Tracker",
    description="Dashboard personal de aprendizaje de inglés.",
    version="1.0.0",
)

COOKIE_NAME = "session"
COOKIE_MAX_AGE = 86400 * 7


class VistoBody(BaseModel):
    completado: bool


class NotaBody(BaseModel):
    nota: float


class RegistroBody(BaseModel):
    username: str
    password: str


def get_db():
    sesion = obtener_sesion()
    try:
        yield sesion
    finally:
        sesion.close()


def get_usuario_id(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    return verificar_token(token)


def requiere_sesion(request: Request):
    user_id = get_usuario_id(request)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Sesión no válida")
    return user_id


@app.get("/login", response_class=HTMLResponse)
def pagina_login(request: Request):
    if get_usuario_id(request) is not None:
        return RedirectResponse("/", status_code=302)
    html = (RUTA_WEB / "login.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.post("/login")
def login_post(username: str = Form(...), password: str = Form(...)):
    usuario = autenticar_usuario(username, password)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = crear_token(usuario.id)
    response = JSONResponse(content={"ok": True})
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return response


@app.post("/logout")
def logout_post():
    response = JSONResponse(content={"ok": True})
    response.delete_cookie(COOKIE_NAME)
    return response


@app.get("/api/rol")
def api_obtener_rol(user_id: int = Depends(requiere_sesion)):
    rol = obtener_rol(user_id)
    return {"rol": rol}


@app.post("/registro")
def registro_post(body: RegistroBody):
    try:
        crear_usuario(body.username, body.password)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
def raiz(request: Request):
    if get_usuario_id(request) is None:
        return RedirectResponse("/login", status_code=302)
    return FileResponse(RUTA_WEB / "index.html")


@app.get("/api/resumen")
def api_resumen(user_id: int = Depends(requiere_sesion), sesion=Depends(get_db)):
    try:
        return resumen(sesion, user_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


@app.get("/api/por-nivel")
def api_por_nivel(user_id: int = Depends(requiere_sesion), sesion=Depends(get_db)):
    try:
        return por_nivel(sesion, user_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


@app.get("/api/por-categoria")
def api_por_categoria(user_id: int = Depends(requiere_sesion), sesion=Depends(get_db)):
    try:
        return por_categoria(sesion, user_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


@app.get("/api/racha")
def api_racha(user_id: int = Depends(requiere_sesion), sesion=Depends(get_db)):
    try:
        return racha(sesion, user_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


@app.get("/api/insights")
def api_insights(user_id: int = Depends(requiere_sesion), sesion=Depends(get_db)):
    try:
        return insights(sesion, user_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


@app.get("/api/quiz-stats")
def api_quiz_stats(user_id: int = Depends(requiere_sesion), sesion=Depends(get_db)):
    try:
        return {
            "evolucion": evolucion_notas(sesion, user_id),
            "distribucion": distribucion_notas(sesion, user_id),
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


@app.get("/api/recomendaciones")
def api_recomendaciones(
    limite_categorias: int = Query(3, ge=1, le=12),
    videos_por_categoria: int = Query(5, ge=1, le=20),
    user_id: int = Depends(requiere_sesion),
    sesion=Depends(get_db),
):
    return recomendaciones(sesion, user_id, limite_categorias, videos_por_categoria)


@app.get("/api/videos")
def api_videos(
    nivel: str | None = None,
    categoria: str | None = None,
    texto: str | None = None,
    estado: str | None = Query(None, pattern="^(vistos|pendientes)$"),
    limite: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(requiere_sesion),
    sesion=Depends(get_db),
):
    return listar_videos(
        sesion,
        user_id,
        nivel=nivel,
        categoria=categoria,
        texto=texto,
        estado=estado,
        limite=limite,
        offset=offset,
    )


@app.get("/api/videos/{video_id}")
def api_video(video_id: int, user_id: int = Depends(requiere_sesion), sesion=Depends(get_db)):
    video = obtener_video(sesion, video_id, user_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    return video


@app.post("/api/videos/{video_id}/visto")
def api_marcar_visto(
    video_id: int,
    body: VistoBody,
    user_id: int = Depends(requiere_sesion),
    sesion=Depends(get_db),
):
    try:
        return marcar_visto(sesion, video_id, body.completado, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


@app.post("/api/videos/{video_id}/nota")
def api_registrar_nota(
    video_id: int,
    body: NotaBody,
    user_id: int = Depends(requiere_sesion),
    sesion=Depends(get_db),
):
    try:
        return registrar_nota(sesion, video_id, body.nota, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


@app.post("/api/reset-progreso")
def api_reset_progreso(user_id: int = Depends(requiere_sesion), sesion=Depends(get_db)):
    try:
        reset_progreso(sesion, user_id)
        return {"ok": True}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


@app.get("/api/usuarios")
def api_listar_usuarios(user_id: int = Depends(requiere_sesion)):
    return listar_usuarios()


@app.delete("/api/usuarios/{usuario_id}")
def api_eliminar_usuario(usuario_id: int, user_id: int = Depends(requiere_sesion)):
    if not es_admin(user_id):
        raise HTTPException(status_code=403, detail="Solo administradores")
    try:
        eliminar_usuario(usuario_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


app.mount("/static", StaticFiles(directory=RUTA_WEB), name="static")
