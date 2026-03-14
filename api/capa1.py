from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path_csv = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(path_csv)
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # Datos del último sorteo para el encabezado
            ultimo = df.iloc[0]
            # Capa 1: Frecuencia Total
            frec = pd.Series(df[cols].values.flatten()).value_counts().head(7).index.tolist()
            
            res = {
                "concurso": int(ultimo['CONCURSO']),
                "numeros_ultimo": [int(x) for x in ultimo[cols].values],
                "capa1": sorted(frec)
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
