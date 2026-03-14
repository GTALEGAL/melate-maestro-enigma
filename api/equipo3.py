from http.server import BaseHTTPRequestHandler
import pandas as pd
import json, os
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            df = pd.read_csv(os.path.join(os.getcwd(), 'datos.csv'))
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Capa 9 (Gatillos) + Capa 5 (Pares)
            ultimo = df.iloc[0][['R1','R2','R3','R4','R5','R6','R7']].values
            c5_pool = []
            for i in range(1, len(df)-1):
                if any(x in df.iloc[i+1][['R1','R2','R3','R4','R5','R6','R7']].values for x in ultimo):
                    c5_pool.extend(df.iloc[i][['R1','R2','R3','R4','R5','R6','R7']].values)
            
            pool = sorted([int(n) for n, c in Counter(c5_pool).most_common(7)])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # PARCHE
            self.end_headers()
            self.wfile.write(json.dumps({"equipo": "Eq3", "pool": pool, "objetivo": "C5-C9"}).encode())
        except Exception as e:
            self.send_response(200); self.send_header('Access-Control-Allow-Origin', '*'); self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
