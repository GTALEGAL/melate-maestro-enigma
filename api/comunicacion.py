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
            ruta = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(ruta)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
            
            # 1. CAPA 1: FRECUENCIA GENERAL (Últimos 1000)
            f_gen = Counter(df[cols].values.flatten())
            c1 = [int(n) for n, c in f_gen.most_common(7)]
            
            # 2. CAPA 5 Y 6: ANÁLISIS DE SEGUIDORES
            ult_nums = set(df.iloc[0][cols].values)
            pares_ult = [set(p) for p in combinations(ult_nums, 2)]
            trios_ult = [set(t) for t in combinations(ult_nums, 3)]
            
            seg_pares = []
            seg_trios = []
            marea = df.head(600) # Profundidad balanceada
            
            for i in range(1, len(marea)):
                hist = set(marea.iloc[i][cols].values)
                sig = marea.iloc[i-1][cols].values
                if any(p.issubset(hist) for p in pares_ult):
                    seg_pares.extend(sig)
                if any(t.issubset(hist) for t in trios_ult):
                    seg_trios.extend(sig)

            # Resultados por capa
            f_pares = Counter(seg_pares)
            f_trios = Counter(seg_trios)
            
            c5 = [int(n) for n, c in f_pares.most_common(7)] if seg_pares else c1
            c6 = [int(n) for n, c in f_trios.most_common(7)] if seg_trios else c1
            
            # 3. CAPA 10: SCORE MAESTRO (PESOS COMBINADOS)
            score = {}
            for n in range(1, 57):
                puntos = (f_trios[n] * 15) + (f_pares[n] * 7) + (f_gen[n] * 0.2)
                score[n] = round(puntos, 2)
            
            c10 = sorted(score, key=score.get, reverse=True)[:7]

            res = {
                "concurso": int(df.iloc[0]['CONCURSO']),
                "capas": {
                    "c1": sorted(c1),
                    "c5": sorted(c5),
                    "c6": sorted(c6),
                    "c10": sorted([int(x) for x in c10])
                },
                "status": "ANALISIS_PROFUNDO_OK"
            }
        except Exception as e:
            res = {"error": str(e)}
        
        self.wfile.write(json.dumps(res).encode())
