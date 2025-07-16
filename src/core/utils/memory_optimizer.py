#!/usr/bin/env python3
"""
Optimizador de Memoria para Datasets Grandes
============================================

Sistema de optimización de memoria para manejar datasets grandes eficientemente:
- Reducción de tipos de datos
- Compresión de datos
- Gestión de memoria inteligente
- Monitoreo de uso de memoria
- Limpieza automática de memoria

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-15
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import psutil
import gc
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import warnings
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

@dataclass
class MemoryConfig:
    """Configuración del optimizador de memoria."""
    max_memory_usage_mb: int = 2048  # 2GB por defecto
    compression_threshold_mb: int = 100  # Comprimir datasets >100MB
    cleanup_threshold_percent: float = 80.0  # Limpiar cuando uso >80%
    enable_monitoring: bool = True
    auto_cleanup: bool = True
    optimize_dtypes: bool = True
    use_compression: bool = True

class MemoryOptimizer:
    """
    Optimizador de memoria para datasets grandes.
    
    Funcionalidades:
    - Reducción automática de tipos de datos
    - Compresión de datasets grandes
    - Monitoreo de uso de memoria
    - Limpieza automática
    - Gestión eficiente de memoria
    """
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        """
        Inicializa el optimizador de memoria.
        
        Args:
            config: Configuración del optimizador
        """
        self.config = config or MemoryConfig()
        self.memory_history = []
        self.optimization_stats = {
            'total_optimizations': 0,
            'memory_saved_mb': 0.0,
            'compression_ratio': 0.0
        }
        
        logger.info(f"🧠 Optimizador de memoria inicializado: {self.config.max_memory_usage_mb}MB límite")
    
    def optimize_dataframe(self, df: pd.DataFrame, 
                          target_memory_mb: Optional[float] = None) -> pd.DataFrame:
        """
        Optimiza un DataFrame para reducir uso de memoria.
        
        Args:
            df: DataFrame a optimizar
            target_memory_mb: Memoria objetivo en MB
            
        Returns:
            DataFrame optimizado
        """
        try:
            if df is None or df.empty:
                return df
            
            initial_memory = self._get_dataframe_memory_mb(df)
            logger.info(f"📊 Optimizando DataFrame: {df.shape}, memoria inicial: {initial_memory:.2f}MB")
            
            # Optimizar tipos de datos
            if self.config.optimize_dtypes:
                df_optimized = self._optimize_dtypes(df)
            else:
                df_optimized = df.copy()
            
            # Comprimir si es necesario
            if self.config.use_compression and initial_memory > self.config.compression_threshold_mb:
                df_optimized = self._compress_dataframe(df_optimized)
            
            # Verificar límite de memoria
            final_memory = self._get_dataframe_memory_mb(df_optimized)
            target_memory = target_memory_mb or self.config.max_memory_usage_mb
            
            if final_memory > target_memory:
                logger.warning(f"⚠️ Memoria final ({final_memory:.2f}MB) excede objetivo ({target_memory}MB)")
                df_optimized = self._reduce_dataframe_size(df_optimized, target_memory)
                final_memory = self._get_dataframe_memory_mb(df_optimized)
            
            # Actualizar estadísticas
            memory_saved = initial_memory - final_memory
            self.optimization_stats['total_optimizations'] += 1
            self.optimization_stats['memory_saved_mb'] += memory_saved
            self.optimization_stats['compression_ratio'] = final_memory / initial_memory if initial_memory > 0 else 1.0
            
            logger.info(f"✅ DataFrame optimizado: {df_optimized.shape}, "
                       f"memoria final: {final_memory:.2f}MB, "
                       f"ahorro: {memory_saved:.2f}MB ({memory_saved/initial_memory*100:.1f}%)")
            
            return df_optimized
            
        except Exception as e:
            logger.error(f"❌ Error optimizando DataFrame: {e}")
            return df
    
    def _optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimiza tipos de datos del DataFrame."""
        try:
            df_optimized = df.copy()
            
            # Optimizar columnas numéricas
            for col in df_optimized.select_dtypes(include=['int64']).columns:
                col_min = df_optimized[col].min()
                col_max = df_optimized[col].max()
                
                if col_min >= np.iinfo(np.int8).min and col_max <= np.iinfo(np.int8).max:
                    df_optimized[col] = df_optimized[col].astype(np.int8)
                elif col_min >= np.iinfo(np.int16).min and col_max <= np.iinfo(np.int16).max:
                    df_optimized[col] = df_optimized[col].astype(np.int16)
                elif col_min >= np.iinfo(np.int32).min and col_max <= np.iinfo(np.int32).max:
                    df_optimized[col] = df_optimized[col].astype(np.int32)
            
            # Optimizar columnas float
            for col in df_optimized.select_dtypes(include=['float64']).columns:
                df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
            
            # Optimizar columnas object
            for col in df_optimized.select_dtypes(include=['object']).columns:
                if df_optimized[col].nunique() / len(df_optimized) < 0.5:
                    df_optimized[col] = df_optimized[col].astype('category')
            
            logger.info("✅ Tipos de datos optimizados")
            return df_optimized
            
        except Exception as e:
            logger.error(f"❌ Error optimizando tipos de datos: {e}")
            return df
    
    def _compress_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Comprime DataFrame usando técnicas de compresión."""
        try:
            # Comprimir columnas categóricas
            for col in df.select_dtypes(include=['object']).columns:
                if df[col].nunique() / len(df) < 0.8:
                    df[col] = df[col].astype('category')
            
            # Comprimir columnas numéricas con muchos valores repetidos
            for col in df.select_dtypes(include=[np.number]).columns:
                if df[col].nunique() / len(df) < 0.3:
                    df[col] = df[col].astype('category')
            
            logger.info("✅ DataFrame comprimido")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error comprimiendo DataFrame: {e}")
            return df
    
    def _reduce_dataframe_size(self, df: pd.DataFrame, target_memory_mb: float) -> pd.DataFrame:
        """Reduce el tamaño del DataFrame para cumplir con el límite de memoria."""
        try:
            current_memory = self._get_dataframe_memory_mb(df)
            
            if current_memory <= target_memory_mb:
                return df
            
            # Calcular factor de reducción
            reduction_factor = target_memory_mb / current_memory
            
            # Reducir número de filas
            target_rows = int(len(df) * reduction_factor)
            if target_rows < 100:  # Mantener mínimo de filas
                target_rows = 100
            
            # Muestrear DataFrame
            df_reduced = df.sample(n=target_rows, random_state=42)
            
            logger.info(f"📉 DataFrame reducido: {len(df)} -> {len(df_reduced)} filas")
            return df_reduced
            
        except Exception as e:
            logger.error(f"❌ Error reduciendo DataFrame: {e}")
            return df
    
    def _get_dataframe_memory_mb(self, df: pd.DataFrame) -> float:
        """Obtiene el uso de memoria de un DataFrame en MB."""
        try:
            memory_usage = df.memory_usage(deep=True)
            total_memory = memory_usage.sum()
            return total_memory / (1024 * 1024)  # Convertir a MB
        except Exception as e:
            logger.error(f"❌ Error calculando memoria: {e}")
            return 0.0
    
    def monitor_memory_usage(self) -> Dict[str, Any]:
        """Monitorea el uso de memoria del sistema."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            memory_stats = {
                'rss_mb': memory_info.rss / (1024 * 1024),  # Memoria residente
                'vms_mb': memory_info.vms / (1024 * 1024),  # Memoria virtual
                'percent': process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / (1024 * 1024),
                'total_mb': psutil.virtual_memory().total / (1024 * 1024),
                'timestamp': time.time()
            }
            
            # Guardar historial
            self.memory_history.append(memory_stats)
            
            # Limpiar historial si es muy largo
            if len(self.memory_history) > 1000:
                self.memory_history = self.memory_history[-500:]
            
            # Limpieza automática si es necesario
            if self.config.auto_cleanup and memory_stats['percent'] > self.config.cleanup_threshold_percent:
                self._auto_cleanup()
            
            return memory_stats
            
        except Exception as e:
            logger.error(f"❌ Error monitoreando memoria: {e}")
            return {}
    
    def _auto_cleanup(self):
        """Limpieza automática de memoria."""
        try:
            logger.info("🧹 Ejecutando limpieza automática de memoria...")
            
            # Forzar garbage collection
            gc.collect()
            
            # Limpiar variables no utilizadas
            for name in list(globals().keys()):
                if name.startswith('temp_') or name.startswith('cache_'):
                    del globals()[name]
            
            logger.info("✅ Limpieza automática completada")
            
        except Exception as e:
            logger.error(f"❌ Error en limpieza automática: {e}")
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de optimización."""
        return {
            'optimization_stats': self.optimization_stats.copy(),
            'memory_history': self.memory_history[-10:],  # Últimos 10 registros
            'config': {
                'max_memory_usage_mb': self.config.max_memory_usage_mb,
                'compression_threshold_mb': self.config.compression_threshold_mb,
                'cleanup_threshold_percent': self.config.cleanup_threshold_percent,
                'auto_cleanup': self.config.auto_cleanup
            }
        }
    
    def clear_memory_history(self):
        """Limpia el historial de memoria."""
        self.memory_history.clear()
        logger.info("🗑️ Historial de memoria limpiado")
    
    def set_memory_limit(self, limit_mb: float):
        """Establece un nuevo límite de memoria."""
        self.config.max_memory_usage_mb = limit_mb
        logger.info(f"📏 Nuevo límite de memoria: {limit_mb}MB")

# Instancia global del optimizador
memory_optimizer = MemoryOptimizer()

def optimize_large_dataset(df: pd.DataFrame, 
                          target_memory_mb: Optional[float] = None) -> pd.DataFrame:
    """
    Función de utilidad para optimizar datasets grandes.
    
    Args:
        df: DataFrame a optimizar
        target_memory_mb: Memoria objetivo en MB
        
    Returns:
        DataFrame optimizado
    """
    return memory_optimizer.optimize_dataframe(df, target_memory_mb)

def get_memory_usage() -> Dict[str, Any]:
    """Obtiene el uso actual de memoria."""
    return memory_optimizer.monitor_memory_usage()

def get_optimization_stats() -> Dict[str, Any]:
    """Obtiene estadísticas de optimización."""
    return memory_optimizer.get_optimization_stats() 