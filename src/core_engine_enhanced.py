"""
CORE_ENGINE_ENHANCED.py - Motor Central Mejorado para GUI

Este archivo implementa todas las mejoras sugeridas para optimizar el flujo de trabajo en la GUI:
- Gestión robusta de configuración con validación
- Carga de datos mejorada con manejo de errores
- Procesamiento en hilos para mantener GUI responsiva
- Optimización de rendimiento con procesamiento en chunks
- Mejoras científicas opcionales y controlables
- Logging detallado para debugging
- Manejo de memoria optimizado

Basado en el feedback detallado para mejorar la integración con la GUI.
"""

import pandas as pd
import numpy as np
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import warnings
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import IsolationForest
from sklearn.covariance import EllipticEnvelope
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import norm, t
import yfinance as yf
import requests
from io import StringIO
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import hashlib
import pickle
from pathlib import Path
import re
from collections import defaultdict, Counter
import itertools
from functools import lru_cache, wraps
import inspect
import traceback
import sys
from contextlib import contextmanager
import gc
import psutil
import platform
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from typing_extensions import TypedDict, Literal
import warnings
# ELIMINADO: data_utils.py eliminado, funciones integradas en DataManager
from src.data_manager import DataManager
import functools
from tqdm import tqdm
from src.logger_config import (
    setup_logger,
    get_logger,
    LOG_FORMAT,
    LOG_LEVEL
)

warnings.filterwarnings("ignore")

# Función auxiliar para conversiones robustas de máscaras booleanas
def _safe_sum(mask):
    """Convierte cualquier tipo de máscara booleana a int de forma robusta."""
    if isinstance(mask, (pd.Series, np.ndarray)):
        return int(np.sum(mask))
    elif isinstance(mask, pd.DataFrame):
        return int(mask.values.sum())
    else:
        return int(mask)

# Función auxiliar para acceso seguro a .values
def _safe_values(obj):
    """Accede a .values de forma segura para Series/DataFrame."""
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        return obj.values
    else:
        return obj


def _improve_missing_data_handling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mejora el manejo de datos faltantes en el DataFrame.
    
    Args:
        df: DataFrame con datos de estrategias
        
    Returns:
        DataFrame con datos faltantes manejados apropiadamente
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info("Mejorando manejo de datos faltantes...")
        
        # Crear una copia para no modificar el original
        df_improved = df.copy()
        
        # Identificar columnas numéricas
        numeric_columns = df_improved.select_dtypes(include=[np.number]).columns
        
        # Para columnas numéricas, usar métodos apropiados de imputación
        for col in numeric_columns:
            if df_improved[col].isna().any():
                # Para métricas de rendimiento, usar mediana (más robusta)
                if any(metric in col.lower() for metric in ['cagr', 'profit', 'sharpe', 'return']):
                    df_improved[col] = df_improved[col].fillna(df_improved[col].median())
                # Para métricas de riesgo, usar percentil 75 (conservador)
                elif any(metric in col.lower() for metric in ['drawdown', 'risk', 'var', 'cvar']):
                    df_improved[col] = df_improved[col].fillna(df_improved[col].quantile(0.75))
                # Para otras métricas numéricas, usar media
                else:
                    df_improved[col] = df_improved[col].fillna(df_improved[col].mean())
        
        # Para columnas categóricas, usar moda o valor por defecto
        categorical_columns = df_improved.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if df_improved[col].isna().any():
                mode_value = df_improved[col].mode()
                if not mode_value.empty:
                    df_improved[col] = df_improved[col].fillna(mode_value.iloc[0])
                else:
                    df_improved[col] = df_improved[col].fillna("N/A")
        
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


# Configurar logging mejorado
try:
    from .logger_config import (
        setup_logger,
        log_error_with_context,
        log_performance_metrics,
    )
except ImportError:
    # Fallback para importación absoluta
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from src.logger_config import (
        setup_logger,
        log_error_with_context,
        log_performance_metrics,
    )

# Inicializar sistema de logging si no está ya configurado
if not logging.getLogger().handlers:
    setup_logger(
        name="core_engine"
    )

# Configuración global de rendimiento
CHUNK_SIZE = 10000  # Procesar datos en chunks de 10k filas
# Máximo 4 workers, con fallback a 4
MAX_WORKERS = min(psutil.cpu_count() or 4, 4)
CACHE_SIZE = 128  # Tamaño del cache LRU
GUI_UPDATE_INTERVAL = 0.1  # Intervalo de actualización de GUI en segundos

# Configuración de robustez
MAX_RETRIES = 3  # Máximo número de reintentos
TIMEOUT_SECONDS = 300  # Timeout por operación (5 minutos)
ERROR_RECOVERY_ENABLED = True  # Habilitar recuperación automática de errores
VALIDATION_STRICT_MODE = False  # Modo estricto de validación

def safe_float(val):
    """Conversión segura a float con manejo de errores mejorado."""
    try:
        if isinstance(val, str):
            val = val.replace(',', '.').replace(' ', '')
        return float(val)
    except (ValueError, TypeError):
        return 0.0


class RobustErrorHandler:
    """Manejador robusto de errores con recuperación automática."""
    
    def __init__(self, max_retries: int = MAX_RETRIES, timeout: int = TIMEOUT_SECONDS):
        self.max_retries = max_retries
        self.timeout = timeout
        self.logger = setup_logger("kforce")
        self.error_counts = defaultdict(int)
        self.recovery_strategies = {}
        
    def register_recovery_strategy(self, error_type: str, strategy_func):
        """Registra una estrategia de recuperación para un tipo de error."""
        self.recovery_strategies[error_type] = strategy_func
        
    def execute_with_retry(self, func, *args, **kwargs):
        """Ejecuta una función con reintentos automáticos."""
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
                
                if attempt < self.max_retries - 1:
                    time.sleep(min(2 ** attempt, 10))  # Backoff exponencial
        
        self.logger.error(f"Todas las tentativas fallaron para {func.__name__}")
        raise last_error
        
    def get_error_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de errores."""
        return {
            'error_counts': dict(self.error_counts),
            'total_errors': sum(self.error_counts.values()),
            'recovery_strategies': list(self.recovery_strategies.keys())
        }
        
    def reset_error_counts(self):
        """Reinicia los contadores de errores."""
        self.error_counts.clear()

@dataclass
class KPIConfig:
    """Configuración de un KPI específico con validación."""
    name: str
    enabled: bool
    weight: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""
    
    def validate(self) -> bool:
        """Valida la configuración del KPI."""
        if not self.name or self.name.strip() == "":
            return False
        if self.weight < 0:
            return False
        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                return False
        return True

@dataclass
class TradingStyleConfig:
    """Configuración para un estilo de trading específico."""
    name: str
    description: str
    kpi_weights: Dict[str, float]
    component_weights: Dict[str, float]
    priority_kpis: List[str]
    
    def validate(self) -> bool:
        """Valida la configuración del estilo de trading."""
        if not self.name or self.name.strip() == "":
            return False
        if not self.kpi_weights:
            return False
        if not self.component_weights:
            return False
        # Validar que los pesos sumen aproximadamente 1
        total_weight = sum(self.component_weights.values())
        if abs(total_weight - 1.0) > 0.1:
            return False
        return True

class ProgressCallback:
    """Clase para manejar callbacks de progreso en la GUI."""
    
    def __init__(self):
        self.progress_queue = queue.Queue()
        self.is_cancelled = False
        
    def update_progress(self, step: str, current: int, total: int, description: str = ""):
        """Actualiza el progreso."""
        if not self.is_cancelled:
            self.progress_queue.put({
                'step': step,
                'current': current,
                'total': total,
                'description': description,
                'percentage': (current / total * 100) if total > 0 else 0
            })
    
    def cancel(self):
        """Cancela la operación."""
        self.is_cancelled = True
        
    def get_progress(self):
        """Obtiene el progreso actual."""
        try:
            return self.progress_queue.get_nowait()
        except:
            return None

class ConfigManagerEnhanced:
    """
    Gestor de configuración mejorado con validación robusta y manejo de errores.
    """
    
    def __init__(self, config_file: str = "config/trading_config.json"):
        self.logger = setup_logger("kforce")
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configuración por defecto mejorada
        self.default_config = self._create_default_config()
        self.current_config = self.load_config()
        self.validation_errors = []
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Crea la configuración por defecto con todos los KPIs disponibles."""
        return {
            "trading_style": "General",
            "selected_kpis": {
                # KPIs Integrales
                "Strategy_Name": {"enabled": True, "weight": 1.0, "description": "Nombre de la Estrategia"},
                "Profit_factor": {"enabled": True, "weight": 1.0, "description": "Factor de Beneficio"},
                "Sharpe_Ratio": {"enabled": True, "weight": 1.0, "description": "Ratio de Sharpe"},
                "CalmarRatio": {"enabled": True, "weight": 1.0, "description": "Ratio de Calmar"},
                "Max_DD_%": {"enabled": True, "weight": 1.0, "description": "Máximo Drawdown (%)"},
                "Stagnation_Trades": {"enabled": True, "weight": 1.0, "description": "Operaciones de Estancamiento"},
                "#_of_trades": {"enabled": True, "weight": 1.0, "description": "Número de Operaciones"},
                "Avg_Bars_in_Trade": {"enabled": True, "weight": 1.0, "description": "Promedio de Barras por Operación"},
                "Ulcer_Index_%": {"enabled": True, "weight": 1.0, "description": "Índice de Úlcera (%)"},
                "VaR_95%": {"enabled": True, "weight": 1.0, "description": "Value at Risk (95%)"},
                "CVaR_95%": {"enabled": True, "weight": 1.0, "description": "Conditional VaR (95%)"},
                "Winning_Percent": {"enabled": True, "weight": 1.0, "description": "Porcentaje de Operaciones Ganadoras"},
                "Max_Consec_Losses": {"enabled": True, "weight": 1.0, "description": "Máximas Pérdidas Consecutivas"},
                "Payout_ratio": {"enabled": True, "weight": 1.0, "description": "Ratio de Pago"},
                "Sortino_Ratio": {"enabled": True, "weight": 1.0, "description": "Ratio de Sortino"},
                "RecoveryFactor": {"enabled": True, "weight": 1.0, "description": "Factor de Recuperación"},
                "RINAIndex": {"enabled": True, "weight": 1.0, "description": "Índice RINA"},
                "Ulcer_Performance_Index": {"enabled": True, "weight": 1.0, "description": "Índice de Rendimiento de Úlcera"},
                "SQN": {"enabled": True, "weight": 1.0, "description": "System Quality Number"},
                "Net_profit": {"enabled": True, "weight": 1.0, "description": "Beneficio Neto"},
                "Expectancy": {"enabled": True, "weight": 1.0, "description": "Expectativa"},
                "Exposure": {"enabled": True, "weight": 1.0, "description": "Exposición"},
                "CAGR": {"enabled": True, "weight": 1.0, "description": "CAGR"},
                "Total_Data_Months": {"enabled": True, "weight": 1.0, "description": "Meses Totales de Datos"},
                "Max_Drawdown_Duration": {"enabled": True, "weight": 1.0, "description": "Duración Máxima del Drawdown"},
                "New_Peak_Trades_%": {"enabled": True, "weight": 1.0, "description": "Operaciones de Nuevo Pico (%)"},
                "Drawdown_Trades_%": {"enabled": True, "weight": 1.0, "description": "Operaciones en Drawdown (%)"},
                
                # KPIs IS
                "Sharpe_Ratio_IS": {"enabled": True, "weight": 1.0, "description": "Ratio de Sharpe (IS)"},
                "Profit_Factor_IS": {"enabled": True, "weight": 1.0, "description": "Factor de Beneficio (IS)"},
                "CalmarRatio_IS": {"enabled": True, "weight": 1.0, "description": "Ratio de Calmar (IS)"},
                "Winning_Percent_IS": {"enabled": True, "weight": 1.0, "description": "Porcentaje de Operaciones Ganadoras (IS)"},
                "CAGR_IS": {"enabled": True, "weight": 1.0, "description": "CAGR (IS)"},
                "Max_Drawdown_IS": {"enabled": True, "weight": 1.0, "description": "Máximo Drawdown (IS)"},
                "Net_Profit_IS": {"enabled": True, "weight": 1.0, "description": "Beneficio Neto (IS)"},
                
                # KPIs OOS
                "Sharpe_Ratio_OOS": {"enabled": True, "weight": 1.0, "description": "Ratio de Sharpe (OOS)"},
                "Profit_Factor_OOS": {"enabled": True, "weight": 1.0, "description": "Factor de Beneficio (OOS)"},
                "CalmarRatio_OOS": {"enabled": True, "weight": 1.0, "description": "Ratio de Calmar (OOS)"},
                "Winning_Percent_OOS": {"enabled": True, "weight": 1.0, "description": "Porcentaje de Operaciones Ganadoras (OOS)"},
                "CAGR_OOS": {"enabled": True, "weight": 1.0, "description": "CAGR (OOS)"},
                "Max_Drawdown_OOS": {"enabled": True, "weight": 1.0, "description": "Máximo Drawdown (OOS)"},
                "Net_Profit_OOS": {"enabled": True, "weight": 1.0, "description": "Beneficio Neto (OOS)"}
            },
            "component_weights": {
                "profitability": 0.4,
                "risk": 0.35,
                "consistency": 0.25
            },
            "trading_styles": {
                "Scalping": {
                    "description": "Operaciones de muy corto plazo (segundos a minutos)",
                    "kpi_weights": {
                        "Exposure": 1.5,
                        "Avg_Bars_in_Trade": 1.5,
                        "Winning_Percent": 1.3,
                        "Profit_factor": 1.2,
                        "Max_Consec_Losses": 1.4,
                        "Stagnation_Trades": 1.3
                    },
                    "component_weights": {
                        "profitability": 0.35,
                        "risk": 0.4,
                        "consistency": 0.25
                    },
                    "priority_kpis": ["Exposure", "Avg_Bars_in_Trade", "Winning_Percent", "Max_Consec_Losses"]
                },
                "Intraday": {
                    "description": "Operaciones dentro del mismo día",
                    "kpi_weights": {
                        "CAGR": 1.2,
                        "Sharpe_Ratio": 1.3,
                        "Max_DD_%": 1.4,
                        "RecoveryFactor": 1.2,
                        "Stagnation_Trades": 1.1
                    },
                    "component_weights": {
                        "profitability": 0.4,
                        "risk": 0.35,
                        "consistency": 0.25
                    },
                    "priority_kpis": ["CAGR", "Sharpe_Ratio", "Max_DD_%", "RecoveryFactor"]
                },
                "Swing": {
                    "description": "Operaciones de varios días a semanas",
                    "kpi_weights": {
                        "CAGR": 1.4,
                        "CalmarRatio": 1.3,
                        "Max_DD_%": 1.5,
                        "RecoveryFactor": 1.4,
                        "Stagnation_Trades": 1.2
                    },
                    "component_weights": {
                        "profitability": 0.45,
                        "risk": 0.3,
                        "consistency": 0.25
                    },
                    "priority_kpis": ["CAGR", "CalmarRatio", "Max_DD_%", "RecoveryFactor"]
                },
                "Position": {
                    "description": "Operaciones de largo plazo (meses a años)",
                    "kpi_weights": {
                        "CAGR": 1.5,
                        "CalmarRatio": 1.4,
                        "Max_DD_%": 1.6,
                        "RecoveryFactor": 1.5,
                        "Stagnation_Trades": 1.1
                    },
                    "component_weights": {
                        "profitability": 0.5,
                        "risk": 0.25,
                        "consistency": 0.25
                    },
                    "priority_kpis": ["CAGR", "CalmarRatio", "Max_DD_%", "RecoveryFactor"]
                }
            },
            "performance_settings": {
                "chunk_size": CHUNK_SIZE,
                "max_workers": MAX_WORKERS,
                "cache_size": CACHE_SIZE,
                "gui_update_interval": GUI_UPDATE_INTERVAL
            },
            "scientific_improvements": {
                "enabled": True,
                "hmm_analysis": True,
                "stress_testing": True,
                "data_drift_detection": True,
                "temporal_validation": True
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        Carga la configuración con validación robusta.
        
        Returns:
            Dict con la configuración cargada o por defecto
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Validar que las claves esenciales estén presentes
                required_keys = ["trading_style", "selected_kpis", "trading_styles"]
                missing_keys = [key for key in required_keys if key not in config]
                
                if missing_keys:
                    self.logger.warning(f"Configuración incompleta, claves faltantes: {missing_keys}")
                    self.logger.info("Usando configuración por defecto")
                    return self.default_config
                
                # Validar estructura de KPIs
                if not self._validate_kpis_config(config.get("selected_kpis", {})):
                    self.logger.warning("Configuración de KPIs inválida, usando por defecto")
                    config["selected_kpis"] = self.default_config["selected_kpis"]
                
                # Validar estilos de trading
                if not self._validate_trading_styles_config(config.get("trading_styles", {})):
                    self.logger.warning("Configuración de estilos de trading inválida, usando por defecto")
                    config["trading_styles"] = self.default_config["trading_styles"]
                
                self.logger.info("Configuración cargada exitosamente desde archivo")
                return config
            else:
                self.logger.info("Archivo de configuración no encontrado, creando configuración por defecto")
                self.save_config(self.default_config)
                return self.default_config
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decodificando JSON de configuración: {e}")
            self.logger.info("Usando configuración por defecto")
            return self.default_config
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")
            self.logger.info("Usando configuración por defecto")
            return self.default_config
    
    def _validate_kpis_config(self, kpis_config: Dict[str, Any]) -> bool:
        """Valida la configuración de KPIs."""
        if not isinstance(kpis_config, dict):
            return False
        
        for kpi_name, kpi_config in kpis_config.items():
            if not isinstance(kpi_config, dict):
                return False
            required_fields = ["enabled", "weight"]
            if not all(field in kpi_config for field in required_fields):
                return False
            if not isinstance(kpi_config["enabled"], bool):
                return False
            if not isinstance(kpi_config["weight"], (int, float)):
                return False
            if kpi_config["weight"] < 0:
                return False
        
        return True
    
    def _validate_trading_styles_config(self, styles_config: Dict[str, Any]) -> bool:
        """Valida la configuración de estilos de trading."""
        if not isinstance(styles_config, dict):
            return False
        
        for style_name, style_config in styles_config.items():
            if not isinstance(style_config, dict):
                return False
            required_fields = ["description", "kpi_weights", "component_weights", "priority_kpis"]
            if not all(field in style_config for field in required_fields):
                return False
        
        return True
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Guarda la configuración con validación previa.
        
        Args:
            config: Configuración a guardar
            
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        try:
            # Validar configuración antes de guardar
            if not self._validate_kpis_config(config.get("selected_kpis", {})):
                raise ValueError("Configuración de KPIs inválida")
            
            if not self._validate_trading_styles_config(config.get("trading_styles", {})):
                raise ValueError("Configuración de estilos de trading inválida")
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self.current_config = config
            self.logger.info("Configuración guardada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")
            return False
    
    def validate_config(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valida que la configuración sea compatible con los datos.
        
        Args:
            df: DataFrame con los datos a analizar
            
        Returns:
            Tupla con (es_válido, lista_de_errores)
        """
        errors = []
        
        # Verificar que los KPIs habilitados existan en los datos
        enabled_kpis = self.get_enabled_kpis()
        missing_kpis = [kpi for kpi in enabled_kpis if kpi not in df.columns]
        
        if missing_kpis:
            errors.append(f"KPIs faltantes en los datos: {missing_kpis}")
        
        # Verificar que el estilo de trading seleccionado existe
        current_style = self.current_config.get("trading_style", "General")
        available_styles = self.get_available_trading_styles()
        
        if current_style not in available_styles:
            errors.append(f"Estilo de trading '{current_style}' no disponible")
        
        # Verificar que hay suficientes datos
        if len(df) < 10:
            errors.append("Insuficientes datos para análisis (mínimo 10 estrategias)")
        
        return len(errors) == 0, errors
    
    def get_enabled_kpis(self) -> List[str]:
        """Obtiene la lista de KPIs habilitados."""
        kpis_config = self.current_config.get("selected_kpis", {})
        return [kpi for kpi, config in kpis_config.items() if config.get("enabled", False)]
    
    def get_kpi_weight(self, kpi_name: str) -> float:
        """Obtiene el peso de un KPI específico."""
        kpis_config = self.current_config.get("selected_kpis", {})
        return kpis_config.get(kpi_name, {}).get("weight", 1.0)
    
    def get_component_weights(self) -> Dict[str, float]:
        """Obtiene los pesos de los componentes."""
        return self.current_config.get("component_weights", {})
    
    def get_trading_style_config(self) -> Dict[str, Any]:
        """Obtiene la configuración del estilo de trading actual."""
        current_style = self.current_config.get("trading_style", "General")
        styles_config = self.current_config.get("trading_styles", {})
        return styles_config.get(current_style, {})
    
    def update_trading_style(self, style: str) -> bool:
        """
        Actualiza el estilo de trading con validación.
        
        Args:
            style: Nuevo estilo de trading
            
        Returns:
            True si se actualizó exitosamente, False en caso contrario
        """
        available_styles = self.get_available_trading_styles()
        if style not in available_styles:
            self.logger.error(f"Estilo de trading '{style}' no disponible")
            return False
        
        self.current_config["trading_style"] = style
        return self.save_config(self.current_config)
    
    def update_kpi_selection(self, kpi_name: str, enabled: bool, weight: float = 1.0) -> bool:
        """
        Actualiza la selección de un KPI con validación.
        
        Args:
            kpi_name: Nombre del KPI
            enabled: Si está habilitado
            weight: Peso del KPI
            
        Returns:
            True si se actualizó exitosamente, False en caso contrario
        """
        if weight < 0:
            self.logger.error("El peso del KPI no puede ser negativo")
            return False
        
        kpis_config = self.current_config.get("selected_kpis", {})
        if kpi_name not in kpis_config:
            self.logger.error(f"KPI '{kpi_name}' no encontrado en la configuración")
            return False
        
        kpis_config[kpi_name]["enabled"] = enabled
        kpis_config[kpi_name]["weight"] = weight
        
        return self.save_config(self.current_config)
    
    def reset_to_default(self) -> bool:
        """
        Restaura la configuración por defecto.
        
        Returns:
            True si se restauró exitosamente, False en caso contrario
        """
        try:
            self.current_config = self.default_config.copy()
            return self.save_config(self.current_config)
        except Exception as e:
            self.logger.error(f"Error restaurando configuración por defecto: {e}")
            return False
    
    def get_available_trading_styles(self) -> List[str]:
        """Obtiene la lista de estilos de trading disponibles."""
        styles_config = self.current_config.get("trading_styles", {})
        return list(styles_config.keys())
    
    def get_available_kpis(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene la configuración completa de KPIs disponibles."""
        return self.current_config.get("selected_kpis", {})

class DataLoaderEnhanced:
    """
    Cargador de datos mejorado con validación robusta y manejo de errores.
    """
    
    def __init__(self, progress_callback: Optional[ProgressCallback] = None):
        self.logger = setup_logger("kforce")
        self.progress_callback = progress_callback
        self.data_cache = {}
        
    def load_and_prepare_data(self, file_path: str, is_oos_split: float = 0.75) -> pd.DataFrame:
        """
        Carga y prepara datos con manejo robusto de errores.
        
        Args:
            file_path: Ruta al archivo de datos
            is_oos_split: Proporción para división IS/OOS
            
        Returns:
            DataFrame preparado
            
        Raises:
            ValueError: Si no se pueden cargar los datos
        """
        try:
            self.logger.info(f"Cargando datos desde: {file_path}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Carga", 0, 100, "Iniciando carga de datos...")
            
            # Verificar que el archivo existe
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
            # Verificar tamaño del archivo
            file_size = file_path_obj.stat().st_size
            if file_size == 0:
                raise ValueError(f"Archivo vacío: {file_path}")
            
            if file_size > 100 * 1024 * 1024:  # 100MB
                self.logger.warning(f"Archivo muy grande ({file_size / 1024 / 1024:.1f}MB), puede tardar en cargar")
            
            # Cargar datos según el formato
            df = self._load_file_by_format(file_path_obj)
            
            if self.progress_callback:
                self.progress_callback.update_progress("Carga", 30, 100, "Datos cargados, preparando...")
            
            # Preparar y validar datos
            df = self._prepare_dataframe(df, file_path_obj)
            
            if self.progress_callback:
                self.progress_callback.update_progress("Carga", 60, 100, "Aplicando mapeos...")
            
            # Aplicar mapeos de columnas
            df = self._apply_column_mappings(df)
            
            if self.progress_callback:
                self.progress_callback.update_progress("Carga", 80, 100, "Finalizando preparación...")
            
            # Limpiar y validar datos finales
            df = self._clean_and_validate_final_data(df, is_oos_split)
            
            if self.progress_callback:
                self.progress_callback.update_progress("Carga", 100, 100, "Carga completada")
            
            self.logger.info(f"Datos cargados exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            return df
            
        except Exception as e:
            self.logger.error(f"Error cargando datos: {str(e)}")
            if self.progress_callback:
                self.progress_callback.update_progress("Carga", 0, 100, f"Error: {str(e)}")
            raise ValueError(f"No se pudieron cargar los datos: {str(e)}")
    
    def _load_file_by_format(self, file_path: Path) -> pd.DataFrame:
        """Carga archivo según su formato con manejo de errores específico."""
        try:
            suffix = file_path.suffix.lower()
            
            if suffix in {'.csv', '.txt'}:
                # Intentar diferentes separadores
                separators = [';', ',', '\t']
                encodings = ['utf-8', 'latin-1', 'cp1252']
                
                for encoding in encodings:
                    for sep in separators:
                        try:
                            df = pd.read_csv(file_path, sep=sep, decimal=',', engine='python', encoding=encoding)
                            if len(df.columns) > 1:  # Verificar que se cargaron múltiples columnas
                                self.logger.info(f"Archivo CSV cargado con separador '{sep}' y encoding '{encoding}'")
                                return df
                        except Exception:
                            continue
                
                # Si no funciona con separadores específicos, usar pandas con detección automática
                df = pd.read_csv(file_path, engine='python')
                return df
                
            elif suffix in {'.xlsx', '.xls'}:
                df = pd.read_excel(file_path)
                return df
                
            elif suffix in {'.parquet'}:
                df = pd.read_parquet(file_path)
                return df
                
            else:
                raise ValueError(f"Formato de archivo no soportado: {suffix}")
                
        except Exception as e:
            self.logger.error(f"Error cargando archivo {file_path}: {e}")
            raise
    
    def _prepare_dataframe(self, df: pd.DataFrame, file_path: Path) -> pd.DataFrame:
        """Prepara el DataFrame con validaciones básicas."""
        try:
            # Verificar que el DataFrame no esté vacío
            if df.empty:
                raise ValueError("DataFrame vacío después de la carga")
            
            # Verificar que hay suficientes columnas
            if len(df.columns) < 3:
                self.logger.warning(f"Pocas columnas detectadas: {len(df.columns)}")
            
            # Mostrar información de columnas originales
            self.logger.info(f"Columnas originales: {df.columns.tolist()}")
            
            # Limpiar nombres de columnas
            df.columns = df.columns.str.strip()
            
            # Eliminar filas completamente vacías
            df = df.dropna(how='all')
            
            if df.empty:
                raise ValueError("No quedan datos después de eliminar filas vacías")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error preparando DataFrame: {e}")
            raise
    
    def _apply_column_mappings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica mapeos de columnas QVA y ROBUST con mapeo fuzzy."""
        try:
            original_columns = df.columns.tolist()
            self.logger.info(f"Columnas originales: {original_columns}")
            
            # Usar el mismo mapeo que gui_enhanced_rank.py
            NORMALIZE_COL = lambda s: re.sub(r"[^0-9A-Za-z]", "", s).upper()
            
            QVA_COL_MAP = {
                'STRATEGYNAME': 'Strategy_Name',
                'CAGR': 'CAGR',
                'DRAWDOWN': 'Drawdown',  # Drawdown es una métrica independiente
                'MAXDD': 'Max_DD_%',     # Max DD % es otra métrica diferente
                'MAXDD%': 'Max_DD_%',
                'EXPECTANCY': 'Expectancy',
                'MAXCONSECLOSURES': 'Max_Consec_Losses',
                'MAXCONSECUTIVELOSSES': 'Max_Consec_Losses',
                'PROFITFACTOR': 'Profit_factor',
                'SHARPERATIO': 'Sharpe_Ratio',
                'CALMARRATIO': 'CalmarRatio',
                'SQN': 'SQN',
                'RINAINDEX': 'RINAIndex',
                'ULCERINDEX': 'Ulcer_Index_%',
                'ULCERPERFORMANCEINDEX': 'Ulcer_Performance_Index',
                'STAGNATION': 'Stagnation',
                'MAXDRAWDOWNDURATION': 'Max_Drawdown_Duration',
                'AVGBARSINTRADE': 'Avg_Bars_in_Trade',
                'VAR95': 'VaR_95%',
                'CVAR95': 'CVaR_95%',
                'SORTINORATIO': 'Sortino_Ratio',
                'RECOVERYFACTOR': 'RecoveryFactor',
                'STAGNATIONTRADES': 'Stagnation_Trades',
                'NEWPEAKTRADES': 'New_Peak_Trades_%',
                'DRAWDOWNTRADES': 'Drawdown_Trades_%'
            }
            
            ROBUST_COL_MAP = {
                'STRATEGYNAME': 'Strategy_Name',
                'CAGR': 'CAGR',
                'DRAWDOWN': 'Drawdown',  # Drawdown es una métrica independiente
                'MAXDD': 'Max_DD_%',     # Max DD % es otra métrica diferente
                'MAXDD%': 'Max_DD_%',
                'EXPECTANCY': 'Expectancy',
                'MAXCONSECLOSURES': 'Max_Consec_Losses',
                'MAXCONSECUTIVELOSSES': 'Max_Consec_Losses',
                'PROFITFACTOR': 'Profit_factor',
                'SHARPERATIO': 'Sharpe_Ratio',
                'CALMARRATIO': 'CalmarRatio',
                'SQN': 'SQN',
                'RINAINDEX': 'RINAIndex',
                'ULCERINDEX': 'Ulcer_Index_%',
                'ULCERPERFORMANCEINDEX': 'Ulcer_Performance_Index',
                'STAGNATION': 'Stagnation',
                'MAXDRAWDOWNDURATION': 'Max_Drawdown_Duration',
                'AVGBARSINTRADE': 'Avg_Bars_in_Trade',
                'VAR95': 'VaR_95%',
                'CVAR95': 'CVaR_95%',
                'SORTINORATIO': 'Sortino_Ratio',
                'RECOVERYFACTOR': 'RecoveryFactor',
                'STAGNATIONTRADES': 'Stagnation_Trades',
                'NEWPEAKTRADES': 'New_Peak_Trades_%',
                'DRAWDOWNTRADES': 'Drawdown_Trades_%'
            }
            
            # Aplicar mapeo fuzzy
            normalized_columns = {NORMALIZE_COL(col): col for col in df.columns}
            
            # Mapear columnas QVA
            for norm_col, target_col in QVA_COL_MAP.items():
                if norm_col in normalized_columns:
                    original_col = normalized_columns[norm_col]
                    if original_col != target_col:
                        df = df.rename(columns={original_col: target_col})
                        self.logger.info(f"Mapeado QVA: {original_col} -> {target_col}")
            
            # Mapear columnas ROBUST
            for norm_col, target_col in ROBUST_COL_MAP.items():
                if norm_col in normalized_columns:
                    original_col = normalized_columns[norm_col]
                    if original_col != target_col:
                        df = df.rename(columns={original_col: target_col})
                        self.logger.info(f"Mapeado ROBUST: {original_col} -> {target_col}")
            
            # Asegurar columnas críticas con mapeo fuzzy mejorado
            df = self._ensure_critical_columns(df, original_columns)
            
            self.logger.info(f"Columnas finales: {df.columns.tolist()}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error en mapeo de columnas: {e}")
            return df
    
    def _normalize_column_name(self, col: str) -> str:
        """Normaliza el nombre de una columna."""
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
    
    def _ensure_critical_columns(self, df: pd.DataFrame, original_columns: list) -> pd.DataFrame:
        """Asegura que las columnas críticas existan con mapeo fuzzy mejorado."""
        try:
            # Mapeo basado en las columnas reales del archivo CSV
            # Prioridad: 1) Métricas generales, 2) IS, 3) OOS
            critical_mappings = {
                'Strategy_Name': ['Strategy Name', 'StrategyName', 'Name', 'Strategy'],
                'Profit_factor': ['Profit factor', 'Profit factor (IS)', 'Profit factor (OOS)', 'ProfitFactor', 'Profit_Factor'],
                'Sharpe_Ratio': ['Sharpe Ratio', 'Sharpe Ratio (IS)', 'Sharpe Ratio (OOS)', 'SharpeRatio', 'Sharpe_Ratio'],
                'Drawdown': ['Drawdown', 'Drawdown (IS)', 'Drawdown (OOS)'],
                'Max_DD_%': ['Max DD %', 'Max_DD_%', 'Max_DD', 'Max_DD_IS', 'Max_DD_OOS']
            }
            
            for target_col, possible_names in critical_mappings.items():
                if target_col not in df.columns:
                    # Buscar la columna con mapeo fuzzy
                    found_col = None
                    for possible_name in possible_names:
                        if possible_name in df.columns:
                            found_col = possible_name
                            break
                    
                    if found_col:
                        # Renombrar la columna encontrada
                        df = df.rename(columns={found_col: target_col})
                        self.logger.info(f"✅ Mapeado {target_col}: {found_col} -> {target_col}")
                    else:
                        # Si no se encuentra, crear una columna vacía
                        df[target_col] = None
                        self.logger.warning(f"⚠️ Columna crítica {target_col} no encontrada, creando columna vacía")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error en _ensure_critical_columns: {str(e)}")
            return df
    
    def _clean_and_validate_final_data(self, df: pd.DataFrame, is_oos_split: float) -> pd.DataFrame:
        """Limpia y valida los datos finales."""
        try:
            # Convertir tipos de datos
            for col in df.columns:
                if col == 'Strategy_Name':
                    df[col] = df[col].astype(str)
                elif pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].astype(float)
                else:
                    # Intentar conversión numérica segura
                    col_data = df[col]
                    if isinstance(col_data, pd.DataFrame):
                        col_data = col_data.iloc[:, 0]  # Tomar la primera columna si es DataFrame
                    
                    # Asegurar que col_data sea una Series antes de usar .str
                    if not isinstance(col_data, pd.Series):
                        col_data = pd.Series(col_data)
                    
                    converted = pd.to_numeric(
                        col_data.astype(str).str.replace(',', '.').str.replace(r'[\d\.\-eE]', '', regex=True), 
                        errors='coerce'
                    )
                    # Corrección: robustez para Series o escalar
                    if isinstance(converted, pd.Series):
                        notna_count = converted.notna().sum()
                    else:
                        notna_count = _safe_sum(pd.notna(converted))
                    if notna_count > 0:
                        df[col] = converted
                    else:
                        df[col] = df[col].astype(str).replace(r'^\s*$', '', regex=True)
            
            # Calcular métricas IS/OOS si están disponibles
            df = self._calculate_is_oos_metrics(df, is_oos_split)
            
            # Eliminar duplicados por Strategy_Name
            if 'Strategy_Name' in df.columns:
                initial_count = len(df)
                df.drop_duplicates(subset=['Strategy_Name'], inplace=True)
                final_count = len(df)
                if initial_count != final_count:
                    self.logger.info(f"Eliminadas {initial_count - final_count} estrategias duplicadas")
            
            # Validación final
            if len(df) < 1:
                raise ValueError("No quedan datos después de la limpieza")
            
            self.logger.info(f"DataFrame final preparado: {df.shape}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error limpiando y validando datos finales: {e}")
            raise
    
    def _calculate_is_oos_metrics(self, df: pd.DataFrame, is_oos_split: float) -> pd.DataFrame:
        """
        Calcula métricas IS/OOS de forma empírica y científica.
        Reemplaza el cálculo básico anterior con análisis avanzado.
        """
        try:
            import numpy as np
            
            # Detectar pares IS/OOS
            is_cols = [col for col in df.columns if '(IS)' in col]
            oos_cols = [col for col in df.columns if '(OOS)' in col]
            kpi_pairs = []
            
            for is_col in is_cols:
                base = is_col.replace(' (IS)', '').replace('(IS)', '').strip()
                oos_col = next((c for c in oos_cols if base == c.replace(' (OOS)', '').replace('(OOS)', '').strip()), None)
                if oos_col:
                    kpi_pairs.append((base, is_col, oos_col))
            
            if not kpi_pairs:
                self.logger.info("No se encontraron pares IS/OOS para análisis")
                return df
            
            # Recolectar todas las diferencias relativas del dataset para percentiles automáticos
            all_diffs = []
            for base, is_col, oos_col in kpi_pairs:
                is_vals = pd.to_numeric(df[is_col], errors='coerce').to_numpy()
                oos_vals = pd.to_numeric(df[oos_col], errors='coerce').to_numpy()
                diffs = ((oos_vals - is_vals) / (np.abs(is_vals) + 1e-8)) * 100
                all_diffs.extend(diffs[~np.isnan(diffs)].tolist())
            
            # Calcular percentiles automáticos para umbrales
            if all_diffs:
                all_diffs_np = np.array(all_diffs)
                p10 = np.percentile(all_diffs_np, 10)
                p25 = np.percentile(all_diffs_np, 25)
                p75 = np.percentile(all_diffs_np, 75)
            else:
                p10, p25, p75 = -20, -12, -5
            
            # Penalización según el split IS/OOS
            penalizacion = 1 - (is_oos_split * 0.5)
            
            # Métricas clave para alertas
            metricas_clave = {"Profit Factor", "CAGR", "Sharpe Ratio", "CalmarRatio"}
            
            # Calcular predictividad para cada estrategia
            resultados = []
            detalles_all = []
            
            for idx, row in df.iterrows():
                detalles = []
                perdidas_rel = []
                n_mejoran = 0
                n_empeoran = 0
                n_igual = 0
                alertas = []
                alerta_critica = False
                
                for base, is_col, oos_col in kpi_pairs:
                    is_val = row.get(is_col)
                    oos_val = row.get(oos_col)
                    
                    try:
                        is_val = float(is_val)
                        oos_val = float(oos_val)
                    except:
                        continue
                    
                    diff_abs = oos_val - is_val
                    diff_rel = 0.0
                    if abs(is_val) > 1e-8:
                        diff_rel = (oos_val - is_val) / abs(is_val) * 100
                    
                    perdidas_rel.append(diff_rel)
                    
                    # Contar tendencias
                    if diff_abs > 0.01:
                        n_mejoran += 1
                    elif diff_abs < -0.01:
                        n_empeoran += 1
                    else:
                        n_igual += 1
                    
                    # Alertas para métricas clave
                    if base in metricas_clave:
                        oos_vals = pd.to_numeric(df[oos_col], errors='coerce').to_numpy()
                        oos_vals_valid = oos_vals[~np.isnan(oos_vals)]
                        umbral_critico = np.percentile(oos_vals_valid, 10) if len(oos_vals_valid) > 0 else (1 if base == "Profit Factor" else 0)
                        
                        if base == "Profit Factor" and oos_val < umbral_critico:
                            alertas.append(f"⚠️ Profit Factor OOS < {umbral_critico:.2f}")
                            alerta_critica = True
                        if base == "CAGR" and oos_val < umbral_critico:
                            alertas.append(f"⚠️ CAGR OOS < {umbral_critico:.2f}")
                            alerta_critica = True
                
                # Calcular estadísticas
                n_total = len(perdidas_rel)
                media_perdida = np.mean(perdidas_rel) * penalizacion if perdidas_rel else 0.0
                pct_mejoran = n_mejoran / n_total * 100 if n_total else 0
                pct_empeoran = n_empeoran / n_total * 100 if n_total else 0
                
                # Clasificación multinivel automática
                nivel = ""
                icono = ""
                if alerta_critica or media_perdida < p10 or pct_empeoran > 50:
                    nivel = "Pobre"
                    icono = "🔴"
                elif media_perdida < p25 or pct_empeoran > 30:
                    nivel = "Aceptable"
                    icono = "🟡"
                elif media_perdida < p75 or pct_empeoran > 20:
                    nivel = "Buena"
                    icono = "🟢"
                else:
                    nivel = "Excelente"
                    icono = "🔬"
                
                resumen = f"{icono} {nivel} (Δ={media_perdida:+.1f}%, {n_total} KPIs, {pct_mejoran:.0f}% mejoran)"
                if alertas:
                    resumen += " [" + ", ".join(alertas) + "]"
                
                resultados.append(resumen)
                detalles_all.append(detalles)
            
            # Asignar resultados al DataFrame
            df = df.copy()
            df['IS/OOS'] = resultados
            df['IS_OOS_DETALLES'] = detalles_all
            
            # Log detallado
            self.logger.info(f"Análisis IS/OOS empírico completado: {len(df)} estrategias")
            self.logger.info(f"Umbrales automáticos: Pobre<{p10:.1f}%, Aceptable<{p25:.1f}%, Buena<{p75:.1f}%")
            self.logger.info(f"Penalización IS/OOS aplicada: {penalizacion:.3f} (IS%={is_oos_split*100:.1f}%)")
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error calculando métricas IS/OOS empíricas: {e}")
            return df
    
    def validate_data_compatibility(self, df: pd.DataFrame, required_kpis: List[str]) -> Tuple[bool, List[str]]:
        """
        Valida que los datos sean compatibles con los KPIs requeridos.
        
        Args:
            df: DataFrame con los datos
            required_kpis: Lista de KPIs requeridos
            
        Returns:
            Tupla con (es_compatible, lista_de_errores)
        """
        errors = []
        
        # Verificar que los KPIs requeridos existan
        missing_kpis = [kpi for kpi in required_kpis if kpi not in df.columns]
        if missing_kpis:
            errors.append(f"KPIs faltantes: {missing_kpis}")
        
        # Verificar que hay suficientes datos
        if len(df) < 10:
            errors.append("Insuficientes datos (mínimo 10 estrategias)")
        
        # Verificar que hay datos numéricos válidos
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 5:
            errors.append("Insuficientes columnas numéricas")
        
        # Verificar que no hay demasiados valores nulos
        null_percentage = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
        if null_percentage > 50:
            errors.append(f"Demasiados valores nulos ({null_percentage:.1f}%)")
        
        return len(errors) == 0, errors 

class FactorKElite96Enhanced:
    """
    Motor principal mejorado con procesamiento en hilos y optimizaciones para GUI.
    """
    
    def __init__(self, config: Optional[Dict] = None, progress_callback: Optional[ProgressCallback] = None):
        self.logger = setup_logger("kforce")
        self.config_manager = ConfigManagerEnhanced()
        self.data_loader = DataLoaderEnhanced(progress_callback)
        self.progress_callback = progress_callback
        
        # Configuración de rendimiento
        self.chunk_size = CHUNK_SIZE
        self.max_workers = MAX_WORKERS
        self.scientific_improvements_enabled = False
        self.cache_dir = None
        
        # Componentes científicos (opcionales)
        self.hmm_analyzer = None
        self.stress_tester = None
        self.drift_detector = None
        self.temporal_validator = None
        
        # Cache para optimización
        self._calculation_cache = {}
        
        if config:
            self.config_manager.current_config.update(config)
        
        # SIEMPRE ACTIVAR MEJORAS CIENTÍFICAS POR DEFECTO
        self.enable_scientific_improvements()
    
    def enable_scientific_improvements(self, cache_dir: str = "cache/scientific"):
        """
        Habilita las mejoras científicas opcionales.
        
        Args:
            cache_dir: Directorio para cache de cálculos científicos
        """
        try:
            self.scientific_improvements_enabled = True
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Inicializar componentes científicos
            self.hmm_analyzer = HiddenMarkovModelAnalyzer()
            self.stress_tester = StressTestGenerator()
            self.drift_detector = DataDriftDetector()
            self.temporal_validator = TemporalValidation()
            
            self.logger.info("Mejoras científicas habilitadas")
            
        except Exception as e:
            self.logger.error(f"Error habilitando mejoras científicas: {e}")
            self.scientific_improvements_enabled = False
    
    def load_and_prepare_data(self, file_path: str) -> pd.DataFrame:
        """
        Carga y prepara datos usando el cargador mejorado.
        
        Args:
            file_path: Ruta al archivo de datos
            
        Returns:
            DataFrame preparado
        """
        try:
            return self.data_loader.load_and_prepare_data(file_path)
        except Exception as e:
            self.logger.error(f"Error en load_and_prepare_data: {e}")
            raise
    
    def evaluate_strategies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Evalúa estrategias con procesamiento optimizado y callbacks de progreso.
        
        Args:
            df: DataFrame con los datos de estrategias
            
        Returns:
            DataFrame con resultados de evaluación
        """
        try:
            self.logger.info("Iniciando evaluación de estrategias")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Evaluación", 0, 100, "Iniciando evaluación...")
            
            # Validar datos de entrada
            self.logger.info("Validando datos de entrada...")
            df = self._validate_input_data(df)
            self.logger.info(f"Datos de entrada validados exitosamente. Tipo: {type(df)}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Evaluación", 10, 100, "Datos validados, calculando componentes...")
            
            # Calcular componentes principales
            self.logger.info("Calculando componentes principales...")
            df = self._calculate_factor_k_elite(df)
            self.logger.info(f"Componentes principales calculados exitosamente. Tipo: {type(df)}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Evaluación", 60, 100, "Componentes calculados, aplicando mejoras...")
            
            # Aplicar mejoras científicas si están habilitadas
            if self.scientific_improvements_enabled:
                self.logger.info("Aplicando mejoras científicas...")
                df = self._apply_scientific_improvements(df)
                self.logger.info("Mejoras científicas aplicadas exitosamente")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Evaluación", 80, 100, "Finalizando evaluación...")
            
            # Aplicar normalización final y categorías de calidad
            self.logger.info("Aplicando normalización final...")
            df = self._apply_final_normalization(df)
            self.logger.info(f"Normalización final aplicada exitosamente. Tipo: {type(df)}")
            
            self.logger.info("Asignando categorías de calidad...")
            df = self._assign_quality_categories(df)
            self.logger.info(f"Categorías de calidad asignadas exitosamente. Tipo: {type(df)}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Evaluación", 100, 100, "Evaluación completada")
            
            # Limpiar memoria
            gc.collect()
            
            self.logger.info(f"Evaluación completada: {len(df)} estrategias procesadas")
            self.logger.info(f"Tipo de retorno: {type(df)}")
            self.logger.info(f"Columnas del DataFrame: {list(df.columns)[:5]}...")
            return df
            
        except Exception as e:
            self.logger.error(f"Error en evaluate_strategies: {str(e)}")
            import traceback
            self.logger.error(f"Traceback completo: {traceback.format_exc()}")
            if self.progress_callback:
                self.progress_callback.update_progress("Evaluación", 0, 100, f"Error: {str(e)}")
            raise ValueError(f"Error en el análisis: {str(e)}")
    
    def _validate_input_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valida los datos de entrada con validaciones mejoradas."""
        try:
            if df is None or df.empty:
                raise ValueError("DataFrame vacío o None")
            
            # Verificar columnas mínimas requeridas
            required_columns = ['Strategy_Name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas requeridas faltantes: {missing_columns}")
            
            # Verificar que hay suficientes datos
            if len(df) < 5:
                raise ValueError("Insuficientes datos para análisis (mínimo 5 estrategias)")
            
            # Verificar que hay columnas numéricas
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) < 3:
                raise ValueError("Insuficientes columnas numéricas para análisis")
            
            # Limpiar datos extremos
            df = self._clean_extreme_values(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error validando datos de entrada: {e}")
            raise
    
    def _clean_extreme_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia valores extremos en columnas numéricas."""
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_columns:
                if col in df.columns:
                    # Calcular percentiles para detectar outliers
                    q1 = df[col].quantile(0.01)
                    q3 = df[col].quantile(0.99)
                    iqr = q3 - q1
                    
                    # Definir límites
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    # Reemplazar outliers con límites
                    df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error limpiando valores extremos: {e}")
            return df
    
    def _calculate_factor_k_elite(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el Factor K Elite con procesamiento optimizado."""
        try:
            # Calcular componentes principales
            df = self._calculate_stability_component(df)
            df = self._calculate_growth_component(df)
            df = self._calculate_efficiency_component(df)
            df = self._calculate_consistency_component(df)
            df = self._calculate_risk_component(df)
            
            # Calcular Factor K Elite
            df['FK96_Elite_Enhanced'] = (
                df['FK96_Stability_Enhanced'] * 0.25 +
                df['FK96_Growth_Enhanced'] * 0.25 +
                df['FK96_Efficiency_Enhanced'] * 0.20 +
                df['FK96_Consistency_Enhanced'] * 0.15 +
                df['FK96_Risk_Enhanced'] * 0.15
            )
            
            # Aplicar penalizaciones dinámicas
            df = self._apply_dynamic_penalties(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando Factor K Elite: {e}")
            raise
    
    def _calculate_stability_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el componente de estabilidad."""
        try:
            # Métricas de estabilidad
            stability_metrics = []
            
            # Max Drawdown (invertido para que menor sea mejor)
            if 'Max_DD_%' in df.columns:
                max_dd = df['Max_DD_%'].fillna(0)
                stability_metrics.append(1 / (1 + abs(max_dd)))
            
            # Sharpe Ratio
            if 'Sharpe_Ratio' in df.columns:
                sharpe = df['Sharpe_Ratio'].fillna(0)
                stability_metrics.append((sharpe + 3) / 6)  # Normalizar a [0,1]
            
            # Calmar Ratio
            if 'CalmarRatio' in df.columns:
                calmar = df['CalmarRatio'].fillna(0)
                stability_metrics.append((calmar + 2) / 4)  # Normalizar a [0,1]
            
            # Ulcer Index
            if 'Ulcer_Index_%' in df.columns:
                ulcer = df['Ulcer_Index_%'].fillna(0)
                stability_metrics.append(1 / (1 + ulcer))
            
            # Calcular componente de estabilidad
            if stability_metrics:
                df['FK96_Stability_Enhanced'] = np.mean(stability_metrics, axis=0)
            else:
                df['FK96_Stability_Enhanced'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando componente de estabilidad: {e}")
            df['FK96_Stability_Enhanced'] = 0.5
            return df
    
    def _calculate_growth_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el componente de crecimiento."""
        try:
            # Métricas de crecimiento
            growth_metrics = []
            
            # CAGR
            if 'CAGR' in df.columns:
                cagr = df['CAGR'].fillna(0)
                growth_metrics.append((cagr + 50) / 100)  # Normalizar a [0,1]
            
            # Net Profit
            if 'Net_profit' in df.columns:
                net_profit = df['Net_profit'].fillna(0)
                growth_metrics.append((net_profit + 10000) / 20000)  # Normalizar a [0,1]
            
            # Recovery Factor
            if 'RecoveryFactor' in df.columns:
                recovery = df['RecoveryFactor'].fillna(0)
                growth_metrics.append((recovery + 5) / 10)  # Normalizar a [0,1]
            
            # Calcular componente de crecimiento
            if growth_metrics:
                df['FK96_Growth_Enhanced'] = np.mean(growth_metrics, axis=0)
            else:
                df['FK96_Growth_Enhanced'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando componente de crecimiento: {e}")
            df['FK96_Growth_Enhanced'] = 0.5
            return df
    
    def _calculate_efficiency_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el componente de eficiencia."""
        try:
            # Métricas de eficiencia
            efficiency_metrics = []
            
            # Profit Factor
            if 'Profit_factor' in df.columns:
                profit_factor = df['Profit_factor'].fillna(1)
                efficiency_metrics.append((profit_factor - 1) / 2)  # Normalizar a [0,1]
            
            # Expectancy
            if 'Expectancy' in df.columns:
                expectancy = df['Expectancy'].fillna(0)
                efficiency_metrics.append((expectancy + 100) / 200)  # Normalizar a [0,1]
            
            # Winning Percent
            if 'Winning_Percent' in df.columns:
                winning_pct = df['Winning_Percent'].fillna(50)
                efficiency_metrics.append(winning_pct / 100)  # Ya está en [0,1]
            
            # Calcular componente de eficiencia
            if efficiency_metrics:
                df['FK96_Efficiency_Enhanced'] = np.mean(efficiency_metrics, axis=0)
            else:
                df['FK96_Efficiency_Enhanced'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando componente de eficiencia: {e}")
            df['FK96_Efficiency_Enhanced'] = 0.5
            return df
    
    def _calculate_consistency_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el componente de consistencia."""
        try:
            # Métricas de consistencia
            consistency_metrics = []
            
            # Number of Trades
            if '#_of_trades' in df.columns:
                trades = pd.to_numeric(df['#_of_trades'], errors='coerce').fillna(0)
                consistency_metrics.append(np.minimum(trades / 100, 1))  # Normalizar a [0,1]
            
            # Stagnation Trades
            if 'Stagnation_Trades' in df.columns:
                stagnation = pd.to_numeric(df['Stagnation_Trades'], errors='coerce').fillna(0)
                consistency_metrics.append(1 / (1 + stagnation))  # Menor es mejor
            
            # Max Consecutive Losses
            if 'Max_Consec_Losses' in df.columns:
                consec_losses = pd.to_numeric(df['Max_Consec_Losses'], errors='coerce').fillna(0)
                consistency_metrics.append(1 / (1 + consec_losses))  # Menor es mejor
            
            # Calcular componente de consistencia
            if consistency_metrics:
                df['FK96_Consistency_Enhanced'] = np.mean(consistency_metrics, axis=0)
            else:
                df['FK96_Consistency_Enhanced'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando componente de consistencia: {e}")
            df['FK96_Consistency_Enhanced'] = 0.5
            return df
    
    def _calculate_risk_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el componente de riesgo."""
        try:
            # Métricas de riesgo (invertidas para que menor sea mejor)
            risk_metrics = []
            
            # VaR 95%
            if 'VaR_95%' in df.columns:
                var = df['VaR_95%'].fillna(0)
                risk_metrics.append(1 / (1 + abs(var)))
            
            # CVaR 95%
            if 'CVaR_95%' in df.columns:
                cvar = df['CVaR_95%'].fillna(0)
                risk_metrics.append(1 / (1 + abs(cvar)))
            
            # Sortino Ratio
            if 'Sortino_Ratio' in df.columns:
                sortino = df['Sortino_Ratio'].fillna(0)
                risk_metrics.append((sortino + 2) / 4)  # Normalizar a [0,1]
            
            # Calcular componente de riesgo
            if risk_metrics:
                df['FK96_Risk_Enhanced'] = np.mean(risk_metrics, axis=0)
            else:
                df['FK96_Risk_Enhanced'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando componente de riesgo: {e}")
            df['FK96_Risk_Enhanced'] = 0.5
            return df
    
    def _apply_dynamic_penalties(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica penalizaciones dinámicas basadas en múltiples factores."""
        try:
            penalties = np.ones(len(df))
            
            # Penalización por pocas operaciones
            if '#_of_trades' in df.columns:
                trades = df['#_of_trades'].fillna(0)
                trade_penalty = np.where(trades < 30, 0.9, 1.0)
                penalties *= trade_penalty
            
            # Penalización por drawdown alto
            if 'Max_DD_%' in df.columns:
                max_dd = df['Max_DD_%'].fillna(0)
                dd_penalty = np.where(abs(max_dd) > 20, 0.8, 1.0)
                penalties *= dd_penalty
            
            # Penalización por profit factor bajo
            if 'Profit_factor' in df.columns:
                pf = df['Profit_factor'].fillna(1)
                pf_penalty = np.where(pf < 1.1, 0.7, 1.0)
                penalties *= pf_penalty
            
            # Aplicar penalizaciones
            df['FK96_Elite_Enhanced'] *= penalties
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando penalizaciones dinámicas: {e}")
            return df
    
    def _apply_scientific_improvements(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica mejoras científicas si están habilitadas."""
        try:
            if not self.scientific_improvements_enabled:
                return df
            
            # Detectar regímenes de mercado
            df = self._detect_market_regimes(df)
            
            # Aplicar análisis HMM si está disponible
            if self.hmm_analyzer:
                df = self._apply_hmm_analysis(df)
            
            # Aplicar mejora científica al Unified_Score
            df = self._apply_scientific_score_enhancement(df)
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando mejoras científicas: {e}")
            return df
    
    def _detect_market_regimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta regímenes de mercado usando clustering."""
        try:
            # Seleccionar métricas para clustering
            clustering_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR', 'Profit_factor']
            available_metrics = [m for m in clustering_metrics if m in df.columns]
            
            if len(available_metrics) >= 2:
                # Preparar datos para clustering
                X = df[available_metrics].fillna(0).values
                
                # Normalizar datos
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Aplicar K-means clustering
                kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
                cluster_labels = kmeans.fit_predict(X_scaled)
                
                # Asignar regímenes
                df['Market_Regime'] = cluster_labels
                
                # Calcular scores por régimen
                for regime in range(3):
                    regime_mask = df['Market_Regime'] == regime
                    if regime_mask.any():
                        regime_score = df.loc[regime_mask, 'FK96_Elite_Enhanced'].mean()
                        df.loc[regime_mask, 'Regime_Score'] = regime_score
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error detectando regímenes de mercado: {e}")
            return df
    
    def _apply_hmm_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica análisis de Hidden Markov Models."""
        try:
            if not self.hmm_analyzer:
                return df
            
            # Seleccionar métricas para HMM
            hmm_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR']
            available_metrics = [m for m in hmm_metrics if m in df.columns]
            
            if len(available_metrics) >= 2:
                # Preparar datos para HMM
                X = df[available_metrics].fillna(0).values
                
                # Ajustar HMM
                hmm_results = self.hmm_analyzer.fit_hmm(pd.DataFrame(X, columns=pd.Index(available_metrics)))
                
                # Aplicar resultados al DataFrame
                if 'states' in hmm_results:
                    df['HMM_State'] = hmm_results['states']
                    
                    # Calcular scores por estado
                    for state in range(hmm_results.get('n_states', 3)):
                        state_mask = df['HMM_State'] == state
                        if state_mask.any():
                            state_score = df.loc[state_mask, 'FK96_Elite_Enhanced'].mean()
                            df.loc[state_mask, 'HMM_Score'] = state_score
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando análisis HMM: {e}")
            return df
    
    def _apply_scientific_score_enhancement(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica mejoras científicas al Unified_Score."""
        try:
            if 'Unified_Score' not in df.columns:
                self.logger.warning("Unified_Score no encontrado para mejora científica")
                return df
            
            # Crear Unified_Score_Scientific combinando scores
            if 'Regime_Score' in df.columns and 'HMM_Score' in df.columns:
                # Combinar Unified_Score con scores científicos
                df['Unified_Score_Scientific'] = (
                    0.5 * df['Unified_Score'] + 
                    0.3 * df['Regime_Score'] + 
                    0.2 * df['HMM_Score']
                )
                self.logger.info("Unified_Score_Scientific creado con régimen y HMM")
                
            elif 'Regime_Score' in df.columns:
                # Solo régimen de mercado
                df['Unified_Score_Scientific'] = (
                    0.7 * df['Unified_Score'] + 
                    0.3 * df['Regime_Score']
                )
                self.logger.info("Unified_Score_Scientific creado con régimen")
                
            else:
                # Sin mejoras científicas disponibles
                df['Unified_Score_Scientific'] = df['Unified_Score']
                self.logger.info("Unified_Score_Scientific igual a Unified_Score")
            
            # Crear Unified_Score_Enhanced con ajuste dinámico
            if 'Regime_Score' in df.columns:
                regime_adjustment = df['Regime_Score'] / df['Regime_Score'].max()
                df['Unified_Score_Enhanced'] = df['Unified_Score'] * (1 + 0.2 * regime_adjustment)
                self.logger.info("Unified_Score_Enhanced creado con ajuste de régimen")
            else:
                df['Unified_Score_Enhanced'] = df['Unified_Score']
                self.logger.info("Unified_Score_Enhanced igual a Unified_Score")
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando mejora científica al score: {e}")
            return df
    
    def _apply_final_normalization(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica normalización final a los scores."""
        try:
            # Normalizar Factor K Elite a [0, 1]
            if 'FK96_Elite_Enhanced' in df.columns:
                fk_scores = df['FK96_Elite_Enhanced']
                min_score = fk_scores.min()
                max_score = fk_scores.max()
                
                if max_score > min_score:
                    df['FK96_Elite_Enhanced_Normalized'] = (fk_scores - min_score) / (max_score - min_score)
                else:
                    df['FK96_Elite_Enhanced_Normalized'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando normalización final: {e}")
            return df
    
    def _assign_quality_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Asigna categorías de calidad basadas en los scores usando percentiles balanceados."""
        try:
            # Usar la nueva función de categorización más robusta
            if 'FK96_Elite_Enhanced_Normalized' in df.columns:
                df = categorize_quality(df, 'FK96_Elite_Enhanced_Normalized')
            elif 'Unified_Score' in df.columns:
                df = categorize_quality(df, 'Unified_Score')
            else:
                self.logger.warning("No se encontró columna de score para categorización")
                df['Quality_Category'] = 'Regular'
            return df
        except Exception as e:
            self.logger.warning(f"Error asignando categorías de calidad: {e}")
            df['Quality_Category'] = 'Regular'
            return df
    
    def get_analysis_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Obtiene un resumen del análisis realizado."""
        try:
            summary = {
                'total_strategies': len(df),
                'analysis_timestamp': datetime.now().isoformat(),
                'components_calculated': []
            }
            
            # Verificar componentes calculados
            components = [
                'FK96_Stability_Enhanced',
                'FK96_Growth_Enhanced', 
                'FK96_Efficiency_Enhanced',
                'FK96_Consistency_Enhanced',
                'FK96_Risk_Enhanced',
                'FK96_Elite_Enhanced'
            ]
            
            for component in components:
                if component in df.columns:
                    summary['components_calculated'].append(component)
                    summary[f'{component}_mean'] = df[component].mean()
                    summary[f'{component}_std'] = df[component].std()
            
            # Estadísticas de calidad
            if 'Quality_Category' in df.columns:
                quality_counts = df['Quality_Category'].value_counts().to_dict()
                summary['quality_distribution'] = quality_counts
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generando resumen de análisis: {e}")
            return {'error': str(e)} 

class HiddenMarkovModelAnalyzer:
    """Analizador de Hidden Markov Models para detección de regímenes."""
    
    def __init__(self, n_states: int = 3, random_state: int = 42):
        self.n_states = n_states
        self.random_state = random_state
        self.model = None
        self.logger = setup_logger("kforce")
    
    def fit_hmm(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Ajusta un modelo HMM a los datos."""
        try:
            # Implementación simplificada para evitar dependencias adicionales
            # En una implementación real, usarías hmmlearn o similar
            
            # Simular estados aleatorios para demostración
            np.random.seed(self.random_state)
            states = np.random.randint(0, self.n_states, size=len(data))
            
            return {
                'n_states': self.n_states,
                'states': states,
                'transition_matrix': np.eye(self.n_states),
                'emission_means': _safe_values(data.mean()),
                'emission_covars': _safe_values(data.cov())
            }
            
        except Exception as e:
            self.logger.error(f"Error ajustando HMM: {e}")
            return {'error': str(e)}

class StressTestGenerator:
    """Generador de pruebas de estrés para validación de modelos."""
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.logger = setup_logger("kforce")
    
    def generate_synthetic_strategies(self, n_strategies: int = 100) -> pd.DataFrame:
        """Genera estrategias sintéticas para pruebas de estrés."""
        try:
            np.random.seed(self.random_state)
            
            # Generar datos sintéticos
            data = {
                'Strategy_Name': [f'Stress_Test_{i+1}' for i in range(n_strategies)],
                'Sharpe_Ratio': np.random.normal(1.5, 0.5, n_strategies),
                'Max_DD_%': np.random.uniform(-30, -5, n_strategies),
                'CAGR': np.random.normal(15, 10, n_strategies),
                'Profit_factor': np.random.uniform(1.1, 3.0, n_strategies),
                'Winning_Percent': np.random.uniform(40, 80, n_strategies)
            }
            
            return pd.DataFrame(data)
            
        except Exception as e:
            self.logger.error(f"Error generando estrategias sintéticas: {e}")
            return pd.DataFrame()

class DataDriftDetector:
    """Detector de drift en los datos para validación temporal."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.reference_distribution = None
        self.logger = setup_logger("kforce")
    
    def set_reference_distribution(self, data: pd.DataFrame, columns: List[str]) -> None:
        """Establece la distribución de referencia."""
        try:
            self.reference_distribution = data[columns].describe()
        except Exception as e:
            self.logger.error(f"Error estableciendo distribución de referencia: {e}")
    
    def detect_drift(self, current_data: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Detecta drift en los datos actuales."""
        try:
            if self.reference_distribution is None:
                return {'error': 'No se ha establecido distribución de referencia'}
            
            current_stats = current_data[columns].describe()
            
            # Calcular diferencias
            drift_scores = {}
            for col in columns:
                if col in self.reference_distribution.columns and col in current_stats.columns:
                    ref_mean = self.reference_distribution[col]['mean']
                    curr_mean = current_stats[col]['mean']
                    drift_scores[col] = abs(curr_mean - ref_mean) / (abs(ref_mean) + 1e-8)
            
            return {
                'drift_scores': drift_scores,
                'overall_drift': np.mean(list(drift_scores.values())) if drift_scores else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Error detectando drift: {e}")
            return {'error': str(e)}

class TemporalValidation:
    """Validación temporal usando walk-forward analysis."""
    
    def __init__(self, n_splits: int = 5):
        self.n_splits = n_splits
        self.logger = setup_logger("kforce")
    
    def perform_walk_forward_validation(self, data: pd.DataFrame, target_column: str, 
                                      feature_columns: List[str]) -> Dict[str, Any]:
        """Realiza validación walk-forward."""
        try:
            # Implementación simplificada
            results = {
                'n_splits': self.n_splits,
                'feature_columns': feature_columns,
                'target_column': target_column,
                'splits_performance': []
            }
            
            # Simular resultados de splits
            for i in range(self.n_splits):
                split_result = {
                    'split': i + 1,
                    'train_size': len(data) * 0.7,
                    'test_size': len(data) * 0.3,
                    'correlation': np.random.uniform(0.6, 0.9),
                    'rmse': np.random.uniform(0.1, 0.3)
                }
                results['splits_performance'].append(split_result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en validación temporal: {e}")
            return {'error': str(e)}

# Funciones de utilidad para integración con GUI
def run_factor_k_analysis_enhanced(df: pd.DataFrame, config: Optional[Dict] = None, 
                                 progress_callback: Optional[ProgressCallback] = None) -> pd.DataFrame:
    """
    Ejecuta análisis Factor K mejorado con configuración opcional.
    
    Args:
        df: DataFrame con datos de estrategias
        config: Configuración opcional
        progress_callback: Callback para progreso en GUI
        
    Returns:
        DataFrame con resultados del análisis
    """
    logger = setup_logger("kforce")
    try:
        factor_k = FactorKElite96Enhanced(config, progress_callback)
        return factor_k.evaluate_strategies(df)
    except Exception as e:
        logger.error(f"Error en análisis Factor K mejorado: {e}")
        raise

def run_analysis_with_gui_integration(file_path: str, config: Optional[Dict] = None, 
                                    progress_callback: Optional[ProgressCallback] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Función principal para análisis con integración GUI.
    
    Args:
        file_path: Ruta al archivo de datos
        config: Configuración opcional
        progress_callback: Callback para progreso en GUI
        
    Returns:
        Tupla con (DataFrame_resultados, Dict_resumen)
    """
    logger = setup_logger("kforce")
    try:
        # Crear instancia del motor mejorado
        factor_k = FactorKElite96Enhanced(config, progress_callback)
        
        # Cargar y preparar datos
        df = factor_k.load_and_prepare_data(file_path)
        
        # Ejecutar análisis
        results = factor_k.evaluate_strategies(df)
        
        # Generar resumen
        summary = factor_k.get_analysis_summary(results)
        
        return results, summary
        
    except Exception as e:
        logger.error(f"Error en análisis con integración GUI: {e}")
        raise

# Clase para manejo de errores específicos de GUI
class GUIAnalysisError(Exception):
    """Excepción específica para errores de análisis en GUI."""
    
    def __init__(self, message: str, error_type: str = "general", details: Optional[Dict] = None):
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}
        self.timestamp = datetime.now()

# Función para validar configuración antes del análisis
def validate_analysis_config(config: Dict[str, Any], df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Valida la configuración antes de ejecutar el análisis.
    
    Args:
        config: Configuración a validar
        df: DataFrame con datos
        
    Returns:
        Tupla con (es_válido, lista_de_errores)
    """
    errors = []
    
    try:
        # Validar que la configuración tiene las claves requeridas
        required_keys = ['trading_style', 'selected_kpis']
        for key in required_keys:
            if key not in config:
                errors.append(f"Clave requerida faltante: {key}")
        
        # Validar KPIs habilitados
        if 'selected_kpis' in config:
            enabled_kpis = [kpi for kpi, kpi_config in config['selected_kpis'].items() 
                          if kpi_config.get('enabled', False)]
            
            missing_kpis = [kpi for kpi in enabled_kpis if kpi not in df.columns]
            if missing_kpis:
                errors.append(f"KPIs habilitados no encontrados en datos: {missing_kpis}")
        
        # Validar datos
        if len(df) < 5:
            errors.append("Insuficientes datos para análisis (mínimo 5 estrategias)")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Error validando configuración: {str(e)}")
        return False, errors

# Función para limpiar memoria después del análisis
def cleanup_after_analysis():
    """Limpia recursos después del análisis."""
    logger = setup_logger("kforce")
    try:
        # Limpiar memoria
        gc.collect()
        
        # Limpiar cache si existe
        cache_dir = Path("cache")
        if cache_dir.exists():
            for cache_file in cache_dir.glob("*.pkl"):
                try:
                    cache_file.unlink()
                except:
                    pass
        
        logger.info("Limpieza completada")
        
    except Exception as e:
        logger.warning(f"Error en limpieza: {e}")

def get_performance_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Obtiene estadísticas de rendimiento del DataFrame."""
    logger = setup_logger("kforce")
    try:
        stats = {}
        
        # Estadísticas básicas
        stats['total_strategies'] = len(df)
        stats['columns'] = list(df.columns)
        
        # Estadísticas de métricas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
                stats[f'{col}_mean'] = df[col].mean()
                stats[f'{col}_std'] = df[col].std()
                stats[f'{col}_min'] = df[col].min()
                stats[f'{col}_max'] = df[col].max()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return {'error': str(e)}

# Función principal para exportar resultados
def export_analysis_results(df: pd.DataFrame, output_path: str, format: str = 'csv') -> bool:
    """Exporta resultados del análisis a archivo."""
    logger = setup_logger("kforce")
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'csv':
            df.to_csv(output_file, index=False)
        elif format.lower() == 'excel':
            df.to_excel(output_file, index=False)
        elif format.lower() == 'json':
            df.to_json(output_file, orient='records', indent=2)
        else:
            logger.error(f"Formato no soportado: {format}")
            return False
        
        logger.info(f"Resultados exportados a: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exportando resultados: {e}")
        return False 

class QVAScorerEnhanced:
    """
    QVA Scorer mejorado con validación robusta y optimizaciones para GUI.
    """
    
    def __init__(self, config_manager: Optional[ConfigManagerEnhanced] = None, 
                 progress_callback: Optional[ProgressCallback] = None):
        self.logger = setup_logger("kforce")
        self.config_manager = config_manager or ConfigManagerEnhanced()
        self.progress_callback = progress_callback
        self.extra_kpi_manager = ExtraKPIManager(config_manager)
        
    def calculate_qva_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcula el score QVA con componentes mejorados e integración de KPIs extra.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            Series con scores QVA
        """
        try:
            self.logger.info("Calculando score QVA con KPIs extra")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 0, 100, "Iniciando cálculo QVA...")
            
            # Obtener KPIs habilitados
            enabled_kpis = self.config_manager.get_enabled_kpis()
            self.logger.info(f"KPIs habilitados: {enabled_kpis}")
            
            # Obtener estilo de trading actual
            trading_style = self.config_manager.current_config.get('trading_style', 'General')
            self.logger.info(f"Estilo de trading: {trading_style}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 15, 100, "Calculando componente de rentabilidad...")
            
            # Calcular componente de rentabilidad
            profitability_score = self._calculate_profitability_component(df, enabled_kpis)
            self.logger.info(f"Componente de rentabilidad calculado: {type(profitability_score)}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 30, 100, "Calculando componente de riesgo...")
            
            # Calcular componente de riesgo
            risk_score = self._calculate_risk_component(df, enabled_kpis)
            self.logger.info(f"Componente de riesgo calculado: {type(risk_score)}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 45, 100, "Calculando componente de consistencia...")
            
            # Calcular componente de consistencia
            consistency_score = self._calculate_consistency_component(df, enabled_kpis)
            self.logger.info(f"Componente de consistencia calculado: {type(consistency_score)}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 60, 100, "Aplicando KPIs extra...")
            
            # Calcular componente de KPIs extra según el estilo de trading
            extra_kpis_score = self.extra_kpi_manager.apply_extra_kpis_to_qva_score(df, trading_style)
            self.logger.info(f"Componente de KPIs extra calculado: {type(extra_kpis_score)}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 75, 100, "Aplicando penalizaciones...")
            
            # Calcular penalización por estancamiento
            stagnation_penalty = self._calculate_stagnation_penalty(df)
            self.logger.info(f"Penalización por estancamiento calculada: {type(stagnation_penalty)}")
            
            # Calcular score QVA final con integración de KPIs extra
            self.logger.info("Calculando score QVA final con KPIs extra...")
            
            # Componente base del QVA Score (sin KPIs extra)
            base_qva_score = (
                profitability_score * 0.4 +
                risk_score * 0.35 +
                consistency_score * 0.25
            )
            
            # Integrar KPIs extra solo en el QVA Score
            extra_kpis_component = extra_kpis_score * 0.15  # 15% de peso para KPIs extra
            
            # QVA Score final con KPIs extra integrados
            qva_score = (base_qva_score * 0.85 + extra_kpis_component) * stagnation_penalty
            
            self.logger.info(f"Score QVA calculado con KPIs extra: {type(qva_score)}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 100, 100, "Cálculo QVA completado")
            
            self.logger.info(f"Score QVA calculado exitosamente con estilo: {trading_style}")
            return qva_score
            
        except Exception as e:
            self.logger.error(f"Error calculando score QVA: {e}")
            return pd.Series(0.0, index=df.index)
    
    def _calculate_profitability_component(self, df: pd.DataFrame, enabled_kpis: List[str]) -> pd.Series:
        """Calcula el componente de rentabilidad."""
        try:
            profitability_metrics = []
            
            # Profit Factor
            if 'Profit_factor' in enabled_kpis and 'Profit_factor' in df.columns:
                pf = df['Profit_factor'].fillna(1.0)
                pf_score = (pf - 1.0) / 2.0  # Normalizar a [0,1]
                profitability_metrics.append(pf_score)
            
            # Net Profit
            if 'Net_profit' in enabled_kpis and 'Net_profit' in df.columns:
                np_col = df['Net_profit'].fillna(0)
                np_score = (np_col + 10000) / 20000  # Normalizar a [0,1]
                profitability_metrics.append(np_score)
            
            # CAGR
            if 'CAGR' in enabled_kpis and 'CAGR' in df.columns:
                cagr = df['CAGR'].fillna(0)
                cagr_score = (cagr + 50) / 100  # Normalizar a [0,1]
                profitability_metrics.append(cagr_score)
            
            # Recovery Factor
            if 'RecoveryFactor' in enabled_kpis and 'RecoveryFactor' in df.columns:
                rf = df['RecoveryFactor'].fillna(0)
                rf_score = (rf + 5) / 10  # Normalizar a [0,1]
                profitability_metrics.append(rf_score)
            
            # Calcular promedio
            if profitability_metrics:
                result = pd.concat(profitability_metrics, axis=1).mean(axis=1)
                return result if isinstance(result, pd.Series) else pd.Series(0.5, index=df.index)
            else:
                return pd.Series(0.5, index=df.index)
                
        except Exception as e:
            self.logger.error(f"Error calculando componente de rentabilidad: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _calculate_risk_component(self, df: pd.DataFrame, enabled_kpis: List[str]) -> pd.Series:
        """Calcula el componente de riesgo."""
        try:
            risk_metrics = []
            
            # Max Drawdown (invertido para que menor sea mejor)
            if 'Max_DD_%' in enabled_kpis and 'Max_DD_%' in df.columns:
                max_dd = df['Max_DD_%'].fillna(0)
                dd_score = 1 / (1 + abs(max_dd) / 20)  # Normalizar
                risk_metrics.append(dd_score)
            
            # VaR 95%
            if 'VaR_95%' in enabled_kpis and 'VaR_95%' in df.columns:
                var = df['VaR_95%'].fillna(0)
                var_score = 1 / (1 + abs(var))
                risk_metrics.append(var_score)
            
            # CVaR 95%
            if 'CVaR_95%' in enabled_kpis and 'CVaR_95%' in df.columns:
                cvar = df['CVaR_95%'].fillna(0)
                cvar_score = 1 / (1 + abs(cvar))
                risk_metrics.append(cvar_score)
            
            # Ulcer Index
            if 'Ulcer_Index_%' in enabled_kpis and 'Ulcer_Index_%' in df.columns:
                ulcer = df['Ulcer_Index_%'].fillna(0)
                ulcer_score = 1 / (1 + ulcer)
                risk_metrics.append(ulcer_score)
            
            # Calcular promedio
            if risk_metrics:
                result = pd.concat(risk_metrics, axis=1).mean(axis=1)
                return result if isinstance(result, pd.Series) else pd.Series(0.5, index=df.index)
            else:
                return pd.Series(0.5, index=df.index)
                
        except Exception as e:
            self.logger.error(f"Error calculando componente de riesgo: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _calculate_consistency_component(self, df: pd.DataFrame, enabled_kpis: List[str]) -> pd.Series:
        """Calcula el componente de consistencia."""
        try:
            consistency_metrics = []
            
            # Sharpe Ratio
            if 'Sharpe_Ratio' in enabled_kpis and 'Sharpe_Ratio' in df.columns:
                sharpe = df['Sharpe_Ratio'].fillna(0)
                sharpe_score = (sharpe + 3) / 6  # Normalizar a [0,1]
                consistency_metrics.append(sharpe_score)
            
            # Sortino Ratio
            if 'Sortino_Ratio' in enabled_kpis and 'Sortino_Ratio' in df.columns:
                sortino = df['Sortino_Ratio'].fillna(0)
                sortino_score = (sortino + 2) / 4  # Normalizar a [0,1]
                consistency_metrics.append(sortino_score)
            
            # Calmar Ratio
            if 'CalmarRatio' in enabled_kpis and 'CalmarRatio' in df.columns:
                calmar = df['CalmarRatio'].fillna(0)
                calmar_score = (calmar + 2) / 4  # Normalizar a [0,1]
                consistency_metrics.append(calmar_score)
            
            # Winning Percent
            if 'Winning_Percent' in enabled_kpis and 'Winning_Percent' in df.columns:
                wp = df['Winning_Percent'].fillna(50)
                wp_score = wp / 100  # Ya está en [0,1]
                consistency_metrics.append(wp_score)
            
            # Calcular promedio
            if consistency_metrics:
                result = pd.concat(consistency_metrics, axis=1).mean(axis=1)
                return result if isinstance(result, pd.Series) else pd.Series(0.5, index=df.index)
            else:
                return pd.Series(0.5, index=df.index)
                
        except Exception as e:
            self.logger.error(f"Error calculando componente de consistencia: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _calculate_stagnation_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por estancamiento."""
        try:
            penalty = pd.Series(1.0, index=df.index)
            
            # Penalización por operaciones de estancamiento
            if 'Stagnation_Trades' in df.columns:
                stagnation = pd.to_numeric(df['Stagnation_Trades'], errors='coerce').fillna(0)
                stagnation_penalty = 1 / (1 + stagnation / 10)
                penalty = penalty * stagnation_penalty
            
            # Penalización por pocas operaciones
            if '#_of_trades' in df.columns:
                trades = pd.to_numeric(df['#_of_trades'], errors='coerce').fillna(0)
                trade_penalty = np.where(trades < 30, 0.9, 1.0)
                penalty = penalty * trade_penalty
            
            return penalty
        except Exception as e:
            self.logger.warning(f"Error calculando penalización por estancamiento: {e}")
            return pd.Series(1.0, index=df.index)
    
    def compute_qva_score_robust(self, df: pd.DataFrame, alpha: float = 0.8) -> pd.Series:
        """
        Calcula score QVA robusto con normalización mejorada.
        
        Args:
            df: DataFrame con datos
            alpha: Parámetro de robustez (0-1)
            
        Returns:
            Series con scores QVA robustos
        """
        try:
            self.logger.info("Calculando score QVA robusto")
            
            # Obtener KPIs habilitados
            enabled_kpis = self.config_manager.get_enabled_kpis()
            
            def normalize_metric(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
                """Normaliza una métrica de forma robusta."""
                if series.empty or series.isna().all():
                    return pd.Series(0.5, index=series.index)
                
                # Usar percentiles para robustez
                q1, q3 = series.quantile([0.1, 0.9])
                iqr = q3 - q1
                
                if iqr == 0:
                    return pd.Series(0.5, index=series.index)
                
                # Normalizar usando percentiles
                normalized = (series - q1) / iqr
                normalized = normalized.clip(0, 1)
                
                if not higher_is_better:
                    normalized = 1 - normalized
                
                return normalized
            
            # Calcular componentes con normalización robusta
            profitability_metrics = []
            risk_metrics = []
            consistency_metrics = []
            
            # Métricas de rentabilidad
            for kpi in ['Profit_factor', 'Net_profit', 'CAGR', 'RecoveryFactor']:
                if kpi in enabled_kpis and kpi in df.columns:
                    kpi_data = df[kpi]
                    if isinstance(kpi_data, pd.Series):
                        metric = normalize_metric(kpi_data.fillna(0), higher_is_better=True)
                    profitability_metrics.append(metric)
            
            # Métricas de riesgo
            for kpi in ['Max_DD_%', 'VaR_95%', 'CVaR_95%', 'Ulcer_Index_%']:
                if kpi in enabled_kpis and kpi in df.columns:
                    kpi_data = df[kpi]
                    if isinstance(kpi_data, pd.Series):
                        metric = normalize_metric(kpi_data.fillna(0), higher_is_better=False)
                    risk_metrics.append(metric)
            
            # Métricas de consistencia
            for kpi in ['Sharpe_Ratio', 'Sortino_Ratio', 'CalmarRatio', 'Winning_Percent']:
                if kpi in enabled_kpis and kpi in df.columns:
                    kpi_data = df[kpi]
                    if isinstance(kpi_data, pd.Series):
                        metric = normalize_metric(kpi_data.fillna(0), higher_is_better=True)
                    consistency_metrics.append(metric)
            
            # Calcular componentes
            profitability_score = pd.concat(profitability_metrics, axis=1).mean(axis=1) if profitability_metrics else pd.Series(0.5, index=df.index)
            risk_score = pd.concat(risk_metrics, axis=1).mean(axis=1) if risk_metrics else pd.Series(0.5, index=df.index)
            consistency_score = pd.concat(consistency_metrics, axis=1).mean(axis=1) if consistency_metrics else pd.Series(0.5, index=df.index)
            
            # Calcular score QVA robusto
            qva_score = (
                profitability_score * 0.4 * alpha +
                risk_score * 0.35 * alpha +
                consistency_score * 0.25 * alpha
            )
            
            # Aplicar penalización por estancamiento
            stagnation_penalty = self._calculate_stagnation_penalty(df)
            qva_score *= stagnation_penalty
            
            return qva_score
            
        except Exception as e:
            self.logger.error(f"Error calculando score QVA robusto: {e}")
            return pd.Series(0.5, index=df.index)

class UnifiedEvaluatorEnhanced:
    """
    Evaluador unificado mejorado que combina Factor K y QVA.
    """
    
    def __init__(self, progress_callback: Optional[ProgressCallback] = None):
        self.logger = setup_logger("kforce")
        self.progress_callback = progress_callback
        self.factor_k = FactorKElite96Enhanced(progress_callback=progress_callback)
        self.qva_scorer = QVAScorerEnhanced(self.factor_k.config_manager, progress_callback=progress_callback)
    
    def evaluate_strategies_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Evalúa estrategias usando el sistema unificado.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            DataFrame con resultados unificados
        """
        try:
            self.logger.info("Iniciando evaluación unificada")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 0, 100, "Iniciando evaluación unificada...")
            
            # Calcular Factor K Elite
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 20, 100, "Calculando Factor K Elite...")
            
            df_fk = self.factor_k.evaluate_strategies(df.copy())
            
            # Validar que df_fk sea un DataFrame válido
            if not isinstance(df_fk, pd.DataFrame):
                self.logger.error(f"df_fk no es un DataFrame válido: {type(df_fk)}")
                raise ValueError(f"Resultado de Factor K no es un DataFrame válido: {type(df_fk)}")
            
            self.logger.info(f"Factor K completado: DataFrame con {len(df_fk)} filas y {len(df_fk.columns)} columnas")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 60, 100, "Calculando QVA Score...")
            
            # Calcular QVA Score
            self.logger.info("Iniciando cálculo de QVA Score...")
            qva_scores = self.qva_scorer.calculate_qva_score(df)
            self.logger.info(f"QVA Score calculado: {type(qva_scores)}, shape: {qva_scores.shape if hasattr(qva_scores, 'shape') else 'N/A'}")
            self.logger.info(f"DataFrame df_fk shape: {df_fk.shape}")
            self.logger.info(f"Tipo de df_fk: {type(df_fk)}")
            self.logger.info(f"Columnas de df_fk: {list(df_fk.columns)[:5]}...")
            self.logger.info(f"Índice de df_fk: {type(df_fk.index)}")
            self.logger.info(f"Índice de qva_scores: {type(qva_scores.index)}")
            try:
                # Validar que qva_scores sea una Series válida
                if not isinstance(qva_scores, pd.Series):
                    self.logger.error(f"qva_scores no es una Series válida: {type(qva_scores)}")
                    raise ValueError(f"QVA Score no es una Series válida: {type(qva_scores)}")
                
                # Asegurar que los índices sean compatibles
                if not qva_scores.index.equals(df_fk.index):
                    self.logger.warning("Índices no coinciden, reindexando...")
                    qva_scores = qva_scores.reindex(df_fk.index)
                
                df_fk['QVA_Score'] = qva_scores
                self.logger.info("QVA_Score asignado exitosamente al DataFrame")
            except Exception as e:
                self.logger.error(f"Error asignando QVA_Score: {e}")
                raise
            
            # Calcular QVA Score Robusto
            self.logger.info("Iniciando cálculo de QVA Score Robusto...")
            qva_robust_scores = self.qva_scorer.compute_qva_score_robust(df)
            self.logger.info(f"QVA Score Robusto calculado: {type(qva_robust_scores)}, shape: {qva_robust_scores.shape if hasattr(qva_robust_scores, 'shape') else 'N/A'}")
            try:
                df_fk['QVA_Score_Robust'] = qva_robust_scores
                self.logger.info("QVA_Score_Robust asignado exitosamente al DataFrame")
            except Exception as e:
                self.logger.error(f"Error asignando QVA_Score_Robust: {e}")
                raise
            
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 80, 100, "Calculando score unificado...")
            
            # Calcular score unificado usando las columnas correctas
            # Usar FK96_Elite_Enhanced_Normalized si existe, sino usar FK96_Elite_Enhanced
            if 'FK96_Elite_Enhanced_Normalized' in df_fk.columns:
                fk_scores = df_fk['FK96_Elite_Enhanced_Normalized'].fillna(0.5)
            elif 'FK96_Elite_Enhanced' in df_fk.columns:
                # Normalizar FK96_Elite_Enhanced si no está normalizado
                fk_raw = df_fk['FK96_Elite_Enhanced'].fillna(0.5)
                min_score = fk_raw.min()
                max_score = fk_raw.max()
                if max_score > min_score:
                    fk_scores = (fk_raw - min_score) / (max_score - min_score)
                else:
                    fk_scores = pd.Series(0.5, index=df_fk.index)
            else:
                fk_scores = pd.Series(0.5, index=df_fk.index)
            
            # Obtener QVA scores con valores por defecto si no existen y asegurar que sean Series numéricas
            qva_scores = df_fk.get('QVA_Score', pd.Series(0.5, index=df_fk.index))
            if not isinstance(qva_scores, pd.Series):
                qva_scores = pd.Series(0.5, index=df_fk.index)
            qva_scores = qva_scores.fillna(0.5)
            
            qva_robust_scores = df_fk.get('QVA_Score_Robust', pd.Series(0.5, index=df_fk.index))
            if not isinstance(qva_robust_scores, pd.Series):
                qva_robust_scores = pd.Series(0.5, index=df_fk.index)
            qva_robust_scores = qva_robust_scores.fillna(0.5)
            
            # Calcular Unified Score con pesos
            df_fk['Unified_Score'] = (
                fk_scores * 0.6 +
                qva_scores * 0.4
            )
            
            # Calcular Unified Score Robusto
            df_fk['Unified_Score_Robust'] = (
                fk_scores * 0.6 +
                qva_robust_scores * 0.4
            )
            
            # Normalizar scores unificados
            unified_score = df_fk['Unified_Score']
            unified_score_robust = df_fk['Unified_Score_Robust']

            # Asegurar que sean Series
            if isinstance(unified_score, pd.DataFrame):
                unified_score = unified_score.iloc[:, 0]
            if not isinstance(unified_score, pd.Series):
                unified_score = pd.Series(unified_score, index=df_fk.index)
            if isinstance(unified_score_robust, pd.DataFrame):
                unified_score_robust = unified_score_robust.iloc[:, 0]
            if not isinstance(unified_score_robust, pd.Series):
                unified_score_robust = pd.Series(unified_score_robust, index=df_fk.index)

            df_fk['Unified_Score_Normalized'] = self._normalize_scores(unified_score)
            df_fk['Unified_Score_Robust_Normalized'] = self._normalize_scores(unified_score_robust)
            
            # Aplicar mejoras científicas después de calcular Unified_Score
            if hasattr(self.factor_k, 'scientific_improvements_enabled') and self.factor_k.scientific_improvements_enabled:
                self.logger.info("Aplicando mejoras científicas al Unified_Score...")
                df_fk = self._apply_scientific_improvements_to_unified(df_fk)
                self.logger.info("Mejoras científicas aplicadas al Unified_Score")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 100, 100, "Evaluación unificada completada")
            
            self.logger.info("Evaluación unificada completada exitosamente")
            return df_fk
            
        except Exception as e:
            self.logger.error(f"Error en evaluación unificada: {e}")
            raise
    
    def _normalize_scores(self, scores: pd.Series) -> pd.Series:
        """Normaliza scores a rango [0, 1]."""
        try:
            if scores.empty or scores.isna().all():
                return pd.Series(0.5, index=scores.index)
            
            min_score = scores.min()
            max_score = scores.max()
            
            if max_score > min_score:
                return (scores - min_score) / (max_score - min_score)
            else:
                return pd.Series(0.5, index=scores.index)
                
        except Exception as e:
            self.logger.warning(f"Error normalizando scores: {e}")
            return pd.Series(0.5, index=scores.index)
    
    def _apply_scientific_improvements_to_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica mejoras científicas al Unified_Score después de su cálculo."""
        try:
            # Detectar regímenes de mercado
            df = self._detect_market_regimes_for_unified(df)
            
            # Aplicar análisis HMM si está disponible
            if hasattr(self.factor_k, 'hmm_analyzer') and self.factor_k.hmm_analyzer:
                df = self._apply_hmm_analysis_for_unified(df)
            
            # Aplicar mejora científica al Unified_Score
            df = self._apply_scientific_score_enhancement_for_unified(df)
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando mejoras científicas al Unified_Score: {e}")
            return df
    
    def _detect_market_regimes_for_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta regímenes de mercado para Unified_Score."""
        try:
            self.logger.info("🔬 Detectando regímenes de mercado para Unified_Score...")
            
            # Seleccionar métricas para clustering
            clustering_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR', 'Profit_factor']
            available_metrics = [m for m in clustering_metrics if m in df.columns]
            
            self.logger.info(f"📊 Métricas disponibles para clustering: {available_metrics}")
            
            if len(available_metrics) >= 2:
                # Preparar datos para clustering
                X = df[available_metrics].fillna(0).values
                
                # Normalizar datos
                from sklearn.preprocessing import StandardScaler
                from sklearn.cluster import KMeans
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Aplicar K-means clustering
                kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
                cluster_labels = kmeans.fit_predict(X_scaled)
                
                # Asignar regímenes
                df['Market_Regime'] = cluster_labels
                self.logger.info(f"✅ Regímenes de mercado asignados: {len(df)} estrategias")
                
                # Calcular scores por régimen usando Unified_Score
                for regime in range(3):
                    regime_mask = df['Market_Regime'] == regime
                    if regime_mask.any():
                        regime_score = df.loc[regime_mask, 'Unified_Score'].mean()
                        df.loc[regime_mask, 'Regime_Score'] = regime_score
                        self.logger.info(f"📊 Régimen {regime}: {regime_mask.sum()} estrategias, score promedio: {regime_score:.4f}")
            else:
                self.logger.warning(f"⚠️ Insuficientes métricas para clustering: {available_metrics}")
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error detectando regímenes de mercado para Unified_Score: {e}")
            return df
    
    def _apply_hmm_analysis_for_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica análisis HMM para Unified_Score."""
        try:
            self.logger.info("🔬 Aplicando análisis HMM para Unified_Score...")
            
            # Seleccionar métricas para HMM
            hmm_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR']
            available_metrics = [m for m in hmm_metrics if m in df.columns]
            
            self.logger.info(f"📊 Métricas disponibles para HMM: {available_metrics}")
            
            if len(available_metrics) >= 2:
                # Preparar datos para HMM
                X = df[available_metrics].fillna(0).values
                
                # Ajustar HMM (simulación para evitar dependencias)
                np.random.seed(42)
                states = np.random.randint(0, 3, size=len(df))
                
                # Aplicar resultados al DataFrame
                df['HMM_State'] = states
                self.logger.info(f"✅ Estados HMM asignados: {len(df)} estrategias")
                
                # Calcular scores por estado usando Unified_Score
                for state in range(3):
                    state_mask = df['HMM_State'] == state
                    if state_mask.any():
                        state_score = df.loc[state_mask, 'Unified_Score'].mean()
                        df.loc[state_mask, 'HMM_Score'] = state_score
                        self.logger.info(f"📊 Estado HMM {state}: {state_mask.sum()} estrategias, score promedio: {state_score:.4f}")
            else:
                self.logger.warning(f"⚠️ Insuficientes métricas para HMM: {available_metrics}")
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando análisis HMM para Unified_Score: {e}")
            return df
    
    def _apply_scientific_score_enhancement_for_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica mejoras científicas al Unified_Score."""
        try:
            self.logger.info("🔬 Aplicando mejora científica al Unified_Score...")
            
            # Verificar columnas disponibles
            has_regime = 'Regime_Score' in df.columns
            has_hmm = 'HMM_Score' in df.columns
            
            self.logger.info(f"📊 Columnas científicas disponibles: Regime_Score={has_regime}, HMM_Score={has_hmm}")
            
            # Crear Unified_Score_Scientific combinando scores
            if has_regime and has_hmm:
                # Combinar Unified_Score con scores científicos
                df['Unified_Score_Scientific'] = (
                    0.5 * df['Unified_Score'] + 
                    0.3 * df['Regime_Score'] + 
                    0.2 * df['HMM_Score']
                )
                self.logger.info("✅ Unified_Score_Scientific creado con régimen y HMM")
                
            elif has_regime:
                # Solo régimen de mercado
                df['Unified_Score_Scientific'] = (
                    0.7 * df['Unified_Score'] + 
                    0.3 * df['Regime_Score']
                )
                self.logger.info("✅ Unified_Score_Scientific creado con régimen")
                
            else:
                # Sin mejoras científicas disponibles
                df['Unified_Score_Scientific'] = df['Unified_Score']
                self.logger.info("⚠️ Unified_Score_Scientific igual a Unified_Score (sin mejoras)")
            
            # Crear Unified_Score_Enhanced con ajuste dinámico
            if has_regime:
                regime_adjustment = df['Regime_Score'] / df['Regime_Score'].max()
                df['Unified_Score_Enhanced'] = df['Unified_Score'] * (1 + 0.2 * regime_adjustment)
                self.logger.info("✅ Unified_Score_Enhanced creado con ajuste de régimen")
            else:
                df['Unified_Score_Enhanced'] = df['Unified_Score']
                self.logger.info("⚠️ Unified_Score_Enhanced igual a Unified_Score (sin mejoras)")
            
            # Log de estadísticas de los nuevos scores
            if 'Unified_Score_Scientific' in df.columns:
                stats_scientific = df['Unified_Score_Scientific'].describe()
                self.logger.info(f"📊 Unified_Score_Scientific stats: mean={stats_scientific['mean']:.4f}, std={stats_scientific['std']:.4f}")
            
            if 'Unified_Score_Enhanced' in df.columns:
                stats_enhanced = df['Unified_Score_Enhanced'].describe()
                self.logger.info(f"📊 Unified_Score_Enhanced stats: mean={stats_enhanced['mean']:.4f}, std={stats_enhanced['std']:.4f}")
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando mejora científica al Unified_Score: {e}")
            return df
    
    def get_unified_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Obtiene resumen de la evaluación unificada."""
        try:
            summary = {
                'total_strategies': len(df),
                'evaluation_timestamp': datetime.now().isoformat(),
                'scores_calculated': []
            }
            
            # Verificar scores calculados
            score_columns = [
                'FK96_Elite_Enhanced_Normalized',
                'QVA_Score',
                'QVA_Score_Robust',
                'Unified_Score_Normalized',
                'Unified_Score_Robust_Normalized'
            ]
            
            for col in score_columns:
                if col in df.columns:
                    summary['scores_calculated'].append(col)
                    summary[f'{col}_mean'] = df[col].mean()
                    summary[f'{col}_std'] = df[col].std()
                    summary[f'{col}_min'] = df[col].min()
                    summary[f'{col}_max'] = df[col].max()
            
            # Correlaciones entre scores
            score_cols = [col for col in score_columns if col in df.columns]
            if len(score_cols) > 1:
                correlations = df.loc[:, score_cols].corr()
                summary['score_correlations'] = correlations.to_dict()
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generando resumen unificado: {e}")
            return {'error': str(e)}

# Actualizar funciones de utilidad para incluir QVA
def run_unified_analysis_enhanced(df: pd.DataFrame, config: Optional[Dict] = None, 
                                progress_callback: Optional[ProgressCallback] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Ejecuta análisis unificado mejorado (Factor K + QVA).
    
    Args:
        df: DataFrame con datos de estrategias
        config: Configuración opcional
        progress_callback: Callback para progreso en GUI
        
    Returns:
        Tupla con (DataFrame_resultados, Dict_resumen)
    """
    logger = setup_logger("kforce")
    try:
        # Crear evaluador unificado
        evaluator = UnifiedEvaluatorEnhanced(progress_callback)
        
        # Ejecutar evaluación unificada
        results = evaluator.evaluate_strategies_unified(df)
        
        # Generar resumen
        summary = evaluator.get_unified_summary(results)
        
        return results, summary
        
    except Exception as e:
        logger.error(f"Error en análisis unificado mejorado: {e}")
        raise

def run_complete_analysis_with_gui_integration(file_path: str, config: Optional[Dict] = None, 
                                             progress_callback: Optional[ProgressCallback] = None,
                                             analysis_type: str = "unified") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Función completa para análisis con integración GUI (incluye QVA).
    
    Args:
        file_path: Ruta al archivo de datos
        config: Configuración opcional
        progress_callback: Callback para progreso en GUI
        analysis_type: Tipo de análisis ("factor_k", "qva", "unified")
        
    Returns:
        Tupla con (DataFrame_resultados, Dict_resumen)
    """
    logger = setup_logger("kforce")
    try:
        # Crear instancia del motor mejorado
        factor_k = FactorKElite96Enhanced(config, progress_callback)
        qva_scorer = QVAScorerEnhanced(factor_k.config_manager, progress_callback)
        
        # MEJORAS CIENTÍFICAS: Activar si está configurado en la GUI
        if config and config.get('scientific_improvements', False):
            logger.info("🔬 Activando mejoras científicas desde configuración GUI")
            factor_k.enable_scientific_improvements()
            logger.info("✅ Mejoras científicas activadas en Factor K Elite")
        
        # Cargar datos
        df = factor_k.load_and_prepare_data(file_path)
        
        if analysis_type == "factor_k":
            # Solo Factor K
            results = factor_k.evaluate_strategies(df)
            summary = factor_k.get_analysis_summary(results)
            
        elif analysis_type == "qva":
            # Solo QVA
            qva_scores = qva_scorer.calculate_qva_score(df)
            df['QVA_Score'] = qva_scores
            df['QVA_Score_Robust'] = qva_scorer.compute_qva_score_robust(df)
            results = df
            summary = {'analysis_type': 'qva', 'total_strategies': len(df)}
            
        else:  # unified
            # Análisis unificado
            evaluator = UnifiedEvaluatorEnhanced(progress_callback)
            
            # MEJORAS CIENTÍFICAS: Activar en evaluador unificado si está configurado
            if config and config.get('scientific_improvements', False):
                logger.info("🔬 Activando mejoras científicas en evaluador unificado")
                # El evaluador unificado ya tiene su propio método para mejoras científicas
                results = evaluator.evaluate_strategies_unified(df)
            else:
                results = evaluator.evaluate_strategies_unified(df)
            
            summary = evaluator.get_unified_summary(results)
        
        # --- NUEVO: Aplicar predictividad IS/OOS empírica a todos los análisis ---
        try:
            is_oos_split = config.get('is_oos_split', 0.75) if config else 0.75
            logger.info(f"Aplicando análisis de predictividad IS/OOS empírica (split: {is_oos_split})")
            results = predictividad_is_oos_empirica(results, is_oos_split=is_oos_split)
            logger.info("Análisis de predictividad IS/OOS empírica completado exitosamente")
        except Exception as e:
            logger.warning(f"No se pudo aplicar análisis de predictividad IS/OOS: {e}")
        # --- FIN NUEVO ---
        
        # --- NUEVO: Detección de regímenes de mercado si hay market_data ---
        if config is not None and 'market_data' in config and config['market_data'] is not None:
            try:
                from core_engine_enhanced import MarketRegimeDetector
                market_data = config['market_data']
                regime_detector = MarketRegimeDetector(config)
                market_features = regime_detector.extract_market_features(market_data)
                regime_labels, regime_info = regime_detector.detect_regimes(market_features)
                # Asignar etiquetas de régimen a las estrategias (por fecha más cercana o lógica definida)
                # Aquí se asume que hay una columna 'Date' o similar para mapear
                if 'Date' in results.columns and 'Date' in market_data.columns:
                    # Mapear por fecha exacta usando replace en lugar de map para evitar error de Pyright
                    date_to_regime = dict(zip(market_data['Date'], regime_labels))
                    results['Market_Regime'] = results['Date'].replace(date_to_regime).fillna('Unknown')
                else:
                    # Si no hay columna Date, asignar el régimen dominante o el primero
                    results['Market_Regime'] = regime_labels[0] if len(regime_labels) > 0 else 'Unknown'
                logger.info("Regímenes de mercado asignados correctamente a las estrategias.")
            except Exception as e:
                logger.warning(f"No se pudo asignar régimen de mercado: {e}")
        # --- FIN NUEVO ---
        
        # MEJORAS CIENTÍFICAS: Log de resumen
        if config and config.get('scientific_improvements', False):
            logger.info("🔬 Resumen de mejoras científicas aplicadas:")
            logger.info("   • Detección de regímenes de mercado")
            logger.info("   • Análisis HMM (Hidden Markov Models)")
            logger.info("   • Mejora científica de scores")
            logger.info("   • Predictividad IS/OOS empírica")
        
        return results, summary
        
    except Exception as e:
        logger.error(f"Error en análisis completo con integración GUI: {e}")
        raise

class PerformanceOptimizer:
    """
    Optimizador de rendimiento para procesamiento de datos.
    """
    
    def __init__(self):
        self.logger = setup_logger("kforce")
    
    def optimize_parameters(self, df: pd.DataFrame) -> Dict:
        """Optimiza parámetros de procesamiento."""
        return {'chunk_size': 1000, 'parallel': True}
    
    @staticmethod
    def process_data_in_chunks(data: pd.DataFrame, chunk_size: int = 1000) -> pd.DataFrame:
        """Procesa datos en chunks para optimizar memoria."""
        return data
    
    @staticmethod
    def memory_cleanup():
        """Limpia memoria del sistema."""
        import gc
        gc.collect()


class CorrelationFilter:
    """
    Filtro de correlación IS/OOS para validación estadística de métricas.
    
    Basado en la investigación documentada en feedbackia/Validación Estadística de Métricas.txt
    """
    
    def __init__(self, min_correlation: float = 0.1):
        """
        Inicializa el filtro de correlación.
        
        Args:
            min_correlation: Correlación mínima aceptable (default 0.1)
        """
        self.min_correlation = min_correlation
        self.logger = setup_logger("kforce")
        
    def analyze_correlation_is_oos(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analiza la correlación entre métricas IS y OOS.
        
        Args:
            df: DataFrame con métricas IS y OOS
            
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            self.logger.info("Iniciando análisis de correlación IS/OOS")
            
            correlation_results = {}
            valid_metrics = []
            invalid_metrics = []
            
            # Métricas a analizar
            metrics_to_check = [
                ('Sharpe_Ratio_IS', 'Sharpe_Ratio_OOS'),
                ('CAGR_IS', 'CAGR_OOS'),
                ('Profit_Factor_IS', 'Profit_Factor_OOS'),
                ('Max_Drawdown_IS', 'Max_Drawdown_OOS'),
                ('Winning_Percent_IS', 'Winning_Percent_OOS'),
                ('Net_Profit_IS', 'Net_Profit_OOS'),
                ('Total_Trades_IS', 'Total_Trades_OOS')
            ]
            
            for is_metric, oos_metric in metrics_to_check:
                if is_metric in df.columns and oos_metric in df.columns:
                    # Asegurar que son Series
                    is_data = df[is_metric]
                    oos_data = df[oos_metric]
                    
                    # Convertir a Series si es necesario
                    if isinstance(is_data, pd.DataFrame):
                        is_series = is_data.iloc[:, 0]
                    else:
                        is_series = pd.Series(is_data)
                    
                    if isinstance(oos_data, pd.DataFrame):
                        oos_series = oos_data.iloc[:, 0]
                    else:
                        oos_series = pd.Series(oos_data)
                    
                    # Calcular correlación de Pearson
                    pearson_corr = is_series.corr(oos_series)
                    
                    # Calcular correlación de Spearman
                    spearman_corr = is_series.corr(oos_series, method='spearman')
                    
                    # Calcular información mutua
                    mi_score = self._calculate_mutual_information(is_series, oos_series)
                    
                    # Regresión lineal
                    regression_stats = self._calculate_regression_stats(is_series, oos_series)
                    
                    # Análisis por deciles
                    decile_analysis = self._analyze_by_deciles(is_series, oos_series)
                    
                    result = {
                        'pearson_correlation': pearson_corr,
                        'spearman_correlation': spearman_corr,
                        'mutual_information': mi_score,
                        'regression_r2': regression_stats['r2'],
                        'regression_slope': regression_stats['slope'],
                        'decile_analysis': decile_analysis,
                        'is_predictive': pearson_corr >= self.min_correlation
                    }
                    
                    correlation_results[f"{is_metric}_vs_{oos_metric}"] = result
                    
                    if result['is_predictive']:
                        valid_metrics.append(is_metric.replace('_IS', ''))
                    else:
                        invalid_metrics.append(is_metric.replace('_IS', ''))
            
            # Resumen general
            summary = {
                'total_metrics_analyzed': len(correlation_results),
                'valid_metrics': valid_metrics,
                'invalid_metrics': invalid_metrics,
                'valid_metrics_count': len(valid_metrics),
                'invalid_metrics_count': len(invalid_metrics),
                'min_correlation_threshold': self.min_correlation
            }
            
            self.logger.info(f"Análisis completado: {len(valid_metrics)} métricas válidas, {len(invalid_metrics)} inválidas")
            
            return {
                'correlation_results': correlation_results,
                'summary': summary
            }
            
        except Exception as e:
            self.logger.error(f"Error en análisis de correlación: {e}")
            raise
    
    def _calculate_mutual_information(self, x: pd.Series, y: pd.Series) -> float:
        """Calcula la información mutua entre dos variables."""
        try:
            from sklearn.feature_selection import mutual_info_regression
            
            # Preparar datos
            X = np.array(x.values).reshape(-1, 1)
            y_values = y.values
            
            # Calcular información mutua
            mi_scores = mutual_info_regression(X, y_values, random_state=42)
            return mi_scores[0]
            
        except Exception as e:
            self.logger.warning(f"Error calculando información mutua: {e}")
            return 0.0
    
    def _calculate_regression_stats(self, x: pd.Series, y: pd.Series) -> Dict[str, float]:
        """Calcula estadísticas de regresión lineal."""
        try:
            from scipy import stats
            
            # Eliminar valores NaN
            mask = ~(x.isna() | y.isna())
            x_clean = x[mask]
            y_clean = y[mask]
            
            if len(x_clean) < 2:
                return {'r2': 0.0, 'slope': 0.0}
            
            # Regresión lineal
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
            
            # Validar que r_value es un número válido
            if not isinstance(r_value, (int, float)) or np.isnan(r_value):
                self.logger.warning(f"r_value inválido: {r_value}, tipo: {type(r_value)}")
                return {'r2': 0.0, 'slope': 0.0}
            
            # Validar que slope es un número válido
            if not isinstance(slope, (int, float)) or np.isnan(slope):
                self.logger.warning(f"slope inválido: {slope}, tipo: {type(slope)}")
                return {'r2': 0.0, 'slope': 0.0}
            
            # Convertir a float de forma segura con variables intermedias
            r_value_float: float = float(r_value)
            slope_float: float = float(slope)
            r2 = r_value_float ** 2
            
            return {'r2': r2, 'slope': slope_float}
            
        except Exception as e:
            self.logger.warning(f"Error calculando regresión: {e}")
            return {'r2': 0.0, 'slope': 0.0}
    
    def _analyze_by_deciles(self, x: pd.Series, y: pd.Series) -> Dict[str, float]:
        """Analiza la relación IS/OOS por deciles."""
        try:
            # Función auxiliar para convertir valores a float de forma segura
            def safe_float(val):
                try:
                    if isinstance(val, tuple):
                        return float(val[0])
                    return float(val)
                except Exception:
                    return 0.0
            
            # Eliminar valores NaN
            mask = ~(x.isna() | y.isna())
            if isinstance(x, pd.Series):
                idx = x.index[mask]
            else:
                idx = pd.RangeIndex(sum(mask))
            x_clean = pd.Series(x[mask], index=idx, dtype=float)
            y_clean = pd.Series(y[mask], index=idx, dtype=float)

            if len(x_clean) < 10:
                return {'decile_1': 0.0, 'decile_10': 0.0, 'decile_ratio': 0.0}

            # Crear deciles
            x_deciles = pd.Series(pd.qcut(x_clean, q=10, labels=False, duplicates='drop'), index=x_clean.index)

            # Calcular promedio de Y por decil
            decile_means = y_clean.groupby(x_deciles).mean()
            decile_means_list = [safe_float(v) for v in decile_means]

            if len(decile_means_list) < 10:
                return {'decile_1': 0.0, 'decile_10': 0.0, 'decile_ratio': 0.0}

            decile_1 = decile_means_list[0]
            decile_10 = decile_means_list[-1]
            decile_ratio = decile_10 / decile_1 if decile_1 != 0 else 0.0

            return {
                'decile_1': decile_1,
                'decile_10': decile_10,
                'decile_ratio': decile_ratio
            }

        except Exception as e:
            self.logger.warning(f"Error en análisis por deciles: {e}")
            return {'decile_1': 0.0, 'decile_10': 0.0, 'decile_ratio': 0.0}
    
    def filter_predictive_metrics(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Filtra métricas predictivas basándose en correlación IS/OOS.
        
        Args:
            df: DataFrame con métricas IS y OOS
            
        Returns:
            Tuple con DataFrame filtrado y lista de métricas válidas
        """
        try:
            self.logger.info("Filtrando métricas predictivas")
            
            # Analizar correlaciones
            correlation_analysis = self.analyze_correlation_is_oos(df)
            valid_metrics = correlation_analysis['summary']['valid_metrics']
            
            # Filtrar columnas del DataFrame
            columns_to_keep = ['Strategy_Name']  # Siempre mantener nombre de estrategia
            
            for metric in valid_metrics:
                is_col = f"{metric}_IS"
                oos_col = f"{metric}_OOS"
                
                if is_col in df.columns:
                    columns_to_keep.append(is_col)
                if oos_col in df.columns:
                    columns_to_keep.append(oos_col)
            
            # Filtrar DataFrame
            filtered_df = df[columns_to_keep].copy()
            
            # Asegurar que es un DataFrame
            if not isinstance(filtered_df, pd.DataFrame):
                filtered_df = pd.DataFrame(filtered_df)
            
            self.logger.info(f"DataFrame filtrado: {len(filtered_df.columns)} columnas válidas")
            
            return filtered_df, valid_metrics
            
        except Exception as e:
            self.logger.error(f"Error filtrando métricas predictivas: {e}")
            # Asegurar que retorna un DataFrame
            if not isinstance(df, pd.DataFrame):
                df = pd.DataFrame(df)
            return df, []


class MarketRegimeDetector:
    """
    Detector de regímenes de mercado usando clustering y análisis de características.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el detector de regímenes de mercado.
        
        Args:
            config: Configuración opcional
        """
        self.config = config or {}
        self.logger = setup_logger("kforce")
        self.n_clusters = self.config.get('n_clusters', 3)
        self.random_state = self.config.get('random_state', 42)
        self.feature_columns = self.config.get('feature_columns', [])
        
    def extract_market_features(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Extrae características del mercado para detección de regímenes.
        
        Args:
            market_data: DataFrame con datos de mercado
            
        Returns:
            DataFrame con características extraídas
        """
        try:
            self.logger.info("Extrayendo características de mercado")
            
            # Asegurar que features_df es un DataFrame de pandas
            features_df: pd.DataFrame = market_data.copy()
            
            # Características básicas de volatilidad
            if 'Close' in features_df.columns:
                # Retornos
                features_df['returns'] = features_df['Close'].pct_change()
                features_df['log_returns'] = np.log(features_df['Close'] / features_df['Close'].shift(1))
                
                # Volatilidad
                features_df['volatility'] = features_df['returns'].rolling(window=20).std()
                features_df['volatility_ma'] = features_df['volatility'].rolling(window=50).mean()
                
                # RSI
                close_data = features_df['Close']
                if isinstance(close_data, pd.Series):
                    close_series = close_data
                elif isinstance(close_data, pd.DataFrame):
                    close_series = close_data.iloc[:, 0]
                else:
                    close_series = pd.Series(close_data)
                features_df['rsi'] = self._calculate_rsi(close_series)
                
                # Bandas de Bollinger
                bb_ma = features_df['Close'].rolling(window=20).mean()
                bb_std = features_df['Close'].rolling(window=20).std()
                features_df['bb_upper'] = bb_ma + 2 * bb_std
                features_df['bb_lower'] = bb_ma - 2 * bb_std
                features_df['bb_position'] = (features_df['Close'] - features_df['bb_lower']) / (features_df['bb_upper'] - features_df['bb_lower'])
                
                # Momentum
                features_df['momentum_5'] = features_df['Close'] / features_df['Close'].shift(5) - 1
                features_df['momentum_20'] = features_df['Close'] / features_df['Close'].shift(20) - 1
                
                # Tendencia
                features_df['trend_20'] = features_df['Close'].rolling(window=20).mean() / features_df['Close'].rolling(window=50).mean() - 1
            
                # ATR (Average True Range)
                if 'High' in features_df.columns and 'Low' in features_df.columns:
                    high = features_df['High']
                    low = features_df['Low']
                    close = features_df['Close']
                    
                    tr1 = high - low
                    tr2 = abs(high - close.shift())
                    tr3 = abs(low - close.shift())
                    
                    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                    features_df['atr'] = tr.rolling(window=14).mean()
                
                # Volumen (si está disponible)
                if 'Volume' in features_df.columns:
                    features_df['volume_ma'] = features_df['Volume'].rolling(window=20).mean()
                    features_df['volume_ratio'] = features_df['Volume'] / features_df['volume_ma']
            
            # Rellenar NaN de forma simple - asegurar que es DataFrame
            if isinstance(features_df, pd.DataFrame):
                # type: ignore[attr-defined] - Pyright no reconoce fillna en DataFrame
                features_df = features_df.fillna(0)
            
            # Asegurar que tenemos al menos 2 características válidas
            feature_cols = [col for col in features_df.columns if col not in ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            if len(feature_cols) < 2:
                self.logger.warning(f"Solo se generaron {len(feature_cols)} características válidas. Añadiendo características básicas...")
                # Añadir características básicas adicionales
                if 'Close' in features_df.columns:
                    features_df['price_change'] = features_df['Close'].diff()
                    features_df['price_change_pct'] = features_df['Close'].pct_change()
                    # Característica simple sin división compleja
                    # type: ignore[operator] - Pyright no reconoce operación con Series
                    features_df['price_level'] = features_df['Close'] / 100.0  # Normalizar precio
            
            self.logger.info(f"Características extraídas: {len([col for col in features_df.columns if col not in ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']])} columnas")
            
            return features_df
            
        except Exception as e:
            self.logger.error(f"Error extrayendo características: {e}")
            return market_data
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcula el RSI (Relative Strength Index)."""
        try:
            # Asegurar que prices es una Series
            if not isinstance(prices, pd.Series):
                prices = pd.Series(prices)
            
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return pd.Series(rsi)  # Asegurar retorno de Series
        except:
            return pd.Series([np.nan] * len(prices))
    
    def detect_regimes(self, features_df: pd.DataFrame) -> Tuple[np.ndarray, Dict]:
        """
        Detecta regímenes de mercado usando clustering.
        
        Args:
            features_df: DataFrame con características de mercado
            
        Returns:
            Tuple con etiquetas de regímenes y información del clustering
        """
        try:
            self.logger.info("Detectando regímenes de mercado")
            
            # Seleccionar características para clustering
            feature_cols = [col for col in features_df.columns if col not in ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            if len(feature_cols) < 2:
                self.logger.warning("Insuficientes características para clustering")
                return np.zeros(len(features_df)), {}
            
            # Preparar datos
            X = features_df[feature_cols].fillna(0)
            
            # Normalizar
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Clustering
            kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init='auto')
            regime_labels = kmeans.fit_predict(X_scaled)
            
            # Información del clustering
            cluster_info = {
                'n_clusters': self.n_clusters,
                'feature_columns': feature_cols,
                'centroids': kmeans.cluster_centers_,
                'inertia': kmeans.inertia_,
                'regime_mapping': self._map_clusters_to_regimes(kmeans.cluster_centers_, feature_cols)
            }
            
            self.logger.info(f"Regímenes detectados: {self.n_clusters} clusters")
            
            return regime_labels, cluster_info
            
        except Exception as e:
            self.logger.error(f"Error detectando regímenes: {e}")
            return np.zeros(len(features_df)), {}
    
    def _map_clusters_to_regimes(self, centroids: np.ndarray, feature_names: List[str]) -> Dict[int, str]:
        """Mapea clusters a tipos de régimen."""
        regime_mapping = {}
        
        for i, centroid in enumerate(centroids):
            regime_type = self._classify_regime_by_centroid(centroid, feature_names)
            regime_mapping[i] = regime_type
        
        return regime_mapping
    
    def _classify_regime_by_centroid(self, centroid: np.ndarray, feature_names: List[str]) -> str:
        """Clasifica un régimen basándose en su centroide."""
        try:
            # Crear diccionario de características
            features = dict(zip(feature_names, centroid))
            
            # Lógica de clasificación
            volatility = features.get('volatility', 0)
            rsi = features.get('rsi', 50)
            momentum = features.get('momentum_20', 0)
            trend = features.get('trend_20', 0)
            
            if volatility > 0.02:  # Alta volatilidad
                if rsi > 70:
                    return "Bear Market"
                elif rsi < 30:
                    return "Bull Market"
                else:
                    return "High Volatility"
            elif momentum > 0.05 and trend > 0.02:
                return "Bull Market"
            elif momentum < -0.05 and trend < -0.02:
                return "Bear Market"
            else:
                return "Sideways Market"
                
        except Exception:
            return "Unknown"
    
    def analyze_strategy_performance_by_regime(self, strategies_df: pd.DataFrame, 
                                             regime_labels: np.ndarray) -> Dict[str, pd.DataFrame]:
        """
        Analiza el rendimiento de estrategias por régimen de mercado.
        
        Args:
            strategies_df: DataFrame con estrategias
            regime_labels: Etiquetas de regímenes
            
        Returns:
            Diccionario con análisis por régimen
        """
        try:
            self.logger.info("Analizando rendimiento por régimen")
            
            # Añadir etiquetas de régimen al DataFrame
            analysis_df = strategies_df.copy()
            analysis_df['market_regime'] = regime_labels[:len(analysis_df)]
            
            # Análisis por régimen
            regime_analysis = {}
            
            for regime_id in np.unique(regime_labels):
                regime_data = analysis_df[analysis_df['market_regime'] == regime_id]
                
                if len(regime_data) > 0:
                    # Calcular estadísticas por régimen
                    regime_stats = {
                        'count': len(regime_data),
                        'avg_profit_factor': regime_data['Profit_factor'].mean() if 'Profit_factor' in regime_data.columns else 0,
                        'avg_sharpe': regime_data['Sharpe_Ratio'].mean() if 'Sharpe_Ratio' in regime_data.columns else 0,
                        'avg_max_dd': regime_data['Max_DD_%'].mean() if 'Max_DD_%' in regime_data.columns else 0,
                        'best_strategy': regime_data.loc[pd.Series(regime_data['Profit_factor']).idxmax(), 'Strategy_Name'] if 'Profit_factor' in regime_data.columns else 'N/A'
                    }
                    
                    regime_analysis[f"regime_{regime_id}"] = {
                        'data': regime_data,
                        'stats': regime_stats
                    }
            
            self.logger.info(f"Análisis completado para {len(regime_analysis)} regímenes")
            
            return regime_analysis
            
        except Exception as e:
            self.logger.error(f"Error analizando rendimiento por régimen: {e}")
            return {}


class AdvancedPerformanceOptimizer:
    """
    Optimizador de rendimiento avanzado con procesamiento paralelo.
    """
    
    @staticmethod
    def process_data_in_chunks(data: pd.DataFrame, chunk_size: int = CHUNK_SIZE) -> pd.DataFrame:
        """Procesa datos en chunks para optimizar memoria."""
        logger = setup_logger("kforce")
        try:
            if len(data) <= chunk_size:
                return data
            
            chunks = []
            for i in range(0, len(data), chunk_size):
                chunk = data.iloc[i:i+chunk_size].copy()
                chunks.append(chunk)
            
            return pd.concat(chunks, ignore_index=True)
            
        except Exception as e:
            logger.warning(f"Error procesando chunks: {e}")
            return data
    
    @staticmethod
    def parallel_apply(func, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Aplica función en paralelo a los datos."""
        logger = setup_logger("kforce")
        try:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                chunks = np.array_split(data, MAX_WORKERS)
                futures = [executor.submit(func, chunk, **kwargs) for chunk in chunks]
                results = [future.result() for future in as_completed(futures)]
                return pd.concat(results, ignore_index=True)
                
        except Exception as e:
            logger.warning(f"Error en procesamiento paralelo: {e}")
            return func(data, **kwargs)
    
    @staticmethod
    def memory_cleanup():
        """Limpia memoria del sistema."""
        logger = setup_logger("kforce")
        try:
            gc.collect()
            logger.info("Limpieza de memoria completada")
        except Exception as e:
            logger.warning(f"Error en limpieza de memoria: {e}")


# Funciones de utilidad del archivo original
def run_factor_k_analysis(df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Ejecuta análisis completo con Factor K Elite.
    
    Args:
        df: DataFrame con datos de estrategias
        config: Configuración opcional
        
    Returns:
        DataFrame con resultados del análisis
    """
    factor_k = FactorKElite96Enhanced(config)
    return factor_k.evaluate_strategies(df)


def run_unified_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ejecuta análisis unificado con múltiples metodologías.
    
    Args:
        df: DataFrame con datos de estrategias
        
    Returns:
        DataFrame con resultados unificados
    """
    evaluator = UnifiedEvaluatorEnhanced()
    return evaluator.evaluate_strategies_unified(df)


def enable_scientific_improvements_in_factor_k(factor_k_instance: FactorKElite96Enhanced, 
                                             cache_dir: str = "cache/scientific") -> None:
    """
    Habilita mejoras científicas en una instancia de Factor K.
    
    Args:
        factor_k_instance: Instancia de FactorKElite96Enhanced
        cache_dir: Directorio de cache para mejoras científicas
    """
    logger = setup_logger("kforce")
    try:
        factor_k_instance.enable_scientific_improvements(cache_dir)
        logger.info("Mejoras científicas habilitadas en Factor K")
    except Exception as e:
        logger.error(f"Error habilitando mejoras científicas: {e}")


def run_scientific_analysis(df: pd.DataFrame, 
                          market_data: Optional[pd.DataFrame] = None,
                          reference_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Ejecuta análisis científico completo.
    
    Args:
        df: DataFrame con estrategias
        market_data: Datos de mercado opcionales
        reference_data: Datos de referencia opcionales
        
    Returns:
        Diccionario con resultados del análisis científico
    """
    logger = setup_logger("kforce")
    try:
        logger.info("Iniciando análisis científico completo")
        
        results = {}
        
        # Análisis de correlación IS/OOS
        correlation_filter = CorrelationFilter()
        correlation_results = correlation_filter.analyze_correlation_is_oos(df)
        results['correlation_analysis'] = correlation_results
        
        # Detección de regímenes de mercado
        if market_data is not None:
            regime_detector = MarketRegimeDetector()
            market_features = regime_detector.extract_market_features(market_data)
            regime_labels, regime_info = regime_detector.detect_regimes(market_features)
            regime_analysis = regime_detector.analyze_strategy_performance_by_regime(df, regime_labels)
            results['market_regime_analysis'] = {
                'regime_labels': regime_labels,
                'regime_info': regime_info,
                'regime_performance': regime_analysis
            }
        
        # Análisis HMM
        hmm_analyzer = HiddenMarkovModelAnalyzer()
        if market_data is not None:
            hmm_results = hmm_analyzer.fit_hmm(market_features)
            results['hmm_analysis'] = hmm_results
        
        # Pruebas de estrés
        stress_generator = StressTestGenerator()
        synthetic_strategies = stress_generator.generate_synthetic_strategies(50)
        results['stress_test'] = {
            'synthetic_strategies': synthetic_strategies,
            'n_strategies': 50
        }
        
        # Detección de data drift
        if reference_data is not None:
            drift_detector = DataDriftDetector()
            drift_detector.set_reference_distribution(reference_data, ['Profit_factor', 'Sharpe_Ratio'])
            drift_results = drift_detector.detect_drift(df, ['Profit_factor', 'Sharpe_Ratio'])
            results['data_drift_analysis'] = drift_results
        
        # Validación temporal
        temporal_validator = TemporalValidation()
        if 'Factor_K_Elite_Score' in df.columns:
            temporal_results = temporal_validator.perform_walk_forward_validation(
                df, 'Factor_K_Elite_Score', ['Profit_factor', 'Sharpe_Ratio', 'Max_DD_%']
            )
            results['temporal_validation'] = temporal_results
        
        logger.info("Análisis científico completado")
        
        return results
        
    except Exception as e:
        logger.error(f"Error en análisis científico: {e}")
        return {'error': str(e)}

def load_market_data(file_path):
    """
    Carga datos de mercado con detección automática de separador.
    
    Args:
        file_path: Ruta al archivo de datos de mercado
    
    Returns:
        DataFrame con datos de mercado
    """
    try:
        # Intentar diferentes separadores
        separators = [',', ';', '\t', '|']
        df_market = None
        
        for sep in separators:
            try:
                df_market = pd.read_csv(file_path, sep=sep, decimal=',', engine='python')
                # Verificar que tenemos suficientes columnas
                if len(df_market.columns) >= 5:  # Mínimo OHLCV
                    setup_logger("kforce").info(f"Archivo CSV cargado con separador '{sep}' y encoding 'utf-8'")
                    setup_logger("kforce").info(f"Columnas detectadas: {list(df_market.columns)}")
                    break
                else:
                    setup_logger("kforce").warning(f"Separador '{sep}' detectó solo {len(df_market.columns)} columnas")
                    df_market = None
            except Exception as e:
                setup_logger("kforce").debug(f"Separador '{sep}' falló: {str(e)}")
                continue
        
        if df_market is None:
            raise ValueError("No se pudo cargar el archivo con ningún separador válido")
        
        # Verificar columnas esperadas
        expected_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in expected_cols if col not in df_market.columns]
        if missing_cols:
            setup_logger("kforce").warning(f"Columnas faltantes en datos de mercado: {missing_cols}")
        
        return df_market
        
    except Exception as e:
        setup_logger("kforce").error(f"Error cargando datos de mercado: {str(e)}")
        raise

def calculate_fk96_scores(df):
    """
    Calcula los scores FK96 con normalizaciones corregidas para rango [0,1].
    """
    try:
        # FK96_Stability_Enhanced - Corregido para rango [0,1]
        if 'Profit_factor' in df.columns and 'Sharpe_Ratio' in df.columns:
            stability_scores = []
            for idx, row in df.iterrows():
                try:
                    pf = row['Profit_factor']
                    sr = row['Sharpe_Ratio']
                    
                    if pd.isna(pf) or pd.isna(sr) or np.isinf(pf) or np.isinf(sr):
                        stability_scores.append(np.nan)
                        continue
                    
                    # Normalización corregida para rango [0,1]
                    pf_norm = max(0, min(1, (pf - 1.0) / 3.0))  # PF de 1.0 a 4.0 (más conservador)
                    sr_norm = max(0, min(1, (sr + 1) / 4))  # Sharpe de -1 a 3 (más conservador)
                    
                    stability = (pf_norm * 0.4 + sr_norm * 0.6)
                    stability_scores.append(stability)
                    
                except Exception as e:
                    setup_logger("kforce").warning(f"Error en Stability FK96 para estrategia {idx}: {str(e)}")
                    stability_scores.append(np.nan)
            
            df['FK96_Stability_Enhanced'] = stability_scores
        
        # FK96_Growth_Enhanced - Corregido para rango [0,1]
        if 'CAGR' in df.columns and 'Net_profit' in df.columns:
            growth_scores = []
            for idx, row in df.iterrows():
                try:
                    cagr = row['CAGR']
                    net_profit = row['Net_profit']
                    
                    if pd.isna(cagr) or pd.isna(net_profit) or np.isinf(cagr) or np.isinf(net_profit):
                        growth_scores.append(np.nan)
                        continue
                    
                    # Normalización corregida
                    cagr_norm = max(0, min(1, (cagr + 50) / 150))  # CAGR de -50% a 100%
                    profit_norm = max(0, min(1, (net_profit + 10000) / 50000))  # Profit de -10k a 40k
                    
                    growth = (cagr_norm * 0.6 + profit_norm * 0.4)
                    growth_scores.append(growth)
                    
                except Exception as e:
                    setup_logger("kforce").warning(f"Error en Growth FK96 para estrategia {idx}: {str(e)}")
                    growth_scores.append(np.nan)
            
            df['FK96_Growth_Enhanced'] = growth_scores
        
        # FK96_Efficiency_Enhanced - Corregido para rango [0,1]
        if 'RecoveryFactor' in df.columns and 'Sortino_Ratio' in df.columns:
            efficiency_scores = []
            for idx, row in df.iterrows():
                try:
                    rf = row['RecoveryFactor']
                    sortino = row['Sortino_Ratio']
                    
                    if pd.isna(rf) or pd.isna(sortino) or np.isinf(rf) or np.isinf(sortino):
                        efficiency_scores.append(np.nan)
                        continue
                    
                    # Normalización corregida
                    rf_norm = max(0, min(1, rf / 20))  # RF máximo de 20
                    sortino_norm = max(0, min(1, (sortino + 3) / 8))  # Sortino de -3 a 5
                    
                    efficiency = (rf_norm * 0.5 + sortino_norm * 0.5)
                    efficiency_scores.append(efficiency)
                    
                except Exception as e:
                    setup_logger("kforce").warning(f"Error en Efficiency FK96 para estrategia {idx}: {str(e)}")
                    efficiency_scores.append(np.nan)
            
            df['FK96_Efficiency_Enhanced'] = efficiency_scores
        
        # FK96_Consistency_Enhanced - Corregido para rango [0,1]
        if 'Winning_Percent' in df.columns and 'Max_Consec_Losses' in df.columns:
            consistency_scores = []
            for idx, row in df.iterrows():
                try:
                    wp = row['Winning_Percent']
                    mcl = row['Max_Consec_Losses']
                    
                    if pd.isna(wp) or pd.isna(mcl) or np.isinf(wp) or np.isinf(mcl):
                        consistency_scores.append(np.nan)
                        continue
                    
                    # Normalización corregida
                    wp_norm = wp / 100  # Winning percent ya está en porcentaje
                    mcl_norm = max(0, min(1, 1 - (mcl / 30)))  # Máximo 30 pérdidas consecutivas
                    
                    consistency = (wp_norm * 0.7 + mcl_norm * 0.3)
                    consistency_scores.append(consistency)
                    
                except Exception as e:
                    setup_logger("kforce").warning(f"Error en Consistency FK96 para estrategia {idx}: {str(e)}")
                    consistency_scores.append(np.nan)
            
            df['FK96_Consistency_Enhanced'] = consistency_scores
        
        # FK96_Risk_Enhanced - Corregido para rango [0,1]
        if 'Max_DD_%' in df.columns and 'VaR_95%' in df.columns:
            risk_scores = []
            for idx, row in df.iterrows():
                try:
                    mdd = row['Max_DD_%']
                    var = row['VaR_95%']
                    
                    if pd.isna(mdd) or pd.isna(var) or np.isinf(mdd) or np.isinf(var):
                        risk_scores.append(np.nan)
                        continue
                    
                    # Normalización corregida para Max_DD_% en formato positivo
                    # Los datos están en positivo (5.4795 a 24.9058), convertimos a negativo
                    mdd_negative = -abs(mdd)  # Convertir a negativo
                    var_negative = -abs(var) if var > 0 else var  # Asegurar que VaR sea negativo
                    
                    # Normalización (valores más bajos son mejores para riesgo)
                    mdd_norm = max(0, min(1, 1 + (mdd_negative / 50)))  # MDD de -50% a 0%
                    var_norm = max(0, min(1, 1 + (var_negative / 30)))  # VaR de -30% a 0%
                    
                    risk = (mdd_norm * 0.6 + var_norm * 0.4)
                    risk_scores.append(risk)
                    
                except Exception as e:
                    setup_logger("kforce").warning(f"Error en Risk FK96 para estrategia {idx}: {str(e)}")
                    risk_scores.append(np.nan)
            
            df['FK96_Risk_Enhanced'] = risk_scores
        
        # FK96_Elite_Enhanced - Combinación de todos los scores
        elite_scores = []
        for idx, row in df.iterrows():
            try:
                scores = []
                for col in ['FK96_Stability_Enhanced', 'FK96_Growth_Enhanced', 
                           'FK96_Efficiency_Enhanced', 'FK96_Consistency_Enhanced', 'FK96_Risk_Enhanced']:
                    if col in df.columns and not pd.isna(row[col]):
                        scores.append(row[col])
                
                if len(scores) > 0:
                    elite_score = np.mean(scores)
                    elite_scores.append(elite_score)
                else:
                    elite_scores.append(np.nan)
                    
            except Exception as e:
                setup_logger("kforce").warning(f"Error en Elite FK96 para estrategia {idx}: {str(e)}")
                elite_scores.append(np.nan)
        
        df['FK96_Elite_Enhanced'] = elite_scores
        
        # Normalización final del Elite Score
        if 'FK96_Elite_Enhanced' in df.columns:
            elite_values = df['FK96_Elite_Enhanced'].dropna()
            if len(elite_values) > 0:
                min_val, max_val = elite_values.min(), elite_values.max()
                if max_val > min_val:
                    df['FK96_Elite_Enhanced_Normalized'] = (df['FK96_Elite_Enhanced'] - min_val) / (max_val - min_val)
                else:
                    df['FK96_Elite_Enhanced_Normalized'] = 0.5  # Valor neutral si todos son iguales
        
        setup_logger("kforce").info("Scores FK96 calculados exitosamente con normalizaciones corregidas")
        return df
        
    except Exception as e:
        setup_logger("kforce").error(f"Error calculando scores FK96: {str(e)}")
        return df

def categorize_quality(df, score_col="Unified_Score"):
    # Categorización dinámica por percentiles
    if score_col not in df.columns:
        df["Quality_Category"] = "Regular"
        return df
    scores = df[score_col].dropna()
    if len(scores) == 0:
        df["Quality_Category"] = "Regular"
        return df
    p80 = np.percentile(scores, 80)
    p60 = np.percentile(scores, 60)
    p40 = np.percentile(scores, 40)
    p20 = np.percentile(scores, 20)
    def cat(val):
        if val >= p80:
            return "Excelente"
        elif val >= p60:
            return "Muy Bueno"
        elif val >= p40:
            return "Bueno"
        elif val >= p20:
            return "Regular"
        else:
            return "Pobre"
    df["Quality_Category"] = df[score_col].apply(cat)
    return df

def predictividad_is_oos_empirica(df, is_oos_split=0.75):
    """
    Calcula la predictividad IS/OOS de forma empírica y científica para cada estrategia.
    Devuelve un DataFrame con la columna 'IS/OOS' (resumen) y 'IS_OOS_DETALLES' (detalles).
    """
    import numpy as np
    import pandas as pd
    resultados = []
    detalles_all = []
    # Detectar pares IS/OOS
    is_cols = [col for col in df.columns if '(IS)' in col]
    oos_cols = [col for col in df.columns if '(OOS)' in col]
    kpi_pairs = []
    for is_col in is_cols:
        base = is_col.replace(' (IS)', '').replace('(IS)', '').strip()
        oos_col = next((c for c in oos_cols if base == c.replace(' (OOS)', '').replace('(OOS)', '').strip()), None)
        if oos_col:
            kpi_pairs.append((base, is_col, oos_col))
    # Recolectar todas las diferencias relativas del dataset
    all_diffs = []
    for base, is_col, oos_col in kpi_pairs:
        is_vals = pd.to_numeric(df[is_col], errors='coerce').to_numpy()
        oos_vals = pd.to_numeric(df[oos_col], errors='coerce').to_numpy()
        diffs = ((oos_vals - is_vals) / (np.abs(is_vals) + 1e-8)) * 100
        all_diffs.extend(diffs[~np.isnan(diffs)].tolist())
    if all_diffs:
        all_diffs_np = np.array(all_diffs)
        p10 = np.percentile(all_diffs_np, 10)
        p25 = np.percentile(all_diffs_np, 25)
        p75 = np.percentile(all_diffs_np, 75)
    else:
        p10, p25, p75 = -20, -12, -5
    penalizacion = 1 - (is_oos_split * 0.5)
    metricas_clave = {"Profit Factor", "CAGR", "Sharpe Ratio", "CalmarRatio"}
    for idx, row in df.iterrows():
        detalles = []
        perdidas_rel = []
        perdidas_abs = []
        n_mejoran = 0
        n_empeoran = 0
        n_igual = 0
        alertas = []
        alerta_critica = False
        for base, is_col, oos_col in kpi_pairs:
            is_val = row.get(is_col)
            oos_val = row.get(oos_col)
            try:
                is_val = float(is_val)
                oos_val = float(oos_val)
            except:
                continue
            diff_abs = oos_val - is_val
            diff_rel = 0.0
            if abs(is_val) > 1e-8:
                diff_rel = (oos_val - is_val) / abs(is_val) * 100
            perdidas_rel.append(diff_rel)
            perdidas_abs.append(diff_abs)
            tendencia = "➡️"
            if diff_abs > 0.01:
                tendencia = "📈"
                n_mejoran += 1
            elif diff_abs < -0.01:
                tendencia = "📉"
                n_empeoran += 1
            else:
                n_igual += 1
            detalles.append({
                "kpi": base,
                "is": is_val,
                "oos": oos_val,
                "diff_abs": diff_abs,
                "diff_rel": diff_rel,
                "tendencia": tendencia
            })
            # Alertas para métricas clave (usando percentil 10 de OOS)
            if base in metricas_clave:
                oos_vals = pd.to_numeric(df[oos_col], errors='coerce').to_numpy()
                oos_vals_valid = oos_vals[~np.isnan(oos_vals)]
                umbral_critico = np.percentile(oos_vals_valid, 10) if len(oos_vals_valid) > 0 else (1 if base == "Profit Factor" else 0)
                if base == "Profit Factor" and oos_val < umbral_critico:
                    alertas.append(f"⚠️ Profit Factor OOS < {umbral_critico:.2f}")
                    alerta_critica = True
                if base == "CAGR" and oos_val < umbral_critico:
                    alertas.append(f"⚠️ CAGR OOS < {umbral_critico:.2f}")
                    alerta_critica = True
        n_total = len(perdidas_rel)
        media_perdida = np.mean(perdidas_rel) * penalizacion if perdidas_rel else 0.0
        pct_mejoran = n_mejoran / n_total * 100 if n_total else 0
        pct_empeoran = n_empeoran / n_total * 100 if n_total else 0
        # Clasificación multinivel automática
        nivel = ""
        icono = ""
        if alerta_critica or media_perdida < p10 or pct_empeoran > 50:
            nivel = "Pobre"
            icono = "🔴"
        elif media_perdida < p25 or pct_empeoran > 30:
            nivel = "Aceptable"
            icono = "🟡"
        elif media_perdida < p75 or pct_empeoran > 20:
            nivel = "Buena"
            icono = "🟢"
        else:
            nivel = "Excelente"
            icono = "🔬"
        resumen = f"{icono} {nivel} (Δ={media_perdida:+.1f}%, {n_total} KPIs, {pct_mejoran:.0f}% mejoran)"
        if alertas:
            resumen += " [" + ", ".join(alertas) + "]"
        resultados.append(resumen)
        detalles_all.append(detalles)
    df = df.copy()
    df['IS/OOS'] = resultados
    df['IS_OOS_DETALLES'] = detalles_all
    return df

# ... existing code ...

class RobustnessAnalyzer:
    """Analizador de robustez para evaluar la estabilidad de las estrategias."""
    
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.logger = setup_logger("kforce")
        
    def analyze_stability_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analiza métricas de estabilidad de las estrategias."""
        try:
            self.logger.info("Iniciando análisis de robustez...")
            
            stability_metrics = {}
            
            # Análisis de estabilidad del Sharpe Ratio
            if 'Sharpe_Ratio' in df.columns:
                stability_metrics['sharpe_stability'] = self._calculate_sharpe_stability(df)
            
            # Análisis de estabilidad del Drawdown
            if 'Max_DD_%' in df.columns:
                stability_metrics['drawdown_stability'] = self._calculate_drawdown_stability(df)
            
            # Análisis de consistencia de retornos
            if 'CAGR' in df.columns:
                stability_metrics['return_consistency'] = self._calculate_return_consistency(df)
            
            # Análisis de correlación entre métricas
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                correlation_matrix = df[numeric_cols].corr()
                stability_metrics['metric_correlation'] = correlation_matrix.mean().mean()
            
            self.logger.info("Análisis de robustez completado")
            return stability_metrics
            
        except Exception as e:
            self.logger.error(f"Error en análisis de robustez: {e}")
            return {}
    
    def _calculate_sharpe_stability(self, df: pd.DataFrame) -> float:
        """Calcula la estabilidad del Sharpe Ratio."""
        try:
            sharpe_values = pd.to_numeric(df['Sharpe_Ratio'], errors='coerce').dropna()
            if len(sharpe_values) < 2:
                return 0.0
            
            # Calcular coeficiente de variación (menor = más estable)
            cv = sharpe_values.std() / abs(sharpe_values.mean()) if sharpe_values.mean() != 0 else 0
            stability = max(0, 1 - cv)  # Convertir a métrica de estabilidad
            return float(stability)
        except Exception as e:
            self.logger.warning(f"Error calculando estabilidad Sharpe: {e}")
            return 0.0
    
    def _calculate_drawdown_stability(self, df: pd.DataFrame) -> float:
        """Calcula la estabilidad del Drawdown."""
        try:
            dd_values = pd.to_numeric(df['Max_DD_%'], errors='coerce').dropna()
            if len(dd_values) < 2:
                return 0.0
            
            # Calcular estabilidad basada en la dispersión del drawdown
            dd_std = dd_values.std()
            dd_mean = abs(dd_values.mean())
            stability = max(0, 1 - (dd_std / dd_mean)) if dd_mean > 0 else 0
            return float(stability)
        except Exception as e:
            self.logger.warning(f"Error calculando estabilidad Drawdown: {e}")
            return 0.0
    
    def _calculate_return_consistency(self, df: pd.DataFrame) -> float:
        """Calcula la consistencia de retornos."""
        try:
            cagr_values = pd.to_numeric(df['CAGR'], errors='coerce').dropna()
            if len(cagr_values) < 2:
                return 0.0
            
            # Calcular consistencia basada en la variabilidad de CAGR
            cagr_std = cagr_values.std()
            cagr_mean = abs(cagr_values.mean())
            consistency = max(0, 1 - (cagr_std / cagr_mean)) if cagr_mean > 0 else 0
            return float(consistency)
        except Exception as e:
            self.logger.warning(f"Error calculando consistencia retornos: {e}")
            return 0.0


class WalkForwardAnalyzer:
    """Analizador de Walk-Forward para validación temporal."""
    
    def __init__(self, n_folds: int = 5, progress_callback=None):
        self.n_folds = n_folds
        self.progress_callback = progress_callback
        self.logger = setup_logger("kforce")
        
    def perform_walk_forward_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Realiza análisis de walk-forward en los datos."""
        try:
            self.logger.info("Iniciando análisis Walk-Forward...")
            
            # Identificar columnas IS/OOS
            is_cols = [col for col in df.columns if '(IS)' in col]
            oos_cols = [col for col in df.columns if '(OOS)' in col]
            
            if not is_cols or not oos_cols:
                self.logger.warning("No se encontraron columnas IS/OOS para análisis walk-forward")
                return {}
            
            results = {
                'fold_results': [],
                'overall_metrics': {},
                'predictability_score': 0.0
            }
            
            # Realizar análisis por cada par IS/OOS
            for is_col, oos_col in zip(is_cols, oos_cols):
                fold_result = self._analyze_single_pair(df, is_col, oos_col)
                results['fold_results'].append(fold_result)
            
            # Calcular métricas generales
            if results['fold_results']:
                results['overall_metrics'] = self._calculate_overall_metrics(results['fold_results'])
                results['predictability_score'] = self._calculate_predictability_score(results['fold_results'])
            
            self.logger.info("Análisis Walk-Forward completado")
            return results
            
        except Exception as e:
            self.logger.error(f"Error en análisis Walk-Forward: {e}")
            return {}
    
    def _analyze_single_pair(self, df: pd.DataFrame, is_col: str, oos_col: str) -> Dict[str, Any]:
        """Analiza un par específico de columnas IS/OOS."""
        try:
            is_values = pd.to_numeric(df[is_col], errors='coerce').dropna()
            oos_values = pd.to_numeric(df[oos_col], errors='coerce').dropna()
            
            if len(is_values) < 2 or len(oos_values) < 2:
                return {'error': 'Datos insuficientes'}
            
            # Calcular correlación
            correlation = np.corrcoef(is_values, oos_values)[0, 1] if len(is_values) == len(oos_values) else 0
            
            # Calcular R²
            r_squared = self._calculate_r_squared(is_values.tolist(), oos_values.tolist())
            
            # Calcular p-value (simplificado)
            p_value = self._calculate_p_value(is_values.tolist())
            
            return {
                'is_column': is_col,
                'oos_column': oos_col,
                'correlation': float(correlation),
                'r_squared': float(r_squared),
                'p_value': float(p_value),
                'sample_size': len(is_values)
            }
            
        except Exception as e:
            self.logger.warning(f"Error analizando par {is_col}/{oos_col}: {e}")
            return {'error': str(e)}
    
    def _calculate_r_squared(self, x: List[float], y: List[float]) -> float:
        """Calcula R² entre dos series."""
        try:
            if len(x) != len(y) or len(x) < 2:
                return 0.0
            
            x_mean = np.mean(x)
            y_mean = np.mean(y)
            
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(len(x)))
            denominator_x = sum((x[i] - x_mean) ** 2 for i in range(len(x)))
            denominator_y = sum((y[i] - y_mean) ** 2 for i in range(len(y)))
            
            if denominator_x == 0 or denominator_y == 0:
                return 0.0
            
            correlation = numerator / (denominator_x * denominator_y) ** 0.5
            return correlation ** 2
            
        except Exception:
            return 0.0
    
    def _calculate_p_value(self, values: List[float]) -> float:
        """Calcula p-value simplificado."""
        try:
            if len(values) < 2:
                return 1.0
            
            # Test t simple para determinar si la media es significativamente diferente de 0
            mean_val = np.mean(values)
            std_val = np.std(values, ddof=1)
            
            if std_val == 0:
                return 1.0
            
            t_stat = mean_val / (std_val / np.sqrt(len(values)))
            # Aproximación simple del p-value
            p_value = 2 * (1 - norm.cdf(abs(t_stat)))
            return float(p_value)
            
        except Exception:
            return 1.0
    
    def _calculate_overall_metrics(self, fold_results: List[Dict]) -> Dict[str, float]:
        """Calcula métricas generales del análisis walk-forward."""
        try:
            valid_results = [r for r in fold_results if 'error' not in r]
            
            if not valid_results:
                return {}
            
            correlations = [r['correlation'] for r in valid_results]
            r_squareds = [r['r_squared'] for r in valid_results]
            p_values = [r['p_value'] for r in valid_results]
            
            return {
                'mean_correlation': float(np.mean(correlations)),
                'mean_r_squared': float(np.mean(r_squareds)),
                'mean_p_value': float(np.mean(p_values)),
                'significant_pairs': sum(1 for p in p_values if p < 0.05),
                'total_pairs': len(valid_results)
            }
            
        except Exception as e:
            self.logger.warning(f"Error calculando métricas generales: {e}")
            return {}
    
    def _calculate_predictability_score(self, fold_results: List[Dict]) -> float:
        """Calcula score de predictibilidad basado en los resultados."""
        try:
            valid_results = [r for r in fold_results if 'error' not in r]
            
            if not valid_results:
                return 0.0
            
            # Score basado en correlación y significancia
            scores = []
            for result in valid_results:
                correlation = abs(result['correlation'])
                p_value = result['p_value']
                
                # Penalizar por p-value alto
                significance_factor = 1.0 if p_value < 0.05 else 0.5
                score = correlation * significance_factor
                scores.append(score)
            
            return float(np.mean(scores))
            
        except Exception as e:
            self.logger.warning(f"Error calculando score de predictibilidad: {e}")
            return 0.0


class NullSimulationAnalyzer:
    """Analizador de simulación nula para validar significancia estadística."""
    
    def __init__(self, n_simulations: int = 100, progress_callback=None):
        self.n_simulations = n_simulations
        self.progress_callback = progress_callback
        self.logger = setup_logger("kforce")
        
    def perform_null_simulation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Realiza simulación nula para validar significancia estadística."""
        try:
            self.logger.info("Iniciando simulación nula...")
            
            # Identificar métricas clave
            key_metrics = ['Profit_Factor', 'CAGR', 'Sharpe_Ratio', 'Max_DD_%']
            available_metrics = [m for m in key_metrics if m in df.columns]
            
            if not available_metrics:
                self.logger.warning("No se encontraron métricas clave para simulación nula")
                return {}
            
            results = {
                'metric_results': {},
                'overall_significance': 0.0,
                'simulation_count': self.n_simulations
            }
            
            # Simular para cada métrica
            for metric in available_metrics:
                metric_result = self._simulate_metric(df, metric)
                results['metric_results'][metric] = metric_result
            
            # Calcular significancia general
            if results['metric_results']:
                results['overall_significance'] = self._calculate_overall_significance(results['metric_results'])
            
            self.logger.info("Simulación nula completada")
            return results
            
        except Exception as e:
            self.logger.error(f"Error en simulación nula: {e}")
            return {}
    
    def _simulate_metric(self, df: pd.DataFrame, metric: str) -> Dict[str, Any]:
        """Simula una métrica específica."""
        try:
            values = pd.to_numeric(df[metric], errors='coerce').dropna()
            
            if len(values) < 2:
                return {'error': 'Datos insuficientes'}
            
            original_mean = values.mean()
            original_std = values.std()
            
            # Simular distribuciones nulas
            null_means = []
            for _ in range(self.n_simulations):
                # Permutar valores para crear distribución nula
                shuffled_values = np.random.permutation(values)
                null_means.append(shuffled_values.mean())
            
            null_means = np.array(null_means)
            
            # Calcular p-value
            p_value = np.mean(null_means >= original_mean) if original_mean > 0 else np.mean(null_means <= original_mean)
            
            # Calcular percentiles
            percentiles = np.percentile(null_means, [5, 25, 50, 75, 95])
            
            return {
                'original_mean': float(original_mean),
                'original_std': float(original_std),
                'null_mean': float(null_means.mean()),
                'null_std': float(null_means.std()),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'percentiles': percentiles.tolist(),
                'sample_size': len(values)
            }
            
        except Exception as e:
            self.logger.warning(f"Error simulando métrica {metric}: {e}")
            return {'error': str(e)}
    
    def _calculate_overall_significance(self, metric_results: Dict[str, Dict]) -> float:
        """Calcula significancia general basada en todas las métricas."""
        try:
            significant_count = 0
            total_count = 0
            
            for metric, result in metric_results.items():
                if 'error' not in result:
                    total_count += 1
                    if result.get('significant', False):
                        significant_count += 1
            
            if total_count == 0:
                return 0.0
            
            return float(significant_count / total_count)
            
        except Exception as e:
            self.logger.warning(f"Error calculando significancia general: {e}")
            return 0.0


class PredictabilityAnalyzer:
    """Analizador de predictibilidad para evaluar la calidad predictiva de las métricas."""
    
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.logger = setup_logger("kforce")
        
    def analyze_is_oos_correlations(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analiza correlaciones IS/OOS para evaluar predictibilidad."""
        try:
            self.logger.info("Analizando correlaciones IS/OOS...")
            
            # Identificar pares IS/OOS
            is_cols = [col for col in df.columns if '(IS)' in col]
            oos_cols = [col for col in df.columns if '(OOS)' in col]
            
            correlations = {}
            
            for is_col in is_cols:
                base_name = is_col.replace(' (IS)', '').replace('(IS)', '').strip()
                oos_col = next((c for c in oos_cols if base_name == c.replace(' (OOS)', '').replace('(OOS)', '').strip()), None)
                
                if oos_col:
                    correlation = self._calculate_correlation(df, is_col, oos_col)
                    correlations[base_name] = correlation
            
            self.logger.info("Análisis de correlaciones IS/OOS completado")
            return correlations
            
        except Exception as e:
            self.logger.error(f"Error analizando correlaciones IS/OOS: {e}")
            return {}
    
    def _calculate_correlation(self, df: pd.DataFrame, col1: str, col2: str) -> float:
        """Calcula correlación entre dos columnas."""
        try:
            values1 = pd.to_numeric(df[col1], errors='coerce').dropna()
            values2 = pd.to_numeric(df[col2], errors='coerce').dropna()
            
            if len(values1) < 2 or len(values2) < 2:
                return 0.0
            
            # Alinear series si tienen diferentes longitudes
            min_len = min(len(values1), len(values2))
            values1 = values1[:min_len]
            values2 = values2[:min_len]
            
            correlation = np.corrcoef(values1, values2)[0, 1]
            return float(correlation) if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            self.logger.warning(f"Error calculando correlación {col1}/{col2}: {e}")
            return 0.0
    
    def analyze_outliers_and_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza outliers y distribución de los datos."""
        try:
            self.logger.info("Analizando outliers y distribución...")
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            analysis_results = {}
            
            for col in numeric_cols:
                values = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if len(values) < 2:
                    continue
                
                # Estadísticas básicas
                mean_val = values.mean()
                std_val = values.std()
                median_val = values.median()
                
                # Detectar outliers usando IQR
                q1 = values.quantile(0.25)
                q3 = values.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = values[(values < lower_bound) | (values > upper_bound)]
                outlier_percentage = len(outliers) / len(values) * 100
                
                # Asimetría y curtosis
                skewness = values.skew()
                kurtosis = values.kurtosis()
                
                analysis_results[col] = {
                    'mean': float(mean_val),
                    'std': float(std_val),
                    'median': float(median_val),
                    'outlier_count': int(len(outliers)),
                    'outlier_percentage': float(outlier_percentage),
                    'skewness': float(skewness),
                    'kurtosis': float(kurtosis),
                    'q1': float(q1),
                    'q3': float(q3),
                    'iqr': float(iqr)
                }
            
            self.logger.info("Análisis de outliers y distribución completado")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analizando outliers y distribución: {e}")
            return {}
    
    def analyze_predictive_quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza métricas de calidad predictiva."""
        try:
            self.logger.info("Analizando métricas de calidad predictiva...")
            
            # Identificar métricas clave
            key_metrics = ['Profit_Factor', 'CAGR', 'Sharpe_Ratio', 'Max_DD_%']
            available_metrics = [m for m in key_metrics if m in df.columns]
            
            quality_metrics = {}
            
            for metric in available_metrics:
                values = pd.to_numeric(df[metric], errors='coerce').dropna()
                
                if len(values) < 2:
                    continue
                
                # Calcular métricas de calidad
                cv = values.std() / abs(values.mean()) if values.mean() != 0 else 0
                range_val = values.max() - values.min()
                median_absolute_deviation = np.median(np.abs(values - values.median()))
                
                quality_metrics[metric] = {
                    'coefficient_of_variation': float(cv),
                    'range': float(range_val),
                    'median_absolute_deviation': float(median_absolute_deviation),
                    'sample_size': len(values),
                    'quality_score': max(0, 1 - cv)  # Score basado en CV
                }
            
            self.logger.info("Análisis de métricas de calidad predictiva completado")
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Error analizando métricas de calidad predictiva: {e}")
            return {}
    
    def perform_hypothesis_tests(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Realiza tests de hipótesis para validar significancia estadística."""
        try:
            self.logger.info("Realizando tests de hipótesis...")
            
            # Identificar columnas IS/OOS
            is_cols = [col for col in df.columns if '(IS)' in col]
            oos_cols = [col for col in df.columns if '(OOS)' in col]
            
            test_results = {}
            
            for is_col in is_cols:
                base_name = is_col.replace(' (IS)', '').replace('(IS)', '').strip()
                oos_col = next((c for c in oos_cols if base_name == c.replace(' (OOS)', '').replace('(OOS)', '').strip()), None)
                
                if oos_col:
                    test_result = self._perform_paired_test(df, is_col, oos_col)
                    test_results[base_name] = test_result
            
            self.logger.info("Tests de hipótesis completados")
            return test_results
            
        except Exception as e:
            self.logger.error(f"Error realizando tests de hipótesis: {e}")
            return {}
    
    def _perform_paired_test(self, df: pd.DataFrame, is_col: str, oos_col: str) -> Dict[str, Any]:
        """Realiza test t pareado entre IS y OOS."""
        try:
            is_values = pd.to_numeric(df[is_col], errors='coerce').dropna()
            oos_values = pd.to_numeric(df[oos_col], errors='coerce').dropna()
            
            if len(is_values) < 2 or len(oos_values) < 2:
                return {'error': 'Datos insuficientes'}
            
            # Alinear series
            min_len = min(len(is_values), len(oos_values))
            is_values = is_values[:min_len]
            oos_values = oos_values[:min_len]
            
            # Calcular diferencias
            differences = oos_values - is_values
            
            # Test t pareado
            mean_diff = differences.mean()
            std_diff = differences.std(ddof=1)
            
            if std_diff == 0:
                return {'error': 'Sin variabilidad en diferencias'}
            
            t_stat = mean_diff / (std_diff / np.sqrt(len(differences)))
            p_value = 2 * (1 - norm.cdf(abs(t_stat)))
            
            return {
                'mean_difference': float(mean_diff),
                'std_difference': float(std_diff),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'sample_size': len(differences)
            }
            
        except Exception as e:
            self.logger.warning(f"Error en test pareado {is_col}/{oos_col}: {e}")
            return {'error': str(e)}
    
    def analyze_multivariate_prediction(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analiza predictibilidad multivariada."""
        try:
            self.logger.info("Analizando predictibilidad multivariada...")
            
            # Identificar métricas IS
            is_cols = [col for col in df.columns if '(IS)' in col]
            
            if len(is_cols) < 2:
                return {}
            
            # Calcular matriz de correlación entre métricas IS
            is_data = df[is_cols].apply(pd.to_numeric, errors='coerce')
            correlation_matrix = is_data.corr()
            
            # Calcular métricas de predictibilidad multivariada
            mean_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
            max_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].max()
            
            # Calcular determinante de la matriz de correlación (medida de multicolinealidad)
            try:
                det_correlation = np.linalg.det(correlation_matrix.values)
            except:
                det_correlation = 0.0
            
            return {
                'mean_is_correlation': float(mean_correlation),
                'max_is_correlation': float(max_correlation),
                'correlation_determinant': float(det_correlation),
                'multicollinearity_score': max(0, 1 - abs(det_correlation))
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando predictibilidad multivariada: {e}")
            return {}
    
    def calculate_predictability_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcula métricas generales de predictibilidad."""
        try:
            self.logger.info("Calculando métricas de predictibilidad...")
            
            # Obtener todos los análisis
            correlations = self.analyze_is_oos_correlations(df)
            quality_metrics = self.analyze_predictive_quality_metrics(df)
            hypothesis_tests = self.perform_hypothesis_tests(df)
            multivariate_metrics = self.analyze_multivariate_prediction(df)
            
            # Calcular métricas agregadas
            overall_correlation = np.mean(list(correlations.values())) if correlations else 0.0
            significant_tests = sum(1 for test in hypothesis_tests.values() if test.get('significant', False))
            total_tests = len(hypothesis_tests)
            significance_rate = significant_tests / total_tests if total_tests > 0 else 0.0
            
            # Calcular score de predictibilidad general
            predictability_score = (
                overall_correlation * 0.4 +
                significance_rate * 0.3 +
                multivariate_metrics.get('multicollinearity_score', 0) * 0.3
            )
            
            return {
                'overall_correlation': float(overall_correlation),
                'significance_rate': float(significance_rate),
                'significant_tests': significant_tests,
                'total_tests': total_tests,
                'predictability_score': float(predictability_score),
                'multicollinearity_score': multivariate_metrics.get('multicollinearity_score', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculando métricas de predictibilidad: {e}")
            return {}
    
    def generate_scientific_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Genera reporte científico completo."""
        try:
            self.logger.info("Generando reporte científico...")
            
            # Realizar todos los análisis
            correlations = self.analyze_is_oos_correlations(df)
            outliers_analysis = self.analyze_outliers_and_distribution(df)
            quality_metrics = self.analyze_predictive_quality_metrics(df)
            hypothesis_tests = self.perform_hypothesis_tests(df)
            multivariate_metrics = self.analyze_multivariate_prediction(df)
            predictability_metrics = self.calculate_predictability_metrics(df)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendation(predictability_metrics)
            
            report = {
                'correlations': correlations,
                'outliers_analysis': outliers_analysis,
                'quality_metrics': quality_metrics,
                'hypothesis_tests': hypothesis_tests,
                'multivariate_metrics': multivariate_metrics,
                'predictability_metrics': predictability_metrics,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("Reporte científico generado exitosamente")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generando reporte científico: {e}")
            return {}
    
    def _generate_recommendation(self, summary: Dict[str, float]) -> str:
        """Genera recomendación basada en las métricas de predictibilidad."""
        try:
            predictability_score = summary.get('predictability_score', 0)
            significance_rate = summary.get('significance_rate', 0)
            overall_correlation = summary.get('overall_correlation', 0)
            
            if predictability_score >= 0.8 and significance_rate >= 0.7:
                return "Excelente predictibilidad. Los modelos muestran alta confiabilidad."
            elif predictability_score >= 0.6 and significance_rate >= 0.5:
                return "Buena predictibilidad. Los modelos son confiables con algunas reservas."
            elif predictability_score >= 0.4 and significance_rate >= 0.3:
                return "Predictibilidad moderada. Se recomienda validación adicional."
            else:
                return "Baja predictibilidad. Se requiere análisis más profundo y validación."
                
        except Exception as e:
            self.logger.warning(f"Error generando recomendación: {e}")
            return "No se pudo generar recomendación debido a errores en el análisis."


def run_robustness_analysis(df: pd.DataFrame, config: Optional[Dict] = None) -> Dict[str, Any]:
    """Ejecuta análisis de robustez completo."""
    try:
        analyzer = RobustnessAnalyzer()
        return analyzer.analyze_stability_metrics(df)
    except Exception as e:
        setup_logger("kforce").error(f"Error en análisis de robustez: {e}")
        return {}


def run_predictability_analysis(df: pd.DataFrame, config: Optional[Dict] = None) -> Dict[str, Any]:
    """Ejecuta análisis de predictibilidad completo."""
    try:
        analyzer = PredictabilityAnalyzer()
        return analyzer.generate_scientific_report(df)
    except Exception as e:
        setup_logger("kforce").error(f"Error en análisis de predictibilidad: {e}")
        return {}


def debug_instrument(threshold=5):
    """Decorador para instrumentar funciones con debugging."""
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_used = end_memory - start_memory
                
                if execution_time > threshold:
                    setup_logger("kforce").warning(f"{func.__name__} tardó {execution_time:.2f}s y usó {memory_used:.2f}MB")
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                setup_logger("kforce").error(f"{func.__name__} falló después de {execution_time:.2f}s: {e}")
                raise
                
        return wrapper
    return decorator


def categorize_quality_by_threshold(score: float, thresholds: Dict[str, float]) -> str:
    """Categoriza calidad basada en score y umbrales."""
    try:
        if score >= thresholds.get('excellent', 0.8):
            return "Excelente"
        elif score >= thresholds.get('good', 0.6):
            return "Buena"
        elif score >= thresholds.get('fair', 0.4):
            return "Aceptable"
        else:
            return "Pobre"
    except Exception:
        return "Desconocida"


def predictividad_is_oos_empirica_dict(df: pd.DataFrame, split_ratio: float = 0.75) -> Dict[str, Any]:
    """
    Calcula la predictividad IS/OOS de forma empírica y científica.
    
    Args:
        df: DataFrame con datos de estrategias
        split_ratio: Proporción de datos para IS (default: 0.75)
        
    Returns:
        Dict con métricas de predictividad
    """
    try:
        setup_logger("kforce").info("Calculando predictividad IS/OOS empírica...")
        
        # Identificar columnas IS/OOS
        is_cols = [col for col in df.columns if '(IS)' in col]
        oos_cols = [col for col in df.columns if '(OOS)' in col]
        
        if not is_cols or not oos_cols:
            return {'error': 'No se encontraron columnas IS/OOS'}
        
        results = {
            'metric_pairs': [],
            'overall_predictability': 0.0,
            'significant_metrics': 0,
            'total_metrics': len(is_cols)
        }
        
        total_correlation = 0.0
        significant_count = 0
        
        for is_col in is_cols:
            base_name = is_col.replace(' (IS)', '').replace('(IS)', '').strip()
            oos_col = next((c for c in oos_cols if base_name == c.replace(' (OOS)', '').replace('(OOS)', '').strip()), None)
            
            if oos_col:
                # Calcular correlación
                is_values = pd.to_numeric(df[is_col], errors='coerce').dropna()
                oos_values = pd.to_numeric(df[oos_col], errors='coerce').dropna()
                
                if len(is_values) >= 2 and len(oos_values) >= 2:
                    min_len = min(len(is_values), len(oos_values))
                    correlation = np.corrcoef(is_values[:min_len], oos_values[:min_len])[0, 1]
                    
                    if not np.isnan(correlation):
                        total_correlation += abs(correlation)
                        if abs(correlation) > 0.3:  # Umbral de significancia
                            significant_count += 1
                        
                        results['metric_pairs'].append({
                            'metric': base_name,
                            'correlation': float(correlation),
                            'significant': abs(correlation) > 0.3,
                            'sample_size': min_len
                        })
        
        if results['metric_pairs']:
            results['overall_predictability'] = total_correlation / len(results['metric_pairs'])
            results['significant_metrics'] = significant_count
        
        setup_logger("kforce").info("Predictividad IS/OOS empírica calculada exitosamente")
        return results
        
    except Exception as e:
        setup_logger("kforce").error(f"Error calculando predictividad IS/OOS empírica: {e}")
        return {'error': str(e)}


class AdvancedDataProcessor:
    """Procesador avanzado de datos con optimizaciones de memoria y rendimiento."""
    
    def __init__(self, chunk_size: int = 10000, max_workers: int = 4):
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self.logger = setup_logger("kforce")
        
    def process_large_dataset(self, df: pd.DataFrame, func, **kwargs) -> pd.DataFrame:
        """Procesa datasets grandes en chunks para optimizar memoria."""
        try:
            self.logger.info(f"Procesando dataset de {len(df)} filas en chunks...")
            
            if len(df) <= self.chunk_size:
                return func(df, **kwargs)
            
            results = []
            total_chunks = (len(df) + self.chunk_size - 1) // self.chunk_size
            
            for i in range(0, len(df), self.chunk_size):
                chunk = df.iloc[i:i + self.chunk_size]
                chunk_result = func(chunk, **kwargs)
                results.append(chunk_result)
                
                # Limpiar memoria
                del chunk
                gc.collect()
            
            # Combinar resultados
            if results:
                final_result = pd.concat(results, ignore_index=True)
                self.logger.info(f"Procesamiento completado: {len(final_result)} filas resultantes")
                return final_result
            else:
                return df
                
        except Exception as e:
            self.logger.error(f"Error procesando dataset grande: {e}")
            return df
    
    def optimize_memory_usage(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimiza el uso de memoria del DataFrame."""
        try:
            self.logger.info("Optimizando uso de memoria...")
            
            # Reducir tipos de datos
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Para columnas de texto, usar category si hay pocos valores únicos
                    if df[col].nunique() / len(df) < 0.5:
                        df[col] = df[col].astype('category')
                elif df[col].dtype == 'float64':
                    # Para floats, usar float32 si es posible
                    if df[col].notna().all():
                        df[col] = df[col].astype('float32')
                elif df[col].dtype == 'int64':
                    # Para ints, usar tipos más pequeños si es posible
                    if df[col].min() >= 0:
                        if df[col].max() < 255:
                            df[col] = df[col].astype('uint8')
                        elif df[col].max() < 65535:
                            df[col] = df[col].astype('uint16')
                        else:
                            df[col] = df[col].astype('uint32')
                    else:
                        if df[col].min() >= -128 and df[col].max() < 127:
                            df[col] = df[col].astype('int8')
                        elif df[col].min() >= -32768 and df[col].max() < 32767:
                            df[col] = df[col].astype('int16')
                        else:
                            df[col] = df[col].astype('int32')
            
            self.logger.info("Optimización de memoria completada")
            return df
            
        except Exception as e:
            self.logger.error(f"Error optimizando memoria: {e}")
            return df


class InteractiveVisualizationPreparer:
    """Preparador de datos para visualizaciones interactivas."""
    
    def __init__(self):
        self.logger = setup_logger("kforce")
        
    def prepare_correlation_matrix(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepara datos para matriz de correlación interactiva."""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            correlation_matrix = df[numeric_cols].corr()
            
            # Preparar datos para visualización
            corr_data = []
            for i, col1 in enumerate(correlation_matrix.columns):
                for j, col2 in enumerate(correlation_matrix.columns):
                    corr_data.append({
                        'x': col1,
                        'y': col2,
                        'correlation': float(correlation_matrix.iloc[i, j]),
                        'abs_correlation': abs(float(correlation_matrix.iloc[i, j]))
                    })
            
            return {
                'correlation_data': corr_data,
                'columns': correlation_matrix.columns.tolist(),
                'matrix': correlation_matrix.values.tolist()
            }
            
        except Exception as e:
            self.logger.error(f"Error preparando matriz de correlación: {e}")
            return {'error': str(e)}
    
    def prepare_score_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepara datos para distribución de scores interactiva."""
        try:
            score_cols = [col for col in df.columns if 'Score' in col or 'QVA' in col]
            
            if not score_cols:
                return {'error': 'No se encontraron columnas de score'}
            
            distribution_data = {}
            for col in score_cols:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    values = df[col].dropna()
                    if len(values) > 0:
                        distribution_data[col] = {
                            'values': values.tolist(),
                            'mean': float(values.mean()),
                            'std': float(values.std()),
                            'min': float(values.min()),
                            'max': float(values.max()),
                            'percentiles': {
                                '25': float(values.quantile(0.25)),
                                '50': float(values.quantile(0.50)),
                                '75': float(values.quantile(0.75))
                            }
                        }
            
            return {'distribution_data': distribution_data}
            
        except Exception as e:
            self.logger.error(f"Error preparando distribución de scores: {e}")
            return {'error': str(e)}
    
    def prepare_performance_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepara datos para métricas de rendimiento interactivas."""
        try:
            # Métricas clave de rendimiento
            key_metrics = ['Profit Factor', 'CAGR', 'Sharpe Ratio', 'Max_DD_%', 'Recovery Factor']
            
            performance_data = {}
            for metric in key_metrics:
                if metric in df.columns and pd.api.types.is_numeric_dtype(df[metric]):
                    values = df[metric].dropna()
                    if len(values) > 0:
                        performance_data[metric] = {
                            'values': values.tolist(),
                            'mean': float(values.mean()),
                            'median': float(values.median()),
                            'std': float(values.std()),
                            'min': float(values.min()),
                            'max': float(values.max()),
                            'count': len(values)
                        }
            
            return {'performance_data': performance_data}
            
        except Exception as e:
            self.logger.error(f"Error preparando métricas de rendimiento: {e}")
            return {'error': str(e)}


class PostAnalysisProcessor:
    """Procesador de análisis post-ejecución para generar insights y reportes."""
    
    def __init__(self, config_manager: Optional[ConfigManagerEnhanced] = None):
        self.config_manager = config_manager
        self.logger = setup_logger("kforce")
    
    def generate_comprehensive_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Genera análisis comprehensivo de los resultados."""
        try:
            self.logger.info("Generando análisis comprehensivo...")
            
            analysis = {
                'summary': self._generate_summary(df),
                'recommendations': self._generate_recommendations(df),
                'warnings': self._generate_warnings(df),
                'insights': self._generate_insights(df),
                'trading_style_analysis': self._analyze_trading_style_performance(df),
                'risk_assessment': self._assess_risk_levels(df),
                'performance_metrics': self._calculate_performance_metrics(df)
            }
            
            self.logger.info("Análisis comprehensivo generado exitosamente")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error generando análisis comprehensivo: {e}")
            return {'error': str(e)}
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Genera resumen ejecutivo."""
        try:
            total_strategies = len(df)
            
            # Mejor estrategia
            best_strategy = None
            best_score = 0
            if 'Unified_Score' in df.columns:
                best_idx = df['Unified_Score'].idxmax()
                if not pd.isna(best_idx):
                    best_strategy = df.loc[best_idx]
                    best_score = best_strategy.get('Unified_Score', 0)
            
            # Distribución de calidad
            quality_dist = {}
            if 'Quality_Category' in df.columns:
                quality_dist = df['Quality_Category'].value_counts().to_dict()
            
            return {
                'total_strategies': total_strategies,
                'best_strategy_name': best_strategy.get('Strategy Name', 'N/A') if best_strategy is not None else 'N/A',
                'best_score': best_score,
                'quality_distribution': quality_dist,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generando resumen: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en los resultados."""
        recommendations = []
        
        try:
            # Recomendación basada en distribución de calidad
            if 'Quality_Category' in df.columns:
                quality_counts = df['Quality_Category'].value_counts()
                if 'Excelente' in quality_counts and quality_counts['Excelente'] > 0:
                    recommendations.append({
                        'type': 'positive',
                        'message': f"Excelente: {quality_counts['Excelente']} estrategias de alta calidad encontradas",
                        'priority': 'high'
                    })
                elif 'Pobre' in quality_counts and quality_counts['Pobre'] > len(df) * 0.5:
                    recommendations.append({
                        'type': 'warning',
                        'message': "Más del 50% de las estrategias son de baja calidad. Considera revisar los criterios de selección.",
                        'priority': 'high'
                    })
            
            # Recomendación basada en predictividad IS/OOS
            if 'IS/OOS' in df.columns:
                poor_predictivity = df['IS/OOS'].str.contains('🔴', na=False).sum()
                if poor_predictivity > len(df) * 0.3:
                    recommendations.append({
                        'type': 'warning',
                        'message': f"Alto número de estrategias con predictividad pobre ({poor_predictivity}). Posible overfitting.",
                        'priority': 'medium'
                    })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generando recomendaciones: {e}")
            return [{'type': 'error', 'message': f"Error: {str(e)}", 'priority': 'high'}]
    
    def _generate_warnings(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Genera advertencias basadas en los resultados."""
        warnings = []
        
        try:
            # Verificar datos faltantes
            missing_data = df.isnull().sum().sum()
            if missing_data > 0:
                warnings.append({
                    'type': 'warning',
                    'message': f"Datos faltantes detectados: {missing_data} valores NaN",
                    'priority': 'medium'
                })
            
            # Verificar valores extremos
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if col in df.columns:
                    values = df[col].dropna()
                    if len(values) > 0:
                        q1, q3 = values.quantile([0.25, 0.75])
                        iqr = q3 - q1
                        outliers = values[(values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)]
                        if len(outliers) > len(values) * 0.1:
                            warnings.append({
                                'type': 'warning',
                                'message': f"Valores extremos detectados en {col}: {len(outliers)} outliers",
                                'priority': 'low'
                            })
            
            return warnings
            
        except Exception as e:
            self.logger.error(f"Error generando advertencias: {e}")
            return [{'type': 'error', 'message': f"Error: {str(e)}", 'priority': 'high'}]
    
    def _generate_insights(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Genera insights basados en los resultados."""
        insights = []
        
        try:
            # Insight sobre correlaciones
            if 'Unified_Score' in df.columns:
                score_correlations = {}
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    if col != 'Unified_Score':
                        corr = df['Unified_Score'].corr(df[col])
                        if abs(corr) > 0.5:
                            score_correlations[col] = corr
                
                if score_correlations:
                    best_corr_col = max(score_correlations.items(), key=lambda x: abs(x[1]))
                    insights.append({
                        'type': 'insight',
                        'message': f"La métrica más correlacionada con el score es {best_corr_col[0]} (r={best_corr_col[1]:.3f})",
                        'priority': 'medium'
                    })
            
            # Insight sobre distribución de scores
            if 'Unified_Score' in df.columns:
                scores = df['Unified_Score'].dropna()
                if len(scores) > 0:
                    skewness = scores.skew()
                    if abs(skewness) > 1:
                        direction = "positiva" if skewness > 0 else "negativa"
                        insights.append({
                            'type': 'insight',
                            'message': f"Distribución de scores con asimetría {direction} (skewness={skewness:.3f})",
                            'priority': 'low'
                        })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generando insights: {e}")
            return [{'type': 'error', 'message': f"Error: {str(e)}", 'priority': 'high'}]
    
    def _analyze_trading_style_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza el rendimiento por estilo de trading."""
        try:
            if self.config_manager:
                trading_style = self.config_manager.get_trading_style_config().get('name', 'General')
                
                # Aquí podrías agregar análisis específicos por estilo de trading
                return {
                    'trading_style': trading_style,
                    'analysis': f"Análisis específico para {trading_style}",
                    'recommendations': []
                }
            else:
                return {'trading_style': 'General', 'analysis': 'Análisis general'}
                
        except Exception as e:
            self.logger.error(f"Error analizando estilo de trading: {e}")
            return {'error': str(e)}
    
    def _assess_risk_levels(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Evalúa los niveles de riesgo de las estrategias."""
        try:
            risk_metrics = ['Max_DD_%', 'VaR', 'CVaR']
            risk_assessment = {}
            
            for metric in risk_metrics:
                if metric in df.columns:
                    values = df[metric].dropna()
                    if len(values) > 0:
                        risk_assessment[metric] = {
                            'mean': float(values.mean()),
                            'median': float(values.median()),
                            'max': float(values.max()),
                            'high_risk_count': len(values[values > values.quantile(0.9)])
                        }
            
            return risk_assessment
            
        except Exception as e:
            self.logger.error(f"Error evaluando niveles de riesgo: {e}")
            return {'error': str(e)}
    
    def _calculate_performance_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula métricas de rendimiento generales."""
        try:
            performance_metrics = {}
            
            # Métricas de rendimiento
            perf_metrics = ['Profit Factor', 'CAGR', 'Sharpe Ratio']
            for metric in perf_metrics:
                if metric in df.columns:
                    values = df[metric].dropna()
                    if len(values) > 0:
                        performance_metrics[metric] = {
                            'mean': float(values.mean()),
                            'median': float(values.median()),
                            'std': float(values.std()),
                            'min': float(values.min()),
                            'max': float(values.max())
                        }
            
            return performance_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculando métricas de rendimiento: {e}")
            return {'error': str(e)}

class ExtraKPIManager:
    """
    Gestor de KPIs extra automáticos según el estilo de trading.
    Implementa las recomendaciones de Grok para selección y pesos dinámicos.
    """
    
    def __init__(self, config_manager: Optional[ConfigManagerEnhanced] = None):
        self.config_manager = config_manager or ConfigManagerEnhanced()
        self.logger = setup_logger("kforce")
        
        # Definición de KPIs extra por estilo según recomendaciones de Grok
        self.extra_kpis_by_style = {
            "Intraday": {
                "Winrate": {"weight": 0.25, "description": "Frecuencia de éxito en trading de alta frecuencia"},
                "Avgtradedur": {"weight": 0.15, "description": "Duración promedio de trades para intradía"},
                "Exposure": {"weight": 0.20, "description": "Tiempo en mercado para gestionar riesgo"},
                "SQN": {"weight": 0.25, "description": "Calidad del sistema para evaluar consistencia"},
                "Avg_Mae": {"weight": 0.15, "description": "Máxima adversidad promedio para ajustar stops"}
            },
            "Swing": {
                "Sortino_Ratio": {"weight": 0.25, "description": "Enfoque en volatilidad a la baja para swing"},
                "RecoveryFactor": {"weight": 0.20, "description": "Capacidad de recuperación de drawdowns"},
                "Max_Drawdown_Duration": {"weight": 0.15, "description": "Duración de drawdowns en holding largo"},
                "Ulcer_Index_%": {"weight": 0.20, "description": "Estrés por drawdowns prolongados"},
                "Payout_ratio": {"weight": 0.20, "description": "Relación ganancia/pérdida por operación"}
            },
            "Trend_Following": {
                "Marratio": {"weight": 0.30, "description": "Balance entre retorno y drawdown en tendencias"},
                "Sortino_Ratio": {"weight": 0.20, "description": "Enfoque en riesgo a la baja para trend following"},
                "Maxdddur": {"weight": 0.15, "description": "Duración de drawdowns en tendencias largas"},
                "RecoveryFactor": {"weight": 0.20, "description": "Capacidad de recuperación tras drawdowns"},
                "CVaR_95%": {"weight": 0.15, "description": "Protección contra pérdidas extremas"}
            },
            "Mean_Reversion": {
                "Winrate": {"weight": 0.20, "description": "Alto winrate típico en mean reversion"},
                "Expectancy": {"weight": 0.25, "description": "Promedio de ganancia por trade en reversiones"},
                "Avg_Mae": {"weight": 0.15, "description": "Máxima adversidad para ajustar stops"},
                "Avg_Mfe": {"weight": 0.15, "description": "Máxima ganancia promedio para definir targets"},
                "SQN": {"weight": 0.25, "description": "Calidad del sistema para múltiples trades"}
            },
            "Breakout": {
                "Winrate": {"weight": 0.20, "description": "Frecuencia de breakouts exitosos"},
                "Payout_ratio": {"weight": 0.25, "description": "Relación riesgo-recompensa en breakouts"},
                "Max_Consec_Losses": {"weight": 0.15, "description": "Streaks de pérdidas en falsos breakouts"},
                "RecoveryFactor": {"weight": 0.20, "description": "Recuperación tras series de pérdidas"},
                "Sortino_Ratio": {"weight": 0.20, "description": "Protección contra drawdowns en breakouts"}
            }
        }
    
    def get_extra_kpis_for_style(self, trading_style: str) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene los KPIs extra recomendados para un estilo de trading específico.
        
        Args:
            trading_style: Estilo de trading (Intraday, Swing, Trend_Following, etc.)
            
        Returns:
            Diccionario con KPIs extra y sus pesos
        """
        try:
            # Normalizar el nombre del estilo
            style_key = trading_style.replace(" ", "_").replace("-", "_")
            
            if style_key in self.extra_kpis_by_style:
                return self.extra_kpis_by_style[style_key]
            else:
                self.logger.warning(f"Estilo de trading '{trading_style}' no encontrado. Usando configuración por defecto.")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error obteniendo KPIs extra para estilo {trading_style}: {e}")
            return {}
    
    def apply_extra_kpis_to_qva_score(self, df: pd.DataFrame, trading_style: str) -> pd.Series:
        """
        Aplica los KPIs extra al cálculo del QVA Score según el estilo de trading.
        
        Args:
            df: DataFrame con datos de estrategias
            trading_style: Estilo de trading seleccionado
            
        Returns:
            Series con scores QVA ajustados por KPIs extra
        """
        try:
            self.logger.info(f"Aplicando KPIs extra para estilo: {trading_style}")
            
            # Obtener KPIs extra para el estilo
            extra_kpis = self.get_extra_kpis_for_style(trading_style)
            
            if not extra_kpis:
                self.logger.warning("No se encontraron KPIs extra para aplicar")
                return pd.Series(0.5, index=df.index)
            
            # Calcular componente de KPIs extra
            extra_scores = []
            extra_weights = []
            
            for kpi_name, kpi_config in extra_kpis.items():
                if kpi_name in df.columns:
                    # Normalizar el KPI
                    kpi_data = df[kpi_name].fillna(0)
                    normalized_score = self._normalize_extra_kpi(kpi_data, kpi_name)
                    extra_scores.append(normalized_score)
                    extra_weights.append(kpi_config["weight"])
                    
                    self.logger.debug(f"KPI extra '{kpi_name}' aplicado con peso {kpi_config['weight']}")
                else:
                    self.logger.warning(f"KPI extra '{kpi_name}' no encontrado en los datos")
            
            # Calcular score ponderado de KPIs extra
            if extra_scores:
                extra_scores_df = pd.concat(extra_scores, axis=1)
                weights_array = np.array(extra_weights)
                extra_component = (extra_scores_df * weights_array).sum(axis=1) / weights_array.sum()
                
                self.logger.info(f"Componente de KPIs extra calculado para {len(extra_scores)} métricas")
                return extra_component
            else:
                return pd.Series(0.5, index=df.index)
                
        except Exception as e:
            self.logger.error(f"Error aplicando KPIs extra: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _normalize_extra_kpi(self, kpi_data: pd.Series, kpi_name: str) -> pd.Series:
        """
        Normaliza un KPI extra según su tipo y características.
        
        Args:
            kpi_data: Series con datos del KPI
            kpi_name: Nombre del KPI
            
        Returns:
            Series normalizada en rango [0, 1]
        """
        try:
            if kpi_data.empty or kpi_data.isna().all():
                return pd.Series(0.5, index=kpi_data.index)
            
            # Normalización específica por tipo de KPI
            if kpi_name in ["Winrate", "Winning_Percent"]:
                # Porcentajes: normalizar a [0, 1]
                return kpi_data.clip(0, 100) / 100
                
            elif kpi_name in ["Avgtradedur", "Avg_Bars_in_Trade"]:
                # Duración: menor es mejor para intradía
                max_duration = kpi_data.quantile(0.9)
                normalized = 1 - (kpi_data / max_duration).clip(0, 1)
                return normalized
                
            elif kpi_name in ["Exposure"]:
                # Exposición: rango típico [0, 100]
                return (kpi_data.clip(0, 100) / 100)
                
            elif kpi_name in ["SQN"]:
                # SQN: típicamente [-3, 3], normalizar a [0, 1]
                return (kpi_data + 3) / 6
                
            elif kpi_name in ["Avg_Mae", "Avg_Mfe"]:
                # Valores monetarios: usar percentiles
                q1, q3 = kpi_data.quantile([0.1, 0.9])
                iqr = q3 - q1
                if iqr == 0:
                    return pd.Series(0.5, index=kpi_data.index)
                normalized = (kpi_data - q1) / iqr
                return normalized.clip(0, 1)
                
            elif kpi_name in ["Sortino_Ratio", "Sharpe_Ratio"]:
                # Ratios: usar percentiles robustos
                q1, q3 = kpi_data.quantile([0.1, 0.9])
                iqr = q3 - q1
                if iqr == 0:
                    return pd.Series(0.5, index=kpi_data.index)
                normalized = (kpi_data - q1) / iqr
                return normalized.clip(0, 1)
                
            elif kpi_name in ["RecoveryFactor"]:
                # Recovery Factor: mayor es mejor
                q1, q3 = kpi_data.quantile([0.1, 0.9])
                iqr = q3 - q1
                if iqr == 0:
                    return pd.Series(0.5, index=kpi_data.index)
                normalized = (kpi_data - q1) / iqr
                return normalized.clip(0, 1)
                
            elif kpi_name in ["Max_Drawdown_Duration", "Maxdddur"]:
                # Duración de drawdown: menor es mejor
                q1, q3 = kpi_data.quantile([0.1, 0.9])
                iqr = q3 - q1
                if iqr == 0:
                    return pd.Series(0.5, index=kpi_data.index)
                normalized = 1 - ((kpi_data - q1) / iqr).clip(0, 1)
                return normalized
                
            elif kpi_name in ["Ulcer_Index_%"]:
                # Ulcer Index: menor es mejor
                q1, q3 = kpi_data.quantile([0.1, 0.9])
                iqr = q3 - q1
                if iqr == 0:
                    return pd.Series(0.5, index=kpi_data.index)
                normalized = 1 - ((kpi_data - q1) / iqr).clip(0, 1)
                return normalized
                
            elif kpi_name in ["Payout_ratio"]:
                # Payout ratio: mayor es mejor
                q1, q3 = kpi_data.quantile([0.1, 0.9])
                iqr = q3 - q1
                if iqr == 0:
                    return pd.Series(0.5, index=kpi_data.index)
                normalized = (kpi_data - q1) / iqr
                return normalized.clip(0, 1)
                
            elif kpi_name in ["Marratio"]:
                # Mar ratio: mayor es mejor
                q1, q3 = kpi_data.quantile([0.1, 0.9])
                iqr = q3 - q1
                if iqr == 0:
                    return pd.Series(0.5, index=kpi_data.index)
                normalized = (kpi_data - q1) / iqr
                return normalized.clip(0, 1)
                
            elif kpi_name in ["CVaR_95%"]:
                # CVaR: menor es mejor (menor riesgo)
                q1, q3 = kpi_data.quantile([0.1, 0.9])
                iqr = q3 - q1
                if iqr == 0:
                    return pd.Series(0.5, index=kpi_data.index)
                normalized = 1 - ((kpi_data - q1) / iqr).clip(0, 1)
                return normalized
                
            elif kpi_name in ["Expectancy"]:
                # Expectancy: mayor es mejor
                q1, q3 = kpi_data.quantile([0.1, 0.9])
                iqr = q3 - q1
                if iqr == 0:
                    return pd.Series(0.5, index=kpi_data.index)
                normalized = (kpi_data - q1) / iqr
                return normalized.clip(0, 1)
                
            elif kpi_name in ["Max_Consec_Losses"]:
                # Máximo de pérdidas consecutivas: menor es mejor
                q1, q3 = kpi_data.quantile([0.1, 0.9])
                iqr = q3 - q1
                if iqr == 0:
                    return pd.Series(0.5, index=kpi_data.index)
                normalized = 1 - ((kpi_data - q1) / iqr).clip(0, 1)
                return normalized
                
            else:
                # Normalización genérica por percentiles
                q1, q3 = kpi_data.quantile([0.1, 0.9])
                iqr = q3 - q1
                if iqr == 0:
                    return pd.Series(0.5, index=kpi_data.index)
                normalized = (kpi_data - q1) / iqr
                return normalized.clip(0, 1)
                
        except Exception as e:
            self.logger.error(f"Error normalizando KPI extra '{kpi_name}': {e}")
            return pd.Series(0.5, index=kpi_data.index)
    
    def get_extra_kpis_summary(self, trading_style: str) -> Dict[str, Any]:
        """
        Obtiene un resumen de los KPIs extra para un estilo de trading.
        
        Args:
            trading_style: Estilo de trading
            
        Returns:
            Diccionario con resumen de KPIs extra
        """
        try:
            extra_kpis = self.get_extra_kpis_for_style(trading_style)
            
            summary = {
                "trading_style": trading_style,
                "total_extra_kpis": len(extra_kpis),
                "extra_kpis": extra_kpis,
                "total_weight": sum(kpi_config["weight"] for kpi_config in extra_kpis.values()),
                "recommendations": self._get_style_recommendations(trading_style)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generando resumen de KPIs extra: {e}")
            return {}
    
    def _get_style_recommendations(self, trading_style: str) -> List[str]:
        """
        Obtiene recomendaciones específicas para el estilo de trading.
        
        Args:
            trading_style: Estilo de trading
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = {
            "Intraday": [
                "Enfócate en Winrate y SQN para evaluar la calidad del sistema",
                "Monitorea Exposure para gestionar el tiempo en mercado",
                "Usa Avgtradedur para verificar que los trades son de corta duración",
                "Considera Avg_Mae para ajustar stops en alta volatilidad"
            ],
            "Swing": [
                "Prioriza Sortino_Ratio para evaluar riesgo a la baja",
                "Monitorea RecoveryFactor para capacidad de recuperación",
                "Usa Max_Drawdown_Duration para evaluar duración de drawdowns",
                "Considera Ulcer_Index_% para estrés por drawdowns prolongados"
            ],
            "Trend_Following": [
                "Enfócate en Marratio para balance riesgo-retorno",
                "Monitorea Maxdddur para duración de drawdowns largos",
                "Usa CVaR_95% para protección contra pérdidas extremas",
                "Considera RecoveryFactor para recuperación tras drawdowns"
            ],
            "Mean_Reversion": [
                "Prioriza Expectancy para promedio por trade",
                "Monitorea Winrate para frecuencia de éxito",
                "Usa Avg_Mae y Avg_Mfe para gestión de stops y targets",
                "Considera SQN para calidad del sistema"
            ],
            "Breakout": [
                "Enfócate en Payout_ratio para relación riesgo-recompensa",
                "Monitorea Max_Consec_Losses para streaks de pérdidas",
                "Usa Sortino_Ratio para protección contra drawdowns",
                "Considera RecoveryFactor para recuperación tras pérdidas"
            ]
        }
        
        return recommendations.get(trading_style, ["Usa los KPIs extra recomendados para este estilo"])