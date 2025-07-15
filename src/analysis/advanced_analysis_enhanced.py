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

# Configurar logger
logger = logging.getLogger(__name__)

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

# Importar librerías para reducción de dimensionalidad avanzada
try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False
    logger.warning("UMAP no disponible. Algunas visualizaciones avanzadas no estarán disponibles.")

from sklearn.mixture import GaussianMixture

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
        self.logger = logging.getLogger(__name__)
        
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
                    'Avg. Stagnation Trades': 'Avg_Stagnation',
        'Stagnation (Trades)': 'Stagnation',
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
    
    def regime_analysis(self, n_regimes: int = 3, method: str = "auto") -> AnalysisResult:
        """
        Análisis de regímenes de mercado mejorado con clustering adaptativo y visualización avanzada.
        Args:
            n_regimes: Número inicial de regímenes a detectar (usado solo si method='kmeans')
            method: 'auto', 'kmeans', 'dbscan', 'gmm'. 'auto' selecciona el mejor método y K óptimo.
        Returns:
            AnalysisResult con resultados del análisis de regímenes
        """
        try:
            logger.info(f"🔍 Ejecutando análisis de regímenes (n_regimes: {n_regimes}, method: {method})...")
            regime_features = self._extract_regime_features()
            if len(regime_features) < 2:
                logger.warning("⚠️ Pocas estrategias/características para análisis de regímenes")
                return AnalysisResult(
                    analysis_type=AnalysisType.REGIME_ANALYSIS,
                    data={},
                    metrics={"error": "Insuficientes datos para clustering"},
                    visualizations=[],
                    insights=["No se pudo realizar clustering por falta de datos"],
                    recommendations=["Agregar más estrategias o métricas"]
                )
            # Selección adaptativa de método y K
            if method == "auto":
                best_k, best_score = self._select_optimal_k(regime_features)
                logger.info(f"K óptimo por silhouette: {best_k} (score={best_score:.3f})")
                if best_score > 0.45:
                    method = "kmeans"
                    n_regimes = best_k
                else:
                    method = "dbscan"
            if method == "kmeans":
                clusterer = KMeans(n_clusters=n_regimes, random_state=42)
                regime_labels = clusterer.fit_predict(regime_features)
                silhouette_avg = silhouette_score(regime_features, regime_labels)
                calinski_avg = calinski_harabasz_score(regime_features, regime_labels)
            elif method == "dbscan":
                clusterer = DBSCAN(eps=0.7, min_samples=3)
                regime_labels = clusterer.fit_predict(regime_features)
                silhouette_avg = silhouette_score(regime_features, regime_labels) if len(set(regime_labels)) > 1 else -1
                calinski_avg = calinski_harabasz_score(regime_features, regime_labels) if len(set(regime_labels)) > 1 else -1
            elif method == "gmm":
                clusterer = GaussianMixture(n_components=n_regimes, random_state=42)
                regime_labels = clusterer.fit_predict(regime_features)
                silhouette_avg = silhouette_score(regime_features, regime_labels)
                calinski_avg = calinski_harabasz_score(regime_features, regime_labels)
            else:
                raise ValueError(f"Método de clustering no soportado: {method}")
            regime_characteristics = self._analyze_regime_characteristics(regime_labels, len(set(regime_labels)))
            insights = []
            if silhouette_avg > 0.5:
                insights.append("Los regímenes están bien definidos")
            elif silhouette_avg > 0.3:
                insights.append("Los regímenes son moderadamente distinguibles")
            else:
                insights.append("Los regímenes están poco definidos")
            insights.append(f"Se detectaron {len(set(regime_labels))} regímenes distintos (método: {method})")
            recommendations = [
                "Adaptar estrategias según el régimen de mercado actual",
                "Diversificar entre diferentes regímenes para reducir riesgo"
            ]
            visualizations = []
            if PLOTLY_AVAILABLE:
                # t-SNE/UMAP para visualización avanzada
                tsne_fig = self._plot_tsne_umap(regime_features, regime_labels)
                if tsne_fig:
                    visualizations.append(tsne_fig)
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
                    "n_regimes": len(set(regime_labels)),
                    "method": method
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
    def _select_optimal_k(self, X: pd.DataFrame, k_range: range = range(2, 8)) -> tuple:
        """Selecciona el K óptimo usando silhouette_score."""
        best_k = 2
        best_score = -1
        for k in k_range:
            try:
                labels = KMeans(n_clusters=k, random_state=0).fit_predict(X)
                score = silhouette_score(X, labels)
                if score > best_score:
                    best_k, best_score = k, score
            except Exception as e:
                self.logger.debug(f"Error evaluando K={k} en _select_optimal_k: {e}")
                continue
        return best_k, best_score
    def _plot_tsne_umap(self, X: pd.DataFrame, labels: np.ndarray):
        """Genera visualización t-SNE o UMAP coloreada por régimen."""
        try:
            if UMAP_AVAILABLE:
                reducer = umap.UMAP(n_components=2, random_state=42)
                emb = reducer.fit_transform(X)
                title = "UMAP: visualización de regímenes"
            else:
                emb = TSNE(n_components=2, random_state=42).fit_transform(X)
                title = "t-SNE: visualización de regímenes"
            fig = go.Figure(go.Scatter(
                x=emb[:, 0], y=emb[:, 1],
                mode='markers',
                marker={'size': 8, 'color': labels, 'colorscale': 'Viridis', 'showscale': True},
                name='Embedding'))
            fig.update_layout(title=title, xaxis_title="Componente 1", yaxis_title="Componente 2")
            return fig
        except Exception as e:
            self.logger.warning(f"No se pudo generar visualización t-SNE/UMAP: {e}")
            return None
    
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
    
    def clustering_analysis(self, method: str = "auto", n_clusters: int = 5, 
                           features: Optional[List[str]] = None) -> AnalysisResult:
        """
        Análisis de clustering adaptativo avanzado.
        
        Args:
            method: 'auto', 'kmeans', 'dbscan', 'gmm', 'agglomerative'
            n_clusters: Número de clústers (usado solo para métodos que lo requieren)
            features: Lista de características específicas para clustering
            
        Returns:
            AnalysisResult con resultados del análisis de clustering
        """
        try:
            logger.info(f"🔍 Ejecutando análisis de clustering (method: {method}, n_clusters: {n_clusters})...")
            
            # Preparar características para clustering
            if features:
                clustering_features = self._extract_specific_features(features)
            else:
                clustering_features = self._extract_clustering_features()
            
            if len(clustering_features) < 3:
                logger.warning("⚠️ Pocos datos para clustering confiable")
                return AnalysisResult(
                    analysis_type=AnalysisType.CLUSTERING,
                    data={},
                    metrics={"error": "Insuficientes datos para clustering"},
                    visualizations=[],
                    insights=["Se necesitan más datos para clustering confiable"],
                    recommendations=["Agregar más estrategias o métricas"]
                )
            
            # Normalizar características
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(clustering_features)
            
            # Selección adaptativa de método y parámetros
            if method == "auto":
                best_method, best_params = self._select_optimal_clustering_method(features_scaled)
                logger.info(f"Método óptimo seleccionado: {best_method} con parámetros: {best_params}")
                method = best_method
                if 'n_clusters' in best_params:
                    n_clusters = best_params['n_clusters']
            
            # Aplicar clustering según método seleccionado
            clustering_result = self._apply_clustering_method(features_scaled, method, n_clusters)
            
            if clustering_result is None:
                return AnalysisResult(
                    analysis_type=AnalysisType.CLUSTERING,
                    data={},
                    metrics={"error": "No se pudo aplicar clustering"},
                    visualizations=[],
                    insights=["Error en aplicación de clustering"],
                    recommendations=["Revisar parámetros o datos"]
                )
            
            labels = clustering_result['labels']
            n_clusters_actual = len(set(labels))
            
            # Calcular métricas de calidad
            quality_metrics = self._calculate_clustering_quality(features_scaled, labels)
            
            # Analizar características de cada clúster
            cluster_characteristics = self._analyze_cluster_characteristics(labels, n_clusters_actual)
            
            # Generar insights
            insights = []
            if quality_metrics['silhouette_score'] > 0.5:
                insights.append("Clústers bien definidos y separados")
            elif quality_metrics['silhouette_score'] > 0.3:
                insights.append("Clústers moderadamente distinguibles")
            else:
                insights.append("Clústers poco definidos")
            
            insights.append(f"Se detectaron {n_clusters_actual} clústers distintos")
            insights.append(f"Método utilizado: {method}")
            
            # Generar recomendaciones
            recommendations = [
                "Analizar las características distintivas de cada clúster",
                "Considerar estrategias de diversificación entre clústers",
                "Monitorear cambios en la estructura de clústers"
            ]
            
            # Preparar visualizaciones
            visualizations = []
            if PLOTLY_AVAILABLE:
                # Visualización t-SNE/UMAP
                tsne_fig = self._plot_clustering_visualization(features_scaled, labels, method)
                if tsne_fig:
                    visualizations.append(tsne_fig)
                
                # Gráfico de métricas de calidad
                quality_fig = self._plot_clustering_quality_metrics(quality_metrics)
                if quality_fig:
                    visualizations.append(quality_fig)
            
            return AnalysisResult(
                analysis_type=AnalysisType.CLUSTERING,
                data={
                    'labels': labels,
                    'cluster_characteristics': cluster_characteristics,
                    'features': clustering_features,
                    'method': method,
                    'n_clusters': n_clusters_actual
                },
                metrics={
                    **quality_metrics,
                    'method': method,
                    'n_clusters': n_clusters_actual
                },
                visualizations=visualizations,
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de clustering: {e}")
            return AnalysisResult(
                analysis_type=AnalysisType.CLUSTERING,
                data={},
                metrics={"error": str(e)},
                visualizations=[],
                insights=["Error en análisis de clustering"],
                recommendations=["Revisar datos de entrada"]
            )
    
    def _extract_clustering_features(self) -> pd.DataFrame:
        """Extrae características relevantes para clustering."""
        try:
            # Características balanceadas para clustering
            clustering_columns = [
                'CAGR', 'Sharpe_Ratio', 'Drawdown', 'Profit_Factor',
                'Winrate', 'Sortino_Ratio', 'Calmar_Ratio', 'SQN',
                'Expectancy', 'Payout_Ratio', 'Trades', 'Exposure'
            ]
            
            # Filtrar columnas disponibles
            available_columns = [col for col in clustering_columns if col in self.numeric_columns]
            
            if len(available_columns) < 3:
                logger.warning("⚠️ Pocas características para clustering")
                # Usar todas las columnas numéricas disponibles
                available_columns = self.numeric_columns[:6]  # Limitar a 6 columnas
            
            features_df = self.filtered_strategies[available_columns].copy()
            
            # Crear DataFrame con tipos explícitos
            result_df = pd.DataFrame(features_df.values)
            result_df.columns = available_columns
            result_df.index = features_df.index
            return result_df
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo características de clustering: {e}")
            return pd.DataFrame()
    
    def _extract_specific_features(self, features: List[str]) -> pd.DataFrame:
        """Extrae características específicas para clustering."""
        try:
            # Filtrar características disponibles
            available_features = [f for f in features if f in self.numeric_columns]
            
            if len(available_features) < 2:
                logger.warning("⚠️ Pocas características específicas disponibles")
                return self._extract_clustering_features()
            
            features_df = self.filtered_strategies[available_features].copy()
            
            # Crear DataFrame con tipos explícitos
            result_df = pd.DataFrame(features_df.values)
            result_df.columns = available_features
            result_df.index = features_df.index
            return result_df
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo características específicas: {e}")
            return pd.DataFrame()
    
    def _select_optimal_clustering_method(self, features_scaled: np.ndarray) -> tuple:
        """Selecciona el método de clustering óptimo."""
        try:
            methods_results = {}
            
            # Probar K-means con diferentes K
            for k in range(2, min(8, len(features_scaled) // 2)):
                try:
                    kmeans = KMeans(n_clusters=k, random_state=42)
                    labels = kmeans.fit_predict(features_scaled)
                    silhouette = silhouette_score(features_scaled, labels)
                    methods_results[f'kmeans_k{k}'] = {
                        'method': 'kmeans',
                        'silhouette': silhouette,
                        'params': {'n_clusters': k}
                    }
                except Exception:
                    continue
            
            # Probar DBSCAN con diferentes eps
            for eps in [0.3, 0.5, 0.7, 1.0]:
                try:
                    dbscan = DBSCAN(eps=eps, min_samples=3)
                    labels = dbscan.fit_predict(features_scaled)
                    if len(set(labels)) > 1:
                        silhouette = silhouette_score(features_scaled, labels)
                        methods_results[f'dbscan_eps{eps}'] = {
                            'method': 'dbscan',
                            'silhouette': silhouette,
                            'params': {'eps': eps}
                        }
                except Exception:
                    continue
            
            # Probar GMM con diferentes componentes
            for n_components in range(2, min(6, len(features_scaled) // 2)):
                try:
                    gmm = GaussianMixture(n_components=n_components, random_state=42)
                    labels = gmm.fit_predict(features_scaled)
                    silhouette = silhouette_score(features_scaled, labels)
                    methods_results[f'gmm_n{n_components}'] = {
                        'method': 'gmm',
                        'silhouette': silhouette,
                        'params': {'n_clusters': n_components}
                    }
                except Exception:
                    continue
            
            if not methods_results:
                return 'kmeans', {'n_clusters': 3}
            
            # Seleccionar el mejor método por silhouette score
            best_method_key = max(methods_results.keys(), key=lambda k: methods_results[k]['silhouette'])
            best_result = methods_results[best_method_key]
            
            return best_result['method'], best_result['params']
            
        except Exception as e:
            logger.warning(f"Error en selección de método óptimo: {e}")
            return 'kmeans', {'n_clusters': 3}
    
    def _apply_clustering_method(self, features_scaled: np.ndarray, method: str, n_clusters: int) -> Optional[Dict]:
        """Aplica el método de clustering especificado."""
        try:
            if method == "kmeans":
                clusterer = KMeans(n_clusters=n_clusters, random_state=42)
                labels = clusterer.fit_predict(features_scaled)
                
            elif method == "dbscan":
                clusterer = DBSCAN(eps=0.7, min_samples=3)
                labels = clusterer.fit_predict(features_scaled)
                
            elif method == "gmm":
                clusterer = GaussianMixture(n_components=n_clusters, random_state=42)
                labels = clusterer.fit_predict(features_scaled)
                
            elif method == "agglomerative":
                clusterer = AgglomerativeClustering(n_clusters=n_clusters)
                labels = clusterer.fit_predict(features_scaled)
                
            else:
                raise ValueError(f"Método de clustering no soportado: {method}")
            
            return {
                'labels': labels,
                'method': method,
                'n_clusters': len(set(labels))
            }
            
        except Exception as e:
            logger.error(f"Error aplicando método de clustering {method}: {e}")
            return None
    
    def _calculate_clustering_quality(self, features_scaled: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """Calcula métricas de calidad del clustering."""
        try:
            n_clusters = len(set(labels))
            
            if n_clusters < 2:
                return {
                    'silhouette_score': -1.0,
                    'calinski_harabasz_score': 0.0,
                    'n_clusters': n_clusters
                }
            
            silhouette = silhouette_score(features_scaled, labels)
            calinski = calinski_harabasz_score(features_scaled, labels)
            
            return {
                'silhouette_score': float(silhouette),
                'calinski_harabasz_score': float(calinski),
                'n_clusters': int(n_clusters)
            }
            
        except Exception as e:
            logger.warning(f"Error calculando métricas de calidad: {e}")
            return {
                'silhouette_score': -1.0,
                'calinski_harabasz_score': 0.0,
                'n_clusters': 1
            }
    
    def _analyze_cluster_characteristics(self, labels: np.ndarray, n_clusters: int) -> Dict:
        """Analiza las características de cada clúster."""
        try:
            characteristics = {}
            
            for cluster_id in range(n_clusters):
                cluster_mask = labels == cluster_id
                cluster_strategies = self.filtered_strategies[cluster_mask]
                
                if len(cluster_strategies) == 0:
                    continue
                
                # Calcular estadísticas del clúster
                cluster_stats = {}
                for col in self.numeric_columns:
                    if col in cluster_strategies.columns:
                        cluster_stats[col] = {
                            'mean': float(cluster_strategies[col].mean()),
                            'std': float(cluster_strategies[col].std()),
                            'min': float(cluster_strategies[col].min()),
                            'max': float(cluster_strategies[col].max())
                        }
                
                characteristics[f"cluster_{cluster_id}"] = {
                    'count': int(len(cluster_strategies)),
                    'stats': cluster_stats
                }
            
            return characteristics
            
        except Exception as e:
            logger.error(f"❌ Error analizando características de clústers: {e}")
            return {}
    
    def _plot_clustering_visualization(self, features_scaled: np.ndarray, labels: np.ndarray, method: str):
        """Genera visualización de clustering."""
        try:
            if UMAP_AVAILABLE:
                reducer = umap.UMAP(n_components=2, random_state=42)
                emb = reducer.fit_transform(features_scaled)
                title = f"UMAP: Clustering ({method})"
            else:
                emb = TSNE(n_components=2, random_state=42).fit_transform(features_scaled)
                title = f"t-SNE: Clustering ({method})"
            
            fig = go.Figure()
            
            # Crear scatter plot por clúster
            unique_labels = sorted(set(labels))
            colors = px.colors.qualitative.Set3[:len(unique_labels)]
            
            for i, label in enumerate(unique_labels):
                mask = labels == label
                fig.add_trace(go.Scatter(
                    x=emb[mask, 0],
                    y=emb[mask, 1],
                    mode='markers',
                    name=f'Clúster {label}',
                    marker=dict(color=colors[i], size=8),
                    hovertemplate=f'Clúster {label}<extra></extra>'
                ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Componente 1",
                yaxis_title="Componente 2",
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            logger.warning(f"No se pudo generar visualización de clustering: {e}")
            return None
    
    def _plot_clustering_quality_metrics(self, quality_metrics: Dict[str, float]):
        """Genera gráfico de métricas de calidad del clustering."""
        try:
            metrics_names = ['Silhouette Score', 'Calinski-Harabasz Score']
            metrics_values = [quality_metrics['silhouette_score'], quality_metrics['calinski_harabasz_score']]
            
            fig = go.Figure(data=[
                go.Bar(x=metrics_names, y=metrics_values, name='Métricas de Calidad')
            ])
            
            fig.update_layout(
                title="Métricas de Calidad del Clustering",
                xaxis_title="Métrica",
                yaxis_title="Valor",
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            logger.warning(f"No se pudo generar gráfico de métricas: {e}")
            return None
    
    def correlation_analysis(self, window_size: int = 10, method: str = "dynamic") -> AnalysisResult:
        """
        Análisis de correlaciones dinámicas y estabilidad temporal.
        
        Args:
            window_size: Tamaño de ventana para análisis dinámico
            method: 'dynamic', 'static', 'rolling', 'regime_change'
            
        Returns:
            AnalysisResult con resultados del análisis de correlaciones
        """
        try:
            logger.info(f"🔍 Ejecutando análisis de correlaciones (method: {method}, window_size: {window_size})...")
            
            # Preparar datos para análisis de correlaciones
            correlation_features = self._extract_correlation_features()
            
            if len(correlation_features) < window_size:
                logger.warning(f"⚠️ Pocos datos para análisis dinámico con ventana {window_size}")
                window_size = min(window_size, len(correlation_features))
            
            # Normalizar características
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(correlation_features)
            
            correlation_results = {}
            
            if method == "dynamic":
                # Análisis de correlaciones dinámicas por ventanas
                dynamic_correlations = self._calculate_dynamic_correlations(features_scaled, window_size)
                stability_metrics = self._calculate_correlation_stability(dynamic_correlations)
                
                correlation_results = {
                    'dynamic_correlations': dynamic_correlations,
                    'stability_metrics': stability_metrics,
                    'method': 'dynamic'
                }
                
            elif method == "static":
                # Análisis de correlaciones estáticas
                static_corr_matrix = np.corrcoef(features_scaled.T)
                correlation_results = {
                    'static_correlation_matrix': static_corr_matrix,
                    'method': 'static'
                }
                
            elif method == "rolling":
                # Análisis de correlaciones con ventana móvil
                rolling_correlations = self._calculate_rolling_correlations(features_scaled, window_size)
                correlation_results = {
                    'rolling_correlations': rolling_correlations,
                    'method': 'rolling'
                }
                
            elif method == "regime_change":
                # Detección de cambios de régimen en correlaciones
                regime_changes = self._detect_correlation_regime_changes(features_scaled, window_size)
                correlation_results = {
                    'regime_changes': regime_changes,
                    'method': 'regime_change'
                }
                
            else:
                raise ValueError(f"Método de análisis de correlaciones no soportado: {method}")
            
            # Generar insights
            insights = self._generate_correlation_insights(correlation_results, method)
            
            # Generar recomendaciones
            recommendations = [
                "Monitorear cambios en correlaciones para detectar cambios de régimen",
                "Considerar rebalanceo si las correlaciones cambian significativamente",
                "Analizar la estabilidad de correlaciones para optimizar portafolio"
            ]
            
            # Preparar visualizaciones
            visualizations = []
            if PLOTLY_AVAILABLE:
                corr_fig = self._plot_correlation_analysis(correlation_results, method)
                if corr_fig:
                    visualizations.append(corr_fig)
            
            return AnalysisResult(
                analysis_type=AnalysisType.CORRELATION,
                data=correlation_results,
                metrics={
                    'method': method,
                    'window_size': window_size,
                    'n_features': len(correlation_features.columns)
                },
                visualizations=visualizations,
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de correlaciones: {e}")
            return AnalysisResult(
                analysis_type=AnalysisType.CORRELATION,
                data={},
                metrics={"error": str(e)},
                visualizations=[],
                insights=["Error en análisis de correlaciones"],
                recommendations=["Revisar datos de entrada"]
            )
    
    def _extract_correlation_features(self) -> pd.DataFrame:
        """Extrae características relevantes para análisis de correlaciones."""
        try:
            # Características principales para análisis de correlaciones
            correlation_columns = [
                'CAGR', 'Sharpe_Ratio', 'Drawdown', 'Profit_Factor',
                'Winrate', 'Sortino_Ratio', 'Calmar_Ratio', 'SQN',
                'Expectancy', 'Payout_Ratio', 'Trades', 'Exposure'
            ]
            
            # Filtrar columnas disponibles
            available_columns = [col for col in correlation_columns if col in self.numeric_columns]
            
            if len(available_columns) < 3:
                logger.warning("⚠️ Pocas características para análisis de correlaciones")
                # Usar todas las columnas numéricas disponibles
                available_columns = self.numeric_columns[:8]  # Limitar a 8 columnas
            
            features_df = self.filtered_strategies[available_columns].copy()
            
            # Crear DataFrame con tipos explícitos
            result_df = pd.DataFrame(features_df.values)
            result_df.columns = available_columns
            result_df.index = features_df.index
            return result_df
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo características de correlaciones: {e}")
            return pd.DataFrame()
    
    def _calculate_dynamic_correlations(self, features_scaled: np.ndarray, window_size: int) -> Dict:
        """Calcula correlaciones dinámicas por ventanas."""
        try:
            dynamic_correlations = {}
            
            for i in range(len(features_scaled) - window_size + 1):
                window_data = features_scaled[i:i+window_size]
                corr_matrix = np.corrcoef(window_data.T)
                dynamic_correlations[f"window_{i}"] = corr_matrix
            
            return dynamic_correlations
            
        except Exception as e:
            logger.error(f"❌ Error calculando correlaciones dinámicas: {e}")
            return {}
    
    def _calculate_rolling_correlations(self, features_scaled: np.ndarray, window_size: int) -> Dict:
        """Calcula correlaciones con ventana móvil."""
        try:
            rolling_correlations = {}
            
            for i in range(window_size, len(features_scaled)):
                window_data = features_scaled[i-window_size:i]
                corr_matrix = np.corrcoef(window_data.T)
                rolling_correlations[f"position_{i}"] = corr_matrix
            
            return rolling_correlations
            
        except Exception as e:
            logger.error(f"❌ Error calculando correlaciones móviles: {e}")
            return {}
    
    def _detect_correlation_regime_changes(self, features_scaled: np.ndarray, window_size: int) -> Dict:
        """Detecta cambios de régimen en correlaciones."""
        try:
            regime_changes = {}
            
            # Calcular correlaciones por ventanas
            window_correlations = []
            for i in range(0, len(features_scaled) - window_size + 1, window_size // 2):
                window_data = features_scaled[i:i+window_size]
                corr_matrix = np.corrcoef(window_data.T)
                window_correlations.append(corr_matrix)
            
            # Detectar cambios significativos
            if len(window_correlations) > 1:
                changes = []
                for i in range(1, len(window_correlations)):
                    diff = np.mean(np.abs(window_correlations[i] - window_correlations[i-1]))
                    if diff > 0.1:  # Umbral de cambio
                        changes.append({
                            'position': i * window_size // 2,
                            'change_magnitude': float(diff)
                        })
                
                regime_changes = {
                    'n_changes': len(changes),
                    'changes': changes,
                    'mean_change_magnitude': float(np.mean([c['change_magnitude'] for c in changes])) if changes else 0.0
                }
            
            return regime_changes
            
        except Exception as e:
            logger.error(f"❌ Error detectando cambios de régimen: {e}")
            return {}
    
    def _generate_correlation_insights(self, correlation_results: Dict, method: str) -> List[str]:
        """Genera insights basados en los resultados de correlaciones."""
        insights = []
        
        if method == "dynamic":
            stability_metrics = correlation_results.get('stability_metrics', {})
            if stability_metrics.get('mean_correlation_variance', 0) > 0.1:
                insights.append("Las correlaciones muestran alta variabilidad temporal")
            else:
                insights.append("Las correlaciones son relativamente estables")
                
        elif method == "regime_change":
            regime_changes = correlation_results.get('regime_changes', {})
            n_changes = regime_changes.get('n_changes', 0)
            if n_changes > 0:
                insights.append(f"Se detectaron {n_changes} cambios de régimen en correlaciones")
            else:
                insights.append("No se detectaron cambios significativos de régimen")
        
        insights.append(f"Método de análisis: {method}")
        
        return insights
    
    def _plot_correlation_analysis(self, correlation_results: Dict, method: str):
        """Genera visualización del análisis de correlaciones."""
        try:
            if method == "dynamic":
                return self._plot_dynamic_correlations(correlation_results)
            elif method == "static":
                return self._plot_static_correlations(correlation_results)
            elif method == "rolling":
                return self._plot_rolling_correlations(correlation_results)
            elif method == "regime_change":
                return self._plot_regime_changes(correlation_results)
            else:
                return None
                
        except Exception as e:
            logger.warning(f"No se pudo generar visualización de correlaciones: {e}")
            return None
    
    def _plot_dynamic_correlations(self, correlation_results: Dict):
        """Genera visualización de correlaciones dinámicas."""
        try:
            dynamic_correlations = correlation_results.get('dynamic_correlations', {})
            if not dynamic_correlations:
                return None
            
            # Tomar solo las primeras 5 ventanas para visualización
            sample_windows = list(dynamic_correlations.items())[:5]
            
            fig = go.Figure()
            
            for window_name, corr_matrix in sample_windows:
                fig.add_trace(go.Heatmap(
                    z=corr_matrix,
                    name=window_name,
                    showscale=True
                ))
            
            fig.update_layout(
                title="Correlaciones Dinámicas",
                xaxis_title="Variables",
                yaxis_title="Variables"
            )
            
            return fig
            
        except Exception as e:
            logger.warning(f"No se pudo generar visualización de correlaciones dinámicas: {e}")
            return None
    
    def _plot_static_correlations(self, correlation_results: Dict):
        """Genera visualización de correlaciones estáticas."""
        try:
            static_corr_matrix = correlation_results.get('static_correlation_matrix')
            if static_corr_matrix is None:
                return None
            
            fig = go.Figure(data=go.Heatmap(
                z=static_corr_matrix,
                colorscale='RdBu',
                zmid=0
            ))
            
            fig.update_layout(
                title="Matriz de Correlaciones Estáticas",
                xaxis_title="Variables",
                yaxis_title="Variables"
            )
            
            return fig
            
        except Exception as e:
            logger.warning(f"No se pudo generar visualización de correlaciones estáticas: {e}")
            return None
    
    def _plot_rolling_correlations(self, correlation_results: Dict):
        """Genera visualización de correlaciones móviles."""
        try:
            rolling_correlations = correlation_results.get('rolling_correlations', {})
            if not rolling_correlations:
                return None
            
            # Calcular promedio de correlaciones por posición
            positions = []
            mean_correlations = []
            
            for pos_name, corr_matrix in rolling_correlations.items():
                pos = int(pos_name.split('_')[1])
                positions.append(pos)
                mean_correlations.append(np.mean(corr_matrix))
            
            fig = go.Figure(data=go.Scatter(
                x=positions,
                y=mean_correlations,
                mode='lines+markers',
                name='Correlación Promedio'
            ))
            
            fig.update_layout(
                title="Evolución de Correlaciones Móviles",
                xaxis_title="Posición",
                yaxis_title="Correlación Promedio"
            )
            
            return fig
            
        except Exception as e:
            logger.warning(f"No se pudo generar visualización de correlaciones móviles: {e}")
            return None
    
    def _plot_regime_changes(self, correlation_results: Dict):
        """Genera visualización de cambios de régimen."""
        try:
            regime_changes = correlation_results.get('regime_changes', {})
            changes = regime_changes.get('changes', [])
            
            if not changes:
                return None
            
            positions = [c['position'] for c in changes]
            magnitudes = [c['change_magnitude'] for c in changes]
            
            fig = go.Figure(data=go.Scatter(
                x=positions,
                y=magnitudes,
                mode='markers',
                marker=dict(size=10, color='red'),
                name='Cambios de Régimen'
            ))
            
            fig.update_layout(
                title="Detección de Cambios de Régimen en Correlaciones",
                xaxis_title="Posición",
                yaxis_title="Magnitud del Cambio"
            )
            
            return fig
            
        except Exception as e:
            logger.warning(f"No se pudo generar visualización de cambios de régimen: {e}")
            return None
    
    def anomaly_detection(self, method: str = "ensemble", contamination: float = 0.05) -> AnalysisResult:
        """
        Detección de anomalías multivariadas avanzada.
        
        Args:
            method: 'ensemble', 'isolation_forest', 'lof', 'elliptic_envelope'
            contamination: Fracción esperada de anomalías (0.01-0.1)
            
        Returns:
            AnalysisResult con resultados de detección de anomalías
        """
        try:
            logger.info(f"🔍 Ejecutando detección de anomalías (method: {method}, contamination: {contamination})...")
            
            # Preparar datos para detección de anomalías
            anomaly_features = self._extract_anomaly_features()
            
            if len(anomaly_features) < 10:
                logger.warning("⚠️ Pocos datos para detección de anomalías confiable")
                return AnalysisResult(
                    analysis_type=AnalysisType.ANOMALY_DETECTION,
                    data={},
                    metrics={"error": "Insuficientes datos para detección de anomalías"},
                    visualizations=[],
                    insights=["Se necesitan más datos para detección confiable"],
                    recommendations=["Recopilar más datos de estrategias"]
                )
            
            # Normalizar características para detección de anomalías
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(anomaly_features)
            
            anomaly_results = {}
            
            if method == "ensemble":
                # Ensemble de métodos para mayor robustez
                methods = {
                    'isolation_forest': IsolationForest(contamination=contamination, random_state=42),  # type: ignore
                    'lof': LocalOutlierFactor(contamination=contamination),  # type: ignore
                    'elliptic_envelope': EllipticEnvelope(contamination=contamination, random_state=42)  # type: ignore
                }
                
                ensemble_predictions = {}
                ensemble_scores = {}
                
                for method_name, detector in methods.items():
                    try:
                        if method_name == 'lof':
                            # LOF no tiene predict, solo fit_predict
                            labels = detector.fit_predict(features_scaled)
                            scores = detector.negative_outlier_factor_
                        else:
                            detector.fit(features_scaled)
                            labels = detector.predict(features_scaled)
                            scores = detector.decision_function(features_scaled)
                        
                        ensemble_predictions[method_name] = labels
                        ensemble_scores[method_name] = scores
                        
                        n_anomalies = np.sum(labels == -1)
                        anomaly_percentage = (n_anomalies / len(labels)) * 100
                        
                        anomaly_results[method_name] = {
                            'n_anomalies': int(n_anomalies),
                            'anomaly_percentage': float(anomaly_percentage),
                            'labels': labels,
                            'scores': scores
                        }
                        
                    except Exception as e:
                        logger.warning(f"Error en método {method_name}: {e}")
                        continue
                
                # Votación por mayoría para ensemble
                if len(ensemble_predictions) > 1:
                    votes = np.zeros(len(features_scaled))
                    for labels in ensemble_predictions.values():
                        votes += (labels == -1).astype(int)
                    
                    # Estrategia de votación: si al menos 2 métodos detectan anomalía
                    threshold = max(1, len(ensemble_predictions) // 2)
                    ensemble_labels = (votes >= threshold).astype(int) * 2 - 1  # Convertir a -1/1
                    
                    n_anomalies = np.sum(ensemble_labels == -1)
                    anomaly_percentage = (n_anomalies / len(ensemble_labels)) * 100
                    
                    # Asegurar que 'scores' esté presente aunque sea una lista de ceros
                    ensemble_scores_array = np.zeros(len(ensemble_labels))
                    anomaly_results['ensemble'] = {
                        'n_anomalies': int(n_anomalies),
                        'anomaly_percentage': float(anomaly_percentage),
                        'labels': ensemble_labels,
                        'votes': votes,
                        'scores': ensemble_scores_array
                    }
                
            else:
                # Método individual
                if method == "isolation_forest":
                    detector = IsolationForest(contamination=contamination, random_state=42)  # type: ignore
                elif method == "lof":
                    detector = LocalOutlierFactor(contamination=contamination)  # type: ignore
                elif method == "elliptic_envelope":
                    detector = EllipticEnvelope(contamination=contamination, random_state=42)  # type: ignore
                else:
                    raise ValueError(f"Método de detección no soportado: {method}")
                
                try:
                    if method == "lof":
                        labels = detector.fit_predict(features_scaled)
                        scores = detector.negative_outlier_factor_
                    else:
                        detector.fit(features_scaled)
                        labels = detector.predict(features_scaled)
                        scores = detector.decision_function(features_scaled)
                    
                    n_anomalies = np.sum(labels == -1)
                    anomaly_percentage = (n_anomalies / len(labels)) * 100
                    
                    anomaly_results[method] = {
                        'n_anomalies': int(n_anomalies),
                        'anomaly_percentage': float(anomaly_percentage),
                        'labels': labels,
                        'scores': scores
                    }
                    
                except Exception as e:
                    logger.error(f"Error en detección de anomalías con {method}: {e}")
                    return AnalysisResult(
                        analysis_type=AnalysisType.ANOMALY_DETECTION,
                        data={},
                        metrics={"error": str(e)},
                        visualizations=[],
                        insights=["Error en detección de anomalías"],
                        recommendations=["Revisar parámetros o datos"]
                    )
            
            # Generar insights
            insights = []
            best_method = max(anomaly_results.keys(), key=lambda k: anomaly_results[k]['n_anomalies'])
            best_result = anomaly_results[best_method]
            
            if best_result['anomaly_percentage'] > 10:
                insights.append(f"Alto porcentaje de anomalías detectadas: {best_result['anomaly_percentage']:.1f}%")
            elif best_result['anomaly_percentage'] > 5:
                insights.append(f"Anomalías moderadas detectadas: {best_result['anomaly_percentage']:.1f}%")
            else:
                insights.append(f"Pocas anomalías detectadas: {best_result['anomaly_percentage']:.1f}%")
            
            insights.append(f"Método más efectivo: {best_method}")
            
            # Generar recomendaciones
            recommendations = [
                "Investigar estrategias marcadas como anomalías",
                "Considerar si las anomalías representan oportunidades o riesgos",
                "Monitorear cambios en patrones de anomalías"
            ]
            
            # Preparar visualizaciones
            visualizations = []
            if PLOTLY_AVAILABLE:
                anomaly_fig = self._plot_anomaly_detection(features_scaled, best_result['labels'], best_result['scores'])
                if anomaly_fig:
                    visualizations.append(anomaly_fig)
            
            # Generar insights adicionales
            if not anomaly_results:
                logger.error("No se pudo calcular ninguna métrica de anomalías (todos los métodos fallaron)")
                return AnalysisResult(
                    analysis_type=AnalysisType.ANOMALY_DETECTION,
                    data={},
                    metrics={
                        'best_method': None,
                        'n_anomalies': 0,
                        'anomaly_percentage': 0.0,
                        'total_strategies': len(anomaly_features)
                    },
                    visualizations=[],
                    insights=["No se pudo calcular ninguna métrica de anomalías"],
                    recommendations=["Revisar datos y parámetros"]
                )
            
            return AnalysisResult(
                analysis_type=AnalysisType.ANOMALY_DETECTION,
                data=anomaly_results,
                metrics={
                    'best_method': best_method,
                    'n_anomalies': best_result['n_anomalies'],
                    'anomaly_percentage': best_result['anomaly_percentage'],
                    'total_strategies': len(anomaly_features)
                },
                visualizations=visualizations,
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Error en detección de anomalías: {e}")
            return AnalysisResult(
                analysis_type=AnalysisType.ANOMALY_DETECTION,
                data={},
                metrics={"error": str(e)},
                visualizations=[],
                insights=["Error en detección de anomalías"],
                recommendations=["Revisar datos de entrada"]
            )
    
    def _extract_anomaly_features(self) -> pd.DataFrame:
        """Extrae características relevantes para detección de anomalías."""
        try:
            # Características más sensibles a anomalías
            anomaly_columns = [
                'CAGR', 'Sharpe_Ratio', 'Drawdown', 'Profit_Factor',
                'Winrate', 'Sortino_Ratio', 'Calmar_Ratio', 'SQN',
                'Expectancy', 'Payout_Ratio', 'Ulcer_Index', 'RINA_Index'
            ]
            
            # Filtrar columnas disponibles
            available_columns = [col for col in anomaly_columns if col in self.numeric_columns]
            
            if len(available_columns) < 3:
                logger.warning("⚠️ Pocas características para detección de anomalías")
                # Usar todas las columnas numéricas disponibles
                available_columns = self.numeric_columns[:8]  # Limitar a 8 columnas
            
            features_df = self.filtered_strategies[available_columns].copy()
            
            # Crear DataFrame con tipos explícitos
            result_df = pd.DataFrame(features_df.values)
            result_df.columns = available_columns
            result_df.index = features_df.index
            return result_df
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo características de anomalías: {e}")
            return pd.DataFrame()
    
    def _plot_anomaly_detection(self, features_scaled: np.ndarray, labels: np.ndarray, scores: np.ndarray):
        """Genera visualización de detección de anomalías."""
        try:
            # PCA para visualización 2D
            pca = PCA(n_components=2)
            features_2d = pca.fit_transform(features_scaled)
            
            # Crear figura con scatter plot
            fig = go.Figure()
            
            # Puntos normales
            normal_mask = labels == 1
            if np.any(normal_mask):
                fig.add_trace(go.Scatter(
                    x=features_2d[normal_mask, 0],
                    y=features_2d[normal_mask, 1],
                    mode='markers',
                    name='Normal',
                    marker=dict(color='blue', size=6),
                    hovertemplate='<b>Normal</b><br>Score: %{customdata}<extra></extra>',
                    customdata=scores[normal_mask]
                ))
            
            # Puntos anómalos
            anomaly_mask = labels == -1
            if np.any(anomaly_mask):
                fig.add_trace(go.Scatter(
                    x=features_2d[anomaly_mask, 0],
                    y=features_2d[anomaly_mask, 1],
                    mode='markers',
                    name='Anomalía',
                    marker=dict(color='red', size=10, symbol='x'),
                    hovertemplate='<b>Anomalía</b><br>Score: %{customdata}<extra></extra>',
                    customdata=scores[anomaly_mask]
                ))
            
            fig.update_layout(
                title="Detección de Anomalías Multivariadas",
                xaxis_title="Componente Principal 1",
                yaxis_title="Componente Principal 2",
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            logger.warning(f"No se pudo generar visualización de anomalías: {e}")
            return None
    
    def dimensionality_reduction(self, method: str = "auto", n_components: int = 2, 
                               supervised: bool = False, target_column: Optional[str] = None) -> AnalysisResult:
        """
        Reducción de dimensionalidad interpretativa avanzada.
        
        Args:
            method: 'auto', 'pca', 'umap', 'tsne'
            n_components: Número de componentes a retener
            supervised: Si usar información de etiquetas para UMAP supervisado
            target_column: Columna objetivo para UMAP supervisado
            
        Returns:
            AnalysisResult con resultados de reducción de dimensionalidad
        """
        try:
            logger.info(f"🔍 Ejecutando reducción de dimensionalidad (method: {method}, n_components: {n_components})...")
            
            # Preparar datos para reducción de dimensionalidad
            reduction_features = self._extract_reduction_features()
            
            if len(reduction_features) < 3:
                logger.warning("⚠️ Pocos datos para reducción de dimensionalidad confiable")
                return AnalysisResult(
                    analysis_type=AnalysisType.DIMENSIONALITY_REDUCTION,
                    data={},
                    metrics={"error": "Insuficientes datos para reducción de dimensionalidad"},
                    visualizations=[],
                    insights=["Se necesitan más datos para reducción confiable"],
                    recommendations=["Agregar más estrategias o métricas"]
                )
            
            # Normalizar características
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(reduction_features)
            
            # Selección adaptativa de método
            if method == "auto":
                if len(reduction_features.columns) > 10:
                    method = "pca"  # Para muchas dimensiones, PCA es más eficiente
                else:
                    method = "umap"  # Para pocas dimensiones, UMAP es más expresivo
            
            reduction_results = {}
            
            if method == "pca":
                # PCA con análisis de varianza explicada
                pca_results = self._apply_pca_reduction(features_scaled, n_components)
                reduction_results = pca_results
                
            elif method == "umap":
                # UMAP con opción supervisada
                umap_results = self._apply_umap_reduction(features_scaled, n_components, supervised, target_column)
                reduction_results = umap_results
                
            elif method == "tsne":
                # t-SNE para visualización
                tsne_results = self._apply_tsne_reduction(features_scaled, n_components)
                reduction_results = tsne_results
                
            else:
                raise ValueError(f"Método de reducción de dimensionalidad no soportado: {method}")
            
            # Generar insights
            insights = self._generate_reduction_insights(reduction_results, method)
            
            # Generar recomendaciones
            recommendations = [
                "Usar los componentes principales para análisis de patrones",
                "Considerar la interpretabilidad de los componentes",
                "Monitorear cambios en la estructura de dimensionalidad"
            ]
            
            # Preparar visualizaciones
            visualizations = []
            if PLOTLY_AVAILABLE:
                # Visualización de reducción
                reduction_fig = self._plot_dimensionality_reduction(reduction_results, method)
                if reduction_fig:
                    visualizations.append(reduction_fig)
                
                # Gráfico de varianza explicada (solo para PCA)
                if method == "pca":
                    variance_fig = self._plot_explained_variance(reduction_results)
                    if variance_fig:
                        visualizations.append(variance_fig)
            
            return AnalysisResult(
                analysis_type=AnalysisType.DIMENSIONALITY_REDUCTION,
                data=reduction_results,
                metrics={
                    'method': method,
                    'n_components': (
                        len(reduction_results['components'][0])
                        if (
                            reduction_results['components'] is not None
                            and hasattr(reduction_results['components'], '__getitem__')
                            and len(reduction_results['components']) > 0
                            and reduction_results['components'][0] is not None
                            and hasattr(reduction_results['components'][0], '__len__')
                        )
                        else 0
                    ),
                    'n_original_features': len(reduction_features.columns),
                    'supervised': supervised
                },
                visualizations=visualizations,
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Error en reducción de dimensionalidad: {e}")
            return AnalysisResult(
                analysis_type=AnalysisType.DIMENSIONALITY_REDUCTION,
                data={},
                metrics={"error": str(e)},
                visualizations=[],
                insights=["Error en reducción de dimensionalidad"],
                recommendations=["Revisar datos de entrada"]
            )
    
    def _extract_reduction_features(self) -> pd.DataFrame:
        """Extrae características relevantes para reducción de dimensionalidad."""
        try:
            # Características balanceadas para reducción de dimensionalidad
            reduction_columns = [
                'CAGR', 'Sharpe_Ratio', 'Drawdown', 'Profit_Factor',
                'Winrate', 'Sortino_Ratio', 'Calmar_Ratio', 'SQN',
                'Expectancy', 'Payout_Ratio', 'Trades', 'Exposure',
                'Recovery_Factor', 'Ulcer_Index', 'RINA_Index'
            ]
            
            # Filtrar columnas disponibles
            available_columns = [col for col in reduction_columns if col in self.numeric_columns]
            
            if len(available_columns) < 3:
                logger.warning("⚠️ Pocas características para reducción de dimensionalidad")
                # Usar todas las columnas numéricas disponibles
                available_columns = self.numeric_columns[:10]  # Limitar a 10 columnas
            
            features_df = self.filtered_strategies[available_columns].copy()
            
            # Crear DataFrame con tipos explícitos
            result_df = pd.DataFrame(features_df.values)
            result_df.columns = available_columns
            result_df.index = features_df.index
            return result_df
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo características de reducción: {e}")
            return pd.DataFrame()
    
    def _apply_pca_reduction(self, features_scaled: np.ndarray, n_components: int) -> Dict:
        """Aplica PCA con análisis de varianza explicada."""
        try:
            # Aplicar PCA
            pca = PCA(n_components=min(n_components, features_scaled.shape[1]))
            components = pca.fit_transform(features_scaled)
            
            # Calcular varianza explicada
            explained_variance_ratio = pca.explained_variance_ratio_
            cumulative_variance = np.cumsum(explained_variance_ratio)
            
            # Analizar loadings (contribuciones de variables originales)
            loadings = pca.components_.T
            
            return {
                'components': components,
                'explained_variance_ratio': explained_variance_ratio,
                'cumulative_variance': cumulative_variance,
                'loadings': loadings,
                'n_components': (
                    len(components[0])
                    if (
                        components is not None
                        and hasattr(components, '__getitem__')
                        and len(components) > 0
                        and components[0] is not None
                        and hasattr(components[0], '__len__')
                    )
                    else 0
                ),
                'total_variance_explained': float(np.sum(explained_variance_ratio))
            }
            
        except Exception as e:
            logger.error(f"❌ Error aplicando PCA: {e}")
            return {}
    
    def _apply_umap_reduction(self, features_scaled: np.ndarray, n_components: int, 
                             supervised: bool, target_column: Optional[str]) -> Dict:
        """Aplica UMAP con opción supervisada."""
        try:
            if not UMAP_AVAILABLE:
                logger.warning("UMAP no disponible, usando t-SNE como alternativa")
                return self._apply_tsne_reduction(features_scaled, n_components)
            
            # Preparar etiquetas para UMAP supervisado
            labels = None
            if supervised and target_column and target_column in self.numeric_columns:
                labels = self.filtered_strategies[target_column].values
                # Convertir a etiquetas categóricas si es necesario
                if len(set(labels)) > 10:  # Si hay muchos valores únicos, discretizar
                    labels = pd.cut(labels, bins=5, labels=False)
            
            # Aplicar UMAP
            if supervised and labels is not None:
                reducer = umap.UMAP(n_components=n_components, random_state=42)
                components = reducer.fit_transform(features_scaled, y=labels)
            else:
                reducer = umap.UMAP(n_components=n_components, random_state=42)
                components = reducer.fit_transform(features_scaled)
            
            return {
                'components': components,
                'n_components': (
                    len(components[0])
                    if (
                        components is not None
                        and hasattr(components, '__getitem__')
                        and len(components) > 0
                        and components[0] is not None
                        and hasattr(components[0], '__len__')
                    )
                    else 0
                ),
                'supervised': supervised,
                'method': 'umap'
            }
            
        except Exception as e:
            logger.error(f"❌ Error aplicando UMAP: {e}")
            return {}
    
    def _apply_tsne_reduction(self, features_scaled: np.ndarray, n_components: int) -> Dict:
        """Aplica t-SNE para visualización."""
        try:
            # t-SNE para visualización (solo 2D o 3D)
            n_components = min(n_components, 3)
            
            tsne = TSNE(n_components=n_components, random_state=42)
            components = tsne.fit_transform(features_scaled)
            
            return {
                'components': components,
                'n_components': (
                    len(components[0])
                    if (
                        components is not None
                        and hasattr(components, '__getitem__')
                        and len(components) > 0
                        and components[0] is not None
                        and hasattr(components[0], '__len__')
                    )
                    else 0
                ),
                'method': 'tsne'
            }
            
        except Exception as e:
            logger.error(f"❌ Error aplicando t-SNE: {e}")
            return {}
    
    def _generate_reduction_insights(self, reduction_results: Dict, method: str) -> List[str]:
        """Genera insights basados en los resultados de reducción de dimensionalidad."""
        insights = []
        
        if method == "pca":
            total_variance = reduction_results.get('total_variance_explained', 0)
            n_components = reduction_results.get('n_components', 0)
            
            if total_variance > 0.8:
                insights.append(f"Los primeros {n_components} componentes explican {total_variance:.1%} de la varianza")
            elif total_variance > 0.6:
                insights.append(f"Los primeros {n_components} componentes explican {total_variance:.1%} de la varianza")
            else:
                insights.append(f"Se necesitan más componentes para explicar la varianza ({total_variance:.1%})")
                
        elif method == "umap":
            supervised = reduction_results.get('supervised', False)
            if supervised:
                insights.append("UMAP supervisado aplicado para preservar estructura de etiquetas")
            else:
                insights.append("UMAP no supervisado aplicado para preservar estructura local")
                
        insights.append(f"Método de reducción: {method}")
        
        return insights
    
    def _plot_dimensionality_reduction(self, reduction_results: Dict, method: str):
        """Genera visualización de reducción de dimensionalidad."""
        try:
            components = reduction_results.get('components')
            if components is None or len(components) == 0 or components[0] is None or len(components[0]) < 2:
                return None
            
            if components is not None and len(components) > 0 and components[0] is not None and len(components[0]) == 2:
                # Visualización 2D
                fig = go.Figure(data=go.Scatter(
                    x=components[:, 0],
                    y=components[:, 1],
                    mode='markers',
                    marker=dict(size=8, color='blue'),
                    name='Estrategias'
                ))
                
                fig.update_layout(
                    title=f"Reducción de Dimensionalidad ({method.upper()})",
                    xaxis_title="Componente 1",
                    yaxis_title="Componente 2"
                )
            
            elif components is not None and len(components) > 0 and components[0] is not None and len(components[0]) == 3:
                # Visualización 3D
                fig = go.Figure(data=go.Scatter3d(
                    x=components[:, 0],
                    y=components[:, 1],
                    z=components[:, 2],
                    mode='markers',
                    marker=dict(size=6, color='blue'),
                    name='Estrategias'
                ))
                
                fig.update_layout(
                    title=f"Reducción de Dimensionalidad 3D ({method.upper()})",
                    scene=dict(
                        xaxis_title="Componente 1",
                        yaxis_title="Componente 2",
                        zaxis_title="Componente 3"
                    )
                )
            
            return fig
            
        except Exception as e:
            logger.warning(f"No se pudo generar visualización de reducción: {e}")
            return None
    
    def _plot_explained_variance(self, reduction_results: Dict):
        """Genera gráfico de varianza explicada para PCA."""
        try:
            explained_variance = reduction_results.get('explained_variance_ratio')
            cumulative_variance = reduction_results.get('cumulative_variance')
            
            if explained_variance is None:
                return None
            
            fig = go.Figure()
            
            # Varianza explicada por componente
            fig.add_trace(go.Bar(
                x=list(range(1, len(explained_variance) + 1)),
                y=explained_variance,
                name='Varianza por Componente'
            ))
            
            # Varianza acumulada
            fig.add_trace(go.Scatter(
                x=list(range(1, len(cumulative_variance) + 1)) if cumulative_variance is not None else [],
                y=cumulative_variance if cumulative_variance is not None else [],
                mode='lines+markers',
                name='Varianza Acumulada'
            ))
            
            fig.update_layout(
                title="Análisis de Varianza Explicada (PCA)",
                xaxis_title="Componente",
                yaxis_title="Varianza Explicada",
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            logger.warning(f"No se pudo generar gráfico de varianza explicada: {e}")
            return None


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