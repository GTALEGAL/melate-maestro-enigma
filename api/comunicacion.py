from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
import os
from collections import Counter
from itertools import combinations
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            # Ruta de datos
            ruta = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(ruta)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
            df['FECHA_DT'] = pd.to_datetime(df['FECHA'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=cols)

            # Análisis de día
            proximo_idx = {0:2, 1:2, 2:4, 3:4, 4:6, 5:6, 6:2}[datetime.now().weekday()]
            tipo = {2: "MIÉRCOLES", 4: "VIERNES", 6: "DOMINGO"}[proximo_idx]

            # Procesamiento
            f_glo = Counter(df[cols].values.flatten())
            ult_nums = set(df.iloc[0][cols].values)
            pares = [set(p) for p in combinations(ult_nums, 2)]
            
            marea = df.head(800)
            seg_glo, seg_esp = [], []
            for i in range(1, len(marea)):
                h, s = set(marea.iloc[i][cols].values), marea.iloc[i-1][cols].values
                if any(p.issubset(h) for p in pares):
                    seg_glo.extend(s)
                    if marea.iloc[i]['FECHA_DT'].weekday() == proximo_idx:
                        seg_esp.extend(s)

            # Generar listas
            c1 = [int(n) for n, c in f_glo.most_common(7)]
            c5 = [int(n) for n, c in Counter(seg_glo).most_common(7)] if seg_glo else c1
            f_esp_c = Counter(seg_esp)
            f_glo_c = Counter(seg_glo)
            
            score = {n: (f_esp_c[n]*12)+(f_glo_c[n]*6)+(f_glo[n]*0.2) for n in range(1, 57)}
            c10 = sorted(score, key=score.get, reverse=True)[:7]

            # RESPUESTA PLANA (Sin carpetas raras)
            res = {
                "status": "OK",
                "concurso": int(df.iloc[0]['CONCURSO']),
                "proximo": tipo,
                "ultimo": [int(x) for x in df.iloc[0][cols].values],
                "c1": sorted(c1),
                "c5": sorted(c5),
                "c10": sorted([int(x) for x in c10])
            }
        except Exception as e:
            res = {"status": "ERROR", "mensaje": str(e)}

        self.wfile.write(json.dumps(res).encode())
