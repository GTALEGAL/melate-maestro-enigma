from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            # 1. Cargar la base de datos (datos.csv debe estar en la raíz)
            ruta_csv = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(ruta_csv)
            
            # 2. Limpiar nombres de columnas
            df.columns = [c.strip().upper() for c in df.columns]
            cols_r = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']

            # 3. Lógica Maestra: Frecuencia de los últimos 500 sorteos
            marea = df.head(500)
            todos_numeros = marea[cols_r].values.flatten()
            
            from collections import Counter
            conteo = Counter(todos_numeros)
            
            # Sacamos los 7 más frecuentes (Capas C1 y C10 combinadas)
            prediccion = [n for n, c in conteo.most_common(7)]
            prediccion.sort()

            # 4. Respuesta para el Hosting
            respuesta = {
                "equipo": "MAESTRO-ALFA",
                "pool": prediccion,
                "concurso": int(df.iloc[0]['CONCURSO']),
                "status": "OPERATIVO"
            }

        except Exception as e:
            respuesta = {
                "error": str(e),
                "status": "FALLO_MOTOR"
            }

        self.wfile.write(json.dumps(respuesta).encode())
