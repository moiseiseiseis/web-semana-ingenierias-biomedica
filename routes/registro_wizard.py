# routes/registro_wizard.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.user import User
from models.equipo import Equipo
from models.miembro_equipo import MiembroEquipo
from utils.codegen import generate_equipo_code
from forms.registro_wizard_forms import (
    PasoSelectorForm, PasoAlumnoForm, PasoEquipoForm, PasoAcademicoForm
)

bp = Blueprint("registro_wizard", __name__)

@bp.route("/registro", methods=["GET", "POST"])
def registro():
    paso = int(request.args.get("paso", 1))

    # -----------------------
    # PASO 1: Selección
    # -----------------------
    if paso == 1:
        form = PasoSelectorForm()
        if form.validate_on_submit():
            session["registro_modo"] = form.modo.data  # alumno | academico | equipo
            return redirect(url_for("registro_wizard.registro", paso=2))

        if "registro_modo" in session:
            form.modo.data = session["registro_modo"]

        return render_template("registro_wizard.html", paso=1, form=form, titulo="Registro")

    modo = session.get("registro_modo", "alumno")

    # -----------------------
    # PASO 2: Alumno
    # -----------------------
    if paso == 2 and modo == "alumno":
        form = PasoAlumnoForm()
        if form.validate_on_submit():
            email = (form.email.data or "").strip().lower()
            student_code = (form.student_code.data or "").strip()

            # Unicidad
            if User.query.filter_by(email=email).first():
                flash("Ese correo ya está registrado.", "error")
                return render_template("registro_wizard.html", paso=2, modo=modo, form=form, titulo="Registro")

            if User.query.filter_by(student_code=student_code).first():
                flash("Ese código de estudiante ya está en uso.", "error")
                return render_template("registro_wizard.html", paso=2, modo=modo, form=form, titulo="Registro")

            u = User(
                nombre=(form.nombre.data or "").strip(),
                email=email,
                role="alumno",
                student_code=student_code
            )
            u.set_password(form.password.data)
            db.session.add(u)
            db.session.commit()

            session["registro_ok"] = f"Alumno registrado: {u.nombre}"
            return redirect(url_for("registro_wizard.registro", paso=3))

        return render_template("registro_wizard.html", paso=2, modo=modo, form=form, titulo="Registro")

    # -----------------------
    # PASO 2: Académico (SIN claves, solo cuenta)
    # -----------------------
    if paso == 2 and modo == "academico":
        form = PasoAcademicoForm()
        if form.validate_on_submit():
            email = (form.email.data or "").strip().lower()

            # Doble validación de dominio
            if not email.endswith("@academicos.udg.mx"):
                flash("Debes usar tu correo @academicos.udg.mx", "error")
                return render_template("registro_wizard.html", paso=2, modo=modo, form=form, titulo="Registro")

            if User.query.filter_by(email=email).first():
                flash("Ese correo ya está registrado.", "error")
                return render_template("registro_wizard.html", paso=2, modo=modo, form=form, titulo="Registro")

            u = User(
                nombre=(form.nombre.data or "").strip(),
                email=email,
                role="academico"
            )
            u.set_password(form.password.data)
            db.session.add(u)
            db.session.commit()

            # Mensaje claro: las claves se asignan luego en el dashboard
            session["registro_ok"] = (
                f"Académico registrado: {u.nombre}. "
                "Podrás asignarte equipos desde tu panel al iniciar sesión."
            )
            return redirect(url_for("registro_wizard.registro", paso=3))

        return render_template("registro_wizard.html", paso=2, modo=modo, form=form, titulo="Registro")

    # -----------------------
    # PASO 2: Equipo
    # -----------------------
    if paso == 2 and modo == "equipo":
        form = PasoEquipoForm()
        if form.validate_on_submit():
            grado = int(form.grado.data)
            tipo = "Proyecto Modular" if grado in (7, 9) else "Cartel"

            # Genera clave tipo INBI{grado}-NN (según tu utils.codegen)
            clave = generate_equipo_code(grado)

            e = Equipo(
                clave_equipo=clave,
                grado=grado,
                integrantes="",  # ya no usamos texto libre
                nombre_cartel=(form.nombre_cartel.data or "").strip(),
                tipo_evaluacion=tipo,
                estado="Pendiente"
            )
            db.session.add(e)
            db.session.flush()  # necesitamos e.id

            # Vincular miembros por student_code (existan o no)
            raw = [x.strip() for x in (form.integrantes_codigos.data or "").splitlines() if x.strip()]
            for code in raw:
                alumno = User.query.filter_by(student_code=code).first()
                db.session.add(MiembroEquipo(
                    equipo_id=e.id,
                    alumno_id=alumno.id if alumno else None,
                    student_code=code
                ))

            db.session.commit()
            session["registro_ok"] = f"Equipo registrado. Clave: {clave}"
            return redirect(url_for("registro_wizard.registro", paso=3))

        return render_template("registro_wizard.html", paso=2, modo=modo, form=form, titulo="Registro")

    # -----------------------
    # PASO 3: Confirmación
    # -----------------------
    if paso == 3:
        confirm_msg = session.pop("registro_ok", None)
        if not confirm_msg:
            return redirect(url_for("registro_wizard.registro", paso=1))
        return render_template("registro_wizard.html", paso=3, titulo="Registro", confirm_msg=confirm_msg)

    # Fallback: vuelve al paso 1
    return redirect(url_for("registro_wizard.registro", paso=1))
