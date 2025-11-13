# utils/export_pdf.py
from flask import render_template, current_app
import os
from io import BytesIO

# Usaremos xhtml2pdf para evitar dependencias nativas en Windows
# (No importamos nada al nivel de módulo que reviente la app)
def render_pdf(datos, grado=None):
    try:
        html = render_template("export_pdf.html", datos=datos, grado=grado)

        # Importar aquí (lazy) para no romper el arranque si falta el paquete
        from xhtml2pdf import pisa

        out_dir = os.path.join(current_app.root_path, "static", "exports")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "resultados.pdf")

        # Generar PDF
        pdf_bytes = BytesIO()
        result = pisa.CreatePDF(src=html, dest=pdf_bytes, encoding='utf-8')
        if result.err:
            current_app.logger.error("xhtml2pdf: error al generar el PDF")
            return None

        with open(out_path, "wb") as f:
            f.write(pdf_bytes.getvalue())

        return out_path
    except Exception as e:
        current_app.logger.error(f"Error generando PDF: {e}")
        return None
