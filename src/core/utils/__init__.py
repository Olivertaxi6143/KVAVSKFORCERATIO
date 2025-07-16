"""
Módulo de Utilidades del Core
=============================

Utilidades centrales para el sistema de análisis cuantitativo:
- memory_optimizer.py: Optimización de memoria para datasets grandes
- parallel_trainer.py: Paralelización de entrenamiento de modelos
- intelligent_cache.py: Cache inteligente para resultados
- error_handler.py: Manejo centralizado de errores
- validation_utils.py: Utilidades de validación

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-15
"""

# Imports desde memory_optimizer.py
from .memory_optimizer import (
    MemoryOptimizer,
    MemoryConfig,
    optimize_large_dataset,
    get_memory_usage,
    get_optimization_stats
)

# Imports desde parallel_trainer.py
from .parallel_trainer import (
    ParallelTrainer,
    ParallelConfig,
    train_models_parallel,
    get_training_stats,
    monitor_training_progress
)

# Imports desde intelligent_cache.py
from .intelligent_cache import (
    IntelligentCache,
    CacheConfig,
    cache_result,
    get_cached_result,
    get_cache_stats,
    clear_cache
)

# Imports desde error_handler.py
from .error_handler import (
    RobustErrorHandler,
    retry_on_error,
    handle_specific_errors,
    validate_input,
    log_execution_time
)

# Imports desde validation_utils.py
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

# Lista de todas las funciones exportadas
__all__ = [
    # Memory Optimizer
    'MemoryOptimizer',
    'MemoryConfig',
    'optimize_large_dataset',
    'get_memory_usage',
    'get_optimization_stats',
    
    # Parallel Trainer
    'ParallelTrainer',
    'ParallelConfig',
    'train_models_parallel',
    'get_training_stats',
    'monitor_training_progress',
    
    # Intelligent Cache
    'IntelligentCache',
    'CacheConfig',
    'cache_result',
    'get_cached_result',
    'get_cache_stats',
    'clear_cache',
    
    # Error Handler
    'RobustErrorHandler',
    'retry_on_error',
    'handle_specific_errors',
    'validate_input',
    'log_execution_time',
    
    # Validation Utils
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
