#!/usr/bin/env python3
"""
Paralelizador de Entrenamiento de Modelos
=========================================

Sistema de paralelización para entrenamiento eficiente de modelos ML:
- Entrenamiento paralelo de múltiples modelos
- Gestión de recursos de CPU
- Optimización de tiempo de entrenamiento
- Monitoreo de progreso en tiempo real
- Gestión de errores y recuperación

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-15
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from pathlib import Path
import warnings
from dataclasses import dataclass
import time
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp
from queue import Queue
import joblib
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score, mean_squared_error

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

@dataclass
class ParallelConfig:
    """Configuración del paralelizador."""
    max_workers: int = None  # None = usar todos los cores disponibles
    use_processes: bool = True  # True = ProcessPoolExecutor, False = ThreadPoolExecutor
    chunk_size: int = 1
    timeout_seconds: int = 3600  # 1 hora
    enable_progress_monitoring: bool = True
    save_intermediate_results: bool = True
    error_handling: str = 'continue'  # 'continue', 'stop', 'retry'

class ParallelTrainer:
    """
    Paralelizador de entrenamiento de modelos.
    
    Funcionalidades:
    - Entrenamiento paralelo de múltiples modelos
    - Gestión eficiente de recursos de CPU
    - Monitoreo de progreso en tiempo real
    - Gestión de errores y recuperación
    - Optimización de tiempo de entrenamiento
    """
    
    def __init__(self, config: Optional[ParallelConfig] = None):
        """
        Inicializa el paralelizador.
        
        Args:
            config: Configuración del paralelizador
        """
        self.config = config or ParallelConfig()
        
        # Configurar número de workers
        if self.config.max_workers is None:
            self.config.max_workers = mp.cpu_count()
        
        # Estadísticas de entrenamiento
        self.training_stats = {
            'total_models': 0,
            'completed_models': 0,
            'failed_models': 0,
            'total_time': 0.0,
            'average_time_per_model': 0.0
        }
        
        # Cola para monitoreo de progreso
        self.progress_queue = Queue()
        
        logger.info(f"⚡ Paralelizador inicializado: {self.config.max_workers} workers, "
                   f"{'procesos' if self.config.use_processes else 'hilos'}")
    
    def train_models_parallel(self, 
                            models_config: List[Dict[str, Any]],
                            data: pd.DataFrame,
                            target_column: str) -> Dict[str, Any]:
        """
        Entrena múltiples modelos en paralelo.
        
        Args:
            models_config: Lista de configuraciones de modelos
            data: DataFrame con datos de entrenamiento
            target_column: Columna objetivo
            
        Returns:
            Dict con resultados de entrenamiento
        """
        try:
            logger.info(f"🚀 Iniciando entrenamiento paralelo: {len(models_config)} modelos")
            
            start_time = time.time()
            self.training_stats['total_models'] = len(models_config)
            self.training_stats['completed_models'] = 0
            self.training_stats['failed_models'] = 0
            
            # Preparar datos para entrenamiento paralelo
            prepared_data = self._prepare_data_for_parallel(data, target_column)
            
            # Crear executor
            executor_class = ProcessPoolExecutor if self.config.use_processes else ThreadPoolExecutor
            results = {}
            
            with executor_class(max_workers=self.config.max_workers) as executor:
                # Enviar tareas
                future_to_model = {}
                for model_config in models_config:
                    future = executor.submit(
                        self._train_single_model_worker,
                        model_config,
                        prepared_data,
                        target_column
                    )
                    future_to_model[future] = model_config['model_type']
                
                # Procesar resultados
                for future in as_completed(future_to_model, timeout=self.config.timeout_seconds):
                    model_type = future_to_model[future]
                    
                    try:
                        result = future.result()
                        if result is not None:
                            results[model_type] = result
                            self.training_stats['completed_models'] += 1
                            logger.info(f"✅ {model_type} completado")
                        else:
                            self.training_stats['failed_models'] += 1
                            logger.error(f"❌ {model_type} falló")
                            
                    except Exception as e:
                        self.training_stats['failed_models'] += 1
                        logger.error(f"❌ Error en {model_type}: {e}")
                        
                        if self.config.error_handling == 'stop':
                            logger.error("🛑 Deteniendo entrenamiento por error")
                            break
                        elif self.config.error_handling == 'retry':
                            logger.info(f"🔄 Reintentando {model_type}")
                            # Implementar reintento aquí
            
            # Calcular estadísticas finales
            end_time = time.time()
            self.training_stats['total_time'] = end_time - start_time
            if self.training_stats['completed_models'] > 0:
                self.training_stats['average_time_per_model'] = (
                    self.training_stats['total_time'] / self.training_stats['completed_models']
                )
            
            logger.info(f"🎯 Entrenamiento paralelo completado: "
                       f"{self.training_stats['completed_models']}/{self.training_stats['total_models']} modelos, "
                       f"tiempo: {self.training_stats['total_time']:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en entrenamiento paralelo: {e}")
            return {}
    
    def _prepare_data_for_parallel(self, data: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """Prepara datos para entrenamiento paralelo."""
        try:
            # Separar features y target
            X = data.drop(columns=[target_column], errors='ignore')
            y = data[target_column]
            
            # Convertir a formato serializable
            prepared_data = {
                'X': X.to_dict('records'),
                'y': y.tolist(),
                'feature_names': list(X.columns),
                'target_name': target_column,
                'data_shape': X.shape
            }
            
            logger.info(f"📊 Datos preparados para paralelización: {X.shape}")
            return prepared_data
            
        except Exception as e:
            logger.error(f"❌ Error preparando datos: {e}")
            return {}
    
    def _train_single_model_worker(self, 
                                  model_config: Dict[str, Any],
                                  prepared_data: Dict[str, Any],
                                  target_column: str) -> Optional[Dict[str, Any]]:
        """Worker para entrenar un modelo individual."""
        try:
            model_type = model_config['model_type']
            logger.info(f"🤖 Worker iniciando {model_type}")
            
            # Reconstruir datos
            X = pd.DataFrame(prepared_data['X'])
            y = pd.Series(prepared_data['y'])
            
            # Crear y entrenar modelo
            model = self._create_model(model_config)
            if model is None:
                return None
            
            # División temporal
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Entrenar modelo
            start_time = time.time()
            model.fit(X, y)
            training_time = time.time() - start_time
            
            # Evaluar modelo
            training_score = model.score(X, y)
            
            # Validación cruzada temporal
            cv_scores = []
            for train_idx, val_idx in tscv.split(X):
                X_train_fold = X.iloc[train_idx]
                X_val_fold = X.iloc[val_idx]
                y_train_fold = y.iloc[train_idx]
                y_val_fold = y.iloc[val_idx]
                
                model_fold = self._create_model(model_config)
                model_fold.fit(X_train_fold, y_train_fold)
                score = model_fold.score(X_val_fold, y_val_fold)
                cv_scores.append(score)
            
            validation_score = np.mean(cv_scores)
            
            # Obtener importancia de features si está disponible
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                feature_importance = dict(zip(X.columns, model.feature_importances_))
            elif hasattr(model, 'coef_'):
                feature_importance = dict(zip(X.columns, np.abs(model.coef_)))
            
            # Crear resultado
            result = {
                'model_type': model_type,
                'training_score': float(training_score),
                'validation_score': float(validation_score),
                'training_time': training_time,
                'feature_importance': feature_importance,
                'model_params': model.get_params() if hasattr(model, 'get_params') else {},
                'timestamp': time.time()
            }
            
            logger.info(f"✅ {model_type} completado: val_score={validation_score:.4f}, "
                       f"time={training_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en worker {model_config.get('model_type', 'unknown')}: {e}")
            return None
    
    def _create_model(self, model_config: Dict[str, Any]):
        """Crea un modelo según la configuración."""
        try:
            model_type = model_config['model_type']
            
            if model_type == 'random_forest':
                from sklearn.ensemble import RandomForestRegressor
                return RandomForestRegressor(
                    n_estimators=model_config.get('n_estimators', 100),
                    max_depth=model_config.get('max_depth', 10),
                    random_state=42
                )
            
            elif model_type == 'gradient_boosting':
                from sklearn.ensemble import GradientBoostingRegressor
                return GradientBoostingRegressor(
                    n_estimators=model_config.get('n_estimators', 100),
                    learning_rate=model_config.get('learning_rate', 0.1),
                    random_state=42
                )
            
            elif model_type == 'linear_regression':
                from sklearn.linear_model import LinearRegression
                return LinearRegression()
            
            elif model_type == 'ridge_regression':
                from sklearn.linear_model import Ridge
                return Ridge(alpha=model_config.get('alpha', 1.0))
            
            elif model_type == 'lasso_regression':
                from sklearn.linear_model import Lasso
                return Lasso(alpha=model_config.get('alpha', 1.0))
            
            elif model_type == 'elastic_net':
                from sklearn.linear_model import ElasticNet
                return ElasticNet(
                    alpha=model_config.get('alpha', 1.0),
                    l1_ratio=model_config.get('l1_ratio', 0.5)
                )
            
            elif model_type == 'svr':
                from sklearn.svm import SVR
                return SVR(
                    kernel=model_config.get('kernel', 'rbf'),
                    C=model_config.get('C', 1.0)
                )
            
            elif model_type == 'neural_network':
                from sklearn.neural_network import MLPRegressor
                return MLPRegressor(
                    hidden_layer_sizes=model_config.get('hidden_layer_sizes', (100, 50)),
                    max_iter=model_config.get('max_iter', 500),
                    random_state=42
                )
            
            else:
                logger.error(f"❌ Tipo de modelo no soportado: {model_type}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creando modelo {model_config.get('model_type', 'unknown')}: {e}")
            return None
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de entrenamiento."""
        return {
            'training_stats': self.training_stats.copy(),
            'config': {
                'max_workers': self.config.max_workers,
                'use_processes': self.config.use_processes,
                'timeout_seconds': self.config.timeout_seconds,
                'error_handling': self.config.error_handling
            }
        }
    
    def monitor_progress(self) -> Dict[str, Any]:
        """Monitorea el progreso del entrenamiento."""
        try:
            progress = {
                'completed': self.training_stats['completed_models'],
                'total': self.training_stats['total_models'],
                'failed': self.training_stats['failed_models'],
                'progress_percent': (
                    self.training_stats['completed_models'] / self.training_stats['total_models'] * 100
                    if self.training_stats['total_models'] > 0 else 0
                ),
                'average_time': self.training_stats['average_time_per_model'],
                'total_time': self.training_stats['total_time']
            }
            
            return progress
            
        except Exception as e:
            logger.error(f"❌ Error monitoreando progreso: {e}")
            return {}
    
    def clear_stats(self):
        """Limpia las estadísticas de entrenamiento."""
        self.training_stats = {
            'total_models': 0,
            'completed_models': 0,
            'failed_models': 0,
            'total_time': 0.0,
            'average_time_per_model': 0.0
        }
        logger.info("🗑️ Estadísticas de entrenamiento limpiadas")

# Instancia global del paralelizador
parallel_trainer = ParallelTrainer()

def train_models_parallel(models_config: List[Dict[str, Any]],
                         data: pd.DataFrame,
                         target_column: str) -> Dict[str, Any]:
    """
    Función de utilidad para entrenar modelos en paralelo.
    
    Args:
        models_config: Lista de configuraciones de modelos
        data: DataFrame con datos de entrenamiento
        target_column: Columna objetivo
        
    Returns:
        Dict con resultados de entrenamiento
    """
    return parallel_trainer.train_models_parallel(models_config, data, target_column)

def get_training_stats() -> Dict[str, Any]:
    """Obtiene estadísticas de entrenamiento."""
    return parallel_trainer.get_training_stats()

def monitor_training_progress() -> Dict[str, Any]:
    """Monitorea el progreso del entrenamiento."""
    return parallel_trainer.monitor_progress() 