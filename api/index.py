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
            # 1. CARGA Y LIMPIEZA
            base_path = os.path.dirname(os.path.dirname(__file__))
            path_csv = os.path.join(base_path, 'datos.csv')
            if not os.path.exists(path_csv): path_csv = os.path.join(os.getcwd(), 'datos.csv')
            
            df = pd.read_csv(path_csv)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            
            # --- CAPA 0: EL DETONANTE (Último Sorteo) ---
            ultimo_row = df.iloc[0]
            ultimo_sorteo = sorted([int(x) for x in ultimo_row[cols].values])
            
            # --- CAPA 1: FRECUENCIAS ---
            todos_numeros = df[cols].values.flatten()
            c1_frecuencia = [n[0] for n in Counter(todos_numeros).most_common(7)]

            # --- CAPAS 2, 3, 7 y 8: RELACIONES Y CLUSTERS ---
            marea_reciente = df.head(400)
            pares_frecuentes = []
            trios_frecuentes = []
            
            for _, row in marea_reciente[cols].iterrows():
                sorted_vals = sorted(row.values)
                pares_frecuentes.extend(list(combinations(sorted_vals, 2)))
                trios_frecuentes.extend(list(combinations(sorted_vals, 3)))
            
            # Capa 7/8 (Nodos Fuertes): Números que más co-aparecen
            c2_top_pares = Counter(pares_frecuentes).most_common(5)
            c3_top_trios = Counter(trios_frecuentes).most_common(3)

            # --- CAPAS 4, 5, 6 y 9: DISTANCIAS Y GATILLOS (1D) ---
            seguidores_indiv = []
            seguidores_pares = []
            seguidores_trios = []
            
            # Pares y tríos del sorteo actual para buscar su "efecto"
            pares_act = list(combinations(ultimo_sorteo, 2))
            trios_act = list(combinations(ultimo_sorteo, 3))

            for i in range(1, len(marea_reciente) - 1):
                sorteo_h = set(marea_reciente.iloc[i][cols].values)
                
                # Capa 9: Gatillos individuales
                for n in ultimo_sorteo:
                    if n in sorteo_h:
                        seguidores_indiv.extend(marea_reciente.iloc[i-1][cols].values)
                
                # Capa 5: Efecto Pares
                for p in pares_act:
                    if set(p).issubset(sorteo_h):
                        seguidores_pares.extend(marea_reciente.iloc[i-1][cols].values)
                
                # Capa 6: Efecto Tríos
                for t in trios_act:
                    if set(t).issubset(sorteo_h):
                        seguidores_trios.extend(marea_reciente.iloc[i-1][cols].values)

            # --- CAPA 10: SISTEMA DE SCORE PONDERADO ---
            f_gen = Counter(todos_numeros)
            f_gatillo = Counter(seguidores_indiv)
            f_pares_seq = Counter(seguidores_pares)
            f_trios_seq = Counter(seguidores_trios)
            
            score_final = {}
            for n in range(1, 57):
                # Ponderación Maestro: Tríos(x10) + Pares(x5) + Gatillos(x2) + Frecuencia(x0.1)
                p = (f_trios_seq[n] * 10) + (f_pares_seq[n] * 5) + (f_gatillo[n] * 2) + (f_gen[n] * 0.1)
                score_final[n] = round(p, 2)
            
            top_maestro = sorted(score_final, key=score_final.get, reverse=True)[:7]

            res = {
                "status": "OPERATIVO",
                "info": {"concurso": int(ultimo_row['CONCURSO']), "numeros": ultimo_sorteo},
                "analisis": {
                    "c1_frec": sorted(c1_frecuencia),
                    "c2_pares": [{"p": list(x[0]), "f": x[1]} for x in c2_top_pares],
                    "c3_trios": [{"t": list(x[0]), "f": x[1]} for x in c3_top_trios],
                    "c5_pares_seq": [n[0] for n in Counter(seguidores_pares).most_common(7)],
                    "c6_trios_seq": [n[0] for n in Counter(seguidores_trios).most_common(7)],
                    "c9_gatillos": [n[0] for n in Counter(seguidores_indiv).most_common(7)],
                    "c10_score": sorted(top_maestro)
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
