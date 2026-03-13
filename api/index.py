from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 1. RASTREO DINÁMICO DEL CSV
            # Buscamos en raíz, en api/ y en el directorio del script
            posibles_rutas = [
                os.path.join(os.getcwd(), 'datos.csv'),
                os.path.join(os.path.dirname(__file__), 'datos.csv'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datos.csv'),
                'datos.csv'
            ]
            
            path_csv = None
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    path_csv = ruta
                    break
            
            if not path_csv:
                # Si no lo encuentra, nos dirá dónde buscó (esto aparecerá en tu pantalla)
                raise FileNotFoundError(f"CSV no hallado. Busqué en: {posibles_rutas}")

            # 2. PROCESAMIENTO
            df = pd.read_csv(path_csv)
            # Limpieza rápida por si hay espacios en los nombres de columnas
            df.columns = df.columns.str.strip()
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            ultimo = df.iloc[0]
            numeros_base = [int(x) for x in ultimo[cols].values]

            # 3. RESONANCIA
            df_marea = df.head(300)
            socios = []
            for n in numeros_base:
                mask = df_marea[cols].apply(lambda x: n in x.values, axis=1)
                matches = df_marea[mask][cols].values.flatten()
                socios.extend([int(v) for v in matches if v != n])

            counts = pd.Series(socios).value_counts()
            prediccion = sorted(counts.head(7).index.tolist())

            # 4. ENVÍO DE TELEMETRÍA
            res = {
                "status": "OPERATIVO",
                "concurso": int(ultimo['CONCURSO']),
                "ultimo_sorteo": numeros_base,
                "prediccion": prediccion,
                "metricas": {
                    "paridad": f"{sum(1 for n in prediccion if n % 2 == 0)}P/{sum(1 for n in prediccion if n % 2 != 0)}N",
                    "suma": sum(prediccion)
                }
            }
            self.send_response(200)

        except Exception as e:
            # ESTO ES LO MÁS IMPORTANTE: Envía el error real al navegador
            res = {
                "status": "ERROR_CRÍTICO",
                "mensaje": str(e),
                "directorio_actual": os.getcwd(),
                "archivos_visibles": os.listdir(os.getcwd())
            }
            self.send_response(200) # Enviamos 200 para que el HTML pueda leer el error

        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())
