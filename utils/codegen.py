# utils/codegen.py
from models.equipo import Equipo
from models import db

def generate_equipo_code(grado: int) -> str:
    """
    Genera un código único con formato:
    INBI<Grado>-<Número consecutivo de dos dígitos>
    Ejemplo: INBI1-01, INBI7-03
    """
    prefix = f"INBI{grado}"
    existing_count = Equipo.query.filter_by(grado=grado).count()
    consecutive = existing_count + 1
    return f"{prefix}-{consecutive:02d}"