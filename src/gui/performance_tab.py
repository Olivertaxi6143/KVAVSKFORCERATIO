#!/usr/bin/env python3
"""
Performance Tab para QVA Strategy Studio
=======================================

Pestaña de optimización de performance que integra:
- Monitoreo de recursos en tiempo real
- Optimización de carga de datos
- Gestión de cache
- Estadísticas de performance
- Configuración de optimización

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-16
Versión: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import logging
from typing import Dict, Any, Optional
import psutil

from src.core.utils.performance_optimizer import (
    PerformanceOptimizer, 
    PerformanceConfig,
    get_performance_optimizer
)

logger = logging.getLogger(__name__)

class PerformanceTab(ttk.Frame):
    """
    Pestaña de optimización de performance.
    
    Funcionalidades:
    - Monitoreo de recursos en tiempo real
    - Configuración de optimización
    - Estadísticas de performance
    - Gestión de cache
    - Optimización de datos
    """
    
    def __init__(self, parent, data_manager=None):
        """
        Inicializa la pestaña de performance.
        
        Args:
            parent: Widget padre
            data_manager: Gestor de datos
        """
        super().__init__(parent)
        self.data_manager = data_manager
        self.performance_optimizer = get_performance_optimizer()
        
        # Configuración de monitoreo
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Variables de control
        self.memory_var = tk.StringVar()
        self.cpu_var = tk.StringVar()
        self.cache_hits_var = tk.StringVar()
        self.cache_misses_var = tk.StringVar()
        self.processing_time_var = tk.StringVar()
        
        self._create_widgets()
        self._start_monitoring()
    
    def _create_widgets(self):
        """Crea los widgets de la interfaz."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="⚡ Optimización de Performance", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de monitoreo en tiempo real
        monitoring_frame = ttk.LabelFrame(main_frame, text="📊 Monitoreo en Tiempo Real")
        monitoring_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Métricas de sistema
        system_frame = ttk.Frame(monitoring_frame)
        system_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # CPU
        ttk.Label(system_frame, text="CPU:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(system_frame, textvariable=self.cpu_var, font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W)
        
        # Memoria
        ttk.Label(system_frame, text="Memoria:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(system_frame, textvariable=self.memory_var, font=("Arial", 10, "bold")).grid(row=1, column=1, sticky=tk.W)
        
        # Frame de estadísticas de performance
        stats_frame = ttk.LabelFrame(main_frame, text="📈 Estadísticas de Performance")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Cache hits
        ttk.Label(stats_frame, text="Cache Hits:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Label(stats_frame, textvariable=self.cache_hits_var, font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Cache misses
        ttk.Label(stats_frame, text="Cache Misses:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Label(stats_frame, textvariable=self.cache_misses_var, font=("Arial", 10, "bold")).grid(row=1, column=1, sticky=tk.W, padx=(0, 20))
        
        # Tiempo de procesamiento
        ttk.Label(stats_frame, text="Tiempo de Procesamiento:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Label(stats_frame, textvariable=self.processing_time_var, font=("Arial", 10, "bold")).grid(row=2, column=1, sticky=tk.W, padx=(0, 20))
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(main_frame, text="🎛️ Controles de Optimización")
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones de control
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Botón de limpiar cache
        clear_cache_btn = ttk.Button(
            buttons_frame,
            text="🗑️ Limpiar Cache",
            command=self._clear_cache
        )
        clear_cache_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de optimizar datos
        optimize_data_btn = ttk.Button(
            buttons_frame,
            text="⚡ Optimizar Datos",
            command=self._optimize_data
        )
        optimize_data_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de configuración
        config_btn = ttk.Button(
            buttons_frame,
            text="⚙️ Configuración",
            command=self._show_config_dialog
        )
        config_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de estadísticas detalladas
        stats_btn = ttk.Button(
            buttons_frame,
            text="📊 Estadísticas Detalladas",
            command=self._show_detailed_stats
        )
        stats_btn.pack(side=tk.LEFT)
        
        # Frame de información
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Información")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Área de texto para información
        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD)
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Mostrar información inicial
        self._update_info()
    
    def _start_monitoring(self):
        """Inicia el monitoreo en tiempo real."""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.monitoring_thread.start()
        logger.info("📊 Monitoreo de performance iniciado")
    
    def _monitor_resources(self):
        """Monitorea recursos del sistema."""
        while self.monitoring_active:
            try:
                # Obtener métricas del sistema
                cpu_percent = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                
                # Obtener estadísticas de performance
                stats = self.performance_optimizer.get_performance_stats()
                
                # Actualizar variables en el hilo principal
                self.after(0, self._update_metrics, cpu_percent, memory_info, stats)
                
                time.sleep(2)  # Actualizar cada 2 segundos
                
            except Exception as e:
                logger.error(f"Error en monitoreo: {e}")
                time.sleep(5)
    
    def _update_metrics(self, cpu_percent: float, memory_info: Any, stats: Dict[str, Any]):
        """Actualiza las métricas en la interfaz."""
        try:
            # Actualizar métricas del sistema
            self.cpu_var.set(f"{cpu_percent:.1f}%")
            self.memory_var.set(f"{memory_info.percent:.1f}% ({memory_info.used / (1024**3):.1f}GB / {memory_info.total / (1024**3):.1f}GB)")
            
            # Actualizar estadísticas de performance
            self.cache_hits_var.set(f"{stats.get('cache_hits', 0)}")
            self.cache_misses_var.set(f"{stats.get('cache_misses', 0)}")
            self.processing_time_var.set(f"{stats.get('processing_time', 0):.2f}s")
            
        except Exception as e:
            logger.error(f"Error actualizando métricas: {e}")
    
    def _clear_cache(self):
        """Limpia el cache."""
        try:
            self.performance_optimizer.clear_cache()
            messagebox.showinfo("Cache Limpiado", "✅ Cache limpiado exitosamente")
            self._update_info()
            logger.info("🗑️ Cache limpiado desde GUI")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error limpiando cache: {e}")
            logger.error(f"Error limpiando cache: {e}")
    
    def _optimize_data(self):
        """Optimiza los datos cargados."""
        try:
            if self.data_manager and hasattr(self.data_manager, 'get_data'):
                data = self.data_manager.get_data()
                if data is not None and len(data) > 0:
                    # Optimizar datos
                    optimized_data = self.performance_optimizer.load_data_incremental(data)
                    
                    # Actualizar datos en el data manager
                    if hasattr(self.data_manager, 'set_data'):
                        self.data_manager.set_data(optimized_data)
                    
                    messagebox.showinfo(
                        "Datos Optimizados", 
                        f"✅ Datos optimizados exitosamente\n"
                        f"Filas: {len(optimized_data)}\n"
                        f"Memoria optimizada: {optimized_data.memory_usage(deep=True).sum() / (1024**2):.2f}MB"
                    )
                    self._update_info()
                    logger.info("⚡ Datos optimizados desde GUI")
                else:
                    messagebox.showwarning("Sin Datos", "⚠️ No hay datos cargados para optimizar")
            else:
                messagebox.showwarning("Sin Data Manager", "⚠️ No hay gestor de datos disponible")
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error optimizando datos: {e}")
            logger.error(f"Error optimizando datos: {e}")
    
    def _show_config_dialog(self):
        """Muestra diálogo de configuración."""
        try:
            config_dialog = PerformanceConfigDialog(self)
            config_dialog.grab_set()  # Hacer modal
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error mostrando configuración: {e}")
            logger.error(f"Error mostrando configuración: {e}")
    
    def _show_detailed_stats(self):
        """Muestra estadísticas detalladas."""
        try:
            stats = self.performance_optimizer.get_performance_stats()
            
            stats_text = f"""📊 ESTADÍSTICAS DETALLADAS DE PERFORMANCE

🔧 Configuración:
• Memoria máxima: {self.performance_optimizer.config.max_memory_usage_mb}MB
• Tamaño de chunk: {self.performance_optimizer.config.chunk_size}
• Workers: {self.performance_optimizer.config.max_workers}
• Cache habilitado: {self.performance_optimizer.config.cache_enabled}
• Compresión habilitada: {self.performance_optimizer.config.compression_enabled}

📈 Métricas de Performance:
• Datos cargados: {stats.get('data_loaded_mb', 0):.2f}MB
• Cache hits: {stats.get('cache_hits', 0)}
• Cache misses: {stats.get('cache_misses', 0)}
• Ratio de cache: {stats.get('cache_hit_ratio', 0):.2%}
• Tiempo de procesamiento: {stats.get('processing_time', 0):.2f}s
• Ratio de compresión: {stats.get('compression_ratio', 0):.2f}

💾 Cache:
• Elementos en cache: {stats.get('cache_size', 0)}
• Memoria usada: {stats.get('memory_usage_mb', 0):.2f}MB

🖥️ Sistema:
• CPU: {stats.get('cpu_percent', 0):.1f}%
• Memoria: {stats.get('memory_percent', 0):.1f}%
• Memoria disponible: {stats.get('memory_available_gb', 0):.2f}GB"""
            
            # Crear ventana de estadísticas
            stats_window = tk.Toplevel(self)
            stats_window.title("📊 Estadísticas Detalladas de Performance")
            stats_window.geometry("600x500")
            stats_window.resizable(True, True)
            
            # Área de texto
            text_widget = tk.Text(stats_window, wrap=tk.WORD, font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(stats_window, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
            
            # Insertar estadísticas
            text_widget.insert(tk.END, stats_text)
            text_widget.config(state=tk.DISABLED)
            
            logger.info("📊 Estadísticas detalladas mostradas")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error mostrando estadísticas: {e}")
            logger.error(f"Error mostrando estadísticas: {e}")
    
    def _update_info(self):
        """Actualiza la información en el área de texto."""
        try:
            stats = self.performance_optimizer.get_performance_stats()
            
            info_text = f"""⚡ OPTIMIZADOR DE PERFORMANCE

El optimizador de performance está diseñado para mejorar el rendimiento
del sistema QVA Strategy Studio con las siguientes funcionalidades:

🔧 Funcionalidades Principales:
• Carga incremental de datos para optimizar memoria
• Sistema de cache inteligente con TTL configurable
• Optimización automática de tipos de datos
• Compresión de datos para reducir uso de memoria
• Paginación para datasets grandes
• Procesamiento optimizado de chunks

📊 Estado Actual:
• Cache hits: {stats.get('cache_hits', 0)}
• Cache misses: {stats.get('cache_misses', 0)}
• Datos cargados: {stats.get('data_loaded_mb', 0):.2f}MB
• Tiempo de procesamiento: {stats.get('processing_time', 0):.2f}s
• Elementos en cache: {stats.get('cache_size', 0)}

💡 Consejos de Uso:
• Use "Limpiar Cache" cuando la memoria sea alta
• "Optimizar Datos" mejora el rendimiento de datasets grandes
• Monitoree las estadísticas para identificar cuellos de botella
• Configure el optimizador según sus necesidades específicas

🔄 El monitoreo se actualiza automáticamente cada 2 segundos."""
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, info_text)
            self.info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error actualizando información: {e}")
    
    def stop_monitoring(self):
        """Detiene el monitoreo."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("📊 Monitoreo de performance detenido")


class PerformanceConfigDialog(tk.Toplevel):
    """Diálogo de configuración de performance."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.performance_optimizer = parent.performance_optimizer
        
        self.title("⚙️ Configuración de Performance")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="⚙️ Configuración de Performance", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Variables de configuración
        self.max_memory_var = tk.IntVar(value=self.performance_optimizer.config.max_memory_usage_mb)
        self.chunk_size_var = tk.IntVar(value=self.performance_optimizer.config.chunk_size)
        self.max_workers_var = tk.IntVar(value=self.performance_optimizer.config.max_workers)
        self.cache_enabled_var = tk.BooleanVar(value=self.performance_optimizer.config.cache_enabled)
        self.compression_enabled_var = tk.BooleanVar(value=self.performance_optimizer.config.compression_enabled)
        self.parallel_processing_var = tk.BooleanVar(value=self.performance_optimizer.config.parallel_processing)
        
        # Configuración de memoria
        ttk.Label(main_frame, text="Memoria máxima (MB):").pack(anchor=tk.W, pady=(0, 5))
        memory_entry = ttk.Entry(main_frame, textvariable=self.max_memory_var, width=20)
        memory_entry.pack(anchor=tk.W, pady=(0, 10))
        
        # Configuración de chunk size
        ttk.Label(main_frame, text="Tamaño de chunk:").pack(anchor=tk.W, pady=(0, 5))
        chunk_entry = ttk.Entry(main_frame, textvariable=self.chunk_size_var, width=20)
        chunk_entry.pack(anchor=tk.W, pady=(0, 10))
        
        # Configuración de workers
        ttk.Label(main_frame, text="Número de workers:").pack(anchor=tk.W, pady=(0, 5))
        workers_entry = ttk.Entry(main_frame, textvariable=self.max_workers_var, width=20)
        workers_entry.pack(anchor=tk.W, pady=(0, 10))
        
        # Checkboxes
        ttk.Checkbutton(
            main_frame, 
            text="Habilitar cache", 
            variable=self.cache_enabled_var
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Checkbutton(
            main_frame, 
            text="Habilitar compresión", 
            variable=self.compression_enabled_var
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Checkbutton(
            main_frame, 
            text="Procesamiento paralelo", 
            variable=self.parallel_processing_var
        ).pack(anchor=tk.W, pady=5)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            buttons_frame,
            text="💾 Guardar",
            command=self._save_config
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text="❌ Cancelar",
            command=self.destroy
        ).pack(side=tk.LEFT)
    
    def _save_config(self):
        """Guarda la configuración."""
        try:
            # Crear nueva configuración
            new_config = PerformanceConfig(
                max_memory_usage_mb=self.max_memory_var.get(),
                chunk_size=self.chunk_size_var.get(),
                max_workers=self.max_workers_var.get(),
                cache_enabled=self.cache_enabled_var.get(),
                compression_enabled=self.compression_enabled_var.get(),
                parallel_processing=self.parallel_processing_var.get()
            )
            
            # Actualizar configuración del optimizador
            self.performance_optimizer.config = new_config
            
            messagebox.showinfo("Configuración Guardada", "✅ Configuración guardada exitosamente")
            self.destroy()
            
            logger.info("⚙️ Configuración de performance actualizada")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error guardando configuración: {e}")
            logger.error(f"Error guardando configuración: {e}")


def create_performance_tab(parent, data_manager=None):
    """
    Crea una pestaña de performance.
    
    Args:
        parent: Widget padre
        data_manager: Gestor de datos
        
    Returns:
        PerformanceTab o Frame de fallback
    """
    try:
        return PerformanceTab(parent, data_manager)
    except Exception as e:
        logger.error(f"Error creando pestaña de performance: {e}")
        
        # Crear frame de fallback
        fallback_frame = ttk.Frame(parent)
        fallback_label = ttk.Label(
            fallback_frame,
            text="❌ Error cargando pestaña de Performance\n"
                 "El módulo de optimización no está disponible",
            font=("Arial", 12),
            foreground="red"
        )
        fallback_label.pack(expand=True)
        
        return fallback_frame 