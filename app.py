import os
import threading
import time
import cv2
from flask import Flask, jsonify, render_template, request, Response
from detector_mascarillas import DetectorMascarillas
from logger import BioseguridadLogger

app = Flask(__name__)

STATE = {
    "last_update": "",
    "total": 0,
    "con_mascarilla": 0,
    "sin_mascarilla": 0,
    "porcentaje_con": 0.0,
    "porcentaje_sin": 0.0,
    "alerta": False,
    "registros": 0,
    "logs": [],
    "alerts": [],
    "camera_status": "idle",
    "video_ready": False,
    "daily_total": 0,
    "daily_con": 0,
    "daily_sin": 0,
    "daily_pct_con": 0.0,
    "daily_pct_sin": 0.0,
    "recommendation_title": "Esperando datos",
    "recommendation_text": "Aún no hay suficiente información diaria para una recomendación.",
    "risk_level": "Sin datos",
    "risk_description": "Todavía no hay detecciones suficientes para estimar el nivel de riesgo.",
}


detector = None
background_thread = None
stop_event = threading.Event()
logger = BioseguridadLogger()


def calcular_nivel_riesgo(metrics, daily_metrics):
    total = metrics.get("total", 0)
    sin_mascarilla = metrics.get("sin_mascarilla", 0)
    daily_total = daily_metrics.get("total", 0)
    daily_pct_con = daily_metrics.get("porcentaje_con", 0.0)

    if total == 0 and daily_total == 0:
        return {
            "level": "Sin datos",
            "description": "Todavía no hay personas detectadas para estimar el nivel de riesgo.",
        }

    if daily_total > 0 and daily_pct_con < 70:
        return {
            "level": "Riesgo crítico",
            "description": "El cumplimiento diario está por debajo del 70%. Se recomienda reforzar controles de ingreso y recordatorios de uso de mascarilla.",
        }

    if total == 0:
        return {
            "level": "Sin datos",
            "description": "No hay personas en la última lectura. El sistema mantiene las métricas diarias registradas.",
        }

    if sin_mascarilla == 0:
        return {
            "level": "Riesgo bajo",
            "description": "No se detectaron personas sin mascarilla en la última lectura.",
        }

    if sin_mascarilla == 1:
        return {
            "level": "Riesgo moderado",
            "description": "Se detectó una persona sin mascarilla. Se recomienda solicitar el uso correcto antes del ingreso.",
        }

    return {
        "level": "Riesgo alto",
        "description": "Se detectaron varias personas sin mascarilla. Se recomienda reforzar el control de ingreso.",
    }


def generar_recomendacion(daily_metrics, metrics=None):
    pct_con = daily_metrics.get("porcentaje_con", 0.0)
    pct_sin = daily_metrics.get("porcentaje_sin", 0.0)
    total = daily_metrics.get("total", 0)
    sin_actual = (metrics or {}).get("sin_mascarilla", 0)

    if total == 0:
        return {
            "title": "Esperando datos",
            "text": "Aún no hay suficiente información diaria para una recomendación.",
        }

    if pct_con < 70:
        return {
            "title": "Riesgo crítico",
            "text": f"El cumplimiento diario está en {pct_con:.1f}% ({daily_metrics.get('con_mascarilla', 0)} de {total} detecciones con mascarilla). Se recomienda aplicar controles más estrictos y reforzar los recordatorios de bioseguridad.",
        }

    if sin_actual > 0:
        return {
            "title": "Reforzar control",
            "text": f"Se detectaron personas sin mascarilla en la última lectura. El cumplimiento diario es {pct_con:.1f}% y el incumplimiento acumulado es {pct_sin:.1f}%; se recomienda solicitar el uso correcto antes del ingreso.",
        }

    if pct_sin >= 15:
        return {
            "title": "Reforzar la comunicación de bioseguridad",
            "text": f"El incumplimiento diario acumulado es {pct_sin:.1f}%. Se recomienda reforzar mensajes visibles y supervisión en la entrada.",
        }

    return {
        "title": "Cumplimiento adecuado",
        "text": f"No se detectan personas sin mascarilla en la última lectura. El cumplimiento diario se mantiene en {pct_con:.1f}% con {daily_metrics.get('con_mascarilla', 0)} detecciones correctas.",
    }


def actualizar_estado(frame, metrics):
    global detector
    daily_metrics = logger.obtener_resumen_diario()
    recommendation = generar_recomendacion(daily_metrics, metrics)
    risk = calcular_nivel_riesgo(metrics, daily_metrics)

    STATE.update({
        "last_update": metrics.get("timestamp", ""),
        "total": metrics.get("total", 0),
        "con_mascarilla": metrics.get("con_mascarilla", 0),
        "sin_mascarilla": metrics.get("sin_mascarilla", 0),
        "porcentaje_con": metrics.get("porcentaje_con", 0.0),
        "porcentaje_sin": metrics.get("porcentaje_sin", 0.0),
        "alerta": metrics.get("alerta", False),
        "registros": metrics.get("registros", 0),
        "camera_status": "running",
        "video_ready": True,
        "daily_total": daily_metrics.get("total", 0),
        "daily_con": daily_metrics.get("con_mascarilla", 0),
        "daily_sin": daily_metrics.get("sin_mascarilla", 0),
        "daily_pct_con": daily_metrics.get("porcentaje_con", 0.0),
        "daily_pct_sin": daily_metrics.get("porcentaje_sin", 0.0),
        "recommendation_title": recommendation["title"],
        "recommendation_text": recommendation["text"],
        "risk_level": risk["level"],
        "risk_description": risk["description"],
    })

    if detector is not None:
        STATE["logs"] = detector.logger.leer_registros(limit=8)
        STATE["alerts"] = detector.logger.obtener_alertas(limit=8)

    if frame is not None:
        try:
            success, encoded = cv2.imencode('.jpg', frame)
            if success:
                STATE['latest_frame'] = encoded.tobytes()
        except Exception:
            pass


def background_loop():
    global detector
    try:
        detector = DetectorMascarillas(callback=actualizar_estado)
        detector.analizar_webcam(mostrar_ventana=False, stop_event=stop_event)
    except Exception as exc:
        STATE['camera_status'] = f'error: {exc}'


@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/api/state')
def api_state():
    payload = {key: value for key, value in STATE.items() if key != 'latest_frame'}
    return jsonify(payload)


@app.route('/api/history')
def api_history():
    start = request.args.get('start', '').strip()
    end = request.args.get('end', '').strip()

    if not start or not end:
        return jsonify({"error": "Debe enviar fecha inicial y fecha final."}), 400

    return jsonify(logger.consultar_por_fechas(start, end))


@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            frame = STATE.get('latest_frame')
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                time.sleep(0.2)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


def start_background_detection():
    global background_thread
    if background_thread is None or not background_thread.is_alive():
        stop_event.clear()
        background_thread = threading.Thread(target=background_loop, daemon=True)
        background_thread.start()


def main():
    if not os.path.exists('best_mask_mrisdi.pt'):
        print('Modelo no encontrado. Verifica best_mask_mrisdi.pt')
        return
    start_background_detection()
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()
