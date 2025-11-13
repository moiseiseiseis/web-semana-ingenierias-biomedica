# forms/registro_unico_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Optional

class RegistroUnicoForm(FlaskForm):
    modo = SelectField(
        "Registro de",
        choices=[("alumno", "Alumno/a"), ("academico", "Académico/a"), ("equipo", "Equipo")],
        validators=[DataRequired()]
    )

    # Comunes (para alumno/academico)
    nombre = StringField("Nombre completo", validators=[Optional(), Length(max=120)])
    email = StringField("Correo", validators=[Optional(), Email(), Length(max=120)])
    password = PasswordField("Contraseña", validators=[Optional(), Length(min=4, max=128)])
    password2 = PasswordField("Confirmar contraseña", validators=[Optional(), EqualTo("password")])

    # Alumno
    student_code = StringField("Código de estudiante", validators=[Optional(), Length(max=32)])

    # Académico
    claves = TextAreaField("Claves de equipos a evaluar (una por línea, opcional)", validators=[Optional()])

    # Equipo
    grado = IntegerField("Grado (1,3,5,7,9)", validators=[Optional(), NumberRange(min=1, max=9)])
    nombre_cartel = StringField("Nombre del Cartel / Proyecto", validators=[Optional(), Length(max=200)])
    integrantes_codigos = TextAreaField("Códigos de estudiante (uno por línea)", validators=[Optional()])

    submit = SubmitField("Registrar")
