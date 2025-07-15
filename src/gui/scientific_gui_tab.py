from typing import Optional, Any, Union
import warnings
#!/usr/bin/env python3
"""
Pestaña de Análisis Científico
===============================

Nueva pestaña con el mismo diseño que las actuales
para análisis científico avanzado.

⚠️ RESTRICCIÓN: Solo funciona con estrategias que pasaron el primer filtro
del análisis actual (Factor K, QVA, Unificado).

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import numpy as np
import logging
import threading
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

# Importar módulos científicos
from src.analysis.scientific_analysis import (
    ScientificAnalysisFilter,
    ScientificVisualizationManager,
    create_scientific_analysis_filter,
    create_scientific_visualization_manager
)

# Configurar logger
logger = logging.getLogger(__name__)


class ScientificAnalysisTab(ttk.Frame):
    """
    Pestaña de Análisis Científico para la GUI.
    
    ⚠️ RESTRICCIÓN: Solo funciona con estrategias que pasaron el primer filtro.
    """
    
    def __init__(self, parent, data_manager, filtered_strategies_df: pd.DataFrame):
        """
        Inicializa la pestaña de análisis científico.
        
        Args:
            parent: Widget padre
            data_manager: Gestor de datos
            filtered_strategies_df: DataFrame con estrategias filtradas del análisis actual
        """
        super().__init__(parent)
        self.parent = parent
        self.data_manager = data_manager
        self.filtered_strategies = filtered_strategies_df.copy()
        
        # Inicializar analizadores científicos
        self.scientific_analyzer = create_scientific_analysis_filter(filtered_strategies_df)
        self.visualization_manager = create_scientific_visualization_manager(filtered_strategies_df)
        
        # Variables de control
        self.analysis_running = False
        self.current_results = {}
        
        # Construir interfaz
        self._build_ui()
        
        logger.info(f"🔬 ScientificAnalysisTab inicializada con {len(self.filtered_strategies)} estrategias filtradas")
    
    def _build_ui(self):
        """Construye la interfaz de usuario de la pestaña científica."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔬 Análisis Científico Avanzado", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Información de estrategias filtradas
        self._build_strategies_info(main_frame)
        
        # Notebook para diferentes secciones
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestañas del análisis científico
        self._build_configuration_tab()
        self._build_results_tab()
        self._build_visualizations_tab()
        self._build_export_tab()
    
    def _build_strategies_info(self, parent):
        """Construye la sección de información de estrategias filtradas."""
        info_frame = ttk.LabelFrame(parent, text="📊 Información de Estrategias Filtradas")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Información básica
        strategies_info = self.scientific_analyzer.get_filtered_strategies_info()
        
        info_text = f"""
        🔍 Estrategias disponibles para análisis científico: {strategies_info['count']}
        📋 Columnas disponibles: {len(strategies_info.get('columns', []))}
        ⚠️ RESTRICCIÓN: Solo se analizan estrategias que pasaron el primer filtro
        """
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(padx=10, pady=10)
        
        # Botón para ver detalles
        details_btn = ttk.Button(info_frame, text="Ver Detalles de Estrategias", 
                               command=self._show_strategies_details)
        details_btn.pack(pady=(0, 10))
    
    def _build_configuration_tab(self):
        """Construye la pestaña de configuración de análisis científico."""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ Configuración")
        
        # Título
        title_label = ttk.Label(config_frame, text="Configuración de Análisis Científico", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        # Frame para controles
        controls_frame = ttk.Frame(config_frame)
        controls_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tipos de análisis disponibles
        analysis_types = self.scientific_analyzer.get_available_analyses()
        
        # Variables de control
        self.analysis_vars = {}
        
        # Crear checkboxes para cada tipo de análisis
        for i, analysis_type in enumerate(analysis_types):
            var = tk.BooleanVar(value=True)  # Por defecto activados
            self.analysis_vars[analysis_type] = var
            
            cb = ttk.Checkbutton(controls_frame, 
                                text=f"📊 {analysis_type.replace('_', ' ').title()}", 
                                variable=var)
            cb.grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # Botones de control
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=len(analysis_types), column=0, columnspan=2, pady=20)
        
        # Botón ejecutar análisis
        self.run_btn = ttk.Button(buttons_frame, text="🚀 Ejecutar Análisis Científico", 
                                 command=self._run_scientific_analysis)
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón detener análisis
        self.stop_btn = ttk.Button(buttons_frame, text="⏹️ Detener Análisis", 
                                  command=self._stop_analysis, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(buttons_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # Label de estado
        self.status_label = ttk.Label(buttons_frame, text="Listo para análisis científico")
        self.status_label.pack()
    
    def _build_results_tab(self):
        """Construye la pestaña de resultados del análisis científico."""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📈 Resultados")
        
        # Título
        title_label = ttk.Label(results_frame, text="Resultados del Análisis Científico", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        # Frame para resultados
        self.results_frame = ttk.Frame(results_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Texto de resultados
        self.results_text = ScrolledText(self.results_frame, height=20, width=80)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Botones de acción
        buttons_frame = ttk.Frame(results_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Botón copiar resultados
        copy_btn = ttk.Button(buttons_frame, text="📋 Copiar Resultados", 
                             command=self._copy_results)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón guardar resultados
        save_btn = ttk.Button(buttons_frame, text="💾 Guardar Resultados", 
                             command=self._save_results)
        save_btn.pack(side=tk.LEFT, padx=5)
    
    def _build_visualizations_tab(self):
        """Construye la pestaña de visualizaciones científicas."""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="📊 Visualizaciones")
        
        # Título
        title_label = ttk.Label(viz_frame, text="Visualizaciones Científicas", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        # Frame para controles de visualización
        controls_frame = ttk.Frame(viz_frame)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Botones para diferentes tipos de visualización
        viz_buttons_frame = ttk.Frame(controls_frame)
        viz_buttons_frame.pack()
        
        # Botón matriz de correlación
        corr_btn = ttk.Button(viz_buttons_frame, text="📊 Matriz de Correlación", 
                             command=self._show_correlation_matrix)
        corr_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón distribución de scores
        dist_btn = ttk.Button(viz_buttons_frame, text="📈 Distribución de Scores", 
                             command=self._show_score_distribution)
        dist_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón métricas de rendimiento
        perf_btn = ttk.Button(viz_buttons_frame, text="📊 Métricas de Rendimiento", 
                             command=self._show_performance_metrics)
        perf_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame para visualizaciones
        self.viz_frame = ttk.Frame(viz_frame)
        self.viz_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Label para mostrar información de visualización
        self.viz_label = ttk.Label(self.viz_frame, text="Seleccione un tipo de visualización para comenzar")
        self.viz_label.pack(pady=50)
    
    def _build_export_tab(self):
        """Construye la pestaña de exportación de resultados científicos."""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="💾 Exportación")
        
        # Título
        title_label = ttk.Label(export_frame, text="Exportación de Resultados Científicos", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        # Frame para opciones de exportación
        options_frame = ttk.LabelFrame(export_frame, text="Opciones de Exportación")
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Variables de control
        self.export_vars = {
            'include_metadata': tk.BooleanVar(value=True),
            'include_visualizations': tk.BooleanVar(value=True),
            'include_raw_data': tk.BooleanVar(value=False),
            'format_json': tk.BooleanVar(value=True),
            'format_csv': tk.BooleanVar(value=False)
        }
        
        # Checkboxes para opciones
        row = 0
        for key, var in self.export_vars.items():
            text = key.replace('_', ' ').title()
            cb = ttk.Checkbutton(options_frame, text=text, variable=var)
            cb.grid(row=row, column=0, sticky=tk.W, pady=2)
            row += 1
        
        # Frame para botones de exportación
        export_buttons_frame = ttk.Frame(export_frame)
        export_buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Botón exportar todo
        export_all_btn = ttk.Button(export_buttons_frame, text="💾 Exportar Todo", 
                                   command=self._export_all_results)
        export_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón exportar seleccionado
        export_selected_btn = ttk.Button(export_buttons_frame, text="📋 Exportar Seleccionado", 
                                       command=self._export_selected_results)
        export_selected_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón limpiar resultados
        clear_btn = ttk.Button(export_buttons_frame, text="🗑️ Limpiar Resultados", 
                              command=self._clear_results)
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def _run_scientific_analysis(self):
        """Ejecuta el análisis científico en un hilo separado."""
        if self.analysis_running:
            messagebox.showwarning("Análisis en Progreso", 
                                 "Ya hay un análisis científico en ejecución.")
            return
        
        # Obtener tipos de análisis seleccionados
        selected_analyses = [analysis_type for analysis_type, var in self.analysis_vars.items() 
                           if var.get()]
        
        if not selected_analyses:
            messagebox.showwarning("Sin Análisis Seleccionado", 
                                 "Debe seleccionar al menos un tipo de análisis.")
            return
        
        # Iniciar análisis en hilo separado
        self.analysis_running = True
        self.run_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.status_label.configure(text="Ejecutando análisis científico...")
        
        # Crear hilo para análisis
        analysis_thread = threading.Thread(
            target=self._execute_scientific_analysis,
            args=(selected_analyses,)
        )
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def _execute_scientific_analysis(self, analysis_types: List[str]):
        """Ejecuta el análisis científico en hilo separado."""
        try:
            logger.info(f"🔬 Iniciando análisis científico: {analysis_types}")
            
            # Actualizar progreso
            self.progress_var.set(0)
            total_analyses = len(analysis_types)
            
            results = {}
            
            for i, analysis_type in enumerate(analysis_types):
                if not self.analysis_running:
                    break
                
                # Actualizar progreso
                progress = (i / total_analyses) * 100
                self.progress_var.set(progress)
                self.status_label.configure(text=f"Ejecutando {analysis_type}...")
                
                # Ejecutar análisis específico
                analysis_result = self.scientific_analyzer.apply_scientific_analysis(analysis_type)
                results[analysis_type] = analysis_result
                
                # Pequeña pausa para permitir actualización de GUI
                time.sleep(0.1)
            
            # Completar progreso
            self.progress_var.set(100)
            
            # Guardar resultados
            self.current_results = results
            
            # Actualizar GUI en hilo principal
            self.after(0, self._analysis_completed, results)
            
        except Exception as e:
            logger.error(f"❌ Error en análisis científico: {e}")
            self.after(0, self._analysis_error, str(e))
    
    def _analysis_completed(self, results: Dict[str, Any]):
        """Maneja la finalización del análisis científico."""
        self.analysis_running = False
        self.run_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.status_label.configure(text="Análisis científico completado")
        
        # Mostrar resultados
        self._display_results(results)
        
        messagebox.showinfo("Análisis Completado", 
                          f"Análisis científico completado exitosamente.\n"
                          f"Tipos de análisis ejecutados: {len(results)}")
    
    def _analysis_error(self, error_message: str):
        """Maneja errores en el análisis científico."""
        self.analysis_running = False
        self.run_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.status_label.configure(text="Error en análisis científico")
        
        messagebox.showerror("Error en Análisis", 
                           f"Error durante el análisis científico:\n{error_message}")
    
    def _stop_analysis(self):
        """Detiene el análisis científico en progreso."""
        self.analysis_running = False
        self.run_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.status_label.configure(text="Análisis detenido por el usuario")
        
        logger.info("⏹️ Análisis científico detenido por el usuario")
    
    def _display_results(self, results: Dict[str, Any]):
        """Muestra los resultados del análisis científico."""
        # Limpiar texto anterior
        self.results_text.delete(1.0, tk.END)
        
        # Formatear y mostrar resultados
        results_text = "🔬 RESULTADOS DEL ANÁLISIS CIENTÍFICO\n"
        results_text += "=" * 50 + "\n\n"
        
        for analysis_type, result in results.items():
            results_text += f"📊 {analysis_type.upper()}\n"
            results_text += "-" * 30 + "\n"
            
            if "error" in result:
                results_text += f"❌ Error: {result['error']}\n"
            else:
                # Mostrar métricas principales
                if "filtered_strategies_count" in result:
                    results_text += f"📈 Estrategias analizadas: {result['filtered_strategies_count']}\n"
                
                if "timestamp" in result:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", 
                                            time.localtime(result['timestamp']))
                    results_text += f"⏰ Timestamp: {timestamp}\n"
                
                # Mostrar métricas específicas según el tipo de análisis
                if analysis_type == "predictability" and "predictability_score" in result:
                    predictability_score = result['predictability_score']
                    results_text += f"🎯 Score de Predictibilidad: {predictability_score:.3f}\n"
                    
                    # Interpretación de la predictibilidad
                    interpretation = self._interpret_predictability_score(predictability_score)
                    results_text += f"📊 Interpretación: {interpretation['level']}\n"
                    results_text += f"💡 Recomendación: {interpretation['recommendation']}\n"
                    
                    # Detalles adicionales si están disponibles
                    if 'predictability_details' in result:
                        details = result['predictability_details']
                        results_text += f"📈 Consistencia IS/OOS: {details.get('is_oos_consistency', 0):.1f}%\n"
                        results_text += f"🛡️ Robustez Temporal: {details.get('temporal_robustness', 0):.1f}%\n"
                        results_text += f"🔍 Detección Sobreajuste: {details.get('overfitting_detection', 0):.1f}%\n"
                        results_text += f"⚖️ Estabilidad: {details.get('stability_score', 0):.1f}%\n"
                
                if analysis_type == "robustness" and "stability_score" in result:
                    results_text += f"🛡️ Score de Estabilidad: {result['stability_score']:.3f}\n"
                
                if analysis_type == "walk_forward" and "validation_score" in result:
                    results_text += f"✅ Score de Validación: {result['validation_score']:.3f}\n"
            
            results_text += "\n"
        
        # Insertar en el widget de texto
        self.results_text.insert(1.0, results_text)
    
    def _show_strategies_details(self):
        """Muestra detalles de las estrategias filtradas."""
        strategies_info = self.scientific_analyzer.get_filtered_strategies_info()
        
        details_window = tk.Toplevel(self)
        details_window.title("Detalles de Estrategias Filtradas")
        details_window.geometry("600x400")
        
        # Texto con detalles
        details_text = ScrolledText(details_window, wrap=tk.WORD)
        details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        details_content = f"""
        📊 DETALLES DE ESTRATEGIAS FILTRADAS
        =====================================
        
        🔍 Total de estrategias: {strategies_info['count']}
        📋 Columnas disponibles: {len(strategies_info.get('columns', []))}
        
        📝 Columnas:
        {', '.join(strategies_info.get('columns', []))}
        
        🎯 Estrategias:
        {chr(10).join(strategies_info.get('strategies', []))}
        
        ⚠️ RESTRICCIÓN: Estas son las únicas estrategias que pasaron el primer filtro
        y están disponibles para análisis científico.
        """
        
        details_text.insert(1.0, details_content)
        details_text.configure(state=tk.DISABLED)
    
    def _show_correlation_matrix(self):
        """Muestra la matriz de correlación."""
        try:
            results = self.visualization_manager.prepare_correlation_matrix()
            
            if "error" in results:
                messagebox.showerror("Error", f"Error al generar matriz de correlación:\n{results['error']}")
                return
            
            # Actualizar label con información
            self.viz_label.configure(text=f"📊 Matriz de Correlación generada\n"
                                      f"Estrategias analizadas: {results.get('filtered_strategies_count', 0)}")
            
            logger.info("✅ Matriz de correlación mostrada")
            
        except Exception as e:
            logger.error(f"❌ Error mostrando matriz de correlación: {e}")
            messagebox.showerror("Error", f"Error al mostrar matriz de correlación:\n{str(e)}")
    
    def _show_score_distribution(self):
        """Muestra la distribución de scores."""
        try:
            results = self.visualization_manager.prepare_score_distribution()
            
            if "error" in results:
                messagebox.showerror("Error", f"Error al generar distribución de scores:\n{results['error']}")
                return
            
            # Actualizar label con información
            self.viz_label.configure(text=f"📈 Distribución de Scores generada\n"
                                      f"Estrategias analizadas: {results.get('filtered_strategies_count', 0)}")
            
            logger.info("✅ Distribución de scores mostrada")
            
        except Exception as e:
            logger.error(f"❌ Error mostrando distribución de scores: {e}")
            messagebox.showerror("Error", f"Error al mostrar distribución de scores:\n{str(e)}")
    
    def _show_performance_metrics(self):
        """Muestra las métricas de rendimiento."""
        try:
            results = self.visualization_manager.prepare_performance_metrics()
            
            if "error" in results:
                messagebox.showerror("Error", f"Error al generar métricas de rendimiento:\n{results['error']}")
                return
            
            # Actualizar label con información
            self.viz_label.configure(text=f"📊 Métricas de Rendimiento generadas\n"
                                      f"Estrategias analizadas: {results.get('filtered_strategies_count', 0)}")
            
            logger.info("✅ Métricas de rendimiento mostradas")
            
        except Exception as e:
            logger.error(f"❌ Error mostrando métricas de rendimiento: {e}")
            messagebox.showerror("Error", f"Error al mostrar métricas de rendimiento:\n{str(e)}")
    
    def _copy_results(self):
        """Copia los resultados al portapapeles."""
        try:
            results_text = self.results_text.get(1.0, tk.END)
            self.clipboard_clear()
            self.clipboard_append(results_text)
            
            messagebox.showinfo("Copiado", "Resultados copiados al portapapeles")
            
        except Exception as e:
            logger.error(f"❌ Error copiando resultados: {e}")
            messagebox.showerror("Error", f"Error al copiar resultados:\n{str(e)}")
    
    def _save_results(self):
        """Guarda los resultados en un archivo."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            
            if filename:
                results_text = self.results_text.get(1.0, tk.END)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(results_text)
                
                messagebox.showinfo("Guardado", f"Resultados guardados en:\n{filename}")
                
        except Exception as e:
            logger.error(f"❌ Error guardando resultados: {e}")
            messagebox.showerror("Error", f"Error al guardar resultados:\n{str(e)}")
    
    def _export_all_results(self):
        """Exporta todos los resultados científicos."""
        try:
            if not self.current_results:
                messagebox.showwarning("Sin Resultados", 
                                     "No hay resultados para exportar. Ejecute un análisis primero.")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
            )
            
            if filename:
                # Preparar datos para exportación
                export_data = {
                    "metadata": {
                        "export_timestamp": time.time(),
                        "filtered_strategies_count": len(self.filtered_strategies),
                        "analysis_types": list(self.current_results.keys())
                    },
                    "results": self.current_results
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Exportado", f"Resultados exportados a:\n{filename}")
                
        except Exception as e:
            logger.error(f"❌ Error exportando resultados: {e}")
            messagebox.showerror("Error", f"Error al exportar resultados:\n{str(e)}")
    
    def _export_selected_results(self):
        """Exporta resultados seleccionados."""
        messagebox.showinfo("Exportación Selectiva", 
                          "Funcionalidad de exportación selectiva en desarrollo.")
    
    def _clear_results(self):
        """Limpia los resultados actuales."""
        self.current_results = {}
        self.results_text.delete(1.0, tk.END)
        self.viz_label.configure(text="Seleccione un tipo de visualización para comenzar")
        
        messagebox.showinfo("Limpiado", "Resultados científicos limpiados")

    def _interpret_predictability_score(self, score: float) -> dict:
        """
        Interpreta el score de predictibilidad y proporciona recomendaciones amigables y lógicas.
        Args:
            score: Score de predictibilidad (0-100)
        Returns:
            Dict con nivel y recomendación
        """
        if score >= 90:
            return {
                "level": "🟢 EXCELENTE",
                "recommendation": "Muy alta predictibilidad. Estrategia sobresaliente para trading real."
            }
        elif score >= 80:
            return {
                "level": "🟡 BUENA",
                "recommendation": "Buena predictibilidad. Confiable, pero monitoree su rendimiento."
            }
        elif score >= 70:
            return {
                "level": "🟠 ACEPTABLE",
                "recommendation": "Aceptable. Úsela con precaución y valide regularmente."
            }
        elif score >= 60:
            return {
                "level": "🔴 BAJA",
                "recommendation": "Baja predictibilidad. Requiere validación adicional antes de operar."
            }
        else:
            return {
                "level": "⚫ MUY BAJA",
                "recommendation": "No recomendable para trading real sin mejoras significativas."
            }


def create_scientific_tab(parent, data_manager, filtered_strategies_df: pd.DataFrame) -> ScientificAnalysisTab:
    """
    Factory function para crear la pestaña de análisis científico.
    
    Args:
        parent: Widget padre
        data_manager: Gestor de datos
        filtered_strategies_df: DataFrame con estrategias filtradas
        
    Returns:
        ScientificAnalysisTab configurada
    """
    return ScientificAnalysisTab(parent, data_manager, filtered_strategies_df)


if __name__ == "__main__":
    # Test básico del módulo
    print("🔬 Módulo de Pestaña Científica cargado correctamente")
    print("⚠️ RESTRICCIÓN: Solo funciona con estrategias filtradas del análisis actual") 