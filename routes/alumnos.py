from flask import Blueprint, render_template, request, redirect, url_for, flash
from forms.alumno_form import AlumnoRegistroForm
from models import db
from models.equipo import Equipo

bp = Blueprint("alumnos", __name__)

@bp.route("/registro", methods=["GET", "POST"])
def registro_equipo():
    form = AlumnoRegistroForm()
    if form.validate_on_submit():
        clave = form.clave_equipo.data.strip()
        existe = Equipo.query.filter_by(clave_equipo=clave).first()
        if existe:
            flash("La clave de equipo ya existe. Usa una diferente.", "error")
            return render_template("alumnos_registro.html", form=form)

        grado = form.grado.data
        tipo = "Proyecto Modular" if grado in (7, 9) else "Cartel"

        equipo = Equipo(
            clave_equipo=clave,
            grado=grado,
            integrantes=form.integrantes.data.strip(),
            nombre_cartel=form.nombre_cartel.data.strip(),
            tipo_evaluacion=tipo,
            estado="Pendiente"
        )
        db.session.add(equipo)
        db.session.commit()
        flash("Equipo registrado correctamente.", "success")
        return redirect(url_for("alumnos.registro_equipo"))
    return render_template("alumnos_registro.html", form=form)
