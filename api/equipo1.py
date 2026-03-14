from http.server import BaseHTTPRequestHandler
import pandas as pd
import json, os, requests
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            df = pd.read_csv(os.path.join(os.getcwd(), 'datos.csv'))
            df.columns = [c.strip().upper() for c in df.columns]
            
            # CAPA 1: Frecuencia Simple
            todos = df[['R1','R2','R3','R4','R5','R6','R7']].values.flatten()
            pool = [int(n) for n, c in Counter(todos).most_common(7)]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"equipo": "Eq1", "pool": sorted(pool), "objetivo": "C1-Frecuencia"}).encode())
        except Exception as e:
            self.send_response(200); self.send_header('Access-Control-Allow-Origin', '*'); self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
