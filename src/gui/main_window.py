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

# Importar módulos de la aplicación
from src.data.data_manager import DataManager
# from src.analysis.scientific_analysis import ScientificAnalysis  # Comentado temporalmente
from src.gui.advanced_filters_popup import create_advanced_filters_popup
from src.gui.interactive_charts import create_interactive_chart_manager
from src.gui.strategy_comparison import create_strategy_comparison_manager
from src.gui.advanced_export import create_advanced_export_manager
# Añadir import del exportador .sqx
from src.data.sqx_exporter import SQXExporter

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
        
        # Variables de estado
        self.current_data = None
        self.filtered_data = None
        self.selected_strategies = []
        
        # Cola para comunicación entre hilos
        self.message_queue = queue.Queue()
        
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
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="🧪 Análisis Científico")
        
        # Controles de análisis
        controls_frame = ttk.Frame(analysis_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(controls_frame, text="🚀 Ejecutar Análisis", 
                  command=self._run_scientific_analysis).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="📊 Ver Resultados", 
                  command=self._show_scientific_results).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="💾 Guardar Análisis", 
                  command=self._save_scientific_analysis).pack(side="left", padx=5)
        
        # Área de resultados
        results_frame = ttk.Frame(analysis_frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.scientific_text = tk.Text(results_frame, wrap="word")
        self.scientific_text.pack(fill="both", expand=True)
    
    def _create_tail_risk_tab(self):
        """Crea pestaña de Tail Risk Analysis."""
        tail_risk_frame = ttk.Frame(self.notebook)
        self.notebook.add(tail_risk_frame, text="📈 Tail Risk Analysis")
        
        # Controles de Tail Risk
        controls_frame = ttk.Frame(tail_risk_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(controls_frame, text="📊 Analizar Tail Risk", 
                  command=self._run_tail_risk_analysis).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="📈 Ver Gráficos", 
                  command=self._show_tail_risk_charts).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="💾 Exportar Análisis", 
                  command=self._export_tail_risk).pack(side="left", padx=5)
        
        # Área de resultados
        results_frame = ttk.Frame(tail_risk_frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tail_risk_text = tk.Text(results_frame, wrap="word")
        self.tail_risk_text.pack(fill="both", expand=True)
    
    def _create_axis_tab(self):
        """Crea pestaña de AXISelect Analysis."""
        axis_frame = ttk.Frame(self.notebook)
        self.notebook.add(axis_frame, text="🎯 AXISelect Analysis")
        
        # Controles de AXISelect
        controls_frame = ttk.Frame(axis_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(controls_frame, text="🎯 Ejecutar AXISelect", 
                  command=self._run_axis_analysis).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="📊 Ver Selección", 
                  command=self._show_axis_results).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="💾 Guardar Selección", 
                  command=self._save_axis_selection).pack(side="left", padx=5)
        
        # Área de resultados
        results_frame = ttk.Frame(axis_frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.axis_text = tk.Text(results_frame, wrap="word")
        self.axis_text.pack(fill="both", expand=True)
    
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
            
            logger.info("✅ Gestores avanzados inicializados")
            
        except Exception as e:
            logger.error(f"Error inicializando gestores avanzados: {e}")
            # Crear gestores mock si falla la inicialización
            self.chart_manager = Mock()
            self.comparison_manager = Mock()
            self.export_manager = Mock()
    
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
            data = self.data_manager.load_data()
            
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
            
            corr_config = self.chart_manager.create_correlation_matrix_chart(
                self.current_data, "Matriz de Correlación de Estrategias"
            )
            corr_widget = self.chart_manager.create_chart_widget(corr_frame, corr_config)
            corr_widget.pack(fill="both", expand=True)
            
            # Gráfico de dispersión
            scatter_frame = ttk.Frame(notebook)
            notebook.add(scatter_frame, text="📊 Dispersión")
            
            scatter_config = self.chart_manager.create_scatter_plot(
                self.current_data, "CAGR_IS", "Sharpe_Ratio_IS", 
                color_col="Factor_K", title="CAGR vs Sharpe Ratio"
            )
            scatter_widget = self.chart_manager.create_chart_widget(scatter_frame, scatter_config)
            scatter_widget.pack(fill="both", expand=True)
            
            # Histograma
            hist_frame = ttk.Frame(notebook)
            notebook.add(hist_frame, text="📈 Histograma")
            
            hist_config = self.chart_manager.create_histogram_chart(
                self.current_data, "Factor_K", title="Distribución Factor K"
            )
            hist_widget = self.chart_manager.create_chart_widget(hist_frame, hist_config)
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
                self.comparison_manager.set_data(self.current_data)
                self.comparison_manager.select_strategies(selected_strategies)
                
                # Ejecutar comparación
                results = self.comparison_manager.compare_strategies()
                
                # Mostrar resultados
                results_frame = ttk.Frame(main_frame)
                results_frame.pack(fill="both", expand=True)
                
                results_widget = self.comparison_manager.create_comparison_widget(results_frame, results)
                results_widget.pack(fill="both", expand=True)
            
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
            self.export_manager.set_data(self.current_data)
            
            # Crear ventana de exportación
            export_window = tk.Toplevel(self.root)
            export_window.title("📤 Exportación Avanzada")
            export_window.geometry("600x400")
            
            # Crear diálogo de exportación
            export_widget = self.export_manager.create_export_dialog(export_window)
            export_widget.pack(fill="both", expand=True, padx=10, pady=10)
            
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
        messagebox.showinfo("Tail Risk", "Análisis de Tail Risk en desarrollo")
    
    def _run_axis_analysis(self):
        """Ejecuta análisis AXISelect."""
        messagebox.showinfo("AXISelect", "Análisis AXISelect en desarrollo")
    
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
                    results = sqx_exporter.complete_sqx_workflow(
                        strategies_data=data_to_export,
                        output_dir=output_path,
                        ranking_column='CAGR'
                    )
                    
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
        """Muestra la ayuda."""
        messagebox.showinfo("Ayuda", "Sistema de ayuda en desarrollo")
    
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
    
    def run(self):
        """Ejecuta la aplicación."""
        try:
            logger.info("🚀 Iniciando QVA Strategy Studio")
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Error ejecutando aplicación: {e}")

# Funciones de conveniencia
def create_main_window() -> MainWindow:
    """Crea la ventana principal de la aplicación."""
    return MainWindow()

def run_gui():
    """Ejecuta la interfaz gráfica."""
    app = create_main_window()
    app.run() 