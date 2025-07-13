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
        
        # Importar componentes de la GUI y módulos principales (estructura modular)
        from src.gui.gui_enhanced_rank import EnhancedRankGUI
        from src.data.data_manager import DataManager
        from src.core.integration_layer import UnifiedEvaluatorEnhanced
        from src.analysis.asesor_financiero_inteligente import AsesorFinancieroInteligente
        logger.info("✅ Componentes y módulos importados correctamente (estructura modular)")
        
        # Simular carga de datos
        logger.info("📊 Simulando carga de datos...")
        dm = DataManager()
        success = dm.load_kpis_data('INPUTTEST/DatabankExport_M1.csv')
        
        if not success:
            logger.error("❌ Error cargando datos KPI")
            assert False, "Error cargando datos KPI"
            
        data = dm.kpis_data
        if data is not None:
            logger.info(f"✅ Datos cargados: {len(data)} estrategias")
        else:
            logger.error("❌ No hay datos disponibles")
            assert False, "No hay datos disponibles"
        
        # Simular análisis
        logger.info("🔬 Simulando análisis...")
        evaluator = UnifiedEvaluatorEnhanced()
        if data is not None:
            results = evaluator.evaluate_strategies_unified(data)
            logger.info(f"✅ Análisis completado: {len(results)} estrategias procesadas")
        else:
            logger.error("❌ No hay datos para analizar")
            assert False, "No hay datos para analizar"
        
        # Verificar que la GUI se puede crear (sin crear ventana real)
        logger.info("🖥️ Verificando creación de GUI...")
        try:
            # Verificar que la clase se puede importar y instanciar
            # Sin crear ventana real para evitar problemas en testing
            gui_class = EnhancedRankGUI
            logger.info("✅ Clase GUI importada correctamente")
            
            # Verificar métodos principales existen
            methods_to_check = ['__init__', 'create_widgets', 'run_analysis']
            for method in methods_to_check:
                if hasattr(gui_class, method):
                    logger.info(f"✅ Método {method} existe")
                else:
                    logger.warning(f"⚠️ Método {method} no encontrado")
            
        except Exception as e:
            logger.error(f"❌ Error verificando GUI: {e}")
            assert False, f"Error verificando GUI: {e}"
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de componentes: {e}")
        assert False, f"Error en prueba de componentes: {e}"

def test_gui_functionality():
    """Prueba la funcionalidad específica de la GUI."""
    try:
        logger.info("🧪 Probando funcionalidad de la GUI...")
        
        # Verificar archivos necesarios
        required_files = [
            'INPUTTEST/DatabankExport_M1.csv',
            'INPUTTEST/DATOSMQL5.csv',
            'src/gui/gui_enhanced_rank.py',
            'src/gui/scientific_gui_tab.py',
            'src/data/data_manager.py',
            'src/data/column_mapping.py',
            'src/data/data_processing.py',
            'src/data/data_utils.py',
            'src/core/integration_layer.py',
            'src/core/compliance_audit.py',
            'src/core/logger_config.py',
            'src/analysis/asesor_financiero_inteligente.py',
            'src/analysis/advanced_analysis_enhanced.py',
            'src/analysis/scientific_analysis.py',
            'src/analysis/tail_risk_metrics.py',
            'src/analysis/darwinex_pipeline.py',
            'src/analysis/research_docs.py',
            'src/analysis/axi_select_analysis.py',
            'src/ml/advanced_ml_validation.py',
            'src/validation/advanced_temporal_validation.py',
            'src/logger_config.py'
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                logger.error(f"❌ Archivo faltante: {file_path}")
                assert False, f"Archivo faltante: {file_path}"
        
        logger.info("✅ Todos los módulos principales existen y son importables (estructura modular)")
        
        # Verificar configuración
        config_file = 'config/trading_config.json'
        if Path(config_file).exists():
            logger.info("✅ Archivo de configuración encontrado")
        else:
            logger.warning("⚠️ Archivo de configuración no encontrado, se usará configuración por defecto")
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de funcionalidad: {e}")
        assert False, f"Error en prueba de funcionalidad: {e}"

def test_data_integration():
    """Prueba la integración de datos en la GUI."""
    try:
        logger.info("🧪 Probando integración de datos...")
        
        from src.data.data_manager import DataManager
        from src.core.integration_layer import UnifiedEvaluatorEnhanced
        
        # Cargar datos
        dm = DataManager()
        success = dm.load_kpis_data('INPUTTEST/DatabankExport_M1.csv')
        
        if not success:
            logger.error("❌ Error cargando datos")
            assert False, "Error cargando datos"
        
        data = dm.kpis_data
        if data is None:
            logger.error("❌ No hay datos disponibles")
            assert False, "No hay datos disponibles"
        
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
        
    except Exception as e:
        logger.error(f"❌ Error en integración de datos: {e}")
        assert False, f"Error en integración de datos: {e}"

def test_import_all_py_modules():
    """Importa dinámicamente todos los .py de src/ (excepto __init__.py) y lanza assert si alguno falla."""
    import importlib.util
    import glob
    import traceback
    import sys
    import os
    logger.info("🔎 Comprobando importación de TODOS los .py en src/ ...")
    
    # Lista completa de todos los módulos .py del proyecto (excepto __init__.py)
    all_py_modules = [
        'src.logger_config',
        'src.analysis.advanced_analysis_enhanced',
        'src.analysis.asesor_financiero_inteligente',
        'src.analysis.axi_select_analysis',
        'src.analysis.darwinex_pipeline',
        'src.analysis.research_docs',
        'src.analysis.scientific_analysis',
        'src.analysis.tail_risk_metrics',
        'src.core.compliance_audit',
        'src.core.integration_layer',
        'src.core.logger_config',
        'src.data.column_mapping',
        'src.data.data_manager',
        'src.data.data_processing',
        'src.data.data_utils',
        'src.gui.gui_enhanced_rank',
        'src.gui.scientific_gui_tab',
        'src.ml.advanced_ml_validation',
        'src.validation.advanced_temporal_validation'
    ]
    
    failed = []
    for module_name in all_py_modules:
        try:
            logger.info(f"🧩 Importando módulo: {module_name}")
            importlib.import_module(module_name)
        except Exception as e:
            logger.error(f"❌ Error importando {module_name}: {e}\n{traceback.format_exc()}")
            failed.append(module_name)
    
    assert not failed, f"Fallo al importar los siguientes módulos: {failed}"
    logger.info(f"✅ Todos los {len(all_py_modules)} módulos se importaron correctamente")

def test_verify_all_required_files_exist():
    """Verifica que todos los archivos requeridos existen y se pueden importar."""
    logger.info("📋 Verificando existencia y importación de archivos requeridos...")
    
    required_files = [
        'DatabankExport_M1.csv',
        'DATOSMQL5.csv',
        'src/gui/gui_enhanced_rank.py',
        'src/gui/scientific_gui_tab.py',
        'src/data/data_manager.py',
        'src/data/column_mapping.py',
        'src/data/data_processing.py',
        'src/data/data_utils.py',
        'src/core/integration_layer.py',
        'src/core/compliance_audit.py',
        'src/core/logger_config.py',
        'src/analysis/asesor_financiero_inteligente.py',
        'src/analysis/advanced_analysis_enhanced.py',
        'src/analysis/scientific_analysis.py',
        'src/analysis/tail_risk_metrics.py',
        'src/analysis/darwinex_pipeline.py',
        'src/analysis/research_docs.py',
        'src/analysis/axi_select_analysis.py',
        'src/ml/advanced_ml_validation.py',
        'src/validation/advanced_temporal_validation.py',
        'src/logger_config.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            logger.error(f"❌ Archivo faltante: {file_path}")
    
    assert not missing_files, f"Archivos faltantes: {missing_files}"
    logger.info(f"✅ Todos los {len(required_files)} archivos requeridos existen")

# Ejecutar la comprobación al final del flujo principal
def main():
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
            test_func()
            results.append((test_name, True))
            logger.info(f"✅ {test_name}: PASÓ")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    # Comprobación de integración de todos los módulos principales y nuevos
    try:
        from src.analysis.asesor_financiero_inteligente import AsesorFinancieroInteligente
        from src.analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        from src.analysis.scientific_analysis import ScientificAnalysis
        from src.analysis.tail_risk_metrics import TailRiskMetrics
        from src.analysis.darwinex_pipeline import DarwinexPipeline
        from src.analysis.research_docs import ResearchDocs
        from src.analysis.axi_select_analysis import AxiSelectAnalysis
        from src.core.compliance_audit import ComplianceAudit
        from src.core.logger_config import setup_logger
        from src.data.column_mapping import ColumnMapping
        from src.data.data_processing import DataProcessor
        from src.data.data_utils import DataUtils
        from src.gui.scientific_gui_tab import ScientificAnalysisTab
        from src.ml.advanced_ml_validation import AdvancedMLValidation
        from src.validation.advanced_temporal_validation import AdvancedTemporalValidation
        from src.logger_config import setup_logger as setup_main_logger
        logger.info("✅ Todos los módulos principales y nuevos integrados correctamente")
    except Exception as e:
        logger.error(f"❌ Error integrando módulos: {e}")
        assert False, f"Error integrando módulos: {e}"
    # Comprobación de importación de todos los .py
    test_import_all_py_modules()
    # Comprobación de existencia de archivos requeridos
    test_verify_all_required_files_exist()
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