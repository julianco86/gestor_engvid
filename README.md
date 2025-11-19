# 🇬🇧 EngVid Learning Tracker

> **Un gestor administrativo y de análisis de datos para optimizar el aprendizaje de inglés con EngVid.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-Web_Scraping-green)](https://www.selenium.dev/)
[![Status](https://img.shields.io/badge/Status-En_Desarrollo-orange)]()

## 📖 Sobre el Proyecto

**EngVid Learning Tracker** nace de una necesidad personal: llevar un control detallado y analítico del progreso educativo en la plataforma [engvid.com](https://www.engvid.com/). Aunque el sitio ofrece contenido increíble, este proyecto busca añadir una capa de gestión personalizada ("Administrative Manager") para convertir el estudio pasivo en un seguimiento activo basado en datos.

El objetivo es dejar de preguntarse "¿qué video vi ayer?" y empezar a responder "¿en qué categoría estoy fallando más?" o "¿cuál es mi rendimiento semanal?".

## 🚀 Funcionalidades Principales

### ✅ Actuales (MVP)
- **Extracción Masiva de Datos:** Script automatizado con **Selenium** que recopila el catálogo completo de lecciones (Título, Nivel, Categoría, URL) superando la carga dinámica (JavaScript/Lazy Loading).
- **Exportación Estructurada:** Generación automática de bases de datos en formato `.csv` para su posterior análisis.

### 🌟 Hoja de Ruta (Roadmap)
- [ ] **Tracker de Historial:** Marcar videos como "Visto" / "Pendiente".
- [ ] **Registro de Quizzes:** Sistema para ingresar y almacenar la nota obtenida en cada quiz de lección.
- [ ] **Dashboard de Estadísticas:** Análisis visual de datos:
    - Porcentaje de videos completados por nivel.
    - Promedio de calificaciones en quizzes.
    - Temas más estudiados vs. temas olvidados.
- [ ] **Recomendador:** Sugerencia de videos basada en áreas donde el puntaje de los quizzes sea bajo.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3
* **Web Scraping:** Selenium Webdriver (Manejo de DOM y contenido dinámico).
* **Gestión de Drivers:** Webdriver Manager.
* **Almacenamiento de Datos:** CSV (Fase inicial) / SQLite (Planeado).
* **Análisis de Datos:** Pandas (Planeado).

## ⚙️ Instalación y Uso

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/engvid-learning-tracker.git](https://github.com/TU_USUARIO/engvid-learning-tracker.git)
    cd engvid-learning-tracker
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install selenium webdriver-manager pandas
    ```

3.  **Ejecutar el Scraper:**
    Este script abrirá el navegador, extraerá el catálogo actual de EngVid y generará el archivo maestro.
    ```bash
    python scraper.py
    ```

4.  **Consultar los datos:**
    Se generará un archivo `engvid_completo.csv` en la raíz del proyecto.

## 📂 Estructura del Proyecto

```text
engvid-learning-tracker/
├── data/                # Archivos CSV generados
├── src/                 # Código fuente
│   ├── scraper.py       # Lógica de extracción con Selenium
│   └── analyzer.py      # (Próximamente) Lógica de estadísticas
├── .gitignore
└── README.md