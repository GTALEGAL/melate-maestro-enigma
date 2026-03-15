from http.server import BaseHTTPRequestHandler
import json
import pymysql
import os
from collections import Counter
from datetime import datetime

# ── Credenciales MySQL ──────────────────────────────────────────
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'dreamdia_melate_db')
DB_USER = os.environ.get('DB_USER', 'dreamdia_cgt')
DB_PASS = os.environ.get('DB_PASS', 'w0h#7tVAMidh(jO0')
# ───────────────────────────────────────────────────────────────

def get_data():
    conn = pymysql.connect(
        host=DB_HOST, user=DB_USER,
        password=DB_PASS, database=DB_NAME,
        charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT concurso, fecha, r1, r2, r3, r4, r5, r6, r7
                FROM sorteos
                ORDER BY concurso DESC
            """)
            rows = cur.fetchall()
    return rows

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            rows = get_data()
            cols = ['r1','r2','r3','r4','r5','r6','r7']

            # ── Identificar próximo sorteo ──
            hoy_idx     = datetime.now().weekday()
            proximo_idx = 2
            for d in [2, 4, 6]:
                if d > hoy_idx:
                    proximo_idx = d
                    break
            nombre_dia = {2: "MIÉRCOLES", 4: "VIERNES", 6: "DOMINGO"}[proximo_idx]

            # ── Todos los números planos ──
            todos = [row[c] for row in rows for c in cols]
            f_global = Counter(todos)

            # ── C1: Frecuencia global ──
            c1_frec = [int(n) for n, _ in f_global.most_common(7)]

            # ── C5: Resonancia (seguidores del último sorteo) ──
            ultimos = [rows[0][c] for c in cols]
            set_ultimos = set(ultimos)

            seguidores = []
            for i in range(1, min(500, len(rows) - 1)):
                pasados = set(rows[i][c] for c in cols)
                if set_ultimos & pasados:
                    seguidores.extend(rows[i-1][c] for c in cols)

            f_seguidores = Counter(seguidores)
            c5_seq = [int(n) for n, _ in f_seguidores.most_common(7)] if seguidores else c1_frec

            # ── C10: Score maestro ponderado ──
            numeros_dia = [
                row[c]
                for row in rows
                if row['fecha'] and row['fecha'].weekday() == proximo_idx
                for c in cols
            ][:700]

            score = {}
            for n in range(1, 57):
                p_global     = f_global[n]     * 0.5
                p_resonancia = f_seguidores[n] * 2.0
                p_dia        = 5 if n in numeros_dia else 0
                score[n]     = round(p_global + p_resonancia + p_dia, 2)

            c10_score = sorted(score, key=score.get, reverse=True)[:7]

            respuesta = {
                "status": "OK",
                "mensaje": "MOTOR ENIGMA - ESCANEO COMPLETO",
                "proximo_sorteo": nombre_dia,
                "info": {
                    "concurso": int(rows[0]['concurso']),
                    "numeros":  [int(rows[0][c]) for c in cols]
                },
                "analisis": {
                    "c1_frec":      sorted(c1_frec),
                    "c5_pares_seq": sorted(c5_seq),
                    "c10_score":    sorted([int(x) for x in c10_score]),
                    "confianza":    "ALTA" if len(rows) > 1000 else "MEDIA"
                }
            }

        except Exception as e:
            respuesta = {"status": "ERROR", "mensaje": str(e)}

        self.wfile.write(json.dumps(respuesta, ensure_ascii=False).encode())
