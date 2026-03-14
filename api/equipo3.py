from http.server import BaseHTTPRequestHandler
import pandas as pd
import json, os, requests
from collections import Counter
from itertools import combinations

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            df = pd.read_csv(os.path.join(os.getcwd(), 'datos.csv'))
            df.columns = [c.strip().upper() for c in df.columns]
            df['FECHA'] = pd.to_datetime(df['FECHA'], dayfirst=True)
            ultimo_dia = df['FECHA'].dt.day_name().iloc[0]
            target = "Sunday" if ultimo_dia == "Friday" else "Friday"

            # Lógica: Buscar seguidores de los pares del último sorteo
            ultimo_sorteo = set(df.iloc[0][['R1','R2','R3','R4','R5','R6','R7']].values)
            seguidores = []
            for i in range(1, 300): # Ventana de 300 sorteos
                if len(ultimo_sorteo.intersection(set(df.iloc[i][['R1','R2','R3','R4','R5','R6','R7']].values))) >= 2:
                    seguidores.extend(df.iloc[i-1][['R1','R2','R3','R4','R5','R6','R7']].values)
            
            pool = [int(n) for n, c in Counter(seguidores).most_common(7)]

            # Reportar al SQL
            requests.post("https://dreamdiamante-torres.com/api_memoria.php", json={
                "equipo": "Equipo3", "dia": target, "anotacion": "Resonancia de pares activa.",
                "aciertos": None, "numeros": ",".join(map(str, sorted(pool)))
            })

            self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({"equipo": "Eq3", "objetivo": target, "pool": sorted(pool), "memoria": "Buscando ecos del sorteo anterior"}).encode())
        except Exception as e:
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps({"error": str(e)}).encode())
