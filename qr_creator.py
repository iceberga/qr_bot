import qrcode
from qrcode.image.pure import PyPNGImage


def create_qr(user_id):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.make(fit=True)
    img = qrcode.make(f"Капучино 300 мл\n{user_id}", image_factory=PyPNGImage)

    return img
