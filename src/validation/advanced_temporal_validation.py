#!/usr/bin/env python3
"""
Módulo de Validación Cruzada Temporal Avanzada
===============================================

Implementa validación walk-forward avanzada para estrategias de trading:
- Validación temporal con múltiples ventanas
- Análisis de estabilidad temporal
- Detección de degradación de predictibilidad
- Análisis de robustez temporal
- Métricas de validación temporal avanzadas

Basado en metodologías de validación temporal para finanzas cuantitativas.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler
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
class TemporalValidationResult:
    """Resultado de validación temporal."""
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


class AdvancedTemporalValidator:
    """
    Validador temporal avanzado para estrategias de trading.
    
    Funcionalidades principales:
    - Validación walk-forward con múltiples configuraciones
    - Análisis de estabilidad temporal
    - Detección de degradación de predictibilidad
    - Análisis de robustez temporal
    - Métricas de validación temporal avanzadas
    """
    
    def __init__(self, config: Optional[WalkForwardConfig] = None):
        """
        Inicializa el validador temporal avanzado.
        
        Args:
            config: Configuración para walk-forward validation
        """
        self.config = config or WalkForwardConfig()
        self.logger = logger
        
        # Inicializar modelo
        self._initialize_model()
        
        self.logger.info(f"🔬 AdvancedTemporalValidator inicializado con {self.config.n_splits} splits")
    
    def _initialize_model(self):
        """Inicializa el modelo de predicción."""
        if self.config.model_type == "random_forest":
            self.model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
        else:
            # Fallback a Random Forest
            self.model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
    
    def perform_walk_forward_validation(self, 
                                      data: pd.DataFrame,
                                      target_column: Optional[str] = None,
                                      feature_columns: Optional[List[str]] = None) -> TemporalValidationResult:
        """
        Realiza validación walk-forward temporal avanzada.
        
        Args:
            data: DataFrame con datos de estrategias
            target_column: Columna objetivo (opcional)
            feature_columns: Columnas de características (opcional)
            
        Returns:
            TemporalValidationResult con resultados de validación
        """
        try:
            self.logger.info("🔍 Ejecutando validación walk-forward temporal...")
            
            # Usar configuración o parámetros proporcionados
            target_col = target_column or self.config.target_column
            feature_cols = feature_columns or self.config.feature_columns
            
            # Seleccionar características si no se proporcionan
            if feature_cols is None:
                feature_cols = self._select_temporal_features(data, target_col)
            
            # Preparar datos
            X, y = self._prepare_temporal_data(data, feature_cols, target_col)
            
            if len(X) < self.config.min_train_size:
                self.logger.warning(f"⚠️ Pocos datos para walk-forward: {len(X)} < {self.config.min_train_size}")
                return self._create_empty_temporal_result()
            
            # Configurar TimeSeriesSplit
            tscv = TimeSeriesSplit(
                n_splits=self.config.n_splits,
                test_size=int(len(X) * self.config.test_size)
            )
            
            fold_results = []
            all_predictions = []
            all_actuals = []
            
            # Realizar validación por folds
            for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                
                # Verificar tamaño mínimo
                if len(X_train) < self.config.min_train_size:
                    self.logger.warning(f"⚠️ Fold {fold + 1}: datos insuficientes para entrenamiento")
                    continue
                
                # Entrenar modelo
                self.model.fit(X_train, y_train)
                
                # Predecir
                y_pred = self.model.predict(X_test)
                
                # Calcular métricas
                fold_metrics = self._calculate_temporal_metrics(y_test, y_pred)
                
                # Calcular importancia de características
                feature_importance = self._calculate_feature_importance(X_train, y_train)
                
                fold_result = {
                    'fold': fold + 1,
                    'train_size': len(X_train),
                    'test_size': len(X_test),
                    'train_period': f"{X_train.index[0]} - {X_train.index[-1]}",
                    'test_period': f"{X_test.index[0]} - {X_test.index[-1]}",
                    'metrics': fold_metrics,
                    'feature_importance': feature_importance,
                    'predictions': y_pred.tolist(),
                    'actuals': y_test.tolist()
                }
                
                fold_results.append(fold_result)
                all_predictions.extend(y_pred)
                all_actuals.extend(y_test)
            
            # Calcular métricas generales
            overall_metrics = self._calculate_overall_temporal_metrics(fold_results)
            stability_analysis = self._analyze_temporal_stability(fold_results)
            degradation_analysis = self._analyze_temporal_degradation(fold_results)
            robustness_score = self._calculate_temporal_robustness(fold_results)
            temporal_consistency = self._calculate_temporal_consistency(all_predictions, all_actuals)
            
            result = TemporalValidationResult(
                fold_results=fold_results,
                overall_metrics=overall_metrics,
                stability_analysis=stability_analysis,
                degradation_analysis=degradation_analysis,
                robustness_score=robustness_score,
                temporal_consistency=temporal_consistency
            )
            
            self.logger.info("✅ Validación walk-forward temporal completada")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error en validación temporal: {e}")
            return self._create_empty_temporal_result()
    
    def _select_temporal_features(self, data: pd.DataFrame, target_column: str) -> List[str]:
        """Selecciona características para validación temporal."""
        # Excluir la columna objetivo y columnas no numéricas
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        
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
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
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
            r2 = r2_score(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mae = mean_absolute_error(y_true, y_pred)
            
            # Métricas adicionales para validación temporal
            correlation = np.corrcoef(y_true, y_pred)[0, 1] if len(y_true) > 1 else 0.0
            bias = np.mean(y_pred - y_true)
            
            return {
                'r2_score': float(r2),
                'rmse': float(rmse),
                'mae': float(mae),
                'correlation': float(correlation),
                'bias': float(bias)
            }
        except Exception as e:
            self.logger.warning(f"Error calculando métricas temporales: {e}")
            return {
                'r2_score': 0.0, 'rmse': 0.0, 'mae': 0.0,
                'correlation': 0.0, 'bias': 0.0
            }
    
    def _calculate_feature_importance(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Calcula importancia de características."""
        try:
            # Entrenar modelo temporal para obtener importancia
            temp_model = RandomForestRegressor(n_estimators=50, random_state=42)
            temp_model.fit(X, y)
            
            importance = dict(zip(X.columns, temp_model.feature_importances_))
            return importance
        except Exception as e:
            self.logger.warning(f"Error calculando importancia: {e}")
            return {col: 1.0/len(X.columns) for col in X.columns}
    
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
            'stability_score': float(max(0.0, min(1.0, float(stability_score)))),
            'consistency': float(max(0.0, min(1.0, float(consistency)))),
            'volatility': float(volatility)
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
            'trend': float(trend),
            'acceleration': float(acceleration)
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
        
        return float(max(0.0, min(1.0, float(robustness))))
    
    def _calculate_temporal_consistency(self, predictions: List[float], actuals: List[float]) -> float:
        """Calcula consistencia temporal."""
        if len(predictions) != len(actuals) or len(predictions) < 2:
            return 0.0
        
        try:
            # Calcular correlación entre predicciones y valores reales
            correlation = np.corrcoef(predictions, actuals)[0, 1]
            consistency = abs(correlation) if not np.isnan(correlation) else 0.0
            
            return float(max(0.0, min(1.0, float(consistency))))
        except Exception:
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


def run_advanced_temporal_validation(data: pd.DataFrame,
                                   target_column: str = 'Unified_Score',
                                   feature_columns: Optional[List[str]] = None,
                                   config: Optional[WalkForwardConfig] = None) -> Dict[str, Any]:
    """
    Ejecuta validación temporal avanzada completa.
    
    Args:
        data: DataFrame con datos de estrategias
        target_column: Columna objetivo
        feature_columns: Columnas de características (opcional)
        config: Configuración de walk-forward (opcional)
        
    Returns:
        Diccionario con resultados de validación temporal
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🔬 Iniciando validación temporal avanzada...")
        
        validator = AdvancedTemporalValidator(config)
        results = validator.perform_walk_forward_validation(data, target_column, feature_columns)
        
        # Convertir resultados a diccionario
        output = {
            'fold_results': results.fold_results,
            'overall_metrics': results.overall_metrics,
            'stability_analysis': results.stability_analysis,
            'degradation_analysis': results.degradation_analysis,
            'robustness_score': results.robustness_score,
            'temporal_consistency': results.temporal_consistency,
            'validation_summary': {
                'total_folds': len(results.fold_results),
                'mean_r2': results.overall_metrics.get('mean_r2', 0.0),
                'stability_score': results.stability_analysis.get('stability_score', 0.0),
                'robustness_score': results.robustness_score,
                'temporal_consistency': results.temporal_consistency
            }
        }
        
        logger.info("✅ Validación temporal avanzada completada")
        return output
        
    except Exception as e:
        logger.error(f"❌ Error en validación temporal avanzada: {e}")
        return {'error': str(e)}


if __name__ == "__main__":
    # Test del módulo
    import numpy as np
    import pandas as pd
    
    # Crear datos de prueba
    np.random.seed(42)
    n_strategies = 200
    
    test_data = pd.DataFrame({
        'Sharpe_Ratio': np.random.normal(1.0, 0.5, n_strategies),
        'Max_DD_%': np.random.uniform(-0.3, -0.05, n_strategies),
        'CAGR': np.random.uniform(0.1, 0.5, n_strategies),
        'Profit_factor': np.random.uniform(1.0, 3.0, n_strategies),
        'Win_Rate_%': np.random.uniform(0.4, 0.8, n_strategies),
        'Total_Trades': np.random.randint(50, 500, n_strategies),
        'Unified_Score': np.random.uniform(0.3, 0.9, n_strategies)
    })
    
    # Ejecutar validación temporal
    results = run_advanced_temporal_validation(test_data)
    print("Resultados de validación temporal:", json.dumps(results, indent=2)) 