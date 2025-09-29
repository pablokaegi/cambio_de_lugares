"""
Módulo de preguntas de trivia organizadas por materias
Diseñado para el sistema educativo de Córdoba, Argentina
"""

import random
from typing import Dict, List, Any, Optional

class BancoPreguntas:
    """Clase para manejar el banco de preguntas de trivia por materias"""
    
    def __init__(self):
        self.preguntas = {
            'historia_cordoba': [
                {
                    'pregunta': '¿En qué año se fundó la ciudad de Córdoba?',
                    'opciones': ['1573', '1580', '1588', '1595'],
                    'respuesta_correcta': 0,
                    'puntos': 15,
                    'explicacion': 'Córdoba fue fundada por Jerónimo Luis de Cabrera el 6 de julio de 1573.',
                    'nivel': 'basico'
                },
                {
                    'pregunta': '¿Quién fundó la Universidad Nacional de Córdoba?',
                    'opciones': ['Los Jesuitas', 'Los Franciscanos', 'El Virrey', 'Los Dominicos'],
                    'respuesta_correcta': 0,
                    'puntos': 15,
                    'explicacion': 'La UNC fue fundada por los Jesuitas en 1613, siendo la más antigua de Argentina.',
                    'nivel': 'intermedio'
                },
                {
                    'pregunta': '¿Cómo se llama el barrio histórico de Córdoba Capital?',
                    'opciones': ['La Cañada', 'Güemes', 'San Vicente', 'Alberdi'],
                    'respuesta_correcta': 0,
                    'puntos': 10,
                    'explicacion': 'La Cañada es el barrio histórico donde está la Catedral y el Cabildo.',
                    'nivel': 'basico'
                },
                {
                    'pregunta': '¿Qué edificio histórico fue construido por los Jesuitas en Córdoba?',
                    'opciones': ['La Manzana Jesuítica', 'Casa de Gobierno', 'Teatro del Libertador', 'Palacio Ferreyra'],
                    'respuesta_correcta': 0,
                    'puntos': 20,
                    'explicacion': 'La Manzana Jesuítica es Patrimonio de la Humanidad por la UNESCO.',
                    'nivel': 'avanzado'
                }
            ],
            
            'geografia_cordoba': [
                {
                    'pregunta': '¿Cuál es el río más importante de Córdoba?',
                    'opciones': ['Río Primero', 'Río Segundo', 'Río Tercero', 'Río Cuarto'],
                    'respuesta_correcta': 0,
                    'puntos': 10,
                    'explicacion': 'El Río Primero (Suquía) atraviesa la capital cordobesa.',
                    'nivel': 'basico'
                },
                {
                    'pregunta': '¿En qué sierras se encuentra el Cerro Champaquí?',
                    'opciones': ['Sierras Grandes', 'Sierras Chicas', 'Sierras del Norte', 'Sierras del Sur'],
                    'respuesta_correcta': 0,
                    'puntos': 15,
                    'explicacion': 'El Champaquí (2884m) es el pico más alto de Córdoba, en las Sierras Grandes.',
                    'nivel': 'intermedio'
                },
                {
                    'pregunta': '¿Cuál es la principal laguna de Córdoba?',
                    'opciones': ['Mar Chiquita', 'Laguna Azul', 'Los Molinos', 'San Roque'],
                    'respuesta_correcta': 0,
                    'puntos': 15,
                    'explicacion': 'Mar Chiquita es la laguna salina más grande de Argentina.',
                    'nivel': 'intermedio'
                },
                {
                    'pregunta': '¿Qué departamento de Córdoba limita con Santiago del Estero?',
                    'opciones': ['Río Primero', 'Tulumba', 'Sobremonte', 'Río Seco'],
                    'respuesta_correcta': 2,
                    'puntos': 20,
                    'explicacion': 'Sobremonte es el departamento más al norte de Córdoba.',
                    'nivel': 'avanzado'
                }
            ],
            
            'cultura_argentina': [
                {
                    'pregunta': '¿Quién escribió el Martín Fierro?',
                    'opciones': ['José Hernández', 'Domingo Sarmiento', 'Bartolomé Mitre', 'Leopoldo Lugones'],
                    'respuesta_correcta': 0,
                    'puntos': 15,
                    'explicacion': 'José Hernández escribió este poema gauchesco en 1872.',
                    'nivel': 'intermedio'
                },
                {
                    'pregunta': '¿Cuál es el baile nacional de Argentina?',
                    'opciones': ['Tango', 'Zamba', 'Chacarera', 'Pericón'],
                    'respuesta_correcta': 3,
                    'puntos': 10,
                    'explicacion': 'El Pericón fue declarado danza nacional argentina.',
                    'nivel': 'basico'
                },
                {
                    'pregunta': '¿Qué escritor cordobés escribió "Adán Buenosayres"?',
                    'opciones': ['Leopoldo Marechal', 'Julio Cortázar', 'Arturo Capdevila', 'Marcos Aguinis'],
                    'respuesta_correcta': 0,
                    'puntos': 20,
                    'explicacion': 'Leopoldo Marechal, nacido en Buenos Aires pero radicado en Córdoba.',
                    'nivel': 'avanzado'
                }
            ],
            
            'ciencias_naturales': [
                {
                    'pregunta': '¿Qué tipo de clima predomina en Córdoba?',
                    'opciones': ['Templado', 'Subtropical', 'Árido', 'Tropical'],
                    'respuesta_correcta': 0,
                    'puntos': 10,
                    'explicacion': 'Córdoba tiene clima templado con estaciones bien diferenciadas.',
                    'nivel': 'basico'
                },
                {
                    'pregunta': '¿Cuál es el ave provincial de Córdoba?',
                    'opciones': ['Cóndor', 'Hornero', 'Calandria', 'Ñandú'],
                    'respuesta_correcta': 2,
                    'puntos': 15,
                    'explicacion': 'La Calandria fue declarada ave provincial por su canto melodioso.',
                    'nivel': 'intermedio'
                },
                {
                    'pregunta': '¿Qué tipo de formación geológica son las Sierras de Córdoba?',
                    'opciones': ['Plegamiento andino', 'Pampásicas', 'Volcánicas', 'Sedimentarias'],
                    'respuesta_correcta': 1,
                    'puntos': 20,
                    'explicacion': 'Las Sierras Pampásicas son muy antiguas, del Precámbrico.',
                    'nivel': 'avanzado'
                }
            ],
            
            'educacion_civica': [
                {
                    'pregunta': '¿Cuántos departamentos tiene la provincia de Córdoba?',
                    'opciones': ['24', '26', '28', '30'],
                    'respuesta_correcta': 1,
                    'puntos': 15,
                    'explicacion': 'Córdoba está dividida en 26 departamentos.',
                    'nivel': 'intermedio'
                },
                {
                    'pregunta': '¿Cuál es la capital del departamento Colón?',
                    'opciones': ['Colón', 'Jesús María', 'Villa Carlos Paz', 'La Falda'],
                    'respuesta_correcta': 1,
                    'puntos': 15,
                    'explicacion': 'Jesús María es la ciudad cabecera del departamento Colón.',
                    'nivel': 'intermedio'
                },
                {
                    'pregunta': '¿En qué año se sancionó la Constitución Provincial de Córdoba vigente?',
                    'opciones': ['1987', '1983', '1994', '2001'],
                    'respuesta_correcta': 0,
                    'puntos': 20,
                    'explicacion': 'La Constitución de Córdoba fue sancionada en 1987.',
                    'nivel': 'avanzado'
                }
            ],
            
            'matematicas_aplicadas': [
                {
                    'pregunta': 'Si en Córdoba hay 3.8 millones de habitantes y el 40% vive en la capital, ¿cuántos viven en la capital?',
                    'opciones': ['1.2 millones', '1.52 millones', '1.8 millones', '2.1 millones'],
                    'respuesta_correcta': 1,
                    'puntos': 15,
                    'explicacion': '40% de 3.8 millones = 0.4 × 3.8 = 1.52 millones.',
                    'nivel': 'intermedio'
                },
                {
                    'pregunta': 'El Champaquí mide 2884m. ¿Cuántos kilómetros son?',
                    'opciones': ['2.884 km', '28.84 km', '288.4 km', '0.2884 km'],
                    'respuesta_correcta': 0,
                    'puntos': 10,
                    'explicacion': '2884 metros = 2.884 kilómetros.',
                    'nivel': 'basico'
                },
                {
                    'pregunta': 'Si un campo en Córdoba tiene forma rectangular de 2km × 1.5km, ¿cuál es su área en hectáreas?',
                    'opciones': ['300 ha', '30 ha', '3000 ha', '3 ha'],
                    'respuesta_correcta': 0,
                    'puntos': 20,
                    'explicacion': '2km × 1.5km = 3 km² = 300 hectáreas (1 km² = 100 ha).',
                    'nivel': 'avanzado'
                }
            ]
        }
    
    def obtener_pregunta_aleatoria(self, materia: Optional[str] = None, nivel: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene una pregunta aleatoria, opcionalmente filtrada por materia y nivel
        """
        if materia and materia in self.preguntas:
            preguntas_disponibles = self.preguntas[materia]
        else:
            # Si no se especifica materia, usar todas las preguntas
            preguntas_disponibles = []
            for materia_preguntas in self.preguntas.values():
                preguntas_disponibles.extend(materia_preguntas)
        
        # Filtrar por nivel si se especifica
        if nivel:
            preguntas_disponibles = [p for p in preguntas_disponibles if p.get('nivel') == nivel]
        
        if not preguntas_disponibles:
            return None
            
        pregunta = random.choice(preguntas_disponibles)
        # Agregar información de contexto
        pregunta_completa = pregunta.copy()
        pregunta_completa['materia'] = self._obtener_materia_pregunta(pregunta)
        
        return pregunta_completa
    
    def _obtener_materia_pregunta(self, pregunta_buscada: Dict[str, Any]) -> str:
        """Encuentra a qué materia pertenece una pregunta"""
        for materia, preguntas in self.preguntas.items():
            if pregunta_buscada in preguntas:
                return materia
        return 'desconocida'
    
    def obtener_materias_disponibles(self) -> List[str]:
        """Retorna la lista de materias disponibles"""
        return list(self.preguntas.keys())
    
    def obtener_niveles_disponibles(self) -> List[str]:
        """Retorna la lista de niveles disponibles"""
        niveles = set()
        for materia_preguntas in self.preguntas.values():
            for pregunta in materia_preguntas:
                if 'nivel' in pregunta:
                    niveles.add(pregunta['nivel'])
        return sorted(list(niveles))
    
    def obtener_estadisticas_banco(self) -> Dict[str, Any]:
        """Retorna estadísticas del banco de preguntas"""
        stats = {
            'total_preguntas': 0,
            'por_materia': {},
            'por_nivel': {},
            'puntos_promedio': 0
        }
        
        total_puntos = 0
        for materia, preguntas in self.preguntas.items():
            stats['por_materia'][materia] = len(preguntas)
            stats['total_preguntas'] += len(preguntas)
            
            for pregunta in preguntas:
                total_puntos += pregunta.get('puntos', 0)
                nivel = pregunta.get('nivel', 'sin_nivel')
                stats['por_nivel'][nivel] = stats['por_nivel'].get(nivel, 0) + 1
        
        if stats['total_preguntas'] > 0:
            stats['puntos_promedio'] = round(total_puntos / stats['total_preguntas'], 2)
        
        return stats
    
    def agregar_pregunta(self, materia: str, pregunta: Dict[str, Any]) -> bool:
        """Agrega una nueva pregunta a una materia específica"""
        if materia not in self.preguntas:
            self.preguntas[materia] = []
        
        # Validar estructura de la pregunta
        campos_requeridos = ['pregunta', 'opciones', 'respuesta_correcta', 'puntos', 'explicacion']
        if not all(campo in pregunta for campo in campos_requeridos):
            return False
        
        self.preguntas[materia].append(pregunta)
        return True
    
    def eliminar_pregunta(self, materia: str, indice: int) -> bool:
        """Elimina una pregunta específica"""
        if materia in self.preguntas and 0 <= indice < len(self.preguntas[materia]):
            del self.preguntas[materia][indice]
            return True
        return False

# Instancia global del banco de preguntas
banco_preguntas = BancoPreguntas()

# Funciones de compatibilidad con el sistema existente
def obtener_pregunta_aleatoria():
    """Función de compatibilidad con el sistema existente"""
    return banco_preguntas.obtener_pregunta_aleatoria()

def obtener_pregunta_por_materia(materia: str):
    """Obtiene una pregunta de una materia específica"""
    return banco_preguntas.obtener_pregunta_aleatoria(materia=materia)

def obtener_pregunta_por_nivel(nivel: str):
    """Obtiene una pregunta de un nivel específico"""
    return banco_preguntas.obtener_pregunta_aleatoria(nivel=nivel)