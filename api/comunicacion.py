from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
import os
from collections import Counter
from itertools import combinations
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # Crucial para la terminal
        self.end_headers()

        try:
            # 1. CARGA DE DATOS (Ruta compatible con Vercel)
            # Buscamos el archivo en la raíz del proyecto
            base_path = os.path.dirname(os.path.dirname(__file__))
            ruta = os.path.join(base_path, 'datos.csv')
            
            if not os.path.exists(ruta):
                # Intento secundario si el archivo está en la raíz absoluta
                ruta = os.path.join(os.getcwd(), 'datos.csv')

            df = pd.read_csv(ruta)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
            
            # Limpieza
            df['FECHA_DT'] = pd.to_datetime(df['FECHA'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=cols)

            # 2. DETECCIÓN DEL PRÓXIMO SORTEO
            hoy_idx = datetime.now().weekday()
            dias_sorteo = [2, 4, 6] # Miércoles, Viernes, Domingo
            
            proximo_idx = 2
            for d in dias_sorteo:
                if d > hoy_idx:
                    proximo_idx = d
                    break
            
            nombres_dias = {2: "MIÉRCOLES", 4: "VIERNES", 6: "DOMINGO"}
            tipo_analisis = nombres_dias[proximo_idx]

            # 3. ANÁLISIS POR CAPAS
            # Capa 1: Global
            f_global = Counter(df[cols].values.flatten())
            c1 = [int(n) for n, c in f_global.most_common(7)]

            # Capa 5: Secuencias de Pares
            ult_nums = set(df.iloc[0][cols].values)
            pares_ult = [set(p) for p in combinations(ult_nums, 2)]
            
            marea = df.head(800)
            seg_globales = []
            seg_dia_especifico = []

            for i in range(1, len(marea)):
                hist = set(marea.iloc[i][cols].values)
                sig = marea.iloc[i-1][cols].values
                
                if any(p.issubset(hist) for p in pares_ult):
                    seg_globales.extend(sig)
                    if marea.iloc[i]['FECHA_DT'].weekday() == proximo_idx:
                        seg_dia_especifico.extend(sig)

            f_glo = Counter(seg_globales)
            f_esp = Counter(seg_dia_especifico)
            c5 = [int(n) for n, c in f_glo.most_common(7)] if seg_globales else c1

            # 4. CAPA 10: SCORE MAESTRO
            score = {}
            for n in range(1, 57):
                p = (f_esp[n] * 12) + (f_glo[n] * 6) + (f_global[n] * 0.2)
                score[n] = round(p, 2)
            
            c10 = sorted(score, key=score.get, reverse=True)[:7]

            # 5. ESTRUCTURA DE RESPUESTA
            respuesta = {
                "status": "OK",
                "info": {
                    "concurso": int(df.iloc[0]['CONCURSO']),
                    "numeros_anteriores": [int(x) for x in df.iloc[0][cols].values]
                },
                "proximo_sorteo": f"{tipo_analisis}",
                "analisis": {
                    "c1_frec": sorted(c1),
                    "c5_pares_seq": sorted(c5),
                    "c10_score": sorted([int(x) for x in c10])
                }
            }

        except Exception as e:
            respuesta = {"status": "ERROR", "mensaje": str(e)}

        self.wfile.write(json.dumps(respuesta).encode())
