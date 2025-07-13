"""
Métricas de Predictibilidad usando datos empíricos reales.
Basado únicamente en datos del Excel DatabankExport_M1.csv sin manipulación.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

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
    
    def __init__(self):
        self.logger = logging.getLogger("predictability_analyzer")
        
        # Umbrales basados en datos empíricos reales
        self.thresholds = {
            # Consistencia IS/OOS (datos reales del Excel)
            "min_is_oos_ratio": 0.7,  # OOS debe ser al menos 70% de IS
            "max_is_oos_ratio": 1.3,  # OOS no debe ser más de 130% de IS
            
            # Robustez temporal (datos reales)
            "min_total_months": 12,    # Mínimo 12 meses de datos
            "min_trades": 50,          # Mínimo 50 trades
            "preferred_months": 24,    # Preferido 24+ meses
            "preferred_trades": 200,   # Preferido 200+ trades
            
            # Calidad vs sobreajuste (datos reales)
            "max_dd_threshold": 20.0,  # Máximo 20% drawdown
            "min_recovery_factor": 1.0, # Mínimo Recovery Factor 1.0
            "max_profit_factor_is": 3.0, # Máximo Profit Factor IS 3.0
            
            # Estabilidad (datos reales)
            "min_calmar_ratio": 1.0,   # Mínimo Calmar Ratio 1.0
            "min_sqn": 1.0,            # Mínimo SQN 1.0
            "min_sortino": 1.0         # Mínimo Sortino Ratio 1.0
        }
    
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
                cagr_is = strategy_data['CAGR (IS)']
                cagr_oos = strategy_data['CAGR (OOS)']
                
                if cagr_is > 0:
                    cagr_ratio = cagr_oos / cagr_is
                    if self.thresholds["min_is_oos_ratio"] <= cagr_ratio <= self.thresholds["max_is_oos_ratio"]:
                        consistency_score += 25  # Excelente consistencia
                    elif 0.5 <= cagr_ratio <= 1.5:
                        consistency_score += 15  # Buena consistencia
                    elif cagr_ratio > 0:
                        consistency_score += 5   # Consistencia básica
            
            # 2. Sharpe Ratio IS/OOS (datos reales)
            if 'Sharpe Ratio (IS)' in strategy_data and 'Sharpe Ratio (OOS)' in strategy_data:
                sharpe_is = strategy_data['Sharpe Ratio (IS)']
                sharpe_oos = strategy_data['Sharpe Ratio (OOS)']
                
                if sharpe_is > 0:
                    sharpe_ratio = sharpe_oos / sharpe_is
                    if self.thresholds["min_is_oos_ratio"] <= sharpe_ratio <= self.thresholds["max_is_oos_ratio"]:
                        consistency_score += 25  # Excelente consistencia
                    elif 0.5 <= sharpe_ratio <= 1.5:
                        consistency_score += 15  # Buena consistencia
                    elif sharpe_ratio > 0:
                        consistency_score += 5   # Consistencia básica
            
            # 3. Profit Factor IS/OOS (datos reales)
            if 'Profit factor (IS)' in strategy_data and 'Profit factor (OOS)' in strategy_data:
                pf_is = strategy_data['Profit factor (IS)']
                pf_oos = strategy_data['Profit factor (OOS)']
                
                if pf_is > 1:
                    pf_ratio = pf_oos / pf_is
                    if self.thresholds["min_is_oos_ratio"] <= pf_ratio <= self.thresholds["max_is_oos_ratio"]:
                        consistency_score += 25  # Excelente consistencia
                    elif 0.5 <= pf_ratio <= 1.5:
                        consistency_score += 15  # Buena consistencia
                    elif pf_ratio > 0:
                        consistency_score += 5   # Consistencia básica
            
            # 4. Drawdown IS/OOS (datos reales)
            if 'Drawdown (IS)' in strategy_data and 'Drawdown (OOS)' in strategy_data:
                dd_is = abs(strategy_data['Drawdown (IS)'])
                dd_oos = abs(strategy_data['Drawdown (OOS)'])
                
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
                total_months = strategy_data['Total Data Months']
                
                if total_months >= self.thresholds["preferred_months"]:
                    robustness_score += 30  # Excelente robustez
                elif total_months >= self.thresholds["min_total_months"]:
                    robustness_score += 20  # Buena robustez
                elif total_months >= 6:
                    robustness_score += 10  # Robustez básica
            
            # 2. Number of Trades (datos reales)
            if '# of trades' in strategy_data:
                trades = strategy_data['# of trades']
                
                if trades >= self.thresholds["preferred_trades"]:
                    robustness_score += 30  # Excelente robustez
                elif trades >= self.thresholds["min_trades"]:
                    robustness_score += 20  # Buena robustez
                elif trades >= 25:
                    robustness_score += 10  # Robustez básica
            
            # 3. Winning Percent (datos reales)
            if 'Winning Percent' in strategy_data:
                win_rate = strategy_data['Winning Percent']
                
                if 0.4 <= win_rate <= 0.7:  # Rango óptimo
                    robustness_score += 20
                elif 0.3 <= win_rate <= 0.8:  # Rango aceptable
                    robustness_score += 10
            
            # 4. Exposure (datos reales)
            if 'Exposure' in strategy_data:
                exposure = strategy_data['Exposure']
                
                if 0.1 <= exposure <= 0.9:  # Rango saludable
                    robustness_score += 10
                elif 0.05 <= exposure <= 0.95:  # Rango aceptable
                    robustness_score += 5
            
            # 5. Max Drawdown Duration (datos reales)
            if 'Max Drawdown Duration' in strategy_data:
                dd_duration = strategy_data['Max Drawdown Duration']
                
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
            
            # 1. Profit Factor IS vs OOS (datos reales)
            if 'Profit factor (IS)' in strategy_data and 'Profit factor (OOS)' in strategy_data:
                pf_is = strategy_data['Profit factor (IS)']
                pf_oos = strategy_data['Profit factor (OOS)']
                
                if pf_is > self.thresholds["max_profit_factor_is"]:
                    overfitting_score -= 30  # IS demasiado bueno
                
                if pf_oos < pf_is * 0.7:
                    overfitting_score -= 25  # OOS mucho peor que IS
            
            # 2. Drawdown IS vs OOS (datos reales)
            if 'Drawdown (IS)' in strategy_data and 'Drawdown (OOS)' in strategy_data:
                dd_is = abs(strategy_data['Drawdown (IS)'])
                dd_oos = abs(strategy_data['Drawdown (OOS)'])
                
                if dd_oos > dd_is * 1.5:
                    overfitting_score -= 20  # OOS drawdown mucho peor
            
            # 3. Sharpe Ratio IS vs OOS (datos reales)
            if 'Sharpe Ratio (IS)' in strategy_data and 'Sharpe Ratio (OOS)' in strategy_data:
                sharpe_is = strategy_data['Sharpe Ratio (IS)']
                sharpe_oos = strategy_data['Sharpe Ratio (OOS)']
                
                if sharpe_oos < sharpe_is * 0.6:
                    overfitting_score -= 20  # OOS Sharpe mucho peor
            
            # 4. Max DD % (datos reales)
            if 'Max DD %' in strategy_data:
                max_dd = strategy_data['Max DD %']
                
                if max_dd > self.thresholds["max_dd_threshold"]:
                    overfitting_score -= 15  # Drawdown muy alto
            
            # 5. Recovery Factor (datos reales)
            if 'RecoveryFactor' in strategy_data:
                recovery_factor = strategy_data['RecoveryFactor']
                
                if recovery_factor < self.thresholds["min_recovery_factor"]:
                    overfitting_score -= 10  # Recuperación pobre
            
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
                calmar = strategy_data['CalmarRatio']
                
                if calmar >= self.thresholds["min_calmar_ratio"]:
                    stability_score += 25
                elif calmar >= 0.5:
                    stability_score += 15
                elif calmar >= 0:
                    stability_score += 5
            
            # 2. SQN (datos reales)
            if 'SQN' in strategy_data:
                sqn = strategy_data['SQN']
                
                if sqn >= self.thresholds["min_sqn"]:
                    stability_score += 25
                elif sqn >= 0.5:
                    stability_score += 15
                elif sqn >= 0:
                    stability_score += 5
            
            # 3. Sortino Ratio (datos reales)
            if 'Sortino Ratio' in strategy_data:
                sortino = strategy_data['Sortino Ratio']
                
                if sortino >= self.thresholds["min_sortino"]:
                    stability_score += 20
                elif sortino >= 0.5:
                    stability_score += 10
                elif sortino >= 0:
                    stability_score += 5
            
            # 4. VaR (datos reales)
            if 'VaR (95%)' in strategy_data:
                var = abs(strategy_data['VaR (95%)'])
                
                if var <= 0.05:  # VaR bajo
                    stability_score += 15
                elif var <= 0.10:
                    stability_score += 10
                elif var <= 0.15:
                    stability_score += 5
            
            # 5. CVaR (datos reales)
            if 'CVaR (95%)' in strategy_data:
                cvar = abs(strategy_data['CVaR (95%)'])
                
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
        
        Args:
            strategy_data: Datos de la estrategia del Excel
            
        Returns:
            Métricas de predictibilidad completas
        """
        try:
            # Calcular todas las métricas
            is_oos_consistency = self.calculate_is_oos_consistency(strategy_data)
            temporal_robustness = self.calculate_temporal_robustness(strategy_data)
            overfitting_detection = self.detect_overfitting(strategy_data)
            stability_score = self.calculate_stability_score(strategy_data)
            
            # Score general de predictibilidad (promedio ponderado)
            overall_predictability = (
                is_oos_consistency * 0.30 +      # 30% peso
                temporal_robustness * 0.25 +     # 25% peso
                overfitting_detection * 0.25 +    # 25% peso
                stability_score * 0.20            # 20% peso
            )
            
            return PredictabilityMetrics(
                is_oos_consistency=is_oos_consistency,
                temporal_robustness=temporal_robustness,
                overfitting_detection=overfitting_detection,
                stability_score=stability_score,
                overall_predictability=overall_predictability
            )
            
        except Exception as e:
            self.logger.error(f"Error calculando predictibilidad general: {e}")
            return PredictabilityMetrics(0.0, 0.0, 0.0, 0.0, 0.0)

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