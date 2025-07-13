"""
ROBUSTNESS_ANALYZER.py - Análisis de Robustez

Este módulo contiene las clases para análisis de robustez:
- RobustnessAnalyzer: Análisis de estabilidad de métricas
- StressTestGenerator: Generador de pruebas de estrés
- AdvancedDataProcessor: Procesamiento avanzado de datos

Extraído de core_engine_enhanced.py para modularización.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from scipy import stats
from scipy.stats import variation, skew, kurtosis
import warnings
from dataclasses import dataclass
from enum import Enum
import itertools
from sklearn.ensemble import IsolationForest
from sklearn.covariance import EllipticEnvelope
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

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

class RobustnessLevel(Enum):
    """Niveles de robustez."""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"

@dataclass
class RobustnessResult:
    """Resultado del análisis de robustez."""
    stability_score: float
    consistency_score: float
    outlier_percentage: float
    robustness_level: str
    recommendations: List[str]

class RobustnessAnalyzer:
    """
    Analizador de robustez de métricas.
    
    Esta clase implementa análisis de robustez para evaluar la estabilidad
    y consistencia de las métricas de trading.
    """
    
    def __init__(self, progress_callback=None):
        """
        Inicializa el analizador de robustez.
        
        Args:
            progress_callback: Callback para actualizar progreso
        """
        self.progress_callback = progress_callback
        self.outlier_threshold = 0.05  # 5% de outliers máximo
        self.stability_threshold = 0.7  # 70% de estabilidad mínimo
        
    def analyze_stability_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Analiza métricas de estabilidad.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con métricas de estabilidad
        """
        try:
            logger.info("Analizando métricas de estabilidad...")
            
            stability_metrics = {}
            
            # Métricas clave para análisis de estabilidad
            key_metrics = ['Sharpe Ratio', 'CAGR', 'Drawdown', 'Profit factor']
            
            for metric in key_metrics:
                if metric in df.columns:
                    # Calcular estabilidad de Sharpe
                    if metric == 'Sharpe Ratio':
                        stability = self._calculate_sharpe_stability(df)
                        stability_metrics['sharpe_stability'] = stability
                    
                    # Calcular estabilidad de Drawdown
                    elif metric == 'Drawdown':
                        stability = self._calculate_drawdown_stability(df)
                        stability_metrics['drawdown_stability'] = stability
                    
                    # Calcular consistencia de retornos
                    elif metric == 'CAGR':
                        stability = self._calculate_return_consistency(df)
                        stability_metrics['return_consistency'] = stability
                    
                    # Calcular estabilidad de Profit Factor
                    elif metric == 'Profit factor':
                        stability = self._calculate_profit_factor_stability(df)
                        stability_metrics['profit_factor_stability'] = stability
            
            # Calcular estabilidad general
            if stability_metrics:
                overall_stability = np.mean(list(stability_metrics.values()))
                stability_metrics['overall_stability'] = float(overall_stability)
                
                # Clasificar nivel de estabilidad
                if overall_stability >= 0.8:
                    stability_metrics['stability_level'] = RobustnessLevel.VERY_HIGH.value
                elif overall_stability >= 0.6:
                    stability_metrics['stability_level'] = RobustnessLevel.HIGH.value
                elif overall_stability >= 0.4:
                    stability_metrics['stability_level'] = RobustnessLevel.MODERATE.value
                elif overall_stability >= 0.2:
                    stability_metrics['stability_level'] = RobustnessLevel.LOW.value
                else:
                    stability_metrics['stability_level'] = RobustnessLevel.VERY_LOW.value
            
            logger.info(f"Análisis de estabilidad completado: {len(stability_metrics)} métricas")
            return stability_metrics
            
        except Exception as e:
            logger.error(f"Error analizando estabilidad: {str(e)}")
            raise
    
    def _calculate_sharpe_stability(self, df: pd.DataFrame) -> float:
        """
        Calcula estabilidad del Sharpe Ratio.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Score de estabilidad (0-1)
        """
        try:
            sharpe_data = pd.to_numeric(df['Sharpe Ratio'], errors='coerce').dropna()
            
            if safe_len(sharpe_data) < 10:
                return 0.0
            
            # Calcular coeficiente de variación (inverso de estabilidad)
            cv = variation(sharpe_data)
            
            # Convertir a score de estabilidad (0-1)
            # CV bajo = alta estabilidad
            stability_score = 1.0 / (1.0 + cv)
            
            return float(stability_score)
            
        except Exception as e:
            logger.warning(f"Error calculando estabilidad de Sharpe: {str(e)}")
            return 0.0
    
    def _calculate_drawdown_stability(self, df: pd.DataFrame) -> float:
        """
        Calcula estabilidad del Drawdown.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Score de estabilidad (0-1)
        """
        try:
            drawdown_data = pd.to_numeric(df['Drawdown'], errors='coerce').dropna()
            
            if safe_len(drawdown_data) < 10:
                return 0.0
            
            # Para drawdown, queremos baja variabilidad (estabilidad)
            cv = variation(drawdown_data)
            
            # Convertir a score de estabilidad
            stability_score = 1.0 / (1.0 + cv)
            
            return float(stability_score)
            
        except Exception as e:
            logger.warning(f"Error calculando estabilidad de Drawdown: {str(e)}")
            return 0.0
    
    def _calculate_return_consistency(self, df: pd.DataFrame) -> float:
        """
        Calcula consistencia de retornos.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Score de consistencia (0-1)
        """
        try:
            cagr_data = pd.to_numeric(df['CAGR'], errors='coerce').dropna()
            
            if safe_len(cagr_data) < 10:
                return 0.0
            
            # Calcular consistencia basada en distribución
            # Menor skewness y kurtosis = mayor consistencia
            skewness = abs(skew(cagr_data))
            kurt = abs(kurtosis(cagr_data))
            
            # Normalizar y combinar
            skewness_score = 1.0 / (1.0 + skewness)
            kurtosis_score = 1.0 / (1.0 + kurt)
            
            consistency_score = (skewness_score + kurtosis_score) / 2
            
            return float(consistency_score)
            
        except Exception as e:
            logger.warning(f"Error calculando consistencia de retornos: {str(e)}")
            return 0.0
    
    def _calculate_profit_factor_stability(self, df: pd.DataFrame) -> float:
        """
        Calcula estabilidad del Profit Factor.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Score de estabilidad (0-1)
        """
        try:
            pf_data = pd.to_numeric(df['Profit factor'], errors='coerce').dropna()
            
            if safe_len(pf_data) < 10:
                return 0.0
            
            # Calcular estabilidad basada en variación
            cv = variation(pf_data)
            
            # Convertir a score de estabilidad
            stability_score = 1.0 / (1.0 + cv)
            
            return float(stability_score)
            
        except Exception as e:
            logger.warning(f"Error calculando estabilidad de Profit Factor: {str(e)}")
            return 0.0
    
    def detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detecta outliers en las métricas.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con información de outliers
        """
        try:
            logger.info("Detectando outliers en métricas...")
            
            outlier_info = {}
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                data = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if safe_len(data) >= 10:
                    # Detectar outliers usando IQR
                    Q1 = data.quantile(0.25)
                    Q3 = data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = data[(data < lower_bound) | (data > upper_bound)]
                    
                    # Asegurar que los datos son iterables
                    outlier_count = safe_len(outliers)
                    data_count = safe_len(data)
                    
                    outlier_info[col] = {
                        'outlier_count': outlier_count,
                        'outlier_percentage': float(outlier_count / data_count * 100) if data_count > 0 else 0.0,
                        'total_count': data_count,
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound)
                    }
            
            # Calcular estadísticas agregadas
            if outlier_info:
                total_outliers = sum(info['outlier_count'] for info in outlier_info.values())
                total_data_points = sum(info['total_count'] for info in outlier_info.values())
                overall_outlier_percentage = (total_outliers / total_data_points * 100) if total_data_points > 0 else 0
                
                outlier_info['summary'] = {
                    'total_outliers': total_outliers,
                    'total_data_points': total_data_points,
                    'overall_outlier_percentage': float(overall_outlier_percentage),
                    'metrics_with_outliers': len([info for info in outlier_info.values() 
                                                if info['outlier_count'] > 0])
                }
            
            logger.info(f"Detección de outliers completada: {len(outlier_info)} métricas")
            return outlier_info
            
        except Exception as e:
            logger.error(f"Error detectando outliers: {str(e)}")
            raise
    
    def analyze_distribution_robustness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analiza robustez de distribución de métricas.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con análisis de distribución
        """
        try:
            logger.info("Analizando robustez de distribución...")
            
            distribution_analysis = {}
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                data = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if safe_len(data) >= 10:
                    # Estadísticas de distribución
                    data_array = np.asarray(data).flatten()  # Asegurar array 1D
                    
                    # Validar que los datos no sean idénticos para evitar precision loss
                    if np.allclose(data_array, data_array[0], rtol=1e-10):
                        # Si todos los valores son prácticamente idénticos, usar valores por defecto
                        mean_val = float(data_array[0])
                        std_val = 0.0
                        skewness_val = 0.0  # Distribución simétrica
                        kurtosis_val = 3.0  # Distribución normal
                    else:
                        # Calcular estadísticas normalmente
                        mean_val = float(np.mean(data_array))
                        std_val = float(np.std(data_array))
                        
                        # Calcular skewness y kurtosis con manejo de warnings
                        try:
                            skewness_val = float(skew(data_array))
                            kurtosis_val = float(kurtosis(data_array))
                        except (RuntimeWarning, ValueError):
                            # Si hay problemas de precisión, usar valores por defecto
                            skewness_val = 0.0
                            kurtosis_val = 3.0
                    
                    # Calcular robustez de distribución
                    # Distribución normal tiene skewness ≈ 0 y kurtosis ≈ 3
                    skewness_robustness = 1.0 / (1.0 + abs(skewness_val))
                    kurtosis_robustness = 1.0 / (1.0 + abs(kurtosis_val - 3))
                    
                    # Robustez general
                    distribution_robustness = (skewness_robustness + kurtosis_robustness) / 2
                    
                    distribution_analysis[col] = {
                        'mean': mean_val,
                        'std': std_val,
                        'skewness': skewness_val,
                        'kurtosis': kurtosis_val,
                        'skewness_robustness': float(skewness_robustness),
                        'kurtosis_robustness': float(kurtosis_robustness),
                        'distribution_robustness': float(distribution_robustness)
                    }
            
            # Calcular robustez agregada
            if distribution_analysis:
                avg_robustness = np.mean([info['distribution_robustness'] 
                                        for info in distribution_analysis.values()])
                distribution_analysis['summary'] = {
                    'average_distribution_robustness': float(avg_robustness),
                    'metrics_analyzed': len(distribution_analysis)
                }
            
            logger.info(f"Análisis de distribución completado: {len(distribution_analysis)} métricas")
            return distribution_analysis
            
        except Exception as e:
            logger.error(f"Error analizando distribución: {str(e)}")
            raise
    
    def calculate_overall_robustness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula robustez general del conjunto de datos.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            Diccionario con análisis de robustez general
        """
        try:
            logger.info("Calculando robustez general...")
            
            # Análisis completo
            stability_metrics = self.analyze_stability_metrics(df)
            outlier_info = self.detect_outliers(df)
            distribution_analysis = self.analyze_distribution_robustness(df)
            
            # Calcular score de robustez general
            overall_stability = stability_metrics.get('overall_stability', 0.0)
            
            # Robustez basada en outliers
            outlier_percentage = outlier_info.get('summary', {}).get('overall_outlier_percentage', 0.0)
            outlier_robustness = max(0.0, 1.0 - (outlier_percentage / 100.0))
            
            # Robustez basada en distribución
            distribution_robustness = distribution_analysis.get('summary', {}).get('average_distribution_robustness', 0.0)
            
            # Score compuesto
            overall_robustness = (overall_stability + outlier_robustness + distribution_robustness) / 3
            
            # Clasificar nivel de robustez
            if overall_robustness >= 0.8:
                robustness_level = RobustnessLevel.VERY_HIGH.value
            elif overall_robustness >= 0.6:
                robustness_level = RobustnessLevel.HIGH.value
            elif overall_robustness >= 0.4:
                robustness_level = RobustnessLevel.MODERATE.value
            elif overall_robustness >= 0.2:
                robustness_level = RobustnessLevel.LOW.value
            else:
                robustness_level = RobustnessLevel.VERY_LOW.value
            
            # Generar recomendaciones
            recommendations = self._generate_robustness_recommendations(
                overall_robustness, outlier_percentage, overall_stability
            )
            
            results = {
                'overall_robustness': float(overall_robustness),
                'robustness_level': robustness_level,
                'stability_score': float(overall_stability),
                'outlier_robustness': float(outlier_robustness),
                'distribution_robustness': float(distribution_robustness),
                'outlier_percentage': float(outlier_percentage),
                'recommendations': recommendations,
                'detailed_analysis': {
                    'stability_metrics': stability_metrics,
                    'outlier_analysis': outlier_info,
                    'distribution_analysis': distribution_analysis
                }
            }
            
            logger.info(f"Análisis de robustez completado: score={overall_robustness:.3f}")
            return results
            
        except Exception as e:
            logger.error(f"Error calculando robustez general: {str(e)}")
            raise
    
    def _generate_robustness_recommendations(self, overall_robustness: float, 
                                          outlier_percentage: float, 
                                          stability_score: float) -> List[str]:
        """
        Genera recomendaciones basadas en análisis de robustez.
        
        Args:
            overall_robustness: Score de robustez general
            outlier_percentage: Porcentaje de outliers
            stability_score: Score de estabilidad
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        if overall_robustness < 0.5:
            recommendations.append("ROBUSTEZ BAJA: Se recomienda revisar la calidad de los datos y métricas.")
        
        if outlier_percentage > 10:
            recommendations.append("OUTLIERS ELEVADOS: Considerar limpieza de datos o ajuste de métricas.")
        
        if stability_score < 0.6:
            recommendations.append("ESTABILIDAD BAJA: Las métricas muestran alta variabilidad. Revisar metodología.")
        
        if overall_robustness >= 0.8:
            recommendations.append("ROBUSTEZ EXCELENTE: Los datos son confiables para análisis avanzado.")
        
        return recommendations

    @property
    def contamination(self):
        # Valor por defecto para compatibilidad con tests
        return getattr(self, '_contamination', 0.05)

    @property
    def safe_len(self):
        return safe_len

    def analyze_robustness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analiza la robustez general de las estrategias.
        
        Args:
            df: DataFrame con métricas de estrategias
            
        Returns:
            Diccionario con análisis de robustez
        """
        try:
            logger.info("Iniciando análisis de robustez...")
            
            # Análisis de estabilidad
            stability_results = self.analyze_stability_metrics(df)
            
            # Detección de outliers
            outlier_results = self.detect_outliers(df)
            
            # Análisis de distribución
            distribution_results = self.analyze_distribution_robustness(df)
            
            # Cálculo de robustez general
            overall_results = self.calculate_overall_robustness(df)
            
            # Combinar resultados
            robustness_results = {
                'score': overall_results.get('overall_robustness', 0.5),
                'stability_score': stability_results.get('overall_stability', 0.5),
                'outlier_percentage': outlier_results.get('outlier_percentage', 0.0),
                'distribution_robustness': distribution_results.get('distribution_robustness', 0.5), # Changed from 'distribution_score' to 'distribution_robustness'
                'recommendations': overall_results.get('recommendations', []),
                'level': overall_results.get('robustness_level', 'moderate')
            }
            
            logger.info(f"Análisis de robustez completado: score={robustness_results['score']:.3f}")
            return robustness_results
            
        except Exception as e:
            logger.error(f"Error en análisis de robustez: {e}")
            return {
                'score': 0.5,
                'stability_score': 0.5,
                'outlier_percentage': 0.0,
                'distribution_robustness': 0.5,
                'recommendations': ['Error en análisis de robustez'],
                'level': 'moderate'
            }

class StressTestGenerator:
    """
    Generador de pruebas de estrés.
    
    Esta clase implementa generación de datos sintéticos para
    probar la robustez de las estrategias bajo condiciones extremas.
    """
    
    def __init__(self, random_state: int = 42):
        """
        Inicializa el generador de pruebas de estrés.
        
        Args:
            random_state: Semilla para reproducibilidad
        """
        self.random_state = random_state
        np.random.seed(random_state)
        
    def generate_synthetic_strategies(self, n_strategies: int = 100) -> pd.DataFrame:
        """
        Genera estrategias sintéticas para pruebas de estrés.
        
        Args:
            n_strategies: Número de estrategias a generar
            
        Returns:
            DataFrame con estrategias sintéticas
        """
        try:
            logger.info(f"Generando {n_strategies} estrategias sintéticas...")
            
            # Generar datos sintéticos realistas
            strategies_data = []
            
            for i in range(n_strategies):
                # Generar métricas con distribución realista
                cagr = np.random.normal(0.15, 0.10)  # CAGR entre -5% y 35%
                sharpe = np.random.normal(1.2, 0.8)   # Sharpe entre -0.4 y 2.8
                drawdown = np.random.normal(-0.15, 0.10)  # Drawdown entre -35% y 5%
                profit_factor = np.random.normal(1.5, 0.5)  # Profit factor entre 0.5 y 2.5
                
                # Asegurar valores realistas
                cagr = max(-0.5, min(0.5, cagr))
                sharpe = max(-1.0, min(3.0, sharpe))
                drawdown = max(-0.5, min(0.0, drawdown))
                profit_factor = max(0.1, min(5.0, profit_factor))
                
                strategy = {
                    'Strategy Name': f'Synthetic_Strategy_{i:03d}',
                    'CAGR': cagr,
                    'Sharpe Ratio': sharpe,
                    'Drawdown': drawdown,
                    'Profit factor': profit_factor,
                    'Total Trades': np.random.randint(50, 500),
                    'Win Rate %': np.random.uniform(0.4, 0.7),
                    'Max Consecutive Losses': np.random.randint(3, 15),
                    'Ulcer Index %': np.random.uniform(0.05, 0.25)
                }
                
                strategies_data.append(strategy)
            
            df = pd.DataFrame(strategies_data)
            
            logger.info(f"Estrategias sintéticas generadas: {len(df)} estrategias")
            return df
            
        except Exception as e:
            logger.error(f"Error generando estrategias sintéticas: {str(e)}")
            raise
    
    def generate_stress_scenarios(self, base_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Genera escenarios de estrés basados en datos reales.
        
        Args:
            base_df: DataFrame base con datos reales
            
        Returns:
            Diccionario con diferentes escenarios de estrés
        """
        try:
            logger.info("Generando escenarios de estrés...")
            
            scenarios = {}
            
            # Escenario 1: Crisis de mercado (drawdowns extremos)
            crisis_df = base_df.copy()
            crisis_df['Drawdown'] = crisis_df['Drawdown'] * 2.0  # Doblar drawdowns
            crisis_df['Sharpe Ratio'] = crisis_df['Sharpe Ratio'] * 0.5  # Reducir Sharpe
            scenarios['crisis_market'] = crisis_df
            
            # Escenario 2: Alta volatilidad (Sharpe reducido)
            volatile_df = base_df.copy()
            volatile_df['Sharpe Ratio'] = volatile_df['Sharpe Ratio'] * 0.7
            volatile_df['CAGR'] = volatile_df['CAGR'] * 0.8
            scenarios['high_volatility'] = volatile_df
            
            # Escenario 3: Mercado lateral (profit factor reducido)
            sideways_df = base_df.copy()
            sideways_df['Profit factor'] = sideways_df['Profit factor'] * 0.6
            sideways_df['CAGR'] = sideways_df['CAGR'] * 0.5
            scenarios['sideways_market'] = sideways_df
            
            # Escenario 4: Outliers extremos
            outlier_df = base_df.copy()
            # Añadir algunos outliers extremos
            outlier_indices = np.random.choice(len(outlier_df), size=5, replace=False)
            outlier_df.loc[outlier_indices, 'CAGR'] = np.random.uniform(-0.8, 1.0, size=5)
            outlier_df.loc[outlier_indices, 'Sharpe Ratio'] = np.random.uniform(-2.0, 4.0, size=5)
            scenarios['extreme_outliers'] = outlier_df
            
            logger.info(f"Escenarios de estrés generados: {len(scenarios)} escenarios")
            return scenarios
            
        except Exception as e:
            logger.error(f"Error generando escenarios de estrés: {str(e)}")
            raise
    
    def test_robustness_under_stress(self, base_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Prueba la robustez bajo condiciones de estrés.
        
        Args:
            base_df: DataFrame base con datos reales
            
        Returns:
            Diccionario con resultados de pruebas de estrés
        """
        try:
            logger.info("Probando robustez bajo condiciones de estrés...")
            
            # Generar escenarios de estrés
            stress_scenarios = self.generate_stress_scenarios(base_df)
            
            # Analizar cada escenario
            stress_results = {}
            
            for scenario_name, scenario_df in stress_scenarios.items():
                # Aplicar análisis de robustez
                robustness_analyzer = RobustnessAnalyzer()
                robustness_result = robustness_analyzer.calculate_overall_robustness(scenario_df)
                
                stress_results[scenario_name] = {
                    'robustness_score': robustness_result['overall_robustness'],
                    'robustness_level': robustness_result['robustness_level'],
                    'stability_score': robustness_result['stability_score'],
                    'outlier_percentage': robustness_result['outlier_percentage']
                }
            
            # Calcular robustez general bajo estrés
            avg_stress_robustness = np.mean([result['robustness_score'] 
                                           for result in stress_results.values()])
            
            # Clasificar resistencia al estrés
            if avg_stress_robustness >= 0.7:
                stress_resistance = "ALTA"
            elif avg_stress_robustness >= 0.5:
                stress_resistance = "MODERADA"
            elif avg_stress_robustness >= 0.3:
                stress_resistance = "BAJA"
            else:
                stress_resistance = "MUY BAJA"
            
            results = {
                'stress_scenarios': stress_results,
                'average_stress_robustness': float(avg_stress_robustness),
                'stress_resistance_level': stress_resistance,
                'scenarios_tested': len(stress_scenarios)
            }
            
            logger.info(f"Pruebas de estrés completadas: resistencia={stress_resistance}")
            return results
            
        except Exception as e:
            logger.error(f"Error en pruebas de estrés: {str(e)}")
            raise

class AdvancedDataProcessor:
    """
    Procesador avanzado de datos.
    
    Esta clase implementa procesamiento avanzado de datos para
    mejorar la calidad y robustez de los análisis.
    """
    
    def __init__(self, chunk_size: int = 10000, max_workers: int = 4):
        """
        Inicializa el procesador avanzado.
        
        Args:
            chunk_size: Tamaño de chunks para procesamiento
            max_workers: Número máximo de workers
        """
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        
    def process_large_dataset(self, df: pd.DataFrame, func, **kwargs) -> pd.DataFrame:
        """
        Procesa datasets grandes en chunks.
        
        Args:
            df: DataFrame a procesar
            func: Función a aplicar
            **kwargs: Argumentos adicionales
            
        Returns:
            DataFrame procesado
        """
        try:
            logger.info(f"Procesando dataset grande en chunks de {self.chunk_size}...")
            
            if len(df) <= self.chunk_size:
                # Dataset pequeño, procesar directamente
                return func(df, **kwargs)
            
            # Procesar en chunks
            chunks = []
            for i in range(0, len(df), self.chunk_size):
                chunk = df.iloc[i:i+self.chunk_size]
                processed_chunk = func(chunk, **kwargs)
                chunks.append(processed_chunk)
            
            # Combinar resultados
            result = pd.concat(chunks, ignore_index=True)
            
            logger.info(f"Procesamiento en chunks completado: {len(result)} filas")
            return result
            
        except Exception as e:
            logger.error(f"Error procesando dataset grande: {str(e)}")
            raise
    
    def optimize_memory_usage(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimiza el uso de memoria del DataFrame.
        
        Args:
            df: DataFrame a optimizar
            
        Returns:
            DataFrame optimizado
        """
        try:
            logger.info("Optimizando uso de memoria...")
            
            optimized_df = df.copy()
            
            # Optimizar tipos de datos
            for col in optimized_df.columns:
                col_type = optimized_df[col].dtype
                
                if col_type == 'object':
                    # Convertir a category si tiene pocos valores únicos
                    if optimized_df[col].nunique() / len(optimized_df) < 0.5:
                        optimized_df[col] = optimized_df[col].astype('category')
                
                elif col_type == 'float64':
                    # Reducir precisión si es posible
                    if optimized_df[col].notna().all().item():
                        optimized_df[col] = optimized_df[col].astype('float32')
                
                elif col_type == 'int64':
                    # Reducir tamaño de enteros si es posible
                    col_min = optimized_df[col].min()
                    col_max = optimized_df[col].max()
                    
                    if col_min >= 0:
                        if col_max < 255:
                            optimized_df[col] = optimized_df[col].astype('uint8')
                        elif col_max < 65535:
                            optimized_df[col] = optimized_df[col].astype('uint16')
                        else:
                            optimized_df[col] = optimized_df[col].astype('uint32')
                    else:
                        if col_min > -128 and col_max < 127:
                            optimized_df[col] = optimized_df[col].astype('int8')
                        elif col_min > -32768 and col_max < 32767:
                            optimized_df[col] = optimized_df[col].astype('int16')
                        else:
                            optimized_df[col] = optimized_df[col].astype('int32')
            
            # Limpiar memoria
            import gc
            gc.collect()
            
            logger.info("Optimización de memoria completada")
            return optimized_df
            
        except Exception as e:
            logger.error(f"Error optimizando memoria: {str(e)}")
            return df
    
    def detect_and_handle_outliers(self, df: pd.DataFrame, method: str = 'isolation_forest') -> pd.DataFrame:
        """
        Detecta y maneja outliers en el DataFrame.
        
        Args:
            df: DataFrame a procesar
            method: Método de detección ('isolation_forest', 'elliptic_envelope', 'iqr')
            
        Returns:
            DataFrame con outliers manejados
        """
        try:
            logger.info(f"Detectando outliers usando método: {method}")
            
            cleaned_df = df.copy()
            numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                data = cleaned_df[col].dropna()
                
                if safe_len(data) < 10:
                    continue
                
                if method == 'iqr':
                    # Método IQR
                    Q1 = data.quantile(0.25)
                    Q3 = data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    # Asegurar que la comparación sea válida
                    outlier_mask = pd.Series(False, index=cleaned_df.index)
                    if not cleaned_df[col].isna().all().item():
                        outlier_mask = (cleaned_df[col] < lower_bound) | (cleaned_df[col] > upper_bound)
                elif method == 'isolation_forest':
                    # Isolation Forest
                    iso_forest = IsolationForest(contamination='auto', random_state=42)
                    data_scaled = StandardScaler().fit_transform(data.values.reshape(-1, 1))
                    outlier_labels = iso_forest.fit_predict(data_scaled)
                    outlier_mask = pd.Series(outlier_labels == -1, index=data.index)
                elif method == 'elliptic_envelope':
                    # Elliptic Envelope
                    scaler = StandardScaler()
                    data_scaled = scaler.fit_transform(data.values.reshape(-1, 1))
                    envelope = EllipticEnvelope(contamination=0.1, random_state=42)
                    outlier_labels = envelope.fit_predict(data_scaled)
                    outlier_mask = pd.Series(outlier_labels == -1, index=data.index)
                else:
                    continue
                # Reemplazar outliers con valores interpolados
                if isinstance(outlier_mask, pd.Series) and outlier_mask.any():
                    cleaned_df.loc[outlier_mask, col] = np.nan
                    cleaned_df[col] = cleaned_df[col].interpolate(method='linear')
            
            logger.info("Manejo de outliers completado")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Error manejando outliers: {str(e)}")
            return df 