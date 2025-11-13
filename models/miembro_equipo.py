# models/miembro_equipo.py
from models import db

class MiembroEquipo(db.Model):
    __tablename__ = "miembros_equipo"
    id = db.Column(db.Integer, primary_key=True)
    equipo_id = db.Column(db.Integer, db.ForeignKey("equipos.id"), nullable=False, index=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    student_code = db.Column(db.String(32), nullable=False, index=True)  # p.ej. código de estudiante

    __table_args__ = (
        db.UniqueConstraint("equipo_id", "student_code", name="uq_equipo_studentcode"),
    )
