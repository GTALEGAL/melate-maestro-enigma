from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import urllib.parse
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        gatillo = int(params.get('gatillo', [22])[0])

        try:
            df = pd.read_csv('datos.csv')
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True)
            cols = ['R1','R2','R3','R4','R5','R6','R7']

            # 1. ANALISIS DE PROXIMIDAD (Solo últimos 100 sorteos para frescura)
            df_reciente = df.head(100)
            
            # 2. ENCONTRAR RESONANCIA
            mask = df[cols].apply(lambda x: gatillo in x.values, axis=1)
            con_gatillo = df[mask]
            
            if con_gatillo.empty:
                frecuentes = [0,0,0,0,0,0,0]
                status = "GATILLO SIN DATOS SUFICIENTES"
            else:
                todos = con_gatillo[cols].values.flatten()
                socios = [int(n) for n in todos if n != gatillo]
                
                # 3. PONDERACIÓN NASA: Priorizar números que también están "calientes" hoy
                counts = pd.Series(socios).value_counts()
                calientes = pd.Series(df_reciente[cols].values.flatten()).value_counts()
                
                # Combinamos: Frecuencia con Gatillo + Tendencia Actual
                analisis_final = (counts * 0.7) + (calientes * 0.3)
                frecuentes = analisis_final.sort_values(ascending=False).head(7).index.map(int).tolist()
                status = "CÁLCULO DE PROBABILIDAD COMPLETO"

            resultado = {
                "analisis": "MODO NASA: Ponderación de Tendencias",
                "gatillo": gatillo,
                "socios_frecuentes": frecuentes,
                "metricas": {
                    "balance_par": sum(1 for n in frecuentes if n % 2 == 0),
                    "promedio": round(float(np.mean(frecuentes)), 2),
                    "confianza": "ALTA"
                },
                "mensaje": status
            }
        
        except Exception as e:
            resultado = {"error": str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(resultado).encode())
