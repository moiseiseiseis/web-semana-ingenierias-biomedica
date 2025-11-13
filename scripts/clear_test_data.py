# scripts/clear_test_data.py
import os
import sys

# ✅ Asegurar que Python puede encontrar app.py y models/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app import app
from models import db
from models.equipo import Equipo
from models.evaluacion import Evaluacion
from models.asignacion import Asignacion
from models.user import User

with app.app_context():
    print("🧹 Eliminando registros de prueba...")

    # Borramos dependencias primero para evitar errores de integridad
    Evaluacion.query.delete()
    Asignacion.query.delete()
    Equipo.query.delete()

    # Mantener admin y borrar resto
    User.query.filter(User.role != "admin").delete()

    db.session.commit()
    print("✅ Base de datos limpia (solo queda el admin).")
