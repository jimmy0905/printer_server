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
PRINTER_NAME = "Brother QL-820NWB"


# set the font
FONTNAME = "Msjh"
pdfmetrics.registerFont(TTFont(FONTNAME, "./msjh.ttf"))
FONTNAMEBOLD = "MsjhBold"
pdfmetrics.registerFont(TTFont(FONTNAMEBOLD, "./msjhbd.ttc"))
# Convert dimensions from mm to points (1mm = 2.83465 points)

# Badge configuration
WIDTH, HEIGHT = 90 * mm, 62 * mm
MARGIN = 1 * mm
NAME_LINE_HEIGHT = 10 * mm
COMPANY_LINE_HEIGHT = 6* mm
QRCODE_SIZE = 25 * mm
QRCODE_MARGIN = 2 * mm

CORNER_MARGIN = 1 * mm


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
            # print("Landscape mode, tall image, rotate bitmap.")
            img = img.rotate(90, expand=True)
    else:
        if img.size[1] < img.size[0]:
            # print("Portrait mode, wide image, rotate bitmap.")
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
    tl,
    tr,
    bl,
    br,
):
    # remove the all the file name limit characters
    fullname = remove_not_allowed_chars(fullname)
    company = remove_not_allowed_chars(company)
    pdfName = fullname + "_" + company + ".pdf"
    pdf_path = os.path.join("docs", pdfName)
    # create the pdf
    c = canvas.Canvas(pdf_path, pagesize=(WIDTH, HEIGHT))
    # config the font and wrap the text - fullName
    custom_text_wrapper = CustomTextWrapper(width=15)
    wrapped_fullname = custom_text_wrapper.fill(fullname)
    wrapped_fullname_lines = wrapped_fullname.splitlines()
    fullname_line_used = 0
    # draw the text - fullName
    for i, line in enumerate(wrapped_fullname_lines):
        c.setFont(FONTNAMEBOLD, 26)
        c.drawString(MARGIN, HEIGHT - 10 * mm - (fullname_line_used * NAME_LINE_HEIGHT), line)
        fullname_line_used = fullname_line_used + 1

    # config the font and wrap the text - company
    custom_text_wrapper = CustomTextWrapper(width=20)
    wrapped_company = custom_text_wrapper.fill(company)
    wrapped_company_lines = wrapped_company.splitlines()
    company_line_used = 0
    # draw the text - company
    for i, line in enumerate(wrapped_company_lines):
        c.setFont(FONTNAME, 14)
        c.drawString(MARGIN, HEIGHT - 10 * mm - (company_line_used * COMPANY_LINE_HEIGHT) - 28* mm, line)
        company_line_used = company_line_used + 1

    # draw the qr code
    if qrcode_context is not None and qrcode_context != "":
        qr = QRCodeImage(qrcode_context, size=QRCODE_SIZE)
        qr.drawOn(
            c, WIDTH - QRCODE_SIZE - QRCODE_MARGIN, HEIGHT - 30 * mm - QRCODE_SIZE
        )
    # draw the text - top left
    c.setFont(FONTNAME, 10)
    # get the height and width of the text
    tl_width, tl_height = c.stringWidth(tl, FONTNAME, 10), c._leading
    c.drawString(CORNER_MARGIN , HEIGHT - CORNER_MARGIN - tl_height, tl)
    # draw the text - top right
    tr_width, tr_height = c.stringWidth(tr, FONTNAME, 10), c._leading
    c.drawString(WIDTH - CORNER_MARGIN - tr_width, HEIGHT - CORNER_MARGIN - tr_height, tr)
    # draw the text - bottom left
    bl_width, bl_height = c.stringWidth(bl, FONTNAME, 10), c._leading
    c.drawString(CORNER_MARGIN, CORNER_MARGIN, bl)
    # draw the text - bottom right
    br_width, br_height = c.stringWidth(br, FONTNAME, 10), c._leading
    c.drawString(WIDTH - CORNER_MARGIN - br_width, CORNER_MARGIN, br)
    c.save()
    # convert the pdf to image
    images = convert_from_path(pdf_path)
    image_path = os.path.join("docs", pdfName + ".jpg")
    images[0].save(image_path, "JPEG")
    # print the image
    print_with_selected_printer(PRINTER_NAME, image_path)
