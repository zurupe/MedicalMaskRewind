import os
from datetime import datetime

class BioseguridadLogger:
    def __init__(self, filename="registro_bioseguridad.txt"):
        self.filename = filename
        self.ultimo_registro_tiempo = None
        self._inicializar_archivo()

    def _inicializar_archivo(self):
        # Abre en modo 'w' para sobreescribir el archivo cada vez que inicia la app
        with open(self.filename, mode='w', encoding='utf-8') as file:
            file.write("============================================================\n")
            file.write(f" REPORTE DE BIOSEGURIDAD - INICIADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("============================================================\n\n")

    def registrar(self, total, con_mascarilla, sin_mascarilla, incorrecta):
        if total == 0:
            return

        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M:%S")
        tiempo_actual = f"{fecha} {hora}"

        # Evitar registrar múltiples veces en el mismo segundo (útil para la webcam)
        if self.ultimo_registro_tiempo == tiempo_actual:
            return

        self.ultimo_registro_tiempo = tiempo_actual
        
        alerta_txt = " ⚠️ ALERTA: Incumplimiento detectado" if sin_mascarilla > 0 else ""
        
        # Formato de texto mucho más legible y humano
        linea_registro = f"[{tiempo_actual}] Personas en escena: {total} | Con Mascarilla: {con_mascarilla} | Sin Mascarilla: {sin_mascarilla}{alerta_txt}\n"

        # Abre en modo 'a' para ir añadiendo líneas (el archivo ya se vació al inicio)
        with open(self.filename, mode='a', encoding='utf-8') as file:
            file.write(linea_registro)
            
        # Emitir alerta en consola si hay alguien sin mascarilla
        if sin_mascarilla > 0:
            print(f"⚠️ [ALERTA - {hora}] Se han detectado {sin_mascarilla} persona(s) sin mascarilla en el área.")
