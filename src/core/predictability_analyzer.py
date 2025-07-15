"""
PREDICTABILITY_ANALYZER.py - Análisis de Predictibilidad

Este módulo contiene las clases para análisis de predictibilidad:
- PredictabilityAnalyzer: Análisis de correlaciones IS/OOS
- WalkForwardAnalyzer: Validación walk-forward
- NullSimulationAnalyzer: Simulaciones de hipótesis nula

Extraído de core_engine_enhanced.py para modularización.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, cast
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
import warnings
from dataclasses import dataclass
from enum import Enum
import itertools
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from pandas import Timestamp, Timedelta

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

# Tipos no indexables global para safe_getitem
NON_INDEXABLE_TYPES = (float, int, complex, np.floating, np.integer, type(pd.NA), type(pd.NaT), Timestamp, Timedelta)

# Helper seguro para longitud
_DEF_NA_TYPES = (type(pd.NA), type(pd.NaT), type(None))
def safe_len(obj: Any) -> int:
    if obj is None or isinstance(obj, _DEF_NA_TYPES):
        return 0
    if hasattr(obj, '__len__'):
        try:
            return len(obj)
        except Exception:
            return 0
    return 0

def safe_getitem(obj: Any, idx: int, default: Any = 0.0) -> Any:
    if obj is None or isinstance(obj, NON_INDEXABLE_TYPES):
        return default
    # Solo intentar indexar si es un tipo indexable conocido
    if isinstance(obj, (list, tuple, np.ndarray, pd.Series)):
        try:
            if len(obj) > idx:
                return obj[idx]
        except Exception:
            pass
    return default

def to_numeric_clean(s) -> pd.Series:
    """Convierte a numérico y elimina nulos. Siempre retorna una Serie estándar."""
    if isinstance(s, pd.DataFrame):
        s = s.squeeze()
    if not isinstance(s, pd.Series):
        s = pd.Series(s)
    result = pd.to_numeric(s, errors='coerce')
    if not isinstance(result, pd.Series):
        result = pd.Series(result)
    return result.dropna()

# NOTA SOBRE PYRIGHT Y pearsonr:
# Pyright puede reportar un falso positivo en el acceso por índice al resultado de pearsonr.
# pearsonr de scipy.stats siempre retorna una tupla de dos floats (coeficiente, p-valor).
# El código implementa chequeo de tipo y fallback seguro, por lo que es robusto y seguro.
# Este warning puede ignorarse con seguridad.
class PredictabilityLevel(Enum):
    """Niveles de predictibilidad."""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"

@dataclass
class PredictabilityResult:
    """Resultado del análisis de predictibilidad."""
    correlation_is_oos: float
    predictability_score: float
    confidence_interval: Tuple[float, float]
    significance_level: float
    recommendation: str

class PredictabilityAnalyzer:
    """
    Analizador de predictibilidad IS/OOS.
    
    Esta clase implementa análisis de predictibilidad usando correlaciones
    entre métricas in-sample y out-of-sample para evaluar la robustez
    de las estrategias de trading.
    """
    
    def __init__(self, progress_callback=None):
        """
        Inicializa el analizador de predictibilidad.
        
        Args:
            progress_callback: Callback para actualizar progreso
        """
        self.progress_callback = progress_callback
        self.min_correlation_threshold = 0.3
        self.significance_level = 0.05
        
    def analyze_is_oos_correlations(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Analiza correlaciones entre métricas IS y OOS.
        
        Args:
            df: DataFrame con métricas IS y OOS
            
        Returns:
            Diccionario con correlaciones por métrica
        """
        try:
            logger.info("Analizando correlaciones IS/OOS...")
            
            correlations = {}
            
            # Identificar pares de métricas IS/OOS
            is_oos_pairs = self._identify_is_oos_pairs(df)
            
            for is_col, oos_col in is_oos_pairs:
                if is_col in df.columns and oos_col in df.columns:
                    correlation = self._calculate_correlation(df, is_col, oos_col)
                    correlations[f"{is_col}_vs_{oos_col}"] = correlation
                    
                    # Actualizar progreso si hay callback
                    if self.progress_callback:
                        self.progress_callback.update_progress(
                            "predictability", 
                            len(correlations), 
                            len(is_oos_pairs),
                            f"Analizando {is_col} vs {oos_col}"
                        )
            
            logger.info(f"Análisis de correlaciones completado: {len(correlations)} pares")
            return correlations
            
        except Exception as e:
            logger.error(f"Error analizando correlaciones IS/OOS: {str(e)}")
            raise
    
    def _identify_is_oos_pairs(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Identifica pares de métricas IS/OOS en el DataFrame.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Lista de tuplas (is_col, oos_col)
        """
        pairs = []
        
        # Validar que df.columns sea iterable y contenga strings
        try:
            columns = df.columns.tolist()
        except (AttributeError, TypeError):
            logger.warning("DataFrame columns no es iterable, usando índices numéricos")
            columns = [str(i) for i in range(len(df.columns))]
        
        # Convertir todas las columnas a strings y validar
        valid_columns = []
        for col in columns:
            if isinstance(col, (int, float)):
                col_str = str(col)
                logger.debug(f"Convirtiendo columna numérica {col} a string: {col_str}")
                valid_columns.append(col_str)
            elif isinstance(col, str):
                valid_columns.append(col)
            else:
                logger.warning(f"Columna ignorada por tipo no soportado: {type(col)}")
        
        # Buscar pares IS/OOS
        for col in valid_columns:
            if '_IS' in col:
                oos_col = col.replace('_IS', '_OOS')
                if oos_col in valid_columns:
                    pairs.append((col, oos_col))
            elif '_is' in col:
                oos_col = col.replace('_is', '_oos')
                if oos_col in valid_columns:
                    pairs.append((col, oos_col))
        
        # Si no hay pares IS/OOS, buscar métricas relacionadas
        if not pairs:
            # Buscar métricas que podrían estar relacionadas
            try:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                # Convertir columnas numéricas a strings
                numeric_cols = [str(col) if isinstance(col, (int, float)) else col for col in numeric_cols]
                
                for i, col1 in enumerate(numeric_cols):
                    for col2 in numeric_cols[i+1:]:
                        if self._are_related_metrics(col1, col2):
                            pairs.append((col1, col2))
            except Exception as e:
                logger.warning(f"Error buscando métricas relacionadas: {e}")
        
        logger.debug(f"Pares IS/OOS identificados: {pairs}")
        return pairs
    
    def _are_related_metrics(self, col1: str, col2: str) -> bool:
        """
        Determina si dos métricas están relacionadas.
        
        Args:
            col1: Nombre de la primera métrica
            col2: Nombre de la segunda métrica
            
        Returns:
            True si las métricas están relacionadas
        """
        # Métricas de rendimiento
        performance_metrics = ['cagr', 'profit', 'return', 'gain']
        # Métricas de riesgo
        risk_metrics = ['drawdown', 'var', 'cvar', 'ulcer', 'risk']
        # Métricas de calidad
        quality_metrics = ['sharpe', 'sortino', 'calmar', 'mar']
        
        col1_lower = col1.lower()
        col2_lower = col2.lower()
        
        # Verificar si ambas son del mismo tipo
        for metric_group in [performance_metrics, risk_metrics, quality_metrics]:
            if any(metric in col1_lower for metric in metric_group) and \
               any(metric in col2_lower for metric in metric_group):
                return True
        
        return False
    
    def _calculate_correlation(self, df: pd.DataFrame, col1: str, col2: str) -> float:
        """
        Calcula correlación entre dos columnas.
        
        Args:
            df: DataFrame con datos
            col1: Primera columna
            col2: Segunda columna
            
        Returns:
            Coeficiente de correlación
        """
        try:
            # Limpiar datos
            col1_data = df[col1]
            col2_data = df[col2]
            if not isinstance(col1_data, pd.Series):
                col1_data = pd.Series(col1_data)
            if not isinstance(col2_data, pd.Series):
                col2_data = pd.Series(col2_data)
            data1 = to_numeric_clean(col1_data)
            data2 = to_numeric_clean(col2_data)
            if safe_len(data1) < 10:
                return 0.0
            # pearsonr siempre devuelve (coeficiente, p-valor)
            corr, p_value = cast(Tuple[float, float], pearsonr(data1, data2))
            correlation = corr
            if not isinstance(p_value, (float, int)) or p_value > self.significance_level:
                correlation = 0.0
            return correlation
            
        except Exception as e:
            logger.warning(f"Error calculando correlación entre {col1} y {col2}: {str(e)}")
            return 0.0
    
    def analyze_outliers_and_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analiza outliers y distribución de métricas.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con análisis de outliers
        """
        try:
            logger.info("Analizando outliers y distribución...")
            
            analysis = {}
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                col_data = df[col]
                if not isinstance(col_data, pd.Series):
                    col_data = pd.Series(col_data)
                data = to_numeric_clean(col_data)
                
                if safe_len(data) > 0:
                    # Estadísticas básicas
                    data_array = np.asarray(data).flatten()
                    stats_info = {
                        'mean': float(data.mean()),
                        'std': float(data.std()),
                        'median': float(data.median()),
                        'skewness': float(stats.skew(data_array)),
                        'kurtosis': float(stats.kurtosis(data_array))
                    }
                    
                    # Detectar outliers usando IQR
                    Q1 = data.quantile(0.25)
                    Q3 = data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = data[(data < lower_bound) | (data > upper_bound)]
                    
                    stats_info.update({
                        'outliers_count': safe_len(outliers),
                        'outliers_percentage': float(safe_len(outliers) / safe_len(data) * 100) if safe_len(data) > 0 else 0.0,
                        'iqr': float(IQR),
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound)
                    })
                    
                    analysis[col] = stats_info
            
            logger.info(f"Análisis de outliers completado: {len(analysis)} métricas")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando outliers: {str(e)}")
            raise
    
    def analyze_predictive_quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analiza métricas de calidad predictiva.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con análisis de calidad predictiva
        """
        try:
            logger.info("Analizando métricas de calidad predictiva...")
            
            quality_metrics = {}
            
            # Identificar métricas IS/OOS
            is_oos_pairs = self._identify_is_oos_pairs(df)
            
            for is_col, oos_col in is_oos_pairs:
                if is_col in df.columns and oos_col in df.columns:
                    # Calcular métricas de calidad
                    quality_score = self._calculate_predictive_quality(df, is_col, oos_col)
                    quality_metrics[f"{is_col}_quality"] = quality_score
            
            # Análisis agregado
            if quality_metrics:
                avg_quality = np.mean(list(quality_metrics.values()))
                quality_metrics['overall_quality'] = float(avg_quality)
                
                # Clasificar calidad general
                if avg_quality >= 0.7:
                    quality_metrics['quality_level'] = PredictabilityLevel.HIGH.value
                elif avg_quality >= 0.5:
                    quality_metrics['quality_level'] = PredictabilityLevel.MODERATE.value
                elif avg_quality >= 0.3:
                    quality_metrics['quality_level'] = PredictabilityLevel.LOW.value
                else:
                    quality_metrics['quality_level'] = PredictabilityLevel.VERY_LOW.value
            
            logger.info(f"Análisis de calidad predictiva completado")
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error analizando calidad predictiva: {str(e)}")
            raise
    
    def _calculate_predictive_quality(self, df: pd.DataFrame, is_col: str, oos_col: str) -> float:
        """
        Calcula calidad predictiva entre métricas IS y OOS.
        
        Args:
            df: DataFrame con datos
            is_col: Columna in-sample
            oos_col: Columna out-of-sample
            
        Returns:
            Score de calidad predictiva (0-1)
        """
        try:
            # Obtener datos limpios
            is_data = to_numeric_clean(df[is_col])
            oos_data = to_numeric_clean(df[oos_col])
            
            # Alinear datos
            common_index = is_data.index.intersection(oos_data.index)
            if safe_len(common_index) < 10:
                return 0.0
            
            is_aligned = is_data.loc[common_index]
            oos_aligned = oos_data.loc[common_index]
            
            # Calcular correlación
            # pearsonr siempre devuelve (coeficiente, p-valor)
            corr, p_value = cast(Tuple[float, float], pearsonr(is_aligned, oos_aligned))
            correlation = corr
            
            # Calcular R²
            r_squared = correlation ** 2
            
            # Calcular error cuadrático medio
            mse = mean_squared_error(oos_aligned, is_aligned)
            
            # Normalizar MSE
            mse_normalized = 1.0 / (1.0 + mse)
            
            # Score compuesto
            quality_score = (r_squared + mse_normalized) / 2
            
            # Ajustar por significancia
            if p_value > self.significance_level:
                quality_score *= 0.5
            
            return float(max(0.0, min(1.0, quality_score)))
            
        except Exception as e:
            logger.warning(f"Error calculando calidad predictiva: {str(e)}")
            return 0.0
    
    def perform_hypothesis_tests(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Realiza tests de hipótesis para predictibilidad.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con resultados de tests
        """
        try:
            logger.info("Realizando tests de hipótesis...")
            
            test_results = {}
            is_oos_pairs = self._identify_is_oos_pairs(df)
            
            for is_col, oos_col in is_oos_pairs:
                if is_col in df.columns and oos_col in df.columns:
                    test_result = self._perform_paired_test(df, is_col, oos_col)
                    test_results[f"{is_col}_vs_{oos_col}_test"] = test_result
            
            logger.info(f"Tests de hipótesis completados: {len(test_results)} pares")
            return test_results
            
        except Exception as e:
            logger.error(f"Error realizando tests de hipótesis: {str(e)}")
            raise
    
    def _perform_paired_test(self, df: pd.DataFrame, is_col: str, oos_col: str) -> Dict[str, Any]:
        """
        Realiza test t pareado entre métricas IS y OOS.
        
        Args:
            df: DataFrame con datos
            is_col: Columna in-sample
            oos_col: Columna out-of-sample
            
        Returns:
            Resultado del test
        """
        try:
            # Obtener datos limpios
            is_data = to_numeric_clean(df[is_col])
            oos_data = to_numeric_clean(df[oos_col])
            
            # Alinear datos
            common_index = is_data.index.intersection(oos_data.index)
            if safe_len(common_index) < 10:
                return {'significant': False, 'p_value': 1.0, 'statistic': 0.0}
            
            is_aligned = is_data.loc[common_index]
            oos_aligned = oos_data.loc[common_index]
            
            # Test t pareado
            statistic, p_value = stats.ttest_rel(is_aligned, oos_aligned)
            
            return {
                'significant': p_value < self.significance_level,
                'p_value': float(p_value),
                'statistic': float(statistic),
                'sample_size': safe_len(common_index)
            }
            
        except Exception as e:
            logger.warning(f"Error en test pareado: {str(e)}")
            return {'significant': False, 'p_value': 1.0, 'statistic': 0.0}
    
    def analyze_multivariate_prediction(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Analiza predicción multivariada usando regresión.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con métricas de predicción multivariada
        """
        try:
            logger.info("Analizando predicción multivariada...")
            
            # Identificar métricas IS y OOS
            is_metrics = [col for col in df.columns if '_IS' in col or '_is' in col]
            oos_metrics = [col for col in df.columns if '_OOS' in col or '_oos' in col]
            
            if not is_metrics or not oos_metrics:
                return {'multivariate_r2': 0.0, 'prediction_accuracy': 0.0}
            
            # Usar primera métrica OOS como objetivo
            target_col = oos_metrics[0]
            
            # Preparar datos
            X = df[is_metrics].select_dtypes(include=[np.number]).fillna(0)
            y = to_numeric_clean(df[target_col]).fillna(0)
            
            if safe_len(X) < 10 or X.empty or y.isna().all():
                return {'multivariate_r2': 0.0, 'prediction_accuracy': 0.0}
            
            # Ajustar modelo de regresión
            model = LinearRegression()
            model.fit(X, y)
            
            # Predicciones
            y_pred = model.predict(X)
            
            # Métricas
            r2 = r2_score(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            
            # Precisión de predicción (simplificada)
            accuracy = 1.0 / (1.0 + mse)
            
            return {
                'multivariate_r2': float(r2),
                'prediction_accuracy': float(accuracy),
                'mse': float(mse),
                'n_features': safe_len(is_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis multivariado: {str(e)}")
            return {'multivariate_r2': 0.0, 'prediction_accuracy': 0.0}
    
    def calculate_predictability_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calcula métricas agregadas de predictibilidad.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con métricas de predictibilidad
        """
        try:
            logger.info("Calculando métricas agregadas de predictibilidad...")
            
            # Análisis de correlaciones
            correlations = self.analyze_is_oos_correlations(df)
            
            # Análisis de calidad predictiva
            quality_metrics = self.analyze_predictive_quality_metrics(df)
            
            # Análisis multivariado
            multivariate_metrics = self.analyze_multivariate_prediction(df)
            
            # Métricas agregadas
            avg_correlation = np.mean(list(correlations.values())) if correlations else 0.0
            overall_quality = quality_metrics.get('overall_quality', 0.0)
            multivariate_r2 = multivariate_metrics.get('multivariate_r2', 0.0)
            
            # Score de predictibilidad compuesto
            predictability_score = (avg_correlation + overall_quality + multivariate_r2) / 3
            
            metrics = {
                'average_correlation': float(avg_correlation),
                'overall_quality': float(overall_quality),
                'multivariate_r2': float(multivariate_r2),
                'predictability_score': float(predictability_score),
                'n_correlations': len(correlations)
            }
            
            # Clasificar nivel de predictibilidad
            if predictability_score >= 0.7:
                metrics['predictability_level'] = PredictabilityLevel.VERY_HIGH.value
            elif predictability_score >= 0.5:
                metrics['predictability_level'] = PredictabilityLevel.HIGH.value
            elif predictability_score >= 0.3:
                metrics['predictability_level'] = PredictabilityLevel.MODERATE.value
            elif predictability_score >= 0.1:
                metrics['predictability_level'] = PredictabilityLevel.LOW.value
            else:
                metrics['predictability_level'] = PredictabilityLevel.VERY_LOW.value
            
            logger.info(f"Métricas de predictibilidad calculadas: score={predictability_score:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculando métricas de predictibilidad: {str(e)}")
            raise
    
    def generate_scientific_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Genera reporte científico completo de predictibilidad.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con reporte completo
        """
        try:
            logger.info("Generando reporte científico de predictibilidad...")
            
            # Análisis completo
            correlations = self.analyze_is_oos_correlations(df)
            outliers_analysis = self.analyze_outliers_and_distribution(df)
            quality_metrics = self.analyze_predictive_quality_metrics(df)
            hypothesis_tests = self.perform_hypothesis_tests(df)
            multivariate_metrics = self.analyze_multivariate_prediction(df)
            predictability_metrics = self.calculate_predictability_metrics(df)
            
            # Generar recomendaciones
            recommendation = self._generate_recommendation(predictability_metrics)
            
            report = {
                'correlations': correlations,
                'outliers_analysis': outliers_analysis,
                'quality_metrics': quality_metrics,
                'hypothesis_tests': hypothesis_tests,
                'multivariate_metrics': multivariate_metrics,
                'predictability_metrics': predictability_metrics,
                'recommendation': recommendation,
                'summary': {
                    'total_metrics_analyzed': len(correlations),
                    'significant_correlations': len([c for c in correlations.values() if c > 0.3]),
                    'overall_predictability_score': predictability_metrics.get('predictability_score', 0.0),
                    'predictability_level': predictability_metrics.get('predictability_level', 'unknown')
                }
            }
            
            logger.info("Reporte científico de predictibilidad generado exitosamente")
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte científico: {str(e)}")
            raise
    
    def _generate_recommendation(self, metrics: Dict[str, float]) -> str:
        """
        Genera recomendación basada en métricas de predictibilidad.
        
        Args:
            metrics: Diccionario con métricas
            
        Returns:
            Recomendación textual
        """
        score = metrics.get('predictability_score', 0.0)
        level = metrics.get('predictability_level', 'unknown')
        
        if score >= 0.7:
            return ("EXCELENTE predictibilidad. Las estrategias muestran alta consistencia "
                   "entre datos IS y OOS. Confianza alta en resultados.")
        elif score >= 0.5:
            return ("BUENA predictibilidad. Las estrategias muestran consistencia moderada. "
                   "Resultados confiables con algunas reservas.")
        elif score >= 0.3:
            return ("PREDICTIBILIDAD MODERADA. Algunas inconsistencias entre IS y OOS. "
                   "Recomendado validación adicional.")
        elif score >= 0.1:
            return ("PREDICTIBILIDAD BAJA. Inconsistencias significativas entre IS y OOS. "
                   "Resultados poco confiables.")
        else:
            return ("PREDICTIBILIDAD MUY BAJA. Inconsistencias graves entre IS y OOS. "
                   "No se recomienda usar estos resultados.")

    def regime_adaptive_scoring(self, market_data: pd.DataFrame, strategies: pd.DataFrame) -> Dict[str, float]:
        """
        Implementar scoring adaptativo por régimen de mercado.
        
        Args:
            market_data: Datos de mercado para detección de régimen
            strategies: DataFrame con estrategias
            
        Returns:
            Diccionario con pesos optimizados por régimen
        """
        try:
            logger.info("Calculando scoring adaptativo por régimen...")
            
            # Detectar régimen actual
            current_regime = self.detect_market_regime(market_data)
            
            # Calcular rendimiento histórico por régimen
            regime_performance = self.calculate_regime_performance(strategies, current_regime)
            
            # Optimizar pesos por régimen
            optimized_weights = self.optimize_weights_by_regime(regime_performance, current_regime)
            
            logger.info(f"Scoring adaptativo calculado para régimen: {current_regime}")
            return optimized_weights
            
        except Exception as e:
            logger.error(f"Error en scoring adaptativo: {str(e)}")
            return {'default': 1.0}
    
    def detect_market_regime(self, market_data: pd.DataFrame) -> str:
        """
        Detecta el régimen de mercado actual.
        
        Args:
            market_data: Datos de mercado
            
        Returns:
            Régimen detectado: 'bull', 'bear', 'sideways', 'crisis'
        """
        try:
            if market_data.empty:
                return 'sideways'
            
            # Calcular métricas de volatilidad y tendencia
            returns = market_data['returns'].dropna() if 'returns' in market_data.columns else pd.Series([0])
            
            if len(returns) < 30:
                return 'sideways'
            
            # Calcular métricas de régimen
            volatility = returns.std()
            trend = returns.mean()
            skewness = returns.skew()
            
            # Clasificar régimen
            if trend > 0.001 and volatility < 0.02:
                return 'bull'
            elif trend < -0.001 and volatility > 0.03:
                return 'bear'
            elif volatility > 0.04:
                return 'crisis'
            else:
                return 'sideways'
                
        except Exception as e:
            logger.warning(f"Error detectando régimen: {str(e)}")
            return 'sideways'
    
    def calculate_regime_performance(self, strategies: pd.DataFrame, regime: str) -> Dict[str, float]:
        """
        Calcula rendimiento histórico por régimen.
        
        Args:
            strategies: DataFrame con estrategias
            regime: Régimen de mercado
            
        Returns:
            Diccionario con rendimiento por régimen
        """
        try:
            # Pesos por régimen (basados en feedback técnico)
            regime_weights = {
                'bull': {'stability': 0.3, 'growth': 0.5, 'efficiency': 0.2},
                'bear': {'stability': 0.5, 'growth': 0.2, 'efficiency': 0.3},
                'sideways': {'stability': 0.4, 'growth': 0.3, 'efficiency': 0.3},
                'crisis': {'stability': 0.6, 'growth': 0.1, 'efficiency': 0.3}
            }
            
            weights = regime_weights.get(regime, regime_weights['sideways'])
            
            # Calcular métricas por régimen
            performance = {}
            for metric, weight in weights.items():
                if metric == 'stability':
                    performance[metric] = self._calculate_stability_score(strategies)
                elif metric == 'growth':
                    performance[metric] = self._calculate_growth_score(strategies)
                elif metric == 'efficiency':
                    performance[metric] = self._calculate_efficiency_score(strategies)
            
            return performance
            
        except Exception as e:
            logger.error(f"Error calculando rendimiento por régimen: {str(e)}")
            return {'stability': 0.5, 'growth': 0.5, 'efficiency': 0.5}
    
    def optimize_weights_by_regime(self, regime_performance: Dict[str, float], regime: str) -> Dict[str, float]:
        """
        Optimiza pesos por régimen de mercado.
        
        Args:
            regime_performance: Rendimiento por régimen
            regime: Régimen actual
            
        Returns:
            Pesos optimizados
        """
        try:
            # Pesos base por régimen
            base_weights = {
                'bull': {'stability': 0.3, 'growth': 0.5, 'efficiency': 0.2},
                'bear': {'stability': 0.5, 'growth': 0.2, 'efficiency': 0.3},
                'sideways': {'stability': 0.4, 'growth': 0.3, 'efficiency': 0.3},
                'crisis': {'stability': 0.6, 'growth': 0.1, 'efficiency': 0.3}
            }
            
            weights = base_weights.get(regime, base_weights['sideways'])
            
            # Ajustar pesos según rendimiento
            adjusted_weights = {}
            for metric, base_weight in weights.items():
                performance = regime_performance.get(metric, 0.5)
                # Ajustar peso según rendimiento (mejor rendimiento = más peso)
                adjusted_weight = base_weight * (0.5 + performance)
                adjusted_weights[metric] = min(1.0, max(0.1, adjusted_weight))
            
            # Normalizar pesos
            total_weight = sum(adjusted_weights.values())
            if total_weight > 0:
                adjusted_weights = {k: v/total_weight for k, v in adjusted_weights.items()}
            
            return adjusted_weights
            
        except Exception as e:
            logger.error(f"Error optimizando pesos: {str(e)}")
            return {'stability': 0.33, 'growth': 0.33, 'efficiency': 0.34}
    
    def bootstrap_ci(self, data: pd.Series, metric_func, n_bootstraps: int = 1000, confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Implementar intervalos de confianza con bootstrap.
        
        Args:
            data: Datos para análisis
            metric_func: Función de métrica a calcular
            n_bootstraps: Número de bootstrap samples
            confidence: Nivel de confianza
            
        Returns:
            Tupla (lower_bound, upper_bound, original_metric)
        """
        try:
            if len(data) < 10:
                return 0.0, 0.0, 0.0
            
            # Calcular métrica original
            original_metric = metric_func(data)
            
            # Bootstrap samples
            bootstrap_metrics = []
            for _ in range(n_bootstraps):
                # Block bootstrap para preservar dependencia temporal
                resampled_data = self._block_bootstrap(data)
                if len(resampled_data) > 0:
                    bootstrap_metric = metric_func(resampled_data)
                    bootstrap_metrics.append(bootstrap_metric)
            
            if len(bootstrap_metrics) < 100:
                return 0.0, 0.0, original_metric
            
            # Calcular intervalos de confianza
            alpha = 1 - confidence
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            
            lower_bound = np.percentile(bootstrap_metrics, lower_percentile)
            upper_bound = np.percentile(bootstrap_metrics, upper_percentile)
            
            return float(lower_bound), float(upper_bound), float(original_metric)
            
        except Exception as e:
            logger.error(f"Error en bootstrap CI: {str(e)}")
            return 0.0, 0.0, 0.0
    
    def _block_bootstrap(self, data: pd.Series, block_size: int = 5) -> pd.Series:
        """
        Block bootstrap para preservar dependencia temporal.
        
        Args:
            data: Datos originales
            block_size: Tamaño del bloque
            
        Returns:
            Datos resampleados
        """
        try:
            if len(data) < block_size:
                return data
            
            # Crear índices de bloques en lugar de bloques
            n_blocks = len(data) // block_size
            block_indices = []
            
            for i in range(n_blocks):
                start_idx = i * block_size
                end_idx = start_idx + block_size
                block_indices.append((start_idx, end_idx))
            
            # Resamplear bloques usando índices
            resampled_data = []
            n_blocks_needed = max(1, len(data) // block_size)
            
            for _ in range(n_blocks_needed):
                # Seleccionar bloque aleatorio
                random_block_idx = np.random.randint(0, len(block_indices))
                start_idx, end_idx = block_indices[random_block_idx]
                
                # Extraer bloque
                block = data.iloc[start_idx:end_idx]
                resampled_data.append(block)
            
            # Concatenar bloques
            if resampled_data:
                resampled_data = pd.concat(resampled_data, ignore_index=True)
                
                # Asegurar que sea una Serie
                if isinstance(resampled_data, pd.DataFrame):
                    resampled_data = resampled_data.iloc[:, 0]
                
                # Ajustar longitud
                if len(resampled_data) > len(data):
                    resampled_data = resampled_data.iloc[:len(data)]
                
                return resampled_data
            else:
                return data
            
        except Exception as e:
            logger.warning(f"Error en block bootstrap: {str(e)}")
            return data
    
    def calculate_tail_risk(self, strategy_data: pd.Series) -> float:
        """
        Calcular métricas de riesgo de cola institucionales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            Score de riesgo de cola
        """
        try:
            if len(strategy_data) < 30:
                return 0.0
            
            # Calcular retornos
            returns = strategy_data.pct_change().dropna()
            
            if len(returns) < 10:
                return 0.0
            
            # CVaR (Conditional Value at Risk)
            cvar = self._calculate_cvar(returns, confidence=0.95)
            
            # Maximum Drawdown
            mdd = self._calculate_max_drawdown(returns)
            
            # Tail risk score (combinación de CVaR y MDD)
            tail_risk_score = cvar + 0.5 * mdd
            
            # Normalizar a 0-1
            normalized_score = min(1.0, max(0.0, tail_risk_score))
            
            return float(normalized_score)
            
        except Exception as e:
            logger.error(f"Error calculando tail risk: {str(e)}")
            return 0.0
    
    def _calculate_cvar(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Calcula Conditional Value at Risk.
        
        Args:
            returns: Retornos de la estrategia
            confidence: Nivel de confianza
            
        Returns:
            CVaR
        """
        try:
            if len(returns) < 10:
                return 0.0
            
            # Calcular VaR
            var = float(np.percentile(returns, (1 - confidence) * 100))
            
            # Calcular CVaR (promedio de pérdidas más allá del VaR)
            tail_losses = returns[returns <= var]
            
            if len(tail_losses) == 0:
                return abs(var)
            
            cvar = tail_losses.mean()
            return abs(float(cvar))
            
        except Exception as e:
            logger.warning(f"Error calculando CVaR: {str(e)}")
            return 0.0
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """
        Calcula Maximum Drawdown.
        
        Args:
            returns: Retornos de la estrategia
            
        Returns:
            Maximum Drawdown
        """
        try:
            if len(returns) < 10:
                return 0.0
            
            # Calcular equity curve
            equity_curve = (1 + returns).cumprod()
            
            # Calcular drawdown
            rolling_max = equity_curve.expanding().max()
            drawdown = (equity_curve - rolling_max) / rolling_max
            
            # Maximum drawdown
            max_dd = drawdown.min()
            
            return abs(float(max_dd))
            
        except Exception as e:
            logger.warning(f"Error calculando Max DD: {str(e)}")
            return 0.0
    
    def _calculate_stability_score(self, strategies: pd.DataFrame) -> float:
        """Calcula score de estabilidad."""
        try:
            if 'Sharpe Ratio' in strategies.columns:
                sharpe_scores = strategies['Sharpe Ratio'].dropna()
                if len(sharpe_scores) > 0:
                    return float(sharpe_scores.mean() / 3.0)  # Normalizar
            return 0.5
        except Exception:
            return 0.5
    
    def _calculate_growth_score(self, strategies: pd.DataFrame) -> float:
        """Calcula score de crecimiento."""
        try:
            if 'CAGR' in strategies.columns:
                cagr_scores = strategies['CAGR'].dropna()
                if len(cagr_scores) > 0:
                    return float(cagr_scores.mean() / 0.5)  # Normalizar
            return 0.5
        except Exception:
            return 0.5
    
    def _calculate_efficiency_score(self, strategies: pd.DataFrame) -> float:
        """Calcula score de eficiencia."""
        try:
            if 'Profit factor' in strategies.columns:
                pf_scores = strategies['Profit factor'].dropna()
                if len(pf_scores) > 0:
                    return float(pf_scores.mean() / 3.0)  # Normalizar
            return 0.5
        except Exception:
            return 0.5

    def validate_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validación robusta de calidad de datos.
        
        Args:
            data: DataFrame con datos a validar
            
        Returns:
            Diccionario con resultados de validación
        """
        try:
            logger.info("Validando calidad de datos...")
            
            if data.empty:
                return {
                    'drift_detected': True,
                    'temporal_quality': {'is_valid': False, 'issues': ['Datos vacíos']},
                    'outliers': [],
                    'is_valid': False,
                    'overall_score': 0.0
                }
            
            # Detectar data drift
            drift_detected = self.detect_data_drift(data)
            
            # Validar calidad temporal
            temporal_quality = self.validate_temporal_quality(data)
            
            # Detectar outliers
            outliers = self.detect_outliers(data)
            
            # Calcular score general
            overall_score = self._calculate_data_quality_score(drift_detected, temporal_quality, outliers)
            
            is_valid = not drift_detected and temporal_quality['is_valid'] and overall_score >= 0.7
            
            return {
                'drift_detected': drift_detected,
                'temporal_quality': temporal_quality,
                'outliers': outliers,
                'is_valid': is_valid,
                'overall_score': overall_score
            }
            
        except Exception as e:
            logger.error(f"Error en validación de datos: {str(e)}")
            return {
                'drift_detected': True,
                'temporal_quality': {'is_valid': False, 'issues': [str(e)]},
                'outliers': [],
                'is_valid': False,
                'overall_score': 0.0
            }
    
    def detect_data_drift(self, data: pd.DataFrame) -> bool:
        """
        Detecta data drift en los datos.
        
        Args:
            data: DataFrame con datos
            
        Returns:
            True si se detecta drift, False en caso contrario
        """
        try:
            if data.empty:
                return True
            
            drift_indicators = []
            
            # Verificar cambios en estadísticas básicas
            if len(data) > 100:
                # Dividir datos en dos períodos
                mid_point = len(data) // 2
                period1 = data.iloc[:mid_point]
                period2 = data.iloc[mid_point:]
                
                # Comparar estadísticas entre períodos
                for col in data.select_dtypes(include=[np.number]).columns:
                    if col in period1.columns and col in period2.columns:
                        mean1 = period1[col].mean()
                        mean2 = period2[col].mean()
                        std1 = period1[col].std()
                        std2 = period2[col].std()
                        
                        # Detectar cambios significativos
                        mean_change = abs(mean2 - mean1) / (std1 + 1e-8)
                        std_change = abs(std2 - std1) / (std1 + 1e-8)
                        
                        if mean_change > 2.0 or std_change > 1.5:
                            drift_indicators.append(f"Cambio significativo en {col}")
            
            # Verificar patrones temporales
            temporal_drift = self._detect_temporal_patterns(data)
            if temporal_drift:
                drift_indicators.append("Patrón temporal detectado")
            
            # Verificar outliers extremos
            extreme_outliers = self._detect_extreme_outliers(data)
            if extreme_outliers:
                drift_indicators.append("Outliers extremos detectados")
            
            return len(drift_indicators) > 0
            
        except Exception as e:
            logger.warning(f"Error detectando data drift: {str(e)}")
            return False
    
    def _detect_temporal_patterns(self, data: pd.DataFrame) -> bool:
        """
        Detecta patrones temporales que indican drift.
        
        Args:
            data: DataFrame con datos
            
        Returns:
            True si se detectan patrones temporales
        """
        try:
            if len(data) < 50:
                return False
            
            # Buscar columnas con datos temporales
            temporal_columns = []
            for col in data.columns:
                if any(keyword in col.lower() for keyword in ['date', 'time', 'month', 'year']):
                    temporal_columns.append(col)
            
            if not temporal_columns:
                return False
            
            # Analizar tendencias temporales
            for col in temporal_columns[:3]:  # Máximo 3 columnas
                if col in data.columns:
                    values = pd.to_numeric(data[col], errors='coerce').dropna()
                    if len(values) > 10:
                        # Convertir a numpy array para cálculos
                        values_array = values.to_numpy()
                        x = np.arange(len(values_array))
                        
                        # Calcular tendencia
                        slope, _ = np.polyfit(x, values_array, 1)
                        
                        # Si la tendencia es muy fuerte, puede indicar drift
                        if abs(slope) > np.std(values_array) * 0.1:
                            return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error detectando patrones temporales: {str(e)}")
            return False
    
    def _detect_extreme_outliers(self, data: pd.DataFrame) -> bool:
        """
        Detecta outliers extremos en los datos.
        Args:
            data: DataFrame con datos
        Returns:
            True si hay outliers extremos, False en caso contrario
        """
        try:
            extreme_count = 0
            total_count = 0
            for col in data.select_dtypes(include=[np.number]).columns:
                values = data[col].dropna()
                if not isinstance(values, pd.Series):
                    values = pd.Series(values)
                values = values.astype(float)
                if len(values) < 10:
                    continue
                Q1 = values.quantile(0.25)
                Q3 = values.quantile(0.75)
                IQR = Q3 - Q1
                # Outliers extremos (más allá de 3*IQR)
                extreme_outliers = values[(values < Q1 - 3*IQR) | (values > Q3 + 3*IQR)]
                extreme_count += int(len(extreme_outliers))
                total_count += int(len(values))
            if total_count > 0:
                return (extreme_count / total_count) > 0.05
            return False
        except Exception as e:
            logger.warning(f"Error detectando outliers extremos: {str(e)}")
            return False
    
    def validate_temporal_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Valida la calidad temporal de los datos.
        Args:
            data: DataFrame con datos
        Returns:
            Diccionario con resultados de validación temporal
        """
        try:
            issues = []
            quality_score = 1.0
            outliers: List[Dict[str, Any]] = []  # Inicializar para evitar error de variable no definida
            # Verificar completitud temporal
            if len(data) < 30:
                issues.append("Datos insuficientes para análisis temporal")
                quality_score *= 0.5
            # Verificar consistencia de fechas
            date_columns = [col for col in data.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_columns:
                for col in date_columns[:2]:  # Máximo 2 columnas de fecha
                    if col in data.columns:
                        # Asegurar que se pasa una Serie
                        series = data[col]
                        if not isinstance(series, pd.Series):
                            series = pd.Series(series)
                        date_issues = self._validate_date_consistency(series)
                        issues.extend(date_issues)
                        if date_issues:
                            quality_score *= 0.8
            # Verificar gaps temporales
            temporal_gaps = self._detect_temporal_gaps(data)
            if temporal_gaps:
                issues.append(f"Gaps temporales detectados: {temporal_gaps}")
                quality_score *= 0.7
            # Verificar estacionalidad
            seasonality_issues = self._detect_seasonality_issues(data)
            if seasonality_issues:
                issues.extend(seasonality_issues)
                quality_score *= 0.9
            return {
                'is_valid': quality_score >= 0.7,
                'score': quality_score,
                'issues': issues
            }
        except Exception as e:
            logger.warning(f"Error validando calidad temporal: {str(e)}")
            return {
                'is_valid': False,
                'score': 0.0,
                'issues': [str(e)]
            }
    
    def _validate_date_consistency(self, date_series: pd.Series) -> List[str]:
        """
        Valida consistencia de fechas.
        
        Args:
            date_series: Serie con fechas
            
        Returns:
            Lista de problemas encontrados
        """
        issues = []
        try:
            # Asegurar que sea una Serie
            if not isinstance(date_series, pd.Series):
                issues.append("Datos de fecha no son una Serie")
                return issues
            # Convertir a datetime
            dates = pd.to_datetime(date_series, errors='coerce')
            # Verificar valores nulos
            null_count = dates.isna().sum()
            if null_count > 0:
                issues.append(f"Fechas nulas: {null_count}")
            # Verificar orden temporal
            if len(dates.dropna()) > 1:
                sorted_dates = dates.dropna().sort_values()
                if not (sorted_dates == dates.dropna()).all():
                    issues.append("Fechas no están en orden cronológico")
            # Verificar duplicados
            duplicates = dates.duplicated().sum()
            if duplicates > 0:
                issues.append(f"Fechas duplicadas: {duplicates}")
        except Exception as e:
            issues.append(f"Error procesando fechas: {str(e)}")
        return issues
    
    def _detect_temporal_gaps(self, data: pd.DataFrame) -> int:
        """
        Detecta gaps temporales en los datos.
        
        Args:
            data: DataFrame con datos
            
        Returns:
            Número de gaps detectados
        """
        try:
            gap_count = 0
            
            # Buscar columnas de fecha
            date_columns = [col for col in data.columns if 'date' in col.lower()]
            
            for col in date_columns[:1]:  # Solo la primera columna de fecha
                if col in data.columns:
                    dates = pd.to_datetime(data[col], errors='coerce').dropna()
                    if len(dates) > 1:
                        # Ordenar fechas
                        dates = dates.sort_values()
                        
                        # Calcular diferencias
                        date_diffs = dates.diff().dropna()
                        
                        # Detectar gaps (diferencias muy grandes)
                        median_diff = date_diffs.median()
                        if median_diff > pd.Timedelta(0):
                            large_gaps = date_diffs > 3 * median_diff
                            gap_count = large_gaps.sum()
            
            return gap_count
            
        except Exception as e:
            logger.warning(f"Error detectando gaps temporales: {str(e)}")
            return 0
    
    def _detect_seasonality_issues(self, data: pd.DataFrame) -> List[str]:
        """
        Detecta problemas de estacionalidad.
        
        Args:
            data: DataFrame con datos
            
        Returns:
            Lista de problemas de estacionalidad
        """
        issues = []
        
        try:
            # Buscar columnas numéricas
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols[:3]:  # Máximo 3 columnas
                values = data[col].dropna()
                if len(values) > 50:
                    # Calcular autocorrelación
                    autocorr = values.autocorr()
                    
                    # Si la autocorrelación es muy alta, puede indicar estacionalidad no manejada
                    if abs(autocorr) > 0.8:
                        issues.append(f"Alta autocorrelación en {col}: {autocorr:.3f}")
            
        except Exception as e:
            logger.warning(f"Error detectando estacionalidad: {str(e)}")
        
        return issues
    
    def detect_outliers(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detecta outliers en los datos.
        
        Args:
            data: DataFrame con datos
            
        Returns:
            Lista de outliers detectados
        """
        try:
            outliers: List[Dict[str, Any]] = []  # Inicializar correctamente
            for col in data.select_dtypes(include=[np.number]).columns:
                values = data[col].dropna()
                if not isinstance(values, pd.Series):
                    values = pd.Series(values)
                values = values.astype(float)
                if len(values) < 10:
                    continue
                # Método IQR
                Q1 = values.quantile(0.25)
                Q3 = values.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_mask = (values < lower_bound) | (values > upper_bound)
                outlier_indices = list(values[outlier_mask].index)  # Asegurar iterable
                for idx in outlier_indices:
                    outliers.append({
                        'column': col,
                        'index': idx,
                        'value': float(values[idx]),
                        'method': 'IQR',
                        'severity': 'moderate'
                    })
                # Método Z-score para outliers extremos
                values_np = values.to_numpy(dtype=float)
                z_scores = np.abs((values_np - np.mean(values_np)) / np.std(values_np))
                extreme_outliers = z_scores > 3
                extreme_indices = values.index[extreme_outliers].tolist()  # Asegurar iterable siempre
                for idx in extreme_indices:
                    if idx not in outlier_indices:  # Evitar duplicados
                        outliers.append({
                            'column': col,
                            'index': idx,
                            'value': float(values[idx]),
                            'method': 'Z-score',
                            'severity': 'extreme'
                        })
            return outliers
        except Exception as e:
            logger.error(f"Error detectando outliers: {str(e)}")
            return []
    
    def _calculate_data_quality_score(self, drift_detected: bool, temporal_quality: Dict[str, Any], 
                                    outliers: List[Dict[str, Any]]) -> float:
        """
        Calcula score general de calidad de datos.
        
        Args:
            drift_detected: Si se detectó drift
            temporal_quality: Resultados de validación temporal
            outliers: Lista de outliers detectados
            
        Returns:
            Score de calidad (0-1)
        """
        try:
            score = 1.0
            
            # Penalizar por drift
            if drift_detected:
                score *= 0.5
            
            # Penalizar por problemas temporales
            temporal_score = temporal_quality.get('score', 0.0)
            score *= temporal_score
            
            # Penalizar por outliers
            outlier_penalty = min(0.2, len(outliers) * 0.01)
            score *= (1.0 - outlier_penalty)
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"Error calculando score de calidad: {str(e)}")
            return 0.0

    @property
    def correlation_threshold(self):
        return getattr(self, 'min_correlation_threshold', 0.3)

    @property
    def safe_len(self):
        return safe_len

    @property
    def safe_getitem(self):
        return safe_getitem
    
    @property
    def predictability_metrics(self):
        """Retorna las métricas de predictibilidad calculadas."""
        return {
            'correlation_threshold': self.correlation_threshold,
            'min_correlation_threshold': self.min_correlation_threshold,
            'significance_level': self.significance_level
        }

class WalkForwardAnalyzer:
    """
    Analizador de validación walk-forward.
    
    Esta clase implementa validación walk-forward para evaluar
    la robustez temporal de las estrategias de trading.
    """
    
    def __init__(self, n_folds: int = 5, progress_callback=None):
        """
        Inicializa el analizador walk-forward.
        
        Args:
            n_folds: Número de folds para validación
            progress_callback: Callback para actualizar progreso
        """
        self.n_folds = n_folds
        self.progress_callback = progress_callback
        
    def perform_walk_forward_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Realiza análisis walk-forward completo.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            logger.info(f"Realizando análisis walk-forward con {self.n_folds} folds...")
            
            # Identificar pares IS/OOS
            is_oos_pairs = self._identify_is_oos_pairs(df)
            
            if not is_oos_pairs:
                logger.warning("No se encontraron pares IS/OOS para análisis walk-forward")
                return {'error': 'No IS/OOS pairs found'}
            
            fold_results = []
            
            for i, (is_col, oos_col) in enumerate(is_oos_pairs):
                if is_col in df.columns and oos_col in df.columns:
                    # Analizar par individual
                    pair_result = self._analyze_single_pair(df, is_col, oos_col)
                    fold_results.append(pair_result)
                    
                    # Actualizar progreso
                    if self.progress_callback:
                        self.progress_callback.update_progress(
                            "walk_forward",
                            i + 1,
                            len(is_oos_pairs),
                            f"Analizando {is_col} vs {oos_col}"
                        )
            
            # Calcular métricas agregadas
            overall_metrics = self._calculate_overall_metrics(fold_results)
            predictability_score = self._calculate_predictability_score(fold_results)
            
            results = {
                'fold_results': fold_results,
                'overall_metrics': overall_metrics,
                'predictability_score': predictability_score,
                'n_pairs_analyzed': len(fold_results)
            }
            
            logger.info(f"Análisis walk-forward completado: {len(fold_results)} pares")
            return results
            
        except Exception as e:
            logger.error(f"Error en análisis walk-forward: {str(e)}")
            raise
    
    def _identify_is_oos_pairs(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Identifica pares de métricas IS/OOS.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Lista de tuplas (is_col, oos_col)
        """
        pairs = []
        
        # Validar que df.columns sea iterable y contenga strings
        try:
            columns = df.columns.tolist()
        except (AttributeError, TypeError):
            logger.warning("DataFrame columns no es iterable, usando índices numéricos")
            columns = [str(i) for i in range(len(df.columns))]
        
        # Convertir todas las columnas a strings y validar
        valid_columns = []
        for col in columns:
            if isinstance(col, (int, float)):
                col_str = str(col)
                logger.debug(f"Convirtiendo columna numérica {col} a string: {col_str}")
                valid_columns.append(col_str)
            elif isinstance(col, str):
                valid_columns.append(col)
            else:
                logger.warning(f"Columna ignorada por tipo no soportado: {type(col)}")
        
        # Buscar pares IS/OOS
        for col in valid_columns:
            if '_IS' in col:
                oos_col = col.replace('_IS', '_OOS')
                if oos_col in valid_columns:
                    pairs.append((col, oos_col))
            elif '_is' in col:
                oos_col = col.replace('_is', '_oos')
                if oos_col in valid_columns:
                    pairs.append((col, oos_col))
        
        # Si no hay pares IS/OOS, buscar métricas relacionadas
        if not pairs:
            # Buscar métricas que podrían estar relacionadas
            try:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                # Convertir columnas numéricas a strings
                numeric_cols = [str(col) if isinstance(col, (int, float)) else col for col in numeric_cols]
                
                for i, col1 in enumerate(numeric_cols):
                    for col2 in numeric_cols[i+1:]:
                        if self._are_related_metrics(col1, col2):
                            pairs.append((col1, col2))
            except Exception as e:
                logger.warning(f"Error buscando métricas relacionadas: {e}")
        
        logger.debug(f"Pares IS/OOS identificados: {pairs}")
        return pairs
    
    def _analyze_single_pair(self, df: pd.DataFrame, is_col: str, oos_col: str) -> Dict[str, Any]:
        """
        Analiza un par individual de métricas IS/OOS.
        
        Args:
            df: DataFrame con datos
            is_col: Columna in-sample
            oos_col: Columna out-of-sample
            
        Returns:
            Resultado del análisis del par
        """
        try:
            # Obtener datos limpios
            is_data = to_numeric_clean(df[is_col])
            oos_data = to_numeric_clean(df[oos_col])
            
            # Alinear datos
            common_index = is_data.index.intersection(oos_data.index)
            if safe_len(common_index) < 10:
                return {
                    'is_col': is_col,
                    'oos_col': oos_col,
                    'correlation': 0.0,
                    'r_squared': 0.0,
                    'p_value': 1.0,
                    'sample_size': 0,
                    'error': 'Insufficient data'
                }
            
            is_aligned = is_data.loc[common_index]
            oos_aligned = oos_data.loc[common_index]
            
            # Calcular correlación
            # pearsonr siempre devuelve (coeficiente, p-valor)
            corr, p_value = cast(Tuple[float, float], pearsonr(is_aligned, oos_aligned))
            correlation = corr
            
            # Calcular R²
            r_squared = correlation ** 2
            
            # Calcular error cuadrático medio
            mse = mean_squared_error(oos_aligned, is_aligned)
            
            return {
                'is_col': is_col,
                'oos_col': oos_col,
                'correlation': correlation,
                'r_squared': r_squared,
                'p_value': p_value,
                'mse': mse,
                'sample_size': safe_len(common_index),
                'significant': p_value < 0.05
            }
            
        except Exception as e:
            logger.warning(f"Error analizando par {is_col} vs {oos_col}: {str(e)}")
            return {
                'is_col': is_col,
                'oos_col': oos_col,
                'correlation': 0.0,
                'r_squared': 0.0,
                'p_value': 1.0,
                'sample_size': 0,
                'error': str(e)
            }
    
    def _calculate_overall_metrics(self, fold_results: List[Dict]) -> Dict[str, float]:
        """
        Calcula métricas agregadas de todos los folds.
        
        Args:
            fold_results: Lista de resultados de folds
            
        Returns:
            Diccionario con métricas agregadas
        """
        try:
            # Filtrar resultados válidos
            valid_results = [r for r in fold_results if 'error' not in r]
            
            if not valid_results:
                return {
                    'avg_correlation': 0.0,
                    'avg_r_squared': 0.0,
                    'avg_mse': 0.0,
                    'significant_pairs': 0,
                    'total_pairs': len(fold_results)
                }
            
            # Calcular métricas agregadas
            correlations = [r['correlation'] for r in valid_results]
            r_squared_values = [r['r_squared'] for r in valid_results]
            mse_values = [r['mse'] for r in valid_results]
            significant_count = sum(1 for r in valid_results if r.get('significant', False))
            
            return {
                'avg_correlation': float(np.mean(correlations)),
                'avg_r_squared': float(np.mean(r_squared_values)),
                'avg_mse': float(np.mean(mse_values)),
                'std_correlation': float(np.std(correlations)),
                'significant_pairs': significant_count,
                'total_pairs': len(fold_results),
                'valid_pairs': len(valid_results)
            }
            
        except Exception as e:
            logger.error(f"Error calculando métricas agregadas: {str(e)}")
            return {
                'avg_correlation': 0.0,
                'avg_r_squared': 0.0,
                'avg_mse': 0.0,
                'significant_pairs': 0,
                'total_pairs': len(fold_results)
            }
    
    def _calculate_predictability_score(self, fold_results: List[Dict]) -> float:
        """
        Calcula score de predictibilidad basado en resultados walk-forward.
        
        Args:
            fold_results: Lista de resultados de folds
            
        Returns:
            Score de predictibilidad (0-1)
        """
        try:
            valid_results = [r for r in fold_results if 'error' not in r]
            
            if not valid_results:
                return 0.0
            
            # Componentes del score
            avg_correlation = np.mean([r['correlation'] for r in valid_results])
            avg_r_squared = np.mean([r['r_squared'] for r in valid_results])
            significant_ratio = sum(1 for r in valid_results if r.get('significant', False)) / len(valid_results)
            
            # Score compuesto
            predictability_score = (avg_correlation + avg_r_squared + significant_ratio) / 3
            
            # Convertir a float antes de min/max para evitar errores con np.float64
            predictability_score = float(predictability_score)
            return max(0.0, min(1.0, predictability_score))
            
        except Exception as e:
            logger.error(f"Error calculando score de predictibilidad: {str(e)}")
            return 0.0

class NullSimulationAnalyzer:
    """
    Analizador de simulaciones de hipótesis nula.
    
    Esta clase implementa simulaciones para evaluar la significancia
    estadística de las correlaciones IS/OOS.
    """
    
    def __init__(self, n_simulations: int = 100, progress_callback=None):
        """
        Inicializa el analizador de simulaciones nulas.
        
        Args:
            n_simulations: Número de simulaciones
            progress_callback: Callback para actualizar progreso
        """
        self.n_simulations = n_simulations
        self.progress_callback = progress_callback
        
    def perform_null_simulation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Realiza simulación de hipótesis nula.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con resultados de la simulación
        """
        try:
            logger.info(f"Realizando simulación de hipótesis nula con {self.n_simulations} iteraciones...")
            
            # Identificar métricas numéricas
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if safe_len(numeric_cols) < 2:
                return {'error': 'Insufficient numeric columns for simulation'}
            
            simulation_results = {}
            
            for i, col in enumerate(numeric_cols):
                if i % 10 == 0 and self.progress_callback:
                    self.progress_callback.update_progress(
                        "null_simulation",
                        i,
                        len(numeric_cols),
                        f"Simulando {col}"
                    )
                
                metric_result = self._simulate_metric(df, col)
                simulation_results[col] = metric_result
            
            # Calcular significancia general
            overall_significance = self._calculate_overall_significance(simulation_results)
            
            results = {
                'simulation_results': simulation_results,
                'overall_significance': overall_significance,
                'n_metrics_simulated': len(simulation_results),
                'n_simulations': self.n_simulations
            }
            
            logger.info(f"Simulación de hipótesis nula completada: {len(simulation_results)} métricas")
            return results
            
        except Exception as e:
            logger.error(f"Error en simulación de hipótesis nula: {str(e)}")
            raise
    
    def _simulate_metric(self, df: pd.DataFrame, metric: str) -> Dict[str, Any]:
        """
        Simula una métrica específica.
        
        Args:
            df: DataFrame con datos
            metric: Nombre de la métrica
            
        Returns:
            Resultado de la simulación
        """
        try:
            col_data = df[metric]
            if not isinstance(col_data, pd.Series):
                col_data = pd.Series(col_data)
            data = to_numeric_clean(col_data)
            
            if safe_len(data) < 10:
                return {
                    'original_correlation': 0.0,
                    'null_correlations': [],
                    'p_value': 1.0,
                    'significant': False,
                    'sample_size': safe_len(data)
                }
            
            # Calcular correlación original (si hay pares)
            original_correlation = 0.0
            if '_IS' in metric:
                oos_metric = metric.replace('_IS', '_OOS')
                if oos_metric in df.columns:
                    oos_data = to_numeric_clean(df[oos_metric])
                    common_index = data.index.intersection(oos_data.index)
                    if safe_len(common_index) >= 10:
                        # pearsonr siempre devuelve (coeficiente, p-valor)
                        corr, _ = cast(Tuple[float, float], pearsonr(data.loc[common_index], oos_data.loc[common_index]))
                        original_correlation = corr
            # Simular correlaciones nulas
            null_correlations = []
            for _ in range(self.n_simulations):
                # Permutar datos aleatoriamente
                shuffled_data = data.sample(frac=1.0, random_state=np.random.randint(1000))
                # Calcular correlación con datos permutados
                if safe_len(data) >= 10:
                    # pearsonr siempre devuelve (coeficiente, p-valor)
                    corr, _ = cast(Tuple[float, float], pearsonr(data, shuffled_data))
                    null_correlations.append(corr)
                p_value = np.mean([abs(float(corr)) >= abs(float(original_correlation)) for corr in null_correlations])
            return {
                'original_correlation': original_correlation,
                'null_correlations': null_correlations,
                'p_value': p_value,
                'significant': p_value < 0.05,
                'sample_size': safe_len(data),
                'null_mean': float(np.mean(null_correlations)) if null_correlations else 0.0,
                'null_std': float(np.std(null_correlations)) if null_correlations else 0.0
            }
            
        except Exception as e:
            logger.warning(f"Error simulando métrica {metric}: {str(e)}")
            return {
                'original_correlation': 0.0,
                'null_correlations': [],
                'p_value': 1.0,
                'significant': False,
                'sample_size': 0,
                'error': str(e)
            }
    
    def _calculate_overall_significance(self, simulation_results: Dict[str, Dict]) -> float:
        """
        Calcula significancia general de las simulaciones.
        
        Args:
            simulation_results: Resultados de simulaciones
            
        Returns:
            Significancia general (0-1)
        """
        try:
            valid_results = [r for r in simulation_results.values() if 'error' not in r]
            
            if not valid_results:
                return 0.0
            
            # Calcular significancia agregada
            significant_count = sum(1 for r in valid_results if r.get('significant', False))
            overall_significance = significant_count / len(valid_results)
            
            return float(overall_significance)
            
        except Exception as e:
            logger.error(f"Error calculando significancia general: {str(e)}")
            return 0.0 

    def optimize_portfolio_allocation(self, strategies: pd.DataFrame, max_position_size: float = 0.1, 
                                    max_sector_exposure: float = 0.3, max_volatility: float = 0.15) -> Dict[str, float]:
        """
        Optimización de capital con restricciones institucionales.
        
        Args:
            strategies: DataFrame con estrategias
            max_position_size: Tamaño máximo de posición individual
            max_sector_exposure: Exposición máxima por sector
            max_volatility: Volatilidad máxima del portfolio
            
        Returns:
            Diccionario con pesos optimizados por estrategia
        """
        try:
            logger.info("Optimizando asignación de capital...")
            
            if strategies.empty:
                return {}
            
            # Preparar datos para optimización
            returns_data = self._prepare_returns_data(strategies)
            
            if returns_data.empty:
                return {}
            
            # Calcular matriz de covarianza
            cov_matrix = returns_data.cov()
            
            # Calcular retornos esperados
            expected_returns = returns_data.mean()
            # Forzar a pd.Series si no lo es
            if not isinstance(expected_returns, pd.Series):
                expected_returns = pd.Series(expected_returns)
            
            # Optimización con restricciones
            optimal_weights = self._solve_portfolio_optimization(
                expected_returns, cov_matrix, max_position_size, 
                max_sector_exposure, max_volatility
            )
            
            # Crear diccionario de resultados
            allocation = {}
            for i, strategy_name in enumerate(returns_data.columns):
                if i < len(optimal_weights):
                    allocation[strategy_name] = float(optimal_weights[i])
            
            logger.info(f"Optimización completada: {len(allocation)} estrategias")
            return allocation
            
        except Exception as e:
            logger.error(f"Error en optimización de portfolio: {str(e)}")
            return {}
    
    def _prepare_returns_data(self, strategies: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara datos de retornos para optimización.
        
        Args:
            strategies: DataFrame con estrategias
            
        Returns:
            DataFrame con retornos
        """
        try:
            # Buscar columnas de retornos
            returns_columns = []
            for col in strategies.columns:
                if 'return' in col.lower() or 'cagr' in col.lower():
                    returns_columns.append(col)
            
            if not returns_columns:
                # Usar CAGR como proxy de retornos
                if 'CAGR' in strategies.columns:
                    returns_columns = ['CAGR']
                else:
                    return pd.DataFrame()
            
            # Crear DataFrame de retornos
            returns_data = strategies[returns_columns].copy()
            
            # Limpiar datos
            returns_data = returns_data.dropna()
            
            # Normalizar retornos (convertir a retornos diarios si es necesario)
            for col in returns_data.columns:
                if 'CAGR' in col:
                    # Convertir CAGR anual a retorno diario aproximado
                    returns_data[col] = returns_data[col] / 252
            
            # Asegurar que sea DataFrame
            if isinstance(returns_data, pd.Series):
                returns_data = returns_data.to_frame()
            
            return returns_data
            
        except Exception as e:
            logger.warning(f"Error preparando datos de retornos: {str(e)}")
            return pd.DataFrame()
    
    def _solve_portfolio_optimization(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame,
                                    max_position_size: float, max_sector_exposure: float, 
                                    max_volatility: float) -> np.ndarray:
        """
        Resuelve optimización de portfolio con restricciones.
        """
        try:
            # Verificar que expected_returns sea una Serie
            if not isinstance(expected_returns, pd.Series):
                logger.warning("expected_returns no es una Serie, usando valores por defecto")
                return np.array([])
            n_assets = len(expected_returns)
            if n_assets == 0:
                return np.array([])
            # Usar optimización simple si no hay cvxpy
            try:
                import cvxpy as cp
                return self._solve_with_cvxpy(expected_returns, cov_matrix, max_position_size, 
                                            max_sector_exposure, max_volatility)
            except ImportError:
                # Fallback: optimización simple
                return self._solve_simple_optimization(expected_returns, cov_matrix, max_position_size)
        except Exception as e:
            logger.warning(f"Error en optimización: {str(e)}")
            # Retornar pesos iguales
            n_assets = len(expected_returns) if isinstance(expected_returns, pd.Series) else 0
            return np.ones(n_assets) / n_assets if n_assets > 0 else np.array([])
    
    def _solve_with_cvxpy(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame,
                          max_position_size: float, max_sector_exposure: float, 
                          max_volatility: float) -> np.ndarray:
        """
        Optimización usando cvxpy (si está disponible).
        """
        import cvxpy as cp
        
        n_assets = len(expected_returns)
        w = cp.Variable(n_assets)
        
        # Función objetivo: maximizar retorno esperado
        objective = cp.Maximize(expected_returns.values @ w)
        
        # Restricciones
        constraints = [
            cp.sum(w) == 1,  # Pesos suman 1
            w >= 0,  # Pesos no negativos
            w <= max_position_size,  # Tamaño máximo de posición
            cp.quad_form(w, cov_matrix.values) <= max_volatility**2  # Volatilidad máxima
        ]
        
        # Resolver problema
        prob = cp.Problem(objective, constraints)
        prob.solve()
        
        if prob.status == 'optimal' and w.value is not None:
            return w.value
        else:
            # Fallback a pesos iguales
            return np.ones(n_assets) / n_assets
    
    def _solve_simple_optimization(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame,
                                 max_position_size: float) -> np.ndarray:
        """
        Optimización simple sin cvxpy.
        """
        n_assets = len(expected_returns)
        
        # Pesos iniciales iguales
        weights = np.ones(n_assets) / n_assets
        
        # Ajustar según retornos esperados
        for i in range(n_assets):
            if expected_returns.iloc[i] > 0:
                weights[i] *= 1.2  # Dar más peso a estrategias con retorno positivo
            else:
                weights[i] *= 0.8  # Reducir peso a estrategias con retorno negativo
        
        # Normalizar y aplicar restricción de tamaño máximo
        weights = weights / np.sum(weights)
        weights = np.minimum(weights, max_position_size)
        weights = weights / np.sum(weights)
        
        return weights
    
    def stress_test_portfolio(self, strategies: pd.DataFrame, allocation: Dict[str, float],
                            stress_scenarios: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Stress testing sistemático del portfolio.
        
        Args:
            strategies: DataFrame con estrategias
            allocation: Asignación de capital
            stress_scenarios: Escenarios de estrés personalizados (cada dict debe tener clave 'name': str y el resto float)
            
        Returns:
            Resultados del stress testing
        """
        try:
            logger.info("Ejecutando stress testing...")
            if not allocation:
                return {'error': 'No hay asignación de capital'}
            # Escenarios de estrés por defecto
            if stress_scenarios is None:
                # Forzar todos los valores a float salvo 'name'
                stress_scenarios = [
                    {'name': 'Crisis de Mercado', 'market_shock': -0.2, 'volatility_increase': 2.0},
                    {'name': 'Recesión', 'market_shock': -0.1, 'volatility_increase': 1.5},
                    {'name': 'Crisis de Liquidez', 'market_shock': -0.15, 'liquidity_shock': 0.5},
                    {'name': 'Crisis de Correlación', 'correlation_increase': 0.3}
                ]
            # Validar que stress_scenarios es una lista de dict[str, float] salvo 'name'
            if stress_scenarios is not None:
                for scenario in stress_scenarios:
                    for k, v in scenario.items():
                        if k != 'name' and not isinstance(v, float):
                            try:
                                scenario[k] = float(v)
                            except Exception:
                                scenario[k] = 0.0
            results = {}
            for scenario in (stress_scenarios or []):
                scenario_result = self._run_stress_scenario(strategies, allocation, scenario)
                results[scenario.get('name', f'scenario_{id(scenario)}')] = scenario_result
            # Calcular métricas agregadas
            aggregate_metrics = self._calculate_stress_aggregates(results)
            results['aggregate'] = aggregate_metrics
            logger.info(f"Stress testing completado: {len(results)} escenarios")
            return results
        except Exception as e:
            logger.error(f"Error en stress testing: {str(e)}")
            return {'error': str(e)}
    
    def _run_stress_scenario(self, strategies: pd.DataFrame, allocation: Dict[str, float],
                           scenario: Dict[str, float]) -> Dict[str, float]:
        """
        Ejecuta un escenario de estrés específico.
        
        Args:
            strategies: DataFrame con estrategias
            allocation: Asignación de capital
            scenario: Escenario de estrés
            
        Returns:
            Resultados del escenario
        """
        try:
            # Simular impacto del escenario
            stressed_returns = {}
            
            for strategy, weight in allocation.items():
                if strategy in strategies.index:
                    # Obtener métricas de la estrategia
                    strategy_data = strategies.loc[strategy]
                    
                    # Calcular retorno base
                    base_return = strategy_data.get('CAGR', 0.0) / 252  # Convertir a diario
                    
                    # Aplicar shocks del escenario
                    stressed_return = base_return
                    
                    if 'market_shock' in scenario:
                        # Shock de mercado afecta a todas las estrategias
                        stressed_return += scenario['market_shock'] * 0.1
                    
                    if 'volatility_increase' in scenario:
                        # Aumento de volatilidad reduce retornos
                        stressed_return *= (1 - 0.1 * scenario['volatility_increase'])
                    
                    if 'liquidity_shock' in scenario:
                        # Shock de liquidez afecta más a estrategias con mayor exposición
                        exposure = strategy_data.get('Exposure', 0.5)
                        stressed_return *= (1 - scenario['liquidity_shock'] * exposure)
                    
                    stressed_returns[strategy] = stressed_return
            
            # Calcular métricas del portfolio estresado
            portfolio_return = sum(stressed_returns.values())
            portfolio_volatility = np.std(list(stressed_returns.values())) if len(stressed_returns) > 1 else 0.0
            sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0.0
            
            return {
                'portfolio_return': float(portfolio_return),
                'portfolio_volatility': float(portfolio_volatility),
                'sharpe_ratio': float(sharpe_ratio),
                'max_drawdown': float(min(0, portfolio_return * 0.5)),  # Estimación simple
                'var_95': float(np.percentile(list(stressed_returns.values()), 5) if stressed_returns else 0.0)
            }
            
        except Exception as e:
            logger.warning(f"Error en escenario de estrés: {str(e)}")
            return {
                'portfolio_return': 0.0,
                'portfolio_volatility': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'var_95': 0.0
            }
    
    def _calculate_stress_aggregates(self, results: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Calcula métricas agregadas del stress testing.
        
        Args:
            results: Resultados de todos los escenarios
            
        Returns:
            Métricas agregadas
        """
        try:
            # Filtrar resultados válidos
            valid_results = {k: v for k, v in results.items() if 'error' not in v}
            
            if not valid_results:
                return {'error': 'No hay resultados válidos'}
            
            # Calcular métricas agregadas
            returns = [r['portfolio_return'] for r in valid_results.values()]
            volatilities = [r['portfolio_volatility'] for r in valid_results.values()]
            sharpe_ratios = [r['sharpe_ratio'] for r in valid_results.values()]
            
            return {
                'avg_return': float(np.mean(returns)),
                'worst_return': float(np.min(returns)),
                'avg_volatility': float(np.mean(volatilities)),
                'max_volatility': float(np.max(volatilities)),
                'avg_sharpe': float(np.mean(sharpe_ratios)),
                'worst_sharpe': float(np.min(sharpe_ratios)),
                'scenarios_tested': len(valid_results)
            }
            
        except Exception as e:
            logger.warning(f"Error calculando agregados: {str(e)}")
            return {'error': str(e)}
    
    def calculate_compliance_score(self, strategies: pd.DataFrame, allocation: Dict[str, float]) -> float:
        """
        Calcula score de compliance institucional.
        
        Args:
            strategies: DataFrame con estrategias
            allocation: Asignación de capital
            
        Returns:
            Score de compliance (0-100)
        """
        try:
            if not allocation:
                return 0.0
            
            compliance_checks = []
            
            # Verificar diversificación
            if len(allocation) >= 5:
                compliance_checks.append(1.0)  # Buena diversificación
            elif len(allocation) >= 3:
                compliance_checks.append(0.7)  # Diversificación moderada
            else:
                compliance_checks.append(0.3)  # Poca diversificación
            
            # Verificar concentración
            max_weight = max(allocation.values()) if allocation else 0.0
            if max_weight <= 0.1:
                compliance_checks.append(1.0)  # Buena concentración
            elif max_weight <= 0.2:
                compliance_checks.append(0.7)  # Concentración moderada
            else:
                compliance_checks.append(0.3)  # Alta concentración
            
            # Verificar métricas de riesgo
            risk_metrics = []
            for strategy, weight in allocation.items():
                if strategy in strategies.index:
                    strategy_data = strategies.loc[strategy]
                    
                    # Sharpe Ratio
                    sharpe = strategy_data.get('Sharpe Ratio', 0.0)
                    if sharpe >= 1.0:
                        risk_metrics.append(1.0)
                    elif sharpe >= 0.5:
                        risk_metrics.append(0.7)
                    else:
                        risk_metrics.append(0.3)
                    
                    # Drawdown
                    drawdown = strategy_data.get('Drawdown', 100.0)
                    if drawdown <= 10.0:
                        risk_metrics.append(1.0)
                    elif drawdown <= 20.0:
                        risk_metrics.append(0.7)
                    else:
                        risk_metrics.append(0.3)
            
            # Calcular score final
            all_checks = compliance_checks + risk_metrics
            compliance_score = np.mean(all_checks) * 100
            
            return float(compliance_score)
            
        except Exception as e:
            logger.error(f"Error calculando compliance score: {str(e)}")
            return 0.0 