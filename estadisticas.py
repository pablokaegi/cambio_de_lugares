import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import statistics
from datetime import datetime
import numpy as np

# Configuración
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AnalizadorVotaciones:
    def __init__(self, anio):
        self.anio = anio
        self.archivo_votos = f'votos_{anio}.json'
        self.votos = self.cargar_votos()
        
    def cargar_votos(self):
        """Carga los votos del archivo JSON"""
        if os.path.exists(self.archivo_votos):
            try:
                with open(self.archivo_votos, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"❌ Error: Archivo {self.archivo_votos} corrupto")
                return {}
        else:
            print(f"❌ Error: No existe {self.archivo_votos}")
            return {}
    
    def generar_estadisticas_completas(self):
        """Genera todas las estadísticas pedagógicas"""
        if not self.votos:
            print("❌ No hay votos para analizar")
            return None
        
        print(f"📊 ANÁLISIS COMPLETO - {self.anio.upper()}")
        print("=" * 60)
        
        # 1. Estadísticas básicas
        stats_basicas = self.estadisticas_basicas()
        self.mostrar_estadisticas_basicas(stats_basicas)
        
        # 2. Análisis de popularidad
        print("\n🌟 ANÁLISIS DE POPULARIDAD")
        print("-" * 40)
        self.analizar_popularidad()
        
        # 3. Análisis de bloqueos
        print("\n🚫 ANÁLISIS DE BLOQUEOS")
        print("-" * 40)
        self.analizar_bloqueos()
        
        # 4. Matriz de afinidad
        print("\n💕 MATRIZ DE AFINIDAD")
        print("-" * 40)
        self.analizar_afinidad_mutua()
        
        # 5. Patrones de votación
        print("\n📈 PATRONES DE VOTACIÓN")
        print("-" * 40)
        self.analizar_patrones()
        
        # 6. Recomendaciones pedagógicas
        print("\n🎓 RECOMENDACIONES PEDAGÓGICAS")
        print("-" * 40)
        self.generar_recomendaciones()
        
        return True
    
    def estadisticas_basicas(self):
        """Calcula estadísticas básicas"""
        total_votantes = len(self.votos)
        total_ratings = 0
        total_bloqueos = 0
        distribución_ratings = Counter()
        
        for votante, datos in self.votos.items():
            ratings = datos.get('ratings', {})
            bloqueado = datos.get('bloqueado')
            
            total_ratings += len(ratings)
            if bloqueado:
                total_bloqueos += 1
            
            for rating in ratings.values():
                distribución_ratings[rating] += 1
        
        return {
            'total_votantes': total_votantes,
            'total_ratings': total_ratings,
            'total_bloqueos': total_bloqueos,
            'promedio_ratings_por_persona': total_ratings / total_votantes if total_votantes > 0 else 0,
            'distribución_ratings': distribución_ratings
        }
    
    def mostrar_estadisticas_basicas(self, stats):
        """Muestra estadísticas básicas"""
        print(f"👥 Participantes: {stats['total_votantes']}")
        print(f"⭐ Total evaluaciones: {stats['total_ratings']}")
        print(f"🚫 Distancia solicitada: {stats['total_bloqueos']}")
        print(f"📊 Promedio evaluaciones por persona: {stats['promedio_ratings_por_persona']:.1f}")
        
        print("\n📈 Distribución de puntuaciones:")
        for rating in sorted(stats['distribución_ratings'].keys()):
            cantidad = stats['distribución_ratings'][rating]
            porcentaje = (cantidad / stats['total_ratings']) * 100
            print(f"   {rating} estrellas: {cantidad:3d} ({porcentaje:5.1f}%)")
    
    def analizar_popularidad(self):
        """Analiza popularidad de estudiantes"""
        puntuaciones_recibidas = defaultdict(list)
        
        # Recopilar todas las puntuaciones recibidas
        for votante, datos in self.votos.items():
            ratings = datos.get('ratings', {})
            for evaluado, puntuacion in ratings.items():
                puntuaciones_recibidas[evaluado].append(puntuacion)
        
        if not puntuaciones_recibidas:
            print("❌ No hay datos de popularidad")
            return
        
        # Calcular estadísticas por alumno
        stats_alumnos = {}
        for alumno, puntuaciones in puntuaciones_recibidas.items():
            stats_alumnos[alumno] = {
                'promedio': statistics.mean(puntuaciones),
                'total_votos': len(puntuaciones),
                'suma_total': sum(puntuaciones),
                'puntuacion_maxima': max(puntuaciones),
                'puntuacion_minima': min(puntuaciones),
                'desviacion': statistics.stdev(puntuaciones) if len(puntuaciones) > 1 else 0
            }
        
        # Ordenar por popularidad (promedio + consistencia)
        alumnos_ordenados = sorted(
            stats_alumnos.items(),
            key=lambda x: (x[1]['promedio'], x[1]['total_votos'], -x[1]['desviacion']),
            reverse=True
        )
        
        print("🏆 TOP 10 CON MEJOR VALORACIÓN GRUPAL:")
        for i, (alumno, stats) in enumerate(alumnos_ordenados[:10], 1):
            print(f"{i:2d}. {alumno[:25]:25s} | "
                  f"⭐{stats['promedio']:.2f} | "
                  f"📊{stats['total_votos']:2d} votos | "
                  f"🎯{stats['desviacion']:.2f} desv")
        
        print("\n⚠️  BOTTOM 5 CON MENOR VALORACIÓN GRUPAL:")
        for i, (alumno, stats) in enumerate(alumnos_ordenados[-5:], 1):
            print(f"{i:2d}. {alumno[:25]:25s} | "
                  f"⭐{stats['promedio']:.2f} | "
                  f"📊{stats['total_votos']:2d} votos")
    
    def analizar_bloqueos(self):
        """Analiza bloqueos y conflictos"""
        bloqueos_recibidos = Counter()
        bloqueos_realizados = Counter()
        bloqueos_mutuos = []
        
        # Contar bloqueos
        for votante, datos in self.votos.items():
            bloqueado = datos.get('bloqueado')
            if bloqueado:
                bloqueos_recibidos[bloqueado] += 1
                bloqueos_realizados[votante] += 1
        
        # Detectar bloqueos mutuos
        for votante, datos in self.votos.items():
            bloqueado = datos.get('bloqueado')
            if bloqueado and bloqueado in self.votos:
                datos_bloqueado = self.votos[bloqueado]
                if datos_bloqueado.get('bloqueado') == votante:
                    par_bloqueado = tuple(sorted([votante, bloqueado]))
                    if par_bloqueado not in bloqueos_mutuos:
                        bloqueos_mutuos.append(par_bloqueado)
        
        if not bloqueos_recibidos:
            print("✅ ¡Excelente! No hay registros de inafinidad")
            return
        
        print("🚨 REGISTRO DE INAFINIDAD:")
        for alumno, cantidad in bloqueos_recibidos.most_common(10):
            print(f"   {alumno[:30]:30s} | {cantidad} señalamiento(s)")
        
        if bloqueos_mutuos:
            print(f"\n💥 CONFLICTOS MUTUOS ({len(bloqueos_mutuos)}):")
            for alumno1, alumno2 in bloqueos_mutuos:
                print(f"   ⚠️  {alumno1} ↔ {alumno2}")
        else:
            print("\n✅ No hay bloqueos mutuos")
    
    def analizar_afinidad_mutua(self):
        """Analiza afinidad mutua entre estudiantes"""
        afinidades_mutuas = []
        
        for votante, datos in self.votos.items():
            ratings = datos.get('ratings', {})
            for evaluado, puntuacion1 in ratings.items():
                if evaluado in self.votos:
                    datos_evaluado = self.votos[evaluado]
                    ratings_evaluado = datos_evaluado.get('ratings', {})
                    if votante in ratings_evaluado:
                        puntuacion2 = ratings_evaluado[votante]
                        
                        # Evitar duplicados
                        par = tuple(sorted([votante, evaluado]))
                        if not any(a['par'] == par for a in afinidades_mutuas):
                            afinidades_mutuas.append({
                                'par': par,
                                'alumno1': votante,
                                'alumno2': evaluado,
                                'puntuacion1': puntuacion1,
                                'puntuacion2': puntuacion2,
                                'promedio': (puntuacion1 + puntuacion2) / 2,
                                'diferencia': abs(puntuacion1 - puntuacion2)
                            })
        
        if not afinidades_mutuas:
            print("❌ No hay afinidades mutuas para analizar")
            return
        
        # Ordenar por mejor afinidad
        mejores_afinidades = sorted(
            afinidades_mutuas,
            key=lambda x: (-x['promedio'], x['diferencia'])
        )
        
        print("💕 TOP 10 MEJORES AFINIDADES MUTUAS:")
        for i, afinidad in enumerate(mejores_afinidades[:10], 1):
            print(f"{i:2d}. {afinidad['alumno1'][:15]:15s} ↔ {afinidad['alumno2'][:15]:15s} | "
                  f"⭐{afinidad['promedio']:.1f} | "
                  f"📊{afinidad['puntuacion1']}-{afinidad['puntuacion2']} | "
                  f"Δ{afinidad['diferencia']}")
        
        # Estadísticas de afinidad
        promedios = [a['promedio'] for a in afinidades_mutuas]
        diferencias = [a['diferencia'] for a in afinidades_mutuas]
        
        print(f"\n📈 ESTADÍSTICAS DE AFINIDAD:")
        print(f"   Promedio general: {statistics.mean(promedios):.2f}")
        print(f"   Diferencia promedio: {statistics.mean(diferencias):.2f}")
        print(f"   Afinidades perfectas (5-5): {len([a for a in afinidades_mutuas if a['promedio'] == 5])}")
    
    def analizar_patrones(self):
        """Analiza patrones de votación"""
        # Patrón de generosidad vs exigencia
        generosidad = {}
        
        for votante, datos in self.votos.items():
            ratings = datos.get('ratings', {})
            if ratings:
                promedio = statistics.mean(ratings.values())
                generosidad[votante] = promedio
        
        if generosidad:
            promedio_general = statistics.mean(generosidad.values())
            
            generosos = {k: v for k, v in generosidad.items() if v > promedio_general + 0.5}
            exigentes = {k: v for k, v in generosidad.items() if v < promedio_general - 0.5}
            
            print(f"📊 Promedio general de calificaciones: {promedio_general:.2f}")
            
            if generosos:
                print(f"\n😊 VOTANTES MÁS GENEROSOS ({len(generosos)}):")
                for alumno, promedio in sorted(generosos.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"   {alumno[:25]:25s} | ⭐{promedio:.2f}")
            
            if exigentes:
                print(f"\n🤨 VOTANTES MÁS EXIGENTES ({len(exigentes)}):")
                for alumno, promedio in sorted(exigentes.items(), key=lambda x: x[1])[:5]:
                    print(f"   {alumno[:25]:25s} | ⭐{promedio:.2f}")
    
    def generar_recomendaciones(self):
        """Genera recomendaciones pedagógicas"""
        recomendaciones = []
        
        # Analizar datos para recomendaciones
        bloqueos = sum(1 for datos in self.votos.values() if datos.get('bloqueado'))
        total_votantes = len(self.votos)
        
        if bloqueos > total_votantes * 0.3:
            recomendaciones.append("⚠️  ALTO NIVEL DE CONFLICTOS: Considerar actividades de team building")
        
        # Analizar polarización
        puntuaciones_recibidas = defaultdict(list)
        for votante, datos in self.votos.items():
            ratings = datos.get('ratings', {})
            for evaluado, puntuacion in ratings.items():
                puntuaciones_recibidas[evaluado].append(puntuacion)
        
        if puntuaciones_recibidas:
            desviaciones = []
            for puntuaciones in puntuaciones_recibidas.values():
                if len(puntuaciones) > 1:
                    desviaciones.append(statistics.stdev(puntuaciones))
            
            if desviaciones and statistics.mean(desviaciones) > 1.5:
                recomendaciones.append("📊 ALTA POLARIZACIÓN: Algunos estudiantes generan opiniones muy divididas")
        
        # Verificar participación
        if total_votantes < 20:  # Ajustar según el tamaño de clase esperado
            recomendaciones.append("📢 BAJA PARTICIPACIÓN: Motivar a más estudiantes a participar")
        
        if not recomendaciones:
            recomendaciones.append("✅ El grupo muestra patrones de interacción saludables")
        
        for rec in recomendaciones:
            print(f"   {rec}")
    
    def exportar_excel(self, nombre_archivo=None):
        """Exporta todos los datos a Excel"""
        if not self.votos:
            print("❌ No hay datos para exportar")
            return False
        
        if not nombre_archivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            nombre_archivo = f'estadisticas_{self.anio}_{timestamp}.xlsx'
        
        # Preparar datos para Excel
        datos_votos = []
        for votante, datos in self.votos.items():
            ratings = datos.get('ratings', {})
            bloqueado = datos.get('bloqueado', '')
            fecha = datos.get('fecha', '')
            
            for evaluado, puntuacion in ratings.items():
                datos_votos.append({
                    'Votante': votante,
                    'Evaluado': evaluado,
                    'Puntuacion': puntuacion,
                    'Bloqueado': bloqueado,
                    'Fecha': fecha[:10] if fecha else ''
                })
        
        # Crear DataFrames
        df_votos = pd.DataFrame(datos_votos)
        
        # Estadísticas por alumno
        puntuaciones_recibidas = defaultdict(list)
        for votante, datos in self.votos.items():
            ratings = datos.get('ratings', {})
            for evaluado, puntuacion in ratings.items():
                puntuaciones_recibidas[evaluado].append(puntuacion)
        
        datos_estadisticas = []
        for alumno, puntuaciones in puntuaciones_recibidas.items():
            if puntuaciones:
                datos_estadisticas.append({
                    'Alumno': alumno,
                    'Promedio': statistics.mean(puntuaciones),
                    'Total_Votos': len(puntuaciones),
                    'Puntuacion_Maxima': max(puntuaciones),
                    'Puntuacion_Minima': min(puntuaciones),
                    'Desviacion': statistics.stdev(puntuaciones) if len(puntuaciones) > 1 else 0
                })
        
        df_estadisticas = pd.DataFrame(datos_estadisticas)
        
        # Guardar en Excel
        try:
            with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
                df_votos.to_excel(writer, sheet_name='Votos_Detallados', index=False)
                df_estadisticas.to_excel(writer, sheet_name='Estadisticas_Alumnos', index=False)
            
            print(f"✅ Datos exportados a: {nombre_archivo}")
            return True
        except Exception as e:
            print(f"❌ Error exportando: {e}")
            return False

def menu_principal():
    """Menú principal interactivo"""
    print("\n" + "="*60)