from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import json
import os
import math
from functools import wraps
from collections import Counter, defaultdict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Importar el manejador de base de datos
from database import db_manager

# Importar módulos modularizados
from preguntas_trivia import banco_preguntas, obtener_pregunta_aleatoria
from gestor_alumnos import gestor_alumnos, obtener_alumnos_por_anio
from analizador_psicopedagogico import analizador_psicopedagogico

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'puertas_del_sol_secret_key_2024')

# Configurar el analizador psicopedagógico con la base de datos
analizador_psicopedagogico.db_manager = db_manager

# 1. PRIMERO: Usuarios base — se cargan desde usuarios.json (ver .gitignore)
# Las contraseñas NO deben estar en el código fuente.
USUARIOS_DOCENTES = {}

# 2. SEGUNDO: Definir las funciones helper
def cargar_json_seguro(archivo):
    """Función helper para cargar archivos JSON de forma segura"""
    if os.path.exists(archivo):
        try:
            with open(archivo, encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def guardar_json_seguro(archivo, datos):
    """Función helper para guardar archivos JSON de forma segura"""
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando {archivo}: {e}")
        return False
# Agregar después de las funciones helper existentes:

import random
from datetime import datetime

# Base de datos de preguntas para trivia
PREGUNTAS_TRIVIA = {
    'historia_cordoba': [
        {
            'pregunta': '¿En qué año se fundó la ciudad de Córdoba?',
            'opciones': ['1573', '1580', '1588', '1595'],
            'respuesta_correcta': 0,
            'puntos': 15,
            'explicacion': 'Córdoba fue fundada por Jerónimo Luis de Cabrera el 6 de julio de 1573.'
        },
        {
            'pregunta': '¿Quién fundó la Universidad Nacional de Córdoba?',
            'opciones': ['Los Jesuitas', 'Los Franciscanos', 'El Virrey', 'Los Dominicos'],
            'respuesta_correcta': 0,
            'puntos': 15,
            'explicacion': 'La UNC fue fundada por los Jesuitas en 1613, siendo la más antigua de Argentina.'
        },
        {
            'pregunta': '¿Cómo se llama el barrio histórico de Córdoba Capital?',
            'opciones': ['La Cañada', 'Güemes', 'San Vicente', 'Alberdi'],
            'respuesta_correcta': 0,
            'puntos': 10,
            'explicacion': 'La Cañada es el barrio histórico donde está la Catedral y el Cabildo.'
        }
    ],
    'geografia_cordoba': [
        {
            'pregunta': '¿Cuál es el río más importante de Córdoba?',
            'opciones': ['Río Primero', 'Río Segundo', 'Río Tercero', 'Río Cuarto'],
            'respuesta_correcta': 0,
            'puntos': 10,
            'explicacion': 'El Río Primero (Suquía) atraviesa la capital cordobesa.'
        },
        {
            'pregunta': '¿En qué sierras se encuentra el Cerro Champaquí?',
            'opciones': ['Sierras Grandes', 'Sierras Chicas', 'Sierras del Norte', 'Sierras del Sur'],
            'respuesta_correcta': 0,
            'puntos': 15,
            'explicacion': 'El Champaquí (2884m) es el pico más alto de Córdoba, en las Sierras Grandes.'
        }
    ],
    'cultura_argentina': [
        {
            'pregunta': '¿Quién escribió el Martín Fierro?',
            'opciones': ['José Hernández', 'Domingo Sarmiento', 'Bartolomé Mitre', 'Leopoldo Lugones'],
            'respuesta_correcta': 0,
            'puntos': 15,
            'explicacion': 'José Hernández escribió "El Gaucho Martín Fierro" (1872) y "La Vuelta de Martín Fierro" (1879).'
        },
        {
            'pregunta': '¿En qué año se sancionó la Constitución Nacional Argentina?',
            'opciones': ['1853', '1860', '1810', '1816'],
            'respuesta_correcta': 0,
            'puntos': 15,
            'explicacion': 'La Constitución fue sancionada en Santa Fe en 1853.'
        }
    ],
    'ciencias_naturales': [
        {
            'pregunta': '¿Cuál es el animal nacional de Argentina?',
            'opciones': ['El Hornero', 'El Cóndor', 'El Ñandú', 'La Vicuña'],
            'respuesta_correcta': 0,
            'puntos': 10,
            'explicacion': 'El Hornero es el ave nacional argentina, símbolo del trabajo y la perseverancia.'
        },
        {
            'pregunta': '¿Qué tipo de clima predomina en Córdoba?',
            'opciones': ['Templado continental', 'Subtropical', 'Árido', 'Mediterráneo'],
            'respuesta_correcta': 0,
            'puntos': 12,
            'explicacion': 'Córdoba tiene clima templado continental con veranos cálidos e inviernos secos.'
        }
    ],
    'matematicas': [
        {
            'pregunta': '¿Cuál es el resultado de 15² - 10²?',
            'opciones': ['125', '225', '325', '25'],
            'respuesta_correcta': 0,
            'puntos': 12,
            'explicacion': '15² = 225 y 10² = 100, por lo tanto 225 - 100 = 125.'
        },
        {
            'pregunta': 'Si un triángulo tiene ángulos de 60°, 60° y 60°, ¿qué tipo de triángulo es?',
            'opciones': ['Equilátero', 'Isósceles', 'Escaleno', 'Rectángulo'],
            'respuesta_correcta': 0,
            'puntos': 10,
            'explicacion': 'Un triángulo con los tres ángulos iguales (60°) es equilátero.'
        }
    ],
    'deportes_cordoba': [
        {
            'pregunta': '¿Cuál es el club de fútbol más antiguo de Córdoba?',
            'opciones': ['Talleres', 'Belgrano', 'Instituto', 'Racing'],
            'respuesta_correcta': 0,
            'puntos': 15,
            'explicacion': 'Talleres fue fundado en 1913, siendo el club más antiguo de la provincia.'
        }
    ]
}

def obtener_pregunta_aleatoria():
    """Selecciona una pregunta aleatoria de cualquier categoría"""
    # Obtener todas las preguntas de todas las categorías
    todas_preguntas = []
    for categoria, preguntas in PREGUNTAS_TRIVIA.items():
        for pregunta in preguntas:
            pregunta_con_categoria = pregunta.copy()
            pregunta_con_categoria['categoria'] = categoria
            todas_preguntas.append(pregunta_con_categoria)
    
    return random.choice(todas_preguntas)

def calcular_puntos_gamificacion(voto_data, respuesta_trivia=None):
    """Calcula puntos gamificados basados en votación + trivia educativa"""
    puntos = 0
    
    # ✅ PUNTOS BASE por completar votación
    puntos += 50  # Puntos base más altos
    
    # ✅ PUNTOS por diversidad en calificaciones (premiar pensamiento crítico)
    ratings = voto_data.get('ratings', {})
    if ratings:
        valores_unicos = len(set(ratings.values()))
        if valores_unicos >= 4:  # Usó al menos 4 valores diferentes
            puntos += 20  # Bonus por evaluación diversa
        elif valores_unicos >= 3:
            puntos += 10
    
    # ✅ PUNTOS TRIVIA - Lo más importante ahora
    if respuesta_trivia:
        if respuesta_trivia.get('correcta', False):
            pregunta_puntos = respuesta_trivia.get('puntos_pregunta', 10)
            puntos += pregunta_puntos  # Puntos de la pregunta específica
            
            # Bonus por categoría difícil
            categoria = respuesta_trivia.get('categoria', '')
            if categoria in ['historia_cordoba', 'matematicas']:
                puntos += 5  # Bonus por categorías más desafiantes
        else:
            puntos += 2  # Puntos de consolación por intentar
    
    # ✅ BONUS por buen comportamiento social
    bloqueado = voto_data.get('bloqueado')
    if not bloqueado:  # No bloqueó a nadie
        puntos += 5  # Bonus por convivencia positiva
    
    return puntos

def actualizar_ranking_clase(anio, alumno, puntos, datos_trivia=None):
    """Actualiza el ranking usando la base de datos"""
    from datetime import datetime
    
    # Obtener datos actuales del alumno desde la base de datos
    ranking_alumno = db_manager.obtener_ranking_alumno(anio, alumno)
    
    # Actualizar puntos
    ranking_alumno['puntos_totales'] += puntos
    ranking_alumno['fecha_ultimo_voto'] = datetime.now().isoformat()
    
    # ✅ ACTUALIZAR estadísticas de trivia
    if datos_trivia:
        stats = ranking_alumno['trivia_stats']
        stats['preguntas_respondidas'] += 1
        
        if datos_trivia.get('correcta', False):
            stats['preguntas_correctas'] += 1
            stats['racha_actual'] += 1
            stats['mejor_racha'] = max(stats['mejor_racha'], stats['racha_actual'])
            
            # Agregar categoría dominada
            categoria = datos_trivia.get('categoria', '')
            if categoria not in stats['categorias_dominadas']:
                stats['categorias_dominadas'].append(categoria)
        else:
            stats['racha_actual'] = 0
    
    # Calcular nivel basado en puntos (más generoso)
    puntos_totales = ranking_alumno['puntos_totales']
    nuevo_nivel = min(20, (puntos_totales // 100) + 1)  # Nivel cada 100 puntos, máximo 20
    
    if nuevo_nivel > ranking_alumno['nivel']:
        ranking_alumno['nivel'] = nuevo_nivel
        # Otorgar badge por subir nivel
        ranking_alumno['badges'].append(f"🎓 Nivel {nuevo_nivel}")
    
    # Guardar en la base de datos
    exito = db_manager.actualizar_ranking_completo(anio, alumno, ranking_alumno)
    
    if not exito:
        print(f"⚠️ Error guardando ranking para {alumno} en {anio}")
    
    return ranking_alumno

def otorgar_badges_trivia(alumno_stats, datos_trivia):
    """Otorga badges basados en desempeño en trivia"""
    badges_nuevos = []
    
    if not datos_trivia:
        return badges_nuevos
        
    trivia_stats = alumno_stats.get('trivia_stats', {})
    
    # Badge por primera respuesta correcta
    if trivia_stats.get('preguntas_correctas', 0) == 1:
        badges_nuevos.append("🌟 Primer Acierto")
    
    # Badge por racha de respuestas correctas
    racha_actual = trivia_stats.get('racha_actual', 0)
    if racha_actual == 3:
        badges_nuevos.append("🔥 Racha x3")
    elif racha_actual == 5:
        badges_nuevos.append("🏆 Racha x5")
    elif racha_actual >= 10:
        badges_nuevos.append("👑 Súper Racha!")
    
    # Badge por dominar categorías
    categorias = trivia_stats.get('categorias_dominadas', [])
    if len(categorias) >= 3:
        badges_nuevos.append("🎯 Conocimiento Diverso")
    if len(categorias) >= 5:
        badges_nuevos.append("🧠 Erudito")
    
    # Badge por categorías específicas
    if datos_trivia.get('correcta', False):
        categoria = datos_trivia.get('categoria', '')
        if categoria == 'historia_cordoba':
            badges_nuevos.append("🏛️ Historiador Cordobés")
        elif categoria == 'matematicas':
            badges_nuevos.append("🔢 Matemático")
        elif categoria == 'geografia_cordoba':
            badges_nuevos.append("🗺️ Explorador Provincial")
    
    # Badge por excelencia académica
    correctas = trivia_stats.get('preguntas_correctas', 0)
    total = trivia_stats.get('preguntas_respondidas', 1)
    if total >= 5 and (correctas / total) >= 0.8:
        badges_nuevos.append("⭐ Excelencia Académica")
    
    return badges_nuevos
# 3. TERCERO: Cargar usuarios desde archivo externo (nunca hardcodeados en el código)
usuarios_archivo = cargar_json_seguro('usuarios.json')
if usuarios_archivo:
    USUARIOS_DOCENTES.update(usuarios_archivo)
else:
    print("[ADVERTENCIA] usuarios.json no encontrado o vacío. No hay usuarios cargados.")
    print("[ADVERTENCIA] Creá usuarios.json con el formato: {'usuario': {'password': '...', 'rol': '...'}}")
    print("[ADVERTENCIA] Roles válidos: administrador, psicopedagogo, profesor")

# 4. CUARTO: Resto de tu código (decoradores, alumnos, etc.)
def login_required(f):
    # ...tu código existente...

# ...resto de tu código...
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Debes iniciar sesión para acceder al sistema", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para roles específicos
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session:
                flash("Debes iniciar sesión para acceder al sistema", "warning")
                return redirect(url_for('login'))
            
            user_rol = session.get('rol', '')
            if user_rol not in roles:
                flash("No tienes permisos para acceder a esta sección", "error")
                return redirect(url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Obtener alumnos desde el gestor modularizado
alumnos_por_anio = obtener_alumnos_por_anio()

def get_alumnos_actuales():
    """
    ✅ FUNCIÓN AUXILIAR: Obtiene los datos actuales de alumnos
    Esta función asegura que siempre trabajemos con datos frescos del archivo
    """
    return obtener_alumnos_por_anio()

def generar_asignaciones_por_anio():
    """Genera asignaciones de 5 compañeros por alumno (sin repetir al mismo)"""
    asignaciones = {}
    for anio, alumnos in alumnos_por_anio.items():
        random.seed(42)  # Seed fija para consistencia
        asignaciones[anio] = {}
        
        for alumno in alumnos:
            otros_alumnos = [a for a in alumnos if a != alumno]
            num_opciones = min(5, len(otros_alumnos))
            
            if num_opciones > 0:
                asignaciones[anio][alumno] = random.sample(otros_alumnos, num_opciones)
            else:
                asignaciones[anio][alumno] = []
    
    return asignaciones

# Generar asignaciones
asignaciones_por_anio = generar_asignaciones_por_anio()

def calcular_disposicion_aula(num_alumnos):
    """Calcula la disposición del aula: 6 bancos por fila"""
    filas = math.ceil(num_alumnos / 6)
    return 6, filas

# RUTAS
@app.route("/")
def index():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route("/diag")
def diag():
    """Endpoint de diagnóstico - muestra estado completo del sistema"""
    import sys, traceback
    from flask import jsonify
    info = {'backend': db_manager.backend, 'errors': []}
    try:
        with db_manager._connect() as conn:
            cursor = conn.cursor()
            info['connection'] = 'OK'
            # Listar tablas
            if db_manager.backend == 'mysql':
                cursor.execute("SHOW TABLES")
                info['tables'] = [r[0] for r in cursor.fetchall()]
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                info['tables'] = [r[0] for r in cursor.fetchall()]
            # Contar filas
            info['row_counts'] = {}
            for t in info['tables']:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {t}")
                    info['row_counts'][t] = cursor.fetchone()[0]
                except Exception as e:
                    info['row_counts'][t] = f"ERROR: {e}"
            # Config aula
            try:
                info['config_aula'] = db_manager.cargar_configuracion_aula()
            except Exception as e:
                info['config_aula'] = f"ERROR: {e}"
            # Votos por año
            info['votos_por_anio'] = {}
            alumnos_act = obtener_alumnos_por_anio()
            info['anios_disponibles'] = list(alumnos_act.keys())
            info['alumnos_count'] = {k: len(v) for k, v in alumnos_act.items()}
            for anio in alumnos_act.keys():
                try:
                    votos = db_manager.obtener_votos_por_anio(anio)
                    info['votos_por_anio'][anio] = len(votos) if votos else 0
                except Exception as e:
                    info['votos_por_anio'][anio] = f"ERROR: {e}"
            # Test write
            try:
                cursor.execute(db_manager._ph(
                    "SELECT COUNT(*) FROM db_migrations WHERE migration_id = ?"
                ), ('diag_test',))
                info['test_read'] = 'OK'
            except Exception as e:
                info['test_read'] = f"ERROR: {e}"
    except Exception as e:
        info['connection'] = f"FAILED: {e}"
        info['traceback'] = traceback.format_exc()
    # Env vars (sin password)
    info['env'] = {
        'DB_HOST': os.environ.get('DB_HOST', '(not set)'),
        'DB_USER': os.environ.get('DB_USER', '(not set)'),
        'DB_NAME': os.environ.get('DB_NAME', '(not set)'),
        'DB_PASSWORD': '***' if os.environ.get('DB_PASSWORD') else '(not set)',
        'SECRET_KEY': '***' if os.environ.get('SECRET_KEY') else '(not set)',
    }
    info['usuarios_cargados'] = len(USUARIOS_DOCENTES)
    info['python_version'] = sys.version
    return jsonify(info)

@app.route("/test_votar_page/<anio>/<nombre>")
def test_votar_page(anio, nombre):
    """Renderiza votar.html SIN login, para diagnosticar problemas de template."""
    import traceback
    from urllib.parse import unquote
    nombre = unquote(nombre)
    anio = unquote(anio)
    try:
        alumnos_actuales = obtener_alumnos_por_anio()
        alumnos = alumnos_actuales.get(anio, [])
        if nombre not in alumnos:
            return f"<h1>Alumno '{nombre}' no encontrado en {anio}</h1><p>Alumnos disponibles: {alumnos[:5]}...</p>", 404
        otros = [a for a in alumnos if a != nombre]
        import random
        muestra = random.sample(otros, min(5, len(otros)))
        return render_template('votar.html', nombre=nombre, anio=anio, alumnos=muestra)
    except Exception as e:
        return f"<h1>Error rendering votar.html</h1><pre>{traceback.format_exc()}</pre>", 500

@app.route("/test_vote/<anio>")
def test_vote(anio):
    """Test completo: inserta un voto de prueba, lo lee, lo borra. Sin login."""
    from flask import jsonify
    import traceback
    result = {'anio': anio, 'steps': []}

    alumnos_act = obtener_alumnos_por_anio()
    if anio not in alumnos_act or len(alumnos_act[anio]) < 3:
        return jsonify({'error': f'Año {anio} no encontrado o sin suficientes alumnos'}), 400

    test_alumno = '__TEST_VOTE__'
    test_ratings = {alumnos_act[anio][0]: 5, alumnos_act[anio][1]: 3}
    test_ts = datetime.now().isoformat()

    # Step 1: guardar voto
    try:
        ok = db_manager.guardar_voto(anio, test_alumno, test_ratings, None, test_ts)
        result['steps'].append({'guardar_voto': ok})
    except Exception as e:
        result['steps'].append({'guardar_voto': f'EXCEPTION: {e}', 'tb': traceback.format_exc()})
        return jsonify(result), 500

    # Step 2: leer voto
    try:
        votos = db_manager.obtener_votos_por_anio(anio)
        found = test_alumno in votos
        result['steps'].append({'leer_voto': found, 'voto_data': votos.get(test_alumno, 'NOT FOUND')})
    except Exception as e:
        result['steps'].append({'leer_voto': f'EXCEPTION: {e}'})

    # Step 3: borrar voto de prueba
    try:
        with db_manager._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(db_manager._ph('DELETE FROM votos WHERE anio = ? AND alumno = ?'),
                           (anio, test_alumno))
            result['steps'].append({'borrar_voto': 'OK'})
    except Exception as e:
        result['steps'].append({'borrar_voto': f'EXCEPTION: {e}'})

    result['conclusion'] = 'DB write/read/delete OK' if all(
        s.get('guardar_voto') is True or s.get('leer_voto') is True or s.get('borrar_voto') == 'OK'
        for s in result['steps']
    ) else 'ALGO FALLO'
    return jsonify(result)

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'logged_in' in session:
        return redirect(url_for('home'))
        
    if request.method == "POST":
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        if usuario in USUARIOS_DOCENTES and USUARIOS_DOCENTES[usuario]['password'] == password:
            session['logged_in'] = True
            session['usuario'] = usuario
            session['rol'] = USUARIOS_DOCENTES[usuario]['rol']
            flash(f"¡Bienvenido/a {usuario}! ({USUARIOS_DOCENTES[usuario]['rol'].title()})", "success")
            return redirect(url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos", "error")
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    usuario = session.get('usuario', 'Usuario')
    session.clear()
    flash(f"¡Hasta luego {usuario}! Sesión cerrada exitosamente", "info")
    return redirect(url_for('login'))

@app.route("/home")
@login_required
def home():
    anio = request.args.get('anio', '')
    
    # ✅ CORREGIDO: Usar función que lee archivo actual
    alumnos_actuales = obtener_alumnos_por_anio()
    alumnos = alumnos_actuales.get(anio, [])
    
    # Obtener votos desde la base de datos
    votos_bd = db_manager.obtener_votos_por_anio(anio) if anio else {}
    ya_votaron = set(votos_bd.keys())
    
    return render_template("home.html", 
                         alumnos=alumnos, 
                         ya_votaron=ya_votaron, 
                         anio=anio, 
                         alumnos_por_anio=alumnos_actuales,  # ✅ También corregido aquí
                         usuario=session.get('usuario'),
                         rol=session.get('rol'))

@app.route('/votar/<anio>/<nombre>', methods=['GET', 'POST'])
@login_required
def votar(anio, nombre):
    import sys, traceback
    from urllib.parse import unquote
    nombre = unquote(nombre)
    anio = unquote(anio)
    print(f"[VOTAR] {request.method} anio={anio} nombre={nombre}", flush=True)
    try:
        return _votar_inner(anio, nombre)
    except Exception as e:
        print(f"[VOTAR] CRASH: {e}", flush=True)
        traceback.print_exc()
        # En vez de 500, mostrar el error
        return f"<h1>Error en /votar</h1><pre>{traceback.format_exc()}</pre>", 500

def _votar_inner(anio, nombre):
    # ✅ CORREGIDO: Usar función que lee archivo actual
    alumnos_actuales = obtener_alumnos_por_anio()
    alumnos = alumnos_actuales.get(anio, [])
    
    if nombre not in alumnos:
        # DEBUG: mostrar exactamente qué nombre llegó vs lista
        from urllib.parse import unquote, unquote_plus
        repr_nombre = repr(nombre)
        repr_lista = repr(alumnos[:3])
        double_unquoted = unquote(unquote(nombre))
        plus_unquoted = unquote_plus(nombre)
        raw_path = request.environ.get('PATH_INFO', 'N/A')
        return (
            f"<h2>DEBUG: Alumno no encontrado</h2>"
            f"<p><b>nombre recibido (repr):</b> {repr_nombre}</p>"
            f"<p><b>len:</b> {len(nombre)}</p>"
            f"<p><b>double unquote:</b> {repr(double_unquoted)}</p>"
            f"<p><b>unquote_plus:</b> {repr(plus_unquoted)}</p>"
            f"<p><b>PATH_INFO raw:</b> {raw_path}</p>"
            f"<p><b>primeros 3 de lista:</b> {repr_lista}</p>"
            f"<p><b>bytes nombre:</b> {nombre.encode('utf-8').hex()}</p>"
            f"<p><b>bytes lista[0]:</b> {alumnos[0].encode('utf-8').hex() if alumnos else 'vacia'}</p>"
        ), 200
    
    # Cargar votos existentes desde la base de datos
    votos_bd = db_manager.obtener_votos_por_anio(anio)
    
    if request.method == 'GET':
        # Verificar si ya votó
        if nombre in votos_bd:
            flash('Ya has completado tu votación', 'info')
            return redirect(url_for('home', anio=anio))
        
        # ✅ VERIFICAR si la trivia es obligatoria antes de mostrarla
        config_aula = db_manager.cargar_configuracion_aula()
        trivia_obligatoria = config_aula.get('trivia_obligatoria', False)
        
        if trivia_obligatoria and not session.get(f'trivia_completada_{anio}_{nombre}', False):
            return redirect(url_for('trivia_educativa', anio=anio, nombre=nombre))
        
        # Obtener otros alumnos (excluir al que está votando)
        otros_alumnos = [a for a in alumnos if a != nombre]
        
        # Seleccionar aleatoriamente 5 compañeros para evaluar
        import random
        random.seed()  # Asegurar aleatoriedad
        alumnos_a_evaluar = random.sample(otros_alumnos, min(5, len(otros_alumnos)))
        
        # Guardar la selección en la sesión para mantener consistencia
        session[f'alumnos_evaluar_{anio}_{nombre}'] = alumnos_a_evaluar
        
        return render_template('votar.html', 
                             nombre=nombre, 
                             anio=anio, 
                             alumnos=alumnos_a_evaluar)
    
    # POST - procesar votación
    import sys, traceback
    print(f"[VOTAR POST] anio={anio}, nombre={nombre}", flush=True)
    print(f"[VOTAR POST] form keys: {list(request.form.keys())}", flush=True)

    alumnos_a_evaluar = session.get(f'alumnos_evaluar_{anio}_{nombre}', [])
    print(f"[VOTAR POST] session alumnos_a_evaluar: {alumnos_a_evaluar}", flush=True)

    # Fallback: si la sesión no persistió, reconstruir la lista desde el formulario
    if not alumnos_a_evaluar:
        alumnos_a_evaluar = [
            key.replace('rating_', '', 1)
            for key in request.form.keys()
            if key.startswith('rating_') and request.form[key]
        ]
        print(f"[VOTAR POST] fallback alumnos_a_evaluar: {alumnos_a_evaluar}", flush=True)

    if not alumnos_a_evaluar:
        print(f"[VOTAR POST] ERROR: lista vacia, redirigiendo", flush=True)
        flash('Error en la sesión. Intenta nuevamente.', 'error')
        return redirect(url_for('votar', anio=anio, nombre=nombre))

    # Recoger ratings
    ratings = {}
    for alumno in alumnos_a_evaluar:
        rating_key = f'rating_{alumno}'
        if rating_key in request.form and request.form[rating_key]:
            try:
                rating_value = int(request.form[rating_key])
                if 1 <= rating_value <= 5:
                    ratings[alumno] = rating_value
                else:
                    flash(f'Rating inválido para {alumno}', 'error')
                    return redirect(url_for('votar', anio=anio, nombre=nombre))
            except ValueError:
                flash(f'Rating no válido para {alumno}', 'error')
                return redirect(url_for('votar', anio=anio, nombre=nombre))

    # Validaciones
    if len(ratings) != len(alumnos_a_evaluar):
        flash('Debes evaluar a todos los compañeros asignados', 'error')
        return redirect(url_for('votar', anio=anio, nombre=nombre))

    # Verificar que no todos tengan rating 1
    if all(rating == 1 for rating in ratings.values()):
        flash('No puedes calificar a todos con la puntuación mínima', 'error')
        return redirect(url_for('votar', anio=anio, nombre=nombre))

    # Procesar bloqueo (opcional)
    bloqueado = None
    if 'bloqueado' in request.form:
        bloqueados = request.form.getlist('bloqueado')
        if bloqueados:
            bloqueado = bloqueados[0] if bloqueados[0] in alumnos_a_evaluar else None

    # Guardar votación
    from datetime import datetime
    voto_data = {
        'ratings': ratings,
        'bloqueado': bloqueado,
        'alumnos_evaluados': alumnos_a_evaluar,
        'fecha': datetime.now().isoformat(),
        'ip': request.remote_addr
    }

    # ✅ GAMIFICACIÓN: Calcular puntos
    puntos_obtenidos = calcular_puntos_gamificacion(voto_data)
    voto_data['puntos_obtenidos'] = puntos_obtenidos
    
    # 🔥 CORREGIDO: GUARDAR EL VOTO EN LA BASE DE DATOS
    print(f"[VOTAR POST] guardando voto: ratings={ratings}, bloqueado={bloqueado}", flush=True)
    try:
        exito_guardado = db_manager.guardar_voto(
            anio=anio,
            alumno=nombre,
            calificaciones=ratings,
            alumno_bloqueado=bloqueado,
            timestamp=voto_data['fecha']
        )
        print(f"[VOTAR POST] guardar_voto resultado: {exito_guardado}", flush=True)
    except Exception as e:
        print(f"[VOTAR POST] EXCEPTION en guardar_voto: {e}", flush=True)
        traceback.print_exc()
        exito_guardado = False
    
    if not exito_guardado:
        flash('❌ Error al guardar el voto en la base de datos', 'error')
        return redirect(url_for('votar', anio=anio, nombre=nombre))
    
    # Obtener datos de trivia de la sesión
    datos_trivia = session.get(f'resultado_trivia_{anio}_{nombre}')
    
    # ✅ GAMIFICACIÓN: Actualizar ranking con trivia
    try:
        alumno_stats = actualizar_ranking_clase(anio, nombre, puntos_obtenidos, datos_trivia)
        badges_nuevos = otorgar_badges_trivia(alumno_stats, datos_trivia)
    except Exception as e:
        print(f"[VOTAR POST] EXCEPTION en gamificacion: {e}", flush=True)
        traceback.print_exc()
        alumno_stats = {'nivel': 1}
        badges_nuevos = []
    
    # Limpiar la sesión
    session.pop(f'alumnos_evaluar_{anio}_{nombre}', None)
    session.pop(f'trivia_completada_{anio}_{nombre}', None)
    session.pop(f'resultado_trivia_{anio}_{nombre}', None)
    
    # ✅ GAMIFICACIÓN: Flash message mejorado
    mensaje_puntos = f'¡Votación registrada! 🎉 Ganaste {puntos_obtenidos} puntos.'
    if datos_trivia and datos_trivia.get('correcta'):
        mensaje_puntos += f' 🧠 ¡Trivia correcta: +{datos_trivia.get("puntos_pregunta", 0)} puntos!'
    mensaje_puntos += f' Nivel actual: {alumno_stats["nivel"]}'
    
    flash(mensaje_puntos, 'success')
    
    if badges_nuevos:
        flash(f'¡Nuevos logros: {", ".join(badges_nuevos)}! 🏆', 'info')
    
    return redirect(url_for('home', anio=anio))

@app.route('/trivia_educativa/<anio>/<nombre>', methods=['GET', 'POST'])
@login_required
def trivia_educativa(anio, nombre):
    """Trivia educativa antes de votar"""
    from urllib.parse import unquote
    nombre = unquote(nombre)
    anio = unquote(anio)
    # ✅ CORREGIDO: Usar función que lee archivo actual
    alumnos_actuales = obtener_alumnos_por_anio()
    alumnos = alumnos_actuales.get(anio, [])
    
    if nombre not in alumnos:
        flash('Alumno no encontrado', 'error')
        return redirect(url_for('home', anio=anio))
    
    if request.method == 'GET':
        # Generar pregunta aleatoria
        pregunta = obtener_pregunta_aleatoria()
        pregunta_id = hash(pregunta['pregunta']) % 10000  # ID único para la pregunta
        
        # Guardar pregunta en sesión
        session[f'pregunta_actual_{anio}_{nombre}'] = {
            'pregunta': pregunta,
            'pregunta_id': pregunta_id,
            'inicio_tiempo': datetime.now().isoformat()
        }
        
        return render_template('trivia.html', 
                             nombre=nombre, 
                             anio=anio, 
                             pregunta=pregunta,
                             pregunta_id=pregunta_id)
    
    # POST - procesar respuesta de trivia
    pregunta_data = session.get(f'pregunta_actual_{anio}_{nombre}')
    if not pregunta_data:
        flash('Error en la sesión de trivia', 'error')
        return redirect(url_for('trivia_educativa', anio=anio, nombre=nombre))
    
    pregunta = pregunta_data['pregunta']
    respuesta_alumno = request.form.get('respuesta')
    
    # Evaluar respuesta
    es_correcta = False
    puntos_ganados = 0
    
    if respuesta_alumno is not None:
        respuesta_int = int(respuesta_alumno)
        es_correcta = respuesta_int == pregunta['respuesta_correcta']
        
        if es_correcta:
            puntos_ganados = pregunta['puntos']
        else:
            puntos_ganados = 2  # Puntos de consolación
    
    # Guardar resultado en sesión
    resultado_trivia = {
        'correcta': es_correcta,
        'puntos_pregunta': pregunta['puntos'],
        'puntos_ganados': puntos_ganados,
        'categoria': pregunta.get('categoria', ''),
        'pregunta_texto': pregunta['pregunta'],
        'respuesta_correcta': pregunta['opciones'][pregunta['respuesta_correcta']]
    }
    
    session[f'resultado_trivia_{anio}_{nombre}'] = resultado_trivia
    session[f'trivia_completada_{anio}_{nombre}'] = True
    
    # Limpiar pregunta actual
    session.pop(f'pregunta_actual_{anio}_{nombre}', None)
    
    # Mostrar resultado y continuar
    flash(f'{"¡Correcto!" if es_correcta else "Incorrecto"} Ganaste {puntos_ganados} puntos.', 
          'success' if es_correcta else 'warning')
    
    return redirect(url_for('votar', anio=anio, nombre=nombre))

@app.route("/procesar_voto", methods=["POST"])
@login_required
def procesar_voto():
    nombre = request.form.get('nombre')
    anio = request.form.get('anio')
    
    try:
        # ✅ CORREGIDO: Usar datos actuales
        alumnos_actuales = get_alumnos_actuales()
        if not anio or anio not in alumnos_actuales:
            flash("Año no válido", "error")
            return redirect(url_for('home'))
        
        asignaciones = asignaciones_por_anio.get(anio, {})
        opciones = asignaciones.get(nombre, [])
        
        if not opciones:
            flash("No se encontraron opciones para este alumno", "error")
            return redirect(url_for('home', anio=anio))
        
        # Verificar si ya votó (desde base de datos)
        votos_bd = db_manager.obtener_votos_por_anio(anio)
        
        if nombre in votos_bd:
            flash(f"{nombre} ya ha votado", "warning")
            return redirect(url_for('home', anio=anio))
        
        calificaciones = {}
        alumno_bloqueado = request.form.get('bloquear', '')
        
        # Recoger calificaciones
        for compañero in opciones:
            calificacion = request.form.get(compañero, '')
            if calificacion:
                calificaciones[compañero] = int(calificacion)
            else:
                flash(f"Falta calificación para {compañero}", "error")
                return redirect(url_for('votar', nombre=nombre, anio=anio))
        
        # Validación de calificaciones
        if len(calificaciones) != len(opciones):
            flash("Debes calificar a todos tus compañeros", "error")
            return redirect(url_for('votar', nombre=nombre, anio=anio))
        
        valores = list(calificaciones.values())
        valores_esperados = list(range(1, len(opciones) + 1))
        
        if sorted(valores) != valores_esperados:
            flash(f"Debes asignar cada puntaje del 1 al {len(opciones)} una sola vez", "error")
            return redirect(url_for('votar', nombre=nombre, anio=anio))
        
        # Validación de bloqueo
        if alumno_bloqueado and alumno_bloqueado not in opciones:
            flash("Solo puedes bloquear a uno de los compañeros que calificaste", "error")
            return redirect(url_for('votar', nombre=nombre, anio=anio))
        
        # Guardar voto usando base de datos
        timestamp_actual = datetime.now().isoformat()
        
        # Guardar en base de datos
        db_success = db_manager.guardar_voto(
            anio=anio,
            alumno=nombre, 
            calificaciones=calificaciones,
            alumno_bloqueado=alumno_bloqueado,
            timestamp=timestamp_actual
        )
        
        if db_success:
            flash(f"✅ Voto de {nombre} registrado exitosamente!", "success")
        else:
            flash("❌ Error al guardar el voto", "error")
            
        return redirect(url_for("home", anio=anio))
        
    except Exception as e:
        print(f"Error en procesar_voto: {e}")
        flash("Error al procesar el voto", "error")
        return redirect(url_for('home', anio=anio))

@app.route("/resultados")
@login_required  
def resultados():
    anio = request.args.get('anio', '')
    
    # ✅ CORREGIDO: Usar datos actuales
    alumnos_actuales = get_alumnos_actuales()
    if not anio or anio not in alumnos_actuales:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    # Cargar votos desde base de datos
    votos = db_manager.obtener_votos_por_anio(anio)
    
    if not votos:
        flash("No hay votos registrados para mostrar resultados", "warning")
        return redirect(url_for('home', anio=anio))
    
    # ✅ CORREGIDO: Usar datos actuales
    emparejamientos = generar_emparejamientos(votos, alumnos_actuales[anio])
    
    # ✅ AGREGAR: Generar pares para bancos
    pares_para_bancos = []
    alumnos_solos = []
    
    for grupo in emparejamientos:
        if len(grupo) == 1:
            alumnos_solos.extend(grupo)
        elif len(grupo) == 2:
            pares_para_bancos.append(grupo)
        elif len(grupo) >= 3:
            # Dividir grupos grandes en pares
            for i in range(0, len(grupo)-1, 2):
                if i+1 < len(grupo):
                    pares_para_bancos.append([grupo[i], grupo[i+1]])
                else:
                    alumnos_solos.append(grupo[i])
    
    # Emparejar alumnos solos
    while len(alumnos_solos) >= 2:
        par = [alumnos_solos.pop(0), alumnos_solos.pop(0)]
        pares_para_bancos.append(par)
    
    # Si queda uno solo, crear un "banco" individual
    if alumnos_solos:
        pares_para_bancos.append(alumnos_solos)
    
    return render_template("resultados.html",
                         emparejamientos=emparejamientos,
                         pares_bancos=pares_para_bancos,  # ✅ NUEVO
                         anio=anio)

@app.route("/asignacion_bancos")
@login_required
def asignacion_bancos():
    anio = request.args.get('anio', '')
    regenerar = request.args.get('regenerar', 'false') == 'true'
    cargar_guardado = request.args.get('cargar', 'false') == 'true'
    
    if not anio or anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    # Si se solicita cargar guardado
    if cargar_guardado:
        # Cargar desde base de datos
        bancos_data = db_manager.cargar_asignacion_bancos(anio)
        
        if bancos_data and 'asignacion' in bancos_data:
            asignacion = bancos_data['asignacion']
            total_alumnos = bancos_data.get('total_alumnos', 0)
            filas = bancos_data.get('configuracion', {}).get('filas', math.ceil(total_alumnos / 6))
            
            flash(f"Asignación cargada exitosamente", "info")
            
            return render_template("asignacion_bancos.html", 
                                 aula=asignacion,
                                 grupos=[],
                                 anio=anio,
                                 cols=3,  # ✅ 3 columnas
                                 filas=filas,
                                 total_alumnos=total_alumnos,
                                 guardado_disponible=True)
    
    # Cargar votos desde la base de datos y generar emparejamientos
    votos = db_manager.obtener_votos_por_anio(anio)
    
    if not votos:
        flash("No hay votos registrados para generar asignación de bancos", "warning")
        return redirect(url_for('home', anio=anio))
    
    # ✅ USAR emparejamientos YA generados por el algoritmo
    emparejamientos = generar_emparejamientos(votos, alumnos_por_anio[anio])
    
    if not emparejamientos:
        flash("No se pudieron generar emparejamientos", "warning")
        return redirect(url_for('home', anio=anio))
    
    # ✅ CONVERTIR grupos en PARES para los bancos
    pares_para_bancos = []
    alumnos_solos = []
    
    for grupo in emparejamientos:
        if len(grupo) == 1:
            alumnos_solos.append(grupo[0])
        elif len(grupo) == 2:
            pares_para_bancos.append(grupo)
        elif len(grupo) >= 3:
            # Dividir grupos grandes en pares
            for i in range(0, len(grupo)-1, 2):
                if i+1 < len(grupo):
                    pares_para_bancos.append([grupo[i], grupo[i+1]])
                else:
                    alumnos_solos.append(grupo[i])
    
    # ✅ EMPAREJAR alumnos solos entre sí
    while len(alumnos_solos) >= 2:
        par = [alumnos_solos.pop(0), alumnos_solos.pop(0)]
        pares_para_bancos.append(par)
    
    # Si queda uno solo, agregarlo a un par existente (máximo 3 por banco)
    if alumnos_solos and pares_para_bancos:
        pares_para_bancos[-1].append(alumnos_solos[0])
        alumnos_solos = []
    elif alumnos_solos:
        # Crear un "par" de una sola persona
        pares_para_bancos.append(alumnos_solos)
        alumnos_solos = []
    
    total_bancos = len(pares_para_bancos)
    
    # ✅ CONFIGURACIÓN del aula: 3 COLUMNAS, distribución automática de filas
    cols = 3  # 3 columnas (izquierda - pasillo - centro - pasillo - derecha)
    filas = math.ceil(total_bancos / cols)
    
    # ✅ CREAR matriz del aula con layout específico
    aula = []
    banco_index = 0
    
    for fila in range(filas):
        for col in range(cols):
            banco_numero = fila * cols + col + 1;
            
            if banco_index < len(pares_para_bancos):
                par = pares_para_bancos[banco_index]
                
                # Determinar a qué grupo original pertenecen
                grupo_numero = 0
                for i, grupo_original in enumerate(emparejamientos, 1):
                    if any(alumno in grupo_original for alumno in par):
                        grupo_numero = i
                        break
                
                aula.append({
                    'fila': fila + 1,
                    'columna': col + 1,
                    'numero': banco_numero,
                    'alumnos': par,  # ✅ Lista de alumnos en el banco
                    'grupo': grupo_numero,
                    'ocupado': True,
                    'cantidad': len(par),
                    'posicion': ['Izquierda', 'Centro', 'Derecha'][col]
                })
                banco_index += 1
            else:
                # Banco vacío
                aula.append({
                    'fila': fila + 1,
                    'columna': col + 1,
                    'numero': banco_numero,
                    'alumnos': [],
                    'grupo': 0,
                    'ocupado': False,
                    'cantidad': 0,
                    'posicion': ['Izquierda', 'Centro', 'Derecha'][col]
                })
    
    # Verificar si hay asignación guardada en la base de datos
    asignaciones_guardadas = db_manager.listar_asignaciones_bancos(anio)
    guardado_disponible = len(asignaciones_guardadas) > 0
    
    return render_template("asignacion_bancos.html", 
                         aula=aula,
                         grupos=emparejamientos,  # Grupos originales para referencia
                         pares=pares_para_bancos,  # Pares específicos para bancos
                         anio=anio,
                         cols=cols,
                         filas=filas,
                         total_alumnos=sum(len(par) for par in pares_para_bancos),
                         total_bancos=total_bancos,
                         guardado_disponible=guardado_disponible)

@app.route("/cargar_bancos/<anio>")
@role_required('administrador', 'psicopedagogo')
def cargar_bancos(anio):
    """Carga una asignación de bancos guardada"""
    return redirect(url_for('asignacion_bancos', anio=anio, cargar='true'))

@app.route("/guardar_bancos", methods=["POST"])
@role_required('administrador', 'psicopedagogo')
def guardar_bancos():
    """Guarda la asignación actual de bancos con nombre personalizado"""
    anio = request.form.get('anio', '')
    asignacion_data = request.form.get('asignacion_data', '')
    nombre_asignacion = request.form.get('nombre_asignacion', f"Asignación_{datetime.now().strftime('%Y%m%d_%H%M')}")
    
    if not anio or not asignacion_data:
        flash("Datos incompletos para guardar", "error")
        return redirect(url_for('home'))
    
    try:
        import json
        asignacion = json.loads(asignacion_data)
        
        # Calcular datos de la asignación
        total_alumnos = len([banco for banco in asignacion if banco.get('ocupado')])
        filas = max(banco.get('fila', 1) for banco in asignacion)
        columnas = 6
        
        # Guardar en base de datos
        db_success = db_manager.guardar_asignacion_bancos(
            anio=anio,
            nombre_asignacion=nombre_asignacion,
            asignacion_data=asignacion,
            total_alumnos=total_alumnos,
            filas=filas,
            columnas=columnas,
            es_actual=True
        )
        
        if db_success:
            flash(f"✅ Asignación '{nombre_asignacion}' guardada exitosamente", "success")
        else:
            flash("❌ Error al guardar la asignación en la base de datos", "error")
            
    except Exception as e:
        print(f"Error guardando bancos: {e}")
        flash("❌ Error al procesar los datos", "error")
    
    return redirect(url_for('asignacion_bancos', anio=anio))

@app.route("/listar_asignaciones/<anio>")
@role_required('administrador', 'psicopedagogo')
def listar_asignaciones(anio):
    """Lista todas las asignaciones guardadas para un año"""
    try:
        asignaciones = db_manager.listar_asignaciones_bancos(anio)
        return {
            'success': True,
            'asignaciones': asignaciones
        }
    except Exception as e:
        print(f"Error listando asignaciones: {e}")
        return {
            'success': False,
            'error': 'Error al cargar asignaciones'
        }

@app.route("/cargar_asignacion", methods=['POST'])
@role_required('administrador', 'psicopedagogo')
def cargar_asignacion():
    """Carga una asignación específica"""
    anio = request.form.get('anio', '')
    nombre_asignacion = request.form.get('nombre_asignacion', '')
    
    if not anio or not nombre_asignacion:
        flash("Datos incompletos para cargar asignación", "error")
        return redirect(url_for('home'))
    
    try:
        # Cargar desde base de datos
        asignacion_data = db_manager.cargar_asignacion_bancos(anio, nombre_asignacion)
        
        if not asignacion_data:
            flash(f"No se encontró la asignación '{nombre_asignacion}'", "error")
            return redirect(url_for('asignacion_bancos', anio=anio))
        
        # Marcar como actual en base de datos
        db_manager.guardar_asignacion_bancos(
            anio=anio,
            nombre_asignacion=nombre_asignacion,
            asignacion_data=asignacion_data['asignacion'],
            total_alumnos=asignacion_data['total_alumnos'],
            filas=asignacion_data['configuracion']['filas'],
            columnas=asignacion_data['configuracion']['columnas'],
            es_actual=True
        )
        
        # También actualizar archivo JSON como respaldo
        bancos_archivo = f"bancos_{anio}.json"
        guardar_json_seguro(bancos_archivo, asignacion_data)
        
        flash(f"✅ Asignación '{nombre_asignacion}' cargada exitosamente", "success")
        
    except Exception as e:
        print(f"Error cargando asignación: {e}")
        flash("❌ Error al cargar la asignación", "error")
    
    return redirect(url_for('asignacion_bancos', anio=anio))

@app.route("/auto_guardar_tras_votacion", methods=['POST'])
@role_required('administrador', 'psicopedagogo')
def auto_guardar_tras_votacion():
    """Guarda automáticamente la asignación después de completar votaciones"""
    anio = request.form.get('anio', '')
    
    if not anio:
        return {'success': False, 'error': 'Año no especificado'}
    
    try:
        # Verificar que haya votos suficientes desde la base de datos
        votos = db_manager.obtener_votos_por_anio(anio)
        
        if len(votos) < 2:  # Mínimo 2 votos para generar asignación
            return {'success': False, 'error': 'Votos insuficientes'}
        
        # Generar asignación automática
        emparejamientos = generar_emparejamientos(votos, alumnos_por_anio[anio])
        
        # Crear configuración básica de bancos
        config_actual = db_manager.cargar_configuracion_aula()
        filas = config_actual.get('filas', 6)
        columnas = config_actual.get('columnas', 6)
        
        # Simular asignación básica (esto se puede mejorar con lógica específica)
        asignacion = []
        for fila in range(1, filas + 1):
            for col in range(1, columnas + 1):
                asignacion.append({
                    'fila': fila,
                    'columna': col,
                    'ocupado': False,
                    'alumno': None
                })
        
        # Asignar alumnos según emparejamientos
        banco_index = 0
        for pareja in emparejamientos:
            if banco_index < len(asignacion) - 1:  # Asegurar que hay espacio
                asignacion[banco_index].update({
                    'ocupado': True,
                    'alumno': pareja[0]
                })
                asignacion[banco_index + 1].update({
                    'ocupado': True,
                    'alumno': pareja[1]
                })
                banco_index += 2
        
        # Guardar con nombre automático
        nombre_auto = f"Auto_Post_Votacion_{datetime.now().strftime('%Y%m%d_%H%M')}"
        total_alumnos = len([b for b in asignacion if b.get('ocupado')])
        
        success = db_manager.guardar_asignacion_bancos(
            anio=anio,
            nombre_asignacion=nombre_auto,
            asignacion_data=asignacion,
            total_alumnos=total_alumnos,
            filas=filas,
            columnas=columnas,
            es_actual=True
        )
        
        if success:
            return {'success': True, 'nombre': nombre_auto}
        else:
            return {'success': False, 'error': 'Error al guardar'}
            
    except Exception as e:
        print(f"Error en auto-guardado: {e}")
        return {'success': False, 'error': str(e)}

@app.route("/exportar_bancos/<anio>")
@role_required('administrador', 'psicopedagogo')
def exportar_bancos(anio):
    """Exporta la asignación de bancos a Excel desde la base de datos"""
    # Obtener la asignación actual desde la base de datos
    bancos_data = db_manager.cargar_asignacion_bancos(anio)
    
    if not bancos_data or 'asignacion' not in bancos_data:
        flash("No hay asignación de bancos para exportar", "warning")
        return redirect(url_for('asignacion_bancos', anio=anio))
    
    try:
        try:
            import pandas as pd
        except ImportError:
            flash("❌ Funcionalidad de exportación no disponible (pandas no instalado)", "error")
            return redirect(url_for('asignacion_bancos', anio=anio))
        
        # Preparar datos para Excel
        asignacion = bancos_data['asignacion']
        datos_excel = []
        
        for banco in asignacion:
            datos_excel.append({
                'Fila': banco.get('fila', ''),
                'Columna': banco.get('columna', ''),
                'Numero_Banco': banco.get('numero', ''),
                'Alumno': banco.get('alumno', ''),
                'Grupo': banco.get('grupo', ''),
                'Ocupado': 'Sí' if banco.get('ocupado') else 'No'
            })
        
        # Crear DataFrame
        df = pd.DataFrame(datos_excel)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nombre_archivo = f"bancos_{anio}_{timestamp}.xlsx"
        
        # Guardar Excel
        df.to_excel(nombre_archivo, index=False, engine='openpyxl')
        
        flash(f"✅ Asignación exportada a {nombre_archivo}", "success")
        
        # Devolver archivo para descarga
        from flask import send_file
        return send_file(nombre_archivo, as_attachment=True)
        
    except Exception as e:
        print(f"Error exportando bancos: {e}")
        flash("❌ Error al exportar la asignación", "error")
        return redirect(url_for('asignacion_bancos', anio=anio))

@app.route("/historial_bancos/<anio>")
@role_required('administrador', 'psicopedagogo')
def historial_bancos(anio):
    """Muestra el historial de asignaciones de bancos desde la base de datos"""
    if anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    # Obtener historial desde la base de datos
    historial_bd = db_manager.listar_asignaciones_bancos(anio)
    
    historial = []
    for asignacion in historial_bd:
        historial.append({
            'id': asignacion.get('id'),
            'nombre': asignacion.get('nombre_asignacion', 'Sin nombre'),
            'fecha': asignacion.get('fecha_creacion', 'N/A'),
            'total_alumnos': asignacion.get('total_alumnos', 0),
            'filas': asignacion.get('filas', 'N/A'),
            'columnas': asignacion.get('columnas', 'N/A'),
            'es_actual': asignacion.get('es_actual', False)
        })
    
    # Ya viene ordenado por fecha desde la BD (más reciente primero)
    
    return render_template("historial_bancos.html",
                         anio=anio,
                         historial=historial)

@app.route("/configuracion_aula", methods=["GET", "POST"])
@role_required('administrador')
def configuracion_aula():
    """Configuración avanzada del aula"""
    if request.method == "POST":
        # Guardar configuración personalizada
        config = {
            'filas_maximas': int(request.form.get('filas', 6)),
            'columnas_por_fila': int(request.form.get('columnas', 6)),
            'espacios_libres': request.form.getlist('espacios_libres'),
            'configuracion_especial': request.form.get('especial', False),
            'trivia_obligatoria': request.form.get('trivia_obligatoria') == 'on',
            'fecha_modificacion': datetime.now().isoformat(),
            'usuario_modificacion': session.get('usuario')
        }
        
        # Guardar en base de datos
        db_manager.guardar_configuracion_aula(config)
        flash("Configuración del aula guardada exitosamente", "success")
        return redirect(url_for('configuracion_aula'))
    
    # Cargar configuración actual de la base de datos
    config_actual = db_manager.cargar_configuracion_aula()
    
    return render_template("configuracion_aula.html",
                         config=config_actual)

@app.route("/estadisticas/<anio>")
@role_required('administrador', 'psicopedagogo')
def estadisticas(anio):
    """Muestra estadísticas detalladas de votación desde la base de datos"""
    from collections import Counter, defaultdict
    import statistics
    
    if anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    # Cargar votos desde la base de datos
    votos = db_manager.obtener_votos_por_anio(anio)
    
    if not votos:
        flash("No hay votos registrados para este año", "warning")
        return redirect(url_for('home', anio=anio))
    
    # Calcular estadísticas básicas
    total_votantes = len(votos)
    total_ratings = 0
    total_bloqueos = 0
    distribución_ratings = Counter()
    
    # Análisis de popularidad
    puntuaciones_recibidas = defaultdict(list)
    bloqueos_recibidos = Counter()
    bloqueos_mutuos = []
    
    for votante, datos in votos.items():
        # En BD: 'calificaciones' en lugar de 'ratings'
        ratings = datos.get('calificaciones', {})
        # En BD: 'alumno_bloqueado' en lugar de 'bloqueado'
        bloqueado = datos.get('alumno_bloqueado')
        
        total_ratings += len(ratings)
        if bloqueado:
            total_bloqueos += 1
            bloqueos_recibidos[bloqueado] += 1
        
        for evaluado, puntuacion in ratings.items():
            distribución_ratings[puntuacion] += 1
            puntuaciones_recibidas[evaluado].append(puntuacion)
    
    # Detectar bloqueos mutuos
    for votante, datos in votos.items():
        bloqueado = datos.get('alumno_bloqueado')
        if bloqueado and bloqueado in votos:
            datos_bloqueado = votos[bloqueado]
            if datos_bloqueado.get('alumno_bloqueado') == votante:
                par_bloqueado = tuple(sorted([votante, bloqueado]))
                if par_bloqueado not in bloqueos_mutuos:
                    bloqueos_mutuos.append(par_bloqueado)
    
    # Calcular estadísticas por alumno
    stats_alumnos = {}
    for alumno, puntuaciones in puntuaciones_recibidas.items():  # ✅ CORREGIDO
        if puntuaciones:
            import statistics
            stats_alumnos[alumno] = {
                'promedio': statistics.mean(puntuaciones),
                'total_votos': len(puntuaciones),
                'suma_total': sum(puntuaciones),
                'puntuacion_maxima': max(puntuaciones),
                'puntuacion_minima': min(puntuaciones),
                'desviacion': statistics.stdev(puntuaciones) if len(puntuaciones) > 1 else 0
            }
    
    # Ordenar por popularidad
    alumnos_populares = sorted(
        stats_alumnos.items(),
        key=lambda x: (x[1]['promedio'], x[1]['total_votos']),
        reverse=True
    )
    
    # Análisis de afinidad mutua
    afinidades_mutuas = []
    for votante, datos in votos.items():
        ratings = datos.get('ratings', {})
        for evaluado, puntuacion1 in ratings.items():
            if evaluado in votos:
                datos_evaluado = votos[evaluado]
                ratings_evaluado = datos_evaluado.get('ratings', {})
                if votante in ratings_evaluado:
                    puntuacion2 = ratings_evaluado[votante]
                    
                    par = tuple(sorted([votante, evaluado]))
                    if not any(a['par'] == par for a in afinidades_mutuas):
                        afinidades_mutuas.append({
                            'par': par,
                            'alumno1': votante,
                            'alumno2': evaluado,
                            'puntuacion1': puntuacion1,
                            'puntuacion2': puntuacion2,
                            'promedio': (puntuacion1 + puntuacion2) / 2
                        })
    
    # Ordenar afinidades
    mejores_afinidades = sorted(
        afinidades_mutuas,
        key=lambda x: x['promedio'],
        reverse=True
    )
    
    # Preparar datos para el template
    estadisticas_data = {
        'anio': anio,
        'total_votantes': total_votantes,
        'total_ratings': total_ratings,
        'total_bloqueos': total_bloqueos,
        'promedio_ratings_por_persona': total_ratings / total_votantes if total_votantes > 0 else 0,
        'distribución_ratings': dict(distribución_ratings),
        'alumnos_populares': alumnos_populares[:10],
        'alumnos_menos_populares': alumnos_populares[-5:] if len(alumnos_populares) >= 5 else [],
        'alumnos_mas_bloqueados': bloqueos_recibidos.most_common(10),
        'bloqueos_mutuos': bloqueos_mutuos,
        'mejores_afinidades': mejores_afinidades[:10],
        'participacion': round((total_votantes / len(alumnos_por_anio[anio])) * 100, 1) if anio in alumnos_por_anio else 0
    };
    
    return render_template("estadisticas.html", **estadisticas_data)
# Agrega esta ruta antes del if __name__ == "__main__":

# O usa esta versión que funciona 100% en Render:

@app.route("/reset_votos_render", methods=["POST"])
@role_required('administrador')
def reset_votos_render():
    """Reset completo - Archivos JSON Y base de datos"""
    anio = request.form.get('anio', '')
    
    if not anio or anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    try:
        from datetime import datetime
        import os
        
        # 1. RESETEAR BASE DE DATOS (Principal)
        try:
            # Borrar votos
            exito_votos, votos_borrados = db_manager.borrar_votos_anio(anio)
            
            # Borrar rankings  
            exito_rankings, rankings_borrados = db_manager.borrar_rankings_anio(anio)
            
            # Borrar asignaciones de bancos
            exito_bancos, bancos_borrados = db_manager.borrar_asignaciones_bancos_anio(anio)
            
            # Resultados del reset
            if exito_votos and exito_rankings and exito_bancos:
                flash(f"✅ Base de datos: {votos_borrados} votos, {rankings_borrados} rankings y {bancos_borrados} asignaciones eliminados", "success")
            else:
                # Reporte detallado de qué funcionó y qué no
                mensajes = []
                if exito_votos:
                    mensajes.append(f"{votos_borrados} votos")
                if exito_rankings:
                    mensajes.append(f"{rankings_borrados} rankings")  
                if exito_bancos:
                    mensajes.append(f"{bancos_borrados} asignaciones")
                
                if mensajes:
                    flash(f"⚠️ Reset parcial: {', '.join(mensajes)} eliminados", "warning")
                else:
                    flash(f"❌ Error al borrar datos de la base de datos", "error")
        except Exception as e:
            print(f"❌ Error en borrado DB: {e}")
            flash(f"⚠️ Error en base de datos: {str(e)}", "warning")
        
        # 2. LIMPIAR ARCHIVOS JSON EXISTENTES (solo si existen)
        archivos_limpiar = [
            f"votos_{anio}.json",
            f"bancos_{anio}.json", 
            f"ranking_{anio}.json"
        ]
        
        archivos_limpiados = []
        
        for archivo in archivos_limpiar:
            try:
                if os.path.exists(archivo):
                    os.remove(archivo)
                    archivos_limpiados.append(archivo)
                    print(f"🗑️ Eliminado archivo: {archivo}")
            except Exception as e:
                print(f"❌ Error eliminando {archivo}: {e}")
        
        # Mensaje de éxito final
        flash(f"✅ Reset completo para {anio}: Base de datos limpiada", "success")
        if archivos_limpiados:
            flash(f"�️ Archivos JSON eliminados: {len(archivos_limpiados)}", "info")
        else:
            flash(f"ℹ️ No había archivos JSON para limpiar", "info")
            
    except Exception as e:
        error_msg = f"Error en reset: {str(e)}"
        print(error_msg)
        flash(f"❌ {error_msg}", "error")
    
    return redirect(url_for('home', anio=anio))

@app.route("/exportar_votos/<anio>")
@role_required('administrador', 'psicopedagogo')
def exportar_votos(anio):
    """Exporta los votos de un año a Excel desde la base de datos"""
    if anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    # Obtener votos desde la base de datos
    votos = db_manager.obtener_votos_por_anio(anio)
    
    if not votos:
        flash("No hay votos para exportar", "warning")
        return redirect(url_for('home', anio=anio))
    
    try:
        # Crear datos para Excel
        datos_excel = []
        for votante, datos in votos.items():
            ratings = datos.get('calificaciones', {})
            bloqueado = datos.get('alumno_bloqueado', '')
            fecha = datos.get('timestamp', '')
            
            for evaluado, puntuacion in ratings.items():
                datos_excel.append({
                    'Votante': votante,
                    'Evaluado': evaluado,
                    'Puntuacion': puntuacion,
                    'Bloqueado_por_Votante': bloqueado,
                    'Fecha_Voto': fecha[:19] if fecha else ''
                })
        
        # Crear DataFrame
        try:
            import pandas as pd
        except ImportError:
            flash("❌ Funcionalidad de exportación no disponible (pandas no instalado)", "error")
            return redirect(url_for('home', anio=anio))
            
        df = pd.DataFrame(datos_excel)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nombre_archivo = f"votos_{anio}_{timestamp}.xlsx"
        
        # Guardar Excel
        df.to_excel(nombre_archivo, index=False, engine='openpyxl')
        
        flash(f"✅ Votos exportados a {nombre_archivo}", "success")
        
        # Devolver archivo para descarga
        from flask import send_file
        return send_file(nombre_archivo, as_attachment=True)
        
    except Exception as e:
        print(f"Error exportando: {e}")
        flash("Error al exportar los votos", "error")
        return redirect(url_for('home', anio=anio))

@app.route("/backup_sistema")
@role_required('administrador')
def backup_sistema():
    """Crea backup completo del sistema"""
    try:
        import zipfile
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_completo_{timestamp}.zip"
        
        with zipfile.ZipFile(backup_name, 'w') as backup_zip:
            # Incluir todos los archivos JSON
            for archivo in os.listdir('.'):
                if archivo.endswith('.json'):
                    backup_zip.write(archivo)
            
            # Incluir archivos de configuración
            archivos_importantes = ['app.py', 'estadisticas.py']
            for archivo in archivos_importantes:
                if os.path.exists(archivo):
                    backup_zip.write(archivo)
        
        flash(f"✅ Backup completo creado: {backup_name}", "success")
        
        from flask import send_file
        return send_file(backup_name, as_attachment=True)
        
    except Exception as e:
        print(f"Error creando backup: {e}")
        flash("Error al crear backup del sistema", "error")
        return redirect(url_for('home'))

@app.route("/gestionar_usuarios")
@role_required('administrador')
def gestionar_usuarios():
    """Panel de gestión de usuarios - SOLO ADMINISTRADORES"""
    return render_template("gestionar_usuarios.html", 
                         usuarios=USUARIOS_DOCENTES,
                         usuario_actual=session.get('usuario'))

@app.route("/agregar_usuario", methods=["POST"])
@role_required('administrador')
def agregar_usuario():
    """Agrega un nuevo usuario al sistema"""
    usuario = request.form.get('usuario', '').strip()
    password = request.form.get('password', '').strip()
    rol = request.form.get('rol', '').strip()
    
    if not usuario or not password or not rol:
        flash("Todos los campos son obligatorios", "error")
        return redirect(url_for('gestionar_usuarios'))
    
    if usuario in USUARIOS_DOCENTES:
        flash("El usuario ya existe", "error")
        return redirect(url_for('gestionar_usuarios'))
    
    if rol not in ['administrador', 'psicopedagogo', 'profesor']:
        flash("Rol no válido", "error")
        return redirect(url_for('gestionar_usuarios'))
    
    # Agregar usuario (en una implementación real, esto debería ir a una base de datos)
    USUARIOS_DOCENTES[usuario] = {
        'password': password,
        'rol': rol
    }
    
    # Guardar usuarios en archivo JSON
    if guardar_json_seguro('usuarios.json', USUARIOS_DOCENTES):
        flash(f"✅ Usuario '{usuario}' agregado exitosamente", "success")
    else:
        flash("Error al guardar el usuario", "error")
    
    return redirect(url_for('gestionar_usuarios'))

@app.route("/eliminar_usuario/<usuario>", methods=["POST"])
@role_required('administrador')
def eliminar_usuario(usuario):
    """Elimina un usuario del sistema"""
    if usuario == session.get('usuario'):
        flash("No puedes eliminarte a ti mismo", "error")
        return redirect(url_for('gestionar_usuarios'))
    
    if usuario in USUARIOS_DOCENTES:
        del USUARIOS_DOCENTES[usuario]
        
        if guardar_json_seguro('usuarios.json', USUARIOS_DOCENTES):
            flash(f"✅ Usuario '{usuario}' eliminado exitosamente", "success")
        else:
            flash("Error al eliminar el usuario", "error")
    else:
        flash("Usuario no encontrado", "error")
    
    return redirect(url_for('gestionar_usuarios'))

@app.route("/ranking/<anio>")
@login_required
def ranking(anio):
    """Muestra el ranking gamificado de la clase"""
    if anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    # Cargar ranking desde la base de datos
    ranking_data = db_manager.cargar_ranking(anio)
    
    if not ranking_data:
        flash("Aún no hay datos de ranking para este año", "info")
        return redirect(url_for('home', anio=anio))
    
    # Ordenar por puntos (descendente)
    ranking_ordenado = sorted(
        ranking_data.items(),
        key=lambda x: x[1]['puntos_totales'],
        reverse=True
    )
    
    # Calcular estadísticas
    total_participantes = len(ranking_data)
    puntos_promedio = sum(stats['puntos_totales'] for stats in ranking_data.values()) / total_participantes if total_participantes > 0 else 0
    nivel_promedio = sum(stats['nivel'] for stats in ranking_data.values()) / total_participantes if total_participantes > 0 else 0
    total_badges = sum(len(stats['badges']) for stats in ranking_data.values())
    
    return render_template("ranking.html",
                         anio=anio,
                         ranking_ordenado=ranking_ordenado,
                         total_participantes=total_participantes,
                         puntos_promedio=puntos_promedio,
                         nivel_promedio=nivel_promedio,
                         total_badges=total_badges)

def generar_emparejamientos(votos, lista_alumnos):
    """
    Genera emparejamientos óptimos basados en las votaciones mutuas
    Prioriza afinidades altas y evita bloqueos
    """
    if not votos:
        return []
    
    # 1. Calcular afinidades mutuas
    afinidades_mutuas = {}
    bloqueos = set()
    
    for votante, datos in votos.items():
        ratings = datos.get('ratings', {})
        bloqueado = datos.get('bloqueado')
        
        # Registrar bloqueos
        if bloqueado:
            bloqueos.add((votante, bloqueado))
            bloqueos.add((bloqueado, votante))  # Bloqueo bidireccional
        
        # Calcular afinidades mutuas
        for evaluado, puntuacion1 in ratings.items():
            if evaluado in votos:
                datos_evaluado = votos[evaluado]
                ratings_evaluado = datos_evaluado.get('ratings', {})
                
                if votante in ratings_evaluado:
                    puntuacion2 = ratings_evaluado[votante]
                    
                    # Crear clave única para la pareja (ordenada alfabéticamente)
                    pareja = tuple(sorted([votante, evaluado]))
                    
                    if pareja not in afinidades_mutuas:
                        promedio_afinidad = (puntuacion1 + puntuacion2) / 2
                        afinidades_mutuas[pareja] = {
                            'promedio': promedio_afinidad,
                            'puntuaciones': [puntuacion1, puntuacion2],
                            'diferencia': abs(puntuacion1 - puntuacion2)
                        }
    
    # 2. Filtrar parejas bloqueadas
    afinidades_filtradas = {
        pareja: datos for pareja, datos in afinidades_mutuas.items()
        if pareja not in bloqueos and (pareja[1], pareja[0]) not in bloqueos
    }
    
    # 3. Ordenar por mejor afinidad (promedio alto, diferencia baja)
    parejas_ordenadas = sorted(
        afinidades_filtradas.items(),
        key=lambda x: (-x[1]['promedio'], x[1]['diferencia'])
    )
    
    # 4. Formar grupos usando algoritmo greedy
    grupos = []
    alumnos_asignados = set()
    
    # Primero formar parejas con alta afinidad
    for (alumno1, alumno2), datos in parejas_ordenadas:
        if alumno1 not in alumnos_asignados and alumno2 not in alumnos_asignados:
            # Verificar que ambos votaron (están en la lista de votos)
            if alumno1 in votos and alumno2 in votos:
                if datos['promedio'] >= 3.5:  # Solo parejas con buena afinidad
                    grupos.append([alumno1, alumno2])
                    alumnos_asignados.add(alumno1)
                    alumnos_asignados.add(alumno2)
    
    # 5. Intentar expandir grupos existentes
    for votante, datos in votos.items():
        if votante in alumnos_asignados:
            continue
        
        ratings = datos.get('ratings', {})
        mejor_grupo = None
        mejor_puntuacion = 0
        
        # Buscar el grupo donde este alumno tiene mejor afinidad
        for i, grupo in enumerate(grupos):
            if len(grupo) >= 4:  # Limitar tamaño de grupos
                continue
            
            puntuaciones_grupo = []
            puede_unirse = True
            
            for miembro in grupo:
                # Verificar que no esté bloqueado con ningún miembro
                if (votante, miembro) in bloqueos or (miembro, votante) in bloqueos:
                    puede_unirse = False
                    break
                
                # Obtener puntuación que le dio a este miembro
                if miembro in ratings:
                    puntuaciones_grupo.append(ratings[miembro])
            
            if puede_unirse and puntuaciones_grupo:
                promedio_grupo = sum(puntuaciones_grupo) / len(puntuaciones_grupo)
                if promedio_grupo > mejor_puntuacion and promedio_grupo >= 3.0:
                    mejor_puntuacion = promedio_grupo
                    mejor_grupo = i
        
        # Unirse al mejor grupo encontrado
        if mejor_grupo is not None:
            grupos[mejor_grupo].append(votante)
            alumnos_asignados.add(votante)
    
    # 6. Formar grupos con alumnos restantes que votaron
    alumnos_sin_grupo = [alumno for alumno in votos.keys() if alumno not in alumnos_asignados]
    
    # Agrupar alumnos restantes de a pares si tienen afinidad
    i = 0
    while i < len(alumnos_sin_grupo) - 1:
        alumno1 = alumnos_sin_grupo[i]
        mejor_compañero = None
        mejor_afinidad = 0
        
        datos1 = votos.get(alumno1, {})
        ratings1 = datos1.get('ratings', {})
        
        for j in range(i + 1, len(alumnos_sin_grupo)):
            alumno2 = alumnos_sin_grupo[j]
            
            # Verificar que no estén bloqueados
            if (alumno1, alumno2) in bloqueos or (alumno2, alumno1) in bloqueos:
                continue
            
            # Calcular afinidad mutua si existe
            if alumno2 in ratings1:
                datos2 = votos.get(alumno2, {})
                ratings2 = datos2.get('ratings', {})
                
                if alumno1 in ratings2:
                    afinidad = (ratings1[alumno2] + ratings2[alumno1]) / 2
                    if afinidad > mejor_afinidad:
                        mejor_afinidad = afinidad
                        mejor_compañero = j
        
        if mejor_compañero is not None and mejor_afinidad >= 2.5:
            # Formar grupo con el mejor compañero
            alumno2 = alumnos_sin_grupo[mejor_compañero]
            grupos.append([alumno1, alumno2])
            alumnos_asignados.add(alumno1)
            alumnos_asignados.add(alumno2)
            
            # Remover de la lista (el de mayor índice primero)
            alumnos_sin_grupo.pop(mejor_compañero)
            alumnos_sin_grupo.pop(i)
        else:
            i += 1
    
    # 7. Agregar alumnos individuales restantes que votaron
    for alumno in alumnos_sin_grupo:
        if alumno not in alumnos_asignados:
            grupos.append([alumno])
            alumnos_asignados.add(alumno)
    
    # 8. Agregar alumnos que no votaron como grupos individuales
    alumnos_no_votaron = [alumno for alumno in lista_alumnos if alumno not in votos]
    for alumno in alumnos_no_votaron:
        grupos.append([alumno])
    
    # 9. Ordenar grupos por tamaño (grupos más grandes primero)
    grupos.sort(key=len, reverse=True)
    
    # 10. Filtrar grupos vacíos
    grupos = [grupo for grupo in grupos if grupo]
    
    return grupos

def obtener_estadisticas_emparejamiento(emparejamientos, votos):
    """
    Calcula estadísticas sobre la calidad del emparejamiento
    """
    if not emparejamientos or not votos:
        return {}
    
    total_grupos = len(emparejamientos)
    total_alumnos_agrupados = sum(len(grupo) for grupo in emparejamientos)
    grupos_con_afinidad = 0
    afinidad_promedio_total = 0
    contador_afinidades = 0
    
    for grupo in emparejamientos:
        if len(grupo) >= 2:
            afinidades_grupo = []
            
            # Calcular afinidades dentro del grupo
            for i in range(len(grupo)):
                for j in range(i + 1, len(grupo)):
                    alumno1, alumno2 = grupo[i], grupo[j]
                    
                    if alumno1 in votos and alumno2 in votos:
                        ratings1 = votos[alumno1].get('ratings', {})
                        ratings2 = votos[alumno2].get('ratings', {})
                        
                        if alumno2 in ratings1 and alumno1 in ratings2:
                            afinidad = (ratings1[alumno2] + ratings2[alumno1]) / 2
                            afinidades_grupo.append(afinidad)
                            afinidad_promedio_total += afinidad
                            contador_afinidades += 1
            
            if afinidades_grupo and sum(afinidades_grupo) / len(afinidades_grupo) >= 3.0:
                grupos_con_afinidad += 1
    
    return {
        'total_grupos': total_grupos,
        'total_alumnos': total_alumnos_agrupados,
        'grupos_con_buena_afinidad': grupos_con_afinidad,
        'porcentaje_grupos_exitosos': (grupos_con_afinidad / total_grupos * 100) if total_grupos > 0 else 0,
        'afinidad_promedio_general': (afinidad_promedio_total / contador_afinidades) if contador_afinidades > 0 else 0
    }
# Agregar esta función helper:

@app.route("/verificar_reset/<anio>")
@role_required('administrador')
def verificar_reset(anio):
    """Verifica el estado de los archivos después del reset"""
    if anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))

    
    archivos_estado = {}
    
    archivos_verificar = [
        f"votos_{anio}.json",
        f"bancos_{anio}.json", 
        f"ranking_{anio}.json"
    ]
    
    for archivo in archivos_verificar:
        if os.path.exists(archivo):
            try:
                data = cargar_json_seguro(archivo)
                archivos_estado[archivo] = {
                    'existe': True,
                    'vacio': len(data) == 0,
                    'tamaño': len(data)
                }
            except:
                archivos_estado[archivo] = {
                    'existe': True,
                    'vacio': None,
                    'error': True
                }
        else:
            archivos_estado[archivo] = {
                'existe': False,
                'vacio': True
            }
    
    # Crear mensaje de estado
    mensaje_estado = []
    for archivo, estado in archivos_estado.items():
        if estado['existe'] and estado.get('vacio'):
            mensaje_estado.append(f"✅ {archivo}: Vacío")
        elif estado['existe']:
            mensaje_estado.append(f"📁 {archivo}: {estado['tamaño']} elementos")
        else:
            mensaje_estado.append(f"❌ {archivo}: No existe")
    
    flash(f"Estado de archivos para {anio}:", "info")
    for msg in mensaje_estado:
        flash(msg, "info")
    
    return redirect(url_for('home', anio=anio))

# ===== RUTAS DE GESTIÓN DE ALUMNOS =====

@app.route("/gestion_alumnos")
@role_required('administrador')
def gestion_alumnos():
    """Panel de gestión de alumnos"""
    stats = gestor_alumnos.obtener_estadisticas()
    return render_template('gestion_alumnos.html', 
                         stats=stats,
                         anios=gestor_alumnos.obtener_todos_los_anios())

@app.route("/agregar_alumno", methods=['POST'])
@role_required('administrador')
def agregar_alumno():
    """Agrega un nuevo alumno"""
    anio = request.form.get('anio', '')
    nombre = request.form.get('nombre', '').strip()
    
    if not anio or not nombre:
        flash("Año y nombre son requeridos", "error")
        return redirect(url_for('gestion_alumnos'))
    
    if gestor_alumnos.agregar_alumno(anio, nombre):
        flash(f"✅ Alumno {nombre} agregado a {anio}", "success")
        # Actualizar la variable global
        global alumnos_por_anio
        alumnos_por_anio = obtener_alumnos_por_anio()
    else:
        flash(f"❌ El alumno ya existe en {anio}", "error")
    
    return redirect(url_for('gestion_alumnos'))

@app.route("/eliminar_alumno", methods=['POST'])
@role_required('administrador')
def eliminar_alumno():
    """Elimina un alumno"""
    anio = request.form.get('anio', '')
    nombre = request.form.get('nombre', '')
    
    if not anio or not nombre:
        flash("Datos incompletos", "error")
        return redirect(url_for('gestion_alumnos'))
    
    if gestor_alumnos.eliminar_alumno(anio, nombre):
        flash(f"✅ Alumno {nombre} eliminado de {anio}", "success")
        # Actualizar la variable global
        global alumnos_por_anio
        alumnos_por_anio = obtener_alumnos_por_anio()
    else:
        flash(f"❌ Error al eliminar alumno", "error")
    
    return redirect(url_for('gestion_alumnos'))

@app.route("/importar_csv", methods=['POST'])
@role_required('administrador')
def importar_csv():
    """Importa alumnos desde CSV"""
    anio = request.form.get('anio', '')
    columna_nombre = request.form.get('columna_nombre', 'nombre')
    
    if 'archivo_csv' not in request.files:
        flash("No se seleccionó archivo", "error")
        return redirect(url_for('gestion_alumnos'))
    
    archivo = request.files['archivo_csv']
    if archivo.filename == '':
        flash("No se seleccionó archivo", "error")
        return redirect(url_for('gestion_alumnos'))
    
    if archivo and archivo.filename and archivo.filename.endswith('.csv'):
        # Guardar archivo temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as temp_file:
            archivo.save(temp_file.name)
            
            # Importar desde el archivo temporal
            exito, mensaje, cantidad = gestor_alumnos.importar_desde_csv(
                temp_file.name, anio, columna_nombre
            )
            
            # Limpiar archivo temporal
            os.unlink(temp_file.name)
            
            if exito:
                flash(f"✅ {mensaje}", "success")
                # Actualizar la variable global
                global alumnos_por_anio
                alumnos_por_anio = obtener_alumnos_por_anio()
            else:
                flash(f"❌ {mensaje}", "error")
    else:
        flash("❌ Solo se permiten archivos CSV", "error")
    
    return redirect(url_for('gestion_alumnos'))

@app.route("/validar_csv", methods=['POST'])
@role_required('administrador')
def validar_csv():
    """Valida un archivo CSV antes de importar"""
    if 'archivo_csv' not in request.files:
        return {'success': False, 'error': 'No se seleccionó archivo'}
    
    archivo = request.files['archivo_csv']
    if not archivo.filename or archivo.filename == '' or not archivo.filename.endswith('.csv'):
        return {'success': False, 'error': 'Archivo inválido'}
    
    # Guardar temporalmente y validar
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as temp_file:
        archivo.save(temp_file.name)
        
        exito, mensaje, columnas = gestor_alumnos.validar_estructura_csv(temp_file.name)
        
        # Limpiar archivo temporal
        os.unlink(temp_file.name)
        
        if exito:
            return {
                'success': True,
                'mensaje': mensaje,
                'columnas': columnas
            }
        else:
            return {'success': False, 'error': mensaje}

# ===== RUTAS DE ANÁLISIS PSICOPEDAGÓGICO =====

@app.route("/analisis_psicopedagogico/<anio>")
@role_required('administrador', 'psicopedagogo')
def analisis_psicopedagogico(anio):
    """Panel de análisis psicopedagógico"""
    if anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    # Cargar votos desde la base de datos
    votos = db_manager.obtener_votos_por_anio(anio)
    
    if not votos:
        flash("No hay datos de votos para analizar", "warning")
        return redirect(url_for('home', anio=anio))
    
    # Realizar análisis
    analisis = analizador_psicopedagogico.analizar_relaciones_sociales(anio, votos)
    
    return render_template('analisis_psicopedagogico.html',
                         anio=anio,
                         analisis=analisis,
                         total_alumnos=len(alumnos_por_anio[anio]))

@app.route("/reporte_psicopedagogico/<anio>")
@role_required('administrador', 'psicopedagogo')
def reporte_psicopedagogico(anio):
    """Genera reporte completo para el gabinete"""
    if anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    reporte = analizador_psicopedagogico.generar_reporte_completo(anio)
    
    if 'error' in reporte:
        flash(reporte['error'], "error")
        return redirect(url_for('home', anio=anio))
    
    return render_template('reporte_psicopedagogico.html',
                         anio=anio,
                         reporte=reporte)

@app.route("/exportar_analisis/<anio>")
@role_required('administrador', 'psicopedagogo')
def exportar_analisis(anio):
    """Exporta el análisis psicopedagógico a JSON"""
    reporte = analizador_psicopedagogico.generar_reporte_completo(anio)
    
    if 'error' in reporte:
        flash(reporte['error'], "error")
        return redirect(url_for('analisis_psicopedagogico', anio=anio))
    
    from flask import jsonify, make_response
    
    response = make_response(jsonify(reporte))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=analisis_psicopedagogico_{anio}_{datetime.now().strftime("%Y%m%d")}.json'
    
    return response

# ===== RUTAS DE BANCO DE PREGUNTAS =====

@app.route("/gestion_preguntas")
@role_required('administrador', 'profesor')
def gestion_preguntas():
    """Panel de gestión del banco de preguntas"""
    stats = banco_preguntas.obtener_estadisticas_banco()
    materias = banco_preguntas.obtener_materias_disponibles()
    niveles = banco_preguntas.obtener_niveles_disponibles()
    
    return render_template('gestion_preguntas.html',
                         stats=stats,
                         materias=materias,
                         niveles=niveles)

@app.route("/agregar_pregunta", methods=['POST'])
@role_required('administrador', 'profesor')
def agregar_pregunta():
    """Agrega una nueva pregunta al banco"""
    materia = request.form.get('materia', '')
    pregunta_texto = request.form.get('pregunta', '')
    opciones = [
        request.form.get('opcion1', ''),
        request.form.get('opcion2', ''),
        request.form.get('opcion3', ''),
        request.form.get('opcion4', '')
    ]
    respuesta_correcta = int(request.form.get('respuesta_correcta', 0))
    puntos = int(request.form.get('puntos', 10))
    explicacion = request.form.get('explicacion', '')
    nivel = request.form.get('nivel', 'basico')
    
    nueva_pregunta = {
        'pregunta': pregunta_texto,
        'opciones': opciones,
        'respuesta_correcta': respuesta_correcta,
        'puntos': puntos,
        'explicacion': explicacion,
        'nivel': nivel
    }
    
    if banco_preguntas.agregar_pregunta(materia, nueva_pregunta):
        flash(f"✅ Pregunta agregada a {materia}", "success")
    else:
        flash("❌ Error al agregar pregunta", "error")
    
    return redirect(url_for('gestion_preguntas'))

@app.route("/api/estado_votacion/<anio>")
@login_required
def api_estado_votacion(anio):
    """API para obtener el estado de votación en tiempo real"""
    from flask import jsonify
    from datetime import datetime
    
    # ✅ CORREGIDO: Usar función que lee el archivo actual, no variable global
    alumnos_actuales = obtener_alumnos_por_anio()
    
    if anio not in alumnos_actuales:
        return jsonify({'error': 'Año no válido'}), 400
    
    alumnos = alumnos_actuales.get(anio, [])
    total_alumnos = len(alumnos)
    
    # Obtener votos desde la base de datos
    votos_bd = db_manager.obtener_votos_por_anio(anio)
    ya_votaron = set(votos_bd.keys()) if votos_bd else set()
    
    votaron = len(ya_votaron)
    restantes = total_alumnos - votaron
    porcentaje = (votaron / total_alumnos * 100) if total_alumnos > 0 else 0
    
    # Estados de alumnos
    estados_alumnos = {}
    for alumno in alumnos:
        estados_alumnos[alumno] = 'completado' if alumno in ya_votaron else 'pendiente'
    
    return jsonify({
        'total_alumnos': total_alumnos,
        'votaron': votaron,
        'restantes': restantes,
        'porcentaje': round(porcentaje, 1),
        'estados_alumnos': estados_alumnos,
        'ya_votaron': list(ya_votaron),
        'timestamp': datetime.now().isoformat(),
        'cache_buster': int(datetime.now().timestamp())
    })

@app.route("/dashboard")
@role_required('administrador', 'profesor', 'psicopedagogo')
def dashboard():
    """Dashboard principal para docentes con todas las funcionalidades"""
    from datetime import datetime, timedelta
    
    # ✅ CORREGIDO: Usar función que lee archivo actual
    alumnos_actuales = obtener_alumnos_por_anio()
    
    # Obtener estadísticas generales
    estadisticas_generales = {}
    
    # Contar alumnos por año
    total_alumnos = sum(len(alumnos) for alumnos in alumnos_actuales.values())
    estadisticas_generales['total_alumnos'] = total_alumnos
    estadisticas_generales['años_activos'] = len(alumnos_actuales)
    
    # Estadísticas de votación
    total_votos = 0
    votos_por_anio = {}
    for anio in alumnos_actuales.keys():
        votos_bd = db_manager.obtener_votos_por_anio(anio)
        votos_count = len(votos_bd) if votos_bd else 0
        votos_por_anio[anio] = votos_count
        total_votos += votos_count
    
    estadisticas_generales['total_votos'] = total_votos
    estadisticas_generales['votos_por_anio'] = votos_por_anio
    
    # Porcentaje de participación
    porcentaje_participacion = (total_votos / total_alumnos * 100) if total_alumnos > 0 else 0
    estadisticas_generales['porcentaje_participacion'] = round(porcentaje_participacion, 1)
    
    # Configuración actual
    config_actual = db_manager.cargar_configuracion_aula()
    
    return render_template('dashboard.html',
                         estadisticas=estadisticas_generales,
                         alumnos_por_anio=alumnos_por_anio,
                         config=config_actual,
                         usuario=session.get('usuario'),
                         rol=session.get('rol'))

@app.route("/dashboard/carga_alumnos", methods=['GET', 'POST'])
@role_required('administrador', 'profesor')
def dashboard_carga_alumnos():
    """Panel para carga masiva de alumnos"""
    if request.method == 'POST':
        # Manejar carga de CSV
        if 'archivo_csv' not in request.files:
            flash('No se seleccionó archivo', 'error')
            return redirect(url_for('dashboard_carga_alumnos'))
        
        archivo = request.files['archivo_csv']
        anio = request.form.get('anio', '').strip()
        
        if archivo.filename == '':
            flash('No se seleccionó archivo', 'error')
            return redirect(url_for('dashboard_carga_alumnos'))
        
        if not anio:
            flash('Debe especificar el año del curso', 'error')
            return redirect(url_for('dashboard_carga_alumnos'))
        
        try:
            # Leer CSV
            import io
            import csv
            stream = io.StringIO(archivo.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)
            
            alumnos_nuevos = []
            for row_num, row in enumerate(csv_input, 1):
                if row and len(row) > 0:
                    nombre = row[0].strip()
                    if nombre and nombre not in ['nombre', 'Nombre', 'NOMBRE']:  # Skip headers
                        alumnos_nuevos.append(nombre)
            
            if alumnos_nuevos:
                # Usar el gestor de alumnos para agregar
                for alumno in alumnos_nuevos:
                    gestor_alumnos.agregar_alumno(anio, alumno)
                
                # Actualizar la variable global
                global alumnos_por_anio
                from gestor_alumnos import obtener_alumnos_por_anio
                alumnos_por_anio = obtener_alumnos_por_anio()
                
                flash(f'✅ Se agregaron {len(alumnos_nuevos)} alumnos al año {anio}', 'success')
            else:
                flash('No se encontraron alumnos válidos en el archivo', 'warning')
                
        except Exception as e:
            flash(f'Error procesando archivo CSV: {str(e)}', 'error')
        
        return redirect(url_for('dashboard_carga_alumnos'))
    
    return render_template('dashboard_carga_alumnos.html',
                         alumnos_por_anio=alumnos_por_anio,
                         usuario=session.get('usuario'),
                         rol=session.get('rol'))

@app.route("/dashboard/analisis_problematicos")
@role_required('administrador', 'psicopedagogo')
def dashboard_analisis_problematicos():
    """Panel de análisis de alumnos problemáticos"""
    # Análisis por año
    analisis_por_anio = {}
    
    for anio, alumnos in alumnos_por_anio.items():
        if not alumnos:
            continue
            
        # Obtener votos del año
        votos_bd = db_manager.obtener_votos_por_anio(anio)
        
        # Análisis de calificaciones recibidas
        calificaciones_recibidas = {}
        bloqueos_recibidos = {}
        
        for votante, voto_data in votos_bd.items():
            calificaciones = voto_data.get('calificaciones', {})
            bloqueado = voto_data.get('alumno_bloqueado')
            
            # Procesar calificaciones
            for alumno_evaluado, calificacion in calificaciones.items():
                if alumno_evaluado not in calificaciones_recibidas:
                    calificaciones_recibidas[alumno_evaluado] = []
                calificaciones_recibidas[alumno_evaluado].append(calificacion)
            
            # Procesar bloqueos
            if bloqueado:
                if bloqueado not in bloqueos_recibidos:
                    bloqueos_recibidos[bloqueado] = 0
                bloqueos_recibidos[bloqueado] += 1
        
        # Calcular métricas
        metricas_alumnos = []
        for alumno in alumnos:
            califs = calificaciones_recibidas.get(alumno, [])
            bloqueos = bloqueos_recibidos.get(alumno, 0)
            
            if califs:
                promedio = sum(califs) / len(califs)
                califs_bajas = sum(1 for c in califs if c <= 2)
                porcentaje_bajas = (califs_bajas / len(califs)) * 100
            else:
                promedio = 0
                porcentaje_bajas = 0
                califs_bajas = 0
            
            # Score de riesgo (0-100, donde 100 es más problemático)
            score_riesgo = 0
            if califs:
                score_riesgo += (5 - promedio) * 15  # Promedio bajo
                score_riesgo += porcentaje_bajas * 0.8  # Muchas calificaciones bajas
                score_riesgo += bloqueos * 10  # Bloqueos recibidos
                score_riesgo = min(score_riesgo, 100)
            
            metricas_alumnos.append({
                'nombre': alumno,
                'promedio_calificaciones': round(promedio, 2),
                'total_evaluaciones': len(califs),
                'calificaciones_bajas': califs_bajas,
                'porcentaje_bajas': round(porcentaje_bajas, 1),
                'bloqueos_recibidos': bloqueos,
                'score_riesgo': round(score_riesgo, 1),
                'nivel_riesgo': 'Alto' if score_riesgo >= 70 else 'Medio' if score_riesgo >= 40 else 'Bajo'
            })
        
        # Ordenar por score de riesgo
        metricas_alumnos.sort(key=lambda x: x['score_riesgo'], reverse=True)
        
        analisis_por_anio[anio] = {
            'alumnos': metricas_alumnos,
            'total_evaluaciones': len(votos_bd),
            'alumnos_alto_riesgo': len([a for a in metricas_alumnos if a['score_riesgo'] >= 70]),
            'alumnos_medio_riesgo': len([a for a in metricas_alumnos if 40 <= a['score_riesgo'] < 70]),
            'alumnos_bajo_riesgo': len([a for a in metricas_alumnos if a['score_riesgo'] < 40])
        }
    
    return render_template('dashboard_analisis_problematicos.html',
                         analisis=analisis_por_anio,
                         usuario=session.get('usuario'),
                         rol=session.get('rol'))

@app.route("/dashboard/estadisticas_completas")
@role_required('administrador', 'profesor', 'psicopedagogo')
def dashboard_estadisticas_completas():
    """Panel completo de estadísticas con gráficos"""
    estadisticas = {}
    
    # Estadísticas por año
    for anio, alumnos in alumnos_por_anio.items():
        votos_bd = db_manager.obtener_votos_por_anio(anio)
        
        # Estadísticas básicas
        stats_anio = {
            'total_alumnos': len(alumnos),
            'total_votos': len(votos_bd),
            'participacion': (len(votos_bd) / len(alumnos) * 100) if alumnos else 0,
            'distribuciones_calificaciones': {},
            'tendencias_bloqueo': {},
            'patrones_votacion': {}
        }
        
        # Análisis de calificaciones
        todas_calificaciones = []
        for voto_data in votos_bd.values():
            calificaciones = voto_data.get('calificaciones', {})
            todas_calificaciones.extend(calificaciones.values())
        
        if todas_calificaciones:
            # Distribución de calificaciones
            for i in range(1, 6):
                count = todas_calificaciones.count(i)
                stats_anio['distribuciones_calificaciones'][i] = {
                    'count': count,
                    'porcentaje': (count / len(todas_calificaciones)) * 100
                }
        
        estadisticas[anio] = stats_anio
    
    return render_template('dashboard_estadisticas.html',
                         estadisticas=estadisticas,
                         usuario=session.get('usuario'),
                         rol=session.get('rol'))

@app.route("/dashboard/omitir_trivia/<anio>", methods=['POST'])
@role_required('administrador', 'profesor')
def omitir_trivia_curso(anio):
    """Permite al docente omitir la trivia para todos los alumnos de un año"""
    try:
        # Obtener alumnos del año
        alumnos_actuales = get_alumnos_actuales()
        alumnos = alumnos_actuales.get(anio, [])
        
        if not alumnos:
            flash(f'No se encontraron alumnos en el año {anio}', 'error')
            return redirect(url_for('dashboard'))
        
        # Marcar trivia como completada para todos los alumnos del año
        contador_omitidos = 0
        for alumno in alumnos:
            session[f'trivia_completada_{anio}_{alumno}'] = True
            contador_omitidos += 1
        
        flash(f'✅ Trivia omitida para {contador_omitidos} alumnos de {anio}. Ahora pueden votar directamente.', 'success')
        
    except Exception as e:
        flash(f'Error al omitir trivia: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route("/dashboard/asignacion_aleatoria/<anio>", methods=['POST'])
@role_required('administrador', 'profesor')
def asignacion_aleatoria_automatica(anio):
    """Genera asignaciones aleatorias automáticas sin votación de los alumnos"""
    try:
        # Obtener alumnos del año
        alumnos_actuales = get_alumnos_actuales()
        alumnos = alumnos_actuales.get(anio, [])
        
        if not alumnos:
            flash(f'No se encontraron alumnos en el año {anio}', 'error')
            return redirect(url_for('dashboard'))
        
        if len(alumnos) < 2:
            flash(f'Se necesitan al menos 2 alumnos para generar asignaciones', 'warning')
            return redirect(url_for('dashboard'))
        
        # Generar votos aleatorios para todos los alumnos
        import random
        from datetime import datetime
        
        votos_generados = 0
        timestamp_base = datetime.now().isoformat()
        
        for i, alumno in enumerate(alumnos):
            # Verificar si ya votó
            votos_existentes = db_manager.obtener_votos_por_anio(anio)
            if votos_existentes and alumno in votos_existentes:
                continue  # Saltar si ya votó
            
            # Obtener otros alumnos (excluir al que está "votando")
            otros_alumnos = [a for a in alumnos if a != alumno]
            
            # Seleccionar 5 alumnos aleatorios para evaluar
            num_evaluaciones = min(5, len(otros_alumnos))
            alumnos_a_evaluar = random.sample(otros_alumnos, num_evaluaciones)
            
            # Generar calificaciones aleatorias (pero realistas)
            ratings = {}
            for alumno_eval in alumnos_a_evaluar:
                # Distribución más realista: más 3s y 4s, menos 1s y 5s
                calificacion = random.choices([1, 2, 3, 4, 5], weights=[10, 20, 40, 25, 5])[0]
                ratings[alumno_eval] = calificacion
            
            # Ocasionalmente bloquear a alguien (20% de probabilidad)
            alumno_bloqueado = random.choice(alumnos_a_evaluar) if random.random() < 0.2 else None
            
            # Timestamp único para cada voto
            timestamp_voto = f"{timestamp_base}_{i:03d}"
            
            # Guardar voto automático
            exito = db_manager.guardar_voto(
                anio=anio,
                alumno=alumno,
                calificaciones=ratings,
                alumno_bloqueado=alumno_bloqueado,
                timestamp=timestamp_voto
            )
            
            if exito:
                votos_generados += 1
        
        if votos_generados > 0:
            flash(f'✅ Se generaron {votos_generados} asignaciones aleatorias para {anio}. Los resultados están listos.', 'success')
        else:
            flash(f'ℹ️ Todos los alumnos de {anio} ya habían votado', 'info')
            
    except Exception as e:
        flash(f'Error generando asignaciones aleatorias: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route("/dashboard/resetear_trivia/<anio>", methods=['POST'])
@role_required('administrador', 'profesor')
def resetear_trivia_curso(anio):
    """Resetea el estado de trivia para todos los alumnos de un año"""
    try:
        # Obtener alumnos del año
        alumnos_actuales = get_alumnos_actuales()
        alumnos = alumnos_actuales.get(anio, [])
        
        if not alumnos:
            flash(f'No se encontraron alumnos en el año {anio}', 'error')
            return redirect(url_for('dashboard'))
        
        # Resetear trivia para todos los alumnos del año
        contador_reseteados = 0
        for alumno in alumnos:
            session_key = f'trivia_completada_{anio}_{alumno}'
            if session_key in session:
                session.pop(session_key, None)
                contador_reseteados += 1
        
        flash(f'✅ Estado de trivia reseteado para {contador_reseteados} alumnos de {anio}', 'success')
        
    except Exception as e:
        flash(f'Error al resetear trivia: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route("/dashboard/resetear_completo/<anio>", methods=['POST'])
@role_required('administrador', 'profesor')
def resetear_completo_curso(anio):
    """Resetea COMPLETAMENTE un año: borra votos de BD + limpia sesión trivia"""
    try:
        # Obtener alumnos del año
        alumnos_actuales = get_alumnos_actuales()
        alumnos = alumnos_actuales.get(anio, [])
        
        if not alumnos:
            flash(f'No se encontraron alumnos en el año {anio}', 'error')
            return redirect(url_for('dashboard'))
        
        # 1. Borrar TODOS los votos de la base de datos
        exito_bd, votos_borrados = db_manager.borrar_votos_anio(anio)
        
        # 2. Limpiar sesiones de trivia
        contador_trivia = 0
        for alumno in alumnos:
            session_key = f'trivia_completada_{anio}_{alumno}'
            if session_key in session:
                session.pop(session_key, None)
                contador_trivia += 1
        
        if exito_bd:
            flash(f'✅ RESETEO COMPLETO: {votos_borrados} votos borrados de BD + {contador_trivia} sesiones de trivia limpiadas para {anio}', 'success')
        else:
            flash(f'❌ Error al borrar votos de la base de datos para {anio}', 'error')
        
    except Exception as e:
        flash(f'Error en reseteo completo: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route("/dashboard/borrar_voto/<anio>/<alumno>", methods=['POST'])
@role_required('administrador', 'profesor')
def borrar_voto_individual(anio, alumno):
    """Borra el voto de un alumno específico"""
    try:
        exito = db_manager.borrar_voto_alumno(anio, alumno)
        
        if exito:
            # También limpiar sesión de trivia de ese alumno
            session_key = f'trivia_completada_{anio}_{alumno}'
            session.pop(session_key, None)
            
            flash(f'✅ Voto de {alumno} borrado exitosamente', 'success')
        else:
            flash(f'⚠️ {alumno} no tenía voto registrado', 'warning')
            
    except Exception as e:
        flash(f'Error borrando voto de {alumno}: {str(e)}', 'error')
    
    return redirect(url_for('home', anio=anio))

# --- RUTA TEMPORAL PARA INICIALIZAR TABLAS EN PRODUCCIÓN (cPanel) ---
@app.route("/sys_admin/inicializar_db")
@role_required('administrador')
def inicializar_db_web():
    """Crea todas las tablas definidas en los modelos usando las credenciales cargadas en entorno web.
    IMPORTANTE: Eliminar esta ruta una vez ejecutada exitosamente en producción.
    """
    try:
        # Importar explícitamente el gestor ORM para acceder al engine SQLAlchemy
        from db_models import Base, db_manager as orm_db_manager
        import traceback, os
        # Log inicial
        log_path = os.path.join(os.path.dirname(__file__), 'init_db_log.txt')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n--- Intento creación tablas {datetime.now().isoformat()} ---\n")
            f.write(f"DATABASE_URL={os.environ.get('DATABASE_URL','(no definida)')}\n")
        
        Base.metadata.create_all(orm_db_manager.engine)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write("OK: Tablas creadas sin excepción.\n")
        return "✅ Tablas creadas correctamente en la base de datos. Puedes eliminar esta ruta."
    except Exception as e:
        import traceback, os
        log_path = os.path.join(os.path.dirname(__file__), 'init_db_log.txt')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write("ERROR: Excepción durante creación de tablas\n")
            f.write(str(e) + "\n")
            f.write(traceback.format_exc() + "\n")
        return f"❌ Error creando tablas: {type(e).__name__}: {str(e)} (ver init_db_log.txt)"

# Ruta de diagnóstico para revisar entorno y acceso a ORM
@app.route("/sys_admin/diagnostico_db")
@role_required('administrador')
def diagnostico_db():
    try:
        import os, traceback, importlib
        from sqlalchemy import text, inspect
        from db_models import DATABASE_URL, db_manager as orm_db_manager
        detalles = []
        detalles.append(f"DATABASE_URL={DATABASE_URL}")
        detalles.append(f"CWD={os.getcwd()}")
        detalles.append(f"__file__={__file__}")
        detalles.append(f"Engine class={orm_db_manager.engine.__class__.__name__}")
        # Driver pymysql
        try:
            pymysql_mod = importlib.import_module('pymysql')
            detalles.append(f"pymysql_version={getattr(pymysql_mod, '__version__', 'desconocida')}")
        except Exception as e:
            detalles.append(f"pymysql_import_error={type(e).__name__}: {e}")
        # Probar conexión simple
        try:
            with orm_db_manager.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                detalles.append("Test SELECT 1=OK")
        except Exception as e:
            detalles.append(f"Test SELECT 1 ERROR: {type(e).__name__}: {e}")
        # Listar tablas (SQLAlchemy 2.x via inspect)
        try:
            inspector = inspect(orm_db_manager.engine)
            tablas = inspector.get_table_names()
            detalles.append(f"Tablas={tablas if tablas else '[]'}")
        except Exception as e:
            detalles.append(f"Inspector ERROR: {type(e).__name__}: {e}")
        # Variables de entorno relevantes
        for var in ["PYTHONPATH", "PATH", "HOME"]:
            detalles.append(f"ENV {var}={os.environ.get(var,'(no)')}")
        return "\n".join(detalles)
    except Exception as e:
        return f"❌ Diagnóstico falló: {type(e).__name__}: {e}"

if __name__ == "__main__":
    app.run(debug=True)