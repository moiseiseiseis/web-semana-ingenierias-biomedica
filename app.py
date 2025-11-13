from flask import Flask, render_template, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user
from models import db
from models.user import User
from routes import register_blueprints
import os
from config import load_config
from forms.login_form import LoginForm


csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    #
    return db.session.get(User, int(user_id))      

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    load_config(app)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    register_blueprints(app)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif current_user.role == "academico":
                return redirect(url_for("academicos.dashboard"))
        # Si no ha iniciado sesión, muestra el login reutilizable con un form válido
        form = LoginForm()
        return render_template("home.html")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
