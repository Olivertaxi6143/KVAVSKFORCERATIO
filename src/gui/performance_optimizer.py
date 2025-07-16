"""
GUI Performance Optimizer
Optimizador de performance para mejorar responsividad de la GUI
"""

import time
import threading
from typing import Any, Callable, Dict, List, Optional
import logging
import tkinter as tk
from tkinter import ttk
import queue

logger = logging.getLogger(__name__)

class GUIPerformanceOptimizer:
    """
    Optimizador de performance para la GUI.
    
    Características:
    - Carga asíncrona de componentes pesados
    - Threading para operaciones bloqueantes
    - Lazy loading de widgets
    - Optimización de actualizaciones de UI
    """
    
    def __init__(self, root: tk.Tk):
        """
        Inicializa el optimizador de GUI.
        
        Args:
            root: Ventana principal de tkinter
        """
        self.root = root
        self.async_queue = queue.Queue()
        self.background_tasks: List[threading.Thread] = []
        self.widget_cache: Dict[str, Any] = {}
        self.performance_stats = {
            'widget_loads': 0,
            'async_tasks': 0,
            'cache_hits': 0,
            'total_load_time': 0.0
        }
        
        # Configurar procesamiento asíncrono
        self._setup_async_processing()
        logger.info("GUI Performance Optimizer inicializado")
    
    def _setup_async_processing(self):
        """Configura el procesamiento asíncrono."""
        def process_async_queue():
            """Procesa tareas asíncronas en el hilo principal."""
            try:
                while True:
                    try:
                        # Obtener tarea de la cola (timeout para no bloquear)
                        task = self.async_queue.get(timeout=0.1)
                        if task is None:  # Señal de parada
                            break
                        
                        # Ejecutar tarea
                        task()
                        
                    except queue.Empty:
                        continue
                    except Exception as e:
                        logger.error(f"Error en tarea asíncrona: {e}")
                        
            except Exception as e:
                logger.error(f"Error en procesamiento asíncrono: {e}")
        
        # Iniciar procesamiento asíncrono
        self.async_thread = threading.Thread(target=process_async_queue, daemon=True)
        self.async_thread.start()
    
    def load_widget_lazy(self, widget_name: str, widget_creator: Callable, 
                        parent: tk.Widget, **kwargs) -> Any:
        """
        Carga un widget de forma diferida.
        
        Args:
            widget_name: Nombre del widget para cache
            widget_creator: Función que crea el widget
            parent: Widget padre
            **kwargs: Argumentos para el widget
            
        Returns:
            Widget creado o cacheado
        """
        try:
            # Verificar cache
            if widget_name in self.widget_cache:
                self.performance_stats['cache_hits'] += 1
                logger.debug(f"Widget {widget_name} cargado desde cache")
                return self.widget_cache[widget_name]
            
            # Crear widget
            start_time = time.time()
            widget = widget_creator(parent, **kwargs)
            load_time = time.time() - start_time
            
            # Guardar en cache
            self.widget_cache[widget_name] = widget
            self.performance_stats['widget_loads'] += 1
            self.performance_stats['total_load_time'] += load_time
            
            logger.info(f"✅ Widget {widget_name} creado en {load_time:.3f}s")
            return widget
            
        except Exception as e:
            logger.error(f"Error cargando widget {widget_name}: {e}")
            return None
    
    def run_async_task(self, task: Callable, callback: Optional[Callable] = None):
        """
        Ejecuta una tarea de forma asíncrona.
        
        Args:
            task: Tarea a ejecutar
            callback: Función de callback (opcional)
        """
        try:
            def async_wrapper():
                try:
                    # Ejecutar tarea
                    result = task()
                    
                    # Ejecutar callback en hilo principal si existe
                    if callback is not None:
                        callback_func = callback  # Capturar en variable local
                        self.root.after(0, lambda: callback_func(result))
                    
                    self.performance_stats['async_tasks'] += 1
                    
                except Exception as e:
                    logger.error(f"Error en tarea asíncrona: {e}")
            
            # Agregar tarea a la cola
            self.async_queue.put(async_wrapper)
            
        except Exception as e:
            logger.error(f"Error programando tarea asíncrona: {e}")
    
    def optimize_dataframe_display(self, df, max_rows: int = 1000) -> Any:
        """
        Optimiza la visualización de DataFrames grandes.
        
        Args:
            df: DataFrame a optimizar
            max_rows: Número máximo de filas a mostrar
            
        Returns:
            DataFrame optimizado para visualización
        """
        try:
            if len(df) > max_rows:
                # Mostrar solo las primeras filas
                display_df = df.head(max_rows).copy()
                logger.info(f"DataFrame optimizado: {len(df)} → {len(display_df)} filas")
                return display_df
            else:
                return df
                
        except Exception as e:
            logger.warning(f"Error optimizando DataFrame para display: {e}")
            return df
    
    def create_loading_widget(self, parent: tk.Widget, text: str = "Cargando...") -> ttk.Frame:
        """
        Crea un widget de carga para mostrar durante operaciones pesadas.
        
        Args:
            parent: Widget padre
            text: Texto a mostrar
            
        Returns:
            Widget de carga
        """
        loading_frame = ttk.Frame(parent)
        
        # Spinner
        spinner = ttk.Progressbar(loading_frame, mode='indeterminate')
        spinner.pack(pady=10)
        spinner.start()
        
        # Texto
        label = ttk.Label(loading_frame, text=text)
        label.pack(pady=5)
        
        return loading_frame
    
    def update_ui_safely(self, update_func: Callable):
        """
        Actualiza la UI de forma segura desde hilos secundarios.
        
        Args:
            update_func: Función de actualización
        """
        try:
            self.root.after(0, update_func)
        except Exception as e:
            logger.error(f"Error actualizando UI: {e}")
    
    def batch_update_widgets(self, widgets: List[tk.Widget], update_func: Callable):
        """
        Actualiza múltiples widgets en lote para mejor performance.
        
        Args:
            widgets: Lista de widgets a actualizar
            update_func: Función de actualización
        """
        try:
            def batch_update():
                for widget in widgets:
                    try:
                        update_func(widget)
                    except Exception as e:
                        logger.warning(f"Error actualizando widget: {e}")
            
            self.root.after(0, batch_update)
            
        except Exception as e:
            logger.error(f"Error en actualización por lotes: {e}")
    
    def optimize_scrollable_frame(self, parent: tk.Widget, max_height: int = 400) -> ttk.Frame:
        """
        Crea un frame con scroll optimizado para mejor performance.
        
        Args:
            parent: Widget padre
            max_height: Altura máxima del frame
            
        Returns:
            Frame con scroll optimizado
        """
        try:
            # Frame principal
            main_frame = ttk.Frame(parent)
            
            # Canvas para scroll
            canvas = tk.Canvas(main_frame, height=max_height)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            
            # Frame interno
            scrollable_frame = ttk.Frame(canvas)
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            # Configurar canvas
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Empaquetar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            return scrollable_frame
            
        except Exception as e:
            logger.error(f"Error creando frame con scroll: {e}")
            return ttk.Frame(parent)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de performance."""
        return {
            **self.performance_stats,
            'widget_cache_size': len(self.widget_cache),
            'background_tasks': len(self.background_tasks)
        }
    
    def clear_widget_cache(self):
        """Limpia el cache de widgets."""
        self.widget_cache.clear()
        logger.info("Cache de widgets limpiado")
    
    def shutdown(self):
        """Cierra el optimizador de forma segura."""
        try:
            # Señal de parada para el procesamiento asíncrono
            self.async_queue.put(None)
            
            # Esperar a que termine el hilo
            if hasattr(self, 'async_thread'):
                self.async_thread.join(timeout=2.0)
            
            logger.info("GUI Performance Optimizer cerrado")
            
        except Exception as e:
            logger.error(f"Error cerrando optimizador: {e}")

# Decorador para optimizar funciones de GUI
def gui_async_task(callback: Optional[Callable] = None):
    """
    Decorador para ejecutar funciones de GUI de forma asíncrona.
    
    Args:
        callback: Función de callback (opcional)
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Obtener instancia del optimizador si está disponible
            optimizer = getattr(args[0], 'performance_optimizer', None)
            
            if optimizer:
                optimizer.run_async_task(
                    lambda: func(*args, **kwargs),
                    callback
                )
            else:
                # Ejecutar directamente si no hay optimizador
                return func(*args, **kwargs)
        
        return wrapper
    return decorator 