"""
Utilidades de validación para el core engine.

Este módulo contiene funciones para validar datos y configuración.
NOTA: Las funciones básicas de validación se han centralizado en src/gui/utils.py
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Funciones de validación básicas eliminadas - usar src/gui/utils.py en su lugar
# from src.gui.utils import validate_dataframe, validate_numeric_column

# ===================== FUNCIONES ESPECÍFICAS DEL CORE (NO DUPLICADAS) =====================

def validate_config(config: Dict[str, Any], required_keys: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
    """
    Valida una configuración.
    
    Args:
        config: Configuración a validar
        required_keys: Claves requeridas en la configuración
        
    Returns:
        tuple: (es_válido, lista_de_errores)
    """
    errors = []
    
    if not isinstance(config, dict):
        errors.append("Configuración debe ser un diccionario")
        return False, errors
    
    # Verificar claves requeridas
    if required_keys is not None:
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            errors.append(f"Claves faltantes en configuración: {missing_keys}")
    
    # Validar tipos de valores
    for key, value in config.items():
        if key.endswith('_enabled') and not isinstance(value, bool):
            errors.append(f"'{key}' debe ser un booleano")
        elif key.endswith('_weight') and not isinstance(value, (int, float)):
            errors.append(f"'{key}' debe ser numérico")
        elif key.endswith('_threshold') and not isinstance(value, (int, float)):
            errors.append(f"'{key}' debe ser numérico")
    
    return len(errors) == 0, errors


def validate_kpi_config(kpi_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida configuración específica de KPIs.
    
    Args:
        kpi_config: Configuración de KPIs
        
    Returns:
        tuple: (es_válido, lista_de_errores)
    """
    errors = []
    
    if not isinstance(kpi_config, dict):
        errors.append("Configuración de KPIs debe ser un diccionario")
        return False, errors
    
    for kpi_name, kpi_data in kpi_config.items():
        if not isinstance(kpi_data, dict):
            errors.append(f"Configuración de KPI '{kpi_name}' debe ser un diccionario")
            continue
        
        # Verificar campos requeridos
        required_fields = ['enabled', 'weight']
        for field in required_fields:
            if field not in kpi_data:
                errors.append(f"KPI '{kpi_name}' falta campo '{field}'")
        
        # Validar tipos
        if 'enabled' in kpi_data and not isinstance(kpi_data['enabled'], bool):
            errors.append(f"KPI '{kpi_name}' campo 'enabled' debe ser booleano")
        
        if 'weight' in kpi_data and not isinstance(kpi_data['weight'], (int, float)):
            errors.append(f"KPI '{kpi_name}' campo 'weight' debe ser numérico")
        
        if 'weight' in kpi_data and kpi_data['weight'] < 0:
            errors.append(f"KPI '{kpi_name}' peso no puede ser negativo")
    
    return len(errors) == 0, errors


def validate_trading_style_config(style_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida configuración de estilos de trading.
    
    Args:
        style_config: Configuración de estilos
        
    Returns:
        tuple: (es_válido, lista_de_errores)
    """
    errors = []
    
    if not isinstance(style_config, dict):
        errors.append("Configuración de estilos debe ser un diccionario")
        return False, errors
    
    for style_name, style_data in style_config.items():
        if not isinstance(style_data, dict):
            errors.append(f"Configuración de estilo '{style_name}' debe ser un diccionario")
            continue
        
        # Verificar campos requeridos
        required_fields = ['description', 'kpi_weights', 'component_weights']
        for field in required_fields:
            if field not in style_data:
                errors.append(f"Estilo '{style_name}' falta campo '{field}'")
        
        # Validar pesos de componentes
        if 'component_weights' in style_data:
            weights = style_data['component_weights']
            if not isinstance(weights, dict):
                errors.append(f"Estilo '{style_name}' component_weights debe ser diccionario")
            else:
                total_weight = sum(weights.values())
                if abs(total_weight - 1.0) > 0.1:
                    errors.append(f"Estilo '{style_name}' pesos de componentes deben sumar ~1.0 (actual: {total_weight})")
    
    return len(errors) == 0, errors


def validate_file_path(file_path: str, file_type: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    Valida que un archivo exista y sea del tipo correcto.
    
    Args:
        file_path: Ruta del archivo
        file_type: Tipo de archivo esperado (opcional)
        
    Returns:
        tuple: (es_válido, lista_de_errores)
    """
    errors = []
    
    path = Path(file_path)
    
    if not path.exists():
        errors.append(f"Archivo no existe: {file_path}")
        return False, errors
    
    if not path.is_file():
        errors.append(f"Ruta no es un archivo: {file_path}")
        return False, errors
    
    # Verificar extensión si se especifica
    if file_type is not None:
        if not path.suffix.lower() == f".{file_type.lower()}":
            errors.append(f"Archivo debe tener extensión .{file_type}")
    
    return len(errors) == 0, errors


def validate_numeric_range(value: float, min_val: Optional[float] = None, max_val: Optional[float] = None, 
                          name: str = "valor") -> Tuple[bool, List[str]]:
    """
    Valida que un valor numérico esté en el rango especificado.
    
    Args:
        value: Valor a validar
        min_val: Valor mínimo (opcional)
        max_val: Valor máximo (opcional)
        name: Nombre del valor para mensajes de error
        
    Returns:
        tuple: (es_válido, lista_de_errores)
    """
    errors = []
    
    if not isinstance(value, (int, float)):
        errors.append(f"{name} debe ser numérico")
        return False, errors
    
    if min_val is not None and value < min_val:
        errors.append(f"{name} debe ser >= {min_val}")
    
    if max_val is not None and value > max_val:
        errors.append(f"{name} debe ser <= {max_val}")
    
    return len(errors) == 0, errors


def validate_percentage(value: float, name: str = "porcentaje") -> Tuple[bool, List[str]]:
    """
    Valida que un valor sea un porcentaje válido (0-100).
    
    Args:
        value: Valor a validar
        name: Nombre del valor para mensajes de error
        
    Returns:
        tuple: (es_válido, lista_de_errores)
    """
    return validate_numeric_range(value, 0.0, 100.0, name)


def validate_probability(value: float, name: str = "probabilidad") -> Tuple[bool, List[str]]:
    """
    Valida que un valor sea una probabilidad válida (0-1).
    
    Args:
        value: Valor a validar
        name: Nombre del valor para mensajes de error
        
    Returns:
        tuple: (es_válido, lista_de_errores)
    """
    return validate_numeric_range(value, 0.0, 1.0, name)


def validate_series_quality(series: pd.Series, min_non_null: float = 0.5) -> Tuple[bool, List[str]]:
    """
    Valida la calidad de una serie de datos.
    
    Args:
        series: Serie a validar
        min_non_null: Proporción mínima de valores no nulos
        
    Returns:
        tuple: (es_válido, lista_de_errores)
    """
    errors = []
    
    if series.empty:
        errors.append("Serie está vacía")
        return False, errors
    
    # Verificar proporción de valores no nulos
    non_null_ratio = series.notna().mean()
    if non_null_ratio < min_non_null:
        errors.append(f"Proporción de valores no nulos ({non_null_ratio:.2%}) es menor al mínimo ({min_non_null:.2%})")
    
    # Verificar valores infinitos
    if np.isinf(series).any():
        errors.append("Serie contiene valores infinitos")
    
    # Verificar valores extremos (outliers)
    if series.dtype in ['float64', 'int64']:
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        outliers = series[(series < Q1 - 1.5 * IQR) | (series > Q3 + 1.5 * IQR)]
        if len(outliers) > len(series) * 0.1:  # Más del 10% son outliers
            errors.append(f"Serie contiene muchos outliers ({len(outliers)} de {len(series)})")
    
    return len(errors) == 0, errors


def validate_correlation_matrix(corr_matrix: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Valida una matriz de correlación.
    
    Args:
        corr_matrix: Matriz de correlación a validar
        
    Returns:
        tuple: (es_válido, lista_de_errores)
    """
    errors = []
    
    if corr_matrix.empty:
        errors.append("Matriz de correlación está vacía")
        return False, errors
    
    # Verificar que sea cuadrada
    if corr_matrix.shape[0] != corr_matrix.shape[1]:
        errors.append("Matriz de correlación debe ser cuadrada")
    
    # Verificar que los valores estén en [-1, 1]
    if (corr_matrix < -1).any().any() or (corr_matrix > 1).any().any():
        errors.append("Valores de correlación deben estar en [-1, 1]")
    
    # Verificar diagonal
    diagonal = np.diag(corr_matrix.values)
    if not np.allclose(diagonal, 1.0):
        errors.append("Diagonal de matriz de correlación debe ser 1")
    
    # Verificar simetría
    if not np.allclose(corr_matrix.values, corr_matrix.values.T):
        errors.append("Matriz de correlación debe ser simétrica")
    
    return len(errors) == 0, errors


def validate_analysis_results(results: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida resultados de análisis.
    
    Args:
        results: Resultados a validar
        
    Returns:
        tuple: (es_válido, lista_de_errores)
    """
    errors = []
    
    if not isinstance(results, dict):
        errors.append("Resultados deben ser un diccionario")
        return False, errors
    
    # Verificar campos requeridos
    required_fields = ['status', 'data']
    for field in required_fields:
        if field not in results:
            errors.append(f"Campo requerido '{field}' no encontrado en resultados")
    
    # Validar status
    if 'status' in results and results['status'] not in ['success', 'error', 'warning']:
        errors.append("Status debe ser 'success', 'error' o 'warning'")
    
    # Validar timestamp si existe
    if 'timestamp' in results:
        try:
            from datetime import datetime
            datetime.fromisoformat(results['timestamp'])
        except (ValueError, TypeError):
            errors.append("Timestamp debe ser una fecha ISO válida")
    
    return len(errors) == 0, errors 