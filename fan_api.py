import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class FanAPIHandler:
    """Class managing the HTTP server for the API"""
    
    def __init__(self, config_items, tacho_reader, fan_control=None):
        self.tacho_reader = tacho_reader
        self.fan_control = fan_control
        self.api_port = None
        
        if config_items:
            for item in config_items:
                if "api_port" in item:
                    val = item["api_port"]
                    if val is not None and str(val).lower() != "none":
                        self.api_port = int(val)
                    break
                    
        self.server = None
        self.thread = None

    def start(self):
        if not self.api_port:
            print("No api_port configuration or api_port = None. API server is not starting.")
            return

        # Nested HTTP handler class
        class _RequestHandler(BaseHTTPRequestHandler):
            def do_GET(req_self):
                if req_self.path == '/api/fan':
                    req_self.send_response(200)
                    req_self.send_header('Content-Type', 'application/json')
                    req_self.end_headers()
                    
                    data = {}
                    if self.tacho_reader:
                        rpm = self.tacho_reader.get_rpm()
                        if rpm is not None:
                            data["rpm"] = rpm
                            
                    if self.fan_control:
                        if hasattr(self.fan_control, 'get_state'):
                            data.update(self.fan_control.get_state())
                            
                    response_json = json.dumps(data)
                    req_self.wfile.write(response_json.encode('utf-8'))
                else:
                    req_self.send_response(404)
                    req_self.end_headers()

            def log_message(req_self, format, *args):
                pass

        self.server = HTTPServer(('0.0.0.0', self.api_port), _RequestHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"API server listening on http://0.0.0.0:{self.api_port}/api/fan")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread and self.thread.is_alive():
            self.thread.join()
        print("API server stopped.")