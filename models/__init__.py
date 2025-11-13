from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# importa modelos para el metadata
from .user import User
from .equipo import Equipo
from .miembro_equipo import MiembroEquipo
from .evento import Evento  
