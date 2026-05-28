from http.server import BaseHTTPRequestHandler, HTTPServer

class FanAPIHandler(BaseHTTPRequestHandler):
    """Klasa obsługująca zapytania HTTP"""
    
    def do_GET(self):
        # Definiujemy prosty routing - reagujemy tylko na ścieżkę /api/tacho
        if self.path == '/api/tacho':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Pobieramy aktualne obroty
            rpm = fan_reader.get_rpm() if fan_reader else 0
            
            # Tworzymy słownik i konwertujemy na JSON
            data = {"rpm": rpm}
            response_json = json.dumps(data)
            
            # Wysyłamy dane do klienta
            self.wfile.write(response_json.encode('utf-8'))
        else:
            # Dla innych ścieżek zwracamy 404 Not Found
            self.send_response(404)
            self.end_headers()

    # Opcjonalnie: nadpisujemy metodę log_message, aby ukryć spam w konsoli 
    # przy każdym zapytaniu od Telegrafa. Zostaw ją, jeśli wolisz widzieć logi.
    def log_message(self, format, *args):
        pass