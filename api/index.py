from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            df = pd.read_csv('datos.csv')
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # 1. DETECCIÓN AUTOMÁTICA DEL ÚLTIMO SORTEO
            ultimo_registro = df.iloc[0]
            concurso_id = int(ultimo_registro['CONCURSO'])
            fecha_ultimo = ultimo_registro['FECHA']
            numeros_actuales = ultimo_registro[cols].values.tolist()

            # 2. ANÁLISIS DE RESONANCIA DE CONJUNTO
            # Buscamos qué números suelen acompañar a este set de 7
            socios_acumulados = []
            for n in numeros_actuales:
                mask = df[cols].apply(lambda x: n in x.values, axis=1)
                con_n = df[mask]
                # Extraer todos los números excepto el gatillo actual
                todos = con_n[cols].values.flatten()
                socios_acumulados.extend([int(v) for v in todos if v != n])

            # 3. GENERACIÓN DEL VECTOR PREDICTIVO (Top 7 más frecuentes del conjunto)
            counts = pd.Series(socios_acumulados).value_counts()
            prediccion = counts.head(7).index.map(int).tolist()
            prediccion.sort()

            # 4. MÉTRICAS DE DASHBOARD
            suma_v = sum(prediccion)
            res = {
                "status": "OPERATIVO",
                "ultimo_sorteo": {
                    "concurso": concurso_id,
                    "fecha": fecha_ultimo,
                    "numeros": numeros_actuales
                },
                "prediccion": prediccion,
                "metricas": {
                    "paridad": f"{sum(1 for n in prediccion if n % 2 == 0)}P/{sum(1 for n in prediccion if n % 2 != 0)}N",
                    "promedio": round(float(np.mean(prediccion)), 1),
                    "suma_total": suma_v,
                    "alerta_dorada": "ACTIVA" if 130 <= suma_v <= 210 else "NORMAL"
                }
            }
        except Exception as e:
            res = {"status": "ERROR", "mensaje": str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())
