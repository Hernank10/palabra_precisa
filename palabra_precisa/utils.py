import json
import random
from datetime import datetime

class GeneradorEjercicios:
    def __init__(self, archivo_base='ejercicios.json', archivo_usuario='ejercicios_usuario.json'):
        self.archivo_base = archivo_base
        self.archivo_usuario = archivo_usuario
        self.ejercicios = self.cargar_ejercicios()
    
    def cargar_ejercicios(self):
        """Carga todos los ejercicios (base + usuario)"""
        ejercicios = []
        
        # Cargar ejercicios base
        try:
            with open(self.archivo_base, 'r', encoding='utf-8') as f:
                ejercicios_base = json.load(f)
                ejercicios.extend(ejercicios_base)
                print(f"✅ Cargados {len(ejercicios_base)} ejercicios base")
        except FileNotFoundError:
            print(f"⚠️ Archivo {self.archivo_base} no encontrado")
        except json.JSONDecodeError as e:
            print(f"❌ Error en formato JSON de {self.archivo_base}: {e}")
        
        # Cargar ejercicios de usuario
        try:
            with open(self.archivo_usuario, 'r', encoding='utf-8') as f:
                ejercicios_usuario = json.load(f)
                ejercicios.extend(ejercicios_usuario)
                print(f"✅ Cargados {len(ejercicios_usuario)} ejercicios de usuario")
        except FileNotFoundError:
            print(f"ℹ️ Archivo {self.archivo_usuario} no encontrado, se creará al guardar")
        except json.JSONDecodeError as e:
            print(f"❌ Error en formato JSON de {self.archivo_usuario}: {e}")
        
        print(f"📚 Total de ejercicios: {len(ejercicios)}")
        return ejercicios
    
    def guardar_ejercicio_usuario(self, ejercicio):
        """Guarda un ejercicio creado por usuario"""
        try:
            with open(self.archivo_usuario, 'r', encoding='utf-8') as f:
                ejercicios = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            ejercicios = []
        
        # Asignar nuevo ID
        max_id = max([e.get('id', 0) for e in self.ejercicios] + [0])
        ejercicio['id'] = max_id + 1
        ejercicio['fecha_creacion'] = datetime.now().isoformat()
        ejercicio['usuario_creador'] = True
        
        ejercicios.append(ejercicio)
        
        with open(self.archivo_usuario, 'w', encoding='utf-8') as f:
            json.dump(ejercicios, f, indent=2, ensure_ascii=False)
        
        # Actualizar lista en memoria
        self.ejercicios.append(ejercicio)
        print(f"✅ Ejercicio guardado con ID: {ejercicio['id']}")
        return ejercicio['id']
    
    def obtener_ejercicio_aleatorio(self, categoria=None, dificultad=None):
        """Obtiene un ejercicio aleatorio con filtros opcionales"""
        ejercicios_filtrados = self.ejercicios.copy()
        
        if categoria:
            ejercicios_filtrados = [e for e in ejercicios_filtrados 
                                   if e.get('categoria', '').lower() == categoria.lower()]
        
        if dificultad:
            ejercicios_filtrados = [e for e in ejercicios_filtrados 
                                   if e.get('dificultad') == dificultad]
        
        if not ejercicios_filtrados:
            return None
        
        return random.choice(ejercicios_filtrados)
    
    def obtener_ejercicios_por_categoria(self, categoria):
        """Obtiene todos los ejercicios de una categoría"""
        return [e for e in self.ejercicios 
                if e.get('categoria', '').lower() == categoria.lower()]
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas de los ejercicios"""
        stats = {
            'total': len(self.ejercicios),
            'por_categoria': {},
            'por_dificultad': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            'total_puntos': 0
        }
        
        for e in self.ejercicios:
            cat = e.get('categoria', 'Sin categoría')
            stats['por_categoria'][cat] = stats['por_categoria'].get(cat, 0) + 1
            stats['por_dificultad'][e.get('dificultad', 1)] += 1
            stats['total_puntos'] += e.get('puntos', 10)
        
        return stats
    
    def generar_practica(self, num_preguntas=10, categorias=None):
        """Genera una práctica con número específico de preguntas"""
        ejercicios_disponibles = self.ejercicios.copy()
        
        if categorias:
            if isinstance(categorias, str):
                categorias = [categorias]
            ejercicios_disponibles = [e for e in ejercicios_disponibles 
                                     if e.get('categoria') in categorias]
        
        if len(ejercicios_disponibles) < num_preguntas:
            num_preguntas = len(ejercicios_disponibles)
            print(f"⚠️ Solo hay {num_preguntas} ejercicios disponibles")
        
        if num_preguntas == 0:
            return []
        
        return random.sample(ejercicios_disponibles, num_preguntas)


class SistemaPuntuacion:
    def __init__(self):
        self.bonificaciones = {
            'racha_3': 5,
            'racha_5': 10,
            'racha_10': 25,
            'perfecto': 50,
            'rapidez': 10
        }
    
    def calcular_puntos(self, ejercicio, tiempo_respuesta=None, racha_actual=0):
        """Calcula puntos incluyendo bonificaciones"""
        puntos_base = ejercicio.get('puntos', 10)
        puntos_totales = puntos_base
        
        # Bonificación por dificultad
        dificultad = ejercicio.get('dificultad', 1)
        puntos_totales *= dificultad
        
        # Bonificación por racha
        if racha_actual >= 10:
            puntos_totales += self.bonificaciones['racha_10']
        elif racha_actual >= 5:
            puntos_totales += self.bonificaciones['racha_5']
        elif racha_actual >= 3:
            puntos_totales += self.bonificaciones['racha_3']
        
        # Bonificación por rapidez (menos de 5 segundos)
        if tiempo_respuesta and tiempo_respuesta < 5:
            puntos_totales += self.bonificaciones['rapidez']
        
        return puntos_totales
    
    def calcular_nivel(self, puntos_totales):
        """Calcula el nivel del usuario basado en puntos"""
        if puntos_totales < 100:
            return 1, "Principiante"
        elif puntos_totales < 300:
            return 2, "Aprendiz"
        elif puntos_totales < 600:
            return 3, "Intermedio"
        elif puntos_totales < 1000:
            return 4, "Avanzado"
        elif puntos_totales < 1500:
            return 5, "Experto"
        else:
            return 6, "Maestro"
