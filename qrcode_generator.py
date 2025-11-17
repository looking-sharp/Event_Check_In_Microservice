import qrcode
import qrcode.image.svg

def create_qr_code(data: str) -> str:
    factory = qrcode.image.svg.SvgImage
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(image_factory=factory)
    svg_bytes = img.to_string()
    svg_str = svg_bytes.decode("utf-8") 
    svg_str = svg_str.replace("<svg:rect", "<rect").replace("</svg:rect>", "</rect>")
    return svg_str