from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Localizar CSV
            base_path = os.path.dirname(os.path.dirname(__file__))
            path_csv = os.path.join(base_path, 'datos.csv')
            if not os.path.exists(path_csv):
                path_csv = os.path.join(os.getcwd(), 'datos.csv')

            df = pd.read_csv(path_csv)
            
            # Mapeo de columnas según tu estructura (D, #, n1...a)
            # Suponiendo que en tu CSV las columnas de números son R1 a R7
            cols_numeros = ['R1','R2','R3','R4','R5','R6','R7']
            
            # 1. Obtener último sorteo
            ultimo_row = df.iloc[0]
            dia_map = {'M': 'Miércoles', 'V': 'Viernes', 'D': 'Domingo'}
            
            # Datos del último evento
            ultimo_data = {
                "concurso": int(ultimo_row['CONCURSO']),
                "fecha": str(ultimo_row['FECHA']),
                "dia": str(ultimo_row['FECHA']).split()[-1] if ' ' in str(ultimo_row['FECHA']) else "Análisis", 
                "numeros": [int(x) for x in ultimo_row[cols_numeros].values]
            }

            # CAPA 1: FRECUENCIA GENERAL
            todos_f = df[cols_numeros].values.flatten()
            top_general = pd.Series(todos_f).value_counts().head(7).index.tolist()

            # CAPA 1: FRECUENCIA POR DÍA (Filtrando por la columna de fecha o día si existe)
            # Aquí asumimos que buscamos los que más salen en el mismo "mes/periodo" 
            # o podrías filtrar por la columna 'D' si ya la tienes limpia.
            top_dia = pd.Series(todos_f).value_counts().iloc[7:14].index.tolist() # Simulación mientras pulimos la col 'D'

            res = {
                "status": "OK",
                "ultimo": ultimo_data,
                "capa1": {
                    "general": sorted(top_general),
                    "por_dia": sorted(top_dia)
                }
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode())

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
