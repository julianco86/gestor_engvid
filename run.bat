@echo off
setlocal
cd /d "%~dp0"
title EngVid Learning Tracker

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Falta el entorno virtual.
    echo Ejecuta primero setup.bat
    echo.
    pause
    exit /b 1
)

.venv\Scripts\python.exe src\iniciar.py
if errorlevel 1 (
    echo.
    echo El servidor se detuvo con un error.
    pause
)
