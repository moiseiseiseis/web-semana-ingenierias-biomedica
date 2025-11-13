# routes/registro_ext.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user
from models import db
from models.user import User
from models.equipo import Equipo
from models.miembro_equipo import MiembroEquipo
from forms.alumno_individual_form import AlumnoIndividualForm
from forms.equipo_registro_form import EquipoRegistroForm
from utils.codegen import generate_equipo_code

bp = Blueprint("registro_ext", __name__)

@bp.route("/registro/alumno", methods=["GET","POST"])
def registro_alumno_individual():
    form = AlumnoIndividualForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if User.query.filter_by(email=email).first():
            flash("Ese correo ya está registrado.", "error")
            return render_template("registro_alumno.html", form=form)

        if User.query.filter_by(student_code=form.student_code.data.strip()).first():
            flash("Ese código de estudiante ya está en uso.", "error")
            return render_template("registro_alumno.html", form=form)

        u = User(
            nombre=form.nombre.data.strip(),
            email=email,
            role="alumno",
            grado=None,
            student_code=form.student_code.data.strip()
        )
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()
        flash("Cuenta creada. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login_general"))
    return render_template("registro_alumno.html", form=form, titulo="Registro Alumno")

@bp.route("/registro/equipo", methods=["GET","POST"])
def registro_equipo():
    form = EquipoRegistroForm()
    if form.validate_on_submit():
        grado = int(form.grado.data)
        tipo = "Proyecto Modular" if grado in (7, 9) else "Cartel"
        clave = generate_equipo_code(grado)

        e = Equipo(
            clave_equipo=clave,
            grado=grado,
            integrantes="",  # ya no la usamos como texto libre
            nombre_cartel=form.nombre_cartel.data.strip(),
            tipo_evaluacion=tipo,
            estado="Pendiente"
        )
        db.session.add(e)
        db.session.flush()

        # Códigos de estudiante → miembros_equipo
        raw = [x.strip() for x in form.integrantes_codigos.data.splitlines() if x.strip()]
        for code in raw:
            # Si ya existe el alumno, lo linkeamos; si no, solo guardamos el code.
            alumno = User.query.filter_by(student_code=code).first()
            db.session.add(MiembroEquipo(
                equipo_id=e.id,
                alumno_id=alumno.id if alumno else None,
                student_code=code
            ))

        db.session.commit()
        flash(f"Equipo registrado. Clave asignada: {clave}", "success")
        return redirect(url_for("main.home"))
    return render_template("registro_equipo.html", form=form, titulo="Registro de Equipo")


# --- Alias para compatibilidad con enlaces antiguos ---
@bp.route("/alumnos/registro")
def alumnos_registro_equipo_alias():
    """Redirige a la ruta actual /registro/equipo"""
    from flask import redirect, url_for
    return redirect(url_for("registro_ext.registro_equipo"))
