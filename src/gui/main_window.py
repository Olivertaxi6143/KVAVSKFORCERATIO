import numpy as np
from typing import Optional, Any, Union
import warnings
"""
Main Window - Ventana Principal Modularizada

Este módulo contiene la ventana principal que integra todos los pasos
del wizard de análisis de estrategias de trading.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import pandas as pd
from typing import Optional, Dict, Any, Callable
from pathlib import Path

# Importar módulos de pasos
from .steps.step1_load import Step1LoadFrame
from .steps.step2_configure import Step2ConfigureFrame

# Importar módulos de análisis avanzado
from src.analysis.tail_risk_metrics import TailRiskAnalyzer

# Importar utilidades GUI
from .utils import (
    create_styled_button, create_styled_label, show_info_message,
    show_error_message, GUIAnalysisError, create_menu_bar, center_window
)

# Configurar logging
try:
    from core.logger_config import setup_logger
    logger = setup_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class MainWindow(tk.Tk):
    """
    Ventana principal modularizada del sistema de análisis cuantitativo.
    
    Esta clase reemplaza la clase monolítica EnhancedRankGUI y organiza
    la interfaz en módulos separados para mejor mantenibilidad.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa la ventana principal.
        
        Args:
            *args: Argumentos para tk.Tk
            **kwargs: Argumentos adicionales
        """
        super().__init__(*args, **kwargs)
        
        # Configurar ventana principal
        self.title("QVA Strategy Studio - Análisis Cuantitativo")
        self.geometry("1200x800")
        center_window(self, 1200, 800)
        
        # Inicializar componentes
        self._init_components()
        self._init_data_managers()
        self._init_variables()
        self._build_interface()
        self._setup_logging()
        
        logger.info("✅ MainWindow inicializada correctamente")
    
    def _init_components(self):
        """Inicializa los componentes principales."""
        # Notebook principal
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pasos del wizard
        self.wizard_steps = {}
        self.current_step = 1
        
        # Frames de pasos
        self.step_frames = {}
        
        # Datos compartidos entre pasos
        self.shared_data: Dict[str, Any] = {
            'loaded_data': None,
            'configuration': None,
            'analysis_results': None,
            'filtered_results': None,
            'advisor_results': None
        }
    
    def _init_data_managers(self):
        """Inicializa los gestores de datos."""
        try:
            # DataManager
            from data.data_manager import DataManager
            self.data_manager = DataManager()
            
            # ConfigManager
            from src.core.config.config_manager import ConfigManagerEnhanced as ConfigManager
            self.config_manager = ConfigManager()
            
            logger.info("✅ Gestores de datos inicializados")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando gestores de datos: {e}")
            self.data_manager = None
            self.config_manager = None
    
    def _init_variables(self):
        """Inicializa variables de la interfaz."""
        # Variables de archivos
        self.kpi_file_var = tk.StringVar()
        self.strategies_folder_var = tk.StringVar()
        self.market_file_var = tk.StringVar()
        self.destination_folder_var = tk.StringVar()
        
        # Variables de configuración
        self.trading_style_var = tk.StringVar(value="Swing")
        self.alpha_var = tk.DoubleVar(value=0.8)
        self.percentile_var = tk.IntVar(value=80)
        self.top_n_var = tk.IntVar(value=20)
        
        # Variables de estado
        self.analysis_running = False
        self.data_loaded = False
        self.config_ready = False
    
    def _build_interface(self):
        """Construye la interfaz principal."""
        # Crear menú
        self._create_menu()
        
        # Crear pasos del wizard
        self._create_wizard_steps()
        
        # Crear pestañas adicionales
        self._create_additional_tabs()
        
        # Configurar navegación
        self._setup_navigation()
    
    def _create_menu(self):
        """Crea la barra de menú."""
        self.menubar = create_menu_bar(self)
    
    def _create_wizard_steps(self):
        """Crea los pasos del wizard."""
        # Paso 1: Cargar Datos
        self._create_step1()
        
        # Paso 2: Configurar Análisis
        self._create_step2()
        
        # Paso 3: Ejecutar Análisis (placeholder)
        self._create_step3()
        
        # Paso 4: Resultados y Filtrado (placeholder)
        self._create_step4()
        
        # Paso 5: Asesor Inteligente (placeholder)
        self._create_step5()
        
        # Paso 6: Exportar y Reportar (placeholder)
        self._create_step6()
    
    def _create_step1(self):
        """Crea el Paso 1: Cargar Datos."""
        try:
            step1_frame = Step1LoadFrame(
                self.notebook,
                data_manager=self.data_manager,
                on_data_loaded=self._on_data_loaded,
                on_next_step=lambda: self._go_to_step(2)
            )
            
            self.notebook.add(step1_frame, text="1️⃣ Cargar Datos")
            self.wizard_steps[1] = step1_frame
            self.step_frames['step1'] = step1_frame
            
            logger.info("✅ Paso 1 creado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error creando Paso 1: {e}")
            self._create_step1_placeholder()
    
    def _create_step2(self):
        """Crea el Paso 2: Configurar Análisis."""
        try:
            step2_frame = Step2ConfigureFrame(
                self.notebook,
                config_manager=self.config_manager,
                on_config_changed=self._on_config_changed,
                on_next_step=lambda: self._go_to_step(3),
                on_previous_step=lambda: self._go_to_step(1)
            )
            
            self.notebook.add(step2_frame, text="2️⃣ Configurar Análisis")
            self.wizard_steps[2] = step2_frame
            self.step_frames['step2'] = step2_frame
            
            logger.info("✅ Paso 2 creado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error creando Paso 2: {e}")
            self._create_step2_placeholder()
    
    def _create_step3(self):
        """Crea el Paso 3: Ejecutar Análisis (placeholder)."""
        step3_frame = ttk.Frame(self.notebook)
        
        # Título
        title_label = ttk.Label(
            step3_frame, 
            text="🚀 PASO 3: EJECUTAR ANÁLISIS", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Descripción
        desc_label = ttk.Label(
            step3_frame, 
            text="Este paso será implementado próximamente...", 
            font=("Arial", 10)
        )
        desc_label.pack(pady=10)
        
        self.notebook.add(step3_frame, text="3️⃣ Ejecutar Análisis")
        self.wizard_steps[3] = step3_frame
        self.step_frames['step3'] = step3_frame
    
    def _create_step4(self):
        """Crea el Paso 4: Resultados y Filtrado (placeholder)."""
        step4_frame = ttk.Frame(self.notebook)
        
        # Título
        title_label = ttk.Label(
            step4_frame, 
            text="📊 PASO 4: RESULTADOS Y FILTRADO", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Descripción
        desc_label = ttk.Label(
            step4_frame, 
            text="Este paso será implementado próximamente...", 
            font=("Arial", 10)
        )
        desc_label.pack(pady=10)
        
        self.notebook.add(step4_frame, text="4️⃣ Resultados")
        self.wizard_steps[4] = step4_frame
        self.step_frames['step4'] = step4_frame
    
    def _create_step5(self):
        """Crea el Paso 5: Asesor Inteligente (placeholder)."""
        step5_frame = ttk.Frame(self.notebook)
        
        # Título
        title_label = ttk.Label(
            step5_frame, 
            text="🎯 PASO 5: ASESOR INTELIGENTE", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Descripción
        desc_label = ttk.Label(
            step5_frame, 
            text="Este paso será implementado próximamente...", 
            font=("Arial", 10)
        )
        desc_label.pack(pady=10)
        
        self.notebook.add(step5_frame, text="5️⃣ Asesor")
        self.wizard_steps[5] = step5_frame
        self.step_frames['step5'] = step5_frame
    
    def _create_step6(self):
        """Crea el Paso 6: Exportar y Reportar (placeholder)."""
        step6_frame = ttk.Frame(self.notebook)
        
        # Título
        title_label = ttk.Label(
            step6_frame, 
            text="📤 PASO 6: EXPORTAR Y REPORTAR", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Descripción
        desc_label = ttk.Label(
            step6_frame, 
            text="Este paso será implementado próximamente...", 
            font=("Arial", 10)
        )
        desc_label.pack(pady=10)
        
        self.notebook.add(step6_frame, text="6️⃣ Exportar")
        self.wizard_steps[6] = step6_frame
        self.step_frames['step6'] = step6_frame
    
    def _create_step1_placeholder(self):
        """Crea un placeholder para el Paso 1 si falla la carga."""
        step1_frame = ttk.Frame(self.notebook)
        
        # Título
        title_label = ttk.Label(
            step1_frame, 
            text="📁 PASO 1: CARGAR DATOS", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Error
        error_label = ttk.Label(
            step1_frame, 
            text="Error cargando el módulo del Paso 1", 
            font=("Arial", 10),
            foreground="red"
        )
        error_label.pack(pady=10)
        
        self.notebook.add(step1_frame, text="1️⃣ Cargar Datos")
        self.wizard_steps[1] = step1_frame
    
    def _create_step2_placeholder(self):
        """Crea un placeholder para el Paso 2 si falla la carga."""
        step2_frame = ttk.Frame(self.notebook)
        
        # Título
        title_label = ttk.Label(
            step2_frame, 
            text="⚙️ PASO 2: CONFIGURAR ANÁLISIS", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Error
        error_label = ttk.Label(
            step2_frame, 
            text="Error cargando el módulo del Paso 2", 
            font=("Arial", 10),
            foreground="red"
        )
        error_label.pack(pady=10)
        
        self.notebook.add(step2_frame, text="2️⃣ Configurar Análisis")
        self.wizard_steps[2] = step2_frame
    
    def _create_additional_tabs(self):
        """Crea pestañas adicionales."""
        # Pestaña de Log
        self._create_log_tab()
        
        # Pestaña de Ayuda
        self._create_help_tab()
        
        # Pestaña de Régimen Adaptativo
        self._create_regime_tab()

        # Pestaña de Análisis de Tail Risk
        self._create_tail_risk_tab()
    
    def _create_log_tab(self):
        """Crea la pestaña de log."""
        log_frame = ttk.Frame(self.notebook)
        
        # Título
        title_label = ttk.Label(
            log_frame, 
            text="📝 Log de Análisis", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Área de texto para log
        self.log_text = tk.Text(
            log_frame, 
            height=20, 
            width=80,
            bg="black",
            fg="white",
            font=("Consolas", 9)
        )
        self.log_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.notebook.add(log_frame, text="📝 Log")
    
    def _create_help_tab(self):
        """Crea la pestaña de ayuda."""
        help_frame = ttk.Frame(self.notebook)
        
        # Título
        title_label = ttk.Label(
            help_frame, 
            text="❓ Ayuda", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Contenido de ayuda
        help_text = """
        Guía de Uso del Sistema:
        
        1. Cargar Datos: Selecciona archivos CSV o Excel con datos de estrategias
        2. Configurar Análisis: Ajusta parámetros y KPIs para el análisis
        3. Ejecutar Análisis: Procesa los datos y genera resultados
        4. Resultados: Visualiza y filtra los resultados del análisis
        5. Asesor: Obtén recomendaciones inteligentes sobre las estrategias
        6. Exportar: Guarda los resultados en diferentes formatos
        
        Para más información, consulta la documentación del proyecto.
        """
        
        help_text_widget = tk.Text(
            help_frame, 
            height=20, 
            width=80,
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        help_text_widget.pack(padx=10, pady=10, fill="both", expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.configure(state=tk.DISABLED)
        
        self.notebook.add(help_frame, text="❓ Ayuda")
    
    def _create_regime_tab(self):
        """Crea la pestaña de régimen adaptativo."""
        regime_frame = ttk.Frame(self.notebook)
        
        # Título
        title_label = ttk.Label(
            regime_frame, 
            text="🎯 Régimen de Mercado Adaptativo", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Frame principal con scroll
        main_scroll = ttk.Scrollbar(regime_frame, orient="vertical")
        main_scroll.pack(side="right", fill="y")
        
        canvas = tk.Canvas(regime_frame, yscrollcommand=main_scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        main_scroll.config(command=canvas.yview)
        
        # Frame interno para contenido
        content_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Sección 1: Información del Régimen Actual
        regime_info_frame = ttk.LabelFrame(content_frame, text="📊 Régimen Actual", padding=10)
        regime_info_frame.pack(fill="x", padx=10, pady=5)
        
        self.regime_current_label = ttk.Label(regime_info_frame, text="Régimen: No detectado")
        self.regime_current_label.pack(anchor="w")
        
        self.regime_confidence_label = ttk.Label(regime_info_frame, text="Confianza: N/A")
        self.regime_confidence_label.pack(anchor="w")
        
        # Sección 2: Pesos Optimizados
        weights_frame = ttk.LabelFrame(content_frame, text="⚙️ Pesos Optimizados", padding=10)
        weights_frame.pack(fill="x", padx=10, pady=5)
        
        self.weights_profitability_label = ttk.Label(weights_frame, text="Rentabilidad: 40%")
        self.weights_profitability_label.pack(anchor="w")
        
        self.weights_risk_label = ttk.Label(weights_frame, text="Riesgo: 30%")
        self.weights_risk_label.pack(anchor="w")
        
        self.weights_consistency_label = ttk.Label(weights_frame, text="Consistencia: 30%")
        self.weights_consistency_label.pack(anchor="w")
        
        self.weights_ml_label = ttk.Label(weights_frame, text="ML: 15%")
        self.weights_ml_label.pack(anchor="w")
        
        # Sección 3: Estrategias Óptimas
        optimal_frame = ttk.LabelFrame(content_frame, text="🏆 Estrategias Óptimas", padding=10)
        optimal_frame.pack(fill="x", padx=10, pady=5)
        
        self.optimal_count_label = ttk.Label(optimal_frame, text="Cantidad: 0")
        self.optimal_count_label.pack(anchor="w")
        
        # Lista de estrategias óptimas
        self.optimal_listbox = tk.Listbox(optimal_frame, height=8, width=60)
        self.optimal_listbox.pack(fill="x", pady=5)
        
        # Sección 4: Botones de Control
        control_frame = ttk.Frame(content_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.detect_regime_button = ttk.Button(
            control_frame, 
            text="🔍 Detectar Régimen",
            command=self._detect_current_regime
        )
        self.detect_regime_button.pack(side="left", padx=5)
        
        self.optimize_weights_button = ttk.Button(
            control_frame, 
            text="⚙️ Optimizar Pesos",
            command=self._optimize_weights
        )
        self.optimize_weights_button.pack(side="left", padx=5)
        
        self.apply_adaptive_scoring_button = ttk.Button(
            control_frame, 
            text="🎯 Aplicar Scoring Adaptativo",
            command=self._apply_adaptive_scoring
        )
        self.apply_adaptive_scoring_button.pack(side="left", padx=5)
        
        # Configurar scroll
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        self.notebook.add(regime_frame, text="🎯 Régimen")
    
    def _create_tail_risk_tab(self):
        """Crea la pestaña de análisis de Tail Risk."""
        tail_risk_frame = ttk.Frame(self.notebook)
        
        # Título
        title_label = ttk.Label(
            tail_risk_frame, 
            text="🧱 Análisis de Tail Risk", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Frame principal con scroll
        main_scroll = ttk.Scrollbar(tail_risk_frame, orient="vertical")
        main_scroll.pack(side="right", fill="y")
        
        canvas = tk.Canvas(tail_risk_frame, yscrollcommand=main_scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        main_scroll.config(command=canvas.yview)
        
        # Frame interno para contenido
        content_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Sección 1: Información de Tail Risk
        tail_risk_info_frame = ttk.LabelFrame(content_frame, text="📊 Información de Tail Risk", padding=10)
        tail_risk_info_frame.pack(fill="x", padx=10, pady=5)
        
        self.tail_risk_summary_label = ttk.Label(tail_risk_info_frame, text="Resumen: No disponible")
        self.tail_risk_summary_label.pack(anchor="w")
        
        self.tail_risk_max_drawdown_label = ttk.Label(tail_risk_info_frame, text="Máx. Drawdown: N/A")
        self.tail_risk_max_drawdown_label.pack(anchor="w")
        
        self.tail_risk_tail_ratio_label = ttk.Label(tail_risk_info_frame, text="Tail Ratio: N/A")
        self.tail_risk_tail_ratio_label.pack(anchor="w")
        
        # Sección 2: Botones de Control
        control_frame = ttk.Frame(content_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.analyze_tail_risk_button = ttk.Button(
            control_frame, 
            text="📊 Analizar Tail Risk",
            command=self._analyze_tail_risk
        )
        self.analyze_tail_risk_button.pack(side="left", padx=5)
        
        self.tail_risk_results_button = ttk.Button(
            control_frame, 
            text="📈 Ver Resultados",
            command=self._view_tail_risk_results
        )
        self.tail_risk_results_button.pack(side="left", padx=5)
        
        # Configurar scroll
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        self.notebook.add(tail_risk_frame, text="🧱 Tail Risk")
    
    def _detect_current_regime(self):
        """Detecta el régimen de mercado actual."""
        try:
            logger.info("🔍 Detectando régimen de mercado...")
            
            # Obtener datos de mercado si están disponibles
            market_data = self.shared_data.get('market_data')
            if market_data is None:
                show_error_message("Error", "No hay datos de mercado disponibles")
                return
            
            # Importar y usar el detector de régimen
            from src.core.market_regime_analyzer import MarketRegimeDetector
            regime_detector = MarketRegimeDetector()
            
            # Detectar régimen
            current_regime = regime_detector.detect_current_regime(market_data)
            
            # Actualizar interfaz
            self.regime_current_label.config(text=f"Régimen: {current_regime.upper()}")
            self.regime_confidence_label.config(text="Confianza: Alta")
            
            # Guardar régimen en datos compartidos
            self.shared_data['current_regime'] = current_regime
            
            logger.info(f"✅ Régimen detectado: {current_regime}")
            show_info_message("Éxito", f"Régimen detectado: {current_regime}")
            
        except Exception as e:
            logger.error(f"❌ Error detectando régimen: {e}")
            show_error_message("Error", f"Error detectando régimen: {str(e)}")
    
    def _optimize_weights(self):
        """Optimiza pesos basado en el régimen actual."""
        try:
            logger.info("⚙️ Optimizando pesos...")
            
            current_regime = self.shared_data.get('current_regime')
            if not current_regime:
                show_error_message("Error", "Primero detecta el régimen actual")
                return
            
            strategies = self.shared_data.get('loaded_data')
            if strategies is None:
                show_error_message("Error", "No hay estrategias cargadas")
                return
            
            # Importar y usar el detector de régimen
            from src.core.market_regime_analyzer import MarketRegimeDetector
            regime_detector = MarketRegimeDetector()
            
            # Calcular rendimiento por régimen
            regime_performance = regime_detector.calculate_regime_performance(strategies, current_regime)
            
            # Optimizar pesos
            optimized_weights = regime_detector.optimize_weights_by_regime(regime_performance, current_regime)
            
            # Actualizar interfaz
            self.weights_profitability_label.config(text=f"Rentabilidad: {optimized_weights.get('profitability', 0.4)*100:.1f}%")
            self.weights_risk_label.config(text=f"Riesgo: {optimized_weights.get('risk', 0.3)*100:.1f}%")
            self.weights_consistency_label.config(text=f"Consistencia: {optimized_weights.get('consistency', 0.3)*100:.1f}%")
            self.weights_ml_label.config(text=f"ML: {optimized_weights.get('ml', 0.15)*100:.1f}%")
            
            # Guardar pesos optimizados
            self.shared_data['optimized_weights'] = optimized_weights
            
            logger.info(f"✅ Pesos optimizados: {optimized_weights}")
            show_info_message("Éxito", "Pesos optimizados correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error optimizando pesos: {e}")
            show_error_message("Error", f"Error optimizando pesos: {str(e)}")
    
    def _apply_adaptive_scoring(self):
        """Aplica scoring adaptativo a las estrategias."""
        try:
            logger.info("🎯 Aplicando scoring adaptativo...")
            
            strategies = self.shared_data.get('loaded_data')
            optimized_weights = self.shared_data.get('optimized_weights')
            
            if strategies is None:
                show_error_message("Error", "No hay estrategias cargadas")
                return
            
            if optimized_weights is None:
                show_error_message("Error", "Primero optimiza los pesos")
                return
            
            # Importar y usar el detector de régimen
            from src.core.market_regime_analyzer import MarketRegimeDetector
            regime_detector = MarketRegimeDetector()
            
            # Aplicar scoring adaptativo
            adaptive_scores = regime_detector.apply_adaptive_scoring(strategies, optimized_weights)
            
            # Actualizar lista de estrategias óptimas
            optimal_strategies = adaptive_scores.head(10)['Strategy_Name'].tolist()
            self.optimal_count_label.config(text=f"Cantidad: {len(optimal_strategies)}")
            
            # Limpiar y llenar listbox
            self.optimal_listbox.delete(0, tk.END)
            for i, strategy in enumerate(optimal_strategies, 1):
                self.optimal_listbox.insert(tk.END, f"{i}. {strategy}")
            
            # Guardar resultados
            self.shared_data['adaptive_scores'] = adaptive_scores
            
            logger.info(f"✅ Scoring adaptativo aplicado a {len(adaptive_scores)} estrategias")
            show_info_message("Éxito", f"Scoring adaptativo aplicado a {len(adaptive_scores)} estrategias")
            
        except Exception as e:
            logger.error(f"❌ Error aplicando scoring adaptativo: {e}")
            show_error_message("Error", f"Error aplicando scoring adaptativo: {str(e)}")
    
    def _analyze_tail_risk(self):
        """Ejecuta el análisis de Tail Risk."""
        try:
            logger.info("📊 Analizando Tail Risk...")
            
            strategies = self.shared_data.get('loaded_data')
            if strategies is None:
                show_error_message("Error", "No hay estrategias cargadas para analizar Tail Risk")
                return
            
            # Crear instancia del analizador de Tail Risk
            tail_risk_analyzer = TailRiskAnalyzer()
            
            # Realizar análisis usando el método correcto
            results = tail_risk_analyzer.analyze_tail_risk_metrics(strategies)
            
            if "error" in results:
                show_error_message("Error", f"Error en análisis de Tail Risk: {results['error']}")
                return
            
            # Calcular métricas agregadas
            summary = f"Analizadas {len(results)} estrategias"
            max_drawdown = max([r.get('max_drawdown', 0) for r in results.values() if not pd.isna(r.get('max_drawdown', 0))], default=0)
            avg_var_95 = np.mean([r.get('var_95', 0) for r in results.values() if not pd.isna(r.get('var_95', 0))])
            
            # Actualizar interfaz
            self.tail_risk_summary_label.config(text=f"Resumen: {summary}")
            self.tail_risk_max_drawdown_label.config(text=f"Máx. Drawdown: {max_drawdown:.2f}%")
            self.tail_risk_tail_ratio_label.config(text=f"Avg VaR 95%: {avg_var_95:.4f}")
            
            # Guardar resultados
            self.shared_data['tail_risk_results'] = results
            
            logger.info(f"✅ Tail Risk analizado. {summary}")
            show_info_message("Éxito", "Tail Risk analizado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error analizando Tail Risk: {e}")
            show_error_message("Error", f"Error analizando Tail Risk: {str(e)}")
    
    def _view_tail_risk_results(self):
        """Muestra los resultados del análisis de Tail Risk."""
        try:
            results = self.shared_data.get('tail_risk_results')
            if results is None:
                show_error_message("Error", "No hay resultados de Tail Risk para mostrar")
                return
            
            # Crear una ventana emergente para mostrar los resultados
            tail_risk_window = tk.Toplevel(self)
            tail_risk_window.title("Resultados de Tail Risk")
            tail_risk_window.geometry("800x600")
            center_window(tail_risk_window, 800, 600)

            # Frame principal con scroll
            main_frame = ttk.Frame(tail_risk_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Título
            title_label = ttk.Label(main_frame, text="📊 Resultados de Análisis de Tail Risk", 
                                   font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 10))

            # Texto para mostrar los resultados detallados
            results_text = "=== RESULTADOS DE TAIL RISK ===\n\n"
            
            for strategy_name, metrics in results.items():
                if strategy_name == "error":
                    continue
                    
                results_text += f"🔸 ESTRATEGIA: {strategy_name}\n"
                results_text += f"   VaR 95%: {metrics.get('var_95', 'N/A'):.4f}\n"
                results_text += f"   CVaR 95%: {metrics.get('cvar_95', 'N/A'):.4f}\n"
                results_text += f"   Expected Shortfall: {metrics.get('expected_shortfall', 'N/A'):.4f}\n"
                results_text += f"   Max Drawdown: {metrics.get('max_drawdown', 'N/A'):.2f}%\n"
                results_text += f"   Tail Concentration: {metrics.get('tail_concentration', 'N/A'):.4f}\n"
                results_text += f"   Extreme Loss Prob: {metrics.get('extreme_loss_probability', 'N/A'):.4f}\n"
                results_text += f"   Skewness: {metrics.get('skewness', 'N/A'):.4f}\n"
                results_text += f"   Kurtosis: {metrics.get('kurtosis', 'N/A'):.4f}\n"
                results_text += "-" * 50 + "\n\n"
            
            # Widget de texto con scroll
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill="both", expand=True)
            
            text_widget = tk.Text(text_frame, font=("Consolas", 9), wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            text_widget.insert(tk.END, results_text)
            text_widget.configure(state=tk.DISABLED)

            # Botones de acción
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x", pady=10)
            
            # Botón para copiar resultados
            copy_btn = ttk.Button(button_frame, text="📋 Copiar Resultados", 
                                 command=lambda: self._copy_tail_risk_results(results_text))
            copy_btn.pack(side="left", padx=5)
            
            # Botón para cerrar
            close_button = ttk.Button(button_frame, text="Cerrar", command=tail_risk_window.destroy)
            close_button.pack(side="right", padx=5)

            logger.info("📈 Mostrando resultados detallados de Tail Risk")
            
        except Exception as e:
            logger.error(f"❌ Error mostrando resultados de Tail Risk: {e}")
            show_error_message("Error", f"Error mostrando resultados de Tail Risk: {str(e)}")
    
    def _copy_tail_risk_results(self, results_text: str):
        """Copia los resultados de Tail Risk al portapapeles."""
        try:
            self.clipboard_clear()
            self.clipboard_append(results_text)
            show_info_message("Éxito", "Resultados de Tail Risk copiados al portapapeles")
            logger.info("📋 Resultados de Tail Risk copiados al portapapeles")
        except Exception as e:
            logger.error(f"❌ Error copiando resultados: {e}")
            show_error_message("Error", f"Error copiando resultados: {str(e)}")
    
    def _setup_navigation(self):
        """Configura la navegación entre pasos."""
        # Bind para cambio de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _setup_logging(self):
        """Configura el logging para la interfaz."""
        try:
            # Configurar handler para el widget de texto
            from .utils import setup_logging_to_widget
            setup_logging_to_widget(self.log_text)
            
            logger.info("✅ Logging configurado para la interfaz")
            
        except Exception as e:
            logger.error(f"❌ Error configurando logging: {e}")
    
    def _on_tab_changed(self, event):
        """Maneja el cambio de pestaña."""
        try:
            current_tab = self.notebook.select()
            tab_id = self.notebook.index(current_tab)
            
            # Actualizar paso actual
            if tab_id < 6:  # Solo los pasos del wizard
                self.current_step = tab_id + 1
                logger.info(f"✅ Cambiado al paso {self.current_step}")
            
        except Exception as e:
            logger.error(f"❌ Error cambiando pestaña: {e}")
    
    def _go_to_step(self, step_number):
        """Navega a un paso específico del wizard."""
        try:
            if step_number in self.wizard_steps:
                self.notebook.select(self.wizard_steps[step_number])
                self.current_step = step_number
                logger.info(f"✅ Navegando al paso {step_number}")
            else:
                logger.warning(f"⚠️ Paso {step_number} no encontrado")
                
        except Exception as e:
            logger.error(f"❌ Error navegando al paso {step_number}: {e}")
    
    def _on_data_loaded(self, data):
        """Callback cuando se cargan datos."""
        try:
            self.shared_data['loaded_data'] = data
            self.data_loaded = True
            
            # Habilitar siguiente paso
            if hasattr(self, 'step_frames') and 'step2' in self.step_frames:
                step2 = self.step_frames['step2']
                if hasattr(step2, 'is_ready_for_next_step'):
                    # El paso 2 ahora puede continuar
                    pass
            
            logger.info("✅ Datos cargados correctamente")
            show_info_message("Éxito", "Datos cargados correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error procesando datos cargados: {e}")
            show_error_message("Error", f"Error procesando datos: {str(e)}")
    
    def _on_config_changed(self):
        """Callback cuando cambia la configuración."""
        try:
            # Obtener configuración del paso 2
            if hasattr(self, 'step_frames') and 'step2' in self.step_frames:
                step2 = self.step_frames['step2']
                if hasattr(step2, 'get_configuration'):
                    config = step2.get_configuration()
                    self.shared_data['configuration'] = config
                    self.config_ready = True
                    
                    logger.info("✅ Configuración actualizada")
            
        except Exception as e:
            logger.error(f"❌ Error procesando cambio de configuración: {e}")
    
    def get_shared_data(self) -> Dict[str, Any]:
        """Obtiene los datos compartidos entre pasos."""
        return self.shared_data.copy()
    
    def set_shared_data(self, key: str, value: Any):
        """Establece un valor en los datos compartidos."""
        self.shared_data[key] = value
    
    def run_analysis(self):
        """Ejecuta el análisis completo."""
        try:
            if not self.data_loaded:
                show_error_message("Error", "Por favor, carga los datos primero")
                return
            
            if not self.config_ready:
                show_error_message("Error", "Por favor, configura el análisis primero")
                return
            
            # Aquí se implementaría la lógica de análisis
            logger.info("🚀 Iniciando análisis...")
            show_info_message("Análisis", "Análisis iniciado...")
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando análisis: {e}")
            show_error_message("Error", f"Error ejecutando análisis: {str(e)}")
    
    def export_results(self):
        """Exporta los resultados."""
        try:
            if not self.shared_data.get('analysis_results'):
                show_error_message("Error", "No hay resultados para exportar")
                return
            
            # Aquí se implementaría la lógica de exportación
            logger.info("📤 Exportando resultados...")
            show_info_message("Exportación", "Resultados exportados...")
            
        except Exception as e:
            logger.error(f"❌ Error exportando resultados: {e}")
            show_error_message("Error", f"Error exportando resultados: {str(e)}")
    
    def reset_wizard(self):
        """Reinicia el wizard."""
        try:
            # Reiniciar todos los pasos
            for step_name, step_frame in self.step_frames.items():
                if hasattr(step_frame, 'reset_step'):
                    step_frame.reset_step()
            
            # Limpiar datos compartidos
            self.shared_data = {
                'loaded_data': None,
                'configuration': None,
                'analysis_results': None,
                'filtered_results': None,
                'advisor_results': None
            }
            
            # Ir al primer paso
            self._go_to_step(1)
            
            logger.info("✅ Wizard reiniciado")
            show_info_message("Reinicio", "Wizard reiniciado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error reiniciando wizard: {e}")
            show_error_message("Error", f"Error reiniciando wizard: {str(e)}")
    
    def show_about(self):
        """Muestra el diálogo 'Acerca de'."""
        try:
            from .utils import create_about_dialog
            create_about_dialog(self)
            
        except Exception as e:
            logger.error(f"❌ Error mostrando diálogo 'Acerca de': {e}")
            show_error_message("Error", f"Error mostrando información: {str(e)}")


def create_main_window():
    """
    Función factory para crear la ventana principal.
    
    Returns:
        MainWindow: Instancia de la ventana principal
    """
    return MainWindow()


if __name__ == "__main__":
    # Test de la ventana principal
    app = create_main_window()
    app.mainloop() 