from http.server import BaseHTTPRequestHandler
import pandas as pd
import json, os
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            df = pd.read_csv(os.path.join(os.getcwd(), 'datos.csv'))
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Capa 5 y 9: Gatillos y Secuencias
            frec_indices = df[['R1','R2','R3','R4','R5','R6','R7']].head(50).values.flatten()
            pool = [int(n) for n, c in Counter(frec_indices).most_common(7)]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"equipo": "Eq3", "pool": sorted(pool), "objetivo": "C5-C9"}).encode())
        except Exception as e:
            self.send_response(200); self.send_header('Access-Control-Allow-Origin', '*'); self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
