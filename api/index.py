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
            # 1. LOCALIZACIÓN DE DATOS
            base_path = os.path.dirname(os.path.dirname(__file__))
            path_csv = os.path.join(base_path, 'datos.csv')
            if not os.path.exists(path_csv): path_csv = os.path.join(os.getcwd(), 'datos.csv')
            
            # Carga rápida: solo las columnas necesarias
            cols = ['R1','R2','R3','R4','R5','R6','R7']
            df = pd.read_csv(path_csv, usecols=['CONCURSO', 'FECHA'] + cols)
            df.columns = [c.strip().upper() for c in df.columns]

            # --- CAPA 0: EL DETONANTE ---
            ultimo_sorteo = sorted([int(x) for x in df.iloc[0][cols].values])
            set_ultimo = set(ultimo_sorteo)
            
            # --- VENTANAS DE TRABAJO (Para evitar el trabado) ---
            # Usamos los últimos 400 para secuencias y 200 para tríos (más pesado)
            marea_seq = df.head(400)
            marea_trios = df.head(150) 

            # --- CÁLCULO DE GATILLOS Y SECUENCIAS ---
            seguidores = []
            pares_act = list(combinations(ultimo_sorteo, 2))

            for i in range(1, len(marea_seq) - 1):
                sorteo_h = set(marea_seq.iloc[i][cols].values)
                
                # Capa 9: Gatillos Individuales (Muy rápido)
                if not set_ultimo.isdisjoint(sorteo_h):
                    seguidores.extend(marea_seq.iloc[i-1][cols].values)
                
                # Capa 5: Secuencia de Pares
                for p in pares_act:
                    if set(p).issubset(sorteo_h):
                        seguidores.extend(marea_seq.iloc[i-1][cols].values)

            # --- CAPA 10: SCORE MAESTRO ---
            f_gen = Counter(df[cols].values.flatten()) # Frecuencia total
            f_seq = Counter(seguidores) # Gatillos + Pares
            
            score_final = {}
            for n in range(1, 57):
                # Ponderación: Secuencias(x5) + Frecuencia(x0.2)
                p = (f_seq[n] * 5) + (f_gen[n] * 0.2)
                score_final[n] = round(p, 2)
            
            top_maestro = sorted(score_final, key=score_final.get, reverse=True)[:7]

            res = {
                "status": "OPERATIVO",
                "info": {"concurso": int(df.iloc[0]['CONCURSO']), "numeros": ultimo_sorteo},
                "analisis": {
                    "c1_frec": [n[0] for n in f_gen.most_common(7)],
                    "c5_pares_seq": [n[0] for n in f_seq.most_common(7)],
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
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ERROR", "mensaje": str(e)}).encode())
