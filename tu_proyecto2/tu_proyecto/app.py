from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import json
import os
import math
from functools import wraps
from collections import Counter, defaultdict

app = Flask(__name__)
app.secret_key = 'puertas_del_sol_secret_key_2024'

# Usuarios con roles
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

# Decorador para requerir login
def login_required(f):
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

@app.route("/votar/<nombre>")
@login_required
def votar(nombre):
    anio = request.args.get('anio', '')
    if not anio or anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    asignaciones = asignaciones_por_anio.get(anio, {})
    alumnos = alumnos_por_anio.get(anio, [])
    
    if nombre not in alumnos:
        flash("Alumno no encontrado", "error")
        return redirect(url_for('home', anio=anio))
    
    # Verificar si ya votó
    votos_archivo = f"votos_{anio}.json"
    votos = cargar_json_seguro(votos_archivo)
    
    if nombre in votos:
        flash(f"{nombre} ya ha votado", "warning")
        return redirect(url_for('home', anio=anio))
    
    return render_template("votar.html", 
                         nombre=nombre, 
                         opciones=asignaciones.get(nombre, []), 
                         alumnos=alumnos, 
                         anio=anio)

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
    anio = request.args.get('anio', 'sexto')
    votos_archivo = f"votos_{anio}.json"
    
    votos = cargar_json_seguro(votos_archivo)
    
    if not votos:
        flash("No hay votos registrados para este año", "warning")
        return redirect(url_for('home', anio=anio))
    
    # Obtener TODOS los alumnos del año
    todos_alumnos = set(alumnos_por_anio.get(anio, []))
    disponibles = todos_alumnos.copy()
    emparejamientos = []
    
    # Extraer solo las calificaciones para compatibilidad
    calificaciones_simples = {}
    for alumno, datos in votos.items():
        if isinstance(datos, dict) and 'calificaciones' in datos:
            calificaciones_simples[alumno] = datos['calificaciones']
        else:
            # Compatibilidad con formato anterior
            calificaciones_simples[alumno] = datos
    
    # Fase 1: Buscar emparejamientos con votos mutuos
    while len(disponibles) > 1:
        mejor_nivel = 0
        mejor_par = None
        
        for a1 in disponibles:
            for a2 in disponibles:
                if a1 != a2:
                    if (a1 in calificaciones_simples and a2 in calificaciones_simples.get(a1, {}) and 
                        a2 in calificaciones_simples and a1 in calificaciones_simples.get(a2, {})):
                        nivel = min(calificaciones_simples[a1][a2], calificaciones_simples[a2][a1])
                        if nivel > mejor_nivel:
                            mejor_nivel = nivel
                            mejor_par = (a1, a2)
        
        if mejor_par:
            emparejamientos.append(list(mejor_par))
            disponibles.remove(mejor_par[0])
            disponibles.remove(mejor_par[1])
        else:
            break
    
    # Fase 2: Emparejar alumnos restantes
    while len(disponibles) > 1:
        mejor_nivel = 0
        mejor_par = None
        
        for a1 in disponibles:
            for a2 in disponibles:
                if a1 != a2:
                    nivel = 0
                    if a1 in calificaciones_simples and a2 in calificaciones_simples.get(a1, {}):
                        nivel = max(nivel, calificaciones_simples[a1][a2])
                    if a2 in calificaciones_simples and a1 in calificaciones_simples.get(a2, {}):
                        nivel = max(nivel, calificaciones_simples[a2][a1])
                    
                    if nivel > mejor_nivel:
                        mejor_nivel = nivel
                        mejor_par = (a1, a2)
        
        if mejor_par:
            emparejamientos.append(list(mejor_par))
            disponibles.remove(mejor_par[0])
            disponibles.remove(mejor_par[1])
        else:
            if len(disponibles) >= 2:
                primeros_dos = list(disponibles)[:2]
                emparejamientos.append(primeros_dos)
                disponibles.remove(primeros_dos[0])
                disponibles.remove(primeros_dos[1])
            break
    
    # Fase 3: Agregar alumno restante
    if len(disponibles) == 1 and emparejamientos:
        emparejamientos[-1].append(list(disponibles)[0])
    elif len(disponibles) > 0:
        if emparejamientos:
            emparejamientos[-1].extend(list(disponibles))
        else:
            emparejamientos.append(list(disponibles))
    
    return render_template("resultados.html", 
                         emparejamientos=emparejamientos, 
                         anio=anio)

@app.route("/asignacion_bancos")
@login_required
def asignacion_bancos():
    anio = request.args.get('anio', '')
    regenerar = request.args.get('regenerar', 'false') == 'true'
    
    if not anio or anio not in alumnos_por_anio:
        flash("Año no válido", "error")
        return redirect(url_for('home'))
    
    # Obtener grupos formados (usando la misma lógica que resultados)
    votos_archivo = f"votos_{anio}.json"
    votos = cargar_json_seguro(votos_archivo)
    grupos = []
    
    if votos:
        # Extraer solo las calificaciones para compatibilidad
        calificaciones_simples = {}
        for alumno, datos in votos.items():
            if isinstance(datos, dict) and 'calificaciones' in datos:
                calificaciones_simples[alumno] = datos['calificaciones']
            else:
                calificaciones_simples[alumno] = datos
        
        # Usar el mismo algoritmo que en resultados
        todos_alumnos = set(alumnos_por_anio.get(anio, []))
        disponibles = todos_alumnos.copy()
        
        # Fase 1: Buscar emparejamientos con votos mutuos
        while len(disponibles) > 1:
            mejor_nivel = 0
            mejor_par = None
            
            for a1 in disponibles:
                for a2 in disponibles:
                    if a1 != a2:
                        if (a1 in calificaciones_simples and a2 in calificaciones_simples.get(a1, {}) and 
                            a2 in calificaciones_simples and a1 in calificaciones_simples.get(a2, {})):
                            nivel = min(calificaciones_simples[a1][a2], calificaciones_simples[a2][a1])
                            if nivel > mejor_nivel:
                                mejor_nivel = nivel
                                mejor_par = (a1, a2)
            
            if mejor_par:
                grupos.append(list(mejor_par))
                disponibles.remove(mejor_par[0])
                disponibles.remove(mejor_par[1])
            else:
                break
        
        # Fase 2: Emparejar alumnos restantes
        while len(disponibles) > 1:
            mejor_nivel = 0
            mejor_par = None
            
            for a1 in disponibles:
                for a2 in disponibles:
                    if a1 != a2:
                        nivel = 0
                        if a1 in calificaciones_simples and a2 in calificaciones_simples.get(a1, {}):
                            nivel = max(nivel, calificaciones_simples[a1][a2])
                        if a2 in calificaciones_simples and a1 in calificaciones_simples.get(a2, {}):
                            nivel = max(nivel, calificaciones_simples[a2][a1])
                        
                        if nivel > mejor_nivel:
                            mejor_nivel = nivel
                            mejor_par = (a1, a2)
            
            if mejor_par:
                grupos.append(list(mejor_par))
                disponibles.remove(mejor_par[0])
                disponibles.remove(mejor_par[1])
            else:
                if len(disponibles) >= 2:
                    primeros_dos = list(disponibles)[:2]
                    grupos.append(primeros_dos)
                    disponibles.remove(primeros_dos[0])
                    disponibles.remove(primeros_dos[1])
                break
        
        # Fase 3: Agregar alumnos restantes
        if len(disponibles) == 1 and grupos:
            grupos[-1].append(list(disponibles)[0])
        elif len(disponibles) > 0:
            if grupos:
                grupos[-1].extend(list(disponibles))
            else:
                grupos.append(list(disponibles))
    
    # Si no hay votos, usar todos los alumnos sin agrupar
    if not grupos:
        alumnos_lista = alumnos_por_anio.get(anio, [])
        grupos = [[alumno] for alumno in alumnos_lista]
    
    # Calcular disposición del aula: 6 bancos por fila
    total_alumnos = sum(len(grupo) for grupo in grupos)
    filas = math.ceil(total_alumnos / 6)
    
    # Generar asignación aleatoria de bancos
    if regenerar:
        import time
        random.seed(int(time.time()))
    else:
        random.seed(42)
    
    # Crear lista plana de todos los alumnos manteniendo grupos juntos
    alumnos_ordenados = []
    grupo_asignado = {}
    
    for i, grupo in enumerate(grupos):
        random.shuffle(grupo)
        for alumno in grupo:
            alumnos_ordenados.append(alumno)
            grupo_asignado[alumno] = i + 1
    
    random.shuffle(alumnos_ordenados)
    
    # Crear array de bancos
    total_bancos = filas * 6
    aula = []
    
    for i in range(total_bancos):
        if i < len(alumnos_ordenados):
            alumno = alumnos_ordenados[i]
            aula.append({
                'alumno': alumno,
                'grupo': grupo_asignado.get(alumno, 0),
                'ocupado': True
            })
        else:
            aula.append({
                'alumno': '',
                'grupo': 0,
                'ocupado': False
            })
    
    return render_template("asignacion_bancos.html", 
                         aula=aula,
                         grupos=grupos,
                         anio=anio,
                         cols=6,
                         filas=filas,
                         total_alumnos=total_alumnos)

@app.route("/estadisticas")
@role_required('administrador', 'psicopedagogo')
def estadisticas():
    anio = request.args.get('anio', 'sexto')
    votos_archivo = f"votos_{anio}.json"
    
    votos = cargar_json_seguro(votos_archivo)
    
    if not votos:
        flash("No hay votos registrados para este año", "warning")
        return redirect(url_for('home', anio=anio))
    
    # Inicializar estadísticas
    alumnos_año = alumnos_por_anio.get(anio, [])
    total_alumnos = len(alumnos_año)
    total_votos = len(votos)
    
    # Contadores para estadísticas
    puntuaciones = defaultdict(list)  # {alumno: [lista de puntuaciones recibidas]}
    bloqueos = defaultdict(int)  # {alumno: cantidad de veces bloqueado}
    bloqueadores = []  # Lista de quién bloqueó a quién
    votaron = list(votos.keys())
    no_votaron = [a for a in alumnos_año if a not in votaron]
    
    # Procesar votos
    for votante, datos in votos.items():
        # Extraer datos según formato
        if isinstance(datos, dict) and 'calificaciones' in datos:
            calificaciones = datos['calificaciones']
            bloqueado = datos.get('bloqueado')
        else:
            # Formato anterior (solo calificaciones)
            calificaciones = datos
            bloqueado = None
        
        # Procesar calificaciones
        for evaluado, puntuacion in calificaciones.items():
            puntuaciones[evaluado].append(puntuacion)
        
        # Procesar bloqueos
        if bloqueado:
            bloqueos[bloqueado] += 1
            bloqueadores.append({'votante': votante, 'bloqueado': bloqueado})
    
    # Calcular estadísticas de popularidad
    mas_elegidos = []
    menos_elegidos = []
    promedios = {}
    
    for alumno in alumnos_año:
        if alumno in puntuaciones and puntuaciones[alumno]:
            promedio = sum(puntuaciones[alumno]) / len(puntuaciones[alumno])
            total_puntos = sum(puntuaciones[alumno])
            votos_recibidos = len(puntuaciones[alumno])
            
            promedios[alumno] = {
                'promedio': round(promedio, 2),
                'total_puntos': total_puntos,
                'votos_recibidos': votos_recibidos,
                'puntuaciones': sorted(puntuaciones[alumno], reverse=True)
            }
    
    # Ordenar por promedio (mayor = más elegido)
    alumnos_ordenados = sorted(promedios.items(), key=lambda x: x[1]['promedio'], reverse=True)
    
    if alumnos_ordenados:
        mas_elegidos = alumnos_ordenados[:5]  # Top 5
        menos_elegidos = alumnos_ordenados[-5:]  # Bottom 5
    
    # Estadísticas de bloqueos
    mas_bloqueados = sorted(bloqueos.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Estadísticas de participación
    porcentaje_participacion = (total_votos / total_alumnos * 100) if total_alumnos > 0 else 0
    
    # Análisis de reciprocidad
    reciprocidades = []
    calificaciones_simples = {}
    
    for alumno, datos in votos.items():
        if isinstance(datos, dict) and 'calificaciones' in datos:
            calificaciones_simples[alumno] = datos['calificaciones']
        else:
            calificaciones_simples[alumno] = datos
    
    for a1 in calificaciones_simples:
        for a2, punt1 in calificaciones_simples[a1].items():
            if a2 in calificaciones_simples and a1 in calificaciones_simples[a2]:
                punt2 = calificaciones_simples[a2][a1]
                reciprocidades.append({
                    'alumno1': a1,
                    'alumno2': a2,
                    'puntuacion1': punt1,
                    'puntuacion2': punt2,
                    'diferencia': abs(punt1 - punt2),
                    'promedio': (punt1 + punt2) / 2
                })
    
    # Mejores reciprocidades (menor diferencia, mayor promedio)
    mejores_reciprocidades = sorted(reciprocidades, 
                                  key=lambda x: (-x['promedio'], x['diferencia']))[:10]
    
    return render_template("estadisticas.html",
                         anio=anio,
                         total_alumnos=total_alumnos,
                         total_votos=total_votos,
                         porcentaje_participacion=round(porcentaje_participacion, 1),
                         mas_elegidos=mas_elegidos,
                         menos_elegidos=menos_elegidos,
                         mas_bloqueados=mas_bloqueados,
                         bloqueadores=bloqueadores,
                         votaron=votaron,
                         no_votaron=no_votaron,
                         mejores_reciprocidades=mejores_reciprocidades,
                         promedios=promedios)

@app.route("/reset_votos", methods=["POST"])
@login_required
def reset_votos():
    anio = request.form.get('anio', '')
    if anio:
        votos_archivo = f"votos_{anio}.json"
        if os.path.exists(votos_archivo):
            os.remove(votos_archivo)
        flash(f"Votos de {anio} año resetados exitosamente", "success")
    return redirect(url_for('home', anio=anio))

if __name__ == "__main__":
    print("=== SERVIDOR INICIADO ===")
    print("Accede a: http://localhost:5000")
    print("Usuarios disponibles:")
    for user, info in USUARIOS_DOCENTES.items():
        print(f"  {user} ({info['rol']}): {info['password']}")
    app.run(debug=True, host='0.0.0.0', port=5000)