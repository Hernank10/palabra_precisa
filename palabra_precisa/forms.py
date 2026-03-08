from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', 
        validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este usuario ya existe')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está registrado')

class EjercicioForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    categoria = StringField('Categoría', validators=[DataRequired()])
    pregunta = TextAreaField('Pregunta', validators=[DataRequired()])
    opciones = TextAreaField('Opciones (separadas por |)')
    respuesta_correcta = StringField('Respuesta correcta', validators=[DataRequired()])
    explicacion = TextAreaField('Explicación')
    dificultad = SelectField('Dificultad', 
        choices=[(1, 'Fácil'), (2, 'Media'), (3, 'Difícil')],
        coerce=int)
