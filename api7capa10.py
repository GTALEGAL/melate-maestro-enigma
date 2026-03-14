from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path_csv = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(path_csv)
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # Simplificamos el Score para rapidez: Frecuencia + Recientes
            f_gen = Counter(df[cols].values.flatten())
            f_reciente = Counter(df.head(50)[cols].values.flatten())
            
            score = {}
            for n in range(1, 57):
                puntos = (f_reciente[n] * 4) + (f_gen[n] * 0.5)
                score[n] = puntos
            
            top_c10 = sorted(score, key=score.get, reverse=True)[:7]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"capa10": sorted(top_c10)}).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
