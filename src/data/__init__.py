"""
Módulo de Datos Unificado
=========================

Este módulo centraliza todo el tratamiento de datos del sistema:
- data_manager.py: Gestión centralizada de datos
- data_utils.py: Utilidades unificadas de procesamiento
- column_mapping.py: Normalización única de columnas
- visualization.py: Visualización de datos

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

# Imports principales desde data_utils.py
from .data_utils import (
    # Funciones básicas
    NORMALIZE_COL,
    read_and_prepare,
    extract_float_from_tuple,
    safe_float,
    calculate_basic_stats,
    detect_outliers_iqr,
    
    # Funciones de métricas
    calculate_max_drawdown,
    calculate_percentile_tail,
    calculate_cumulative_returns,
    clean_returns,
    
    # Funciones de procesamiento
    safe_sum,
    safe_values,
    improve_missing_data_handling,
    clean_extreme_values,
    normalize_series,
    calculate_percentiles,
    
    # Funciones de conversión de tipos
    convert_types,
    safe_int,
    safe_str,
    safe_bool,
    convert_series_types,
    convert_dataframe_types,
    validate_types,
    infer_numeric_type,
    normalize_numeric_series,
    ensure_numeric_columns,
    convert_to_datetime,
    safe_convert_to_numeric,
    safe_replace_date,
    safe_str_arg
)

# Imports desde visualization.py
from .visualization import (
    create_correlation_heatmap,
    create_distribution_plot,
    create_performance_chart,
    create_comparison_plot
)

# Imports desde column_mapping.py
from .column_mapping import normalize_column_names

# Imports desde data_manager.py
from .data_manager import DataManager, create_data_manager, load_data_from_config, load_inputtest_data_pipeline

# Lista de todas las funciones exportadas
__all__ = [
    # Funciones básicas
    'NORMALIZE_COL',
    'read_and_prepare',
    'extract_float_from_tuple',
    'safe_float',
    'calculate_basic_stats',
    'detect_outliers_iqr',
    
    # Funciones de métricas
    'calculate_max_drawdown',
    'calculate_percentile_tail',
    'calculate_cumulative_returns',
    'clean_returns',
    
    # Funciones de procesamiento
    'safe_sum',
    'safe_values',
    'improve_missing_data_handling',
    'clean_extreme_values',
    'normalize_series',
    'calculate_percentiles',
    
    # Funciones de conversión de tipos
    'convert_types',
    'safe_int',
    'safe_str',
    'safe_bool',
    'convert_series_types',
    'convert_dataframe_types',
    'validate_types',
    'infer_numeric_type',
    'normalize_numeric_series',
    'ensure_numeric_columns',
    'convert_to_datetime',
    'safe_convert_to_numeric',
    'safe_replace_date',
    'safe_str_arg',
    
    # Funciones de visualización
    'create_correlation_heatmap',
    'create_distribution_plot',
    'create_performance_chart',
    'create_comparison_plot',
    
    # Funciones de normalización
    'normalize_column_names',
    
    # Clases principales
    'DataManager',
    'create_data_manager',
    'load_data_from_config',
    'load_inputtest_data_pipeline'
] 