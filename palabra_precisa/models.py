from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    puntos_totales = db.Column(db.Integer, default=0)
    nivel = db.Column(db.Integer, default=1)
    racha_actual = db.Column(db.Integer, default=0)
    mejor_racha = db.Column(db.Integer, default=0)
    ejercicios_completados = db.Column(db.Integer, default=0)
    ejercicios_correctos = db.Column(db.Integer, default=0)
    
    # Relaciones
    intentos = db.relationship('IntentoEjercicio', backref='usuario', lazy=True)
    ejercicios_creados = db.relationship('EjercicioPersonalizado', backref='creador', lazy=True)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    icono = db.Column(db.String(50), default='bi-book')
    
    ejercicios = db.relationship('EjercicioPersonalizado', backref='categoria', lazy=True)

class EjercicioPersonalizado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    pregunta = db.Column(db.Text, nullable=False)
    opciones = db.Column(db.Text)  # JSON string
    respuesta_correcta = db.Column(db.Text, nullable=False)
    explicacion = db.Column(db.Text)
    dificultad = db.Column(db.Integer, default=1)
    puntos = db.Column(db.Integer, default=10)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    creado_por = db.Column(db.Integer, db.ForeignKey('user.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    veces_usado = db.Column(db.Integer, default=0)
    veces_acertado = db.Column(db.Integer, default=0)

class IntentoEjercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ejercicio_id = db.Column(db.Integer, nullable=False)
    ejercicio_tipo = db.Column(db.String(20))  # 'base' o 'personalizado'
    respuesta_usuario = db.Column(db.Text)
    es_correcto = db.Column(db.Boolean)
    puntos_obtenidos = db.Column(db.Integer)
    tiempo_respuesta = db.Column(db.Float)  # en segundos
    fecha_intento = db.Column(db.DateTime, default=datetime.utcnow)

class Practica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime)
    puntuacion_total = db.Column(db.Integer, default=0)
    ejercicios_totales = db.Column(db.Integer)
    ejercicios_correctos = db.Column(db.Integer, default=0)
    completada = db.Column(db.Boolean, default=False)
    
    detalles = db.relationship('DetallePractica', backref='practica', lazy=True)

class DetallePractica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    practica_id = db.Column(db.Integer, db.ForeignKey('practica.id'), nullable=False)
    ejercicio_id = db.Column(db.Integer, nullable=False)
    ejercicio_tipo = db.Column(db.String(20))
    respuesta_usuario = db.Column(db.Text)
    es_correcto = db.Column(db.Boolean)
    puntos_obtenidos = db.Column(db.Integer)
    orden = db.Column(db.Integer)
# Modelo para Flashcards
class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nivel = db.Column(db.Integer, nullable=False)  # 1-5 (Principiante a Experto)
    categoria = db.Column(db.String(100), nullable=False)
    pregunta = db.Column(db.Text, nullable=False)
    respuesta_correcta = db.Column(db.Text, nullable=False)
    pista = db.Column(db.Text)
    explicacion = db.Column(db.Text)
    puntos = db.Column(db.Integer, default=10)
    veces_usada = db.Column(db.Integer, default=0)
    veces_acertada = db.Column(db.Integer, default=0)

class IntentoFlashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcard.id'), nullable=False)
    respuesta_usuario = db.Column(db.Text)
    es_correcto = db.Column(db.Boolean)
    tiempo_respuesta = db.Column(db.Float)
    fecha_intento = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('User', backref='intentos_flashcard')
    flashcard = db.relationship('Flashcard', backref='intentos')
