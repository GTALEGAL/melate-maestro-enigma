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

            # CAPA 9: Gatillos del último sorteo
            ultimo_resultado = set(df.iloc[0][['R1','R2','R3','R4','R5','R6','R7']].values)
            seguidores = []
            
            # Buscamos en los últimos 500 sorteos (Capa 5: Resonancia de Pares)
            for i in range(1, 500):
                sorteo_h = set(df.iloc[i][['R1','R2','R3','R4','R5','R6','R7']].values)
                # Si hubo coincidencia de 2 o más números (Capa 5)
                if len(ultimo_resultado.intersection(sorteo_h)) >= 2:
                    seguidores.extend(df.iloc[i-1][['R1','R2','R3','R4','R5','R6','R7']].values)

            pool = [int(n) for n, c in Counter(seguidores).most_common(7)]

            # Reportar al SQL
            requests.post("https://dreamdiamante-torres.com/api_memoria.php", json={
                "equipo": "Equipo3", "dia": target, "anotacion": "Capa 5 y 9 activas: Rastreo de pares y gatillos.",
                "aciertos": None, "numeros": ",".join(map(str, sorted(pool)))
            })

            # RESPUESTA CORS
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"equipo": "Eq3", "objetivo": target, "pool": sorted(pool), "memoria": "Analizando resonancia de pares (C5)."}).encode())
        except Exception as e:
            self.send_response(200); self.send_header('Access-Control-Allow-Origin', '*'); self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
