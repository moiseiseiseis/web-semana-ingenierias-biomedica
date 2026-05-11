from flask import Blueprint, jsonify, abort
from models.evento import Evento
from datetime import date

bp = Blueprint("main", __name__)

# ==========================================
# HELPER: Función para serializar el modelo
# ==========================================
def serialize_evento(ev):
    """Convierte el objeto de SQLAlchemy a un diccionario que JSON puede entender"""
    return {
        "id": ev.id,
        "titulo": ev.titulo,
        "tipo": ev.tipo,
        "ponente_nombre": getattr(ev, 'ponente_nombre', None),
        # Convertimos la fecha y hora a string para evitar errores en JSON
        "fecha": ev.fecha.strftime("%d/%m/%Y") if ev.fecha else None,
        "hora_inicio": str(ev.hora_inicio) if ev.hora_inicio else None,
        "imagen": ev.imagen,
        "descripcion_corta": ev.descripcion_corta,
        "slug": ev.slug,
        "lugar": getattr(ev, 'lugar', None)
    }

# ==========================================
# RUTAS API
# Te sugiero añadir el prefijo '/api' para no confundirlas con las rutas de React
# ==========================================

@bp.route("/api/home")
def home_data():
    """API para la página principal — devuelve eventos y datos del aside"""
    eventos = (
        Evento.query
        .filter_by(published=True)
        .order_by(Evento.fecha, Evento.hora_inicio)
        .all()
    )

    # Convertimos la lista de objetos SQLAlchemy a una lista de diccionarios
    eventos_json = [serialize_evento(ev) for ev in eventos]

    # Panel lateral (se queda igual porque ya es un diccionario válido)
    side = {
        "ubicacion": {
            "sede": "CUTLAJO",
            "direccion": "Tlajomulco de Zúñiga, Jalisco",
            "fechas": "18–22 noviembre 2025", # Puedes actualizar el año si quieres para el portafolio
            "maps_url": "https://www.google.com/maps/place/Centro+Universitario+de+Tlajomulco+(CUTLAJO)+-+UDG/@20.4645456,-103.4135878,17z/data=!3m1!4b1!4m6!3m5!1s0x842f513ccb331403:0x87335adf8940dff9!8m2!3d20.4645456!4d-103.4135878!16s%2Fg%2F11k7jxw3qf?entry=ttu&g_ep=EgoyMDI1MTExMC4wIKXMDSoASAFQAw%3D%3D",
        },
        "pasos": [
            {"n": 1, "t": "Crea tu cuenta", "d": "Usa el registro unificado: alumno, académico o equipo."},
            {"n": 2, "t": "Completa tu perfil", "d": "Si eres alumno, agrega tu código. Si eres académico, asigna equipos."},
            {"n": 3, "t": "Participa", "d": "Consulta horarios y asiste a tus eventos."},
        ],
        "logos": [
            {"src": "/static/img/logo_cu.png", "alt": "Logo CU"},
            {"src": "/static/img/logo_si.png", "alt": "Logo Semana"},
        ],
    }

    # Devolvemos un JSON limpio
    return jsonify({
        "eventos": eventos_json,
        "side": side
    })


@bp.route("/api/evento/<slug>")
def evento_detalle_data(slug):
    """API para el detalle de un evento individual"""
    ev = Evento.query.filter_by(slug=slug, published=True).first_or_404()
    return jsonify(serialize_evento(ev))


@bp.route("/api/tutorial")
def tutorial_data():
    """
    Si el tutorial es estático, podrías simplemente armarlo en React.
    Si necesitas datos del backend, los mandas por aquí.
    """
    return jsonify({"mensaje": "Datos del tutorial listos para React"})