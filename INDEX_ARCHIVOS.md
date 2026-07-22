# 📦 ÍNDICE DE ARCHIVOS DE EMPAQUETADO

## 🚀 PARA INICIAR (ELIGE UNO)

### ⭐ **OPCIÓN 1: Lo más fácil** 
```
GENERAR_EJECUTABLE.bat
```
- Haz doble clic
- Espera 5-10 minutos
- Se abre carpeta con todo listo
- **RECOMENDADO PARA USUARIOS NO TÉCNICOS**

### ⭐ **OPCIÓN 2: Por terminal** 
```
python generate_executable.py
```
- Terminal → tipo este comando
- Genera la misma carpeta lista para USB
- **RECOMENDADO SI ENTIENDES DE TERMINAL**

### 📄 **OPCIÓN 3: Build tradicional**
```
build.bat
```
- Compilation tradicional con PyInstaller
- Requiere más conocimiento
- Menos automatizado

---

## 📋 ARCHIVOS PRINCIPALES

### 🔧 **Scripts de Empaquetado**

| Archivo | Descripción |
|---------|-------------|
| `GENERAR_EJECUTABLE.bat` | ⭐ Script batch para generar todo automáticamente |
| `generate_executable.py` | Generador automático (Python) |
| `build_executable.py` | Script alternativo de compilación |
| `build.bat` | Batch tradicional con PyInstaller |

### ⚙️ **Configuración**

| Archivo | Descripción |
|---------|-------------|
| `app.spec` | Configuración detallada de PyInstaller |
| `path_utils.py` | Utilidades para manejar rutas en ejecutable |

### 🎁 **Instalador Profesional (Opcional)**

| Archivo | Descripción |
|---------|-------------|
| `installer.nsi` | Script NSIS para crear instalador .exe profesional |

### 📚 **Documentación**

| Archivo | Descripción |
|---------|-------------|
| `INSTRUCCIONES_SIMPLIFICADAS.md` | ⭐ Guía simple en español |
| `PACKAGING_GUIDE.md` | Guía completa con todas las opciones |
| `INDEX_ARCHIVOS.md` | Este archivo |

---

## 🎯 FLUJO DE TRABAJO RECOMENDADO

### Paso 1: Preparación
```bash
# En terminal (opcional)
pip install --upgrade pyinstaller
pip install -r requirements.txt
```

### Paso 2: Generar ejecutable
```
Haz doble clic en: GENERAR_EJECUTABLE.bat
```

### Paso 3: Resultado
- Carpeta `USB_Listo` se abre automáticamente
- Contiene `DetectorMascarillas.exe` + todos los archivos necesarios

### Paso 4: Llevar en USB
- Copia `USB_Listo` a una USB flash
- Lleva la USB a otra computadora

### Paso 5: Ejecutar
- Haz doble clic en `DetectorMascarillas.exe`
- ¡Listo!

---

## 📊 TAMAÑO DE ARCHIVOS

| Archivo | Tamaño Aprox | Notas |
|---------|-------------|-------|
| DetectorMascarillas.exe | 500 MB | Incluye Python + modelos YOLO |
| Carpeta dist/ | 550 MB | Todos los archivos empaquetados |
| Carpeta USB_Listo/ | 500 MB | Lista para copiar a USB |

---

## ✅ ANTES DE COMPARTIR

- [ ] Prueba el .exe en tu computadora
- [ ] Verifica que se abra en `http://127.0.0.1:5000`
- [ ] Prueba todas las funcionalidades
- [ ] Elimina archivos sensibles (groq_key.txt si existe)
- [ ] Copia carpeta completa a USB (no solo el .exe)

---

## 🔍 SOLUCIÓN DE PROBLEMAS

| Problema | Solución |
|----------|----------|
| "pyinstaller no encontrado" | `pip install pyinstaller` |
| "No se abre el .exe" | Instala Visual C++ Redistributable |
| "Antivirus lo bloquea" | Agrega excepción al antivirus |
| "Se demora mucho" | Normal en primera ejecución |
| "El ejecutable es muy grande" | Esto es normal con PyInstaller |

---

## 💡 INFORMACIÓN TÉCNICA

### ¿Qué incluye el ejecutable?
- Python 3.x empotrado
- Todas las librerías (Flask, OpenCV, Ultralytics, etc.)
- Modelos YOLO preentrenados (.pt)
- Templates HTML y CSS

### ¿Por qué es tan grande?
PyInstaller empaqueta todo el intérprete de Python + librerías. Esto es normal y esperado.

### ¿Se puede reducir?
Sí, pero comprimiendo con WinRAR o 7-Zip (la USB lo descomprime automáticamente).

### ¿Funciona offline?
Sí, excepto las recomendaciones que necesitan Groq API.

---

## 🚀 PRÓXIMOS PASOS

1. **Ahora**: Lee `INSTRUCCIONES_SIMPLIFICADAS.md`
2. **Luego**: Haz doble clic en `GENERAR_EJECUTABLE.bat`
3. **Finalmente**: Copia carpeta `USB_Listo` a tu USB

---

Creado: 2026-07-21  
Última actualización: 2026-07-21  
Versión del proyecto: 1.0
