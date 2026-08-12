# 🇬🇧 EngVid Learning Tracker

> **Un gestor administrativo y de análisis de datos para optimizar el aprendizaje de inglés con EngVid.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-Web_Scraping-green)](https://www.selenium.dev/)
[![Status](https://img.shields.io/badge/Status-En_Desarrollo-orange)]()

## 📖 Sobre el Proyecto

**EngVid Learning Tracker** nace de una necesidad personal: llevar un control detallado y analítico del progreso educativo en la plataforma [engvid.com](https://www.engvid.com/). Aunque el sitio ofrece contenido increíble, este proyecto busca añadir una capa de gestión personalizada ("Administrative Manager") para convertir el estudio pasivo en un seguimiento activo basado en datos.

El objetivo es dejar de preguntarse "¿qué video vi ayer?" y empezar a responder "¿en qué categoría estoy fallando más?" o "¿cuál es mi rendimiento semanal?".

## 🚀 Funcionalidades Principales

### ✅ Funcionalidades
- **Extracción Masiva de Datos:** Script automatizado con **Selenium** que recopila el catálogo completo de lecciones (Título, Nivel, Categoría, URL) superando la carga dinámica (JavaScript/Lazy Loading).
- **Limpieza y Procesamiento:** Normalización de niveles (incluye videos con varios niveles) y extracción de categorías con **Pandas**.
- **Base de Datos SQLite:** Esquema con dos tablas: `videos` (catálogo) y `progreso` (historial personal).
- **Tracker de Historial:** Marcar videos como "Visto" / "Pendiente" desde un menú interactivo de consola.
- **Registro de Quizzes:** Ingresar la nota obtenida en cada quiz de lección (0-10) con contador de intentos.
- **Dashboard de Estadísticas:** Porcentaje de videos completados por nivel, promedio de calificaciones por categoría, temas más estudiados.
- **Dashboard Web (FastAPI):** Panel visual interactivo en el navegador con gráficos (Chart.js), filtros de videos, y edición de progreso (marcar visto, notas de quiz).
- **Recomendador:** Sugerencia de videos pendientes en las áreas donde el puntaje de los quizzes es más bajo.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3
* **Web Scraping:** Selenium Webdriver (Manejo de DOM y contenido dinámico).
* **Gestión de Drivers:** Webdriver Manager.
* **Almacenamiento de Datos:** CSV y SQLite (vía SQLAlchemy).
* **Análisis de Datos:** Pandas.

## ⚙️ Instalación y Uso

> **Modo rápido (recomendado):** seguí la [`GUIA_DE_USO.md`](GUIA_DE_USO.md).
> 1. Instalá Python 3.10+ (marcando "Add Python to PATH").
> 2. Doble clic en `setup.bat` (una sola vez).
> 3. Doble clic en `run.bat` — se abre el navegador con el dashboard.

### Modo desarrollador

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/engvid-learning-tracker.git](https://github.com/TU_USUARIO/engvid-learning-tracker.git)
    cd engvid-learning-tracker
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Pipeline de datos:**
    ```bash
    # 1. (Opcional) Extraer el catálogo actual de EngVid con Selenium
    python src/scraper_selenium.py

    # 2. Limpiar y normalizar el CSV
    python src/procesar_data.py

    # 3. Regenerar la base de datos SQLite
    python src/crearBD.py
    ```

4.  **Uso diario:**
    ```bash
    # Menú interactivo: marcar visto/pendiente, registrar notas, ver progreso
    python src/tracker.py

    # Dashboard de estadísticas y recomendaciones
    python src/analyzer.py
    # Solo recomendaciones
    python src/analyzer.py --recomendar

    # Dashboard web (FastAPI) — abrir http://127.0.0.1:8000
    python -m uvicorn src.api:app --reload
    ```

## 📂 Estructura del Proyecto

```text
gestor_engvid/
├── data/                    # Archivos generados (CSV y base de datos)
├── src/                     # Código fuente
│   ├── scraper_selenium.py  # Extracción con Selenium
│   ├── procesar_data.py     # Limpieza y normalización (Pandas)
│   ├── crearBD.py           # Creación de la base SQLite
│   ├── consultas.py         # Queries reutilizables (CLI y web)
│   ├── api.py               # Backend FastAPI (JSON + frontend)
│   ├── web/                 # Frontend estático (HTML/CSS/JS + Chart.js)
│   ├── tracker.py           # CLI: historial y quizzes
│   ├── analyzer.py          # Dashboard de estadísticas y recomendador
│   ├── categorias.py        # Definición de categorías/niveles conocidos
│   ├── conexion.py          # Rutas y conexión a la base de datos
│   └── modelos.py           # Modelos ORM (videos, progreso)
├── requirements.txt          # Dependencias completas (incluye scraper)
├── requirements-web.txt      # Dependencias livianas (solo panel web)
├── setup.bat                 # Instalación automática (Windows)
├── run.bat                   # Arranque del panel (Windows)
├── GUIA_DE_USO.md            # Guía para colaboradoras/es
├── .gitignore
└── README.md
```

## ⚠️Disclaimer Ético

Este proyecto es una herramienta educativa y de uso personal para gestionar el progreso de aprendizaje. No tiene relación oficial con EngVid. El script de scraping respeta los tiempos de carga para no saturar el servidor. Por favor, usa esta herramienta responsablemente.

Desarrollado con 💙 y Python.