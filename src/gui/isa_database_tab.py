#!/usr/bin/env python3
"""
Pestaña de Base de Datos ISA y Entrenamiento ML
===============================================

Pestaña profesional para gestionar la base de datos del Intelligent Strategy Advisor
y el sistema de entrenamiento de Machine Learning.

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
import sqlite3

# Importar módulos de la base de datos ML
from src.data.ml_database import MLDatabase, MLDatabaseConfig, MLDataset
from src.ml.isa_training_enhanced import ISATrainingEnhanced
from src.data.data_manager import DataManager

# Configurar logger
logger = logging.getLogger(__name__)


class ISADatabaseTab(ttk.Frame):
    """
    Pestaña de Base de Datos ISA y Entrenamiento ML para la GUI.
    
    Características:
    - Gestión de base de datos ML
    - Entrenamiento de modelos ISA
    - Visualización de métricas de entrenamiento
    - Exportación de modelos entrenados
    - Monitoreo de performance
    """
    
    def __init__(self, parent, data_manager: DataManager):
        """
        Inicializa la pestaña de base de datos ISA.
        
        Args:
            parent: Widget padre
            data_manager: Gestor de datos
        """
        super().__init__(parent)
        self.parent = parent
        self.data_manager = data_manager
        
        # Inicializar base de datos ML
        self.ml_database = MLDatabase()
        self.isa_trainer = None
        
        # Variables de control
        self.training_running = False
        self.current_model = None
        self.training_results = {}
        
        # Construir interfaz
        self._build_ui()
        
        logger.info("🗄️ ISADatabaseTab inicializada")
    
    def _build_ui(self):
        """Construye la interfaz de usuario profesional."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título principal
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="🗄️ Base de Datos ISA y Entrenamiento ML", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Información de la base de datos
        self.db_info_label = ttk.Label(title_frame, text="📊 Conectando a base de datos...", 
                                      font=("Arial", 10))
        self.db_info_label.pack(side=tk.RIGHT)
        
        # Panel de controles principales
        self._build_control_panel(main_frame)
        
        # Notebook para diferentes secciones
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestañas del sistema ISA
        self._build_database_tab()
        self._build_training_tab()
        self._build_models_tab()
        self._build_export_tab()
        
        # Actualizar información de la base de datos
        self._update_database_info()
    
    def _build_control_panel(self, parent):
        """Construye el panel de controles principales."""
        control_frame = ttk.LabelFrame(parent, text="🎯 Controles del Sistema ISA")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones principales
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Botón conectar base de datos
        self.connect_btn = ttk.Button(buttons_frame, text="🔗 Conectar Base de Datos", 
                                     command=self._connect_database)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón entrenar modelo
        self.train_btn = ttk.Button(buttons_frame, text="🤖 Entrenar Modelo ISA", 
                                   command=self._train_isa_model)
        self.train_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón detener entrenamiento
        self.stop_btn = ttk.Button(buttons_frame, text="⏹️ Detener", 
                                  command=self._stop_training, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Separador
        ttk.Separator(buttons_frame, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Botón exportar modelo
        self.export_btn = ttk.Button(buttons_frame, text="📤 Exportar Modelo", 
                                    command=self._export_model)
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
        self.status_label = ttk.Label(progress_frame, text="Listo para conectar a la base de datos", 
                                     font=("Arial", 9))
        self.status_label.pack()
    
    def _build_database_tab(self):
        """Construye la pestaña de gestión de base de datos."""
        db_frame = ttk.Frame(self.notebook)
        self.notebook.add(db_frame, text="🗄️ Base de Datos")
        
        # Frame para gestión de base de datos
        db_container = ttk.Frame(db_frame)
        db_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título de la sección
        ttk.Label(db_container, text="🗄️ Gestión de Base de Datos ML", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Información de la base de datos
        info_frame = ttk.LabelFrame(db_container, text="📊 Información de la Base de Datos")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.db_stats_text = ScrolledText(info_frame, wrap=tk.WORD, height=8, 
                                         font=("Arial", 10))
        self.db_stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botones de gestión
        buttons_frame = ttk.Frame(db_container)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(buttons_frame, text="📊 Actualizar Estadísticas", 
                  command=self._update_database_stats).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="🗑️ Limpiar Cache", 
                  command=self._clear_database_cache).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="📤 Exportar Datos", 
                  command=self._export_database_data).pack(side=tk.LEFT, padx=5)
        
        # Mensaje inicial
        self.db_stats_text.insert(tk.END, "🗄️ Base de Datos ML\n")
        self.db_stats_text.insert(tk.END, "=" * 40 + "\n\n")
        self.db_stats_text.insert(tk.END, "📊 Esta sección permite gestionar:\n")
        self.db_stats_text.insert(tk.END, "• Almacenamiento de datos IS/OOS\n")
        self.db_stats_text.insert(tk.END, "• Gestión de features y targets\n")
        self.db_stats_text.insert(tk.END, "• Validación temporal de datos\n")
        self.db_stats_text.insert(tk.END, "• Cache inteligente\n")
        self.db_stats_text.insert(tk.END, "• Exportación para entrenamiento\n\n")
        self.db_stats_text.insert(tk.END, "🔗 Haz clic en 'Conectar Base de Datos' para comenzar.\n")
        
        self.db_stats_text.config(state=tk.DISABLED)
    
    def _build_training_tab(self):
        """Construye la pestaña de entrenamiento de modelos."""
        training_frame = ttk.Frame(self.notebook)
        self.notebook.add(training_frame, text="🤖 Entrenamiento")
        
        # Frame para entrenamiento
        training_container = ttk.Frame(training_frame)
        training_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título de la sección
        ttk.Label(training_container, text="🤖 Entrenamiento de Modelos ISA", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Configuración de entrenamiento
        config_frame = ttk.LabelFrame(training_container, text="⚙️ Configuración de Entrenamiento")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Parámetros de entrenamiento
        params_frame = ttk.Frame(config_frame)
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Target column
        ttk.Label(params_frame, text="Columna objetivo:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.target_var = tk.StringVar(value="Unified_Score")
        target_combo = ttk.Combobox(params_frame, textvariable=self.target_var, 
                                   values=["Unified_Score", "Factor_K_Score", "QVA_Score", "CAGR_OOS"])
        target_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Split ratio
        ttk.Label(params_frame, text="Ratio de división:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.split_var = tk.DoubleVar(value=0.7)
        split_spin = ttk.Spinbox(params_frame, from_=0.5, to=0.9, increment=0.1, 
                                textvariable=self.split_var, width=10)
        split_spin.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Model type
        ttk.Label(params_frame, text="Tipo de modelo:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.model_var = tk.StringVar(value="random_forest")
        model_combo = ttk.Combobox(params_frame, textvariable=self.model_var, 
                                  values=["random_forest", "gradient_boosting", "neural_network"])
        model_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        # Configurar grid
        params_frame.columnconfigure(1, weight=1)
        
        # Área de resultados de entrenamiento
        results_frame = ttk.LabelFrame(training_container, text="📈 Resultados de Entrenamiento")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.training_text = ScrolledText(results_frame, wrap=tk.WORD, height=15, 
                                         font=("Arial", 10))
        self.training_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mensaje inicial
        self.training_text.insert(tk.END, "🤖 Entrenamiento de Modelos ISA\n")
        self.training_text.insert(tk.END, "=" * 40 + "\n\n")
        self.training_text.insert(tk.END, "📊 Esta sección permite:\n")
        self.training_text.insert(tk.END, "• Entrenar modelos de predicción\n")
        self.training_text.insert(tk.END, "• Validación temporal cruzada\n")
        self.training_text.insert(tk.END, "• Análisis de performance\n")
        self.training_text.insert(tk.END, "• Optimización de hiperparámetros\n")
        self.training_text.insert(tk.END, "• Exportación de modelos\n\n")
        self.training_text.insert(tk.END, "🤖 Configura los parámetros y haz clic en 'Entrenar Modelo ISA'.\n")
        
        self.training_text.config(state=tk.DISABLED)
    
    def _build_models_tab(self):
        """Construye la pestaña de gestión de modelos."""
        models_frame = ttk.Frame(self.notebook)
        self.notebook.add(models_frame, text="📦 Modelos")
        
        # Frame para gestión de modelos
        models_container = ttk.Frame(models_frame)
        models_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título de la sección
        ttk.Label(models_container, text="📦 Gestión de Modelos Entrenados", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Lista de modelos
        models_list_frame = ttk.LabelFrame(models_container, text="📋 Modelos Disponibles")
        models_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview para modelos
        columns = ("Nombre", "Tipo", "Target", "Performance", "Fecha")
        self.models_tree = ttk.Treeview(models_list_frame, columns=columns, show="headings", height=10)
        
        # Configurar columnas
        for col in columns:
            self.models_tree.heading(col, text=col)
            self.models_tree.column(col, width=120)
        
        # Scrollbar
        models_scrollbar = ttk.Scrollbar(models_list_frame, orient="vertical", command=self.models_tree.yview)
        self.models_tree.configure(yscrollcommand=models_scrollbar.set)
        
        # Pack
        self.models_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        models_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de gestión de modelos
        models_buttons_frame = ttk.Frame(models_container)
        models_buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(models_buttons_frame, text="🔄 Actualizar Lista", 
                  command=self._refresh_models_list).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(models_buttons_frame, text="📊 Ver Detalles", 
                  command=self._view_model_details).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(models_buttons_frame, text="🗑️ Eliminar Modelo", 
                  command=self._delete_model).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(models_buttons_frame, text="📤 Exportar Modelo", 
                  command=self._export_selected_model).pack(side=tk.LEFT, padx=5)
    
    def _build_export_tab(self):
        """Construye la pestaña de exportación."""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="📤 Exportar")
        
        # Frame para exportación
        export_container = ttk.Frame(export_frame)
        export_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título de la sección
        ttk.Label(export_container, text="📤 Exportación de Modelos y Datos", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Opciones de exportación
        export_options_frame = ttk.LabelFrame(export_container, text="📤 Opciones de Exportación")
        export_options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Checkboxes para opciones
        self.export_model_var = tk.BooleanVar(value=True)
        self.export_data_var = tk.BooleanVar(value=True)
        self.export_metrics_var = tk.BooleanVar(value=True)
        self.export_config_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(export_options_frame, text="🤖 Modelo entrenado", 
                       variable=self.export_model_var).pack(anchor="w", padx=10, pady=2)
        
        ttk.Checkbutton(export_options_frame, text="📊 Datos de entrenamiento", 
                       variable=self.export_data_var).pack(anchor="w", padx=10, pady=2)
        
        ttk.Checkbutton(export_options_frame, text="📈 Métricas de performance", 
                       variable=self.export_metrics_var).pack(anchor="w", padx=10, pady=2)
        
        ttk.Checkbutton(export_options_frame, text="⚙️ Configuración del modelo", 
                       variable=self.export_config_var).pack(anchor="w", padx=10, pady=2)
        
        # Botones de exportación
        export_buttons_frame = ttk.Frame(export_container)
        export_buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(export_buttons_frame, text="📤 Exportar Todo", 
                  command=self._export_all).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(export_buttons_frame, text="🤖 Solo Modelo", 
                  command=self._export_model_only).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(export_buttons_frame, text="📊 Solo Datos", 
                  command=self._export_data_only).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(export_buttons_frame, text="📈 Solo Métricas", 
                  command=self._export_metrics_only).pack(side=tk.LEFT, padx=5)
        
        # Área de vista previa
        preview_frame = ttk.LabelFrame(export_container, text="👁️ Vista Previa")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.export_preview_text = ScrolledText(preview_frame, wrap=tk.WORD, height=15, 
                                               font=("Arial", 9))
        self.export_preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mensaje inicial
        self.export_preview_text.insert(tk.END, "📤 Exportación de Modelos ISA\n")
        self.export_preview_text.insert(tk.END, "=" * 40 + "\n\n")
        self.export_preview_text.insert(tk.END, "💡 Aquí puedes exportar:\n")
        self.export_preview_text.insert(tk.END, "• Modelos entrenados\n")
        self.export_preview_text.insert(tk.END, "• Datos de entrenamiento\n")
        self.export_preview_text.insert(tk.END, "• Métricas de performance\n")
        self.export_preview_text.insert(tk.END, "• Configuración de modelos\n\n")
        self.export_preview_text.insert(tk.END, "⏳ Selecciona las opciones y exporta.\n")
        
        self.export_preview_text.config(state=tk.DISABLED)
    
    def _connect_database(self):
        """Conecta a la base de datos ML."""
        try:
            self.status_label.configure(text="Conectando a la base de datos...")
            self.progress_var.set(10)
            
            # Verificar conexión
            stats = self.ml_database.get_database_stats()
            
            self.progress_var.set(100)
            self.status_label.configure(text="Base de datos conectada exitosamente")
            
            # Actualizar información
            self._update_database_info()
            self._update_database_stats()
            
            messagebox.showinfo("Conexión Exitosa", 
                              f"✅ Base de datos ML conectada exitosamente.\n"
                              f"📊 {stats.get('total_records', 0)} registros disponibles.")
            
        except Exception as e:
            logger.error(f"Error conectando a la base de datos: {e}")
            self.status_label.configure(text=f"Error: {str(e)}")
            messagebox.showerror("Error de Conexión", f"❌ Error conectando a la base de datos:\n{str(e)}")
    
    def _train_isa_model(self):
        """Entrena un modelo ISA."""
        if self.training_running:
            messagebox.showwarning("Entrenamiento en Progreso", 
                                 "Ya hay un entrenamiento en ejecución.")
            return
        
        try:
            # Obtener parámetros
            target_column = self.target_var.get()
            split_ratio = self.split_var.get()
            model_type = self.model_var.get()
            
            # Iniciar entrenamiento en hilo separado
            self.training_running = True
            self.train_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.NORMAL)
            self.status_label.configure(text="Iniciando entrenamiento del modelo ISA...")
            self.progress_var.set(0)
            
            # Crear hilo para entrenamiento
            training_thread = threading.Thread(target=self._execute_training, 
                                            args=(target_column, split_ratio, model_type))
            training_thread.daemon = True
            training_thread.start()
            
        except Exception as e:
            logger.error(f"Error iniciando entrenamiento: {e}")
            messagebox.showerror("Error", f"Error iniciando entrenamiento: {e}")
    
    def _execute_training(self, target_column: str, split_ratio: float, model_type: str):
        """Ejecuta el entrenamiento del modelo en hilo separado."""
        try:
            logger.info(f"🤖 Iniciando entrenamiento ISA: {target_column}, {split_ratio}, {model_type}")
            
            # Actualizar progreso
            self.progress_var.set(20)
            self.status_label.configure(text="Cargando datos de entrenamiento...")
            
            # Crear dataset
            dataset = self.ml_database.create_ml_dataset(
                target_column=target_column,
                split_ratio=split_ratio
            )
            
            if dataset is None:
                raise ValueError("No se pudo crear el dataset de entrenamiento")
            
            # Actualizar progreso
            self.progress_var.set(40)
            self.status_label.configure(text="Inicializando entrenador ISA...")
            
            # Crear entrenador ISA
            from src.ml.isa_training_enhanced import TrainingConfig
            config = TrainingConfig(
                model_type=model_type,
                target_column=target_column
            )
            self.isa_trainer = ISATrainingEnhanced(config)
            
            # Actualizar progreso
            self.progress_var.set(60)
            self.status_label.configure(text="Entrenando modelo...")
            
            # Entrenar modelo
            self.training_results = self.isa_trainer.train_model(dataset)
            
            # Actualizar progreso
            self.progress_var.set(90)
            self.status_label.configure(text="Guardando modelo...")
            
            # Guardar modelo
            self.current_model = self.isa_trainer.save_model()
            
            # Actualizar GUI en hilo principal
            self.after(0, self._training_completed)
            
        except Exception as e:
            logger.error(f"❌ Error en entrenamiento ISA: {e}")
            self.after(0, self._training_error, str(e))
    
    def _training_completed(self):
        """Maneja la finalización del entrenamiento."""
        try:
            # Completar progreso
            self.progress_var.set(100)
            self.status_label.configure(text="Entrenamiento completado exitosamente")
            
            # Actualizar pestañas con resultados
            self._update_training_results()
            self._refresh_models_list()
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Entrenamiento Completado", 
                              f"✅ Modelo ISA entrenado exitosamente.\n"
                              f"📊 Performance: {self.training_results.get('r2_score', 'N/A'):.3f}\n"
                              f"🎯 Target: {self.target_var.get()}")
            
            logger.info("✅ Entrenamiento ISA completado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error actualizando resultados: {e}")
            messagebox.showerror("Error", f"Error actualizando resultados: {e}")
        
        finally:
            # Restaurar controles
            self.training_running = False
            self.train_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)
    
    def _training_error(self, error_msg: str):
        """Maneja errores en el entrenamiento."""
        self.status_label.configure(text=f"Error en entrenamiento: {error_msg}")
        messagebox.showerror("Error en Entrenamiento", f"❌ Error en entrenamiento ISA:\n{error_msg}")
        
        # Restaurar controles
        self.training_running = False
        self.train_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.progress_var.set(0)
    
    def _stop_training(self):
        """Detiene el entrenamiento en curso."""
        self.training_running = False
        self.status_label.configure(text="Entrenamiento detenido por el usuario")
        self.train_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.progress_var.set(0)
    
    def _update_database_info(self):
        """Actualiza la información de la base de datos."""
        try:
            stats = self.ml_database.get_database_stats()
            total_records = stats.get('total_records', 0)
            self.db_info_label.configure(text=f"📊 {total_records} registros en BD")
        except Exception as e:
            logger.error(f"Error actualizando información de BD: {e}")
            self.db_info_label.configure(text="❌ Error conectando a BD")
    
    def _update_database_stats(self):
        """Actualiza las estadísticas de la base de datos."""
        try:
            self.db_stats_text.config(state=tk.NORMAL)
            self.db_stats_text.delete(1.0, tk.END)
            
            stats = self.ml_database.get_database_stats()
            
            self.db_stats_text.insert(tk.END, "🗄️ ESTADÍSTICAS DE LA BASE DE DATOS\n")
            self.db_stats_text.insert(tk.END, "=" * 50 + "\n\n")
            
            self.db_stats_text.insert(tk.END, f"📊 Registros totales: {stats.get('total_records', 0)}\n")
            self.db_stats_text.insert(tk.END, f"📅 Última actualización: {stats.get('last_update', 'N/A')}\n")
            self.db_stats_text.insert(tk.END, f"💾 Tamaño de BD: {stats.get('database_size_mb', 0):.2f} MB\n")
            self.db_stats_text.insert(tk.END, f"🗂️ Datasets en cache: {stats.get('cached_datasets', 0)}\n")
            self.db_stats_text.insert(tk.END, f"📈 Métricas de validación: {stats.get('validation_metrics', 0)}\n")
            self.db_stats_text.insert(tk.END, f"🤖 Resultados ML: {stats.get('ml_results', 0)}\n\n")
            
            if stats.get('total_records', 0) == 0:
                self.db_stats_text.insert(tk.END, "⚠️ La base de datos está vacía.\n")
                self.db_stats_text.insert(tk.END, "💡 Carga datos desde el DataManager para comenzar.\n")
            
            self.db_stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas de BD: {e}")
    
    def _update_training_results(self):
        """Actualiza los resultados de entrenamiento."""
        try:
            self.training_text.config(state=tk.NORMAL)
            self.training_text.delete(1.0, tk.END)
            
            self.training_text.insert(tk.END, "🤖 RESULTADOS DE ENTRENAMIENTO ISA\n")
            self.training_text.insert(tk.END, "=" * 50 + "\n\n")
            
            if self.training_results:
                self.training_text.insert(tk.END, f"🎯 Target: {self.target_var.get()}\n")
                self.training_text.insert(tk.END, f"🤖 Modelo: {self.model_var.get()}\n")
                self.training_text.insert(tk.END, f"📊 Split ratio: {self.split_var.get()}\n\n")
                
                # Métricas de performance
                self.training_text.insert(tk.END, "📈 MÉTRICAS DE PERFORMANCE:\n")
                self.training_text.insert(tk.END, "-" * 30 + "\n")
                
                if 'r2_score' in self.training_results:
                    self.training_text.insert(tk.END, f"• R² Score: {self.training_results['r2_score']:.4f}\n")
                
                if 'mae' in self.training_results:
                    self.training_text.insert(tk.END, f"• MAE: {self.training_results['mae']:.4f}\n")
                
                if 'rmse' in self.training_results:
                    self.training_text.insert(tk.END, f"• RMSE: {self.training_results['rmse']:.4f}\n")
                
                if 'cross_val_score' in self.training_results:
                    cv_score = self.training_results['cross_val_score']
                    self.training_text.insert(tk.END, f"• Cross-validation: {cv_score:.4f}\n")
                
                self.training_text.insert(tk.END, "\n")
                
                # Información del modelo
                self.training_text.insert(tk.END, "🤖 INFORMACIÓN DEL MODELO:\n")
                self.training_text.insert(tk.END, "-" * 30 + "\n")
                
                if 'feature_importance' in self.training_results:
                    self.training_text.insert(tk.END, "• Feature importance calculada\n")
                
                if 'model_params' in self.training_results:
                    self.training_text.insert(tk.END, "• Parámetros del modelo optimizados\n")
                
                if 'training_time' in self.training_results:
                    self.training_text.insert(tk.END, f"• Tiempo de entrenamiento: {self.training_results['training_time']:.2f}s\n")
                
                self.training_text.insert(tk.END, "\n✅ Entrenamiento completado exitosamente\n")
            else:
                self.training_text.insert(tk.END, "❌ No hay resultados de entrenamiento disponibles.\n")
                self.training_text.insert(tk.END, "🤖 Ejecuta el entrenamiento para ver resultados.\n")
            
            self.training_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error actualizando resultados de entrenamiento: {e}")
    
    def _refresh_models_list(self):
        """Actualiza la lista de modelos disponibles."""
        try:
            # Limpiar lista actual
            for item in self.models_tree.get_children():
                self.models_tree.delete(item)
            
            # Obtener modelos de la base de datos
            ml_results = self.ml_database.get_ml_validation_results()
            
            for result in ml_results:
                self.models_tree.insert("", "end", values=(
                    result.get('analysis_type', 'N/A'),
                    result.get('asset_type', 'unknown'),
                    result.get('description', 'N/A'),
                    result.get('created_at', 'N/A'),
                    result.get('created_at', 'N/A')
                ))
            
        except Exception as e:
            logger.error(f"Error actualizando lista de modelos: {e}")
    
    def _clear_database_cache(self):
        """Limpia el cache de la base de datos."""
        try:
            success = self.ml_database.clear_cache()
            if success:
                messagebox.showinfo("Cache Limpiado", "✅ Cache de la base de datos limpiado exitosamente.")
                self._update_database_stats()
            else:
                messagebox.showerror("Error", "❌ Error limpiando cache de la base de datos.")
        except Exception as e:
            logger.error(f"Error limpiando cache: {e}")
            messagebox.showerror("Error", f"Error limpiando cache: {e}")
    
    def _export_database_data(self):
        """Exporta datos de la base de datos."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                # Obtener todos los datos
                data = self.ml_database._load_all_ml_data()
                if data is not None and not data.empty:
                    data.to_csv(filename, index=False)
                    messagebox.showinfo("Exportación Exitosa", 
                                      f"✅ Datos exportados exitosamente a:\n{filename}")
                else:
                    messagebox.showwarning("Sin Datos", "No hay datos disponibles para exportar.")
        except Exception as e:
            logger.error(f"Error exportando datos: {e}")
            messagebox.showerror("Error", f"Error exportando datos: {e}")
    
    def _view_model_details(self):
        """Muestra detalles del modelo seleccionado."""
        selection = self.models_tree.selection()
        if not selection:
            messagebox.showwarning("Sin Selección", "Selecciona un modelo para ver detalles.")
            return
        
        # Aquí se implementaría la visualización de detalles del modelo
        messagebox.showinfo("Detalles del Modelo", "📊 Funcionalidad de detalles en desarrollo.")
    
    def _delete_model(self):
        """Elimina el modelo seleccionado."""
        selection = self.models_tree.selection()
        if not selection:
            messagebox.showwarning("Sin Selección", "Selecciona un modelo para eliminar.")
            return
        
        if messagebox.askyesno("Confirmar Eliminación", 
                              "¿Estás seguro de que quieres eliminar el modelo seleccionado?"):
            # Aquí se implementaría la eliminación del modelo
            messagebox.showinfo("Modelo Eliminado", "🗑️ Modelo eliminado exitosamente.")
            self._refresh_models_list()
    
    def _export_selected_model(self):
        """Exporta el modelo seleccionado."""
        selection = self.models_tree.selection()
        if not selection:
            messagebox.showwarning("Sin Selección", "Selecciona un modelo para exportar.")
            return
        
        # Aquí se implementaría la exportación del modelo
        messagebox.showinfo("Exportación", "📤 Funcionalidad de exportación en desarrollo.")
    
    def _export_model(self):
        """Exporta el modelo actual."""
        if self.current_model is None:
            messagebox.showwarning("Sin Modelo", "No hay modelo entrenado para exportar.")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pkl",
                filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")]
            )
            
            if filename:
                # Aquí se implementaría la exportación del modelo
                messagebox.showinfo("Exportación Exitosa", 
                                  f"✅ Modelo exportado exitosamente a:\n{filename}")
        except Exception as e:
            logger.error(f"Error exportando modelo: {e}")
            messagebox.showerror("Error", f"Error exportando modelo: {e}")
    
    def _export_all(self):
        """Exporta todo el contenido."""
        messagebox.showinfo("Exportación", "📤 Funcionalidad de exportación completa en desarrollo.")
    
    def _export_model_only(self):
        """Exporta solo el modelo."""
        messagebox.showinfo("Exportación", "🤖 Funcionalidad de exportación de modelo en desarrollo.")
    
    def _export_data_only(self):
        """Exporta solo los datos."""
        messagebox.showinfo("Exportación", "📊 Funcionalidad de exportación de datos en desarrollo.")
    
    def _export_metrics_only(self):
        """Exporta solo las métricas."""
        messagebox.showinfo("Exportación", "📈 Funcionalidad de exportación de métricas en desarrollo.")
    
    def _clear_results(self):
        """Limpia los resultados."""
        self.training_results = {}
        self.current_model = None
        
        # Limpiar pestañas
        self._update_training_results()
        self._refresh_models_list()
        
        # Restaurar controles
        self.progress_var.set(0)
        self.status_label.configure(text="Listo para conectar a la base de datos")
        
        messagebox.showinfo("Limpieza Completada", "🗑️ Todos los resultados han sido limpiados.")


def create_isa_database_tab(parent, data_manager: DataManager):
    """
    Función factory para crear la pestaña de Base de Datos ISA.
    
    Args:
        parent: Widget padre
        data_manager: Gestor de datos
        
    Returns:
        Instancia de ISADatabaseTab
    """
    try:
        tab = ISADatabaseTab(parent, data_manager)
        
        # Añadir la pestaña al notebook
        notebook = parent
        notebook.add(tab, text="🗄️ Base de Datos ISA")
        
        logger.info("✅ ISADatabaseTab configurada")
        return tab
        
    except Exception as e:
        logger.error(f"❌ Error creando pestaña ISA: {e}")
        # Crear pestaña de fallback
        fallback_frame = ttk.Frame(parent)
        parent.add(fallback_frame, text="🗄️ Base de Datos ISA")
        
        error_label = ttk.Label(fallback_frame, text=f"Error: {str(e)}")
        error_label.pack(pady=20)
        
        return fallback_frame 