from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Cabeceras de éxito y permisos totales (CORS)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # 2. El mensaje de prueba
        datos = {
            "letra": "Z",
            "mensaje": "CONEXIÓN ESTABLECIDA",
            "servidor": "Vercel-Opal"
        }
        
        self.wfile.write(json.dumps(datos).encode())

    # Responder a la verificación de seguridad del navegador
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
