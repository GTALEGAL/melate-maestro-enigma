from http.server import BaseHTTPRequestHandler
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        message = "Motor Enigma 2.0 listo para procesar ideas."
        self.wfile.write(message.encode())
        return
