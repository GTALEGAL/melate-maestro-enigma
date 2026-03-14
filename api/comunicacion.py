from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
import os
from collections import Counter
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            # 1. LOCALIZACIÓN DE DATOS (Ruta Robusta)
            base_path = os.path.dirname(os.path.dirname(__file__))
            ruta = os.path.join(base_path, 'datos.csv')
            if not os.path.exists(ruta):
                ruta = os.path.join(os.getcwd(), 'datos.csv')

            df = pd.read_csv(ruta)
            df.columns = [c.strip().upper() for c in df.columns]
            cols = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
            
            # Limpieza de fechas y datos
            df['FECHA_DT'] = pd.to_datetime(df['FECHA'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=cols)

            # 2. IDENTIFICAR DÍA DE SORTEO (Para Ponderación)
            # 2=Mie, 4=Vie, 6=Dom
            hoy_idx = datetime.now().weekday()
            proximo_idx = 2
            for d in [2, 4, 6]:
                if d > hoy_idx:
                    proximo_idx = d
                    break
            
            # 3. ANÁLISIS DE FRECUENCIA (CAPA 1 - EL MOTOR QUE SÍ JALA)
            f_global = Counter(df[cols].values.flatten())
            
            # 4. ANÁLISIS DE SECUENCIAS (CAPA 5 - RESONANCIA)
            # Miramos qué salió después de los últimos números registrados
            ultimos_ganadores = df.iloc[0][cols].values
            seguidores = []
            
            # Buscamos en los últimos 500 sorteos para no perder frescura
            for i in range(1, 500):
                ganadores_pasados = set(df.iloc[i][cols].values)
                # Si hubo coincidencia de al menos 1 número, guardamos los que siguieron
                if any(n in ganadores_pasados for n in ultimos_ganadores):
                    seguidores.extend(df.iloc[i-1][cols].values)
            
            f_seguidores = Counter(seguidores)

            # 5. SCORE MAESTRO (CAPA 10 - EL EQUILIBRIO)
            score = {}
            for n in range(1, 57):
                # Puntos por Frecuencia Global (Peso 1)
                p_global = f_global[n] * 0.5
                # Puntos por Resonancia/Seguidores (Peso 2)
                p_resonancia = f_seguidores[n] * 2.0
                # Bono por Día de Sorteo (Peso 1.5 si coincide el día)
                p_dia = 0
                filtro_dia = df[df['FECHA_DT'].dt.weekday == proximo_idx].head(100)
                if n in filtro_dia[cols].values:
                    p_dia = 5 # Bono fijo por presencia reciente en el día
                
                score[n] = round(p_global + p_resonancia + p_dia, 2)

            # Extraemos los 7 mejores
            c10 = sorted(score, key=score.get, reverse=True)[:7]

            respuesta = {
                "status": "OK",
                "proximo_sorteo": "DOMINGO" if proximo_idx == 6 else ("MIÉRCOLES" if proximo_idx == 2 else "VIERNES"),
                "analisis": {
                    "c10_score": sorted([int(x) for x in c10]),
                    "confianza": "ALTA" if len(df) > 1000 else "MEDIA"
                },
                "mensaje": "MOTOR ENIGMA REESTABLECIDO - CAPA 10 ACTIVA"
            }

        except Exception as e:
            respuesta = {"status": "ERROR", "mensaje": str(e)}

        self.wfile.write(json.dumps(respuesta).encode())
