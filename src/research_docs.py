"""
Funciones básicas de utilidad para investigación y validación.
Módulo simplificado con solo las funciones esenciales.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List
from scipy import stats

logger = logging.getLogger(__name__)

def _to_float(val: Any) -> float:
    """Convierte un valor a float de forma segura."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def extract_float_from_tuple(data: Any, index: int = 0, default: float = 0.0) -> float:
    """
    Extrae un valor numérico de una tupla de forma segura.
    
    Args:
        data: Tupla que contiene el valor.
        index: Índice del valor a extraer.
        default: Valor por defecto si la tupla es inválida.
    
    Returns:
        float: Valor numérico extraído.
    """
    if isinstance(data, tuple) and len(data) > index:
        try:
            return float(data[index])
        except (ValueError, TypeError):
            return default
    elif isinstance(data, (int, float)):
        return float(data)
    return default

def validate_numeric_column(df: pd.DataFrame, column: str) -> bool:
    """
    Valida si una columna es numérica y contiene datos válidos.
    
    Args:
        df: DataFrame a validar
        column: Nombre de la columna
        
    Returns:
        True si la columna es válida, False en caso contrario
    """
    try:
        if column not in df.columns:
            return False
        # Convertir a numérico
        df[column] = pd.to_numeric(df[column], errors='coerce')
        # Verificar que no sea todo NaN
        is_all_nan = bool(df[column].isna().all())
        if is_all_nan:
            return False
        return True
    except Exception as e:
        logger.warning(f"Error validando columna {column}: {e}")
        return False

def calculate_basic_stats(df: pd.DataFrame, column: str) -> Dict[str, float]:
    """
    Calcula estadísticas básicas de una columna.
    
    Args:
        df: DataFrame
        column: Nombre de la columna
        
    Returns:
        Diccionario con estadísticas básicas
    """
    try:
        if not validate_numeric_column(df, column):
            return {}
        stats_dict = {
            'mean': df[column].mean(),
            'std': df[column].std(),
            'min': df[column].min(),
            'max': df[column].max(),
            'median': df[column].median(),
            'count': df[column].count()
        }
        return stats_dict
    except Exception as e:
        logger.error(f"Error calculando estadísticas de {column}: {e}")
        return {}

def detect_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 1.5) -> Dict[str, Any]:
    """
    Detecta outliers usando el método IQR.
    
    Args:
        df: DataFrame
        column: Nombre de la columna
        factor: Factor para el cálculo de outliers
        
    Returns:
        Diccionario con información de outliers
    """
    try:
        if not validate_numeric_column(df, column):
            return {'outliers': [], 'count': 0, 'percentage': 0.0}
            
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR
        
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
            
        return {
            'outliers': outliers[column].tolist(),
            'count': len(outliers),
            'percentage': len(outliers) / len(df) * 100,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }
        
    except Exception as e:
        logger.error(f"Error detectando outliers en {column}: {e}")
        return {'outliers': [], 'count': 0, 'percentage': 0.0} 