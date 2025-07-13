"""
Conversores de tipos para el core engine.

Este módulo contiene funciones para conversión segura de tipos de datos.
"""

import pandas as pd
import numpy as np
from typing import Any, Union, List, Dict, Optional, Literal
import logging

logger = logging.getLogger(__name__)


def convert_types(data: Any, target_type: str) -> Any:
    """
    Convierte datos a un tipo específico de forma segura.
    
    Args:
        data: Datos a convertir
        target_type: Tipo objetivo ('float', 'int', 'str', 'bool')
        
    Returns:
        Datos convertidos al tipo especificado
    """
    try:
        if target_type == 'float':
            return safe_float(data)
        elif target_type == 'int':
            return safe_int(data)
        elif target_type == 'str':
            return safe_str(data)
        elif target_type == 'bool':
            return safe_bool(data)
        else:
            logger.warning(f"Tipo de conversión '{target_type}' no soportado")
            return data
    except Exception as e:
        logger.error(f"Error convirtiendo {type(data)} a {target_type}: {e}")
        return data


def safe_float(val: Any) -> float:
    """
    Conversión segura a float.
    Soporta formatos con coma o punto decimal y separador de miles, incluyendo casos ambiguos y entradas con solo números.
    """
    try:
        if isinstance(val, str):
            val = val.replace(' ', '')
            # Si tiene tanto punto como coma, decidir por la posición
            if ',' in val and '.' in val:
                if val.rfind(',') > val.rfind('.'):
                    # 1.234,56 -> 1234.56
                    val = val.replace('.', '').replace(',', '.')
                else:
                    # 1,234.56 -> 1234.56
                    val = val.replace(',', '')
            elif val.count(',') > 1:
                # 1,234,567 -> 1234567
                val = val.replace(',', '')
            elif val.count('.') > 1:
                # 1.234.567 -> 1234567
                val = val.replace('.', '')
            elif ',' in val:
                # 1234,56 -> 1234.56
                val = val.replace(',', '.')
            # Si solo tiene punto, ya es formato estándar
            # Si solo tiene dígitos
            if val.replace('.', '').isdigit():
                return float(val)
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def safe_int(val: Any) -> int:
    """
    Conversión segura a int.
    
    Args:
        val: Valor a convertir
        
    Returns:
        int: Valor convertido o 0 si falla
    """
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def safe_str(val: Any) -> str:
    """
    Conversión segura a string.
    
    Args:
        val: Valor a convertir
        
    Returns:
        str: Valor convertido o string vacío si falla
    """
    try:
        return str(val)
    except Exception:
        return ""


def safe_bool(val: Any) -> bool:
    """
    Conversión segura a boolean.
    
    Args:
        val: Valor a convertir
        
    Returns:
        bool: Valor convertido
    """
    if isinstance(val, bool):
        return val
    elif isinstance(val, (int, float)):
        return bool(val)
    elif isinstance(val, str):
        return val.lower() in ('true', '1', 'yes', 'on')
    else:
        return False


def convert_series_types(series: pd.Series, target_type: str) -> pd.Series:
    """
    Convierte tipos de una serie de pandas.
    
    Args:
        series: Serie a convertir
        target_type: Tipo objetivo
        
    Returns:
        Serie con tipos convertidos
    """
    if not isinstance(series, pd.Series):
        if isinstance(series, pd.DataFrame):
            # Selecciona la primera columna si es DataFrame
            series = series.iloc[:, 0]
        else:
            raise TypeError("convert_series_types espera una pd.Series")
    try:
        if target_type == 'float':
            return series.astype(float)
        elif target_type == 'int':
            return series.astype(int)
        elif target_type == 'str':
            return series.astype(str)
        elif target_type == 'bool':
            return series.astype(bool)
        else:
            logger.warning(f"Tipo de conversión '{target_type}' no soportado para Series")
            return series
    except Exception as e:
        logger.error(f"Error convirtiendo Series a {target_type}: {e}")
        return series


def convert_dataframe_types(df: pd.DataFrame, type_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Convierte tipos de columnas específicas en un DataFrame.
    
    Args:
        df: DataFrame a convertir
        type_mapping: Mapeo de columnas a tipos {'columna': 'tipo'}
        
    Returns:
        DataFrame con tipos convertidos
    """
    df_converted = df.copy()
    
    for column, target_type in type_mapping.items():
        if column in df_converted.columns:
            try:
                column_data = df_converted[column]
                if isinstance(column_data, pd.Series):
                    df_converted[column] = convert_series_types(column_data, target_type)
                else:
                    logger.warning(f"Columna '{column}' no es una Series válida")
            except Exception as e:
                logger.error(f"Error convirtiendo columna '{column}' a {target_type}: {e}")
    
    return df_converted


def validate_types(data: Any, expected_type: type) -> bool:
    """
    Valida que los datos sean del tipo esperado.
    
    Args:
        data: Datos a validar
        expected_type: Tipo esperado
        
    Returns:
        bool: True si los datos son del tipo esperado
    """
    try:
        if isinstance(data, expected_type):
            return True
        elif expected_type == float and isinstance(data, (int, str)):
            float(data)  # Probar conversión
            return True
        elif expected_type == int and isinstance(data, (float, str)):
            int(float(data))  # Probar conversión
            return True
        else:
            return False
    except (ValueError, TypeError):
        return False


def infer_numeric_type(series: pd.Series) -> str:
    """
    Infiere el tipo numérico más apropiado para una serie.
    
    Args:
        series: Serie a analizar
        
    Returns:
        str: Tipo inferido ('int', 'float', 'mixed')
    """
    try:
        # Intentar convertir a int
        int_series = series.astype(int)
        if (int_series == series).all():
            return 'int'
        else:
            return 'float'
    except (ValueError, TypeError):
        return 'mixed'


def normalize_numeric_series(series: pd.Series) -> pd.Series:
    """
    Normaliza una serie numérica para análisis.
    
    Args:
        series: Serie a normalizar
        
    Returns:
        Serie normalizada
    """
    if not isinstance(series, pd.Series):
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]
        else:
            raise TypeError("normalize_numeric_series espera una pd.Series")
    try:
        numeric_series = pd.to_numeric(series, errors='coerce')
        
        # Reemplazar infinitos con NaN de forma segura
        numeric_series = numeric_series.replace([np.inf, -np.inf], np.nan)  # type: ignore
        
        # Asegurar que el resultado sea una Series
        if not isinstance(numeric_series, pd.Series):
            numeric_series = pd.Series(numeric_series, index=series.index)
        
        return numeric_series
    except Exception as e:
        logger.error(f"Error normalizando serie: {e}")
        return pd.Series([np.nan]*len(series), index=series.index)


def ensure_numeric_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Asegura que las columnas especificadas sean numéricas (float).
    
    Args:
        df: DataFrame a procesar
        columns: Lista de columnas a convertir
        
    Returns:
        DataFrame con columnas numéricas (float)
    """
    df_processed = df.copy()
    
    for column in columns:
        if column in df_processed.columns:
            try:
                column_data = df_processed[column]
                if isinstance(column_data, pd.Series):
                    # Forzar conversión a float SIEMPRE
                    df_processed[column] = pd.to_numeric(column_data, errors='coerce').astype(float)
                else:
                    logger.warning(f"Columna '{column}' no es una Series válida")
            except Exception as e:
                logger.error(f"Error procesando columna '{column}': {e}")
    
    return df_processed


def convert_to_datetime(series: pd.Series, format: Optional[str] = None) -> pd.Series:
    """
    Convierte una serie a datetime de forma segura.
    
    Args:
        series: Serie a convertir
        format: Formato de fecha (opcional)
        
    Returns:
        Serie convertida a datetime
    """
    if not isinstance(series, pd.Series):
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]
        else:
            raise TypeError("convert_to_datetime espera una pd.Series")
    if format is not None:
        fmt = safe_str_arg(format)
        result = pd.to_datetime(series, format=fmt, errors='coerce')
    else:
        result = pd.to_datetime(series, errors='coerce')
    if not isinstance(result, pd.Series):
        result = pd.Series(result, index=series.index)
    return result


def safe_convert_to_numeric(series: pd.Series, downcast: Optional[str] = None) -> pd.Series:
    """
    Conversión segura a numérico con downcasting opcional.
    
    Args:
        series: Serie a convertir
        downcast: Tipo de downcast ('integer', 'signed', 'unsigned', 'float')
        
    Returns:
        Serie convertida a numérico
    """
    if not isinstance(series, pd.Series):
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]
        else:
            raise TypeError("safe_convert_to_numeric espera una pd.Series")
    
    valid_downcast = {'integer', 'signed', 'unsigned', 'float'}
    
    if downcast is not None and downcast in valid_downcast:
        result = pd.to_numeric(series, errors='coerce', downcast=downcast)  # type: ignore
    else:
        result = pd.to_numeric(series, errors='coerce')
    
    if not isinstance(result, pd.Series):
        result = pd.Series(result, index=series.index)
    
    return result

# Corrección para replace(year=..., month=...):
def safe_replace_date(dt, year=None, month=None):
    """Reemplaza año y mes de un datetime de forma segura."""
    def to_int_or_none(val):
        if isinstance(val, list):
            return None
        if isinstance(val, int) and not isinstance(val, bool):
            return val
        if isinstance(val, float) and val.is_integer():
            return int(val)
        return None
    y = to_int_or_none(year)
    m = to_int_or_none(month)
    try:
        return dt.replace(year=y, month=m)
    except Exception:
        return dt

# Corrección para argumentos str:
def safe_str_arg(val) -> str:
    return str(val) if val is not None else "" 


def test_safe_float_cases():
    cases = {
        "123.45": 123.45,
        "1,234.56": 1234.56,
        123.45: 123.45,
        "invalid": 0.0,
        None: 0.0
    }
    for s, expected in cases.items():
        result = safe_float(s)
        assert abs(result - expected) < 1e-6, f"safe_float({s!r}) == {result}, esperado {expected}"
    print("✅ Todos los casos de safe_float pasan") 