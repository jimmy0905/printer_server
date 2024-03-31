import win32ui, win32con, win32print
from PIL import Image, ImageWin
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
import textwrap
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab_qrcode import QRCodeImage
from pdf2image import convert_from_path
import os


# set the font
FONTNAME = "Msjh"
pdfmetrics.registerFont(TTFont(FONTNAME, "./msjh.ttf"))
# Convert dimensions from mm to points (1mm = 2.83465 points)

width, height = 90 * mm, 62 * mm
margin = 5 * mm


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
    pdfName = fullName + "_" + company + ".pdf"
    pdfPath = os.path.join("docs", pdfName)
    c = canvas.Canvas(pdfPath, pagesize=(width, height))

    if language == "en":
        fullName = fullName.split(" ")[1:]
        fullName = " ".join(fullName)
    elif language == "DONT SKIP":
        fullName = fullName
    else:
        fullName = fullName[:-2]

    wrapped_fullName = textwrap.fill(fullName, 20)
    wrapped_fullName_lines = wrapped_fullName.splitlines()

    line_used = 0
    line_height = 8 * mm
    for i, line in enumerate(wrapped_fullName_lines):
        c.setFont(FONTNAME, 20)
        c.drawString(margin, height - 15 * mm - (line_used * line_height), line)
        line_used = line_used + 1

    wrapped_company = textwrap.fill(company, 20)
    wrapped_company_lines = wrapped_company.splitlines()

    for i, line in enumerate(wrapped_company_lines):
        c.setFont(FONTNAME, 14)
        c.drawString(margin, height - 15 * mm - (line_used * line_height), line)
        line_used = line_used + 1

    # draw the 4 concer
    c.setFont(FONTNAME, 8)
    c.drawString(margin, height - margin, top_left_text)
    c.drawRightString(width - margin, height - margin, top_right_text)
    c.drawString(margin, margin, bottom_left_text)
    c.drawRightString(width - margin, margin, bottom_right_text)
    # draw the qr code
    if qrcode_id is not None:

        size = 20 * mm
        qrcode_margin = 3 * mm
        qr = QRCodeImage(qrcode_id, size=size)
        qr.drawOn(c, width - size - qrcode_margin, height - 25 * mm - size)
    c.save()
    images = convert_from_path(pdfPath)
    imagePath = os.path.join("docs", pdfName + ".jpg")
    images[0].save(imagePath, "JPEG")
    print_name = win32print.GetDefaultPrinter()
    # print_name = "Brother QL-820NWB"
    print_with_selected_printer(print_name, imagePath)


def create_docs_folder():
    if not os.path.exists("docs"):
        os.makedirs("docs")


add_poppler_to_path()

create_docs_folder()


# app server code

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route("/print", methods=["POST"])
def print_card():
    jsondata = request.json
    print(jsondata)
    ticket_type = (
        jsondata.get("ticket_type") if jsondata.get("ticket_type") is not None else ""
    )
    if ticket_type == "student_full":
        return "Student ticket is not allowed to print"
    if ticket_type == "":
        return {"error": "ticket_type is required"}
    fullName = jsondata.get("fullName") if jsondata.get("fullName") is not None else ""
    company = jsondata.get("company") if jsondata.get("company") is not None else ""
    title = jsondata.get("title") if jsondata.get("title") is not None else ""
    top_left_text = (
        jsondata.get("top_left_text")
        if jsondata.get("top_left_text") is not None
        else ""
    )
    top_right_text = (
        jsondata.get("top_right_text")
        if jsondata.get("top_right_text") is not None
        else ""
    )
    bottom_left_text = (
        jsondata.get("bottom_left_text")
        if jsondata.get("bottom_left_text") is not None
        else ""
    )
    bottom_right_text = (
        jsondata.get("bottom_right_text")
        if jsondata.get("bottom_right_text") is not None
        else ""
    )
    qrcode_id = (
        jsondata.get("qrcode_id") if jsondata.get("qrcode_id") is not None else None
    )
    language = (
        jsondata.get("language")
        if jsondata.get("language") is not None
        else "DONT SKIP"
    )
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
    return "Card printed"

@app.route("/test", methods=["GET"])
def test():
    return "Hello World"

app.run(host="0.0.0.0", port=5000)