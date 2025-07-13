#!/usr/bin/env python3
"""
Script de debug para ejecutar la GUI y capturar errores
"""

import sys
import os
import traceback

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("🔍 Iniciando debug de la GUI...")
    
    try:
        print("📦 Importando módulos...")
        import tkinter as tk
        print("✅ tkinter importado")
        
        import pandas as pd
        print("✅ pandas importado")
        
        import numpy as np
        print("✅ numpy importado")
        
        print("📦 Importando módulos del proyecto...")
        from src.core.integration_layer import FactorKElite96Enhanced
        print("✅ core_engine_enhanced importado")
        
        from data_manager import DataManager
        print("✅ data_manager importado")
        
        from asesor_financiero_inteligente import ejecutar_analisis_completo
        print("✅ asesor_financiero_inteligente importado")
        
        print("📦 Importando GUI...")
        from gui_enhanced_rank import EnhancedRankGUI
        print("✅ GUI importada")
        
        print("🚀 Iniciando aplicación GUI...")
        app = EnhancedRankGUI()
        print("✅ GUI creada")
        
        print("🔄 Iniciando mainloop...")
        app.mainloop()
        print("✅ GUI cerrada")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("📋 Traceback completo:")
        traceback.print_exc()
        return 1
    
    print("✅ Debug completado exitosamente")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 