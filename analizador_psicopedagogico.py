"""
Módulo de análisis psicopedagógico
Proporciona herramientas de análisis para el gabinete psicopedagógico
"""

import json
import math
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import statistics

class AnalizadorPsicopedagogico:
    """Clase para análisis psicopedagógico de relaciones sociales y dinámicas grupales"""
    
    def __init__(self, database_manager=None):
        self.db_manager = database_manager
    
    def analizar_relaciones_sociales(self, anio: str, votos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza las relaciones sociales basadas en los votos de los alumnos
        
        Returns:
            Análisis completo de relaciones sociales
        """
        if not votos:
            return {'error': 'No hay datos de votos para analizar'}
        
        # Extraer datos de calificaciones
        relaciones = {}
        popularidad = defaultdict(list)  # quién recibe qué calificaciones
        reciprocidad = {}  # relaciones mutuas
        
        for votante, datos_voto in votos.items():
            calificaciones = datos_voto.get('calificaciones', {})
            relaciones[votante] = calificaciones
            
            # Analizar popularidad
            for evaluado, puntaje in calificaciones.items():
                popularidad[evaluado].append(puntaje)
        
        # Calcular métricas de popularidad
        metricas_popularidad = {}
        for alumno, puntajes in popularidad.items():
            if puntajes:
                metricas_popularidad[alumno] = {
                    'promedio': round(statistics.mean(puntajes), 2),
                    'mediana': statistics.median(puntajes),
                    'total_votos': len(puntajes),
                    'puntaje_max': max(puntajes),
                    'puntaje_min': min(puntajes),
                    'desviacion_std': round(statistics.stdev(puntajes) if len(puntajes) > 1 else 0, 2)
                }
        
        # Analizar reciprocidad
        reciprocidad_datos = self._analizar_reciprocidad(relaciones)
        
        # Identificar grupos y clusters
        clusters = self._identificar_clusters_sociales(relaciones)
        
        # Detectar alumnos en riesgo social
        riesgo_social = self._detectar_riesgo_social(metricas_popularidad, votos)
        
        # Análisis de liderazgo
        liderazgo = self._analizar_liderazgo(metricas_popularidad, relaciones)
        
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'anio': anio,
            'total_participantes': len(votos),
            'metricas_popularidad': metricas_popularidad,
            'reciprocidad': reciprocidad_datos,
            'clusters_sociales': clusters,
            'alumnos_riesgo': riesgo_social,
            'liderazgo': liderazgo,
            'recomendaciones': self._generar_recomendaciones(metricas_popularidad, riesgo_social, clusters)
        }
    
    def _analizar_reciprocidad(self, relaciones: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """Analiza las relaciones recíprocas entre alumnos"""
        reciprocas = []
        no_reciprocas = []
        
        for alumno_a, califs_a in relaciones.items():
            for alumno_b, puntaje_a_b in califs_a.items():
                if alumno_b in relaciones:
                    puntaje_b_a = relaciones[alumno_b].get(alumno_a, 0)
                    
                    diferencia = abs(puntaje_a_b - puntaje_b_a)
                    relacion = {
                        'alumno_1': alumno_a,
                        'alumno_2': alumno_b,
                        'puntaje_1_a_2': puntaje_a_b,
                        'puntaje_2_a_1': puntaje_b_a,
                        'diferencia': diferencia,
                        'es_reciproca': diferencia <= 1  # Consideramos recíproca si la diferencia es ≤ 1
                    }
                    
                    if relacion['es_reciproca']:
                        reciprocas.append(relacion)
                    else:
                        no_reciprocas.append(relacion)
        
        # Eliminar duplicados (A->B y B->A son la misma relación)
        reciprocas_unicas = []
        procesadas = set()
        
        for rel in reciprocas:
            par = tuple(sorted([rel['alumno_1'], rel['alumno_2']]))
            if par not in procesadas:
                reciprocas_unicas.append(rel)
                procesadas.add(par)
        
        return {
            'relaciones_reciprocas': reciprocas_unicas,
            'relaciones_no_reciprocas': no_reciprocas,
            'porcentaje_reciprocidad': round(len(reciprocas_unicas) / (len(reciprocas_unicas) + len(no_reciprocas)) * 100, 2) if (reciprocas_unicas or no_reciprocas) else 0
        }
    
    def _identificar_clusters_sociales(self, relaciones: Dict[str, Dict[str, int]]) -> List[Dict[str, Any]]:
        """Identifica grupos sociales basados en calificaciones altas mutuas"""
        clusters = []
        umbral_afinidad = 4  # Puntajes ≥ 4 indican afinidad
        
        # Crear grafo de afinidades
        afinidades = defaultdict(set)
        for alumno_a, califs in relaciones.items():
            for alumno_b, puntaje in califs.items():
                if puntaje >= umbral_afinidad:
                    afinidades[alumno_a].add(alumno_b)
        
        # Encontrar grupos donde todos se califican bien mutuamente
        alumnos_procesados = set()
        
        for alumno in afinidades:
            if alumno in alumnos_procesados:
                continue
            
            # Encontrar todos los alumnos conectados
            grupo = {alumno}
            amigos = afinidades[alumno].copy()
            
            # Expandir el grupo con amigos mutuos
            for amigo in amigos:
                if amigo in afinidades:
                    # Verificar si hay afinidad mutua
                    amigos_del_amigo = afinidades[amigo]
                    if alumno in amigos_del_amigo:
                        grupo.add(amigo)
            
            if len(grupo) >= 2:  # Solo grupos de 2 o más
                clusters.append({
                    'miembros': list(grupo),
                    'tamaño': len(grupo),
                    'cohesion': self._calcular_cohesion_grupo(grupo, relaciones)
                })
                alumnos_procesados.update(grupo)
        
        return sorted(clusters, key=lambda x: x['cohesion'], reverse=True)
    
    def _calcular_cohesion_grupo(self, grupo: set, relaciones: Dict[str, Dict[str, int]]) -> float:
        """Calcula la cohesión interna de un grupo"""
        if len(grupo) < 2:
            return 0.0
        
        puntajes_internos = []
        for miembro_a in grupo:
            for miembro_b in grupo:
                if miembro_a != miembro_b and miembro_a in relaciones:
                    puntaje = relaciones[miembro_a].get(miembro_b, 0)
                    puntajes_internos.append(puntaje)
        
        return round(statistics.mean(puntajes_internos), 2) if puntajes_internos else 0.0
    
    def _detectar_riesgo_social(self, metricas_popularidad: Dict[str, Dict], votos: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta alumnos que podrían estar en riesgo de aislamiento social"""
        riesgo = []
        
        if not metricas_popularidad:
            return riesgo
        
        promedios = [m['promedio'] for m in metricas_popularidad.values()]
        promedio_general = statistics.mean(promedios)
        desviacion_general = statistics.stdev(promedios) if len(promedios) > 1 else 0
        
        for alumno, metricas in metricas_popularidad.items():
            factores_riesgo = []
            nivel_riesgo = 0
            
            # Factor 1: Promedio muy bajo
            if metricas['promedio'] < promedio_general - desviacion_general:
                factores_riesgo.append('Promedio de calificaciones bajo')
                nivel_riesgo += 2
            
            # Factor 2: Muchas calificaciones mínimas
            puntajes_bajos = sum(1 for p in votos.values() 
                               if p.get('calificaciones', {}).get(alumno, 0) <= 2)
            if puntajes_bajos > len(votos) * 0.3:  # Más del 30% le da puntajes bajos
                factores_riesgo.append('Recibe muchas calificaciones bajas')
                nivel_riesgo += 2
            
            # Factor 3: Alta variabilidad (algunos lo aman, otros no)
            if metricas['desviacion_std'] > 1.5:
                factores_riesgo.append('Alta variabilidad en calificaciones')
                nivel_riesgo += 1
            
            # Factor 4: Pocos votos recibidos
            if metricas['total_votos'] < len(votos) * 0.7:  # Menos del 70% lo calificó
                factores_riesgo.append('Pocos compañeros lo conocen/califican')
                nivel_riesgo += 1
            
            if factores_riesgo:
                riesgo.append({
                    'alumno': alumno,
                    'nivel_riesgo': min(nivel_riesgo, 5),  # Máximo 5
                    'factores': factores_riesgo,
                    'metricas': metricas
                })
        
        return sorted(riesgo, key=lambda x: x['nivel_riesgo'], reverse=True)
    
    def _analizar_liderazgo(self, metricas_popularidad: Dict[str, Dict], relaciones: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """Analiza potenciales líderes naturales del grupo"""
        if not metricas_popularidad:
            return {'lideres_potenciales': [], 'analisis': 'Sin datos suficientes'}
        
        lideres = []
        
        for alumno, metricas in metricas_popularidad.items():
            puntaje_liderazgo = 0
            cualidades = []
            
            # Factor 1: Alta popularidad general
            if metricas['promedio'] >= 4.0:
                puntaje_liderazgo += 3
                cualidades.append('Alta popularidad general')
            
            # Factor 2: Consistencia (baja desviación)
            if metricas['desviacion_std'] <= 1.0:
                puntaje_liderazgo += 2
                cualidades.append('Evaluación consistente')
            
            # Factor 3: Reconocimiento amplio
            if metricas['total_votos'] >= len(relaciones) * 0.8:
                puntaje_liderazgo += 2
                cualidades.append('Amplio reconocimiento')
            
            # Factor 4: Recibe muchas calificaciones altas
            califs_altas = sum(1 for califs in relaciones.values() 
                             if califs.get(alumno, 0) >= 4)
            if califs_altas >= len(relaciones) * 0.4:
                puntaje_liderazgo += 2
                cualidades.append('Recibe muchas calificaciones altas')
            
            if puntaje_liderazgo >= 4:  # Umbral para ser considerado líder
                lideres.append({
                    'alumno': alumno,
                    'puntaje_liderazgo': puntaje_liderazgo,
                    'cualidades': cualidades,
                    'metricas': metricas
                })
        
        return {
            'lideres_potenciales': sorted(lideres, key=lambda x: x['puntaje_liderazgo'], reverse=True),
            'total_lideres': len(lideres)
        }
    
    def _generar_recomendaciones(self, metricas_popularidad: Dict, riesgo_social: List, clusters: List) -> List[str]:
        """Genera recomendaciones pedagógicas basadas en el análisis"""
        recomendaciones = []
        
        # Recomendaciones para alumnos en riesgo
        if riesgo_social:
            alto_riesgo = [a for a in riesgo_social if a['nivel_riesgo'] >= 3]
            if alto_riesgo:
                recomendaciones.append(
                    f"PRIORIDAD ALTA: {len(alto_riesgo)} alumno(s) en riesgo de aislamiento social. "
                    f"Considerar actividades de integración grupal."
                )
        
        # Recomendaciones sobre grupos
        if clusters:
            grupos_grandes = [c for c in clusters if c['tamaño'] >= 4]
            if grupos_grandes:
                recomendaciones.append(
                    f"Se detectaron {len(grupos_grandes)} grupo(s) muy cohesionado(s). "
                    f"Considerar distribuirlos en actividades para promover integración."
                )
        
        # Recomendaciones sobre estructura social
        total_alumnos = len(metricas_popularidad)
        alumnos_en_grupos = sum(c['tamaño'] for c in clusters)
        if alumnos_en_grupos < total_alumnos * 0.7:
            recomendaciones.append(
                "Muchos alumnos no pertenecen a grupos definidos. "
                "Considerar actividades de team building."
            )
        
        return recomendaciones
    
    def generar_reporte_completo(self, anio: str) -> Dict[str, Any]:
        """Genera un reporte completo para el gabinete psicopedagógico"""
        if not self.db_manager:
            return {'error': 'Base de datos no disponible'}
        
        # Cargar datos
        votos = self.db_manager.cargar_votos(anio)
        if not votos:
            return {'error': f'No hay datos de votos para el año {anio}'}
        
        # Realizar análisis
        analisis_social = self.analizar_relaciones_sociales(anio, votos)
        
        # Análisis temporal si hay datos históricos
        analisis_temporal = self._analizar_tendencias_temporales(anio)
        
        # Estadísticas de participación en trivia
        stats_trivia = self._analizar_participacion_trivia(anio)
        
        return {
            'metadatos': {
                'fecha_generacion': datetime.now().isoformat(),
                'anio_analizado': anio,
                'tipo_reporte': 'Análisis Psicopedagógico Completo'
            },
            'resumen_ejecutivo': self._generar_resumen_ejecutivo(analisis_social),
            'analisis_social': analisis_social,
            'analisis_temporal': analisis_temporal,
            'participacion_trivia': stats_trivia,
            'recomendaciones_detalladas': self._generar_recomendaciones_detalladas(analisis_social)
        }
    
    def _analizar_tendencias_temporales(self, anio: str) -> Dict[str, Any]:
        """Analiza tendencias temporales en las votaciones"""
        # Placeholder para análisis temporal futuro
        return {
            'disponible': False,
            'mensaje': 'Análisis temporal requiere múltiples períodos de votación'
        }
    
    def _analizar_participacion_trivia(self, anio: str) -> Dict[str, Any]:
        """Analiza la participación en trivia como indicador de engagement"""
        if not self.db_manager:
            return {'disponible': False}
        
        ranking = self.db_manager.cargar_ranking(anio)
        if not ranking:
            return {'disponible': False, 'mensaje': 'No hay datos de trivia'}
        
        participantes = len(ranking)
        total_partidas = sum(r.get('partidas_jugadas', 0) for r in ranking.values())
        promedio_partidas = total_partidas / participantes if participantes > 0 else 0
        
        return {
            'disponible': True,
            'total_participantes': participantes,
            'total_partidas': total_partidas,
            'promedio_partidas_por_alumno': round(promedio_partidas, 2),
            'top_participantes': sorted(
                [(alumno, datos.get('partidas_jugadas', 0)) for alumno, datos in ranking.items()],
                key=lambda x: x[1], reverse=True
            )[:5]
        }
    
    def _generar_resumen_ejecutivo(self, analisis_social: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un resumen ejecutivo del análisis"""
        return {
            'participacion': f"{analisis_social.get('total_participantes', 0)} alumnos participaron",
            'estructura_social': f"{len(analisis_social.get('clusters_sociales', []))} grupos sociales identificados",
            'alumnos_riesgo': len(analisis_social.get('alumnos_riesgo', [])),
            'reciprocidad': f"{analisis_social.get('reciprocidad', {}).get('porcentaje_reciprocidad', 0)}% de relaciones recíprocas",
            'nivel_alerta': 'ALTO' if len(analisis_social.get('alumnos_riesgo', [])) > 3 else 'NORMAL'
        }
    
    def _generar_recomendaciones_detalladas(self, analisis_social: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera recomendaciones detalladas con acciones específicas"""
        recomendaciones = []
        
        # Para alumnos en riesgo
        alumnos_riesgo = analisis_social.get('alumnos_riesgo', [])
        for alumno_riesgo in alumnos_riesgo[:3]:  # Top 3 en riesgo
            recomendaciones.append({
                'tipo': 'individual',
                'prioridad': 'alta',
                'alumno': alumno_riesgo['alumno'],
                'accion': 'Sesión individual de seguimiento',
                'descripcion': f"Factores de riesgo: {', '.join(alumno_riesgo['factores'])}",
                'plazo': '1-2 semanas'
            })
        
        # Para grupos muy cohesionados
        clusters = analisis_social.get('clusters_sociales', [])
        grupos_grandes = [c for c in clusters if c['tamaño'] >= 4]
        if grupos_grandes:
            recomendaciones.append({
                'tipo': 'grupal',
                'prioridad': 'media',
                'accion': 'Actividad de integración inter-grupal',
                'descripcion': f"Integrar {len(grupos_grandes)} grupos muy cohesionados con el resto de la clase",
                'plazo': '2-3 semanas'
            })
        
        return recomendaciones

# Instancia global del analizador
analizador_psicopedagogico = AnalizadorPsicopedagogico()