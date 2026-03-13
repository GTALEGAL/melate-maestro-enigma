from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Escuchar la orden del Director (Parámetros de URL)
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        # Si no escribes nada, por defecto usa el 22
        gatillo_solicitado = int(params.get('gatillo', [22])[0])

        try:
            # 2. Leer base de datos
            df = pd.read_csv('datos.csv')
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True)
            
            # 3. Columnas de números
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # 4. Filtrar sorteos donde salió el número solicitado
            # Quitamos el filtro de "Marzo" para tener más datos, o déjalo si prefieres
            con_gatillo = df[df[cols].apply(lambda x: gatillo_solicitado in x.values, axis=1)]
            
            # 5. Buscar socios frecuentes
            todos_los_numeros = con_gatillo[cols].values.flatten()
            socios = [int(n) for n in todos_los_numeros if n != gatillo_solicitado]
            
            # ¡Aquí está el cambio! Ahora pedimos los 7 más frecuentes
            frecuentes = pd.Series(socios).value_counts().head(7).index.tolist()
            
            resultado = {
                "analisis": f"Resonancia de Datos - Gatillo {gatillo_solicitado}",
                "gatillo": gatillo_solicitado,
                "socios_frecuentes": frecuentes,
                "mensaje": f"Se han detectado los 7 socios principales para el {gatillo_solicitado}."
            }
        
        except Exception as e:
            resultado = {"error": str(e), "mensaje": "Falla en el motor de análisis."}

        # 6. Enviar respuesta a la Terminal Verde
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(resultado).encode())
        return
