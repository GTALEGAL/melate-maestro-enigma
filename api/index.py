from http.server import BaseHTTPRequestHandler
import pandas as pd
import json
import os
import numpy as np
from itertools import combinations
from collections import Counter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            base_path = os.path.dirname(os.path.dirname(__file__))
            path_csv = os.path.join(base_path, 'datos.csv')
            if not os.path.exists(path_csv): path_csv = os.path.join(os.getcwd(), 'datos.csv')
            
            df = pd.read_csv(path_csv)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # --- CAPA 0: REFERENCIA ---
            ultimo_sorteo = sorted([int(x) for x in df.iloc[0][cols].values])
            
            # --- CAPA 1: FRECUENCIAS ---
            todos_numeros = df[cols].values.flatten()
            c1_frecuencia = [n[0] for n in Counter(todos_numeros).most_common(7)]

            # --- CAPAS 2 Y 3: SINCRONÍA (CO-APARICIÓN) ---
            # Pares y Tríos que más han salido juntos en la historia
            marea_short = df.head(300)
            pares_hist = []
            for _, row in marea_short[cols].iterrows():
                pares_hist.extend(list(combinations(sorted(row.values), 2)))
            
            c2_pares = [list(p[0]) for p in Counter(pares_hist).most_common(3)]

            # --- CAPA 9: NÚMEROS GATILLO (EFECTO 1D) ---
            # ¿Qué números salen después de cada número del último sorteo?
            seguidores_individuales = []
            for i in range(1, len(df.head(400)) - 1):
                sorteo_h = set(df.iloc[i][cols].values)
                for n in ultimo_sorteo:
                    if n in sorteo_h:
                        seguidores_individuales.extend(df.iloc[i-1][cols].values)
            
            c9_gatillos = [n[0] for n in Counter(seguidores_individuales).most_common(7)]

            # --- CAPAS 5 Y 6: EFECTO SECUENCIAL (PARES/TRÍOS -> SIGUIENTE) ---
            seguidores_pares = []
            pares_actuales = list(combinations(ultimo_sorteo, 2))
            
            for i in range(1, len(df.head(500)) - 1):
                sorteo_h = set(df.iloc[i][cols].values)
                for par in pares_actuales:
                    if set(par).issubset(sorteo_h):
                        seguidores_pares.extend(df.iloc[i-1][cols].values)
            
            c5_efecto_pares = [n[0] for n in Counter(seguidores_pares).most_common(7)]

            # --- CAPA 10: SCORE MAESTRO (PONDERACIÓN FINAL) ---
            f_gen = Counter(todos_numeros)
            f_indiv = Counter(seguidores_individuales)
            f_pares_seq = Counter(seguidores_pares)
            
            score_final = {}
            for n in range(1, 57):
                # Fórmula: Efecto Pares(x3) + Efecto Gatillo(x2) + Frecuencia(x0.5)
                puntos = (f_pares_seq[n] * 3) + (f_indiv[n] * 2) + (f_gen[n] * 0.5)
                score_final[n] = round(puntos, 1)
            
            c10_score = sorted(score_final, key=score_final.get, reverse=True)[:7]

            res = {
                "status": "OK",
                "ultimo": {"concurso": int(df.iloc[0]['CONCURSO']), "numeros": ultimo_sorteo},
                "capas": {
                    "c1": sorted(c1_frecuencia),
                    "c2": c2_pares,
                    "c5": sorted(c5_efecto_pares),
                    "c9": sorted(c9_gatillos),
                    "c10": sorted(c10_score)
                }
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode())

        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
