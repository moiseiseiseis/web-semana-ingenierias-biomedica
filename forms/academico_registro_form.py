# forms/academico_registro_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class AcademicoRegistroForm(FlaskForm):
    nombre = StringField("Nombre completo", validators=[DataRequired(), Length(max=120)])
    email = StringField("Correo institucional", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=4, max=128)])
    password2 = PasswordField("Confirmar contraseña", validators=[DataRequired(), EqualTo("password")])
   # claves = TextAreaField("Claves de Equipo a evaluar (una por línea)", validators=[DataRequired()])
    submit = SubmitField("Crear cuenta")
