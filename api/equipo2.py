from http.server import BaseHTTPRequestHandler
import pandas as pd
import json, os
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            df = pd.read_csv(os.path.join(os.getcwd(), 'datos.csv'))
            df.columns = [c.strip().upper() for c in df.columns]
            ultimo = set(df.iloc[0][['R1','R2','R3','R4','R5','R6','R7']].values)
            
            seguidores = []
            for i in range(1, min(len(df), 300)):
                if len(ultimo.intersection(set(df.iloc[i][['R1','R2','R3','R4','R5','R6','R7']].values))) >= 2:
                    seguidores.extend(df.iloc[i-1][['R1','R2','R3','R4','R5','R6','R7']].values)
            
            pool = [int(n) for n, c in Counter(seguidores).most_common(7)]
            if not pool: pool = [1,2,3,4,5,6,7] # Fallback

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"equipo": "Eq2", "pool": sorted(pool), "objetivo": "Markov"}).encode())
        except Exception as e:
            self.send_response(200); self.send_header('Access-Control-Allow-Origin', '*'); self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
