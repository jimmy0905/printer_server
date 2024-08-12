import win32ui
import win32con
from PIL import Image, ImageWin
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import mm
from custom_text_wrapper import CustomTextWrapper
from util import remove_not_allowed_chars, add_poppler_to_path, create_docs_folder
from reportlab_qrcode import QRCodeImage
from pdf2image import convert_from_path
import os
from reportlab.pdfgen import canvas

# printname
PRINTER_NAME = "Fax"


# set the font
FONTNAME = "Msjh"
pdfmetrics.registerFont(TTFont(FONTNAME, "./msjh.ttf"))
FONTNAMEBOLD = "MsjhBold"
pdfmetrics.registerFont(TTFont(FONTNAMEBOLD, "./msjhbd.ttc"))
# Convert dimensions from mm to points (1mm = 2.83465 points)

# Badge configuration
WIDTH, HEIGHT = 90 * mm, 62 * mm
MARGIN = 7 * mm
LINE_HEIGHT = 8 * mm
QRCODE_SIZE = 20 * mm
QRCODE_MARGIN = 5 * mm


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
            #print("Landscape mode, tall image, rotate bitmap.")
            img = img.rotate(90, expand=True)
    else:
        if img.size[1] < img.size[0]:
            #print("Portrait mode, wide image, rotate bitmap.")
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


def create_badge(
    fullname,
    company,
    qrcode_context,
):
    # remove the all the file name limit characters
    fullname = remove_not_allowed_chars(fullname)
    company = remove_not_allowed_chars(company)
    pdfName = (
        fullname + "_" + company + ".pdf"
    )
    pdf_path = os.path.join("docs", pdfName)
    # create the pdf
    c = canvas.Canvas(pdf_path, pagesize=(WIDTH, HEIGHT))
    # config the font and wrap the text - fullName
    custom_text_wrapper = CustomTextWrapper(width=15)
    wrapped_fullname = custom_text_wrapper.fill(fullname)
    wrapped_fullname_lines = wrapped_fullname.splitlines()
    line_used = 0
    # draw the text - fullName
    for i, line in enumerate(wrapped_fullname_lines):
        c.setFont(FONTNAMEBOLD, 20)
        c.drawString(MARGIN, HEIGHT - 10 * mm - (line_used * LINE_HEIGHT), line)
        line_used = line_used + 1

    # config the font and wrap the text - company
    custom_text_wrapper = CustomTextWrapper(width=20)
    wrapped_company = custom_text_wrapper.fill(company)
    wrapped_company_lines = wrapped_company.splitlines()

    # draw the text - company
    for i, line in enumerate(wrapped_company_lines):
        c.setFont(FONTNAME, 14)
        c.drawString(MARGIN, HEIGHT - 10 * mm - (line_used * LINE_HEIGHT), line)
        line_used = line_used + 1

    # draw the qr code
    if qrcode_context is not None and qrcode_context != "":
        qr = QRCodeImage(qrcode_context, size=QRCODE_SIZE)
        qr.drawOn(
            c, WIDTH - QRCODE_SIZE - QRCODE_MARGIN, HEIGHT - 25 * mm - QRCODE_SIZE
        )
    c.save()
    # convert the pdf to image
    images = convert_from_path(pdf_path)
    image_path = os.path.join("docs", pdfName + ".jpg")
    images[0].save(image_path, "JPEG")
    # print the image
    print_with_selected_printer(PRINTER_NAME, image_path)
