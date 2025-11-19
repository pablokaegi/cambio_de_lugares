"""
Modelos de Base de Datos usando SQLAlchemy ORM
Soporta SQLite (desarrollo) y MySQL (producción cPanel)
"""
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

# Configuración de la conexión a base de datos
# Lee de variable de entorno o usa SQLite por defecto
DATABASE_URL = os.environ.get(
    'DATABASE_URL', 
    'sqlite:///alumnos_app.db'
)

# Crear el motor de base de datos
# NullPool evita problemas de conexiones en cPanel
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool if 'sqlite' not in DATABASE_URL else None,
    echo=False  # Cambia a True para debug SQL
)

# Base para modelos declarativos
Base = declarative_base()

# Sesión de base de datos
Session = sessionmaker(bind=engine)


# ============================================================================
# MODELOS DE DATOS
# ============================================================================

class Voto(Base):
    """Modelo para almacenar votos de los alumnos"""
    __tablename__ = 'votos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    anio = Column(String(50), nullable=False, index=True)
    alumno = Column(String(100), nullable=False)
    calificaciones = Column(Text, nullable=False)  # JSON serializado
    alumno_bloqueado = Column(String(100))
    timestamp = Column(String(50))
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Restricción única: un alumno solo puede votar una vez por año
    __table_args__ = (
        UniqueConstraint('anio', 'alumno', name='uq_anio_alumno_voto'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el voto a diccionario"""
        return {
            'anio': self.anio,
            'alumno': self.alumno,
            'calificaciones': json.loads(self.calificaciones),
            'alumno_bloqueado': self.alumno_bloqueado,
            'timestamp': self.timestamp
        }


class Ranking(Base):
    """Modelo para almacenar rankings de alumnos"""
    __tablename__ = 'rankings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    anio = Column(String(50), nullable=False, index=True)
    alumno = Column(String(100), nullable=False)
    
    # Métricas de ranking
    promedio_recibido = Column(String(20), default='0.0')
    votos_recibidos = Column(Integer, default=0)
    veces_bloqueado = Column(Integer, default=0)
    
    # Métricas de trivia
    puntos_trivia = Column(Integer, default=0)
    preguntas_correctas = Column(Integer, default=0)
    preguntas_totales = Column(Integer, default=0)
    tiempo_promedio = Column(String(20), default='0.0')
    
    # Métricas adicionales
    puntos_desafio = Column(Integer, default=0)
    desafios_ganados = Column(Integer, default=0)
    desafios_totales = Column(Integer, default=0)
    nivel_conformidad = Column(String(20), default='medio')
    
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Restricción única: un alumno por año
    __table_args__ = (
        UniqueConstraint('anio', 'alumno', name='uq_anio_alumno_ranking'),
    )


class AsignacionBanco(Base):
    """Modelo para almacenar asignaciones de bancos físicos en el aula"""
    __tablename__ = 'asignaciones_bancos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    anio = Column(String(50), nullable=False, index=True)
    alumno = Column(String(100), nullable=False)
    banco = Column(String(50), nullable=False)  # Ej: "A1", "B3"
    fila = Column(String(10))
    columna = Column(String(10))
    fecha_asignacion = Column(DateTime, default=datetime.now)
    
    # Restricción única: un alumno por año, un banco por año
    __table_args__ = (
        UniqueConstraint('anio', 'alumno', name='uq_anio_alumno_banco'),
        UniqueConstraint('anio', 'banco', name='uq_anio_banco'),
    )


class ConfiguracionAula(Base):
    """Modelo para almacenar configuración del aula (layout, filas, columnas)"""
    __tablename__ = 'configuracion_aula'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    anio = Column(String(50), nullable=False, unique=True, index=True)
    configuracion = Column(Text, nullable=False)  # JSON serializado
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ============================================================================
# GESTOR DE BASE DE DATOS ORM
# ============================================================================

class DatabaseManagerORM:
    """Gestor de base de datos usando SQLAlchemy ORM"""
    
    def __init__(self):
        self.engine = engine
        self.Session = Session
    
    def init_db(self):
        """Inicializa las tablas en la base de datos"""
        Base.metadata.create_all(self.engine)
        print(f"✓ Tablas creadas/verificadas en: {DATABASE_URL}")
    
    # ===== MÉTODOS DE VOTOS =====
    
    def guardar_voto(self, anio: str, alumno: str, calificaciones: Dict, 
                     alumno_bloqueado: Optional[str] = None, 
                     timestamp: Optional[str] = None) -> bool:
        """Guarda o actualiza un voto"""
        session = self.Session()
        try:
            calificaciones_json = json.dumps(calificaciones)
            timestamp = timestamp or str(datetime.now().timestamp())
            
            # Buscar voto existente (UPSERT)
            voto = session.query(Voto).filter_by(anio=anio, alumno=alumno).first()
            
            if voto:
                voto.calificaciones = calificaciones_json
                voto.alumno_bloqueado = alumno_bloqueado
                voto.timestamp = timestamp
                voto.fecha_creacion = datetime.now()
            else:
                voto = Voto(
                    anio=anio,
                    alumno=alumno,
                    calificaciones=calificaciones_json,
                    alumno_bloqueado=alumno_bloqueado,
                    timestamp=timestamp
                )
                session.add(voto)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error guardando voto: {e}")
            return False
        finally:
            session.close()
    
    def obtener_votos_por_anio(self, anio: str) -> Dict[str, Dict]:
        """Obtiene todos los votos de un año"""
        session = self.Session()
        try:
            votos = session.query(Voto).filter_by(anio=anio).all()
            resultado = {}
            for voto in votos:
                resultado[voto.alumno] = {
                    'calificaciones': json.loads(voto.calificaciones),
                    'alumno_bloqueado': voto.alumno_bloqueado,
                    'timestamp': voto.timestamp
                }
            return resultado
        finally:
            session.close()
    
    def borrar_votos_anio(self, anio: str) -> bool:
        """Borra todos los votos de un año"""
        session = self.Session()
        try:
            session.query(Voto).filter_by(anio=anio).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error borrando votos: {e}")
            return False
        finally:
            session.close()
    
    # ===== MÉTODOS DE CONFIGURACIÓN AULA =====
    
    def guardar_configuracion(self, anio: str, config: Dict) -> bool:
        """Guarda configuración del aula"""
        session = self.Session()
        try:
            config_json = json.dumps(config)
            config_obj = session.query(ConfiguracionAula).filter_by(anio=anio).first()
            
            if config_obj:
                config_obj.configuracion = config_json
                config_obj.fecha_actualizacion = datetime.now()
            else:
                config_obj = ConfiguracionAula(anio=anio, configuracion=config_json)
                session.add(config_obj)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error guardando configuración: {e}")
            return False
        finally:
            session.close()
    
    def obtener_configuracion(self, anio: str) -> Optional[Dict]:
        """Obtiene configuración del aula"""
        session = self.Session()
        try:
            config = session.query(ConfiguracionAula).filter_by(anio=anio).first()
            if config:
                return json.loads(config.configuracion)
            return None
        finally:
            session.close()


# ============================================================================
# INSTANCIA GLOBAL
# ============================================================================

db_manager = DatabaseManagerORM()


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

if __name__ == '__main__':
    print(f"Conectando a: {DATABASE_URL}")
    db_manager.init_db()
    print("✓ Base de datos inicializada correctamente")
