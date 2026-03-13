from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 1. RUTA CRÍTICA: Vercel a veces requiere rutas absolutas
# Dentro de tu index.py, usa esta lógica para el path
base_dir = os.path.dirname(os.path.abspath(__file__))
# Si el csv está en la raíz y el script en /api:
path_csv = os.path.join(base_dir, '..', 'datos.csv') 

if not os.path.exists(path_csv):
    # Intento 2: si está en la misma carpeta
    path_csv = os.path.join(base_dir, 'datos.csv')

            # 2. LECTURA DE DATOS
            if not os.path.exists(path_csv):
                raise FileNotFoundError(f"No se encontró datos.csv en {path_csv}")

            df = pd.read_csv(path_csv)
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # Tomar el último sorteo
            ultimo = df.iloc[0]
            numeros_base = [int(x) for x in ultimo[cols].values]

            # 3. ANÁLISIS DE RESONANCIA
            df_marea = df.head(300)
            socios_lista = []
            for n in numeros_base:
                mask = df_marea[cols].apply(lambda x: n in x.values, axis=1)
                matches = df_marea[mask][cols].values.flatten()
                socios_lista.extend([int(v) for v in matches if v != n])

            counts = pd.Series(socios_lista).value_counts()
            prediccion = counts.head(7).index.tolist()
            prediccion.sort()

            # 4. RESPUESTA EXITOSA
            res = {
                "status": "OPERATIVO",
                "concurso": int(ultimo['CONCURSO']),
                "fecha": str(ultimo['FECHA']),
                "ultimo_sorteo": numeros_base,
                "prediccion": prediccion,
                "metricas": {
                    "paridad": f"{sum(1 for n in prediccion if n % 2 == 0)}P / {sum(1 for n in prediccion if n % 2 != 0)}N",
                    "promedio": round(float(np.mean(prediccion)), 1),
                    "suma": sum(prediccion)
                }
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode())

        except Exception as e:
            # Si algo falla, enviamos el error en formato JSON para que el JS no se rompa
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_res = {"status": "ERROR", "error": str(e)}
            self.wfile.write(json.dumps(error_res).encode())
