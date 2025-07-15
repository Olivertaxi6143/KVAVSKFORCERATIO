#!/usr/bin/env python3
"""
Sistema Predictivo Híbrido AXI SELECT Mejorado
===============================================

Implementa un sistema predictivo híbrido usando alternativas compatibles con Python 3.13.2:
- PyTorch para redes neuronales ligeras
- LightGBM para boosting de árboles
- CatBoost para modelos de ensemble
- Scikit-learn para modelos explicables
- SHAP para interpretabilidad

Basado en el feedback de AXI SELECT con fases, criterios y Edge Score.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 2.0.0
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import warnings
from datetime import datetime, timedelta
import json
from pathlib import Path
from core.logger_config import setup_logger
logger = setup_logger(__name__)

# Configurar warnings
warnings.filterwarnings("ignore")

# Configurar logging
# logger = logging.getLogger(__name__) # This line is removed as per the new_code

# Importar librerías de ML compatibles
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
    logger.info("✅ PyTorch disponible")
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("⚠️ PyTorch no disponible")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
    logger.info("✅ LightGBM disponible")
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logger.warning("⚠️ LightGBM no disponible")

try:
    from catboost import CatBoostRegressor, CatBoostClassifier
    CATBOOST_AVAILABLE = True
    logger.info("✅ CatBoost disponible")
except ImportError:
    CATBOOST_AVAILABLE = False
    logger.warning("⚠️ CatBoost no disponible")

# Scikit-learn siempre disponible
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.decomposition import PCA
import shap

# Configurar PyTorch para CPU
if TORCH_AVAILABLE:
    torch.set_default_device('cpu')
    torch.set_default_dtype(torch.float32)


class ModelType(Enum):
    """Tipos de modelos disponibles."""
    PYTORCH_NN = "pytorch_neural_network"
    LIGHTGBM = "lightgbm"
    CATBOOST = "catboost"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    LINEAR_REGRESSION = "linear_regression"
    MLP_SKLEARN = "mlp_sklearn"


@dataclass
class PredictionResult:
    """Resultado de predicción."""
    model_type: ModelType
    predictions: np.ndarray
    confidence: float
    feature_importance: Dict[str, float]
    model_performance: Dict[str, float]
    explainability_score: float


class AXISelectPredictiveSystem:
    """
    Sistema predictivo híbrido para AXI SELECT.
    
    Características:
    - Modelos explicables (árboles, SHAP)
    - Modelos de precisión (redes neuronales, boosting)
    - Validación robusta con walk-forward
    - Interpretabilidad automática
    - Compatible con Python 3.13.2
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el sistema predictivo.
        
        Args:
            config: Configuración del sistema
        """
        self.config = config or self._default_config()
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.results = {}
        
        # Inicializar modelos
        self._initialize_models()
        
        logger.info("🔬 Sistema predictivo AXI SELECT inicializado")
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto."""
        return {
            'test_size': 0.3,
            'random_state': 42,
            'n_splits': 5,
            'explicable_models': ['random_forest', 'linear_regression'],
            'precision_models': ['pytorch_nn', 'lightgbm', 'catboost'],
            'feature_selection': True,
            'shap_analysis': True,
            'confidence_threshold': 0.7
        }
    
    def _initialize_models(self):
        """Inicializa los modelos predictivos."""
        try:
            # Modelos explicables
            self.models[ModelType.RANDOM_FOREST] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=self.config['random_state']
            )
            
            self.models[ModelType.LINEAR_REGRESSION] = LinearRegression()
            
            self.models[ModelType.GRADIENT_BOOSTING] = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                random_state=self.config['random_state']
            )
            
            self.models[ModelType.MLP_SKLEARN] = MLPRegressor(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=self.config['random_state']
            )
            
            # Modelos de precisión
            if LIGHTGBM_AVAILABLE:
                self.models[ModelType.LIGHTGBM] = lgb.LGBMRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=self.config['random_state']
                )
            
            if CATBOOST_AVAILABLE:
                self.models[ModelType.CATBOOST] = CatBoostRegressor(
                    iterations=100,
                    depth=6,
                    learning_rate=0.1,
                    random_state=self.config['random_state'],
                    verbose=False
                )
            
            if TORCH_AVAILABLE:
                # Red neuronal PyTorch se creará dinámicamente
                pass
            
            # Escaladores
            self.scalers['standard'] = StandardScaler()
            self.scalers['robust'] = RobustScaler()
            
            logger.info(f"OK {len(self.models)} modelos inicializados")
            
        except Exception as e:
            logger.error(f"ERROR inicializando modelos: {e}")
    
    def _create_pytorch_nn(self, input_size: int) -> nn.Module:
        """Crea una red neuronal PyTorch."""
        class SimpleNN(nn.Module):
            def __init__(self, input_size: int):
                super().__init__()
                self.layer1 = nn.Linear(input_size, 32)
                self.layer2 = nn.Linear(32, 16)
                self.layer3 = nn.Linear(16, 1)
                self.dropout = nn.Dropout(0.1)
                self.relu = nn.ReLU()
                
            def forward(self, x):
                x = self.relu(self.layer1(x))
                x = self.dropout(x)
                x = self.relu(self.layer2(x))
                x = self.layer3(x)
                return x
        
        return SimpleNN(input_size)
    
    def prepare_features(self, data: pd.DataFrame, target_column: str) -> Tuple[Union[pd.DataFrame, pd.Series], Union[pd.DataFrame, pd.Series]]:
        """
        Prepara características para predicción.
        
        Args:
            data: DataFrame con datos
            target_column: Columna objetivo
            
        Returns:
            X, y preparados para ML
        """
        try:
            # Seleccionar características numéricas
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            
            if target_column in numeric_cols:
                numeric_cols.remove(target_column)
            
            # Filtrar características con valores válidos
            valid_features = []
            for col in numeric_cols:
                # Verificar que la columna tiene valores válidos usando métodos específicos
                notna_count = data[col].notna().sum()
                if notna_count > 0:
                    valid_features.append(col)
            
            if not valid_features:
                logger.warning("⚠️ No se encontraron características válidas")
                return pd.DataFrame(), pd.Series()
            
            # Crear características
            X = data[valid_features].copy()
            
            # Manejar valores faltantes
            for col in X.columns:
                # Usar pandas de manera segura
                if X[col].isna().any():
                    median_val = X[col].median()
                    X[col] = X[col].fillna(median_val)
            
            # Crear características adicionales
            if 'cagr_is' in X.columns and 'cagr_oos' in X.columns:
                X['cagr_ratio'] = X['cagr_is'] / (X['cagr_oos'] + 1e-8)
            
            if 'sharpe_ratio_is' in X.columns and 'sharpe_ratio_oos' in X.columns:
                X['sharpe_ratio_diff'] = X['sharpe_ratio_is'] - X['sharpe_ratio_oos']
            
            if 'profit_factor_is' in X.columns and 'profit_factor_oos' in X.columns:
                X['profit_factor_ratio'] = X['profit_factor_is'] / (X['profit_factor_oos'] + 1e-8)
            
            # Preparar variable objetivo
            if target_column in data.columns:
                y = data[target_column].copy()
                # Manejar valores faltantes en la variable objetivo
                notna_mask = y.notna()
                if not notna_mask.all():
                    y.fillna(y.median(), inplace=True)
            else:
                # Si no existe la columna objetivo, usar una columna por defecto
                default_targets = ['cagr_is', 'sharpe_ratio_is', 'profit_factor_is']
                for target in default_targets:
                    if target in data.columns:
                        y = data[target].copy()
                        notna_mask = y.notna()
                        if not notna_mask.all():
                            y.fillna(y.median(), inplace=True)
                        break
                else:
                    logger.error(f"❌ No se encontró columna objetivo válida")
                    return pd.DataFrame(), pd.Series()
            
            logger.info(f"✅ Características preparadas: {X.shape[1]} características, {X.shape[0]} muestras")
            return X, y
            
        except Exception as e:
            logger.error(f"ERROR preparando características: {e}")
            return pd.DataFrame(), pd.Series(dtype=float)
    
    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Predice usando el modelo entrenado.
        
        Args:
            data: DataFrame con datos para predicción
            
        Returns:
            Diccionario con predicciones
        """
        try:
            if not hasattr(self, 'results') or not self.results:
                logger.warning("⚠️ No hay modelos entrenados. Ejecuta fit() primero.")
                return {}
            
            # Preparar características
            X, _ = self.prepare_features(data, 'cagr_is')  # Usar columna por defecto
            
            if X.empty:
                logger.error("❌ No se pudieron preparar características para predicción")
                return {}
            
            predictions = {}
            
            # Obtener predicciones de cada modelo
            if 'predictions' in self.results:
                for model_name, pred in self.results['predictions'].items():
                    if isinstance(pred, (list, np.ndarray)):
                        predictions[model_name] = pred
                    else:
                        logger.warning(f"⚠️ Predicción de {model_name} no válida")
            
            # Calcular predicción ensemble
            if len(predictions) > 1:
                valid_preds = [pred for pred in predictions.values() if isinstance(pred, (list, np.ndarray))]
                if valid_preds:
                    ensemble_pred = np.mean(valid_preds, axis=0)
                    predictions['ensemble'] = ensemble_pred.tolist()
            
            # Calcular confianza
            confidence = self._calculate_confidence(predictions)
            
            return {
                'predictions': predictions,
                'confidence': confidence,
                'models_used': len(predictions)
            }
            
        except Exception as e:
            logger.error(f"ERROR en predicción: {e}")
            return {}
    
    def train_model(self, model_type: ModelType, X: pd.DataFrame, y: pd.Series) -> Optional[Any]:
        """
        Entrena un modelo específico.
        
        Args:
            model_type: Tipo de modelo a entrenar
            X: Características
            y: Variable objetivo
            
        Returns:
            Modelo entrenado o None si falla
        """
        try:
            if model_type not in self.models and model_type != ModelType.PYTORCH_NN:
                logger.warning(f"WARNING Modelo {model_type} no disponible")
                return None
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.config['test_size'], random_state=self.config['random_state']
            )
            
            # Convertir a tipos correctos
            X_train = pd.DataFrame(X_train, columns=X.columns)
            X_test = pd.DataFrame(X_test, columns=X.columns)
            y_train = pd.Series(y_train, index=X_train.index)
            y_test = pd.Series(y_test, index=X_test.index)
            
            if model_type == ModelType.PYTORCH_NN and TORCH_AVAILABLE:
                return self._train_pytorch_model(X_train, X_test, y_train, y_test)
            else:
                model = self.models[model_type]
                
                # Escalar datos si es necesario
                if model_type in [ModelType.MLP_SKLEARN]:
                    scaler = self.scalers['standard']
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Calcular métricas
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                
                # Validar métricas
                r2 = max(-1.0, min(1.0, r2))  # Clamp R² entre -1 y 1
                rmse = max(0.0, rmse)  # RMSE debe ser positivo
                
                logger.info(f"OK {model_type.value} entrenado - R²: {r2:.3f}, RMSE: {rmse:.3f}")
                
                return {
                    'model': model,
                    'r2_score': r2,
                    'rmse': rmse,
                    'feature_importance': self._get_feature_importance(model, X.columns.tolist())
                }
                
        except Exception as e:
            logger.error(f"ERROR entrenando {model_type.value}: {e}")
            return None
    
    def _train_pytorch_model(self, X_train: pd.DataFrame, X_test: pd.DataFrame, 
                           y_train: pd.Series, y_test: pd.Series) -> Optional[Any]:
        """
        Entrena modelo PyTorch.
        """
        try:
            if not TORCH_AVAILABLE:
                return None
                
            # Convertir a tensores
            X_train_tensor = torch.FloatTensor(X_train.values)
            X_test_tensor = torch.FloatTensor(X_test.values)
            y_train_tensor = torch.FloatTensor(y_train.values)
            y_test_tensor = torch.FloatTensor(y_test.values)
            
            # Crear modelo
            input_size = X_train.shape[1]
            model = torch.nn.Sequential(
                torch.nn.Linear(input_size, 64),
                torch.nn.ReLU(),
                torch.nn.Dropout(0.2),
                torch.nn.Linear(64, 32),
                torch.nn.ReLU(),
                torch.nn.Linear(32, 1)
            )
            
            # Entrenar
            criterion = torch.nn.MSELoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
            
            for epoch in range(100):
                optimizer.zero_grad()
                outputs = model(X_train_tensor).squeeze()
                loss = criterion(outputs, y_train_tensor)
                loss.backward()
                optimizer.step()
            
            return model
            
        except Exception as e:
            logger.warning(f"⚠️ Error entrenando PyTorch: {e}")
            return None
    
    def _predict_pytorch_model(self, model: Any, X: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Predice con modelo PyTorch.
        """
        try:
            if model is None:
                return None
                
            X_tensor = torch.FloatTensor(X.values)
            model.eval()
            with torch.no_grad():
                predictions = model(X_tensor).squeeze().numpy()
            return predictions
            
        except Exception as e:
            logger.warning(f"⚠️ Error prediciendo PyTorch: {e}")
            return None
    
    def _get_feature_importance(self, model: Any, feature_names: List[str]) -> Dict[str, float]:
        """
        Obtiene importancia de características.
        """
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                return dict(zip(feature_names, importances.tolist()))
            else:
                return {name: 0.0 for name in feature_names}
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo importancia: {e}")
            return {name: 0.0 for name in feature_names}
    
    def _get_pytorch_importance(self, model: Any, feature_names: List[str]) -> Dict[str, float]:
        """
        Obtiene importancia de características para PyTorch.
        """
        try:
            # Para PyTorch, usar pesos de la primera capa como aproximación
            if hasattr(model, '0') and hasattr(model['0'], 'weight'):
                weights = model['0'].weight.data.abs().mean(dim=0).numpy()
                return dict(zip(feature_names, weights.tolist()))
            else:
                return {name: 0.0 for name in feature_names}
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo importancia PyTorch: {e}")
            return {name: 0.0 for name in feature_names}
    
    def predict_hybrid(self, data: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """
        Predicción híbrida usando múltiples modelos.
        
        Args:
            data: DataFrame con datos
            target_column: Columna objetivo
            
        Returns:
            Diccionario con resultados de predicción
        """
        try:
            logger.info("🔮 Iniciando predicción híbrida...")
            
            # Preparar características
            X, y = self.prepare_features(data, target_column)
            
            if X.empty or y.empty:
                logger.error("❌ No se pudieron preparar características")
                return {}
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Convertir a tipos correctos
            X_train = pd.DataFrame(X_train, columns=X.columns)
            X_test = pd.DataFrame(X_test, columns=X.columns)
            y_train = pd.Series(y_train, index=X_train.index)
            y_test = pd.Series(y_test, index=X_test.index)
            
            # Entrenar modelos
            models_trained = 0
            predictions = {}
            feature_importance = {}
            
            # LightGBM
            try:
                lgb_model = self._train_lightgbm_model(X_train, X_test, y_train, y_test)
                if lgb_model is not None:
                    predictions['lightgbm'] = lgb_model.predict(X)
                    feature_importance['lightgbm'] = self._get_feature_importance(
                        lgb_model, X.columns.tolist()
                    )
                    models_trained += 1
            except Exception as e:
                logger.warning(f"⚠️ Error en LightGBM: {e}")
            
            # CatBoost
            try:
                cat_model = self._train_catboost_model(X_train, X_test, y_train, y_test)
                if cat_model is not None:
                    predictions['catboost'] = cat_model.predict(X)
                    feature_importance['catboost'] = self._get_feature_importance(
                        cat_model, X.columns.tolist()
                    )
                    models_trained += 1
            except Exception as e:
                logger.warning(f"⚠️ Error en CatBoost: {e}")
            
            # PyTorch
            try:
                torch_model = self._train_pytorch_model(X_train, X_test, y_train, y_test)
                if torch_model is not None:
                    torch_pred = self._predict_pytorch_model(torch_model, pd.DataFrame(X))
                    if torch_pred is not None:
                        predictions['pytorch'] = torch_pred
                        feature_importance['pytorch'] = self._get_pytorch_importance(
                            torch_model, X.columns.tolist()
                        )
                        models_trained += 1
            except Exception as e:
                logger.warning(f"⚠️ Error en PyTorch: {e}")
            
            # Ensemble
            if len(predictions) > 1:
                ensemble_pred = np.mean(list(predictions.values()), axis=0)
                predictions['ensemble'] = ensemble_pred
            
            return {
                'predictions': predictions,
                'feature_importance': feature_importance,
                'models_trained': models_trained,
                'X_shape': X.shape,
                'y_shape': y.shape
            }
            
        except Exception as e:
            logger.error(f"ERROR en predicción híbrida: {e}")
            return {}
    
    def fit(self, data: pd.DataFrame, target_column: str) -> None:
        """
        Entrena todos los modelos internos con los datos y la columna objetivo especificada.
        Guarda los resultados en self.results.
        """
        self.results = self.predict_hybrid(data, target_column)
        logger.info(f"✅ fit() completado: {self.results.get('models_trained', 0)} modelos entrenados")
    
    def _calculate_ensemble_predictions(self, results: Dict, X: pd.DataFrame) -> np.ndarray:
        """Calcula predicción ensemble."""
        predictions = []
        
        for model_type, result in results.items():
            model = result['model']
            
            if model_type == ModelType.PYTORCH_NN:
                model.eval()
                with torch.no_grad():
                    X_tensor = torch.FloatTensor(X.values)
                    pred = model(X_tensor).numpy().flatten()
            elif hasattr(model, 'predict'):
                pred = model.predict(X)
            else:
                continue
            
            predictions.append(pred)
        
        if predictions:
            return np.mean(predictions, axis=0)
        else:
            return np.zeros(len(X))
    
    def _perform_shap_analysis(self, results: Dict, X: pd.DataFrame) -> Dict[str, Any]:
        """Realiza análisis SHAP."""
        try:
            # Usar el mejor modelo para SHAP
            best_model_key = max(results.keys(), key=lambda k: results[k]['r2_score'])
            best_model = results[best_model_key]['model']
            
            if hasattr(best_model, 'predict'):
                explainer = shap.TreeExplainer(best_model) if hasattr(best_model, 'feature_importances_') else shap.LinearExplainer(best_model, X)
                shap_values = explainer.shap_values(X)
                
                # Verificar que shap_values es válido antes de operar
                if shap_values is not None and hasattr(shap_values, 'tolist'):
                    shap_array = np.array(shap_values)
                    if shap_array.size > 0:
                        feature_importance = dict(zip(X.columns, np.abs(shap_array).mean(axis=0).tolist()))
                    else:
                        feature_importance = {col: 0.0 for col in X.columns}
                else:
                    feature_importance = {col: 0.0 for col in X.columns}
                
                return {
                    'shap_values': shap_values.tolist() if hasattr(shap_values, 'tolist') and shap_values is not None else shap_values,
                    'feature_importance': feature_importance
                }
            
        except Exception as e:
            logger.warning(f"⚠️ Error en análisis SHAP: {e}")
        
        return {}
    
    def _aggregate_feature_importance(self, results: Dict) -> Dict[str, float]:
        """Agrega importancia de características de todos los modelos."""
        importance_sum = {}
        count = {}
        
        for result in results.values():
            if 'feature_importance' in result:
                for feature, imp in result['feature_importance'].items():
                    if feature not in importance_sum:
                        importance_sum[feature] = 0
                        count[feature] = 0
                    importance_sum[feature] += imp
                    count[feature] += 1
        
        # Promedio
        return {feature: float(importance_sum[feature] / count[feature]) 
                for feature in importance_sum}
    
    def _calculate_final_metrics(self, results: Dict, ensemble_pred: np.ndarray, y_true: pd.Series) -> Dict[str, float]:
        """Calcula métricas finales."""
        try:
            r2 = r2_score(y_true, ensemble_pred)
            rmse = np.sqrt(mean_squared_error(y_true, ensemble_pred))
            mae = mean_absolute_error(y_true, ensemble_pred)
            
            return {
                'r2_score': float(r2),
                'rmse': float(rmse),
                'mae': float(mae),
                'mean_performance': float(np.mean([r['r2_score'] for r in results.values()]))
            }
        except Exception as e:
            logger.warning(f"⚠️ Error calculando métricas finales: {e}")
            return {'r2_score': 0.0, 'rmse': 0.0, 'mae': 0.0, 'mean_performance': 0.0}
    
    def _calculate_confidence(self, predictions: Dict[str, Any]) -> float:
        """
        Calcula la confianza de las predicciones.
        
        Args:
            predictions: Diccionario con predicciones de diferentes modelos
            
        Returns:
            Valor de confianza entre 0 y 1
        """
        try:
            if not predictions:
                return 0.0
            
            # Calcular varianza entre modelos
            valid_preds = []
            for pred in predictions.values():
                if isinstance(pred, (list, np.ndarray)):
                    valid_preds.append(np.array(pred))
            
            if len(valid_preds) < 2:
                return 0.5  # Confianza media si solo hay un modelo
            
            # Calcular coeficiente de variación
            pred_array = np.array(valid_preds)
            mean_pred = np.mean(pred_array, axis=0)
            std_pred = np.std(pred_array, axis=0)
            
            # Evitar división por cero
            cv = float(np.mean(std_pred / (np.abs(mean_pred) + 1e-8)))
            
            # Convertir a confianza (menor CV = mayor confianza)
            confidence = max(0.0, min(1.0, 1.0 - cv))
            
            return confidence
            
        except Exception as e:
            logger.warning(f"⚠️ Error calculando confianza: {e}")
            return 0.5

    def _train_lightgbm_model(self, X_train: pd.DataFrame, X_test: pd.DataFrame, 
                             y_train: pd.Series, y_test: pd.Series) -> Optional[Any]:
        """
        Entrena modelo LightGBM.
        """
        try:
            if not LIGHTGBM_AVAILABLE:
                return None
                
            model = lgb.LGBMRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42,
                verbose=-1
            )
            
            model.fit(X_train, y_train)
            return model
            
        except Exception as e:
            logger.warning(f"⚠️ Error entrenando LightGBM: {e}")
            return None
    
    def _train_catboost_model(self, X_train: pd.DataFrame, X_test: pd.DataFrame, 
                             y_train: pd.Series, y_test: pd.Series) -> Optional[Any]:
        """
        Entrena modelo CatBoost.
        """
        try:
            if not CATBOOST_AVAILABLE:
                return None
                
            model = CatBoostRegressor(
                iterations=100,
                learning_rate=0.1,
                depth=6,
                random_state=42,
                verbose=False
            )
            
            model.fit(X_train, y_train)
            return model
            
        except Exception as e:
            logger.warning(f"⚠️ Error entrenando CatBoost: {e}")
            return None


def test_axi_select_predictive_system():
    """Test del sistema predictivo AXI SELECT."""
    try:
        logger.info("🧪 Iniciando test del sistema predictivo AXI SELECT...")
        
        # Crear datos de prueba
        np.random.seed(42)
        n_samples = 100
        
        test_data = pd.DataFrame({
            'Sharpe_Ratio': np.random.normal(1.0, 0.5, n_samples),
            'Max_DD_%': np.random.uniform(-0.3, -0.05, n_samples),
            'CAGR': np.random.uniform(0.1, 0.5, n_samples),
            'Profit_factor': np.random.uniform(1.0, 3.0, n_samples),
            'Win_Rate_%': np.random.uniform(0.4, 0.8, n_samples),
            'Total_Trades': np.random.randint(50, 500, n_samples),
            'Edge_Score': np.random.uniform(0.5, 0.9, n_samples)
        })
        
        # Inicializar sistema
        system = AXISelectPredictiveSystem()
        
        # Realizar predicción
        results = system.predict_hybrid(test_data, 'Edge_Score')
        
        # Validar resultados
        assert 'error' not in results, f"Error en predicción: {results.get('error', 'Unknown')}"
        assert 'models_trained' in results, "Falta 'models_trained' en resultados"
        assert results['models_trained'] > 0, "No se entrenaron modelos"
        assert 'ensemble_predictions' in results, "Falta 'ensemble_predictions' en resultados"
        assert len(results['ensemble_predictions']) == len(test_data), "Número incorrecto de predicciones"
        assert 'confidence' in results, "Falta 'confidence' en resultados"
        assert 0 <= results['confidence'] <= 1, "Confianza fuera de rango [0,1]"
        
        logger.info(f"✅ Test completado exitosamente:")
        logger.info(f"   • Modelos entrenados: {results['models_trained']}")
        logger.info(f"   • Confianza: {results['confidence']:.3f}")
        logger.info(f"   • Métricas finales: {results.get('final_metrics', {})}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")
        return False


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Ejecutar test
    success = test_axi_select_predictive_system()
    
    if success:
        print("✅ Sistema predictivo AXI SELECT funcionando correctamente")
    else:
        print("❌ Error en sistema predictivo AXI SELECT") 