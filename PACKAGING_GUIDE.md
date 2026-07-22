# 📦 Guía de Empaquetado - Detector de Mascarillas

## Opción 1: Ejecutable Simple (RECOMENDADO - Más Fácil)

### Paso 1: Preparar el entorno
```powershell
cd d:\Universidad\AplicacionesBasadas\test_yolo
pip install --upgrade pyinstaller
pip install -r requirements.txt
```

### Paso 2: Generar el ejecutable
Opción A - Usando batch (Windows):
```
build.bat
```

Opción B - Usando Python directamente:
```powershell
python build_executable.py
```

Opción C - Usando PyInstaller manualmente:
```powershell
pyinstaller app.spec
```

### Paso 3: Encontrar el ejecutable
- El archivo estará en: `dist\DetectorMascarillas.exe`
- Cópialo a tu USB junto con esta carpeta: `dist\`

### Paso 4: Ejecutar en otra computadora
- Copia la carpeta `dist` a la otra computadora
- Haz doble clic en `DetectorMascarillas.exe`
- ¡Listo! No necesita instalar nada

---

## Opción 2: Instalador Profesional (NSIS)

### Requisitos previos:
1. Instala NSIS desde: https://nsis.sourceforge.io/Download
2. Descarga la rama de desarrollo de NSIS si tienes problemas

### Paso 1: Crear el ejecutable primero
```powershell
pyinstaller app.spec
```

### Paso 2: Generar el instalador
```powershell
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
```

### Paso 3: Distribuir
- El archivo `DetectorMascarillas_Installer.exe` se puede llevar en USB
- Haz doble clic para instalar en otra computadora
- Crea accesos directos automáticamente

---

## ⚠️ PROBLEMAS COMUNES

### Error: "pyinstaller: command not found"
**Solución:**
```powershell
pip install --upgrade pyinstaller
```

### Error: "No module named 'cv2'"
**Solución:**
```powershell
pip install --upgrade opencv-python
pip install -r requirements.txt
```

### El ejecutable es muy grande (>500MB)
**Normal:** PyInstaller incluye todos los modelos y dependencias. Es esperado.

### Antivirus bloquea el ejecutable
**Solución:**
- Es falsa alarma por PyInstaller
- Agrega una excepción en tu antivirus
- O usa el instalador NSIS en su lugar

### El ejecutable se demora en iniciarse
**Normal:** PyInstaller descomprime archivos en memoria en la primera ejecución.

---

## 📋 ESTRUCTURA FINAL EN LA USB

```
flash_usb/
├── DetectorMascarillas.exe       (si usas Opción 1)
├── DetectorMascarillas_Installer.exe  (si usas Opción 2)
└── dist/                         (si usas Opción 1)
    ├── templates/
    ├── static/
    ├── *.pt (modelos)
    └── otros archivos...
```

---

## ✅ VERIFICACIÓN

Después de crear el ejecutable, pruébalo en tu computadora:

1. Abre una terminal en la carpeta `dist`
2. Ejecuta: `DetectorMascarillas.exe`
3. Verifica que se abra el navegador en `http://127.0.0.1:5000`
4. Prueba todas las funcionalidades

---

## 🚀 DISTRIBUCIÓN RECOMENDADA

**Para uso personal/educativo:**
- Opción 1 (ejecutable simple) es más rápida

**Para distribución profesional:**
- Opción 2 (instalador NSIS) se ve más profesional

---

## 💡 NOTAS FINALES

- El ejecutable necesita Windows 64-bit
- Recomendado: Windows 10 o superior
- Requiere al menos 8GB RAM para YOLO
- Comprime con WinRAR si quieres reducir tamaño en la USB

---

Creado: 2026-07-21
