import cv2
from detector_mascarillas import DetectorMascarillas

def main():
    detector = DetectorMascarillas()
    
    print("=============================================")
    print(" SISTEMA DE DETECCIÓN DE USO DE MASCARILLAS")
    print("=============================================")
    print("Selecciona una opción:")
    print("1. Analizar Imagen Local (prueba.jpg)")
    print("2. Monitoreo en Tiempo Real (Webcam)")
    print("=============================================")
    
    opcion = input("Opción (1/2): ").strip()
    
    if opcion == "1":
        detector.analizar_imagen("prueba.jpg")
    elif opcion == "2":
        detector.analizar_webcam()
    else:
        print("❌ Opción inválida.")

if __name__ == "__main__":
    main()
