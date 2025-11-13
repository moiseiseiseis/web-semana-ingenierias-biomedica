# routes/admin.py
import os
from datetime import date, time

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    abort,
)
from flask_login import login_user, logout_user, login_required, current_user

from forms.login_form import LoginForm
from models import db
from models.user import User
from models.equipo import Equipo
from models.evaluacion import Evaluacion
from models.evento import Evento
from utils.decorators import role_required
from utils.export_pdf import render_pdf

bp = Blueprint("admin", __name__)

# ---------- LOGIN / LOGOUT ----------

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.role == "admin" and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("admin.dashboard"))
        flash("Credenciales inválidas o rol incorrecto.", "error")
    return render_template("login.html", form=form, titulo="Login Admin")


@bp.route("/logout")
@login_required
@role_required("admin")
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


# ---------- DASHBOARD PRINCIPAL ----------

@bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    grado = request.args.get("grado", type=int)

    query = Equipo.query
    if grado:
        query = query.filter_by(grado=grado)
    equipos = query.order_by(Equipo.grado.asc(), Equipo.nombre_cartel.asc()).all()

    # Resumen rápido
    equipos_total = Equipo.query.count()
    equipos_calificados = Equipo.query.filter_by(estado="Calificado").count()
    academicos_total = User.query.filter_by(role="academico").count()
    alumnos_total = User.query.filter_by(role="alumno").count()

    # Habilitar exportar si todos están calificados
    if grado:
        total = Equipo.query.filter_by(grado=grado).count()
        calificados = Equipo.query.filter_by(grado=grado, estado="Calificado").count()
        puede_exportar = (total > 0 and total == calificados)
    else:
        total = Equipo.query.count()
        calificados = Equipo.query.filter_by(estado="Calificado").count()
        puede_exportar = (total > 0 and total == calificados)

    # Listas para pestañas
    academicos = User.query.filter_by(role="academico").all()
    alumnos = User.query.filter_by(role="alumno").all()

    resumen = {
        "equipos_total": equipos_total,
        "equipos_calificados": equipos_calificados,
        "academicos_total": academicos_total,
        "alumnos_total": alumnos_total,
    }

    return render_template(
        "admin_dashboard.html",
        equipos=equipos,
        grado=grado,
        puede_exportar=puede_exportar,
        resumen=resumen,
        academicos=academicos,
        alumnos=alumnos,
    )


# ---------- EXPORTAR PDF ----------

@bp.route("/exportar")
@login_required
@role_required("admin")
def exportar():
    grado = request.args.get("grado", type=int)

    query = db.session.query(
        Equipo.id,
        Equipo.clave_equipo,
        Equipo.grado,
        Equipo.nombre_cartel,
        Equipo.tipo_evaluacion,
    )

    if grado:
        query = query.filter(Equipo.grado == grado)

    equipos = query.all()

    datos = []
    for e in equipos:
        evs = db.session.query(Evaluacion).filter(
            Evaluacion.equipo_id == e.id
        ).all()
        mejor = max(
            [ev.calificacion for ev in evs if ev.calificacion is not None],
            default=None,
        )
        datos.append(
            {
                "grado": e.grado,
                "clave_equipo": e.clave_equipo,
                "nombre_cartel": e.nombre_cartel,
                "tipo": e.tipo_evaluacion,
                "calificacion": mejor if mejor is not None else "-",
            }
        )

    # Ordenar por grado y calificación desc
    datos.sort(
        key=lambda x: (
            x["grado"],
            -(x["calificacion"] if isinstance(x["calificacion"], (int, float)) else -1),
        )
    )

    pdf_path = render_pdf(datos=datos, grado=grado)
    if not pdf_path:
        flash("No fue posible generar el PDF (ver logs).", "error")
        return redirect(url_for("admin.dashboard"))
    return send_file(pdf_path, as_attachment=True, download_name="resultados.pdf")


# ---------- UTIL: TOKEN DE SETUP ----------

def _check_token_or_404():
    """Valida el token de setup usando ADMIN_SETUP_TOKEN (env var)."""
    token = request.args.get("token")
    expected = os.getenv("ADMIN_SETUP_TOKEN")
    if not expected or token != expected:
        abort(404)


# ---------- SETUP ADMIN (CREAR / RESET) ----------

@bp.route("/setup-admin")
def setup_admin():
    """
    Crea o actualiza la cuenta admin en PRODUCCIÓN.
    Protegido con ADMIN_SETUP_TOKEN (querystring ?token=...).
    """
    _check_token_or_404()

    admin = User.query.filter_by(email="admin@institucion.edu").first()

    if not admin:
        admin = User(
            nombre="Admin",
            email="admin@institucion.edu",
            role="admin",
        )
        admin.set_password("admin123")  # contraseña en producción (luego la cambias)
        db.session.add(admin)
        msg = "✔ Admin creado."
    else:
        admin.role = "admin"
        admin.set_password("admin123")
        msg = "✔ Admin actualizado (password reseteado)."

    db.session.commit()
    return msg, 200


# ---------- SEED DE EVENTOS (FLYER EXACTO) ----------

@bp.route("/seed-eventos")
def seed_eventos():
    """Siembra los eventos EXACTOS del flyer en PRODUCCIÓN (solo con token)."""
    _check_token_or_404()

    EVENTS = [
        dict(
            slug="presentacion-proyectos-1-2",
            titulo="Presentación de proyectos finales",
            descripcion_corta="Alumnas y alumnos 1º y 2º",
            tipo="Presentación",
            ponente_nombre=None,
            ponente_afiliacion=None,
            fecha=date(2025, 11, 28),
            hora_inicio=time(7, 0),
            hora_fin=time(10, 0),
            lugar="CUTLAJO - Edificio E",
            published=True,
        ),
        dict(
            slug="conferencia-ai-across-scales",
            titulo='Conferencia “Artificial Intelligence Across Scales”',
            descripcion_corta="",
            tipo="Conferencia",
            ponente_nombre="Mtro. Moisés Sotelo Rodríguez",
            ponente_afiliacion="BioDev Network",
            fecha=date(2025, 11, 28),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            lugar="Coworking CUTLAJO",
            published=True,
        ),
        dict(
            slug="cinco-voces-perspectivas",
            titulo="Cinco voces, cinco perspectivas, una pasión: Ingeniería Biomédica",
            descripcion_corta="Alumn@s de últimos semestres",
            tipo="Foro",
            ponente_nombre=None,
            ponente_afiliacion=None,
            fecha=date(2025, 11, 28),
            hora_inicio=time(11, 0),
            hora_fin=time(12, 0),
            lugar="Coworking CUTLAJO",
            published=True,
        ),
        dict(
            slug="taller-senales-ml-bradicardias",
            titulo='Taller “De Señales a Diagnósticos: ML en Bradicardias”',
            descripcion_corta="Taller práctico de machine learning en bradicardias",
            tipo="Taller",
            ponente_nombre=None,
            ponente_afiliacion=None,
            fecha=date(2025, 11, 28),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            lugar="Coworking CUTLAJO",
            published=True,
        ),
        dict(
            slug="presentacion-modulares-finales",
            titulo="Presentación de Modulares y Proyectos finales",
            descripcion_corta="Alumn@s de Ingeniería Biomédica",
            tipo="Presentación",
            ponente_nombre=None,
            ponente_afiliacion=None,
            fecha=date(2025, 11, 28),
            hora_inicio=time(12, 0),
            hora_fin=time(15, 0),
            lugar="CUTLAJO - Edificio E",
            published=True,
        ),
        dict(
            slug="pelea-de-sumos",
            titulo="Pelea de sumos",
            descripcion_corta="Dentro de la agenda de presentación de proyectos modulares",
            tipo="Exhibición",
            ponente_nombre=None,
            ponente_afiliacion=None,
            fecha=date(2025, 11, 28),
            hora_inicio=time(13, 30),
            hora_fin=time(15, 0),
            lugar="Coworking CUTLAJO",
            published=True,
        ),
    ]

    db.session.query(Evento).delete()
    for d in EVENTS:
        db.session.add(Evento(**d))
    db.session.commit()

    return f"✔ Se cargaron {len(EVENTS)} eventos (flyer exacto) en producción."
