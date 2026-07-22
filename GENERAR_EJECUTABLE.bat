@echo off
chcp 65001 >nul
title Generador de Ejecutable - Detector de Mascarillas

cls
echo.
echo ===============================================
echo   GENERADOR AUTOMÁTICO DE EJECUTABLE
echo   Detector de Mascarillas - Versión Portable
echo ===============================================
echo.
echo Verificando Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: Python no está instalado
    echo.
    echo Solución:
    echo   1. Descarga Python desde https://www.python.org
    echo   2. Durante la instalación marca "Add Python to PATH"
    echo   3. Reinicia esta ventana
    echo.
    pause
    exit /b 1
)

echo ✓ Python encontrado
echo.
echo Ejecutando generador automático...
echo.

python generate_executable.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Error durante la generación
    pause
    exit /b 1
)

echo.
echo ✅ ¡Completado! Revisa la carpeta que se acaba de abrir
echo.
pause
