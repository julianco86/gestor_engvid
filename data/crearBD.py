import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
import os

# 1. MANEJO DE RUTAS (DINÁMICO)
# Obtenemos la carpeta donde vive este script (es decir, la carpeta 'data')
RUTA_CARPETA_DATA = os.path.dirname(__file__)

# Construimos las rutas completas
RUTA_DB = os.path.join(RUTA_CARPETA_DATA, "engvid_database.db")
RUTA_CSV = os.path.join(RUTA_CARPETA_DATA, 'engvid_completo_limpio.csv')

# 2. CONFIGURACIÓN DE SQLALCHEMY
# Ahora el engine usa la ruta completa hacia la carpeta data
engine = create_engine(f"sqlite:///{RUTA_DB}", echo=False)
Base = declarative_base()

# --- Definición de Modelos (Sin cambios) ---
class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    titulo = Column(String)
    detalles = Column(String)
    url = Column(String)
    nivel = Column(String)

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    email = Column(String, unique=True)

class Progreso(Base):
    __tablename__ = 'progreso'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    video_id = Column(Integer, ForeignKey('videos.id'))
    completado = Column(Boolean, default=True)

# 3. LÓGICA DE CARGA
def cargar_csv_a_db():
    # Creamos las tablas justo antes de cargar
    Base.metadata.create_all(engine)
    
    try:
        # Leemos el CSV usando la ruta calculada
        df = pd.read_csv(RUTA_CSV)
        
        # Normalizamos nombres de columnas
        df.columns = [c.lower() for c in df.columns]
        
        # Insertar en la base de datos
        df.to_sql('videos', con=engine, if_exists='replace', index=False)
        
        print(f"✅ Base de datos creada en: {RUTA_DB}")
        print(f"✅ Se han cargado {len(df)} videos desde: {RUTA_CSV}")
        
    except FileNotFoundError:
        print(f"❌ ERROR: No se encontró el archivo en {RUTA_CSV}")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    cargar_csv_a_db()