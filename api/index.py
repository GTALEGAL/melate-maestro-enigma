from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 1. BUSCADOR DINÁMICO DE ARCHIVO
            # Intentamos encontrar el CSV en diferentes niveles (Vercel lo mueve a veces)
            posibles_rutas = [
                os.path.join(os.getcwd(), 'datos.csv'),
                os.path.join(os.getcwd(), 'api', 'datos.csv'),
                './datos.csv'
            ]
            
            path_csv = None
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    path_csv = ruta
                    break
            
            if not path_csv:
                raise FileNotFoundError("ERROR_SISTEMA: No se detectó 'datos.csv' en la base de la terminal.")

            # 2. PROCESAMIENTO DE DATOS HISTÓRICOS
            df = pd.read_csv(path_csv)
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # Identificar el sorteo más reciente (Concurso 4185 en tu caso)
            ultimo_registro = df.iloc[0]
            numeros_base = [int(x) for x in ultimo_registro[cols].values]
            concurso_id = int(ultimo_registro['CONCURSO'])
            fecha_ref = str(ultimo_registro['FECHA'])

            # 3. ALGORITMO DE RESONANCIA (Análisis de Socios Frecuentes)
            # Analizamos la marea de los últimos 350 sorteos
            df_marea = df.head(350)
            socios_lista = []
            
            for n in numeros_base:
                # Filtrar sorteos donde apareció cada número del set último
                mask = df_marea[cols].apply(lambda x: n in x.values, axis=1)
                apariciones = df_marea[mask][cols].values.flatten()
                # Recolectar compañeros de ese número
                socios_lista.extend([int(v) for v in apariciones if v != n])

            # 4. GENERACIÓN DE PREDICCIÓN (Top 7 Frecuentes)
            frecuencias = pd.Series(socios_lista).value_counts()
            vector_sugerido = frecuencias.head(7).index.tolist()
            vector_sugerido.sort()

            # 5. CÁLCULO DE MÉTRICAS OPERATIVAS
            suma_total = sum(vector_sugerido)
            paridad_pares = sum(1 for n in vector_sugerido if n % 2 == 0)

            # 6. EMPAQUETADO DE TELEMETRÍA
            res = {
                "status": "OPERATIVO",
                "concurso": concurso_id,
                "fecha": fecha_ref,
                "ultimo_sorteo": numeros_base,
                "prediccion": vector_sugerido,
                "metricas": {
                    "paridad": f"{paridad_pares}P / {7 - paridad_pares}N",
                    "promedio": round(float(np.mean(vector_sugerido)), 1),
                    "suma": suma_total
                }
            }

        except Exception as e:
            res = {
                "status": "ERROR",
                "mensaje": str(e),
                "log": "Verificar que el CSV tenga las columnas CONCURSO, FECHA, R1...R7"
            }

        # 7. TRANSMISIÓN DE RESPUESTA
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())
