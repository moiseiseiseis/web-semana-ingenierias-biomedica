# routes/admin_setup.py
from flask import Blueprint, current_app, request, abort
from models import db
from models.user import User

bp = Blueprint("admin_setup", __name__)

@bp.route("/setup/create-admin")
def create_admin():
    token = request.args.get("token")
    expected = current_app.config.get("ADMIN_SETUP_TOKEN")

    # Si no hay token o no coincide -> 404 para no dar pistas
    if not expected or token != expected:
        abort(404)

    email = "admin@institucion.edu"
    password = "admin123"   # aquí defines la contraseña que quieres usar en PRODUCCIÓN

    admin = User.query.filter_by(email=email, role="admin").first()

    if not admin:
        admin = User(
            nombre="Admin",
            email=email,
            role="admin",
            grado=None
        )
        admin.set_password(password)
        db.session.add(admin)
        msg = "Admin creado."
    else:
        admin.set_password(password)
        msg = "Admin actualizado."

    db.session.commit()
    return msg
