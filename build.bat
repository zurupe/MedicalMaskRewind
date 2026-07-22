@echo off
chcp 65001 >nul
echo.
echo ================================================
echo   Generador de Ejecutable - Detector Mascarillas
echo ================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python no está instalado o no está en PATH
    echo Por favor, instala Python desde https://www.python.org
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

echo ✓ Python encontrado
echo.

REM Instalar PyInstaller si no existe
echo 📦 Instalando PyInstaller...
pip install --upgrade pyinstaller >nul 2>&1

if %errorlevel% neq 0 (
    echo ❌ Error al instalar PyInstaller
    pause
    exit /b 1
)

echo ✓ PyInstaller instalado
echo.

REM Limpiar builds anteriores
if exist build rmdir /s /q build >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1

echo 🔨 Compilando ejecutable...
echo (Este proceso puede tardar 5-10 minutos)
echo.

REM Ejecutar PyInstaller con el spec file
pyinstaller app.spec

if %errorlevel% neq 0 (
    echo.
    echo ❌ Error al compilar el ejecutable
    pause
    exit /b 1
)

echo.
echo ✅ ¡ÉXITO! Ejecutable creado correctamente
echo.
echo 📍 Ubicación del archivo:
echo    dist\DetectorMascarillas.exe
echo.
echo 💾 Ahora puedes:
echo    1. Copiar dist\DetectorMascarillas.exe a tu USB
echo    2. Ejecutarlo en otra computadora con Windows
echo.
echo ⚠️  IMPORTANTE: Si hay archivos adicionales necesarios,
echo    copia también toda la carpeta "dist" completa.
echo.
pause
