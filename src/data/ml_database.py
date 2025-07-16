#!/usr/bin/env python3
"""
Base de Datos ML (Machine Learning) para Análisis Cuantitativo
==============================================================

Sistema de gestión de datos para entrenamiento de modelos ML:
- Almacenamiento estructurado de datos IS/OOS
- Gestión de features y targets para ML
- Validación temporal de datos
- Cache inteligente para optimización
- Exportación para entrenamiento
- Clasificación por tipo de activo

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 2.0.0
"""

import pandas as pd
import numpy as np
import sqlite3
import json
import pickle
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import warnings
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import IsolationForest
import hashlib

from src.logger_config import setup_logger

logger = setup_logger(__name__)
warnings.filterwarnings('ignore')

@dataclass
class MLDatabaseConfig:
    """Configuración de la base de datos ML."""
    db_path: str = "data/ml_database.db"
    cache_dir: str = "cache/ml"
    max_cache_size_mb: int = 500
    cache_ttl_hours: int = 24
    validation_strict: bool = True
    min_data_points: int = 50
    feature_columns: Optional[List[str]] = None
    target_columns: Optional[List[str]] = None
    temporal_split_ratio: float = 0.7
    outlier_detection: bool = True
    outlier_contamination: float = 0.1

@dataclass
class MLDataset:
    """Dataset estructurado para Machine Learning."""
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    feature_names: List[str]
    target_name: str
    split_ratio: float
    timestamp: datetime
    metadata: Dict[str, Any]

class MLDatabase:
    """
    Base de datos ML para gestión de datos de entrenamiento ML.
    
    Funcionalidades:
    - Almacenamiento estructurado de datos IS/OOS
    - Gestión de features y targets para ML
    - Validación temporal de datos
    - Cache inteligente para optimización
    - Exportación para entrenamiento
    - Clasificación por tipo de activo
    """
    
    def __init__(self, config: Optional[MLDatabaseConfig] = None):
        """
        Inicializa la base de datos ML.
        
        Args:
            config: Configuración de la base de datos
        """
        self.config = config or MLDatabaseConfig()
        self.db_path = Path(self.config.db_path)
        self.cache_dir = Path(self.config.cache_dir)
        
        # Crear directorios si no existen
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar base de datos
        self._init_database()
        
        # Configurar features y targets por defecto
        self._setup_default_columns()
        
        logger.info(f"🗄️ Base de datos ML inicializada: {self.db_path}")
    
    def _init_database(self):
        """Inicializa la estructura de la base de datos."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla principal de datos ML
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ml_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        strategy_name TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        data_hash TEXT UNIQUE NOT NULL,
                        features TEXT NOT NULL,
                        targets TEXT NOT NULL,
                        metadata TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabla de cache de datasets
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ml_datasets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        dataset_hash TEXT UNIQUE NOT NULL,
                        config_hash TEXT NOT NULL,
                        X_train_path TEXT NOT NULL,
                        X_test_path TEXT NOT NULL,
                        y_train_path TEXT NOT NULL,
                        y_test_path TEXT NOT NULL,
                        feature_names TEXT NOT NULL,
                        target_name TEXT NOT NULL,
                        split_ratio REAL NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        last_used TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabla de métricas de validación
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS validation_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        dataset_hash TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        validation_type TEXT NOT NULL,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabla de resultados avanzados de ML/IA
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ml_validation_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        analysis_type TEXT NOT NULL,
                        asset_type TEXT DEFAULT 'unknown',
                        parameters TEXT,
                        results_json TEXT NOT NULL,
                        description TEXT,
                        tags TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.debug("✅ Estructura de base de datos ML creada")
                
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos ML: {e}")
            raise
    
    def _setup_default_columns(self):
        """Configura las columnas por defecto para features y targets."""
        if self.config.feature_columns is None:
            self.config.feature_columns = [
                'CAGR_IS', 'Sharpe_Ratio_IS', 'Max_Drawdown_IS', 'Profit_Factor_IS',
                'Total_Trades_IS', 'Win_Rate_IS', 'Average_Trade_IS', 'Recovery_Factor_IS',
                'Calmar_Ratio_IS', 'Sortino_Ratio_IS', 'Risk_Reward_Ratio_IS'
            ]
        
        if self.config.target_columns is None:
            self.config.target_columns = [
                'CAGR_OOS', 'Sharpe_Ratio_OOS', 'Max_Drawdown_OOS', 'Profit_Factor_OOS',
                'Unified_Score', 'Factor_K_Score', 'QVA_Score'
            ]
    
    def store_ml_data(self, data: pd.DataFrame, strategy_name: str = "batch") -> bool:
        """
        Almacena datos ML en la base de datos.
        
        Args:
            data: DataFrame con datos IS/OOS
            strategy_name: Nombre de la estrategia o batch
            
        Returns:
            bool: True si se almacenó correctamente
        """
        try:
            # Validar datos
            if not self._validate_ml_data(data):
                logger.error("❌ Datos ML no válidos")
                return False
            
            # Preparar datos
            features = self._extract_features(data)
            targets = self._extract_targets(data)
            
            # Generar hash único
            data_hash = self._generate_data_hash(features, targets)
            
            # Verificar si ya existe
            if self._data_exists(data_hash):
                logger.warning(f"⚠️ Datos ya existen en la base de datos: {data_hash[:8]}")
                return True
            
            # Almacenar en base de datos
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO ml_data (strategy_name, timestamp, data_hash, features, targets, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    strategy_name,
                    datetime.now().isoformat(),
                    data_hash,
                    json.dumps(features.to_dict()),
                    json.dumps(targets.to_dict()),
                    json.dumps({
                        'shape': data.shape,
                        'feature_columns': list(features.columns),
                        'target_columns': list(targets.columns),
                        'validation_passed': True
                    })
                ))
                
                conn.commit()
            
            logger.info(f"✅ Datos ML almacenados: {len(data)} registros, hash: {data_hash[:8]}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error almacenando datos ML: {e}")
            return False
    
    def _validate_ml_data(self, data: pd.DataFrame) -> bool:
        """Valida que los datos ML cumplan los requisitos."""
        try:
            # Verificar columnas requeridas
            required_features = [col for col in self.config.feature_columns if col in data.columns]
            required_targets = [col for col in self.config.target_columns if col in data.columns]
            
            if len(required_features) < 3:
                logger.error(f"❌ Insuficientes features: {len(required_features)}/3")
                return False
            
            if len(required_targets) < 1:
                logger.error(f"❌ Sin targets válidos: {len(required_targets)}")
                return False
            
            # Verificar datos no nulos
            if data[required_features + required_targets].isnull().sum().sum() > 0:
                logger.warning("⚠️ Datos con valores nulos detectados")
            
            # Verificar tamaño mínimo
            if len(data) < self.config.min_data_points:
                logger.error(f"❌ Datos insuficientes: {len(data)}/{self.config.min_data_points}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validando datos ISA: {e}")
            return False
    
    def _extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extrae features de los datos."""
        available_features = [col for col in self.config.feature_columns if col in data.columns]
        features = data[available_features].copy()
        
        # Limpiar datos
        features = features.replace([np.inf, -np.inf], np.nan)
        features = features.fillna(features.median())
        
        return features
    
    def _extract_targets(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extrae targets de los datos."""
        available_targets = [col for col in self.config.target_columns if col in data.columns]
        targets = data[available_targets].copy()
        
        # Limpiar datos
        targets = targets.replace([np.inf, -np.inf], np.nan)
        targets = targets.fillna(targets.median())
        
        return targets
    
    def _generate_data_hash(self, features: pd.DataFrame, targets: pd.DataFrame) -> str:
        """Genera hash único para los datos."""
        data_str = f"{features.to_string()}{targets.to_string()}"
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _data_exists(self, data_hash: str) -> bool:
        """Verifica si los datos ya existen en la base de datos."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM isa_data WHERE data_hash = ?", (data_hash,))
                return cursor.fetchone()[0] > 0
        except Exception as e:
            logger.error(f"❌ Error verificando existencia de datos: {e}")
            return False
    
    def create_ml_dataset(self, 
                         target_column: str = 'Unified_Score',
                         split_ratio: Optional[float] = None,
                         use_cache: bool = True) -> Optional[MLDataset]:
        """
        Crea dataset para Machine Learning.
        
        Args:
            target_column: Columna objetivo para predicción
            split_ratio: Ratio de división temporal (None = usar config)
            use_cache: Usar cache si está disponible
            
        Returns:
            MLDataset: Dataset estructurado para ML
        """
        try:
            split_ratio = split_ratio or self.config.temporal_split_ratio
            
            # Verificar cache
            if use_cache:
                cached_dataset = self._get_cached_dataset(target_column, split_ratio)
                if cached_dataset is not None:
                    logger.info("✅ Dataset recuperado de cache")
                    return cached_dataset
            
            # Cargar datos de la base de datos
            data = self._load_all_ml_data()
            if data is None or len(data) == 0:
                logger.error("❌ No hay datos ML disponibles")
                return None
            
            # Crear dataset
            dataset = self._create_dataset_from_data(data, target_column, split_ratio)
            if dataset is None:
                logger.error("❌ Error creando dataset")
                return None
            
            # Guardar en cache
            if use_cache:
                self._cache_dataset(dataset, target_column, split_ratio)
            
            logger.info(f"✅ Dataset ML creado: {len(dataset.X_train)} train, {len(dataset.X_test)} test")
            return dataset
            
        except Exception as e:
            logger.error(f"❌ Error creando dataset ML: {e}")
            return None
    
    def _load_all_ml_data(self) -> Optional[pd.DataFrame]:
        """Carga todos los datos ML de la base de datos."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT features, targets, metadata 
                    FROM ml_data 
                    ORDER BY created_at DESC
                """
                
                results = pd.read_sql_query(query, conn)
                
                if len(results) == 0:
                    return None
                
                # Reconstruir DataFrame
                all_features = []
                all_targets = []
                
                for _, row in results.iterrows():
                    features = pd.DataFrame(json.loads(row['features']))
                    targets = pd.DataFrame(json.loads(row['targets']))
                    
                    all_features.append(features)
                    all_targets.append(targets)
                
                # Concatenar
                combined_features = pd.concat(all_features, ignore_index=True)
                combined_targets = pd.concat(all_targets, ignore_index=True)
                
                # Combinar features y targets
                combined_data = pd.concat([combined_features, combined_targets], axis=1)
                
                # Eliminar duplicados
                combined_data = combined_data.drop_duplicates()
                
                logger.info(f"📊 Datos ML cargados: {len(combined_data)} registros")
                return combined_data
                
        except Exception as e:
            logger.error(f"❌ Error cargando datos ML: {e}")
            return None
    
    def _create_dataset_from_data(self, 
                                 data: pd.DataFrame, 
                                 target_column: str, 
                                 split_ratio: float) -> Optional[MLDataset]:
        """Crea dataset ML a partir de los datos."""
        try:
            # Extraer features y target
            available_features = [col for col in self.config.feature_columns if col in data.columns]
            if target_column not in data.columns:
                logger.error(f"❌ Columna objetivo no encontrada: {target_column}")
                return None
            
            X = data[available_features].copy()
            y = data[target_column].copy()
            
            # Limpiar datos
            X = X.replace([np.inf, -np.inf], np.nan)
            X = X.fillna(X.median())
            y = y.replace([np.inf, -np.inf], np.nan)
            y = y.fillna(y.median())
            
            # Detección de outliers si está habilitada
            if self.config.outlier_detection:
                X, y = self._remove_outliers(X, y)
            
            # División temporal
            split_idx = int(len(X) * split_ratio)
            X_train = X.iloc[:split_idx]
            X_test = X.iloc[split_idx:]
            y_train = y.iloc[:split_idx]
            y_test = y.iloc[split_idx:]
            
            # Crear dataset
            dataset = MLDataset(
                X_train=X_train,
                X_test=X_test,
                y_train=y_train,
                y_test=y_test,
                feature_names=available_features,
                target_name=target_column,
                split_ratio=split_ratio,
                timestamp=datetime.now(),
                metadata={
                    'total_samples': len(X),
                    'train_samples': len(X_train),
                    'test_samples': len(X_test),
                    'features_count': len(available_features),
                    'outlier_detection': self.config.outlier_detection
                }
            )
            
            return dataset
            
        except Exception as e:
            logger.error(f"❌ Error creando dataset: {e}")
            return None
    
    def _remove_outliers(self, X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
        """Elimina outliers usando Isolation Forest."""
        try:
            # Combinar X e y para detección
            combined_data = pd.concat([X, y], axis=1)
            
            # Detectar outliers
            iso_forest = IsolationForest(
                contamination=self.config.outlier_contamination,
                random_state=42
            )
            outlier_labels = iso_forest.fit_predict(combined_data)
            
            # Filtrar outliers
            mask = outlier_labels != -1
            X_clean = X[mask]
            y_clean = y[mask]
            
            removed_count = len(X) - len(X_clean)
            if removed_count > 0:
                logger.info(f"🧹 Outliers removidos: {removed_count} ({removed_count/len(X)*100:.1f}%)")
            
            return X_clean, y_clean
            
        except Exception as e:
            logger.error(f"❌ Error removiendo outliers: {e}")
            return X, y
    
    def _get_cached_dataset(self, target_column: str, split_ratio: float) -> Optional[MLDataset]:
        """Recupera dataset del cache."""
        try:
            config_hash = self._generate_config_hash(target_column, split_ratio)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM ml_datasets 
                    WHERE config_hash = ? 
                    ORDER BY last_used DESC 
                    LIMIT 1
                """, (config_hash,))
                
                result = cursor.fetchone()
                if result is None:
                    return None
                
                # Verificar que los archivos existen
                X_train_path = Path(result[3])
                X_test_path = Path(result[4])
                y_train_path = Path(result[5])
                y_test_path = Path(result[6])
                
                if not all(path.exists() for path in [X_train_path, X_test_path, y_train_path, y_test_path]):
                    logger.warning("⚠️ Archivos de cache no encontrados")
                    return None
                
                # Cargar datos
                X_train = pd.read_pickle(X_train_path)
                X_test = pd.read_pickle(X_test_path)
                y_train = pd.read_pickle(y_train_path)
                y_test = pd.read_pickle(y_test_path)
                
                # Actualizar timestamp de uso
                cursor.execute("""
                    UPDATE ml_datasets 
                    SET last_used = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (result[0],))
                
                conn.commit()
                
                # Crear dataset
                dataset = MLDataset(
                    X_train=X_train,
                    X_test=X_test,
                    y_train=y_train,
                    y_test=y_test,
                    feature_names=json.loads(result[7]),
                    target_name=result[8],
                    split_ratio=result[9],
                    timestamp=datetime.fromisoformat(result[11]),
                    metadata={'from_cache': True}
                )
                
                return dataset
                
        except Exception as e:
            logger.error(f"❌ Error recuperando cache: {e}")
            return None
    
    def _cache_dataset(self, dataset: MLDataset, target_column: str, split_ratio: float):
        """Guarda dataset en cache."""
        try:
            config_hash = self._generate_config_hash(target_column, split_ratio)
            dataset_hash = self._generate_dataset_hash(dataset)
            
            # Crear nombres de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            X_train_path = self.cache_dir / f"X_train_{timestamp}.pkl"
            X_test_path = self.cache_dir / f"X_test_{timestamp}.pkl"
            y_train_path = self.cache_dir / f"y_train_{timestamp}.pkl"
            y_test_path = self.cache_dir / f"y_test_{timestamp}.pkl"
            
            # Guardar archivos
            dataset.X_train.to_pickle(X_train_path)
            dataset.X_test.to_pickle(X_test_path)
            dataset.y_train.to_pickle(y_train_path)
            dataset.y_test.to_pickle(y_test_path)
            
            # Guardar en base de datos
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO ml_datasets 
                    (dataset_hash, config_hash, X_train_path, X_test_path, y_train_path, y_test_path,
                     feature_names, target_name, split_ratio, created_at, last_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    dataset_hash,
                    config_hash,
                    str(X_train_path),
                    str(X_test_path),
                    str(y_train_path),
                    str(y_test_path),
                    json.dumps(dataset.feature_names),
                    dataset.target_name,
                    dataset.split_ratio
                ))
                
                conn.commit()
            
            logger.info(f"💾 Dataset cacheado: {dataset_hash[:8]}")
            
        except Exception as e:
            logger.error(f"❌ Error cacheando dataset: {e}")
    
    def _generate_config_hash(self, target_column: str, split_ratio: float) -> str:
        """Genera hash de configuración."""
        config_str = f"{target_column}_{split_ratio}_{self.config.outlier_detection}_{self.config.outlier_contamination}"
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def _generate_dataset_hash(self, dataset: MLDataset) -> str:
        """Genera hash del dataset."""
        dataset_str = f"{len(dataset.X_train)}_{len(dataset.X_test)}_{dataset.target_name}_{dataset.split_ratio}"
        return hashlib.md5(dataset_str.encode()).hexdigest()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la base de datos ISA."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Estadísticas de datos ML
                cursor.execute("SELECT COUNT(*) FROM ml_data")
                ml_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM ml_datasets")
                dataset_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM validation_metrics")
                metrics_count = cursor.fetchone()[0]
                
                # Estadísticas por tipo de activo
                cursor.execute("""
                    SELECT asset_type, COUNT(*) as count 
                    FROM ml_validation_results 
                    GROUP BY asset_type
                """)
                asset_type_stats = dict(cursor.fetchall())
                
                # Tamaño de la base de datos
                db_size = self.db_path.stat().st_size / (1024 * 1024)  # MB
                
                return {
                    'ml_records': ml_count,
                    'ml_datasets': dataset_count,
                    'validation_metrics': metrics_count,
                    'asset_type_stats': asset_type_stats,
                    'db_size_mb': round(db_size, 2),
                    'cache_dir': str(self.cache_dir),
                    'config': asdict(self.config)
                }
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def clear_cache(self) -> bool:
        """Limpia el cache de datasets."""
        try:
            # Eliminar archivos de cache
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            
            # Limpiar base de datos
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ml_datasets")
                conn.commit()
            
            logger.info("🧹 Cache limpiado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error limpiando cache: {e}")
            return False 

    def store_ml_validation_result(self, analysis_type: str, parameters: dict, results: dict, asset_type: str = "unknown", description: str = "", tags: str = "") -> bool:
        """
        Almacena un resultado avanzado de ML/IA en la base de datos.
        
        Args:
            analysis_type: Tipo de análisis (regime_detection, data_drift, walk_forward, etc.)
            parameters: Parámetros del análisis
            results: Resultados del análisis
            asset_type: Tipo de activo (indices, forex, commodities, crypto, unknown)
            description: Descripción opcional
            tags: Tags opcionales
            
        Returns:
            bool: True si se almacenó correctamente
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO ml_validation_results (analysis_type, asset_type, parameters, results_json, description, tags)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        analysis_type,
                        asset_type,
                        json.dumps(parameters, default=str),
                        json.dumps(results, default=str),
                        description,
                        tags
                    )
                )
                conn.commit()
            logger.info(f"✅ Resultado ML almacenado: {analysis_type} - {asset_type}")
            return True
        except Exception as e:
            logger.error(f"❌ Error almacenando resultado ML: {e}")
            return False

    def get_ml_validation_results(self, analysis_type: str = None, asset_type: str = None, tags: str = None, date_range: tuple = None) -> list:
        """
        Consulta resultados avanzados de ML/IA almacenados.
        
        Args:
            analysis_type: Filtrar por tipo de análisis
            asset_type: Filtrar por tipo de activo (indices, forex, commodities, crypto, unknown)
            tags: Filtrar por tags
            date_range: Rango de fechas (start_date, end_date)
            
        Returns:
            list: Lista de resultados filtrados
        """
        try:
            query = "SELECT * FROM ml_validation_results WHERE 1=1"
            params = []
            
            if analysis_type:
                query += " AND analysis_type = ?"
                params.append(analysis_type)
            
            if asset_type:
                query += " AND asset_type = ?"
                params.append(asset_type)
            
            if tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tags}%")
            
            if date_range:
                query += " AND created_at BETWEEN ? AND ?"
                params.extend(date_range)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convertir a lista de dicts
                results = []
                for row in rows:
                    results.append({
                        'id': row[0],
                        'analysis_type': row[1],
                        'asset_type': row[2],
                        'parameters': json.loads(row[3]) if row[3] else {},
                        'results': json.loads(row[4]) if row[4] else {},
                        'description': row[5],
                        'tags': row[6],
                        'created_at': row[7]
                    })
                return results
        except Exception as e:
            logger.error(f"❌ Error consultando resultados ML: {e}")
            return [] 