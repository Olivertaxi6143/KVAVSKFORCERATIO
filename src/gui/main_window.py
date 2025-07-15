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
        self.shared_data = {
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
            from core.config.config_manager import ConfigManager
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
        help_text_widget.config(state=tk.DISABLED)
        
        self.notebook.add(help_frame, text="❓ Ayuda")
    
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