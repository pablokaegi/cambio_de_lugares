"""
DatabaseManager con soporte dual: SQLite (dev local) y MySQL (produccion cPanel).
Detecta automaticamente el backend segun variables de entorno.

  - Si DB_HOST esta definido en .env -> usa MySQL (pymysql)
  - Si no -> usa SQLite (archivo local alumnos_app.db)
"""
import os
import json
from datetime import datetime
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.db_host = os.environ.get('DB_HOST', '')

        if self.db_host:
            # -- MySQL ---------------------------------------------------
            self.backend = 'mysql'
            import pymysql
            import pymysql.cursors
            self._pymysql = pymysql
            self._db_config = {
                'host': self.db_host,
                'user': os.environ.get('DB_USER', ''),
                'password': os.environ.get('DB_PASSWORD', ''),
                'database': os.environ.get('DB_NAME', ''),
                'charset': 'utf8mb4',
                'cursorclass': pymysql.cursors.Cursor,
                'autocommit': False,
            }
            print(f"[DB] MySQL -> {self._db_config['database']}@{self.db_host}")
        else:
            # -- SQLite --------------------------------------------------
            self.backend = 'sqlite'
            import sqlite3
            self._sqlite3 = sqlite3
            self.db_path = os.environ.get('DB_PATH', 'alumnos_app.db')
            print(f"[DB] SQLite -> {self.db_path}")

        self.init_database()

    # ==================================================================
    #  Helpers de conexion y SQL
    # ==================================================================
    @contextmanager
    def _connect(self):
        """Context manager: abre conexion, auto-commit / rollback, cierra."""
        if self.backend == 'mysql':
            conn = self._pymysql.connect(**self._db_config)
        else:
            conn = self._sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _ph(self, sql):
        """Convierte placeholders: ? -> %s si el backend es MySQL."""
        if self.backend == 'mysql':
            return sql.replace('?', '%s')
        return sql

    def _column_exists(self, cursor, table, column):
        if self.backend == 'mysql':
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_schema = %s AND table_name = %s AND column_name = %s",
                (self._db_config['database'], table, column),
            )
            return cursor.fetchone()[0] > 0
        else:
            cursor.execute(f"PRAGMA table_info({table})")
            return column in [row[1] for row in cursor.fetchall()]

    def _add_column_safe(self, cursor, table, column, definition):
        """ALTER TABLE ADD COLUMN que no falla si ya existe."""
        if not self._column_exists(cursor, table, column):
            try:
                cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')
            except Exception:
                pass

    # ==================================================================
    #  Inicializacion (DDL + migraciones)
    # ==================================================================
    def init_database(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            if self.backend == 'mysql':
                self._ddl_mysql(cursor)
            else:
                self._ddl_sqlite(cursor)
            self._run_migrations(cursor)

    # -- DDL MySQL -----------------------------------------------------
    def _ddl_mysql(self, c):
        c.execute('''
            CREATE TABLE IF NOT EXISTS votos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                anio VARCHAR(50) NOT NULL,
                alumno VARCHAR(200) NOT NULL,
                calificaciones TEXT NOT NULL,
                alumno_bloqueado VARCHAR(200),
                timestamp VARCHAR(50) NOT NULL,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_voto (anio, alumno)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS asignaciones_bancos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                anio VARCHAR(50) NOT NULL,
                nombre_asignacion VARCHAR(200) NOT NULL,
                asignacion_data LONGTEXT NOT NULL,
                total_alumnos INT,
                filas INT,
                columnas INT,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                es_actual BOOLEAN DEFAULT FALSE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS rankings (
                id INT PRIMARY KEY AUTO_INCREMENT,
                anio VARCHAR(50) NOT NULL,
                alumno VARCHAR(200) NOT NULL,
                puntos_totales INT DEFAULT 0,
                nivel INT DEFAULT 1,
                badges TEXT,
                partidas_jugadas INT DEFAULT 0,
                fecha_ultimo_voto VARCHAR(50),
                trivia_preguntas_respondidas INT DEFAULT 0,
                trivia_preguntas_correctas INT DEFAULT 0,
                trivia_categorias_dominadas TEXT,
                trivia_racha_actual INT DEFAULT 0,
                trivia_mejor_racha INT DEFAULT 0,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uq_ranking (anio, alumno)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS configuracion_aula (
                id INT PRIMARY KEY AUTO_INCREMENT,
                filas INT NOT NULL DEFAULT 6,
                columnas INT NOT NULL DEFAULT 6,
                trivia_obligatoria BOOLEAN DEFAULT FALSE,
                configuracion_json TEXT,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS db_migrations (
                migration_id VARCHAR(100) PRIMARY KEY,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS conformidad (
                id INT PRIMARY KEY AUTO_INCREMENT,
                alumno VARCHAR(200) NOT NULL,
                companero VARCHAR(200) NOT NULL,
                puntaje INT NOT NULL,
                metodo VARCHAR(50) DEFAULT 'afinidad',
                timestamp VARCHAR(50) NOT NULL,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')

    # -- DDL SQLite ----------------------------------------------------
    def _ddl_sqlite(self, c):
        c.execute('''
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
        c.execute('''
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
        c.execute('''
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
        c.execute('''
            CREATE TABLE IF NOT EXISTS configuracion_aula (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filas INTEGER NOT NULL DEFAULT 6,
                columnas INTEGER NOT NULL DEFAULT 6,
                trivia_obligatoria BOOLEAN DEFAULT FALSE,
                configuracion_json TEXT,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS db_migrations (
                migration_id TEXT PRIMARY KEY,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS conformidad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alumno TEXT NOT NULL,
                companero TEXT NOT NULL,
                puntaje INTEGER NOT NULL CHECK(puntaje BETWEEN 1 AND 5),
                metodo TEXT DEFAULT 'afinidad',
                timestamp TEXT NOT NULL,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    # -- Migraciones ---------------------------------------------------
    def _run_migrations(self, cursor):
        """Migraciones idempotentes para ambos backends."""
        cols = [
            ('rankings', 'puntos_totales', 'INT DEFAULT 0'),
            ('rankings', 'nivel', 'INT DEFAULT 1'),
            ('rankings', 'fecha_ultimo_voto', 'VARCHAR(50)'),
            ('rankings', 'trivia_preguntas_respondidas', 'INT DEFAULT 0'),
            ('rankings', 'trivia_preguntas_correctas', 'INT DEFAULT 0'),
            ('rankings', 'trivia_categorias_dominadas', 'TEXT'),
            ('rankings', 'trivia_racha_actual', 'INT DEFAULT 0'),
            ('rankings', 'trivia_mejor_racha', 'INT DEFAULT 0'),
            ('configuracion_aula', 'trivia_obligatoria', 'BOOLEAN DEFAULT FALSE'),
            ('configuracion_aula', 'configuracion_json', 'TEXT'),
        ]
        for table, col, defn in cols:
            self._add_column_safe(cursor, table, col, defn)

        # Fix trivia_obligatoria en filas existentes
        cursor.execute(self._ph(
            "SELECT COUNT(*) FROM db_migrations WHERE migration_id = ?"
        ), ('fix_trivia_default_false',))
        if cursor.fetchone()[0] == 0:
            cursor.execute('UPDATE configuracion_aula SET trivia_obligatoria = 0 WHERE trivia_obligatoria = 1')
            cursor.execute(self._ph(
                "INSERT INTO db_migrations (migration_id) VALUES (?)"
            ), ('fix_trivia_default_false',))

        # Limpiar trivia_obligatoria del JSON blob
        cursor.execute(self._ph(
            "SELECT COUNT(*) FROM db_migrations WHERE migration_id = ?"
        ), ('fix_trivia_json_blob',))
        if cursor.fetchone()[0] == 0:
            cursor.execute('SELECT id, configuracion_json FROM configuracion_aula WHERE configuracion_json IS NOT NULL')
            for row_id, json_text in cursor.fetchall():
                try:
                    cfg = json.loads(json_text)
                    if 'trivia_obligatoria' in cfg:
                        cfg.pop('trivia_obligatoria')
                        cursor.execute(self._ph(
                            'UPDATE configuracion_aula SET configuracion_json = ? WHERE id = ?'
                        ), (json.dumps(cfg), row_id))
                except Exception:
                    pass
            cursor.execute(self._ph(
                "INSERT INTO db_migrations (migration_id) VALUES (?)"
            ), ('fix_trivia_json_blob',))

    # ==================================================================
    #  VOTOS
    # ==================================================================
    def guardar_voto(self, anio, alumno, calificaciones, alumno_bloqueado=None, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(self._ph('''
                    REPLACE INTO votos
                    (anio, alumno, calificaciones, alumno_bloqueado, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                '''), (anio, alumno, json.dumps(calificaciones), alumno_bloqueado, timestamp))
                return True
            except Exception as e:
                print(f"Error guardando voto: {e}")
                return False

    def cargar_votos(self, anio):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(self._ph('''
                SELECT alumno, calificaciones, alumno_bloqueado, timestamp
                FROM votos WHERE anio = ?
            '''), (anio,))
            votos = {}
            for row in cursor.fetchall():
                alumno, cal_json, bloqueado, ts = row
                votos[alumno] = {
                    'calificaciones': json.loads(cal_json),
                    'bloqueado': bloqueado,
                    'timestamp': ts,
                }
            return votos

    def obtener_votos_por_anio(self, anio):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(self._ph('''
                SELECT alumno, calificaciones, alumno_bloqueado, timestamp
                FROM votos WHERE anio = ?
            '''), (anio,))
            votos = {}
            for row in cursor.fetchall():
                alumno, cal_json, bloqueado, ts = row
                try:
                    votos[alumno] = {
                        'calificaciones': json.loads(cal_json),
                        'alumno_bloqueado': bloqueado,
                        'timestamp': ts,
                    }
                except json.JSONDecodeError:
                    pass
            return votos

    def borrar_votos_anio(self, anio):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(self._ph('SELECT COUNT(*) FROM votos WHERE anio = ?'), (anio,))
                total = cursor.fetchone()[0]
                cursor.execute(self._ph('DELETE FROM votos WHERE anio = ?'), (anio,))
                return True, total
        except Exception as e:
            print(f"Error borrando votos del anio {anio}: {e}")
            return False, 0

    def borrar_voto_alumno(self, anio, alumno):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(self._ph(
                    'SELECT COUNT(*) FROM votos WHERE anio = ? AND alumno = ?'
                ), (anio, alumno))
                if cursor.fetchone()[0] == 0:
                    return False
                cursor.execute(self._ph(
                    'DELETE FROM votos WHERE anio = ? AND alumno = ?'
                ), (anio, alumno))
                return True
        except Exception as e:
            print(f"Error borrando voto de {alumno} en {anio}: {e}")
            return False

    # ==================================================================
    #  ASIGNACIONES DE BANCOS
    # ==================================================================
    def guardar_asignacion_bancos(self, anio, nombre_asignacion, asignacion_data,
                                 total_alumnos, filas, columnas, es_actual=True):
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                if es_actual:
                    cursor.execute(self._ph(
                        'UPDATE asignaciones_bancos SET es_actual = FALSE WHERE anio = ?'
                    ), (anio,))
                cursor.execute(self._ph('''
                    INSERT INTO asignaciones_bancos
                    (anio, nombre_asignacion, asignacion_data, total_alumnos, filas, columnas, es_actual)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                '''), (anio, nombre_asignacion, json.dumps(asignacion_data),
                       total_alumnos, filas, columnas, es_actual))
                return True
            except Exception as e:
                print(f"Error guardando asignacion: {e}")
                return False

    def cargar_asignacion_bancos(self, anio, nombre_asignacion=None):
        with self._connect() as conn:
            cursor = conn.cursor()
            if nombre_asignacion:
                cursor.execute(self._ph('''
                    SELECT asignacion_data, total_alumnos, filas, columnas, fecha_creacion
                    FROM asignaciones_bancos
                    WHERE anio = ? AND nombre_asignacion = ?
                    ORDER BY fecha_creacion DESC LIMIT 1
                '''), (anio, nombre_asignacion))
            else:
                cursor.execute(self._ph('''
                    SELECT asignacion_data, total_alumnos, filas, columnas, fecha_creacion
                    FROM asignaciones_bancos
                    WHERE anio = ? AND es_actual = TRUE
                    ORDER BY fecha_creacion DESC LIMIT 1
                '''), (anio,))
            row = cursor.fetchone()
            if row:
                return {
                    'asignacion': json.loads(row[0]),
                    'fecha_guardado': row[4],
                    'total_alumnos': row[1],
                    'configuracion': {'filas': row[2], 'columnas': row[3]},
                }
            return {}

    def listar_asignaciones_bancos(self, anio):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(self._ph('''
                SELECT nombre_asignacion, total_alumnos, fecha_creacion, es_actual
                FROM asignaciones_bancos WHERE anio = ?
                ORDER BY fecha_creacion DESC
            '''), (anio,))
            return [
                {'nombre': r[0], 'total_alumnos': r[1], 'fecha': r[2], 'es_actual': bool(r[3])}
                for r in cursor.fetchall()
            ]

    def borrar_asignaciones_bancos_anio(self, anio):
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(self._ph('SELECT COUNT(*) FROM asignaciones_bancos WHERE anio = ?'), (anio,))
                total = cursor.fetchone()[0]
                cursor.execute(self._ph('DELETE FROM asignaciones_bancos WHERE anio = ?'), (anio,))
                return True, total
            except Exception as e:
                print(f"Error borrando asignaciones de bancos de {anio}: {e}")
                return False, 0

    # ==================================================================
    #  RANKINGS
    # ==================================================================
    def actualizar_ranking_completo(self, anio, alumno, datos_ranking):
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(self._ph(
                    'SELECT COUNT(*) FROM rankings WHERE anio = ? AND alumno = ?'
                ), (anio, alumno))
                exists = cursor.fetchone()[0] > 0

                params = (
                    datos_ranking.get('puntos_totales', 0),
                    datos_ranking.get('nivel', 1),
                    json.dumps(datos_ranking.get('badges', [])),
                    datos_ranking.get('partidas_jugadas', 0),
                    datos_ranking.get('fecha_ultimo_voto'),
                    datos_ranking.get('trivia_stats', {}).get('preguntas_respondidas', 0),
                    datos_ranking.get('trivia_stats', {}).get('preguntas_correctas', 0),
                    json.dumps(datos_ranking.get('trivia_stats', {}).get('categorias_dominadas', [])),
                    datos_ranking.get('trivia_stats', {}).get('racha_actual', 0),
                    datos_ranking.get('trivia_stats', {}).get('mejor_racha', 0),
                )

                if exists:
                    cursor.execute(self._ph('''
                        UPDATE rankings SET
                            puntos_totales = ?, nivel = ?, badges = ?,
                            partidas_jugadas = ?, fecha_ultimo_voto = ?,
                            trivia_preguntas_respondidas = ?, trivia_preguntas_correctas = ?,
                            trivia_categorias_dominadas = ?, trivia_racha_actual = ?,
                            trivia_mejor_racha = ?
                        WHERE anio = ? AND alumno = ?
                    '''), params + (anio, alumno))
                else:
                    cursor.execute(self._ph('''
                        INSERT INTO rankings
                        (anio, alumno, puntos_totales, nivel, badges, partidas_jugadas,
                         fecha_ultimo_voto, trivia_preguntas_respondidas, trivia_preguntas_correctas,
                         trivia_categorias_dominadas, trivia_racha_actual, trivia_mejor_racha)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''), (anio, alumno) + params)
                return True
            except Exception as e:
                print(f"Error actualizando ranking completo: {e}")
                return False

    def obtener_ranking_alumno(self, anio, alumno):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(self._ph('''
                SELECT puntos_totales, nivel, badges, partidas_jugadas, fecha_ultimo_voto,
                       trivia_preguntas_respondidas, trivia_preguntas_correctas,
                       trivia_categorias_dominadas, trivia_racha_actual, trivia_mejor_racha
                FROM rankings WHERE anio = ? AND alumno = ?
            '''), (anio, alumno))
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
                        'mejor_racha': row[9] or 0,
                    },
                }
            return {
                'puntos_totales': 0, 'nivel': 1, 'badges': [],
                'partidas_jugadas': 0, 'fecha_ultimo_voto': None,
                'trivia_stats': {
                    'preguntas_respondidas': 0, 'preguntas_correctas': 0,
                    'categorias_dominadas': [], 'racha_actual': 0, 'mejor_racha': 0,
                },
            }

    def actualizar_ranking(self, anio, alumno, puntos, badges, partidas_jugadas):
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(self._ph(
                    'SELECT COUNT(*) FROM rankings WHERE anio = ? AND alumno = ?'
                ), (anio, alumno))
                if cursor.fetchone()[0] > 0:
                    cursor.execute(self._ph('''
                        UPDATE rankings
                        SET puntos_totales = ?, badges = ?, partidas_jugadas = ?
                        WHERE anio = ? AND alumno = ?
                    '''), (puntos, json.dumps(badges), partidas_jugadas, anio, alumno))
                else:
                    cursor.execute(self._ph('''
                        INSERT INTO rankings (anio, alumno, puntos_totales, badges, partidas_jugadas)
                        VALUES (?, ?, ?, ?, ?)
                    '''), (anio, alumno, puntos, json.dumps(badges), partidas_jugadas))
                return True
            except Exception as e:
                print(f"Error actualizando ranking: {e}")
                return False

    def cargar_ranking(self, anio):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(self._ph('''
                SELECT alumno, puntos_totales, nivel, badges, partidas_jugadas, fecha_ultimo_voto,
                       trivia_preguntas_respondidas, trivia_preguntas_correctas,
                       trivia_categorias_dominadas, trivia_racha_actual, trivia_mejor_racha
                FROM rankings WHERE anio = ?
                ORDER BY puntos_totales DESC
            '''), (anio,))
            ranking = {}
            for row in cursor.fetchall():
                ranking[row[0]] = {
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
                        'mejor_racha': row[10] or 0,
                    },
                }
            return ranking

    def borrar_rankings_anio(self, anio):
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(self._ph('SELECT COUNT(*) FROM rankings WHERE anio = ?'), (anio,))
                total = cursor.fetchone()[0]
                cursor.execute(self._ph('DELETE FROM rankings WHERE anio = ?'), (anio,))
                return True, total
            except Exception as e:
                print(f"Error borrando rankings de {anio}: {e}")
                return False, 0

    # ==================================================================
    #  CONFIGURACION DEL AULA
    # ==================================================================
    def guardar_configuracion_aula(self, config_dict):
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM configuracion_aula')
                json_limpio = {k: v for k, v in config_dict.items() if k != 'trivia_obligatoria'}
                cursor.execute(self._ph('''
                    INSERT INTO configuracion_aula (filas, columnas, trivia_obligatoria, configuracion_json)
                    VALUES (?, ?, ?, ?)
                '''), (
                    config_dict.get('filas_maximas', 6),
                    config_dict.get('columnas_por_fila', 6),
                    config_dict.get('trivia_obligatoria', False),
                    json.dumps(json_limpio),
                ))
                return True
            except Exception as e:
                print(f"Error guardando configuracion: {e}")
                return False

    def cargar_configuracion_aula(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT filas, columnas, trivia_obligatoria, configuracion_json
                FROM configuracion_aula
                ORDER BY fecha_actualizacion DESC LIMIT 1
            ''')
            row = cursor.fetchone()
            if row:
                trivia_val = bool(row[2])
                base_config = {
                    'filas_maximas': row[0],
                    'columnas_por_fila': row[1],
                    'trivia_obligatoria': trivia_val,
                }
                if row[3]:
                    try:
                        extra = json.loads(row[3])
                        extra.pop('trivia_obligatoria', None)
                        base_config.update(extra)
                    except Exception:
                        pass
                return base_config
            return {'filas_maximas': 6, 'columnas_por_fila': 6, 'trivia_obligatoria': False}

    # ==================================================================
    #  CONFORMIDAD
    # ==================================================================
    def guardar_conformidad(self, alumno, companero, puntaje, metodo='afinidad', timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(self._ph('''
                    INSERT INTO conformidad (alumno, companero, puntaje, metodo, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                '''), (alumno, companero, puntaje, metodo, timestamp))
                return True
            except Exception as e:
                print(f"Error guardando conformidad: {e}")
                return False

    def obtener_conformidad(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT alumno, companero, puntaje, metodo, timestamp FROM conformidad')
            return [
                {'alumno': r[0], 'companero': r[1], 'puntaje': r[2], 'metodo': r[3], 'timestamp': r[4]}
                for r in cursor.fetchall()
            ]


# -- Instancia global --------------------------------------------------
db_manager = DatabaseManager()
