from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import json
import os
import math
from functools import wraps
from collections import Counter, defaultdict
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'puertas_del_sol_secret_key_2024'

# 1. PRIMERO: Usuarios base (sin cargar archivo aún)
USUARIOS_DOCENTES = {
    'admin': {'password': 'admin123', 'rol': 'administrador'},
    'director': {'password': 'director2024', 'rol': 'administrador'},
    'coordinador': {'password': 'coord123', 'rol': 'administrador'},
    'psicopedagogo1': {'password': 'psico123', 'rol': 'psicopedagogo'},
    'psicopedagogo2': {'password': 'psico456', 'rol': 'psicopedagogo'},
    'profesor1': {'password': 'prof2024', 'rol': 'profesor'},
    'profesor2': {'password': 'prof456', 'rol': 'profesor'},
    'secretaria': {'password': 'secre123', 'rol': 'profesor'}
}

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

# 3. TERCERO: AHORA SÍ cargar usuarios adicionales
usuarios_archivo = cargar_json_seguro('usuarios.json')
if usuarios_archivo:
    USUARIOS_DOCENTES.update(usuarios_archivo)

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

# Diccionario de alumnos por año
alumnos_por_anio = {
    'primero': [
        "ISABELLA ALBERIONE FIORE", "BENJAMIN MATIAS ALDAVE", "MALENA ARMADA",
        "MIA BALDONCINI", "FRANCESCO BALEANI", "OCTAVIO BARRIONUEVO SORIA",
        "BENJAMIN ALEXIS BELTRAMO", "LAUTARO OMAR BONO", "MIA CASTRO",
        "CATALINA CICCIOLI", "ALAN DIDIER", "ISABELLA FALCONNAT",
        "AXEL ARIEL FERREYRA", "LUCIA INES FRANCO", "GENARO ZACARÍAS FRARESSO",
        "JUSTINO FRARESSO ZORRILLA", "CATALINA GALETTO GALVAN", "FELIPE LOZANO DE FRANCISCO",
        "LAZARO MARINSALDA SONTULLO", "IGNACIO MELANO", "MATEO MERCADO BOTTOSSO",
        "OLIVIA JAZMIN MONTE", "ANGELINA NICOLE MOYANO CARBAJAL", "GIULIANA OLDANI",
        "JULIANA PEROGLIA PAINA", "EZEQUIEL FEDERICO PERREN", "FERMIN RAMONDA ROSAS",
        "LOURDES RE", "BIANCA SOFIA RE OLIVERA", "VICTORIA SCARAMUZZA MATTIA",
        "VICTORIA TANTUCCI VIANO", "VALENTINO TAPIA CERQUATTI", "ISABELLA VEGA AHUMADA",
        "LARA VENTRE", "RINGO JAVIER ZUPPA"
    ],
    'segundo': [
        "SANTINO CERUTTI", "HELENA CLARK ETCHEVERRY", "BENJAMIN CRESATTI MIÑO",
        "EMILIA FALCO GARINO", "FRANCISCO FERRERO FONSECA", "MIA GABRIELA GARCIA",
        "HELENA MANSILLA", "FELIPE RE", "MARTIN ANGEL ROSINA",
        "MARTINIANO SORIANO PRANZONI", "MELANY TORRESI", "JOAQUIN BAUTISTA VERDICCHIO"
    ],
    'tercero': [
        "SANTIAGO BALDONCINI", "LUCIA BERTEA CASAGRANDE", "ZAIRA BIANI",
        "BENJAMIN CABANILLAS MONNIER", "BIANCA DE LOURDES CAMPANA", "EUGENIA GUADALUPE CAROLINI CIRIACI",
        "JOAQUIN CASTELLINA", "MARTINA CEJAS FONT", "VALENTINA CINGOLANI",
        "MATEO CORNEJO", "CATALINA DI GREGORIO MARINSALDA", "CRISTOBAL ELLENA CITTADINI",
        "JAZMIN FODDANU", "GUADALUPE FOLLONIER OLDANI", "MATEO ANGEL FRANCO",
        "AGUSTIN NICOLAS GAIDO", "LORENZO GALETTO GALVAN", "ISABELLA GASPARINI",
        "JAZMIN GIOTTO", "CATALINA GOMEZ", "RAMIRO JOAQUIN LOVERA",
        "BRIANA ELIZABETH LUQUE", "SANTIAGO ARIEL MANDILE", "LORENZO MASSEI",
        "SOFIA NUÑEZ", "AGUSTINA OCHETTI", "AGUSTINA OLDANI",
        "MERCEDES LUJAN OLMOS", "IGNACIO FEDERICO PERREN", "FRANCESCA PESANDO",
        "AGOSTINA RODRIGUEZ RE", "RENATA ROPOLO", "FAUSTINA SCARAMUZZA",
        "SANTIAGO ANDRES SONZINI FINELLI", "SOLANGE TISSERA", "MAXIMO TORRES FORTINI",
        "SOFIA VALENTINA VECCHIO FERNANDEZ", "DANTE VILLARREAL BALDONCINI", "ALMA MORENA LOURDES ZUPPA"
    ],
    'cuarto': [
        "RENATA BARBERO MARTINEZ", "MARTIN JESUS BELTRAMO", "ARANZA BONFIGLI",
        "TOMAS CAMILETTI", "JUANA CAMPODONICO FALCO", "SANTINO CAMPODÓNICO SALIBI",
        "PAULINA BERENICE CASTELLANO BECK", "ATILIO FERREYRA FRARESSO", "AUGUSTO FUENTES",
        "LARA HERNANDEZ", "THIAGO BAUTISTA INAMORATO MOYANO", "FELIPE LIBRA",
        "BAUTISTA LOPEZ CALCATERRA", "ANALUZ MALDONADO MENDEZ", "LUCERO MIA MARINSALDA SONTULLO",
        "UMMA MILLER LUPIDI", "DELFINA MURIÑO", "JUAN CRUZ OLIVA",
        "FELIPE LUCIANO PICCA", "SOFIA ROSAS", "VALENTIN ROSSI",
        "FRANCESCO SCARAMUZZA", "FRANCO SCARAMUZZA MATTIA", "CATALINA TANTUCCI BERTOTTO",
        "FRANCISCO TANTUCCI VIANO", "BAUTISTA TULIAN", "MAXIMO JOSE ZUPPA"
    ],
    'quinto': [
        "PALOMA AIMAR", "JULIANA BELTRAMO", "VALENTINA MORENA BRAGAYOLI PINO",
        "JOAQUINA BRAVO GARNERO", "AUGUSTO NICOLA CERUTTI", "NICOLAS CICCIOLI",
        "BAUTISTA CORDOBA GONZALEZ", "GENARO LEONEL ESQUIVEL", "JOAQUIN FERNANDEZ",
        "CANDELA FERNANDEZ VENTRE", "RAMIRO FRARESSO", "AARON LUCIANO GALVAN CORDOBA",
        "MELODY LUZ GOMEZ", "JULIAN GUZMAN BAIADERA", "DANTE LIBRA",
        "PAULINA MANZOTTI", "ANA PAULA MARIN", "NAHUEL BENJAMIN MARINSALDA MASSOLA",
        "DANILO MARTINANGELO", "JULIETA MERCADO BOTTOSSO", "ANA PAULA MONTE",
        "FELIPE OLAIZ", "VICTORIA OLDANI", "MARIA DEL ROSARIO OLMOS",
        "ANA CELINA OSTORERO", "MIA PERALTA", "VALENTIN RAMONDA ROSAS",
        "LUCIA BELEN RE OLIVERA", "VALENTINO ROPOLO", "MARTINA TORRES VAZQUEZ"
    ],
    'sexto': [
        "GUADALUPE AIMAR", "JUAN CRUZ ANTONELLO VEGA", "SANTINO ARNOLETTO FERRERO",
        "ANA PAULA BALDONCINI", "LOLA DE LOURDES BLANGINO", "VICTORIA LUZ BORTOLINI",
        "BAUTISTA BROMBIN BENEDETTI", "FERNANDO CACERES", "IGNACIO DANIEL CAMPANA",
        "DELFINA DAFNE CARBAJAL", "ALMA CAROLINI", "CHIARA COMBA GALVAGNO",
        "LOURDES CRISTALLI", "RAMIRO CRISTALLI", "SEBASTIAN DAVICO FLAUMER",
        "CHIARA DUARTE CUEVA", "JUAN CRUZ FANTONI", "LUCÍA MARÍA FRARESSO",
        "VICTORIA FRARESSO", "LORENZO MALIZIA MACAGNO", "AZUL MORENA MATTIA",
        "EMILIA MURATURE", "JUANITA MUÑOZ VERDICCHIO", "LUCIA SCHERMA MARCHEGIANI",
        "CATALINA VICENTE SORIA", "SANTIAGO VILLARREAL", "MAGALI WALKER",
        "MARTINA BELÉN ZORRILLA", "LOURDES PAULINA ZUPPA"
    ]
}

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
    alumnos = alumnos_por_anio.get(anio, [])
    
    votos_archivo = f"votos_{anio}.json" if anio else "votos.json"
    votos = cargar_json_seguro(votos_archivo)
    
    ya_votaron = set(votos.keys())
    return render_template("home.html", 
                         alumnos=alumnos, 
                         ya_votaron=ya_votaron, 
                         anio=anio, 
                         alumnos_por_anio=alumnos_por_anio,
                         usuario=session.get('usuario'),
                         rol=session.get('rol'))

@app.route('/votar/<anio>/<nombre>', methods=['GET', 'POST'])
@login_required
def votar(anio, nombre):
    # Verificar que el alumno pertenece al año
    alumnos = alumnos_por_anio.get(anio, [])
    if nombre not in alumnos:
        flash('Alumno no encontrado en este año', 'error')
        return redirect(url_for('home', anio=anio))
    
    # Cargar votos existentes
    archivo_votos = f'votos_{anio}.json'
    votos = cargar_json_seguro(archivo_votos)
    
    if request.method == 'GET':
        # Verificar si ya votó
        if nombre in votos:
            flash('Ya has completado tu votación', 'info')
            return redirect(url_for('home', anio=anio))
        
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
    alumnos_a_evaluar = session.get(f'alumnos_evaluar_{anio}_{nombre}', [])
    
    if not alumnos_a_evaluar:
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
            # Tomar solo el primer bloqueado (debería ser solo uno por el JavaScript)
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
    
    # Guardar en el archivo de votos
    votos[nombre] = voto_data
    guardar_json_seguro(archivo_votos, votos)
    
    # Limpiar la sesión
    session.pop(f'alumnos_evaluar_{anio}_{nombre}', None)
    
    flash('¡Votación registrada exitosamente!', 'success')
    return redirect(url_for('home', anio=anio))

@app.route("/procesar_voto", methods=["POST"])
@login_required
def procesar_voto():
    nombre = request.form.get('nombre')
    anio = request.form.get('anio')
    
    try:
        if not anio or anio not in alumnos_por_anio:
            flash("Año no válido", "error")
            return redirect(url_for('home'))
        
        asignaciones = asignaciones_por_anio.get(anio, {})
        opciones = asignaciones.get(nombre, [])
        
        if not opciones:
            flash("No se encontraron opciones para este alumno", "error")
            return redirect(url_for('home', anio=anio))
        
        # Verificar si ya votó
        votos_archivo = f"votos_{anio}.json"
        votos = cargar_json_seguro(votos_archivo)
        
        if nombre in votos:
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
        
        # Guardar voto
        voto_data = {
            'calificaciones': calificaciones,
            'bloqueado': alumno_bloqueado if alumno_bloqueado else None,
            'timestamp': str(os.times().elapsed)
        }
        
        votos[nombre] = voto_data
        
        if guardar_json_seguro(votos_archivo, votos):
            flash(f"✅ Voto de {nombre} registrado exitosamente!", "success")
        else:
            flash("Error al guardar el voto", "error")
            
        return redirect(url_for("home", anio=anio))
        
    except Exception as e:
        print(f"Error en procesar_voto: {e}")
        flash("Error al procesar el voto", "error")
        return redirect(url_for('home', anio=anio))

@app.route("/resultados")
@login_required  
def resultados():
    anio = request.args.get('anio', '')
    
    if not anio or anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    votos_archivo = f"votos_{anio}.json"
    votos = cargar_json_seguro(votos_archivo)
    
    if not votos:
        flash("No hay votos registrados para mostrar resultados", "warning")
        return redirect(url_for('home', anio=anio))
    
    emparejamientos = generar_emparejamientos(votos, alumnos_por_anio[anio])
    
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
        bancos_archivo = f"bancos_{anio}.json"
        bancos_data = cargar_json_seguro(bancos_archivo)
        
        if bancos_data and 'asignacion' in bancos_data:
            asignacion = bancos_data['asignacion']
            total_alumnos = bancos_data.get('total_alumnos', 0)
            filas = bancos_data.get('configuracion', {}).get('filas', math.ceil(total_alumnos / 6))
            
            flash(f"Asignación cargada desde archivo guardado", "info")
            
            return render_template("asignacion_bancos.html", 
                                 aula=asignacion,
                                 grupos=[],
                                 anio=anio,
                                 cols=3,  # ✅ 3 columnas
                                 filas=filas,
                                 total_alumnos=total_alumnos,
                                 guardado_disponible=True)
    
    # Cargar votos y generar emparejamientos
    votos_archivo = f"votos_{anio}.json"
    votos = cargar_json_seguro(votos_archivo)
    
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
            banco_numero = fila * cols + col + 1
            
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
    
    # Verificar si hay asignación guardada
    bancos_archivo = f"bancos_{anio}.json"
    guardado_disponible = os.path.exists(bancos_archivo)
    
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
    """Guarda la asignación actual de bancos"""
    anio = request.form.get('anio', '')
    asignacion_data = request.form.get('asignacion_data', '')
    
    if not anio or not asignacion_data:
        flash("Datos incompletos para guardar", "error")
        return redirect(url_for('home'))
    
    try:
        import json
        asignacion = json.loads(asignacion_data)
        
        # Preparar datos para guardar
        datos_guardar = {
            'asignacion': asignacion,
            'fecha_guardado': datetime.now().isoformat(),
            'total_alumnos': len([banco for banco in asignacion if banco.get('ocupado')]),
            'configuracion': {
                'filas': max(banco.get('fila', 1) for banco in asignacion),
                'columnas': 6
            }
        }
        
        # Guardar archivo
        bancos_archivo = f"bancos_{anio}.json"
        if guardar_json_seguro(bancos_archivo, datos_guardar):
            flash("✅ Asignación de bancos guardada exitosamente", "success")
        else:
            flash("❌ Error al guardar la asignación", "error")
            
    except Exception as e:
        print(f"Error guardando bancos: {e}")
        flash("❌ Error al procesar los datos", "error")
    
    return redirect(url_for('asignacion_bancos', anio=anio))

@app.route("/exportar_bancos/<anio>")
@role_required('administrador', 'psicopedagogo')
def exportar_bancos(anio):
    """Exporta la asignación de bancos a Excel"""
    bancos_archivo = f"bancos_{anio}.json"
    bancos_data = cargar_json_seguro(bancos_archivo)
    
    if not bancos_data or 'asignacion' not in bancos_data:
        flash("No hay asignación de bancos para exportar", "warning")
        return redirect(url_for('asignacion_bancos', anio=anio))
    
    try:
        import pandas as pd
        
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
    """Muestra el historial de asignaciones de bancos"""
    if anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    # Buscar todos los archivos de backup
    import glob
    pattern = f"bancos_{anio}*.json"
    archivos = glob.glob(pattern)
    
    historial = []
    for archivo in archivos:
        data = cargar_json_seguro(archivo)
        if data:
            historial.append({
                'archivo': archivo,
                'fecha': data.get('fecha_creacion', 'N/A'),
                'usuario': data.get('usuario_creador', 'N/A'),
                'total_alumnos': data.get('total_alumnos', 0)
            })
    
    # Ordenar por fecha (más reciente primero)
    historial.sort(key=lambda x: x['fecha'], reverse=True)
    
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
            'fecha_modificacion': datetime.now().isoformat(),
            'usuario_modificacion': session.get('usuario')
        }
        
        if guardar_json_seguro('config_aula.json', config):
            flash("Configuración del aula guardada exitosamente", "success")
        else:
            flash("Error al guardar configuración", "error")
    
    # Cargar configuración actual
    config_actual = cargar_json_seguro('config_aula.json')
    
    return render_template("configuracion_aula.html",
                         config=config_actual)

@app.route("/estadisticas/<anio>")
@role_required('administrador', 'psicopedagogo')
def estadisticas(anio):
    """Muestra estadísticas detalladas de votación"""
    if anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    votos_archivo = f"votos_{anio}.json"
    votos = cargar_json_seguro(votos_archivo)
    
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
        ratings = datos.get('ratings', {})
        bloqueado = datos.get('bloqueado')
        
        total_ratings += len(ratings)
        if bloqueado:
            total_bloqueos += 1
            bloqueos_recibidos[bloqueado] += 1
        
        for evaluado, puntuacion in ratings.items():
            distribución_ratings[puntuacion] += 1
            puntuaciones_recibidas[evaluado].append(puntuacion)
    
    # Detectar bloqueos mutuos
    for votante, datos in votos.items():
        bloqueado = datos.get('bloqueado')
        if bloqueado and bloqueado in votos:
            datos_bloqueado = votos[bloqueado]
            if datos_bloqueado.get('bloqueado') == votante:
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
    }
    
    return render_template("estadisticas.html", **estadisticas_data)
# Agrega esta ruta antes del if __name__ == "__main__":

@app.route("/reset_votos", methods=["POST"])
@role_required('administrador')
def reset_votos():
    """Resetea todos los votos de un año específico - SOLO ADMINISTRADORES"""
    anio = request.form.get('anio', '')
    
    if not anio or anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    # Confirmación de seguridad
    confirmacion = request.form.get('confirmacion', '')
    if confirmacion != 'RESET':
        flash("Debes escribir 'RESET' para confirmar el borrado", "error")
        return redirect(url_for('home', anio=anio))
    
    try:
        # Archivo de votos
        votos_archivo = f"votos_{anio}.json"
        
        # Crear backup antes de borrar
        if os.path.exists(votos_archivo):
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_archivo = f"backup_votos_{anio}_{timestamp}.json"
            
            # Copiar archivo actual como backup
            import shutil
            shutil.copy2(votos_archivo, backup_archivo)
            
            # Borrar archivo principal
            os.remove(votos_archivo)
            
            flash(f"✅ Votos de {anio} reseteados exitosamente. Backup guardado como {backup_archivo}", "success")
        else:
            flash(f"No había votos para resetear en {anio}", "info")
        
        # También resetear bancos si existen
        bancos_archivo = f"bancos_{anio}.json"
        if os.path.exists(bancos_archivo):
            backup_bancos = f"backup_bancos_{anio}_{timestamp}.json"
            shutil.copy2(bancos_archivo, backup_bancos)
            os.remove(bancos_archivo)
            flash(f"También se resetearon las asignaciones de bancos", "info")
            
    except Exception as e:
        print(f"Error en reset_votos: {e}")
        flash("Error al resetear los votos", "error")
    
    return redirect(url_for('home', anio=anio))

@app.route("/exportar_votos/<anio>")
@role_required('administrador', 'psicopedagogo')
def exportar_votos(anio):
    """Exporta los votos de un año a Excel"""
    if anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    votos_archivo = f"votos_{anio}.json"
    votos = cargar_json_seguro(votos_archivo)
    
    if not votos:
        flash("No hay votos para exportar", "warning")
        return redirect(url_for('home', anio=anio))
    
    try:
        # Crear datos para Excel
        datos_excel = []
        for votante, datos in votos.items():
            ratings = datos.get('ratings', {})
            bloqueado = datos.get('bloqueado', '')
            fecha = datos.get('fecha', '')
            ip = datos.get('ip', '')
            
            for evaluado, puntuacion in ratings.items():
                datos_excel.append({
                    'Votante': votante,
                    'Evaluado': evaluado,
                    'Puntuacion': puntuacion,
                    'Bloqueado_por_Votante': bloqueado,
                    'Fecha_Voto': fecha[:19] if fecha else '',
                    'IP_Address': ip
                })
        
        # Crear DataFrame
        import pandas as pd
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
# Tu if __name__ == "__main__": va aquí
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

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