# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from models.user import User
from models import db
from forms.login_general_form import LoginGeneralForm

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login_general():
    if current_user.is_authenticated:
        return _redir_by_role(current_user)

    form = LoginGeneralForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Credenciales inválidas.", "error")
            return render_template("login_general.html", form=form, titulo="Login")

        login_user(user)
        return _redir_by_role(user)

    return render_template("login_general.html", form=form, titulo="Login")

def _redir_by_role(user: User):
    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    if user.role == "academico":
        return redirect(url_for("academicos.dashboard"))
    if user.role == "alumno":
        return redirect(url_for("alumnos.dashboard"))  # nuevo
    # fallback
    return redirect(url_for("main.home"))

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("auth.login_general"))
