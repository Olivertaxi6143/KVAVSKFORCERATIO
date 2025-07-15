from typing import Optional, Any, Union
#!/usr/bin/env python3
"""
Módulo de Machine Learning Avanzado para Validación de Estrategias
==================================================================

Implementa funcionalidades avanzadas de ML para:
- Detección robusta de regímenes de mercado
- Detección de data drift con múltiples métodos
- Validación walk-forward temporal avanzada
- Análisis de estabilidad temporal
- Predicción de rendimiento con validación robusta

Basado en metodologías de ML para finanzas cuantitativas.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from getattr(sklearn, 'model', None)_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import warnings
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

# Configurar warnings
warnings.filterwarnings("ignore")

# Configurar logging
logger = logging.getLogger(__name__)


@dataclass
class RegimeDetectionResult:
    """Resultado de detección de regímenes."""
    regime_labels: np.ndarray
    regime_centers: np.ndarray
    regime_characteristics: Dict[str, Any]
    quality_metrics: Dict[str, float]
    feature_importance: Dict[str, float]


@dataclass
class DataDriftResult:
    """Resultado de detección de data drift."""
    drift_scores: Dict[str, float]
    overall_drift: float
    drift_detected: bool
    affected_features: List[str]
    confidence_level: float


@dataclass
class WalkForwardResult:
    """Resultado de validación walk-forward."""
    fold_results: List[Dict[str, Any]]
    overall_metrics: Dict[str, float]
    stability_score: float
    degradation_score: float
    predictability_score: float


@dataclass
class TemporalValidationResult:
    """Resultado de validación temporal avanzada."""
    fold_results: List[Dict[str, Any]]
    overall_metrics: Dict[str, float]
    stability_analysis: Dict[str, float]
    degradation_analysis: Dict[str, float]
    robustness_score: float
    temporal_consistency: float


@dataclass
class WalkForwardConfig:
    """Configuración para walk-forward validation."""
    n_splits: int = 5
    test_size: float = 0.2
    min_train_size: int = 30
    target_column: str = "Unified_Score"
    feature_columns: Optional[List[str]] = None
    model_type: str = "random_forest"


class AdvancedMLValidator:
    """
    Validador avanzado de ML para estrategias de trading.
    
    Funcionalidades principales:
    - Detección robusta de regímenes de mercado
    - Detección de data drift con múltiples métodos
    - Validación walk-forward temporal avanzada
    - Análisis de estabilidad temporal
    """
    
    def __init__(self, 
                 n_regimes: int = 3,
                 drift_threshold: float = 0.1,
                 walk_forward_folds: int = 5,
                 config: Optional[WalkForwardConfig] = None,
                 model: Optional[Any] = None):
        """
        Inicializa el validador ML avanzado.
        
        Args:
            n_regimes: Número de regímenes de mercado a detectar
            drift_threshold: Umbral para detección de data drift
            walk_forward_folds: Número de folds para walk-forward validation
            config: Configuración para walk-forward validation
            model: Modelo ML a usar (opcional)
        """
        self.n_regimes = n_regimes
        self.drift_threshold = drift_threshold
        self.walk_forward_folds = walk_forward_folds
        getattr(self, 'config', None) = config or WalkForwardConfig()
        getattr(self, 'model', None) = model
        self.logger = logging.getLogger(__name__)
        
        # Inicializar modelos
        self._initialize_models()
        
        self.logger.info(f"🔬 AdvancedMLValidator inicializado con {n_regimes} regímenes")
    
    def _initialize_models(self):
        """Inicializa los modelos de ML."""
        # Modelo de clustering para regímenes
        self.regime_model = KMeans(
            n_clusters=self.n_regimes, 
            random_state=42, 
            n_init='auto'
        )
        
        # Modelo de detección de anomalías para drift
        self.drift_detector = IsolationForest(
            contamination="auto",
            random_state=42
        )
        
        # Modelo de predicción para walk-forward
        self.prediction_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
    
    def detect_market_regimes(self, 
                            data: pd.DataFrame,
                            feature_columns: Optional[List[str]] = None) -> RegimeDetectionResult:
        """
        Detecta regímenes de mercado usando clustering avanzado.
        
        Args:
            data: DataFrame con datos de estrategias
            feature_columns: Columnas a usar para clustering
            
        Returns:
            RegimeDetectionResult con resultados de detección
        """
        try:
            self.logger.info("🔍 Detectando regímenes de mercado...")
            
            # Seleccionar características
            if feature_columns is None:
                feature_columns = self._select_regime_features(data)
            
            if len(feature_columns) < 2:
                self.logger.warning("⚠️ Insuficientes características para clustering")
                return self._create_empty_regime_result()
            
            # Preparar datos
            X = data[feature_columns].copy()
            if isinstance(X, pd.Series):
                X = X.to_frame()
            X = self._preprocess_features(X)
            
            # Aplicar clustering
            regime_labels = self.regime_model.fit_predict(X)
            regime_centers = self.regime_model.cluster_centers_
            
            # Calcular métricas de calidad
            quality_metrics = self._calculate_clustering_quality(X, regime_labels)
            
            # Analizar características de regímenes
            regime_characteristics = self._analyze_regime_characteristics(
                data, regime_labels, feature_columns
            )
            
            # Calcular importancia de características
            feature_importance = self._calculate_feature_importance(X, regime_labels)
            
            result = RegimeDetectionResult(
                regime_labels=regime_labels,
                regime_centers=regime_centers,
                regime_characteristics=regime_characteristics,
                quality_metrics=quality_metrics,
                feature_importance=feature_importance
            )
            
            self.logger.info(f"✅ Regímenes detectados: {self.n_regimes} clusters")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error detectando regímenes: {e}")
            return self._create_empty_regime_result()
    
    def detect_data_drift(self,
                         reference_data: pd.DataFrame,
                         current_data: pd.DataFrame,
                         feature_columns: Optional[List[str]] = None) -> DataDriftResult:
        """
        Detecta data drift usando múltiples métodos.
        
        Args:
            reference_data: Datos de referencia
            current_data: Datos actuales
            feature_columns: Columnas a analizar
            
        Returns:
            DataDriftResult con resultados de detección
        """
        try:
            self.logger.info("🔍 Detectando data drift...")
            
            # Seleccionar características
            if feature_columns is None:
                feature_columns = self._select_drift_features(reference_data)
            
            # Método 1: Comparación estadística
            statistical_drift = self._detect_statistical_drift(
                reference_data, current_data, feature_columns
            )
            
            # Método 2: Detección de anomalías
            anomaly_drift = self._detect_anomaly_drift(
                reference_data, current_data, feature_columns
            )
            
            # Método 3: Análisis de distribución
            distribution_drift = self._detect_distribution_drift(
                reference_data, current_data, feature_columns
            )
            
            # Combinar resultados
            drift_scores = {}
            for col in feature_columns:
                scores = []
                if col in statistical_drift:
                    scores.append(statistical_drift[col])
                if col in anomaly_drift:
                    scores.append(anomaly_drift[col])
                if col in distribution_drift:
                    scores.append(distribution_drift[col])
                
                if scores:
                    drift_scores[col] = np.mean(scores)
            
            overall_drift = np.mean(list(drift_scores.values())) if drift_scores else 0.0
            drift_detected = overall_drift > self.drift_threshold
            
            # Identificar características más afectadas
            affected_features = [
                col for col, score in drift_scores.items() 
                if score > self.drift_threshold
            ]
            
            # Calcular nivel de confianza
            confidence_level = self._calculate_drift_confidence(drift_scores)
            
            result = DataDriftResult(
                drift_scores=drift_scores,
                overall_drift=float(overall_drift) if overall_drift is not None else 0.0 if overall_drift is not None else 0.0,
                drift_detected=bool(drift_detected),
                affected_features=affected_features,
                confidence_level=float(confidence_level) if confidence_level is not None else 0.0 if confidence_level is not None else 0.0
            )
            
            self.logger.info(f"✅ Data drift detectado: {drift_detected}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error detectando data drift: {e}")
            return self._create_empty_drift_result()
    
    def perform_walk_forward_validation(self,
                                      data: pd.DataFrame,
                                      target_column: str,
                                      feature_columns: Optional[List[str]] = None) -> WalkForwardResult:
        """
        Realiza validación walk-forward temporal avanzada.
        
        Args:
            data: DataFrame con datos
            target_column: Columna objetivo
            feature_columns: Columnas de características
            
        Returns:
            WalkForwardResult con resultados de validación
        """
        try:
            self.logger.info("🔍 Ejecutando validación walk-forward...")
            
            # Seleccionar características
            if feature_columns is None:
                feature_columns = self._select_walk_forward_features(data, target_column)
            
            # Preparar datos
            X = data[feature_columns].copy()
            y = data[target_column]
            
            # Limpiar datos
            if isinstance(X, pd.Series):
                X = X.to_frame()
            if isinstance(y, pd.DataFrame):
                y = y.iloc[:, 0]  # Tomar la primera columna si es DataFrame
            X, y = self._clean_walk_forward_data(X, y)
            
            if len(X) < 10:
                self.logger.warning("⚠️ Pocos datos para walk-forward")
                return self._create_empty_walk_forward_result()
            
            # Configurar TimeSeriesSplit
            tscv = TimeSeriesSplit(n_splits=self.walk_forward_folds)
            
            fold_results = []
            predictions = []
            actuals = []
            
            # Realizar validación por folds
            for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                
                # Entrenar modelo
                self.prediction_model.fit(X_train, y_train)
                
                # Predecir
                y_pred = self.prediction_model.predict(X_test)
                
                # Calcular métricas
                fold_metrics = self._calculate_fold_metrics(y_test, y_pred)
                
                fold_result = {
                    'fold': fold + 1,
                    'train_size': len(X_train),
                    'test_size': len(X_test),
                    'metrics': fold_metrics,
                    'predictions': ((y_pred.tolist() if hasattr(y_pred, 'tolist') else list(y_pred)) if hasattr(y_pred, 'tolist') else list(y_pred)),
                    'actuals': ((y_test.tolist() if hasattr(y_test, 'tolist') else list(y_test)) if hasattr(y_test, 'tolist') else list(y_test))
                }
                
                fold_results.append(fold_result)
                predictions.extend(y_pred)
                actuals.extend(y_test)
            
            # Calcular métricas generales
            overall_metrics = self._calculate_overall_metrics(fold_results)
            stability_score = self._calculate_stability_score(fold_results)
            degradation_score = self._calculate_degradation_score(fold_results)
            predictability_score = self._calculate_predictability_score(predictions, actuals)
            
            result = WalkForwardResult(
                fold_results=fold_results,
                overall_metrics=overall_metrics,
                stability_score=stability_score,
                degradation_score=degradation_score,
                predictability_score=predictability_score
            )
            
            self.logger.info("✅ Validación walk-forward completada")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error en walk-forward: {e}")
            return self._create_empty_walk_forward_result()
    
    def _select_regime_features(self, data: pd.DataFrame) -> List[str]:
        """Selecciona características para detección de regímenes."""
        regime_features = [
            'Sharpe_Ratio', 'Max_DD_%', 'CAGR', 'Profit_factor',
            'Win_Rate_%', 'Total_Trades', 'Avg_Trade_%'
        ]
        
        available_features = [f for f in regime_features if f in data.columns]
        
        if len(available_features) < 2:
            # Usar columnas numéricas como fallback
            numeric_cols = data.select_dtypes(include=[np.number]).((columns.tolist() if hasattr(columns, 'tolist') else list(columns)) if hasattr(columns, 'tolist') else list(columns))
            available_features = numeric_cols[:5]  # Top 5 columnas numéricas
        
        return available_features
    
    def _select_drift_features(self, data: pd.DataFrame) -> List[str]:
        """Selecciona características para detección de drift."""
        drift_features = [
            'Profit_factor', 'Sharpe_Ratio', 'Max_DD_%',
            'Win_Rate_%', 'Total_Trades'
        ]
        
        available_features = [f for f in drift_features if f in data.columns]
        
        if len(available_features) < 2:
            numeric_cols = data.select_dtypes(include=[np.number]).((columns.tolist() if hasattr(columns, 'tolist') else list(columns)) if hasattr(columns, 'tolist') else list(columns))
            available_features = numeric_cols[:3]
        
        return available_features
    
    def _select_walk_forward_features(self, data: pd.DataFrame, target_column: str) -> List[str]:
        """Selecciona características para walk-forward."""
        # Excluir la columna objetivo y columnas no numéricas
        numeric_cols = data.select_dtypes(include=[np.number]).((columns.tolist() if hasattr(columns, 'tolist') else list(columns)) if hasattr(columns, 'tolist') else list(columns))
        
        if target_column in numeric_cols:
            numeric_cols.remove(target_column)
        
        # Priorizar características relevantes
        priority_features = [
            'Profit_factor', 'Sharpe_Ratio', 'Max_DD_%',
            'Win_Rate_%', 'Total_Trades', 'CAGR'
        ]
        
        selected_features = []
        for feature in priority_features:
            if feature in numeric_cols:
                selected_features.append(feature)
                numeric_cols.remove(feature)
        
        # Agregar otras características numéricas
        selected_features.extend(numeric_cols[:5])
        
        return selected_features[:10]  # Máximo 10 características
    
    def _preprocess_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Preprocesa características para clustering."""
        # Limpiar datos
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median())
        
        # Normalizar
        scaler = RobustScaler()
        X_scaled = scaler.fit_transform(X)
        
        return pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
    
    def _calculate_clustering_quality(self, X: pd.DataFrame, labels: np.ndarray) -> Dict[str, float]:
        """Calcula métricas de calidad del clustering."""
        try:
            silhouette_avg = silhouette_score(X, labels)
            calinski_avg = calinski_harabasz_score(X, labels)
            
            return {
                'silhouette_score': silhouette_avg,
                'calinski_harabasz_score': calinski_avg,
                'n_clusters': len(np.unique(labels))
            }
        except Exception as e:
            self.logger.warning(f"Error calculando calidad de clustering: {e}")
            return {'silhouette_score': 0.0, 'calinski_harabasz_score': 0.0, 'n_clusters': 0}
    
    def _analyze_regime_characteristics(self, 
                                      data: pd.DataFrame, 
                                      labels: np.ndarray,
                                      feature_columns: List[str]) -> Dict[str, Any]:
        """Analiza características de cada régimen."""
        characteristics = {}
        
        for regime in range(self.n_regimes):
            regime_mask = labels == regime
            regime_data = data[regime_mask]
            
            if len(regime_data) > 0:
                regime_stats = {}
                for col in feature_columns:
                    if col in regime_data.columns:
                        regime_stats[col] = {
                            'mean': float(regime_data[col].mean()),
                            'std': float(regime_data[col].std()),
                            'count': int(len(regime_data))
                        }
                
                characteristics[f'regime_{regime}'] = regime_stats
        
        return characteristics
    
    def _calculate_feature_importance(self, X: pd.DataFrame, labels: np.ndarray) -> Dict[str, float]:
        """Calcula importancia de características para clustering."""
        try:
            # Usar Random Forest para estimar importancia
            rf = RandomForestRegressor(n_estimators=50, random_state=42)
            rf.fit(X, labels)
            
            importance = dict(zip(X.columns, rf.feature_importances_))
            return importance
        except Exception as e:
            self.logger.warning(f"Error calculando importancia: {e}")
            return {col: 1.0/len(X.columns) for col in X.columns}
    
    def _detect_statistical_drift(self, 
                                 reference_data: pd.DataFrame,
                                 current_data: pd.DataFrame,
                                 feature_columns: List[str]) -> Dict[str, float]:
        """Detecta drift usando comparación estadística."""
        drift_scores = {}
        
        for col in feature_columns:
            if col in reference_data.columns and col in current_data.columns:
                ref_mean = reference_data[col].mean()
                curr_mean = current_data[col].mean()
                ref_std = reference_data[col].std()
                
                if ref_std > 0:
                    drift_score = abs(curr_mean - ref_mean) / ref_std
                    drift_scores[col] = drift_score
        
        return drift_scores
    
    def _detect_anomaly_drift(self,
                             reference_data: pd.DataFrame,
                             current_data: pd.DataFrame,
                             feature_columns: List[str]) -> Dict[str, float]:
        """Detecta drift usando detección de anomalías."""
        drift_scores = {}
        
        try:
            # Entrenar detector de anomalías en datos de referencia
            ref_features = reference_data[feature_columns].fillna(0)
            self.drift_detector.fit(ref_features)
            
            # Detectar anomalías en datos actuales
            curr_features = current_data[feature_columns].fillna(0)
            anomaly_scores = self.drift_detector.decision_function(curr_features)
            
            # Calcular score de drift por característica
            for i, col in enumerate(feature_columns):
                if col in curr_features.columns:
                    drift_scores[col] = float(np.mean(anomaly_scores))
        
        except Exception as e:
            self.logger.warning(f"Error en detección de anomalías: {e}")
        
        return drift_scores
    
    def _detect_distribution_drift(self,
                                 reference_data: pd.DataFrame,
                                 current_data: pd.DataFrame,
                                 feature_columns: List[str]) -> Dict[str, float]:
        """Detecta drift usando análisis de distribución."""
        drift_scores = {}
        
        for col in feature_columns:
            if col in reference_data.columns and col in current_data.columns:
                ref_data = reference_data[col].dropna()
                curr_data = current_data[col].dropna()
                
                if len(ref_data) > 0 and len(curr_data) > 0:
                    # Calcular diferencia en percentiles
                    ref_percentiles = np.percentile(ref_data, [25, 50, 75])
                    curr_percentiles = np.percentile(curr_data, [25, 50, 75])
                    
                    drift_score = np.mean(np.abs(curr_percentiles - ref_percentiles))
                    drift_scores[col] = float(drift_score) if drift_score is not None else 0.0 if drift_score is not None else 0.0
        
        return drift_scores
    
    def _calculate_drift_confidence(self, drift_scores: Dict[str, float]) -> float:
        """Calcula nivel de confianza en la detección de drift."""
        if not drift_scores:
            return 0.0
        
        # Basado en la consistencia de los scores
        scores = list(drift_scores.values())
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        if std_score == 0:
            confidence = 1.0 if mean_score > self.drift_threshold else 0.0
        else:
            # Normalizar y calcular confianza
            normalized_scores = [(s - mean_score) / std_score for s in scores]
            confidence = 1.0 - np.mean([abs(s) for s in normalized_scores])
        
        return max(0.0, min(1.0, float(confidence) if confidence is not None else 0.0 if confidence is not None else 0.0))
    
    def _clean_walk_forward_data(self, X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
        """Limpia datos para walk-forward."""
        # Limpiar X
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median())
        
        # Limpiar y
        y = y.replace([np.inf, -np.inf], np.nan)
        y = y.dropna()
        
        # Alinear índices
        common_index = X.index.intersection(y.index)
        X = X.loc[common_index]
        y = y.loc[common_index]
        
        return X, y
    
    def _calculate_fold_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """Calcula métricas para un fold."""
        try:
            from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
            
            r2 = r2_score(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mae = mean_absolute_error(y_true, y_pred)
            
            return {
                'r2_score': float(r2) if r2 is not None else 0.0 if r2 is not None else 0.0,
                'rmse': float(rmse) if rmse is not None else 0.0 if rmse is not None else 0.0,
                'mae': float(mae) if mae is not None else 0.0 if mae is not None else 0.0
            }
        except Exception as e:
            self.logger.warning(f"Error calculando métricas de fold: {e}")
            return {'r2_score': 0.0, 'rmse': 0.0, 'mae': 0.0}
    
    def _calculate_overall_metrics(self, fold_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcula métricas generales de walk-forward."""
        if not fold_results:
            return {}
        
        r2_scores = [fold['metrics']['r2_score'] for fold in fold_results]
        rmse_scores = [fold['metrics']['rmse'] for fold in fold_results]
        
        return {
            'mean_r2': float(np.mean(r2_scores)),
            'std_r2': float(np.std(r2_scores)),
            'mean_rmse': float(np.mean(rmse_scores)),
            'std_rmse': float(np.std(rmse_scores))
        }
    
    def _calculate_stability_score(self, fold_results: List[Dict[str, Any]]) -> float:
        """Calcula score de estabilidad."""
        if not fold_results:
            return 0.0
        
        r2_scores = [fold['metrics']['r2_score'] for fold in fold_results]
        stability = 1.0 - np.std(r2_scores)  # Menor std = mayor estabilidad
        
        return max(0.0, min(1.0, float(stability) if stability is not None else 0.0 if stability is not None else 0.0))
    
    def _calculate_degradation_score(self, fold_results: List[Dict[str, Any]]) -> float:
        """Calcula score de degradación."""
        if len(fold_results) < 2:
            return 0.0
        
        # Calcular degradación entre folds consecutivos
        degradations = []
        for i in range(1, len(fold_results)):
            prev_r2 = fold_results[i-1]['metrics']['r2_score']
            curr_r2 = fold_results[i]['metrics']['r2_score']
            
            if prev_r2 > 0:
                degradation = (prev_r2 - curr_r2) / prev_r2
                degradations.append(degradation)
        
        return float(np.mean(degradations)) if degradations else 0.0
    
    def _calculate_predictability_score(self, predictions: List[float], actuals: List[float]) -> float:
        """Calcula score de predictibilidad."""
        if len(predictions) != len(actuals) or len(predictions) < 2:
            return 0.0
        
        try:
            correlation = np.corrcoef(predictions, actuals)[0, 1]
            return max(0.0, min(1.0, abs(correlation)))
        except Exception:
            return 0.0
    
    def _create_empty_regime_result(self) -> RegimeDetectionResult:
        """Crea resultado vacío para regímenes."""
        return RegimeDetectionResult(
            regime_labels=np.array([]),
            regime_centers=np.array([]),
            regime_characteristics={},
            quality_metrics={'silhouette_score': 0.0, 'calinski_harabasz_score': 0.0, 'n_clusters': 0},
            feature_importance={}
        )
    
    def _create_empty_drift_result(self) -> DataDriftResult:
        """Crea resultado vacío para drift."""
        return DataDriftResult(
            drift_scores={},
            overall_drift=0.0,
            drift_detected=False,
            affected_features=[],
            confidence_level=0.0
        )
    
    def _create_empty_walk_forward_result(self) -> WalkForwardResult:
        """Crea resultado vacío para walk-forward."""
        return WalkForwardResult(
            fold_results=[],
            overall_metrics={},
            stability_score=0.0,
            degradation_score=0.0,
            predictability_score=0.0
        )
    
    def perform_advanced_temporal_validation(self, 
                                          data: pd.DataFrame,
                                          target_column: Optional[str] = None,
                                          feature_columns: Optional[List[str]] = None) -> TemporalValidationResult:
        """
        Realiza validación temporal avanzada con análisis de estabilidad y degradación.
        
        Args:
            data: DataFrame con datos de estrategias
            target_column: Columna objetivo para validación
            feature_columns: Columnas de características (opcional)
            
        Returns:
            TemporalValidationResult con análisis temporal completo
        """
        try:
            self.logger.info("🔬 Iniciando validación temporal avanzada...")
            
            # Configuración por defecto
            if target_column is None:
                target_column = getattr(self, 'config', None).target_column
            
            # Asegurar que target_column no sea None
            if target_column is None:
                target_column = "Unified_Score"
            
            if feature_columns is None:
                feature_columns = self._select_temporal_features(data, target_column)
            
            # Preparar datos
            X, y = self._prepare_temporal_data(data, feature_columns, target_column)
            
            if len(X) < getattr(self, 'config', None).min_train_size:
                self.logger.warning(f"⚠️ Datos insuficientes para validación temporal: {len(X)} < {getattr(self, 'config', None).min_train_size}")
                return self._create_empty_temporal_result()
            
            # Realizar walk-forward validation
            fold_results = []
            all_predictions = []
            all_actuals = []
            
            # Configurar TimeSeriesSplit para validación temporal
            from getattr(sklearn, 'model', None)_selection import TimeSeriesSplit
            tscv = TimeSeriesSplit(n_splits=getattr(self, 'config', None).n_splits)
            
            for fold_idx, (train_idx, test_idx) in enumerate(tscv.split(X)):
                try:
                    # Dividir datos temporalmente
                    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                    
                    # Entrenar modelo
                    if getattr(self, 'model', None) is not None:
                        getattr(self, 'model', None).fit(X_train, y_train)
                        
                        # Predecir
                        y_pred = getattr(self, 'model', None).predict(X_test)
                    else:
                        # Usar modelo por defecto si no hay uno configurado
                        from sklearn.ensemble import RandomForestRegressor
                        default_model = RandomForestRegressor(n_estimators=100, random_state=42)
                        default_model.fit(X_train, y_train)
                        y_pred = default_model.predict(X_test)
                    
                    # Calcular métricas
                    metrics = self._calculate_temporal_metrics(y_test, y_pred)
                    
                    # Calcular importancia de características
                    feature_importance = self._calculate_feature_importance(X_train, y_train)
                    
                    fold_result = {
                        'fold': fold_idx + 1,
                        'train_size': len(X_train),
                        'test_size': len(X_test),
                        'metrics': metrics,
                        'feature_importance': feature_importance,
                        'predictions': ((y_pred.tolist() if hasattr(y_pred, 'tolist') else list(y_pred)) if hasattr(y_pred, 'tolist') else list(y_pred)),
                        'actuals': ((y_test.tolist() if hasattr(y_test, 'tolist') else list(y_test)) if hasattr(y_test, 'tolist') else list(y_test))
                    }
                    
                    fold_results.append(fold_result)
                    all_predictions.extend(((y_pred.tolist() if hasattr(y_pred, 'tolist') else list(y_pred)) if hasattr(y_pred, 'tolist') else list(y_pred)))
                    all_actuals.extend(((y_test.tolist() if hasattr(y_test, 'tolist') else list(y_test)) if hasattr(y_test, 'tolist') else list(y_test)))
                    
                except Exception as e:
                    self.logger.warning(f"Error en fold {fold_idx + 1}: {e}")
                    continue
            
            if not fold_results:
                self.logger.error("❌ No se pudo completar ningún fold de validación temporal")
                return self._create_empty_temporal_result()
            
            # Calcular métricas generales
            overall_metrics = self._calculate_overall_temporal_metrics(fold_results)
            
            # Análisis de estabilidad temporal
            stability_analysis = self._analyze_temporal_stability(fold_results)
            
            # Análisis de degradación temporal
            degradation_analysis = self._analyze_temporal_degradation(fold_results)
            
            # Calcular robustez temporal
            robustness_score = self._calculate_temporal_robustness(fold_results)
            
            # Calcular consistencia temporal
            temporal_consistency = self._calculate_temporal_consistency(all_predictions, all_actuals)
            
            result = TemporalValidationResult(
                fold_results=fold_results,
                overall_metrics=overall_metrics,
                stability_analysis=stability_analysis,
                degradation_analysis=degradation_analysis,
                robustness_score=robustness_score,
                temporal_consistency=temporal_consistency
            )
            
            self.logger.info("✅ Validación temporal avanzada completada")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error en validación temporal: {e}")
            return self._create_empty_temporal_result()
    
    def _select_temporal_features(self, data: pd.DataFrame, target_column: str) -> List[str]:
        """Selecciona características para validación temporal."""
        # Excluir la columna objetivo y columnas no numéricas
        numeric_cols = data.select_dtypes(include=[np.number]).((columns.tolist() if hasattr(columns, 'tolist') else list(columns)) if hasattr(columns, 'tolist') else list(columns))
        
        if target_column in numeric_cols:
            numeric_cols.remove(target_column)
        
        # Priorizar características relevantes para validación temporal
        priority_features = [
            'Profit_factor', 'Sharpe_Ratio', 'Max_DD_%',
            'Win_Rate_%', 'Total_Trades', 'CAGR',
            'FK96_Elite_Enhanced', 'QVA_Score', 'Unified_Score'
        ]
        
        selected_features = []
        for feature in priority_features:
            if feature in numeric_cols:
                selected_features.append(feature)
                numeric_cols.remove(feature)
        
        # Agregar otras características numéricas
        selected_features.extend(numeric_cols[:5])
        
        return selected_features[:10]  # Máximo 10 características
    
    def _prepare_temporal_data(self, 
                              data: pd.DataFrame, 
                              feature_columns: List[str], 
                              target_column: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepara datos para validación temporal."""
        # Verificar que las columnas existen
        available_features = [col for col in feature_columns if col in data.columns]
        
        if len(available_features) < 2:
            self.logger.warning("⚠️ Pocas características disponibles para validación temporal")
            # Usar columnas numéricas como fallback
            numeric_cols = data.select_dtypes(include=[np.number]).((columns.tolist() if hasattr(columns, 'tolist') else list(columns)) if hasattr(columns, 'tolist') else list(columns))
            if target_column in numeric_cols:
                numeric_cols.remove(target_column)
            available_features = numeric_cols[:5]
        
        if target_column not in data.columns:
            raise ValueError(f"Columna objetivo '{target_column}' no encontrada en los datos")
        
        # Preparar X e y
        X = data[available_features].copy()
        y = data[target_column]
        
        # Limpiar datos
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median())
        
        y = y.replace([np.inf, -np.inf], np.nan)
        y = y.dropna()
        
        # Alinear índices
        common_index = X.index.intersection(y.index)
        X = X.loc[common_index]
        y = y.loc[common_index]
        
        return X, y
    
    def _calculate_temporal_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
        """Calcula métricas para un fold temporal."""
        try:
            from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
            
            r2 = r2_score(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mae = mean_absolute_error(y_true, y_pred)
            
            # Métricas adicionales para validación temporal
            correlation = np.corrcoef(y_true, y_pred)[0, 1] if len(y_true) > 1 else 0.0
            bias = np.mean(y_pred - y_true)
            
            return {
                'r2_score': float(r2) if r2 is not None else 0.0 if r2 is not None else 0.0,
                'rmse': float(rmse) if rmse is not None else 0.0 if rmse is not None else 0.0,
                'mae': float(mae) if mae is not None else 0.0 if mae is not None else 0.0,
                'correlation': float(correlation) if correlation is not None else 0.0 if correlation is not None else 0.0,
                'bias': float(bias) if bias is not None else 0.0 if bias is not None else 0.0
            }
        except Exception as e:
            self.logger.warning(f"Error calculando métricas temporales: {e}")
            return {
                'r2_score': 0.0, 'rmse': 0.0, 'mae': 0.0,
                'correlation': 0.0, 'bias': 0.0
            }
    
    def _calculate_overall_temporal_metrics(self, fold_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcula métricas generales de validación temporal."""
        if not fold_results:
            return {}
        
        # Extraer métricas de todos los folds
        r2_scores = [fold['metrics']['r2_score'] for fold in fold_results]
        rmse_scores = [fold['metrics']['rmse'] for fold in fold_results]
        correlation_scores = [fold['metrics']['correlation'] for fold in fold_results]
        bias_scores = [fold['metrics']['bias'] for fold in fold_results]
        
        return {
            'mean_r2': float(np.mean(r2_scores)),
            'std_r2': float(np.std(r2_scores)),
            'mean_rmse': float(np.mean(rmse_scores)),
            'std_rmse': float(np.std(rmse_scores)),
            'mean_correlation': float(np.mean(correlation_scores)),
            'std_correlation': float(np.std(correlation_scores)),
            'mean_bias': float(np.mean(bias_scores)),
            'std_bias': float(np.std(bias_scores))
        }
    
    def _analyze_temporal_stability(self, fold_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analiza estabilidad temporal."""
        if len(fold_results) < 2:
            return {'stability_score': 0.0, 'consistency': 0.0, 'volatility': 0.0}
        
        # Calcular estabilidad basada en R²
        r2_scores = [fold['metrics']['r2_score'] for fold in fold_results]
        stability_score = 1.0 - np.std(r2_scores)
        
        # Calcular consistencia (cuánto se mantienen las métricas)
        consistency = 1.0 - np.std([fold['metrics']['correlation'] for fold in fold_results])
        
        # Calcular volatilidad de las métricas
        volatility = np.std([fold['metrics']['rmse'] for fold in fold_results])
        
        return {
            'stability_score': float(max(0.0, min(1.0, float(stability_score) if stability_score is not None else 0.0 if stability_score is not None else 0.0))),
            'consistency': float(max(0.0, min(1.0, float(consistency) if consistency is not None else 0.0 if consistency is not None else 0.0))),
            'volatility': float(volatility) if volatility is not None else 0.0 if volatility is not None else 0.0
        }
    
    def _analyze_temporal_degradation(self, fold_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analiza degradación temporal."""
        if len(fold_results) < 2:
            return {'degradation_score': 0.0, 'trend': 0.0, 'acceleration': 0.0}
        
        # Calcular degradación entre folds consecutivos
        degradations = []
        for i in range(1, len(fold_results)):
            prev_r2 = fold_results[i-1]['metrics']['r2_score']
            curr_r2 = fold_results[i]['metrics']['r2_score']
            
            if prev_r2 > 0:
                degradation = (prev_r2 - curr_r2) / prev_r2
                degradations.append(degradation)
        
        degradation_score = float(np.mean(degradations)) if degradations else 0.0
        
        # Calcular tendencia de degradación
        if len(degradations) > 1:
            trend = np.polyfit(range(len(degradations)), degradations, 1)[0]
            acceleration = np.polyfit(range(len(degradations)), degradations, 2)[0] if len(degradations) > 2 else 0.0
        else:
            trend = 0.0
            acceleration = 0.0
        
        return {
            'degradation_score': degradation_score,
            'trend': float(trend) if trend is not None else 0.0 if trend is not None else 0.0,
            'acceleration': float(acceleration) if acceleration is not None else 0.0 if acceleration is not None else 0.0
        }
    
    def _calculate_temporal_robustness(self, fold_results: List[Dict[str, Any]]) -> float:
        """Calcula score de robustez temporal."""
        if not fold_results:
            return 0.0
        
        # Robustez basada en estabilidad y consistencia
        r2_scores = [fold['metrics']['r2_score'] for fold in fold_results]
        correlation_scores = [fold['metrics']['correlation'] for fold in fold_results]
        
        # Calcular robustez como combinación de estabilidad y predictibilidad
        stability = 1.0 - np.std(r2_scores)
        predictability = np.mean([abs(corr) for corr in correlation_scores])
        
        robustness = (stability + predictability) / 2.0
        
        return max(0.0, min(1.0, float(robustness) if robustness is not None else 0.0 if robustness is not None else 0.0))
    
    def _calculate_temporal_consistency(self, predictions: List[float], actuals: List[float]) -> float:
        """Calcula consistencia temporal entre predicciones y valores reales."""
        if len(predictions) != len(actuals) or len(predictions) < 2:
            return 0.0
        
        try:
            # Calcular correlación entre predicciones y valores reales
            correlation = np.corrcoef(predictions, actuals)[0, 1]
            
            # Calcular consistencia como medida de estabilidad temporal
            consistency = max(0.0, min(1.0, abs(correlation)))
            
            return float(consistency) if consistency is not None else 0.0 if consistency is not None else 0.0
        except Exception as e:
            self.logger.warning(f"Error calculando consistencia temporal: {e}")
            return 0.0
    
    def _create_empty_temporal_result(self) -> TemporalValidationResult:
        """Crea resultado vacío para validación temporal."""
        return TemporalValidationResult(
            fold_results=[],
            overall_metrics={},
            stability_analysis={'stability_score': 0.0, 'consistency': 0.0, 'volatility': 0.0},
            degradation_analysis={'degradation_score': 0.0, 'trend': 0.0, 'acceleration': 0.0},
            robustness_score=0.0,
            temporal_consistency=0.0
        )


def run_advanced_ml_validation(data: pd.DataFrame,
                              reference_data: Optional[pd.DataFrame] = None,
                              target_column: str = 'Unified_Score') -> Dict[str, Any]:
    """
    Ejecuta validación ML avanzada completa.
    
    Args:
        data: DataFrame con datos de estrategias
        reference_data: Datos de referencia para drift (opcional)
        target_column: Columna objetivo para walk-forward
        
    Returns:
        Diccionario con resultados de validación ML
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🔬 Iniciando validación ML avanzada...")
        
        validator = AdvancedMLValidator()
        results = {}
        
        # 1. Detección de regímenes
        regime_result = validator.detect_market_regimes(data)
        results['regime_detection'] = {
            'regime_labels': regime_result.((regime_labels.tolist() if hasattr(regime_labels, 'tolist') else list(regime_labels)) if hasattr(regime_labels, 'tolist') else list(regime_labels)),
            'regime_centers': regime_result.((regime_centers.tolist() if hasattr(regime_centers, 'tolist') else list(regime_centers)) if hasattr(regime_centers, 'tolist') else list(regime_centers)),
            'regime_characteristics': regime_result.regime_characteristics,
            'quality_metrics': regime_result.quality_metrics,
            'feature_importance': regime_result.feature_importance
        }
        
        # 2. Detección de data drift
        if reference_data is not None:
            drift_result = validator.detect_data_drift(reference_data, data)
            results['data_drift'] = {
                'drift_scores': drift_result.drift_scores,
                'overall_drift': drift_result.overall_drift,
                'drift_detected': drift_result.drift_detected,
                'affected_features': drift_result.affected_features,
                'confidence_level': drift_result.confidence_level
            }
        
        # 3. Validación walk-forward
        if target_column in data.columns:
            walk_forward_result = validator.perform_walk_forward_validation(data, target_column)
            results['walk_forward'] = {
                'fold_results': walk_forward_result.fold_results,
                'overall_metrics': walk_forward_result.overall_metrics,
                'stability_score': walk_forward_result.stability_score,
                'degradation_score': walk_forward_result.degradation_score,
                'predictability_score': walk_forward_result.predictability_score
            }
        
        logger.info("✅ Validación ML avanzada completada")
        return results
        
    except Exception as e:
        logger.error(f"❌ Error en validación ML avanzada: {e}")
        return {'error': str(e)}


if __name__ == "__main__":
    # Test del módulo
    import numpy as np
    import pandas as pd
    
    # Crear datos de prueba
    np.random.seed(42)
    n_strategies = 100
    
    test_data = pd.DataFrame({
        'Sharpe_Ratio': np.random.normal(1.0, 0.5, n_strategies),
        'Max_DD_%': np.random.uniform(-0.3, -0.05, n_strategies),
        'CAGR': np.random.uniform(0.1, 0.5, n_strategies),
        'Profit_factor': np.random.uniform(1.0, 3.0, n_strategies),
        'Win_Rate_%': np.random.uniform(0.4, 0.8, n_strategies),
        'Total_Trades': np.random.randint(50, 500, n_strategies),
        'Unified_Score': np.random.uniform(0.3, 0.9, n_strategies)
    })
    
    # Ejecutar validación
    results = run_advanced_ml_validation(test_data)
    print("Resultados de validación ML:", json.dumps(results, indent=2)) 