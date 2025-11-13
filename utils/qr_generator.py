import qrcode
import os

def generate_qr(url: str, filename: str = "qr.png", out_dir: str = "static/qr"):
    os.makedirs(out_dir, exist_ok=True)
    img = qrcode.make(url)
    path = os.path.join(out_dir, filename)
    img.save(path)
    return path
