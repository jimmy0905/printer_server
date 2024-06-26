import socket
import json
import ssl
import socketserver
import http.server
import win32ui
import win32con
import win32print
from PIL import Image, ImageWin
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
import textwrap
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab_qrcode import QRCodeImage
from pdf2image import convert_from_path
import os


# printname
print_name = "PrinterB"
# set the font
FONTNAME = "Msjh"
pdfmetrics.registerFont(TTFont(FONTNAME, "./msjh.ttf"))
FONTNAMEBOLD = "MsjhBold"
pdfmetrics.registerFont(TTFont(FONTNAMEBOLD, "./msjhbd.ttc"))
# Convert dimensions from mm to points (1mm = 2.83465 points)

width, height = 90 * mm, 62 * mm
margin = 5 * mm


def get_width_of_string(s):
    width = 0
    for character in s:
        if '\u4e00' <= character <= '\u9fff':
            width += 2
        else:
            width += 1
    return width


class CustomTextWrapper(textwrap.TextWrapper):
    def _split(self, text):
        chunks = super()._split(text)
        new_chunks = []
        for chunk in chunks:
            #print(chunk)
            if '\u4e00' <= chunk[0] <= '\u9fff':
                new_chunks.extend(list(chunk))
            else:
                new_chunks.append(chunk)
        return new_chunks

    def _wrap_chunks(self, chunks):
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)
        if chunks:
            cur_line = [chunks.pop(0)]
            cur_len = get_width_of_string(cur_line[0])
        else:
            cur_line = []
            cur_len = 0
        while chunks:
            chunk_width = get_width_of_string(chunks[0])
            if cur_len + chunk_width <= self.width:
                cur_len += chunk_width
                cur_line.append(chunks.pop(0))
            else:
                lines.append(''.join(cur_line))
                cur_line = [chunks.pop(0)]
                cur_len = get_width_of_string(cur_line[0])
        if cur_line:
            lines.append(''.join(cur_line))
        return lines


def add_poppler_to_path():
    poppler_relative_path = "poppler-24.02.0/Library/bin"
    poppler_path = os.path.abspath(poppler_relative_path)

    print(poppler_path)

    # Get the current PATH variable
    current_path = os.environ.get("PATH", "")

    # Append the Poppler path to the current PATH variable
    updated_path = f"{current_path};{poppler_path}"

    # Update the PATH variable
    os.environ["PATH"] = updated_path


def print_with_selected_printer(printer_name, filename):

    try:
        img = Image.open(filename, "r")
    except:
        print("error")
        return

    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    horzres = hdc.GetDeviceCaps(win32con.HORZRES)
    vertres = hdc.GetDeviceCaps(win32con.VERTRES)

    landscape = horzres > vertres

    if landscape:
        if img.size[1] > img.size[0]:
            print("Landscape mode, tall image, rotate bitmap.")
            img = img.rotate(90, expand=True)
    else:
        if img.size[1] < img.size[0]:
            print("Portrait mode, wide image, rotate bitmap.")
            img = img.rotate(90, expand=True)

    img_width = img.size[0]
    img_height = img.size[1]

    if landscape:
        # we want image width to match page width
        ratio = vertres / horzres
        max_width = img_width
        max_height = (int)(img_width * ratio)
    else:
        # we want image height to match page height
        ratio = horzres / vertres
        max_height = img_height
        max_width = (int)(max_height * ratio)

    # map image size to page size
    hdc.SetMapMode(win32con.MM_ISOTROPIC)
    hdc.SetViewportExt((horzres, vertres))
    hdc.SetWindowExt((max_width, max_height))

    # offset image so it is centered horizontally
    offset_x = (int)((max_width - img_width) / 2)
    offset_y = (int)((max_height - img_height) / 2)
    hdc.SetWindowOrg((-offset_x, -offset_y))

    hdc.StartDoc("Result")
    hdc.StartPage()

    dib = ImageWin.Dib(img)
    dib.draw(hdc.GetHandleOutput(), (0, 0, img_width, img_height))

    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()

    # print( 'Debug info:' )
    # print( 'Landscape: %d' % landscape )
    # print( 'horzres: %d' % horzres )
    # print( 'vertres: %d' % vertres )

    # print( 'img_width: %d' % img_width )
    # print( 'img_height: %d' % img_height )

    # print( 'max_width: %d' % max_width )
    # print( 'max_height: %d' % max_height )

    # print( 'offset_x: %d' % offset_x )
    # print( 'offset_y: %d' % offset_y )


def print_badge(
    fullName,
    company,
    title,
    top_left_text,
    top_right_text,
    bottom_left_text,
    bottom_right_text,
    qrcode_id,
    language="DONT SKIP",
):
    # remove the all the file name limit characters
    fullName = fullName.replace("/", "")
    fullName = fullName.replace("\\", "")
    fullName = fullName.replace(":", "")
    fullName = fullName.replace("*", "")
    fullName = fullName.replace("?", "")
    fullName = fullName.replace('"', "")
    fullName = fullName.replace("<", "")
    fullName = fullName.replace(">", "")
    fullName = fullName.replace("|", "")
    fullName = fullName.replace("\n", "")

    company = company.replace("/", "")
    company = company.replace("\\", "")
    company = company.replace(":", "")
    company = company.replace("*", "")
    company = company.replace("?", "")
    company = company.replace('"', "")
    company = company.replace("<", "")
    company = company.replace(">", "")
    company = company.replace("|", "")
    company = company.replace("\n", "")
    pdfName = qrcode_id + ".pdf" if qrcode_id is not None and qrcode_id != "" else fullName +".pdf"
    pdfPath = os.path.join("docs", pdfName)
    c = canvas.Canvas(pdfPath, pagesize=(width, height))

    if language == "en":
        fullName = fullName.split(" ")[1:]
        fullName = " ".join(fullName)
    elif language == "DONT SKIP":
        fullName = fullName
    else:
        fullName = fullName[:-2]

    customTextWrapper = CustomTextWrapper(width=15)
    wrapped_fullName = customTextWrapper.fill(fullName)
    wrapped_fullName_lines = wrapped_fullName.splitlines()
    #print("wrapped_fullName_lines")
    line_used = 0
    line_height = 8 * mm
    for i, line in enumerate(wrapped_fullName_lines):
        c.setFont(FONTNAMEBOLD, 20)
        c.drawString(margin, height - 10 * mm -
                     (line_used * line_height), line)
        line_used = line_used + 1

    #print("drawed name")
    customTextWrapper = CustomTextWrapper(width=20)
    wrapped_company = customTextWrapper.fill(company)
    wrapped_company_lines = wrapped_company.splitlines()

    #print("wrapped_company_lines")
    for i, line in enumerate(wrapped_company_lines):
        c.setFont(FONTNAME, 14)
        c.drawString(margin, height - 10 * mm -
                     (line_used * line_height), line)
        line_used = line_used + 1

    #print("drawed company")
    # draw the 4 concer
    c.setFont(FONTNAME, 8)
    c.drawString(margin, height - margin, top_left_text)
    c.drawRightString(width - margin, height - margin, top_right_text)
    c.drawString(margin, margin, bottom_left_text)
    c.drawRightString(width - margin, margin, bottom_right_text)
    # draw the qr code
    print("fullName:" + fullName)
    print("qrcode:" + qrcode_id)
    if qrcode_id is not None and qrcode_id != "":
        print("draw qr code")
        size = 20 * mm
        qrcode_margin = 5 * mm
        qr = QRCodeImage(qrcode_id, size=size)
        qr.drawOn(c, width - size - qrcode_margin, height - 25 * mm - size)
    c.save()
    images = convert_from_path(pdfPath)
    imagePath = os.path.join("docs", pdfName + ".jpg")
    images[0].save(imagePath, "JPEG")
    print_with_selected_printer(print_name, imagePath)


def create_docs_folder():
    if not os.path.exists("docs"):
        os.makedirs("docs")


add_poppler_to_path()

create_docs_folder()


# app server code


# Set up the server parameters
host = "0.0.0.0"
port = 8000  # 3000, 5000, 8080, 8000

# Generate an SSL/TLS certificate
certfile = "cert.pem"
keyfile = "key.pem"

# Create the HTTP request handler


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        super().end_headers()

    def do_OPTIONS(self):
        print("OPTIONS")
        print(self.path)
        self.send_response(200, "ok")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hello, world!")

    def do_POST(self):
        print(self.path)
        if self.path == "/print":
            # print the ip address of the client
            print(self.client_address)
            print("POST /print")
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            jsondata = json.loads(body)

            ticket_type = jsondata.get("ticket_type", "")

            if ticket_type == "":
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(
                    {"error": "ticket_type is required"}).encode())
                return

            fullName = jsondata.get("fullName") if jsondata.get(
                "fullName") is not None else ""
            company = jsondata.get("company") if jsondata.get(
                "company") is not None else ""
            title = jsondata.get("title") if jsondata.get(
                "title") is not None else ""
            top_left_text = jsondata.get("top_left_text") if jsondata.get(
                "top_left_text") is not None else ""
            top_right_text = jsondata.get("top_right_text") if jsondata.get(
                "top_right_text") is not None else ""
            bottom_left_text = jsondata.get("bottom_left_text") if jsondata.get(
                "bottom_left_text") is not None else ""
            bottom_right_text = jsondata.get("bottom_right_text") if jsondata.get(
                "bottom_right_text") is not None else ""
            qrcode_id = jsondata.get("qrcode_id") if jsondata.get(
                "qrcode_id") is not None else ""
            language = jsondata.get("language") if jsondata.get(
                "language") is not None else "DONT SKIP"

            print_badge(
                fullName=fullName,
                company=company,
                title=title,
                top_left_text=top_left_text,
                top_right_text=top_right_text,
                bottom_left_text=bottom_left_text,
                bottom_right_text=bottom_right_text,
                qrcode_id=qrcode_id,
                language=language,
            )

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Card printed")


# Create the HTTPS server
httpd = socketserver.TCPServer((host, port), MyHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(
    httpd.socket, certfile=certfile, keyfile=keyfile, server_side=True)

# log my ip address
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
print("Your Computer IP Address is:" + IPAddr)
# other devices can access the server using the IP address printed above
print(f"Server running on https://{IPAddr}:{port}")


# Start the server
print(f"Server running on https://{host}:{port}")
httpd.serve_forever()
