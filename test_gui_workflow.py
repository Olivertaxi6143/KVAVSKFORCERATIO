#!/usr/bin/env python3
"""
Script de prueba del flujo de trabajo de la GUI
Simula el uso real de la interfaz gráfica
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import tkinter as tk
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gui_components():
    """Prueba los componentes principales de la GUI."""
    try:
        logger.info("🧪 Probando componentes de la GUI...")
        
        # Importar componentes de la GUI
        from src.gui_enhanced_rank import EnhancedRankGUI
        from src.data_manager import DataManager
        from src.core_engine_enhanced import UnifiedEvaluatorEnhanced
        
        logger.info("✅ Componentes importados correctamente")
        
        # Simular carga de datos
        logger.info("📊 Simulando carga de datos...")
        dm = DataManager()
        success = dm.load_kpis_data('DatabankExport_M1.csv')
        
        if not success:
            logger.error("❌ Error cargando datos KPI")
            return False
            
        data = dm.kpis_data
        if data is not None:
            logger.info(f"✅ Datos cargados: {len(data)} estrategias")
        else:
            logger.error("❌ No hay datos disponibles")
            return False
        
        # Simular análisis
        logger.info("🔬 Simulando análisis...")
        evaluator = UnifiedEvaluatorEnhanced()
        if data is not None:
            results = evaluator.evaluate_strategies_unified(data)
            logger.info(f"✅ Análisis completado: {len(results)} estrategias procesadas")
        else:
            logger.error("❌ No hay datos para analizar")
            return False
        
        # Verificar que la GUI se puede crear
        logger.info("🖥️ Verificando creación de GUI...")
        try:
            # Crear ventana temporal para prueba
            root = tk.Tk()
            root.withdraw()  # Ocultar ventana
            
            # Crear instancia de GUI
            gui = EnhancedRankGUI()
            logger.info("✅ GUI creada correctamente")
            
            # Cerrar ventana de prueba
            root.destroy()
            
        except Exception as e:
            logger.error(f"❌ Error creando GUI: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de componentes: {e}")
        return False

def test_gui_functionality():
    """Prueba la funcionalidad específica de la GUI."""
    try:
        logger.info("🧪 Probando funcionalidad de la GUI...")
        
        # Verificar archivos necesarios
        required_files = [
            'DatabankExport_M1.csv',
            'DATOSMQL5.csv',
            'src/gui_enhanced_rank.py',
            'src/data_manager.py',
            'src/core_engine_enhanced.py'
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                logger.error(f"❌ Archivo faltante: {file_path}")
                return False
        
        logger.info("✅ Todos los archivos necesarios están presentes")
        
        # Verificar configuración
        config_file = 'config/trading_config.json'
        if Path(config_file).exists():
            logger.info("✅ Archivo de configuración encontrado")
        else:
            logger.warning("⚠️ Archivo de configuración no encontrado, se usará configuración por defecto")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de funcionalidad: {e}")
        return False

def test_data_integration():
    """Prueba la integración de datos en la GUI."""
    try:
        logger.info("🧪 Probando integración de datos...")
        
        from src.data_manager import DataManager
        from src.core_engine_enhanced import UnifiedEvaluatorEnhanced
        
        # Cargar datos
        dm = DataManager()
        success = dm.load_kpis_data('DatabankExport_M1.csv')
        
        if not success:
            logger.error("❌ Error cargando datos")
            return False
        
        data = dm.kpis_data
        if data is None:
            logger.error("❌ No hay datos disponibles")
            return False
        
        # Verificar columnas importantes
        required_columns = ['Strategy_Name', 'Profit_factor', 'Sharpe_Ratio', 'CalmarRatio']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            logger.warning(f"⚠️ Columnas faltantes: {missing_columns}")
        else:
            logger.info("✅ Todas las columnas requeridas están presentes")
        
        # Probar análisis
        evaluator = UnifiedEvaluatorEnhanced()
        results = evaluator.evaluate_strategies_unified(data)
        
        # Verificar resultados
        if 'QVA_Score' in results.columns:
            logger.info("✅ QVA Score calculado correctamente")
        else:
            logger.warning("⚠️ QVA Score no encontrado en resultados")
        
        if 'Quality_Category' in results.columns:
            logger.info("✅ Categorías de calidad asignadas")
        else:
            logger.warning("⚠️ Categorías de calidad no encontradas")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en integración de datos: {e}")
        return False

def main():
    """Ejecuta todas las pruebas de la GUI."""
    logger.info("🚀 Iniciando pruebas del flujo de trabajo de la GUI")
    logger.info("=" * 60)
    
    tests = [
        ("Componentes de GUI", test_gui_components),
        ("Funcionalidad de GUI", test_gui_functionality),
        ("Integración de datos", test_data_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 Ejecutando: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                logger.info(f"✅ {test_name}: PASÓ")
            else:
                logger.error(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMEN DE PRUEBAS DE GUI")
    logger.info("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        logger.info("🎉 ¡TODAS LAS PRUEBAS DE GUI PASARON!")
        logger.info("✅ La GUI está lista para usar")
        logger.info("🚀 Para ejecutar la GUI: python src/gui_enhanced_rank.py")
        return True
    else:
        logger.error("⚠️ Algunas pruebas de GUI fallaron")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 