from detector_mascarillas import DetectorMascarillas


def main():
    detector = DetectorMascarillas()

    print("=============================================")
    print(" SISTEMA DE DETECCIÓN DE USO DE MASCARILLAS")
    print("=============================================")
    print("Selecciona una opción:")
    print("1. Analizar Imagen Local (prueba.jpg)")
    print("2. Monitoreo en Tiempo Real (Webcam)")
    print("3. Iniciar Dashboard Web")
    print("4. Salir")
    print("=============================================")

    opcion = input("Opción (1/2/3/4): ").strip()

    if opcion == "1":
        detector.analizar_imagen("prueba.jpg")
    elif opcion == "2":
        detector.analizar_webcam()
    elif opcion == "3":
        print("Abriendo dashboard en http://127.0.0.1:5000")
        print("Presiona Ctrl+C para detener el servidor.")
        import app
        app.main()
    elif opcion == "4":
        print("Saliendo del sistema.")
    else:
        print("❌ Opción inválida.")


if __name__ == "__main__":
    main()
