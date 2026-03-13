from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 1. LOCALIZACIÓN ROBUSTA DEL CSV
            # Buscamos en el directorio actual (raíz del proyecto en Vercel)
            path_csv = os.path.join(os.getcwd(), 'datos.csv')
            
            if not os.path.exists(path_csv):
                # Si falla, intentamos buscarlo un nivel arriba (común en despliegues API)
                path_csv = os.path.join(os.getcwd(), '..', 'datos.csv')

            df = pd.read_csv(path_csv)
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # 2. IDENTIFICACIÓN DEL ÚLTIMO SORTEO
            # Tomamos la primera fila (la más reciente según tu archivo)
            ultimo = df.iloc[0]
            concurso = int(ultimo['CONCURSO'])
            fecha = str(ultimo['FECHA'])
            numeros_base = [int(x) for x in ultimo[cols].values]

            # 3. ANÁLISIS DE SOCIOS (RESONANCIA)
            # Analizamos los últimos 300 registros para encontrar patrones de compañía
            df_analisis = df.head(300)
            socios_totales = []

            for n in numeros_base:
                # Filtrar filas donde aparece este número del último sorteo
                mask = df_analisis[cols].apply(lambda x: n in x.values, axis=1)
                matches = df_analisis[mask][cols].values.flatten()
                # Extraemos los números que lo acompañaron (excluyendo al original)
                socios_totales.extend([int(v) for v in matches if v != n])

            # 4. GENERACIÓN DEL VECTOR PREDICTIVO (TOP 7)
            counts = pd.Series(socios_totales).value_counts()
            prediccion = counts.head(7).index.tolist()
            prediccion.sort()

            # 5. MÉTRICAS DASHBOARD
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
            res = {"status": "ERROR", "error": str(e)}

        # SALIDA JSON
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())
