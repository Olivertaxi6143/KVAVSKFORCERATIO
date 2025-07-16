#!/usr/bin/env python3
"""
Pestaña del Asesor Financiero Inteligente
=========================================

Pestaña profesional y amigable para el Asesor Financiero Inteligente
con interfaz moderna, consejos destacados y análisis visual.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 1.0.0
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

# Importar módulos del asesor
from src.analysis.asesor_financiero_inteligente import (
    AsesorFinancieroInteligente,
    crear_asesor_financiero,
    ejecutar_analisis_completo
)

# Configurar logger
logger = logging.getLogger(__name__)


class AsesorFinancieroTab(ttk.Frame):
    """
    Pestaña del Asesor Financiero Inteligente para la GUI.
    
    Características:
    - Interfaz amigable y profesional
    - Consejos destacados en tarjetas
    - Análisis visual con gráficos
    - Exportación de recomendaciones
    - Progreso visual durante análisis
    """
    
    def __init__(self, parent, data_manager, filtered_strategies_df: pd.DataFrame):
        """
        Inicializa la pestaña del asesor financiero.
        
        Args:
            parent: Widget padre
            data_manager: Gestor de datos
            filtered_strategies_df: DataFrame con estrategias filtradas
        """
        super().__init__(parent)
        self.parent = parent
        self.data_manager = data_manager
        self.filtered_strategies = filtered_strategies_df.copy()
        
        # Inicializar asesor financiero
        self.asesor = None
        self.analysis_results = {}
        
        # Variables de control
        self.analysis_running = False
        self.current_advice = []
        
        # Construir interfaz
        self._build_ui()
        
        logger.info(f"🧠 AsesorFinancieroTab inicializada con {len(self.filtered_strategies)} estrategias filtradas")
    
    def _build_ui(self):
        """Construye la interfaz de usuario amigable."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título principal
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="🧠 Asesor Financiero Inteligente", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Información de estrategias
        info_label = ttk.Label(title_frame, text=f"📊 {len(self.filtered_strategies)} estrategias disponibles", 
                              font=("Arial", 10))
        info_label.pack(side=tk.RIGHT)
        
        # Panel de controles principales
        self._build_control_panel(main_frame)
        
        # Notebook para diferentes secciones
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestañas del asesor
        self._build_advice_tab()
        self._build_analysis_tab()
        self._build_recommendations_tab()
        self._build_export_tab()
    
    def _build_control_panel(self, parent):
        """Construye el panel de controles principales."""
        control_frame = ttk.LabelFrame(parent, text="🎯 Controles del Asesor")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones principales
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Botón ejecutar análisis
        self.run_btn = ttk.Button(buttons_frame, text="🚀 Ejecutar Análisis Completo", 
                                 command=self._run_complete_analysis)
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón consejos rápidos
        self.quick_btn = ttk.Button(buttons_frame, text="💡 Consejos Rápidos", 
                                   command=self._show_quick_advice)
        self.quick_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón detener
        self.stop_btn = ttk.Button(buttons_frame, text="⏹️ Detener", 
                                  command=self._stop_analysis, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Separador
        ttk.Separator(buttons_frame, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Botón exportar
        self.export_btn = ttk.Button(buttons_frame, text="📤 Exportar Consejos", 
                                    command=self._export_advice)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón limpiar
        self.clear_btn = ttk.Button(buttons_frame, text="🗑️ Limpiar", 
                                   command=self._clear_results)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Barra de progreso
        progress_frame = ttk.Frame(control_frame)
        progress_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Etiqueta de estado
        self.status_label = ttk.Label(progress_frame, text="Listo para analizar estrategias", 
                                     font=("Arial", 9))
        self.status_label.pack()
    
    def _build_advice_tab(self):
        """Construye la pestaña de consejos principales."""
        advice_frame = ttk.Frame(self.notebook)
        self.notebook.add(advice_frame, text="💡 Consejos Principales")
        
        # Frame para consejos destacados
        advice_container = ttk.Frame(advice_frame)
        advice_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título de la sección
        ttk.Label(advice_container, text="🎯 Recomendaciones del Asesor", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Área de consejos principales
        self.advice_text = ScrolledText(advice_container, wrap=tk.WORD, height=20, 
                                       font=("Arial", 10))
        self.advice_text.pack(fill=tk.BOTH, expand=True)
        
        # Mensaje inicial
        self.advice_text.insert(tk.END, "🧠 Bienvenido al Asesor Financiero Inteligente\n")
        self.advice_text.insert(tk.END, "=" * 50 + "\n\n")
        self.advice_text.insert(tk.END, "📊 Este asesor analiza tus estrategias y proporciona:\n")
        self.advice_text.insert(tk.END, "• 🎯 Consejos personalizados\n")
        self.advice_text.insert(tk.END, "• 🔍 Detección de outliers\n")
        self.advice_text.insert(tk.END, "• 📈 Análisis de correlación IS/OOS\n")
        self.advice_text.insert(tk.END, "• 🎯 Clustering de estrategias\n")
        self.advice_text.insert(tk.END, "• 📊 Importancia de KPIs\n")
        self.advice_text.insert(tk.END, "• 🔮 Predicción de rendimiento\n\n")
        self.advice_text.insert(tk.END, "🚀 Haz clic en 'Ejecutar Análisis Completo' para comenzar.\n")
        
        self.advice_text.config(state=tk.DISABLED)
    
    def _build_analysis_tab(self):
        """Construye la pestaña de análisis detallado."""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="📊 Análisis Detallado")
        
        # Frame para análisis
        analysis_container = ttk.Frame(analysis_frame)
        analysis_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título de la sección
        ttk.Label(analysis_container, text="📈 Análisis Científico Avanzado", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Área de análisis
        self.analysis_text = ScrolledText(analysis_container, wrap=tk.WORD, height=20, 
                                         font=("Arial", 10))
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
        
        # Mensaje inicial
        self.analysis_text.insert(tk.END, "📊 Análisis Detallado del Asesor\n")
        self.analysis_text.insert(tk.END, "=" * 50 + "\n\n")
        self.analysis_text.insert(tk.END, "🔬 Esta sección mostrará:\n")
        self.analysis_text.insert(tk.END, "• 📊 Correlación IS/OOS\n")
        self.analysis_text.insert(tk.END, "• 🔍 Detección de outliers\n")
        self.analysis_text.insert(tk.END, "• 🎯 Clustering de estrategias\n")
        self.analysis_text.insert(tk.END, "• 📈 Importancia de KPIs (SHAP)\n")
        self.analysis_text.insert(tk.END, "• 🔮 Predicción de rendimiento\n\n")
        self.analysis_text.insert(tk.END, "⏳ Ejecuta el análisis para ver los resultados.\n")
        
        self.analysis_text.config(state=tk.DISABLED)
    
    def _build_recommendations_tab(self):
        """Construye la pestaña de recomendaciones específicas."""
        rec_frame = ttk.Frame(self.notebook)
        self.notebook.add(rec_frame, text="🎯 Recomendaciones")
        
        # Frame para recomendaciones
        rec_container = ttk.Frame(rec_frame)
        rec_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título de la sección
        ttk.Label(rec_container, text="🎯 Recomendaciones Específicas", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Área de recomendaciones
        self.recommendations_text = ScrolledText(rec_container, wrap=tk.WORD, height=20, 
                                               font=("Arial", 10))
        self.recommendations_text.pack(fill=tk.BOTH, expand=True)
        
        # Mensaje inicial
        self.recommendations_text.insert(tk.END, "🎯 Recomendaciones del Asesor\n")
        self.recommendations_text.insert(tk.END, "=" * 50 + "\n\n")
        self.recommendations_text.insert(tk.END, "💡 Aquí encontrarás:\n")
        self.recommendations_text.insert(tk.END, "• 🎯 Estrategias recomendadas\n")
        self.recommendations_text.insert(tk.END, "• ⚠️ Alertas de riesgo\n")
        self.recommendations_text.insert(tk.END, "• ✅ Oportunidades identificadas\n")
        self.recommendations_text.insert(tk.END, "• 📊 Métricas de calidad\n")
        self.recommendations_text.insert(tk.END, "• 🔮 Predicciones de rendimiento\n\n")
        self.recommendations_text.insert(tk.END, "🚀 Ejecuta el análisis para obtener recomendaciones.\n")
        
        self.recommendations_text.config(state=tk.DISABLED)
    
    def _build_export_tab(self):
        """Construye la pestaña de exportación."""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="📤 Exportar")
        
        # Frame para exportación
        export_container = ttk.Frame(export_frame)
        export_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título de la sección
        ttk.Label(export_container, text="📤 Exportar Consejos y Análisis", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Botones de exportación
        export_buttons_frame = ttk.Frame(export_container)
        export_buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(export_buttons_frame, text="📊 Exportar a Excel", 
                  command=self._export_to_excel).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(export_buttons_frame, text="📄 Exportar a PDF", 
                  command=self._export_to_pdf).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(export_buttons_frame, text="🌐 Exportar a HTML", 
                  command=self._export_to_html).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(export_buttons_frame, text="📋 Copiar al Portapapeles", 
                  command=self._copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        
        # Área de vista previa
        preview_frame = ttk.LabelFrame(export_container, text="👁️ Vista Previa")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.preview_text = ScrolledText(preview_frame, wrap=tk.WORD, height=15, 
                                        font=("Arial", 9))
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mensaje inicial
        self.preview_text.insert(tk.END, "📤 Exportación de Consejos\n")
        self.preview_text.insert(tk.END, "=" * 30 + "\n\n")
        self.preview_text.insert(tk.END, "💡 Aquí puedes exportar:\n")
        self.preview_text.insert(tk.END, "• 📊 Análisis completo\n")
        self.preview_text.insert(tk.END, "• 🎯 Recomendaciones\n")
        self.preview_text.insert(tk.END, "• 📈 Métricas detalladas\n")
        self.preview_text.insert(tk.END, "• 🔮 Predicciones\n\n")
        self.preview_text.insert(tk.END, "⏳ Ejecuta el análisis primero para exportar.\n")
        
        self.preview_text.config(state=tk.DISABLED)
    
    def _run_complete_analysis(self):
        """Ejecuta el análisis completo del asesor."""
        if self.analysis_running:
            messagebox.showwarning("Análisis en Progreso", 
                                 "Ya hay un análisis del asesor en ejecución.")
            return
        
        if len(self.filtered_strategies) == 0:
            messagebox.showwarning("Sin Estrategias", 
                                 "No hay estrategias disponibles para analizar.")
            return
        
        # Iniciar análisis en hilo separado
        self.analysis_running = True
        self.run_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.status_label.configure(text="Iniciando análisis del asesor...")
        self.progress_var.set(0)
        
        # Crear hilo para análisis
        analysis_thread = threading.Thread(target=self._execute_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def _execute_analysis(self):
        """Ejecuta el análisis del asesor en hilo separado."""
        try:
            logger.info("🧠 Iniciando análisis del Asesor Financiero Inteligente")
            
            # Actualizar progreso
            self.progress_var.set(10)
            self.status_label.configure(text="Inicializando asesor...")
            
            # Crear asesor
            kpis_default = ['Factor_K', 'CAGR_IS', 'Sharpe_Ratio_IS', 'Max_Drawdown_IS', 
                           'Profit_Factor_IS', 'Total_Trades_IS', 'Win_Rate_IS']
            
            self.asesor = crear_asesor_financiero(self.filtered_strategies, kpis_default)
            
            # Actualizar progreso
            self.progress_var.set(30)
            self.status_label.configure(text="Ejecutando análisis completo...")
            
            # Ejecutar análisis completo
            self.analysis_results = ejecutar_analisis_completo(self.filtered_strategies, kpis_default)
            
            # Actualizar progreso
            self.progress_var.set(90)
            self.status_label.configure(text="Procesando resultados...")
            
            # Actualizar GUI en hilo principal
            self.after(0, self._analysis_completed)
            
        except Exception as e:
            logger.error(f"❌ Error en análisis del asesor: {e}")
            self.after(0, self._analysis_error, str(e))
    
    def _analysis_completed(self):
        """Maneja la finalización del análisis."""
        try:
            # Completar progreso
            self.progress_var.set(100)
            self.status_label.configure(text="Análisis completado exitosamente")
            
            # Actualizar pestañas con resultados
            self._update_advice_tab()
            self._update_analysis_tab()
            self._update_recommendations_tab()
            self._update_export_tab()
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Análisis Completado", 
                              f"✅ Análisis del asesor completado exitosamente.\n"
                              f"📊 {len(self.filtered_strategies)} estrategias analizadas.\n"
                              f"💡 Revisa las pestañas para ver los consejos y recomendaciones.")
            
            logger.info("✅ Análisis del asesor completado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error actualizando resultados: {e}")
            messagebox.showerror("Error", f"Error actualizando resultados: {e}")
        
        finally:
            # Restaurar controles
            self.analysis_running = False
            self.run_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)
    
    def _analysis_error(self, error_msg: str):
        """Maneja errores en el análisis."""
        self.status_label.configure(text=f"Error en análisis: {error_msg}")
        messagebox.showerror("Error en Análisis", f"❌ Error en análisis del asesor:\n{error_msg}")
        
        # Restaurar controles
        self.analysis_running = False
        self.run_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.progress_var.set(0)
    
    def _stop_analysis(self):
        """Detiene el análisis en curso."""
        self.analysis_running = False
        self.status_label.configure(text="Análisis detenido por el usuario")
        self.run_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.progress_var.set(0)
    
    def _show_quick_advice(self):
        """Muestra consejos rápidos sin análisis completo."""
        if len(self.filtered_strategies) == 0:
            messagebox.showwarning("Sin Estrategias", 
                                 "No hay estrategias disponibles para consejos rápidos.")
            return
        
        # Generar consejos básicos
        quick_advice = self._generate_quick_advice()
        
        # Mostrar en ventana emergente
        advice_window = tk.Toplevel(self)
        advice_window.title("💡 Consejos Rápidos del Asesor")
        advice_window.geometry("600x400")
        advice_window.resizable(True, True)
        
        # Contenido de la ventana
        text_widget = ScrolledText(advice_window, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "💡 CONSEJOS RÁPIDOS DEL ASESOR\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        for advice in quick_advice:
            text_widget.insert(tk.END, f"{advice}\n\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def _generate_quick_advice(self) -> List[str]:
        """Genera consejos rápidos basados en datos básicos."""
        advice = []
        
        try:
            # Consejos básicos
            advice.append("🎯 CONSEJOS GENERALES:")
            advice.append("• Revisa la consistencia IS/OOS de tus estrategias")
            advice.append("• Identifica outliers que puedan afectar tu portafolio")
            advice.append("• Considera la diversificación entre diferentes estilos")
            advice.append("• Monitorea las métricas de riesgo regularmente")
            
            advice.append("\n📊 ESTADÍSTICAS BÁSICAS:")
            if 'Factor_K' in self.filtered_strategies.columns:
                avg_factor_k = self.filtered_strategies['Factor_K'].mean()
                advice.append(f"• Factor K promedio: {avg_factor_k:.2f}")
            
            if 'CAGR_IS' in self.filtered_strategies.columns:
                avg_cagr = self.filtered_strategies['CAGR_IS'].mean()
                advice.append(f"• CAGR promedio: {avg_cagr:.2f}%")
            
            if 'Sharpe_Ratio_IS' in self.filtered_strategies.columns:
                avg_sharpe = self.filtered_strategies['Sharpe_Ratio_IS'].mean()
                advice.append(f"• Sharpe Ratio promedio: {avg_sharpe:.2f}")
            
            advice.append(f"\n📈 ESTRATEGIAS DISPONIBLES: {len(self.filtered_strategies)}")
            
        except Exception as e:
            logger.error(f"Error generando consejos rápidos: {e}")
            advice.append("❌ Error generando consejos rápidos")
        
        return advice
    
    def _update_advice_tab(self):
        """Actualiza la pestaña de consejos principales."""
        try:
            self.advice_text.config(state=tk.NORMAL)
            self.advice_text.delete(1.0, tk.END)
            
            if 'consejos_completos' in self.analysis_results:
                consejos = self.analysis_results['consejos_completos']
                
                self.advice_text.insert(tk.END, "💡 CONSEJOS DEL ASESOR FINANCIERO\n")
                self.advice_text.insert(tk.END, "=" * 50 + "\n\n")
                
                for consejo in consejos:
                    self.advice_text.insert(tk.END, f"{consejo}\n")
                
                # Añadir resumen ejecutivo si está disponible
                if hasattr(self.asesor, 'obtener_resumen_ejecutivo'):
                    resumen = self.asesor.obtener_resumen_ejecutivo()
                    self.advice_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                    self.advice_text.insert(tk.END, "📋 RESUMEN EJECUTIVO\n")
                    self.advice_text.insert(tk.END, "=" * 50 + "\n")
                    self.advice_text.insert(tk.END, resumen)
            
            else:
                self.advice_text.insert(tk.END, "❌ No hay consejos disponibles\n")
                self.advice_text.insert(tk.END, "Ejecuta el análisis completo para obtener consejos.")
            
            self.advice_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error actualizando pestaña de consejos: {e}")
    
    def _update_analysis_tab(self):
        """Actualiza la pestaña de análisis detallado."""
        try:
            self.analysis_text.config(state=tk.NORMAL)
            self.analysis_text.delete(1.0, tk.END)
            
            self.analysis_text.insert(tk.END, "📊 ANÁLISIS DETALLADO DEL ASESOR\n")
            self.analysis_text.insert(tk.END, "=" * 50 + "\n\n")
            
            # Mostrar resultados de análisis
            if 'correlacion_is_oos' in self.analysis_results:
                corr = self.analysis_results['correlacion_is_oos']
                self.analysis_text.insert(tk.END, "📊 CORRELACIÓN IS/OOS:\n")
                if 'pairs_analyzed' in corr:
                    self.analysis_text.insert(tk.END, f"• Métricas analizadas: {corr['pairs_analyzed']}\n")
                if 'consistent_pairs' in corr:
                    self.analysis_text.insert(tk.END, f"• Pares consistentes: {corr['consistent_pairs']}\n")
                self.analysis_text.insert(tk.END, "\n")
            
            if 'outliers' in self.analysis_results:
                outliers = self.analysis_results['outliers']
                self.analysis_text.insert(tk.END, "🔍 DETECCIÓN DE OUTLIERS:\n")
                if 'outliers' in outliers:
                    self.analysis_text.insert(tk.END, f"• Outliers detectados: {len(outliers['outliers'])}\n")
                if 'buenos_outliers' in outliers:
                    self.analysis_text.insert(tk.END, f"• Buenos outliers: {len(outliers['buenos_outliers'])}\n")
                if 'malos_outliers' in outliers:
                    self.analysis_text.insert(tk.END, f"• Malos outliers: {len(outliers['malos_outliers'])}\n")
                self.analysis_text.insert(tk.END, "\n")
            
            if 'clustering' in self.analysis_results:
                cluster = self.analysis_results['clustering']
                self.analysis_text.insert(tk.END, "🎯 CLUSTERING DE ESTRATEGIAS:\n")
                if 'silhouette_score' in cluster:
                    self.analysis_text.insert(tk.END, f"• Score de clustering: {cluster['silhouette_score']:.3f}\n")
                if 'cluster_analysis' in cluster:
                    for c in cluster['cluster_analysis']:
                        self.analysis_text.insert(tk.END, f"• Cluster {c['cluster_id']}: {c['size']} estrategias\n")
                self.analysis_text.insert(tk.END, "\n")
            
            if 'importancia_kpis' in self.analysis_results:
                imp = self.analysis_results['importancia_kpis']
                self.analysis_text.insert(tk.END, "📈 IMPORTANCIA DE KPIs:\n")
                if 'top_kpis' in imp:
                    for i, (kpi, importance) in enumerate(imp['top_kpis'].items(), 1):
                        self.analysis_text.insert(tk.END, f"• {i}. {kpi}: {importance:.3f}\n")
                self.analysis_text.insert(tk.END, "\n")
            
            if 'prediccion' in self.analysis_results:
                pred = self.analysis_results['prediccion']
                self.analysis_text.insert(tk.END, "🔮 PREDICCIÓN DE RENDIMIENTO:\n")
                if 'r2_mean' in pred:
                    self.analysis_text.insert(tk.END, f"• R² promedio: {pred['r2_mean']:.3f}\n")
                if 'mae' in pred:
                    self.analysis_text.insert(tk.END, f"• Error promedio: {pred['mae']:.3f}\n")
                self.analysis_text.insert(tk.END, "\n")
            
            self.analysis_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error actualizando pestaña de análisis: {e}")
    
    def _update_recommendations_tab(self):
        """Actualiza la pestaña de recomendaciones."""
        try:
            self.recommendations_text.config(state=tk.NORMAL)
            self.recommendations_text.delete(1.0, tk.END)
            
            self.recommendations_text.insert(tk.END, "🎯 RECOMENDACIONES ESPECÍFICAS\n")
            self.recommendations_text.insert(tk.END, "=" * 50 + "\n\n")
            
            # Generar recomendaciones específicas
            recommendations = self._generate_specific_recommendations()
            
            for rec in recommendations:
                self.recommendations_text.insert(tk.END, f"{rec}\n")
            
            self.recommendations_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error actualizando pestaña de recomendaciones: {e}")
    
    def _generate_specific_recommendations(self) -> List[str]:
        """Genera recomendaciones específicas basadas en el análisis."""
        recommendations = []
        
        try:
            recommendations.append("🎯 RECOMENDACIONES ESPECÍFICAS:")
            recommendations.append("")
            
            # Recomendaciones basadas en outliers
            if 'outliers' in self.analysis_results:
                outliers = self.analysis_results['outliers']
                if 'malos_outliers' in outliers and len(outliers['malos_outliers']) > 0:
                    recommendations.append("⚠️ ALERTAS DE RIESGO:")
                    recommendations.append(f"• {len(outliers['malos_outliers'])} estrategias con riesgo elevado detectadas")
                    recommendations.append("• Considera revisar parámetros de estas estrategias")
                    recommendations.append("")
            
            # Recomendaciones basadas en clustering
            if 'clustering' in self.analysis_results:
                cluster = self.analysis_results['clustering']
                if 'cluster_analysis' in cluster:
                    recommendations.append("📊 DIVERSIFICACIÓN:")
                    recommendations.append("• Estrategias agrupadas por similitud")
                    recommendations.append("• Considera diversificar entre clusters diferentes")
                    recommendations.append("")
            
            # Recomendaciones basadas en importancia de KPIs
            if 'importancia_kpis' in self.analysis_results:
                imp = self.analysis_results['importancia_kpis']
                if 'top_kpis' in imp:
                    recommendations.append("📈 KPIs MÁS IMPORTANTES:")
                    for i, (kpi, importance) in enumerate(imp['top_kpis'].items(), 1):
                        recommendations.append(f"• {i}. {kpi}: {importance:.3f}")
                    recommendations.append("")
            
            # Recomendaciones generales
            recommendations.append("💡 RECOMENDACIONES GENERALES:")
            recommendations.append("• Revisa regularmente la consistencia IS/OOS")
            recommendations.append("• Monitorea outliers y estrategias atípicas")
            recommendations.append("• Considera la diversificación temporal")
            recommendations.append("• Evalúa la importancia de diferentes KPIs")
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones específicas: {e}")
            recommendations.append("❌ Error generando recomendaciones específicas")
        
        return recommendations
    
    def _update_export_tab(self):
        """Actualiza la pestaña de exportación."""
        try:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            
            self.preview_text.insert(tk.END, "📤 VISTA PREVIA DE EXPORTACIÓN\n")
            self.preview_text.insert(tk.END, "=" * 40 + "\n\n")
            
            if self.analysis_results:
                self.preview_text.insert(tk.END, "✅ Análisis disponible para exportar:\n")
                self.preview_text.insert(tk.END, "• Consejos del asesor\n")
                self.preview_text.insert(tk.END, "• Análisis detallado\n")
                self.preview_text.insert(tk.END, "• Recomendaciones específicas\n")
                self.preview_text.insert(tk.END, "• Métricas y estadísticas\n\n")
                
                # Vista previa del contenido
                if 'consejos_completos' in self.analysis_results:
                    consejos = self.analysis_results['consejos_completos']
                    self.preview_text.insert(tk.END, "📋 VISTA PREVIA DE CONSEJOS:\n")
                    self.preview_text.insert(tk.END, "-" * 30 + "\n")
                    
                    for i, consejo in enumerate(consejos[:5], 1):  # Mostrar solo los primeros 5
                        self.preview_text.insert(tk.END, f"{i}. {consejo}\n")
                    
                    if len(consejos) > 5:
                        self.preview_text.insert(tk.END, f"... y {len(consejos) - 5} consejos más\n")
            else:
                self.preview_text.insert(tk.END, "⏳ No hay análisis disponible para exportar.\n")
                self.preview_text.insert(tk.END, "Ejecuta el análisis completo primero.")
            
            self.preview_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error actualizando pestaña de exportación: {e}")
    
    def _export_advice(self):
        """Exporta los consejos del asesor."""
        if not self.analysis_results:
            messagebox.showwarning("Sin Datos", "No hay análisis disponible para exportar.")
            return
        
        try:
            # Crear contenido para exportar
            content = self._prepare_export_content()
            
            # Guardar archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("Exportación Exitosa", 
                                  f"✅ Consejos exportados exitosamente a:\n{filename}")
                
        except Exception as e:
            logger.error(f"Error exportando consejos: {e}")
            messagebox.showerror("Error", f"Error exportando consejos: {e}")
    
    def _prepare_export_content(self) -> str:
        """Prepara el contenido para exportar."""
        content = []
        content.append("🧠 ASESOR FINANCIERO INTELIGENTE")
        content.append("=" * 50)
        content.append(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"Estrategias analizadas: {len(self.filtered_strategies)}")
        content.append("")
        
        # Añadir consejos
        if 'consejos_completos' in self.analysis_results:
            content.append("💡 CONSEJOS DEL ASESOR:")
            content.append("-" * 30)
            for consejo in self.analysis_results['consejos_completos']:
                content.append(f"• {consejo}")
            content.append("")
        
        # Añadir análisis detallado
        content.append("📊 ANÁLISIS DETALLADO:")
        content.append("-" * 30)
        
        if 'correlacion_is_oos' in self.analysis_results:
            corr = self.analysis_results['correlacion_is_oos']
            content.append("📊 Correlación IS/OOS:")
            if 'pairs_analyzed' in corr:
                content.append(f"  • Métricas analizadas: {corr['pairs_analyzed']}")
            if 'consistent_pairs' in corr:
                content.append(f"  • Pares consistentes: {corr['consistent_pairs']}")
        
        if 'outliers' in self.analysis_results:
            outliers = self.analysis_results['outliers']
            content.append("🔍 Detección de Outliers:")
            if 'outliers' in outliers:
                content.append(f"  • Outliers detectados: {len(outliers['outliers'])}")
            if 'buenos_outliers' in outliers:
                content.append(f"  • Buenos outliers: {len(outliers['buenos_outliers'])}")
            if 'malos_outliers' in outliers:
                content.append(f"  • Malos outliers: {len(outliers['malos_outliers'])}")
        
        return "\n".join(content)
    
    def _export_to_excel(self):
        """Exporta a Excel."""
        messagebox.showinfo("Exportación Excel", "📊 Función de exportación a Excel en desarrollo.")
    
    def _export_to_pdf(self):
        """Exporta a PDF."""
        messagebox.showinfo("Exportación PDF", "📄 Función de exportación a PDF en desarrollo.")
    
    def _export_to_html(self):
        """Exporta a HTML."""
        messagebox.showinfo("Exportación HTML", "🌐 Función de exportación a HTML en desarrollo.")
    
    def _copy_to_clipboard(self):
        """Copia al portapapeles."""
        try:
            content = self._prepare_export_content()
            self.clipboard_clear()
            self.clipboard_append(content)
            messagebox.showinfo("Copiado", "✅ Contenido copiado al portapapeles.")
        except Exception as e:
            logger.error(f"Error copiando al portapapeles: {e}")
            messagebox.showerror("Error", f"Error copiando al portapapeles: {e}")
    
    def _clear_results(self):
        """Limpia los resultados del análisis."""
        self.analysis_results = {}
        self.current_advice = []
        
        # Limpiar pestañas
        self._update_advice_tab()
        self._update_analysis_tab()
        self._update_recommendations_tab()
        self._update_export_tab()
        
        # Restaurar controles
        self.progress_var.set(0)
        self.status_label.configure(text="Listo para analizar estrategias")
        
        messagebox.showinfo("Limpieza Completada", "🗑️ Todos los resultados han sido limpiados.")


def create_asesor_tab(parent, data_manager, filtered_strategies_df: pd.DataFrame) -> AsesorFinancieroTab:
    """
    Función factory para crear la pestaña del Asesor Financiero Inteligente.
    
    Args:
        parent: Widget padre
        data_manager: Gestor de datos
        filtered_strategies_df: DataFrame con estrategias filtradas
        
    Returns:
        Instancia de AsesorFinancieroTab
    """
    tab = AsesorFinancieroTab(parent, data_manager, filtered_strategies_df)
    
    # Añadir la pestaña al notebook
    notebook = parent
    notebook.add(tab, text="🧠 Asesor Inteligente")
    
    logger.info("✅ AsesorFinancieroTab configurada")
    return tab 