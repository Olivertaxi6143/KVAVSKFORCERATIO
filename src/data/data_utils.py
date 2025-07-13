"""
Utilidades para manejo de datos y validación.
Módulo simplificado con solo las funciones esenciales utilizadas en el flujo.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
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

def validate_dataframe(df: pd.DataFrame | None) -> bool:
    """
    Valida si un DataFrame es válido.
    
    Args:
        df: DataFrame a validar
        
    Returns:
        True si el DataFrame es válido, False en caso contrario
    """
    if df is None:
        return False
    
    if not isinstance(df, pd.DataFrame):
        return False
    
    if df.empty:
        return False
    
    return True

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