"""
Módulo de Utilidades Compartidas para Análisis
==============================================

Contiene funciones y utilidades compartidas entre los diferentes
módulos de análisis para evitar duplicación de código.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

from src.gui.utils import (
    validate_dataframe,
    validate_numeric_column,
    clean_numeric_data,
    normalize_series,
    calculate_percentiles,
    safe_float,
    safe_int,
    safe_str,
    safe_bool,
    convert_types,
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

from .visualization import (
    create_correlation_heatmap,
    create_distribution_plot,
    create_performance_chart,
    create_comparison_plot
)

from .validation import (
    validate_analysis_input,
    check_data_quality,
    validate_metrics_range,
    ensure_positive_values
)

from .metrics_calculation import (
    calculate_max_drawdown,
    calculate_percentile_tail,
    calculate_cumulative_returns,
    clean_returns
)

__all__ = [
    # Data processing
    'clean_numeric_data',
    'validate_dataframe', 
    'extract_numeric_columns',
    'handle_missing_values',
    'normalize_metrics',
    
    # Visualization
    'create_correlation_heatmap',
    'create_distribution_plot',
    'create_performance_chart',
    'create_comparison_plot',
    
    # Validation
    'validate_analysis_input',
    'check_data_quality',
    'validate_metrics_range',
    'ensure_positive_values',
    
    # Metrics calculation
    'calculate_max_drawdown',
    'calculate_percentile_tail',
    'calculate_cumulative_returns',
    'clean_returns'
] 