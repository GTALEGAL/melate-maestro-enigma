from http.server import BaseHTTPRequestHandler
import pandas as pd
import json, os
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            df = pd.read_csv(os.path.join(os.getcwd(), 'datos.csv'))
            df.columns = [c.strip().upper() for c in df.columns]
            
            # CAPA 10: Score de Ausencia
            scores = {}
            for n in range(1, 57):
                for i, row in enumerate(df[['R1','R2','R3','R4','R5','R6','R7']].values):
                    if n in row:
                        scores[n] = i
                        break
            
            pool = sorted(scores, key=scores.get, reverse=True)[:7]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"equipo": "Eq4", "pool": sorted(pool), "objetivo": "C10-Score"}).encode())
        except Exception as e:
            self.send_response(200); self.send_header('Access-Control-Allow-Origin', '*'); self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
