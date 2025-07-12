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
from typing import Dict, List, Any, Optional, Tuple, Union
from scipy import stats
from scipy.stats import norm, t
import warnings
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime

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
    Analizador de métricas de tail risk para estrategias de trading.
    
    Calcula métricas avanzadas de riesgo de cola incluyendo:
    - VaR (Value at Risk) en múltiples niveles de confianza
    - CVaR (Conditional Value at Risk)
    - Expected Shortfall
    - Análisis de concentración de riesgo en colas
    - Métricas de asimetría y curtosis
    """
    
    def __init__(self, confidence_levels: Optional[List[float]] = None):
        """
        Inicializa el analizador de tail risk.
        
        Args:
            confidence_levels: Lista de niveles de confianza para VaR/CVaR
        """
        self.confidence_levels = confidence_levels or [0.90, 0.95, 0.99]
        self.logger = logger
        self.results = {}
        
        self.logger.info(f"🔬 TailRiskAnalyzer inicializado con niveles: {self.confidence_levels}")
    
    def calculate_tail_risk_metrics(self, 
                                  returns: pd.Series, 
                                  strategy_name: str = "Unknown",
                                  method: str = "historical") -> TailRiskMetrics:
        """
        Calcula todas las métricas de tail risk para una estrategia.
        
        Args:
            returns: Serie de retornos de la estrategia
            strategy_name: Nombre de la estrategia
            method: Método de cálculo ('historical', 'parametric', 'monte_carlo')
            
        Returns:
            TailRiskMetrics con todas las métricas calculadas
        """
        try:
            self.logger.info(f"📊 Calculando métricas de tail risk para {strategy_name}")
            
            # Limpiar datos
            returns_clean = self._clean_returns(returns)
            
            if len(returns_clean) < 30:
                self.logger.warning(f"⚠️ Pocos datos para {strategy_name}: {len(returns_clean)} observaciones")
                return self._create_empty_metrics(strategy_name)
            
            # Calcular métricas básicas
            var_metrics = self._calculate_var(returns_clean, method)
            cvar_metrics = self._calculate_cvar(returns_clean, method)
            expected_shortfall = self._calculate_expected_shortfall(returns_clean)
            
            # Métricas avanzadas
            tail_concentration = self._calculate_tail_concentration(returns_clean)
            extreme_loss_prob = self._calculate_extreme_loss_probability(returns_clean)
            max_dd_risk = self._calculate_max_drawdown_risk(returns_clean)
            vol_tails = self._calculate_volatility_of_tails(returns_clean)
            
            # Estadísticas de forma
            skewness = float(returns_clean.skew())
            kurtosis = float(returns_clean.kurtosis())
            
            metrics = TailRiskMetrics(
                strategy_name=strategy_name,
                var_90=var_metrics.get(0.90, 0.0),
                var_95=var_metrics.get(0.95, 0.0),
                var_99=var_metrics.get(0.99, 0.0),
                cvar_90=cvar_metrics.get(0.90, 0.0),
                cvar_95=cvar_metrics.get(0.95, 0.0),
                cvar_99=cvar_metrics.get(0.99, 0.0),
                expected_shortfall=expected_shortfall,
                tail_concentration=tail_concentration,
                extreme_loss_probability=extreme_loss_prob,
                max_drawdown_risk=max_dd_risk,
                volatility_of_tails=vol_tails,
                skewness=skewness,
                kurtosis=kurtosis
            )
            
            self.logger.info(f"✅ Métricas de tail risk calculadas para {strategy_name}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando métricas de tail risk para {strategy_name}: {e}")
            return self._create_empty_metrics(strategy_name)
    
    def _clean_returns(self, returns: pd.Series) -> pd.Series:
        """Limpia y prepara los retornos para análisis."""
        # Remover valores nulos e infinitos
        clean_returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
        
        # Convertir a porcentajes si es necesario
        if clean_returns.max() > 1.0:
            clean_returns = clean_returns / 100.0
        
        return clean_returns
    
    def _calculate_var(self, returns: pd.Series, method: str = "historical") -> Dict[float, float]:
        """Calcula Value at Risk en múltiples niveles de confianza."""
        var_metrics = {}
        
        try:
            for confidence in self.confidence_levels:
                if method == "historical":
                    var = np.percentile(returns, (1 - confidence) * 100)
                elif method == "parametric":
                    # Asumiendo distribución normal
                    mean_return = returns.mean()
                    std_return = returns.std()
                    var = mean_return + norm.ppf(1 - confidence) * std_return
                else:
                    # Método histórico por defecto
                    var = np.percentile(returns, (1 - confidence) * 100)
                
                var_metrics[confidence] = var
            
            return var_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculando VaR: {e}")
            return {conf: 0.0 for conf in self.confidence_levels}
    
    def _calculate_cvar(self, returns: pd.Series, method: str = "historical") -> Dict[float, float]:
        """Calcula Conditional Value at Risk (Expected Shortfall)."""
        cvar_metrics = {}
        
        try:
            for confidence in self.confidence_levels:
                if method == "historical":
                    threshold = np.percentile(returns, (1 - confidence) * 100)
                    tail_returns = returns[returns <= threshold]
                    cvar = tail_returns.mean() if len(tail_returns) > 0 else threshold
                elif method == "parametric":
                    # Asumiendo distribución normal
                    mean_return = returns.mean()
                    std_return = returns.std()
                    var = mean_return + norm.ppf(1 - confidence) * std_return
                    cvar = mean_return - (norm.pdf(norm.ppf(1 - confidence)) / (1 - confidence)) * std_return
                else:
                    # Método histórico por defecto
                    threshold = np.percentile(returns, (1 - confidence) * 100)
                    tail_returns = returns[returns <= threshold]
                    cvar = tail_returns.mean() if len(tail_returns) > 0 else threshold
                
                cvar_metrics[confidence] = cvar
            
            return cvar_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculando CVaR: {e}")
            return {conf: 0.0 for conf in self.confidence_levels}
    
    def _calculate_expected_shortfall(self, returns: pd.Series) -> float:
        """Calcula Expected Shortfall (pérdida esperada en el peor 5% de casos)."""
        try:
            threshold = np.percentile(returns, 5)  # Peor 5%
            tail_returns = returns[returns <= threshold]
            return float(tail_returns.mean()) if len(tail_returns) > 0 else float(threshold)
        except Exception as e:
            self.logger.error(f"Error calculando Expected Shortfall: {e}")
            return 0.0
    
    def _calculate_tail_concentration(self, returns: pd.Series) -> float:
        """Calcula concentración de riesgo en las colas."""
        try:
            # Calcular qué porcentaje del riesgo total está en el peor 5%
            worst_5_percent = np.percentile(returns, 5)
            tail_returns = returns[returns <= worst_5_percent]
            
            if len(tail_returns) == 0:
                return 0.0
            
            # Concentración = pérdida en cola / pérdida total
            total_loss = returns[returns < 0].sum()
            tail_loss = tail_returns.sum()
            
            return abs(tail_loss / total_loss) if total_loss != 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculando concentración de cola: {e}")
            return 0.0
    
    def _calculate_extreme_loss_probability(self, returns: pd.Series) -> float:
        """Calcula probabilidad de pérdidas extremas (> 2 desviaciones estándar)."""
        try:
            mean_return = returns.mean()
            std_return = returns.std()
            extreme_threshold = mean_return - 2 * std_return
            
            extreme_losses = returns[returns <= extreme_threshold]
            return len(extreme_losses) / len(returns)
            
        except Exception as e:
            self.logger.error(f"Error calculando probabilidad de pérdidas extremas: {e}")
            return 0.0
    
    def _calculate_max_drawdown_risk(self, returns: pd.Series) -> float:
        """Calcula riesgo basado en drawdown máximo."""
        try:
            cumulative_returns = (1 + returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            
            return drawdown.min()
            
        except Exception as e:
            self.logger.error(f"Error calculando riesgo de drawdown: {e}")
            return 0.0
    
    def _calculate_volatility_of_tails(self, returns: pd.Series) -> float:
        """Calcula volatilidad de las colas (último 10% de retornos)."""
        try:
            tail_threshold = np.percentile(returns, 10)
            tail_returns = returns[returns <= tail_threshold]
            
            return float(tail_returns.std()) if len(tail_returns) > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculando volatilidad de colas: {e}")
            return 0.0
    
    def _create_empty_metrics(self, strategy_name: str) -> TailRiskMetrics:
        """Crea métricas vacías cuando no hay suficientes datos."""
        return TailRiskMetrics(
            strategy_name=strategy_name,
            var_90=0.0, var_95=0.0, var_99=0.0,
            cvar_90=0.0, cvar_95=0.0, cvar_99=0.0,
            expected_shortfall=0.0,
            tail_concentration=0.0,
            extreme_loss_probability=0.0,
            max_drawdown_risk=0.0,
            volatility_of_tails=0.0,
            skewness=0.0,
            kurtosis=0.0
        )
    
    def analyze_portfolio_tail_risk(self, 
                                  strategies_metrics: List[TailRiskMetrics],
                                  weights: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Analiza el tail risk del portafolio completo.
        
        Args:
            strategies_metrics: Lista de métricas de tail risk por estrategia
            weights: Pesos de cada estrategia en el portafolio
            
        Returns:
            Diccionario con análisis de tail risk del portafolio
        """
        try:
            self.logger.info("📊 Analizando tail risk del portafolio completo")
            
            if not strategies_metrics:
                return {"error": "No hay métricas de estrategias para analizar"}
            
            # Usar pesos iguales si no se proporcionan
            if weights is None:
                weights = [1.0 / len(strategies_metrics)] * len(strategies_metrics)
            
            # Calcular métricas agregadas del portafolio
            portfolio_analysis = {
                "total_strategies": len(strategies_metrics),
                "portfolio_weights": weights,
                "average_var_95": np.average([m.var_95 for m in strategies_metrics], weights=weights),
                "average_cvar_95": np.average([m.cvar_95 for m in strategies_metrics], weights=weights),
                "max_var_95": max([m.var_95 for m in strategies_metrics]),
                "max_cvar_95": max([m.cvar_95 for m in strategies_metrics]),
                "portfolio_concentration": np.average([m.tail_concentration for m in strategies_metrics], weights=weights),
                "extreme_risk_strategies": [m.strategy_name for m in strategies_metrics if m.extreme_loss_probability > 0.1],
                "high_skewness_strategies": [m.strategy_name for m in strategies_metrics if abs(m.skewness) > 2.0],
                "high_kurtosis_strategies": [m.strategy_name for m in strategies_metrics if m.kurtosis > 10.0]
            }
            
            self.logger.info("✅ Análisis de tail risk del portafolio completado")
            return portfolio_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error analizando tail risk del portafolio: {e}")
            return {"error": str(e)}
    
    def generate_tail_risk_report(self, 
                                strategies_metrics: List[TailRiskMetrics],
                                output_path: Optional[str] = None) -> str:
        """
        Genera un reporte completo de tail risk.
        
        Args:
            strategies_metrics: Lista de métricas de tail risk
            output_path: Ruta para guardar el reporte (opcional)
            
        Returns:
            Contenido del reporte como string
        """
        try:
            self.logger.info("📋 Generando reporte de tail risk")
            
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("REPORTE DE TAIL RISK - ESTRATEGIAS DE TRADING")
            report_lines.append("=" * 80)
            report_lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Total de estrategias: {len(strategies_metrics)}")
            report_lines.append("")
            
            # Resumen ejecutivo
            report_lines.append("RESUMEN EJECUTIVO:")
            report_lines.append("-" * 40)
            
            if strategies_metrics:
                avg_var_95 = np.mean([m.var_95 for m in strategies_metrics])
                avg_cvar_95 = np.mean([m.cvar_95 for m in strategies_metrics])
                high_risk_count = len([m for m in strategies_metrics if m.var_95 < -0.05])
                
                report_lines.append(f"• VaR 95% promedio: {avg_var_95:.4f} ({avg_var_95*100:.2f}%)")
                report_lines.append(f"• CVaR 95% promedio: {avg_cvar_95:.4f} ({avg_cvar_95*100:.2f}%)")
                report_lines.append(f"• Estrategias de alto riesgo: {high_risk_count}")
                report_lines.append("")
            
            # Detalle por estrategia
            report_lines.append("DETALLE POR ESTRATEGIA:")
            report_lines.append("-" * 40)
            
            for metrics in strategies_metrics:
                report_lines.append(f"\nEstrategia: {metrics.strategy_name}")
                report_lines.append(f"  VaR 95%: {metrics.var_95:.4f} ({metrics.var_95*100:.2f}%)")
                report_lines.append(f"  CVaR 95%: {metrics.cvar_95:.4f} ({metrics.cvar_95*100:.2f}%)")
                report_lines.append(f"  Expected Shortfall: {metrics.expected_shortfall:.4f}")
                report_lines.append(f"  Concentración de cola: {metrics.tail_concentration:.4f}")
                report_lines.append(f"  Prob. pérdidas extremas: {metrics.extreme_loss_probability:.4f}")
                report_lines.append(f"  Asimetría: {metrics.skewness:.4f}")
                report_lines.append(f"  Curtosis: {metrics.kurtosis:.4f}")
            
            report_content = "\n".join(report_lines)
            
            # Guardar reporte si se especifica ruta
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                self.logger.info(f"📄 Reporte guardado en: {output_path}")
            
            return report_content
            
        except Exception as e:
            self.logger.error(f"❌ Error generando reporte de tail risk: {e}")
            return f"Error generando reporte: {e}"

    def export_report_json(self, strategies_metrics: List[TailRiskMetrics], output_path: str) -> None:
        """Exporta el reporte de tail risk a formato JSON profesional."""
        try:
            data = [metrics.__dict__ for metrics in strategies_metrics]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False, default=str)
            self.logger.info(f"📄 Reporte JSON exportado en: {output_path}")
        except Exception as e:
            self.logger.error(f"❌ Error exportando reporte JSON: {e}")

    def export_report_csv(self, strategies_metrics: List[TailRiskMetrics], output_path: str) -> None:
        """Exporta el reporte de tail risk a formato CSV profesional."""
        try:
            df = pd.DataFrame([metrics.__dict__ for metrics in strategies_metrics])
            df.to_csv(output_path, index=False, encoding='utf-8')
            self.logger.info(f"📄 Reporte CSV exportado en: {output_path}")
        except Exception as e:
            self.logger.error(f"❌ Error exportando reporte CSV: {e}")

    def generate_alerts(self, strategies_metrics: List[TailRiskMetrics], var_critical: float = -0.05, cvar_critical: float = -0.10) -> list:
        """
        Genera una lista estructurada de alertas automáticas para riesgos críticos.
        Args:
            strategies_metrics: Lista de métricas de tail risk
            var_critical: Umbral crítico para VaR 95%
            cvar_critical: Umbral crítico para CVaR 95%
        Returns:
            Lista de diccionarios con alertas
        """
        alerts = []
        for m in strategies_metrics:
            if m.var_95 < var_critical:
                alerts.append({
                    'strategy': m.strategy_name,
                    'type': 'Riesgo Crítico',
                    'metric': 'VaR 95%',
                    'value': m.var_95,
                    'message': f'🔴 VaR 95% crítico: {m.var_95:.4f}'
                })
            if m.cvar_95 < cvar_critical:
                alerts.append({
                    'strategy': m.strategy_name,
                    'type': 'Riesgo Crítico',
                    'metric': 'CVaR 95%',
                    'value': m.cvar_95,
                    'message': f'🔴 CVaR 95% crítico: {m.cvar_95:.4f}'
                })
            if m.extreme_loss_probability > 0.1:
                alerts.append({
                    'strategy': m.strategy_name,
                    'type': 'Alerta',
                    'metric': 'Prob. pérdidas extremas',
                    'value': m.extreme_loss_probability,
                    'message': f'⚠️ Probabilidad de pérdidas extremas alta: {m.extreme_loss_probability:.2%}'
                })
        self.logger.info(f"🚨 {len(alerts)} alertas generadas para riesgos críticos")
        return alerts

    def export_alerts_json(self, alerts: list, output_path: str) -> None:
        """Exporta las alertas generadas a un archivo JSON."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(alerts, f, indent=4, ensure_ascii=False, default=str)
            self.logger.info(f"📄 Alertas exportadas en: {output_path}")
        except Exception as e:
            self.logger.error(f"❌ Error exportando alertas JSON: {e}")


def analyze_tail_risk_for_dataframe(df: pd.DataFrame, 
                                  returns_column: str = "Returns",
                                  strategy_column: str = "Strategy",
                                  confidence_levels: Optional[List[float]] = None) -> Dict[str, Any]:
    """
    Función de conveniencia para analizar tail risk de un DataFrame.
    
    Args:
        df: DataFrame con estrategias y retornos
        returns_column: Columna con retornos
        strategy_column: Columna con nombres de estrategias
        confidence_levels: Niveles de confianza para VaR/CVaR
        
    Returns:
        Diccionario con resultados del análisis
    """
    try:
        analyzer = TailRiskAnalyzer(confidence_levels)
        results = {}
        
        for strategy_name in df[strategy_column].unique():
            strategy_data = df[df[strategy_column] == strategy_name]
            returns = pd.Series(strategy_data[returns_column].iloc[0])
            
            metrics = analyzer.calculate_tail_risk_metrics(returns, strategy_name)
            results[strategy_name] = metrics
        
        return results
        
    except Exception as e:
        logger.error(f"Error en análisis de tail risk: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Ejemplo de uso
    logging.basicConfig(level=logging.INFO)
    
    # Crear datos de ejemplo
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.001, 0.02, 1000))
    
    analyzer = TailRiskAnalyzer()
    metrics = analyzer.calculate_tail_risk_metrics(returns, "Estrategia_Ejemplo")
    
    print(f"VaR 95%: {metrics.var_95:.4f}")
    print(f"CVaR 95%: {metrics.cvar_95:.4f}")
    print(f"Expected Shortfall: {metrics.expected_shortfall:.4f}") 