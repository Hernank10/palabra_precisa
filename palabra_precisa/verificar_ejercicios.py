import json
from collections import Counter

try:
    with open('ejercicios.json', 'r', encoding='utf-8') as f:
        ejercicios = json.load(f)
    
    print("=" * 60)
    print("📊 VERIFICACIÓN DE EJERCICIOS")
    print("=" * 60)
    print(f"Total de ejercicios: {len(ejercicios)}")
    
    if len(ejercicios) < 100:
        print(f"⚠️ Faltan {100 - len(ejercicios)} ejercicios para llegar a 100")
    elif len(ejercicios) > 100:
        print(f"⚠️ Hay {len(ejercicios) - 100} ejercicios de más")
    else:
        print("✅ ¡Tienes exactamente 100 ejercicios!")
    
    print("\n📚 Distribución por categoría:")
    categorias = Counter([e.get('categoria', 'Sin categoría') for e in ejercicios])
    for cat, count in sorted(categorias.items()):
        print(f"   {cat}: {count} ejercicios")
    
    print("\n🎯 Distribución por dificultad:")
    dificultades = Counter([e.get('dificultad', 1) for e in ejercicios])
    for dif, count in sorted(dificultades.items()):
        print(f"   Nivel {dif}: {count} ejercicios")
    
    print("\n💰 Puntuación total disponible:")
    puntos_totales = sum([e.get('puntos', 10) for e in ejercicios])
    print(f"   {puntos_totales} puntos")
    
    print("\n✅ Verificando IDs únicos:")
    ids = [e.get('id', 0) for e in ejercicios]
    if len(set(ids)) == len(ids):
        print("   Todos los IDs son únicos ✓")
    else:
        duplicados = [id for id in ids if ids.count(id) > 1]
        print(f"   ⚠️ Hay IDs duplicados: {set(duplicados)}")
    
    print("\n🔍 Primeros 5 ejercicios:")
    for i, e in enumerate(ejercicios[:5]):
        print(f"   {i+1}. [{e.get('categoria', 'N/A')}] {e.get('pregunta', 'N/A')[:50]}...")
    
    print("\n🔍 Últimos 5 ejercicios:")
    for i, e in enumerate(ejercicios[-5:]):
        print(f"   {len(ejercicios)-4+i}. [{e.get('categoria', 'N/A')}] {e.get('pregunta', 'N/A')[:50]}...")
    
    print("\n" + "=" * 60)
    
    # Verificar estructura de cada ejercicio
    print("\n🔧 Verificando estructura de ejercicios:")
    errores = 0
    for i, e in enumerate(ejercicios):
        campos_requeridos = ['id', 'categoria', 'pregunta', 'opciones', 'respuesta_correcta', 'explicacion', 'dificultad', 'puntos']
        for campo in campos_requeridos:
            if campo not in e:
                print(f"   ⚠️ Ejercicio {i+1} falta el campo: {campo}")
                errores += 1
    
    if errores == 0:
        print("   ✅ Todos los ejercicios tienen la estructura correcta")
    
except FileNotFoundError:
    print("❌ No se encuentra el archivo ejercicios.json")
    print("   Crea el archivo primero con: nano ejercicios.json")
except json.JSONDecodeError as e:
    print(f"❌ Error en el formato JSON: {e}")
    print("   Revisa que el JSON tenga comillas y comas correctamente")
