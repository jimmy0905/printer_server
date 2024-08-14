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
        #print(self.path)
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
            fullname = (
                jsondata.get("fullName") if jsondata.get("fullName") is not None else ""
            )
            company = (
                jsondata.get("organizationName") if jsondata.get("organizationName") is not None else ""
            )
            qr_code = (
                jsondata.get("qrCode")
                if jsondata.get("qrCode") is not None
                else ""
            )
            create_badge(
                fullname,
                company,
                qr_code,
                tl="",
                tr="",
                bl="",
                br="",
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
