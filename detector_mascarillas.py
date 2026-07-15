import os
import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO
from logger import BioseguridadLogger

# Colores BGR para OpenCV
COLOR_CON_MASCARILLA = (0, 255, 0)
COLOR_SIN_MASCARILLA = (0, 0, 255)


class SimpleTracker:
    def __init__(self, max_missed=5, dist_threshold=90):
        self.max_missed = max_missed
        self.dist_threshold = dist_threshold
        self.next_id = 1
        self.tracks = []

    def _centroid(self, box):
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def _distance(self, box_a, box_b):
        cx_a, cy_a = self._centroid(box_a)
        cx_b, cy_b = self._centroid(box_b)
        return ((cx_a - cx_b) ** 2 + (cy_a - cy_b) ** 2) ** 0.5

    def _deduplicate_detections(self, detections):
        unique = []
        for detection in detections:
            class_id, box = detection
            should_add = True
            for existing_class_id, existing_box in unique:
                if existing_class_id != class_id:
                    continue
                if self._distance(existing_box, box) <= self.dist_threshold / 2.0:
                    should_add = False
                    break
            if should_add:
                unique.append((class_id, box))
        return unique

    def update(self, detections):
        detections = self._deduplicate_detections(detections)
        if not detections:
            self._prune_tracks()
            return self.get_active_tracks()

        active_tracks = list(self.tracks)
        matched_tracks = []
        unmatched_tracks = list(range(len(active_tracks)))
        unmatched_detections = list(range(len(detections)))

        while unmatched_tracks and unmatched_detections:
            best_track_idx = None
            best_det_idx = None
            best_distance = None
            best_track = None
            best_detection = None

            for ti in unmatched_tracks:
                track = active_tracks[ti]
                for di in unmatched_detections:
                    class_id, box = detections[di]
                    distance = self._distance(track["bbox"], box)
                    if track["class_id"] != -1 and track["class_id"] != class_id:
                        distance += 100
                    if best_distance is None or distance < best_distance:
                        best_distance = distance
                        best_track_idx = ti
                        best_det_idx = di
                        best_track = track
                        best_detection = (class_id, box)

            if best_track_idx is None or best_distance is None or best_distance > self.dist_threshold:
                break

            track = active_tracks[best_track_idx]
            class_id, box = detections[best_det_idx]
            track["bbox"] = box
            track["class_id"] = class_id
            track["missed_count"] = 0
            matched_tracks.append(best_track_idx)
            unmatched_tracks.remove(best_track_idx)
            unmatched_detections.remove(best_det_idx)

        for ti in unmatched_tracks:
            active_tracks[ti]["missed_count"] += 1

        self.tracks = [track for track in active_tracks if track["missed_count"] <= self.max_missed]

        for di in unmatched_detections:
            class_id, box = detections[di]
            self.tracks.append({
                "id": self.next_id,
                "bbox": box,
                "class_id": class_id,
                "missed_count": 0,
            })
            self.next_id += 1

        return self.get_active_tracks()

    def _prune_tracks(self):
        self.tracks = [track for track in self.tracks if track["missed_count"] <= self.max_missed]
        for track in self.tracks:
            track["missed_count"] += 1

    def get_active_tracks(self):
        return [track for track in self.tracks if track["missed_count"] <= self.max_missed]

    def get_counts(self):
        tracks = self.get_active_tracks()
        con_mascarilla = sum(1 for track in tracks if track["class_id"] == 0)
        sin_mascarilla = sum(1 for track in tracks if track["class_id"] == 1)
        return {
            "total": con_mascarilla + sin_mascarilla,
            "con_mascarilla": con_mascarilla,
            "sin_mascarilla": sin_mascarilla,
        }


class DetectorMascarillas:
    def __init__(self, modelo_path="best_mask_mrisdi.pt", callback=None):
        self.modelo_path = modelo_path
        self.logger = BioseguridadLogger()
        self.callback = callback
        self.tracker = SimpleTracker()
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

    def reset_tracker(self):
        self.tracker = SimpleTracker()

    def procesar_frame(self, frame_bgr):
        resultados = self.modelo(frame_bgr, verbose=False)[0]

        detecciones = []
        if resultados.boxes is not None and len(resultados.boxes) > 0:
            cajas = resultados.boxes.xyxy.cpu().numpy()
            clases = resultados.boxes.cls.cpu().numpy()
            confs = resultados.boxes.conf.cpu().numpy()

            for (x1, y1, x2, y2), clase_id, conf in zip(cajas, clases, confs):
                clase_id = int(clase_id)
                if clase_id == self.MASK_CLASS:
                    color = COLOR_CON_MASCARILLA
                    etiqueta = f"Con Mascarilla {conf:.2f}"
                elif clase_id == self.NO_MASK_CLASS:
                    color = COLOR_SIN_MASCARILLA
                    etiqueta = f"SIN Mascarilla {conf:.2f}"
                else:
                    continue

                detecciones.append((clase_id, (float(x1), float(y1), float(x2), float(y2))))
                cv2.rectangle(frame_bgr, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                (tw, th), _ = cv2.getTextSize(etiqueta, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(frame_bgr, (int(x1), int(y1) - th - 10), (int(x1) + tw, int(y1)), color, -1)
                cv2.putText(frame_bgr, etiqueta, (int(x1), int(y1) - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        tracked_objects = self.tracker.update(detecciones)
        counts = self.tracker.get_counts()
        con_mascarilla = counts["con_mascarilla"]
        sin_mascarilla = counts["sin_mascarilla"]

        for track in tracked_objects:
            x1, y1, x2, y2 = track["bbox"]
            color = COLOR_CON_MASCARILLA if track["class_id"] == self.MASK_CLASS else COLOR_SIN_MASCARILLA
            cv2.rectangle(frame_bgr, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(frame_bgr, f"ID {track['id']}", (int(x1), int(y1) - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        total = con_mascarilla + sin_mascarilla
        metrics = self.logger.registrar(total, con_mascarilla, sin_mascarilla, incorrecta=0)

        if self.callback is not None:
            self.callback(frame_bgr, metrics)

        return frame_bgr, con_mascarilla, sin_mascarilla

    def analizar_imagen(self, ruta_imagen="prueba.jpg"):
        self.reset_tracker()
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
        self.reset_tracker()
        # Intentar abrir varias cámaras (índices 0..3) para compatibilidad
        cap = None
        opened_index = None
        for idx in range(0, 4):
            try_cap = cv2.VideoCapture(idx)
            if try_cap.isOpened():
                cap = try_cap
                opened_index = idx
                break
            else:
                try_cap.release()

        if cap is None or not cap.isOpened():
            print("❌ No se pudo acceder a ninguna cámara (índices 0..3).")
            if self.callback is not None:
                # notify the caller that camera couldn't open
                try:
                    self.callback(None, {"error": "camera_unavailable"})
                except Exception:
                    pass
            return False
        else:
            print(f"✅ Cámara abierta en índice {opened_index}.")

        print("🎥 Iniciando monitoreo... Presiona ESC para salir.")
        while True:
            if stop_event is not None and stop_event.is_set():
                break

            ret, frame = cap.read()
            if not ret:
                print("⚠️ Frame vacío recibido de la cámara. Terminando loop de captura.")
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
