from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Localizar el archivo en la raíz (subiendo un nivel desde /api)
            base_path = os.path.dirname(os.path.dirname(__file__))
            path_csv = os.path.join(base_path, 'datos.csv')
            
            # Si no existe ahí, buscar en el directorio actual
            if not os.path.exists(path_csv):
                path_csv = os.path.join(os.getcwd(), 'datos.csv')

            if not os.path.exists(path_csv):
                raise FileNotFoundError(f"Archivo datos.csv no hallado en {path_csv}")

            df = pd.read_csv(path_csv)
            # Aseguramos que no haya espacios en los nombres de las columnas
            df.columns = [c.strip() for c in df.columns]
            
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            ultimo = df.iloc[0]
            numeros_base = [int(x) for x in ultimo[cols].values]

            # Lógica de Resonancia
            df_marea = df.head(300)
            socios = []
            for n in numeros_base:
                mask = df_marea[cols].apply(lambda x: n in x.values, axis=1)
                matches = df_marea[mask][cols].values.flatten()
                socios.extend([int(v) for v in matches if v != n])

            counts = pd.Series(socios).value_counts()
            prediccion = sorted(counts.head(7).index.tolist())

            res = {
                "status": "OPERATIVO",
                "concurso": int(ultimo['CONCURSO']),
                "fecha": str(ultimo['FECHA']),
                "ultimo_sorteo": numeros_base,
                "prediccion": prediccion,
                "metricas": {
                    "paridad": f"{sum(1 for n in prediccion if n % 2 == 0)}P/{sum(1 for n in prediccion if n % 2 != 0)}N",
                    "promedio": round(float(np.mean(prediccion)), 1),
                    "suma": sum(prediccion)
                }
            }
            
            self.send_response(200)

        except Exception as e:
            res = {"status": "ERROR", "mensaje": str(e)}
            self.send_response(200) # Enviamos 200 para que el HTML no se rompa y muestre el error

        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())
