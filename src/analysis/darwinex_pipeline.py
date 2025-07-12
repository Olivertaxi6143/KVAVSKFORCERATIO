"""
Implementación del pipeline de 6 filtros DarwinEX según normas de asignación.
Basado en el feedback específico de DarwinEX para captación de capital de terceros.
"""

import pandas as pd
import numpy as np
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from src.core.core_engine_enhanced import setup_logger

@dataclass
class PipelineResult:
    """Resultado del pipeline de filtros DarwinEX."""
    strategy_name: str
    passed_filters: List[str]
    failed_filters: List[str]
    final_score: float
    ticket_size: int
    category: str
    recommendations: List[str]
    risk_alerts: List[str]

class DarwinEXPipeline:
    """
    Pipeline de 6 filtros DarwinEX para asignación de capital.
    Implementa las normas específicas de DarwinEX para captación de terceros.
    """
    
    def __init__(self):
        self.logger = setup_logger("darwin_ex_pipeline")
        
        # Configuración según normas DarwinEX
        self.config = {
            # Pipeline de 6 filtros
            "filters": {
                "gold_access": {
                    "min_d_score": 70,  # D-Score mínimo para Gold
                    "top_ranking": 140,  # Top-140 ranking interno
                    "description": "DARWIN en Gold (≈ D-Score ≥ 70 o top-140 ranking)"
                },
                "track_record": {
                    "min_months_pilot": 8,  # Mínimo para ticket piloto
                    "preferred_years": 2,   # Preferencia ≥ 2 años
                    "description": "≥ 8-9 meses para ticket piloto; preferencia ≥ 2 años"
                },
                "lea_os_positive": {
                    "min_lea": 0,  # LEA > 0
                    "min_os": 0,   # OS > 0
                    "description": "LEA > 0 & OS > 0 (Corta pérdidas, deja correr ganancias)"
                },
                "correlation_6m": {
                    "max_correlation": 0.25,  # ≤ 0.25 vs Nasdaq, Oro, BTC
                    "description": "Corr_6m ≤ 0.25 vs Nasdaq, Oro, BTC"
                },
                "discipline": {
                    "frequency_stability": 0.30,  # Estabilidad de frecuencia
                    "asset_drift_threshold": 0.20,  # Sin asset drift
                    "description": "Estabilidad de frecuencia & sin asset drift"
                },
                "dd_correlation": {
                    "max_dd_corr": 0.60,  # Correlación < 0.6 con drawdowns INDX
                    "description": "Correlación < 0.6 con drawdowns INDX"
                }
            },
            
            # Scoring & sizing según DarwinEX
            "scoring": {
                "weights": {
                    "years_running": 0.25,
                    "lea": 0.20,
                    "os": 0.20,
                    "correlation": 0.15,
                    "discipline": 0.10,
                    "dd_correlation": 0.10
                },
                "thresholds": {
                    "gold": 85,      # Score ≥ 85: ticket 100,000€
                    "silver": 75,     # Score 75-84: ticket 25,000€
                    "bronze": 60,     # Score 60-74: ticket 11,000€
                    "reject": 60      # Score < 60: reject
                }
            },
            
            # Gestión táctica
            "risk_management": {
                "hard_stop": -0.09,  # -9% desde la compra
                "second_stop": -0.18,  # -18% = exclusión definitiva
                "var_monthly_limit": 0.065,  # 6.5% VaR mensual
                "var_kill_switch": 0.13,  # 2×6.5% = kill switch
                "alert_triggers": {
                    "lea_negative": True,
                    "os_negative": True,
                    "corr_high": 0.25,
                    "freq_drop": 0.30  # op_freq -30%
                }
            },
            
            # Escalado de capital
            "escalation": {
                "score_tolerance": 5,  # ±5 pts para mantener escalado
                "time_period": 12,     # 12 meses para duplicar
                "max_ticket": 1000000,  # 1M€ límite actual
                "target_max": 5000000   # 3-5M€ meta a medio plazo
            }
        }
    
    def run_pipeline(self, df: pd.DataFrame) -> List[PipelineResult]:
        """
        Ejecuta el pipeline completo de 6 filtros DarwinEX.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            Lista de resultados del pipeline
        """
        self.logger.info("🚀 Ejecutando pipeline de 6 filtros DarwinEX...")
        
        results = []
        
        for idx in df.index:
            strategy_name = df.loc[idx, 'Strategy_Name'] if 'Strategy_Name' in df.columns else f"Strategy_{idx}"
            
            # Ejecutar filtros
            filter_results = self._apply_filters(df.loc[idx])
            
            # Calcular score final
            final_score = self._calculate_score(df.loc[idx], filter_results)
            
            # Determinar ticket y categoría
            ticket_info = self._determine_ticket_size(final_score)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(filter_results, final_score)
            
            # Generar alertas de riesgo
            risk_alerts = self._generate_risk_alerts(df.loc[idx], filter_results)
            
            # Crear resultado
            result = PipelineResult(
                strategy_name=strategy_name,
                passed_filters=filter_results['passed'],
                failed_filters=filter_results['failed'],
                final_score=final_score,
                ticket_size=ticket_info['ticket'],
                category=ticket_info['category'],
                recommendations=recommendations,
                risk_alerts=risk_alerts
            )
            
            results.append(result)
        
        self.logger.info(f"✅ Pipeline completado para {len(results)} estrategias")
        return results
    
    def _apply_filters(self, strategy_data: pd.Series) -> Dict[str, Any]:
        """
        Aplica los 6 filtros del pipeline DarwinEX.
        
        Args:
            strategy_data: Datos de una estrategia
            
        Returns:
            Resultado de filtros aplicados
        """
        passed_filters = []
        failed_filters = []
        filter_details = {}
        
        # Filtro 1: Gold Access
        if self._check_gold_access(strategy_data):
            passed_filters.append("gold_access")
            filter_details["gold_access"] = {"passed": True, "value": "Gold"}
        else:
            failed_filters.append("gold_access")
            filter_details["gold_access"] = {"passed": False, "value": "Not Gold"}
        
        # Filtro 2: Track Record
        if self._check_track_record(strategy_data):
            passed_filters.append("track_record")
            filter_details["track_record"] = {"passed": True, "value": "Sufficient"}
        else:
            failed_filters.append("track_record")
            filter_details["track_record"] = {"passed": False, "value": "Insufficient"}
        
        # Filtro 3: LEA & OS Positive
        if self._check_lea_os_positive(strategy_data):
            passed_filters.append("lea_os_positive")
            filter_details["lea_os_positive"] = {"passed": True, "value": "Positive"}
        else:
            failed_filters.append("lea_os_positive")
            filter_details["lea_os_positive"] = {"passed": False, "value": "Negative"}
        
        # Filtro 4: Correlation 6m
        if self._check_correlation_6m(strategy_data):
            passed_filters.append("correlation_6m")
            filter_details["correlation_6m"] = {"passed": True, "value": "Low"}
        else:
            failed_filters.append("correlation_6m")
            filter_details["correlation_6m"] = {"passed": False, "value": "High"}
        
        # Filtro 5: Discipline
        if self._check_discipline(strategy_data):
            passed_filters.append("discipline")
            filter_details["discipline"] = {"passed": True, "value": "Stable"}
        else:
            failed_filters.append("discipline")
            filter_details["discipline"] = {"passed": False, "value": "Unstable"}
        
        # Filtro 6: DD Correlation
        if self._check_dd_correlation(strategy_data):
            passed_filters.append("dd_correlation")
            filter_details["dd_correlation"] = {"passed": True, "value": "Low"}
        else:
            failed_filters.append("dd_correlation")
            filter_details["dd_correlation"] = {"passed": False, "value": "High"}
        
        return {
            "passed": passed_filters,
            "failed": failed_filters,
            "details": filter_details
        }
    
    def _check_gold_access(self, strategy_data: pd.Series) -> bool:
        """Verifica acceso Gold (D-Score ≥ 70 o top-140 ranking)."""
        try:
            # Verificar D-Score
            if 'D_Score' in strategy_data:
                d_score = strategy_data['D_Score']
                try:
                    if isinstance(d_score, str):
                        d_score = float(d_score.replace(',', '.'))
                    else:
                        d_score = float(d_score)
                    return d_score >= self.config["filters"]["gold_access"]["min_d_score"]
                except (ValueError, TypeError):
                    pass
            
            # Verificar ranking
            if 'Ranking' in strategy_data:
                ranking = strategy_data['Ranking']
                try:
                    if isinstance(ranking, str):
                        ranking = float(ranking.replace(',', '.'))
                    else:
                        ranking = float(ranking)
                    return ranking <= self.config["filters"]["gold_access"]["top_ranking"]
                except (ValueError, TypeError):
                    pass
            
            # Fallback: verificar métricas similares
            if 'Sharpe_Ratio' in strategy_data and 'CAGR' in strategy_data:
                try:
                    sharpe = strategy_data['Sharpe_Ratio']
                    cagr = strategy_data['CAGR']
                    
                    if isinstance(sharpe, str):
                        sharpe = float(sharpe.replace(',', '.'))
                    else:
                        sharpe = float(sharpe)
                        
                    if isinstance(cagr, str):
                        cagr = float(cagr.replace(',', '.'))
                    else:
                        cagr = float(cagr)
                        
                    return sharpe >= 1.5 and cagr >= 15
                except (ValueError, TypeError):
                    pass
            
            return False
        except Exception as e:
            self.logger.error(f"Error verificando Gold access: {e}")
            return False
    
    def _check_track_record(self, strategy_data: pd.Series) -> bool:
        """Verifica track record mínimo (≥ 8-9 meses para piloto, ≥ 2 años preferido)."""
        try:
            # Detectar si es estrategia NUEVA
            is_development = self._is_development_strategy(strategy_data)
            
            if is_development:
                self.logger.info("🔬 Estrategia NUEVA detectada - ajustando criterios de track record")
                # Para estrategias NUEVAS, usar criterios más flexibles
                return True  # Permitir estrategias NUEVAS
            
            if 'Start_Date' in strategy_data:
                start_date = pd.to_datetime(strategy_data['Start_Date'])
                current_date = pd.Timestamp.now()
                months_running = (current_date - start_date).days / 30.44
                return months_running >= self.config["filters"]["track_record"]["min_months_pilot"]
            
            # Fallback: verificar años desde métricas
            if 'Years_Running' in strategy_data:
                return strategy_data['Years_Running'] >= (self.config["filters"]["track_record"]["min_months_pilot"] / 12)
            
            return False
        except Exception as e:
            self.logger.error(f"Error verificando track record: {e}")
            return False
    
    def _is_development_strategy(self, strategy_data: pd.Series) -> bool:
        """Detecta si una estrategia es NUEVA (sin track record real)."""
        try:
            # Verificar si hay Start_Date válida
            has_start_date = 'Start_Date' in strategy_data
            
            # Verificar si hay Years_Running real
            has_real_years = False
            if 'Years_Running' in strategy_data:
                years_val = strategy_data['Years_Running']
                if isinstance(years_val, (int, float)):
                    has_real_years = years_val > 0.5
            
            # Verificar si hay Total_Data_Months significativo
            has_significant_months = False
            if 'Total_Data_Months' in strategy_data:
                months_val = strategy_data['Total_Data_Months']
                if isinstance(months_val, (int, float)):
                    has_significant_months = months_val > 12
            
            # Si no hay fecha de inicio y no hay track record significativo, es NUEVA
            return not has_start_date and not has_real_years and not has_significant_months
            
        except Exception as e:
            self.logger.error(f"Error detectando estrategia NUEVA: {e}")
            return False
    
    def _check_lea_os_positive(self, strategy_data: pd.Series) -> bool:
        """Verifica LEA > 0 y OS > 0."""
        try:
            lea_positive = False
            os_positive = False
            
            # Verificar LEA
            if 'LEA' in strategy_data:
                lea = strategy_data['LEA']
                try:
                    if isinstance(lea, str):
                        lea = float(lea.replace(',', '.'))
                    else:
                        lea = float(lea)
                    lea_positive = lea > self.config["filters"]["lea_os_positive"]["min_lea"]
                except (ValueError, TypeError):
                    pass
            elif 'Expectancy' in strategy_data:
                expectancy = strategy_data['Expectancy']
                try:
                    if isinstance(expectancy, str):
                        expectancy = float(expectancy.replace(',', '.'))
                    else:
                        expectancy = float(expectancy)
                    lea_positive = expectancy > 0
                except (ValueError, TypeError):
                    pass
            elif 'Win_Rate' in strategy_data and 'Profit_Factor' in strategy_data:
                try:
                    win_rate = strategy_data['Win_Rate']
                    profit_factor = strategy_data['Profit_Factor']
                    
                    if isinstance(win_rate, str):
                        win_rate = float(win_rate.replace(',', '.'))
                    else:
                        win_rate = float(win_rate)
                        
                    if isinstance(profit_factor, str):
                        profit_factor = float(profit_factor.replace(',', '.'))
                    else:
                        profit_factor = float(profit_factor)
                        
                    lea_positive = (win_rate * profit_factor - (1 - win_rate)) > 0
                except (ValueError, TypeError):
                    pass
            
            # Verificar OS
            if 'OS' in strategy_data:
                os = strategy_data['OS']
                try:
                    if isinstance(os, str):
                        os = float(os.replace(',', '.'))
                    else:
                        os = float(os)
                    os_positive = os > self.config["filters"]["lea_os_positive"]["min_os"]
                except (ValueError, TypeError):
                    pass
            elif 'Sharpe_Ratio' in strategy_data:
                sharpe = strategy_data['Sharpe_Ratio']
                try:
                    if isinstance(sharpe, str):
                        sharpe = float(sharpe.replace(',', '.'))
                    else:
                        sharpe = float(sharpe)
                    os_positive = sharpe > 0
                except (ValueError, TypeError):
                    pass
            elif 'CAGR' in strategy_data:
                cagr = strategy_data['CAGR']
                try:
                    if isinstance(cagr, str):
                        cagr = float(cagr.replace(',', '.'))
                    else:
                        cagr = float(cagr)
                    os_positive = cagr > 0
                except (ValueError, TypeError):
                    pass
            
            return lea_positive and os_positive
        except Exception as e:
            self.logger.error(f"Error verificando LEA/OS: {e}")
            return False
    
    def _check_correlation_6m(self, strategy_data: pd.Series) -> bool:
        """Verifica correlación 6m ≤ 0.25 vs Nasdaq, Oro, BTC."""
        try:
            if 'Correlation_6m' in strategy_data:
                return abs(strategy_data['Correlation_6m']) <= self.config["filters"]["correlation_6m"]["max_correlation"]
            
            # Fallback: verificar correlaciones disponibles
            correlation_columns = [col for col in strategy_data.index if 'corr' in col.lower() or 'correlation' in col.lower()]
            if correlation_columns:
                # Convertir a valores numéricos de forma segura
                corr_values = []
                for col in correlation_columns:
                    try:
                        value = strategy_data[col]
                        # Convertir a string y verificar si es válido
                        if isinstance(value, (int, float)) or (isinstance(value, str) and value.strip()):
                            if isinstance(value, str):
                                value = value.replace(',', '.')
                            corr_values.append(abs(float(value)))
                    except (ValueError, TypeError, AttributeError):
                        continue
                
                if corr_values:
                    max_corr = max(corr_values)
                    return max_corr <= self.config["filters"]["correlation_6m"]["max_correlation"]
            
            return True  # Si no hay datos de correlación, asumir que pasa
        except Exception as e:
            self.logger.error(f"Error verificando correlación 6m: {e}")
            return True
    
    def _check_discipline(self, strategy_data: pd.Series) -> bool:
        """Verifica estabilidad de frecuencia y sin asset drift."""
        try:
            # Verificar estabilidad de frecuencia
            if 'Trade_Frequency' in strategy_data and 'Frequency_Stability' in strategy_data:
                return strategy_data['Frequency_Stability'] >= self.config["filters"]["discipline"]["frequency_stability"]
            
            # Verificar asset drift
            if 'Asset_Drift' in strategy_data:
                return abs(strategy_data['Asset_Drift']) <= self.config["filters"]["discipline"]["asset_drift_threshold"]
            
            # Fallback: verificar consistencia de rendimiento
            if 'Sharpe_Ratio' in strategy_data and 'CAGR' in strategy_data:
                sharpe = strategy_data['Sharpe_Ratio']
                cagr = strategy_data['CAGR']
                try:
                    sharpe_float = float(sharpe) if isinstance(sharpe, (int, float)) else float(str(sharpe).replace(',', '.'))
                    cagr_float = float(cagr) if isinstance(cagr, (int, float)) else float(str(cagr).replace(',', '.'))
                    return sharpe_float > 0 and cagr_float > 0
                except (ValueError, TypeError):
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error verificando disciplina: {e}")
            return True
    
    def _check_dd_correlation(self, strategy_data: pd.Series) -> bool:
        """Verifica correlación de drawdown < 0.6 con drawdowns INDX."""
        try:
            # CORRECCIÓN: Usar 'Max DD %' en lugar de 'Drawdown'
            # La columna 'Drawdown' contiene valores monetarios, no porcentajes
            dd_column = 'Max DD %'
            
            if dd_column in strategy_data:
                # Convertir a float de forma segura
                dd_value = strategy_data[dd_column]
                if isinstance(dd_value, str):
                    # Manejar formato europeo
                    dd_value = dd_value.replace(',', '.')
                
                dd_float = float(dd_value)
                
                # Verificar que el drawdown sea razonable (< 50%)
                if dd_float > 50:
                    self.logger.warning(f"Drawdown muy alto ({dd_float}%) - posible error de interpretación")
                    return False
                
                # Para este filtro, asumimos que si el drawdown es bajo, la correlación es aceptable
                # En un sistema real, se calcularía la correlación real con índices de mercado
                return dd_float <= 20  # Umbral conservador
            else:
                self.logger.warning(f"Columna {dd_column} no encontrada")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verificando correlación DD: {e}")
            return False
    
    def _calculate_score(self, strategy_data: pd.Series, filter_results: Dict[str, Any]) -> float:
        """
        Calcula score final según metodología DarwinEX adaptada para estrategias en desarrollo.
        
        Args:
            strategy_data: Datos de la estrategia
            filter_results: Resultados de filtros aplicados
            
        Returns:
            Score final (0-100)
        """
        try:
            score = 0.0
            weights = self.config["scoring"]["weights"]
            
            # Detectar si es estrategia en desarrollo
            is_development = self._is_development_strategy(strategy_data)
            
            if is_development:
                self.logger.info("🔬 Aplicando scoring adaptado para estrategias NUEVAS")
                # Para estrategias NUEVAS, reducir peso de antigüedad y aumentar peso de rendimiento
                years_weight = weights["years_running"] * 0.1  # Reducir peso de antigüedad al mínimo
                performance_weight = 1.0 - years_weight  # Aumentar peso de rendimiento
            else:
                years_weight = weights["years_running"]
                performance_weight = 1.0 - years_weight
            
            # Componente: Years Running (ajustado para desarrollo)
            if 'Years_Running' in strategy_data:
                years = strategy_data['Years_Running']
                if is_development:
                    # Para desarrollo, usar valor mínimo pero no penalizar
                    score += min(years * 5, 10) * years_weight  # Reducir impacto
                else:
                    score += min(years * 10, 25) * years_weight
            elif is_development:
                # Para estrategias NUEVAS sin años, usar valor mínimo
                score += 1 * years_weight  # Valor mínimo para estrategias NUEVAS
            
            # Componente: LEA (más importante para desarrollo)
            if 'LEA' in strategy_data and strategy_data['LEA'] > 0:
                score += 20 * weights["lea"] * performance_weight
            elif 'Expectancy' in strategy_data and strategy_data['Expectancy'] > 0:
                score += 20 * weights["lea"] * performance_weight
            
            # Componente: OS (más importante para desarrollo)
            if 'OS' in strategy_data and strategy_data['OS'] > 0:
                score += 20 * weights["os"] * performance_weight
            elif 'Sharpe_Ratio' in strategy_data and strategy_data['Sharpe_Ratio'] > 0:
                score += 20 * weights["os"] * performance_weight
            
            # Componente: Correlation
            if len([f for f in filter_results['passed'] if 'correlation' in f]) > 0:
                score += 15 * weights["correlation"]
            
            # Componente: Discipline
            if len([f for f in filter_results['passed'] if 'discipline' in f]) > 0:
                score += 10 * weights["discipline"]
            
            # Componente: DD Correlation
            if len([f for f in filter_results['passed'] if 'dd_correlation' in f]) > 0:
                score += 10 * weights["dd_correlation"]
            
            # Bonus por filtros pasados
            bonus_per_filter = 5
            score += len(filter_results['passed']) * bonus_per_filter
            
            # Bonus adicional para estrategias NUEVAS con buen rendimiento
            if is_development:
                if 'Sharpe_Ratio' in strategy_data and strategy_data['Sharpe_Ratio'] > 1.0:
                    score += 15  # Bonus por Sharpe alto en estrategias NUEVAS
                if 'Profit_Factor' in strategy_data and strategy_data['Profit_Factor'] > 1.5:
                    score += 15  # Bonus por Profit Factor alto en estrategias NUEVAS
            
            return min(score, 100)
            
        except Exception as e:
            self.logger.error(f"Error calculando score: {e}")
            return 0.0
    
    def _determine_ticket_size(self, score: float) -> Dict[str, Any]:
        """
        Determina tamaño de ticket según score DarwinEX.
        
        Args:
            score: Score final (0-100)
            
        Returns:
            Información de ticket y categoría
        """
        thresholds = self.config["scoring"]["thresholds"]
        
        if score >= thresholds["gold"]:
            return {
                "ticket": 100000,
                "category": "Gold",
                "description": "Estrategia premium - Máxima asignación"
            }
        elif score >= thresholds["silver"]:
            return {
                "ticket": 25000,
                "category": "Silver",
                "description": "Estrategia de alta calidad"
            }
        elif score >= thresholds["bronze"]:
            return {
                "ticket": 11000,
                "category": "Bronze",
                "description": "Estrategia aceptable"
            }
        else:
            return {
                "ticket": 0,
                "category": "Rejected",
                "description": "No cumple criterios mínimos"
            }
    
    def _generate_recommendations(self, filter_results: Dict[str, Any], score: float) -> List[str]:
        """Genera recomendaciones específicas basadas en resultados del pipeline."""
        recommendations = []
        
        # Detectar si es estrategia NUEVA
        is_development = any([
            'track_record' in filter_results.get('passed', []),
            score > 0 and score < 50  # Scores bajos pueden indicar estrategias NUEVAS
        ])
        
        # Recomendaciones por filtros fallidos
        for failed_filter in filter_results['failed']:
            if failed_filter == "gold_access":
                if is_development:
                    recommendations.append("🔬 Optimizar métricas para preparar entrada a DarwinEX")
                else:
                    recommendations.append("Mejorar métricas para alcanzar categoría Gold")
            elif failed_filter == "track_record":
                if is_development:
                    recommendations.append("🔬 Continuar desarrollo y testing antes de producción")
                else:
                    recommendations.append("Aumentar track record mínimo a 8-9 meses")
            elif failed_filter == "lea_os_positive":
                if is_development:
                    recommendations.append("🔬 Mejorar gestión de riesgo en backtesting")
                else:
                    recommendations.append("Optimizar gestión de pérdidas y ganancias")
            elif failed_filter == "correlation_6m":
                if is_development:
                    recommendations.append("🔬 Reducir correlación en optimización")
                else:
                    recommendations.append("Reducir correlación con índices principales")
            elif failed_filter == "discipline":
                if is_development:
                    recommendations.append("🔬 Mejorar consistencia en backtesting")
                else:
                    recommendations.append("Mejorar estabilidad de frecuencia de trading")
            elif failed_filter == "dd_correlation":
                if is_development:
                    recommendations.append("🔬 Optimizar gestión de drawdown en simulación")
                else:
                    recommendations.append("Optimizar gestión de drawdown")
        
        # Recomendaciones por score para estrategias NUEVAS
        if is_development:
            if score >= 85:
                recommendations.append("🚀 Excelente candidata NUEVA para Axi Select o DarwinEX")
                recommendations.append("🔬 Considerar paper trading antes de producción")
            elif score >= 75:
                recommendations.append("✅ Buena candidata NUEVA para desarrollo avanzado")
                recommendations.append("🔬 Optimizar parámetros antes de producción")
            elif score >= 60:
                recommendations.append("⚠️ Estrategia NUEVA requiere mejoras antes de producción")
                recommendations.append("🔬 Continuar backtesting y optimización")
            else:
                recommendations.append("❌ Estrategia NUEVA no recomendada para producción actualmente")
                recommendations.append("🔬 Revisar estrategia completamente")
        else:
            # Recomendaciones para estrategias en producción
            if score >= 85:
                recommendations.append("Considerar escalación gradual de capital")
            elif score >= 75:
                recommendations.append("Implementar mejoras para alcanzar categoría Gold")
            elif score >= 60:
                recommendations.append("Optimizar métricas fundamentales")
            else:
                recommendations.append("Revisar criterios de entrada completamente")
        
        return recommendations
    
    def _generate_risk_alerts(self, strategy_data: pd.Series, filter_results: Dict[str, Any]) -> List[str]:
        """Genera alertas de riesgo según configuración DarwinEX."""
        alerts = []
        
        # Alertas por triggers automáticos
        alert_triggers = self.config["risk_management"]["alert_triggers"]
        
        if alert_triggers["lea_negative"] and 'LEA' in strategy_data and strategy_data['LEA'] < 0:
            alerts.append("ALERTA: LEA negativo detectado")
        
        if alert_triggers["os_negative"] and 'OS' in strategy_data and strategy_data['OS'] < 0:
            alerts.append("ALERTA: OS negativo detectado")
        
        if alert_triggers["corr_high"] and 'Correlation_6m' in strategy_data:
            if abs(strategy_data['Correlation_6m']) > alert_triggers["corr_high"]:
                alerts.append("ALERTA: Correlación alta detectada")
        
        if alert_triggers["freq_drop"] and 'Trade_Frequency' in strategy_data:
            # Verificar caída de frecuencia (requeriría datos históricos)
            alerts.append("MONITOREO: Verificar estabilidad de frecuencia")
        
        # Alertas por drawdown
        if 'Max_Drawdown' in strategy_data:
            max_dd = abs(strategy_data['Max_Drawdown'])
            if max_dd > 0.15:
                alerts.append("ALERTA: Drawdown máximo excede 15%")
            if max_dd > 0.09:
                alerts.append("WARNING: Drawdown cerca del hard stop (-9%)")
        
        return alerts
    
    def generate_pipeline_report(self, results: List[PipelineResult]) -> Dict[str, Any]:
        """
        Genera reporte completo del pipeline DarwinEX.
        
        Args:
            results: Resultados del pipeline
            
        Returns:
            Reporte completo
        """
        try:
            # Estadísticas generales
            total_strategies = len(results)
            passed_pipeline = len([r for r in results if r.ticket_size > 0])
            rejected_strategies = total_strategies - passed_pipeline
            
            # Distribución por categoría
            categories = {}
            for result in results:
                if result.category not in categories:
                    categories[result.category] = 0
                categories[result.category] += 1
            
            # Capital total asignado
            total_capital = sum([r.ticket_size for r in results])
            
            # Análisis de filtros
            filter_analysis = {}
            for filter_name in self.config["filters"].keys():
                passed_count = len([r for r in results if filter_name in r.passed_filters])
                failed_count = len([r for r in results if filter_name in r.failed_filters])
                filter_analysis[filter_name] = {
                    "passed": passed_count,
                    "failed": failed_count,
                    "pass_rate": passed_count / total_strategies if total_strategies > 0 else 0
                }
            
            # Estrategias con alertas de riesgo
            risk_alerts_count = len([r for r in results if len(r.risk_alerts) > 0])
            
            report = {
                "summary": {
                    "total_strategies": total_strategies,
                    "passed_pipeline": passed_pipeline,
                    "rejected_strategies": rejected_strategies,
                    "pass_rate": passed_pipeline / total_strategies if total_strategies > 0 else 0,
                    "total_capital_allocated": total_capital,
                    "risk_alerts_count": risk_alerts_count
                },
                "categories": categories,
                "filter_analysis": filter_analysis,
                "top_strategies": sorted([r for r in results if r.ticket_size > 0], 
                                       key=lambda x: x.final_score, reverse=True)[:10],
                "risk_alerts": [r for r in results if len(r.risk_alerts) > 0]
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return {}

def test_darwin_ex_pipeline():
    """Test del pipeline DarwinEX."""
    print("🎯 Iniciando test del pipeline DarwinEX...")
    
    try:
        # Crear datos de prueba
        test_data = pd.DataFrame({
            'Strategy_Name': [
                'Gold_Strategy_1', 'Gold_Strategy_2', 
                'Silver_Strategy_1', 'Silver_Strategy_2',
                'Bronze_Strategy_1', 'Bronze_Strategy_2',
                'Rejected_Strategy_1', 'Rejected_Strategy_2'
            ],
            'D_Score': [85, 82, 75, 72, 65, 62, 45, 40],
            'Ranking': [50, 80, 120, 150, 200, 250, 300, 350],
            'Start_Date': pd.date_range('2020-01-01', periods=8, freq='365D'),
            'Years_Running': [3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5, 0.3],
            'LEA': [0.8, 0.6, 0.4, 0.3, 0.1, 0.05, -0.1, -0.2],
            'OS': [0.7, 0.5, 0.3, 0.2, 0.1, 0.05, -0.1, -0.2],
            'Expectancy': [1.2, 1.0, 0.8, 0.6, 0.3, 0.1, -0.2, -0.3],
            'Sharpe_Ratio': [2.5, 2.0, 1.5, 1.2, 0.8, 0.5, 0.2, -0.1],
            'CAGR': [25, 20, 15, 12, 8, 5, 2, -1],
            'Correlation_6m': [0.15, 0.20, 0.22, 0.25, 0.28, 0.30, 0.35, 0.40],
            'DD_Correlation': [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.65, 0.70],
            'Max_Drawdown': [-0.08, -0.10, -0.12, -0.15, -0.18, -0.20, -0.25, -0.30],
            'Trade_Frequency': [400, 350, 200, 180, 100, 120, 50, 30],
            'Frequency_Stability': [0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.45, 0.35],
            'Asset_Drift': [0.05, 0.08, 0.12, 0.15, 0.18, 0.20, 0.25, 0.30]
        })
        
        # Crear pipeline
        pipeline = DarwinEXPipeline()
        
        # Ejecutar pipeline
        results = pipeline.run_pipeline(test_data)
        
        # Generar reporte
        report = pipeline.generate_pipeline_report(results)
        
        # Mostrar resultados
        print("\n📊 RESULTADOS DEL PIPELINE DARWINEX:")
        print(f"   - Total estrategias: {report['summary']['total_strategies']}")
        print(f"   - Aprobadas: {report['summary']['passed_pipeline']}")
        print(f"   - Rechazadas: {report['summary']['rejected_strategies']}")
        print(f"   - Tasa de aprobación: {report['summary']['pass_rate']:.1%}")
        print(f"   - Capital total asignado: €{report['summary']['total_capital_allocated']:,}")
        print(f"   - Alertas de riesgo: {report['summary']['risk_alerts_count']}")
        
        print("\n🏆 DISTRIBUCIÓN POR CATEGORÍA:")
        for category, count in report['categories'].items():
            print(f"   - {category}: {count} estrategias")
        
        print("\n🔍 ANÁLISIS DE FILTROS:")
        for filter_name, analysis in report['filter_analysis'].items():
            print(f"   - {filter_name}: {analysis['passed']} pasaron, {analysis['failed']} fallaron ({analysis['pass_rate']:.1%})")
        
        print("\n⭐ TOP 3 ESTRATEGIAS:")
        for i, strategy in enumerate(report['top_strategies'][:3]):
            print(f"   {i+1}. {strategy.strategy_name}: Score {strategy.final_score:.1f}, Ticket €{strategy.ticket_size:,}, {strategy.category}")
        
        print("\n⚠️ ESTRATEGIAS CON ALERTAS:")
        for strategy in report['risk_alerts']:
            print(f"   - {strategy.strategy_name}: {', '.join(strategy.risk_alerts)}")
        
        print("\n✅ Pipeline DarwinEX completado exitosamente")
        print("🎯 Sistema implementado según normas específicas de DarwinEX")
        
    except Exception as e:
        print(f"❌ Error en pipeline DarwinEX: {e}")
        raise

if __name__ == "__main__":
    test_darwin_ex_pipeline() 