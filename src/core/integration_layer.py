from typing import Optional, Any, Union
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
from src.data.data_utils import ensure_numeric_columns
from src.core.config.progress_callback import ProgressCallback
from src.gui.utils import GUIAnalysisError
from src.core.logger_config import setup_logger

# Importar el nuevo módulo de inteligencia ML
from src.core.analysis.ml_intelligence_enhancer import MLIntelligenceEnhancer, MLIntelligenceType, enhance_core_analysis_with_ml

# Configurar logging
logger = logging.getLogger(__name__)

# ============================================================================
# CLASES DE UTILIDAD (reemplazan las de core_engine_enhanced.py)
# ============================================================================

# Eliminar definición local de ProgressCallback y UnifiedEvaluatorEnhanced

# Clase GUIAnalysisError eliminada - usar src/gui/utils.py en su lugar
# from src.gui.utils import GUIAnalysisError

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

class CoreEngine:
    """
    Motor principal del sistema de análisis cuantitativo.
    
    Integra todos los componentes de análisis:
    - Factor K Enhanced
    - QVA Analyzer
    - Market Regime Analyzer
    - Predictability Analyzer
    - Robustness Analyzer
    - ML Intelligence Enhancer (NUEVO)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el core engine con todos los componentes.
        
        Args:
            config: Configuración opcional
        """
        self.config = config or {}
        self.logger = setup_logger("core_engine")
        
        # Componentes existentes
        self.factor_k_analyzer = FactorKAnalyzer()
        self.qva_analyzer = QVAScorerEnhanced(ConfigManagerEnhanced(), progress_callback=None)
        self.market_regime_analyzer = MarketRegimeDetector()
        self.predictability_analyzer = PredictabilityAnalyzer()
        self.robustness_analyzer = RobustnessAnalyzer()
        
        # NUEVO: Componente de inteligencia ML
        self.ml_intelligence_enhancer = MLIntelligenceEnhancer(
            config=self.config.get('ml_intelligence', {}),
            enable_shap=True,
            enable_confidence_scores=True
        )
        
        # Configuración de análisis ML
        self.ml_analysis_types = [
            MLIntelligenceType.PERFORMANCE_PREDICTOR,
            MLIntelligenceType.QUALITY_CLASSIFIER,
            MLIntelligenceType.RISK_PROFILE_ANALYZER,
            MLIntelligenceType.CONSISTENCY_VALIDATOR,
            MLIntelligenceType.ADAPTIVE_THRESHOLD_OPTIMIZER
        ]
        
        self.logger.info("🚀 Core Engine inicializado con ML Intelligence Enhancer")

    def run_comprehensive_analysis(self, 
                                 df: pd.DataFrame,
                                 enable_ml_intelligence: bool = True,
                                 ml_analysis_types: Optional[List[MLIntelligenceType]] = None) -> Dict[str, Any]:
        """
        Ejecuta análisis completo incluyendo inteligencia ML.
        
        Args:
            df: DataFrame con estrategias
            enable_ml_intelligence: Si habilitar análisis ML
            ml_analysis_types: Tipos específicos de análisis ML
            
        Returns:
            Diccionario con todos los resultados
        """
        try:
            self.logger.info("🔍 Iniciando análisis completo con ML Intelligence...")
            
            # Análisis tradicional
            results = {
                'factor_k': self.factor_k_analyzer.evaluate_strategies(df),
                'qva': self.qva_analyzer.calculate_qva_score(df),
                'market_regime': self.market_regime_analyzer.detect_regimes(df),
                'predictability': self.predictability_analyzer.analyze_is_oos_correlations(df),
                'robustness': self.robustness_analyzer.analyze_robustness(df)
            }
            
            # NUEVO: Análisis de inteligencia ML
            if enable_ml_intelligence:
                ml_results = self.ml_intelligence_enhancer.enhance_analysis(
                    df, 
                    analysis_types=ml_analysis_types or self.ml_analysis_types
                )
                results['ml_intelligence'] = ml_results
                
                # Integrar insights de ML en el análisis principal
                self._integrate_ml_insights(results, ml_results)
            
            # Generar resumen unificado
            results['summary'] = self._generate_unified_summary(results)
            
            self.logger.info("✅ Análisis completo finalizado")
            return results
            
        except Exception as e:
            self.logger.error(f"Error en análisis completo: {e}")
            raise
    
    def _integrate_ml_insights(self, results: Dict[str, Any], ml_results: Dict[str, Any]):
        """
        Integra insights de ML en el análisis principal.
        
        Args:
            results: Resultados del análisis principal
            ml_results: Resultados de ML Intelligence
        """
        try:
            # Integrar predicciones de rendimiento
            if 'performance_predictor' in ml_results:
                predictor_result = ml_results['performance_predictor']
                if predictor_result.predictions is not None:
                    if isinstance(results['factor_k'], pd.DataFrame):
                        results['factor_k']['Predicted_OOS_Performance'] = predictor_result.predictions
                    elif isinstance(results['factor_k'], dict):
                        results['factor_k']['data'] = results['factor_k'].get('data', {})
                        results['factor_k']['data']['Predicted_OOS_Performance'] = predictor_result.predictions
            
            # Integrar clasificaciones de calidad
            if 'quality_classifier' in ml_results:
                classifier_result = ml_results['quality_classifier']
                if classifier_result.classifications is not None:
                    if isinstance(results['qva'], pd.DataFrame):
                        results['qva']['ML_Quality_Classification'] = classifier_result.classifications
                    elif isinstance(results['qva'], dict):
                        results['qva']['data'] = results['qva'].get('data', {})
                        results['qva']['data']['ML_Quality_Classification'] = classifier_result.classifications
            
            # Integrar perfiles de riesgo
            if 'risk_profile_analyzer' in ml_results:
                risk_result = ml_results['risk_profile_analyzer']
                if risk_result.risk_profiles:
                    if isinstance(results['market_regime'], dict):
                        results['market_regime']['data'] = results['market_regime'].get('data', {})
                        results['market_regime']['data']['Risk_Profiles'] = risk_result.risk_profiles
            
            # Integrar scores de consistencia
            if 'consistency_validator' in ml_results:
                consistency_result = ml_results['consistency_validator']
                if consistency_result.consistency_scores is not None:
                    if isinstance(results['robustness'], dict):
                        results['robustness']['data'] = results['robustness'].get('data', {})
                        results['robustness']['data']['ML_Consistency_Scores'] = consistency_result.consistency_scores
            
            # Integrar umbrales optimizados
            if 'adaptive_threshold_optimizer' in ml_results:
                threshold_result = ml_results['adaptive_threshold_optimizer']
                if threshold_result.optimized_thresholds:
                    if 'summary' not in results:
                        results['summary'] = {}
                    results['summary']['optimized_thresholds'] = threshold_result.optimized_thresholds
            
            self.logger.info("🔗 Insights de ML integrados en análisis principal")
            
        except Exception as e:
            self.logger.warning(f"Error integrando insights de ML: {e}")
    
    def _generate_unified_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera resumen unificado incluyendo ML Intelligence.
        
        Args:
            results: Todos los resultados de análisis
            
        Returns:
            Resumen unificado
        """
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'analysis_components': list(results.keys()),
                'insights': [],
                'recommendations': [],
                'ml_intelligence_summary': {}
            }
            
            # Recopilar insights de todos los componentes
            for component, result in results.items():
                if isinstance(result, dict) and 'insights' in result:
                    summary['insights'].extend(result['insights'])
                if isinstance(result, dict) and 'recommendations' in result:
                    summary['recommendations'].extend(result['recommendations'])
            
            # Resumen específico de ML Intelligence
            if 'ml_intelligence' in results:
                ml_summary = self.ml_intelligence_enhancer.get_summary()
                summary['ml_intelligence_summary'] = ml_summary
                
                # Agregar insights clave de ML
                for analysis_type, result in results['ml_intelligence'].items():
                    if hasattr(result, 'insights') and result.insights:
                        summary['insights'].extend(result.insights[:1])  # Top insight por tipo
            
            # Limitar número de insights y recomendaciones
            summary['insights'] = summary['insights'][:10]
            summary['recommendations'] = summary['recommendations'][:5]
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generando resumen unificado: {e}")
            return {'error': str(e)}


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
            if hasattr(self.market_regime_detector, 'detect_regimes'):
                results = self.market_regime_detector.detect_regimes(df)
            else:
                # Fallback si el método no existe
                results = {"regime_labels": [], "details": {}}
            
            if isinstance(results, tuple):
                # Si retorna tuple, convertir a dict de forma segura y sin índices
                results_list = list(results)
                if len(results_list) == 2:
                    regime_labels, details = results_list[0], results_list[1]
                elif len(results_list) == 1:
                    regime_labels, details = results_list[0], {}
                else:
                    regime_labels, details = [], {}
                results = {"regime_labels": regime_labels, "details": details}
            
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
            return float(s) if s is not None else 0.0 if s is not None else 0.0
        return float(val) if val is not None else 0.0 if val is not None else 0.0
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
    """
    Genera insights automáticos basados en los datos.
    
    Args:
        df: DataFrame con análisis completado
        
    Returns:
        Lista de insights generados
    """
    insights = []
    
    try:
        # Insight 1: Mejores estrategias por Factor K
        if 'Factor_K' in df.columns:
            top_factor_k = df.nlargest(3, 'Factor_K')
            data_obj = top_factor_k[['Strategy Name', 'Factor_K']]
            if isinstance(data_obj, pd.DataFrame):
                data_records = data_obj.to_dict(orient='records')
            elif isinstance(data_obj, np.ndarray):
                data_records = pd.DataFrame(data_obj).to_dict(orient='records')
            else:
                data_records = []
            insights.append({
                'type': 'top_performers',
                'title': 'Top 3 Estrategias por Factor K',
                'data': data_records
            })
        
        # Insight 2: Análisis de riesgo
        if 'Max_DD_%' in df.columns:
            low_risk = df[df['Max_DD_%'] < df['Max_DD_%'].quantile(0.25)]
            data_obj = low_risk[['Strategy Name', 'Max_DD_%']]
            if isinstance(data_obj, pd.DataFrame):
                data_records = data_obj.to_dict(orient='records')
            elif isinstance(data_obj, np.ndarray):
                data_records = pd.DataFrame(data_obj).to_dict(orient='records')
            else:
                data_records = []
            insights.append({
                'type': 'risk_analysis',
                'title': 'Estrategias de Bajo Riesgo',
                'data': data_records
            })
        
        # Insight 3: Análisis de rentabilidad
        if 'CAGR' in df.columns:
            high_growth = df.nlargest(3, 'CAGR')
            data_obj = high_growth[['Strategy Name', 'CAGR']]
            if isinstance(data_obj, pd.DataFrame):
                data_records = data_obj.to_dict(orient='records')
            elif isinstance(data_obj, np.ndarray):
                data_records = pd.DataFrame(data_obj).to_dict(orient='records')
            else:
                data_records = []
            insights.append({
                'type': 'growth_analysis',
                'title': 'Top 3 Estrategias por Crecimiento',
                'data': data_records
            })
            
    except Exception as e:
        logger.error(f"Error generando insights: {e}")
        insights.append({
            'type': 'error',
            'title': 'Error generando insights',
            'message': str(e)
        })
    
    return insights


# ============================================================================
# FUNCIONES DE COMPATIBILIDAD (reemplazan las de core_engine_enhanced.py)
# ============================================================================

def run_unified_analysis_enhanced(df: pd.DataFrame, config: Optional[Dict] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Función de compatibilidad que ejecuta análisis unificado mejorado.
    
    Args:
        df: DataFrame con datos de estrategias
        config: Configuración opcional
        
    Returns:
        Tuple con DataFrame procesado y resumen de resultados
    """
    try:
        logger.info("Ejecutando análisis unificado mejorado...")
        
        # Validar entrada
        if df.empty:
            raise ValueError("DataFrame vacío")
        
        # Crear instancia del motor
        engine = FactorKElite96Enhanced(config=config)
        
        # Ejecutar análisis completo
        result_df = engine.run_complete_analysis(df)
        
        # Generar resumen
        summary = {
            'total_strategies': len(result_df),
            'analysis_completed': True,
            'timestamp': datetime.now().isoformat(),
            'columns_processed': list(result_df.columns)
        }
        
        # Añadir métricas si están disponibles
        if 'Factor_K' in result_df.columns:
            summary['factor_k_stats'] = {
                'mean': float(result_df['Factor_K'].mean()),
                'max': float(result_df['Factor_K'].max()),
                'min': float(result_df['Factor_K'].min())
            }
        
        if 'QVA_Score' in result_df.columns:
            summary['qva_stats'] = {
                'mean': float(result_df['QVA_Score'].mean()),
                'max': float(result_df['QVA_Score'].max()),
                'min': float(result_df['QVA_Score'].min())
            }
        
        logger.info("Análisis unificado completado exitosamente")
        return result_df, summary
        
    except Exception as e:
        logger.error(f"Error en análisis unificado: {e}")
        raise GUIAnalysisError(f"Error en análisis unificado: {e}")


def categorize_quality(df: pd.DataFrame, score_col: str = "Unified_Score") -> pd.DataFrame:
    """
    Categoriza la calidad de las estrategias basada en el score.
    
    Args:
        df: DataFrame con estrategias
        score_col: Nombre de la columna de score
        
    Returns:
        DataFrame con columna de categoría añadida
    """
    try:
        if df.empty:
            return df
        
        # Determinar qué columna usar para categorización
        available_scores = ['Factor_K', 'QVA_Score', 'Unified_Score', 'predictability_score']
        score_column = None
        
        for col in available_scores:
            if col in df.columns:
                score_column = col
                break
        
        if score_column is None:
            logger.warning("No se encontró columna de score para categorización")
            df['Quality_Category'] = 'Unknown'
            return df
        
        # Definir umbrales de categorización
        thresholds = {
            'Elite': 9.2,
            'Excellent': 8.2,
            'Very Good': 7.2,
            'Good': 6.2,
            'Average': 5.2,
            'Below Average': 4.2,
            'Poor': 3.2,
            'Very Poor': 0.0
        }
        
        # Aplicar categorización
        df['Quality_Category'] = 'Very Poor'
        
        for category, threshold in thresholds.items():
            df.loc[df[score_column] >= threshold, 'Quality_Category'] = category
        
        logger.info(f"Categorización completada usando {score_column}")
        return df
        
    except Exception as e:
        logger.error(f"Error en categorización: {e}")
        df['Quality_Category'] = 'Error'
        return df


def predictividad_is_oos_empirica(df: pd.DataFrame, is_oos_split: float = 0.75) -> pd.DataFrame:
    """
    Calcula la predictividad IS/OOS usando PredictabilityAnalyzer.
    
    Args:
        df: DataFrame con datos de estrategias
        is_oos_split: Proporción para split IS/OOS (default 0.75)
        
    Returns:
        DataFrame con métricas de predictividad añadidas
    """
    try:
        if df.empty:
            logger.warning("DataFrame vacío para análisis de predictividad")
            return df
        
        # Importar PredictabilityAnalyzer
        from src.core.predictability_analyzer import PredictabilityAnalyzer
        
        # Crear instancia del analizador
        analyzer = PredictabilityAnalyzer()
        
        # Verificar si ya existen columnas IS/OOS
        is_oos_pairs = analyzer._identify_is_oos_pairs(df)
        
        if is_oos_pairs:
            # Si hay pares IS/OOS, usar análisis directo
            logger.info(f"Encontrados {len(is_oos_pairs)} pares IS/OOS para análisis")
            
            # Analizar correlaciones IS/OOS
            correlations = analyzer.analyze_is_oos_correlations(df)
            
            # Analizar calidad predictiva
            quality_metrics = analyzer.analyze_predictive_quality_metrics(df)
            
            # Calcular score promedio de predictibilidad
            if correlations:
                avg_correlation = sum(correlations.values()) / len(correlations)
                predictability_score = max(0.0, min(1.0, avg_correlation))
            else:
                predictability_score = 0.5
                
            # Añadir métricas al DataFrame
            df['predictability_score'] = predictability_score
            df['is_oos_correlation'] = avg_correlation if correlations else 0.0
            
            # Añadir correlaciones específicas si existen
            for pair_name, correlation in correlations.items():
                df[f'correlation_{pair_name}'] = correlation
                
            # Añadir métricas de calidad si existen
            if 'predictive_quality_scores' in quality_metrics:
                for metric_name, quality_score in quality_metrics['predictive_quality_scores'].items():
                    df[f'quality_{metric_name}'] = quality_score
                    
        else:
            # Si no hay pares IS/OOS, simular split como antes
            logger.info("No se encontraron pares IS/OOS, simulando split...")
            
            # Verificar columnas necesarias para simulación
            required_columns = ['CAGR', 'Sharpe_Ratio', 'Profit_factor']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.warning(f"Columnas faltantes para predictividad: {missing_columns}")
                df['predictability_score'] = 0.5
                df['is_oos_correlation'] = 0.0
                return df
            
            # Simular split IS/OOS
            n_strategies = len(df)
            is_size = int(n_strategies * is_oos_split)
            
            # Crear índices aleatorios para simular split
            np.random.seed(42)  # Para reproducibilidad
            indices = np.random.permutation(n_strategies)
            is_indices = indices[:is_size]
            oos_indices = indices[is_size:]
            
            # Calcular métricas IS
            df_is = df.iloc[is_indices]
            is_cagr_mean = df_is['CAGR'].mean()
            is_sharpe_mean = df_is['Sharpe_Ratio'].mean()
            is_profit_factor_mean = df_is['Profit_factor'].mean()
            
            # Calcular métricas OOS
            df_oos = df.iloc[oos_indices]
            oos_cagr_mean = df_oos['CAGR'].mean()
            oos_sharpe_mean = df_oos['Sharpe_Ratio'].mean()
            oos_profit_factor_mean = df_oos['Profit_factor'].mean()
            
            # Calcular correlaciones usando PredictabilityAnalyzer
            cagr_correlation = 0.0
            sharpe_correlation = 0.0
            
            if len(df_is) > 1 and len(df_oos) > 1:
                try:
                    # Crear DataFrame temporal con pares IS/OOS
                    temp_df = pd.DataFrame({
                        'CAGR_IS': df_is['CAGR'].values,
                        'CAGR_OOS': df_oos['CAGR'].values,
                        'Sharpe_Ratio_IS': df_is['Sharpe_Ratio'].values,
                        'Sharpe_Ratio_OOS': df_oos['Sharpe_Ratio'].values
                    })
                    
                    # Usar PredictabilityAnalyzer para correlaciones
                    temp_correlations = analyzer.analyze_is_oos_correlations(temp_df)
                    
                    if 'CAGR_IS_vs_CAGR_OOS' in temp_correlations:
                        cagr_correlation = temp_correlations['CAGR_IS_vs_CAGR_OOS']
                    if 'Sharpe_Ratio_IS_vs_Sharpe_Ratio_OOS' in temp_correlations:
                        sharpe_correlation = temp_correlations['Sharpe_Ratio_IS_vs_Sharpe_Ratio_OOS']
                        
                except Exception as e:
                    logger.warning(f"Error calculando correlaciones con PredictabilityAnalyzer: {e}")
                    # Fallback a cálculo manual
                    try:
                        cagr_corr_matrix = np.corrcoef(df_is['CAGR'], df_oos['CAGR'])
                        cagr_correlation = cagr_corr_matrix[0, 1] if not np.isnan(cagr_corr_matrix[0, 1]) else 0.0
                    except Exception:
                        cagr_correlation = 0.0
                        
                    try:
                        sharpe_corr_matrix = np.corrcoef(df_is['Sharpe_Ratio'], df_oos['Sharpe_Ratio'])
                        sharpe_correlation = sharpe_corr_matrix[0, 1] if not np.isnan(sharpe_corr_matrix[0, 1]) else 0.0
                    except Exception:
                        sharpe_correlation = 0.0
            
            # Calcular score de predictibilidad
            predictability_score = (cagr_correlation + sharpe_correlation) / 2.0
            predictability_score = max(0.0, min(1.0, predictability_score))  # Clamp entre 0 y 1
            
            # Añadir métricas al DataFrame
            df['predictability_score'] = predictability_score
            df['is_oos_correlation'] = (cagr_correlation + sharpe_correlation) / 2.0
            df['is_cagr_mean'] = is_cagr_mean
            df['oos_cagr_mean'] = oos_cagr_mean
            df['is_sharpe_mean'] = is_sharpe_mean
            df['oos_sharpe_mean'] = oos_sharpe_mean
        
        logger.info(f"Predictibilidad calculada usando PredictabilityAnalyzer: score={predictability_score:.3f}")
        return df
        
    except Exception as e:
        logger.error(f"Error calculando predictibilidad: {e}")
        df['predictability_score'] = 0.5
        df['is_oos_correlation'] = 0.0
        return df


# ============================================================================
# FUNCIONES DE UTILIDAD ADICIONALES
# ============================================================================

def get_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Genera un resumen completo del análisis.
    
    Args:
        df: DataFrame con análisis completado
        
    Returns:
        Diccionario con resumen del análisis
    """
    summary = {
        'total_strategies': len(df),
        'analysis_timestamp': datetime.now().isoformat(),
        'available_metrics': list(df.columns)
    }
    
    # Estadísticas por métrica
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_columns:
        if col in df.columns:
            # Verificar si la columna tiene datos válidos
            col_data = df[col]
            try:
                if hasattr(col_data, 'isna'):
                    isna_result = col_data.isna()
                    if hasattr(isna_result, 'all'):
                        has_nulls = bool(isna_result.all())
                        if not has_nulls:
                            summary[f'{col}_stats'] = {
                                'mean': float(df[col].mean()),
                                'std': float(df[col].std()),
                                'min': float(df[col].min()),
                                'max': float(df[col].max()),
                                'median': float(df[col].median())
                            }
            except Exception:
                # Si hay error, continuar con la siguiente columna
                continue
    
    # Categorías si existen
    if 'Quality_Category' in df.columns:
        category_counts = df['Quality_Category'].value_counts().to_dict()
        summary['quality_distribution'] = category_counts
    
    return summary


def export_analysis_results(df: pd.DataFrame, output_path: str, format: str = 'csv') -> bool:
    """
    Exporta los resultados del análisis.
    
    Args:
        df: DataFrame con resultados
        output_path: Ruta de salida
        format: Formato de exportación ('csv', 'excel', 'json')
        
    Returns:
        True si la exportación fue exitosa
    """
    try:
        if format.lower() == 'csv':
            df.to_csv(output_path, index=False)
        elif format.lower() == 'excel':
            df.to_excel(output_path, index=False)
        elif format.lower() == 'json':
            df.to_json(output_path, orient='records', indent=2)
        else:
            raise ValueError(f"Formato no soportado: {format}")
        
        logger.info(f"Resultados exportados exitosamente a {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error exportando resultados: {e}")
        return False


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
    # Funciones de compatibilidad añadidas
    'run_unified_analysis_enhanced',
    'categorize_quality',
    'predictividad_is_oos_empirica',
    'get_analysis_summary',
    'export_analysis_results',
    # Exportar importadas para compatibilidad
    'UnifiedEvaluatorEnhanced',
    'ProgressCallback',
    'ConfigManagerEnhanced',
    'GUIAnalysisError',
] 