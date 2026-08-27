# Guía de uso rapida (para colaboradores)

Esta guia explica como poner en marcha el proyecto en tu computadora.

## Requisito: tener Python 3.10+ instalado

1. Entrá a https://www.python.org/downloads/
2. Descargá la ultima version (3.10 o superior).
3. Al instalarla, **marcá la casilla "Add Python to PATH"** antes de hacer clic en "Install Now".
4. Terminá la instalacion.

> En Windows, si el instalador te pregunta "Disable path length limit", marcala tambien.

## Primera vez: instalar el entorno

1. Clona el repositorio (o descarga el ZIP y descomprimilo).
2. Hace **doble clic** en **`setup.bat`**.
   - Se abre una ventana negra (consola). Espera a que termine.
   - Cuando diga "Setup completado correctamente", presiona cualquier tecla.

## Abrir el panel (todas las veces)

1. Hace **doble clic** en **`run.bat`**.
2. Se abre la consola y el navegador con el panel en `http://127.0.0.1:8000`.
3. Cuando termines, cerra la ventana de la consola (o presiona `Ctrl+C`).

## Ingresar al sistema

### Si sos admin

- Usuario: `admin`
- Contraseña: `admin123`

### Si sos usuario nuevo

1. Andá a la pagina de login
2. Hace clic en **"Crear cuenta"**
3. Elegí tu usuario y contraseña
4. Inicia sesion

## Que podes hacer en el panel

- **Resumen:** progreso global (videos vistos, % completado, promedio de notas, racha de estudio).
- **Gráficos:** evolucion de notas de quiz, distribucion de notas.
- **Videos:** buscar y filtrar el catalogo; marcar videos como "visto" y guardar la nota de cada quiz.
- **Recomendaciones:** videos pendientes en las areas donde estas mas debil.
- **Usuarios (solo admin):** ver la lista de usuarios y eliminar usuarios.

## Progreso independiente

Cada usuario tiene su propio progreso. Tus videos vistos, notas y racha estan separados de los demas usuarios.

## Como se guardan tus datos

- Tu progreso queda en `data/engvid_database.db`, solo en tu computadora.
- Ese archivo no se sube a GitHub (esta ignorado a proposito).
- Cada usuario tiene su propio progreso en la misma base de datos.

## Actualizar videos

Si EngVid publica nuevos videos:

1. Correr el scraper: `python src/scraper_selenium.py`
2. Procesar el CSV: `python src/procesar_data.py`
3. Push a GitHub: `git add . && git commit -m "Actualizar videos" && git push`

## Solucion de problemas

| Problema | Solucion |
|---|---|
| `run.bat` dice "Falta el entorno virtual" | Ejecuta primero `setup.bat` |
| `setup.bat` dice "Python no encontrado" | Instala Python marcando "Add to PATH" y reinicia |
| El navegador no se abre solo | Abre manualmente `http://127.0.0.1:8000` |
| El puerto 8000 esta ocupado | Cierra otros programas o consolas que usen ese puerto |
| Error despues de un `git pull` | Ejecuta `setup.bat` de nuevo |
