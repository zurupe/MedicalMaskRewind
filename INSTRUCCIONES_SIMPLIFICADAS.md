# 🎯 DETECTOR DE MASCARILLAS - EJECUTABLE PORTABLE

## ⚡ FORMA MÁS FÁCIL (¡RECOMENDADA!)

### 3 pasos nada más:

1. **Haz doble clic en**: `GENERAR_EJECUTABLE.bat`
   
2. **Espera a que termine** (5-10 minutos)
   - Se compilará automáticamente
   - Se abrirá una carpeta con todo listo

3. **Copia la carpeta `USB_Listo` a tu USB flash**
   - Ya está lista para llevar a otra computadora
   - No necesita instalación de nada

---

## 🚀 EN OTRA COMPUTADORA

1. Inserta la USB flash
2. Haz doble clic en `DetectorMascarillas.exe`
3. ¡Listo! La aplicación se abre automáticamente

✅ No necesita Python instalado  
✅ No necesita instalar dependencias  
✅ Funciona en Windows 10 y 11  

---

## 📋 SI ALGO NO FUNCIONA

### ❌ "No se abre nada"
→ Asegúrate que sea Windows 10 o 11 (64-bit)  
→ Instala Visual C++ Redistributable: https://support.microsoft.com/downloads

### ❌ "El antivirus lo bloquea"
→ Es falsa alarma de PyInstaller  
→ Agrega excepción en tu antivirus  

### ❌ "Se demora mucho en abrir"
→ Es normal en la primera ejecución (~30 segundos)  
→ Las próximas veces será más rápido  

### ❌ "Error al compilar"
→ Asegúrate tener Python instalado  
→ Ejecuta: `pip install --upgrade pyinstaller`  

---

## 📂 ALTERNATIVAS

Si quieres hacer tu propio instalador profesional:

1. Edita `installer.nsi` con tus datos
2. Instala NSIS desde: https://nsis.sourceforge.io/Download
3. Haz clic derecho → "Compilar NSIS script"
4. Genera un instalador .exe profesional

---

## 💾 TAMAÑO DEL ARCHIVO

- Ejecutable: ~500 MB
- Una vez copiado en otra PC: mismo tamaño
- Si quieres reducir: comprime con WinRAR

---

## 📞 PREGUNTAS FRECUENTES

**P: ¿Por qué es tan grande el .exe?**  
R: Porque incluye Python, los modelos YOLO y todas las librerías.

**P: ¿Funciona en Mac o Linux?**  
R: Este ejecutable es solo para Windows. Para Mac/Linux necesitas generar versiones diferentes.

**P: ¿Necesita internet?**  
R: No, pero si quieres usar la recomendación de Groq sí necesita conexión.

**P: ¿Se puede ejecutar desde la USB directamente?**  
R: Sí, pero es lento. Mejor cópialo a la PC primero.

---

## ✅ VERIFICACIÓN FINAL

Antes de llevarlo a otra computadora, pruébalo:

1. Haz doble clic en `DetectorMascarillas.exe`
2. Verifica que se abra en `http://127.0.0.1:5000`
3. Prueba las funcionalidades básicas
4. Cierra y listo!

---

**¡Ya está todo listo para llevar en la USB! 🎉**

Creado: 2026-07-21  
Versión: 1.0
