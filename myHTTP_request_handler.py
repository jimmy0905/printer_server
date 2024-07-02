import http.server
import json
from print_driver import create_badge


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        super().end_headers()

    def do_OPTIONS(self):
        print(self.path)
        self.send_response(200, "ok")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Authorization server is running")

    def do_POST(self):
        if self.path == "/print":
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            jsondata = json.loads(body)

            ticket_type = jsondata.get("ticket_type", "")
            print(ticket_type)
            # check if ticket_type is virtual , if yes, then return
            if ticket_type == "virtual":
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "ticket_type is required"}).encode()
                )
                return

            fullName = (
                jsondata.get("fullName") if jsondata.get("fullName") is not None else ""
            )
            company = ( 
                jsondata.get("company") if jsondata.get("company") is not None else ""
            )
            qrcode_context = (
                jsondata.get("qrcode_context")
                if jsondata.get("qrcode_context") is not None
                else ""
            )
            create_badge(
                fullName,
                company,
                qrcode_context,
            )
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Card printed")
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 Not Found")
