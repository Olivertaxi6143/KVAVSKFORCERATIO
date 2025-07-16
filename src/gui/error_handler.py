"""
Sistema de Gestión de Errores Intuitiva
Proporciona manejo profesional de errores con mensajes claros y acciones recomendadas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Optional, Callable
import logging
import traceback
import sys
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class IntuitiveErrorHandler:
    """
    Sistema de gestión de errores intuitiva para la GUI.
    
    Características:
    - Mensajes de error específicos y útiles
    - Sugerencias de solución automáticas
    - Navegación inteligente a secciones problemáticas
    - Prevención de errores comunes
    - Logging detallado para debugging
    """
    
    def __init__(self, parent: tk.Tk):
        """Inicializa el sistema de gestión de errores intuitiva."""
        self.parent = parent
        self.error_window = None
        self.error_history = []
        self.error_counts = {}
        
        # Categorías de errores
        self.error_categories = {
            "data_loading": {
                "title": "📁 Error de Carga de Datos",
                "icon": "📁",
                "color": "#FF6B6B",
                "priority": "high"
            },
            "data_validation": {
                "title": "✅ Error de Validación de Datos",
                "icon": "✅",
                "color": "#FFA500",
                "priority": "medium"
            },
            "analysis": {
                "title": "🧪 Error de Análisis",
                "icon": "🧪",
                "color": "#4ECDC4",
                "priority": "high"
            },
            "export": {
                "title": "📤 Error de Exportación",
                "icon": "📤",
                "color": "#45B7D1",
                "priority": "medium"
            },
            "system": {
                "title": "⚙️ Error del Sistema",
                "icon": "⚙️",
                "color": "#96CEB4",
                "priority": "critical"
            },
            "ui": {
                "title": "🖥️ Error de Interfaz",
                "icon": "🖥️",
                "color": "#FFEAA7",
                "priority": "low"
            }
        }
        
        # Soluciones predefinidas
        self.error_solutions = {
            "data_loading": {
                "file_not_found": {
                    "message": "El archivo no se encontró en la ruta especificada.",
                    "solutions": [
                        "Verificar que la ruta del archivo sea correcta",
                        "Asegurar que el archivo existe y es accesible",
                        "Comprobar permisos de lectura del archivo"
                    ],
                    "action": "show_file_dialog"
                },
                "invalid_format": {
                    "message": "El formato del archivo no es válido.",
                    "solutions": [
                        "Verificar que el archivo sea CSV con delimitador ';'",
                        "Comprobar que use decimal ',' en lugar de '.'",
                        "Asegurar que las columnas requeridas estén presentes"
                    ],
                    "action": "show_format_guide"
                },
                "missing_columns": {
                    "message": "Faltan columnas requeridas en el archivo.",
                    "solutions": [
                        "Verificar que el archivo incluya: Strategy Name, FactorK, CAGR, Sharpe, MaxDD, Trades",
                        "Revisar el formato de encabezados",
                        "Usar la plantilla de ejemplo proporcionada"
                    ],
                    "action": "show_template"
                }
            },
            "data_validation": {
                "invalid_data_types": {
                    "message": "Los tipos de datos no son válidos.",
                    "solutions": [
                        "Verificar que las columnas numéricas contengan solo números",
                        "Comprobar que no haya caracteres especiales en datos numéricos",
                        "Revisar el formato de fechas si aplica"
                    ],
                    "action": "show_data_preview"
                },
                "out_of_range": {
                    "message": "Algunos valores están fuera del rango esperado.",
                    "solutions": [
                        "Verificar que Factor K esté entre 0 y 10",
                        "Comprobar que Sharpe ratio sea razonable (-5 a 10)",
                        "Revisar que drawdown esté entre 0 y 100%"
                    ],
                    "action": "show_range_guide"
                }
            },
            "analysis": {
                "insufficient_data": {
                    "message": "No hay suficientes datos para realizar el análisis.",
                    "solutions": [
                        "Cargar más estrategias en el dataset",
                        "Verificar que los datos tengan la calidad mínima requerida",
                        "Ajustar los parámetros de análisis"
                    ],
                    "action": "show_data_requirements"
                },
                "computation_error": {
                    "message": "Error en el cálculo del análisis.",
                    "solutions": [
                        "Verificar que los datos no contengan valores NaN o infinitos",
                        "Comprobar que las métricas sean calculables",
                        "Revisar la configuración de parámetros"
                    ],
                    "action": "show_computation_guide"
                }
            },
            "export": {
                "permission_denied": {
                    "message": "No se tienen permisos para escribir en el directorio.",
                    "solutions": [
                        "Seleccionar un directorio con permisos de escritura",
                        "Ejecutar la aplicación como administrador si es necesario",
                        "Verificar que el disco tenga espacio disponible"
                    ],
                    "action": "show_directory_dialog"
                },
                "file_in_use": {
                    "message": "El archivo de destino está en uso.",
                    "solutions": [
                        "Cerrar el archivo si está abierto en otra aplicación",
                        "Seleccionar un nombre de archivo diferente",
                        "Esperar unos segundos y reintentar"
                    ],
                    "action": "retry_export"
                }
            },
            "system": {
                "memory_error": {
                    "message": "Error de memoria insuficiente.",
                    "solutions": [
                        "Cerrar otras aplicaciones para liberar memoria",
                        "Reducir el tamaño del dataset cargado",
                        "Reiniciar la aplicación"
                    ],
                    "action": "show_memory_optimization"
                },
                "disk_space": {
                    "message": "Espacio insuficiente en disco.",
                    "solutions": [
                        "Liberar espacio en el disco de destino",
                        "Seleccionar un directorio con más espacio disponible",
                        "Comprimir archivos existentes"
                    ],
                    "action": "show_disk_cleanup"
                }
            }
        }
        
        logger.info("✅ IntuitiveErrorHandler inicializado")
    
    def handle_error(self, error: Exception, context: str = "general", 
                    category: str = "system", show_dialog: bool = True) -> Dict[str, Any]:
        """
        Maneja un error de forma intuitiva.
        
        Args:
            error: Excepción capturada
            context: Contexto donde ocurrió el error
            category: Categoría del error
            show_dialog: Si mostrar diálogo de error
            
        Returns:
            Dict con información del error manejado
        """
        try:
            # Obtener información del error
            error_info = self._analyze_error(error, context, category)
            
            # Registrar en historial
            self._log_error(error_info)
            
            # Mostrar diálogo si es necesario
            if show_dialog:
                self._show_error_dialog(error_info)
            
            # Retornar información del error
            return error_info
            
        except Exception as e:
            logger.error(f"Error en manejo de errores: {e}")
            # Fallback a manejo básico
            return self._fallback_error_handling(error)
    
    def _analyze_error(self, error: Exception, context: str, category: str) -> Dict[str, Any]:
        """Analiza el error y extrae información relevante."""
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        # Determinar categoría específica
        specific_category = self._determine_specific_category(error_type, error_message, context)
        
        # Obtener solución predefinida
        solution = self._get_error_solution(specific_category, error_type, error_message)
        
        # Crear información del error
        error_info = {
            "type": error_type,
            "message": error_message,
            "context": context,
            "category": category,
            "specific_category": specific_category,
            "stack_trace": stack_trace,
            "timestamp": pd.Timestamp.now(),
            "solution": solution,
            "user_friendly_message": self._create_user_friendly_message(error_type, error_message, solution),
            "actions": self._get_recommended_actions(specific_category, error_type)
        }
        
        return error_info
    
    def _determine_specific_category(self, error_type: str, error_message: str, context: str) -> str:
        """Determina la categoría específica del error."""
        error_lower = error_message.lower()
        
        # Errores de carga de datos
        if any(keyword in error_lower for keyword in ["file not found", "no such file", "file_not_found", "archivo no encontrado"]):
            return "file_not_found"
        elif any(keyword in error_lower for keyword in ["file", "not found"]):
            return "file_not_found"
        elif any(keyword in error_lower for keyword in ["format", "delimiter", "encoding"]):
            return "invalid_format"
        elif any(keyword in error_lower for keyword in ["column", "missing", "required"]):
            return "missing_columns"
        
        # Errores de validación
        elif any(keyword in error_lower for keyword in ["type", "dtype", "numeric"]):
            return "invalid_data_types"
        elif any(keyword in error_lower for keyword in ["range", "bounds", "out of"]):
            return "out_of_range"
        
        # Errores de análisis
        elif any(keyword in error_lower for keyword in ["insufficient", "empty", "no data"]):
            return "insufficient_data"
        elif any(keyword in error_lower for keyword in ["computation", "calculation", "math"]):
            return "computation_error"
        
        # Errores de exportación
        elif any(keyword in error_lower for keyword in ["permission", "access", "denied"]):
            return "permission_denied"
        elif any(keyword in error_lower for keyword in ["in use", "locked", "busy"]):
            return "file_in_use"
        
        # Errores del sistema
        elif any(keyword in error_lower for keyword in ["memory", "out of memory"]):
            return "memory_error"
        elif any(keyword in error_lower for keyword in ["disk", "space", "full"]):
            return "disk_space"
        
        # Default
        return "unknown_error"
    
    def _get_error_solution(self, specific_category: str, error_type: str, error_message: str) -> Dict[str, Any]:
        """Obtiene la solución predefinida para el error."""
        # Buscar en soluciones predefinidas
        for category, solutions in self.error_solutions.items():
            if specific_category in solutions:
                return solutions[specific_category]
        
        # Solución genérica
        return {
            "message": f"Error de tipo {error_type}: {error_message}",
            "solutions": [
                "Revisar los datos de entrada",
                "Verificar la configuración del sistema",
                "Consultar la documentación para más detalles"
            ],
            "action": "show_generic_help"
        }
    
    def _create_user_friendly_message(self, error_type: str, error_message: str, solution: Dict[str, Any]) -> str:
        """Crea un mensaje amigable para el usuario."""
        friendly_message = f"❌ {solution.get('message', f'Error: {error_message}')}\n\n"
        friendly_message += "🔧 Soluciones recomendadas:\n"
        
        for i, solution_text in enumerate(solution.get('solutions', []), 1):
            friendly_message += f"{i}. {solution_text}\n"
        
        return friendly_message
    
    def _get_recommended_actions(self, specific_category: str, error_type: str) -> List[Dict[str, Any]]:
        """Obtiene las acciones recomendadas para el error."""
        actions = []
        
        # Acciones específicas según categoría
        if specific_category == "file_not_found":
            actions.append({
                "text": "📁 Seleccionar Archivo",
                "action": "show_file_dialog",
                "icon": "📁"
            })
        elif specific_category == "invalid_format":
            actions.append({
                "text": "📋 Ver Guía de Formato",
                "action": "show_format_guide",
                "icon": "📋"
            })
        elif specific_category == "missing_columns":
            actions.append({
                "text": "📄 Ver Plantilla",
                "action": "show_template",
                "icon": "📄"
            })
        elif specific_category == "permission_denied":
            actions.append({
                "text": "📁 Seleccionar Directorio",
                "action": "show_directory_dialog",
                "icon": "📁"
            })
        
        # Acciones generales
        actions.extend([
            {
                "text": "❓ Ayuda Contextual",
                "action": "show_contextual_help",
                "icon": "❓"
            },
            {
                "text": "📊 Ver Logs",
                "action": "show_error_logs",
                "icon": "📊"
            },
            {
                "text": "🔄 Reintentar",
                "action": "retry_operation",
                "icon": "🔄"
            }
        ])
        
        return actions
    
    def _show_error_dialog(self, error_info: Dict[str, Any]):
        """Muestra el diálogo de error intuitivo."""
        try:
            if self.error_window is not None:
                self.error_window.destroy()
            
            # Crear ventana de error
            self.error_window = tk.Toplevel(self.parent)
            self.error_window.title("❌ Error Detectado")
            self.error_window.geometry("600x500")
            self.error_window.resizable(True, True)
            
            # Configurar estilo
            style = ttk.Style()
            style.configure('ErrorTitle.TLabel', font=('Arial', 14, 'bold'), foreground='red')
            style.configure('ErrorContent.TLabel', font=('Arial', 10))
            style.configure('Action.TButton', font=('Arial', 10, 'bold'))
            
            # Frame principal
            main_frame = ttk.Frame(self.error_window)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título del error
            category_info = self.error_categories.get(error_info["category"], {})
            title_text = f"{category_info.get('icon', '❌')} {category_info.get('title', 'Error del Sistema')}"
            
            title_label = ttk.Label(main_frame, text=title_text, style="ErrorTitle.TLabel")
            title_label.pack(pady=(0, 20))
            
            # Mensaje del error
            message_text = tk.Text(main_frame, height=8, wrap="word", padx=10, pady=10)
            message_text.pack(fill="both", expand=True, pady=(0, 20))
            message_text.insert("1.0", error_info["user_friendly_message"])
            message_text.config(state="disabled")
            
            # Frame para botones de acción
            actions_frame = ttk.Frame(main_frame)
            actions_frame.pack(fill="x", pady=(0, 10))
            
            # Botones de acción
            for action in error_info["actions"]:
                btn = ttk.Button(
                    actions_frame,
                    text=f"{action['icon']} {action['text']}",
                    command=lambda a=action: self._execute_action(a, error_info)
                )
                btn.pack(side="left", padx=5)
            
            # Botón de cerrar
            close_btn = ttk.Button(
                main_frame,
                text="❌ Cerrar",
                command=self.error_window.destroy
            )
            close_btn.pack(pady=(10, 0))
            
            # Centrar ventana
            self.error_window.transient(self.parent)
            self.error_window.grab_set()
            
            logger.info(f"✅ Diálogo de error mostrado para: {error_info['specific_category']}")
            
        except Exception as e:
            logger.error(f"Error mostrando diálogo de error: {e}")
            # Fallback a messagebox básico
            messagebox.showerror("Error", f"Error: {error_info.get('message', str(e))}")
    
    def _execute_action(self, action: Dict[str, Any], error_info: Dict[str, Any]):
        """Ejecuta una acción recomendada."""
        try:
            action_name = action["action"]
            
            if action_name == "show_file_dialog":
                self._show_file_dialog()
            elif action_name == "show_format_guide":
                self._show_format_guide()
            elif action_name == "show_template":
                self._show_template()
            elif action_name == "show_directory_dialog":
                self._show_directory_dialog()
            elif action_name == "show_contextual_help":
                self._show_contextual_help(error_info["context"])
            elif action_name == "show_error_logs":
                self._show_error_logs()
            elif action_name == "retry_operation":
                self._retry_operation(error_info)
            elif action_name == "show_memory_optimization":
                self._show_memory_optimization()
            elif action_name == "show_disk_cleanup":
                self._show_disk_cleanup()
            else:
                logger.warning(f"Acción no implementada: {action_name}")
                
        except Exception as e:
            logger.error(f"Error ejecutando acción {action.get('action')}: {e}")
    
    def _show_file_dialog(self):
        """Muestra diálogo para seleccionar archivo."""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            logger.info(f"Archivo seleccionado: {filename}")
            # Aquí se podría implementar la carga automática del archivo
    
    def _show_format_guide(self):
        """Muestra guía de formato de archivos."""
        guide_text = """📋 GUÍA DE FORMATO DE ARCHIVOS

FORMATO REQUERIDO:
• Delimitador: ';' (punto y coma)
• Decimal: ',' (coma)
• Encoding: UTF-8

COLUMNAS REQUERIDAS:
• Strategy Name: Nombre de la estrategia
• FactorK: Factor K (0-10)
• CAGR: Tasa de crecimiento anual
• Sharpe: Sharpe Ratio
• MaxDD: Máximo Drawdown (%)
• Trades: Número de trades

EJEMPLO:
Strategy Name;FactorK;CAGR;Sharpe;MaxDD;Trades
Estrategia1;8.5;15.2;1.8;12.5;150
Estrategia2;7.2;12.1;1.5;18.3;200"""
        
        messagebox.showinfo("📋 Guía de Formato", guide_text)
    
    def _show_template(self):
        """Muestra plantilla de ejemplo."""
        template_text = """📄 PLANTILLA DE EJEMPLO

Strategy Name;FactorK;CAGR;Sharpe;MaxDD;Trades;WinRate;ProfitFactor
Estrategia_Elite;9.5;18.5;2.1;8.5;300;65.2;2.8
Estrategia_Excellent;8.8;16.2;1.9;12.1;250;62.1;2.5
Estrategia_VeryGood;7.5;14.1;1.6;15.3;200;58.9;2.1
Estrategia_Good;6.8;12.5;1.3;18.7;180;55.2;1.8
Estrategia_Poor;5.2;8.9;0.8;25.4;120;45.1;1.2

NOTAS:
• FactorK: 0-10 (mayor es mejor)
• CAGR: Porcentaje anual
• Sharpe: Ratio de Sharpe (mayor es mejor)
• MaxDD: Porcentaje máximo de pérdida
• Trades: Número total de operaciones
• WinRate: Porcentaje de trades ganadores
• ProfitFactor: Ratio ganancias/pérdidas"""
        
        messagebox.showinfo("📄 Plantilla de Ejemplo", template_text)
    
    def _show_directory_dialog(self):
        """Muestra diálogo para seleccionar directorio."""
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="Seleccionar directorio de destino")
        if directory:
            logger.info(f"Directorio seleccionado: {directory}")
    
    def _show_contextual_help(self, context: str):
        """Muestra ayuda contextual."""
        # Aquí se integraría con el sistema de ayuda contextual
        logger.info(f"Mostrando ayuda contextual para: {context}")
        messagebox.showinfo("❓ Ayuda Contextual", f"Ayuda para: {context}")
    
    def _show_error_logs(self):
        """Muestra logs de errores."""
        log_text = "📊 LOGS DE ERRORES\n\n"
        for error in self.error_history[-10:]:  # Últimos 10 errores
            log_text += f"• {error['timestamp']}: {error['type']} - {error['message']}\n"
        
        messagebox.showinfo("📊 Logs de Errores", log_text)
    
    def _retry_operation(self, error_info: Dict[str, Any]):
        """Reintenta la operación que falló."""
        logger.info(f"Reintentando operación: {error_info['context']}")
        messagebox.showinfo("🔄 Reintentar", "Operación reintentada")
    
    def _show_memory_optimization(self):
        """Muestra guía de optimización de memoria."""
        optimization_text = """⚡ OPTIMIZACIÓN DE MEMORIA

ACCIONES RECOMENDADAS:
1. Cerrar otras aplicaciones
2. Reducir el tamaño del dataset
3. Usar filtros para limitar datos
4. Reiniciar la aplicación
5. Verificar memoria disponible

CONFIGURACIÓN:
• Memoria mínima: 4GB RAM
• Espacio en disco: 2GB libre
• Procesador: Dual-core mínimo"""
        
        messagebox.showinfo("⚡ Optimización de Memoria", optimization_text)
    
    def _show_disk_cleanup(self):
        """Muestra guía de limpieza de disco."""
        cleanup_text = """💾 LIMPIEZA DE DISCO

ACCIONES RECOMENDADAS:
1. Eliminar archivos temporales
2. Vaciar papelera de reciclaje
3. Comprimir archivos grandes
4. Mover archivos a otro disco
5. Usar herramienta de limpieza

REQUISITOS:
• Espacio mínimo: 2GB libre
• Espacio recomendado: 5GB libre"""
        
        messagebox.showinfo("💾 Limpieza de Disco", cleanup_text)
    
    def _log_error(self, error_info: Dict[str, Any]):
        """Registra el error en el historial."""
        self.error_history.append(error_info)
        
        # Contar errores por tipo
        error_type = error_info["specific_category"]
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Logging detallado
        logger.error(f"Error registrado: {error_info['type']} - {error_info['message']}")
        logger.debug(f"Stack trace: {error_info['stack_trace']}")
    
    def _fallback_error_handling(self, error: Exception) -> Dict[str, Any]:
        """Manejo de error de fallback."""
        return {
            "type": type(error).__name__,
            "message": str(error),
            "context": "fallback",
            "category": "system",
            "specific_category": "unknown_error",
            "user_friendly_message": f"❌ Error inesperado: {str(error)}\n\n🔧 Contacte al soporte técnico.",
            "actions": []
        }
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de errores."""
        return {
            "total_errors": len(self.error_history),
            "error_counts": self.error_counts,
            "recent_errors": self.error_history[-5:] if self.error_history else [],
            "most_common_error": max(self.error_counts.items(), key=lambda x: x[1]) if self.error_counts else None
        }
    
    def clear_error_history(self):
        """Limpia el historial de errores."""
        self.error_history.clear()
        self.error_counts.clear()
        logger.info("✅ Historial de errores limpiado")

def create_intuitive_error_handler(parent: tk.Tk) -> IntuitiveErrorHandler:
    """Crea y retorna una instancia del manejador de errores intuitivo."""
    return IntuitiveErrorHandler(parent) 