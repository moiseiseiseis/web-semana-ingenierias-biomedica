from flask import Blueprint, render_template, abort
from models.evento import Evento
from datetime import date

bp = Blueprint("main", __name__)

@bp.route("/")
def home():
    """Página principal — muestra todos los eventos publicados"""
    eventos = (
        Evento.query
        .filter_by(published=True)
        .order_by(Evento.fecha, Evento.hora_inicio)
        .all()
    )

    # Panel lateral (logos, ubicación, pasos)
    side = {
        "ubicacion": {
            "sede": "CUTLAJO",
            "direccion": "Guadalajara, Jalisco",
            "fechas": "18–22 noviembre 2025",
            "maps_url": "https://www.google.com/maps/place/Centro+Universitario+de+Tlajomulco+(CUTLAJO)+-+UDG/@20.4645456,-103.4135878,17z/data=!3m1!4b1!4m6!3m5!1s0x842f513ccb331403:0x87335adf8940dff9!8m2!3d20.4645456!4d-103.4135878!16s%2Fg%2F11k7jxw3qf?entry=ttu&g_ep=EgoyMDI1MTExMC4wIKXMDSoASAFQAw%3D%3D",
        },
        "pasos": [
            {"n": 1, "t": "Crea tu cuenta", "d": "Usa el registro unificado: alumno, académico o equipo."},
            {"n": 2, "t": "Completa tu perfil", "d": "Si eres alumno, agrega tu código. Si eres académico, asigna equipos."},
            {"n": 3, "t": "Participa", "d": "Consulta horarios y asiste a tus eventos."},
        ],
        "logos": [
            {"src": "img/logo_cu.png", "alt": "Logo CU"},
            {"src": "img/logo_si.png", "alt": "Logo Semana"},
        ],
    }

    return render_template("home.html", eventos=eventos, side=side)


@bp.route("/evento/<slug>", endpoint="evento_detalle")
def evento_detalle(slug):
    """Detalle de un evento individual"""
    ev = Evento.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template("evento_detalle.html", ev=ev)


@bp.route("/tutorial")
def tutorial():
    """Página del tutorial"""
    return render_template("tutorial.html")
