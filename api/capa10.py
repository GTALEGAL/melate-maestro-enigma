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
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # --- MOTOR DE SCORE MAESTRO ---
            # 1. Frecuencia Total (Largo Plazo)
            f_gen = Counter(df[cols].values.flatten())
            
            # 2. Tendencia Reciente (Últimos 100 sorteos)
            f_reciente = Counter(df.head(100)[cols].values.flatten())
            
            # 3. Ponderación
            score = {}
            for n in range(1, 57):
                # Damos 10 veces más peso a la tendencia reciente que a la histórica
                puntos = (f_reciente[n] * 10) + (f_gen[n] * 0.5)
                score[n] = puntos
            
            # 4. Extraer los 7 ganadores del ranking
            top_c10 = sorted(score, key=score.get, reverse=True)[:7]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Enviamos la llave "capa10" que es la que el HTML busca
            res = {"capa10": sorted([int(x) for x in top_c10])}
            self.wfile.write(json.dumps(res).encode())
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
