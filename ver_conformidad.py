"""Ver registros de conformidad usando el DatabaseManager unificado."""
from database import db_manager

registros = db_manager.obtener_conformidad()

if not registros:
    print("No hay registros de conformidad.")
else:
    print("Respuestas de la encuesta de conformidad:\n")
    for r in registros:
        print(f"Alumno: {r['alumno']}\tCompa\u00f1ero: {r['companero']}\tPuntaje: {r['puntaje']}\tM\u00e9todo: {r['metodo']}\tFecha: {r['timestamp']}")

