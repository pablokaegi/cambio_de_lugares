"""
Módulo de gestión de alumnos
Incluye funcionalidades para manejar listas de alumnos y importación desde CSV
"""

import csv
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

class GestorAlumnos:
    """Clase para manejar la gestión de alumnos por año"""
    
    def __init__(self, archivo_datos: str = 'alumnos_data.json'):
        self.archivo_datos = archivo_datos
        self.alumnos_por_anio = self._cargar_datos()
    
    def _cargar_datos(self) -> Dict[str, List[str]]:
        """Carga los datos de alumnos desde archivo JSON"""
        if os.path.exists(self.archivo_datos):
            try:
                with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Datos por defecto si no existe el archivo
        return self._obtener_datos_por_defecto()
    
    def _obtener_datos_por_defecto(self) -> Dict[str, List[str]]:
        """Retorna los datos por defecto de alumnos - BACKUP CORRECTO"""
        return {
            'primero': [
                "ISABELLA ALBERIONE FIORE", "BENJAMIN MATIAS ALDAVE", "MALENA ARMADA",
                "MIA BALDONCINI", "FRANCESCO BALEANI", "OCTAVIO BARRIONUEVO SORIA",
                "BENJAMIN ALEXIS BELTRAMO", "LAUTARO OMAR BONO", "MIA CASTRO",
                "CATALINA CICCIOLI", "ALAN DIDIER", "ISABELLA FALCONNAT",
                "AXEL ARIEL FERREYRA", "LUCIA INES FRANCO", "GENARO ZACARÍAS FRARESSO",
                "JUSTINO FRARESSO ZORRILLA", "CATALINA GALETTO GALVAN", "FELIPE LOZANO DE FRANCISCO",
                "LAZARO MARINSALDA SONTULLO", "IGNACIO MELANO", "MATEO MERCADO BOTTOSSO",
                "OLIVIA JAZMIN MONTE", "ANGELINA NICOLE MOYANO CARBAJAL", "GIULIANA OLDANI",
                "JULIANA PEROGLIA PAINA", "EZEQUIEL FEDERICO PERREN", "FERMIN RAMONDA ROSAS",
                "LOURDES RE", "BIANCA SOFIA RE OLIVERA", "VICTORIA SCARAMUZZA MATTIA",
                "VICTORIA TANTUCCI VIANO", "VALENTINO TAPIA CERQUATTI", "ISABELLA VEGA AHUMADA",
                "LARA VENTRE", "RINGO JAVIER ZUPPA"
            ],
            'segundo': [
                "SANTINO CERUTTI", "HELENA CLARK ETCHEVERRY", "BENJAMIN CRESATTI MIÑO",
                "EMILIA FALCO GARINO", "FRANCISCO FERRERO FONSECA", "MIA GABRIELA GARCIA",
                "HELENA MANSILLA", "FELIPE RE", "MARTIN ANGEL ROSINA",
                "MARTINIANO SORIANO PRANZONI", "MELANY TORRESI", "JOAQUIN BAUTISTA VERDICCHIO"
            ],
            'tercero': [
                "SANTIAGO BALDONCINI", "LUCIA BERTEA CASAGRANDE", "ZAIRA BIANI",
                "BENJAMIN CABANILLAS MONNIER", "BIANCA DE LOURDES CAMPANA", "EUGENIA GUADALUPE CAROLINI CIRIACI",
                "JOAQUIN CASTELLINA", "MARTINA CEJAS FONT", "VALENTINA CINGOLANI",
                "MATEO CORNEJO", "CATALINA DI GREGORIO MARINSALDA", "CRISTOBAL ELLENA CITTADINI",
                "JAZMIN FODDANU", "GUADALUPE FOLLONIER OLDANI", "MATEO ANGEL FRANCO",
                "AGUSTIN NICOLAS GAIDO", "LORENZO GALETTO GALVAN", "ISABELLA GASPARINI",
                "JAZMIN GIOTTO", "CATALINA GOMEZ", "RAMIRO JOAQUIN LOVERA",
                "BRIANA ELIZABETH LUQUE", "SANTIAGO ARIEL MANDILE", "LORENZO MASSEI",
                "SOFIA NUÑEZ", "AGUSTINA OCHETTI", "AGUSTINA OLDANI",
                "MERCEDES LUJAN OLMOS", "IGNACIO FEDERICO PERREN", "FRANCESCA PESANDO",
                "AGOSTINA RODRIGUEZ RE", "RENATA ROPOLO", "FAUSTINA SCARAMUZZA",
                "SANTIAGO ANDRES SONZINI FINELLI", "SOLANGE TISSERA", "MAXIMO TORRES FORTINI",
                "SOFIA VALENTINA VECCHIO FERNANDEZ", "DANTE VILLARREAL BALDONCINI", "ALMA MORENA LOURDES ZUPPA"
            ],
            'cuarto': [
                "RENATA BARBERO MARTINEZ", "MARTIN JESUS BELTRAMO", "ARANZA BONFIGLI",
                "TOMAS CAMILETTI", "JUANA CAMPODONICO FALCO", "SANTINO CAMPODÓNICO SALIBI",
                "PAULINA BERENICE CASTELLANO BECK", "ATILIO FERREYRA FRARESSO", "AUGUSTO FUENTES",
                "LARA HERNANDEZ", "THIAGO BAUTISTA INAMORATO MOYANO", "FELIPE LIBRA",
                "BAUTISTA LOPEZ CALCATERRA", "ANALUZ MALDONADO MENDEZ", "LUCERO MIA MARINSALDA SONTULLO",
                "UMMA MILLER LUPIDI", "DELFINA MURIÑO", "JUAN CRUZ OLIVA",
                "FELIPE LUCIANO PICCA", "SOFIA ROSAS", "VALENTIN ROSSI",
                "FRANCESCO SCARAMUZZA", "FRANCO SCARAMUZZA MATTIA", "CATALINA TANTUCCI BERTOTTO",
                "FRANCISCO TANTUCCI VIANO", "BAUTISTA TULIAN", "MAXIMO JOSE ZUPPA"
            ],
            'quinto': [
                "PALOMA AIMAR", "JULIANA BELTRAMO", "VALENTINA MORENA BRAGAYOLI PINO",
                "JOAQUINA BRAVO GARNERO", "AUGUSTO NICOLA CERUTTI", "NICOLAS CICCIOLI",
                "BAUTISTA CORDOBA GONZALEZ", "GENARO LEONEL ESQUIVEL", "JOAQUIN FERNANDEZ",
                "CANDELA FERNANDEZ VENTRE", "RAMIRO FRARESSO", "AARON LUCIANO GALVAN CORDOBA",
                "MELODY LUZ GOMEZ", "JULIAN GUZMAN BAIADERA", "DANTE LIBRA",
                "PAULINA MANZOTTI", "ANA PAULA MARIN", "NAHUEL BENJAMIN MARINSALDA MASSOLA",
                "DANILO MARTINANGELO", "JULIETA MERCADO BOTTOSSO", "ANA PAULA MONTE",
                "FELIPE OLAIZ", "VICTORIA OLDANI", "MARIA DEL ROSARIO OLMOS",
                "ANA CELINA OSTORERO", "MIA PERALTA", "VALENTIN RAMONDA ROSAS",
                "LUCIA BELEN RE OLIVERA", "VALENTINO ROPOLO", "MARTINA TORRES VAZQUEZ"
            ],
            'sexto': [
                "GUADALUPE AIMAR", "JUAN CRUZ ANTONELLO VEGA", "SANTINO ARNOLETTO FERRERO",
                "ANA PAULA BALDONCINI", "LOLA DE LOURDES BLANGINO", "VICTORIA LUZ BORTOLINI",
                "BAUTISTA BROMBIN BENEDETTI", "FERNANDO CACERES", "IGNACIO DANIEL CAMPANA",
                "DELFINA DAFNE CARBAJAL", "ALMA CAROLINI", "CHIARA COMBA GALVAGNO",
                "LOURDES CRISTALLI", "RAMIRO CRISTALLI", "SEBASTIAN DAVICO FLAUMER",
                "CHIARA DUARTE CUEVA", "JUAN CRUZ FANTONI", "LUCÍA MARÍA FRARESSO",
                "VICTORIA FRARESSO", "LORENZO MALIZIA MACAGNO", "AZUL MORENA MATTIA",
                "EMILIA MURATURE", "JUANITA MUÑOZ VERDICCHIO", "LUCIA SCHERMA MARCHEGIANI",
                "CATALINA VICENTE SORIA", "SANTIAGO VILLARREAL", "MAGALI WALKER",
                "MARTINA BELÉN ZORRILLA", "LOURDES PAULINA ZUPPA"
            ]
        }
        
    
    def guardar_datos(self) -> bool:
        """Guarda los datos actuales al archivo JSON"""
        try:
            with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                json.dump(self.alumnos_por_anio, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error guardando datos de alumnos: {e}")
            return False
    
    def obtener_alumnos(self, anio: str) -> List[str]:
        """Obtiene la lista de alumnos de un año específico"""
        return self.alumnos_por_anio.get(anio, [])
    
    def obtener_todos_los_anios(self) -> List[str]:
        """Obtiene la lista de todos los años disponibles"""
        return list(self.alumnos_por_anio.keys())
    
    def agregar_alumno(self, anio: str, nombre: str) -> bool:
        """Agrega un alumno a un año específico"""
        if anio not in self.alumnos_por_anio:
            self.alumnos_por_anio[anio] = []
        
        if nombre not in self.alumnos_por_anio[anio]:
            self.alumnos_por_anio[anio].append(nombre.upper())
            return self.guardar_datos()
        return False
    
    def eliminar_alumno(self, anio: str, nombre: str) -> bool:
        """Elimina un alumno de un año específico"""
        if anio in self.alumnos_por_anio and nombre in self.alumnos_por_anio[anio]:
            self.alumnos_por_anio[anio].remove(nombre)
            return self.guardar_datos()
        return False
    
    def crear_anio(self, anio: str) -> bool:
        """Crea un nuevo año escolar"""
        if anio not in self.alumnos_por_anio:
            self.alumnos_por_anio[anio] = []
            return self.guardar_datos()
        return False
    
    def eliminar_anio(self, anio: str) -> bool:
        """Elimina un año escolar completo"""
        if anio in self.alumnos_por_anio:
            del self.alumnos_por_anio[anio]
            return self.guardar_datos()
        return False
    
    def importar_desde_csv(self, archivo_csv: str, anio: str, 
                          columna_nombre: str = 'nombre') -> Tuple[bool, str, int]:
        """
        Importa alumnos desde un archivo CSV
        
        Returns:
            Tuple[bool, str, int]: (éxito, mensaje, cantidad_importados)
        """
        try:
            if not os.path.exists(archivo_csv):
                return False, "Archivo CSV no encontrado", 0
            
            alumnos_importados = 0
            alumnos_existentes = []
            
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                # Detectar delimitador
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                # Verificar que existe la columna de nombres
                if not reader.fieldnames or columna_nombre not in reader.fieldnames:
                    return False, f"Columna '{columna_nombre}' no encontrada en el CSV", 0
                
                # Crear el año si no existe
                if anio not in self.alumnos_por_anio:
                    self.alumnos_por_anio[anio] = []
                
                for row in reader:
                    nombre = row[columna_nombre].strip().upper()
                    if nombre:  # Solo procesar nombres no vacíos
                        if nombre not in self.alumnos_por_anio[anio]:
                            self.alumnos_por_anio[anio].append(nombre)
                            alumnos_importados += 1
                        else:
                            alumnos_existentes.append(nombre)
            
            # Guardar cambios
            self.guardar_datos()
            
            mensaje = f"Importados: {alumnos_importados} alumnos"
            if alumnos_existentes:
                mensaje += f". {len(alumnos_existentes)} ya existían"
            
            return True, mensaje, alumnos_importados
            
        except Exception as e:
            return False, f"Error al importar CSV: {str(e)}", 0
    
    def exportar_a_csv(self, anio: str, archivo_destino: str) -> Tuple[bool, str]:
        """
        Exporta la lista de alumnos de un año a CSV
        """
        try:
            if anio not in self.alumnos_por_anio:
                return False, f"Año '{anio}' no encontrado"
            
            with open(archivo_destino, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['nombre', 'anio', 'fecha_exportacion'])
                
                fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for alumno in self.alumnos_por_anio[anio]:
                    writer.writerow([alumno, anio, fecha_actual])
            
            return True, f"Exportados {len(self.alumnos_por_anio[anio])} alumnos a {archivo_destino}"
            
        except Exception as e:
            return False, f"Error al exportar CSV: {str(e)}"
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de los alumnos"""
        stats = {
            'total_anios': len(self.alumnos_por_anio),
            'total_alumnos': sum(len(alumnos) for alumnos in self.alumnos_por_anio.values()),
            'por_anio': {},
            'promedio_por_anio': 0
        }
        
        for anio, alumnos in self.alumnos_por_anio.items():
            stats['por_anio'][anio] = len(alumnos)
        
        if stats['total_anios'] > 0:
            stats['promedio_por_anio'] = round(stats['total_alumnos'] / stats['total_anios'], 2)
        
        return stats
    
    def validar_estructura_csv(self, archivo_csv: str) -> Tuple[bool, str, List[str]]:
        """
        Valida la estructura de un archivo CSV antes de importar
        
        Returns:
            Tuple[bool, str, List[str]]: (es_válido, mensaje, columnas_disponibles)
        """
        try:
            if not os.path.exists(archivo_csv):
                return False, "Archivo no encontrado", []
            
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                f.seek(0)
                
                # Detectar delimitador
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(f, delimiter=delimiter)
                columnas = list(reader.fieldnames or [])
                
                if not columnas:
                    return False, "El archivo CSV no tiene encabezados", []
                
                # Contar filas de datos
                filas = sum(1 for row in reader)
                
                mensaje = f"CSV válido: {len(columnas)} columnas, {filas} filas de datos"
                return True, mensaje, columnas
                
        except Exception as e:
            return False, f"Error al validar CSV: {str(e)}", []

# Instancia global del gestor de alumnos
gestor_alumnos = GestorAlumnos()

# Funciones de compatibilidad con el sistema existente
def obtener_alumnos_por_anio():
    """Función de compatibilidad que retorna el diccionario completo"""
    return gestor_alumnos.alumnos_por_anio

def obtener_alumnos(anio: str) -> List[str]:
    """Función de compatibilidad para obtener alumnos de un año"""
    return gestor_alumnos.obtener_alumnos(anio)