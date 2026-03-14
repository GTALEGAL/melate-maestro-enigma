from http.server import BaseHTTPRequestHandler
import pandas as pd
import json, os, requests
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            df = pd.read_csv(os.path.join(os.getcwd(), 'datos.csv'))
            df.columns = [c.strip().upper() for c in df.columns]
            
            # CAPA 1: Frecuencia Total
            todos = df[['R1','R2','R3','R4','R5','R6','R7']].values.flatten()
            frecuencia = Counter(todos)
            
            # CAPA 10: Score de Reversión (Números que deben salir por ley de promedios)
            score_final = {}
            for n in range(1, 57):
                # Peso: Frecuencia (C1) ajustada por el tiempo de ausencia
                ausencia = 0
                for i, sorteo in enumerate(df[['R1','R2','R3','R4','R5','R6','R7']].values):
                    if n in sorteo:
                        ausencia = i
                        break
                score_final[n] = (frecuencia[n] * 0.5) + (ausencia * 2.0)

            pool = sorted(score_final, key=score_final.get, reverse=True)[:7]

            # Reportar al SQL
            requests.post("https://dreamdiamante-torres.com/api_memoria.php", json={
                "equipo": "Equipo4", "dia": "Todos", "anotacion": "Capa 10 aplicada: Score de reversión a la media.",
                "aciertos": None, "numeros": ",".join(map(str, sorted(pool)))
            })

            # RESPUESTA CORS
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"equipo": "Eq4", "objetivo": "C10 Maestro", "pool": sorted(pool), "memoria": "Capa 1 y 10: Máxima probabilidad estadística."}).encode())
        except Exception as e:
            self.send_response(200); self.send_header('Access-Control-Allow-Origin', '*'); self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
