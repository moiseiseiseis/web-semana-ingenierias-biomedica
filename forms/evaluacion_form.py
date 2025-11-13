from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class EvaluacionForm(FlaskForm):
    calificacion = IntegerField("Calificación (0-100)", validators=[DataRequired(), NumberRange(min=0, max=100)])
    comentarios = TextAreaField("Comentarios (opcional)")
    submit = SubmitField("Guardar")
