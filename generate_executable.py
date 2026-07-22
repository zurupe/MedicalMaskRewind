"""
Script automático para generar ejecutable y crear la estructura lista para USB
Simplifica todo el proceso de empaquetado
"""

import os
import sys
import shutil
import subprocess
import webbrowser
from pathlib import Path


class GeneradorEjecutable:
    def __init__(self):
        self.directorio_base = os.path.dirname(os.path.abspath(__file__))
        self.directorio_dist = os.path.join(self.directorio_base, 'dist')
        self.directorio_build = os.path.join(self.directorio_base, 'build')
        
    def limpieza(self):
        """Limpia builds anteriores"""
        print("🧹 Limpiando builds anteriores...")
        if os.path.exists(self.directorio_build):
            shutil.rmtree(self.directorio_build)
            print("   ✓ Carpeta 'build' eliminada")
        if os.path.exists(self.directorio_dist):
            shutil.rmtree(self.directorio_dist)
            print("   ✓ Carpeta 'dist' eliminada")
        if os.path.exists('app.spec'):
            os.remove('app.spec')
            print("   ✓ Archivo 'app.spec' eliminado")
    
    def verificar_dependencias(self):
        """Verifica que todas las dependencias estén instaladas"""
        print("\n📦 Verificando dependencias...")
        
        paquetes_requeridos = [
            'flask',
            'opencv-python',
            'ultralytics',
            'numpy',
            'pillow',
            'supervision',
            'pyinstaller',
        ]
        
        faltantes = []
        for paquete in paquetes_requeridos:
            try:
                __import__(paquete.replace('-', '_'))
                print(f"   ✓ {paquete}")
            except ImportError:
                print(f"   ✗ {paquete} (FALTA)")
                faltantes.append(paquete)
        
        if faltantes:
            print(f"\n⚠️  Instalando paquetes faltantes: {', '.join(faltantes)}")
            for paquete in faltantes:
                subprocess.run([sys.executable, '-m', 'pip', 'install', paquete],
                             check=True)
            print("   ✓ Paquetes instalados")
        
        return len(faltantes) == 0
    
    def generar_ejecutable(self):
        """Genera el ejecutable con PyInstaller"""
        print("\n🔨 Generando ejecutable (esto puede tardar 5-10 minutos)...")
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--name=DetectorMascarillas',
            '--onefile',
            '--windowed',
            '--add-data=templates:templates',
            '--add-data=static:static',
            '--add-data=best_mask_mrisdi.pt:.',
            '--add-data=yolo11n.pt:.',
            '--add-data=yolov8m-mask.pt:.',
            '--add-data=yolov8n.pt:.',
            '--collect-all=ultralytics',
            '--collect-all=flask',
            '--hidden-import=cv2',
            '--hidden-import=ultralytics',
            '--hidden-import=flask',
            '--hidden-import=PIL',
            '--distpath=' + self.directorio_dist,
            '--buildpath=' + self.directorio_build,
            'app.py'
        ]
        
        try:
            resultado = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("   ✓ Ejecutable generado exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ✗ Error: {e.stderr}")
            return False
    
    def crear_estructura_usb(self):
        """Crea una estructura lista para llevar en USB"""
        print("\n💾 Creando estructura para USB...")
        
        carpeta_usb = os.path.join(self.directorio_base, 'USB_Listo')
        
        if os.path.exists(carpeta_usb):
            shutil.rmtree(carpeta_usb)
        
        os.makedirs(carpeta_usb)
        
        # Copiar ejecutable
        ejecutable_src = os.path.join(self.directorio_dist, 'DetectorMascarillas.exe')
        ejecutable_dst = os.path.join(carpeta_usb, 'DetectorMascarillas.exe')
        
        if os.path.exists(ejecutable_src):
            shutil.copy(ejecutable_src, ejecutable_dst)
            print(f"   ✓ Ejecutable copiado ({self.obtener_tamaño_mb(ejecutable_src):.1f} MB)")
        
        # Crear archivo Léeme
        archivo_readme = os.path.join(carpeta_usb, 'LÉEME.txt')
        with open(archivo_readme, 'w', encoding='utf-8') as f:
            f.write("""🎯 DETECTOR DE MASCARILLAS - VERSIÓN PORTABLE
===============================================

✅ ¿CÓMO USAR?

1. Copia la carpeta completa a tu USB
2. Lleválo a otra computadora
3. Haz doble clic en DetectorMascarillas.exe
4. ¡Listo! La aplicación se abrirá automáticamente

✔️ VENTAJAS:
- No necesita instalar nada
- No requiere Python
- Funciona en cualquier Windows 10/11
- Incluye todos los modelos necesarios

⚠️ REQUISITOS:
- Windows 10 o superior (64-bit)
- Al menos 8 GB de RAM
- 500 MB de espacio libre en disco
- Conexión a Internet (opcional, solo para Groq)

🔧 SI NO ABRE:
1. Verifica que sea Windows 64-bit
2. Instala Visual C++ Redistributable: 
   https://support.microsoft.com/en-us/help/2977003
3. Desactiva temporalmente el antivirus
4. Copia toda la carpeta, no solo el .exe

📧 Contacto: [Tu email aquí]

Generado: 2026-07-21
""")
        print("   ✓ Archivo de instrucciones creado")
        
        return carpeta_usb
    
    @staticmethod
    def obtener_tamaño_mb(ruta):
        """Obtiene el tamaño de un archivo en MB"""
        return os.path.getsize(ruta) / (1024 * 1024)
    
    def mostrar_resumen(self, carpeta_usb):
        """Muestra un resumen del proceso completado"""
        print("\n" + "="*60)
        print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print("="*60)
        print(f"\n📍 Carpeta lista para USB: {carpeta_usb}")
        print(f"\n📋 Contenido:")
        for archivo in os.listdir(carpeta_usb):
            ruta_completa = os.path.join(carpeta_usb, archivo)
            if os.path.isfile(ruta_completa):
                tamaño = self.obtener_tamaño_mb(ruta_completa)
                print(f"   • {archivo} ({tamaño:.1f} MB)")
        
        print(f"\n💾 PRÓXIMOS PASOS:")
        print(f"   1. Abre: {carpeta_usb}")
        print(f"   2. Copia TODO a una USB flash")
        print(f"   3. Lleválo a otra computadora")
        print(f"   4. Ejecuta DetectorMascarillas.exe")
        print("\n" + "="*60)
    
    def ejecutar(self):
        """Ejecuta todo el proceso automático"""
        print("\n🚀 INICIO DEL PROCESO DE EMPAQUETADO")
        print("="*60)
        
        try:
            self.limpieza()
            
            if not self.verificar_dependencias():
                print("\n❌ Falló la verificación de dependencias")
                return False
            
            if not self.generar_ejecutable():
                print("\n❌ Falló la generación del ejecutable")
                return False
            
            carpeta_usb = self.crear_estructura_usb()
            
            self.mostrar_resumen(carpeta_usb)
            
            # Abrir carpeta automáticamente
            print("\n📂 Abriendo carpeta...")
            os.startfile(carpeta_usb)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    print("\n🎯 GENERADOR AUTOMÁTICO DE EJECUTABLE")
    print("   Detector de Mascarillas - Versión Portable")
    print()
    
    generador = GeneradorEjecutable()
    exito = generador.ejecutar()
    
    if not exito:
        print("\n❌ El proceso falló. Intenta de nuevo.")
        input("Presiona Enter para salir...")
        sys.exit(1)
    else:
        input("\nPresiona Enter para salir...")
