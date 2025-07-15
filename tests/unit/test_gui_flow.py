#!/usr/bin/env python3
"""
Script de prueba para verificar el flujo completo de la GUI
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_data_manager():
    """Test del DataManager."""
    try:
        from src.data.data_manager import DataManager
        dm = DataManager()
        assert dm is not None, "DataManager no se creó correctamente"
        logger.info("✅ DataManager: OK")
    except Exception as e:
        logger.error(f"❌ DataManager: Error - {e}")
        assert False, f"DataManager: Error - {e}"

def test_core_engine():
    """Test del Core Engine."""
    try:
        from src.data.data_manager import DataManager
        from src.core.integration_layer import UnifiedEvaluatorEnhanced
        
        # Cargar datos
        dm = DataManager()
        dm.load_all_data()
        
        # Crear evaluador
        evaluator = UnifiedEvaluatorEnhanced()
        assert evaluator is not None, "UnifiedEvaluatorEnhanced no se creó correctamente"
        logger.info("✅ Core Engine: OK")
    except Exception as e:
        logger.error(f"❌ Core Engine: Error - {e}")
        assert False, f"Core Engine: Error - {e}"

def test_gui_import():
    """Test de importación de GUI."""
    try:
        from src.gui.main_window import MainWindow as EnhancedRankGUI
        assert EnhancedRankGUI is not None, "EnhancedRankGUI no se importó correctamente"
        logger.info("✅ GUI: OK")
    except Exception as e:
        logger.error(f"❌ GUI: Error de importación - {e}")
        assert False, f"GUI: Error de importación - {e}"

def test_cli():
    """Test del CLI."""
    try:
        import cli_runner
        assert cli_runner is not None, "cli_runner no se importó correctamente"
        logger.info("✅ CLI: OK")
    except Exception as e:
        logger.error(f"❌ CLI: Error - {e}")
        assert False, f"CLI: Error - {e}"

def test_file_structure():
    """Prueba la estructura de archivos."""
    try:
        logger.info("🧪 Verificando estructura de archivos...")
        
        required_files = [
            'src/gui/main_window.py',
            'src/data/data_manager.py',
            'src/core/integration_layer.py',
            'main.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        assert not missing_files, f"Archivos faltantes: {missing_files}"
        logger.info("✅ Estructura de archivos: Correcta")
    except Exception as e:
        logger.error(f"❌ Estructura de archivos: Error - {e}")
        assert False, f"Estructura de archivos: Error - {e}"

def main():
    """Ejecuta todas las pruebas."""
    logger.info("🚀 Iniciando pruebas del sistema KFORCEVSQVARATIOS")
    logger.info("=" * 60)
    
    tests = [
        ("Estructura de archivos", test_file_structure),
        ("DataManager", test_data_manager),
        ("Core Engine", test_core_engine),
        ("GUI", test_gui_import),
        ("CLI", test_cli)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 Ejecutando: {test_name}")
        try:
            test_func()
            results.append((test_name, True))
            logger.info(f"✅ {test_name}: PASÓ")
        except AssertionError as e:
            logger.error(f"❌ {test_name}: FALLÓ - {e}")
            results.append((test_name, False))
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMEN DE PRUEBAS")
    logger.info("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        logger.info("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está listo.")
    else:
        logger.error("⚠️ Algunas pruebas fallaron. Revisar errores.")

if __name__ == "__main__":
    main() 