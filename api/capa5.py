from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os
from itertools import combinations
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path_csv = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(path_csv)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            ultimo_sorteo = set(df.iloc[0][cols].values)
            pares_act = list(combinations(sorted(ultimo_sorteo), 2))
            
            seguidores = []
            # Analizamos 400 sorteos para no saturar el servidor
            for i in range(1, 401):
                sorteo_h = set(df.iloc[i][cols].values)
                for p in pares_act:
                    if set(p).issubset(sorteo_h):
                        seguidores.extend(df.iloc[i-1][cols].values)
            
            top_c5 = [int(n[0]) for n in Counter(seguidores).most_common(7)]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            # La llave DEBE ser "capa5" para que el HTML la lea
            self.wfile.write(json.dumps({"capa5": sorted(top_c5)}).encode())
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
