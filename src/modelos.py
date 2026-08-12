from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    detalles = Column(String)
    url = Column(String)
    nivel = Column(String)
    niveles = Column(String)
    categorias = Column(String)


class Progreso(Base):
    __tablename__ = "progreso"

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey("videos.id"), unique=True, nullable=False)
    completado = Column(Boolean, default=False)
    fecha_visto = Column(Date)
    nota_quiz = Column(Float)
    intentos = Column(Integer, default=0)
