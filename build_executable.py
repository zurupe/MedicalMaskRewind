"""
Script para empaquetar la aplicación con PyInstaller
Crea un ejecutable portable de la aplicación de detección de mascarillas
"""

import os
import shutil
import subprocess
import sys

def crear_ejecutable():
    """Crea el ejecutable con PyInstaller"""
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ Error: No se encontró app.py en el directorio actual")
        print("Asegúrate de ejecutar este script desde la raíz del proyecto")
        return False
    
    print("🔨 Preparando empaquetado de la aplicación...")
    
    # Limpiar builds anteriores
    if os.path.exists('build'):
        print("Limpiando carpeta build...")
        shutil.rmtree('build')
    if os.path.exists('dist'):
        print("Limpiando carpeta dist...")
        shutil.rmtree('dist')
    if os.path.exists('app.spec'):
        os.remove('app.spec')
    
    # Comando PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=DetectorMascarillas',
        '--onefile',  # Crea un archivo único
        '--windowed',  # Sin ventana de consola
        '--icon=CUSTOM_ICON_HERE',  # Opcional: agregar icono
        '--add-data=templates;templates',
        '--add-data=static;static',
        '--add-data=best_mask_mrisdi.pt;.',
        '--add-data=yolo11n.pt;.',
        '--add-data=yolov8m-mask.pt;.',
        '--add-data=yolov8n.pt;.',
        '--add-data=groq_key.txt;.',
        '--collect-all=ultralytics',
        '--collect-all=flask',
        '--collect-all=opencv',
        '--hidden-import=cv2',
        '--hidden-import=ultralytics',
        '--hidden-import=flask',
        '--hidden-import=PIL',
        'app.py'
    ]
    
    print("📦 Compilando ejecutable (esto puede tardar varios minutos)...")
    print(" ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Ejecutable creado exitosamente!")
        print("\n📍 Ubicación: dist/DetectorMascarillas.exe")
        print("\n💾 Copiar 'dist/DetectorMascarillas.exe' a tu USB")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al crear el ejecutable: {e}")
        return False

if __name__ == "__main__":
    crear_ejecutable()
