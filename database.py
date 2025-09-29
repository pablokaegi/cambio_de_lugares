import sqlite3
import json
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='alumnos_app.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla para votos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS votos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anio TEXT NOT NULL,
                    alumno TEXT NOT NULL,
                    calificaciones TEXT NOT NULL,
                    alumno_bloqueado TEXT,
                    timestamp TEXT NOT NULL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(anio, alumno)
                )
            ''')
            
            # Tabla para asignaciones de bancos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS asignaciones_bancos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anio TEXT NOT NULL,
                    nombre_asignacion TEXT NOT NULL,
                    asignacion_data TEXT NOT NULL,
                    total_alumnos INTEGER,
                    filas INTEGER,
                    columnas INTEGER,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    es_actual BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Tabla para rankings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rankings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anio TEXT NOT NULL,
                    alumno TEXT NOT NULL,
                    puntos_totales INTEGER DEFAULT 0,
                    nivel INTEGER DEFAULT 1,
                    badges TEXT DEFAULT '[]',
                    partidas_jugadas INTEGER DEFAULT 0,
                    fecha_ultimo_voto TEXT,
                    trivia_preguntas_respondidas INTEGER DEFAULT 0,
                    trivia_preguntas_correctas INTEGER DEFAULT 0,
                    trivia_categorias_dominadas TEXT DEFAULT '[]',
                    trivia_racha_actual INTEGER DEFAULT 0,
                    trivia_mejor_racha INTEGER DEFAULT 0,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(anio, alumno)
                )
            ''')
            
            # Agregar columnas nuevas si no existen (para bases de datos existentes)
            try:
                cursor.execute('ALTER TABLE rankings ADD COLUMN puntos_totales INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass  # Columna ya existe
            
            try:
                cursor.execute('ALTER TABLE rankings ADD COLUMN nivel INTEGER DEFAULT 1')
            except sqlite3.OperationalError:
                pass
                
            try:
                cursor.execute('ALTER TABLE rankings ADD COLUMN fecha_ultimo_voto TEXT')
            except sqlite3.OperationalError:
                pass
                
            try:
                cursor.execute('ALTER TABLE rankings ADD COLUMN trivia_preguntas_respondidas INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass
                
            try:
                cursor.execute('ALTER TABLE rankings ADD COLUMN trivia_preguntas_correctas INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass
                
            try:
                cursor.execute('ALTER TABLE rankings ADD COLUMN trivia_categorias_dominadas TEXT DEFAULT "[]"')
            except sqlite3.OperationalError:
                pass
                
            try:
                cursor.execute('ALTER TABLE rankings ADD COLUMN trivia_racha_actual INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass
                
            try:
                cursor.execute('ALTER TABLE rankings ADD COLUMN trivia_mejor_racha INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass
            
            # Tabla para configuración del aula
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracion_aula (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filas INTEGER NOT NULL,
                    columnas INTEGER NOT NULL,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def guardar_voto(self, anio, alumno, calificaciones, alumno_bloqueado=None, timestamp=None):
        """Guarda un voto en la base de datos"""
        if timestamp is None:
            timestamp = str(os.times().elapsed)
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO votos 
                    (anio, alumno, calificaciones, alumno_bloqueado, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (anio, alumno, json.dumps(calificaciones), alumno_bloqueado, timestamp))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error guardando voto: {e}")
                return False
    
    def cargar_votos(self, anio):
        """Carga todos los votos de un año"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT alumno, calificaciones, alumno_bloqueado, timestamp 
                FROM votos WHERE anio = ?
            ''', (anio,))
            
            votos = {}
            for row in cursor.fetchall():
                alumno, calificaciones_json, alumno_bloqueado, timestamp = row
                votos[alumno] = {
                    'calificaciones': json.loads(calificaciones_json),
                    'bloqueado': alumno_bloqueado,
                    'timestamp': timestamp
                }
            return votos
    
    def guardar_asignacion_bancos(self, anio, nombre_asignacion, asignacion_data, 
                                 total_alumnos, filas, columnas, es_actual=True):
        """Guarda una asignación de bancos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                # Si es actual, marcar las demás como no actuales
                if es_actual:
                    cursor.execute('''
                        UPDATE asignaciones_bancos 
                        SET es_actual = FALSE 
                        WHERE anio = ?
                    ''', (anio,))
                
                cursor.execute('''
                    INSERT INTO asignaciones_bancos 
                    (anio, nombre_asignacion, asignacion_data, total_alumnos, 
                     filas, columnas, es_actual)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (anio, nombre_asignacion, json.dumps(asignacion_data), 
                      total_alumnos, filas, columnas, es_actual))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error guardando asignación: {e}")
                return False
    
    def cargar_asignacion_bancos(self, anio, nombre_asignacion=None):
        """Carga una asignación de bancos específica o la actual"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if nombre_asignacion:
                cursor.execute('''
                    SELECT asignacion_data, total_alumnos, filas, columnas, fecha_creacion
                    FROM asignaciones_bancos 
                    WHERE anio = ? AND nombre_asignacion = ?
                    ORDER BY fecha_creacion DESC LIMIT 1
                ''', (anio, nombre_asignacion))
            else:
                cursor.execute('''
                    SELECT asignacion_data, total_alumnos, filas, columnas, fecha_creacion
                    FROM asignaciones_bancos 
                    WHERE anio = ? AND es_actual = TRUE
                    ORDER BY fecha_creacion DESC LIMIT 1
                ''', (anio,))
            
            row = cursor.fetchone()
            if row:
                asignacion_json, total_alumnos, filas, columnas, fecha_creacion = row
                return {
                    'asignacion': json.loads(asignacion_json),
                    'fecha_guardado': fecha_creacion,
                    'total_alumnos': total_alumnos,
                    'configuracion': {
                        'filas': filas,
                        'columnas': columnas
                    }
                }
            return {}
    
    def listar_asignaciones_bancos(self, anio):
        """Lista todas las asignaciones guardadas para un año"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT nombre_asignacion, total_alumnos, fecha_creacion, es_actual
                FROM asignaciones_bancos 
                WHERE anio = ?
                ORDER BY fecha_creacion DESC
            ''', (anio,))
            
            asignaciones = []
            for row in cursor.fetchall():
                nombre, total, fecha, es_actual = row
                asignaciones.append({
                    'nombre': nombre,
                    'total_alumnos': total,
                    'fecha': fecha,
                    'es_actual': bool(es_actual)
                })
            return asignaciones
    
    def actualizar_ranking_completo(self, anio, alumno, datos_ranking):
        """Actualiza o crea un registro completo de ranking"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO rankings 
                    (anio, alumno, puntos_totales, nivel, badges, partidas_jugadas,
                     fecha_ultimo_voto, trivia_preguntas_respondidas, trivia_preguntas_correctas,
                     trivia_categorias_dominadas, trivia_racha_actual, trivia_mejor_racha,
                     fecha_actualizacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    anio, alumno, 
                    datos_ranking.get('puntos_totales', 0),
                    datos_ranking.get('nivel', 1),
                    json.dumps(datos_ranking.get('badges', [])),
                    datos_ranking.get('partidas_jugadas', 0),
                    datos_ranking.get('fecha_ultimo_voto'),
                    datos_ranking.get('trivia_stats', {}).get('preguntas_respondidas', 0),
                    datos_ranking.get('trivia_stats', {}).get('preguntas_correctas', 0),
                    json.dumps(datos_ranking.get('trivia_stats', {}).get('categorias_dominadas', [])),
                    datos_ranking.get('trivia_stats', {}).get('racha_actual', 0),
                    datos_ranking.get('trivia_stats', {}).get('mejor_racha', 0)
                ))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error actualizando ranking completo: {e}")
                return False
    
    def obtener_ranking_alumno(self, anio, alumno):
        """Obtiene los datos de ranking de un alumno específico"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT puntos_totales, nivel, badges, partidas_jugadas, fecha_ultimo_voto,
                       trivia_preguntas_respondidas, trivia_preguntas_correctas, 
                       trivia_categorias_dominadas, trivia_racha_actual, trivia_mejor_racha
                FROM rankings WHERE anio = ? AND alumno = ?
            ''', (anio, alumno))
            
            row = cursor.fetchone()
            if row:
                return {
                    'puntos_totales': row[0] or 0,
                    'nivel': row[1] or 1,
                    'badges': json.loads(row[2]) if row[2] else [],
                    'partidas_jugadas': row[3] or 0,
                    'fecha_ultimo_voto': row[4],
                    'trivia_stats': {
                        'preguntas_respondidas': row[5] or 0,
                        'preguntas_correctas': row[6] or 0,
                        'categorias_dominadas': json.loads(row[7]) if row[7] else [],
                        'racha_actual': row[8] or 0,
                        'mejor_racha': row[9] or 0
                    }
                }
            else:
                # Devolver estructura por defecto si no existe
                return {
                    'puntos_totales': 0,
                    'nivel': 1,
                    'badges': [],
                    'partidas_jugadas': 0,
                    'fecha_ultimo_voto': None,
                    'trivia_stats': {
                        'preguntas_respondidas': 0,
                        'preguntas_correctas': 0,
                        'categorias_dominadas': [],
                        'racha_actual': 0,
                        'mejor_racha': 0
                    }
                }

    def actualizar_ranking(self, anio, alumno, puntos, badges, partidas_jugadas):
        """Actualiza el ranking de un alumno"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO rankings 
                    (anio, alumno, puntos, badges, partidas_jugadas)
                    VALUES (?, ?, ?, ?, ?)
                ''', (anio, alumno, puntos, json.dumps(badges), partidas_jugadas))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error actualizando ranking: {e}")
                return False
    
    def cargar_ranking(self, anio):
        """Carga el ranking completo de un año con toda la información"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT alumno, puntos_totales, nivel, badges, partidas_jugadas, fecha_ultimo_voto,
                       trivia_preguntas_respondidas, trivia_preguntas_correctas, 
                       trivia_categorias_dominadas, trivia_racha_actual, trivia_mejor_racha
                FROM rankings WHERE anio = ?
                ORDER BY puntos_totales DESC
            ''', (anio,))
            
            ranking = {}
            for row in cursor.fetchall():
                alumno = row[0]
                ranking[alumno] = {
                    'puntos_totales': row[1] or 0,
                    'nivel': row[2] or 1,
                    'badges': json.loads(row[3]) if row[3] else [],
                    'partidas_jugadas': row[4] or 0,
                    'fecha_ultimo_voto': row[5],
                    'trivia_stats': {
                        'preguntas_respondidas': row[6] or 0,
                        'preguntas_correctas': row[7] or 0,
                        'categorias_dominadas': json.loads(row[8]) if row[8] else [],
                        'racha_actual': row[9] or 0,
                        'mejor_racha': row[10] or 0
                    }
                }
            return ranking
    
    def borrar_rankings_anio(self, anio):
        """Borra todos los rankings de un año específico"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM rankings WHERE anio = ?', (anio,))
                rankings_borrados = cursor.rowcount
                conn.commit()
                return True, rankings_borrados
            except Exception as e:
                print(f"Error borrando rankings de {anio}: {e}")
                return False, 0
                
    def borrar_asignaciones_bancos_anio(self, anio):
        """Borra todas las asignaciones de bancos de un año específico"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM asignaciones_bancos WHERE anio = ?', (anio,))
                asignaciones_borradas = cursor.rowcount
                conn.commit()
                return True, asignaciones_borradas
            except Exception as e:
                print(f"Error borrando asignaciones de bancos de {anio}: {e}")
                return False, 0
    
    def guardar_configuracion_aula(self, config_dict):
        """Guarda la configuración completa del aula"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                # Crear tabla si no existe
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS configuracion_aula (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filas INTEGER,
                        columnas INTEGER,
                        trivia_obligatoria BOOLEAN DEFAULT TRUE,
                        configuracion_json TEXT,
                        fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Eliminar configuración anterior
                cursor.execute('DELETE FROM configuracion_aula')
                
                cursor.execute('''
                    INSERT INTO configuracion_aula (filas, columnas, trivia_obligatoria, configuracion_json)
                    VALUES (?, ?, ?, ?)
                ''', (
                    config_dict.get('filas_maximas', 6),
                    config_dict.get('columnas_por_fila', 6), 
                    config_dict.get('trivia_obligatoria', True),
                    json.dumps(config_dict)
                ))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error guardando configuración: {e}")
                return False
    
    def cargar_configuracion_aula(self):
        """Carga la configuración completa del aula"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Asegurar que la tabla existe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracion_aula (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filas INTEGER,
                    columnas INTEGER,
                    trivia_obligatoria BOOLEAN DEFAULT TRUE,
                    configuracion_json TEXT,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                SELECT filas, columnas, trivia_obligatoria, configuracion_json 
                FROM configuracion_aula 
                ORDER BY fecha_actualizacion DESC LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if row:
                base_config = {
                    'filas_maximas': row[0],
                    'columnas_por_fila': row[1], 
                    'trivia_obligatoria': bool(row[2])
                }
                
                # Agregar configuración adicional del JSON si existe
                if row[3]:
                    try:
                        json_config = json.loads(row[3])
                        base_config.update(json_config)
                    except:
                        pass
                        
                return base_config
            
            # Valores por defecto
            return {
                'filas_maximas': 6, 
                'columnas_por_fila': 6,
                'trivia_obligatoria': True
            }
    
    def obtener_votos_por_anio(self, anio):
        """Obtiene todos los votos de un año específico"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT alumno, calificaciones, alumno_bloqueado, timestamp
                FROM votos WHERE anio = ?
            ''', (anio,))
            
            votos = {}
            for row in cursor.fetchall():
                alumno, calificaciones_json, alumno_bloqueado, timestamp = row
                try:
                    calificaciones = json.loads(calificaciones_json)
                    votos[alumno] = {
                        'calificaciones': calificaciones,
                        'alumno_bloqueado': alumno_bloqueado,
                        'timestamp': timestamp
                    }
                except json.JSONDecodeError:
                    pass
            
            return votos
    
    def borrar_votos_anio(self, anio):
        """Borra TODOS los votos de un año específico de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar votos antes de borrar
                cursor.execute('SELECT COUNT(*) FROM votos WHERE anio = ?', (anio,))
                votos_borrados = cursor.fetchone()[0]
                
                # Borrar los votos
                cursor.execute('DELETE FROM votos WHERE anio = ?', (anio,))
                conn.commit()
                
                return True, votos_borrados
                
        except Exception as e:
            print(f"Error borrando votos del año {anio}: {e}")
            return False, 0
    
    def borrar_voto_alumno(self, anio, alumno):
        """Borra el voto de un alumno específico"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar si existe el voto
                cursor.execute('SELECT COUNT(*) FROM votos WHERE anio = ? AND alumno = ?', (anio, alumno))
                existe = cursor.fetchone()[0] > 0
                
                if existe:
                    # Borrar el voto
                    cursor.execute('DELETE FROM votos WHERE anio = ? AND alumno = ?', (anio, alumno))
                    conn.commit()
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"Error borrando voto de {alumno} en {anio}: {e}")
            return False

# Instancia global
db_manager = DatabaseManager()