from http.server import BaseHTTPRequestHandler
import pandas as pd
import json, os, requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            df = pd.read_csv(os.path.join(os.getcwd(), 'datos.csv'))
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Lógica: Encontrar los 7 números que llevan más sorteos sin aparecer
            ultimo_sorteo = df[['R1','R2','R3','R4','R5','R6','R7']].values
            ausencia = {}
            for n in range(1, 57):
                for i, sorteo in enumerate(ultimo_sorteo):
                    if n in sorteo:
                        ausencia[n] = i
                        break
            
            # Los que tienen mayor índice de ausencia
            pool = sorted(ausencia, key=ausencia.get, reverse=True)[:7]

            self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({"equipo": "Eq4", "objetivo": "Compensación", "pool": sorted(pool), "memoria": "Cazando números con hambre de salir"}).encode())
        except Exception as e:
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps({"error": str(e)}).encode())
