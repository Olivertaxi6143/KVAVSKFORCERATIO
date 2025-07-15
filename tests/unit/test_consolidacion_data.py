#!/usr/bin/env python3
"""
Test de Consolidación de Datos
==============================

Verifica que todas las funciones de datos estén correctamente consolidadas
en la carpeta data/ y que los imports funcionen correctamente.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

import sys
import os
import pandas as pd
import numpy as np
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports_data_utils():
    """Test de imports desde data_utils.py"""
    try:
        from src.data.data_utils import (
            # Funciones básicas
            safe_float, validate_numeric_column,
            calculate_basic_stats, detect_outliers_iqr,
            
            # Funciones de métricas
            calculate_max_drawdown, calculate_percentile_tail,
            calculate_cumulative_returns, clean_returns,
            
            # Funciones de procesamiento
            safe_sum, safe_values, improve_missing_data_handling,
            clean_extreme_values, normalize_series, calculate_percentiles,
            
            # Funciones de conversión de tipos
            convert_types, safe_int, safe_str, safe_bool,
            convert_series_types, convert_dataframe_types,
            validate_types, infer_numeric_type, normalize_numeric_series,
            ensure_numeric_columns, convert_to_datetime,
            safe_convert_to_numeric, safe_replace_date, safe_str_arg
        )
        from src.gui.utils import validate_dataframe
        logger.info("✅ Todos los imports de data_utils.py funcionan correctamente")
        return True
    except ImportError as e:
        logger.error(f"❌ Error importando desde data_utils.py: {e}")
        return False

def test_imports_visualization():
    """Test de imports desde visualization.py"""
    try:
        from src.data.visualization import (
            create_correlation_heatmap,
            create_distribution_plot,
            create_performance_chart,
            create_comparison_plot
        )
        logger.info("✅ Todos los imports de visualization.py funcionan correctamente")
        return True
    except ImportError as e:
        logger.error(f"❌ Error importando desde visualization.py: {e}")
        return False

def test_imports_data_manager():
    """Test de imports desde data_manager.py"""
    try:
        from src.data.data_manager import (
            DataManager, create_data_manager, 
            load_data_from_config, load_inputtest_data_pipeline
        )
        logger.info("✅ Todos los imports de data_manager.py funcionan correctamente")
        return True
    except ImportError as e:
        logger.error(f"❌ Error importando desde data_manager.py: {e}")
        return False

def test_imports_column_mapping():
    """Test de imports desde column_mapping.py"""
    try:
        from src.data.column_mapping import normalize_column_names
        logger.info("✅ Import de column_mapping.py funciona correctamente")
        return True
    except ImportError as e:
        logger.error(f"❌ Error importando desde column_mapping.py: {e}")
        return False

def test_imports_unified():
    """Test de imports unificados desde data/"""
    try:
        from src.data import (
            # Funciones básicas
            safe_float, validate_numeric_column,
            calculate_basic_stats, detect_outliers_iqr,
            
            # Funciones de métricas
            calculate_max_drawdown, calculate_percentile_tail,
            calculate_cumulative_returns, clean_returns,
            
            # Funciones de procesamiento
            safe_sum, safe_values, improve_missing_data_handling,
            clean_extreme_values, normalize_series, calculate_percentiles,
            
            # Funciones de conversión de tipos
            convert_types, safe_int, safe_str, safe_bool,
            convert_series_types, convert_dataframe_types,
            validate_types, infer_numeric_type, normalize_numeric_series,
            ensure_numeric_columns, convert_to_datetime,
            safe_convert_to_numeric, safe_replace_date, safe_str_arg,
            
            # Funciones de visualización
            create_correlation_heatmap, create_distribution_plot,
            create_performance_chart, create_comparison_plot,
            
            # Funciones de normalización
            normalize_column_names,
            
            # Clases principales
            DataManager, create_data_manager, load_data_from_config,
            load_inputtest_data_pipeline
        )
        from src.gui.utils import validate_dataframe
        logger.info("✅ Todos los imports unificados desde data/ funcionan correctamente")
        return True
    except ImportError as e:
        logger.error(f"❌ Error importando desde data/ unificado: {e}")
        return False

def test_core_utils_imports():
    """Test de imports desde core/utils (solo funciones específicas del core)"""
    try:
        from src.core.utils import (
            # Error handling
            RobustErrorHandler, retry_on_error, handle_specific_errors,
            validate_input, log_execution_time, GUIAnalysisError,
            
            # Core validation
            validate_config, validate_kpi_config, validate_trading_style_config,
            validate_file_path, validate_numeric_range, validate_percentage,
            validate_probability, validate_series_quality, validate_correlation_matrix,
            validate_analysis_results
        )
        logger.info("✅ Todos los imports de core/utils funcionan correctamente")
        return True
    except ImportError as e:
        logger.error(f"❌ Error importando desde core/utils: {e}")
        return False

def test_functionality():
    """Test de funcionalidad básica de las funciones consolidadas"""
    try:
        from src.gui.utils import (
            safe_float, validate_dataframe, normalize_series
        )
        
        # Test safe_float
        assert safe_float("123.45") == 123.45
        assert safe_float("1,234.56") == 1234.56
        assert safe_float("invalid") == 0.0
        
        # Test validate_dataframe
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        is_valid, errors = validate_dataframe(df)
        assert is_valid == True
        assert len(errors) == 0
        
        # Test normalize_series
        series = pd.Series([1, 2, 3, 4, 5])
        normalized = normalize_series(series, method='minmax')
        assert len(normalized) == 5
        assert normalized.min() == 0.0
        assert normalized.max() == 1.0
        
        logger.info("✅ Funcionalidad básica de funciones consolidadas funciona correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error en test de funcionalidad: {e}")
        return False

def test_no_duplicates():
    """Test para verificar que no hay duplicados"""
    try:
        # Verificar que no existen archivos duplicados
        core_utils_files = [
            'src/core/utils/data_utils.py',
            'src/core/utils/type_converters.py',
            'src/core/utils/metrics_calculation.py',
            'src/core/utils/visualization.py'
        ]
        
        for file_path in core_utils_files:
            if os.path.exists(file_path):
                logger.error(f"❌ Archivo duplicado aún existe: {file_path}")
                return False
        
        logger.info("✅ No se encontraron archivos duplicados")
        return True
    except Exception as e:
        logger.error(f"❌ Error verificando duplicados: {e}")
        return False

def main():
    """Función principal de testing"""
    logger.info("🚀 Iniciando tests de consolidación de datos...")
    
    tests = [
        ("Imports data_utils.py", test_imports_data_utils),
        ("Imports visualization.py", test_imports_visualization),
        ("Imports data_manager.py", test_imports_data_manager),
        ("Imports column_mapping.py", test_imports_column_mapping),
        ("Imports unificados data/", test_imports_unified),
        ("Imports core/utils", test_core_utils_imports),
        ("Funcionalidad básica", test_functionality),
        ("Verificación de duplicados", test_no_duplicates)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"🧪 Ejecutando: {test_name}")
        try:
            if test_func():
                logger.info(f"✅ {test_name}: PASÓ")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    logger.info(f"📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        logger.info("🎉 ¡TODOS LOS TESTS PASARON! Consolidación exitosa.")
        return True
    else:
        logger.error("💥 ALGUNOS TESTS FALLARON. Revisar consolidación.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 