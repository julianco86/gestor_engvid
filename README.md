# EngVid Learning Tracker

Dashboard personal para trackear tu progreso de aprendizaje de inglés con [EngVid](https://www.engvid.com/).

## Inicio rápido

```bash
# 1. Clonar el repo
git clone https://github.com/julianco86/gestor_engvid.git
cd gestor_engvid

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements-web.txt

# 4. Crear la base de datos
python src/crearBD.py

# 5. Iniciar el servidor
python src/iniciar.py
```

El navegador se abre automáticamente en `http://127.0.0.1:8000`.

## Credenciales por defecto

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador |

Los usuarios nuevos se registran desde la página de login.

## Qué hace cada usuario

| Función | Admin | Usuario normal |
|---|---|---|
| Ver videos, métricas, gráficos | ✅ | ✅ |
| Marcar videos como vistos | ✅ | ✅ |
| Guardar notas de quiz | ✅ | ✅ |
| Resetear su progreso | ✅ | ✅ |
| Ver lista de usuarios | ✅ | ❌ |
| Eliminar usuarios | ✅ | ❌ |

Cada usuario tiene su progreso independiente.

## Deploy con Docker

```bash
# Build
docker build -t engvid-tracker .

# Run
docker run -p 8000:8000 engvid-tracker
```

## Deploy en Render

1. Subir el código a GitHub
2. En [render.com](https://render.com): New → Web Service → Docker
3. Puerto: `8000`
4. La URL pública queda tipo `https://engvid-tracker.onrender.com`

**Nota:** la DB SQLite se regenera en cada reinicio del contenedor.

## Estructura del proyecto

```text
gestor_engvid/
├── data/
│   ├── engvid_completo.csv          # CSV crudo del scraper
│   └── engvid_completo_limpio.csv   # CSV procesado
├── src/
│   ├── api.py           # Backend FastAPI
│   ├── auth.py          # Autenticación y sesiones
│   ├── modelos.py       # Modelos SQLAlchemy (Video, Progreso, Usuario)
│   ├── consultas.py     # Queries de la base de datos
│   ├── conexion.py      # Conexión SQLite
│   ├── crearBD.py       # Creación y migraciones de la DB
│   ├── categorias.py    # Definición de niveles y categorías
│   ├── iniciar.py       # Punto de entrada del servidor
│   ├── scraper_selenium.py  # Scraper de EngVid (Selenium)
│   ├── procesar_data.py     # Limpieza de CSV (Pandas)
│   └── web/
│       ├── index.html   # Dashboard principal
│       ├── login.html   # Página de login
│       ├── app.js       # Lógica del frontend
│       └── style.css    # Estilos (dark theme)
├── Dockerfile
├── .dockerignore
├── requirements-web.txt  # Dependencias del panel web
├── setup.bat             # Instalación automática (Windows)
└── run.bat               # Arranque del panel (Windows)
```

## Actualizar videos de EngVid

```bash
# 1. Correr el scraper (requiere Chrome)
python src/scraper_selenium.py

# 2. Procesar el CSV
python src/procesar_data.py

# 3. Push a GitHub (Render redeploya solo)
git add . && git commit -m "Actualizar videos" && git push
```
