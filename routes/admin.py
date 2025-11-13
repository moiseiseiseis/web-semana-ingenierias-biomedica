# routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
import os
from flask_login import login_user, logout_user, login_required, current_user
from forms.login_form import LoginForm
from models import db
from models.user import User
from models.equipo import Equipo
from models.evaluacion import Evaluacion
from utils.decorators import role_required
from utils.export_pdf import render_pdf



bp = Blueprint("admin", __name__)
from datetime import date, time
from models.evento import Evento


@bp.route("/init-admin")
def init_admin():
    """
    Inicializa o resetea el usuario admin en la BD actual (Render).
    PROTEGER con token en query: /admin/init-admin?token=TU_TOKEN
    """
    token = request.args.get("token")
    expected = os.getenv("ADMIN_SETUP_TOKEN")

    if not expected or token != expected:
        # No revelamos nada, solo 403
        return "Forbidden", 403

    from models.user import User
    from models import db

    email = "admin@institucion.edu"
    password = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin123")

    admin = User.query.filter_by(email=email, role="admin").first()
    if not admin:
        admin = User(nombre="Admin", email=email, role="admin")
        admin.set_password(password)
        db.session.add(admin)
        msg = "Admin creado"
    else:
        admin.set_password(password)
        msg = "Password de admin actualizada"

    db.session.commit()
    return f"{msg} correctamente para {email}.", 200


@bp.route("/seed-eventos")
def seed_eventos():
    """
    Crea los eventos del programa en la BD actual (Render).
    Proteger con token: /admin/seed-eventos?token=TU_TOKEN
    """
    token = request.args.get("token")
    expected = os.getenv("ADMIN_SETUP_TOKEN")  # reutilizamos el mismo token del init-admin

    if not expected or token != expected:
        return "Forbidden", 403

    from models import db

    data = [
        # OJO: usa exactamente los eventos del flyer
        {
            "slug": "apertura-semana-biomedica",
            "titulo": "Ceremonia de Apertura",
            "descripcion_corta": "Inicio de actividades y mensaje de bienvenida.",
            "tipo": "Ceremonia",
            "ponente_nombre": "Comité Académico",
            "ponente_afiliacion": "CUCEI",
            "fecha": date(2025, 11, 18),
            "hora_inicio": time(9, 0),
            "hora_fin": time(9, 30),
            "lugar": "Auditorio Principal",
            "imagen": None,
            "published": True,
        },
        {
            "slug": "taller-senales-biomedicas",
            "titulo": "Taller: Procesamiento de Señales Biomédicas",
            "descripcion_corta": "Pipeline de filtros, features y visualización.",
            "tipo": "Taller",
            "ponente_nombre": "Dra. A. Martínez",
            "ponente_afiliacion": "Laboratorio de Neuroingeniería",
            "fecha": date(2025, 11, 18),
            "hora_inicio": time(10, 0),
            "hora_fin": time(12, 0),
            "lugar": "Lab 2",
            "imagen": None,
            "published": True,
        },
        {
            "slug": "conferencia-innovacion-protesis",
            "titulo": "Conferencia: Innovación en Prótesis Inteligentes",
            "descripcion_corta": "Tendencias en sensores y control.",
            "tipo": "Conferencia",
            "ponente_nombre": "M. García",
            "ponente_afiliacion": "SEVID",
            "fecha": date(2025, 11, 19),
            "hora_inicio": time(11, 0),
            "hora_fin": time(12, 0),
            "lugar": "Aula Magna",
            "imagen": None,
            "published": True,
        },
        # Aquí agrega el resto del programa EXACTO del flyer
        # ...
    ]

    creados = 0
    for d in data:
        existing = Evento.query.filter_by(slug=d["slug"]).first()
        if existing:
            continue
        ev = Evento(**d)
        db.session.add(ev)
        creados += 1

    db.session.commit()
    return f"Eventos sembrados: {creados}", 200



# -------------------- Auth --------------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
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


# -------------------- Dashboard --------------------
@bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    grado = request.args.get("grado", type=int)

    # --- Equipos (con filtro opcional) ---
    equipos_q = Equipo.query
    if grado:
        equipos_q = equipos_q.filter_by(grado=grado)
    equipos = equipos_q.order_by(Equipo.grado.asc(), Equipo.nombre_cartel.asc()).all()

    # --- Usuarios por rol ---
    academicos = User.query.filter_by(role="academico").order_by(User.nombre.asc()).all()
    alumnos    = User.query.filter_by(role="alumno").order_by(User.nombre.asc()).all()

    # --- Resumen (contadores rápidos) ---
    resumen = {
        "equipos_total": Equipo.query.count(),
        "equipos_calificados": Equipo.query.filter_by(estado="Calificado").count(),
        "academicos_total": len(academicos),
        "alumnos_total": len(alumnos),
    }

    # --- Exportar habilitado solo si todos los equipos (del filtro) están calificados ---
    if grado:
        total = Equipo.query.filter_by(grado=grado).count()
        calif = Equipo.query.filter_by(grado=grado, estado="Calificado").count()
        puede_exportar = (total > 0 and total == calif)
    else:
        total = resumen["equipos_total"]
        calif = resumen["equipos_calificados"]
        puede_exportar = (total > 0 and total == calif)

    return render_template(
        "admin_dashboard.html",
        equipos=equipos,
        academicos=academicos,
        alumnos=alumnos,
        grado=grado,
        puede_exportar=puede_exportar,
        resumen=resumen,
    )

# -------------------- Exportación PDF --------------------
@bp.route("/exportar")
@login_required
@role_required("admin")
def exportar():
    grado = request.args.get("grado", type=int)

    q = db.session.query(
        Equipo.id, Equipo.clave_equipo, Equipo.grado, Equipo.nombre_cartel, Equipo.tipo_evaluacion
    )
    if grado:
        q = q.filter(Equipo.grado == grado)

    equipos = q.all()

    # Construir filas con "mejor" calificación por equipo (puede ser None)
    datos = []
    for e in equipos:
        evs = (
            db.session.query(Evaluacion.calificacion)
            .filter(Evaluacion.equipo_id == e.id)
            .all()
        )
        # evs es lista de tuplas [(cal,), ...]
        califs = [row[0] for row in evs if row[0] is not None]
        mejor = max(califs) if califs else None

        datos.append({
            "grado": e.grado,
            "clave_equipo": e.clave_equipo,
            "nombre_cartel": e.nombre_cartel,
            "tipo": e.tipo_evaluacion,
            "calificacion": mejor if mejor is not None else "-"  # para la tabla y el PDF
        })

    # Orden: por grado asc y dentro por calificación desc (None/"-" al final)
    def sort_key(d):
        cal = d["calificacion"]
        cal_num = float(cal) if isinstance(cal, (int, float)) else (-1.0 if cal == "-" else -1.0)
        return (d["grado"], -cal_num)

    datos.sort(key=sort_key)

    pdf_path = render_pdf(datos=datos, grado=grado)
    if not pdf_path:
        flash("No fue posible generar el PDF (ver logs).", "error")
        return redirect(url_for("admin.dashboard"))

    return send_file(pdf_path, as_attachment=True, download_name="resultados.pdf")
