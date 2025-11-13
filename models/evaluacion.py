from models import db

class Evaluacion(db.Model):
    __tablename__ = "evaluaciones"
    id = db.Column(db.Integer, primary_key=True)
    equipo_id = db.Column(db.Integer, db.ForeignKey("equipos.id"), nullable=False)
    academico_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # ← permitir NULL mientras no haya calificación
    calificacion = db.Column(db.Float, nullable=True)

    comentarios = db.Column(db.Text, nullable=True)

    # estado con default “Pendiente”
    estado = db.Column(db.String(20), nullable=False, server_default="Pendiente")
