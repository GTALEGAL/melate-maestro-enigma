from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 1. LOCALIZACIÓN DINÁMICA DEL CSV
            # Intentamos varias rutas comunes en despliegues tipo Vercel/Serverless
            posibles_rutas = [
                os.path.join(os.getcwd(), 'datos.csv'),
                os.path.join(os.getcwd(), 'api', 'datos.csv'),
                '/tmp/datos.csv' # Para entornos de solo lectura
            ]
            
            path_csv = None
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    path_csv = ruta
                    break
            
            if not path_csv:
                raise FileNotFoundError("No se encontró datos.csv en el servidor.")

            # 2. CARGA DE DATOS
            df = pd.read_csv(path_csv)
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # 3. IDENTIFICACIÓN DEL ÚLTIMO SORTEO (Fila 0)
            ultimo = df.iloc[0]
            concurso = int(ultimo['CONCURSO'])
            fecha = str(ultimo['FECHA'])
            numeros_base = [int(x) for x in ultimo[cols].values]

            # 4. ANÁLISIS DE RESONANCIA (Marea Estadística)
            # Analizamos los últimos 400 sorteos para encontrar "compañeros" frecuentes
            df_marea = df.head(400)
            socios_totales = []

            for n in numeros_base:
                # Buscamos filas donde aparece cada número del sorteo base
                mask = df_marea[cols].apply(lambda x: n in x.values, axis=1)
                matches = df_marea[mask][cols].values.flatten()
                # Guardamos los números que salieron con él (excluyendo al original)
                socios_totales.extend([int(v) for v in matches if v != n])

            # 5. GENERACIÓN DEL VECTOR PREDICTIVO
            # Tomamos los 7 números que más veces han resonado con el set anterior
            counts = pd.Series(socios_totales).value_counts()
            prediccion = counts.head(7).index.tolist()
            prediccion.sort()

            # 6. MÉTRICAS DEL PANEL
            suma_v = sum(prediccion)
            pares = sum(1 for n in prediccion if n % 2 == 0)

            res = {
                "status": "OPERATIVO",
                "concurso": concurso,
                "fecha": fecha,
                "ultimo_sorteo": numeros_base,
                "prediccion": prediccion,
                "metricas": {
                    "paridad": f"{pares}P / {7-pares}N",
                    "promedio": round(float(np.mean(prediccion)), 1),
                    "suma": suma_v
                }
            }

        except Exception as e:
            res = {
                "status": "ERROR",
                "error": str(e),
                "debug_path": os.getcwd()
            }

        # 7. SALIDA DE DATOS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # Permite pruebas locales
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())
