"""
Memory Manager para optimización de memoria
Gestor de memoria para datasets grandes y operaciones complejas
"""

import gc
import psutil
import time
from typing import Any, Dict, List, Optional, Tuple
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Gestor de memoria para optimizar uso de memoria.
    
    Características:
    - Monitoreo de uso de memoria
    - Limpieza automática de memoria
    - Optimización de DataFrames
    - Gestión de datasets grandes
    """
    
    def __init__(self, max_memory_percent: float = 80.0):
        """
        Inicializa el gestor de memoria.
        
        Args:
            max_memory_percent: Porcentaje máximo de memoria a usar
        """
        self.max_memory_percent = max_memory_percent
        self.memory_history: List[Dict[str, float]] = []
        self.optimization_stats = {
            'dataframes_optimized': 0,
            'memory_freed_mb': 0.0,
            'gc_runs': 0
        }
        
        logger.info(f"MemoryManager inicializado (max: {max_memory_percent}%)")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        Obtiene información de uso de memoria.
        
        Returns:
            Diccionario con métricas de memoria
        """
        try:
            memory = psutil.virtual_memory()
            return {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percent': memory.percent,
                'free_gb': memory.free / (1024**3)
            }
        except Exception as e:
            logger.warning(f"Error obteniendo uso de memoria: {e}")
            return {
                'total_gb': 0.0,
                'available_gb': 0.0,
                'used_gb': 0.0,
                'percent': 0.0,
                'free_gb': 0.0
            }
    
    def is_memory_critical(self) -> bool:
        """
        Verifica si el uso de memoria es crítico.
        
        Returns:
            True si el uso de memoria es crítico
        """
        memory_info = self.get_memory_usage()
        return memory_info['percent'] > self.max_memory_percent
    
    def optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimiza un DataFrame para reducir uso de memoria.
        
        Args:
            df: DataFrame a optimizar
            
        Returns:
            DataFrame optimizado
        """
        try:
            original_memory = df.memory_usage(deep=True).sum() / (1024 * 1024)
            
            # Optimizar tipos de datos
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
                
                # Optimizar objetos (convertir a categorías si es posible)
                elif col_type == 'object':
                    if optimized_df[col].nunique() / len(optimized_df) < 0.5:
                        optimized_df[col] = optimized_df[col].astype('category')
            
            # Calcular ahorro de memoria
            optimized_memory = optimized_df.memory_usage(deep=True).sum() / (1024 * 1024)
            memory_saved = original_memory - optimized_memory
            
            self.optimization_stats['dataframes_optimized'] += 1
            self.optimization_stats['memory_freed_mb'] += memory_saved
            
            logger.info(f"✅ DataFrame optimizado: {original_memory:.2f}MB → {optimized_memory:.2f}MB (ahorro: {memory_saved:.2f}MB)")
            
            return optimized_df
            
        except Exception as e:
            logger.warning(f"Error optimizando DataFrame: {e}")
            return df
    
    def chunk_dataframe(self, df: pd.DataFrame, chunk_size: int = 1000) -> List[pd.DataFrame]:
        """
        Divide un DataFrame en chunks para procesamiento.
        
        Args:
            df: DataFrame a dividir
            chunk_size: Tamaño de cada chunk
            
        Returns:
            Lista de DataFrames chunks
        """
        try:
            chunks = []
            total_rows = len(df)
            
            for start_idx in range(0, total_rows, chunk_size):
                end_idx = min(start_idx + chunk_size, total_rows)
                chunk = df.iloc[start_idx:end_idx].copy()
                chunks.append(chunk)
            
            logger.info(f"DataFrame dividido en {len(chunks)} chunks de ~{chunk_size} filas")
            return chunks
            
        except Exception as e:
            logger.error(f"Error dividiendo DataFrame: {e}")
            return [df]
    
    def free_memory(self, force_gc: bool = True) -> float:
        """
        Libera memoria del sistema.
        
        Args:
            force_gc: Forzar garbage collection
            
        Returns:
            Memoria liberada en MB
        """
        try:
            memory_before = self.get_memory_usage()
            
            # Forzar garbage collection
            if force_gc:
                collected = gc.collect()
                self.optimization_stats['gc_runs'] += 1
                logger.debug(f"Garbage collection: {collected} objetos liberados")
            
            # Limpiar memoria del sistema
            if hasattr(psutil, 'virtual_memory'):
                # En algunos sistemas, esto puede ayudar
                pass
            
            memory_after = self.get_memory_usage()
            memory_freed = memory_before['used_gb'] - memory_after['used_gb']
            
            if memory_freed > 0:
                logger.info(f"✅ Memoria liberada: {memory_freed:.2f}GB")
                self.optimization_stats['memory_freed_mb'] += memory_freed * 1024
            
            return memory_freed * 1024  # Convertir a MB
            
        except Exception as e:
            logger.warning(f"Error liberando memoria: {e}")
            return 0.0
    
    def monitor_memory_usage(self, interval_seconds: int = 60) -> Dict[str, Any]:
        """
        Monitorea uso de memoria durante un intervalo.
        
        Args:
            interval_seconds: Intervalo de monitoreo en segundos
            
        Returns:
            Estadísticas de monitoreo
        """
        try:
            start_time = time.time()
            start_memory = self.get_memory_usage()
            
            # Registrar punto inicial
            self.memory_history.append({
                'timestamp': start_time,
                'memory_percent': start_memory['percent'],
                'used_gb': start_memory['used_gb']
            })
            
            # Esperar intervalo
            time.sleep(interval_seconds)
            
            # Registrar punto final
            end_time = time.time()
            end_memory = self.get_memory_usage()
            
            self.memory_history.append({
                'timestamp': end_time,
                'memory_percent': end_memory['percent'],
                'used_gb': end_memory['used_gb']
            })
            
            # Calcular estadísticas
            memory_change = end_memory['used_gb'] - start_memory['used_gb']
            time_elapsed = end_time - start_time
            
            stats = {
                'start_memory_gb': start_memory['used_gb'],
                'end_memory_gb': end_memory['used_gb'],
                'memory_change_gb': memory_change,
                'time_elapsed_seconds': time_elapsed,
                'memory_change_rate_gb_per_hour': (memory_change / time_elapsed) * 3600
            }
            
            logger.info(f"📊 Monitoreo de memoria: {memory_change:+.2f}GB en {time_elapsed:.1f}s")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error en monitoreo de memoria: {e}")
            return {}
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de optimización."""
        return {
            **self.optimization_stats,
            'current_memory_usage': self.get_memory_usage(),
            'memory_history_points': len(self.memory_history)
        }
    
    def clear_memory_history(self):
        """Limpia el historial de memoria."""
        self.memory_history.clear()
        logger.info("Historial de memoria limpiado")

# Instancia global del memory manager
memory_manager = MemoryManager() 