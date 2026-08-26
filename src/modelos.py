from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

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

    progreso = relationship("Progreso", uselist=False, back_populates="video", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Video(id={self.id}, titulo='{self.titulo}')>"


class Progreso(Base):
    __tablename__ = "progreso"

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    completado = Column(Boolean, default=False)
    fecha_visto = Column(Date)
    fecha_nota = Column(Date)
    nota_quiz = Column(Float)
    intentos = Column(Integer, default=0)

    video = relationship("Video", back_populates="progreso")

    def __repr__(self):
        return f"<Progreso(video_id={self.video_id}, user_id={self.user_id}, completado={self.completado})>"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hash_password = Column(String, nullable=False)
    rol = Column(String, default="usuario", nullable=False)

    def __repr__(self):
        return f"<Usuario(username='{self.username}', rol='{self.rol}')>"
