import json
import os
import sqlite3
from datetime import datetime


class BioseguridadLogger:
    def __init__(self, filename="registro_bioseguridad.txt", state_filename="registro_bioseguridad.json", db_path="bioseguridad.db"):
        self.filename = filename
        self.state_filename = state_filename
        self.db_path = db_path
        self.historial_filename = state_filename.replace('.json', '_historial.json')
        self.ultimo_registro_tiempo = None
        self._inicializar_archivo()

    def _inicializar_archivo(self):
        with open(self.filename, mode='w', encoding='utf-8') as file:
            file.write("============================================================\n")
            file.write(f" REPORTE DE BIOSEGURIDAD - INICIADO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("============================================================\n\n")

        self._crear_tabla_db()
        self._guardar_estado({
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total": 0,
            "con_mascarilla": 0,
            "sin_mascarilla": 0,
            "porcentaje_con": 0.0,
            "porcentaje_sin": 0.0,
            "alerta": False,
            "registros": 0,
            "detecciones_modelo": 0,
            "personas_reales": 0,
        })

    def _crear_tabla_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS detecciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            total INTEGER NOT NULL,
            con_mascarilla INTEGER NOT NULL,
            sin_mascarilla INTEGER NOT NULL,
            alerta INTEGER NOT NULL,
            porcentaje_con REAL NOT NULL,
            porcentaje_sin REAL NOT NULL
        )
        """)
        conn.commit()
        conn.close()

    def registrar(self, total, con_mascarilla, sin_mascarilla, incorrecta, detecciones_modelo=None, personas_reales=None):
        if total == 0:
            resumen = {
                "total": 0,
                "con_mascarilla": 0,
                "sin_mascarilla": 0,
                "alerta": False,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "detecciones_modelo": 0,
                "personas_reales": 0,
            }
            self._guardar_estado(resumen)
            self._guardar_historial(resumen)
            return resumen

        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M:%S")
        tiempo_actual = f"{fecha} {hora}"

        if self.ultimo_registro_tiempo == tiempo_actual:
            return self.obtener_resumen()

        self.ultimo_registro_tiempo = tiempo_actual

        alerta = sin_mascarilla > 0
        alerta_txt = " ⚠️ ALERTA: Incumplimiento detectado" if alerta else ""
        detecciones_modelo = detecciones_modelo if detecciones_modelo is not None else total
        personas_reales = personas_reales if personas_reales is not None else total
        linea_registro = f"[{tiempo_actual}] Personas en escena: {personas_reales} | Con Mascarilla: {con_mascarilla} | Sin Mascarilla: {sin_mascarilla} | Detecciones modelo: {detecciones_modelo} | Personas reales rastreadas: {personas_reales}{alerta_txt}\n"

        with open(self.filename, mode='a', encoding='utf-8') as file:
            file.write(linea_registro)

        resumen = {
            "timestamp": tiempo_actual,
            "total": total,
            "con_mascarilla": con_mascarilla,
            "sin_mascarilla": sin_mascarilla,
            "alerta": alerta,
            "porcentaje_con": round((con_mascarilla / total) * 100, 2) if total else 0.0,
            "porcentaje_sin": round((sin_mascarilla / total) * 100, 2) if total else 0.0,
            "registros": self._contar_registros(),
            "detecciones_modelo": detecciones_modelo,
            "personas_reales": personas_reales,
        }
        self._guardar_estado(resumen)
        self._guardar_historial(resumen)
        self._guardar_en_db(resumen)

        if alerta:
            print(f"⚠️ [ALERTA - {hora}] Se han detectado {sin_mascarilla} persona(s) sin mascarilla en el área.")

        return resumen

    def _contar_registros(self):
        if not os.path.exists(self.filename):
            return 0
        with open(self.filename, mode='r', encoding='utf-8') as file:
            return sum(1 for line in file if line.startswith("["))

    def _guardar_en_db(self, resumen):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO detecciones (timestamp, total, con_mascarilla, sin_mascarilla, alerta, porcentaje_con, porcentaje_sin) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                resumen["timestamp"],
                resumen["total"],
                resumen["con_mascarilla"],
                resumen["sin_mascarilla"],
                int(resumen["alerta"]),
                resumen["porcentaje_con"],
                resumen["porcentaje_sin"],
            ),
        )
        conn.commit()
        conn.close()

    def _guardar_historial(self, resumen):
        historial = self._leer_historial()
        historial.append(resumen)
        with open(self.historial_filename, mode='w', encoding='utf-8') as file:
            json.dump(historial, file, indent=2)

    def _leer_historial(self):
        if not os.path.exists(self.historial_filename):
            return []
        with open(self.historial_filename, mode='r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []

    def _guardar_estado(self, resumen):
        with open(self.state_filename, mode='w', encoding='utf-8') as file:
            json.dump(resumen, file, indent=2)

    def obtener_resumen(self):
        if not os.path.exists(self.state_filename):
            return {
                "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "total": 0,
                "con_mascarilla": 0,
                "sin_mascarilla": 0,
                "porcentaje_con": 0.0,
                "porcentaje_sin": 0.0,
                "alerta": False,
                "registros": 0,
            }

        with open(self.state_filename, mode='r', encoding='utf-8') as file:
            return json.load(file)

    def leer_registros(self, limit=20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT timestamp, total, con_mascarilla, sin_mascarilla, alerta FROM detecciones ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            f"[{row[0]}] Personas: {row[1]} | Con: {row[2]} | Sin: {row[3]}" + (" ⚠️" if row[4] else "")
            for row in rows
        ][::-1]

    def obtener_alertas(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT timestamp, sin_mascarilla FROM detecciones WHERE alerta = 1 ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"timestamp": row[0], "sin_mascarilla": row[1]} for row in rows]

    def obtener_resumen_diario(self):
        today = datetime.now().strftime("%Y-%m-%d")
        historial = self._leer_historial()
        items = [item for item in historial if str(item.get("timestamp", "")).startswith(today)]

        if not items:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "SELECT COALESCE(SUM(total), 0), COALESCE(SUM(con_mascarilla), 0), COALESCE(SUM(sin_mascarilla), 0) FROM detecciones WHERE substr(timestamp, 1, 10) = ?",
                (today,),
            )
            row = cursor.fetchone()
            conn.close()

            total = int(row[0] or 0)
            con_mascarilla = int(row[1] or 0)
            sin_mascarilla = int(row[2] or 0)
            return {
                "total": total,
                "con_mascarilla": con_mascarilla,
                "sin_mascarilla": sin_mascarilla,
                "porcentaje_con": round((con_mascarilla / total) * 100, 2) if total else 0.0,
                "porcentaje_sin": round((sin_mascarilla / total) * 100, 2) if total else 0.0,
                "detecciones_modelo": total,
                "personas_reales": total,
            }

        total = sum(int(item.get("total", 0) or 0) for item in items)
        con_mascarilla = sum(int(item.get("con_mascarilla", 0) or 0) for item in items)
        sin_mascarilla = sum(int(item.get("sin_mascarilla", 0) or 0) for item in items)
        detecciones_modelo = sum(int(item.get("detecciones_modelo", 0) or 0) for item in items)
        personas_reales = sum(int(item.get("personas_reales", 0) or 0) for item in items)

        return {
            "total": total,
            "con_mascarilla": con_mascarilla,
            "sin_mascarilla": sin_mascarilla,
            "porcentaje_con": round((con_mascarilla / total) * 100, 2) if total else 0.0,
            "porcentaje_sin": round((sin_mascarilla / total) * 100, 2) if total else 0.0,
            "detecciones_modelo": detecciones_modelo,
            "personas_reales": personas_reales,
        }

    def obtener_resumen_por_fechas(self, fecha_inicio, fecha_fin):
        historial = self._leer_historial()
        items = [
            item for item in historial
            if fecha_inicio <= str(item.get("timestamp", "")).split(" ")[0] <= fecha_fin
        ]

        total = sum(int(item.get("total", 0) or 0) for item in items)
        con_mascarilla = sum(int(item.get("con_mascarilla", 0) or 0) for item in items)
        sin_mascarilla = sum(int(item.get("sin_mascarilla", 0) or 0) for item in items)
        detecciones_modelo = sum(int(item.get("detecciones_modelo", 0) or 0) for item in items)
        personas_reales = sum(int(item.get("personas_reales", 0) or 0) for item in items)

        daily_data = []
        by_day = {}
        for item in items:
            fecha = str(item.get("timestamp", "")).split(" ")[0]
            if fecha not in by_day:
                by_day[fecha] = {"fecha": fecha, "total": 0, "con": 0, "sin": 0}
            by_day[fecha]["total"] += int(item.get("total", 0) or 0)
            by_day[fecha]["con"] += int(item.get("con_mascarilla", 0) or 0)
            by_day[fecha]["sin"] += int(item.get("sin_mascarilla", 0) or 0)

        for fecha in sorted(by_day.keys(), reverse=True):
            d = by_day[fecha]
            d_total = int(d["total"] or 0)
            d_con = int(d["con"] or 0)
            d_sin = int(d["sin"] or 0)
            daily_data.append({
                "fecha": fecha,
                "total": d_total,
                "con": d_con,
                "sin": d_sin,
                "pct_con": round((d_con / d_total) * 100, 2) if d_total else 0.0,
                "pct_sin": round((d_sin / d_total) * 100, 2) if d_total else 0.0
            })

        return {
            "rango": f"{fecha_inicio} a {fecha_fin}",
            "total": total,
            "con_mascarilla": con_mascarilla,
            "sin_mascarilla": sin_mascarilla,
            "porcentaje_con": round((con_mascarilla / total) * 100, 2) if total else 0.0,
            "porcentaje_sin": round((sin_mascarilla / total) * 100, 2) if total else 0.0,
            "detecciones_modelo": detecciones_modelo,
            "personas_reales": personas_reales,
            "detalles": daily_data
        }
