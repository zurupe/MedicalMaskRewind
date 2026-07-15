import base64
import io
import os
import threading
import time
import cv2
from flask import Flask, jsonify, render_template, Response, request
from detector_mascarillas import DetectorMascarillas
from logger import BioseguridadLogger
import groq
from dotenv import load_dotenv

load_dotenv()

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
    "daily_detecciones_modelo": 0,
    "daily_personas_reales": 0,
    "recommendation_title": "Esperando datos",
    "recommendation_text": "Aún no hay suficiente información diaria para una recomendación.",
}


detector = None
background_thread = None
stop_event = threading.Event()
logger = BioseguridadLogger()


def generar_recomendacion(daily_metrics):
    pct_con = daily_metrics.get("porcentaje_con", 0.0)
    pct_sin = daily_metrics.get("porcentaje_sin", 0.0)
    total = daily_metrics.get("total", 0)

    if total == 0:
        return {
            "title": "Esperando datos",
            "text": "Aún no hay suficiente información diaria para una recomendación.",
        }

    if pct_con < 70:
        return {
            "title": "Incrementar controles de seguridad",
            "text": f"El cumplimiento diario de mascarilla está en {pct_con:.1f}%. Se recomienda reforzar los recordatorios, supervisión y controles de acceso para mejorar la adopción.",
        }

    if pct_con >= 85 and pct_sin > 0:
        return {
            "title": "Analizar el porcentaje restante",
            "text": f"El cumplimiento diario es alto ({pct_con:.1f}%), pero aún existe un porcentaje de personas sin mascarilla ({pct_sin:.1f}%). Conviene revisar las causas del resto para ajustar la comunicación y la vigilancia.",
        }

    if pct_sin >= 15:
        return {
            "title": "Reforzar la comunicación de bioseguridad",
            "text": f"Se detecta un nivel significativo de incumplimiento ({pct_sin:.1f}%). Es recomendable reforzar mensajes, recordatorios y supervisión en la entrada.",
        }

    return {
        "title": "Cumplimiento estable",
        "text": f"El cumplimiento diario se mantiene en un nivel saludable ({pct_con:.1f}%). Se recomienda mantener la vigilancia y revisar solo los casos aislados que aún incumplen.",
    }


def actualizar_estado(frame, metrics):
    global detector
    # Manejar señales de error enviadas por el detector
    if isinstance(metrics, dict) and metrics.get('error'):
        err = metrics.get('error')
        STATE['camera_status'] = err
        STATE['video_ready'] = False
        return

    daily_metrics = logger.obtener_resumen_diario()
    recommendation = generar_recomendacion(daily_metrics)

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
        "daily_detecciones_modelo": daily_metrics.get("detecciones_modelo", 0),
        "daily_personas_reales": daily_metrics.get("personas_reales", 0),
        "recommendation_title": recommendation["title"],
        "recommendation_text": recommendation["text"],
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
        result = detector.analizar_webcam(mostrar_ventana=False, stop_event=stop_event)
        if result is False:
            STATE['camera_status'] = 'camera_error'
            STATE['video_ready'] = False
            print('Background detection stopped: camera not available.')
    except Exception as exc:
        STATE['camera_status'] = f'error: {exc}'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/metrics')
def metrics():
    return render_template('metrics.html')


@app.route('/logs')
def logs():
    return render_template('logs.html')


@app.route('/api/logs_data')
def api_logs_data():
    if detector is not None:
        logs_list = detector.logger.leer_registros(limit=50)
        alerts_list = detector.logger.obtener_alertas(limit=50)
    else:
        logs_list = logger.leer_registros(limit=50)
        alerts_list = logger.obtener_alertas(limit=50)
    return jsonify({"logs": logs_list, "alerts": alerts_list})


@app.route('/api/logs_by_date')
def api_logs_by_date():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({"error": "Fechas requeridas"}), 400
    
    resumen = logger.obtener_resumen_por_fechas(start, end)
    return jsonify(resumen)


@app.route('/api/generate_ai_report', methods=['POST'])
def generate_ai_report():
    data = request.json
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
             return jsonify({"error": "No se encontró la variable de entorno GROQ_API_KEY. Verifica tu archivo .env"}), 500

        client = groq.Groq(api_key=api_key)
        prompt = f"""
        Eres un asistente de IA experto en seguridad industrial y bioseguridad.
        A continuación se presentan los datos de detecciones de uso de mascarillas en un periodo de tiempo.
        IMPORTANTE: Ten en cuenta que los números representan "detecciones" del modelo de visión; los valores de "personas reales rastreadas" son una estimación del seguimiento y pueden diferir de las detecciones por cuadro.
        Genera un reporte corto y profesional (máximo 3 párrafos cortos) en formato Markdown interpretando los datos, 
        dando una conclusión y sugiriendo si se deben tomar medidas.
        
        Datos del periodo: {data.get('rango')}
        Total de detecciones analizadas: {data.get('total')}
        Detecciones CON mascarilla: {data.get('con_mascarilla')} ({data.get('porcentaje_con')}%)
        Detecciones SIN mascarilla: {data.get('sin_mascarilla')} ({data.get('porcentaje_sin')}%)
        Detecciones del modelo (por cuadro): {data.get('detecciones_modelo')}
        Personas reales rastreadas: {data.get('personas_reales')}
        
        Detalles por día: {data.get('detalles')}
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
        )
        reporte = chat_completion.choices[0].message.content
        return jsonify({"report": reporte})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/state')
def api_state():
    payload = {key: value for key, value in STATE.items() if key != 'latest_frame'}
    return jsonify(payload)


@app.route('/api/export_report_pdf', methods=['POST'])
def export_report_pdf():
    data = request.json or {}
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph('Reporte de Bioseguridad', styles['Title']))
        story.append(Paragraph('Monitoreo de cumplimiento de mascarillas', styles['Heading2']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Periodo analizado: {data.get('rango', 'N/D')}", styles['BodyText']))
        story.append(Spacer(1, 8))

        metrics = [
            ['Indicador', 'Valor'],
            ['Detecciones del modelo', str(data.get('detecciones_modelo', 0))],
            ['Personas reales rastreadas', str(data.get('personas_reales', 0))],
            ['Con mascarilla', f"{data.get('con_mascarilla', 0)} ({data.get('porcentaje_con', 0)}%)"],
            ['Sin mascarilla', f"{data.get('sin_mascarilla', 0)} ({data.get('porcentaje_sin', 0)}%)"],
        ]
        table = Table(metrics, repeatRows=1, colWidths=[220, 180])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 14))
        story.append(Paragraph('Observaciones del informe', styles['Heading3']))
        report_text = data.get('report', 'Sin observaciones adicionales.')

        # Convert simple Markdown (bold, paragraphs, line breaks) to ReportLab-friendly HTML
        import re
        def md_to_paragraphs(md_text, style):
            blocks = re.split(r"\n\s*\n", md_text.strip())
            paras = []
            for b in blocks:
                t = b.strip()
                if not t:
                    continue
                # Replace bold **text** with <b>text</b>
                t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
                # Replace inline italics *text* with <i>text</i>
                t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
                # Preserve single newlines as <br/>
                t = t.replace('\n', '<br/>')
                paras.append(Paragraph(t, style))
            return paras

        for p in md_to_paragraphs(report_text, styles['BodyText']):
            story.append(p)
            story.append(Spacer(1, 6))

        story.append(Spacer(1, 8))
        story.append(Paragraph('Nota: los valores de detecciones corresponden al modelo de visión, mientras que las personas reales rastreadas representan entidades únicas mantenidas por el seguimiento.', styles['Italic']))
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return jsonify({"pdf_url": "data:application/pdf;base64," + base64.b64encode(pdf_bytes).decode('ascii')})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


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
