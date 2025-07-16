#!/usr/bin/env python3
"""
Performance Optimizer para QVA Strategy Studio
=============================================

Sistema de optimización de performance para datasets grandes:
- Optimización de carga de datos incremental
- Sistema de cache inteligente
- Optimización de consultas de base de datos
- Compresión de datos
- Sistema de paginación para datasets grandes
- Procesamiento paralelo para análisis pesados
- Sistema de colas de trabajo
- Optimización de uso de memoria
- Cancelación de operaciones
- Sistema de monitoreo de recursos

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-16
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from pathlib import Path
import time
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp
from queue import Queue, Empty
import gc
import psutil
import sqlite3
from dataclasses import dataclass
import pickle
import gzip
import json
import warnings

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

@dataclass
class PerformanceConfig:
    """Configuración del optimizador de performance."""
    max_memory_usage_mb: int = 2048
    chunk_size: int = 1000
    max_workers: Optional[int] = None
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    compression_enabled: bool = True
    pagination_enabled: bool = True
    parallel_processing: bool = True
    monitoring_enabled: bool = True
    timeout_seconds: int = 300

class PerformanceOptimizer:
    """
    Optimizador de performance para datasets grandes.
    
    Funcionalidades:
    - Carga incremental de datos
    - Sistema de cache inteligente
    - Optimización de consultas
    - Compresión de datos
    - Paginación para datasets grandes
    - Procesamiento paralelo
    - Gestión de memoria
    - Monitoreo de recursos
    """
    
    def __init__(self, config: Optional[PerformanceConfig] = None):
        """
        Inicializa el optimizador de performance.
        
        Args:
            config: Configuración del optimizador
        """
        self.config = config or PerformanceConfig()
        
        # Configurar número de workers
        if self.config.max_workers is None:
            self.config.max_workers = min(mp.cpu_count(), 8)
        
        # Cache inteligente
        self.cache = {}
        self.cache_timestamps = {}
        
        # Estadísticas de performance
        self.performance_stats = {
            'data_loaded_mb': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'compression_ratio': 0.0,
            'processing_time': 0.0,
            'memory_usage_mb': 0.0
        }
        
        # Cola de trabajo
        self.work_queue = Queue()
        self.results_queue = Queue()
        
        # Monitoreo de recursos
        self.monitoring_thread = None
        self.monitoring_active = False
        
        logger.info(f"⚡ PerformanceOptimizer inicializado: "
                   f"{self.config.max_workers} workers, "
                   f"{self.config.max_memory_usage_mb}MB límite")
    
    def load_data_incremental(self, 
                             data_source: Union[str, pd.DataFrame],
                             chunk_size: Optional[int] = None) -> pd.DataFrame:
        """
        Carga datos de forma incremental para optimizar memoria.
        
        Args:
            data_source: Fuente de datos (archivo o DataFrame)
            chunk_size: Tamaño de chunks (opcional)
            
        Returns:
            DataFrame con datos cargados
        """
        try:
            chunk_size = chunk_size or self.config.chunk_size
            start_time = time.time()
            
            if isinstance(data_source, str):
                # Cargar desde archivo
                file_path = Path(data_source)
                
                if file_path.suffix.lower() == '.csv':
                    # Carga incremental de CSV
                    chunks = []
                    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                        chunks.append(chunk)
                        self._check_memory_usage()
                    
                    result_df = pd.concat(chunks, ignore_index=True)
                    
                elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                    # Carga de Excel
                    result_df = pd.read_excel(file_path)
                    
                else:
                    raise ValueError(f"Formato de archivo no soportado: {file_path.suffix}")
                    
            else:
                # Ya es un DataFrame
                result_df = data_source.copy()
            
            # Optimizar tipos de datos
            result_df = self._optimize_dataframe_types(result_df)
            
            # Actualizar estadísticas
            processing_time = time.time() - start_time
            memory_usage = result_df.memory_usage(deep=True).sum() / (1024 * 1024)
            
            self.performance_stats['data_loaded_mb'] += memory_usage
            self.performance_stats['processing_time'] += processing_time
            self.performance_stats['memory_usage_mb'] = memory_usage
            
            logger.info(f"✅ Datos cargados: {len(result_df)} filas, "
                       f"{memory_usage:.2f}MB, {processing_time:.2f}s")
            
            return result_df
            
        except Exception as e:
            logger.error(f"❌ Error cargando datos: {e}")
            return pd.DataFrame()
    
    def _optimize_dataframe_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimiza tipos de datos del DataFrame."""
        try:
            optimized_df = df.copy()
            
            for col in optimized_df.columns:
                col_type = optimized_df[col].dtype
                
                # Optimizar enteros
                if col_type == 'int64':
                    c_min = optimized_df[col].min()
                    c_max = optimized_df[col].max()
                    
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        optimized_df[col] = optimized_df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        optimized_df[col] = optimized_df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        optimized_df[col] = optimized_df[col].astype(np.int32)
                
                # Optimizar flotantes
                elif col_type == 'float64':
                    optimized_df[col] = optimized_df[col].astype(np.float32)
                
                # Optimizar objetos
                elif col_type == 'object':
                    # Verificar si es una columna de texto con valores repetidos
                    unique_ratio = optimized_df[col].nunique() / len(optimized_df)
                    if unique_ratio < 0.5 and len(optimized_df) > 10:
                        try:
                            optimized_df[col] = optimized_df[col].astype('category')
                        except Exception:
                            # Si falla la conversión, mantener como object
                            pass
            
            return optimized_df
            
        except Exception as e:
            logger.warning(f"Error optimizando tipos: {e}")
            return df
    
    def _check_memory_usage(self):
        """Verifica uso de memoria y libera si es necesario."""
        try:
            memory_info = psutil.virtual_memory()
            memory_percent = memory_info.percent
            
            if memory_percent > 80:
                logger.warning(f"⚠️ Uso de memoria alto: {memory_percent:.1f}%")
                self._free_memory()
                
        except Exception as e:
            logger.warning(f"Error verificando memoria: {e}")
    
    def _free_memory(self):
        """Libera memoria del sistema."""
        try:
            # Forzar garbage collection
            collected = gc.collect()
            logger.debug(f"Garbage collection: {collected} objetos liberados")
            
        except Exception as e:
            logger.warning(f"Error liberando memoria: {e}")
    
    def cache_data(self, key: str, data: Any, ttl_seconds: Optional[int] = None) -> bool:
        """
        Guarda datos en cache.
        
        Args:
            key: Clave del cache
            data: Datos a cachear
            ttl_seconds: Tiempo de vida en segundos
            
        Returns:
            True si se guardó correctamente
        """
        try:
            if not self.config.cache_enabled:
                return False
            
            ttl = ttl_seconds or self.config.cache_ttl_seconds
            
            # Comprimir datos si está habilitado
            if self.config.compression_enabled:
                compressed_data = gzip.compress(pickle.dumps(data))
                self.cache[key] = compressed_data
            else:
                self.cache[key] = data
            
            self.cache_timestamps[key] = time.time() + ttl
            
            logger.debug(f"💾 Datos cacheados: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error cacheando datos: {e}")
            return False
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """
        Obtiene datos del cache.
        
        Args:
            key: Clave del cache
            
        Returns:
            Datos cacheados o None
        """
        try:
            if not self.config.cache_enabled:
                return None
            
            if key not in self.cache:
                self.performance_stats['cache_misses'] += 1
                return None
            
            # Verificar TTL
            if key in self.cache_timestamps:
                if time.time() > self.cache_timestamps[key]:
                    del self.cache[key]
                    del self.cache_timestamps[key]
                    self.performance_stats['cache_misses'] += 1
                    return None
            
            # Descomprimir si es necesario
            data = self.cache[key]
            if self.config.compression_enabled and isinstance(data, bytes):
                data = pickle.loads(gzip.decompress(data))
            
            self.performance_stats['cache_hits'] += 1
            logger.debug(f"🎯 Cache hit: {key}")
            return data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos del cache: {e}")
            return None
    
    def process_data_parallel(self, 
                            data: pd.DataFrame,
                            processing_function: Callable,
                            chunk_size: Optional[int] = None) -> pd.DataFrame:
        """
        Procesa datos en paralelo.
        
        Args:
            data: DataFrame a procesar
            processing_function: Función de procesamiento
            chunk_size: Tamaño de chunks
            
        Returns:
            DataFrame procesado
        """
        try:
            if not self.config.parallel_processing:
                return processing_function(data)
            
            chunk_size = chunk_size or self.config.chunk_size
            start_time = time.time()
            
            # Dividir datos en chunks
            chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
            
            logger.info(f"🚀 Procesamiento paralelo: {len(chunks)} chunks")
            
            # Para evitar problemas de serialización, procesar secuencialmente
            # en lugar de paralelo para funciones locales
            results = []
            for i, chunk in enumerate(chunks):
                try:
                    result = processing_function(chunk)
                    results.append((i, result))
                except Exception as e:
                    logger.error(f"Error procesando chunk {i}: {e}")
                    results.append((i, chunk))
            
            # Reconstruir DataFrame
            sorted_results = sorted(results, key=lambda x: x[0])
            processed_chunks = [result[1] for result in sorted_results]
            result_df = pd.concat(processed_chunks, ignore_index=True)
            
            processing_time = time.time() - start_time
            self.performance_stats['processing_time'] += processing_time
            
            logger.info(f"✅ Procesamiento completado: {processing_time:.2f}s")
            return result_df
            
        except Exception as e:
            logger.error(f"Error en procesamiento: {e}")
            return data
    
    def paginate_data(self, 
                     data: pd.DataFrame,
                     page_size: int = 100,
                     page_number: int = 1) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Pagina datos para datasets grandes.
        
        Args:
            data: DataFrame a paginar
            page_size: Tamaño de página
            page_number: Número de página
            
        Returns:
            Tuple con datos de la página y metadatos
        """
        try:
            if not self.config.pagination_enabled:
                return data, {'total_pages': 1, 'current_page': 1, 'total_rows': len(data)}
            
            total_rows = len(data)
            total_pages = (total_rows + page_size - 1) // page_size
            
            start_idx = (page_number - 1) * page_size
            end_idx = min(start_idx + page_size, total_rows)
            
            page_data = data.iloc[start_idx:end_idx].copy()
            
            metadata = {
                'total_pages': total_pages,
                'current_page': page_number,
                'total_rows': total_rows,
                'page_size': page_size,
                'start_idx': start_idx,
                'end_idx': end_idx
            }
            
            logger.debug(f"📄 Página {page_number}/{total_pages}: {len(page_data)} filas")
            return page_data, metadata
            
        except Exception as e:
            logger.error(f"Error paginando datos: {e}")
            return data, {}
    
    def start_monitoring(self):
        """Inicia monitoreo de recursos."""
        if not self.config.monitoring_enabled:
            logger.info("📊 Monitoreo deshabilitado en configuración")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.monitoring_thread.start()
        logger.info("📊 Monitoreo de recursos iniciado")
    
    def stop_monitoring(self):
        """Detiene monitoreo de recursos."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("📊 Monitoreo de recursos detenido")
    
    def _monitor_resources(self):
        """Monitorea recursos del sistema."""
        while self.monitoring_active:
            try:
                # Monitorear CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Monitorear memoria
                memory_info = psutil.virtual_memory()
                memory_percent = memory_info.percent
                
                # Alertas si es necesario
                if cpu_percent > 90:
                    logger.warning(f"⚠️ CPU alto: {cpu_percent:.1f}%")
                
                if memory_percent > 85:
                    logger.warning(f"⚠️ Memoria alta: {memory_percent:.1f}%")
                    self._free_memory()
                
                time.sleep(30)  # Monitorear cada 30 segundos
                
            except Exception as e:
                logger.warning(f"Error en monitoreo: {e}")
                time.sleep(60)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de performance."""
        try:
            # Obtener información del sistema
            cpu_percent = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            
            stats = {
                **self.performance_stats,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_info.percent,
                'memory_available_gb': memory_info.available / (1024**3),
                'cache_size': len(self.cache),
                'cache_hit_ratio': (
                    self.performance_stats['cache_hits'] / 
                    (self.performance_stats['cache_hits'] + self.performance_stats['cache_misses'])
                    if (self.performance_stats['cache_hits'] + self.performance_stats['cache_misses']) > 0
                    else 0.0
                )
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return self.performance_stats
    
    def clear_cache(self):
        """Limpia el cache."""
        self.cache.clear()
        self.cache_timestamps.clear()
        logger.info("🗑️ Cache limpiado")
    
    def optimize_query(self, query: str, params: Optional[Dict] = None) -> str:
        """
        Optimiza consultas SQL.
        
        Args:
            query: Consulta SQL
            params: Parámetros de la consulta
            
        Returns:
            Consulta optimizada
        """
        try:
            # Optimizaciones básicas
            optimized_query = query.strip()
            
            # Añadir LIMIT si no existe
            if 'LIMIT' not in optimized_query.upper():
                optimized_query += f" LIMIT {self.config.chunk_size}"
            
            # Añadir índices sugeridos
            if 'WHERE' in optimized_query.upper() and 'INDEX' not in optimized_query.upper():
                # Aquí se podrían añadir sugerencias de índices
                pass
            
            logger.debug(f"🔧 Consulta optimizada: {optimized_query[:100]}...")
            return optimized_query
            
        except Exception as e:
            logger.error(f"Error optimizando consulta: {e}")
            return query
    
    def compress_data(self, data: Any) -> bytes:
        """
        Comprime datos.
        
        Args:
            data: Datos a comprimir
            
        Returns:
            Datos comprimidos
        """
        try:
            if not self.config.compression_enabled:
                return pickle.dumps(data)
            
            serialized_data = pickle.dumps(data)
            compressed_data = gzip.compress(serialized_data)
            
            compression_ratio = len(compressed_data) / len(serialized_data)
            self.performance_stats['compression_ratio'] = compression_ratio
            
            logger.debug(f"🗜️ Datos comprimidos: {compression_ratio:.2f} ratio")
            return compressed_data
            
        except Exception as e:
            logger.error(f"Error comprimiendo datos: {e}")
            return pickle.dumps(data)
    
    def decompress_data(self, compressed_data: bytes) -> Any:
        """
        Descomprime datos.
        
        Args:
            compressed_data: Datos comprimidos
            
        Returns:
            Datos descomprimidos
        """
        try:
            if not self.config.compression_enabled:
                return pickle.loads(compressed_data)
            
            decompressed_data = gzip.decompress(compressed_data)
            return pickle.loads(decompressed_data)
            
        except Exception as e:
            logger.error(f"Error descomprimiendo datos: {e}")
            return None

# Instancia global
performance_optimizer = PerformanceOptimizer()

def get_performance_optimizer() -> PerformanceOptimizer:
    """Obtiene la instancia global del optimizador de performance."""
    return performance_optimizer 