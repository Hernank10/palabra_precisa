// ========================================
// PRÁCTICA DE EJERCICIOS - JAVASCRIPT
// ========================================

let currentExercise = 0;
let totalExercises = 0;
let userAnswers = [];
let score = 0;
let streak = 0;
let timer = null;
let timePerQuestion = 0;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('📝 Módulo de práctica iniciado');
    initializePractice();
    startTimer();
});

function initializePractice() {
    // Obtener datos del DOM
    totalExercises = parseInt(document.getElementById('totalExercises')?.textContent) || 0;
    score = parseInt(document.getElementById('currentScore')?.textContent) || 0;
    streak = parseInt(document.getElementById('currentStreak')?.textContent) || 0;
    
    // Inicializar contadores
    updateProgress();
}

function startTimer() {
    timePerQuestion = 0;
    timer = setInterval(() => {
        timePerQuestion++;
        const timerElement = document.getElementById('timer');
        if (timerElement) {
            const minutes = Math.floor(timePerQuestion / 60);
            const seconds = timePerQuestion % 60;
            timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    }, 1000);
}

function selectOption(element) {
    // Remover selección previa
    document.querySelectorAll('.option-item').forEach(opt => {
        opt.classList.remove('selected');
    });
    
    // Seleccionar nueva opción
    element.classList.add('selected');
    window.selectedOption = element.getAttribute('data-option');
}

async function checkAnswer() {
    if (!window.selectedOption) {
        showNotification('Por favor, selecciona una opción', 'warning');
        return;
    }
    
    const exerciseId = parseInt(document.getElementById('exerciseId')?.value);
    const feedbackContainer = document.getElementById('feedbackContainer');
    const checkBtn = document.getElementById('checkBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    // Detener timer
    clearInterval(timer);
    
    try {
        // Enviar respuesta al servidor
        const response = await fetch('/api/verificar_respuesta', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ejercicio_id: exerciseId,
                respuesta: window.selectedOption,
                tiempo: timePerQuestion
            })
        });
        
        const data = await response.json();
        
        // Marcar opciones como correctas/incorrectas
        document.querySelectorAll('.option-item').forEach(opt => {
            opt.style.pointerEvents = 'none';
            if (opt.getAttribute('data-option') === data.respuesta_correcta) {
                opt.classList.add('correct');
            } else if (opt.classList.contains('selected') && !data.correcto) {
                opt.classList.add('incorrect');
            }
        });
        
        // Mostrar feedback
        feedbackContainer.style.display = 'block';
        
        if (data.correcto) {
            score += data.puntos;
            streak = data.racha;
            
            feedbackContainer.innerHTML = `
                <div class="feedback-message feedback-correct">
                    <strong>✅ ¡Correcto!</strong><br>
                    +${data.puntos} puntos<br>
                    <small>${data.explicacion || '¡Bien hecho!'}</small>
                </div>
            `;
            
            // Animación de confeti
            if (typeof confetti !== 'undefined') {
                confetti({
                    particleCount: 100,
                    spread: 70,
                    origin: { y: 0.6 }
                });
            }
        } else {
            streak = 0;
            
            feedbackContainer.innerHTML = `
                <div class="feedback-message feedback-incorrect">
                    <strong>❌ Incorrecto</strong><br>
                    La respuesta correcta es: <strong>${data.respuesta_correcta}</strong><br>
                    <small>${data.explicacion || ''}</small>
                </div>
            `;
        }
        
        // Actualizar UI
        document.getElementById('currentScore').textContent = score;
        document.getElementById('currentStreak').textContent = streak;
        
        checkBtn.style.display = 'none';
        nextBtn.style.display = 'block';
        
        // Guardar respuesta
        userAnswers.push({
            exerciseId: exerciseId,
            answer: window.selectedOption,
            correct: data.correcto,
            points: data.puntos,
            time: timePerQuestion
        });
        
    } catch (error) {
        console.error('Error al verificar respuesta:', error);
        showNotification('Error al comunicarse con el servidor', 'error');
    }
}

function nextExercise() {
    currentExercise++;
    
    if (currentExercise < totalExercises) {
        // Recargar la página para el siguiente ejercicio
        window.location.href = `/practica?page=${currentExercise + 1}`;
    } else {
        // Práctica completada - mostrar resultados
        showResults();
    }
}

function showResults() {
    const resultsContainer = document.getElementById('resultsContainer');
    if (resultsContainer) {
        // Calcular estadísticas
        const correctAnswers = userAnswers.filter(a => a.correct).length;
        const accuracy = (correctAnswers / totalExercises * 100).toFixed(1);
        const totalTime = userAnswers.reduce((sum, a) => sum + a.time, 0);
        const avgTime = (totalTime / totalExercises).toFixed(1);
        
        resultsContainer.innerHTML = `
            <div class="exercise-card">
                <h3 class="text-center">📊 Resultados de la práctica</h3>
                
                <div class="row mt-4">
                    <div class="col-md-3">
                        <div class="text-center">
                            <h2 class="text-primary">${score}</h2>
                            <p>Puntos totales</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h2 class="text-success">${correctAnswers}/${totalExercises}</h2>
                            <p>Correctas</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h2 class="text-info">${accuracy}%</h2>
                            <p>Precisión</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h2 class="text-warning">${avgTime}s</h2>
                            <p>Tiempo promedio</p>
                        </div>
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <a href="/practica" class="btn btn-primary">Nueva práctica</a>
                    <a href="/flashcards" class="btn btn-outline-primary">Practicar flashcards</a>
                </div>
            </div>
        `;
    }
}

function updateProgress() {
    const progress = ((currentExercise + 1) / totalExercises) * 100;
    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        progressBar.style.width = progress + '%';
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 3000);
}

// Exportar funciones para uso global
window.selectOption = selectOption;
window.checkAnswer = checkAnswer;
window.nextExercise = nextExercise;
