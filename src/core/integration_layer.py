"""
Módulo de Integración - Reemplazo de core_engine_enhanced.py
============================================================

Este módulo proporciona las mismas interfaces que core_engine_enhanced.py
pero usando los módulos modulares existentes. Permite la migración gradual
sin romper el código existente.

Funcionalidades proporcionadas:
- FactorKElite96Enhanced (usando factor_k_analyzer.py)
- UnifiedEvaluatorEnhanced (usando unified_evaluator.py)
- ConfigManagerEnhanced (usando config_manager.py)
- ProgressCallback y otras clases de utilidad
- Funciones de análisis completo
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass
from datetime import datetime
import warnings

# Importar módulos modulares
from src.core.analysis.factor_k_analyzer import FactorKElite96Enhanced as FactorKAnalyzer
from src.core.analysis.unified_evaluator import UnifiedEvaluatorEnhanced
from src.core.analysis.qva_analyzer import QVAScorerEnhanced
from src.core.config.config_manager import ConfigManagerEnhanced
from src.core.market_regime_analyzer import MarketRegimeDetector
from src.core.predictability_analyzer import PredictabilityAnalyzer
from src.core.robustness_analyzer import RobustnessAnalyzer
from src.data.data_manager import DataManager
from src.core.utils.type_converters import ensure_numeric_columns
from src.core.config.progress_callback import ProgressCallback

# Configurar logging
logger = logging.getLogger(__name__)

# ============================================================================
# CLASES DE UTILIDAD (reemplazan las de core_engine_enhanced.py)
# ============================================================================

# Eliminar definición local de ProgressCallback y UnifiedEvaluatorEnhanced


class GUIAnalysisError(Exception):
    """Excepción específica para errores de análisis en GUI."""
    pass


# Elimino la clase local ConfigManagerEnhanced (definición y métodos)


class ExtraKPIManager:
    """
    Gestor de KPIs adicionales (reemplaza el de core_engine_enhanced.py).
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_kpis = self._get_available_kpis()
    
    def _get_available_kpis(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene los KPIs disponibles."""
        return {
            'Profit_factor': {'description': 'Ratio de beneficio', 'enabled': True},
            'Sharpe_Ratio': {'description': 'Ratio de Sharpe', 'enabled': True},
            'Max_DD_%': {'description': 'Máximo drawdown', 'enabled': True},
            'CAGR': {'description': 'Crecimiento anual compuesto', 'enabled': True},
            'CalmarRatio': {'description': 'Ratio de Calmar', 'enabled': True},
            'Sortino_Ratio': {'description': 'Ratio de Sortino', 'enabled': True},
            'RecoveryFactor': {'description': 'Factor de recuperación', 'enabled': True},
            'Winning_Percent': {'description': 'Porcentaje de operaciones ganadoras', 'enabled': True},
            'Net_profit': {'description': 'Beneficio neto', 'enabled': True},
            '#_of_trades': {'description': 'Número de operaciones', 'enabled': True}
        }
    
    def get_enabled_kpis(self) -> List[str]:
        """Obtiene los KPIs habilitados."""
        return [kpi for kpi, config in self.available_kpis.items() if config['enabled']]
    
    def enable_kpi(self, kpi_name: str) -> bool:
        """Habilita un KPI."""
        if kpi_name in self.available_kpis:
            self.available_kpis[kpi_name]['enabled'] = True
            return True
        return False
    
    def disable_kpi(self, kpi_name: str) -> bool:
        """Deshabilita un KPI."""
        if kpi_name in self.available_kpis:
            self.available_kpis[kpi_name]['enabled'] = False
            return True
        return False


# ============================================================================
# CLASES PRINCIPALES (reemplazan las de core_engine_enhanced.py)
# ============================================================================

class FactorKElite96Enhanced:
    """
    Motor principal mejorado (reemplaza el de core_engine_enhanced.py).
    Usa los módulos modulares existentes.
    """
    
    def __init__(self, config: Optional[Dict] = None, progress_callback: Optional[ProgressCallback] = None):
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManagerEnhanced()
        self.data_manager = DataManager()
        self.progress_callback = progress_callback
        
        # Componentes modulares
        self.factor_k_analyzer = FactorKAnalyzer()
        self.qva_analyzer = QVAScorerEnhanced(self.config_manager, progress_callback=progress_callback)
        self.market_regime_detector = MarketRegimeDetector()
        self.predictability_analyzer = PredictabilityAnalyzer()
        self.robustness_analyzer = RobustnessAnalyzer()
        
        # Configuración
        if config:
            self.config_manager.update_config(config)
    
    def calculate_factor_k(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula el Factor K Elite 9.6 usando el módulo modular.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            DataFrame con Factor K calculado
        """
        try:
            if self.progress_callback:
                self.progress_callback.update(10, "Calculando Factor K...")
            
            # Usar el módulo modular
            result_df = self.factor_k_analyzer.evaluate_strategies(df)
            
            if isinstance(result_df, pd.Series):
                result_df = result_df.to_frame()
            
            if self.progress_callback:
                self.progress_callback.update(50, "Factor K calculado exitosamente")
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"Error calculando Factor K: {e}")
            raise GUIAnalysisError(f"Error en cálculo de Factor K: {e}")
    
    def calculate_qva_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula el score QVA usando el módulo modular.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            DataFrame con QVA calculado
        """
        try:
            if self.progress_callback:
                self.progress_callback.update(60, "Calculando QVA...")
            
            # Usar el módulo modular
            result_df = self.qva_analyzer.calculate_qva_score(df)
            
            if self.progress_callback:
                self.progress_callback.update(80, "QVA calculado exitosamente")
            
            if isinstance(result_df, pd.Series):
                result_df = result_df.to_frame()
            
            return result_df

        except Exception as e:
            self.logger.error(f"Error calculando QVA: {e}")
            raise GUIAnalysisError(f"Error en cálculo de QVA: {e}")
    
    def analyze_market_regimes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analiza regímenes de mercado usando el módulo modular.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            if self.progress_callback:
                self.progress_callback.update(85, "Analizando regímenes de mercado...")
            
            # Usar el módulo modular
            results = self.market_regime_detector.detect_regimes(df)
            
            if isinstance(results, tuple):
                # Si retorna tuple, convertir a dict
                results = {"regime_labels": results[0], "details": results[1]}
            
            if self.progress_callback:
                self.progress_callback.update(90, "Análisis de regímenes completado")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analizando regímenes: {e}")
            return {'error': str(e)}
    
    def run_complete_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta análisis completo usando todos los módulos modulares.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            DataFrame con todos los análisis aplicados
        """
        try:
            if self.progress_callback:
                self.progress_callback.update(0, "Iniciando análisis completo...")
            
            # Validar datos de entrada
            if df.empty:
                raise GUIAnalysisError("DataFrame vacío")
            
            # Asegurar columnas numéricas
            numeric_columns = ['Profit_factor', 'Sharpe_Ratio', 'Max_DD_%', 'CAGR']
            df = ensure_numeric_columns(df, columns=numeric_columns)
            
            # Factor K
            df = self.calculate_factor_k(df)
            
            # QVA
            df = self.calculate_qva_score(df)
            
            # Regímenes de mercado
            regime_results = self.analyze_market_regimes(df)
            
            # Predictabilidad
            if self.predictability_analyzer:
                try:
                    predictability_results = self.predictability_analyzer.analyze_is_oos_correlations(df)
                    # Se puede guardar el score principal si existe
                    score = predictability_results.get('predictability_score', 0.5)
                    df['predictability_score'] = score if isinstance(score, (int, float)) else 0.5
                except Exception as e:
                    self.logger.error(f"Error analizando predictabilidad: {e}")
                    df['predictability_score'] = 0.5
            
            # Robustez
            if self.robustness_analyzer:
                try:
                    robustness_results = self.robustness_analyzer.analyze_robustness(df)
                    df['robustness_score'] = robustness_results.get('score', 0.5)
                except Exception as e:
                    self.logger.error(f"Error analizando robustez: {e}")
                    df['robustness_score'] = 0.5
            
            # Score unificado
            fk_score = df.get('FK96_Elite_Enhanced', pd.Series(0.5, index=df.index))
            qva_score = df.get('QVA_Score', pd.Series(0.5, index=df.index))
            
            fk_score = fk_score if fk_score is not None else pd.Series(0.0, index=df.index)
            qva_score = qva_score if qva_score is not None else pd.Series(0.0, index=df.index)
            
            df['Unified_Score'] = fk_score * 0.6 + qva_score * 0.4
            
            if self.progress_callback:
                self.progress_callback.update(100, "Análisis completo finalizado")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error en análisis completo: {e}")
            raise GUIAnalysisError(f"Error en análisis completo: {e}")


# ============================================================================
# FUNCIONES PRINCIPALES (reemplazan las de core_engine_enhanced.py)
# ============================================================================

def _validate_dataframe_input(df, context=""): 
    import pandas as pd
    import logging
    logger = logging.getLogger(__name__)
    if not isinstance(df, pd.DataFrame):
        logger.error(f"[{context}] Se esperaba un DataFrame, se recibió: {type(df)}")
        raise ValueError(f"[{context}] Se esperaba un DataFrame, se recibió: {type(df)}")


def test_validate_dataframe_input():
    import pytest
    try:
        _validate_dataframe_input(123, context="test")
    except ValueError as e:
        assert "DataFrame" in str(e)
        print("✅ _validate_dataframe_input lanza ValueError para enteros")
    else:
        assert False, "No lanzó ValueError para tipo incorrecto"


def run_complete_analysis_with_gui_integration(
    df: pd.DataFrame,
    config: Optional[Dict] = None,
    progress_callback: Optional[ProgressCallback] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    _validate_dataframe_input(df, context="run_complete_analysis_with_gui_integration")
    try:
        logger.info("Iniciando análisis completo con integración GUI")
        
        # Crear motor principal
        engine = FactorKElite96Enhanced(config, progress_callback)
        
        # Ejecutar análisis completo
        results_df = engine.run_complete_analysis(df)
        
        # Crear evaluador unificado para resumen
        evaluator = UnifiedEvaluatorEnhanced(progress_callback)
        summary = evaluator.get_unified_summary(results_df)
        
        logger.info("Análisis completo finalizado exitosamente")
        
        return results_df, summary
        
    except Exception as e:
        logger.error(f"Error en análisis completo: {e}")
        raise GUIAnalysisError(f"Error en análisis completo: {e}")


def run_factor_k_analysis(df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Ejecuta análisis Factor K.
    
    Args:
        df: DataFrame con datos de estrategias
        config: Configuración opcional
        
    Returns:
        DataFrame con resultados del análisis
    """
    try:
        logger.info("Iniciando análisis Factor K")
        
        engine = FactorKElite96Enhanced(config)
        results_df = engine.calculate_factor_k(df)
        
        logger.info("Análisis Factor K completado")
        
        return results_df
        
    except Exception as e:
        logger.error(f"Error en análisis Factor K: {e}")
        raise GUIAnalysisError(f"Error en análisis Factor K: {e}")


def run_qva_analysis(df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Ejecuta análisis QVA.
    
    Args:
        df: DataFrame con datos de estrategias
        config: Configuración opcional
        
    Returns:
        DataFrame con resultados del análisis
    """
    try:
        logger.info("Iniciando análisis QVA")
        
        engine = FactorKElite96Enhanced(config)
        results_df = engine.calculate_qva_score(df)
        
        logger.info("Análisis QVA completado")
        
        return results_df
        
    except Exception as e:
        logger.error(f"Error en análisis QVA: {e}")
        raise GUIAnalysisError(f"Error en análisis QVA: {e}")


def run_unified_analysis(df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
    """
    Ejecuta análisis unificado.
    
    Args:
        df: DataFrame con datos de estrategias
        config: Configuración opcional
        
    Returns:
        DataFrame con resultados del análisis
    """
    try:
        logger.info("Iniciando análisis unificado")
        
        evaluator = UnifiedEvaluatorEnhanced()
        results_df = evaluator.evaluate_strategies_unified(df)
        
        logger.info("Análisis unificado completado")
        
        return results_df
        
    except Exception as e:
        logger.error(f"Error en análisis unificado: {e}")
        raise GUIAnalysisError(f"Error en análisis unificado: {e}")


# ============================================================================
# FUNCIONES DE UTILIDAD (reemplazan las de core_engine_enhanced.py)
# ============================================================================

def safe_float(val: Any) -> float:
    """Conversión segura a float, soporta formatos internacionales y europeos."""
    try:
        if isinstance(val, str):
            s = val.strip().replace(' ', '')
            # Si hay tanto ',' como '.', decidir cuál es decimal
            if ',' in s and '.' in s:
                if s.rfind(',') > s.rfind('.'):
                    # Formato europeo: 1.234,56 -> 1234.56
                    s = s.replace('.', '').replace(',', '.')
                else:
                    # Formato internacional: 1,234.56 -> 1234.56
                    s = s.replace(',', '')
            elif ',' in s:
                # Si solo hay coma, asumir decimal europeo
                s = s.replace('.', '').replace(',', '.')
            else:
                # Solo punto o sin separador
                s = s.replace(',', '')
            return float(s)
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def validate_dataframe(df: pd.DataFrame) -> bool:
    """Valida que el DataFrame sea válido para análisis."""
    if df is None or df.empty:
        return False
    
    required_columns = ['Strategy_Name']
    for col in required_columns:
        if col not in df.columns:
            return False
    
    return True


def generate_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Genera insights basados en los resultados."""
    insights = []
    
    try:
        # Insight sobre correlaciones
        if 'Unified_Score' in df.columns:
            score_correlations = {}
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if col != 'Unified_Score':
                    try:
                        unified_series = pd.to_numeric(df['Unified_Score'], errors='coerce')
                        col_series = pd.to_numeric(df[col], errors='coerce')
                        if not isinstance(unified_series, pd.Series):
                            unified_series = pd.Series(unified_series, index=df.index)
                        if not isinstance(col_series, pd.Series):
                            col_series = pd.Series(col_series, index=df.index)
                        corr = unified_series.corr(col_series)
                        if abs(corr) > 0.5:
                            score_correlations[col] = corr
                    except Exception:
                        continue
            
            if score_correlations:
                best_corr_col = max(score_correlations.items(), key=lambda x: abs(x[1]))
                insights.append({
                    'type': 'insight',
                    'message': f"La métrica más correlacionada con el score es {best_corr_col[0]} (r={best_corr_col[1]:.3f})",
                    'priority': 'medium'
                })
        
        # Insight sobre distribución
        if 'Unified_Score' in df.columns:
            scores = df['Unified_Score'].dropna()
            if len(scores) > 0:
                mean_score = float(scores.mean())
                std_score = float(scores.std())
                insights.append({
                    'type': 'statistic',
                    'message': f"Score promedio: {mean_score:.3f} ± {std_score:.3f}",
                    'priority': 'low'
                })
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generando insights: {e}")
        return []


# ============================================================================
# EXPORTAR TODAS LAS CLASES Y FUNCIONES NECESARIAS
# ============================================================================

__all__ = [
    # Solo exportar funciones y clases realmente definidas aquí o importadas explícitamente
    'FactorKElite96Enhanced',
    'ExtraKPIManager',
    'run_complete_analysis_with_gui_integration',
    'run_factor_k_analysis',
    'run_qva_analysis',
    'run_unified_analysis',
    'safe_float',
    'validate_dataframe',
    'generate_insights',
    # Exportar importadas para compatibilidad
    'UnifiedEvaluatorEnhanced',
    'ProgressCallback',
    'ConfigManagerEnhanced',
    'GUIAnalysisError',
] 