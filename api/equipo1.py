# Dentro de tu equipo1.py en Vercel:
self.send_response(200)
self.send_header('Content-type', 'application/json')
self.send_header('Access-Control-Allow-Origin', '*') # <--- ESTO ES LO MÁS IMPORTANTE
self.send_header('Access-Control-Allow-Methods', 'GET')
self.end_headers()

self.wfile.write(json.dumps({"pool": ["A", "B", "C"]}).encode())
