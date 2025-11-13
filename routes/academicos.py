# routes/academicos.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from models.equipo import Equipo
from models.evaluacion import Evaluacion
from models.asignacion import Asignacion
from forms.login_form import LoginForm
from forms.evaluacion_form import EvaluacionForm
from forms.academico_registro_form import AcademicoRegistroForm
from utils.decorators import role_required

ACADEMICO_ALLOWED_DOMAIN = "@academicos.udg.mx"

bp = Blueprint("academicos", __name__)

# ---------- Auth ----------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and current_user.role == "academico":
        return redirect(url_for("academicos.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        if user and user.role == "academico" and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("academicos.dashboard"))
        flash("Credenciales inválidas o rol incorrecto.", "error")
    return render_template("login.html", form=form, titulo="Login Académico")


@bp.route("/logout")
@login_required
@role_required("academico")
def logout():
    logout_user()
    return redirect(url_for("academicos.login"))


# ---------- Registro SIN claves (solo crea la cuenta) ----------
@bp.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated and current_user.role == "academico":
        return redirect(url_for("academicos.dashboard"))

    form = AcademicoRegistroForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        if not email.endswith(ACADEMICO_ALLOWED_DOMAIN):
            flash(f"El correo debe terminar en {ACADEMICO_ALLOWED_DOMAIN}", "error")
            return render_template("academico_registro.html", form=form, titulo="Registro de Académico")

        if User.query.filter_by(email=email).first():
            flash("Ese correo ya está registrado.", "error")
            return render_template("academico_registro.html", form=form, titulo="Registro de Académico")

        user = User(
            nombre=form.nombre.data.strip(),
            email=email,
            role="academico",
            grado=None
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Cuenta creada. Inicia sesión para asignarte equipos.", "success")
        return redirect(url_for("academicos.login"))

    return render_template("academico_registro.html", form=form, titulo="Registro de Académico")


# ---------- Dashboard ----------
@bp.route("/dashboard")
@login_required
@role_required("academico")
def dashboard():
    # Equipos asignados a este académico
    asignados = (
        db.session.query(Equipo)
        .join(Asignacion, Asignacion.equipo_id == Equipo.id)
        .filter(Asignacion.academico_id == current_user.id)
        .order_by(Equipo.grado, Equipo.clave_equipo)
        .all()
    )

    # Evaluaciones hechas por este académico (sólo sobre asignados)
    asign_ids = [e.id for e in asignados] or [-1]
    evs = (
        db.session.query(Evaluacion)
        .filter(Evaluacion.academico_id == current_user.id,
                Evaluacion.equipo_id.in_(asign_ids))
        .all()
    )
    ev_by_equipo = {ev.equipo_id: ev for ev in evs}

    # Pendientes: sin eval o con calificación NULL
    pendientes = [e for e in asignados if (e.id not in ev_by_equipo) or (ev_by_equipo[e.id].calificacion is None)]
    # Calificados: calificación no nula
    calificados = [e for e in asignados if (e.id in ev_by_equipo) and (ev_by_equipo[e.id].calificacion is not None)]

    return render_template(
        "academico_dashboard.html",
        pendientes=pendientes,
        calificados=calificados,
        ejemplo="INBI5-01\nINBI7-02"  # placeholder del textarea de asignación
    )


# ---------- Asignar / quitar equipos desde el dashboard ----------
@bp.route("/asignar", methods=["POST"])
@login_required
@role_required("academico")
def asignar():
    raw = (request.form.get("claves") or "").strip()
    if not raw:
        flash("Pega al menos una clave de equipo.", "error")
        return redirect(url_for("academicos.dashboard"))

    claves = [c.strip() for c in raw.splitlines() if c.strip()]
    equipos = Equipo.query.filter(Equipo.clave_equipo.in_(claves)).all()
    encontradas = {e.clave_equipo: e for e in equipos}
    no_encontradas = [c for c in claves if c not in encontradas]

    creadas = 0
    for c in claves:
        e = encontradas.get(c)
        if not e:
            continue
        ya = Asignacion.query.filter_by(academico_id=current_user.id, equipo_id=e.id).first()
        if not ya:
            db.session.add(Asignacion(academico_id=current_user.id, equipo_id=e.id))
            creadas += 1

    db.session.commit()

    if creadas:
        extra = f" Sin encontrar: {', '.join(no_encontradas)}" if no_encontradas else ""
        flash(f"Asignadas {creadas} equipo(s).{extra}", "success")
    else:
        msg = "No hubo cambios."
        if no_encontradas:
            msg += f" Claves inexistentes: {', '.join(no_encontradas)}"
        flash(msg, "error")

    return redirect(url_for("academicos.dashboard"))


@bp.route("/asignacion/<int:equipo_id>/eliminar", methods=["POST"])
@login_required
@role_required("academico")
def eliminar_asignacion(equipo_id):
    asig = Asignacion.query.filter_by(academico_id=current_user.id, equipo_id=equipo_id).first()
    if not asig:
        flash("Esa asignación no existe.", "error")
        return redirect(url_for("academicos.dashboard"))
    db.session.delete(asig)
    db.session.commit()
    flash("Asignación eliminada.", "success")
    return redirect(url_for("academicos.dashboard"))


# ---------- Evaluación ----------
@bp.route("/evaluar/<int:equipo_id>", methods=["GET", "POST"])
@login_required
@role_required("academico")
def evaluar(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)

    # Verifica que el equipo esté asignado a este académico
    asignada = Asignacion.query.filter_by(academico_id=current_user.id, equipo_id=equipo.id).first()
    if not asignada:
        flash("Este equipo no está asignado a tu cuenta.", "error")
        return redirect(url_for("academicos.dashboard"))

    ev = Evaluacion.query.filter_by(equipo_id=equipo.id, academico_id=current_user.id).first()
    form = EvaluacionForm(obj=ev)

    if form.validate_on_submit():
        raw = (request.form.get("calificacion") or "").strip()
        comentarios = (request.form.get("comentarios") or "").strip() or None

        calificacion = None
        if raw != "":
            try:
                calificacion = float(raw)
            except ValueError:
                flash("Calificación inválida.", "error")
                return redirect(url_for("academicos.evaluar", equipo_id=equipo.id))
            if calificacion < 1 or calificacion > 100:
                flash("La calificación debe estar entre 1 y 100.", "error")
                return redirect(url_for("academicos.evaluar", equipo_id=equipo.id))

        if not ev:
            ev = Evaluacion(
                equipo_id=equipo.id,
                academico_id=current_user.id,
                calificacion=calificacion,
                comentarios=comentarios
            )
            db.session.add(ev)
        else:
            ev.calificacion = calificacion
            ev.comentarios = comentarios

        # Solo marcamos "Calificado" si efectivamente tiene calificación
        if calificacion is not None:
            equipo.estado = "Calificado"

        db.session.commit()
        flash("Evaluación guardada.", "success")
        return redirect(url_for("academicos.dashboard"))

    return render_template("evaluacion_form.html", equipo=equipo, form=form)
