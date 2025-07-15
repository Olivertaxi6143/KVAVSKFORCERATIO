"""
Utilidades para manejo de datos y validación.
Módulo simplificado con solo las funciones esenciales utilizadas en el flujo.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union, List
import re

logger = logging.getLogger(__name__)

def NORMALIZE_COL(col: str) -> str:
    """Normaliza el nombre de una columna eliminando espacios, mayúsculas y caracteres especiales."""
    return (
        col.strip()
        .replace('"', '')
        .replace("'", '')
        .replace('%', 'pct')
        .replace('(', '')
        .replace(')', '')
        .replace('.', '_')
        .replace('-', '_')
        .replace(' ', '_')
        .lower()
    )

def read_and_prepare(path: Path, is_oos_split: float = 0.75) -> pd.DataFrame:
    """
    Lee y prepara datos de KPIs con normalización y mapeo de columnas.
    - 'Stagnation': periodo de estancamiento (tiempo o trades sin nuevo máximo de equity).
    - 'Stagnation_Trades': número máximo de operaciones consecutivas en estancamiento (si la fuente lo provee).
    """
    try:
        # Leer archivo
        df = pd.read_csv(path, sep=';', decimal=',')
        
        # Normalizar nombres de columnas
        df.columns = [NORMALIZE_COL(col) for col in df.columns]
        
        # Mapeos de columnas
        QVA_COL_MAP = {
            'STRATEGYNAME': 'Strategy_Name',
            'CAGR': 'CAGR',
            'DRAWDOWN': 'Drawdown',
            'MAXDD': 'Drawdown',
            'EXPECTANCY': 'Expectancy',
            'MAXCONSECLOSURES': 'Max_Consec_Losses',
            'MAXCONSECUTIVELOSSES': 'Max_Consec_Losses',
            'SHARPERATIO': 'Sharpe_Ratio',
            'PROFITFACTOR': 'Profit_factor',
            'RINAINDEX': 'RINAIndex',
            'ULCERINDEX': 'Ulcer_Index_pct',
            'ULCERPINDEX': 'Ulcer_Performance_Index',
            'SORTINORATIO': 'Sortino_Ratio',
            'RECOVERYFACTOR': 'RecoveryFactor',
            'VAR': 'VaR_95pct',
            'VAR95': 'VaR_95pct',
            'CVAR': 'CVaR_95pct',
            'CVAR95': 'CVaR_95pct',
            'WINNINGPERCENT': 'Winning_Percent',
            'WINRATE': 'Winning_Percent',
            'TRADESCOUNT': 'of_trades',
            'OFTRADES': 'of_trades',
            'NUMTRADES': 'of_trades',
            'EXPOSURE': 'Exposure',
            'MAXDRAWDOWNDURATION': 'Max_Drawdown_Duration',
            'AVGBARSINTRADE': 'Avg_Bars_in_Trade',
            'AVG_BARS_TRADE': 'Avg_Bars_in_Trade',
                'AVGSTAGTRADES': 'Avg_Stagnation',
    'MAXSTAGTRADES': 'Stagnation',
            'STAGNATION': 'Stagnation',
            'STAGNATION_TRADES': 'Stagnation_Trades',
            'NEWPEAKTRADESPCT': 'New_Peak_Trades_pct',
            'DRAWDOWNTRADESPCT': 'Drawdown_Trades_pct',
            'AVGMAE': 'Avg_MAE_Profit_loss',
            'AVGMFE': 'Avg_MFE_Profit_loss',
            'PAYOUTRATIO': 'Payout_ratio',
            'CALMAR': 'CalmarRatio',
            'CALMARRATIO': 'CalmarRatio',
            'SQN': 'SQN',
        }

        ROBUST_COL_MAP = {
            'CAGRIS': 'CAGR_IS',
            'CAGROOS': 'CAGR_OOS',
            'DRAWDOWNIS': 'Drawdown_IS',
            'DRAWDOWNOOS': 'Drawdown_OOS',
            'SHARPERATIOIS': 'Sharpe_Ratio_IS',
            'SHARPERATIOOOS': 'Sharpe_Ratio_OOS',
            'PROFITFACTORIS': 'Profit_factor_IS',
            'PROFITFACTOROOS': 'Profit_factor_OOS',
            'CALMARRATIOIS': 'CalmarRatio_IS',
            'CALMARRATIOOOS': 'CalmarRatio_OOS',
            'SQNSCOREIS': 'SQN_Score_IS',
            'SQNSCOREOOS': 'SQN_Score_OOS',
        }

        EXTRA_MAP = {
            'SQNSCORE': 'SQN',
            'ULCERPINDEX': 'Ulcer_Performance_Index',
            'WINNINGPERCENTIS': 'Winning_Percent_IS',
            'WINNINGPERCENTOOS': 'Winning_Percent_OOS',
        }

        # Aplicar mapeos
        for old_col, new_col in QVA_COL_MAP.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]
                
        for old_col, new_col in ROBUST_COL_MAP.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]
                
        for old_col, new_col in EXTRA_MAP.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]

        # Limpiar datos
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        
        logger.info(f"Datos preparados: {len(df)} filas, {len(df.columns)} columnas")
        return df
        
    except Exception as e:
        logger.error(f"Error preparando datos: {e}")
        return pd.DataFrame() 

def extract_float_from_tuple(data: Any, index: int = 0, default: float = 0.0) -> float:
    """Extrae un valor numérico de una tupla de forma segura.
    
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

def safe_float(val: Any) -> float:
    """Conversión segura a float, robusta para strings y valores nulos."""
    try:
        if isinstance(val, str):
            val = val.replace(',', '.').replace(' ', '')
        return float(val)
    except (ValueError, TypeError):
        return 0.0


# Función validate_dataframe eliminada - usar src/gui/utils.py en su lugar
# from src.gui.utils import validate_dataframe

# Función validate_numeric_column eliminada - usar src/gui/utils.py en su lugar
# from src.gui.utils import validate_numeric_column

def calculate_basic_stats(df: pd.DataFrame, column: str) -> Dict[str, float]:
    """Calcula estadísticas básicas de una columna numérica.
    
    Args:
        df: DataFrame
        column: Nombre de la columna
    
    Returns:
        Dict[str, float]: Diccionario con estadísticas básicas
    """
    try:
        # Validación básica sin dependencia externa
        if column not in df.columns:
            logger.warning(f"Columna '{column}' no encontrada en DataFrame.")
            return {}
        
        # Convertir a numérico
        numeric_series = pd.to_numeric(df[column], errors='coerce')
        if numeric_series.isna().all():
            logger.warning(f"Columna '{column}' es completamente NaN.")
            return {}
            
        # Calcular estadísticas de forma segura
        mean_val = numeric_series.mean()
        std_val = numeric_series.std()
        min_val = numeric_series.min()
        max_val = numeric_series.max()
        median_val = numeric_series.median()
        count_val = numeric_series.count()
        
        stats_dict = {
            'mean': float(mean_val) if pd.notna(mean_val) else 0.0,
            'std': float(std_val) if pd.notna(std_val) else 0.0,
            'min': float(min_val) if pd.notna(min_val) else 0.0,
            'max': float(max_val) if pd.notna(max_val) else 0.0,
            'median': float(median_val) if pd.notna(median_val) else 0.0,
            'count': float(count_val) if pd.notna(count_val) else 0.0
        }
        return stats_dict
    except Exception as e:
        logger.error(f"Error calculando estadísticas de {column}: {e}")
        return {}

def detect_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 1.5) -> Dict[str, Any]:
    """Detecta outliers usando el método IQR.
    
    Args:
        df: DataFrame
        column: Nombre de la columna
        factor: Factor para el cálculo de outliers (por defecto 1.5)
    
    Returns:
        Dict[str, Any]: Diccionario con información de outliers
    """
    try:
        if not validate_numeric_column(df, column):
            logger.warning(f"No se pueden detectar outliers: columna '{column}' inválida.")
            return {'outliers': [], 'count': 0, 'percentage': 0.0}
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        return {
            'outliers': outliers[column].tolist(),
            'count': int(len(outliers)),
            'percentage': float(len(outliers)) / float(len(df)) * 100 if len(df) > 0 else 0.0,
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound)
        }
    except Exception as e:
        logger.error(f"Error detectando outliers en {column}: {e}")
        return {'outliers': [], 'count': 0, 'percentage': 0.0}

# ===================== FUNCIONES DE MÉTRICAS (Migradas desde core/utils/metrics_calculation.py) =====================

def calculate_max_drawdown(returns: pd.Series) -> float:
    """
    Calcula el máximo drawdown de una serie de retornos.
    Args:
        returns: Serie de retornos (pueden ser porcentajes o fracciones)
    Returns:
        Drawdown máximo (valor negativo)
    """
    if returns.isnull().all() or len(returns) < 2:
        return np.nan
    cumulative = (1 + returns.fillna(0)).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return float(drawdown.min())


def calculate_percentile_tail(returns: pd.Series, percentile: float = 5.0) -> float:
    """
    Calcula el valor en la cola inferior de la distribución de retornos.
    Args:
        returns: Serie de retornos
        percentile: Percentil de la cola (por ejemplo, 5 para el 5%)
    Returns:
        Valor en el percentil especificado
    """
    if returns.isnull().all() or len(returns) < 2:
        return np.nan
    return float(np.percentile(returns.dropna(), percentile))


def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
    """
    Calcula los retornos acumulados de una serie de retornos.
    Args:
        returns: Serie de retornos
    Returns:
        Serie de retornos acumulados
    """
    if returns.isnull().all() or len(returns) < 2:
        return pd.Series([np.nan] * len(returns), index=returns.index)
    return (1 + returns.fillna(0)).cumprod()


def clean_returns(returns: pd.Series) -> pd.Series:
    """
    Limpia una serie de retornos eliminando NaN, inf y convirtiendo a fracción si es necesario.
    Args:
        returns: Serie de retornos
    Returns:
        Serie de retornos limpia
    """
    clean = returns.replace([np.inf, -np.inf], np.nan).dropna()
    # Si los retornos parecen estar en porcentaje (>1), convertir a fracción
    if clean.max() > 1.0:
        clean = clean / 100.0
    return clean

# ===================== FUNCIONES DE PROCESAMIENTO DE DATOS (Migradas desde core/utils/data_utils.py) =====================

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

# ===================== FUNCIONES DE CONVERSIÓN DE TIPOS (Migradas desde core/utils/type_converters.py) =====================

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


def safe_str_arg(val) -> str:
    """Convierte argumento a string de forma segura."""
    return str(val) if val is not None else "" 