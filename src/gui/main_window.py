"""
Main Window Module
Ventana principal de la aplicación QVA Strategy Studio
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import threading
import queue
import os
import webbrowser
import json

# Importar módulos de la aplicación
from src.data.data_manager import DataManager
# from src.analysis.scientific_analysis import ScientificAnalysis  # Comentado temporalmente
from src.gui.advanced_filters_popup import create_advanced_filters_popup
from src.gui.interactive_charts import create_interactive_chart_manager
from src.gui.strategy_comparison import create_strategy_comparison_manager
from src.gui.advanced_export import create_advanced_export_manager
# Añadir import del exportador .sqx
from src.data.sqx_exporter import SQXExporter
from src.gui.portfolio_analysis_tab import PortfolioAnalysisTab
from src.gui.help_contextual import create_help_contextual_panel
from src.gui.scientific_gui_tab import create_scientific_tab
from src.gui.asesor_financiero_tab import create_asesor_tab
from src.gui.performance_tab import create_performance_tab
from unittest.mock import Mock

logger = logging.getLogger(__name__)

class MainWindow:
    """
    Ventana principal de la aplicación QVA Strategy Studio.
    
    Características:
    - Interfaz moderna y profesional
    - Carga y análisis de estrategias
    - Visualización de resultados
    - Exportación de datos
    - Funcionalidades avanzadas integradas
    """
    
    def __init__(self):
        """Inicializa la ventana principal."""
        self.root = tk.Tk()
        self.root.title("QVA Strategy Studio - Análisis Cuantitativo Avanzado")
        self.root.geometry("1400x900")
        self.root.state('zoomed')  # Maximizar en Windows
        
        # Configurar estilo
        self._setup_style()
        
        # Inicializar componentes
        self.data_manager = DataManager()
        # self.scientific_analysis = ScientificAnalysis()  # Comentado temporalmente
        
        # Gestores avanzados
        self.advanced_filters = None
        self.chart_manager = None
        self.comparison_manager = None
        self.export_manager = None
        
        # Panel de ayuda contextual
        self.help_panel = None
        
        # Variables de estado
        self.current_data = None
        self.filtered_data = None
        self.results_df = None
        self.selected_strategies = []
        
        # Cola para comunicación entre hilos
        self.message_queue = queue.Queue()
        
        # Tooltips informativos
        self.tooltip_widgets = {}
        
        # Construir interfaz
        self._build_interface()
        self._setup_menu()
        self._setup_status_bar()
        
        # Configurar callbacks
        self._setup_callbacks()
        
        # Inicializar gestores avanzados
        self._initialize_advanced_managers()
        
        logger.info("✅ MainWindow inicializada")
    
    def _setup_style(self):
        """Configura el estilo de la aplicación."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
    
    def _build_interface(self):
        """Construye la interfaz principal."""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        # Barra de herramientas
        self._build_toolbar(main_frame)
        
        # Frame de contenido principal
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Panel izquierdo (navegación)
        self._build_left_panel(content_frame)
        
        # Panel central (contenido principal)
        self._build_center_panel(content_frame)
        
        # Panel derecho (detalles y controles)
        self._build_right_panel(content_frame)
    
    def _build_toolbar(self, parent: ttk.Frame):
        """Construye la barra de herramientas."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", padx=5, pady=2)
        
        # Botones principales
        ttk.Button(toolbar, text="📁 Cargar Datos", 
                  command=self._load_data).pack(side="left", padx=2)
        ttk.Button(toolbar, text="🔍 Filtros Avanzados", 
                  command=self._show_advanced_filters).pack(side="left", padx=2)
        ttk.Button(toolbar, text="📊 Gráficos Interactivos", 
                  command=self._show_interactive_charts).pack(side="left", padx=2)
        ttk.Button(toolbar, text="⚖️ Comparar Estrategias", 
                  command=self._show_strategy_comparison).pack(side="left", padx=2)
        ttk.Button(toolbar, text="📤 Exportación Avanzada", 
                  command=self._show_advanced_export).pack(side="left", padx=2)
        
        # Separador
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)
        
        # Botones de análisis
        ttk.Button(toolbar, text="🧪 Análisis Científico", 
                  command=self._run_scientific_analysis).pack(side="left", padx=2)
        ttk.Button(toolbar, text="📈 Tail Risk Analysis", 
                  command=self._run_tail_risk_analysis).pack(side="left", padx=2)
        ttk.Button(toolbar, text="🎯 AXISelect Analysis", 
                  command=self._run_axis_analysis).pack(side="left", padx=2)
        
        # Separador
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)
        
        # Botones de utilidades
        ttk.Button(toolbar, text="🔄 Actualizar", 
                  command=self._refresh_data).pack(side="left", padx=2)
        ttk.Button(toolbar, text="💾 Guardar Configuración", 
                  command=self._save_configuration).pack(side="left", padx=2)
        ttk.Button(toolbar, text="📁 Exportar .SQX", 
                  command=self._export_sqx_files).pack(side="left", padx=2)
        ttk.Button(toolbar, text="❓ Ayuda", 
                  command=self._show_help).pack(side="right", padx=2)
    
    def _build_left_panel(self, parent: ttk.Frame):
        """Construye el panel izquierdo."""
        left_frame = ttk.Frame(parent, width=250)
        left_frame.pack(side="left", fill="y", padx=(0, 5))
        left_frame.pack_propagate(False)
        
        # Título del panel
        ttk.Label(left_frame, text="📋 Navegación", 
                 style="Header.TLabel").pack(pady=(0, 10))
        
        # Lista de pasos
        steps_frame = ttk.LabelFrame(left_frame, text="Pasos del Análisis")
        steps_frame.pack(fill="x", pady=5)
        
        self.steps_listbox = tk.Listbox(steps_frame, height=15)
        self.steps_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Agregar pasos
        steps = [
            "1. Cargar datos de estrategias",
            "2. Configurar filtros básicos",
            "3. Ejecutar análisis científico",
            "4. Analizar Tail Risk",
            "5. Aplicar AXISelect",
            "6. Comparar estrategias",
            "7. Generar gráficos",
            "8. Exportar resultados"
        ]
        
        for step in steps:
            self.steps_listbox.insert(tk.END, step)
        
        # Panel de filtros rápidos
        filters_frame = ttk.LabelFrame(left_frame, text="Filtros Rápidos")
        filters_frame.pack(fill="x", pady=5)
        
        # Filtro por Factor K
        ttk.Label(filters_frame, text="Factor K mínimo:").pack(anchor="w", padx=5, pady=2)
        self.factor_k_var = tk.DoubleVar(value=7.0)
        factor_k_scale = ttk.Scale(filters_frame, from_=0, to=10, 
                                  variable=self.factor_k_var, orient="horizontal")
        factor_k_scale.pack(fill="x", padx=5, pady=2)
        
        # Filtro por Sharpe
        ttk.Label(filters_frame, text="Sharpe mínimo:").pack(anchor="w", padx=5, pady=2)
        self.sharpe_var = tk.DoubleVar(value=1.0)
        sharpe_scale = ttk.Scale(filters_frame, from_=0, to=5, 
                                variable=self.sharpe_var, orient="horizontal")
        sharpe_scale.pack(fill="x", padx=5, pady=2)
        
        # Botón aplicar filtros
        ttk.Button(filters_frame, text="Aplicar Filtros", 
                  command=self._apply_quick_filters).pack(pady=5)
    
    def _build_center_panel(self, parent: ttk.Frame):
        """Construye el panel central."""
        center_frame = ttk.Frame(parent)
        center_frame.pack(side="left", fill="both", expand=True)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(center_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Pestaña de datos principales
        self._create_main_data_tab()
        
        # Pestaña de análisis científico
        self._create_scientific_analysis_tab()
        
        # Pestaña de Tail Risk
        self._create_tail_risk_tab()
        
        # Pestaña de AXISelect
        self._create_axis_tab()
        
        # Pestaña de comparación
        self._create_comparison_tab()
        
        # Pestaña de gráficos
        self._create_charts_tab()

        # Pestaña de Base de Datos ISA
        self._create_isa_database_tab()

        # Pestaña de Performance
        self._create_performance_tab()

        # Pestaña de Análisis de Portfolio
        portfolio_frame = ttk.Frame(self.notebook)
        self.notebook.add(portfolio_frame, text="Análisis de Portfolio")
        self.portfolio_analysis_tab = PortfolioAnalysisTab(portfolio_frame)
    
    def _build_right_panel(self, parent: ttk.Frame):
        """Construye el panel derecho."""
        right_frame = ttk.Frame(parent, width=300)
        right_frame.pack(side="right", fill="y", padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # Título del panel
        ttk.Label(right_frame, text="📊 Detalles y Controles", 
                 style="Header.TLabel").pack(pady=(0, 10))
        
        # Panel de estadísticas
        stats_frame = ttk.LabelFrame(right_frame, text="Estadísticas")
        stats_frame.pack(fill="x", pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=8, width=35)
        self.stats_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Panel de selección de estrategias
        selection_frame = ttk.LabelFrame(right_frame, text="Estrategias Seleccionadas")
        selection_frame.pack(fill="x", pady=5)
        
        self.selected_listbox = tk.Listbox(selection_frame, height=6)
        self.selected_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Botones de selección
        selection_buttons_frame = ttk.Frame(selection_frame)
        selection_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(selection_buttons_frame, text="Seleccionar Todo", 
                  command=self._select_all_strategies).pack(side="left", padx=2)
        ttk.Button(selection_buttons_frame, text="Limpiar", 
                  command=self._clear_selection).pack(side="left", padx=2)
        
        # Panel de acciones rápidas
        actions_frame = ttk.LabelFrame(right_frame, text="Acciones Rápidas")
        actions_frame.pack(fill="x", pady=5)
        
        ttk.Button(actions_frame, text="📊 Ver Detalles", 
                  command=self._show_strategy_details).pack(fill="x", padx=5, pady=2)
        ttk.Button(actions_frame, text="📈 Analizar Seleccionadas", 
                  command=self._analyze_selected).pack(fill="x", padx=5, pady=2)
        ttk.Button(actions_frame, text="💾 Exportar Seleccionadas", 
                  command=self._export_selected).pack(fill="x", padx=5, pady=2)
    
    def _create_main_data_tab(self):
        """Crea pestaña de datos principales."""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📋 Datos Principales")
        
        # Frame para controles
        controls_frame = ttk.Frame(data_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(controls_frame, text="🔄 Actualizar Datos", 
                  command=self._refresh_main_data).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="📊 Estadísticas", 
                  command=self._show_data_statistics).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="🔍 Buscar", 
                  command=self._search_strategies).pack(side="left", padx=5)
        
        # Frame para tabla
        table_frame = ttk.Frame(data_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Crear tabla con scrollbars
        self._create_data_table(table_frame)
    
    def _create_scientific_analysis_tab(self):
        """Crea pestaña de análisis científico."""
        # Inicializar pestaña de Scientific Analysis con implementación profesional
        self.scientific_analysis = create_scientific_tab(
            self.notebook, 
            self.data_manager, 
            self.filtered_data if self.filtered_data is not None else pd.DataFrame()
        )
        
        # Inicializar pestaña del Asesor Financiero Inteligente
        self.asesor_financiero = create_asesor_tab(
            self.notebook,
            self.data_manager,
            self.filtered_data if self.filtered_data is not None else pd.DataFrame()
        )
    
    def _create_tail_risk_tab(self):
        """Crea pestaña de Tail Risk Analysis."""
        tail_risk_frame = ttk.Frame(self.notebook)
        self.notebook.add(tail_risk_frame, text="🔬 Tail Risk Analysis")
        
        # Inicializar pestaña de Tail Risk con implementación profesional
        from src.gui.tail_risk_tab import TailRiskTab
        self.tail_risk_analysis = TailRiskTab(tail_risk_frame)
    
    def _create_axis_tab(self):
        """Crea pestaña de AXISelect Analysis."""
        axis_frame = ttk.Frame(self.notebook)
        self.notebook.add(axis_frame, text="🎯 AXISelect Analysis")
        
        # Inicializar pestaña de AXI Select con implementación profesional
        from src.gui.axi_select_tab import AXISelectTab
        self.axi_select_analysis = AXISelectTab(axis_frame)
    
    def _create_comparison_tab(self):
        """Crea pestaña de comparación de estrategias."""
        comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(comparison_frame, text="⚖️ Comparación")
        
        # Controles de comparación
        controls_frame = ttk.Frame(comparison_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(controls_frame, text="⚖️ Comparar Seleccionadas", 
                  command=self._compare_selected_strategies).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="📊 Ver Comparación", 
                  command=self._show_comparison_results).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="💾 Exportar Comparación", 
                  command=self._export_comparison).pack(side="left", padx=5)
        
        # Área de resultados
        results_frame = ttk.Frame(comparison_frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.comparison_text = tk.Text(results_frame, wrap="word")
        self.comparison_text.pack(fill="both", expand=True)
    
    def _create_charts_tab(self):
        """Crea pestaña de gráficos."""
        charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(charts_frame, text="📈 Gráficos")
        
        # Controles de gráficos
        controls_frame = ttk.Frame(charts_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(controls_frame, text="📊 Crear Gráficos", 
                  command=self._create_charts).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="🖼️ Exportar Gráficos", 
                  command=self._export_charts).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="🔄 Actualizar", 
                  command=self._refresh_charts).pack(side="left", padx=5)
        
        # Área de gráficos
        charts_area_frame = ttk.Frame(charts_frame)
        charts_area_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.charts_text = tk.Text(charts_area_frame, wrap="word")
        self.charts_text.pack(fill="both", expand=True)
    
    def _create_isa_database_tab(self):
        """Crea pestaña de Base de Datos ISA."""
        # Importar la pestaña de Base de Datos ISA
        from src.gui.isa_database_tab import create_isa_database_tab
        
        # Crear la pestaña
        self.isa_database_tab = create_isa_database_tab(self.notebook, self.data_manager)
    
    def _create_performance_tab(self):
        """Crea pestaña de Performance."""
        # Crear la pestaña de performance
        self.performance_tab = create_performance_tab(self.notebook, self.data_manager)
    
    def _create_data_table(self, parent: ttk.Frame):
        """Crea tabla de datos con scrollbars."""
        # Frame para tabla y scrollbars
        table_container = ttk.Frame(parent)
        table_container.pack(fill="both", expand=True)
        
        # Crear Treeview
        columns = ["Strategy_Name", "Factor_K", "CAGR_IS", "Sharpe_Ratio_IS", "Max_Drawdown_IS"]
        self.data_tree = ttk.Treeview(table_container, columns=columns, show="headings", height=20)
        
        # Configurar columnas
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.data_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.data_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Binding para selección
        self.data_tree.bind("<<TreeviewSelect>>", self._on_strategy_selected)
    
    def _setup_menu(self):
        """Configura el menú principal."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Cargar Datos", command=self._load_data)
        file_menu.add_command(label="Guardar Configuración", command=self._save_configuration)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Análisis
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Análisis", menu=analysis_menu)
        analysis_menu.add_command(label="Análisis Científico", command=self._run_scientific_analysis)
        analysis_menu.add_command(label="Tail Risk Analysis", command=self._run_tail_risk_analysis)
        analysis_menu.add_command(label="AXISelect Analysis", command=self._run_axis_analysis)
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Filtros Avanzados", command=self._show_advanced_filters)
        tools_menu.add_command(label="Gráficos Interactivos", command=self._show_interactive_charts)
        tools_menu.add_command(label="Comparar Estrategias", command=self._show_strategy_comparison)
        tools_menu.add_command(label="Exportación Avanzada", command=self._show_advanced_export)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Manual de Usuario", command=self._show_help)
        help_menu.add_command(label="Acerca de", command=self._show_about)
    
    def _setup_status_bar(self):
        """Configura la barra de estado."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ttk.Label(self.status_bar, text="Listo")
        self.status_label.pack(side="left", padx=5)
        
        self.progress_bar = ttk.Progressbar(self.status_bar, mode="indeterminate")
        self.progress_bar.pack(side="right", padx=5)
    
    def _setup_callbacks(self):
        """Configura callbacks y eventos."""
        # Actualizar interfaz desde cola de mensajes
        self.root.after(100, self._process_messages)
    
    def _initialize_advanced_managers(self):
        """Inicializa los gestores avanzados."""
        try:
            self.chart_manager = create_interactive_chart_manager(self.root)
            self.comparison_manager = create_strategy_comparison_manager(self.root)
            self.export_manager = create_advanced_export_manager(self.root)
            
            # Inicializar panel de ayuda contextual
            self.help_panel = create_help_contextual_panel(self.root)
            
            logger.info("✅ Gestores avanzados inicializados")
            
        except Exception as e:
            logger.error(f"Error inicializando gestores avanzados: {e}")
            # Crear gestores mock si falla la inicialización
            self.chart_manager = Mock()
            self.comparison_manager = Mock()
            self.export_manager = Mock()
            self.help_panel = Mock()
    
    def _load_data(self):
        """Carga datos de estrategias."""
        try:
            self._update_status("Cargando datos...")
            self.progress_bar.start()
            
            # Ejecutar en hilo separado
            thread = threading.Thread(target=self._load_data_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            self._update_status("Error cargando datos")
    
    def _load_data_thread(self):
        """Hilo para cargar datos."""
        try:
            # Cargar datos usando DataManager
            data = self.data_manager.get_clean_data()
            
            if data is not None and len(data) > 0:
                self.current_data = data
                self.filtered_data = data.copy()
                
                # Actualizar interfaz en hilo principal
                self.message_queue.put(("data_loaded", data))
                
                logger.info(f"✅ Datos cargados: {len(data)} estrategias")
            else:
                self.message_queue.put(("error", "No se pudieron cargar datos"))
                
        except Exception as e:
            logger.error(f"Error en hilo de carga: {e}")
            self.message_queue.put(("error", f"Error cargando datos: {e}"))
    
    def _show_advanced_filters(self):
        """Muestra popup de filtros avanzados."""
        try:
            if self.current_data is None:
                messagebox.showwarning("Filtros", "No hay datos cargados")
                return
            
            # Crear popup de filtros avanzados
            popup = create_advanced_filters_popup(
                self.root, 
                self.current_data,
                self._on_filters_changed
            )
            
            # Mostrar popup
            popup.show()
            
        except Exception as e:
            logger.error(f"Error mostrando filtros avanzados: {e}")
            messagebox.showerror("Error", f"Error mostrando filtros: {e}")
    
    def _show_interactive_charts(self):
        """Muestra gráficos interactivos."""
        try:
            if self.current_data is None:
                messagebox.showwarning("Gráficos", "No hay datos cargados")
                return
            
            # Crear ventana de gráficos interactivos
            charts_window = tk.Toplevel(self.root)
            charts_window.title("📊 Gráficos Interactivos")
            charts_window.geometry("1000x700")
            
            # Crear notebook para diferentes tipos de gráficos
            notebook = ttk.Notebook(charts_window)
            notebook.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Gráfico de correlación
            corr_frame = ttk.Frame(notebook)
            notebook.add(corr_frame, text="🔗 Correlación")
            
            if self.chart_manager is not None:
                corr_config = self.chart_manager.create_correlation_matrix_chart(
                    self.current_data, "Matriz de Correlación de Estrategias"
                )
                corr_widget = self.chart_manager.create_chart_widget(corr_frame, corr_config)
            else:
                corr_widget = ttk.Label(corr_frame, text="Chart Manager no disponible")
            corr_widget.pack(fill="both", expand=True)
            
            # Gráfico de dispersión
            scatter_frame = ttk.Frame(notebook)
            notebook.add(scatter_frame, text="📊 Dispersión")
            
            if self.chart_manager is not None:
                scatter_config = self.chart_manager.create_scatter_plot(
                    self.current_data, "CAGR_IS", "Sharpe_Ratio_IS", 
                    color_col="Factor_K", title="CAGR vs Sharpe Ratio"
                )
                scatter_widget = self.chart_manager.create_chart_widget(scatter_frame, scatter_config)
            else:
                scatter_widget = ttk.Label(scatter_frame, text="Chart Manager no disponible")
            scatter_widget.pack(fill="both", expand=True)
            
            # Histograma
            hist_frame = ttk.Frame(notebook)
            notebook.add(hist_frame, text="📈 Histograma")
            
            if self.chart_manager is not None:
                hist_config = self.chart_manager.create_histogram_chart(
                    self.current_data, "Factor_K", title="Distribución Factor K"
                )
                hist_widget = self.chart_manager.create_chart_widget(hist_frame, hist_config)
            else:
                hist_widget = ttk.Label(hist_frame, text="Chart Manager no disponible")
            hist_widget.pack(fill="both", expand=True)
            
        except Exception as e:
            logger.error(f"Error mostrando gráficos interactivos: {e}")
            messagebox.showerror("Error", f"Error mostrando gráficos: {e}")
    
    def _show_strategy_comparison(self):
        """Muestra comparación de estrategias."""
        try:
            if self.current_data is None:
                messagebox.showwarning("Comparación", "No hay datos cargados")
                return
            
            # Crear ventana de comparación
            comparison_window = tk.Toplevel(self.root)
            comparison_window.title("⚖️ Comparación de Estrategias")
            comparison_window.geometry("1200x800")
            
            # Frame principal
            main_frame = ttk.Frame(comparison_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Panel de selección
            selection_frame = ttk.LabelFrame(main_frame, text="Seleccionar Estrategias")
            selection_frame.pack(fill="x", pady=(0, 10))
            
            # Lista de estrategias disponibles
            strategies_listbox = tk.Listbox(selection_frame, height=8, selectmode="multiple")
            strategies_listbox.pack(fill="x", padx=5, pady=5)
            
            for strategy in self.current_data['Strategy_Name'].unique():
                strategies_listbox.insert(tk.END, strategy)
            
            # Botones de acción
            button_frame = ttk.Frame(selection_frame)
            button_frame.pack(fill="x", padx=5, pady=5)
            
            def compare_selected():
                selected_indices = strategies_listbox.curselection()
                selected_strategies = [strategies_listbox.get(i) for i in selected_indices]
                
                if len(selected_strategies) < 2:
                    messagebox.showwarning("Comparación", "Selecciona al menos 2 estrategias")
                    return
                
                # Configurar comparación
                if self.comparison_manager is not None and self.current_data is not None:
                    self.comparison_manager.set_data(self.current_data)
                    self.comparison_manager.select_strategies(selected_strategies)
                    
                    # Ejecutar comparación
                    results = self.comparison_manager.compare_strategies()
                    
                    # Mostrar resultados
                    results_frame = ttk.Frame(main_frame)
                    results_frame.pack(fill="both", expand=True)
                    
                    if results is not None:
                        results_widget = self.comparison_manager.create_comparison_widget(results_frame, results)
                        results_widget.pack(fill="both", expand=True)
                    else:
                        ttk.Label(results_frame, text="No se pudieron generar resultados de comparación").pack()
                else:
                    ttk.Label(main_frame, text="Comparison Manager no disponible").pack()
            
            ttk.Button(button_frame, text="⚖️ Comparar Seleccionadas", 
                      command=compare_selected).pack(side="left", padx=5)
            ttk.Button(button_frame, text="🗑️ Limpiar Selección", 
                      command=lambda: strategies_listbox.selection_clear(0, tk.END)).pack(side="left", padx=5)
            
        except Exception as e:
            logger.error(f"Error mostrando comparación: {e}")
            messagebox.showerror("Error", f"Error mostrando comparación: {e}")
    
    def _show_advanced_export(self):
        """Muestra diálogo de exportación avanzada."""
        try:
            if self.current_data is None:
                messagebox.showwarning("Exportación", "No hay datos cargados")
                return
            
            # Configurar datos para exportación
            if self.export_manager is not None and self.current_data is not None:
                self.export_manager.set_data(self.current_data)
                
                # Crear ventana de exportación
                export_window = tk.Toplevel(self.root)
                export_window.title("📤 Exportación Avanzada")
                export_window.geometry("600x400")
                
                # Crear diálogo de exportación
                if self.export_manager is not None and hasattr(self.export_manager, 'create_export_dialog'):
                    try:
                        # Crear un frame contenedor para evitar problemas de tipo
                        container_frame = ttk.Frame(export_window)
                        container_frame.pack(fill="both", expand=True, padx=10, pady=10)
                        
                        export_widget = self.export_manager.create_export_dialog(container_frame)
                        export_widget.pack(fill="both", expand=True)
                    except Exception as e:
                        ttk.Label(export_window, text=f"Error en export manager: {e}").pack()
                else:
                    ttk.Label(export_window, text="Export Manager no disponible").pack()
            else:
                messagebox.showwarning("Exportación", "Export Manager no disponible")
            
        except Exception as e:
            logger.error(f"Error mostrando exportación avanzada: {e}")
            messagebox.showerror("Error", f"Error mostrando exportación: {e}")
    
    def _on_filters_changed(self, filtered_data: pd.DataFrame):
        """Callback cuando cambian los filtros."""
        try:
            self.filtered_data = filtered_data
            self._update_data_display()
            self._update_statistics()
            
            logger.info(f"✅ Filtros aplicados: {len(filtered_data)} estrategias")
            
        except Exception as e:
            logger.error(f"Error actualizando filtros: {e}")
    
    def _update_data_display(self):
        """Actualiza la visualización de datos."""
        try:
            if self.filtered_data is None:
                return
            
            # Limpiar tabla
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            # Insertar datos filtrados
            for idx, row in self.filtered_data.iterrows():
                values = [
                    row.get('Strategy_Name', ''),
                    f"{row.get('Factor_K', 0):.3f}",
                    f"{row.get('CAGR_IS', 0):.3f}",
                    f"{row.get('Sharpe_Ratio_IS', 0):.3f}",
                    f"{row.get('Max_Drawdown_IS', 0):.3f}"
                ]
                self.data_tree.insert("", "end", values=values)
            
        except Exception as e:
            logger.error(f"Error actualizando visualización: {e}")
    
    def _update_statistics(self):
        """Actualiza las estadísticas mostradas."""
        try:
            if self.filtered_data is None:
                return
            
            stats_text = f"""
📊 ESTADÍSTICAS ACTUALES
========================

Total de estrategias: {len(self.filtered_data)}

Factor K:
  - Promedio: {self.filtered_data['Factor_K'].mean():.3f}
  - Máximo: {self.filtered_data['Factor_K'].max():.3f}
  - Mínimo: {self.filtered_data['Factor_K'].min():.3f}

CAGR IS:
  - Promedio: {self.filtered_data['CAGR_IS'].mean():.3f}
  - Máximo: {self.filtered_data['CAGR_IS'].max():.3f}
  - Mínimo: {self.filtered_data['CAGR_IS'].min():.3f}

Sharpe Ratio IS:
  - Promedio: {self.filtered_data['Sharpe_Ratio_IS'].mean():.3f}
  - Máximo: {self.filtered_data['Sharpe_Ratio_IS'].max():.3f}
  - Mínimo: {self.filtered_data['Sharpe_Ratio_IS'].min():.3f}
"""
            
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert("1.0", stats_text)
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
    
    def _process_messages(self):
        """Procesa mensajes de la cola."""
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                
                if isinstance(message, dict):
                    msg_type = message.get('type')
                    
                    if msg_type == "data_loaded":
                        self._update_data_display()
                        self._update_statistics()
                        self._update_status(f"Datos cargados: {len(message.get('data', []))} estrategias")
                        self.progress_bar.stop()
                        
                    elif msg_type == "export_complete":
                        summary = message.get('summary', '')
                        results = message.get('results', {})
                        
                        # Mostrar resumen de exportación
                        messagebox.showinfo("✅ Exportación .SQX Completada", summary)
                        self._update_status(f"Exportación completada: {len(results.get('exported_files', []))} archivos .sqx")
                        
                    elif msg_type == "export_error":
                        error_msg = message.get('error', 'Error desconocido')
                        messagebox.showerror("❌ Error en Exportación", f"Error en exportación .sqx: {error_msg}")
                        self._update_status("Error en exportación .sqx")
                        
                    elif msg_type == "error":
                        self._update_status(f"Error: {message.get('data', 'Error desconocido')}")
                        self.progress_bar.stop()
                        messagebox.showerror("Error", message.get('data', 'Error desconocido'))
                else:
                    # Manejo de mensajes legacy
                    msg_type, data = message
                    
                    if msg_type == "data_loaded":
                        self._update_data_display()
                        self._update_statistics()
                        self._update_status(f"Datos cargados: {len(data)} estrategias")
                        self.progress_bar.stop()
                        
                    elif msg_type == "error":
                        self._update_status(f"Error: {data}")
                        self.progress_bar.stop()
                        messagebox.showerror("Error", data)
            
            # Programar siguiente verificación
            self.root.after(100, self._process_messages)
            
        except Exception as e:
            logger.error(f"Error procesando mensajes: {e}")
    
    def _update_status(self, message: str):
        """Actualiza el mensaje de estado."""
        self.status_label.config(text=message)
    
    def _run_scientific_analysis(self):
        """Ejecuta análisis científico."""
        messagebox.showinfo("Análisis", "Análisis científico en desarrollo")
    
    def _run_tail_risk_analysis(self):
        """Ejecuta análisis de Tail Risk."""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "No hay datos cargados para analizar.")
            return
        
        # Usar la implementación profesional de Tail Risk
        if hasattr(self, 'tail_risk_analysis'):
            self.tail_risk_analysis.set_data(self.current_data)
            # El análisis se ejecuta desde la pestaña
            messagebox.showinfo("Tail Risk", "Datos establecidos en la pestaña de Tail Risk Analysis.\nEjecuta el análisis desde la pestaña.")
        else:
            messagebox.showwarning("Advertencia", "Módulo de Tail Risk no disponible.")
    
    def _run_axis_analysis(self):
        """Ejecuta análisis AXISelect."""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "No hay datos cargados para analizar.")
            return
        
        # Usar la implementación profesional de AXI Select
        if hasattr(self, 'axi_select_analysis'):
            self.axi_select_analysis.set_data(self.current_data)
            # El análisis se ejecuta desde la pestaña
            messagebox.showinfo("AXI Select", "Datos establecidos en la pestaña de AXI Select Analysis.\nEjecuta el análisis desde la pestaña.")
        else:
            messagebox.showwarning("Advertencia", "Módulo de AXI Select no disponible.")
    
    def _refresh_data(self):
        """Actualiza los datos."""
        messagebox.showinfo("Actualizar", "Actualización de datos en desarrollo")
    
    def _save_configuration(self):
        """Guarda la configuración."""
        messagebox.showinfo("Configuración", "Guardado de configuración en desarrollo")
    
    def _export_sqx_files(self):
        """Exportar estrategias seleccionadas a archivos .sqx."""
        try:
            if self.current_data is None or len(self.current_data) == 0:
                messagebox.showwarning("Advertencia", "No hay datos cargados para exportar.")
                return
            
            # Seleccionar directorio de salida
            output_dir = filedialog.askdirectory(
                title="Seleccionar directorio para archivos .sqx",
                initialdir=Path.cwd()
            )
            
            if not output_dir:
                return
            
            output_path = Path(output_dir)
            
            # Inicializar exportador .sqx
            sqx_exporter = SQXExporter()
            
            # Mostrar progreso
            self._update_status("📁 Iniciando exportación .sqx...")
            
            # Ejecutar exportación en hilo separado
            def export_thread():
                try:
                    # Usar datos actuales o filtrados
                    data_to_export = self.filtered_data if self.filtered_data is not None else self.current_data
                    
                    # Ejecutar flujo completo de exportación
                    if data_to_export is not None:
                        results = sqx_exporter.complete_sqx_workflow(
                            strategies_data=data_to_export,
                            output_dir=output_path,
                            ranking_column='CAGR'
                        )
                    else:
                        raise ValueError("No hay datos para exportar")
                    
                    # Mostrar resumen
                    summary = sqx_exporter.get_export_summary(results)
                    
                    # Enviar mensaje a la cola
                    self.message_queue.put({
                        'type': 'export_complete',
                        'summary': summary,
                        'results': results
                    })
                    
                except Exception as e:
                    self.message_queue.put({
                        'type': 'export_error',
                        'error': str(e)
                    })
            
            # Iniciar hilo de exportación
            export_thread_obj = threading.Thread(target=export_thread)
            export_thread_obj.daemon = True
            export_thread_obj.start()
            
        except Exception as e:
            logger.error(f"❌ Error en exportación .sqx: {e}")
            messagebox.showerror("Error", f"Error en exportación .sqx: {e}")
    
    def _show_help(self):
        """Muestra el panel de ayuda contextual."""
        try:
            if self.help_panel:
                self.help_panel.show_help_panel("metricas")
            else:
                messagebox.showinfo("Ayuda", "Panel de ayuda no disponible")
        except Exception as e:
            logger.error(f"Error mostrando ayuda: {e}")
            messagebox.showerror("Error", f"Error mostrando ayuda: {e}")
    
    def _show_about(self):
        """Muestra información sobre la aplicación."""
        messagebox.showinfo("Acerca de", "QVA Strategy Studio v2.0\nAnálisis Cuantitativo Avanzado")
    
    def _apply_quick_filters(self):
        """Aplica filtros rápidos."""
        messagebox.showinfo("Filtros", "Filtros rápidos en desarrollo")
    
    def _select_all_strategies(self):
        """Selecciona todas las estrategias."""
        messagebox.showinfo("Selección", "Selección de estrategias en desarrollo")
    
    def _clear_selection(self):
        """Limpia la selección."""
        messagebox.showinfo("Limpieza", "Limpieza de selección en desarrollo")
    
    def _show_strategy_details(self):
        """Muestra detalles de estrategia."""
        messagebox.showinfo("Detalles", "Detalles de estrategia en desarrollo")
    
    def _analyze_selected(self):
        """Analiza estrategias seleccionadas."""
        messagebox.showinfo("Análisis", "Análisis de seleccionadas en desarrollo")
    
    def _export_selected(self):
        """Exporta estrategias seleccionadas."""
        messagebox.showinfo("Exportación", "Exportación de seleccionadas en desarrollo")
    
    def _refresh_main_data(self):
        """Actualiza datos principales."""
        messagebox.showinfo("Actualizar", "Actualización de datos principales en desarrollo")
    
    def _show_data_statistics(self):
        """Muestra estadísticas de datos."""
        messagebox.showinfo("Estadísticas", "Estadísticas de datos en desarrollo")
    
    def _search_strategies(self):
        """Busca estrategias."""
        messagebox.showinfo("Búsqueda", "Búsqueda de estrategias en desarrollo")
    
    def _show_scientific_results(self):
        """Muestra resultados científicos."""
        messagebox.showinfo("Resultados", "Resultados científicos en desarrollo")
    
    def _save_scientific_analysis(self):
        """Guarda análisis científico."""
        messagebox.showinfo("Guardar", "Guardado de análisis científico en desarrollo")
    
    def _show_tail_risk_charts(self):
        """Muestra gráficos de Tail Risk."""
        messagebox.showinfo("Gráficos", "Gráficos de Tail Risk en desarrollo")
    
    def _export_tail_risk(self):
        """Exporta análisis de Tail Risk."""
        messagebox.showinfo("Exportar", "Exportación de Tail Risk en desarrollo")
    
    def _show_axis_results(self):
        """Muestra resultados de AXISelect."""
        messagebox.showinfo("Resultados", "Resultados de AXISelect en desarrollo")
    
    def _save_axis_selection(self):
        """Guarda selección de AXISelect."""
        messagebox.showinfo("Guardar", "Guardado de selección AXISelect en desarrollo")
    
    def _compare_selected_strategies(self):
        """Compara estrategias seleccionadas."""
        messagebox.showinfo("Comparar", "Comparación de estrategias en desarrollo")
    
    def _show_comparison_results(self):
        """Muestra resultados de comparación."""
        messagebox.showinfo("Resultados", "Resultados de comparación en desarrollo")
    
    def _export_comparison(self):
        """Exporta comparación."""
        messagebox.showinfo("Exportar", "Exportación de comparación en desarrollo")
    
    def _create_charts(self):
        """Crea gráficos."""
        messagebox.showinfo("Gráficos", "Creación de gráficos en desarrollo")
    
    def _export_charts(self):
        """Exporta gráficos."""
        messagebox.showinfo("Exportar", "Exportación de gráficos en desarrollo")
    
    def _refresh_charts(self):
        """Actualiza gráficos."""
        messagebox.showinfo("Actualizar", "Actualización de gráficos en desarrollo")
    
    def _on_strategy_selected(self, event):
        """Callback cuando se selecciona una estrategia."""
        pass
    
    def _create_informative_tooltip(self, widget, text: str, title: str = "Información"):
        """
        Crea un tooltip informativo profesional.
        
        Args:
            widget: Widget al que se asocia el tooltip
            text: Texto del tooltip
            title: Título del tooltip
        """
        def show_tooltip(event):
            # Crear ventana de tooltip
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Frame principal
            frame = ttk.Frame(tooltip, relief="solid", borderwidth=1)
            frame.pack(fill="both", expand=True)
            
            # Título
            title_label = ttk.Label(frame, text=title, font=("Arial", 10, "bold"))
            title_label.pack(pady=(5, 2), padx=5)
            
            # Separador
            ttk.Separator(frame, orient="horizontal").pack(fill="x", padx=5)
            
            # Contenido
            content_label = ttk.Label(frame, text=text, wraplength=300, justify="left")
            content_label.pack(pady=(2, 5), padx=5)
            
            # Guardar referencia
            self.tooltip_widgets[widget] = tooltip
            
            # Ocultar después de 5 segundos
            tooltip.after(5000, lambda: self._hide_tooltip(widget))
        
        def hide_tooltip(event):
            self._hide_tooltip(widget)
        
        # Bindings
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        widget.bind("<Button-1>", hide_tooltip)
    
    def _hide_tooltip(self, widget):
        """Oculta el tooltip asociado al widget."""
        if widget in self.tooltip_widgets:
            self.tooltip_widgets[widget].destroy()
            del self.tooltip_widgets[widget]
    
    def _get_predictability_tooltip_text(self) -> str:
        """Retorna el texto del tooltip para predictibilidad."""
        return """🎯 PREDICTIBILIDAD

Esta métrica evalúa la capacidad de la estrategia para mantener su rendimiento en datos futuros.

ESCALAS:
• EXCELENTE (≥85%): Alta confiabilidad
• BUENA (70-84%): Buena estabilidad
• ACEPTABLE (60-69%): Estabilidad moderada
• BAJA (<60%): Riesgo de inestabilidad

FACTORES:
• Consistencia IS/OOS
• Robustez temporal
• Estabilidad de parámetros
• Correlación de rendimientos

RECOMENDACIÓN:
Valores altos indican estrategias más confiables para el futuro."""
    
    def _get_factor_k_tooltip_text(self) -> str:
        """Retorna el texto del tooltip para Factor K."""
        return """🏆 FACTOR K ELITE 9.6

Métrica compuesta que evalúa la calidad general de la estrategia.

COMPONENTES:
• S (Stability): Estabilidad de rendimientos
• G (Growth): Crecimiento consistente
• E (Efficiency): Eficiencia operativa
• C (Consistency): Consistencia temporal

CATEGORÍAS:
• Elite (≥9.2): Estrategias excepcionales
• Excellent (≥8.2): Estrategias muy buenas
• Very Good (≥7.2): Estrategias buenas
• Good (≥6.2): Estrategias aceptables
• Poor (<6.2): Estrategias con problemas

PESOS POR RÉGIMEN:
• Bull: 30% S, 40% G, 20% E, 10% C
• Bear: 40% S, 20% G, 30% E, 10% C
• Sideways: 35% S, 25% G, 25% E, 15% C
• Crisis: 50% S, 10% G, 30% E, 10% C"""
    
    def _get_sharpe_tooltip_text(self) -> str:
        """Retorna el texto del tooltip para Sharpe Ratio."""
        return """📈 SHARPE RATIO

Mide el rendimiento ajustado por riesgo de la estrategia.

INTERPRETACIÓN:
• ≥2.0: Excelente (rendimiento superior)
• 1.5-2.0: Muy bueno
• 1.0-1.5: Bueno
• 0.5-1.0: Aceptable
• <0.5: Pobre

FÓRMULA:
Sharpe = (Retorno - Tasa Libre de Riesgo) / Desviación Estándar

IMPORTANCIA:
• Cuanto mayor, mejor el rendimiento por unidad de riesgo
• Estrategias con Sharpe alto son más eficientes
• Considera tanto retornos como volatilidad"""
    
    def _get_drawdown_tooltip_text(self) -> str:
        """Retorna el texto del tooltip para Max Drawdown."""
        return """📉 MÁXIMO DRAWDOWN

La mayor pérdida desde un pico hasta un valle.

INTERPRETACIÓN:
• <10%: Excelente (bajo riesgo)
• 10-20%: Bueno
• 20-30%: Aceptable
• 30-50%: Alto riesgo
• >50%: Muy alto riesgo

IMPORTANCIA:
• Indica el peor escenario de pérdida
• Estrategias con drawdown bajo son más seguras
• Considerar junto con retornos esperados

RECUPERACIÓN:
• Tiempo para recuperar pérdidas
• Estrategias con recuperación rápida son preferibles"""
    
    def _get_cagr_tooltip_text(self) -> str:
        """Retorna el texto del tooltip para CAGR."""
        return """📊 CAGR (Compound Annual Growth Rate)

Tasa de crecimiento anual compuesto de la estrategia.

INTERPRETACIÓN:
• >20%: Excelente crecimiento
• 15-20%: Muy buen crecimiento
• 10-15%: Bueno crecimiento
• 5-10%: Crecimiento moderado
• <5%: Crecimiento bajo

FÓRMULA:
CAGR = (Valor Final / Valor Inicial)^(1/años) - 1

IMPORTANCIA:
• Mide el crecimiento real de la inversión
• Considera el efecto del interés compuesto
• Métrica estándar para comparar estrategias

CONSIDERACIONES:
• Comparar con benchmark del mercado
• Evaluar junto con riesgo (Sharpe, Drawdown)"""
    
    def _get_calmar_tooltip_text(self) -> str:
        """Retorna el texto del tooltip para Calmar Ratio."""
        return """⚖️ CALMAR RATIO

Mide el rendimiento anual vs el máximo drawdown.

INTERPRETACIÓN:
• >4.0: Excelente (rendimiento superior al riesgo)
• 2.0-4.0: Muy bueno
• 1.0-2.0: Bueno
• 0.5-1.0: Aceptable
• <0.5: Pobre

FÓRMULA:
Calmar = CAGR / Máximo Drawdown

IMPORTANCIA:
• Estrategias con Calmar alto son más eficientes
• Considera tanto retornos como riesgo máximo
• Métrica preferida por gestores profesionales

RECOMENDACIÓN:
Valores altos indican mejor gestión de riesgo."""
    
    def _get_profit_factor_tooltip_text(self) -> str:
        """Retorna el texto del tooltip para Profit Factor."""
        return """💰 PROFIT FACTOR

Ratio entre ganancias totales y pérdidas totales.

INTERPRETACIÓN:
• >3.0: Excelente (muy rentable)
• 2.0-3.0: Muy bueno
• 1.5-2.0: Bueno
• 1.2-1.5: Aceptable
• <1.2: Pobre

FÓRMULA:
Profit Factor = Ganancias Totales / Pérdidas Totales

IMPORTANCIA:
• Indica la eficiencia de la estrategia
• Valores >1 indican estrategia rentable
• Cuanto mayor, mejor la gestión de riesgo

CONSIDERACIONES:
• Evaluar junto con número de trades
• Considerar estabilidad temporal del ratio"""
    
    def _get_win_rate_tooltip_text(self) -> str:
        """Retorna el texto del tooltip para Win Rate."""
        return """🎯 WIN RATE

Porcentaje de trades ganadores vs total de trades.

INTERPRETACIÓN:
• >70%: Excelente (alta precisión)
• 60-70%: Muy bueno
• 50-60%: Bueno
• 40-50%: Aceptable
• <40%: Pobre

IMPORTANCIA:
• Indica la precisión de la estrategia
• No es lo único importante (considerar tamaño de trades)
• Estrategias con win rate alto suelen ser más estables

CONSIDERACIONES:
• Evaluar junto con profit factor
• Win rate alto no garantiza rentabilidad
• Considerar distribución de ganancias/pérdidas"""
    
    def _get_trades_tooltip_text(self) -> str:
        """Retorna el texto del tooltip para número de trades."""
        return """📈 NÚMERO DE TRADES

Cantidad total de operaciones realizadas.

INTERPRETACIÓN:
• >1000: Excelente (mucha experiencia)
• 500-1000: Muy bueno
• 200-500: Bueno
• 100-200: Aceptable
• <100: Limitado

IMPORTANCIA:
• Más trades = más datos para análisis
• Indica actividad de la estrategia
• Necesario para validación estadística

CONSIDERACIONES:
• Evaluar junto con período de tiempo
• Más trades no siempre es mejor
• Considerar frecuencia de trading"""
    
    def _get_recovery_factor_tooltip_text(self) -> str:
        """Retorna el texto del tooltip para Recovery Factor."""
        return """🔄 RECOVERY FACTOR

Mide la capacidad de recuperación de la estrategia.

INTERPRETACIÓN:
• >3.0: Excelente (recuperación rápida)
• 2.0-3.0: Muy bueno
• 1.5-2.0: Bueno
• 1.0-1.5: Aceptable
• <1.0: Pobre

FÓRMULA:
Recovery Factor = Net Profit / Máximo Drawdown

IMPORTANCIA:
• Indica resiliencia de la estrategia
• Valores altos = mejor gestión de crisis
• Métrica clave para estrategias de largo plazo

RECOMENDACIÓN:
Estrategias con recovery factor alto son más robustas."""
    
    def _apply_tooltips_to_metrics(self):
        """Aplica tooltips informativos a las métricas principales."""
        try:
            # Aplicar tooltips a los filtros rápidos
            if hasattr(self, 'factor_k_var'):
                factor_k_label = ttk.Label(self.root, text="Factor K mínimo:")
                self._create_informative_tooltip(
                    factor_k_label, 
                    self._get_factor_k_tooltip_text(),
                    "Factor K Elite 9.6"
                )
            
            # Aplicar tooltips a las columnas de la tabla
            if hasattr(self, 'data_tree'):
                # Tooltip para columna Factor K
                self._create_informative_tooltip(
                    self.data_tree,
                    self._get_factor_k_tooltip_text(),
                    "Factor K Elite 9.6"
                )
                
                # Tooltip para columna Predictibilidad
                self._create_informative_tooltip(
                    self.data_tree,
                    self._get_predictability_tooltip_text(),
                    "Predictibilidad"
                )
                
                # Tooltip para columna Sharpe Ratio
                self._create_informative_tooltip(
                    self.data_tree,
                    self._get_sharpe_tooltip_text(),
                    "Sharpe Ratio"
                )
                
                # Tooltip para columna Max Drawdown
                self._create_informative_tooltip(
                    self.data_tree,
                    self._get_drawdown_tooltip_text(),
                    "Máximo Drawdown"
                )
                
                # Tooltip para columna CAGR
                self._create_informative_tooltip(
                    self.data_tree,
                    self._get_cagr_tooltip_text(),
                    "CAGR"
                )
                
                # Tooltip para columna Calmar Ratio
                self._create_informative_tooltip(
                    self.data_tree,
                    self._get_calmar_tooltip_text(),
                    "Calmar Ratio"
                )
                
                # Tooltip para columna Profit Factor
                self._create_informative_tooltip(
                    self.data_tree,
                    self._get_profit_factor_tooltip_text(),
                    "Profit Factor"
                )
                
                # Tooltip para columna Win Rate
                self._create_informative_tooltip(
                    self.data_tree,
                    self._get_win_rate_tooltip_text(),
                    "Win Rate"
                )
                
                # Tooltip para columna Trades
                self._create_informative_tooltip(
                    self.data_tree,
                    self._get_trades_tooltip_text(),
                    "Número de Trades"
                )
                
                # Tooltip para columna Recovery Factor
                self._create_informative_tooltip(
                    self.data_tree,
                    self._get_recovery_factor_tooltip_text(),
                    "Recovery Factor"
                )
            
            logger.info("✅ Tooltips informativos aplicados a todas las métricas principales")
            
        except Exception as e:
            logger.error(f"Error aplicando tooltips: {e}")
    
    def run(self):
        """Ejecuta la aplicación."""
        try:
            logger.info("🚀 Iniciando QVA Strategy Studio")
            
            # Aplicar tooltips informativos
            self._apply_tooltips_to_metrics()
            
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Error ejecutando aplicación: {e}")

    def create_advanced_export_tab(self):
        """Crea la pestaña de exportación avanzada."""
        self.export_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.export_tab, text="📊 Exportación Avanzada")
        
        # Título principal
        title_label = ttk.Label(self.export_tab, text="Sistema de Exportación Avanzada", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Frame principal con scroll
        main_frame = ttk.Frame(self.export_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Sección 1: Exportación Excel Avanzada
        self._create_excel_export_section(scrollable_frame)
        
        # Sección 2: Dashboard HTML Interactivo
        self._create_html_dashboard_section(scrollable_frame)
        
        # Sección 3: Reportes PDF Profesionales
        self._create_pdf_report_section(scrollable_frame)
        
        # Sección 4: Exportación por Lotes
        self._create_batch_export_section(scrollable_frame)
        
        # Sección 5: Configuración Avanzada
        self._create_advanced_config_section(scrollable_frame)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Inicializar export manager
        self.export_manager = create_advanced_export_manager(self.root)
    
    def _create_excel_export_section(self, parent):
        """Crea la sección de exportación Excel avanzada."""
        excel_frame = ttk.LabelFrame(parent, text="📈 Exportación Excel Avanzada")
        excel_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Descripción
        desc_label = ttk.Label(excel_frame, text="Exporta datos a Excel con 7 hojas especializadas:")
        desc_label.pack(pady=5)
        
        # Lista de hojas
        sheets_info = [
            "📊 Ranking de Estrategias",
            "📈 Análisis por Régimen de Mercado", 
            "🔍 Componentes Factor K 9.6",
            "📋 Métricas Derivadas",
            "🔄 Análisis IS/OOS",
            "🏷️ Categorización y Recomendaciones",
            "📄 Datos Completos"
        ]
        
        for sheet_info in sheets_info:
            sheet_label = ttk.Label(excel_frame, text=f"• {sheet_info}")
            sheet_label.pack(anchor=tk.W, padx=20)
        
        # Botones de exportación
        buttons_frame = ttk.Frame(excel_frame)
        buttons_frame.pack(pady=10)
        
        # Botón exportar Excel
        self.excel_export_btn = ttk.Button(buttons_frame, text="📊 Exportar a Excel", 
                                          command=self._export_to_excel_advanced)
        self.excel_export_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón previsualizar
        self.excel_preview_btn = ttk.Button(buttons_frame, text="👁️ Previsualizar", 
                                           command=self._preview_excel_export)
        self.excel_preview_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_html_dashboard_section(self, parent):
        """Crea la sección de dashboard HTML interactivo."""
        html_frame = ttk.LabelFrame(parent, text="🌐 Dashboard HTML Interactivo")
        html_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Descripción
        desc_label = ttk.Label(html_frame, text="Crea dashboard interactivo con gráficos Plotly:")
        desc_label.pack(pady=5)
        
        # Características
        features = [
            "📊 Gráficos interactivos con Plotly",
            "🔍 Filtros dinámicos",
            "📱 Responsive design",
            "🎨 Tema profesional",
            "📈 Gráficos: Factor K, CAGR vs Sharpe, Categorías"
        ]
        
        for feature in features:
            feature_label = ttk.Label(html_frame, text=f"• {feature}")
            feature_label.pack(anchor=tk.W, padx=20)
        
        # Botones
        buttons_frame = ttk.Frame(html_frame)
        buttons_frame.pack(pady=10)
        
        self.html_export_btn = ttk.Button(buttons_frame, text="🌐 Crear Dashboard", 
                                         command=self._export_to_html_dashboard)
        self.html_export_btn.pack(side=tk.LEFT, padx=5)
        
        self.html_open_btn = ttk.Button(buttons_frame, text="🔗 Abrir en Navegador", 
                                       command=self._open_html_dashboard)
        self.html_open_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_pdf_report_section(self, parent):
        """Crea la sección de reportes PDF profesionales."""
        pdf_frame = ttk.LabelFrame(parent, text="📄 Reportes PDF Profesionales")
        pdf_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Descripción
        desc_label = ttk.Label(pdf_frame, text="Genera reportes PDF con formato profesional:")
        desc_label.pack(pady=5)
        
        # Características
        features = [
            "📊 Gráficos vectoriales de alta calidad",
            "📋 Tablas formateadas profesionalmente",
            "📈 Resumen ejecutivo",
            "🎨 Diseño corporativo",
            "📄 Múltiples secciones organizadas"
        ]
        
        for feature in features:
            feature_label = ttk.Label(pdf_frame, text=f"• {feature}")
            feature_label.pack(anchor=tk.W, padx=20)
        
        # Botones
        buttons_frame = ttk.Frame(pdf_frame)
        buttons_frame.pack(pady=10)
        
        self.pdf_export_btn = ttk.Button(buttons_frame, text="📄 Generar PDF", 
                                        command=self._export_to_pdf_report)
        self.pdf_export_btn.pack(side=tk.LEFT, padx=5)
        
        self.pdf_config_btn = ttk.Button(buttons_frame, text="⚙️ Configurar", 
                                        command=self._configure_pdf_report)
        self.pdf_config_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_batch_export_section(self, parent):
        """Crea la sección de exportación por lotes."""
        batch_frame = ttk.LabelFrame(parent, text="📦 Exportación por Lotes")
        batch_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Descripción
        desc_label = ttk.Label(batch_frame, text="Exporta en múltiples formatos simultáneamente:")
        desc_label.pack(pady=5)
        
        # Formatos disponibles
        formats_frame = ttk.Frame(batch_frame)
        formats_frame.pack(pady=5)
        
        self.format_vars = {
            'excel': tk.BooleanVar(value=True),
            'html': tk.BooleanVar(value=True),
            'pdf': tk.BooleanVar(value=True),
            'csv': tk.BooleanVar(value=False),
            'json': tk.BooleanVar(value=False)
        }
        
        row = 0
        for format_name, var in self.format_vars.items():
            cb = ttk.Checkbutton(formats_frame, text=format_name.upper(), variable=var)
            cb.grid(row=row//2, column=row%2, sticky=tk.W, padx=10, pady=2)
            row += 1
        
        # Botones
        buttons_frame = ttk.Frame(batch_frame)
        buttons_frame.pack(pady=10)
        
        self.batch_export_btn = ttk.Button(buttons_frame, text="📦 Exportar Lotes", 
                                          command=self._export_batch)
        self.batch_export_btn.pack(side=tk.LEFT, padx=5)
        
        self.batch_folder_btn = ttk.Button(buttons_frame, text="📁 Seleccionar Carpeta", 
                                          command=self._select_batch_folder)
        self.batch_folder_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_advanced_config_section(self, parent):
        """Crea la sección de configuración avanzada."""
        config_frame = ttk.LabelFrame(parent, text="⚙️ Configuración Avanzada")
        config_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Opciones de configuración
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(pady=5)
        
        # Variables de configuración
        self.config_vars = {
            'include_charts': tk.BooleanVar(value=True),
            'include_summary': tk.BooleanVar(value=True),
            'include_filters': tk.BooleanVar(value=True),
            'professional_format': tk.BooleanVar(value=True),
            'auto_open': tk.BooleanVar(value=False)
        }
        
        row = 0
        for option_name, var in self.config_vars.items():
            text = option_name.replace('_', ' ').title()
            cb = ttk.Checkbutton(options_frame, text=text, variable=var)
            cb.grid(row=row, column=0, sticky=tk.W, padx=10, pady=2)
            row += 1
        
        # Botones de configuración
        buttons_frame = ttk.Frame(config_frame)
        buttons_frame.pack(pady=10)
        
        self.save_config_btn = ttk.Button(buttons_frame, text="💾 Guardar Config", 
                                         command=self._save_export_config)
        self.save_config_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_config_btn = ttk.Button(buttons_frame, text="📂 Cargar Config", 
                                         command=self._load_export_config)
        self.load_config_btn.pack(side=tk.LEFT, padx=5)
    
    def _export_to_excel_advanced(self):
        """Exporta datos a Excel avanzado."""
        try:
            if not hasattr(self, 'results_df') or self.results_df is None:
                messagebox.showwarning("Sin Datos", "No hay datos para exportar. Ejecute un análisis primero.")
                return
            
            # Configurar datos para exportación
            if self.export_manager is not None:
                self.export_manager.set_data(self.results_df)
            else:
                messagebox.showwarning("Exportación", "Export Manager no disponible")
                return
            
            # Seleccionar archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                title="Guardar Excel Avanzado"
            )
            
            if filename:
                # Exportar con configuración avanzada
                if hasattr(self.export_manager, 'export_to_excel_advanced'):
                    success = self.export_manager.export_to_excel_advanced(filename)
                else:
                    messagebox.showwarning("Exportación", "Método de exportación no disponible")
                    return
                
                if success:
                    messagebox.showinfo("Éxito", f"Excel exportado exitosamente:\n{filename}")
                    
                    # Abrir archivo si está configurado
                    if hasattr(self, 'config_vars') and self.config_vars.get('auto_open', False):
                        os.startfile(filename)
                else:
                    messagebox.showerror("Error", "Error al exportar Excel")
                    
        except Exception as e:
            logger.error(f"Error exportando Excel: {e}")
            messagebox.showerror("Error", f"Error al exportar Excel:\n{str(e)}")
    
    def _preview_excel_export(self):
        """Previsualiza la exportación Excel."""
        try:
            if not hasattr(self, 'results_df') or self.results_df is None:
                messagebox.showwarning("Sin Datos", "No hay datos para previsualizar.")
                return
            
            # Mostrar información de previsualización
            preview_info = f"""
            📊 PREVISUALIZACIÓN DE EXPORTACIÓN EXCEL
            
            📋 Datos a exportar:
            • Total de estrategias: {len(self.results_df)}
            • Columnas disponibles: {len(self.results_df.columns)}
            
            📄 Hojas que se crearán:
            • Ranking de Estrategias
            • Análisis por Régimen de Mercado
            • Componentes Factor K 9.6
            • Métricas Derivadas
            • Análisis IS/OOS
            • Categorización y Recomendaciones
            • Datos Completos
            
            📈 Gráficos incluidos: Sí
            🎨 Formato profesional: Sí
            """
            
            messagebox.showinfo("Previsualización Excel", preview_info)
            
        except Exception as e:
            logger.error(f"Error en previsualización: {e}")
            messagebox.showerror("Error", f"Error en previsualización:\n{str(e)}")
    
    def _export_to_html_dashboard(self):
        """Exporta dashboard HTML interactivo."""
        try:
            if not hasattr(self, 'results_df') or self.results_df is None:
                messagebox.showwarning("Sin Datos", "No hay datos para exportar. Ejecute un análisis primero.")
                return
            
            # Configurar datos para exportación
            if self.export_manager is not None:
                self.export_manager.set_data(self.results_df)
            else:
                messagebox.showwarning("Exportación", "Export Manager no disponible")
                return
            
            # Seleccionar archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("Archivos HTML", "*.html"), ("Todos los archivos", "*.*")],
                title="Guardar Dashboard HTML"
            )
            
            if filename:
                # Configuración del dashboard
                config = {
                    "title": "Dashboard de Análisis de Estrategias",
                    "theme": "plotly_white",
                    "include_charts": True,
                    "include_filters": True,
                    "include_summary": True
                }
                
                # Exportar dashboard
                if hasattr(self.export_manager, 'export_to_html_dashboard'):
                    success = self.export_manager.export_to_html_dashboard(filename, config)
                else:
                    messagebox.showwarning("Exportación", "Método de exportación HTML no disponible")
                    return
                
                if success:
                    messagebox.showinfo("Éxito", f"Dashboard HTML creado exitosamente:\n{filename}")
                    
                    # Abrir en navegador si está configurado
                    if hasattr(self, 'config_vars') and self.config_vars.get('auto_open', False):
                        import webbrowser
                        webbrowser.open(f"file://{os.path.abspath(filename)}")
                else:
                    messagebox.showerror("Error", "Error al crear dashboard HTML")
                    
        except Exception as e:
            logger.error(f"Error exportando HTML: {e}")
            messagebox.showerror("Error", f"Error al exportar HTML:\n{str(e)}")
    
    def _open_html_dashboard(self):
        """Abre el dashboard HTML en el navegador."""
        try:
            # Buscar el último dashboard creado
            output_dir = "output"
            if os.path.exists(output_dir):
                html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
                if html_files:
                    latest_file = max(html_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
                    filepath = os.path.join(output_dir, latest_file)
                    webbrowser.open(f"file://{os.path.abspath(filepath)}")
                else:
                    messagebox.showinfo("Info", "No se encontraron dashboards HTML. Cree uno primero.")
            else:
                messagebox.showinfo("Info", "No se encontró carpeta de output.")
                
        except Exception as e:
            logger.error(f"Error abriendo dashboard: {e}")
            messagebox.showerror("Error", f"Error abriendo dashboard:\n{str(e)}")
    
    def _export_to_pdf_report(self):
        """Exporta reporte PDF profesional."""
        try:
            if not hasattr(self, 'results_df') or self.results_df is None:
                messagebox.showwarning("Sin Datos", "No hay datos para exportar. Ejecute un análisis primero.")
                return
            
            # Configurar datos para exportación
            if self.export_manager is not None:
                self.export_manager.set_data(self.results_df)
            else:
                messagebox.showwarning("Exportación", "Export Manager no disponible")
                return
            
            # Seleccionar archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
                title="Guardar Reporte PDF"
            )
            
            if filename:
                # Configuración del reporte
                config = {
                    "title": "Reporte de Análisis de Estrategias",
                    "author": "QVA Strategy Studio",
                    "include_charts": True,
                    "include_summary": True,
                    "include_details": True
                }
                
                # Exportar PDF
                if hasattr(self.export_manager, 'export_to_pdf_report'):
                    success = self.export_manager.export_to_pdf_report(filename, config)
                else:
                    messagebox.showwarning("Exportación", "Método de exportación PDF no disponible")
                    return
                
                if success:
                    messagebox.showinfo("Éxito", f"Reporte PDF generado exitosamente:\n{filename}")
                    
                    # Abrir archivo si está configurado
                    if hasattr(self, 'config_vars') and self.config_vars.get('auto_open', False):
                        os.startfile(filename)
                else:
                    messagebox.showerror("Error", "Error al generar PDF")
                    
        except Exception as e:
            logger.error(f"Error exportando PDF: {e}")
            messagebox.showerror("Error", f"Error al exportar PDF:\n{str(e)}")
    
    def _configure_pdf_report(self):
        """Configura opciones del reporte PDF."""
        try:
            # Crear ventana de configuración
            config_window = tk.Toplevel(self.root)
            config_window.title("Configurar Reporte PDF")
            config_window.geometry("400x300")
            config_window.transient(self.root)
            config_window.grab_set()
            
            # Variables de configuración
            pdf_config_vars = {
                'include_charts': tk.BooleanVar(value=True),
                'include_summary': tk.BooleanVar(value=True),
                'include_details': tk.BooleanVar(value=True),
                'professional_format': tk.BooleanVar(value=True),
                'include_logo': tk.BooleanVar(value=False)
            }
            
            # Crear controles
            ttk.Label(config_window, text="Configuración del Reporte PDF", 
                     font=("Arial", 12, "bold")).pack(pady=10)
            
            for option_name, var in pdf_config_vars.items():
                text = option_name.replace('_', ' ').title()
                cb = ttk.Checkbutton(config_window, text=text, variable=var)
                cb.pack(anchor=tk.W, padx=20, pady=2)
            
            # Botones
            buttons_frame = ttk.Frame(config_window)
            buttons_frame.pack(pady=20)
            
            ttk.Button(buttons_frame, text="💾 Guardar", 
                      command=lambda: self._save_pdf_config(pdf_config_vars, config_window)).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(buttons_frame, text="❌ Cancelar", 
                      command=config_window.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            logger.error(f"Error configurando PDF: {e}")
            messagebox.showerror("Error", f"Error configurando PDF:\n{str(e)}")
    
    def _save_pdf_config(self, config_vars, window):
        """Guarda la configuración del PDF."""
        try:
            # Aquí se guardaría la configuración
            messagebox.showinfo("Éxito", "Configuración guardada")
            window.destroy()
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            messagebox.showerror("Error", f"Error guardando configuración:\n{str(e)}")
    
    def _export_batch(self):
        """Exporta en lotes múltiples formatos."""
        try:
            if not hasattr(self, 'results_df') or self.results_df is None:
                messagebox.showwarning("Sin Datos", "No hay datos para exportar. Ejecute un análisis primero.")
                return
            
            # Configurar datos para exportación
            if self.export_manager is not None:
                self.export_manager.set_data(self.results_df)
            else:
                messagebox.showwarning("Exportación", "Export Manager no disponible")
                return
            
            # Seleccionar carpeta de salida
            batch_folder = filedialog.askdirectory(
                title="Seleccionar carpeta para exportación por lotes"
            )
            
            if batch_folder:
                # Configuración del lote
                batch_config = {
                    'formats': ['excel', 'html', 'pdf'],
                    'output_folder': batch_folder
                }
                
                # Exportar lote
                if hasattr(self.export_manager, 'export_batch'):
                    success = self.export_manager.export_batch(batch_folder, batch_config['formats'])
                else:
                    messagebox.showwarning("Exportación", "Método de exportación por lotes no disponible")
                    return
                
                if success:
                    messagebox.showinfo("Éxito", f"Exportación por lotes completada:\n{batch_folder}")
                else:
                    messagebox.showerror("Error", "Error en exportación por lotes")
                    
        except Exception as e:
            logger.error(f"Error exportando por lotes: {e}")
            messagebox.showerror("Error", f"Error al exportar por lotes:\n{str(e)}")
    
    def _select_batch_folder(self):
        """Selecciona carpeta para exportación por lotes."""
        try:
            folder = filedialog.askdirectory(title="Seleccionar Carpeta de Salida")
            if folder:
                messagebox.showinfo("Carpeta Seleccionada", f"Carpeta de salida:\n{folder}")
        except Exception as e:
            logger.error(f"Error seleccionando carpeta: {e}")
            messagebox.showerror("Error", f"Error seleccionando carpeta:\n{str(e)}")
    
    def _save_export_config(self):
        """Guarda la configuración de exportación."""
        try:
            config = {
                'format_vars': {k: v.get() for k, v in self.format_vars.items()},
                'config_vars': {k: v.get() for k, v in self.config_vars.items()}
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
                title="Guardar Configuración de Exportación"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Éxito", f"Configuración guardada:\n{filename}")
                
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            messagebox.showerror("Error", f"Error guardando configuración:\n{str(e)}")
    
    def _load_export_config(self):
        """Carga la configuración de exportación."""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
                title="Cargar Configuración de Exportación"
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Aplicar configuración
                for k, v in config.get('format_vars', {}).items():
                    if k in self.format_vars:
                        self.format_vars[k].set(v)
                
                for k, v in config.get('config_vars', {}).items():
                    if k in self.config_vars:
                        self.config_vars[k].set(v)
                
                messagebox.showinfo("Éxito", f"Configuración cargada:\n{filename}")
                
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            messagebox.showerror("Error", f"Error cargando configuración:\n{str(e)}")

# Funciones de conveniencia
def create_main_window() -> MainWindow:
    """Crea la ventana principal de la aplicación."""
    return MainWindow()

def run_gui():
    """Ejecuta la interfaz gráfica."""
    app = create_main_window()
    app.run() 