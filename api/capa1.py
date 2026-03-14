from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 1. Localizar CSV
            path_csv = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(path_csv)
            
            # 2. Limpieza de columnas
            df.columns = [c.strip().upper() for c in df.columns]
            
            # 3. Mapeo de columnas de números (Asegúrate que coincidan con tu CSV)
            # Si tu CSV tiene n1, n2... cámbialos aquí:
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # 4. Extracción de datos
            # Si la columna se llama # o CONCURSO, la buscamos:
            col_id = 'CONCURSO' if 'CONCURSO' in df.columns else df.columns[1] 
            val_concurso = str(df[col_id].iloc[0])
            
            ultimo_sorteo = [int(x) for x in df.iloc[0][cols].values]
            
            # Frecuencia (Capa 1)
            frec_series = pd.Series(df[cols].values.flatten()).value_counts().head(7)
            frec_lista = sorted([int(x) for x in frec_series.index.tolist()])

            # 5. RESPUESTA (Nombres de llaves idénticos al HTML)
            res = {
                "concurso": val_concurso,
                "numeros_ultimo": ultimo_sorteo,
                "capa1": frec_lista
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
            # Enviamos el error detallado para que el Dashboard lo muestre en azul
            self.wfile.write(json.dumps({"error_detectado": str(e)}).encode())
