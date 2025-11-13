# routes/registro.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.user import User
from models.equipo import Equipo
from models.miembro_equipo import MiembroEquipo
from forms.registro_unico_form import RegistroUnicoForm
from utils.codegen import generate_equipo_code

bp = Blueprint("registro", __name__)
ACADEMICO_DOMAIN = "@academicos.udg.mx"

@bp.route("/registro", methods=["GET","POST"])
def registro_unico():
    form = RegistroUnicoForm()

    if form.validate_on_submit():
        modo = form.modo.data

        # ---------- ALUMNO ----------
        if modo == "alumno":
            for campo, msg in [
                (form.nombre.data, "Nombre requerido."),
                (form.email.data, "Correo requerido."),
                (form.student_code.data, "Código de estudiante requerido."),
                (form.password.data, "Contraseña requerida."),
            ]:
                if not campo:
                    flash(msg, "error"); return render_template("registro_unico.html", form=form, titulo="Registro")

            email = form.email.data.strip().lower()
            if User.query.filter_by(email=email).first():
                flash("Ese correo ya está registrado.", "error")
                return render_template("registro_unico.html", form=form, titulo="Registro")

            if User.query.filter_by(student_code=form.student_code.data.strip()).first():
                flash("Ese código de estudiante ya está en uso.", "error")
                return render_template("registro_unico.html", form=form, titulo="Registro")

            u = User(
                nombre=form.nombre.data.strip(),
                email=email,
                role="alumno",
                student_code=form.student_code.data.strip()
            )
            u.set_password(form.password.data)
            db.session.add(u)
            db.session.commit()
            flash("Cuenta de alumno creada. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login_general"))

        # ---------- ACADÉMICO ----------
        if modo == "academico":
            for campo, msg in [
                (form.nombre.data, "Nombre requerido."),
                (form.email.data, "Correo requerido."),
                (form.password.data, "Contraseña requerida."),
            ]:
                if not campo:
                    flash(msg, "error"); return render_template("registro_unico.html", form=form, titulo="Registro")

            email = form.email.data.strip().lower()
            if not email.endswith(ACADEMICO_DOMAIN):
                flash(f"El correo debe terminar en {ACADEMICO_DOMAIN}", "error")
                return render_template("registro_unico.html", form=form, titulo="Registro")

            if User.query.filter_by(email=email).first():
                flash("Ese correo ya está registrado.", "error")
                return render_template("registro_unico.html", form=form, titulo="Registro")

            u = User(nombre=form.nombre.data.strip(), email=email, role="academico")
            u.set_password(form.password.data)
            db.session.add(u); db.session.flush()

            raw = (form.claves.data or "").splitlines()
            claves = [c.strip() for c in raw if c.strip()]
            if claves:
                equipos = Equipo.query.filter(Equipo.clave_equipo.in_(claves)).all()
                existe = {e.clave_equipo for e in equipos}
                faltantes = [c for c in claves if c not in existe]
                if faltantes:
                    flash("Claves inexistentes: " + ", ".join(faltantes), "error")
                    db.session.rollback()
                    return render_template("registro_unico.html", form=form, titulo="Registro")
                # si manejas Modelo Asignacion, agrega aquí
                # for e in equipos: db.session.add(Asignacion(academico_id=u.id, equipo_id=e.id))

            db.session.commit()
            flash("Cuenta de académico creada.", "success")
            return redirect(url_for("auth.login_general"))

        # ---------- EQUIPO ----------
        if modo == "equipo":
            if not form.grado.data or not form.nombre_cartel.data or not form.integrantes_codigos.data:
                flash("Completa grado, nombre y códigos de estudiante.", "error")
                return render_template("registro_unico.html", form=form, titulo="Registro")

            grado = int(form.grado.data)
            tipo = "Proyecto Modular" if grado in (7,9) else "Cartel"
            clave = generate_equipo_code(grado)

            e = Equipo(
                clave_equipo=clave, grado=grado, integrantes="",
                nombre_cartel=form.nombre_cartel.data.strip(),
                tipo_evaluacion=tipo, estado="Pendiente"
            )
            db.session.add(e); db.session.flush()

            raw = [x.strip() for x in form.integrantes_codigos.data.splitlines() if x.strip()]
            for code in raw:
                alumno = User.query.filter_by(student_code=code).first()
                db.session.add(MiembroEquipo(
                    equipo_id=e.id,
                    alumno_id=alumno.id if alumno else None,
                    student_code=code
                ))
            db.session.commit()
            flash(f"Equipo registrado. Clave asignada: {clave}", "success")
            return redirect(url_for("main.home"))

        flash("Modo de registro inválido.", "error")

    return render_template("registro_unico.html", form=form, titulo="Registro")
