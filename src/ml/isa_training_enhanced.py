#!/usr/bin/env python3
"""
Entrenamiento Mejorado para Intelligent Strategy Advisor (ISA)
============================================================

Sistema de entrenamiento ML avanzado para el ISA:
- Múltiples tipos de modelos (Random Forest, Gradient Boosting, Neural Network)
- Validación temporal cruzada
- Optimización de hiperparámetros
- Análisis de importancia de features
- Exportación de modelos entrenados
- Métricas de performance robustas

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import logging
import time
import pickle
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import warnings
from dataclasses import dataclass

# Scikit-learn imports
from sklearn.model_selection import TimeSeriesSplit, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.feature_selection import SelectKBest, f_regression
import shap

# Configurar warnings
warnings.filterwarnings("ignore")

# Configurar logger
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """Configuración para el entrenamiento ISA."""
    model_type: str = "random_forest"
    target_column: str = "Unified_Score"
    test_size: float = 0.2
    random_state: int = 42
    n_jobs: int = -1
    cv_folds: int = 5
    feature_selection: bool = True
    n_features: int = 10
    hyperparameter_tuning: bool = True
    save_model: bool = True
    model_path: str = "models/isa_model.pkl"

@dataclass
class TrainingResult:
    """Resultado del entrenamiento ISA."""
    model: Any
    r2_score: float
    mae: float
    rmse: float
    cross_val_score: float
    feature_importance: Dict[str, float]
    training_time: float
    model_params: Dict[str, Any]
    shap_values: Optional[np.ndarray] = None
    predictions: Optional[np.ndarray] = None
    actuals: Optional[np.ndarray] = None

class ISATrainingEnhanced:
    """
    Entrenador mejorado para Intelligent Strategy Advisor.
    
    Funcionalidades:
    - Múltiples tipos de modelos
    - Validación temporal cruzada
    - Optimización de hiperparámetros
    - Análisis de importancia de features
    - Exportación de modelos
    """
    
    def __init__(self, config: Optional[TrainingConfig] = None):
        """
        Inicializa el entrenador ISA.
        
        Args:
            config: Configuración de entrenamiento
        """
        self.config = config or TrainingConfig()
        self.model = None
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.training_result = None
        
        # Crear directorio de modelos
        model_dir = Path(self.config.model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🤖 ISATrainingEnhanced inicializado: {self.config.model_type}")
    
    def train_model(self, dataset) -> Dict[str, Any]:
        """
        Entrena el modelo ISA.
        
        Args:
            dataset: Dataset de entrenamiento (X_train, X_test, y_train, y_test)
            
        Returns:
            Dict con resultados del entrenamiento
        """
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Iniciando entrenamiento ISA: {self.config.model_type}")
            
            # Extraer datos del dataset
            X_train = dataset.X_train
            X_test = dataset.X_test
            y_train = dataset.y_train
            y_test = dataset.y_test
            
            # Preprocesamiento
            X_train_processed, X_test_processed = self._preprocess_features(X_train, X_test)
            
            # Selección de features
            if self.config.feature_selection:
                X_train_processed, X_test_processed = self._select_features(
                    X_train_processed, X_test_processed, y_train
                )
            
            # Crear y entrenar modelo
            self.model = self._create_model()
            
            # Optimización de hiperparámetros
            if self.config.hyperparameter_tuning:
                self.model = self._optimize_hyperparameters(
                    X_train_processed, y_train
                )
            
            # Entrenar modelo final
            self.model.fit(X_train_processed, y_train)
            
            # Evaluar modelo
            y_pred = self.model.predict(X_test_processed)
            
            # Calcular métricas
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Validación cruzada temporal
            cv_scores = self._temporal_cross_validation(X_train_processed, y_train)
            cv_score = np.mean(cv_scores)
            
            # Análisis de importancia de features
            feature_importance = self._analyze_feature_importance(
                X_train_processed, y_train
            )
            
            # Análisis SHAP
            shap_values = self._analyze_shap(X_test_processed)
            
            # Crear resultado
            training_time = time.time() - start_time
            
            self.training_result = TrainingResult(
                model=self.model,
                r2_score=float(r2),
                mae=float(mae),
                rmse=float(rmse),
                cross_val_score=float(cv_score),
                feature_importance=feature_importance,
                training_time=training_time,
                model_params=self.model.get_params() if self.model is not None else {},
                shap_values=shap_values,
                predictions=np.array(y_pred) if y_pred is not None else None,
                actuals=np.array(y_test.values) if y_test is not None else None
            )
            
            # Guardar modelo si está configurado
            if self.config.save_model:
                self.save_model()
            
            # Crear diccionario de resultados
            results = {
                'r2_score': r2,
                'mae': mae,
                'rmse': rmse,
                'cross_val_score': cv_score,
                'feature_importance': feature_importance,
                'training_time': training_time,
                'model_params': self.model.get_params(),
                'cv_scores': cv_scores.tolist(),
                'predictions': y_pred.tolist(),
                'actuals': y_test.values.tolist()
            }
            
            logger.info(f"✅ Entrenamiento ISA completado: R²={r2:.4f}, CV={cv_score:.4f}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en entrenamiento ISA: {e}")
            raise
    
    def _preprocess_features(self, X_train: pd.DataFrame, X_test: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Preprocesa las features para el entrenamiento.
        
        Args:
            X_train: Features de entrenamiento
            X_test: Features de test
            
        Returns:
            Tuple con features procesadas
        """
        try:
            # Escalar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Convertir de vuelta a DataFrame
            X_train_processed = pd.DataFrame(
                X_train_scaled, 
                columns=X_train.columns, 
                index=X_train.index
            )
            X_test_processed = pd.DataFrame(
                X_test_scaled, 
                columns=X_test.columns, 
                index=X_test.index
            )
            
            logger.info(f"📊 Features preprocesadas: {X_train_processed.shape}")
            return X_train_processed, X_test_processed
            
        except Exception as e:
            logger.error(f"Error en preprocesamiento: {e}")
            raise
    
    def _select_features(self, X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Selecciona las features más importantes.
        
        Args:
            X_train: Features de entrenamiento
            X_test: Features de test
            y_train: Target de entrenamiento
            
        Returns:
            Tuple con features seleccionadas
        """
        try:
            self.feature_selector = SelectKBest(score_func=f_regression, k=self.config.n_features)
            
            X_train_selected = self.feature_selector.fit_transform(X_train, y_train)
            X_test_selected = self.feature_selector.transform(X_test)
            
            # Obtener nombres de features seleccionadas
            selected_features = X_train.columns[self.feature_selector.get_support()].tolist()
            
            # Convertir de vuelta a DataFrame
            X_train_selected = pd.DataFrame(
                X_train_selected,
                columns=pd.Index(selected_features),
                index=X_train.index
            )
            X_test_selected = pd.DataFrame(
                X_test_selected,
                columns=pd.Index(selected_features),
                index=X_test.index
            )
            
            logger.info(f"🎯 Features seleccionadas: {len(selected_features)} de {X_train.shape[1]}")
            return X_train_selected, X_test_selected
            
        except Exception as e:
            logger.error(f"Error en selección de features: {e}")
            return X_train, X_test
    
    def _create_model(self) -> Any:
        """
        Crea el modelo según el tipo configurado.
        
        Returns:
            Modelo de scikit-learn
        """
        if self.config.model_type == "random_forest":
            return RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.config.random_state,
                n_jobs=self.config.n_jobs
            )
        
        elif self.config.model_type == "gradient_boosting":
            return GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.config.random_state
            )
        
        elif self.config.model_type == "neural_network":
            return MLPRegressor(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                alpha=0.001,
                learning_rate='adaptive',
                max_iter=500,
                random_state=self.config.random_state
            )
        
        elif self.config.model_type == "linear_regression":
            return LinearRegression()
        
        elif self.config.model_type == "ridge":
            return Ridge(alpha=1.0, random_state=self.config.random_state)
        
        elif self.config.model_type == "lasso":
            return Lasso(alpha=0.1, random_state=self.config.random_state)
        
        elif self.config.model_type == "svr":
            return SVR(kernel='rbf', C=1.0, gamma='scale')
        
        else:
            logger.warning(f"Tipo de modelo desconocido: {self.config.model_type}, usando Random Forest")
            return RandomForestRegressor(random_state=self.config.random_state)
    
    def _optimize_hyperparameters(self, X_train: pd.DataFrame, y_train: pd.Series) -> Any:
        """
        Optimiza hiperparámetros del modelo.
        
        Args:
            X_train: Features de entrenamiento
            y_train: Target de entrenamiento
            
        Returns:
            Modelo optimizado
        """
        try:
            logger.info("🔧 Optimizando hiperparámetros...")
            
            # Definir parámetros según el tipo de modelo
            if self.config.model_type == "random_forest":
                param_grid = {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
            
            elif self.config.model_type == "gradient_boosting":
                param_grid = {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7],
                    'min_samples_split': [2, 5, 10]
                }
            
            elif self.config.model_type == "neural_network":
                param_grid = {
                    'hidden_layer_sizes': [(50,), (100,), (100, 50)],
                    'alpha': [0.001, 0.01, 0.1],
                    'learning_rate_init': [0.001, 0.01, 0.1]
                }
            
            else:
                logger.info("⚠️ Optimización de hiperparámetros no disponible para este tipo de modelo")
                return self.model
            
            # Validación cruzada temporal
            tscv = TimeSeriesSplit(n_splits=self.config.cv_folds)
            
            # Grid search
            grid_search = GridSearchCV(
                estimator=self.model,
                param_grid=param_grid,
                cv=tscv,
                scoring='r2',
                n_jobs=self.config.n_jobs,
                verbose=0
            )
            
            grid_search.fit(X_train, y_train)
            
            logger.info(f"✅ Mejores parámetros: {grid_search.best_params_}")
            logger.info(f"📊 Mejor score: {grid_search.best_score_:.4f}")
            
            return grid_search.best_estimator_
            
        except Exception as e:
            logger.error(f"Error en optimización de hiperparámetros: {e}")
            return self.model
    
    def _temporal_cross_validation(self, X: pd.DataFrame, y: pd.Series) -> np.ndarray:
        """
        Realiza validación cruzada temporal.
        
        Args:
            X: Features
            y: Target
            
        Returns:
            Array con scores de validación cruzada
        """
        try:
            tscv = TimeSeriesSplit(n_splits=self.config.cv_folds)
            cv_scores = cross_val_score(
                self.model, X, y, 
                cv=tscv, 
                scoring='r2',
                n_jobs=self.config.n_jobs
            )
            
            logger.info(f"📊 CV Scores: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            return cv_scores
            
        except Exception as e:
            logger.error(f"Error en validación cruzada: {e}")
            return np.array([0.0])
    
    def _analyze_feature_importance(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Analiza la importancia de las features.
        
        Args:
            X: Features
            y: Target
            
        Returns:
            Dict con importancia de features
        """
        try:
            if self.model is not None and hasattr(self.model, 'feature_importances_'):
                # Para modelos basados en árboles
                importance = self.model.feature_importances_
                feature_names = X.columns
                
                # Crear diccionario
                feature_importance = dict(zip(feature_names, importance))
                
                # Ordenar por importancia
                feature_importance = dict(
                    sorted(feature_importance.items(), 
                           key=lambda x: x[1], reverse=True)
                )
                
                logger.info(f"🎯 Top 5 features más importantes:")
                for i, (feature, imp) in enumerate(list(feature_importance.items())[:5]):
                    logger.info(f"   {i+1}. {feature}: {imp:.4f}")
                
                return feature_importance
            
            elif self.model is not None and hasattr(self.model, 'coef_'):
                # Para modelos lineales
                importance = np.abs(self.model.coef_)
                feature_names = X.columns
                
                feature_importance = dict(zip(feature_names, importance))
                feature_importance = dict(
                    sorted(feature_importance.items(), 
                           key=lambda x: x[1], reverse=True)
                )
                
                return feature_importance
                
            else:
                logger.warning("⚠️ No se puede calcular importancia de features para este modelo")
                return {}
            
        except Exception as e:
            logger.error(f"Error analizando importancia de features: {e}")
            return {}
    
    def _analyze_shap(self, X_test: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Analiza valores SHAP para interpretabilidad.
        
        Args:
            X_test: Features de test
            
        Returns:
            Valores SHAP o None
        """
        try:
            if self.model is not None and hasattr(self.model, 'predict'):
                # Crear explainer SHAP
                explainer = shap.TreeExplainer(self.model)
                shap_values = explainer.shap_values(X_test)
                
                logger.info(f"📊 Análisis SHAP completado: {shap_values.shape}")
                return shap_values
            
            else:
                logger.warning("⚠️ Análisis SHAP no disponible para este tipo de modelo")
                return None
                
        except Exception as e:
            logger.error(f"Error en análisis SHAP: {e}")
            return None
    
    def save_model(self) -> str:
        """
        Guarda el modelo entrenado.
        
        Returns:
            Ruta del modelo guardado
        """
        try:
            model_path = Path(self.config.model_path)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar modelo
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            # Guardar metadata
            metadata_path = model_path.with_suffix('.json')
            metadata = {
                'model_type': self.config.model_type,
                'target_column': self.config.target_column,
                'training_date': datetime.now().isoformat(),
                'model_params': self.model.get_params() if self.model is not None else {},
                'feature_names': list(self.model.feature_names_in_) if self.model is not None and hasattr(self.model, 'feature_names_in_') else [],
                'training_result': {
                    'r2_score': self.training_result.r2_score if self.training_result else None,
                    'mae': self.training_result.mae if self.training_result else None,
                    'rmse': self.training_result.rmse if self.training_result else None,
                    'cross_val_score': self.training_result.cross_val_score if self.training_result else None,
                    'training_time': self.training_result.training_time if self.training_result else None
                }
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"💾 Modelo guardado: {model_path}")
            return str(model_path)
            
        except Exception as e:
            logger.error(f"Error guardando modelo: {e}")
            raise
    
    def load_model(self, model_path: str) -> bool:
        """
        Carga un modelo guardado.
        
        Args:
            model_path: Ruta del modelo
            
        Returns:
            True si se cargó correctamente
        """
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            logger.info(f"📂 Modelo cargado: {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            return False
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Realiza predicciones con el modelo entrenado.
        
        Args:
            X: Features para predicción
            
        Returns:
            Array con predicciones
        """
        try:
            if self.model is None:
                raise ValueError("No hay modelo entrenado")
            
            # Preprocesar features
            X_scaled = self.scaler.transform(X)
            X_processed = pd.DataFrame(
                X_scaled, 
                columns=X.columns, 
                index=X.index
            )
            
            # Seleccionar features si hay selector
            if self.feature_selector is not None:
                X_processed = self.feature_selector.transform(X_processed)
                # Convertir a np.ndarray si es una lista para acceder a .shape
                if isinstance(X_processed, list):
                    X_processed = np.array(X_processed)
                if self.model is not None and hasattr(self.model, 'feature_names_in_') and len(self.model.feature_names_in_) == X_processed.shape[1]:
                    feature_names = list(self.model.feature_names_in_)
                    X_processed = pd.DataFrame(
                        X_processed,
                        columns=pd.Index(feature_names),
                        index=X.index
                    )
            
            # Realizar predicción
            predictions = self.model.predict(X_processed)
            
            logger.info(f"🔮 Predicciones realizadas: {len(predictions)}")
            return predictions
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información del modelo.
        
        Returns:
            Dict con información del modelo
        """
        if self.model is None:
            return {"error": "No hay modelo entrenado"}
        
        info = {
            "model_type": self.config.model_type,
            "target_column": self.config.target_column,
            "model_params": self.model.get_params() if self.model is not None else {},
            "feature_names": list(self.model.feature_names_in_) if self.model is not None and hasattr(self.model, 'feature_names_in_') else [],
            "n_features": len(self.model.feature_names_in_) if self.model is not None and hasattr(self.model, 'feature_names_in_') else 0
        }
        
        if self.training_result:
            info.update({
                "r2_score": self.training_result.r2_score,
                "mae": self.training_result.mae,
                "rmse": self.training_result.rmse,
                "cross_val_score": self.training_result.cross_val_score,
                "training_time": self.training_result.training_time,
                "feature_importance": self.training_result.feature_importance
            })
        
        return info 