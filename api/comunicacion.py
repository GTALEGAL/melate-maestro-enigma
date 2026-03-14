from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
import os
from collections import Counter
from itertools import combinations

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            # 1. CARGA DE DATOS
            ruta = os.path.join(os.getcwd(), 'datos.csv')
            if not os.path.exists(ruta):
                raise Exception("No se encontro el archivo datos.csv")

            df = pd.read_csv(ruta)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']

            # 2. FILTRO DE DOMINGOS (DNA DEL DÍA)
            # Convertimos la columna FECHA a formato fecha real
            df['FECHA_DT'] = pd.to_datetime(df['FECHA'], dayfirst=True, errors='coerce')
            
            # Filtramos: Solo sorteos donde el día de la semana es domingo (6)
            df_domingos = df[df['FECHA_DT'].dt.weekday == 6].copy()
            total_domingos = len(df_domingos)

            if total_domingos < 10:
                raise Exception(f"Pocos domingos detectados ({total_domingos}). Revisa el formato de fecha en el CSV.")

            # 3. ANÁLISIS DE SEGUIDORES (Solo en Domingos)
            marea = df_domingos.head(500)
            ult_nums = set(df.iloc[0][cols].values) # El gatillo sigue siendo el último sorteo real
            pares_ult = [set(p) for p in combinations(ult_nums, 2)]
            trios_ult = [set(t) for t in combinations(ult_nums, 3)]

            seg_pares = []
            seg_trios = []

            # Buscamos en el historial de domingos qué números salieron DESPUÉS de esos pares/trios
            for i in range(1, len(marea)):
                sorteo_hist = set(marea.iloc[i][cols].values)
                sorteo_sig = marea.iloc[i-1][cols].values
                
                if any(p.issubset(sorteo_hist) for p in pares_ult):
                    seg_pares.extend(sorteo_sig)
                if any(t.issubset(sorteo_hist) for t in trios_ult):
                    seg_trios.extend(sorteo_sig)

            # 4. FRECUENCIA Y SCORE MAESTRO
            f_gen = Counter(df_domingos[cols].values.flatten())
            f_p = Counter(seg_pares)
            f_t = Counter(seg_trios)

            c1 = [int(n) for n, c in f_gen.most_common(7)]
            c5 = [int(n) for n, c in f_p.most_common(7)] if seg_pares else c1
            c6 = [int(n) for n, c in f_t.most_common(7)] if seg_trios else c1

            # Algoritmo Score Maestro (Peso Dominical)
            score = {}
            for n in range(1, 57):
                puntos = (f_t[n] * 15) + (f_p[n] * 7) + (f_gen[n] * 0.2)
                score[n] = round(puntos, 2)
            
            c10 = sorted(score, key=score.get, reverse=True)[:7]

            # 5. RESPUESTA JSON
            respuesta = {
                "concurso": int(df.iloc[0]['CONCURSO']),
                "proximo_sorteo": "DOMINGO 15/03/2026",
                "capas": {
                    "c1": sorted(c1),
                    "c5": sorted(c5),
                    "c6": sorted(c6),
                    "c10": sorted([int(x) for x in c10])
                },
                "debug": {
                    "domingos_analizados": total_domingos,
                    "motor": "Filtro Dominical Activo"
                }
            }

        except Exception as e:
            respuesta = {"error": str(e), "status": "FAIL"}

        self.wfile.write(json.dumps(respuesta).encode())
