import qrcode
import qrcode.image.svg

def create_qr_code(data: str) -> str:
    """ Creates a QR code as an svg string to be used in a
        HTML file

        Args:
            data (str): the url to turn into a QR code
        
        Returns (str):
            the SVG to be put into a HTML file
    """
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