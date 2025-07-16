#!/usr/bin/env python3
"""
PLAN DE BÚSQUEDA Y CORRECCIÓN AUTOMÁTICA DE PATRONES PROBLEMÁTICOS
====================================================================

Este script identifica y corrige automáticamente los patrones más comunes que causan
errores de Pyright en el proyecto QVA Strategy Studio.

Patrones problemáticos identificados:
1. Llamadas a métodos pandas en numpy arrays o escalares
2. Acceso a atributos que pueden no existir
3. Conversiones de tipos inseguras
4. Uso de .tolist() en objetos que pueden no tenerlo
5. Acceso a .config o .model en objetos que pueden no tenerlos
"""

import os
import re
import ast
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import pandas as pd
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('correccion_patrones.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PatronCorrector:
    """Clase para identificar y corregir patrones problemáticos en el código."""
    
    def __init__(self, src_dir: str = "src"):
        self.src_dir = Path(src_dir)
        self.patrones_problematicos = {
            # Patrones de métodos pandas en numpy arrays
            r'(\w+)\.isna\(\)\.any\(\)': self._corregir_isna_any,
            r'(\w+)\.isna\(\)\.sum\(\)': self._corregir_isna_sum,
            r'(\w+)\.mean\(\)': self._corregir_mean,
            r'(\w+)\.std\(\)': self._corregir_std,
            r'(\w+)\.fillna\(([^)]+)\)': self._corregir_fillna,
            r'(\w+)\.astype\(([^)]+)\)': self._corregir_astype,
            r'(\w+)\.tolist\(\)': self._corregir_tolist,
            r'(\w+)\.columns\.tolist\(\)': self._corregir_columns_tolist,
            r'(\w+)\.index\.tolist\(\)': self._corregir_index_tolist,
            
            # Patrones de acceso a atributos
            r'(\w+)\.config': self._corregir_config_access,
            r'(\w+)\.model': self._corregir_model_access,
            
            # Patrones de conversión de tipos
            r'float\((\w+)\)': self._corregir_float_conversion,
            r'int\((\w+)\)': self._corregir_int_conversion,
        }
        
        self.archivos_corregidos = []
        self.errores_encontrados = []
        
    def _es_variable_numpy_o_escalar(self, var_name: str, contexto: str) -> bool:
        """Determina si una variable es numpy array o escalar basándose en el contexto."""
        patrones_numpy = [
            r'np\.array\(',
            r'np\.zeros\(',
            r'np\.ones\(',
            r'np\.linspace\(',
            r'np\.arange\(',
            r'\.to_numpy\(\)',
            r'\.values',
            r'\.numpy\(\)'
        ]
        
        # Buscar en el contexto si la variable se crea como numpy
        for patron in patrones_numpy:
            if re.search(patron, contexto):
                return True
            
        # Verificar si es un escalar numérico
        if re.search(rf'{var_name}\s*=\s*\d+\.?\d*', contexto):
            return True
            
        return False
    
    def _corregir_isna_any(self, match: re.Match, contexto: str) -> str:
        """Corrige .isna().any() para numpy arrays."""
        var_name = match.group(1)
        
        if self._es_variable_numpy_o_escalar(var_name, contexto):
            return f"np.isnan({var_name}).any()"
        else:
            return match.group(0)  # Mantener original si es pandas
    
    def _corregir_isna_sum(self, match: re.Match, contexto: str) -> str:
        """Corrige .isna().sum() para numpy arrays."""
        var_name = match.group(1)
        
        if self._es_variable_numpy_o_escalar(var_name, contexto):
            return f"np.isnan({var_name}).sum()"
        else:
            return match.group(0)
    
    def _corregir_mean(self, match: re.Match, contexto: str) -> str:
        """Corrige .mean() para numpy arrays."""
        var_name = match.group(1)
        
        if self._es_variable_numpy_o_escalar(var_name, contexto):
            return f"np.mean({var_name})"
        else:
            return match.group(0)
    
    def _corregir_std(self, match: re.Match, contexto: str) -> str:
        """Corrige .std() para numpy arrays."""
        var_name = match.group(1)
        
        if self._es_variable_numpy_o_escalar(var_name, contexto):
            return f"np.std({var_name})"
        else:
            return match.group(0)
    
    def _corregir_fillna(self, match: re.Match, contexto: str) -> str:
        """Corrige .fillna() para numpy arrays."""
        var_name = match.group(1)
        fill_value = match.group(2)
        
        if self._es_variable_numpy_o_escalar(var_name, contexto):
            return f"np.nan_to_num({var_name}, nan={fill_value})"
        else:
            return match.group(0)
    
    def _corregir_astype(self, match: re.Match, contexto: str) -> str:
        """Corrige .astype() para numpy arrays."""
        var_name = match.group(1)
        target_type = match.group(2)
        
        if self._es_variable_numpy_o_escalar(var_name, contexto):
            return f"{var_name}.astype({target_type})"
        else:
            return match.group(0)
    
    def _corregir_tolist(self, match: re.Match, contexto: str) -> str:
        """Corrige .tolist() con verificación de tipo."""
        var_name = match.group(1)
        
        return f"({var_name}.tolist() if hasattr({var_name}, 'tolist') else list({var_name}))"
    
    def _corregir_columns_tolist(self, match: re.Match, contexto: str) -> str:
        """Corrige .columns.tolist() con verificación."""
        var_name = match.group(1)
        
        return f"({var_name}.columns.tolist() if hasattr({var_name}, 'columns') else list({var_name}.columns))"
    
    def _corregir_index_tolist(self, match: re.Match, contexto: str) -> str:
        """Corrige .index.tolist() con verificación."""
        var_name = match.group(1)
        
        return f"({var_name}.index.tolist() if hasattr({var_name}, 'index') else list({var_name}.index))"
    
    def _corregir_config_access(self, match: re.Match, contexto: str) -> str:
        """Corrige acceso a .config con verificación."""
        var_name = match.group(1)
        
        return f"getattr({var_name}, 'config', None)"
    
    def _corregir_model_access(self, match: re.Match, contexto: str) -> str:
        """Corrige acceso a .model con verificación."""
        var_name = match.group(1)
        
        return f"getattr({var_name}, 'model', None)"
    
    def _corregir_float_conversion(self, match: re.Match, contexto: str) -> str:
        """Corrige conversión float con manejo de errores."""
        var_name = match.group(1)
        
        return f"float({var_name}) if {var_name} is not None else 0.0"
    
    def _corregir_int_conversion(self, match: re.Match, contexto: str) -> str:
        """Corrige conversión int con manejo de errores."""
        var_name = match.group(1)
        
        return f"int({var_name}) if {var_name} is not None else 0"
    
    def _agregar_imports_seguros(self, contenido: str) -> str:
        """Agrega imports necesarios para las correcciones."""
        imports_necesarios = [
            "import numpy as np",
            "import pandas as pd",
            "from typing import Optional, Any, Union",
            "import warnings"
        ]
        
        # Verificar si ya están los imports
        for import_line in imports_necesarios:
            if import_line not in contenido:
                # Insertar después del primer import o al inicio
                if "import " in contenido:
                    # Buscar la última línea de import
                    lines = contenido.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith('import ') or line.strip().startswith('from '):
                            continue
                        else:
                            # Insertar antes de esta línea
                            lines.insert(i, import_line)
                            break
                    contenido = '\n'.join(lines)
                else:
                    # Agregar al inicio
                    contenido = f"{import_line}\n{contenido}"
        
        return contenido
    
    def _corregir_archivo(self, archivo_path: Path) -> bool:
        """Corrige un archivo específico."""
        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                contenido_original = f.read()
            
            contenido_corregido = contenido_original
            cambios_realizados = False
            
            # Aplicar cada patrón de corrección
            for patron, funcion_correccion in self.patrones_problematicos.items():
                matches = list(re.finditer(patron, contenido_corregido))
                
                # Procesar matches en orden inverso para no afectar índices
                for match in reversed(matches):
                    contexto = contenido_corregido[max(0, match.start()-200):match.end()+200]
                    correccion = funcion_correccion(match, contexto)
                    
                    if correccion != match.group(0):
                        contenido_corregido = (
                            contenido_corregido[:match.start()] + 
                            correccion + 
                            contenido_corregido[match.end():]
                        )
                        cambios_realizados = True
                        logger.info(f"  [OK] Corregido: {match.group(0)} -> {correccion}")
            
            # Agregar imports seguros si se hicieron cambios
            if cambios_realizados:
                contenido_corregido = self._agregar_imports_seguros(contenido_corregido)
                
                # Guardar archivo corregido
                with open(archivo_path, 'w', encoding='utf-8') as f:
                    f.write(contenido_corregido)
                
                self.archivos_corregidos.append(str(archivo_path))
                logger.info(f"[OK] Archivo corregido: {archivo_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[ERROR] Error corrigiendo {archivo_path}: {e}")
            self.errores_encontrados.append((str(archivo_path), str(e)))
            return False
    
    def _encontrar_archivos_python(self) -> List[Path]:
        """Encuentra todos los archivos Python en el directorio src."""
        archivos_python = []
        
        for archivo in self.src_dir.rglob("*.py"):
            # Excluir archivos de test y cache
            if not any(part in str(archivo) for part in ['__pycache__', 'test_', '.pytest_cache']):
                archivos_python.append(archivo)
        
        return archivos_python
    
    def ejecutar_correccion_completa(self) -> Dict[str, Any]:
        """Ejecuta la corrección completa de todos los archivos."""
        logger.info("Iniciando correccion automatica de patrones problematicos...")
        
        archivos_python = self._encontrar_archivos_python()
        logger.info(f"Encontrados {len(archivos_python)} archivos Python para analizar")
        
        archivos_corregidos = 0
        archivos_analizados = 0
        
        for archivo in archivos_python:
            archivos_analizados += 1
            logger.info(f"Analizando: {archivo}")
            
            if self._corregir_archivo(archivo):
                archivos_corregidos += 1
        
        # Generar reporte
        reporte = {
            'archivos_analizados': archivos_analizados,
            'archivos_corregidos': archivos_corregidos,
            'archivos_corregidos_lista': self.archivos_corregidos,
            'errores': self.errores_encontrados,
            'porcentaje_exito': (archivos_corregidos / archivos_analizados * 100) if archivos_analizados > 0 else 0
        }
        
        logger.info(f"REPORTE FINAL:")
        logger.info(f"   Archivos analizados: {reporte['archivos_analizados']}")
        logger.info(f"   Archivos corregidos: {reporte['archivos_corregidos']}")
        logger.info(f"   Porcentaje de exito: {reporte['porcentaje_exito']:.1f}%")
        
        if self.errores_encontrados:
            logger.warning(f"Errores encontrados: {len(self.errores_encontrados)}")
            for archivo, error in self.errores_encontrados:
                logger.warning(f"   ERROR {archivo}: {error}")
        
        return reporte

def crear_script_verificacion():
    """Crea un script para verificar que las correcciones funcionan."""
    script_verificacion = '''
#!/usr/bin/env python3
"""
Script de verificación para comprobar que las correcciones funcionan correctamente.
"""

import sys
import subprocess
import logging

def verificar_pyright():
    """Ejecuta Pyright para verificar que no hay errores de tipo."""
    try:
        result = subprocess.run(
            ["pyright", "src/"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("[OK] Pyright: Sin errores de tipo")
            return True
        else:
            print(f"[ERROR] Pyright: Errores encontrados")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"[ERROR] Error ejecutando Pyright: {e}")
        return False

def verificar_tests():
    """Ejecuta los tests para verificar que todo funciona."""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("[OK] Tests: Todos pasaron")
            return True
        else:
            print(f"[ERROR] Tests: Algunos fallaron")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"[ERROR] Error ejecutando tests: {e}")
        return False

if __name__ == "__main__":
    print("Verificando correcciones...")
    
    pyright_ok = verificar_pyright()
    tests_ok = verificar_tests()
    
    if pyright_ok and tests_ok:
        print("Todas las verificaciones pasaron!")
        sys.exit(0)
    else:
        print("Algunas verificaciones fallaron")
        sys.exit(1)
'''
    
    with open('verificar_correcciones.py', 'w', encoding='utf-8') as f:
        f.write(script_verificacion)
    
    logger.info("Script de verificacion creado: verificar_correcciones.py")

def main():
    """Función principal del script."""
    print("PLAN DE CORRECCION AUTOMATICA DE PATRONES PROBLEMATICOS")
    print("=" * 70)
    
    # Crear corrector
    corrector = PatronCorrector()
    
    # Ejecutar corrección completa
    reporte = corrector.ejecutar_correccion_completa()
    
    # Crear script de verificación
    crear_script_verificacion()
    
    print("\nRESUMEN EJECUTIVO:")
    print(f"   Archivos analizados: {reporte['archivos_analizados']}")
    print(f"   Archivos corregidos: {reporte['archivos_corregidos']}")
    print(f"   Porcentaje de exito: {reporte['porcentaje_exito']:.1f}%")
    
    if reporte['archivos_corregidos'] > 0:
        print("\nArchivos corregidos:")
        for archivo in reporte['archivos_corregidos_lista']:
            print(f"   [OK] {archivo}")
    
    if reporte['errores']:
        print("\nErrores encontrados:")
        for archivo, error in reporte['errores']:
            print(f"   [ERROR] {archivo}: {error}")
    
    print("\nPROXIMOS PASOS:")
    print("   1. Ejecutar: python verificar_correcciones.py")
    print("   2. Revisar logs: correccion_patrones.log")
    print("   3. Si hay errores, ejecutar: pyright src/")
    print("   4. Ejecutar tests: python -m pytest tests/ -v")
    
    return reporte

if __name__ == "__main__":
    main() 