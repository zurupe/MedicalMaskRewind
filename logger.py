import json
import os
import sqlite3
from datetime import datetime


class BioseguridadLogger:
    def __init__(self, filename="registro_bioseguridad.txt", state_filename="registro_bioseguridad.json", db_path="bioseguridad.db"):
        self.filename = filename
        self.state_filename = state_filename
        self.db_path = db_path
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

    def registrar(self, total, con_mascarilla, sin_mascarilla, incorrecta):
        if total == 0:
            return {
                "total": 0,
                "con_mascarilla": 0,
                "sin_mascarilla": 0,
                "alerta": False,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }

        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M:%S")
        tiempo_actual = f"{fecha} {hora}"

        if self.ultimo_registro_tiempo == tiempo_actual:
            return self.obtener_resumen()

        self.ultimo_registro_tiempo = tiempo_actual

        alerta = sin_mascarilla > 0
        alerta_txt = " ⚠️ ALERTA: Incumplimiento detectado" if alerta else ""
        linea_registro = f"[{tiempo_actual}] Personas en escena: {total} | Con Mascarilla: {con_mascarilla} | Sin Mascarilla: {sin_mascarilla}{alerta_txt}\n"

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
        }
        self._guardar_estado(resumen)
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

    def consultar_por_fechas(self, start_date, end_date):
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
            start_timestamp = f"{start_date} 00:00:00"
            end_timestamp = f"{end_date} 23:59:59"

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT timestamp, total, con_mascarilla, sin_mascarilla,
                       porcentaje_con, porcentaje_sin, alerta
                FROM detecciones
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
                """,
                (start_timestamp, end_timestamp),
            )
            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "timestamp": row["timestamp"],
                    "total": row["total"],
                    "con_mascarilla": row["con_mascarilla"],
                    "sin_mascarilla": row["sin_mascarilla"],
                    "porcentaje_con": row["porcentaje_con"],
                    "porcentaje_sin": row["porcentaje_sin"],
                    "alerta": bool(row["alerta"]),
                }
                for row in rows
            ]
        except Exception as exc:
            print(f"Error al consultar historial por fechas: {exc}")
            return []

    def obtener_resumen_diario(self):
        conn = sqlite3.connect(self.db_path)
        today = datetime.now().strftime("%Y-%m-%d")
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
        }
