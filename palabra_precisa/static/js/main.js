// ========================================
// PALABRA PRECISA - JAVASCRIPT PRINCIPAL
// ========================================

// Esperar a que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Palabra Precisa iniciado');
    
    // Inicializar todas las funcionalidades
    initTooltips();
    initAnimations();
    initFormValidation();
    initCountdowns();
    initAutoHideAlerts();
    initScrollAnimations();
});

// ========================================
// TOOLTIPS
// ========================================

function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltip = e.target.getAttribute('data-tooltip');
    if (!tooltip) return;
    
    const tooltipEl = document.createElement('div');
    tooltipEl.className = 'custom-tooltip';
    tooltipEl.textContent = tooltip;
    tooltipEl.style.cssText = `
        position: absolute;
        background: #333;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 1000;
        pointer-events: none;
    `;
    
    document.body.appendChild(tooltipEl);
    
    const rect = e.target.getBoundingClientRect();
    tooltipEl.style.top = rect.top - tooltipEl.offsetHeight - 5 + 'px';
    tooltipEl.style.left = rect.left + (rect.width / 2) - (tooltipEl.offsetWidth / 2) + 'px';
    
    e.target._tooltip = tooltipEl;
}

function hideTooltip(e) {
    if (e.target._tooltip) {
        e.target._tooltip.remove();
        delete e.target._tooltip;
    }
}

// ========================================
// ANIMACIONES
// ========================================

function initAnimations() {
    // Animación para elementos con clase fade-in
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach((el, index) => {
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Animación para cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Contador animado
    animateCounters();
}

function animateCounters() {
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 segundos
        const step = target / (duration / 16); // 60fps
        
        let current = 0;
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                counter.textContent = target;
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current);
            }
        }, 16);
    });
}

// ========================================
// VALIDACIÓN DE FORMULARIOS
// ========================================

function initFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
    
    const inputs = document.querySelectorAll('input[required], textarea[required], select[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', validateInput);
        input.addEventListener('input', clearValidation);
    });
}

function validateForm(e) {
    const form = e.target;
    let isValid = true;
    
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    inputs.forEach(input => {
        if (!validateInput({ target: input })) {
            isValid = false;
        }
    });
    
    if (!isValid) {
        e.preventDefault();
        showNotification('Por favor, completa todos los campos requeridos', 'error');
    }
    
    return isValid;
}

function validateInput(e) {
    const input = e.target;
    const value = input.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Remover validación previa
    clearValidation(e);
    
    if (!value) {
        isValid = false;
        errorMessage = 'Este campo es requerido';
    } else if (input.type === 'email' && !isValidEmail(value)) {
        isValid = false;
        errorMessage = 'Ingresa un email válido';
    } else if (input.type === 'password' && value.length < 6) {
        isValid = false;
        errorMessage = 'La contraseña debe tener al menos 6 caracteres';
    }
    
    if (!isValid) {
        input.classList.add('is-invalid');
        
        // Crear mensaje de error
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = errorMessage;
        
        input.parentNode.appendChild(feedback);
    }
    
    return isValid;
}

function clearValidation(e) {
    const input = e.target;
    input.classList.remove('is-invalid');
    
    const feedback = input.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// ========================================
// NOTIFICACIONES
// ========================================

function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.setAttribute('role', 'alert');
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(notification, container.firstChild);
    
    if (duration > 0) {
        setTimeout(() => {
            notification.remove();
        }, duration);
    }
}

// ========================================
// CONTADORES REGRESIVOS
// ========================================

function initCountdowns() {
    const countdowns = document.querySelectorAll('.countdown');
    countdowns.forEach(countdown => {
        const endDate = new Date(countdown.getAttribute('data-end')).getTime();
        
        const timer = setInterval(() => {
            const now = new Date().getTime();
            const distance = endDate - now;
            
            if (distance < 0) {
                clearInterval(timer);
                countdown.innerHTML = '¡Tiempo terminado!';
                return;
            }
            
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            
            countdown.innerHTML = `
                <span class="badge bg-primary">${days}d</span>
                <span class="badge bg-primary">${hours}h</span>
                <span class="badge bg-primary">${minutes}m</span>
                <span class="badge bg-primary">${seconds}s</span>
            `;
        }, 1000);
    });
}

// ========================================
// AUTO OCULTAR ALERTAS
// ========================================

function initAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach((alert, index) => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 3000 + (index * 1000));
    });
}

// ========================================
// ANIMACIONES AL SCROLL
// ========================================

function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(el => observer.observe(el));
}

// ========================================
// MANEJO DE RESPUESTAS DE EJERCICIOS
// ========================================

function checkAnswer(button, correctAnswer, points) {
    const selectedOption = document.querySelector('input[name="exerciseOption"]:checked');
    
    if (!selectedOption) {
        showNotification('Por favor, selecciona una opción', 'warning');
        return;
    }
    
    const userAnswer = selectedOption.value;
    const feedback = document.getElementById('exerciseFeedback');
    const isCorrect = userAnswer === correctAnswer;
    
    if (isCorrect) {
        feedback.innerHTML = `
            <div class="alert alert-success">
                <strong>✅ ¡Correcto!</strong><br>
                +${points} puntos
            </div>
        `;
        
        // Actualizar puntuación
        updateScore(points);
    } else {
        feedback.innerHTML = `
            <div class="alert alert-danger">
                <strong>❌ Incorrecto</strong><br>
                La respuesta correcta es: <strong>${correctAnswer}</strong>
            </div>
        `;
    }
    
    // Deshabilitar opciones
    document.querySelectorAll('input[name="exerciseOption"]').forEach(input => {
        input.disabled = true;
    });
    
    button.disabled = true;
    document.getElementById('nextButton').style.display = 'block';
}

function updateScore(points) {
    const scoreElement = document.getElementById('currentScore');
    if (scoreElement) {
        let currentScore = parseInt(scoreElement.textContent);
        currentScore += points;
        scoreElement.textContent = currentScore;
    }
}

// ========================================
// MANEJO DE FLASHCARDS
// ========================================

function toggleFlashcard(flashcard) {
    flashcard.classList.toggle('revealed');
}

function checkFlashcardAnswer(flashcardId, userAnswer, correctAnswer, points) {
    const isCorrect = userAnswer.toLowerCase().trim() === correctAnswer.toLowerCase().trim();
    const feedback = document.getElementById(`feedback-${flashcardId}`);
    
    if (isCorrect) {
        feedback.innerHTML = `
            <div class="alert alert-success mt-3">
                ✅ ¡Correcto! +${points} puntos
            </div>
        `;
        
        // Animar confeti si es correcto
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });
    } else {
        feedback.innerHTML = `
            <div class="alert alert-danger mt-3">
                ❌ Incorrecto. La respuesta es: ${correctAnswer}
            </div>
        `;
    }
}

// ========================================
// FILTROS DE EJERCICIOS
// ========================================

function filterExercises() {
    const category = document.getElementById('categoryFilter')?.value;
    const difficulty = document.getElementById('difficultyFilter')?.value;
    const status = document.getElementById('statusFilter')?.value;
    
    const exercises = document.querySelectorAll('.exercise-item');
    
    exercises.forEach(exercise => {
        let show = true;
        
        if (category && exercise.dataset.category !== category) {
            show = false;
        }
        
        if (difficulty && exercise.dataset.difficulty !== difficulty) {
            show = false;
        }
        
        if (status === 'completed' && !exercise.dataset.completed) {
            show = false;
        }
        
        if (status === 'pending' && exercise.dataset.completed) {
            show = false;
        }
        
        exercise.style.display = show ? 'block' : 'none';
    });
}

// ========================================
// EXPORTAR PROGRESO
// ========================================

function exportProgress() {
    const progress = {
        user: document.getElementById('username')?.textContent,
        points: document.getElementById('totalPoints')?.textContent,
        level: document.getElementById('userLevel')?.textContent,
        streak: document.getElementById('currentStreak')?.textContent,
        date: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(progress, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `progreso_${progress.user}_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

// ========================================
// COMPARTIR EN REDES SOCIALES
// ========================================

function shareProgress() {
    const points = document.getElementById('totalPoints')?.textContent;
    const level = document.getElementById('userLevel')?.textContent;
    
    const text = `🎯 He alcanzado ${points} puntos y nivel ${level} en Palabra Precisa. ¡Aprende lenguaje preciso conmigo!`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Mi progreso en Palabra Precisa',
            text: text,
            url: window.location.origin
        });
    } else {
        // Fallback: copiar al portapapeles
        navigator.clipboard.writeText(text).then(() => {
            showNotification('¡Texto copiado al portapapeles!', 'success');
        });
    }
}

// ========================================
// MODO OSCURO (opcional)
// ========================================

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    
    showNotification(
        isDark ? '🌙 Modo oscuro activado' : '☀️ Modo claro activado',
        'info'
    );
}

// Cargar preferencia de modo oscuro
const savedDarkMode = localStorage.getItem('darkMode') === 'true';
if (savedDarkMode) {
    document.body.classList.add('dark-mode');
}

// ========================================
// REGISTRO DE ERRORES
// ========================================

window.addEventListener('error', function(e) {
    console.error('Error capturado:', e.error);
    
    // Enviar error al servidor si es necesario
    if (window.location.hostname !== 'localhost') {
        fetch('/api/log-error', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: e.error?.message,
                stack: e.error?.stack,
                url: window.location.href
            })
        }).catch(() => {});
    }
});

// ========================================
// INICIALIZACIÓN DE BOOTSTRAP
// ========================================

// Inicializar tooltips de Bootstrap
if (typeof bootstrap !== 'undefined') {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// ========================================
// EXPORTAR FUNCIONES GLOBALES
// ========================================

window.PalabraPrecisa = {
    checkAnswer,
    toggleFlashcard,
    checkFlashcardAnswer,
    filterExercises,
    exportProgress,
    shareProgress,
    toggleDarkMode,
    showNotification
};
