"""
Manejador robusto de errores para el core engine.

Este módulo contiene la clase RobustErrorHandler que proporciona:
- Reintentos automáticos con estrategias de recuperación
- Logging detallado de errores
- Estadísticas de errores
"""

import logging
import time
from typing import Dict, Any, Callable, Optional
from collections import defaultdict
from functools import wraps

# Configuración de robustez
MAX_RETRIES = 3  # Máximo número de reintentos
TIMEOUT_SECONDS = 300  # Timeout por operación (5 minutos)
ERROR_RECOVERY_ENABLED = True  # Habilitar recuperación automática de errores

# Configurar logging
logger = logging.getLogger(__name__)


class RobustErrorHandler:
    """
    Manejador robusto de errores con recuperación automática.
    
    Proporciona:
    - Reintentos automáticos con backoff exponencial
    - Estrategias de recuperación personalizables
    - Logging detallado de errores
    - Estadísticas de errores
    """
    
    def __init__(self, max_retries: int = MAX_RETRIES, timeout: int = TIMEOUT_SECONDS):
        """
        Inicializa el manejador de errores.
        
        Args:
            max_retries: Número máximo de reintentos
            timeout: Timeout en segundos por operación
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.logger = logging.getLogger("kforce")
        self.error_counts = defaultdict(int)
        self.recovery_strategies = {}
        
    def register_recovery_strategy(self, error_type: str, strategy_func: Callable):
        """
        Registra una estrategia de recuperación para un tipo de error.
        
        Args:
            error_type: Tipo de error (ej: 'ValueError', 'ConnectionError')
            strategy_func: Función de recuperación
        """
        self.recovery_strategies[error_type] = strategy_func
        
    def execute_with_retry(self, func: Callable, *args, **kwargs):
        """
        Ejecuta una función con reintentos automáticos.
        
        Args:
            func: Función a ejecutar
            *args: Argumentos posicionales
            **kwargs: Argumentos de palabra clave
            
        Returns:
            Resultado de la función
            
        Raises:
            Exception: Si todos los reintentos fallan
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                self.error_counts[error_type] += 1
                
                self.logger.warning(f"Intento {attempt + 1}/{self.max_retries} falló: {error_type}: {e}")
                
                # Intentar estrategia de recuperación si existe
                if error_type in self.recovery_strategies:
                    try:
                        self.recovery_strategies[error_type](e, *args, **kwargs)
                        self.logger.info(f"Estrategia de recuperación aplicada para {error_type}")
                    except Exception as recovery_error:
                        self.logger.error(f"Estrategia de recuperación falló: {recovery_error}")
                
                # Backoff exponencial (esperar antes del siguiente intento)
                if attempt < self.max_retries - 1:
                    wait_time = min(2 ** attempt, 60)  # Máximo 60 segundos
                    self.logger.info(f"Esperando {wait_time} segundos antes del siguiente intento...")
                    time.sleep(wait_time)
        
        # Si llegamos aquí, todos los intentos fallaron
        self.logger.error(f"Todos los {self.max_retries} intentos fallaron. Último error: {last_error}")
        if last_error is not None:
            raise last_error
        else:
            raise RuntimeError("Todos los reintentos fallaron sin capturar un error específico")
        
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de errores.
        
        Returns:
            Diccionario con estadísticas de errores
        """
        total_errors = sum(self.error_counts.values())
        return {
            'total_errors': total_errors,
            'error_counts': dict(self.error_counts),
            'recovery_strategies': list(self.recovery_strategies.keys()),
            'max_retries': self.max_retries,
            'timeout': self.timeout
        }
        
    def reset_error_counts(self):
        """Reinicia los contadores de errores."""
        self.error_counts.clear()
        self.logger.info("Contadores de errores reiniciados")


def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorador para reintentos automáticos.
    
    Args:
        max_retries: Número máximo de reintentos
        delay: Tiempo de espera inicial en segundos
        backoff: Factor de multiplicación para el tiempo de espera
        
    Returns:
        Decorador que aplica reintentos automáticos
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Intento {attempt + 1}/{max_retries} falló para {func.__name__}: {e}")
                    
                    if attempt < max_retries - 1:
                        wait_time = delay * (backoff ** attempt)
                        logger.info(f"Esperando {wait_time} segundos antes del siguiente intento...")
                        time.sleep(wait_time)
            
            # Si llegamos aquí, todos los intentos fallaron
            logger.error(f"Todos los {max_retries} intentos fallaron para {func.__name__}")
            if last_exception is not None:
                raise last_exception
            else:
                raise RuntimeError(f"Todos los reintentos fallaron para {func.__name__} sin capturar un error específico")
            
        return wrapper
    return decorator


def handle_specific_errors(error_types: list, default_value: Any = None):
    """
    Decorador para manejar errores específicos con valores por defecto.
    
    Args:
        error_types: Lista de tipos de error a capturar
        default_value: Valor por defecto si ocurre un error
        
    Returns:
        Decorador que maneja errores específicos
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except tuple(error_types) as e:
                logger.warning(f"Error capturado en {func.__name__}: {e}. Usando valor por defecto.")
                return default_value
        return wrapper
    return decorator


def validate_input(func: Callable):
    """
    Decorador para validación de entrada.
    
    Args:
        func: Función a decorar
        
    Returns:
        Decorador que valida la entrada
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Validar que los argumentos no sean None
        for i, arg in enumerate(args):
            if arg is None:
                raise ValueError(f"Argumento {i} no puede ser None")
        
        # Validar que los kwargs no sean None
        for key, value in kwargs.items():
            if value is None:
                raise ValueError(f"Argumento '{key}' no puede ser None")
        
        return func(*args, **kwargs)
    return wrapper


def log_execution_time(func: Callable):
    """
    Decorador para logging del tiempo de ejecución.
    
    Args:
        func: Función a decorar
        
    Returns:
        Decorador que registra el tiempo de ejecución
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} ejecutado en {execution_time:.2f} segundos")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} falló después de {execution_time:.2f} segundos: {e}")
            raise
    return wrapper


# Clase GUIAnalysisError eliminada - usar src/gui/utils.py en su lugar
# from src.gui.utils import GUIAnalysisError 