from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 1. LOCALIZACIÓN DE DATOS
            # Usamos una ruta robusta para evitar errores de 'File Not Found'
            path_csv = os.path.join(os.getcwd(), 'datos.csv')
            
            if not os.path.exists(path_csv):
                raise FileNotFoundError("El archivo datos.csv no se encuentra en el directorio.")

            df = pd.read_csv(path_csv)
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # 2. DETECCIÓN DEL ÚLTIMO EVENTO (Renglón 0)
            ultimo_registro = df.iloc[0]
            numeros_base = [int(x) for x in ultimo_registro[cols].values]
            concurso_id = int(ultimo_registro['CONCURSO'])
            fecha_evento = str(ultimo_registro['FECHA'])

            # 3. ANÁLISIS DE RESONANCIA DE CONJUNTO
            # Buscamos qué números aparecen con más frecuencia cuando 
            # cualquiera de los números del último sorteo está presente.
            socios_acumulados = []
            
            # Analizamos los últimos 500 sorteos para mayor precisión (marea estadística)
            df_reciente = df.head(500) 
            
            for n in numeros_base:
                # Máscara: filas donde aparece el número 'n'
                mask = df_reciente[cols].apply(lambda x: n in x.values, axis=1)
                matches = df_reciente[mask][cols].values.flatten()
                # Guardamos los compañeros, excluyendo al propio número 'n'
                socios_acumulados.extend([int(v) for v in matches if v != n])

            # 4. GENERACIÓN DEL VECTOR PREDICTIVO
            # Obtenemos los 7 números con mayor frecuencia de aparición conjunta
            counts = pd.Series(socios_acumulados).value_counts()
            prediccion = counts.head(7).index.tolist()
            prediccion.sort() # Ordenar de menor a mayor para el Dashboard

            # 5. CÁLCULO DE MÉTRICAS OPERATIVAS
            suma_v = sum(prediccion)
            pares = sum(1 for n in prediccion if n % 2 == 0)
            nones = 7 - pares

            res = {
                "status": "OPERATIVO",
                "concurso": concurso_id,
                "fecha": fecha_evento,
                "ultimo_sorteo": numeros_base,
                "prediccion": prediccion,
                "metricas": {
                    "paridad": f"{pares}P / {nones}N",
                    "promedio": round(float(np.mean(prediccion)), 1),
                    "suma": suma_v
                }
            }

        except Exception as e:
            res = {
                "status": "ERROR",
                "error": str(e),
                "mensaje": "Revisar estructura de datos.csv o ruta de archivo"
            }

        # 6. RESPUESTA AL DASHBOARD
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        # Habilitar CORS por si pruebas localmente
        self.send_header('Access-Control-Allow-Origin', '*') 
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())
