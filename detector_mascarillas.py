import os
import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO
from logger import BioseguridadLogger

# Colores BGR para OpenCV
COLOR_CON_MASCARILLA = (0, 255, 0)
COLOR_SIN_MASCARILLA = (0, 0, 255)


class DetectorMascarillas:
    def __init__(self, modelo_path="best_mask_mrisdi.pt", callback=None):
        self.modelo_path = modelo_path
        self.logger = BioseguridadLogger()
        self.callback = callback
        self._cargar_modelo()

    def _cargar_modelo(self):
        if not os.path.exists(self.modelo_path):
            print(f"❌ Error: No se encontró el modelo {self.modelo_path}")
            print("Asegúrate de que se descargó correctamente.")
            raise FileNotFoundError(self.modelo_path)

        print("Cargando modelo...")
        self.modelo = YOLO(self.modelo_path)
        self.MASK_CLASS = 0
        self.NO_MASK_CLASS = 1
        print(f"✅ Modelo cargado. Clases: {self.modelo.names}")

    def procesar_frame(self, frame_bgr):
        resultados = self.modelo(frame_bgr, verbose=False)[0]

        con_mascarilla = 0
        sin_mascarilla = 0

        if resultados.boxes is not None and len(resultados.boxes) > 0:
            cajas = resultados.boxes.xyxy.cpu().numpy()
            clases = resultados.boxes.cls.cpu().numpy()
            confs = resultados.boxes.conf.cpu().numpy()

            for (x1, y1, x2, y2), clase_id, conf in zip(cajas, clases, confs):
                clase_id = int(clase_id)

                if clase_id == self.MASK_CLASS:
                    con_mascarilla += 1
                    color = COLOR_CON_MASCARILLA
                    etiqueta = f"Con Mascarilla {conf:.2f}"
                elif clase_id == self.NO_MASK_CLASS:
                    sin_mascarilla += 1
                    color = COLOR_SIN_MASCARILLA
                    etiqueta = f"SIN Mascarilla {conf:.2f}"
                else:
                    continue

                cv2.rectangle(frame_bgr, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                (tw, th), _ = cv2.getTextSize(etiqueta, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(frame_bgr, (int(x1), int(y1) - th - 10), (int(x1) + tw, int(y1)), color, -1)
                cv2.putText(frame_bgr, etiqueta, (int(x1), int(y1) - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        total = con_mascarilla + sin_mascarilla
        metrics = self.logger.registrar(total, con_mascarilla, sin_mascarilla, incorrecta=0)

        if self.callback is not None:
            self.callback(frame_bgr, metrics)

        return frame_bgr, con_mascarilla, sin_mascarilla

    def analizar_imagen(self, ruta_imagen="prueba.jpg"):
        if not os.path.exists(ruta_imagen):
            print(f"❌ No se encontró la imagen: {ruta_imagen}")
            return

        print(f"Analizando imagen: {ruta_imagen}...")
        imagen_bgr = cv2.imread(ruta_imagen)

        anotada_bgr, con_masc, sin_masc = self.procesar_frame(imagen_bgr.copy())

        print(f"✅ Análisis completado. Con Mascarilla: {con_masc} | Sin Mascarilla: {sin_masc}")

        anotada_rgb = cv2.cvtColor(anotada_bgr, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(12, 6))
        plt.imshow(anotada_rgb)
        plt.axis("off")
        plt.title(f"Resultado - Con Mascarilla: {con_masc} | Sin Mascarilla: {sin_masc}")
        plt.show()

        cv2.imwrite("resultado_mascarillas.jpg", anotada_bgr)
        print("✅ Imagen guardada como resultado_mascarillas.jpg")

    def analizar_webcam(self, mostrar_ventana=True, stop_event=None, callback=None):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ No se pudo acceder a la cámara.")
            return False

        print("🎥 Iniciando monitoreo... Presiona ESC para salir.")
        while True:
            if stop_event is not None and stop_event.is_set():
                break

            ret, frame = cap.read()
            if not ret:
                break

            anotada, con_masc, sin_masc = self.procesar_frame(frame)
            if callback is not None:
                callback(anotada, con_masc, sin_masc)

            if mostrar_ventana:
                info = f"Con: {con_masc} | Sin: {sin_masc}"
                cv2.putText(anotada, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.imshow("Monitoreo de Bioseguridad (Mascarillas)", anotada)

                if cv2.waitKey(1) == 27:
                    break
            else:
                cv2.waitKey(1)

        cap.release()
        if mostrar_ventana:
            cv2.destroyAllWindows()
        return True
