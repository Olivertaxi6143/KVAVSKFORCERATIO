import numpy as np
import pandas as pd
from typing import Optional, Any, Union
import warnings
"""
Step 2: Configurar Análisis - Módulo del Wizard

Este módulo contiene la interfaz para el segundo paso del wizard:
configuración de parámetros de análisis según el estilo de trading.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Dict, Any, Callable, List

# Importar utilidades GUI
from ..utils import (
    create_styled_button, create_styled_label, show_info_message,
    show_error_message, GUIAnalysisError
)

# Configurar logging
try:
    from core.logger_config import setup_logger
    logger = setup_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class Step2ConfigureFrame(ttk.Frame):
    """
    Frame para el Paso 2: Configurar Análisis
    
    Este módulo maneja la configuración de parámetros de análisis:
    - Estilo de trading (Swing, Day Trading, etc.)
    - Métricas y KPIs a evaluar
    - Parámetros de filtrado y selección
    """
    
    def __init__(self, parent, config_manager=None, on_config_changed=None, on_next_step=None, on_previous_step=None):
        """
        Inicializa el frame del Paso 2.
        
        Args:
            parent: Widget padre
            config_manager: Instancia del ConfigManager
            on_config_changed: Callback cuando cambia la configuración
            on_next_step: Callback para ir al siguiente paso
            on_previous_step: Callback para ir al paso anterior
        """
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.on_config_changed = on_config_changed
        self.on_next_step = on_next_step
        self.on_previous_step = on_previous_step
        
        # Variables de configuración
        self.trading_style_var = tk.StringVar(value="Swing")
        self.alpha_var = tk.DoubleVar(value=0.8)
        self.percentile_var = tk.IntVar(value=80)
        self.top_n_var = tk.IntVar(value=20)
        
        # Diccionario de variables de configuración
        self.config_vars = {
            'trading_style': self.trading_style_var,
            'alpha': self.alpha_var,
            'percentile': self.percentile_var,
            'top_n': self.top_n_var
        }
        
        # Lista de KPIs seleccionados
        self.selected_kpis = []
        
        # Construir interfaz
        self._build_interface()
        
        logger.info("✅ Step2ConfigureFrame inicializado correctamente")
    
    def _build_interface(self):
        """Construye la interfaz del Paso 2."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título del paso
        self._build_title_section(main_frame)
        
        # Descripción del paso
        self._build_description_section(main_frame)
        
        # Frame de configuración de análisis
        self._build_analysis_config_section(main_frame)
        
        # Frame de configuración de métricas
        self._build_metrics_config_section(main_frame)
        
        # Frame de navegación
        self._build_navigation_section(main_frame)
    
    def _build_title_section(self, parent):
        """Construye la sección del título."""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame, 
            text="⚙️ PASO 2: CONFIGURAR ANÁLISIS", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(anchor="w")
    
    def _build_description_section(self, parent):
        """Construye la sección de descripción."""
        desc_frame = ttk.Frame(parent)
        desc_frame.pack(fill="x", pady=(0, 20))
        
        desc_label = ttk.Label(
            desc_frame, 
            text="Configura los parámetros de análisis según tu estilo de trading:", 
            font=("Arial", 10)
        )
        desc_label.pack(anchor="w")
        
        # Lista de configuraciones
        config_list = [
            "• Estilo de trading (Swing, Day Trading, etc.)",
            "• Métricas y KPIs a evaluar",
            "• Parámetros de filtrado y selección"
        ]
        
        for config_desc in config_list:
            config_label = ttk.Label(
                desc_frame, 
                text=config_desc, 
                font=("Arial", 9)
            )
            config_label.pack(anchor="w")
    
    def _build_analysis_config_section(self, parent):
        """Construye la sección de configuración de análisis."""
        analysis_frame = ttk.LabelFrame(
            parent, 
            text="🔬 Configuración de Análisis", 
            padding=15
        )
        analysis_frame.pack(fill="x", pady=(0, 20))
        
        # Configuración de análisis
        self._build_analysis_config(analysis_frame)
    
    def _build_analysis_config(self, parent):
        """Construye la configuración de análisis."""
        # Frame para parámetros
        params_frame = ttk.Frame(parent)
        params_frame.pack(fill="x")
        
        # Estilo de trading
        style_frame = ttk.Frame(params_frame)
        style_frame.pack(fill="x", pady=5)
        
        ttk.Label(style_frame, text="Estilo de Trading:", width=20).pack(side="left")
        
        style_combo = ttk.Combobox(
            style_frame, 
            textvariable=self.trading_style_var,
            values=["Swing", "Day Trading", "Scalping", "Position Trading", "Trend Following"],
            state="readonly",
            width=20
        )
        style_combo.pack(side="left", padx=(10, 0))
        style_combo.bind("<<ComboboxSelected>>", self._on_style_changed)
        
        # Alpha
        alpha_frame = ttk.Frame(params_frame)
        alpha_frame.pack(fill="x", pady=5)
        
        ttk.Label(alpha_frame, text="Alpha:", width=20).pack(side="left")
        
        alpha_scale = ttk.Scale(
            alpha_frame,
            from_=0.1,
            to=1.0,
            variable=self.alpha_var,
            orient="horizontal",
            length=200
        )
        alpha_scale.pack(side="left", padx=(10, 5))
        
        alpha_label = ttk.Label(alpha_frame, textvariable=self.alpha_var)
        alpha_label.pack(side="left")
        
        # Percentil
        percentile_frame = ttk.Frame(params_frame)
        percentile_frame.pack(fill="x", pady=5)
        
        ttk.Label(percentile_frame, text="Percentil:", width=20).pack(side="left")
        
        percentile_scale = ttk.Scale(
            percentile_frame,
            from_=50,
            to=95,
            variable=self.percentile_var,
            orient="horizontal",
            length=200
        )
        percentile_scale.pack(side="left", padx=(10, 5))
        
        percentile_label = ttk.Label(percentile_frame, textvariable=self.percentile_var)
        percentile_label.pack(side="left")
        
        # Top N
        topn_frame = ttk.Frame(params_frame)
        topn_frame.pack(fill="x", pady=5)
        
        ttk.Label(topn_frame, text="Top N:", width=20).pack(side="left")
        
        topn_spinbox = ttk.Spinbox(
            topn_frame,
            from_=5,
            to=100,
            textvariable=self.top_n_var,
            width=10
        )
        topn_spinbox.pack(side="left", padx=(10, 0))
    
    def _build_metrics_config_section(self, parent):
        """Construye la sección de configuración de métricas."""
        metrics_frame = ttk.LabelFrame(
            parent, 
            text="📊 Métricas y KPIs", 
            padding=15
        )
        metrics_frame.pack(fill="x", pady=(0, 20))
        
        # Configuración de métricas
        self._build_metrics_config(metrics_frame)
    
    def _build_metrics_config(self, parent):
        """Construye la configuración de métricas."""
        # Frame para controles de métricas
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Botones de selección
        select_all_btn = create_styled_button(
            controls_frame, 
            "📋 Seleccionar Todos", 
            self._select_all_kpis
        )
        select_all_btn.pack(side="left", padx=(0, 5))
        
        deselect_all_btn = create_styled_button(
            controls_frame, 
            "❌ Deseleccionar Todos", 
            self._deselect_all_kpis
        )
        deselect_all_btn.pack(side="left", padx=(0, 5))
        
        # Etiqueta de estado
        self.metrics_status_label = ttk.Label(
            controls_frame, 
            text="📊 Métricas activas: 0/20", 
            font=("Arial", 9)
        )
        self.metrics_status_label.pack(side="right")
        
        # Frame para lista de métricas
        metrics_list_frame = ttk.Frame(parent)
        metrics_list_frame.pack(fill="both", expand=True)
        
        # Crear lista de métricas
        self._create_metrics_list(metrics_list_frame)
    
    def _create_metrics_list(self, parent):
        """Crea la lista de métricas seleccionables."""
        # Lista de métricas disponibles
        self.available_kpis = [
            "CAGR_IS", "CAGR_OOS", "Sharpe_Ratio_IS", "Sharpe_Ratio_OOS",
            "Max_Drawdown_IS", "Max_Drawdown_OOS", "Profit_Factor_IS", "Profit_Factor_OOS",
            "Win_Rate_IS", "Win_Rate_OOS", "Total_Trades_IS", "Total_Trades_OOS",
            "Calmar_Ratio_IS", "Calmar_Ratio_OOS", "SQN_Score_IS", "SQN_Score_OOS",
            "R_Expectancy_IS", "R_Expectancy_OOS", "Recovery_Factor_IS", "Recovery_Factor_OOS"
        ]
        
        # Variables para checkboxes
        self.kpi_vars = {}
        
        # Crear frame con scroll
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Crear checkboxes para métricas
        for i, kpi in enumerate(self.available_kpis):
            var = tk.BooleanVar()
            self.kpi_vars[kpi] = var
            
            checkbox = ttk.Checkbutton(
                scrollable_frame,
                text=kpi,
                variable=var,
                command=self._update_metrics_status
            )
            checkbox.grid(row=i//2, column=i%2, sticky="w", padx=5, pady=2)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _build_navigation_section(self, parent):
        """Construye la sección de navegación."""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill="x", pady=(20, 0))
        
        # Botón anterior
        prev_button = create_styled_button(
            nav_frame, 
            "⬅️ Anterior", 
            self._go_to_previous_step
        )
        prev_button.pack(side="left")
        
        # Botón siguiente
        next_button = create_styled_button(
            nav_frame, 
            "Siguiente ➡️", 
            self._go_to_next_step
        )
        next_button.pack(side="right")
    
    def _on_style_changed(self, event=None):
        """Maneja el cambio de estilo de trading."""
        try:
            style = self.trading_style_var.get()
            logger.info(f"✅ Estilo de trading cambiado a: {style}")
            
            # Actualizar configuración si hay config_manager
            if self.config_manager:
                self.config_manager.update_trading_style(style)
            
            # Llamar callback si existe
            if self.on_config_changed:
                self.on_config_changed()
                
        except Exception as e:
            logger.error(f"❌ Error cambiando estilo de trading: {e}")
    
    def _select_all_kpis(self):
        """Selecciona todos los KPIs."""
        try:
            for var in self.kpi_vars.values():
                var.set(True)
            
            self._update_metrics_status()
            logger.info("✅ Todos los KPIs seleccionados")
            
        except Exception as e:
            logger.error(f"❌ Error seleccionando todos los KPIs: {e}")
    
    def _deselect_all_kpis(self):
        """Deselecciona todos los KPIs."""
        try:
            for var in self.kpi_vars.values():
                var.set(False)
            
            self._update_metrics_status()
            logger.info("✅ Todos los KPIs deseleccionados")
            
        except Exception as e:
            logger.error(f"❌ Error deseleccionando todos los KPIs: {e}")
    
    def _update_metrics_status(self):
        """Actualiza el estado de las métricas."""
        try:
            selected_count = sum(1 for var in self.kpi_vars.values() if var.get())
            total_count = len(self.available_kpis)
            
            self.metrics_status_label.configure(
                text=f"📊 Métricas activas: {selected_count}/{total_count}"
            )
            
            # Actualizar lista de KPIs seleccionados
            self.selected_kpis = [
                kpi for kpi, var in self.kpi_vars.items() if var.get()
            ]
            
            logger.info(f"✅ Métricas actualizadas: {selected_count}/{total_count}")
            
        except Exception as e:
            logger.error(f"❌ Error actualizando estado de métricas: {e}")
    
    def _go_to_previous_step(self):
        """Va al paso anterior del wizard."""
        try:
            if self.on_previous_step:
                self.on_previous_step()
            else:
                logger.info("✅ Navegando al paso anterior")
                
        except Exception as e:
            show_error_message("Error", f"Error navegando al paso anterior: {str(e)}")
            logger.error(f"❌ Error navegando al paso anterior: {e}")
    
    def _go_to_next_step(self):
        """Va al siguiente paso del wizard."""
        try:
            # Verificar que se han seleccionado métricas
            if len(self.selected_kpis) > 0:
                
                # Guardar configuración
                self._save_configuration()
                
                # Llamar callback si existe
                if self.on_next_step:
                    self.on_next_step()
                else:
                    logger.info("✅ Paso 2 completado - Continuando al siguiente paso")
                    
            else:
                show_error_message(
                    "Error", 
                    "Por favor, selecciona al menos una métrica antes de continuar."
                )
                
        except Exception as e:
            show_error_message("Error", f"Error navegando al siguiente paso: {str(e)}")
            logger.error(f"❌ Error navegando al siguiente paso: {e}")
    
    def _save_configuration(self):
        """Guarda la configuración actual."""
        try:
            config = {
                'trading_style': self.trading_style_var.get(),
                'alpha': self.alpha_var.get(),
                'percentile': self.percentile_var.get(),
                'top_n': self.top_n_var.get(),
                'selected_kpis': self.selected_kpis.copy()
            }
            
            # Guardar en config_manager si existe
            if self.config_manager:
                self.config_manager.update_config(config)
            
            logger.info("✅ Configuración guardada")
            
        except Exception as e:
            logger.error(f"❌ Error guardando configuración: {e}")
    
    def get_configuration(self) -> Dict[str, Any]:
        """Obtiene la configuración actual."""
        return {
            'trading_style': self.trading_style_var.get(),
            'alpha': self.alpha_var.get(),
            'percentile': self.percentile_var.get(),
            'top_n': self.top_n_var.get(),
            'selected_kpis': self.selected_kpis.copy()
        }
    
    def set_configuration(self, config: Dict[str, Any]):
        """Establece la configuración desde el exterior."""
        try:
            if 'trading_style' in config:
                self.trading_style_var.set(config['trading_style'])
            
            if 'alpha' in config:
                self.alpha_var.set(config['alpha'])
            
            if 'percentile' in config:
                self.percentile_var.set(config['percentile'])
            
            if 'top_n' in config:
                self.top_n_var.set(config['top_n'])
            
            if 'selected_kpis' in config:
                # Actualizar checkboxes
                for kpi, var in self.kpi_vars.items():
                    var.set(kpi in config['selected_kpis'])
                
                self._update_metrics_status()
            
            logger.info("✅ Configuración establecida en Step2ConfigureFrame")
            
        except Exception as e:
            logger.error(f"❌ Error estableciendo configuración: {e}")
    
    def is_ready_for_next_step(self) -> bool:
        """Verifica si el paso está listo para continuar."""
        return len(self.selected_kpis) > 0
    
    def reset_step(self):
        """Reinicia el paso."""
        try:
            # Limpiar variables
            self.trading_style_var.set("Swing")
            self.alpha_var.set(0.8)
            self.percentile_var.set(80)
            self.top_n_var.set(20)
            
            # Limpiar KPIs seleccionados
            for var in self.kpi_vars.values():
                var.set(False)
            
            self.selected_kpis = []
            self._update_metrics_status()
            
            logger.info("✅ Step2ConfigureFrame reiniciado")
            
        except Exception as e:
            logger.error(f"❌ Error reiniciando paso: {e}")
    
    def _build_configuration_section(self, parent):
        """Construye la sección de configuración."""
        try:
            config_frame = ttk.LabelFrame(parent, text="⚙️ Configuración", padding=10)
            config_frame.pack(fill="x", pady=(0, 10))
            
            # Configuración básica
            basic_frame = ttk.Frame(config_frame)
            basic_frame.pack(fill="x")
            
            # Estilo de trading
            style_frame = ttk.Frame(basic_frame)
            style_frame.pack(fill="x", pady=2)
            ttk.Label(style_frame, text="Estilo:").pack(side="left")
            ttk.Combobox(style_frame, textvariable=self.trading_style_var, 
                        values=["Swing", "Day Trading", "Scalping"], 
                        state="readonly", width=15).pack(side="left", padx=5)
            
            # Alpha
            alpha_frame = ttk.Frame(basic_frame)
            alpha_frame.pack(fill="x", pady=2)
            ttk.Label(alpha_frame, text="Alpha:").pack(side="left")
            ttk.Scale(alpha_frame, from_=0.1, to=1.0, variable=self.alpha_var, 
                     orient="horizontal", length=150).pack(side="left", padx=5)
            ttk.Label(alpha_frame, textvariable=self.alpha_var).pack(side="left")
            
            logger.info("✅ Sección de configuración construida")
            
        except Exception as e:
            logger.error(f"Error construyendo sección de configuración: {e}")
    
    def _build_validation_section(self, parent):
        """Construye la sección de validación."""
        try:
            validation_frame = ttk.LabelFrame(parent, text="✅ Validación", padding=10)
            validation_frame.pack(fill="x", pady=(0, 10))
            
            # Validación de parámetros
            validation_label = ttk.Label(validation_frame, 
                                       text="Los parámetros serán validados antes de continuar")
            validation_label.pack()
            
            logger.info("✅ Sección de validación construida")
            
        except Exception as e:
            logger.error(f"Error construyendo sección de validación: {e}")
    
    def _apply_configuration(self):
        """Aplica la configuración actual."""
        try:
            config = self.get_configuration()
            if self.on_config_changed:
                self.on_config_changed(config)
            logger.info("✅ Configuración aplicada")
            return True
            
        except Exception as e:
            logger.error(f"Error aplicando configuración: {e}")
            return False
    
    def _validate_configuration(self) -> bool:
        """Valida la configuración actual."""
        try:
            # Validar que se seleccionó un estilo
            if not self.trading_style_var.get():
                return False
            
            # Validar que alpha está en rango
            alpha = self.alpha_var.get()
            if alpha < 0.1 or alpha > 1.0:
                return False
            
            # Validar que se seleccionaron KPIs
            if len(self.selected_kpis) == 0:
                return False
            
            logger.info("✅ Configuración validada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error validando configuración: {e}")
            return False
    
    def _show_validation_errors(self, errors: List[str]):
        """Muestra errores de validación."""
        try:
            error_message = "Errores de validación:\n" + "\n".join(errors)
            show_error_message("Errores de Validación", error_message)
            logger.warning(f"Errores de validación mostrados: {errors}")
            
        except Exception as e:
            logger.error(f"Error mostrando errores de validación: {e}")


def create_step2_configure_frame(parent, **kwargs):
    """
    Función factory para crear el frame del Paso 2.
    
    Args:
        parent: Widget padre
        **kwargs: Argumentos adicionales para Step2ConfigureFrame
        
    Returns:
        Step2ConfigureFrame: Instancia del frame del Paso 2
    """
    return Step2ConfigureFrame(parent, **kwargs) 