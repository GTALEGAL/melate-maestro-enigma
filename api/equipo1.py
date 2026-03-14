from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # El permiso clave
        self.end_headers()
        
        # Enviamos la letra A en el lugar de los números
        self.wfile.write(json.dumps({
            "equipo": "PUENTE",
            "pool": ["A", "B", "C"], 
            "memoria": "CONEXIÓN EXITOSA"
        }).encode())
