from http.server import BaseHTTPRequestHandler
import json
import pymysql
from collections import Counter, defaultdict
from itertools import combinations
from datetime import datetime, timedelta


def get_conn():
    return pymysql.connect(
        host="dreamdiamante-torres.com",
        user="dreamdia_cgt",
        password="w0h#7tVAMidh(jO0",
        database="dreamdia_melate_db",
        port=3306,
        charset="utf8mb4",
        connect_timeout=10,
        cursorclass=pymysql.cursors.DictCursor
    )


def cargar_sorteos():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT concurso,fecha,R1,R2,R3,R4,R5,R6,R7 FROM sorteos ORDER BY concurso ASC")
        rows = cur.fetchall()
    conn.close()
    return rows


def nums(s):
    return [int(s[r]) for r in ['R1','R2','R3','R4','R5','R6','R7']]


def dia_semana(fecha):
    """Devuelve el weekday de un campo fecha (date o string)."""
    if hasattr(fecha, 'weekday'):
        return fecha.weekday()
    try:
        return datetime.strptime(str(fecha)[:10], "%Y-%m-%d").weekday()
    except:
        return None


def proximo_dia(ultimo_weekday):
    """
    Dado el día del último sorteo, calcula el próximo:
    Miércoles(2) → Viernes(4)
    Viernes(4)   → Domingo(6)
    Domingo(6)   → Miércoles(2)
    """
    siguiente = {2: 4, 4: 6, 6: 2}
    nombres   = {2: "MIÉRCOLES", 4: "VIERNES", 6: "DOMINGO"}
    pidx = siguiente.get(ultimo_weekday, 2)
    return pidx, nombres[pidx]


# ─── C1: Frecuencia filtrada por día objetivo ─────────────
def capa1(sorteos, dia_objetivo):
    freq = Counter()
    for s in sorteos:
        if dia_semana(s['fecha']) == dia_objetivo:
            freq.update(nums(s))
    return freq


# ─── C2: Pares del último → números que salieron DESPUÉS (mismo día histórico) ──
def capa2_ultimo(sorteos, dia_objetivo):
    ultimo = nums(sorteos[-1])
    pares_ultimo = list(combinations(ultimo, 2))  # 21 pares

    sig_freq = Counter()

    # Solo busca en sorteos del día objetivo
    sorteos_dia = [(i, s) for i, s in enumerate(sorteos)
                   if dia_semana(s['fecha']) == dia_objetivo and i < len(sorteos)-1]

    for i, s in sorteos_dia:
        curr_set = set(nums(s))
        siguiente = nums(sorteos[i+1])
        for par in pares_ultimo:
            if par[0] in curr_set and par[1] in curr_set:
                sig_freq.update(siguiente)

    return {
        "candidatos": [n for n, _ in sig_freq.most_common(7)],
        "sig_freq": sig_freq
    }


# ─── C3: Tríos del último → números que salieron DESPUÉS (mismo día histórico) ──
def capa3_ultimo(sorteos, dia_objetivo):
    ultimo = nums(sorteos[-1])
    trios_ultimo = list(combinations(ultimo, 3))  # 35 tríos

    sig_freq = Counter()

    sorteos_dia = [(i, s) for i, s in enumerate(sorteos)
                   if dia_semana(s['fecha']) == dia_objetivo and i < len(sorteos)-1]

    for i, s in sorteos_dia:
        curr_set = set(nums(s))
        siguiente = nums(sorteos[i+1])
        for trio in trios_ultimo:
            if all(n in curr_set for n in trio):
                sig_freq.update(siguiente)

    return {
        "candidatos": [n for n, _ in sig_freq.most_common(7)],
        "sig_freq": sig_freq
    }


# ─── C4: Distancia temporal filtrada por día ──────────────
def capa4(sorteos, dia_objetivo):
    score = Counter()
    sorteos_dia = [s for s in sorteos if dia_semana(s['fecha']) == dia_objetivo]
    for i in range(1, len(sorteos_dia)-1):
        prev = set(nums(sorteos_dia[i-1]))
        curr = nums(sorteos_dia[i])
        nxt  = set(nums(sorteos_dia[i+1]))
        for n in curr:
            if n in prev: score[n] += 2
            if n in nxt:  score[n] += 2
    return score


# ─── C7: Centralidad de red filtrada por día ──────────────
def capa7(sorteos, dia_objetivo):
    coap = defaultdict(Counter)
    for s in sorteos:
        if dia_semana(s['fecha']) == dia_objetivo:
            n = nums(s)
            for a, b in combinations(n, 2):
                coap[a][b] += 1
                coap[b][a] += 1
    central = {}
    for n in range(1, 57):
        conexiones = coap[n]
        if not conexiones:
            central[n] = 0
            continue
        total = sum(conexiones.values())
        max_c = max(conexiones.values())
        central[n] = round(len(conexiones) * (total / max_c), 2)
    return central


# ─── C9: Gatillos específicos filtrados por día ───────────
def capa9(sorteos, dia_objetivo):
    gatillo    = defaultdict(Counter)
    apariciones = Counter()
    sorteos_dia = [(i, s) for i, s in enumerate(sorteos)
                   if dia_semana(s['fecha']) == dia_objetivo and i < len(sorteos)-1]
    for i, s in sorteos_dia:
        curr = nums(s)
        nxt  = nums(sorteos[i+1])
        for n in curr:
            apariciones[n] += 1
            gatillo[n].update(nxt)
    score = {}
    for n in range(1, 57):
        if not gatillo[n] or apariciones[n] == 0:
            score[n] = 0
            continue
        top = gatillo[n].most_common(1)[0][1]
        score[n] = round(top / apariciones[n], 4)
    return score


# ─── C10: Score compuesto ─────────────────────────────────
def capa10(freq, central, gat, c2_sig, c3_sig):
    def norm(d):
        mx = max(d.values()) if d and max(d.values()) > 0 else 1
        return {k: v/mx for k, v in d.items()}
    nf = norm(dict(freq))
    nc = norm(central)
    ng = norm(gat)
    n2 = norm(dict(c2_sig)) if c2_sig else {}
    n3 = norm(dict(c3_sig)) if c3_sig else {}
    score = {}
    for n in range(1, 57):
        score[n] = round(
            nf.get(n, 0) * 0.15 +
            nc.get(n, 0) * 0.15 +
            ng.get(n, 0) * 0.15 +
            n2.get(n, 0) * 0.30 +
            n3.get(n, 0) * 0.25,
            4
        )
    return score


# ─── 40 COMBINACIONES ─────────────────────────────────────
def generar_combinaciones(score, c2_cands, c3_cands, n_total=40):
    combos = []
    seen   = set()

    def agregar(combo):
        key = tuple(sorted(combo))
        if key not in seen and len(key) == 7:
            seen.add(key)
            combos.append(sorted(list(combo)))

    top_score = sorted(score, key=score.get, reverse=True)

    # Ángulo A — C10 Global (14)
    top14 = top_score[:14]
    for combo in combinations(top14, 7):
        agregar(combo)
        if len(combos) >= 14: break

    # Ángulo B — Candidatos pares C2 (13)
    pool_b = list(dict.fromkeys(c2_cands + [n for n in top_score if n not in c2_cands]))[:14]
    for combo in combinations(pool_b, 7):
        agregar(combo)
        if len(combos) >= 27: break

    # Ángulo C — Candidatos tríos C3 (13)
    pool_c = list(dict.fromkeys(c3_cands + [n for n in top_score if n not in c3_cands]))[:14]
    for combo in combinations(pool_c, 7):
        agregar(combo)
        if len(combos) >= n_total: break

    return combos[:n_total]


# ─── HANDLER ──────────────────────────────────────────────
class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            sorteos  = cargar_sorteos()
            ultimo   = sorteos[-1]
            concurso = int(ultimo['concurso'])

            # Día del último sorteo → calcular próximo
            ultimo_dia_idx = dia_semana(ultimo['fecha'])
            proximo_idx, nombre_dia = proximo_dia(ultimo_dia_idx)
            nombres_dias = {2:"MIÉRCOLES", 4:"VIERNES", 6:"DOMINGO"}
            ultimo_dia_nombre = nombres_dias.get(ultimo_dia_idx, "?")

            # Todas las capas filtradas por día OBJETIVO (el próximo)
            freq    = capa1(sorteos, proximo_idx)
            c2_res  = capa2_ultimo(sorteos, proximo_idx)
            c3_res  = capa3_ultimo(sorteos, proximo_idx)
            dist    = capa4(sorteos, proximo_idx)
            central = capa7(sorteos, proximo_idx)
            gat     = capa9(sorteos, proximo_idx)
            score   = capa10(freq, central, gat, c2_res["sig_freq"], c3_res["sig_freq"])

            top7 = lambda d: sorted(sorted(d, key=d.get, reverse=True)[:7])

            respuesta = {
                "status": "OK",
                "concurso": concurso,
                "ultimo_dia": ultimo_dia_nombre,
                "proximo": nombre_dia,
                "total_sorteos": len(sorteos),
                "ultimo": nums(ultimo),
                "capas": {
                    "c1":           top7(freq),
                    "c2_candidatos": c2_res["candidatos"],
                    "c3_candidatos": c3_res["candidatos"],
                    "c4":           top7(dist),
                    "c7":           top7(central),
                    "c9":           top7(gat),
                    "c10":          top7(score),
                },
                "combinaciones_40": generar_combinaciones(
                    score,
                    c2_res["candidatos"],
                    c3_res["candidatos"]
                )
            }

        except Exception as e:
            import traceback
            respuesta = {
                "status":  "ERROR",
                "mensaje": str(e),
                "detalle": traceback.format_exc()
            }

        self.wfile.write(json.dumps(respuesta, ensure_ascii=False).encode())
