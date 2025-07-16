#!/usr/bin/env python3
"""
Script para corregir imports obsoletos de gui_enhanced_rank.py

Este script actualiza todos los imports que hacen referencia al archivo
gui_enhanced_rank.py obsoleto y los reemplaza con los imports correctos
de la nueva estructura modularizada.
"""

import os
import re
import glob
from pathlib import Path
from typing import List, Tuple

def find_files_with_obsolete_imports() -> List[str]:
    """Encuentra todos los archivos que importan gui_enhanced_rank."""
    pattern = "**/*.py"
    files = []
    
    for file_path in glob.glob(pattern, recursive=True):
        if "node_modules" in file_path or "__pycache__" in file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "gui_enhanced_rank" in content:
                    files.append(file_path)
        except Exception as e:
            print(f"⚠️ Error leyendo {file_path}: {e}")
    
    return files

def get_replacement_imports() -> List[Tuple[str, str]]:
    """Define los reemplazos de imports."""
    return [
        # Imports principales
        (
            "from src.gui.main_window import MainWindow as EnhancedRankGUI",
            "from src.gui.main_window import MainWindow as EnhancedRankGUI"
        ),
        (
            "from src.gui.main_window import MainWindow as EnhancedRankGUI", 
            "from src.gui.main_window import MainWindow as EnhancedRankGUI"
        ),
        (
            "from src.gui.utils import load_data_with_datamanager as read_and_prepare",
            "from src.gui.utils import load_data_with_datamanager as read_and_prepare"
        ),
        (
            "from src.gui.utils import GUIAnalysisError as ErrorDisplayManager",
            "from src.gui.utils import GUIAnalysisError as ErrorDisplayManager"
        ),
        (
            "from src.gui.main_window import MainWindow as QVAStrategyRankerGUI",
            "from src.gui.main_window import MainWindow as QVAStrategyRankerGUI"
        ),
        
        # Imports de normalización
        (
            "from src.data.data_manager import DataManager",
            "from src.data.data_manager import DataManager"
        ),
        
        # Rutas de archivos
        (
            "'src/gui/main_window.py'",
            "'src/gui/main_window.py'"
        ),
        (
            "'src.gui.main_window'",
            "'src.gui.main_window'"
        ),
        
        # Comentarios y referencias
        (
            "# Lógica actual del asesor (líneas en src/gui/main_window.py)",
            "# Lógica actual del asesor (líneas en src/gui/main_window.py)"
        ),
        (
            "Script para limpiar el archivo main_window.py",
            "Script para limpiar el archivo main_window.py"
        ),
        (
            "input_file = 'src/gui/main_window.py'",
            "input_file = 'src/gui/main_window.py'"
        ),
        (
            "output_file = 'src/gui/main_window_clean.py'",
            "output_file = 'src/gui/main_window_clean.py'"
        ),
    ]

def fix_file_imports(file_path: str) -> bool:
    """Corrige los imports obsoletos en un archivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements = get_replacement_imports()
        
        for old_import, new_import in replacements:
            content = content.replace(old_import, new_import)
        
        # Si el contenido cambió, escribir el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corregido: {file_path}")
            return True
        else:
            print(f"ℹ️ Sin cambios: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal del script."""
    print("🔧 Iniciando corrección de imports obsoletos...")
    
    # Encontrar archivos con imports obsoletos
    files_to_fix = find_files_with_obsolete_imports()
    
    if not files_to_fix:
        print("✅ No se encontraron archivos con imports obsoletos")
        return
    
    print(f"📁 Encontrados {len(files_to_fix)} archivos para corregir:")
    for file_path in files_to_fix:
        print(f"  - {file_path}")
    
    # Corregir cada archivo
    fixed_count = 0
    for file_path in files_to_fix:
        if fix_file_imports(file_path):
            fixed_count += 1
    
    print(f"\n📊 Resumen:")
    print(f"  - Archivos procesados: {len(files_to_fix)}")
    print(f"  - Archivos corregidos: {fixed_count}")
    print(f"  - Archivos sin cambios: {len(files_to_fix) - fixed_count}")
    
    if fixed_count > 0:
        print("\n✅ Corrección completada exitosamente")
    else:
        print("\nℹ️ No se realizaron cambios")

if __name__ == "__main__":
    main() 