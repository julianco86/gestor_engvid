import os
import secrets

import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import select

from src.conexion import obtener_sesion
from src.modelos import Usuario

SECRET_KEY = os.environ.get("SESSION_SECRET", secrets.token_hex(32))
serializer = URLSafeTimedSerializer(SECRET_KEY)
SESSION_MAX_AGE = 86400 * 7


def hashear_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password, hash_password):
    return bcrypt.checkpw(password.encode("utf-8"), hash_password.encode("utf-8"))


def crear_usuario(username, password):
    sesion = obtener_sesion()
    try:
        existente = sesion.scalar(select(Usuario).where(Usuario.username == username))
        if existente:
            raise ValueError(f"Ya existe el usuario '{username}'")
        usuario = Usuario(username=username, hash_password=hashear_password(password))
        sesion.add(usuario)
        sesion.commit()
        return usuario
    finally:
        sesion.close()


def autenticar_usuario(username, password):
    sesion = obtener_sesion()
    try:
        usuario = sesion.scalar(select(Usuario).where(Usuario.username == username))
        if usuario and verificar_password(password, usuario.hash_password):
            return usuario
        return None
    finally:
        sesion.close()


def crear_token(user_id):
    return serializer.dumps({"user_id": user_id})


def verificar_token(token):
    try:
        data = serializer.loads(token, max_age=SESSION_MAX_AGE)
        return data.get("user_id")
    except (BadSignature, SignatureExpired):
        return None


def obtener_rol(user_id):
    sesion = obtener_sesion()
    try:
        usuario = sesion.get(Usuario, user_id)
        return usuario.rol if usuario else None
    finally:
        sesion.close()


def es_admin(user_id):
    return obtener_rol(user_id) == "admin"


def listar_usuarios():
    sesion = obtener_sesion()
    try:
        usuarios = sesion.scalars(select(Usuario)).all()
        return [{"id": u.id, "username": u.username, "rol": u.rol} for u in usuarios]
    finally:
        sesion.close()


def eliminar_usuario(user_id):
    sesion = obtener_sesion()
    try:
        usuario = sesion.get(Usuario, user_id)
        if usuario is None:
            raise ValueError("Usuario no encontrado")
        if usuario.username == "admin":
            raise ValueError("No se puede eliminar el usuario admin")
        sesion.delete(usuario)
        sesion.commit()
    finally:
        sesion.close()
