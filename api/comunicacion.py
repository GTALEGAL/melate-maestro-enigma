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
            # Carga de datos
            ruta_csv = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(ruta_csv)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']

            # --- CAPA 1: FRECUENCIA GENERAL (Últimos 500) ---
            marea = df.head(500)
            frec_numeros = marea[cols].values.flatten()
            c1_pool = [int(n) for n, c in Counter(frec_numeros).most_common(7)]
            c1_pool.sort()

            # --- CAPA 5: SECUENCIA POR PARES ---
            ult_nums = set(df.iloc[0][cols].values)
            pares_ult = list(combinations(ult_nums, 2))
            seguidores = []
            
            # Analizamos historial para ver qué salió después de esos pares
            marea_profunda = df.head(1000)
            for i in range(1, len(marea_profunda)):
                sorteo_hist = set(marea_profunda.iloc[i][cols].values)
                # Si el sorteo histórico contiene alguno de los pares del último sorteo
                if any(set(p).issubset(sorteo_hist) for p in pares_ult):
                    seguidores.extend(marea_profunda.iloc[i-1][cols].values)
            
            if seguidores:
                c5_pool = [int(n) for n, c in Counter(seguidores).most_common(7)]
            else:
                c5_pool = c1_pool
            c5_pool.sort()

            respuesta = {
                "equipo": "MAESTRO-ALFA",
                "concurso": int(df.iloc[0]['CONCURSO']),
                "capas": {
                    "c1_frecuencia": c1_pool,
                    "c5_pares": c5_pool
                },
                "status": "SISTEMA_MULTI_CAPA_OK"
            }

        except Exception as e:
            respuesta = {"error": str(e), "status": "ERROR_MOTOR"}

        self.wfile.write(json.dumps(respuesta).encode())
