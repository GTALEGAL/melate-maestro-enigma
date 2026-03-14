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
            ruta_csv = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(ruta_csv)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
            
            # Datos base
            marea = df.head(1000)
            ult_nums = set(df.iloc[0][cols].values)
            pares_ult = list(combinations(ult_nums, 2))
            trios_ult = list(combinations(ult_nums, 3))

            # --- CAPA 1: FRECUENCIA ---
            f_gen = Counter(df[cols].values.flatten())
            c1 = [int(n) for n, c in f_gen.most_common(7)]

            # --- CAPAS DE SECUENCIA (Pares y Tríos) ---
            seg_pares = []
            seg_trios = []
            for i in range(1, len(marea)):
                sorteo_h = set(marea.iloc[i][cols].values)
                if any(set(p).issubset(sorteo_h) for p in pares_ult):
                    seg_pares.extend(marea.iloc[i-1][cols].values)
                if any(set(t).issubset(sorteo_h) for t in trios_ult):
                    seg_trios.extend(marea.iloc[i-1][cols].values)

            f_pares = Counter(seg_pares)
            f_trios = Counter(seg_trios)
            
            c5 = [int(n) for n, c in f_pares.most_common(7)] if seg_pares else c1
            c6 = [int(n) for n, c in f_trios.most_common(7)] if seg_trios else c1

            # --- CAPA 10: SCORE MAESTRO (El Algoritmo Final) ---
            score_final = {}
            for n in range(1, 57):
                # Peso: Tríos(x10) + Pares(x5) + Frecuencia(x0.1)
                puntos = (f_trios[n] * 10) + (f_pares[n] * 5) + (f_gen[n] * 0.1)
                score_final[n] = round(puntos, 2)
            
            c10 = sorted(score_final, key=score_final.get, reverse=True)[:7]

            respuesta = {
                "concurso": int(df.iloc[0]['CONCURSO']),
                "capas": {
                    "c1": sorted(c1),
                    "c5": sorted(c5),
                    "c6": sorted(c6),
                    "c10": sorted(c10)
                }
            }
        except Exception as e:
            respuesta = {"error": str(e)}

        self.wfile.write(json.dumps(respuesta).encode())
