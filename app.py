import socket
import ssl
import socketserver
from util import add_poppler_to_path, create_docs_folder
from myHTTP_request_handler import MyHTTPRequestHandler
from createSSL import createSSL

createSSL()
# Generate an SSL/TLS certificate
certfile = "cert.pem"
keyfile = "key.pem"

add_poppler_to_path()

create_docs_folder()


# app server code


# Set up the server parameters
host = "0.0.0.0"
port = 8000  # 3000, 5000, 8080, 8000


# Create the HTTPS server
httpd = socketserver.TCPServer((host, port), MyHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(
    httpd.socket, certfile=certfile, keyfile=keyfile, server_side=True
)

# log my ip address
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
print("Your Computer IP Address is:" + IPAddr)
# other devices can access the server using the IP address printed above
print(f"Server running on https://{IPAddr}:{port}")


# Start the server
print(f"Server running on https://{host}:{port}")
httpd.serve_forever()
