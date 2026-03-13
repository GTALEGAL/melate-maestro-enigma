from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import urllib.parse
import numpy as np

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        # Recibe el número que escribiste en la terminal (ej. 14)
        gatillo = int(params.get('gatillo', [22])[0])

        try:
            df = pd.read_csv('datos.csv')
            cols = ['R1','R2','R3','R4','R5','R6','R7']

            # FILTRO NASA: Buscamos resonancia histórica
            mask = df[cols].apply(lambda x: gatillo in x.values, axis=1)
            con_gatillo = df[mask]
            
            if con_gatillo.empty:
                frecuentes = [0] * 7
                confianza = "BAJA (SIN DATOS)"
                mensaje = "GATILLO NO ENCONTRADO EN LA BASE DE DATOS"
            else:
                todos = con_gatillo[cols].values.flatten()
                socios = [int(n) for n in todos if n != gatillo]
                
                # Ponderación por frecuencia
                counts = pd.Series(socios).value_counts()
                frecuentes = counts.head(7).index.map(int).tolist()
                
                # Si no completamos 7, rellenamos con los más calientes del año
                if len(frecuentes) < 7:
                    calientes = pd.Series(df[cols].values.flatten()).value_counts().head(7).index.tolist()
                    frecuentes = list(set(frecuentes + calientes))[:7]

                confianza = "ALTA" if len(con_gatillo) > 5 else "MEDIA"
                mensaje = "TRAYECTORIA CALCULADA EXITOSAMENTE"

            # MÉTRICAS PARA EL DASHBOARD
            res = {
                "gatillo": gatillo,
                "socios_frecuentes": sorted(frecuentes),
                "metricas": {
                    "balance_par": sum(1 for n in frecuentes if n % 2 == 0),
                    "promedio": round(float(np.mean(frecuentes)), 1),
                    "confianza": confianza
                },
                "mensaje": mensaje
            }
        
        except Exception as e:
            res = {"error": str(e), "mensaje": "FALLO EN EL NÚCLEO"}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())
