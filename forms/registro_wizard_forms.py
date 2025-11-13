from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Optional
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Regexp

class PasoSelectorForm(FlaskForm):
    modo = RadioField(
        "Registro de",
        choices=[("alumno", "Alumno/a"), ("equipo", "Equipo"), ("academico","Académico/a")],
        default="alumno",
        validators=[DataRequired()]
    )
    continuar = SubmitField("Continuar")

class PasoAlumnoForm(FlaskForm):
    nombre = StringField("Nombre completo", validators=[DataRequired(), Length(max=120)])
    email = StringField("Correo", validators=[DataRequired(), Email(), Length(max=120)])
    student_code = StringField("Código de estudiante", validators=[DataRequired(), Length(max=32)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=4, max=128)])
    password2 = PasswordField("Confirmar contraseña", validators=[DataRequired(), EqualTo("password")])
    enviar = SubmitField("Registrar alumno")

class PasoEquipoForm(FlaskForm):
    grado = IntegerField("Grado (1,3,5,7,9)", validators=[DataRequired(), NumberRange(min=1,max=9)])
    nombre_cartel = StringField("Nombre del Cartel / Proyecto", validators=[DataRequired(), Length(max=200)])
    integrantes_codigos = TextAreaField("Códigos de estudiante (uno por línea)", validators=[DataRequired()])
    enviar = SubmitField("Registrar equipo")

class PasoAcademicoForm(FlaskForm):
    nombre = StringField("Nombre completo", validators=[DataRequired(), Length(max=120)])
    # Acepta solo dominio @academicos.udg.mx
    email = StringField(
        "Correo institucional",
        validators=[
            DataRequired(), Email(), Length(max=120),
            Regexp(r".+@academicos\.udg\.mx$", message="Usa tu correo @academicos.udg.mx")
        ]
    )
  
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=4, max=128)])
    password2 = PasswordField("Confirmar contraseña", validators=[DataRequired(), EqualTo("password")])
    enviar = SubmitField("Registrar académico/a")