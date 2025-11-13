# routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from forms.login_form import LoginForm
from models import db
from models.user import User
from models.equipo import Equipo
from models.evaluacion import Evaluacion
from utils.decorators import role_required
from utils.export_pdf import render_pdf

bp = Blueprint("admin", __name__)

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
