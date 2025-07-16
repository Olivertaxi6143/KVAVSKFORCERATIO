#!/usr/bin/env python3
"""
Script para ejecutar la GUI del sistema KFORCEVSQVARATIOS
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.gui.main_window import MainWindow as EnhancedRankGUI
    
    print("🚀 Iniciando GUI KFORCEVSQVARATIOS...")
    print("📊 Sistema de Análisis Cuantitativo")
    print("=" * 50)
    
    # Crear y ejecutar la GUI
    app = EnhancedRankGUI()
    app.mainloop()
    
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("💡 Asegúrate de que todos los archivos estén en la carpeta src/")
    
except Exception as e:
    print(f"❌ Error ejecutando la GUI: {e}")
    import traceback
    traceback.print_exc() 