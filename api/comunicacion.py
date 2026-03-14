from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
import os
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            # 1. Ruta y carga básica
            ruta = os.path.join(os.getcwd(), 'datos.csv')
            if not os.path.exists(ruta):
                raise Exception("CSV no encontrado")
            
            df = pd.read_csv(ruta)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
            
            # 2. Análisis ultra-rápido (Frecuencia)
            marea = df.head(500)
            f_gen = Counter(marea[cols].values.flatten())
            c1 = [int(n) for n, c in f_gen.most_common(7)]
            
            # 3. Respuesta de seguridad (Si las capas fallan, mandamos frecuencia en todas)
            # Esto evita que el sistema se muera si no encuentra pares/trios
            respuesta = {
                "concurso": int(df.iloc[0]['CONCURSO']),
                "capas": {
                    "c1": sorted(c1),
                    "c5": sorted(c1), 
                    "c6": sorted(c1),
                    "c10": sorted(c1)
                },
                "status": "MODO_RESURRECCION_OK"
            }

        except Exception as e:
            respuesta = {"error": str(e), "status": "ERROR_CRITICO"}

        self.wfile.write(json.dumps(respuesta).encode())
