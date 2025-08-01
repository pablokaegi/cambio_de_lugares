# App de Emparejamiento de Alumnos

Esta aplicación permite organizar grupos de alumnos según sus preferencias y notas, ideal para docentes y equipos psicopedagógicos.

## Características
- Importación de alumnos y notas desde PDF.
- Edición y confirmación de la lista de alumnos y sus notas antes de iniciar la votación.
- Votación anónima: cada alumno puntúa a 5 compañeros y puede bloquear a uno.
- Validación para evitar votos sesgados.
- Emparejamiento automático en grupos de 2 o 3, priorizando afinidad y evitando bloqueos.
- Registro de todas las votaciones y bloqueos en una base de datos SQLite.
- Exportación de estadísticas a Excel.
- Compatible con despliegue local y en Render.com.

## Uso
1. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
2. Ejecuta la app:
   ```
   python app.py
   ```
3. Accede a `http://localhost:5000` en tu navegador.
4. Sube el PDF de notas, confirma/edita la lista y comienza la votación.

## Despliegue en Render
- Incluye `Procfile` y `runtime.txt` para despliegue automático.
- Solo sube el proyecto a GitHub y conéctalo a Render.com.

## Estadísticas
- Usa `estadisticas.py` para ver o exportar los resultados de la base de datos.

---
Desarrollado para facilitar la integración social y académica en el aula.
