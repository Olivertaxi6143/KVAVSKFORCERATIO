#!/usr/bin/env python3
"""
Módulo de Métricas de Tail Risk para Estrategias de Trading
==========================================================

Calcula métricas avanzadas de riesgo de cola (tail risk) para estrategias de trading:
- Value at Risk (VaR) - Valor en Riesgo
- Conditional Value at Risk (CVaR) - Valor en Riesgo Condicional
- Expected Shortfall - Pérdida Esperada
- Análisis de colas extremas
- Stress testing de colas
- Métricas de concentración de riesgo

Basado en metodologías financieras estándar para gestión de riesgo.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import logging
import warnings
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from src.data.data_utils import (
    calculate_max_drawdown,
    calculate_percentile_tail,
    calculate_cumulative_returns,
    clean_returns
)

# Configurar warnings
warnings.filterwarnings("ignore")

# Configurar logging
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Niveles de confianza para cálculos de riesgo."""
    LOW = 0.90
    MEDIUM = 0.95
    HIGH = 0.99
    EXTREME = 0.995

@dataclass
class TailRiskMetrics:
    """Contenedor para métricas de tail risk de una estrategia."""
    strategy_name: str
    var_90: float
    var_95: float
    var_99: float
    cvar_90: float
    cvar_95: float
    cvar_99: float
    expected_shortfall: float
    tail_concentration: float
    extreme_loss_probability: float
    max_drawdown_risk: float
    volatility_of_tails: float
    skewness: float
    kurtosis: float
    confidence_level: float = 0.95

class TailRiskAnalyzer:
    """
    Analizador profesional de métricas de tail risk para estrategias de trading.

    Calcula:
    - VaR (Value at Risk) en múltiples niveles de confianza
    - CVaR (Conditional Value at Risk)
    - Expected Shortfall
    - Drawdown máximo
    - Concentración de cola
    - Probabilidad de pérdida extrema
    - Volatilidad de colas
    - Asimetría (skewness) y curtosis (kurtosis)

    Todos los métodos devuelven un dict plano y usan np.nan para métricas no calculadas.

    Ejemplo de uso:
        analyzer = TailRiskAnalyzer()
        returns = pd.Series([...])
        metrics = analyzer.calculate_tail_risk_metrics(returns, strategy_name="EURUSD_M1")
    """
    def __init__(self, confidence_levels: Optional[List[float]] = None):
        self.confidence_levels = confidence_levels or [0.90, 0.95, 0.99]
        self.logger = logger
        self.logger.info(f"🔬 TailRiskAnalyzer inicializado con niveles: {self.confidence_levels}")

    def calculate_tail_risk_metrics(self, returns: pd.Series, strategy_name: str = "Unknown", method: str = "historical") -> Dict[str, Any]:
        """
        Calcula todas las métricas de tail risk para una estrategia.

        Args:
            returns: Serie de retornos de la estrategia
            strategy_name: Nombre de la estrategia
            method: Método de cálculo ('historical', 'parametric', 'monte_carlo')
        Returns:
            Dict plano con todas las métricas calculadas
        """
        try:
            # Validación y limpieza de datos
            returns_clean = clean_returns(returns)
            if len(returns_clean) < 30:
                self.logger.warning(f"⚠️ Pocos datos para {strategy_name}: {len(returns_clean)} observaciones")
                return self._empty_metrics(strategy_name)

            # VaR y CVaR
            var_metrics = {}
            cvar_metrics = {}
            for cl in self.confidence_levels:
                p = 100 * (1 - cl)
                var = calculate_percentile_tail(returns_clean, p)
                var_metrics[f"var_{int(cl*100)}"] = var
                cvar = returns_clean[returns_clean <= var].mean() if not np.isnan(var) else np.nan
                cvar_metrics[f"cvar_{int(cl*100)}"] = cvar

            # Expected Shortfall (igual a CVaR al 99%)
            expected_shortfall = cvar_metrics.get("cvar_99", np.nan)

            # Concentración de cola (proporción de retornos en la cola inferior al 5%)
            tail_5 = calculate_percentile_tail(returns_clean, 5)
            tail_concentration = np.mean(returns_clean <= tail_5) if not np.isnan(tail_5) else np.nan

            # Probabilidad de pérdida extrema (retornos < -10%)
            extreme_loss_prob = np.mean(returns_clean < -0.10) if len(returns_clean) > 0 else np.nan

            # Drawdown máximo
            max_drawdown = calculate_max_drawdown(returns_clean)

            # Volatilidad de colas (std de los retornos en la cola inferior al 5%)
            vol_tails = returns_clean[returns_clean <= tail_5].std() if not np.isnan(tail_5) else np.nan

            # Estadísticas de forma
            skewness = float(returns_clean.skew()) if len(returns_clean) > 0 else np.nan
            kurtosis = float(returns_clean.kurtosis()) if len(returns_clean) > 0 else np.nan

            metrics = {
                "strategy_name": strategy_name,
                **var_metrics,
                **cvar_metrics,
                "expected_shortfall": expected_shortfall,
                "tail_concentration": tail_concentration,
                "extreme_loss_probability": extreme_loss_prob,
                "max_drawdown": max_drawdown,
                "volatility_of_tails": vol_tails,
                "skewness": skewness,
                "kurtosis": kurtosis
            }
            self.logger.info(f"✅ Métricas de tail risk calculadas para {strategy_name}")
            return metrics
        except Exception as e:
            self.logger.error(f"❌ Error calculando métricas de tail risk para {strategy_name}: {e}")
            return self._empty_metrics(strategy_name)

    def _empty_metrics(self, strategy_name: str) -> Dict[str, Any]:
        """Devuelve un dict plano con np.nan para todas las métricas."""
        return {
            "strategy_name": strategy_name,
            "var_90": np.nan, "var_95": np.nan, "var_99": np.nan,
            "cvar_90": np.nan, "cvar_95": np.nan, "cvar_99": np.nan,
            "expected_shortfall": np.nan,
            "tail_concentration": np.nan,
            "extreme_loss_probability": np.nan,
            "max_drawdown": np.nan,
            "volatility_of_tails": np.nan,
            "skewness": np.nan,
            "kurtosis": np.nan
        }

    def analyze_portfolio_tail_risk(self, strategies_metrics: List[Dict[str, Any]], weights: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Analiza el tail risk del portafolio completo.
        Args:
            strategies_metrics: Lista de dicts de métricas de tail risk por estrategia
            weights: Pesos de cada estrategia en el portafolio
        Returns:
            Dict con análisis de tail risk del portafolio
        """
        try:
            if not strategies_metrics:
                return {"error": "No hay métricas de estrategias para analizar"}
            if weights is None:
                weights = [1.0 / len(strategies_metrics)] * len(strategies_metrics)
            # Extraer métricas agregadas
            def safe_list(key):
                return [m.get(key, np.nan) for m in strategies_metrics]
            portfolio_analysis = {
                "total_strategies": len(strategies_metrics),
                "portfolio_weights": weights,
                "average_var_95": float(np.average(safe_list("var_95"), weights=weights)),
                "average_cvar_95": float(np.average(safe_list("cvar_95"), weights=weights)),
                "max_var_95": float(np.nanmax(safe_list("var_95"))),
                "max_cvar_95": float(np.nanmax(safe_list("cvar_95"))),
                "portfolio_concentration": float(np.average(safe_list("tail_concentration"), weights=weights)),
                "extreme_risk_strategies": [m["strategy_name"] for m in strategies_metrics if m.get("extreme_loss_probability", 0) > 0.1],
                "high_skewness_strategies": [m["strategy_name"] for m in strategies_metrics if abs(m.get("skewness", 0)) > 2.0],
                "high_kurtosis_strategies": [m["strategy_name"] for m in strategies_metrics if m.get("kurtosis", 0) > 10.0]
            }
            self.logger.info("✅ Análisis de tail risk del portafolio completado")
            return portfolio_analysis
        except Exception as e:
            self.logger.error(f"❌ Error analizando tail risk del portafolio: {e}")
            return {"error": str(e)}

    def analyze_tail_risk_metrics(self, df: pd.DataFrame, returns_column: str = "Returns", strategy_column: str = "Strategy") -> Dict[str, Any]:
        """
        Analiza tail risk para cada estrategia en un DataFrame.
        Args:
            df: DataFrame con estrategias y retornos
            returns_column: Columna con retornos (debe ser una Serie por fila)
            strategy_column: Columna con nombres de estrategias
        Returns:
            Dict con resultados del análisis por estrategia
        """
        try:
            results = {}
            for idx, row in df.iterrows():
                strategy_name = row.get(strategy_column, f"Strategy_{idx}")
                returns = row.get(returns_column, pd.Series(dtype=float))
                
                # Validación para evitar None
                if strategy_name is None:
                    strategy_name = f"Strategy_{idx}"
                
                if returns is None:
                    returns = pd.Series(dtype=float)
                
                # Asegurar que returns sea una Serie válida
                if not isinstance(returns, pd.Series):
                    returns = pd.Series(returns) if returns is not None else pd.Series(dtype=float)
                
                metrics = self.calculate_tail_risk_metrics(returns, strategy_name)
                results[strategy_name] = metrics
            return results
        except Exception as e:
            self.logger.error(f"Error en análisis de tail risk: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Ejemplo de uso
    logging.basicConfig(level=logging.INFO)
    
    # Crear datos de ejemplo
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.001, 0.02, 1000))
    
    analyzer = TailRiskAnalyzer()
    metrics = analyzer.calculate_tail_risk_metrics(returns, "Estrategia_Ejemplo")
    
    print(f"VaR 95%: {metrics.get('var_95', np.nan):.4f}")
    print(f"CVaR 95%: {metrics.get('cvar_95', np.nan):.4f}")
    print(f"Expected Shortfall: {metrics.get('expected_shortfall', np.nan):.4f}") 