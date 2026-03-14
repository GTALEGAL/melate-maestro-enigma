from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
import os
from collections import Counter
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            # 1. LOCALIZACIÓN Y CARGA
            base_path = os.path.dirname(os.path.dirname(__file__))
            ruta = os.path.join(base_path, 'datos.csv')
            if not os.path.exists(ruta):
                ruta = os.path.join(os.getcwd(), 'datos.csv')

            df = pd.read_csv(ruta)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
            df['FECHA_DT'] = pd.to_datetime(df['FECHA'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=cols)

            # 2. IDENTIFICACIÓN DE SORTEO
            hoy_idx = datetime.now().weekday()
            proximo_idx = 2
            for d in [2, 4, 6]:
                if d > hoy_idx:
                    proximo_idx = d
                    break
            
            nombre_dia = {2: "MIÉRCOLES", 4: "VIERNES", 6: "DOMINGO"}[proximo_idx]

            # 3. CAPA 1: FRECUENCIA GLOBAL
            f_global = Counter(df[cols].values.flatten())
            c1_frec = [int(n) for n, c in f_global.most_common(7)]

            # 4. CAPA 5: RESONANCIA (SEGUIDORES)
            ultimos_ganadores = df.iloc[0][cols].values
            seguidores = []
            for i in range(1, 500):
                ganadores_pasados = set(df.iloc[i][cols].values)
                if any(n in ganadores_pasados for n in ultimos_ganadores):
                    seguidores.extend(df.iloc[i-1][cols].values)
            
            f_seguidores = Counter(seguidores)
            c5_seq = [int(n) for n, c in f_seguidores.most_common(7)] if seguidores else c1_frec

            # 5. CAPA 10: SCORE MAESTRO (PONDERADO)
            score = {}
            filtro_dia = df[df['FECHA_DT'].dt.weekday == proximo_idx].head(100)
            numeros_dia = filtro_dia[cols].values.flatten()
            
            for n in range(1, 57):
                p_global = f_global[n] * 0.5
                p_resonancia = f_seguidores[n] * 2.0
                p_dia = 5 if n in numeros_dia else 0
                score[n] = round(p_global + p_resonancia + p_dia, 2)

            c10_score = sorted(score, key=score.get, reverse=True)[:7]

            # --- RESPUESTA COMPLETA ---
            respuesta = {
                "status": "OK",
                "mensaje": "MOTOR ENIGMA - ESCANEO COMPLETO",
                "proximo_sorteo": nombre_dia,
                "info": {
                    "concurso": int(df.iloc[0]['CONCURSO']),
                    "numeros": [int(x) for x in ultimos_ganadores]
                },
                "analisis": {
                    "c1_frec": sorted(c1_frec),
                    "c5_pares_seq": sorted(c5_seq),
                    "c10_score": sorted([int(x) for x in c10_score]),
                    "confianza": "ALTA" if len(df) > 1000 else "MEDIA"
                }
            }

        except Exception as e:
            respuesta = {"status": "ERROR", "mensaje": str(e)}

        self.wfile.write(json.dumps(respuesta).encode())
