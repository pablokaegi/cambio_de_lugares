import sqlite3

DB_PATH = 'alumnos_app.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
try:
    c.execute('''SELECT alumno, companero, puntaje, metodo, timestamp FROM conformidad''')
    registros = c.fetchall()
except sqlite3.OperationalError as e:
    print(f"Error accediendo a la tabla conformidad: {e}")
    registros = []
finally:
    conn.close()

if not registros:
    print("No hay registros de conformidad.")
else:
    print("Respuestas de la encuesta de conformidad:\n")
    for alumno, companero, puntaje, metodo, timestamp in registros:
        print(f"Alumno: {alumno}\tCompañero: {companero}\tPuntaje: {puntaje}\tMétodo: {metodo}\tFecha: {timestamp}")

