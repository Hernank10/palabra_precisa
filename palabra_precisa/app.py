from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import random
from datetime import datetime, timedelta

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_muy_segura_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///palabras.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Inicializar extensiones después de app
from models import db, User, Categoria, EjercicioPersonalizado, IntentoEjercicio, Practica, DetallePractica
from forms import LoginForm, RegistrationForm, EjercicioForm
from utils import GeneradorEjercicios, SistemaPuntuacion

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Inicializar generadores
generador = GeneradorEjercicios()
sistema_puntos = SistemaPuntuacion()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas principales
@app.route('/')
def index():
    stats = generador.obtener_estadisticas()
    return render_template('index.html', stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/practica')
@login_required
def practica():
    """Inicia una nueva práctica"""
    num_preguntas = request.args.get('num', 10, type=int)
    categoria = request.args.get('categoria')
    
    if categoria:
        ejercicios = generador.obtener_ejercicios_por_categoria(categoria)
        ejercicios = random.sample(ejercicios, min(num_preguntas, len(ejercicios)))
    else:
        ejercicios = generador.generar_practica(num_preguntas)
    
    # Crear registro de práctica en BD
    practica = Practica(
        usuario_id=current_user.id,
        ejercicios_totales=len(ejercicios)
    )
    db.session.add(practica)
    db.session.commit()
    
    # Guardar IDs en sesión
    session['practica_actual'] = {
        'id': practica.id,
        'ejercicios': [e['id'] for e in ejercicios],
        'indice': 0,
        'respuestas': []
    }
    
    return render_template('practica.html', 
                         ejercicios=ejercicios,
                         total=len(ejercicios))

@app.route('/api/verificar_respuesta', methods=['POST'])
@login_required
def verificar_respuesta():
    """API para verificar respuestas en tiempo real"""
    data = request.json
    ejercicio_id = data.get('ejercicio_id')
    respuesta = data.get('respuesta')
    tiempo = data.get('tiempo', 0)
    
    # Buscar ejercicio
    ejercicio = next((e for e in generador.ejercicios if e['id'] == ejercicio_id), None)
    
    if not ejercicio:
        return jsonify({'error': 'Ejercicio no encontrado'}), 404
    
    # Verificar respuesta
    es_correcto = respuesta.strip().lower() == ejercicio['respuesta_correcta'].strip().lower()
    
    # Calcular puntos
    puntos = sistema_puntos.calcular_puntos(
        ejercicio, 
        tiempo_respuesta=tiempo,
        racha_actual=current_user.racha_actual
    ) if es_correcto else 0
    
    # Actualizar racha
    if es_correcto:
        current_user.racha_actual += 1
        if current_user.racha_actual > current_user.mejor_racha:
            current_user.mejor_racha = current_user.racha_actual
        current_user.puntos_totales += puntos
        current_user.ejercicios_correctos += 1
    else:
        current_user.racha_actual = 0
    
    current_user.ejercicios_completados += 1
    
    # Actualizar nivel
    nivel, _ = sistema_puntos.calcular_nivel(current_user.puntos_totales)
    current_user.nivel = nivel
    
    # Registrar intento
    intento = IntentoEjercicio(
        usuario_id=current_user.id,
        ejercicio_id=ejercicio_id,
        ejercicio_tipo='base',
        respuesta_usuario=respuesta,
        es_correcto=es_correcto,
        puntos_obtenidos=puntos,
        tiempo_respuesta=tiempo
    )
    db.session.add(intento)
    
    # Actualizar práctica actual
    practica_data = session.get('practica_actual', {})
    if practica_data:
        practica = Practica.query.get(practica_data['id'])
        if practica:
            detalle = DetallePractica(
                practica_id=practica.id,
                ejercicio_id=ejercicio_id,
                ejercicio_tipo='base',
                respuesta_usuario=respuesta,
                es_correcto=es_correcto,
                puntos_obtenidos=puntos,
                orden=practica_data['indice']
            )
            db.session.add(detalle)
            
            if es_correcto:
                practica.ejercicios_correctos += 1
            practica.puntuacion_total += puntos
    
    db.session.commit()
    
    return jsonify({
        'correcto': es_correcto,
        'respuesta_correcta': ejercicio['respuesta_correcta'],
        'explicacion': ejercicio.get('explicacion', ''),
        'puntos': puntos,
        'racha': current_user.racha_actual,
        'nivel': current_user.nivel
    })

@app.route('/resultados/<int:practica_id>')
@login_required
def resultados(practica_id):
    """Muestra los resultados de una práctica"""
    practica = Practica.query.get_or_404(practica_id)
    
    if practica.usuario_id != current_user.id:
        flash('No tienes permiso para ver estos resultados', 'danger')
        return redirect(url_for('index'))
    
    # Marcar práctica como completada
    if not practica.completada:
        practica.completada = True
        practica.fecha_fin = datetime.utcnow()
        db.session.commit()
    
    detalles = DetallePractica.query.filter_by(practica_id=practica_id).order_by(DetallePractica.orden).all()
    
    return render_template('resultados.html', 
                         practica=practica,
                         detalles=detalles)

@app.route('/ranking')
def ranking():
    """Muestra el ranking de usuarios"""
    top_usuarios = User.query.order_by(User.puntos_totales.desc()).limit(20).all()
    return render_template('ranking.html', usuarios=top_usuarios)

# Crear tablas si no existen
def init_db():
    with app.app_context():
        db.create_all()
        print("Base de datos inicializada")

# Rutas para Flashcards
@app.route('/flashcards')
@login_required
def flashcards_resumen():
    """Muestra resumen de todos los niveles de flashcards"""
    # Cargar flashcards
    with open('flashcards.json', 'r', encoding='utf-8') as f:
        flashcards = json.load(f)
    
    total_flashcards = len(flashcards)
    
    # Obtener estadísticas por nivel
    stats_niveles = []
    for nivel in range(1, 6):
        flashcards_nivel = [f for f in flashcards if f['nivel'] == nivel]
        total_nivel = len(flashcards_nivel)
        
        # Intentos del usuario en este nivel
        intentos = IntentoFlashcard.query.filter_by(usuario_id=current_user.id).join(
            Flashcard, IntentoFlashcard.flashcard_id == Flashcard.id
        ).filter(Flashcard.nivel == nivel).all()
        
        completadas = len(set([i.flashcard_id for i in intentos if i.es_correcto]))
        puntos = sum([i.puntos_obtenidos or 0 for i in intentos if i.es_correcto])
        progreso = (completadas / total_nivel * 100) if total_nivel > 0 else 0
        
        stats_niveles.append({
            'total': total_nivel,
            'completadas': completadas,
            'puntos': puntos,
            'progreso': round(progreso, 1)
        })
    
    # Calcular estadísticas generales
    total_intentos = IntentoFlashcard.query.filter_by(usuario_id=current_user.id).count()
    total_aciertos = IntentoFlashcard.query.filter_by(usuario_id=current_user.id, es_correcto=True).count()
    promedio_acierto = round((total_aciertos / total_intentos * 100) if total_intentos > 0 else 0, 1)
    
    return render_template('flashcards_resumen.html',
                         total_flashcards=total_flashcards,
                         completadas=total_aciertos,
                         promedio_acierto=promedio_acierto,
                         stats_niveles=stats_niveles)

@app.route('/flashcards/<int:flashcard_id>')
@login_required
def flashcards_practica(flashcard_id):
    """Práctica de flashcards con un ID específico"""
    nivel = request.args.get('nivel', 1, type=int)
    
    # Cargar flashcards
    with open('flashcards.json', 'r', encoding='utf-8') as f:
        flashcards = json.load(f)
    
    # Filtrar por nivel y ordenar
    flashcards_nivel = [f for f in flashcards if f['nivel'] == nivel]
    flashcards_nivel.sort(key=lambda x: x['id'])
    
    if not flashcards_nivel:
        flash('No hay flashcards en este nivel', 'warning')
        return redirect(url_for('flashcards_resumen'))
    
    # Encontrar índice actual
    indices = {f['id']: i for i, f in enumerate(flashcards_nivel)}
    if flashcard_id not in indices:
        flashcard_id = flashcards_nivel[0]['id']
    
    flashcard_actual = next((f for f in flashcards_nivel if f['id'] == flashcard_id), flashcards_nivel[0])
    flashcard_index = indices[flashcard_actual['id']] + 1
    total_flashcards = len(flashcards_nivel)
    
    # Calcular puntos en este nivel
    intentos_nivel = IntentoFlashcard.query.filter_by(usuario_id=current_user.id).join(
        Flashcard, IntentoFlashcard.flashcard_id == Flashcard.id
    ).filter(Flashcard.nivel == nivel).all()
    puntos_nivel = sum([i.puntos_obtenidos or 0 for i in intentos_nivel if i.es_correcto])
    
    progreso = (flashcard_index / total_flashcards * 100)
    
    return render_template('flashcards.html',
                         flashcard=flashcard_actual,
                         flashcard_actual=flashcard_index,
                         total_flashcards=total_flashcards,
                         nivel_actual=nivel,
                         puntos_nivel=puntos_nivel,
                         progreso=progreso)

@app.route('/api/verificar_flashcard', methods=['POST'])
@login_required
def verificar_flashcard():
    """API para verificar respuestas de flashcards"""
    data = request.json
    flashcard_id = data.get('flashcard_id')
    respuesta = data.get('respuesta', '').strip().lower()
    tiempo = data.get('tiempo', 0)
    
    # Cargar flashcard
    with open('flashcards.json', 'r', encoding='utf-8') as f:
        flashcards = json.load(f)
    
    flashcard = next((f for f in flashcards if f['id'] == flashcard_id), None)
    
    if not flashcard:
        return jsonify({'error': 'Flashcard no encontrada'}), 404
    
    # Verificar respuesta (case insensitive, ignorando espacios extras)
    respuesta_correcta = flashcard['respuesta_correcta'].strip().lower()
    es_correcto = respuesta == respuesta_correcta
    
    # Buscar flashcard en BD o crearla
    flashcard_db = Flashcard.query.filter_by(id=flashcard_id).first()
    if not flashcard_db:
        flashcard_db = Flashcard(
            id=flashcard['id'],
            nivel=flashcard['nivel'],
            categoria=flashcard['categoria'],
            pregunta=flashcard['pregunta'],
            respuesta_correcta=flashcard['respuesta_correcta'],
            pista=flashcard.get('pista', ''),
            explicacion=flashcard.get('explicacion', ''),
            puntos=flashcard.get('puntos', 10)
        )
        db.session.add(flashcard_db)
        db.session.commit()
    
    # Calcular puntos
    puntos_base = flashcard.get('puntos', 10)
    puntos_obtenidos = puntos_base if es_correcto else 0
    
    # Bonificación por racha
    if es_correcto and current_user.racha_actual >= 3:
        puntos_obtenidos += 5
    if es_correcto and current_user.racha_actual >= 5:
        puntos_obtenidos += 10
    
    # Registrar intento
    intento = IntentoFlashcard(
        usuario_id=current_user.id,
        flashcard_id=flashcard_db.id,
        respuesta_usuario=data.get('respuesta'),
        es_correcto=es_correcto,
        tiempo_respuesta=tiempo
    )
    db.session.add(intento)
    
    # Actualizar estadísticas de la flashcard
    flashcard_db.veces_usada += 1
    if es_correcto:
        flashcard_db.veces_acertada += 1
    
    # Actualizar usuario
    if es_correcto:
        current_user.puntos_totales += puntos_obtenidos
        current_user.racha_actual += 1
        current_user.ejercicios_correctos += 1
    else:
        current_user.racha_actual = 0
    
    current_user.ejercicios_completados += 1
    
    # Actualizar nivel del usuario
    if current_user.puntos_totales < 100:
        current_user.nivel = 1
    elif current_user.puntos_totales < 300:
        current_user.nivel = 2
    elif current_user.puntos_totales < 600:
        current_user.nivel = 3
    elif current_user.puntos_totales < 1000:
        current_user.nivel = 4
    else:
        current_user.nivel = 5
    
    db.session.commit()
    
    return jsonify({
        'correcto': es_correcto,
        'respuesta_correcta': flashcard['respuesta_correcta'],
        'explicacion': flashcard.get('explicacion', ''),
        'puntos': puntos_obtenidos,
        'puntos_totales': current_user.puntos_totales,
        'racha': current_user.racha_actual,
        'nivel': current_user.nivel
    })
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
