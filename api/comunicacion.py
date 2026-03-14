from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
import os
from collections import Counter
from itertools import combinations
from datetime import datetime, timedelta

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
            
            # --- LÓGICA DE FECHA DEL PRÓXIMO SORTEO ---
            # Asumimos que la columna de fecha se llama 'FECHA'
            ultima_fecha_str = str(df.iloc[0]['FECHA'])
            try:
                # Intentar detectar el formato de fecha (ajustar si es necesario)
                fecha_dt = pd.to_datetime(ultima_fecha_str)
                # Días de sorteo: Miércoles(2), Viernes(4), Domingo(6)
                proximo = fecha_dt + timedelta(days=1)
                while proximo.weekday() not in [2, 4, 6]:
                    proximo += timedelta(days=1)
                fecha_proximo = proximo.strftime('%d/%m/%Y')
            except:
                fecha_proximo = "Pendiente de Actualización"

            # --- ANÁLISIS DE CAPAS (Igual al anterior pero optimizado) ---
            marea = df.head(600)
            f_gen = Counter(df[cols].values.flatten())
            ult_nums = set(df.iloc[0][cols].values)
            pares_ult = [set(p) for p in combinations(ult_nums, 2)]
            trios_ult = [set(t) for t in combinations(ult_nums, 3)]
            
            seg_pares, seg_trios = [], []
            for i in range(1, len(marea)):
                hist = set(marea.iloc[i][cols].values)
                sig = marea.iloc[i-1][cols].values
                if any(p.issubset(hist) for p in pares_ult): seg_pares.extend(sig)
                if any(t.issubset(hist) for t in trios_ult): seg_trios.extend(sig)

            f_p, f_t = Counter(seg_pares), Counter(seg_trios)
            c1 = [int(n) for n, c in f_gen.most_common(7)]
            c5 = [int(n) for n, c in f_p.most_common(7)] if seg_pares else c1
            c6 = [int(n) for n, c in f_t.most_common(7)] if seg_trios else c1
            
            score = {n: round((f_t[n]*15) + (f_p[n]*7) + (f_gen[n]*0.2), 2) for n in range(1, 57)}
            c10 = sorted(score, key=score.get, reverse=True)[:7]

            res = {
                "concurso": int(df.iloc[0]['CONCURSO']),
                "proximo_sorteo": fecha_proximo,
                "capas": {
                    "c1": sorted(c1), "c5": sorted(c5), "c6": sorted(c6), "c10": sorted([int(x) for x in c10])
                }
            }
        except Exception as e:
            res = {"error": str(e)}
        self.wfile.write(json.dumps(res).encode())
