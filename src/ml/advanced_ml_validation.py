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
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
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
                 walk_forward_folds: int = 5):
        """
        Inicializa el validador avanzado de ML.
        
        Args:
            n_regimes: Número de regímenes a detectar
            drift_threshold: Umbral para detectar data drift
            walk_forward_folds: Número de folds para walk-forward
        """
        self.n_regimes = n_regimes
        self.drift_threshold = drift_threshold
        self.walk_forward_folds = walk_forward_folds
        self.logger = logger
        
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
                overall_drift=float(overall_drift),
                drift_detected=bool(drift_detected),
                affected_features=affected_features,
                confidence_level=float(confidence_level)
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
                    'predictions': y_pred.tolist(),
                    'actuals': y_test.tolist()
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
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
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
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            available_features = numeric_cols[:3]
        
        return available_features
    
    def _select_walk_forward_features(self, data: pd.DataFrame, target_column: str) -> List[str]:
        """Selecciona características para walk-forward."""
        # Excluir la columna objetivo y columnas no numéricas
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        
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
                    drift_scores[col] = float(drift_score)
        
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
        
        return max(0.0, min(1.0, float(confidence)))
    
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
                'r2_score': float(r2),
                'rmse': float(rmse),
                'mae': float(mae)
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
        
        return max(0.0, min(1.0, float(stability)))
    
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
            'regime_labels': regime_result.regime_labels.tolist(),
            'regime_centers': regime_result.regime_centers.tolist(),
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