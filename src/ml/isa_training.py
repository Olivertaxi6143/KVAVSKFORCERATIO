#!/usr/bin/env python3
"""
Entrenamiento de Machine Learning para ISA (In-Sample Analysis)
==============================================================

Sistema de entrenamiento de modelos ML para predicción de rendimiento:
- Múltiples algoritmos de ML (Random Forest, XGBoost, Neural Networks)
- Validación temporal robusta
- Optimización de hiperparámetros
- Evaluación de modelos con métricas financieras
- Persistencia y carga de modelos entrenados

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-15
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
import warnings
import joblib
import json

# Scikit-learn imports
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.pipeline import Pipeline

# XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    warnings.warn("XGBoost no disponible - usando alternativas")

# LightGBM
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    warnings.warn("LightGBM no disponible - usando alternativas")

from src.data.ml_database import MLDatabase, MLDataset
from src.logger_config import setup_logger

logger = setup_logger(__name__)
warnings.filterwarnings('ignore')

@dataclass
class ModelConfig:
    """Configuración de modelo ML."""
    model_type: str = "random_forest"
    target_column: str = "Unified_Score"
    split_ratio: float = 0.7
    use_scaling: bool = True
    use_feature_selection: bool = False
    hyperparameter_tuning: bool = True
    cv_folds: int = 5
    random_state: int = 42

@dataclass
class TrainingResult:
    """Resultado del entrenamiento de modelo."""
    model_name: str
    model_type: str
    target_column: str
    training_score: float
    validation_score: float
    test_score: float
    feature_importance: Dict[str, float]
    hyperparameters: Dict[str, Any]
    training_time: float
    timestamp: datetime
    model_path: Optional[str] = None

class ISAModelTrainer:
    """
    Entrenador de modelos ML para análisis ISA.
    
    Funcionalidades:
    - Entrenamiento de múltiples algoritmos
    - Validación temporal robusta
    - Optimización de hiperparámetros
    - Evaluación con métricas financieras
    - Persistencia de modelos
    """
    
    def __init__(self, ml_database: MLDatabase, config: Optional[ModelConfig] = None):
        """
        Inicializa el entrenador de modelos.
        
        Args:
            ml_database: Instancia de la base de datos ML
            config: Configuración del modelo
        """
        self.ml_db = ml_database
        self.config = config or ModelConfig()
        self.models_dir = Path("models/isa")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Modelos disponibles
        self.available_models = self._setup_available_models()
        
        logger.info(f"🤖 Entrenador ISA inicializado: {len(self.available_models)} modelos disponibles")
    
    def _setup_available_models(self) -> Dict[str, Any]:
        """Configura los modelos disponibles."""
        models = {
            'random_forest': {
                'class': RandomForestRegressor,
                'default_params': {
                    'n_estimators': 100,
                    'max_depth': 10,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2,
                    'random_state': self.config.random_state
                },
                'param_grid': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
            },
            'gradient_boosting': {
                'class': GradientBoostingRegressor,
                'default_params': {
                    'n_estimators': 100,
                    'learning_rate': 0.1,
                    'max_depth': 5,
                    'random_state': self.config.random_state
                },
                'param_grid': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                }
            },
            'linear_regression': {
                'class': LinearRegression,
                'default_params': {},
                'param_grid': {}
            },
            'ridge_regression': {
                'class': Ridge,
                'default_params': {'alpha': 1.0},
                'param_grid': {'alpha': [0.1, 1.0, 10.0, 100.0]}
            },
            'lasso_regression': {
                'class': Lasso,
                'default_params': {'alpha': 1.0},
                'param_grid': {'alpha': [0.1, 1.0, 10.0, 100.0]}
            },
            'elastic_net': {
                'class': ElasticNet,
                'default_params': {'alpha': 1.0, 'l1_ratio': 0.5},
                'param_grid': {
                    'alpha': [0.1, 1.0, 10.0],
                    'l1_ratio': [0.1, 0.5, 0.9]
                }
            },
            'svr': {
                'class': SVR,
                'default_params': {'kernel': 'rbf', 'C': 1.0},
                'param_grid': {
                    'C': [0.1, 1.0, 10.0],
                    'gamma': ['scale', 'auto', 0.1, 0.01]
                }
            },
            'neural_network': {
                'class': MLPRegressor,
                'default_params': {
                    'hidden_layer_sizes': (100, 50),
                    'max_iter': 500,
                    'random_state': self.config.random_state
                },
                'param_grid': {
                    'hidden_layer_sizes': [(50,), (100,), (100, 50), (100, 50, 25)],
                    'alpha': [0.0001, 0.001, 0.01]
                }
            }
        }
        
        # Añadir XGBoost si está disponible
        if XGBOOST_AVAILABLE:
            models['xgboost'] = {
                'class': xgb.XGBRegressor,
                'default_params': {
                    'n_estimators': 100,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'random_state': self.config.random_state
                },
                'param_grid': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [3, 6, 9],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'subsample': [0.8, 0.9, 1.0]
                }
            }
        
        # Añadir LightGBM si está disponible
        if LIGHTGBM_AVAILABLE:
            models['lightgbm'] = {
                'class': lgb.LGBMRegressor,
                'default_params': {
                    'n_estimators': 100,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'random_state': self.config.random_state
                },
                'param_grid': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [3, 6, 9],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'num_leaves': [31, 50, 100]
                }
            }
        
        return models
    
    def train_model(self, 
                   model_type: Optional[str] = None,
                   target_column: Optional[str] = None,
                   use_cache: bool = True) -> Optional[TrainingResult]:
        """
        Entrena un modelo ML.
        
        Args:
            model_type: Tipo de modelo a entrenar
            target_column: Columna objetivo
            use_cache: Usar cache de datos
            
        Returns:
            TrainingResult: Resultado del entrenamiento
        """
        try:
            model_type = model_type or self.config.model_type
            target_column = target_column or self.config.target_column
            
            if model_type not in self.available_models:
                logger.error(f"❌ Modelo no disponible: {model_type}")
                return None
            
            # Cargar dataset
            dataset = self.ml_db.create_ml_dataset(
                target_column=target_column,
                split_ratio=self.config.split_ratio,
                use_cache=use_cache
            )
            
            if dataset is None:
                logger.error("❌ No se pudo crear dataset")
                return None
            
            logger.info(f"🚀 Entrenando modelo {model_type} para {target_column}")
            
            # Entrenar modelo
            start_time = datetime.now()
            result = self._train_single_model(model_type, dataset)
            training_time = (datetime.now() - start_time).total_seconds()
            
            if result is None:
                logger.error("❌ Error en entrenamiento")
                return None
            
            # Añadir información adicional
            result.training_time = training_time
            result.timestamp = datetime.now()
            
            # Guardar modelo
            model_path = self._save_model(result, model_type, target_column)
            result.model_path = model_path
            
            logger.info(f"✅ Modelo entrenado: {result.model_name}")
            logger.info(f"   Training Score: {result.training_score:.4f}")
            logger.info(f"   Validation Score: {result.validation_score:.4f}")
            logger.info(f"   Test Score: {result.test_score:.4f}")
            logger.info(f"   Tiempo: {training_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error entrenando modelo: {e}")
            return None
    
    def _train_single_model(self, model_type: str, dataset: MLDataset) -> Optional[TrainingResult]:
        """Entrena un modelo específico."""
        try:
            model_config = self.available_models[model_type]
            model_class = model_config['class']
            default_params = model_config['default_params']
            
            # Preparar datos
            X_train, X_test, y_train, y_test = self._prepare_data(dataset)
            
            # Crear pipeline
            pipeline = self._create_pipeline(model_class, default_params)
            
            # Entrenar modelo
            if self.config.hyperparameter_tuning:
                pipeline = self._optimize_hyperparameters(pipeline, model_type, X_train, y_train)
            else:
                pipeline.fit(X_train, y_train)
            
            # Evaluar modelo
            training_score = pipeline.score(X_train, y_train)
            validation_score = self._cross_validate(pipeline, X_train, y_train)
            test_score = pipeline.score(X_test, y_test)
            
            # Obtener importancia de features
            feature_importance = self._get_feature_importance(pipeline, dataset.feature_names)
            
            # Obtener hiperparámetros
            hyperparameters = self._get_hyperparameters(pipeline)
            
            # Crear resultado
            result = TrainingResult(
                model_name=f"{model_type}_{dataset.target_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                model_type=model_type,
                target_column=dataset.target_name,
                training_score=training_score,
                validation_score=validation_score,
                test_score=test_score,
                feature_importance=feature_importance,
                hyperparameters=hyperparameters,
                training_time=0.0,  # Se actualiza después
                timestamp=datetime.now()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error entrenando modelo {model_type}: {e}")
            return None
    
    def _prepare_data(self, dataset: MLDataset) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Prepara los datos para entrenamiento."""
        X_train = dataset.X_train.copy()
        X_test = dataset.X_test.copy()
        y_train = dataset.y_train.copy()
        y_test = dataset.y_test.copy()
        
        # Limpiar datos
        X_train = X_train.replace([np.inf, -np.inf], np.nan)
        X_test = X_test.replace([np.inf, -np.inf], np.nan)
        
        # Imputar valores faltantes
        X_train = X_train.fillna(X_train.median())
        X_test = X_test.fillna(X_test.median())
        
        return X_train, X_test, y_train, y_test
    
    def _create_pipeline(self, model_class: Any, default_params: Dict[str, Any]) -> Pipeline:
        """Crea pipeline de ML."""
        steps = []
        
        # Añadir escalado si está habilitado
        if self.config.use_scaling:
            steps.append(('scaler', RobustScaler()))
        
        # Añadir modelo
        steps.append(('model', model_class(**default_params)))
        
        return Pipeline(steps)
    
    def _optimize_hyperparameters(self, 
                                 pipeline: Pipeline, 
                                 model_type: str, 
                                 X: pd.DataFrame, 
                                 y: pd.Series) -> Pipeline:
        """Optimiza hiperparámetros del modelo."""
        try:
            param_grid = self.available_models[model_type]['param_grid']
            
            if not param_grid:
                logger.info("⚠️ No hay parámetros para optimizar")
                return pipeline
            
            # Configurar validación temporal
            tscv = TimeSeriesSplit(n_splits=self.config.cv_folds)
            
            # Buscar mejores parámetros
            grid_search = GridSearchCV(
                pipeline,
                param_grid,
                cv=tscv,
                scoring='r2',
                n_jobs=-1,
                verbose=0
            )
            
            grid_search.fit(X, y)
            
            logger.info(f"🎯 Mejores parámetros: {grid_search.best_params_}")
            logger.info(f"🎯 Mejor score CV: {grid_search.best_score_:.4f}")
            
            return grid_search.best_estimator_
            
        except Exception as e:
            logger.error(f"❌ Error optimizando hiperparámetros: {e}")
            return pipeline
    
    def _cross_validate(self, pipeline: Pipeline, X: pd.DataFrame, y: pd.Series) -> float:
        """Realiza validación cruzada temporal."""
        try:
            tscv = TimeSeriesSplit(n_splits=self.config.cv_folds)
            scores = []
            
            for train_idx, val_idx in tscv.split(X):
                X_train_fold = X.iloc[train_idx]
                X_val_fold = X.iloc[val_idx]
                y_train_fold = y.iloc[train_idx]
                y_val_fold = y.iloc[val_idx]
                
                pipeline.fit(X_train_fold, y_train_fold)
                score = pipeline.score(X_val_fold, y_val_fold)
                scores.append(score)
            
            return np.mean(scores)
            
        except Exception as e:
            logger.error(f"❌ Error en validación cruzada: {e}")
            return 0.0
    
    def _get_feature_importance(self, pipeline: Pipeline, feature_names: List[str]) -> Dict[str, float]:
        """Obtiene importancia de features."""
        try:
            model = pipeline.named_steps.get('model', pipeline)
            
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importance = np.abs(model.coef_)
            else:
                # Para modelos sin importancia de features
                importance = np.ones(len(feature_names)) / len(feature_names)
            
            # Crear diccionario
            feature_importance = {}
            for i, feature in enumerate(feature_names):
                if i < len(importance):
                    feature_importance[feature] = float(importance[i])
            
            # Ordenar por importancia
            feature_importance = dict(sorted(
                feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            
            return feature_importance
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo importancia de features: {e}")
            return {}
    
    def _get_hyperparameters(self, pipeline: Pipeline) -> Dict[str, Any]:
        """Obtiene hiperparámetros del modelo."""
        try:
            model = pipeline.named_steps.get('model', pipeline)
            return model.get_params()
        except Exception as e:
            logger.error(f"❌ Error obteniendo hiperparámetros: {e}")
            return {}
    
    def _save_model(self, result: TrainingResult, model_type: str, target_column: str) -> str:
        """Guarda el modelo entrenado."""
        try:
            # Crear nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_filename = f"{model_type}_{target_column}_{timestamp}.joblib"
            model_path = self.models_dir / model_filename
            
            # Guardar modelo
            joblib.dump(result, model_path)
            
            # Guardar metadatos
            metadata_path = model_path.with_suffix('.json')
            metadata = {
                'model_name': result.model_name,
                'model_type': result.model_type,
                'target_column': result.target_column,
                'training_score': result.training_score,
                'validation_score': result.validation_score,
                'test_score': result.test_score,
                'feature_importance': result.feature_importance,
                'hyperparameters': result.hyperparameters,
                'training_time': result.training_time,
                'timestamp': result.timestamp.isoformat(),
                'model_path': str(model_path)
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"💾 Modelo guardado: {model_path}")
            return str(model_path)
            
        except Exception as e:
            logger.error(f"❌ Error guardando modelo: {e}")
            return ""
    
    def load_model(self, model_path: str) -> Optional[TrainingResult]:
        """Carga un modelo guardado."""
        try:
            model_path_obj = Path(model_path)
            if not model_path_obj.exists():
                logger.error(f"❌ Modelo no encontrado: {model_path}")
                return None
            
            result = joblib.load(model_path_obj)
            logger.info(f"📂 Modelo cargado: {model_path}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {e}")
            return None
    
    def get_available_models(self) -> List[str]:
        """Obtiene lista de modelos disponibles."""
        return list(self.available_models.keys())
    
    def get_model_info(self, model_type: str) -> Dict[str, Any]:
        """Obtiene información de un modelo específico."""
        if model_type not in self.available_models:
            return {}
        
        model_config = self.available_models[model_type]
        return {
            'class': model_config['class'].__name__,
            'default_params': model_config['default_params'],
            'has_hyperparameter_tuning': bool(model_config['param_grid']),
            'param_grid': model_config['param_grid']
        }
    
    def compare_models(self, target_column: str = "Unified_Score") -> Dict[str, Any]:
        """Compara múltiples modelos."""
        try:
            results = {}
            
            for model_type in self.available_models.keys():
                logger.info(f"🔄 Entrenando {model_type}...")
                
                result = self.train_model(
                    model_type=model_type,
                    target_column=target_column,
                    use_cache=True
                )
                
                if result is not None:
                    results[model_type] = {
                        'training_score': result.training_score,
                        'validation_score': result.validation_score,
                        'test_score': result.test_score,
                        'training_time': result.training_time,
                        'feature_importance': result.feature_importance
                    }
            
            # Ordenar por test score
            sorted_results = dict(sorted(
                results.items(),
                key=lambda x: x[1]['test_score'],
                reverse=True
            ))
            
            logger.info("📊 Comparación de modelos completada")
            return sorted_results
            
        except Exception as e:
            logger.error(f"❌ Error comparando modelos: {e}")
            return {}
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de entrenamiento."""
        try:
            models_dir = Path(self.models_dir)
            model_files = list(models_dir.glob("*.joblib"))
            
            stats = {
                'total_models': len(model_files),
                'models_dir': str(models_dir),
                'available_models': self.get_available_models(),
                'recent_models': []
            }
            
            # Obtener modelos recientes
            for model_file in sorted(model_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                try:
                    result = joblib.load(model_file)
                    stats['recent_models'].append({
                        'name': result.model_name,
                        'type': result.model_type,
                        'target': result.target_column,
                        'test_score': result.test_score,
                        'timestamp': result.timestamp.isoformat()
                    })
                except Exception as e:
                    logger.warning(f"⚠️ Error cargando modelo {model_file}: {e}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {} 