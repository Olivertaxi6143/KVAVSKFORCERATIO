"""
Módulo de Gestión de Errores Intuitiva para QVA Strategy Studio

Este módulo implementa un sistema profesional de gestión de errores que:
- Destaca visualmente los errores en la interfaz
- Proporciona navegación inteligente para resolver problemas
- Crea mensajes de error específicos y útiles
- Implementa prevención de errores con validaciones
"""

import tkinter as tk
from tkinter import messagebox, ttk
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import traceback
import sys

# Configurar logging
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Enumeración para niveles de severidad de errores."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Enumeración para categorías de errores."""
    DATA_LOAD = "data_load"
    VALIDATION = "validation"
    ANALYSIS = "analysis"
    EXPORT = "export"
    GUI = "gui"
    SYSTEM = "system"


@dataclass
class ErrorInfo:
    """Clase para almacenar información de errores."""
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    component: str
    suggestion: str
    action_required: bool
    navigation_target: Optional[str] = None


class ErrorHandler:
    """
    Clase principal para gestión de errores intuitiva.
    
    Proporciona:
    - Destacados visuales en la interfaz
    - Navegación inteligente para resolver problemas
    - Mensajes de error específicos y útiles
    - Prevención de errores con validaciones
    """
    
    def __init__(self, main_window):
        """Inicializa el manejador de errores."""
        self.main_window = main_window
        self.current_errors: List[ErrorInfo] = []
        self.error_indicators: Dict[str, tk.Widget] = {}
        self.error_colors = {
            ErrorSeverity.INFO: "#E3F2FD",
            ErrorSeverity.WARNING: "#FFF3E0",
            ErrorSeverity.ERROR: "#FFEBEE",
            ErrorSeverity.CRITICAL: "#FCE4EC"
        }
        self.border_colors = {
            ErrorSeverity.INFO: "#2196F3",
            ErrorSeverity.WARNING: "#FF9800",
            ErrorSeverity.ERROR: "#F44336",
            ErrorSeverity.CRITICAL: "#E91E63"
        }
        
        # Configurar callbacks
        self._setup_error_callbacks()
        
        logger.info("ErrorHandler inicializado correctamente")
    
    def _setup_error_callbacks(self):
        """Configura callbacks para manejo de errores."""
        # Interceptar excepciones no manejadas
        sys.excepthook = self._handle_uncaught_exception
        
        # Configurar logging de errores
        logging.getLogger().addHandler(self._create_error_handler())
    
    def _create_error_handler(self):
        """Crea un handler de logging para errores."""
        class ErrorLogHandler(logging.Handler):
            def __init__(self, error_handler):
                super().__init__()
                self.error_handler = error_handler
            
            def emit(self, record):
                if record.levelno >= logging.ERROR:
                    self.error_handler._log_error(record.getMessage(), record.exc_info)
        
        return ErrorLogHandler(self)
    
    def _handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """Maneja excepciones no capturadas."""
        error_msg = f"Error no manejado: {exc_type.__name__}: {exc_value}"
        logger.error(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
        
        # Crear error info
        error_info = ErrorInfo(
            message=str(exc_value),
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SYSTEM,
            component="Sistema",
            suggestion="Reinicie la aplicación y contacte al soporte técnico.",
            action_required=True
        )
        
        self.show_error(error_info)
    
    def _log_error(self, message: str, exc_info=None):
        """Registra un error en el sistema."""
        error_info = ErrorInfo(
            message=message,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.SYSTEM,
            component="Sistema",
            suggestion="Revise los logs para más detalles.",
            action_required=False
        )
        
        self.current_errors.append(error_info)
        logger.error(f"Error registrado: {message}", exc_info=exc_info)
    
    def show_error(self, error_info: ErrorInfo):
        """
        Muestra un error en la interfaz de usuario.
        
        Args:
            error_info: Información del error a mostrar
        """
        self.current_errors.append(error_info)
        
        # Crear ventana de error
        self._create_error_window(error_info)
        
        # Destacar componente problemático
        if error_info.component:
            self._highlight_problematic_component(error_info)
        
        # Navegar automáticamente si es necesario
        if error_info.navigation_target:
            self._navigate_to_target(error_info.navigation_target)
        
        logger.info(f"Error mostrado: {error_info.message}")
    
    def _create_error_window(self, error_info: ErrorInfo):
        """Crea una ventana de error profesional."""
        error_window = tk.Toplevel(self.main_window)
        error_window.title(f"Error - {error_info.severity.value.title()}")
        error_window.geometry("500x400")
        error_window.resizable(False, False)
        
        # Centrar ventana
        error_window.transient(self.main_window)
        error_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(error_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icono y título
        icon_label = ttk.Label(main_frame, text=self._get_error_icon(error_info.severity), 
                              font=("Arial", 24))
        icon_label.pack(pady=(0, 10))
        
        title_label = ttk.Label(main_frame, text=error_info.category.value.replace("_", " ").title(),
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Mensaje de error
        message_frame = ttk.Frame(main_frame)
        message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        message_text = tk.Text(message_frame, wrap=tk.WORD, height=8, 
                              font=("Arial", 10))
        message_text.pack(fill=tk.BOTH, expand=True)
        message_text.insert("1.0", error_info.message)
        message_text.config(state=tk.DISABLED)
        
        # Sugerencia
        if error_info.suggestion:
            suggestion_label = ttk.Label(main_frame, text="Sugerencia:", 
                                       font=("Arial", 10, "bold"))
            suggestion_label.pack(anchor=tk.W, pady=(10, 5))
            
            suggestion_text = ttk.Label(main_frame, text=error_info.suggestion,
                                      wraplength=450, justify=tk.LEFT)
            suggestion_text.pack(anchor=tk.W, pady=(0, 20))
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        if error_info.action_required:
            # Botón para ir a la sección problemática
            if error_info.navigation_target:
                navigate_btn = ttk.Button(button_frame, text="Ir a la sección",
                                        command=lambda: self._navigate_and_close(error_window, error_info.navigation_target))
                navigate_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # Botón para obtener ayuda
            help_btn = ttk.Button(button_frame, text="Obtener Ayuda",
                                command=lambda: self._show_help(error_info))
            help_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón cerrar
        close_btn = ttk.Button(button_frame, text="Cerrar",
                              command=error_window.destroy)
        close_btn.pack(side=tk.RIGHT)
        
        # Aplicar color de fondo según severidad
        error_window.configure(bg=self.error_colors[error_info.severity])
        main_frame.configure(style=self._get_error_style(error_info.severity))
    
    def _get_error_icon(self, severity: ErrorSeverity) -> str:
        """Retorna el icono apropiado para el nivel de severidad."""
        icons = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨"
        }
        return icons.get(severity, "❓")
    
    def _get_error_style(self, severity: ErrorSeverity) -> str:
        """Retorna el estilo apropiado para el nivel de severidad."""
        style_name = f"Error.{severity.value}"
        
        if not hasattr(self, '_styles_created'):
            self._create_error_styles()
        
        return style_name
    
    def _create_error_styles(self):
        """Crea estilos para diferentes niveles de error."""
        style = ttk.Style()
        
        for severity in ErrorSeverity:
            style_name = f"Error.{severity.value}"
            style.configure(style_name, 
                          background=self.error_colors[severity],
                          borderwidth=2,
                          relief="solid",
                          bordercolor=self.border_colors[severity])
        
        self._styles_created = True
    
    def _highlight_problematic_component(self, error_info: ErrorInfo):
        """Destaca visualmente el componente problemático."""
        component = error_info.component.lower()
        
        # Buscar widgets relacionados con el componente
        widgets_to_highlight = []
        
        if "cargar" in component or "data" in component:
            widgets_to_highlight = self._find_data_widgets()
        elif "filtro" in component:
            widgets_to_highlight = self._find_filter_widgets()
        elif "análisis" in component or "analysis" in component:
            widgets_to_highlight = self._find_analysis_widgets()
        elif "export" in component:
            widgets_to_highlight = self._find_export_widgets()
        
        # Aplicar destacado
        for widget in widgets_to_highlight:
            self._apply_highlight(widget, error_info.severity)
    
    def _find_data_widgets(self) -> List[tk.Widget]:
        """Encuentra widgets relacionados con carga de datos."""
        widgets = []
        
        # Buscar botones de carga
        for widget in self.main_window.winfo_children():
            if isinstance(widget, tk.Button) and "cargar" in widget.cget("text").lower():
                widgets.append(widget)
            elif isinstance(widget, ttk.Button) and "cargar" in widget.cget("text").lower():
                widgets.append(widget)
        
        return widgets
    
    def _find_filter_widgets(self) -> List[tk.Widget]:
        """Encuentra widgets relacionados con filtros."""
        widgets = []
        
        # Buscar widgets de filtros
        for widget in self.main_window.winfo_children():
            if isinstance(widget, (tk.Scale, ttk.Scale)):
                widgets.append(widget)
            elif isinstance(widget, (tk.Entry, ttk.Entry)):
                widgets.append(widget)
        
        return widgets
    
    def _find_analysis_widgets(self) -> List[tk.Widget]:
        """Encuentra widgets relacionados con análisis."""
        widgets = []
        
        # Buscar botones de análisis
        for widget in self.main_window.winfo_children():
            if isinstance(widget, tk.Button) and "análisis" in widget.cget("text").lower():
                widgets.append(widget)
            elif isinstance(widget, ttk.Button) and "análisis" in widget.cget("text").lower():
                widgets.append(widget)
        
        return widgets
    
    def _find_export_widgets(self) -> List[tk.Widget]:
        """Encuentra widgets relacionados con exportación."""
        widgets = []
        
        # Buscar botones de exportación
        for widget in self.main_window.winfo_children():
            if isinstance(widget, tk.Button) and "export" in widget.cget("text").lower():
                widgets.append(widget)
            elif isinstance(widget, ttk.Button) and "export" in widget.cget("text").lower():
                widgets.append(widget)
        
        return widgets
    
    def _apply_highlight(self, widget: tk.Widget, severity: ErrorSeverity):
        """Aplica destacado visual a un widget."""
        # Guardar configuración original
        if not hasattr(widget, '_original_config'):
            widget._original_config = {
                'bg': widget.cget('bg') if hasattr(widget, 'cget') else None,
                'fg': widget.cget('fg') if hasattr(widget, 'cget') else None,
                'relief': widget.cget('relief') if hasattr(widget, 'cget') else None,
                'borderwidth': widget.cget('borderwidth') if hasattr(widget, 'cget') else None
            }
        
        # Aplicar destacado
        widget.configure(
            bg=self.error_colors[severity],
            relief="solid",
            borderwidth=3
        )
        
        # Programar restauración después de 5 segundos
        self.main_window.after(5000, lambda: self._restore_widget(widget))
    
    def _restore_widget(self, widget: tk.Widget):
        """Restaura la configuración original de un widget."""
        if hasattr(widget, '_original_config'):
            widget.configure(**widget._original_config)
    
    def _navigate_to_target(self, target: str):
        """Navega automáticamente a un objetivo específico."""
        target = target.lower()
        
        if "cargar" in target or "data" in target:
            self._navigate_to_data_section()
        elif "filtro" in target:
            self._navigate_to_filter_section()
        elif "análisis" in target or "analysis" in target:
            self._navigate_to_analysis_section()
        elif "export" in target:
            self._navigate_to_export_section()
        elif "ayuda" in target or "help" in target:
            self._navigate_to_help_section()
    
    def _navigate_to_data_section(self):
        """Navega a la sección de carga de datos."""
        # Buscar y hacer focus en botón de carga
        for widget in self.main_window.winfo_children():
            if isinstance(widget, (tk.Button, ttk.Button)):
                if "cargar" in widget.cget("text").lower():
                    widget.focus_set()
                    widget.flash()
                    break
    
    def _navigate_to_filter_section(self):
        """Navega a la sección de filtros."""
        # Buscar y hacer focus en panel de filtros
        for widget in self.main_window.winfo_children():
            if isinstance(widget, (tk.Frame, ttk.Frame)):
                if "filtro" in str(widget).lower():
                    widget.focus_set()
                    break
    
    def _navigate_to_analysis_section(self):
        """Navega a la sección de análisis."""
        # Buscar y hacer focus en botón de análisis
        for widget in self.main_window.winfo_children():
            if isinstance(widget, (tk.Button, ttk.Button)):
                if "análisis" in widget.cget("text").lower():
                    widget.focus_set()
                    widget.flash()
                    break
    
    def _navigate_to_export_section(self):
        """Navega a la sección de exportación."""
        # Buscar y hacer focus en botón de exportación
        for widget in self.main_window.winfo_children():
            if isinstance(widget, (tk.Button, ttk.Button)):
                if "export" in widget.cget("text").lower():
                    widget.focus_set()
                    widget.flash()
                    break
    
    def _navigate_to_help_section(self):
        """Navega a la sección de ayuda."""
        # Buscar y hacer focus en botón de ayuda
        for widget in self.main_window.winfo_children():
            if isinstance(widget, (tk.Button, ttk.Button)):
                if "ayuda" in widget.cget("text").lower() or "help" in widget.cget("text").lower():
                    widget.focus_set()
                    widget.flash()
                    break
    
    def _navigate_and_close(self, window: tk.Toplevel, target: str):
        """Navega al objetivo y cierra la ventana de error."""
        window.destroy()
        self._navigate_to_target(target)
    
    def _show_help(self, error_info: ErrorInfo):
        """Muestra ayuda contextual para el error."""
        help_text = self._get_help_text(error_info)
        
        help_window = tk.Toplevel(self.main_window)
        help_window.title("Ayuda Contextual")
        help_window.geometry("600x400")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert("1.0", help_text)
        text_widget.config(state=tk.DISABLED)
        
        close_btn = ttk.Button(help_window, text="Cerrar", command=help_window.destroy)
        close_btn.pack(pady=10)
    
    def _get_help_text(self, error_info: ErrorInfo) -> str:
        """Retorna texto de ayuda contextual para el error."""
        help_texts = {
            ErrorCategory.DATA_LOAD: """
AYUDA: Error de Carga de Datos

Posibles causas:
1. Formato de archivo incorrecto
2. Columnas faltantes
3. Datos corruptos
4. Permisos de archivo

Soluciones:
1. Verificar que el archivo sea CSV con delimitador ';'
2. Asegurar que las columnas obligatorias estén presentes
3. Revisar que los datos numéricos sean válidos
4. Verificar permisos de lectura del archivo

Columnas obligatorias:
- Strategy_Name
- Factor_K
- CAGR_IS
- Sharpe_Ratio_IS
- Max_Drawdown_IS
            """,
            
            ErrorCategory.VALIDATION: """
AYUDA: Error de Validación

Posibles causas:
1. Datos fuera de rango
2. Valores nulos
3. Formato incorrecto
4. Inconsistencias en datos

Soluciones:
1. Revisar rangos de valores esperados
2. Completar datos faltantes
3. Corregir formato de datos
4. Verificar consistencia de métricas
            """,
            
            ErrorCategory.ANALYSIS: """
AYUDA: Error de Análisis

Posibles causas:
1. Datos insuficientes
2. Cálculos complejos
3. Memoria insuficiente
4. Configuración incorrecta

Soluciones:
1. Asegurar datos mínimos requeridos
2. Simplificar análisis si es necesario
3. Cerrar otras aplicaciones
4. Verificar configuración de análisis
            """,
            
            ErrorCategory.EXPORT: """
AYUDA: Error de Exportación

Posibles causas:
1. Permisos de escritura
2. Disco lleno
3. Formato no soportado
4. Datos no válidos

Soluciones:
1. Verificar permisos de escritura
2. Liberar espacio en disco
3. Usar formato soportado
4. Validar datos antes de exportar
            """,
            
            ErrorCategory.GUI: """
AYUDA: Error de Interfaz

Posibles causas:
1. Componente no encontrado
2. Evento no manejado
3. Configuración incorrecta
4. Recursos insuficientes

Soluciones:
1. Reiniciar la aplicación
2. Verificar configuración
3. Actualizar drivers de pantalla
4. Contactar soporte técnico
            """,
            
            ErrorCategory.SYSTEM: """
AYUDA: Error del Sistema

Posibles causas:
1. Memoria insuficiente
2. CPU sobrecargado
3. Archivos corruptos
4. Configuración del sistema

Soluciones:
1. Cerrar otras aplicaciones
2. Reiniciar el sistema
3. Verificar archivos del programa
4. Contactar soporte técnico
            """
        }
        
        return help_texts.get(error_info.category, "Ayuda no disponible para este tipo de error.")
    
    def validate_data_load(self, file_path: str) -> Tuple[bool, Optional[ErrorInfo]]:
        """Valida la carga de datos antes de procesar."""
        import os
        
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            error_info = ErrorInfo(
                message=f"El archivo '{file_path}' no existe.",
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.DATA_LOAD,
                component="Carga de Datos",
                suggestion="Verifique la ruta del archivo y que el archivo exista.",
                action_required=True,
                navigation_target="data_load"
            )
            return False, error_info
        
        # Verificar extensión
        if not file_path.lower().endswith('.csv'):
            error_info = ErrorInfo(
                message="El archivo debe ser un archivo CSV.",
                severity=ErrorSeverity.WARNING,
                category=ErrorCategory.DATA_LOAD,
                component="Carga de Datos",
                suggestion="Seleccione un archivo con extensión .csv",
                action_required=True,
                navigation_target="data_load"
            )
            return False, error_info
        
        # Verificar tamaño del archivo
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            error_info = ErrorInfo(
                message="El archivo está vacío.",
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.DATA_LOAD,
                component="Carga de Datos",
                suggestion="Seleccione un archivo con datos válidos.",
                action_required=True,
                navigation_target="data_load"
            )
            return False, error_info
        
        return True, None
    
    def validate_analysis_parameters(self, params: Dict[str, Any]) -> Tuple[bool, Optional[ErrorInfo]]:
        """Valida parámetros de análisis antes de ejecutar."""
        required_params = ['factor_k_weight', 'predictability_weight', 'sharpe_weight']
        
        for param in required_params:
            if param not in params:
                error_info = ErrorInfo(
                    message=f"Parámetro requerido '{param}' no encontrado.",
                    severity=ErrorSeverity.ERROR,
                    category=ErrorCategory.ANALYSIS,
                    component="Análisis",
                    suggestion="Configure todos los parámetros requeridos.",
                    action_required=True,
                    navigation_target="analysis"
                )
                return False, error_info
        
        # Verificar que los pesos sumen 1.0
        total_weight = sum(params.get(param, 0) for param in required_params)
        if abs(total_weight - 1.0) > 0.01:
            error_info = ErrorInfo(
                message="Los pesos de análisis deben sumar 1.0.",
                severity=ErrorSeverity.WARNING,
                category=ErrorCategory.ANALYSIS,
                component="Análisis",
                suggestion="Ajuste los pesos para que sumen 1.0.",
                action_required=True,
                navigation_target="analysis"
            )
            return False, error_info
        
        return True, None
    
    def clear_errors(self):
        """Limpia todos los errores actuales."""
        self.current_errors.clear()
        
        # Restaurar widgets destacados
        for widget in self.error_indicators.values():
            if hasattr(widget, '_original_config'):
                self._restore_widget(widget)
        
        self.error_indicators.clear()
        logger.info("Todos los errores han sido limpiados")
    
    def get_error_summary(self) -> str:
        """Retorna un resumen de errores actuales."""
        if not self.current_errors:
            return "No hay errores activos."
        
        summary = f"Errores activos: {len(self.current_errors)}\n\n"
        
        for i, error in enumerate(self.current_errors, 1):
            summary += f"{i}. {error.severity.value.upper()}: {error.message}\n"
            summary += f"   Categoría: {error.category.value}\n"
            summary += f"   Componente: {error.component}\n"
            if error.suggestion:
                summary += f"   Sugerencia: {error.suggestion}\n"
            summary += "\n"
        
        return summary


# Funciones de utilidad para uso externo
def create_error_info(message: str, severity: ErrorSeverity, category: ErrorCategory,
                     component: str, suggestion: str = "", action_required: bool = False,
                     navigation_target: Optional[str] = None) -> ErrorInfo:
    """Crea un objeto ErrorInfo con los parámetros especificados."""
    return ErrorInfo(
        message=message,
        severity=severity,
        category=category,
        component=component,
        suggestion=suggestion,
        action_required=action_required,
        navigation_target=navigation_target
    )


def handle_data_validation_error(error_msg: str, component: str = "Validación de Datos") -> ErrorInfo:
    """Crea un error de validación de datos estándar."""
    return create_error_info(
        message=error_msg,
        severity=ErrorSeverity.ERROR,
        category=ErrorCategory.VALIDATION,
        component=component,
        suggestion="Verifique el formato y contenido de los datos.",
        action_required=True,
        navigation_target="data_load"
    )


def handle_analysis_error(error_msg: str, component: str = "Análisis") -> ErrorInfo:
    """Crea un error de análisis estándar."""
    return create_error_info(
        message=error_msg,
        severity=ErrorSeverity.ERROR,
        category=ErrorCategory.ANALYSIS,
        component=component,
        suggestion="Verifique los parámetros de análisis y los datos de entrada.",
        action_required=True,
        navigation_target="analysis"
    )


def handle_export_error(error_msg: str, component: str = "Exportación") -> ErrorInfo:
    """Crea un error de exportación estándar."""
    return create_error_info(
        message=error_msg,
        severity=ErrorSeverity.ERROR,
        category=ErrorCategory.EXPORT,
        component=component,
        suggestion="Verifique los permisos de escritura y el espacio en disco.",
        action_required=True,
        navigation_target="export"
    ) 