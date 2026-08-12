@echo off
setlocal
cd /d "%~dp0"
title EngVid Learning Tracker - Setup

echo ============================================
echo   EngVid Learning Tracker - Setup
echo ============================================
echo.

REM 1) Buscar Python (py launcher o python)
set "PYTHON="
where py >nul 2>nul
if %errorlevel%==0 (
    for /f "delims=" %%i in ('py -3 -c "import sys; print(sys.executable)"') do set "PYTHON=%%i"
)
if not defined PYTHON (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON=python"
)

if not defined PYTHON (
    echo [ERROR] Python no encontrado.
    echo.
    echo Instalalo desde: https://www.python.org/downloads/
    echo IMPORTANTE: al instalar, marca la casilla "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo Usando Python: %PYTHON%

REM 2) Verificar que la version sea 3.10 o superior
"%PYTHON%" -c "import sys; sys.exit(0 if sys.version_info.major == 3 and sys.version_info.minor >= 10 else 1)"
if errorlevel 1 (
    echo [ERROR] Se necesita Python 3.10 o superior.
    "%PYTHON%" --version
    echo.
    pause
    exit /b 1
)

echo Version de Python OK.

REM 3) Crear el entorno virtual si no existe
if not exist ".venv" (
    echo.
    echo Creando entorno virtual...
    "%PYTHON%" -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

set "VENV_PY=.venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo [ERROR] El entorno virtual no se creo correctamente.
    pause
    exit /b 1
)

REM 4) Instalar dependencias
echo.
echo Instalando dependencias (la primera vez puede tardar)...
"%VENV_PY%" -m pip install --upgrade pip
"%VENV_PY%" -m pip install -r requirements-web.txt
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    echo        Revisa tu conexion a internet e intenta de nuevo.
    pause
    exit /b 1
)

REM 5) Crear la base de datos
echo.
echo Creando base de datos...
"%VENV_PY%" src\crearBD.py
if errorlevel 1 (
    echo [ERROR] No se pudo crear la base de datos.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Setup completado correctamente.
echo   Ahora ejecuta run.bat para abrir el panel.
echo ============================================
echo.
pause
