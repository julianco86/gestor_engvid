# 🚀 Guía de uso rápida (para colaboradoras/es)

Esta guía explica cómo poner en marcha el proyecto en tu computadora sin tocar
nada de código ni comandos complicados.

## Requisito único: tener Python instalado

1. Entrá a https://www.python.org/downloads/
2. Descargá la última versión (3.10 o superior).
3. Al instalarla, **marcá la casilla "Add Python to PATH"** antes de hacer clic en "Install Now".
4. Terminá la instalación.

> 💡 En Windows, si el instalador te pregunta "Disable path length limit", marcá esa
> opción también (es recomendable).

## Puesta en marcha (solo la primera vez)

1. Cloná el repositorio (o descargá el ZIP y descomprimilo).
2. Hacé **doble clic** en **`setup.bat`**.
   - Se abre una ventana negra (consola). Esperá a que termine.
   - Cuando diga "Setup completado correctamente", presioná cualquier tecla.
   - Si apareciera algún `[ERROR]`, leelo y avisá: suele ser Python no instalado o
     sin "Add to PATH".

## Abrir el panel (todas las veces que quieras usarlo)

1. Hacé **doble clic** en **`run.bat`**.
2. Se abre la consola y, unos segundos después, **se abre tu navegador** con el
   panel en `http://127.0.0.1:8000`.
3. Cuando termines, cerrá la ventana de la consola (o presioná `Ctrl+C`).

## Qué podés hacer en el panel

- **Resumen:** tu progreso global (videos vistos, % completado, promedio de notas).
- **Gráficos:** rendimiento por nivel y por categoría.
- **Videos:** buscá y filtrá el catálogo; marcá videos como "visto" y guardá la
  nota de cada quiz.
- **Recomendaciones:** videos pendientes en las áreas donde tenés el promedio más bajo.

## Cómo se guardan tus datos

- Tu progreso personal queda en el archivo `data/engvid_database.db`, **solo en tu
  computadora**.
- Ese archivo **no se sube a GitHub** (está ignorado a propósito): cada persona
  tiene su propio progreso, y el catálogo de videos vive en el repositorio.

## Cuando lleguen actualizaciones (git pull)

- Si otra persona sube cambios al repositorio, hacé `git pull`.
- Si los cambios tocaron la base de datos, la consola mostrará algún error al
  abrir el panel; en ese caso, ejecutá de nuevo **`setup.bat`** (recrea la base,
  no borra tu historial si el catálogo no cambió).

## Solución de problemas

| Problema | Solución |
|---|---|
| `run.bat` dice "Falta el entorno virtual" | Ejecutá primero `setup.bat` |
| `setup.bat` dice "Python no encontrado" | Instalá Python marcando "Add to PATH" y reiniciá |
| El navegador no se abre solo | Abrí manualmente `http://127.0.0.1:8000` en tu navegador |
| El puerto 8000 está ocupado | Cerrá otros programas o consolas que usen ese puerto |
| Error raro después de un `git pull` | Ejecutá `setup.bat` de nuevo |
