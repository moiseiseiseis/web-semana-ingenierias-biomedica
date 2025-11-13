# routes/alumnos_dashboard.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db
from models.equipo import Equipo
from models.evaluacion import Evaluacion
from models.miembro_equipo import MiembroEquipo
from sqlalchemy import func

bp = Blueprint("alumnos", __name__)

@bp.route("/alumnos/dashboard")
@login_required
def dashboard():
    # Solo alumnos
    if current_user.role != "alumno":
        return render_template("403.html"), 403

    # Equipos por pertenencia (vía alumno_id o por student_code)
    q = db.session.query(Equipo).join(MiembroEquipo, MiembroEquipo.equipo_id == Equipo.id)\
        .filter(
            (MiembroEquipo.alumno_id == current_user.id) |
            ((MiembroEquipo.alumno_id.is_(None)) & (MiembroEquipo.student_code == current_user.student_code))
        ).distinct()

    equipos = q.all()

    # Calificación agregada por equipo (promedio de evaluaciones)
    promedios = dict(
        db.session.query(
            Evaluacion.equipo_id,
            func.avg(Evaluacion.calificacion).label("prom")
        ).group_by(Evaluacion.equipo_id).all()
    )

    # Preparar datos para template
    datos = []
    for e in equipos:
        prom = promedios.get(e.id)
        datos.append({
            "equipo_id": e.id,
            "clave": e.clave_equipo,
            "grado": e.grado,
            "nombre": e.nombre_cartel,
            "tipo": e.tipo_evaluacion,
            "estado": e.estado,
            "promedio": round(float(prom), 2) if prom is not None else None
        })

    # Si este alumno tiene student_code, intentamos "reconciliar" membresías pendientes
    if current_user.student_code:
        pendientes = MiembroEquipo.query.filter(
            MiembroEquipo.alumno_id.is_(None),
            MiembroEquipo.student_code == current_user.student_code
        ).all()
        changed = False
        for m in pendientes:
            m.alumno_id = current_user.id
            changed = True
        if changed:
            db.session.commit()

    return render_template("alumno_dashboard.html", equipos=datos)
