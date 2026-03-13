from http.server import BaseHTTPRequestHandler
import pandas as pd
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        try:
            # Los ingenieros leen el archivo de combustible
            df = pd.read_csv('datos.csv')
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True)
            
            # Filtro: Solo sorteos de MARZO donde salió el 22
            marzo = df[df['FECHA'].dt.month == 3]
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            con_22 = marzo[marzo[cols].apply(lambda x: 22 in x.values, axis=1)]
            
            # Buscamos a sus "socios" más frecuentes
            todos_los_numeros = con_22[cols].values.flatten()
            socios = [int(n) for n in todos_los_numeros if n != 22]
            frecuentes = pd.Series(socios).value_counts().head(5).index.tolist()
            
            resultado = {
                "analisis": "Resonancia de Marzo",
                "gatillo": 22,
                "socios_frecuentes": frecuentes,
                "mensaje": "Ingenieros del Condominio B reportando éxito."
            }
        
        except Exception as e:
            print(f"ERROR DETECTADO: {e}") # Esto hará que aparezca en el Log
            resultado = {"error": str(e)}

        print(f"RESPUESTA ENVIADA: {resultado}") # Esto imprimirá los números en el Log
        self.wfile.write(json.dumps(resultado).encode())
        return
