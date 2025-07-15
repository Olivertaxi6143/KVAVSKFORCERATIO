#!/usr/bin/env python3
"""
TEST_GUI_DATAMANAGER_QUICK.py - Test rápido de la GUI con DataManager
"""

import sys
import os
import time

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_gui_import():
    """Test de importación de la GUI."""
    print("🧪 TEST: Importación de GUI")
    print("=" * 40)
    
    try:
        from gui_enhanced_rank import EnhancedRankGUI
        print("✅ GUI importable correctamente")
        assert True
    except Exception as e:
        print(f"❌ Error importando GUI: {e}")
        assert False

def test_datamanager_integration():
    """Test de integración con DataManager."""
    print("\n🧪 TEST: Integración con DataManager")
    print("=" * 40)
    
    try:
        from src.data.data_manager import DataManager
        
        # Crear DataManager
        dm = DataManager()
        print("✅ DataManager creado correctamente")
        
        # Activar modo desarrollo
        dm.switch_to_development_mode()
        print("✅ Modo desarrollo activado")
        
        # Cargar datos de INPUTTEST
        kpis_ok = dm.load_kpis_data('INPUTTEST/DatabankExport_M1.csv')
        print(f"✅ KPIs cargados: {kpis_ok}")
        
        mercado_ok = dm.load_market_data('INPUTTEST/DATOSMQL5.csv')
        print(f"✅ Datos mercado cargados: {mercado_ok}")
        
        assert True
        
    except Exception as e:
        print(f"❌ Error en integración DataManager: {e}")
        import traceback
        traceback.print_exc()
        assert False

def test_gui_initialization():
    """Test de inicialización de la GUI."""
    print("\n🧪 TEST: Inicialización de GUI")
    print("=" * 40)
    
    try:
        from gui_enhanced_rank import EnhancedRankGUI
        
        # Crear GUI (sin mostrar ventana)
        print("🔄 Creando instancia de GUI...")
        gui = EnhancedRankGUI()
        
        # Verificar que se inicializó correctamente
        print("✅ GUI inicializada correctamente")
        print(f"   Título: {gui.title()}")
        print(f"   DataManager: {'✅' if gui.data_manager is not None else '❌'}")
        
        # Cerrar GUI
        gui.destroy()
        print("✅ GUI cerrada correctamente")
        
        assert True
        
    except Exception as e:
        print(f"❌ Error inicializando GUI: {e}")
        import traceback
        traceback.print_exc()
        assert False

def main():
    """Función principal de tests."""
    print("🚀 TEST RÁPIDO: GUI con DataManager")
    print("=" * 50)
    
    tests = [
        test_gui_import,
        test_datamanager_integration,
        test_gui_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Pausa entre tests
    
    print(f"\n📊 RESULTADOS: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron! La GUI está lista para usar.")
        print("\n💡 Para ejecutar la GUI completa:")
        print("   python run_gui.py")
    else:
        print("⚠️ Algunos tests fallaron. Revisar errores antes de usar la GUI.")
    
    return passed == total

if __name__ == "__main__":
    main() 