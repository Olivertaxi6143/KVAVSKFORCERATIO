"""
Utilidades de datos para el core engine.

Este módulo contiene funciones auxiliares para el manejo robusto de datos:
- Conversiones seguras de tipos
- Manejo de datos faltantes
- Funciones auxiliares para pandas/numpy
"""

import pandas as pd
import numpy as np
import logging
from typing import Union, Any, Optional, List

# Configurar logging
logger = logging.getLogger(__name__)

def safe_sum(mask: Union[pd.Series, pd.DataFrame, np.ndarray, Any]) -> int:
    """
    Convierte cualquier tipo de máscara booleana a int de forma robusta.
    
    Args:
        mask: Máscara booleana (Series, DataFrame, ndarray, o escalar)
        
    Returns:
        int: Suma de valores True en la máscara
    """
    if isinstance(mask, (pd.Series, np.ndarray)):
        return int(np.sum(mask))
    elif isinstance(mask, pd.DataFrame):
        return int(mask.values.sum())
    else:
        return int(mask)


def safe_values(obj: Union[pd.Series, pd.DataFrame, Any]) -> Union[np.ndarray, Any]:
    """
    Accede a .values de forma segura para Series/DataFrame.
    
    Args:
        obj: Objeto pandas o numpy
        
    Returns:
        np.ndarray: Valores del objeto
    """
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        return obj.values
    else:
        return np.asarray(obj)


def safe_float(val: Any) -> float:
    """
    Conversión segura a float con manejo de errores mejorado.
    
    Args:
        val: Valor a convertir
        
    Returns:
        float: Valor convertido o 0.0 si falla
    """
    try:
        if isinstance(val, str):
            val = val.replace(',', '.').replace(' ', '')
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def improve_missing_data_handling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mejora el manejo de datos faltantes en el DataFrame.
    
    Args:
        df: DataFrame con datos de estrategias
        
    Returns:
        DataFrame con datos faltantes manejados apropiadamente
    """
    try:
        logger.info("Mejorando manejo de datos faltantes...")
        
        # Crear una copia para no modificar el original
        df_improved = df.copy()
        
        # Identificar columnas numéricas
        numeric_columns = df_improved.select_dtypes(include=[np.number]).columns
        
        # Para columnas numéricas, usar métodos apropiados de imputación
        for col in numeric_columns:
            if bool(df_improved[col].isna().any()):
                # Para métricas de rendimiento, usar mediana (más robusta)
                if any(metric in col.lower() for metric in ['cagr', 'profit', 'sharpe', 'return']):
                    df_improved[col] = df_improved[col].fillna(df_improved[col].median())
                # Para métricas de riesgo, usar percentil 75 (conservador)
                elif any(metric in col.lower() for metric in ['drawdown', 'risk', 'var', 'cvar']):
                    quantile_value = df_improved[col].quantile(0.75)
                    df_improved[col] = df_improved[col].fillna(float(quantile_value))
                # Para otras métricas numéricas, usar media
                else:
                    df_improved[col] = df_improved[col].fillna(df_improved[col].mean())
        
        # Para columnas categóricas, usar moda o valor por defecto
        categorical_columns = df_improved.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if bool(df_improved[col].isna().any()):
                mode_value = df_improved[col].mode()
                # Corrección robusta para acceso seguro a datetime64/timedelta64
                if isinstance(mode_value, pd.Series) and not mode_value.empty:
                    # Si es Serie y no está vacía, usar .iloc[0]
                    fill_value = mode_value.iloc[0]
                elif hasattr(mode_value, 'item') and callable(getattr(mode_value, 'item', None)):
                    # Si es numpy escalar (datetime64/timedelta64), usar .item()
                    fill_value = mode_value.item()
                elif hasattr(mode_value, '__getitem__') and len(mode_value) > 0:
                    # Si tiene __getitem__ y no está vacío, usar [0]
                    # Convertir a numpy array antes de indexar para evitar errores de datetime64/timedelta64
                    mode_array = np.array(mode_value)
                    fill_value = mode_array[0]
                else:
                    # Si es escalar, usarlo directamente
                    fill_value = mode_value
                # Convertir fill_value a tipo compatible con fillna
                if isinstance(fill_value, (np.ndarray, pd.Series)):
                    if hasattr(fill_value, 'item'):
                        fill_value = float(fill_value.item())
                    else:
                        # Convertir a numpy array antes de indexar
                        fill_array = np.array(fill_value)
                        fill_value = float(fill_array[0])
                df_improved[col] = df_improved[col].fillna(fill_value)
        
        # Verificar que no queden valores NaN
        remaining_nans = df_improved.isna().sum().sum()
        if remaining_nans > 0:
            logger.warning(f"Quedan {remaining_nans} valores NaN después de la imputación")
            # Imputación final con valores por defecto
            df_improved = df_improved.fillna(0)
        
        logger.info("Manejo de datos faltantes completado exitosamente")
        return df_improved
        
    except Exception as e:
        logger.error(f"Error en manejo de datos faltantes: {e}")
        # En caso de error, devolver el DataFrame original
        return df


def validate_dataframe(df: pd.DataFrame, required_columns: Optional[List[str]] = None) -> tuple[bool, list[str]]:
    """
    Valida que un DataFrame tenga la estructura esperada.
    
    Args:
        df: DataFrame a validar
        required_columns: Lista de columnas requeridas
        
    Returns:
        tuple: (es_válido, lista_de_errores)
    """
    errors = []
    
    # Verificar que no esté vacío
    if df.empty:
        errors.append("DataFrame está vacío")
        return False, errors
    
    columns: List[str] = required_columns if required_columns is not None else []
    if columns:
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Columnas faltantes: {missing_columns}")
    
    # Verificar tipos de datos
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) == 0:
        errors.append("No hay columnas numéricas en el DataFrame")
    
    return len(errors) == 0, errors


def clean_extreme_values(df: pd.DataFrame, method: str = 'iqr', factor: float = 1.5) -> pd.DataFrame:
    """
    Limpia valores extremos del DataFrame.
    
    Args:
        df: DataFrame a limpiar
        method: Método de limpieza ('iqr', 'zscore', 'percentile')
        factor: Factor para el método IQR
        
    Returns:
        DataFrame con valores extremos limpiados
    """
    df_cleaned = df.copy()
    
    numeric_columns = df_cleaned.select_dtypes(include=[np.number]).columns
    
    for col in numeric_columns:
        if method == 'iqr':
            Q1 = df_cleaned[col].quantile(0.25)
            Q3 = df_cleaned[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - factor * IQR
            upper_bound = Q3 + factor * IQR
            
            # Reemplazar valores extremos con los límites
            df_cleaned[col] = df_cleaned[col].clip(lower=lower_bound, upper=upper_bound)
            
        elif method == 'zscore':
            z_scores = np.abs((df_cleaned[col] - df_cleaned[col].mean()) / df_cleaned[col].std())
            df_cleaned[col] = df_cleaned[col].mask(z_scores > factor, df_cleaned[col].median())
            
        elif method == 'percentile':
            lower_percentile = df_cleaned[col].quantile(0.01)
            upper_percentile = df_cleaned[col].quantile(0.99)
            df_cleaned[col] = df_cleaned[col].clip(lower=lower_percentile, upper=upper_percentile)
    
    return df_cleaned


def normalize_series(series: pd.Series, method: str = 'minmax', **kwargs) -> pd.Series:
    """
    Normaliza una serie de datos.
    
    Args:
        series: Serie a normalizar
        method: Método de normalización ('minmax', 'zscore', 'robust')
        **kwargs: Parámetros adicionales
        
    Returns:
        Serie normalizada
    """
    if method == 'minmax':
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series(0.5, index=series.index)
        return (series - min_val) / (max_val - min_val)
        
    elif method == 'zscore':
        mean_val = series.mean()
        std_val = series.std()
        if std_val == 0:
            return pd.Series(0, index=series.index)
        return (series - mean_val) / std_val
        
    elif method == 'robust':
        median_val = series.median()
        mad_val = np.median(np.abs(series - median_val))
        if mad_val == 0:
            return pd.Series(0, index=series.index)
        return (series - median_val) / mad_val
        
    else:
        raise ValueError(f"Método de normalización '{method}' no soportado")


def calculate_percentiles(series: pd.Series, percentiles: Optional[List[int]] = None) -> dict:
    """
    Calcula percentiles de una serie.
    
    Args:
        series: Serie de datos
        percentiles: Lista de percentiles a calcular
        
    Returns:
        Diccionario con percentiles calculados
    """
    plist: List[int] = percentiles if percentiles is not None else [10, 25, 50, 75, 90]
    return {f"p{p}": series.quantile(p/100) for p in plist} 