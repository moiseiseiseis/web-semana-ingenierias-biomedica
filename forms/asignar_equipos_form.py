# forms/asignar_equipos_form.py
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class AsignarEquiposForm(FlaskForm):
    claves = TextAreaField(
        "Claves de equipo (una por línea)",
        validators=[DataRequired(message="Ingresa al menos una clave")]
    )
    submit = SubmitField("Asignar")
