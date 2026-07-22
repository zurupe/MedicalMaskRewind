# Sistema de Monitoreo de Bioseguridad y Detección de Mascarillas mediante Visión por Computadora e IA Explicativa

**Integrantes:** Diana Guerra, Simoné Medina, Pablo Zurita
**Asignatura:** Aplicaciones basadas en el conocimiento
**Fecha:** 21 de Julio de 2026

---

## Resumen (Abstract)
El presente proyecto busca resolver el problema del control de acceso y monitoreo de bioseguridad (uso de mascarillas) en entornos críticos como ingresos hospitalarios, industriales o espacios públicos cerrados. Utilizando un modelo de visión por computadora basado en la arquitectura YOLOv8n (nano) y un algoritmo de seguimiento de centroides (Centroid Tracking), la aplicación es capaz de detectar en tiempo real si las personas portan mascarilla o no, minimizando conteos duplicados. La arquitectura del sistema se compone de un backend asíncrono en Flask que orquesta la captura de video (OpenCV), la inferencia del modelo y el registro de eventos en una base de datos relacional (SQLite). Los datos se exponen a través de un dashboard interactivo web moderno (HTML/CSS/JS con Chart.js). Como característica innovadora, el sistema integra Inteligencia Artificial explicativa (LLM Llama 3.1 8B vía Groq API) para interpretar los registros históricos y generar informes automatizados exportables a PDF. El resultado es un sistema robusto de extremo a extremo, con métricas precisas en tiempo real y conclusiones generadas por IA que facilitan la toma de decisiones gerenciales.

---

## 1. Introducción

### 1.1 Contexto del Problema
En entornos hospitalarios, clínicas, y áreas de alta exigencia sanitaria (como laboratorios o plantas de procesamiento de alimentos), mantener el control estricto del uso correcto de mascarillas es un protocolo estándar para prevenir la propagación de patógenos aerotransportados. Actualmente, este control depende en gran medida de personal humano (guardias de seguridad o supervisores), lo que resulta en un proceso ineficiente, propenso a errores por fatiga visual durante jornadas prolongadas, y genera fricciones en puntos de alto tránsito. 

### 1.2 Justificación
La automatización de este control mediante Visión por Computadora (CV) permite una vigilancia continua (24/7), objetiva y escalable. Sin embargo, los sistemas tradicionales de CV suelen limitarse a proporcionar datos crudos o gráficos que requieren tiempo de análisis por parte del personal administrativo. Al incorporar IA Explicativa (XAI) mediante Grandes Modelos de Lenguaje (LLMs), el sistema no solo reporta anomalías, sino que contextualiza la información. Traduce tablas de datos ("75% de cumplimiento el día martes") en recomendaciones accionables ("El cumplimiento cayó al 75%, se sugiere instalar señalética adicional en el pasillo norte"), agregando un valor gerencial significativo sobre un simple contador de objetos.

### 1.3 Objetivos
**Objetivo General:** 
Desarrollar un sistema integral y escalable para la detección, seguimiento y monitoreo en tiempo real del uso de mascarillas, incorporando un dashboard analítico web y la generación automatizada de reportes mediante Inteligencia Artificial Explicativa.

**Objetivos Específicos:**
1. Entrenar y optimizar un modelo de detección de objetos (YOLOv8) sobre un dataset especializado para distinguir rostros con y sin mascarilla.
2. Implementar un algoritmo de seguimiento de objetos (Object Tracking) para distinguir personas únicas en el flujo de video y evitar falsos positivos o conteos redundantes.
3. Desarrollar una arquitectura de backend en Python (Flask) con base de datos SQLite para la persistencia del estado en tiempo real y almacenamiento histórico de eventos.
4. Diseñar un frontend moderno (Dashboard) que ofrezca métricas en vivo y visualizaciones interactivas.
5. Integrar el LLM Llama-3.1-8b (vía API) capaz de analizar el histórico de detecciones y generar informes ejecutivos automáticos exportables en formato PDF.

---

## 2. Marco Teórico y Tecnologías

### 2.1 Visión por Computadora (YOLOv8 y Tracking)
Para el núcleo de detección, se optó por la arquitectura **YOLO (You Only Look Once)**, específicamente la versión 8 en su variante "nano" (`yolov8n.pt`). YOLO es un modelo de detección de objetos en una sola etapa, conocido por su excepcional velocidad de inferencia, lo que lo hace ideal para aplicaciones en tiempo real operando directamente sobre flujos de video de cámaras (Webcams/RTSP). 
Para resolver el problema del "doble conteo" (cuando una misma persona permanece en escena por múltiples *frames*), se desarrolló un algoritmo de **Centroid Tracking** (`SimpleTracker`). Este algoritmo calcula la distancia euclidiana entre los centroides de los *bounding boxes* detectados entre frames consecutivos, asignando un ID único temporal a cada individuo rastreado.

### 2.2 IA Explicativa (LLM Llama 3.1)
Para dotar al sistema de capacidades de razonamiento sobre los datos, se integró un Modelo de Lenguaje Grande (LLM). Específicamente, se utiliza el modelo de código abierto **Llama 3.1 (8B parámetros)**, alojado en los servidores de inferencia de ultra-baja latencia de **Groq** (usando LPUs). Mediante la técnica de "Prompt Engineering", el modelo actúa bajo la directriz de ser un "experto en seguridad industrial". Se le alimenta con un contexto estructurado que incluye el rango de fechas, total de personas únicas rastreadas, total de detecciones por frame y los porcentajes de cumplimiento/incumplimiento, retornando un informe profesional en formato Markdown.

### 2.3 Stack Tecnológico del Proyecto
- **Lenguaje Principal:** Python 3.x
- **Backend Framework:** Flask (ejecutando hilos en background `threading.Thread` para el procesamiento asíncrono de video).
- **Visión por Computadora:** Ultralytics (YOLOv8), OpenCV (`cv2`) para manipulación y renderizado de frames.
- **Frontend:** Jinja2 Templates (Flask), HTML5, CSS3 Nativo (Variables CSS, Flexbox/Grid, diseño responsivo sin librerías externas), Javascript (Fetch API).
- **Visualización de Datos:** Chart.js para los gráficos de torta/anillo en el dashboard, Phosphor Icons para la iconografía premium.
- **Almacenamiento de Datos:** SQLite3 (Base de datos relacional para el histórico), JSON (para caché de estado de la aplicación).
- **Generación de Reportes:** Librería `reportlab` para la creación dinámica de archivos PDF a partir del texto generado por el LLM.
- **Machine Learning (Entrenamiento):** Plataforma Roboflow para la gestión y descarga del dataset de imágenes.

---

## 3. Diseño y Metodología del Sistema

### 3.1 Arquitectura General del Sistema
El sistema implementa una arquitectura modular de tipo cliente-servidor, donde el servidor asume tareas duales (procesamiento de visión y API REST).
El flujo se describe en las siguientes etapas:
1. **Captura:** Un hilo secundario (Background Loop) en Flask abre el flujo de video usando OpenCV (ya sea cámara web índice 0 o imagen estática).
2. **Inferencia CV:** Cada *frame* capturado se pasa al modelo YOLOv8 cargado en memoria (`best_mask_mrisdi.pt`). YOLO retorna *bounding boxes*, confianzas y clases (0: Con Mascarilla, 1: Sin Mascarilla).
3. **Tracking:** Las detecciones de YOLO se envían a la clase `SimpleTracker`, que actualiza la lista de objetos activos y filtra las anomalías (ej. objetos que desaparecen de escena).
4. **Registro (Logging):** Las métricas de conteo actuales se pasan a la clase `BioseguridadLogger`, que persiste en un estado JSON rápido para el dashboard, y en SQLite si hay variaciones temporales, emitiendo una bandera de "alerta" si se detectan incumplimientos.
5. **Dashboard (SSE / Polling):** El frontend realiza "Short Polling" (cada 2 segundos al endpoint `/api/state`) y un stream de video asíncrono (`multipart/x-mixed-replace`) para mostrar el video anotado y las estadísticas en tiempo real sin recargar la página.
6. **Reporte (LLM):** El usuario en el dashboard solicita un reporte histórico. Flask hace una agregación (GROUP BY) en SQLite para las fechas solicitadas y hace un POST a la API de Groq para obtener el texto interpretativo, permitiendo posteriormente la descarga vía ReportLab.

### 3.2 El Conjunto de Datos (Dataset) y Entrenamiento
Para entrenar el modelo de detección (proceso automatizado en el script `entrenar_modelo.py`), se utilizó un dataset de imágenes públicas etiquetadas obtenidas mediante la API de **Roboflow** (proyecto "mask-wearing"). 
**Metodología de Entrenamiento:**
- **Modelo Base:** `yolov8n.pt` (transfer learning).
- **Hiperparámetros:** 25 Épocas (Epochs), Batch Size de 8, Tamaño de imagen (imgsz) de 640x640 pixeles.
- **Aumento de Datos (Data Augmentation):** Aplicado internamente por Ultralytics durante el entrenamiento (modificaciones de tono, saturación, brillo, recortes y espejado horizontal) para hacer al modelo robusto ante cámaras de baja calidad o cambios de luz.

### 3.3 Diseño del Modelo de Base de Datos
Se implementó una base de datos liviana en SQLite (`bioseguridad.db`). La estructura busca almacenar un muestreo de los estados del tracker a lo largo del tiempo.
- **Tabla `detecciones`:**
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `timestamp` (TEXT): Almacena la fecha y hora en formato ISO o YYYY-MM-DD HH:MM:SS.
  - `total` (INTEGER): Total de detecciones generales en la captura.
  - `con_mascarilla` (INTEGER): Cantidad de detecciones cumpliendo la norma.
  - `sin_mascarilla` (INTEGER): Cantidad de detecciones incumpliendo.
  - `alerta` (INTEGER): Bandera booleana (1 o 0) que indica si se disparó una alerta por incumplimiento en ese timestamp.
  - `porcentaje_con` y `porcentaje_sin` (REAL): Almacenan el porcentaje ya calculado para evitar cómputo extra en consultas grandes.

---

## 4. Implementación y Desarrollo

### 4.1 Módulo Principal (Backend y Rutas)
El archivo principal es `app.py`. En él se define la estructura de Flask. Existe un diccionario global `STATE` que actúa como memoria de estado volátil. Se implementó un generador de streaming `video_feed` que lee bytes de imágenes (`latest_frame`) y las envía al navegador usando el formato `multipart/x-mixed-replace` para crear la ilusión de video fluido. 
El endpoint `/api/state` devuelve un payload JSON limpio con las métricas diarias y en tiempo real, lo que permite que Javascript actualice el DOM de manera eficiente sin interrumpir el stream de video.

### 4.2 Lógica del Object Tracking
El algoritmo presente en `detector_mascarillas.py` (`SimpleTracker`) maneja un ciclo de vida para los objetos detectados.
- **Registro:** Si un objeto no coincide con ningún centroide rastreado anterior (basado en un umbral de distancia `dist_threshold=90`), se registra como nueva entidad.
- **Actualización:** Los rastros activos se emparejan con las nuevas detecciones minimizando la distancia euclidiana (implementando un enfoque "greedy" de asignación).
- **Desaparición:** Si un rastro no se asocia a ninguna detección por `max_missed=5` cuadros consecutivos, es eliminado del conteo.
Además, se implementaron pruebas unitarias (`tests/test_tracker.py`) utilizando la librería `unittest` para asegurar que el conteo en objetos estacionarios no se incremente erróneamente con el paso de los frames.

### 4.3 Módulo de Generación de Reportes PDF e IA
Cuando un usuario consulta el historial (vista `/logs`), interactúa con el endpoint `/api/generate_ai_report`. El servidor Flask actúa de proxy, inyectando la información tabular al modelo de IA:
```python
prompt = f"""
Eres un asistente de IA experto en seguridad industrial y bioseguridad.
Datos del periodo: {rango}
Detecciones CON mascarilla: {con_mascarilla} ({porcentaje_con}%)
Detecciones SIN mascarilla: {sin_mascarilla} ({porcentaje_sin}%)
...
Genera un reporte corto y profesional (máximo 3 párrafos cortos) interpretando los datos...
"""
```
Tras obtener la respuesta en Markdown, el usuario puede exportarla invocando `/api/export_report_pdf`. Este endpoint toma el texto en Markdown, lo procesa mediante expresiones regulares simples (para convertir negritas y cursivas a etiquetas HTML limitadas) y utiliza la librería `ReportLab` (`SimpleDocTemplate`, `Table`, `Paragraph`) para generar un documento PDF estilizado, con tablas de colores corporativos y tipografía profesional, devolviéndolo al navegador como una cadena en base64 para descarga directa.

---

## 5. Resultados y Pruebas

### 5.1 Rendimiento del Modelo de Visión y Sistema
El modelo `yolov8n` fue capaz de procesar el flujo de video (a 640x640) de manera eficiente en CPU, sin retrasar significativamente la respuesta del servidor web Flask gracias a la arquitectura multi-hilo (un hilo dedicado exclusivamente al procesamiento de *frames*).
Las métricas arrojadas en el módulo demostraron que la adición del `SimpleTracker` es indispensable. Sin él, el sistema contaría a la misma persona cientos de veces (una por cada frame procesado). Al separar la métrica "Detecciones del modelo" vs "Personas reales rastreadas" en el Dashboard, el usuario obtiene una perspectiva mucho más precisa de la situación real de afluencia.

### 5.2 Casos de Uso (Demostración Visual)
*(Nota: Añadir aquí capturas de pantalla del proyecto funcionando para evidenciar el trabajo)*
1. **Vista en vivo (`/`):** Captura de la pantalla "Vista en Vivo" evidenciando el reconocimiento facial de varias personas y sus correspondientes identificadores del *Tracker* sobrepuestos (texto y cajas de color verde/rojo).
2. **Dashboard de Métricas (`/metrics`):** Captura de pantalla de la interfaz con paneles estilo "Dark Mode" mostrando los gráficos de anillo (Chart.js) y las sugerencias automatizadas ("Incrementar controles", "Cumplimiento estable") renderizadas en la parte inferior basadas en el estado del día.
3. **Análisis e Historial (`/logs`):** Captura del formulario de búsqueda por fechas donde se logre apreciar el panel de resultados, evidenciando el análisis textual detallado devuelto por la Inteligencia Artificial (Llama 3.1) e idealmente, una captura parcial del archivo PDF exportado.

### 5.3 Análisis de Errores / Limitaciones Encontradas
1. **Oclusiones y Movimiento Rápido:** Si una persona gira la cara de perfil extremo o se mueve a alta velocidad y sale del cuadro temporalmente, el `SimpleTracker` puede perder el ID original. Al reaparecer, la cuenta como una nueva persona.
2. **Variaciones de Iluminación:** El modelo es sensible a condiciones de extremo contraluz, generando posibles "falsos negativos" donde una persona con mascarilla no sea detectada o se clasifique incorrectamente.
3. **Latencia del LLM:** La generación del reporte XAI depende del tiempo de respuesta del servidor externo (Groq). Si el servidor está bajo carga o el internet se desconecta, la funcionalidad de análisis histórico se inactiva (aunque la base de datos local y detección en tiempo real siguen operando con normalidad).

---

## 6. Conclusiones y Trabajos Futuros

### 6.1 Conclusiones Generales
El proyecto cumplió íntegramente con los objetivos planteados, demostrando que es posible integrar de manera armoniosa flujos de trabajo pesados (Deep Learning y Computer Vision) junto con aplicaciones web en tiempo real bajo el framework Flask.
El aporte más destacado fue la integración de Inteligencia Artificial Generativa. Se validó que aplicar una capa de *LLM* por sobre bases de datos tradicionales en aplicaciones industriales reduce considerablemente la fricción en la toma de decisiones, proveyendo al personal directivo no solo del "qué" (los datos), sino del "por qué" y el "qué hacer" de forma instantánea.

### 6.2 Trabajos Futuros y Mejoras Propuestas
Si se contara con mayor tiempo y recursos, el proyecto podría escalarse en las siguientes vertientes:
1. **Soporte de Flujos RTSP/IP:** Adaptar el script principal para orquestar la ingesta paralela de flujos de video provenientes de cámaras de seguridad perimetrales (CCTV) conectadas por red, utilizando librerías como *Celery* para manejo de colas de procesamiento de video.
2. **Anonimización Dinámica (Privacy by Design):** Por normativas de privacidad (ej. GDPR), se sugiere implementar un filtro (Gaussian Blur de OpenCV) sobre los rostros que sí cumplen la normativa, pixelando su identidad antes de retransmitir el flujo de video al frontend.
3. **Sistema de Alertas Multi-Canal:** Expandir el backend para que, si el sistema detecta un incumplimiento grave (ej: 5 personas seguidas sin mascarilla), envíe una notificación instantánea al equipo de seguridad mediante un bot de Telegram, Slack o WhatsApp.

---

## 7. Referencias Bibliográficas
- Jocher, G., Chaurasia, A., & Qiu, J. (2023). *Ultralytics YOLOv8*. Obtenido de https://github.com/ultralytics/ultralytics
- Bradski, G. (2000). *The OpenCV Library*. Dr. Dobb's Journal of Software Tools.
- Meta. (2024). *Llama 3 Model Card*. Obtenido de OpenAI/Groq Docs (https://console.groq.com/docs).
- Roboflow. (2022). *Mask Wearing Dataset*. Obtenido de Universe Roboflow: https://universe.roboflow.com/joseph-nelson/mask-wearing

## 8. Anexos
- **Repositorio de Código del Proyecto:** [Enlace a GitHub / GitLab]
- **Enlace a Video Demostración:** [Enlace a YouTube / Loom (Opcional pero Recomendado)]
