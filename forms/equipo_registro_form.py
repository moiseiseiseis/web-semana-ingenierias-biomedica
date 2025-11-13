from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class EquipoRegistroForm(FlaskForm):
    grado = IntegerField("Grado (1,3,5,7,9)", validators=[DataRequired(), NumberRange(min=1, max=9)])
    nombre_cartel = StringField("Nombre del Cartel / Proyecto", validators=[DataRequired(), Length(max=200)])
    integrantes_codigos = TextAreaField("Códigos de estudiante (uno por línea)", validators=[DataRequired()])
    submit = SubmitField("Registrar equipo")
