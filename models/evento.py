from datetime import datetime, time
from slugify import slugify
from . import db

class Evento(db.Model):
    __tablename__ = "eventos"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50), default="Conferencia")  # Conferencia/Taller/Presentación
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=True)
    lugar = db.Column(db.String(120), nullable=True)

    ponente_nombre = db.Column(db.String(120), nullable=True)
    ponente_afiliacion = db.Column(db.String(160), nullable=True)

    descripcion_corta = db.Column(db.Text, nullable=True)
    imagen = db.Column(db.String(255), nullable=True)  # p. ej. "img/eventos/ai.jpg"
    slug = db.Column(db.String(220), unique=True, index=True)
    published = db.Column(db.Boolean, default=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.slug:
            self.slug = slugify(self.titulo)

    def horario_str(self):
        hi = self.hora_inicio.strftime("%H:%M")
        hf = self.hora_fin.strftime("%H:%M") if self.hora_fin else ""
        if hf:
            return f"{hi}–{hf}"
        return hi
