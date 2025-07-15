from typing import Optional, Any, Union
import warnings
"""
Métricas de Predictibilidad usando datos empíricos reales.
Basado únicamente en datos del Excel DatabankExport_M1.csv sin manipulación.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache
import sys
import os

# Agregar src al path para importar config
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.predictability_config_manager import PredictabilityConfigManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PredictabilityMetrics:
    """Métricas de predictibilidad calculadas con datos empíricos."""
    is_oos_consistency: float
    temporal_robustness: float
    overfitting_detection: float
    stability_score: float
    overall_predictability: float

class PredictabilityAnalyzer:
    """
    Analizador de predictibilidad usando datos empíricos reales.
    Sin manipulación ni "cocina" de datos.
    """
    
    def __init__(self, config_manager: Optional[PredictabilityConfigManager] = None):
        self.logger = logging.getLogger("predictability_analyzer")
        self._metrics_cache = {}  # Cache para evitar recálculos
        
        # Cargar configuración
        self.config_manager = config_manager or PredictabilityConfigManager()
        self._load_configuration()
        
        # Configurar logging según configuración
        logging_settings = self.config_manager.get_logging_settings()
        if logging_settings.get("enable_debug", False):
            self.logger.setLevel(logging.DEBUG)
    
    def _load_configuration(self):
        """Carga configuración desde el gestor de configuración."""
        try:
            # Cargar umbrales
            consistency_thresholds = self.config_manager.get_thresholds("consistency")
            temporal_thresholds = self.config_manager.get_thresholds("temporal_robustness")
            overfitting_thresholds = self.config_manager.get_thresholds("overfitting_detection")
            stability_thresholds = self.config_manager.get_thresholds("stability")
            
            # Combinar todos los umbrales
            self.thresholds = {
                **consistency_thresholds,
                **temporal_thresholds,
                **overfitting_thresholds,
                **stability_thresholds
            }
            
            # Cargar pesos de scoring
            self.scoring_weights = self.config_manager.get_scoring_weights()
            
            # Cargar configuración de validación
            self.validation_settings = self.config_manager.get_validation_settings()
            
            self.logger.info("Configuración de predictibilidad cargada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")
            # Usar configuración por defecto
            self.thresholds = {
                "min_is_oos_ratio": 0.7,
                "max_is_oos_ratio": 1.3,
                "min_total_months": 12,
                "min_trades": 50,
                "preferred_months": 24,
                "preferred_trades": 200,
                "max_dd_threshold": 20.0,
                "min_recovery_factor": 1.0,
                "max_profit_factor_is": 3.0,
                "min_calmar_ratio": 1.0,
                "min_sqn": 1.0,
                "min_sortino": 1.0
            }
            self.scoring_weights = {
                "is_oos_consistency": 0.30,
                "temporal_robustness": 0.25,
                "overfitting_detection": 0.25,
                "stability_score": 0.20
            }
            self.validation_settings = {
                "enable_cache": True,
                "max_cache_size": 1000,
                "enable_numeric_validation": True
            }
    
    def _get_cached_metrics(self, strategy_data: pd.Series) -> Optional[PredictabilityMetrics]:
        """Obtiene métricas cacheadas si existen."""
        if not self.validation_settings.get("enable_cache", True):
            return None
            
        strategy_id = strategy_data.get('Strategy Name', str(id(strategy_data)))
        return self._metrics_cache.get(strategy_id)
    
    def _cache_metrics(self, strategy_data: pd.Series, metrics: PredictabilityMetrics):
        """Cachea métricas calculadas."""
        if not self.validation_settings.get("enable_cache", True):
            return
            
        strategy_id = strategy_data.get('Strategy Name', str(id(strategy_data)))
        
        # Limitar tamaño del cache
        max_cache_size = self.validation_settings.get("max_cache_size", 1000)
        if len(self._metrics_cache) >= max_cache_size:
            # Eliminar entrada más antigua (FIFO)
            oldest_key = next(iter(self._metrics_cache))
            del self._metrics_cache[oldest_key]
        
        self._metrics_cache[strategy_id] = metrics
        
        if self.config_manager.get_logging_settings().get("log_cache_hits", True):
            self.logger.debug(f"Métricas cacheadas para estrategia: {strategy_id}")
    
    def _validate_numeric_value(self, value: Any) -> Optional[float]:
        """
        Valida y convierte valor a numérico de forma segura.
        
        Args:
            value: Valor a validar
            
        Returns:
            Valor numérico o None si no es válido
        """
        if not self.validation_settings.get("enable_numeric_validation", True):
            return value
            
        try:
            if pd.isna(value) or value is None:
                return None
            
            # Convertir string con coma decimal
            if isinstance(value, str):
                value = value.replace(',', '.')
            
            numeric_value = float(value) if value is not None else 0.0 if value is not None else 0.0
            
            # Validar que no sea infinito
            if np.isinf(numeric_value) or np.isnan(numeric_value):
                return None
                
            return numeric_value
            
        except (ValueError, TypeError):
            return None
    
    def calculate_is_oos_consistency(self, strategy_data: pd.Series) -> float:
        """
        Calcula consistencia IS/OOS usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia del Excel
            
        Returns:
            Score de consistencia (0-100)
        """
        try:
            consistency_score = 0.0
            
            # 1. CAGR IS/OOS (datos reales)
            if 'CAGR (IS)' in strategy_data and 'CAGR (OOS)' in strategy_data:
                cagr_is = self._validate_numeric_value(strategy_data['CAGR (IS)'])
                cagr_oos = self._validate_numeric_value(strategy_data['CAGR (OOS)'])
                
                if cagr_is and cagr_is > 0:
                    cagr_ratio = cagr_oos / cagr_is if cagr_oos else 0
                    if self.thresholds["min_is_oos_ratio"] <= cagr_ratio <= self.thresholds["max_is_oos_ratio"]:
                        consistency_score += 25  # Excelente consistencia
                    elif 0.5 <= cagr_ratio <= 1.5:
                        consistency_score += 15  # Buena consistencia
                    elif cagr_ratio > 0:
                        consistency_score += 5   # Consistencia básica
            
            # 2. Sharpe Ratio IS/OOS (datos reales)
            if 'Sharpe Ratio (IS)' in strategy_data and 'Sharpe Ratio (OOS)' in strategy_data:
                sharpe_is = self._validate_numeric_value(strategy_data['Sharpe Ratio (IS)'])
                sharpe_oos = self._validate_numeric_value(strategy_data['Sharpe Ratio (OOS)'])
                
                if sharpe_is and sharpe_is > 0:
                    sharpe_ratio = sharpe_oos / sharpe_is if sharpe_oos else 0
                    if self.thresholds["min_is_oos_ratio"] <= sharpe_ratio <= self.thresholds["max_is_oos_ratio"]:
                        consistency_score += 25  # Excelente consistencia
                    elif 0.5 <= sharpe_ratio <= 1.5:
                        consistency_score += 15  # Buena consistencia
                    elif sharpe_ratio > 0:
                        consistency_score += 5   # Consistencia básica
            
            # 3. Profit Factor IS/OOS (datos reales)
            if 'Profit factor (IS)' in strategy_data and 'Profit factor (OOS)' in strategy_data:
                pf_is = self._validate_numeric_value(strategy_data['Profit factor (IS)'])
                pf_oos = self._validate_numeric_value(strategy_data['Profit factor (OOS)'])
                
                if pf_is and pf_is > 1:
                    pf_ratio = pf_oos / pf_is if pf_oos else 0
                    if self.thresholds["min_is_oos_ratio"] <= pf_ratio <= self.thresholds["max_is_oos_ratio"]:
                        consistency_score += 25  # Excelente consistencia
                    elif 0.5 <= pf_ratio <= 1.5:
                        consistency_score += 15  # Buena consistencia
                    elif pf_ratio > 0:
                        consistency_score += 5   # Consistencia básica
            
            # 4. Drawdown IS/OOS (datos reales)
            if 'Drawdown (IS)' in strategy_data and 'Drawdown (OOS)' in strategy_data:
                dd_is = abs(self._validate_numeric_value(strategy_data['Drawdown (IS)']) or 0)
                dd_oos = abs(self._validate_numeric_value(strategy_data['Drawdown (OOS)']) or 0)
                
                if dd_is > 0:
                    dd_ratio = dd_oos / dd_is
                    if dd_ratio <= 1.5:  # OOS drawdown no mucho peor
                        consistency_score += 25  # Excelente consistencia
                    elif dd_ratio <= 2.0:
                        consistency_score += 15  # Buena consistencia
                    elif dd_ratio <= 3.0:
                        consistency_score += 5   # Consistencia básica
            
            return min(consistency_score, 100)
            
        except Exception as e:
            self.logger.error(f"Error calculando consistencia IS/OOS: {e}")
            return 0.0
    
    def calculate_temporal_robustness(self, strategy_data: pd.Series) -> float:
        """
        Calcula robustez temporal usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia del Excel
            
        Returns:
            Score de robustez temporal (0-100)
        """
        try:
            robustness_score = 0.0
            
            # 1. Total Data Months (datos reales)
            if 'Total Data Months' in strategy_data:
                total_months = self._validate_numeric_value(strategy_data['Total Data Months'])
                
                if total_months:
                    if total_months >= self.thresholds["preferred_months"]:
                        robustness_score += 30  # Excelente robustez
                    elif total_months >= self.thresholds["min_total_months"]:
                        robustness_score += 20  # Buena robustez
                    elif total_months >= 6:
                        robustness_score += 10  # Robustez básica
            
            # 2. Number of Trades (datos reales)
            if '# of trades' in strategy_data:
                trades = self._validate_numeric_value(strategy_data['# of trades'])
                
                if trades:
                    if trades >= self.thresholds["preferred_trades"]:
                        robustness_score += 30  # Excelente robustez
                    elif trades >= self.thresholds["min_trades"]:
                        robustness_score += 20  # Buena robustez
                    elif trades >= 25:
                        robustness_score += 10  # Robustez básica
            
            # 3. Winning Percent (datos reales)
            if 'Winning Percent' in strategy_data:
                win_rate = self._validate_numeric_value(strategy_data['Winning Percent'])
                
                if win_rate:
                    if 0.4 <= win_rate <= 0.7:  # Rango óptimo
                        robustness_score += 20
                    elif 0.3 <= win_rate <= 0.8:  # Rango aceptable
                        robustness_score += 10
            
            # 4. Exposure (datos reales)
            if 'Exposure' in strategy_data:
                exposure = self._validate_numeric_value(strategy_data['Exposure'])
                
                if exposure:
                    if 0.1 <= exposure <= 0.9:  # Rango saludable
                        robustness_score += 10
                    elif 0.05 <= exposure <= 0.95:  # Rango aceptable
                        robustness_score += 5
            
            # 5. Max Drawdown Duration (datos reales)
            if 'Max Drawdown Duration' in strategy_data:
                dd_duration = self._validate_numeric_value(strategy_data['Max Drawdown Duration'])
                
                if dd_duration:
                    if dd_duration <= 30:  # Recuperación rápida
                        robustness_score += 10
                    elif dd_duration <= 60:  # Recuperación moderada
                        robustness_score += 5
            
            return min(robustness_score, 100)
            
        except Exception as e:
            self.logger.error(f"Error calculando robustez temporal: {e}")
            return 0.0
    
    def detect_overfitting(self, strategy_data: pd.Series) -> float:
        """
        Detecta sobreajuste usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia del Excel
            
        Returns:
            Score de detección de sobreajuste (0-100, mayor = menos sobreajuste)
        """
        try:
            overfitting_score = 100.0  # Empezar con score perfecto
            has_valid_data = False  # Flag para verificar si hay datos válidos
            
            # 1. Profit Factor IS vs OOS (datos reales)
            if 'Profit factor (IS)' in strategy_data and 'Profit factor (OOS)' in strategy_data:
                pf_is = self._validate_numeric_value(strategy_data['Profit factor (IS)'])
                pf_oos = self._validate_numeric_value(strategy_data['Profit factor (OOS)'])
                
                if pf_is and pf_is > self.thresholds["max_profit_factor_is"]:
                    overfitting_score -= 30  # IS demasiado bueno
                    has_valid_data = True
                
                if pf_is and pf_oos and pf_oos < pf_is * 0.7:
                    overfitting_score -= 25  # OOS mucho peor que IS
                    has_valid_data = True
            
            # 2. Drawdown IS vs OOS (datos reales)
            if 'Drawdown (IS)' in strategy_data and 'Drawdown (OOS)' in strategy_data:
                dd_is = abs(self._validate_numeric_value(strategy_data['Drawdown (IS)']) or 0)
                dd_oos = abs(self._validate_numeric_value(strategy_data['Drawdown (OOS)']) or 0)
                
                if dd_is > 0 and dd_oos > dd_is * 1.5:
                    overfitting_score -= 20  # OOS drawdown mucho peor
                    has_valid_data = True
            
            # 3. Sharpe Ratio IS vs OOS (datos reales)
            if 'Sharpe Ratio (IS)' in strategy_data and 'Sharpe Ratio (OOS)' in strategy_data:
                sharpe_is = self._validate_numeric_value(strategy_data['Sharpe Ratio (IS)'])
                sharpe_oos = self._validate_numeric_value(strategy_data['Sharpe Ratio (OOS)'])
                
                if sharpe_is and sharpe_oos and sharpe_oos < sharpe_is * 0.6:
                    overfitting_score -= 20  # OOS Sharpe mucho peor
                    has_valid_data = True
            
            # 4. Max DD % (datos reales)
            if 'Max DD %' in strategy_data:
                max_dd = self._validate_numeric_value(strategy_data['Max DD %'])
                
                if max_dd and max_dd > self.thresholds["max_dd_threshold"]:
                    overfitting_score -= 15  # Drawdown muy alto
                    has_valid_data = True
            
            # 5. Recovery Factor (datos reales)
            if 'RecoveryFactor' in strategy_data:
                recovery_factor = self._validate_numeric_value(strategy_data['RecoveryFactor'])
                
                if recovery_factor and recovery_factor < self.thresholds["min_recovery_factor"]:
                    overfitting_score -= 10  # Recuperación pobre
                    has_valid_data = True
            
            # Si no hay datos válidos, retornar 0
            if not has_valid_data:
                return 0.0
            
            return max(overfitting_score, 0)  # No menor que 0
            
        except Exception as e:
            self.logger.error(f"Error detectando sobreajuste: {e}")
            return 0.0
    
    def calculate_stability_score(self, strategy_data: pd.Series) -> float:
        """
        Calcula score de estabilidad usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia del Excel
            
        Returns:
            Score de estabilidad (0-100)
        """
        try:
            stability_score = 0.0
            
            # 1. Calmar Ratio (datos reales)
            if 'CalmarRatio' in strategy_data:
                calmar = self._validate_numeric_value(strategy_data['CalmarRatio'])
                
                if calmar:
                    if calmar >= self.thresholds["min_calmar_ratio"]:
                        stability_score += 25
                    elif calmar >= 0.5:
                        stability_score += 15
                    elif calmar >= 0:
                        stability_score += 5
            
            # 2. SQN (datos reales)
            if 'SQN' in strategy_data:
                sqn = self._validate_numeric_value(strategy_data['SQN'])
                
                if sqn:
                    if sqn >= self.thresholds["min_sqn"]:
                        stability_score += 25
                    elif sqn >= 0.5:
                        stability_score += 15
                    elif sqn >= 0:
                        stability_score += 5
            
            # 3. Sortino Ratio (datos reales)
            if 'Sortino Ratio' in strategy_data:
                sortino = self._validate_numeric_value(strategy_data['Sortino Ratio'])
                
                if sortino:
                    if sortino >= self.thresholds["min_sortino"]:
                        stability_score += 20
                    elif sortino >= 0.5:
                        stability_score += 10
                    elif sortino >= 0:
                        stability_score += 5
            
            # 4. VaR (datos reales)
            if 'VaR (95%)' in strategy_data:
                var = abs(self._validate_numeric_value(strategy_data['VaR (95%)']) or 0)
                
                if var <= 0.05:  # VaR bajo
                    stability_score += 15
                elif var <= 0.10:
                    stability_score += 10
                elif var <= 0.15:
                    stability_score += 5
            
            # 5. CVaR (datos reales)
            if 'CVaR (95%)' in strategy_data:
                cvar = abs(self._validate_numeric_value(strategy_data['CVaR (95%)']) or 0)
                
                if cvar <= 0.10:  # CVaR bajo
                    stability_score += 15
                elif cvar <= 0.20:
                    stability_score += 10
                elif cvar <= 0.30:
                    stability_score += 5
            
            return min(stability_score, 100)
            
        except Exception as e:
            self.logger.error(f"Error calculando score de estabilidad: {e}")
            return 0.0
    
    def calculate_overall_predictability(self, strategy_data: pd.Series) -> PredictabilityMetrics:
        """
        Calcula métricas de predictibilidad completas usando datos empíricos reales.
        Implementa cacheo para evitar recálculos.
        
        Args:
            strategy_data: Datos de la estrategia del Excel
            
        Returns:
            Métricas de predictibilidad completas
        """
        try:
            # Verificar cache primero
            cached_metrics = self._get_cached_metrics(strategy_data)
            if cached_metrics:
                self.logger.debug("Usando métricas cacheadas")
                return cached_metrics
            
            # Calcular todas las métricas
            is_oos_consistency = self.calculate_is_oos_consistency(strategy_data)
            temporal_robustness = self.calculate_temporal_robustness(strategy_data)
            overfitting_detection = self.detect_overfitting(strategy_data)
            stability_score = self.calculate_stability_score(strategy_data)
            
            # Score general de predictibilidad (promedio ponderado)
            overall_predictability = (
                is_oos_consistency * self.scoring_weights["is_oos_consistency"] +
                temporal_robustness * self.scoring_weights["temporal_robustness"] +
                overfitting_detection * self.scoring_weights["overfitting_detection"] +
                stability_score * self.scoring_weights["stability_score"]
            )
            
            metrics = PredictabilityMetrics(
                is_oos_consistency=is_oos_consistency,
                temporal_robustness=temporal_robustness,
                overfitting_detection=overfitting_detection,
                stability_score=stability_score,
                overall_predictability=overall_predictability
            )
            
            # Cachear resultado
            self._cache_metrics(strategy_data, metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculando predictibilidad general: {e}")
            return PredictabilityMetrics(0.0, 0.0, 0.0, 0.0, 0.0)
    
    def clear_cache(self):
        """Limpia el cache de métricas."""
        self._metrics_cache.clear()
        self.logger.debug("Cache de métricas limpiado")
    
    def update_configuration(self, config_updates: Dict[str, Any]):
        """
        Actualiza configuración dinámicamente.
        
        Args:
            config_updates: Diccionario con actualizaciones de configuración
        """
        try:
            self.config_manager.update_config(config_updates)
            self._load_configuration()
            self.logger.info("Configuración actualizada dinámicamente")
        except Exception as e:
            self.logger.error(f"Error actualizando configuración: {e}")

def test_predictability_metrics():
    """Test de las métricas de predictibilidad con datos reales."""
    import pandas as pd
    
    # Cargar datos reales
    df = pd.read_csv('DatabankExport_M1.csv', sep=';', decimal=',')
    
    # Crear analizador
    analyzer = PredictabilityAnalyzer()
    
    # Analizar primera estrategia
    strategy_data = df.iloc[0]
    metrics = analyzer.calculate_overall_predictability(strategy_data)
    
    print("=== TEST MÉTRICAS DE PREDICTIBILIDAD ===")
    print(f"Estrategia: {strategy_data['Strategy Name']}")
    print(f"Consistencia IS/OOS: {metrics.is_oos_consistency:.1f}")
    print(f"Robustez Temporal: {metrics.temporal_robustness:.1f}")
    print(f"Detección Sobreajuste: {metrics.overfitting_detection:.1f}")
    print(f"Score Estabilidad: {metrics.stability_score:.1f}")
    print(f"Predictibilidad General: {metrics.overall_predictability:.1f}")
    print("=" * 50)

if __name__ == "__main__":
    test_predictability_metrics() 