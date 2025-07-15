from typing import Optional, Any, Union
import warnings
"""
Implementación del pipeline de 6 filtros DarwinEX según normas de asignación.
Basado en el feedback específico de DarwinEX para captación de capital de terceros.
Mejorado con configuración externa, validación robusta y predictibilidad Silver→Gold.
"""

import pandas as pd
import numpy as np
import sys
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path

# Configurar logging estructurado
logging.basicConfig(level=logging.INFO)

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from src.analysis.predictability_metrics import PredictabilityAnalyzer

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
    asset_type: Optional[str] = None
    predictability_score: Optional[float] = None
    silver_to_gold_potential: Optional[float] = None

class DarwinEXPipeline:
    """
    Pipeline de 6 filtros DarwinEX para asignación de capital.
    Implementa las normas específicas de DarwinEX para captación de terceros.
    Mejorado con configuración externa y predictibilidad Silver→Gold.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger("darwin_ex_pipeline")
        self.predictability_analyzer = PredictabilityAnalyzer()
        
        # Cargar configuración externa
        self.config = self._load_configuration(config_path)
        
        # Función utilitaria para conversión de floats
        self.to_float = self._create_float_converter()
    
    def _load_configuration(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Carga configuración desde archivo JSON externo.
        
        Args:
            config_path: Ruta al archivo de configuración
            
        Returns:
            Configuración cargada
        """
        try:
            if config_path is None:
                config_path = "config/darwin_ex_config.json"
            
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"✅ Configuración cargada desde {config_path}")
                return config
            else:
                self.logger.warning(f"⚠️ Archivo de configuración no encontrado: {config_path}")
                return self._get_default_config()
                
        except Exception as e:
            self.logger.error(f"❌ Error cargando configuración: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto si no se puede cargar archivo externo."""
        return {
            "filters": {
                "gold_access": {"min_d_score": 70, "top_ranking": 140},
                "track_record": {"min_months_pilot": 8, "preferred_years": 2},
                "lea_os_positive": {"min_lea": 0, "min_os": 0},
                "correlation_6m": {"max_correlation": 0.25},
                "discipline": {"frequency_stability": 0.30, "asset_drift_threshold": 0.20},
                "dd_correlation": {"max_dd_corr": 0.60},
                "max_drawdown": 0.15
            },
            "scoring": {
                "weights": {
                    "years_running": 0.25, "lea": 0.20, "os": 0.20,
                    "correlation": 0.15, "discipline": 0.10, "dd_correlation": 0.10
                },
                "thresholds": {"gold": 85, "silver": 75, "bronze": 60, "reject": 60}
            },
            "risk_management": {
                "hard_stop": -0.09, "second_stop": -0.18, "var_monthly_limit": 0.065,
                "var_kill_switch": 0.13, "alert_triggers": {
                    "lea_negative": True, "os_negative": True, "corr_high": 0.25, "freq_drop": 0.30
                }
            },
            "escalation": {
                "score_tolerance": 5, "time_period": 12, "max_ticket": 1000000, "target_max": 5000000
            },
            "validation": {
                "required_fields": [
                    "Strategy_Name", "D_Score", "Years_Running", "LEA", "OS"
                ],
                "numeric_fields": [
                    "D_Score", "Years_Running", "LEA", "OS", "Sharpe_Ratio", "CAGR", "Max_Drawdown"
                ],
                "new_strategy_criteria": {
                    "max_years_running": 1.0, "min_total_months": 12, "development_mode_flag": True
                }
            }
        }
    
    def _is_scalar_na(self, value: Any) -> bool:
        """Devuelve True si value es un escalar NA o None (nunca devuelve array)."""
        if value is None:
            return True
        if isinstance(value, (int, float, str)):
            return pd.isna(value)
        return False

    def _create_float_converter(self):
        """
        Crea función utilitaria para conversión segura de floats.
        DRY: Evita duplicación de código de conversión.
        """
        def to_float(value: Union[str, float, int, None, pd.Series, Any]) -> float:
            try:
                # Si es un array vacío o Series/DataFrame vacío, retorna 0.0
                if isinstance(value, (np.ndarray, pd.Series, pd.DataFrame)):
                    if value.size == 0:
                        return 0.0
                    # Si es un array/serie de un solo valor, extrae el escalar
                    if hasattr(value, 'item') and value.size == 1:
                        value = value.item()
                # Solo chequea isna/None si value es escalar
                if self._is_scalar_na(value):
                    return 0.0
                if isinstance(value, (int, float)):
                    return float(value) if value is not None else 0.0 if value is not None else 0.0
                if isinstance(value, str):
                    cleaned = value.replace(',', '.').strip()
                    return float(cleaned) if cleaned is not None else 0.0 if cleaned is not None else 0.0
                return 0.0
            except (ValueError, TypeError):
                return 0.0
        
        return to_float
    
    def _validate_strategy_data(self, strategy_data: pd.Series) -> Tuple[bool, List[str]]:
        """
        Valida datos de estrategia con typing estricto.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            (es_válido, lista_de_errores)
        """
        errors = []
        
        # Verificar campos requeridos
        required_fields = self.config.get("validation", {}).get("required_fields", [
            "Strategy_Name", "D_Score", "Years_Running", "LEA", "OS"
        ])
        
        for field in required_fields:
            if field not in strategy_data:
                errors.append(f"Campo requerido faltante: {field}")
                continue
            
            value = strategy_data[field]
            # Control estricto para pandas/numpy
            if isinstance(value, (np.ndarray, pd.Series, pd.DataFrame)):
                if value.size == 0:
                    errors.append(f"Campo requerido vacío: {field}")
                    continue
            # Solo chequea isna/None si value es escalar
            if self._is_scalar_na(value):
                errors.append(f"Campo requerido vacío: {field}")
                continue
            
            # Validar campos numéricos
            numeric_fields = self.config.get("validation", {}).get("numeric_fields", [
                "D_Score", "Years_Running", "LEA", "OS", "Sharpe_Ratio", "CAGR", "Max_Drawdown"
            ])
            
            if field in numeric_fields:
                try:
                    self.to_float(value) if value is not None else 0.0 if value is not None else 0.0
                except (ValueError, TypeError):
                    errors.append(f"Campo numérico inválido: {field} = {value}")
        
        return len(errors) == 0, errors
    
    def _is_new_strategy(self, strategy_data: pd.Series) -> bool:
        """
        Detecta estrategias nuevas con criterios mejorados.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            True si es estrategia nueva
        """
        try:
            criteria = self.config.get("validation", {}).get("new_strategy_criteria", {})
            
            years_running = self.to_float(strategy_data.get('Years_Running', 0))
            total_months = self.to_float(strategy_data.get('Total_Data_Months', 0))
            development_mode = strategy_data.get('Development_Mode', False)
            
            max_years = criteria.get("max_years_running", 1.0)
            min_months = criteria.get("min_total_months", 12)
            dev_flag = criteria.get("development_mode_flag", True)
            
            return (
                years_running < max_years or
                total_months < min_months or
                (dev_flag and bool(development_mode))
            )
            
        except Exception as e:
            self.logger.error(f"Error detectando estrategia nueva: {e}")
            return False
    
    def run_pipeline(self, df: pd.DataFrame) -> List[PipelineResult]:
        """
        Ejecuta el pipeline completo de filtros DarwinEX unificados.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            Lista de resultados del pipeline
        """
        self.logger.info("🚀 Ejecutando pipeline unificado de filtros DarwinEX...")
        
        results = []
        
        for idx in df.index:
            strategy_data = df.loc[idx]
            strategy_name = strategy_data.get('Strategy_Name', f"Strategy_{idx}")
            
            # Validar datos de entrada
            is_valid, validation_errors = self._validate_strategy_data(strategy_data)
            if not is_valid:
                self.logger.warning(f"⚠️ Datos inválidos para {strategy_name}: {validation_errors}")
                continue
            
            # Detectar si es estrategia nueva
            is_new_strategy = self._is_new_strategy(strategy_data)
            
            # Ejecutar filtros unificados (originales + predictibilidad)
            unified_results = self._apply_unified_filters(strategy_data)
            
            # Calcular score final
            final_score = self._calculate_score(strategy_data, unified_results)
            
            # Calcular predictibilidad Silver→Gold
            silver_to_gold_potential = self._calculate_silver_to_gold_potential(
                strategy_data, final_score, is_new_strategy
            )
            
            # Determinar ticket y categoría
            ticket_info = self._determine_ticket_size(final_score)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(unified_results, final_score, silver_to_gold_potential)
            
            # Generar alertas de riesgo
            risk_alerts = self._generate_risk_alerts(strategy_data, unified_results)
            
            # Crear resultado
            result = PipelineResult(
                strategy_name=strategy_name,
                passed_filters=unified_results["passed"],
                failed_filters=unified_results["failed"],
                final_score=final_score,
                ticket_size=ticket_info['ticket'],
                category=ticket_info['category'],
                recommendations=recommendations,
                risk_alerts=risk_alerts,
                asset_type=strategy_data.get('Asset_Type', 'unknown'),
                predictability_score=unified_results.get('predictability_score', 0.0),
                silver_to_gold_potential=silver_to_gold_potential
            )
            
            results.append(result)
        
        self.logger.info(f"✅ Pipeline unificado completado para {len(results)} estrategias")
        return results
    
    def _apply_unified_filters(self, strategy_data: pd.Series) -> Dict[str, Any]:
        """
        Aplica filtros unificados (originales + predictibilidad) en un solo flujo.
        
        Args:
            strategy_data: Datos de una estrategia
            
        Returns:
            Resultado de filtros unificados
        """
        passed_filters = []
        failed_filters = []
        filter_details = {}
        
        # Definir todos los filtros en orden de aplicación
        all_filters = [
            ("gold_access", self._check_gold_access),
            ("track_record", self._check_track_record),
            ("lea_os_positive", self._check_lea_os_positive),
            ("correlation_6m", self._check_correlation_6m),
            ("discipline", self._check_discipline),
            ("dd_correlation", self._check_dd_correlation),
            ("is_oos_consistency", self._check_is_oos_consistency),
            ("temporal_robustness", self._check_temporal_robustness),
            ("overfitting_detection", self._check_overfitting_detection),
            ("stability_score", self._check_stability_score),
            ("drawdown_filter", self._check_drawdown_filter)
        ]
        
        # Aplicar todos los filtros
        for filter_name, filter_func in all_filters:
            try:
                if filter_func(strategy_data):
                    passed_filters.append(filter_name)
                    filter_details[filter_name] = {"passed": True, "value": "Pass"}
                else:
                    failed_filters.append(filter_name)
                    filter_details[filter_name] = {"passed": False, "value": "Fail"}
            except Exception as e:
                self.logger.error(f"Error en filtro {filter_name}: {e}")
                failed_filters.append(filter_name)
                filter_details[filter_name] = {"passed": False, "value": "Error"}
        
        # Calcular score de predictibilidad
        predictability_score = len([f for f in passed_filters if f in [
            "is_oos_consistency", "temporal_robustness", "overfitting_detection", 
            "stability_score", "drawdown_filter"
        ]]) / 5.0  # 5 filtros de predictibilidad
        
        return {
            "passed": passed_filters,
            "failed": failed_filters,
            "details": filter_details,
            "predictability_score": predictability_score,
            "total_passed": len(passed_filters),
            "total_filters": len(all_filters)
        }
    
    def _check_is_oos_consistency(self, strategy_data: pd.Series) -> bool:
        """
        Verifica consistencia IS/OOS usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            True si pasa el filtro de consistencia
        """
        try:
            # Calcular métricas de predictibilidad
            metrics = self.predictability_analyzer.calculate_overall_predictability(strategy_data)
            
            # Umbral mínimo de consistencia IS/OOS
            min_consistency = 60.0  # 60% mínimo
            
            return metrics.is_oos_consistency >= min_consistency
            
        except Exception as e:
            self.logger.error(f"Error verificando consistencia IS/OOS: {e}")
            return False
    
    def _check_temporal_robustness(self, strategy_data: pd.Series) -> bool:
        """
        Verifica robustez temporal usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            True si pasa el filtro de robustez temporal
        """
        try:
            # Calcular métricas de predictibilidad
            metrics = self.predictability_analyzer.calculate_overall_predictability(strategy_data)
            
            # Umbral mínimo de robustez temporal
            min_robustness = 50.0  # 50% mínimo
            
            return metrics.temporal_robustness >= min_robustness
            
        except Exception as e:
            self.logger.error(f"Error verificando robustez temporal: {e}")
            return False
    
    def _check_overfitting_detection(self, strategy_data: pd.Series) -> bool:
        """
        Verifica detección de sobreajuste usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            True si pasa el filtro de detección de sobreajuste
        """
        try:
            # Calcular métricas de predictibilidad
            metrics = self.predictability_analyzer.calculate_overall_predictability(strategy_data)
            
            # Umbral mínimo de detección de sobreajuste
            min_overfitting_detection = 70.0  # 70% mínimo (menos sobreajuste)
            
            return metrics.overfitting_detection >= min_overfitting_detection
            
        except Exception as e:
            self.logger.error(f"Error verificando detección de sobreajuste: {e}")
            return False
    
    def _check_stability_score(self, strategy_data: pd.Series) -> bool:
        """
        Verifica score de estabilidad usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            True si pasa el filtro de estabilidad
        """
        try:
            # Calcular métricas de predictibilidad
            metrics = self.predictability_analyzer.calculate_overall_predictability(strategy_data)
            
            # Umbral mínimo de estabilidad
            min_stability = 50.0  # 50% mínimo
            
            return metrics.stability_score >= min_stability
            
        except Exception as e:
            self.logger.error(f"Error verificando score de estabilidad: {e}")
            return False
    
    def _check_drawdown_filter(self, strategy_data: pd.Series) -> bool:
        """
        Verifica filtro de drawdown propio (mantener lógica original).
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            True si pasa el filtro de drawdown
        """
        try:
            # Usar Max DD % si está disponible
            if 'Max DD %' in strategy_data:
                max_dd = abs(self.to_float(strategy_data['Max DD %']))
                return max_dd <= self.config["filters"]["max_drawdown"]
            
            # Fallback a Drawdown si está disponible
            elif 'Drawdown' in strategy_data:
                dd = abs(self.to_float(strategy_data['Drawdown']))
                # Si el valor es muy alto (>100), probablemente son puntos monetarios
                if dd > 100:
                    return True  # No podemos determinar con seguridad
                else:
                    # Interpretar como decimal
                    dd_percent = dd * 100
                    return dd_percent <= self.config["filters"]["max_drawdown"]
            
            return True  # Si no hay datos de drawdown, pasar
            
        except Exception as e:
            self.logger.error(f"Error verificando filtro de drawdown: {e}")
            return True  # En caso de error, pasar
    
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
                        d_score = float(d_score) if d_score is not None else 0.0 if d_score is not None else 0.0
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
                        ranking = float(ranking) if ranking is not None else 0.0 if ranking is not None else 0.0
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
                        sharpe = float(sharpe) if sharpe is not None else 0.0 if sharpe is not None else 0.0
                        
                    if isinstance(cagr, str):
                        cagr = float(cagr.replace(',', '.'))
                    else:
                        cagr = float(cagr) if cagr is not None else 0.0 if cagr is not None else 0.0
                        
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
            is_development = self._is_new_strategy(strategy_data)
            
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
                        lea = float(lea) if lea is not None else 0.0 if lea is not None else 0.0
                    lea_positive = lea > self.config["filters"]["lea_os_positive"]["min_lea"]
                except (ValueError, TypeError):
                    pass
            elif 'Expectancy' in strategy_data:
                expectancy = strategy_data['Expectancy']
                try:
                    if isinstance(expectancy, str):
                        expectancy = float(expectancy.replace(',', '.'))
                    else:
                        expectancy = float(expectancy) if expectancy is not None else 0.0 if expectancy is not None else 0.0
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
                        win_rate = float(win_rate) if win_rate is not None else 0.0 if win_rate is not None else 0.0
                        
                    if isinstance(profit_factor, str):
                        profit_factor = float(profit_factor.replace(',', '.'))
                    else:
                        profit_factor = float(profit_factor) if profit_factor is not None else 0.0 if profit_factor is not None else 0.0
                        
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
                        os = float(os) if os is not None else 0.0 if os is not None else 0.0
                    os_positive = os > self.config["filters"]["lea_os_positive"]["min_os"]
                except (ValueError, TypeError):
                    pass
            elif 'Sharpe_Ratio' in strategy_data:
                sharpe = strategy_data['Sharpe_Ratio']
                try:
                    if isinstance(sharpe, str):
                        sharpe = float(sharpe.replace(',', '.'))
                    else:
                        sharpe = float(sharpe) if sharpe is not None else 0.0 if sharpe is not None else 0.0
                    os_positive = sharpe > 0
                except (ValueError, TypeError):
                    pass
            elif 'CAGR' in strategy_data:
                cagr = strategy_data['CAGR']
                try:
                    if isinstance(cagr, str):
                        cagr = float(cagr.replace(',', '.'))
                    else:
                        cagr = float(cagr) if cagr is not None else 0.0 if cagr is not None else 0.0
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
            max_correlation = self.config["filters"]["correlation_6m"]["max_correlation"]
            
            # Verificar correlaciones específicas
            correlation_fields = [
                'Correlation_6m_Nasdaq', 'Correlation_6m_Gold', 'Correlation_6m_BTC'
            ]
            
            for field in correlation_fields:
                if field in strategy_data:
                    correlation = abs(self.to_float(strategy_data[field]))
                    if correlation > max_correlation:
                        self.logger.debug(f"Correlación {field} = {correlation} > {max_correlation}")
                        return False
            
            # Si no hay correlaciones específicas, verificar campo genérico
            if 'Correlation_6m' in strategy_data:
                correlation = abs(self.to_float(strategy_data['Correlation_6m']))
                if correlation > max_correlation:
                    self.logger.debug(f"Correlación genérica = {correlation} > {max_correlation}")
                    return False
            
            # Si no hay datos de correlación, pasar
            self.logger.debug("No hay datos de correlación, pasando filtro")
            return True
            
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
                    sharpe_float = float(sharpe) if sharpe is not None else 0.0 if sharpe is not None else 0.0 if isinstance(sharpe, (int, float)) else float(str(sharpe).replace(',', '.'))
                    cagr_float = float(cagr) if cagr is not None else 0.0 if cagr is not None else 0.0 if isinstance(cagr, (int, float)) else float(str(cagr).replace(',', '.'))
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
            max_dd_corr = self.config["filters"]["dd_correlation"]["max_dd_corr"]
            
            # Verificar correlación DD específica
            if 'DD_Correlation_INDX' in strategy_data:
                dd_corr = abs(self.to_float(strategy_data['DD_Correlation_INDX']))
                return dd_corr <= max_dd_corr
            
            # Fallback: verificar campo genérico
            if 'DD_Correlation' in strategy_data:
                dd_corr = abs(self.to_float(strategy_data['DD_Correlation']))
                return dd_corr <= max_dd_corr
            
            # Si no hay datos de correlación DD, pasar
            self.logger.debug("No hay datos de correlación DD, pasando filtro")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verificando correlación DD: {e}")
            return True
    
    def _calculate_score(self, strategy_data: pd.Series, filter_results: Dict[str, Any]) -> float:
        """
        Calcula score final según metodología DarwinEX con predictibilidad mejorada.
        
        Args:
            strategy_data: Datos de la estrategia
            filter_results: Resultados de filtros aplicados
            
        Returns:
            Score final (0-100)
        """
        try:
            # Score base original (mantener lógica original)
            base_score = self._calculate_base_score(strategy_data, filter_results)
            
            # Bonus por predictibilidad (nuevo)
            predictability_bonus = self._calculate_predictability_bonus(strategy_data)
            
            # Score final
            final_score = base_score + predictability_bonus
            return min(final_score, 100)
            
        except Exception as e:
            self.logger.error(f"Error calculando score: {e}")
            return 0.0
    
    def _calculate_base_score(self, strategy_data: pd.Series, filter_results: Dict[str, Any]) -> float:
        """
        Calcula score base original (ajustado para progresión Silver→Gold y mantenimiento Gold, priorizando predictibilidad para estrategias sin real).
        """
        try:
            score = 0.0
            weights = self.config["scoring"]["weights"]
            is_development = self._is_new_strategy(strategy_data)

            # Ajuste: para estrategias nuevas, reducir peso de años y aumentar el de robustez simulada
            years_weight = weights["years_running"] * (0.2 if is_development else 1.0)
            lea_weight = weights["lea"] * (1.2 if is_development else 1.0)
            os_weight = weights["os"] * (1.2 if is_development else 1.0)
            sharpe_weight = 0.20 if is_development else 0.15
            bonus_per_filter = 8 if is_development else 7

            # Years Running (mínimo para nuevas)
            if 'Years_Running' in strategy_data:
                years = self.to_float(strategy_data['Years_Running'])
                score += min(years / 3.0, 1.0) * 10.0 * years_weight

            # LEA
            if 'LEA' in strategy_data:
                lea = self.to_float(strategy_data['LEA'])
                score += max(lea, 0.0) * 30.0 * lea_weight

            # OS
            if 'OS' in strategy_data:
                os_val = self.to_float(strategy_data['OS'])
                score += max(os_val, 0.0) * 30.0 * os_weight

            # Sharpe Ratio
            if 'Sharpe_Ratio' in strategy_data:
                sharpe = self.to_float(strategy_data['Sharpe_Ratio'])
                score += min(sharpe / 2.0, 1.0) * 25.0 * sharpe_weight

            # Correlation
            if len([f for f in filter_results['passed'] if 'correlation' in f]) > 0:
                score += 10 * weights["correlation"]

            # Discipline
            if len([f for f in filter_results['passed'] if 'discipline' in f]) > 0:
                score += 10 * weights["discipline"]

            # DD Correlation
            if len([f for f in filter_results['passed'] if 'dd_correlation' in f]) > 0:
                score += 10 * weights["dd_correlation"]

            # Bonus por filtros pasados
            score += len(filter_results['passed']) * bonus_per_filter

            # Bonus adicional para estrategias Gold con buen track record
            if not is_development and 'Years_Running' in strategy_data and self.to_float(strategy_data['Years_Running']) > 2.0:
                score += 5

            return min(score, 100)
        except Exception as e:
            self.logger.error(f"Error calculando score base: {e}")
            return 0.0

    def _calculate_predictability_bonus(self, strategy_data: pd.Series) -> float:
        """
        Calcula bonus por predictibilidad usando datos empíricos reales.
        Para estrategias nuevas, el bonus puede ser hasta 30 puntos.
        """
        try:
            predictability_metrics = self.predictability_analyzer.calculate_overall_predictability(strategy_data)
            is_development = self._is_new_strategy(strategy_data)
            # Bonus más alto para nuevas
            if is_development:
                if predictability_metrics.overall_predictability >= 80:
                    bonus = 30
                elif predictability_metrics.overall_predictability >= 70:
                    bonus = 22
                elif predictability_metrics.overall_predictability >= 60:
                    bonus = 15
                elif predictability_metrics.overall_predictability >= 50:
                    bonus = 8
                else:
                    bonus = 0
            else:
                if predictability_metrics.overall_predictability >= 80:
                    bonus = 20
                elif predictability_metrics.overall_predictability >= 70:
                    bonus = 15
                elif predictability_metrics.overall_predictability >= 60:
                    bonus = 10
                elif predictability_metrics.overall_predictability >= 50:
                    bonus = 5
                else:
                    bonus = 0
            self.logger.info(f"Predictibilidad: {predictability_metrics.overall_predictability:.1f}, Bonus: {bonus}")
            return bonus
        except Exception as e:
            self.logger.error(f"Error calculando bonus de predictibilidad: {e}")
            return 0.0
    
    def _calculate_silver_to_gold_potential(self, strategy_data: pd.Series, current_score: float, is_new_strategy: bool) -> float:
        """
        Calcula potencial de ascenso Silver→Gold.
        
        Args:
            strategy_data: Datos de la estrategia
            current_score: Score actual
            is_new_strategy: Si es estrategia nueva
            
        Returns:
            Potencial de ascenso (0-100)
        """
        try:
            # Solo evaluar estrategias Silver
            silver_threshold = self.config["scoring"]["thresholds"]["silver"]
            gold_threshold = self.config["scoring"]["thresholds"]["gold"]
            
            if current_score < silver_threshold or current_score >= gold_threshold:
                return 0.0
            
            # Factores de mejora
            improvement_factors = []
            
            # 1. Estabilidad de métricas clave
            stability_score = 0.0
            if 'Frequency_Stability' in strategy_data:
                stability_score += self.to_float(strategy_data['Frequency_Stability'])
            if 'Asset_Drift' in strategy_data:
                drift = self.to_float(strategy_data['Asset_Drift'])
                stability_score += max(0, 1.0 - drift)
            stability_score = min(stability_score, 1.0)
            improvement_factors.append(stability_score)
            
            # 2. Consistencia IS/OOS
            consistency_score = 0.0
            if 'CAGR_IS' in strategy_data and 'CAGR_OOS' in strategy_data:
                cagr_is = self.to_float(strategy_data['CAGR_IS'])
                cagr_oos = self.to_float(strategy_data['CAGR_OOS'])
                if cagr_is > 0:
                    consistency_score = min(cagr_oos / cagr_is, 1.5) / 1.5
            improvement_factors.append(consistency_score)
            
            # 3. Mejora en métricas fundamentales
            fundamental_score = 0.0
            if 'LEA' in strategy_data and 'OS' in strategy_data:
                lea = self.to_float(strategy_data['LEA'])
                os_val = self.to_float(strategy_data['OS'])
                fundamental_score = (max(0, lea) + max(0, os_val)) / 2.0
            improvement_factors.append(fundamental_score)
            
            # 4. Track record
            track_record_score = 0.0
            if 'Years_Running' in strategy_data:
                years = self.to_float(strategy_data['Years_Running'])
                track_record_score = min(years / 3.0, 1.0)
            improvement_factors.append(track_record_score)
            
            # Calcular potencial promedio
            avg_improvement = sum(improvement_factors) / len(improvement_factors)
            
            # Ajustar por distancia al umbral Gold
            distance_to_gold = (gold_threshold - current_score) / (gold_threshold - silver_threshold)
            potential = avg_improvement * (1.0 - distance_to_gold)
            
            # Penalizar estrategias nuevas
            if is_new_strategy:
                potential *= 0.7
            
            return min(max(potential * 100, 0.0), 100.0)
            
        except Exception as e:
            self.logger.error(f"Error calculando potencial Silver→Gold: {e}")
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
    
    def _generate_recommendations(self, filter_results: Dict[str, Any], score: float, silver_to_gold_potential: float) -> List[str]:
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
        
        # Recomendaciones adicionales por potencial Silver→Gold
        if silver_to_gold_potential > 0:
            recommendations.append(f"🚀 Potencial de ascenso Silver→Gold: {silver_to_gold_potential:.1f}%")
            if silver_to_gold_potential > 50:
                recommendations.append("🔬 Considerar optimización de parámetros para alcanzar Gold")
            elif silver_to_gold_potential > 20:
                recommendations.append("🔬 Evaluar estrategia para posibles mejoras de predictibilidad")
        
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
            passed_strategies = len([r for r in results if r.ticket_size > 0])
            rejected_strategies = total_strategies - passed_strategies
            # Distribución por categoría
            ticket_categories = {}
            for result in results:
                if result.category not in ticket_categories:
                    ticket_categories[result.category] = 0
                ticket_categories[result.category] += 1
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
            risk_alerts_list = [r for r in results if len(r.risk_alerts) > 0]
            risk_alerts_count = len(risk_alerts_list)
            # Recomendaciones globales (puede ser vacía)
            recommendations = []
            # Top estrategias aprobadas
            top_strategies = sorted([r for r in results if r.ticket_size > 0], 
                                    key=lambda x: x.final_score, reverse=True)[:10]
            report = {
                "summary": {
                    "total_strategies": total_strategies,
                    "passed_strategies": passed_strategies,
                    "rejected_strategies": rejected_strategies,
                    "pass_rate": passed_strategies / total_strategies if total_strategies > 0 else 0,
                    "total_capital_allocated": total_capital,
                    "risk_alerts_count": risk_alerts_count
                },
                "ticket_categories": ticket_categories,
                "top_strategies": [
                    {
                        "name": r.strategy_name,
                        "score": r.final_score,
                        "ticket": r.ticket_size,
                        "category": r.category
                    } for r in top_strategies
                ],
                "risk_alerts": [
                    {
                        "name": r.strategy_name,
                        "alerts": r.risk_alerts
                    } for r in risk_alerts_list
                ],
                "recommendations": recommendations
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
        print(f"   - Aprobadas: {report['summary']['passed_strategies']}")
        print(f"   - Rechazadas: {report['summary']['rejected_strategies']}")
        print(f"   - Tasa de aprobación: {report['summary']['pass_rate']:.1%}")
        print(f"   - Capital total asignado: €{report['summary']['total_capital_allocated']:,}")
        print(f"   - Alertas de riesgo: {report['summary']['risk_alerts_count']}")
        
        print("\n🏆 DISTRIBUCIÓN POR CATEGORÍA:")
        for category, count in report['ticket_categories'].items():
            print(f"   - {category}: {count} estrategias")
        
        print("\n🔍 ANÁLISIS DE FILTROS:")
        for filter_name, analysis in report['filter_analysis'].items():
            print(f"   - {filter_name}: {analysis['passed']} pasaron, {analysis['failed']} fallaron ({analysis['pass_rate']:.1%})")
        
        print("\n⭐ TOP 3 ESTRATEGIAS:")
        for i, strategy in enumerate(report['top_strategies'][:3]):
            print(f"   {i+1}. {strategy['name']}: Score {strategy['score']:.1f}, Ticket €{strategy['ticket']:,}, {strategy['category']}")
        
        print("\n⚠️ ESTRATEGIAS CON ALERTAS:")
        for strategy in report['risk_alerts']:
            print(f"   - {strategy['name']}: {', '.join(strategy['alerts'])}")
        
        print("\n✅ Pipeline DarwinEX completado exitosamente")
        print("🎯 Sistema implementado según normas específicas de DarwinEX")
        
    except Exception as e:
        print(f"❌ Error en pipeline DarwinEX: {e}")
        raise

if __name__ == "__main__":
    test_darwin_ex_pipeline() 