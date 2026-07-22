"""
Utilidades para manejo de rutas en ejecutables PyInstaller
Este módulo detecta si se está ejecutando como .exe y configura los paths correctamente
"""

import os
import sys
from pathlib import Path


def obtener_ruta_base():
    """
    Obtiene la ruta base del proyecto.
    Funciona tanto en modo desarrollo como en ejecutable PyInstaller
    """
    if getattr(sys, 'frozen', False):
        # Se está ejecutando como .exe (PyInstaller)
        return sys._MEIPASS
    else:
        # Se está ejecutando como script Python
        return os.path.dirname(os.path.abspath(__file__))


def obtener_ruta_recurso(nombre_recurso):
    """
    Obtiene la ruta correcta de un recurso (templates, static, modelos, etc.)
    """
    base = obtener_ruta_base()
    return os.path.join(base, nombre_recurso)


def configurar_rutas():
    """
    Configura las variables de entorno de rutas
    Ejecutar esta función al inicio de app.py
    """
    base = obtener_ruta_base()
    
    # Variables de entorno para acceso desde otros módulos
    os.environ['APP_BASE'] = base
    os.environ['TEMPLATES_DIR'] = os.path.join(base, 'templates')
    os.environ['STATIC_DIR'] = os.path.join(base, 'static')
    
    return {
        'base': base,
        'templates': os.path.join(base, 'templates'),
        'static': os.path.join(base, 'static'),
        'es_ejecutable': getattr(sys, 'frozen', False)
    }


def obtener_ruta_modelo(nombre_modelo):
    """
    Obtiene la ruta correcta de los modelos YOLO
    """
    base = obtener_ruta_base()
    ruta_modelo = os.path.join(base, nombre_modelo)
    
    # Si no existe, intenta en el directorio actual
    if not os.path.exists(ruta_modelo):
        ruta_modelo = nombre_modelo
    
    return ruta_modelo


# Información de depuración
def debug_info():
    """Imprime información de depuración sobre las rutas"""
    rutas = configurar_rutas()
    print("\n" + "="*60)
    print("📍 INFORMACIÓN DE RUTAS")
    print("="*60)
    print(f"Es ejecutable PyInstaller: {rutas['es_ejecutable']}")
    print(f"Directorio base: {rutas['base']}")
    print(f"Directorio templates: {rutas['templates']}")
    print(f"Directorio static: {rutas['static']}")
    print("="*60 + "\n")
