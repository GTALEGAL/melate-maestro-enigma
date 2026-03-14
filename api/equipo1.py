from http.server import BaseHTTPRequestHandler
import pandas as pd
import json, os, requests
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            df = pd.read_csv(os.path.join(os.getcwd(), 'datos.csv'))
            df.columns = [c.strip().upper() for c in df.columns]
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True)
            
            ultimo_dia = df['FECHA'].dt.day_name().iloc[0]
            mapa = {"Wednesday": "Friday", "Friday": "Sunday", "Sunday": "Wednesday"}
            target = mapa.get(ultimo_dia, "Friday")

            # Consultar memoria al Hosting
            url = f"https://dreamdiamante-torres.com/api_memoria.php?equipo=Equipo1&dia={target}"
            mem = requests.get(url).json().get('anotacion', 'Sin notas')

            # Lógica: Números más frecuentes pero con balance Par/Impar (4/3 o 3/4)
            todos = df[['R1','R2','R3','R4','R5','R6','R7']].values.flatten()
            comunes = [n for n, c in Counter(todos).most_common(20)]
            
            pool = []
            pares = [n for n in comunes if n % 2 == 0]
            impares = [n for n in comunes if n % 2 != 0]
            pool = pares[:3] + impares[:4] # Balance estándar

            # Reportar al SQL
            requests.post("https://dreamdiamante-torres.com/api_memoria.php", json={
                "equipo": "Equipo1", "dia": target, "anotacion": "Balance Par/Impar aplicado.",
                "aciertos": None, "numeros": ",".join(map(str, sorted(pool)))
            })

            self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({"equipo": "Eq1", "objetivo": target, "pool": sorted(pool), "memoria": mem}).encode())
        except Exception as e:
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps({"error": str(e)}).encode())
