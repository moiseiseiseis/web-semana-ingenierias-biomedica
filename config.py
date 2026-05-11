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
    # DATABASE
    # ---------------------------
    db_url = os.getenv("DATABASE_URL")

    if db_url:

        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        # Fuerza SSL
        if "sslmode=require" not in db_url:
            separator = "&" if "?" in db_url else "?"
            db_url += f"{separator}sslmode=require"

        app.config["SQLALCHEMY_DATABASE_URI"] = db_url

        # 🔥 IMPORTANTE PARA NEON + RENDER
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }

    else:
        # Fallback LOCAL SOLAMENTE
        instance_path = app.instance_path
        os.makedirs(instance_path, exist_ok=True)

        sqlite_path = os.path.join(instance_path, "database.db")

        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"

    # ---------------------------
    # SQLALCHEMY
    # ---------------------------
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False