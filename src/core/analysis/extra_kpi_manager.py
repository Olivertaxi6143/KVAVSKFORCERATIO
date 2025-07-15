from typing import Optional, Any, Union
import warnings
#!/usr/bin/env python3
"""
ExtraKPIManager - Gestor de KPIs Extra por Estilo de Trading

Implementa la gestión automática de KPIs extra según el estilo de trading seleccionado,
con pesos dinámicos y validación robusta de datos.

Características principales:
- Configuración automática de KPIs extra por estilo de trading
- Pesos dinámicos basados en recomendaciones profesionales
- Normalización inteligente de métricas
- Validación robusta de datos
- Integración con el cálculo del QVA Score
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from src.logger_config import setup_logger

class ExtraKPIManager:
    """
    Gestor de KPIs extra automáticos según el estilo de trading.
    Implementa las recomendaciones profesionales para selección y pesos dinámicos.

    ADVERTENCIA PROFESIONAL:
    ------------------------------------------------------------
    Este módulo SOLO debe recibir DataFrames ya validados y preparados por DataManager
    u otras funciones centralizadas de la capa data. No realizar validación, carga ni
    manipulación local de datos aquí. Toda gestión de datos debe estar centralizada.
    ------------------------------------------------------------
    """
    
    def __init__(self, config_manager=None):
        """
        Inicializa el gestor de KPIs extra.
        
        Args:
            config_manager: Configuración del sistema (opcional)
        """
        self.logger = setup_logger("extra_kpi_manager")
        self.config_manager = config_manager
        
        # Configuración de KPIs extra por estilo de trading
        # Basado en recomendaciones profesionales de Grok
        self.extra_kpis_config = {
            'Intraday': {
                'Winrate': {'weight': 0.25, 'description': 'Frecuencia de éxito en trading de alta frecuencia'},
                'Avgtradedur': {'weight': 0.15, 'description': 'Duración promedio de operaciones'},
                'Exposure': {'weight': 0.20, 'description': 'Tiempo en el mercado'},
                'SQN': {'weight': 0.20, 'description': 'Calidad del sistema de trading'},
                'Sortino_Ratio': {'weight': 0.20, 'description': 'Ratio de Sortino para riesgo asimétrico'}
            },
            'Swing': {
                'Marratio': {'weight': 0.20, 'description': 'Ratio de margen para operaciones de medio plazo'},
                'Maxdddur': {'weight': 0.20, 'description': 'Duración máxima de drawdown'},
                'RecoveryFactor': {'weight': 0.20, 'description': 'Factor de recuperación'},
                'Exposure': {'weight': 0.15, 'description': 'Exposición al mercado'},
                'VaR_(95%)': {'weight': 0.125, 'description': 'Value at Risk'},
                'CVaR_(95%)': {'weight': 0.125, 'description': 'Conditional Value at Risk'}
            },
            'Trend_Following': {
                'Marratio': {'weight': 0.25, 'description': 'Ratio de margen para tendencias'},
                'Maxdddur': {'weight': 0.20, 'description': 'Duración de drawdowns en tendencias'},
                'RecoveryFactor': {'weight': 0.20, 'description': 'Recuperación de tendencias'},
                'CAGR': {'weight': 0.15, 'description': 'Crecimiento anual compuesto'},
                'Sharpe_Ratio': {'weight': 0.20, 'description': 'Ratio de Sharpe para tendencias'}
            },
            'Mean_Reversion': {
                'Expectancy': {'weight': 0.25, 'description': 'Expectativa de retorno'},
                'Avg_Mae': {'weight': 0.20, 'description': 'Error absoluto promedio'},
                'Winrate': {'weight': 0.20, 'description': 'Porcentaje de operaciones ganadoras'},
                'Sortino_Ratio': {'weight': 0.20, 'description': 'Ratio de Sortino'},
                'Maxdddur': {'weight': 0.15, 'description': 'Duración de drawdowns'}
            },
            'Breakout': {
                'Sortino_Ratio': {'weight': 0.25, 'description': 'Ratio de Sortino para breakouts'},
                'RecoveryFactor': {'weight': 0.20, 'description': 'Recuperación de breakouts'},
                'Exposure': {'weight': 0.20, 'description': 'Exposición en breakouts'},
                'Max_Stag_Trades': {'weight': 0.15, 'description': 'Operaciones de estancamiento'},
                'VaR_(95%)': {'weight': 0.20, 'description': 'Value at Risk para breakouts'}
            },
            'Scalping': {
                'Winrate': {'weight': 0.30, 'description': 'Alta frecuencia de éxito'},
                'Avgtradedur': {'weight': 0.20, 'description': 'Duración muy corta'},
                'Exposure': {'weight': 0.15, 'description': 'Tiempo mínimo en mercado'},
                'SQN': {'weight': 0.20, 'description': 'Calidad del sistema'},
                'Sortino_Ratio': {'weight': 0.15, 'description': 'Riesgo asimétrico'}
            },
            'Day_Trading': {
                'Winrate': {'weight': 0.25, 'description': 'Frecuencia de éxito diaria'},
                'Avgtradedur': {'weight': 0.15, 'description': 'Duración de operaciones'},
                'Exposure': {'weight': 0.20, 'description': 'Exposición diaria'},
                'SQN': {'weight': 0.20, 'description': 'Calidad del sistema'},
                'Sortino_Ratio': {'weight': 0.20, 'description': 'Riesgo asimétrico'}
            },
            'Position_Trading': {
                'Marratio': {'weight': 0.25, 'description': 'Ratio de margen para posiciones largas'},
                'Maxdddur': {'weight': 0.20, 'description': 'Duración de drawdowns'},
                'RecoveryFactor': {'weight': 0.20, 'description': 'Recuperación de posiciones'},
                'CAGR': {'weight': 0.20, 'description': 'Crecimiento anual'},
                'Sharpe_Ratio': {'weight': 0.15, 'description': 'Ratio de Sharpe'}
            },
            'General': {
                'Sharpe_Ratio': {'weight': 0.25, 'description': 'Ratio de Sharpe general'},
                'Profit_factor': {'weight': 0.20, 'description': 'Factor de beneficio'},
                'Max_DD_%': {'weight': 0.20, 'description': 'Máximo drawdown'},
                'CAGR': {'weight': 0.20, 'description': 'Crecimiento anual'},
                'CalmarRatio': {'weight': 0.15, 'description': 'Ratio de Calmar'}
            }
        }
        
        # Mapeo de nombres de estilos para compatibilidad
        self.style_mapping = {
            'Intraday': 'Intraday',
            'Swing': 'Swing',
            'Trend Following': 'Trend_Following',
            'Mean Reversion': 'Mean_Reversion',
            'Breakout': 'Breakout',
            'Scalping': 'Scalping',
            'Day Trading': 'Day_Trading',
            'Position Trading': 'Position_Trading',
            'General': 'General'
        }
        
        self.logger.info("✅ ExtraKPIManager inicializado correctamente")
    
    def get_extra_kpis_for_style(self, trading_style: str) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene los KPIs extra configurados para un estilo de trading específico.
        
        Args:
            trading_style: Estilo de trading
            
        Returns:
            Diccionario con KPIs extra y sus configuraciones
        """
        try:
            # Normalizar nombre del estilo
            normalized_style = self.style_mapping.get(trading_style, trading_style)
            
            # Obtener configuración para el estilo
            extra_kpis = self.extra_kpis_config.get(normalized_style, {})
            
            if not extra_kpis:
                self.logger.warning(f"⚠️ No hay KPIs extra configurados para el estilo: {trading_style}")
                # Usar configuración general como fallback
                extra_kpis = self.extra_kpis_config.get('General', {})
            
            self.logger.info(f"🎯 KPIs extra para {trading_style}: {len(extra_kpis)} KPIs")
            return extra_kpis
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo KPIs extra para {trading_style}: {e}")
            return {}
    
    def apply_extra_kpis_to_qva_score(self, df: pd.DataFrame, trading_style: str) -> pd.Series:
        """
        Aplica los KPIs extra al cálculo del QVA Score.
        Recibe un DataFrame ya validado y preparado por DataManager.
        No realizar validación ni carga local aquí.
        """
        self.logger.debug(f"[INICIO] apply_extra_kpis_to_qva_score - Entrada recibida (datos validados por DataManager, estilo: {trading_style})")
        try:
            self.logger.info(f"🔧 Aplicando KPIs extra para estilo: {trading_style}")
            
            if df.empty:
                self.logger.warning("⚠️ DataFrame vacío, retornando scores por defecto")
                return pd.Series(0.5, index=df.index)
            
            # Obtener KPIs extra para el estilo
            extra_kpis_config = self.get_extra_kpis_for_style(trading_style)
            
            if not extra_kpis_config:
                self.logger.warning(f"⚠️ No hay KPIs extra configurados para {trading_style}")
                return pd.Series(0.5, index=df.index)
            
            # Calcular scores individuales para cada KPI extra
            kpi_scores = {}
            available_kpis = []
            
            for kpi_name, kpi_config in extra_kpis_config.items():
                weight = kpi_config.get('weight', 1.0)
                
                # Verificar si el KPI está disponible en los datos
                if kpi_name in df.columns:
                    try:
                        # Normalizar el KPI
                        kpi_values = df[kpi_name].fillna(0)
                        normalized_score = self._normalize_kpi(kpi_values)
                        kpi_scores[kpi_name] = normalized_score * weight
                        available_kpis.append(kpi_name)
                        self.logger.debug(f"✅ KPI {kpi_name} procesado (peso: {weight})")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error procesando KPI {kpi_name}: {e}")
                else:
                    self.logger.debug(f"⚠️ KPI {kpi_name} no disponible en datos")
            
            if not kpi_scores:
                self.logger.warning("⚠️ No hay KPIs extra disponibles en los datos")
                self.logger.debug("[FIN] apply_extra_kpis_to_qva_score - Sin KPIs extra disponibles")
                return pd.Series(0.5, index=df.index)
            
            # Calcular score combinado de KPIs extra
            combined_score = pd.Series(0.0, index=df.index)
            total_weight = 0.0
            
            for kpi_name, kpi_score in kpi_scores.items():
                weight = extra_kpis_config[kpi_name]['weight']
                combined_score += kpi_score
                total_weight += weight
            
            # Normalizar por peso total
            if total_weight > 0:
                combined_score = combined_score / total_weight
            
            # Normalización final robusta
            final_score = self._robust_normalization(combined_score)
            
            self.logger.info(f"✅ KPIs extra aplicados: {len(available_kpis)} KPIs disponibles")
            self.logger.info(f"📊 Score promedio: {final_score.mean():.4f} ± {final_score.std():.4f}")
            
            return final_score
            
        except Exception as e:
            self.logger.error(f"❌ Error aplicando KPIs extra: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _normalize_kpi(self, values: Any, higher_is_better: bool = True) -> pd.Series:
        """
        Normaliza un KPI específico según sus características.
        
        Args:
            values: Valores del KPI a normalizar (cualquier tipo compatible)
            higher_is_better: Si valores más altos son mejores
            
        Returns:
            Series con valores normalizados en [0,1]
        """
        try:
            # Asegurar que values sea siempre un pd.Series
            if isinstance(values, pd.DataFrame):
                if values.shape[1] == 1:
                    values = values.iloc[:, 0]
                else:
                    values = values.squeeze()
            elif not isinstance(values, pd.Series):
                values = pd.Series(values)
            
            # Manejar valores infinitos y NaN
            values = values.replace([np.inf, -np.inf], np.nan)
            values = values.fillna(values.median())
            
            # Normalización robusta usando percentiles
            p5 = values.quantile(0.05)
            p95 = values.quantile(0.95)
            
            if p95 == p5:
                return pd.Series(0.5, index=values.index)
            
            # Normalizar usando percentiles
            if higher_is_better:
                normalized = (values - p5) / (p95 - p5)
            else:
                normalized = (p95 - values) / (p95 - p5)
            
            # Clipping a [0,1]
            normalized = np.clip(normalized, 0, 1)
            
            return pd.Series(normalized, index=values.index)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error normalizando KPI: {e}")
            return pd.Series(0.5, index=values.index if hasattr(values, 'index') else None)
    
    def _is_higher_better(self, kpi_name: str) -> bool:
        """
        Determina si valores más altos son mejores para un KPI.
        
        Args:
            kpi_name: Nombre del KPI
            
        Returns:
            True si valores más altos son mejores
        """
        # KPIs donde valores más altos son mejores
        higher_better_kpis = {
            'Winrate', 'Sharpe_Ratio', 'Sortino_Ratio', 'CAGR', 'Profit_factor',
            'RecoveryFactor', 'CalmarRatio', 'SQN', 'Expectancy', 'Marratio'
        }
        
        # KPIs donde valores más bajos son mejores
        lower_better_kpis = {
            'Max_DD_%', 'Maxdddur', 'Avgtradedur', 'Exposure', 'VaR_(95%)',
            'CVaR_(95%)', 'Avg_Mae', 'Max_Stag_Trades'
        }
        
        if kpi_name in higher_better_kpis:
            return True
        elif kpi_name in lower_better_kpis:
            return False
        else:
            # Por defecto, asumir que valores más altos son mejores
            return True
    
    def _robust_normalization(self, series: pd.Series) -> pd.Series:
        """
        Aplica normalización robusta a una serie.
        
        Args:
            series: Serie a normalizar
            
        Returns:
            Serie normalizada en [0,1]
        """
        try:
            if series.empty:
                return series
            
            # Manejar valores extremos
            series = series.replace([np.inf, -np.inf], np.nan)
            series = series.fillna(series.median())
            
            # Normalización usando sigmoide adaptativa
            mean_val = series.mean()
            std_val = series.std()
            
            if std_val == 0:
                return pd.Series(0.5, index=series.index)
            
            # Aplicar sigmoide para suavizar valores extremos
            normalized = 1 / (1 + np.exp(-(series - mean_val) / (std_val + 1e-8)))
            
            return normalized
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error en normalización robusta: {e}")
            return pd.Series(0.5, index=series.index)
    
    def get_available_extra_kpis(self) -> List[str]:
        """
        Obtiene la lista de todos los KPIs extra disponibles.
        
        Returns:
            Lista de nombres de KPIs extra
        """
        all_kpis = set()
        for style_config in self.extra_kpis_config.values():
            all_kpis.update(style_config.keys())
        return sorted(list(all_kpis))
    
    def get_style_summary(self, trading_style: str) -> Dict[str, Any]:
        """
        Obtiene un resumen de la configuración de KPIs extra para un estilo.
        
        Args:
            trading_style: Estilo de trading
            
        Returns:
            Diccionario con resumen de configuración
        """
        try:
            extra_kpis = self.get_extra_kpis_for_style(trading_style)
            
            summary = {
                'style': trading_style,
                'total_kpis': len(extra_kpis),
                'kpis': list(extra_kpis.keys()),
                'total_weight': sum(config.get('weight', 0) for config in extra_kpis.values()),
                'configurations': extra_kpis
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo resumen para {trading_style}: {e}")
            return {}
    
    def validate_kpis_in_data(self, df: pd.DataFrame, trading_style: str) -> Dict[str, Any]:
        """
        Valida qué KPIs extra están disponibles en los datos.
        
        Args:
            df: DataFrame con datos
            trading_style: Estilo de trading
            
        Returns:
            Diccionario con KPIs disponibles y faltantes
        """
        try:
            extra_kpis = self.get_extra_kpis_for_style(trading_style)
            available_kpis = []
            missing_kpis = []
            
            for kpi_name in extra_kpis.keys():
                if kpi_name in df.columns:
                    available_kpis.append(kpi_name)
                else:
                    missing_kpis.append(kpi_name)
            
            return {
                'available': available_kpis,
                'missing': missing_kpis,
                'coverage': len(available_kpis) / len(extra_kpis) if extra_kpis else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error validando KPIs para {trading_style}: {e}")
            return {'available': [], 'missing': [], 'coverage': 0} 