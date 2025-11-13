import os
from dotenv import load_dotenv

def load_config(app):
    load_dotenv()

    # ---------------------------
    # SECRET KEYS
    # ---------------------------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret")
    app.config["WTF_CSRF_SECRET_KEY"] = os.getenv("WTF_CSRF_SECRET_KEY", "dev_csrf")

    # ---------------------------
    # DATABASE (Render / Railway / Local fallback)
    # ---------------------------
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        # Render usa postgres:// pero SQLAlchemy requiere postgresql://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        app.config["SQLALCHEMY_DATABASE_URI"] = db_url

    else:
        # SQLite LOCAL (solo en desarrollo)
        instance_path = app.instance_path
        os.makedirs(instance_path, exist_ok=True)
        sqlite_path = os.path.join(instance_path, "database.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"

    # ---------------------------
    # SQLALCHEMY
    # ---------------------------
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ---------------------------
    # ADMIN SETUP TOKEN (para crear el admin en producción)
    # ---------------------------
    app.config["ADMIN_SETUP_TOKEN"] = os.getenv("ADMIN_SETUP_TOKEN")
