import numpy as np
import pandas as pd
from typing import Optional, Any, Union
import warnings
"""
Configuración de logging para el sistema de análisis cuantitativo.
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import traceback

# Constantes de formato y nivel de logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO

class UnicodeSafeStreamHandler(logging.StreamHandler):
    """Handler que maneja caracteres Unicode de forma segura en Windows."""
    
    def emit(self, record):
        try:
            msg = self.format(record)
            # Encode como UTF-8 y luego decode para evitar problemas de encoding
            if hasattr(sys.stdout, 'reconfigure'):
                # Python 3.7+
                try:
                    sys.stdout.reconfigure(encoding='utf-8')
                except:
                    pass
            stream = self.stream
            stream.write(msg)
            stream.write(self.terminator)
            self.flush()
        except UnicodeEncodeError:
            # Fallback: reemplazar caracteres problemáticos
            try:
                safe_msg = msg.encode('ascii', errors='replace').decode('ascii')
                stream = self.stream
                stream.write(safe_msg)
                stream.write(self.terminator)
                self.flush()
            except Exception:
                # Último recurso: solo texto ASCII
                stream = self.stream
                stream.write(f"[{record.levelname}] {record.getMessage()}\n")
                self.flush()
        except Exception:
            self.handleError(record)

def setup_logger(name: str = "kforce", level: int = logging.INFO) -> logging.Logger:
    """
    Configura el sistema de logging.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar configurar múltiples handlers
    if logger.handlers:
        return logger
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola con manejo seguro de Unicode
    console_handler = UnicodeSafeStreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/{name}_{timestamp}.log"
    
    # Crear directorio de logs si no existe
    Path("logs").mkdir(exist_ok=True)
    
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback si hay problemas con el archivo
        print(f"Warning: No se pudo crear archivo de log: {e}")
    
    # Configurar nivel
    logger.setLevel(level)
    
    return logger

def log_error_with_context(error: Exception, context: str = "", logger: Optional[logging.Logger] = None) -> None:
    """
    Registra un error con contexto adicional.
    
    Args:
        error: Excepción capturada
        context: Contexto adicional del error
        logger: Logger a usar (opcional)
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    error_msg = f"Error en {context}: {str(error)}" if context else f"Error: {str(error)}"
    logger.error(error_msg)
    logger.error(f"Traceback: {traceback.format_exc()}")

def safe_print(message: str, use_unicode: bool = True) -> None:
    """
    Función segura para imprimir mensajes con caracteres Unicode.
    
    Args:
        message: Mensaje a imprimir
        use_unicode: Si usar caracteres Unicode o ASCII
    """
    try:
        if use_unicode:
            print(message) if message is not None else 0 if message is not None else 0
        else:
            # Versión ASCII segura
            safe_message = message.encode('ascii', errors='replace').decode('ascii')
            print(safe_message) if safe_message is not None else 0 if safe_message is not None else 0
    except UnicodeEncodeError:
        # Fallback completo a ASCII
        safe_message = message.encode('ascii', errors='replace').decode('ascii')
        print(safe_message) if safe_message is not None else 0 if safe_message is not None else 0
    except Exception:
        # Último recurso
        print(f"[INFO] {message}")

# Configuración global para evitar problemas de encoding
def configure_system_encoding():
    """Configura el encoding del sistema para evitar problemas."""
    try:
        # Forzar UTF-8 en Windows
        if os.name == 'nt':
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Configurar encoding al importar el módulo
configure_system_encoding()

def log_performance(operation: str, start_time: float, logger: Optional[logging.Logger] = None) -> None:
    """
    Registra métricas de rendimiento.
    
    Args:
        operation: Nombre de la operación
        start_time: Tiempo de inicio
        logger: Logger a usar (opcional)
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    import time
    execution_time = time.time() - start_time
    logger.info(f"⏱️ {operation} completado en {execution_time:.2f} segundos")

def log_performance_metrics(metrics: dict, logger: Optional[logging.Logger] = None) -> None:
    """
    Registra métricas de rendimiento detalladas.
    
    Args:
        metrics: Diccionario con métricas
        logger: Logger a usar (opcional)
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    logger.info("📊 Métricas de rendimiento:")
    for key, value in metrics.items():
        logger.info(f"  - {key}: {value}")

def get_logger(name: str = "kforce") -> logging.Logger:
    """Devuelve un logger por nombre."""
    return logging.getLogger(name) 