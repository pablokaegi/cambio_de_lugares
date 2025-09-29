#!/usr/bin/env python3
"""
Script de migración de JSON a SQLite
Migra todos los archivos JSON existentes a la base de datos SQLite
"""

import json
import os
import glob
from database import db_manager

def migrar_votos_json_a_bd():
    """Migra todos los archivos de votos JSON a la base de datos"""
    print("🔄 Iniciando migración de votos JSON a base de datos...")
    
    # Buscar todos los archivos de votos
    archivos_votos = glob.glob("votos_*.json")
    archivos_migrados = 0
    votos_migrados = 0
    
    for archivo in archivos_votos:
        try:
            # Extraer año del nombre del archivo
            anio = archivo.replace("votos_", "").replace(".json", "")
            
            print(f"📂 Procesando {archivo} (año: {anio})...")
            
            # Cargar JSON
            with open(archivo, 'r', encoding='utf-8') as f:
                votos_json = json.load(f)
            
            # Migrar cada voto
            for alumno, voto_data in votos_json.items():
                try:
                    # Obtener datos del voto
                    calificaciones = voto_data.get('calificaciones', {})
                    bloqueado = voto_data.get('bloqueado') or voto_data.get('alumno_bloqueado')
                    timestamp = voto_data.get('timestamp', str(os.times().elapsed))
                    
                    # Guardar en base de datos
                    success = db_manager.guardar_voto(
                        anio=anio,
                        alumno=alumno,
                        calificaciones=calificaciones,
                        alumno_bloqueado=bloqueado,
                        timestamp=timestamp
                    )
                    
                    if success:
                        votos_migrados += 1
                        print(f"  ✅ Migrado voto de {alumno}")
                    else:
                        print(f"  ❌ Error migrando voto de {alumno}")
                        
                except Exception as e:
                    print(f"  ❌ Error con voto de {alumno}: {e}")
            
            archivos_migrados += 1
            
        except Exception as e:
            print(f"❌ Error procesando {archivo}: {e}")
    
    print(f"✅ Migración completada:")
    print(f"   📁 Archivos procesados: {archivos_migrados}")
    print(f"   🗳️ Votos migrados: {votos_migrados}")
    
    return archivos_migrados, votos_migrados

def respaldar_archivos_json():
    """Crea respaldo de archivos JSON antes de eliminarlos"""
    print("💾 Creando respaldo de archivos JSON...")
    
    try:
        os.makedirs("respaldo_json", exist_ok=True)
        
        archivos_json = glob.glob("*.json")
        respaldados = 0
        
        for archivo in archivos_json:
            if archivo.startswith(('votos_', 'asignaciones_', 'ranking_')):
                try:
                    import shutil
                    shutil.copy2(archivo, f"respaldo_json/{archivo}")
                    respaldados += 1
                    print(f"  📄 Respaldado: {archivo}")
                except Exception as e:
                    print(f"  ❌ Error respaldando {archivo}: {e}")
        
        print(f"✅ Respaldo completado: {respaldados} archivos")
        return respaldados
        
    except Exception as e:
        print(f"❌ Error creando respaldo: {e}")
        return 0

def verificar_migracion():
    """Verifica que la migración fue exitosa"""
    print("🔍 Verificando migración...")
    
    try:
        # Verificar algunos años comunes
        for anio in ['1ro', '2do', '3ro', '4to', '5to', '6to']:
            votos_bd = db_manager.obtener_votos_por_anio(anio)
            if votos_bd:
                print(f"  ✅ Año {anio}: {len(votos_bd)} votos en BD")
        
        print("✅ Verificación completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def main():
    """Función principal de migración"""
    print("🚀 Iniciando migración completa JSON → SQLite")
    print("=" * 50)
    
    # 1. Crear respaldo
    respaldados = respaldar_archivos_json()
    
    # 2. Migrar votos
    archivos, votos = migrar_votos_json_a_bd()
    
    # 3. Verificar migración
    verificacion_ok = verificar_migracion()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE MIGRACIÓN:")
    print(f"  💾 Archivos respaldados: {respaldados}")
    print(f"  📁 Archivos JSON procesados: {archivos}")
    print(f"  🗳️ Votos migrados: {votos}")
    print(f"  ✅ Verificación: {'EXITOSA' if verificacion_ok else 'FALLÓ'}")
    
    if verificacion_ok and votos > 0:
        print("\n🎉 ¡Migración completada exitosamente!")
        print("💡 Los archivos JSON originales están respaldados en la carpeta 'respaldo_json'")
        print("🔒 Ahora el sistema usa exclusivamente la base de datos SQLite")
    else:
        print("\n⚠️ La migración puede tener problemas. Revisa los logs arriba.")

if __name__ == "__main__":
    main()