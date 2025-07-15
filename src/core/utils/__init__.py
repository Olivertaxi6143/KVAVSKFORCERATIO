"""
Utils Específicos del Core Engine
=================================

Este módulo proporciona acceso a utilidades específicas del core engine:
- error_handler: Manejo centralizado de errores
- validation_utils: Validación específica del core (NO de datos)

NOTA: Todas las funciones de tratamiento de datos han sido migradas a src/data/
Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

# Imports de error handling
from .error_handler import (
    RobustErrorHandler,
    retry_on_error,
    handle_specific_errors,
    validate_input,
    log_execution_time,
    GUIAnalysisError
)

# Imports de validación específica del core
from .validation_utils import (
    validate_config,
    validate_kpi_config,
    validate_trading_style_config,
    validate_file_path,
    validate_numeric_range,
    validate_percentage,
    validate_probability,
    validate_series_quality,
    validate_correlation_matrix,
    validate_analysis_results
)

# Lista de funciones exportadas (solo core-specific)
__all__ = [
    # Error handling
    'RobustErrorHandler',
    'retry_on_error',
    'handle_specific_errors',
    'validate_input',
    'log_execution_time',
    'GUIAnalysisError',
    
    # Core validation
    'validate_config',
    'validate_kpi_config',
    'validate_trading_style_config',
    'validate_file_path',
    'validate_numeric_range',
    'validate_percentage',
    'validate_probability',
    'validate_series_quality',
    'validate_correlation_matrix',
    'validate_analysis_results'
]
