import http.server
import socketserver
import ssl

# Set up the server parameters
host = "localhost"
port = 8000

# Generate an SSL/TLS certificate
certfile = "cert.pem"
keyfile = "key.pem"

# Create the HTTP request handler
class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hello, world!")

# Create the HTTPS server
httpd = socketserver.TCPServer((host, port), MyHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile=certfile, keyfile=keyfile, server_side=True)

# Start the server
print(f"Server running on https://{host}:{port}")
httpd.serve_forever()