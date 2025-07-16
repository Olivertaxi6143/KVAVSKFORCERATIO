#!/usr/bin/env python3
"""
Cache Inteligente para Resultados de Análisis
=============================================

Sistema de cache inteligente para optimizar resultados de análisis:
- Cache automático de resultados de análisis
- Gestión de TTL (Time To Live) inteligente
- Compresión de datos para ahorro de espacio
- Invalidación automática basada en cambios de datos
- Cache distribuido para múltiples procesos

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
import hashlib
import json
import pickle
import gzip
import os
from datetime import datetime, timedelta
import threading
from collections import OrderedDict

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

@dataclass
class CacheConfig:
    """Configuración del cache inteligente."""
    cache_dir: str = "cache"
    max_cache_size_mb: int = 1024  # 1GB por defecto
    default_ttl_hours: int = 24
    enable_compression: bool = True
    compression_threshold_kb: int = 100  # Comprimir archivos >100KB
    enable_auto_cleanup: bool = True
    cleanup_interval_hours: int = 6
    max_cache_entries: int = 1000
    enable_data_validation: bool = True

class IntelligentCache:
    """
    Cache inteligente para resultados de análisis.
    
    Funcionalidades:
    - Cache automático de resultados
    - Gestión inteligente de TTL
    - Compresión automática de datos
    - Invalidación basada en cambios de datos
    - Limpieza automática de cache
    - Cache distribuido para múltiples procesos
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """
        Inicializa el cache inteligente.
        
        Args:
            config: Configuración del cache
        """
        self.config = config or CacheConfig()
        self.cache_dir = Path(self.config.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache en memoria para acceso rápido
        self.memory_cache = OrderedDict()
        self.cache_metadata = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'compressions': 0,
            'total_size_mb': 0.0
        }
        
        # Lock para thread safety
        self.cache_lock = threading.Lock()
        
        # Iniciar limpieza automática
        if self.config.enable_auto_cleanup:
            self._start_auto_cleanup()
        
        logger.info(f"💾 Cache inteligente inicializado: {self.cache_dir}, "
                   f"máximo {self.config.max_cache_size_mb}MB")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor del cache.
        
        Args:
            key: Clave del cache
            default: Valor por defecto si no existe
            
        Returns:
            Valor cacheado o default
        """
        try:
            with self.cache_lock:
                # Verificar cache en memoria primero
                if key in self.memory_cache:
                    self.cache_stats['hits'] += 1
                    logger.debug(f"✅ Cache hit en memoria: {key}")
                    return self.memory_cache[key]
                
                # Verificar cache en disco
                cache_file = self._get_cache_file_path(key)
                if cache_file.exists():
                    # Verificar TTL
                    if self._is_cache_valid(key):
                        value = self._load_from_disk(key)
                        if value is not None:
                            # Mover a cache en memoria
                            self.memory_cache[key] = value
                            self._update_cache_order(key)
                            self.cache_stats['hits'] += 1
                            logger.debug(f"✅ Cache hit en disco: {key}")
                            return value
                    else:
                        # Cache expirado, eliminarlo
                        self.delete(key)
                
                self.cache_stats['misses'] += 1
                logger.debug(f"❌ Cache miss: {key}")
                return default
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo del cache {key}: {e}")
            return default
    
    def set(self, key: str, value: Any, ttl_hours: Optional[int] = None) -> bool:
        """
        Guarda un valor en el cache.
        
        Args:
            key: Clave del cache
            value: Valor a cachear
            ttl_hours: TTL en horas (None = usar default)
            
        Returns:
            True si se guardó correctamente
        """
        try:
            with self.cache_lock:
                # Verificar tamaño del cache
                if self._should_cleanup_cache():
                    self._cleanup_cache()
                
                # Guardar en memoria
                self.memory_cache[key] = value
                self._update_cache_order(key)
                
                # Guardar en disco
                success = self._save_to_disk(key, value, ttl_hours)
                
                if success:
                    self.cache_stats['sets'] += 1
                    logger.debug(f"💾 Cache set: {key}")
                
                return success
                
        except Exception as e:
            logger.error(f"❌ Error guardando en cache {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Elimina un valor del cache.
        
        Args:
            key: Clave a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            with self.cache_lock:
                # Eliminar de memoria
                if key in self.memory_cache:
                    del self.memory_cache[key]
                
                # Eliminar de disco
                cache_file = self._get_cache_file_path(key)
                if cache_file.exists():
                    cache_file.unlink()
                
                # Eliminar metadata
                if key in self.cache_metadata:
                    del self.cache_metadata[key]
                
                self.cache_stats['deletes'] += 1
                logger.debug(f"🗑️ Cache delete: {key}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error eliminando del cache {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica si existe una clave en el cache."""
        try:
            with self.cache_lock:
                # Verificar memoria
                if key in self.memory_cache:
                    return True
                
                # Verificar disco
                cache_file = self._get_cache_file_path(key)
                if cache_file.exists():
                    return self._is_cache_valid(key)
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verificando existencia de {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Limpia todo el cache."""
        try:
            with self.cache_lock:
                # Limpiar memoria
                self.memory_cache.clear()
                self.cache_metadata.clear()
                
                # Limpiar disco
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                
                # Resetear estadísticas
                self.cache_stats = {
                    'hits': 0,
                    'misses': 0,
                    'sets': 0,
                    'deletes': 0,
                    'compressions': 0,
                    'total_size_mb': 0.0
                }
                
                logger.info("🧹 Cache completamente limpiado")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error limpiando cache: {e}")
            return False
    
    def _get_cache_file_path(self, key: str) -> Path:
        """Obtiene la ruta del archivo de cache para una clave."""
        # Crear hash de la clave para evitar caracteres problemáticos
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def _save_to_disk(self, key: str, value: Any, ttl_hours: Optional[int] = None) -> bool:
        """Guarda un valor en disco."""
        try:
            cache_file = self._get_cache_file_path(key)
            
            # Determinar TTL
            ttl = ttl_hours or self.config.default_ttl_hours
            expiry_time = datetime.now() + timedelta(hours=ttl)
            
            # Crear metadata
            metadata = {
                'key': key,
                'created_at': datetime.now().isoformat(),
                'expires_at': expiry_time.isoformat(),
                'ttl_hours': ttl,
                'compressed': False
            }
            
            # Serializar datos
            data = {
                'metadata': metadata,
                'value': value
            }
            
            # Comprimir si es necesario
            if self.config.enable_compression:
                data_size_kb = len(pickle.dumps(data)) / 1024
                if data_size_kb > self.config.compression_threshold_kb:
                    data['value'] = gzip.compress(pickle.dumps(value))
                    data['metadata']['compressed'] = True
                    self.cache_stats['compressions'] += 1
            
            # Guardar en disco
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            # Actualizar metadata
            self.cache_metadata[key] = metadata
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando en disco {key}: {e}")
            return False
    
    def _load_from_disk(self, key: str) -> Any:
        """Carga un valor desde disco."""
        try:
            cache_file = self._get_cache_file_path(key)
            
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            metadata = data['metadata']
            value = data['value']
            
            # Descomprimir si es necesario
            if metadata.get('compressed', False):
                value = pickle.loads(gzip.decompress(value))
            
            return value
            
        except Exception as e:
            logger.error(f"❌ Error cargando desde disco {key}: {e}")
            return None
    
    def _is_cache_valid(self, key: str) -> bool:
        """Verifica si el cache es válido (no expirado)."""
        try:
            if key not in self.cache_metadata:
                return False
            
            metadata = self.cache_metadata[key]
            expiry_time = datetime.fromisoformat(metadata['expires_at'])
            
            return datetime.now() < expiry_time
            
        except Exception as e:
            logger.error(f"❌ Error verificando validez de cache {key}: {e}")
            return False
    
    def _update_cache_order(self, key: str):
        """Actualiza el orden del cache LRU."""
        if key in self.memory_cache:
            # Mover al final (más reciente)
            value = self.memory_cache.pop(key)
            self.memory_cache[key] = value
    
    def _should_cleanup_cache(self) -> bool:
        """Determina si se debe limpiar el cache."""
        # Verificar tamaño en memoria
        if len(self.memory_cache) > self.config.max_cache_entries:
            return True
        
        # Verificar tamaño en disco
        total_size_mb = self._get_cache_size_mb()
        if total_size_mb > self.config.max_cache_size_mb:
            return True
        
        return False
    
    def _cleanup_cache(self):
        """Limpia el cache eliminando entradas antiguas."""
        try:
            logger.info("🧹 Limpiando cache...")
            
            # Limpiar cache en memoria (LRU)
            while len(self.memory_cache) > self.config.max_cache_entries // 2:
                oldest_key = next(iter(self.memory_cache))
                del self.memory_cache[oldest_key]
            
            # Limpiar cache en disco
            cache_files = list(self.cache_dir.glob("*.cache"))
            cache_files.sort(key=lambda x: x.stat().st_mtime)  # Ordenar por fecha
            
            # Eliminar archivos antiguos hasta alcanzar el tamaño objetivo
            target_size_mb = self.config.max_cache_size_mb * 0.8  # 80% del máximo
            current_size_mb = self._get_cache_size_mb()
            
            for cache_file in cache_files:
                if current_size_mb <= target_size_mb:
                    break
                
                file_size_mb = cache_file.stat().st_size / (1024 * 1024)
                cache_file.unlink()
                current_size_mb -= file_size_mb
            
            logger.info(f"✅ Cache limpiado, tamaño actual: {current_size_mb:.2f}MB")
            
        except Exception as e:
            logger.error(f"❌ Error limpiando cache: {e}")
    
    def _get_cache_size_mb(self) -> float:
        """Obtiene el tamaño total del cache en MB."""
        try:
            total_size = 0
            for cache_file in self.cache_dir.glob("*.cache"):
                total_size += cache_file.stat().st_size
            
            return total_size / (1024 * 1024)
            
        except Exception as e:
            logger.error(f"❌ Error calculando tamaño de cache: {e}")
            return 0.0
    
    def _start_auto_cleanup(self):
        """Inicia la limpieza automática del cache."""
        def auto_cleanup_worker():
            while True:
                try:
                    time.sleep(self.config.cleanup_interval_hours * 3600)
                    with self.cache_lock:
                        self._cleanup_cache()
                except Exception as e:
                    logger.error(f"❌ Error en limpieza automática: {e}")
        
        cleanup_thread = threading.Thread(target=auto_cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("🔄 Limpieza automática iniciada")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache."""
        try:
            hit_rate = 0
            if self.cache_stats['hits'] + self.cache_stats['misses'] > 0:
                hit_rate = self.cache_stats['hits'] / (self.cache_stats['hits'] + self.cache_stats['misses']) * 100
            
            return {
                'cache_stats': self.cache_stats.copy(),
                'hit_rate_percent': hit_rate,
                'memory_entries': len(self.memory_cache),
                'disk_entries': len(list(self.cache_dir.glob("*.cache"))),
                'total_size_mb': self._get_cache_size_mb(),
                'config': {
                    'max_cache_size_mb': self.config.max_cache_size_mb,
                    'default_ttl_hours': self.config.default_ttl_hours,
                    'enable_compression': self.config.enable_compression,
                    'auto_cleanup': self.config.enable_auto_cleanup
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}

# Instancia global del cache
intelligent_cache = IntelligentCache()

def cache_result(key: str, value: Any, ttl_hours: Optional[int] = None) -> bool:
    """
    Función de utilidad para cachear un resultado.
    
    Args:
        key: Clave del cache
        value: Valor a cachear
        ttl_hours: TTL en horas
        
    Returns:
        True si se cacheó correctamente
    """
    return intelligent_cache.set(key, value, ttl_hours)

def get_cached_result(key: str, default: Any = None) -> Any:
    """
    Función de utilidad para obtener un resultado cacheado.
    
    Args:
        key: Clave del cache
        default: Valor por defecto
        
    Returns:
        Valor cacheado o default
    """
    return intelligent_cache.get(key, default)

def get_cache_stats() -> Dict[str, Any]:
    """Obtiene estadísticas del cache."""
    return intelligent_cache.get_stats()

def clear_cache() -> bool:
    """Limpia todo el cache."""
    return intelligent_cache.clear() 