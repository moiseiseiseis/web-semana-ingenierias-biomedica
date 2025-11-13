from models import db

class Equipo(db.Model):
    __tablename__ = "equipos"
    id = db.Column(db.Integer, primary_key=True)
    clave_equipo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    grado = db.Column(db.Integer, nullable=False)  # 1,3,5,7,9
    integrantes = db.Column(db.Text, nullable=False)  # Texto libre (nombre1; nombre2; ...)
    nombre_cartel = db.Column(db.String(200), nullable=False)
    tipo_evaluacion = db.Column(db.String(50), nullable=False)  # "Cartel" | "Proyecto Modular"
    estado = db.Column(db.String(20), nullable=False, default="Pendiente")  # Pendiente | Calificado
