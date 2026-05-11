from flask import Flask, jsonify, redirect, url_for # <-- Cambiamos render_template por jsonify
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user
from models import db
from models.user import User
from models.evento import Evento # <-- Importamos Evento para tu ruta /api/eventos
from routes import register_blueprints
import os
from config import load_config
from forms.login_form import LoginForm
from flask_cors import CORS

csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))      

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    CORS(app)
    load_config(app)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    register_blueprints(app)

    @app.route("/")
    def index():
        # Las redirecciones a los dashboards pueden quedarse si aún las usas
        if current_user.is_authenticated:
            if current_user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif current_user.role == "academico":
                return redirect(url_for("academicos.dashboard"))
        
        # EL CAMBIO PRINCIPAL: Si no hay sesión, devolvemos JSON en lugar de HTML
        return jsonify({"status": "online", "mensaje": "API de Semana de Ingenierías funcionando. Conecta React aquí."})

    @app.route('/api/eventos')
    def api_eventos():
        # Ahora esto funcionará porque jsonify y Evento ya están importados
        return jsonify([ev.to_dict() for ev in Evento.query.all()])

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)