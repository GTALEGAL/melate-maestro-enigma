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
            # 1. CARGA DE DATOS
            base_path = os.path.dirname(os.path.dirname(__file__))
            path_csv = os.path.join(base_path, 'datos.csv')
            if not os.path.exists(path_csv): path_csv = os.path.join(os.getcwd(), 'datos.csv')
            
            df = pd.read_csv(path_csv)
            # Limpieza de columnas
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # 2. CAPA 0: EL ÚLTIMO SORTEO (LA CAUSA)
            ultimo_sorteo = sorted([int(x) for x in df.iloc[0][cols].values])
            pares_actuales = list(combinations(ultimo_sorteo, 2))
            trios_actuales = list(combinations(ultimo_sorteo, 3))

            # 3. PROCESAMIENTO MULTI-CAPA (HISTÓRICO)
            seguidores_pares = []
            seguidores_trios = []
            todos_numeros = df[cols].values.flatten()
            
            # Analizamos los últimos 600 sorteos para profundidad estadística
            marea = df.head(600)
            
            for i in range(1, len(marea) - 1):
                sorteo_h = set(marea.iloc[i][cols].values)
                
                # Capa 5: Efecto de Pares
                for par in pares_actuales:
                    if set(par).issubset(sorteo_h):
                        seguidores_pares.extend(marea.iloc[i-1][cols].values)
                
                # Capa 6: Efecto de Tríos
                for trio in trios_actuales:
                    if set(trio).issubset(sorteo_h):
                        seguidores_trios.extend(marea.iloc[i-1][cols].values)

            # 4. CAPA 10: SISTEMA DE SCORE (RANKING MAESTRO)
            # Combinamos Frecuencia (C1), Seguidores de Pares (C5) y Tríos (C6)
            f_gen = Counter(todos_numeros)
            f_pares = Counter(seguidores_pares)
            f_trios = Counter(seguidores_trios)

            score_final = {}
            for n in range(1, 57):
                # Ponderación: Tríos(x5) + Pares(x2) + Frecuencia(x0.5)
                puntos = (f_trios[n] * 5) + (f_pares[n] * 2) + (f_gen[n] * 0.1)
                score_final[n] = round(puntos, 2)

            # Top 7 del Score Maestro
            top_maestro = sorted(score_final, key=score_final.get, reverse=True)[:7]

            res = {
                "status": "OPERATIVO",
                "ultimo": {
                    "concurso": int(df.iloc[0]['CONCURSO']),
                    "numeros": ultimo_sorteo
                },
                "capas": {
                    "c1_frecuencia": sorted(pd.Series(todos_numeros).value_counts().head(7).index.tolist()),
                    "c5_efecto_pares": [n[0] for n in Counter(seguidores_pares).most_common(7)],
                    "c6_efecto_trios": [n[0] for n in Counter(seguidores_trios).most_common(7)],
                    "c10_score_maestro": sorted(top_maestro)
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
            self.wfile.write(json.dumps({"status": "ERROR", "mensaje": str(e)}).encode())
