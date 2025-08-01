from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import json
import os
import math
from functools import wraps

app = Flask(__name__)
app.secret_key = 'puertas_del_sol_secret_key_2024'

# Usuarios y contraseñas de docentes
USUARIOS_DOCENTES = {
    'admin': 'admin123',
    'director': 'director2024',
    'coordinador': 'coord123',
    'profesor1': 'prof2024',
    'secretaria': 'secre123'
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

# Generar asignaciones por año
asignaciones_por_anio = {}
for anio, alumnos in alumnos_por_anio.items():
    random.seed(42)
    asignaciones_por_anio[anio] = {}
    
    for alumno in alumnos:
        otros_alumnos = [a for a in alumnos if a != alumno]
        num_opciones = min(5, len(otros_alumnos))
        
        if num_opciones > 0:
            asignaciones_por_anio[anio][alumno] = random.sample(otros_alumnos, num_opciones)
        else:
            asignaciones_por_anio[anio][alumno] = []

# Reemplaza la función calcular_disposicion_aula con esta:

def calcular_disposicion_aula(num_alumnos):
    """Calcula la disposición del aula: 6 bancos por fila"""
    # Cada fila tiene 6 bancos (3 columnas de 2 bancos cada una)
    filas = math.ceil(num_alumnos / 6)
    return 6, filas  # 6 bancos por fila, número de filas calculado

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
        
        if usuario in USUARIOS_DOCENTES and USUARIOS_DOCENTES[usuario] == password:
            session['logged_in'] = True
            session['usuario'] = usuario
            flash(f"¡Bienvenido/a {usuario}!", "success")
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
    if os.path.exists(votos_archivo):
        with open(votos_archivo, encoding='utf-8') as f:
            votos = json.load(f)
    else:
        votos = {}
    
    ya_votaron = set(votos.keys())
    return render_template("home.html", 
                         alumnos=alumnos, 
                         ya_votaron=ya_votaron, 
                         anio=anio, 
                         alumnos_por_anio=alumnos_por_anio,
                         usuario=session.get('usuario'))

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
        
        calificaciones = {}
        
        # Recoger calificaciones
        for compañero in opciones:
            calificacion = request.form.get(compañero, '')
            if calificacion:
                calificaciones[compañero] = int(calificacion)
            else:
                flash(f"Falta calificación para {compañero}", "error")
                return redirect(url_for('votar', nombre=nombre, anio=anio))
        
        # Validación
        if len(calificaciones) != len(opciones):
            flash("Debes calificar a todos tus compañeros", "error")
            return redirect(url_for('votar', nombre=nombre, anio=anio))
        
        valores = list(calificaciones.values())
        valores_esperados = list(range(1, len(opciones) + 1))
        
        if sorted(valores) != valores_esperados:
            flash(f"Debes asignar cada puntaje del 1 al {len(opciones)} una sola vez", "error")
            return redirect(url_for('votar', nombre=nombre, anio=anio))
        
        # Guardar en archivo JSON
        votos_archivo = f"votos_{anio}.json"
        votos = {}
        
        if os.path.exists(votos_archivo):
            with open(votos_archivo, 'r', encoding='utf-8') as f:
                votos = json.load(f)
        
        votos[nombre] = calificaciones
        
        with open(votos_archivo, "w", encoding='utf-8') as f:
            json.dump(votos, f, ensure_ascii=False, indent=2)
        
        flash(f"✅ Voto de {nombre} registrado exitosamente!", "success")
        return redirect(url_for("home", anio=anio))
        
    except Exception as e:
        print(f"Error en procesar_voto: {e}")
        flash(f"Error al procesar el voto", "error")
        return redirect(url_for('home', anio=anio))

@app.route("/resultados")
@login_required
def resultados():
    anio = request.args.get('anio', 'sexto')
    votos_archivo = f"votos_{anio}.json"
    
    if not os.path.exists(votos_archivo):
        flash("No hay votos registrados para este año", "warning")
        return redirect(url_for('home', anio=anio))
    
    with open(votos_archivo, encoding='utf-8') as f:
        votos = json.load(f)
    
    # Obtener TODOS los alumnos del año, no solo los que votaron
    todos_alumnos = set(alumnos_por_anio.get(anio, []))
    disponibles = todos_alumnos.copy()
    emparejamientos = []
    
    # Fase 1: Buscar emparejamientos con votos mutuos
    while len(disponibles) > 1:
        mejor_nivel = 0
        mejor_par = None
        
        for a1 in disponibles:
            for a2 in disponibles:
                if a1 != a2:
                    # Verificar si ambos votaron y se calificaron mutuamente
                    if (a1 in votos and a2 in votos.get(a1, {}) and 
                        a2 in votos and a1 in votos.get(a2, {})):
                        nivel = min(votos[a1][a2], votos[a2][a1])
                        if nivel > mejor_nivel:
                            mejor_nivel = nivel
                            mejor_par = (a1, a2)
        
        if mejor_par:
            emparejamientos.append(list(mejor_par))
            disponibles.remove(mejor_par[0])
            disponibles.remove(mejor_par[1])
        else:
            break
    
    # Fase 2: Emparejar alumnos restantes (incluso sin votos mutuos)
    while len(disponibles) > 1:
        mejor_nivel = 0
        mejor_par = None
        
        # Buscar cualquier conexión unidireccional
        for a1 in disponibles:
            for a2 in disponibles:
                if a1 != a2:
                    nivel = 0
                    # Si a1 calificó a a2
                    if a1 in votos and a2 in votos.get(a1, {}):
                        nivel = max(nivel, votos[a1][a2])
                    # Si a2 calificó a a1
                    if a2 in votos and a1 in votos.get(a2, {}):
                        nivel = max(nivel, votos[a2][a1])
                    
                    if nivel > mejor_nivel:
                        mejor_nivel = nivel
                        mejor_par = (a1, a2)
        
        if mejor_par:
            emparejamientos.append(list(mejor_par))
            disponibles.remove(mejor_par[0])
            disponibles.remove(mejor_par[1])
        else:
            # Si no hay conexiones, emparejar los dos primeros
            if len(disponibles) >= 2:
                primeros_dos = list(disponibles)[:2]
                emparejamientos.append(primeros_dos)
                disponibles.remove(primeros_dos[0])
                disponibles.remove(primeros_dos[1])
            break
    
    # Fase 3: Agregar alumno restante al último grupo
    if len(disponibles) == 1 and emparejamientos:
        emparejamientos[-1].append(list(disponibles)[0])
        disponibles.clear()
    elif len(disponibles) >= 3:
        # Si quedan 3 o más, hacer un grupo
        emparejamientos.append(list(disponibles))
        disponibles.clear()
    elif len(disponibles) > 0:
        # Si queda alguno, agregarlo al último grupo o crear uno nuevo
        if emparejamientos:
            emparejamientos[-1].extend(list(disponibles))
        else:
            emparejamientos.append(list(disponibles))
    
    return render_template("resultados.html", 
                         emparejamientos=emparejamientos, 
                         anio=anio)

# Reemplaza la función asignacion_bancos completa con esta:

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
    grupos = []
    
    if os.path.exists(votos_archivo):
        with open(votos_archivo, encoding='utf-8') as f:
            votos = json.load(f)
        
        # Usar el mismo algoritmo que en resultados para obtener grupos
        todos_alumnos = set(alumnos_por_anio.get(anio, []))
        disponibles = todos_alumnos.copy()
        grupos = []
        
        # Fase 1: Buscar emparejamientos con votos mutuos
        while len(disponibles) > 1:
            mejor_nivel = 0
            mejor_par = None
            
            for a1 in disponibles:
                for a2 in disponibles:
                    if a1 != a2:
                        if (a1 in votos and a2 in votos.get(a1, {}) and 
                            a2 in votos and a1 in votos.get(a2, {})):
                            nivel = min(votos[a1][a2], votos[a2][a1])
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
                        if a1 in votos and a2 in votos.get(a1, {}):
                            nivel = max(nivel, votos[a1][a2])
                        if a2 in votos and a1 in votos.get(a2, {}):
                            nivel = max(nivel, votos[a2][a1])
                        
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
    filas = math.ceil(total_alumnos / 6)  # 6 bancos por fila
    
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
        random.shuffle(grupo)  # Mezclar dentro del grupo
        for alumno in grupo:
            alumnos_ordenados.append(alumno)
            grupo_asignado[alumno] = i + 1
    
    # Mezclar la lista completa para distribución aleatoria
    random.shuffle(alumnos_ordenados)
    
    # Crear array de bancos (lista plana)
    total_bancos = filas * 6  # 6 bancos por fila
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
                         cols=6,  # Siempre 6 bancos por fila
                         filas=filas,
                         total_alumnos=total_alumnos)

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
    app.run(debug=True, host='0.0.0.0', port=5000)