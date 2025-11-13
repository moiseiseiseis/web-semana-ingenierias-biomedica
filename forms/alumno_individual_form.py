from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class AlumnoIndividualForm(FlaskForm):
    nombre = StringField("Nombre completo", validators=[DataRequired(), Length(max=120)])
    email = StringField("Correo", validators=[DataRequired(), Email(), Length(max=120)])
    student_code = StringField("Código de estudiante", validators=[DataRequired(), Length(max=32)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=4, max=128)])
    password2 = PasswordField("Confirmar contraseña", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Crear cuenta")
