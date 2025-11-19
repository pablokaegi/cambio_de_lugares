# Despliegue en cPanel con MySQL

## Archivos críticos para producción

### 1. passenger_wsgi.py
- **Propósito**: Punto de entrada WSGI para Passenger (cPanel)
- **Ubicación**: Raíz del proyecto
- **Configuración**: Importa `app` desde `app.py`

### 2. db_models.py
- **Propósito**: Capa ORM con SQLAlchemy
- **Modelos**: Voto, Ranking, AsignacionBanco, ConfiguracionAula
- **Características**:
  - Conexión a MySQL/PostgreSQL vía DATABASE_URL
  - Fallback a SQLite para desarrollo local
  - NullPool para compatibilidad con cPanel
  - Serialización JSON para campos complejos

### 3. requirements.txt
- **Nuevas dependencias**:
  - SQLAlchemy==2.0.23
  - pymysql==1.1.0
  - python-dotenv==1.0.0

### 4. analizador_psicopedagogico.py
- **Nueva funcionalidad**: Algoritmo Raptor Mini (Preview)
- **Método**: `generar_grupos_para_trabajo(anio, tamano_maximo=4)`
- **Descripción**: Generación híbrida de grupos balanceando rendimiento académico

## Configuración de cPanel

### Variables de entorno (.env)
```bash
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost/nombre_db
```

### Instalación de dependencias
```bash
pip install -r requirements.txt
```

### Configuración de Passenger
1. Crear aplicación Python en cPanel
2. Establecer ruta del proyecto
3. Configurar archivo de inicio: `passenger_wsgi.py`
4. Configurar Python 3.x (preferible 3.10+)

## Migración de datos

### Desde SQLite a MySQL
1. Exportar datos actuales de SQLite
2. Crear base de datos MySQL en cPanel
3. Configurar DATABASE_URL en .env
4. Ejecutar script de migración o importar manualmente

## Algoritmo Raptor Mini

### Características
- Combina datos de inclusión social (votos) y rendimiento académico (trivia/rankings)
- Balancea grupos heterogéneamente
- Estrategia: Alto rendimiento + Bajo rendimiento + Medio rendimiento
- Métricas por grupo: balance_rendimiento, heterogeneidad

### Uso
```python
from analizador_psicopedagogico import analizador_psicopedagogico

resultado = analizador_psicopedagogico.generar_grupos_para_trabajo(
    anio="cuarto",
    tamano_maximo=4
)

print(resultado['grupos_trabajo'])
print(resultado['metodo'])  # "Raptor Mini (Preview)"
```

## Notas importantes
- **.env NO DEBE subirse a GitHub** (ya está en .gitignore)
- Base de datos SQLite (`*.db`) excluida de Git
- Entorno virtual (`venv/`) excluido de Git
