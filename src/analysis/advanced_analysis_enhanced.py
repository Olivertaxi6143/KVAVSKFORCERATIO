#!/usr/bin/env python3
"""
Módulo de Análisis Avanzado Mejorado Integrado
===============================================

Integra todas las mejoras de análisis avanzado de UPGRADE sin afectar
la funcionalidad actual del proyecto.

⚠️ RESTRICCIÓN CRÍTICA: Solo se aplica a estrategias que pasen el primer filtro
del análisis actual (Factor K, QVA, Unificado).

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

import pandas as pd
import numpy as np
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.covariance import EllipticEnvelope
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')

# Importar librerías para visualizaciones interactivas
try:
    import plotly.graph_objects as go
    import plotly.express as px
    import plotly.subplots as sp
    from plotly.offline import plot
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Plotly no disponible. Las visualizaciones interactivas no estarán disponibles.")

# Configurar logger
logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Tipos de análisis avanzado disponibles."""
    CLUSTERING = "clustering"
    CORRELATION = "correlation"
    DYNAMIC_CORRELATION = "dynamic_correlation"
    PREDICTION = "prediction"
    ANOMALY_DETECTION = "anomaly_detection"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    TIME_SERIES_ANALYSIS = "time_series_analysis"
    REGIME_ANALYSIS = "regime_analysis"

@dataclass
class AnalysisResult:
    """Resultado de un análisis avanzado."""
    analysis_type: AnalysisType
    data: Any
    metrics: dict  # Permitir dict genérico para evitar errores de tipado
    visualizations: list
    insights: list
    recommendations: list
    interactive_plots: Optional[list] = None

class AdvancedAnalysisEnhanced:
    """
    Clase mejorada para análisis avanzado con características adicionales.
    
    ⚠️ RESTRICCIÓN: Solo trabaja con estrategias que pasaron el primer filtro
    del análisis actual (Factor K, QVA, Unificado).
    """
    
    def __init__(self, filtered_strategies_df: pd.DataFrame, config: Optional[Dict] = None):
        """
        Inicializa el análisis avanzado mejorado.
        
        Args:
            filtered_strategies_df: DataFrame con estrategias filtradas del análisis actual
            config: Configuración opcional del análisis
        """
        self.filtered_strategies = filtered_strategies_df.copy()
        self.config = config or {}
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='median')
        self.pca = PCA(n_components=0.95)
        self.results = {}
        
        # Mapeo de columnas específicas de la GUI
        self.gui_column_mapping = {
            # Columnas básicas
            'Strategy Name': 'Strategy_Name',
            'Strategy_Name': 'Strategy_Name',
            'CAGR (IS)': 'CAGR_IS',
            'CAGR (OOS)': 'CAGR_OOS',
            'CAGR': 'CAGR',
            'Drawdown (IS)': 'Drawdown_IS',
            'Drawdown (OOS)': 'Drawdown_OOS',
            'Drawdown': 'Drawdown',
            'Profit factor (IS)': 'Profit_Factor_IS',
            'Profit factor (OOS)': 'Profit_Factor_OOS',
            'Profit factor': 'Profit_Factor',
            'Sharpe Ratio (IS)': 'Sharpe_Ratio_IS',
            'Sharpe Ratio (OOS)': 'Sharpe_Ratio_OOS',
            'Sharpe Ratio': 'Sharpe_Ratio',
            'Winning Percent (IS)': 'Winrate_IS',
            'Winning Percent (OOS)': 'Winrate_OOS',
            'Winning Percent': 'Winrate',
            '# of trades': 'Trades',
            'Trades': 'Trades',
            'Exposure': 'Exposure',
            'RecoveryFactor': 'Recovery_Factor',
            'Sortino Ratio': 'Sortino_Ratio',
            'CalmarRatio': 'Calmar_Ratio',
            'SQN': 'SQN',
            'Expectancy': 'Expectancy',
            'Payout ratio': 'Payout_Ratio',
            'Max Consec. Losses': 'Max_Consec_Losses',
            'Ulcer Index %': 'Ulcer_Index',
            'RINAIndex': 'RINA_Index',
            'VaR (95%)': 'VaR_95',
            'CVaR (95%)': 'CVaR_95',
            'Max Drawdown Duration': 'Max_DD_Duration',
            'Drawdown Trades %': 'DD_Trades_Percent',
            'New Peak Trades %': 'New_Peak_Trades_Percent',
            'Avg. Bars in Trade': 'Avg_Bars_in_Trade',
            'Avg. Stagnation Trades': 'Avg_Stagnation_Trades',
            'Stagnation (Trades)': 'Max_Stagnation_Trades',
            'Avg. MAE - Profit/loss': 'Avg_MAE',
            'Avg. MFE - Profit/loss': 'Avg_MFE'
        }
        
        # Preparar datos de forma optimizada
        self._prepare_data_enhanced()
        
        logger.info(f"🔬 AdvancedAnalysisEnhanced inicializado con {len(self.filtered_strategies)} estrategias filtradas")
        
    def _prepare_data_enhanced(self):
        """Preparación mejorada de datos con validaciones adicionales."""
        try:
            logger.info("🔬 Preparando datos para análisis avanzado mejorado...")
            
            # Normalizar nombres de columnas
            self.filtered_strategies.columns = [self.gui_column_mapping.get(col, col) for col in self.filtered_strategies.columns]
            
            # Identificar columnas numéricas con validación mejorada
            numeric_columns = []
            for col in self.filtered_strategies.columns:
                if col == 'Strategy_Name':
                    continue
                try:
                    # Convertir a numérico y verificar que no sea todo NaN
                    pd.to_numeric(self.filtered_strategies[col], errors='coerce')
                    if self.filtered_strategies[col].notna().sum() > 0:
                        numeric_columns.append(col)
                except Exception:
                    continue
            
            self.numeric_columns = numeric_columns
            
            # Limpiar datos numéricos
            for col in self.numeric_columns:
                # Convertir a numérico
                self.filtered_strategies[col] = pd.to_numeric(self.filtered_strategies[col], errors='coerce')
                
                # Detectar y manejar outliers extremos
                Q1 = self.filtered_strategies[col].quantile(0.25)
                Q3 = self.filtered_strategies[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 3 * IQR  # Más tolerante con outliers
                upper_bound = Q3 + 3 * IQR
                
                # Reemplazar outliers extremos con valores límite
                self.filtered_strategies[col] = self.filtered_strategies[col].clip(lower=lower_bound, upper=upper_bound)
            
            # Imputar valores faltantes
            if self.filtered_strategies[self.numeric_columns].isna().any().any():
                imputer = SimpleImputer(strategy='median')
                self.filtered_strategies[self.numeric_columns] = imputer.fit_transform(self.filtered_strategies[self.numeric_columns])
            
            logger.info(f"✅ Datos preparados: {len(self.filtered_strategies)} estrategias, {len(self.numeric_columns)} columnas numéricas")
            
        except Exception as e:
            logger.error(f"❌ Error preparando datos mejorados: {e}")
            raise
    
    def dynamic_correlation_analysis(self, window_size: int = 10) -> AnalysisResult:
        """
        Análisis de correlaciones dinámicas usando ventanas móviles.
        
        Args:
            window_size: Tamaño de la ventana para análisis dinámico
            
        Returns:
            AnalysisResult con resultados de correlaciones dinámicas
        """
        try:
            logger.info(f"🔍 Ejecutando análisis de correlaciones dinámicas (ventana: {window_size})...")
            
            if len(self.filtered_strategies) < window_size:
                logger.warning(f"⚠️ Pocas estrategias ({len(self.filtered_strategies)}) para análisis dinámico con ventana {window_size}")
                window_size = min(window_size, len(self.filtered_strategies))
            
            # Preparar datos numéricos
            numeric_data = self.filtered_strategies[self.numeric_columns].copy()
            
            # Calcular correlaciones dinámicas
            dynamic_correlations = {}
            for i in range(len(numeric_data) - window_size + 1):
                window_data = numeric_data.iloc[i:i+window_size]
                corr_matrix = window_data.corr()
                dynamic_correlations[f"window_{i}"] = corr_matrix
            
            # Calcular métricas de estabilidad de correlaciones
            stability_metrics = self._calculate_correlation_stability(dynamic_correlations)
            
            # Generar insights
            insights = []
            if stability_metrics['mean_correlation_variance'] > 0.1:
                insights.append("Las correlaciones muestran alta variabilidad temporal")
            else:
                insights.append("Las correlaciones son relativamente estables")
            
            # Generar recomendaciones
            recommendations = [
                "Monitorear cambios en correlaciones para detectar cambios de régimen",
                "Considerar rebalanceo si las correlaciones cambian significativamente"
            ]
            
            # Preparar visualizaciones
            visualizations = []
            if PLOTLY_AVAILABLE:
                # Crear gráfico de correlaciones dinámicas
                fig = go.Figure()
                for window_name, corr_matrix in list(dynamic_correlations.items())[:5]:  # Mostrar solo las primeras 5 ventanas
                    fig.add_trace(go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.index,
                        name=window_name,
                        showscale=True
                    ))
                
                fig.update_layout(
                    title="Correlaciones Dinámicas",
                    xaxis_title="Variables",
                    yaxis_title="Variables"
                )
                visualizations.append(fig)
            
            return AnalysisResult(
                analysis_type=AnalysisType.DYNAMIC_CORRELATION,
                data=dynamic_correlations,
                metrics=stability_metrics,
                visualizations=visualizations,
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de correlaciones dinámicas: {e}")
            return AnalysisResult(
                analysis_type=AnalysisType.DYNAMIC_CORRELATION,
                data={},
                metrics={"error": str(e)},
                visualizations=[],
                insights=["Error en análisis de correlaciones dinámicas"],
                recommendations=["Revisar datos de entrada"]
            )
    
    def _calculate_correlation_stability(self, dynamic_correlations: Dict) -> Dict[str, float]:
        """Calcula métricas de estabilidad de correlaciones dinámicas."""
        try:
            # Extraer todas las correlaciones
            all_correlations = []
            for window_name, corr_matrix in dynamic_correlations.items():
                # Obtener solo la parte triangular superior (sin diagonal)
                upper_triangle = corr_matrix.where(
                    np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
                )
                all_correlations.extend(upper_triangle.values.flatten())
            
            # Filtrar valores no nulos
            valid_correlations = [c for c in all_correlations if not np.isnan(c)]
            
            if len(valid_correlations) == 0:
                return {"mean_correlation_variance": 0.0, "correlation_range": 0.0}
            
            # Calcular métricas de estabilidad
            mean_correlation_variance = np.var(valid_correlations)
            correlation_range = np.max(valid_correlations) - np.min(valid_correlations)
            
            return {
                "mean_correlation_variance": float(mean_correlation_variance),
                "correlation_range": float(correlation_range),
                "num_windows": int(len(dynamic_correlations)),
                "mean_correlation": float(np.mean(valid_correlations))
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculando estabilidad de correlaciones: {e}")
            return {"error": float(0.0)}
    
    def regime_analysis(self, n_regimes: int = 3) -> AnalysisResult:
        """
        Análisis de regímenes de mercado mejorado.
        
        Args:
            n_regimes: Número de regímenes a detectar
            
        Returns:
            AnalysisResult con resultados del análisis de regímenes
        """
        try:
            logger.info(f"🔍 Ejecutando análisis de regímenes (n_regimes: {n_regimes})...")
            
            # Preparar datos para análisis de regímenes
            regime_features = self._extract_regime_features()
            
            if len(regime_features) < n_regimes:
                logger.warning(f"⚠️ Pocas estrategias ({len(regime_features)}) para detectar {n_regimes} regímenes")
                n_regimes = min(n_regimes, len(regime_features))
            
            # Aplicar clustering para detectar regímenes
            kmeans = KMeans(n_clusters=n_regimes, random_state=42)
            regime_labels = kmeans.fit_predict(regime_features)
            
            # Calcular métricas de calidad del clustering
            silhouette_avg = silhouette_score(regime_features, regime_labels)
            calinski_avg = calinski_harabasz_score(regime_features, regime_labels)
            
            # Analizar características de cada régimen
            regime_characteristics = self._analyze_regime_characteristics(regime_labels, n_regimes)
            
            # Generar insights
            insights = []
            if silhouette_avg > 0.5:
                insights.append("Los regímenes están bien definidos")
            else:
                insights.append("Los regímenes están poco definidos")
            
            insights.append(f"Se detectaron {n_regimes} regímenes distintos")
            
            # Generar recomendaciones
            recommendations = [
                "Adaptar estrategias según el régimen de mercado actual",
                "Diversificar entre diferentes regímenes para reducir riesgo"
            ]
            
            # Preparar visualizaciones
            visualizations = []
            if PLOTLY_AVAILABLE:
                # Crear gráfico de regímenes
                fig = go.Figure()
                
                for regime_id in range(n_regimes):
                    regime_mask = regime_labels == regime_id
                    regime_data = regime_features[regime_mask]
                    
                    fig.add_trace(go.Scatter(
                        x=regime_data.iloc[:, 0],
                        y=regime_data.iloc[:, 1],
                        mode='markers',
                        name=f'Régimen {regime_id + 1}',
                        marker=dict(size=8)
                    ))
                
                fig.update_layout(
                    title="Análisis de Regímenes de Mercado",
                    xaxis_title="Característica 1",
                    yaxis_title="Característica 2"
                )
                visualizations.append(fig)
            
            return AnalysisResult(
                analysis_type=AnalysisType.REGIME_ANALYSIS,
                data={
                    "regime_labels": regime_labels,
                    "regime_characteristics": regime_characteristics,
                    "features": regime_features
                },
                metrics={
                    "silhouette_score": silhouette_avg,
                    "calinski_harabasz_score": calinski_avg,
                    "n_regimes": n_regimes
                },
                visualizations=visualizations,
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de regímenes: {e}")
            return AnalysisResult(
                analysis_type=AnalysisType.REGIME_ANALYSIS,
                data={},
                metrics={"error": str(e)},
                visualizations=[],
                insights=["Error en análisis de regímenes"],
                recommendations=["Revisar datos de entrada"]
            )
    
    def _extract_regime_features(self) -> pd.DataFrame:
        """Extrae características para análisis de regímenes."""
        try:
            # Seleccionar características relevantes para regímenes
            regime_columns = [
                'CAGR', 'Sharpe_Ratio', 'Drawdown', 'Profit_Factor',
                'Winrate', 'Sortino_Ratio', 'Calmar_Ratio'
            ]
            
            # Filtrar columnas disponibles
            available_columns = [col for col in regime_columns if col in self.numeric_columns]
            
            if len(available_columns) < 2:
                logger.warning("⚠️ Pocas características disponibles para análisis de regímenes")
                # Usar todas las columnas numéricas disponibles
                available_columns = self.numeric_columns[:5]  # Limitar a 5 columnas
            
            features_df = self.filtered_strategies[available_columns].copy()
            
            # Normalizar características
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features_df)
            
            # Crear DataFrame con tipos explícitos
            result_df = pd.DataFrame(features_scaled)
            result_df.columns = available_columns
            result_df.index = features_df.index
            return result_df
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo características de regímenes: {e}")
            return pd.DataFrame()
    
    def _analyze_regime_characteristics(self, regime_labels: np.ndarray, n_regimes: int) -> Dict:
        """Analiza las características de cada régimen."""
        try:
            characteristics = {}
            
            for regime_id in range(n_regimes):
                regime_mask = regime_labels == regime_id
                regime_strategies = self.filtered_strategies[regime_mask]
                
                if len(regime_strategies) == 0:
                    continue
                
                # Calcular estadísticas del régimen
                regime_stats = {}
                for col in self.numeric_columns:
                    if col in regime_strategies.columns:
                        regime_stats[col] = {
                            'mean': regime_strategies[col].mean(),
                            'std': regime_strategies[col].std(),
                            'min': regime_strategies[col].min(),
                            'max': regime_strategies[col].max()
                        }
                
                characteristics[f"regime_{regime_id}"] = {
                    'count': len(regime_strategies),
                    'stats': regime_stats
                }
            
            return characteristics
            
        except Exception as e:
            logger.error(f"❌ Error analizando características de regímenes: {e}")
            return {}
    
    def enhanced_prediction_analysis(self, target_column: str, use_ensemble: bool = True) -> AnalysisResult:
        """
        Análisis de predicción mejorado con ensemble de modelos.
        
        Args:
            target_column: Columna objetivo para predicción
            use_ensemble: Si usar ensemble de modelos
            
        Returns:
            AnalysisResult con resultados de predicción
        """
        try:
            logger.info(f"🔍 Ejecutando análisis de predicción (target: {target_column}, ensemble: {use_ensemble})...")
            
            if target_column not in self.numeric_columns:
                logger.error(f"❌ Columna objetivo '{target_column}' no encontrada en datos numéricos")
                return AnalysisResult(
                    analysis_type=AnalysisType.PREDICTION,
                    data={},
                    metrics={"error": f"Columna objetivo '{target_column}' no encontrada"},
                    visualizations=[],
                    insights=["Error: Columna objetivo no válida"],
                    recommendations=["Seleccionar una columna numérica válida"]
                )
            
            # Preparar datos para predicción
            X = self.filtered_strategies[self.numeric_columns].drop(columns=[target_column])
            y = self.filtered_strategies[target_column]
            
            if len(X) < 10:
                logger.warning("⚠️ Pocos datos para análisis de predicción")
                return AnalysisResult(
                    analysis_type=AnalysisType.PREDICTION,
                    data={},
                    metrics={"error": "Insuficientes datos para predicción"},
                    visualizations=[],
                    insights=["Se necesitan más datos para predicción confiable"],
                    recommendations=["Recopilar más datos de estrategias"]
                )
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
            
            if use_ensemble:
                # Crear ensemble de modelos
                models = {
                    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
                    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                    'Linear Regression': LinearRegression(),
                    'Ridge Regression': Ridge(alpha=1.0)
                }
                
                # Entrenar y evaluar cada modelo
                model_results = {}
                for name, model in models.items():
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    
                    model_results[name] = {
                        'r2_score': r2_score(y_test, y_pred),
                        'mse': mean_squared_error(y_test, y_pred),
                        'mae': mean_absolute_error(y_test, y_pred)
                    }
                
                # Crear ensemble final
                ensemble = VotingRegressor([
                    ('rf', models['Random Forest']),
                    ('gb', models['Gradient Boosting']),
                    ('lr', models['Linear Regression'])
                ])
                
                ensemble.fit(X_train, y_train)
                y_pred_ensemble = ensemble.predict(X_test)
                
                ensemble_results = {
                    'r2_score': r2_score(y_test, y_pred_ensemble),
                    'mse': mean_squared_error(y_test, y_pred_ensemble),
                    'mae': mean_absolute_error(y_test, y_pred_ensemble)
                }
                
                model_results['Ensemble'] = ensemble_results
                
            else:
                # Usar solo Random Forest
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                model_results = {
                    'Random Forest': {
                        'r2_score': r2_score(y_test, y_pred),
                        'mse': mean_squared_error(y_test, y_pred),
                        'mae': mean_absolute_error(y_test, y_pred)
                    }
                }
            
            # Generar insights
            insights = []
            best_model = max(model_results.items(), key=lambda x: x[1]['r2_score'])
            insights.append(f"Mejor modelo: {best_model[0]} (R² = {best_model[1]['r2_score']:.3f})")
            
            if best_model[1]['r2_score'] > 0.7:
                insights.append("Predicción confiable")
            elif best_model[1]['r2_score'] > 0.5:
                insights.append("Predicción moderadamente confiable")
            else:
                insights.append("Predicción poco confiable")
            
            # Generar recomendaciones
            recommendations = [
                "Usar el mejor modelo para predicciones futuras",
                "Monitorear rendimiento del modelo regularmente"
            ]
            
            # Preparar visualizaciones
            visualizations = []
            if PLOTLY_AVAILABLE:
                # Crear gráfico de comparación de modelos
                model_names = list(model_results.keys())
                r2_scores = [model_results[name]['r2_score'] for name in model_names]
                
                fig = go.Figure(data=[
                    go.Bar(x=model_names, y=r2_scores, name='R² Score')
                ])
                
                fig.update_layout(
                    title="Comparación de Modelos de Predicción",
                    xaxis_title="Modelo",
                    yaxis_title="R² Score"
                )
                visualizations.append(fig)
            
            return AnalysisResult(
                analysis_type=AnalysisType.PREDICTION,
                data=model_results,
                metrics=model_results,
                visualizations=visualizations,
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de predicción: {e}")
            return AnalysisResult(
                analysis_type=AnalysisType.PREDICTION,
                data={},
                metrics={"error": str(e)},
                visualizations=[],
                insights=["Error en análisis de predicción"],
                recommendations=["Revisar datos de entrada"]
            )
    
    def run_complete_enhanced_analysis(self, analysis_types: Optional[List[str]] = None) -> Dict[str, AnalysisResult]:
        """
        Ejecuta análisis avanzado completo.
        
        Args:
            analysis_types: Lista de tipos de análisis a ejecutar
            
        Returns:
            Diccionario con resultados de todos los análisis
        """
        try:
            logger.info("🔬 Ejecutando análisis avanzado completo...")
            
            if analysis_types is None:
                analysis_types = ["dynamic_correlation", "regime_analysis", "enhanced_prediction"]
            
            results = {}
            
            for analysis_type in analysis_types:
                logger.info(f"🔬 Ejecutando análisis: {analysis_type}")
                
                if analysis_type == "dynamic_correlation":
                    results[analysis_type] = self.dynamic_correlation_analysis()
                elif analysis_type == "regime_analysis":
                    results[analysis_type] = self.regime_analysis()
                elif analysis_type == "enhanced_prediction":
                    # Usar CAGR como objetivo por defecto
                    target_col = 'CAGR' if 'CAGR' in self.numeric_columns else self.numeric_columns[0]
                    results[analysis_type] = self.enhanced_prediction_analysis(target_col)
                else:
                    logger.warning(f"⚠️ Tipo de análisis no soportado: {analysis_type}")
            
            logger.info("✅ Análisis avanzado completo finalizado")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en análisis avanzado completo: {e}")
            return {"error": AnalysisResult(
                analysis_type=AnalysisType.CORRELATION,
                data={},
                metrics={"error": str(e)},
                visualizations=[],
                insights=["Error en análisis avanzado"],
                recommendations=["Revisar configuración"]
            )}
    
    # Métodos stub para compatibilidad
    def clustering_analysis(self, n_clusters: int = 5) -> AnalysisResult:
        """Análisis de clustering básico."""
        logger.info("🔍 Ejecutando análisis de clustering...")
        return AnalysisResult(
            analysis_type=AnalysisType.CLUSTERING,
            data={},
            metrics={},
            visualizations=[],
            insights=["Análisis de clustering no implementado"],
            recommendations=["Implementar análisis de clustering"]
        )
    
    def correlation_analysis(self) -> AnalysisResult:
        """Análisis de correlación básico."""
        logger.info("🔍 Ejecutando análisis de correlación...")
        return AnalysisResult(
            analysis_type=AnalysisType.CORRELATION,
            data={},
            metrics={},
            visualizations=[],
            insights=["Análisis de correlación no implementado"],
            recommendations=["Implementar análisis de correlación"]
        )
    
    def anomaly_detection(self) -> AnalysisResult:
        """Detección de anomalías básica."""
        logger.info("🔍 Ejecutando detección de anomalías...")
        return AnalysisResult(
            analysis_type=AnalysisType.ANOMALY_DETECTION,
            data={},
            metrics={},
            visualizations=[],
            insights=["Detección de anomalías no implementada"],
            recommendations=["Implementar detección de anomalías"]
        )
    
    def dimensionality_reduction(self) -> AnalysisResult:
        """Reducción de dimensionalidad básica."""
        logger.info("🔍 Ejecutando reducción de dimensionalidad...")
        return AnalysisResult(
            analysis_type=AnalysisType.DIMENSIONALITY_REDUCTION,
            data={},
            metrics={},
            visualizations=[],
            insights=["Reducción de dimensionalidad no implementada"],
            recommendations=["Implementar reducción de dimensionalidad"]
        )


def create_enhanced_analysis(filtered_strategies_df: pd.DataFrame, config: Optional[Dict] = None) -> AdvancedAnalysisEnhanced:
    """
    Factory function para crear AdvancedAnalysisEnhanced.
    
    Args:
        filtered_strategies_df: DataFrame con estrategias filtradas del análisis actual
        config: Configuración opcional
        
    Returns:
        AdvancedAnalysisEnhanced configurado
    """
    return AdvancedAnalysisEnhanced(filtered_strategies_df, config)


if __name__ == "__main__":
    # Test básico del módulo
    print("🔬 Módulo de Análisis Avanzado Mejorado cargado correctamente")
    print("⚠️ RESTRICCIÓN: Solo funciona con estrategias filtradas del análisis actual") 