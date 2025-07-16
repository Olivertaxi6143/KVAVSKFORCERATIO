#!/usr/bin/env python3
"""
Script de Refactorización Automática para Consolidación de Utils
==============================================================

Este script automatiza la consolidación de funciones duplicadas en las carpetas utils
siguiendo el plan de auditoría profesional.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

import os
import shutil
import re
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UtilsConsolidator:
    """Consolidador profesional de carpetas y funciones utils."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_utils_refactor"
        self.changes_made = []
        
    def create_backup(self) -> bool:
        """Crea backup completo antes de la refactorización."""
        try:
            logger.info("🔄 Creando backup completo...")
            
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            self.backup_dir.mkdir(exist_ok=True)
            
            # Backup de carpetas críticas
            critical_dirs = [
                "src/analysis/utils",
                "src/data",
                "src/core/utils"
            ]
            
            for dir_path in critical_dirs:
                source = self.project_root / dir_path
                if source.exists():
                    dest = self.backup_dir / dir_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(source, dest)
                    logger.info(f"✅ Backup creado: {dir_path}")
            
            logger.info("✅ Backup completado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return False
    
    def move_unique_functions(self) -> bool:
        """Mueve funciones únicas de analysis/utils a core/utils."""
        try:
            logger.info("🔄 Moviendo funciones únicas...")
            
            analysis_utils = self.project_root / "src/analysis/utils"
            core_utils = self.project_root / "src/core/utils"
            
            if not analysis_utils.exists():
                logger.warning("⚠️ src/analysis/utils no existe")
                return True
            
            # Funciones únicas a mover
            unique_files = [
                "visualization.py",
                "metrics_calculation.py"
            ]
            
            for file_name in unique_files:
                source = analysis_utils / file_name
                dest = core_utils / file_name
                
                if source.exists():
                    shutil.move(str(source), str(dest))
                    logger.info(f"✅ Movido: {file_name}")
                    self.changes_made.append(f"MOVED: {source} -> {dest}")
                else:
                    logger.warning(f"⚠️ Archivo no encontrado: {file_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error moviendo funciones únicas: {e}")
            return False
    
    def remove_duplicate_files(self) -> bool:
        """Elimina archivos duplicados de analysis/utils."""
        try:
            logger.info("🔄 Eliminando archivos duplicados...")
            
            analysis_utils = self.project_root / "src/analysis/utils"
            
            if not analysis_utils.exists():
                return True
            
            # Archivos duplicados a eliminar
            duplicate_files = [
                "data_processing.py",
                "validation.py"
            ]
            
            for file_name in duplicate_files:
                file_path = analysis_utils / file_name
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"✅ Eliminado: {file_name}")
                    self.changes_made.append(f"DELETED: {file_path}")
            
            # Eliminar carpeta vacía
            if analysis_utils.exists() and not any(analysis_utils.iterdir()):
                analysis_utils.rmdir()
                logger.info("✅ Carpeta analysis/utils eliminada (vacía)")
                self.changes_made.append(f"DELETED_DIR: {analysis_utils}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error eliminando duplicados: {e}")
            return False
    
    def refactor_data_utils(self) -> bool:
        """Refactoriza src/data/data_utils.py eliminando duplicados."""
        try:
            logger.info("🔄 Refactorizando data_utils.py...")
            
            data_utils_path = self.project_root / "src/data/data_utils.py"
            
            if not data_utils_path.exists():
                logger.warning("⚠️ src/data/data_utils.py no existe")
                return True
            
            # Leer contenido actual
            with open(data_utils_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Funciones a eliminar (duplicadas en core/utils)
            functions_to_remove = [
                r'def validate_dataframe\(.*?\):.*?(?=\n\ndef|\n\n"""|\n\n$)',
                r'def to_float\(.*?\):.*?(?=\n\ndef|\n\n"""|\n\n$)'
            ]
            
            original_content = content
            for pattern in functions_to_remove:
                content = re.sub(pattern, '', content, flags=re.DOTALL)
            
            # Limpiar líneas vacías múltiples
            content = re.sub(r'\n\n\n+', '\n\n', content)
            
            # Escribir contenido refactorizado
            with open(data_utils_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("✅ data_utils.py refactorizado")
            self.changes_made.append(f"REFACTORED: {data_utils_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error refactorizando data_utils.py: {e}")
            return False
    
    def update_imports(self) -> bool:
        """Actualiza imports en archivos Python."""
        try:
            logger.info("🔄 Actualizando imports...")
            
            # Patrones de reemplazo
            replacements = [
                (r'from src\.analysis\.utils\.data_processing', 'from src.core.utils.data_utils'),
                (r'from src\.data\.data_utils', 'from src.core.utils.data_utils'),
                (r'from src\.analysis\.utils\.validation', 'from src.core.utils.validation_utils'),
                (r'from src\.data\.data_processing', 'from src.core.utils.data_utils'),
            ]
            
            # Buscar archivos Python
            python_files = list(self.project_root.rglob("*.py"))
            
            files_updated = 0
            for file_path in python_files:
                if "backup" in str(file_path) or "__pycache__" in str(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    for old_pattern, new_pattern in replacements:
                        content = re.sub(old_pattern, new_pattern, content)
                    
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info(f"✅ Imports actualizados: {file_path}")
                        files_updated += 1
                        self.changes_made.append(f"UPDATED_IMPORTS: {file_path}")
                
                except Exception as e:
                    logger.warning(f"⚠️ Error procesando {file_path}: {e}")
            
            logger.info(f"✅ {files_updated} archivos actualizados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando imports: {e}")
            return False
    
    def create_unified_init(self) -> bool:
        """Crea __init__.py unificado para core/utils."""
        try:
            logger.info("🔄 Creando __init__.py unificado...")
            
            init_content = '''"""
Utils Unificados del Core Engine
================================

Este módulo proporciona acceso unificado a todas las utilidades del core engine:
- data_utils: Funciones de procesamiento de datos
- type_converters: Conversiones seguras de tipos
- validation_utils: Validación robusta de datos
- error_handler: Manejo centralizado de errores

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

# Imports principales
from .data_utils import (
    validate_dataframe,
    normalize_series,
    clean_extreme_values,
    improve_missing_data_handling,
    calculate_percentiles
)

from .type_converters import (
    safe_float,
    safe_int,
    safe_bool,
    convert_to_numeric
)

from .validation_utils import (
    validate_dataframe as validate_dataframe_detailed,
    validate_numeric_data,
    validate_categorical_data
)

from .error_handler import (
    handle_data_error,
    log_error_with_context,
    create_error_summary
)

# Aliases para compatibilidad
__all__ = [
    # Data utils
    'validate_dataframe',
    'normalize_series', 
    'clean_extreme_values',
    'improve_missing_data_handling',
    'calculate_percentiles',
    
    # Type converters
    'safe_float',
    'safe_int',
    'safe_bool',
    'convert_to_numeric',
    
    # Validation
    'validate_dataframe_detailed',
    'validate_numeric_data',
    'validate_categorical_data',
    
    # Error handling
    'handle_data_error',
    'log_error_with_context',
    'create_error_summary'
]
'''
            
            init_path = self.project_root / "src/core/utils/__init__.py"
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(init_content)
            
            logger.info("✅ __init__.py unificado creado")
            self.changes_made.append(f"CREATED: {init_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando __init__.py: {e}")
            return False
    
    def run_consolidation(self) -> bool:
        """Ejecuta la consolidación completa."""
        try:
            logger.info("🚀 Iniciando consolidación de utils...")
            
            steps = [
                ("Crear backup", self.create_backup),
                ("Mover funciones únicas", self.move_unique_functions),
                ("Eliminar duplicados", self.remove_duplicate_files),
                ("Refactorizar data_utils", self.refactor_data_utils),
                ("Actualizar imports", self.update_imports),
                ("Crear __init__.py unificado", self.create_unified_init)
            ]
            
            for step_name, step_func in steps:
                logger.info(f"📋 Ejecutando: {step_name}")
                if not step_func():
                    logger.error(f"❌ Falló: {step_name}")
                    return False
                logger.info(f"✅ Completado: {step_name}")
            
            logger.info("🎉 Consolidación completada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en consolidación: {e}")
            return False
    
    def generate_report(self) -> str:
        """Genera reporte de cambios realizados."""
        report = f"""
# 📊 REPORTE DE CONSOLIDACIÓN UTILS

## 📈 Resumen de Cambios
- **Archivos movidos**: {len([c for c in self.changes_made if c.startswith('MOVED')])}
- **Archivos eliminados**: {len([c for c in self.changes_made if c.startswith('DELETED')])}
- **Archivos refactorizados**: {len([c for c in self.changes_made if c.startswith('REFACTORED')])}
- **Imports actualizados**: {len([c for c in self.changes_made if c.startswith('UPDATED_IMPORTS')])}

## 📋 Cambios Detallados
"""
        
        for change in self.changes_made:
            report += f"- {change}\n"
        
        report += f"""
## 🎯 Próximos Pasos
1. Ejecutar tests de regresión
2. Verificar que no hay imports rotos
3. Actualizar documentación
4. Validar funcionalidad completa

## 📁 Backup
Backup disponible en: {self.backup_dir}
"""
        
        return report

def main():
    """Función principal del script."""
    print("🔍 SCRIPT DE CONSOLIDACIÓN UTILS")
    print("=" * 50)
    
    consolidator = UtilsConsolidator()
    
    # Confirmar ejecución
    response = input("¿Desea ejecutar la consolidación? (y/N): ").lower()
    if response != 'y':
        print("❌ Consolidación cancelada")
        return
    
    # Ejecutar consolidación
    success = consolidator.run_consolidation()
    
    if success:
        print("\n✅ CONSOLIDACIÓN EXITOSA")
        print(consolidator.generate_report())
        
        # Guardar reporte
        report_path = Path("REPORTE_CONSOLIDACION_UTILS.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(consolidator.generate_report())
        print(f"📄 Reporte guardado en: {report_path}")
        
    else:
        print("\n❌ CONSOLIDACIÓN FALLÓ")
        print("Revise los logs para más detalles")

if __name__ == "__main__":
    main() 