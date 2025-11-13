from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class AlumnoRegistroForm(FlaskForm):
    clave_equipo = StringField("Clave de Equipo", validators=[DataRequired(), Length(max=50)])
    grado = IntegerField("Grado (1,3,5,7,9)", validators=[DataRequired(), NumberRange(min=1, max=9)])
    integrantes = TextAreaField("Integrantes (uno por línea o separados por ';')", validators=[DataRequired()])
    nombre_cartel = StringField("Nombre del Cartel / Proyecto", validators=[DataRequired(), Length(max=200)])
    submit = SubmitField("Registrar Equipo")
