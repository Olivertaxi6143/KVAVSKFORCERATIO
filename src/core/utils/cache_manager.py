"""
Cache Manager para optimización de performance
Sistema de cache inteligente para análisis repetitivos
"""

import os
import json
import hashlib
import pickle
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gestor de cache inteligente para optimizar performance.
    
    Características:
    - Cache por hash de datos de entrada
    - Expiración automática de cache
    - Compresión de datos grandes
    - Limpieza automática de cache obsoleto
    """
    
    def __init__(self, cache_dir: Optional[str] = None, max_size_mb: int = 100):
        """
        Inicializa el gestor de cache.
        
        Args:
            cache_dir: Directorio de cache (por defecto: ./cache)
            max_size_mb: Tamaño máximo del cache en MB
        """
        self.cache_dir = Path(cache_dir or "./cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_mb = max_size_mb
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'saves': 0,
            'size_mb': 0
        }
        
        # Configurar limpieza automática
        self._cleanup_old_cache()
        logger.info(f"CacheManager inicializado en: {self.cache_dir}")
    
    def _generate_cache_key(self, data: Any, function_name: str) -> str:
        """
        Genera clave única de cache basada en datos y función.
        
        Args:
            data: Datos de entrada
            function_name: Nombre de la función
            
        Returns:
            Clave única de cache
        """
        try:
            if isinstance(data, pd.DataFrame):
                # Hash basado en contenido del DataFrame
                data_hash = hashlib.md5(
                    pd.util.hash_pandas_object(data, index=True).values
                ).hexdigest()
            elif isinstance(data, dict):
                # Hash basado en contenido del diccionario
                data_str = json.dumps(data, sort_keys=True, default=str)
                data_hash = hashlib.md5(data_str.encode()).hexdigest()
            else:
                # Hash genérico
                data_str = str(data)
                data_hash = hashlib.md5(data_str.encode()).hexdigest()
            
            # Combinar con nombre de función
            cache_key = f"{function_name}_{data_hash}"
            return cache_key
            
        except Exception as e:
            logger.warning(f"Error generando cache key: {e}")
            return f"{function_name}_{int(time.time())}"
    
    def get(self, data: Any, function_name: str, max_age_hours: int = 24) -> Optional[Any]:
        """
        Obtiene resultado del cache si existe y no ha expirado.
        
        Args:
            data: Datos de entrada
            function_name: Nombre de la función
            max_age_hours: Edad máxima del cache en horas
            
        Returns:
            Resultado cacheado o None si no existe/expiró
        """
        try:
            cache_key = self._generate_cache_key(data, function_name)
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            if not cache_file.exists():
                self.cache_stats['misses'] += 1
                return None
            
            # Verificar edad del archivo
            file_age_hours = (time.time() - cache_file.stat().st_mtime) / 3600
            if file_age_hours > max_age_hours:
                logger.debug(f"Cache expirado para {function_name}")
                cache_file.unlink()
                self.cache_stats['misses'] += 1
                return None
            
            # Cargar resultado cacheado
            with open(cache_file, 'rb') as f:
                cached_result = pickle.load(f)
            
            self.cache_stats['hits'] += 1
            logger.debug(f"Cache hit para {function_name}")
            return cached_result
            
        except Exception as e:
            logger.warning(f"Error leyendo cache para {function_name}: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    def set(self, data: Any, function_name: str, result: Any) -> bool:
        """
        Guarda resultado en cache.
        
        Args:
            data: Datos de entrada
            function_name: Nombre de la función
            result: Resultado a cachear
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            cache_key = self._generate_cache_key(data, function_name)
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            # Verificar tamaño del cache
            if self._get_cache_size_mb() > self.max_size_mb:
                self._cleanup_old_cache()
            
            # Guardar resultado
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
            
            self.cache_stats['saves'] += 1
            logger.debug(f"Cache guardado para {function_name}")
            return True
            
        except Exception as e:
            logger.warning(f"Error guardando cache para {function_name}: {e}")
            return False
    
    def _get_cache_size_mb(self) -> float:
        """Calcula tamaño total del cache en MB."""
        try:
            total_size = sum(
                f.stat().st_size for f in self.cache_dir.glob("*.pkl")
            )
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0
    
    def _cleanup_old_cache(self, max_age_hours: int = 24):
        """Limpia cache obsoleto."""
        try:
            current_time = time.time()
            deleted_count = 0
            
            for cache_file in self.cache_dir.glob("*.pkl"):
                file_age_hours = (current_time - cache_file.stat().st_mtime) / 3600
                if file_age_hours > max_age_hours:
                    cache_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Limpieza de cache: {deleted_count} archivos eliminados")
                
        except Exception as e:
            logger.warning(f"Error en limpieza de cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache."""
        return {
            **self.cache_stats,
            'size_mb': self._get_cache_size_mb(),
            'cache_dir': str(self.cache_dir)
        }
    
    def clear_cache(self) -> bool:
        """Limpia todo el cache."""
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            
            self.cache_stats = {
                'hits': 0,
                'misses': 0,
                'saves': 0,
                'size_mb': 0
            }
            
            logger.info("Cache limpiado completamente")
            return True
            
        except Exception as e:
            logger.error(f"Error limpiando cache: {e}")
            return False

# Instancia global del cache manager
cache_manager = CacheManager() 