#!/usr/bin/env python3
"""
Test simple para verificar métodos de DarwinEX en la GUI
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_darwinex_methods():
    """Test simple para verificar métodos de DarwinEX."""
    try:
        from src.gui.gui_enhanced_rank import EnhancedRankGUI
        
        print("Creando GUI...")
        gui = EnhancedRankGUI()
        print("✅ GUI creada exitosamente")
        
        # Verificar métodos específicos
        required_methods = [
            '_build_darwinex_tab',
            '_run_darwinex_pipeline',
            '_show_darwinex_results_in_gui',
            '_show_darwinex_error',
            '_show_darwinex_results',
            '_build_approved_strategies_tab',
            '_build_rejected_strategies_tab',
            '_build_metrics_tab',
            '_export_darwinex_report',
            '_clear_darwinex_results'
        ]
        
        print("\nVerificando métodos de DarwinEX:")
        for method in required_methods:
            if hasattr(gui, method):
                print(f"  ✅ {method}: PRESENTE")
            else:
                print(f"  ❌ {method}: AUSENTE")
        
        # Verificar pestaña
        if hasattr(gui, 'tab_darwinex'):
            print("  ✅ tab_darwinex: PRESENTE")
        else:
            print("  ❌ tab_darwinex: AUSENTE")
        
        # Verificar variables
        if hasattr(gui, 'darwinex_text'):
            print("  ✅ darwinex_text: PRESENTE")
        else:
            print("  ❌ darwinex_text: AUSENTE")
            
        if hasattr(gui, 'darwinex_results_frame'):
            print("  ✅ darwinex_results_frame: PRESENTE")
        else:
            print("  ❌ darwinex_results_frame: AUSENTE")
        
        gui.destroy()
        print("\n✅ Test completado")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_darwinex_methods() 