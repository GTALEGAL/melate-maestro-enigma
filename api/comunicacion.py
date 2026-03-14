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
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            ruta = os.path.join(os.getcwd(), 'datos.csv')
            df = pd.read_csv(ruta)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
            df['FECHA_DT'] = pd.to_datetime(df['FECHA'], dayfirst=True, errors='coerce')

            # 1. DETECCIÓN AUTOMÁTICA DEL PRÓXIMO SORTEO
            hoy_index = datetime.now().weekday() # 0=Lunes, 2=Miércoles, 4=Viernes, 6=Domingo
            dias_sorteo = [2, 4, 6] # M, V, D
            
            # Encontrar el siguiente día de sorteo
            proximo_dia = min([d for d in dias_sorteo if d > hoy_index] or [2])
            nombres = {2: "MIÉRCOLES", 4: "VIERNES", 6: "DOMINGO"}
            tipo_analisis = nombres[proximo_dia]

            # 2. FILTRADO INTELIGENTE (MADURACIÓN)
            # El motor analiza TODO el historial, pero le da 3x peso a los sorteos del mismo día
            df_mismo_dia = df[df['FECHA_DT'].dt.weekday == proximo_dia].head(400)
            df_general = df.head(800)

            ult_nums = set(df.iloc[0][cols].values)
            pares_ult = [set(p) for p in combinations(ult_nums, 2)]
            
            seg_especificos = []
            seg_globales = []

            # Analizar cómo se comporta el Melate específicamente ese día vs el resto
            for i in range(1, len(df_general)):
                hist = set(df_general.iloc[i][cols].values)
                sig = df_general.iloc[i-1][cols].values
                if any(p.issubset(hist) for p in pares_ult):
                    seg_globales.extend(sig)
                    # Si el sorteo histórico ocurrió en el mismo día que el que viene, peso doble
                    if df_general.iloc[i]['FECHA_DT'].weekday() == proximo_dia:
                        seg_especificos.extend(sig)

            # 3. CRUCE DE DATOS
            f_gen = Counter(df_general[cols].values.flatten())
            f_esp = Counter(seg_especificos)
            f_glo = Counter(seg_globales)

            # Capas dinámicas
            c1 = [int(n) for n, c in f_gen.most_common(7)]
            c5 = [int(n) for n, c in f_glo.most_common(7)]
            
            # SCORE MAESTRO: Mezcla ADN Global + ADN Específico del Día
            score = {}
            for n in range(1, 57):
                # Puntos = (Frec. del Día * 10) + (Secuencia Global * 5) + (Frec. General * 0.1)
                p = (f_esp[n] * 10) + (f_glo[n] * 5) + (f_gen[n] * 0.1)
                score[n] = round(p, 2)
            
            c10 = sorted(score, key=score.get, reverse=True)[:7]

            respuesta = {
                "concurso": int(df.iloc[0]['CONCURSO']),
                "proximo_sorteo": f"PRÓXIMO: {tipo_analisis}",
                "capas": {
                    "c1": sorted(c1),
                    "c5": sorted(c5),
                    "c6": sorted([int(n) for n, c in f_esp.most_common(7)]) if seg_especificos else sorted(c1),
                    "c10": sorted([int(x) for x in c10])
                },
                "debug": {
                    "modo": f"Enfoque {tipo_analisis}",
                    "muestras_dia": len(df_mismo_dia)
                }
            }
        except Exception as e:
            respuesta = {"error": str(e)}

        self.wfile.write(json.dumps(respuesta).encode())
