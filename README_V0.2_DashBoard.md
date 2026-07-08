# Informe de cambios y mejoras

## Resumen
Se ha reestructurado la base del proyecto para dejarlo preparado para un uso más serio como sistema de monitoreo de bioseguridad en un ingreso hospitalario.

## Cambios principales
- Se añadió un backend web simple con Flask para exponer métricas del sistema.
- Se creó un dashboard web básico que muestra:
  - última actualización
  - personas detectadas
  - conteo con y sin mascarilla
  - porcentaje de cumplimiento
  - últimos registros del logger
- Se adaptó el logger para que además de escribir en texto también guarde un estado JSON reutilizable por el frontend.
- Se preparó el detector para que pueda enviar métricas a un callback y servir tanto a ventana OpenCV como a backend web.

## Mejoras respecto a la versión anterior
- El proyecto pasa de ser una demo de escritorio a una base preparada para monitorización continua.
- La arquitectura ahora separa mejor:
  - detección visual
  - registro de eventos
  - exposición web de métricas
- El frontend queda listo para crecer con gráficos, alertas y una interfaz más completa.

## Archivos que quedan como núcleo del proyecto
- [main.py](main.py)
- [detector_mascarillas.py](detector_mascarillas.py)
- [logger.py](logger.py)
- [app.py](app.py)

## Próximos pasos recomendados
1. Sustituir el dashboard actual por una interfaz más visual con gráficos.
2. Persistir datos en una base de datos en vez de archivos de texto/JSON.
3. Añadir autenticación y roles para personal de vigilancia.
4. Implementar anonimización y privacidad para la imagen.

## Cómo ejecutar el proyecto (local)

1. Instala las dependencias (usa un entorno virtual recomendado):

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. Ejecuta el dashboard web:

```bash
python app.py
# Luego abre http://127.0.0.1:5000 en el navegador
```

Notas:
- Asegúrate de que `best_mask_mrisdi.pt` esté en la raíz del proyecto.
- Si la cámara está en uso por otra aplicación, cierra esa app o ajusta el índice de `VideoCapture` en `detector_mascarillas.py`.

## Archivos añadidos/actualizados
- `app.py`: backend Flask + dashboard
- `templates/dashboard.html`: plantilla separada
- `logger.py`: guardado a SQLite + resumen diario

Si quieres, genero también un changelog con los diffs aplicados.
