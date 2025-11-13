# models/asignacion.py
from models import db

class Asignacion(db.Model):
    __tablename__ = "asignaciones"
    id = db.Column(db.Integer, primary_key=True)
    academico_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    equipo_id    = db.Column(db.Integer, db.ForeignKey("equipos.id"), nullable=False, index=True)

    # Un académico no debe tener la misma clave dos veces
    __table_args__ = (db.UniqueConstraint("academico_id", "equipo_id", name="uq_asignacion_academico_equipo"),)
