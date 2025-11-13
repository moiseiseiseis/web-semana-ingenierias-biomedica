from .main import bp as main_bp
from .auth import bp as auth_bp
from .registro_wizard import bp as registro_wizard_bp   # ✅ nuevo registro unificado en /registro
from .alumnos_dashboard import bp as alumnos_bp
from .academicos import bp as academicos_bp
from .admin import bp as admin_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # Registro unificado (wizard) -> /registro (pasos)
    app.register_blueprint(registro_wizard_bp)

    # Dashboards y otros
    app.register_blueprint(alumnos_bp)
    app.register_blueprint(academicos_bp, url_prefix="/academicos")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # 🔁 (Opcional) Alias de compatibilidad si aún tienes enlaces viejos:
    # from flask import redirect, url_for
    # @app.route("/registro_unico")
    # def _alias_registro_unico():
    #     return redirect(url_for("registro_wizard.registro"))
