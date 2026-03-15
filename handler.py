from http.server import BaseHTTPRequestHandler
import json
import pymysql
from collections import Counter, defaultdict
from itertools import combinations
from datetime import datetime


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


def capa1(sorteos):
    freq = Counter()
    for s in sorteos:
        freq.update(nums(s))
    return freq


def capa2(sorteos, top=200):
    pares = Counter()
    for s in sorteos:
        for a,b in combinations(nums(s),2):
            pares[(min(a,b),max(a,b))] += 1
    return pares.most_common(top)


def capa3(sorteos, top=100):
    trios = Counter()
    for s in sorteos:
        for combo in combinations(nums(s),3):
            trios[tuple(sorted(combo))] += 1
    return trios.most_common(top)


def capa4(sorteos):
    score = Counter()
    for i in range(1, len(sorteos)-1):
        prev = set(nums(sorteos[i-1]))
        curr = nums(sorteos[i])
        nxt  = set(nums(sorteos[i+1]))
        for n in curr:
            if n in prev: score[n] += 2
            if n in nxt:  score[n] += 2
    return score


def capa5(sorteos, top_pares):
    top_set = set(p for p,_ in top_pares[:50])
    sig = Counter()
    for i in range(len(sorteos)-1):
        curr = nums(sorteos[i])
        siguiente = nums(sorteos[i+1])
        for a,b in combinations(curr,2):
            if (min(a,b),max(a,b)) in top_set:
                sig.update(siguiente)
    return sig


def capa6(sorteos, top_trios):
    top_set = set(t for t,_ in top_trios[:30])
    sig = Counter()
    for i in range(len(sorteos)-1):
        curr = nums(sorteos[i])
        siguiente = nums(sorteos[i+1])
        for combo in combinations(curr,3):
            if tuple(sorted(combo)) in top_set:
                sig.update(siguiente)
    return sig


def capa7(sorteos):
    grado = Counter()
    for s in sorteos:
        for a,b in combinations(nums(s),2):
            grado[a] += 1
            grado[b] += 1
    return {n: grado[n]*grado[n] for n in range(1,57)}


def capa8(sorteos, top=5):
    adj = defaultdict(list)
    for s in sorteos:
        for a,b in combinations(nums(s),2):
            adj[a].append(b)
            adj[b].append(a)
    freq = {n: len(adj[n]) for n in range(1,57)}
    seeds = sorted(freq, key=freq.get, reverse=True)[:top]
    clusters = []
    used = set()
    for seed in seeds:
        if seed in used: continue
        neighbors = [n for n in dict(Counter(adj[seed]).most_common(8)) if n not in used and n != seed]
        cluster = [seed] + neighbors[:6]
        used.update(cluster)
        clusters.append(cluster)
    return clusters


def capa9(sorteos):
    gatillo = defaultdict(Counter)
    for i in range(len(sorteos)-1):
        curr = nums(sorteos[i])
        nxt  = nums(sorteos[i+1])
        for n in curr:
            gatillo[n].update(nxt)
    return {n: sum(gatillo[n].values()) for n in range(1,57)}


def capa10(freq, central, gat, c5, c6):
    def norm(d):
        mx = max(d.values()) if d else 1
        return {k: v/mx for k,v in d.items()}
    nf=norm(dict(freq)); nc=norm(central); ng=norm(gat); n5=norm(dict(c5)); n6=norm(dict(c6))
    return {n: round(nf.get(n,0)*0.20+nc.get(n,0)*0.20+ng.get(n,0)*0.25+n5.get(n,0)*0.20+n6.get(n,0)*0.15,4) for n in range(1,57)}


def generar_combinaciones(score, clusters, top_trios, n_total=40):
    combos = []
    seen = set()
    def agregar(combo):
        key = tuple(sorted(combo))
        if key not in seen and len(key)==7:
            seen.add(key)
            combos.append(sorted(list(combo)))

    # Angulo A — Global C10 (14 combos)
    top14 = sorted(score, key=score.get, reverse=True)[:14]
    for combo in combinations(top14,7):
        agregar(combo)
        if len(combos) >= 14: break

    # Angulo B — Trios C3 (13 combos)
    top_score = sorted(score, key=score.get, reverse=True)[:20]
    for trio,_ in top_trios[:20]:
        extras = [n for n in top_score if n not in trio]
        agregar(list(trio)+extras[:4])
        if len(combos) >= 27: break

    # Angulo C — Clusters C8 (13 combos)
    for cluster in clusters:
        pool = cluster[:10]
        if len(pool) >= 7:
            for combo in combinations(pool,7):
                agregar(combo)
                if len(combos) >= n_total: break
        if len(combos) >= n_total: break

    return combos[:n_total]


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        try:
            sorteos  = cargar_sorteos()
            ultimo   = sorteos[-1]
            concurso = int(ultimo['concurso'])

            hoy = datetime.now().weekday()
            if hoy >= 5:   pidx = 6
            elif hoy < 2:  pidx = 2
            else:          pidx = 4
            nombre_dia = {2:"MIÉRCOLES",4:"VIERNES",6:"DOMINGO"}[pidx]

            freq    = capa1(sorteos)
            top_par = capa2(sorteos)
            top_tri = capa3(sorteos)
            dist    = capa4(sorteos)
            c5      = capa5(sorteos, top_par)
            c6      = capa6(sorteos, top_tri)
            central = capa7(sorteos)
            clustrs = capa8(sorteos)
            gat     = capa9(sorteos)
            score   = capa10(freq, central, gat, c5, c6)

            top7 = lambda d: sorted(sorted(d, key=d.get, reverse=True)[:7])

            respuesta = {
                "status": "OK",
                "concurso": concurso,
                "proximo": nombre_dia,
                "total_sorteos": len(sorteos),
                "ultimo": nums(ultimo),
                "capas": {
                    "c1":  top7(freq),
                    "c4":  top7(dist),
                    "c5":  top7(c5),
                    "c6":  top7(c6),
                    "c7":  top7(central),
                    "c9":  top7(gat),
                    "c10": top7(score),
                    "c2_pares":    [{"par":list(p),"freq":f} for p,f in top_par[:5]],
                    "c3_trios":    [{"trio":list(t),"freq":f} for t,f in top_tri[:5]],
                    "c8_clusters": [{"id":i+1,"nums":c[:7]} for i,c in enumerate(clustrs[:5])],
                },
                "combinaciones_40": generar_combinaciones(score, clustrs, top_tri)
            }
        except Exception as e:
            import traceback
            respuesta = {"status":"ERROR","mensaje":str(e),"detalle":traceback.format_exc()}

        self.wfile.write(json.dumps(respuesta, ensure_ascii=False).encode())
