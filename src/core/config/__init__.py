"""
Módulo de configuración del core engine.

Este módulo contiene todos los componentes de configuración:
- Config Manager
- KPI Config
- Progress Callback
"""

from .config_manager import ConfigManagerEnhanced
from .kpi_config import KPIConfig, TradingStyleConfig
from .progress_callback import ProgressCallback

__all__ = [
    'ConfigManagerEnhanced',
    'KPIConfig',
    'TradingStyleConfig', 
    'ProgressCallback'
] 