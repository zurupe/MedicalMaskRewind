"""
Script para entrenar un modelo YOLOv8 especializado en detección de mascarillas.
Descarga un dataset desde Roboflow y entrena el modelo localmente.

Uso:
    python entrenar_modelo.py

El modelo entrenado se guardará como 'best_mask.pt' en la carpeta actual.
"""
from ultralytics import YOLO
import os
import shutil

# ============================
# CONFIGURACIÓN
# ============================
EPOCHS = 25            # Número de épocas de entrenamiento (aumentar para más precisión)
IMG_SIZE = 640         # Tamaño de imagen
MODELO_BASE = "yolov8n.pt"  # Modelo base (nano, rápido y ligero)

# ============================
# PASO 1: Preparar dataset
# ============================
print("=" * 50)
print("  ENTRENAMIENTO DE MODELO DE MASCARILLAS")
print("=" * 50)

# Verificar si ya existe el dataset
DATASET_DIR = os.path.join(os.getcwd(), "mask_dataset")

if not os.path.exists(DATASET_DIR):
    print("\n📥 Descargando dataset de mascarillas desde Roboflow...")
    print("   (Se necesita la librería 'roboflow'. Instalando...)")
    
    try:
        import roboflow
    except ImportError:
        os.system("pip install roboflow")
        import roboflow

    from roboflow import Roboflow
    
    # Dataset público de detección de mascarillas
    # https://universe.roboflow.com/joseph-nelson/mask-wearing
    rf = Roboflow(api_key="")  # Sin API key para datasets públicos
    project = rf.workspace().project("mask-wearing")
    version = project.version(4)
    dataset = version.download("yolov8", location=DATASET_DIR)
    
    print("✅ Dataset descargado correctamente.")
else:
    print(f"✅ Dataset ya existe en: {DATASET_DIR}")

# ============================
# PASO 2: Entrenar el modelo
# ============================
print(f"\n🚀 Iniciando entrenamiento ({EPOCHS} épocas)...")
print("   Esto puede tardar varios minutos dependiendo de tu hardware.")
print("   Si tienes GPU NVIDIA, el proceso será mucho más rápido.\n")

data_yaml = os.path.join(DATASET_DIR, "data.yaml")

modelo = YOLO(MODELO_BASE)
resultados = modelo.train(
    data=data_yaml,
    epochs=EPOCHS,
    imgsz=IMG_SIZE,
    batch=8,
    name="mask_detection",
    project="runs",
    exist_ok=True
)

# ============================
# PASO 3: Copiar el mejor modelo
# ============================
best_model_path = os.path.join("runs", "mask_detection", "weights", "best.pt")

if os.path.exists(best_model_path):
    shutil.copy(best_model_path, "best_mask.pt")
    print("\n" + "=" * 50)
    print("✅ ¡ENTRENAMIENTO COMPLETADO!")
    print(f"   Modelo guardado como: best_mask.pt")
    print("=" * 50)
    
    # Verificar clases
    modelo_final = YOLO("best_mask.pt")
    print(f"\n📋 Clases del modelo: {modelo_final.names}")
else:
    print("❌ Error: No se encontró el archivo best.pt después del entrenamiento.")
    print(f"   Ruta esperada: {best_model_path}")
