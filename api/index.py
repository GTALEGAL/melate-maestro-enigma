from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Localizar el archivo CSV de forma segura
            path_csv = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(path_csv)
            
            # 1. Tomar el sorteo más reciente (Renglón 0)
            ultimo = df.iloc[0]
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            numeros_base = ultimo[cols].values.tolist()
            
            # 2. Análisis de Resonancia (¿Qué números salen con estos?)
            # Simplificamos: buscamos el socio más fuerte de CADA número del último sorteo
            socios_lista = []
            for n in numeros_base:
                mask = df[cols].apply(lambda x: n in x.values, axis=1)
                matches = df[mask][cols].values.flatten()
                socios_lista.extend([int(v) for v in matches if v != n])
            
            # Top 7 más frecuentes de toda la marea
            prediccion = pd.Series(socios_lista).value_counts().head(7).index.tolist()
            prediccion.sort()

            res = {
                "concurso": int(ultimo['CONCURSO']),
                "fecha": str(ultimo['FECHA']),
                "ultimo_sorteo": numeros_base,
                "prediccion": prediccion,
                "metricas": {
                    "paridad": f"{sum(1 for n in prediccion if n % 2 == 0)}P/{sum(1 for n in prediccion if n % 2 != 0)}N",
                    "suma": sum(prediccion),
                    "promedio": round(float(np.mean(prediccion)), 1)
                }
            }
        except Exception as e:
            res = {"error": str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())
