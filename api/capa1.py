from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path_csv = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(path_csv)
            
            # BLINDAJE: Limpiamos los nombres de las columnas (quitamos espacios y pasamos a mayúsculas)
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Buscamos las columnas de números (R1 a R7)
            # Si en tu Excel se llaman n1, n2... cámbialas aquí abajo:
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # Verificamos si existe la columna de concurso, si no, usamos el índice
            id_concurso = df['CONCURSO'].iloc[0] if 'CONCURSO' in df.columns else "N/A"
            
            ultimo_sorteo = [int(x) for x in df.iloc[0][cols].values]
            frec = pd.Series(df[cols].values.flatten()).value_counts().head(7).index.tolist()
            
            res = {
                "concurso": str(id_concurso),
                "numeros_ultimo": ultimo_sorteo,
                "capa1": sorted([int(x) for x in frec])
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode())
            
        except Exception as e:
            self.send_response(200) # Mandamos 200 para que el HTML pueda leer el error
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error_detectado": str(e)}).encode())
