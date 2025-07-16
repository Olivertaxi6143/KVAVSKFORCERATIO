"""
Lazy Loader para optimización de imports pesados
Sistema de carga diferida para mejorar performance de inicio
"""

import importlib
import time
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class LazyLoader:
    """
    Sistema de carga diferida para optimizar imports pesados.
    
    Características:
    - Carga de módulos solo cuando se necesitan
    - Cache de módulos cargados
    - Medición de tiempo de carga
    - Logging de performance
    """
    
    def __init__(self):
        """Inicializa el lazy loader."""
        self._loaded_modules: Dict[str, Any] = {}
        self._load_times: Dict[str, float] = {}
        self._module_dependencies: Dict[str, list] = {
            'pandas': ['pandas'],
            'numpy': ['numpy'],
            'matplotlib': ['matplotlib', 'matplotlib.pyplot'],
            'plotly': ['plotly', 'plotly.graph_objects'],
            'sklearn': ['sklearn', 'sklearn.ensemble', 'sklearn.preprocessing'],
            'torch': ['torch'],
            'lightgbm': ['lightgbm'],
            'catboost': ['catboost'],
            'xgboost': ['xgboost'],
            'scipy': ['scipy', 'scipy.stats'],
            'seaborn': ['seaborn'],
            'statsmodels': ['statsmodels']
        }
    
    def load_module(self, module_name: str, force_reload: bool = False) -> Any:
        """
        Carga un módulo de forma diferida.
        
        Args:
            module_name: Nombre del módulo a cargar
            force_reload: Forzar recarga del módulo
            
        Returns:
            Módulo cargado
        """
        try:
            # Verificar si ya está cargado
            if module_name in self._loaded_modules and not force_reload:
                logger.debug(f"Módulo {module_name} ya cargado (cache)")
                return self._loaded_modules[module_name]
            
            # Medir tiempo de carga
            start_time = time.time()
            
            # Cargar módulo
            if module_name in self._module_dependencies:
                # Cargar módulo principal y dependencias
                module = importlib.import_module(module_name)
                
                # Cargar dependencias adicionales si existen
                for dep in self._module_dependencies[module_name]:
                    try:
                        importlib.import_module(dep)
                    except ImportError:
                        logger.warning(f"No se pudo cargar dependencia: {dep}")
            else:
                # Carga directa
                module = importlib.import_module(module_name)
            
            # Calcular tiempo de carga
            load_time = time.time() - start_time
            self._load_times[module_name] = load_time
            
            # Guardar en cache
            self._loaded_modules[module_name] = module
            
            logger.info(f"✅ Módulo {module_name} cargado en {load_time:.3f}s")
            return module
            
        except ImportError as e:
            logger.error(f"❌ Error cargando módulo {module_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado cargando {module_name}: {e}")
            return None
    
    def get_module(self, module_name: str) -> Any:
        """
        Obtiene un módulo (carga si es necesario).
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            Módulo cargado
        """
        return self.load_module(module_name)
    
    def preload_critical_modules(self) -> Dict[str, float]:
        """
        Precarga módulos críticos para la aplicación.
        
        Returns:
            Diccionario con tiempos de carga
        """
        critical_modules = [
            'pandas',
            'numpy', 
            'matplotlib',
            'plotly'
        ]
        
        load_times = {}
        for module_name in critical_modules:
            module = self.load_module(module_name)
            if module is not None:
                load_times[module_name] = self._load_times.get(module_name, 0.0)
        
        total_time = sum(load_times.values())
        logger.info(f"⏱️ Precarga de módulos críticos completada en {total_time:.3f}s")
        
        return load_times
    
    def get_load_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de carga de módulos."""
        return {
            'loaded_modules': list(self._loaded_modules.keys()),
            'load_times': self._load_times.copy(),
            'total_modules': len(self._loaded_modules),
            'total_load_time': sum(self._load_times.values())
        }
    
    def clear_cache(self):
        """Limpia el cache de módulos cargados."""
        self._loaded_modules.clear()
        self._load_times.clear()
        logger.info("Cache de módulos limpiado")

# Instancia global del lazy loader
lazy_loader = LazyLoader()

# Funciones de conveniencia para imports comunes
def get_pandas():
    """Obtiene pandas de forma diferida."""
    return lazy_loader.get_module('pandas')

def get_numpy():
    """Obtiene numpy de forma diferida."""
    return lazy_loader.get_module('numpy')

def get_matplotlib():
    """Obtiene matplotlib de forma diferida."""
    return lazy_loader.get_module('matplotlib')

def get_plotly():
    """Obtiene plotly de forma diferida."""
    return lazy_loader.get_module('plotly')

def get_sklearn():
    """Obtiene sklearn de forma diferida."""
    return lazy_loader.get_module('sklearn') 