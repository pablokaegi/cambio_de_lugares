from flask import Flask, render_template, request, redirect, url_for, flash

import random
import json
import os
import sqlite3
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'notas_secret_key'
# Guardamos votos
notas = {}
# Ruta para subir PDF de notas
@app.route("/subir_notas", methods=["POST"])
def subir_notas():
    global notas
    if 'notas_pdf' not in request.files:
        flash('No se seleccionó archivo.')
        return redirect(url_for('home'))
    file = request.files['notas_pdf']
    if file.filename == '':
        flash('No se seleccionó archivo.')
        return redirect(url_for('home'))
    import PyPDF2
    from io import BytesIO
    pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
    texto = ""
    for page in pdf_reader.pages:
        texto += page.extract_text() + "\n"
    # Intentar extraer notas: formato esperado "NOMBRE: NOTA" por línea
    notas_extraidas = {}
    for linea in texto.splitlines():
        partes = linea.split(":")
        if len(partes) == 2:
            nombre = partes[0].strip().upper()
            try:
                nota = float(partes[1].strip().replace(",","."))
                notas_extraidas[nombre] = nota
            except:
                continue
    if notas_extraidas:
        notas = notas_extraidas
        # Guardar temporalmente en sesión
        import pickle
        from flask import session
        session['notas_temp'] = pickle.dumps(notas_extraidas).hex()
        return render_template('confirmar_notas.html', notas=notas_extraidas)
    else:
        flash("No se encontraron notas válidas en el PDF.")
        return redirect(url_for('home'))

# Guardar la lista definitiva de alumnos y notas
@app.route('/guardar_notas', methods=['POST'])
def guardar_notas():
    import pickle
    from flask import session
    total = int(request.form['total'])
    nuevos = {}
    for i in range(total):
        if f'eliminar_{i}' in request.form:
            continue
        nombre = request.form[f'nombre_{i}'].strip().upper()
        try:
            nota = float(request.form[f'nota_{i}'])
        except:
            nota = 0
        nuevos[nombre] = nota
    global notas, alumnos, asignaciones
    notas = nuevos
    alumnos = list(nuevos.keys())
    random.seed(42)
    asignaciones = {alumno: random.sample([a for a in alumnos if a != alumno], 5) for alumno in alumnos}
    session.pop('notas_temp', None)
    flash(f'Alumnos y notas confirmados: {len(alumnos)} alumnos.')
    return redirect(url_for('home'))

# Inicializar base de datos SQLite
DB_PATH = 'registro_votos.db'
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS preferencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno TEXT,
        otro_alumno TEXT,
        puntuacion INTEGER,
        bloqueado BOOLEAN DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()
init_db()

# Lista de alumnos
alumnos = [
    "GUADALUPE IMAR", "JUAN CRUZ ANTONELLO VEGA", "SANTINO ARNOLETTO FERRERO",
    "ANA PAULA BALDONCINI", "LOLA DE LOURDES BLANGINO", "VICTORIA LUZ BORTOLINI",
    "BAUTISTA BROMBIN BENEDETTI", "FERNANDO CACERES", "IGNACIO DANIEL CAMPANA",
    "DELFINA DAFNE CARBAJAL", "ALMA CAROLINI", "CHIARA COMBA GALVAGNO",
    "LOURDES CRISTALLI", "RAMIRO CRISTALLI", "SEBASTIAN DAVICO FLAUMER",
    "CHIARA MARIA AYELEN DUARTE CUEVA", "JUAN CRUZ FANTONI", "LUCÍA MARÍA FRARESSO",
    "VICTORIA FRARESSO", "LORENZO MALIZIA MACAGNO", "AZUL MORENA MATTIA",
    "EMILIA MURATURE", "JUANITA MUÑOZ VERDICCHIO", "LUCIA SCHERMA MARCHEGIANI",
    "CATALINA VICENTE SORIA", "SANTIAGO VILLARREAL", "MAGALI WALKER",
    "MARTINA BELÉN ZORRILLA", "LOURDES PAULINA ZUPPA"
]

# Generamos asignaciones una vez
random.seed(42)
asignaciones = {
    alumno: random.sample([a for a in alumnos if a != alumno], 5)
    for alumno in alumnos
}

# Guardamos votos
if not os.path.exists("votos.json"):
    with open("votos.json", "w") as f:
        json.dump({}, f)

@app.route("/")
def home():
    with open("votos.json") as f:
        votos = json.load(f)
    ya_votaron = set(votos.keys())
    return render_template("home.html", alumnos=alumnos, ya_votaron=ya_votaron)

# Ruta para resetear votos
@app.route("/reset", methods=["POST"])
def reset():
    with open("votos.json", "w") as f:
        json.dump({}, f)
    return redirect(url_for("home"))

# Ruta para selección aleatoria
@app.route("/aleatorio", methods=["POST"])
def aleatorio():
    votos = {}
    for alumno in alumnos:
        votos[alumno] = {comp: random.randint(1, 5) for comp in asignaciones[alumno]}
    with open("votos.json", "w") as f:
        json.dump(votos, f)
    return redirect(url_for("resultados"))



@app.route("/votar/<nombre>", methods=["GET", "POST"])
def votar(nombre):
    with open("votos.json") as f:
        votos = json.load(f)

    if request.method == "POST":
        calificaciones = {}
        bloqueo = request.form.get('bloqueo', '')
        for compañero in asignaciones[nombre]:
            calificaciones[compañero] = int(request.form[compañero])
        # Validación: debe usar cada puntaje del 1 al 5 exactamente una vez
        valores = list(calificaciones.values())
        if sorted(valores) != [1, 2, 3, 4, 5]:
            error = "Debes asignar cada puntaje del 1 al 5 una sola vez entre tus compañeros."
            return render_template("votar.html", nombre=nombre, opciones=asignaciones[nombre], alumnos=alumnos, error=error)
        votos[nombre] = calificaciones
        with open("votos.json", "w") as f:
            json.dump(votos, f)
        # Guardar en base de datos
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for companero, punt in calificaciones.items():
            c.execute("INSERT INTO preferencias (alumno, otro_alumno, puntuacion, bloqueado, timestamp) VALUES (?, ?, ?, ?, ?)",
                      (nombre, companero, punt, 1 if companero == bloqueo else 0, datetime.now()))
        conn.commit()
        conn.close()
        return redirect(url_for("gracias", nombre=nombre))

    return render_template("votar.html", nombre=nombre, opciones=asignaciones[nombre], alumnos=alumnos)

# Página de agradecimiento
@app.route("/gracias/<nombre>")
def gracias(nombre):
    return render_template("gracias.html", nombre=nombre)

@app.route("/resultados")
def resultados():
    with open("votos.json") as f:
        votos = json.load(f)

    disponibles = set(votos.keys())
    emparejamientos = []

    while len(disponibles) > 1:
        mejor_nivel = 0
        mejor_par = None
        # Buscar el par con mayor nivel mutuo
        for a1 in disponibles:
            for a2 in disponibles:
                if a1 != a2 and a2 in votos[a1] and a1 in votos[a2]:
                    nivel = min(votos[a1][a2], votos[a2][a1])
                    if nivel > mejor_nivel:
                        mejor_nivel = nivel
                        mejor_par = (a1, a2)
        if mejor_par:
            emparejamientos.append(mejor_par)
            disponibles.remove(mejor_par[0])
            disponibles.remove(mejor_par[1])
        else:
            # Si no hay pares con votos mutuos, emparejar los dos primeros
            a1, a2 = list(disponibles)[:2]
            emparejamientos.append((a1, a2))
            disponibles.remove(a1)
            disponibles.remove(a2)

    if len(disponibles) == 3:
        trio = list(disponibles)
        emparejamientos.append((trio[0], trio[1], trio[2]))
    elif len(disponibles) == 2:
        duo = list(disponibles)
        emparejamientos.append((duo[0], duo[1]))
    # Si queda 1, lo suma al último grupo de 2 para formar un trío
    elif len(disponibles) == 1 and len(emparejamientos) > 0:
        ultimo = emparejamientos.pop()
        solo = list(disponibles)[0]
        if len(ultimo) == 2:
            emparejamientos.append((ultimo[0], ultimo[1], solo))
        else:
            emparejamientos.append(ultimo)

    return render_template("resultados.html", emparejamientos=emparejamientos)

if __name__ == "__main__":
    app.run(debug=True)
