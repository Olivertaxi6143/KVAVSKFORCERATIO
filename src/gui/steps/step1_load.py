import numpy as np
from typing import Optional, Any, Union
import warnings
"""
Step 1: Cargar Datos - Módulo del Wizard

Este módulo contiene la interfaz para el primer paso del wizard:
carga de archivos de datos necesarios para el análisis.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import pandas as pd
from typing import Optional, Dict, Any, Callable
from pathlib import Path

# Importar utilidades GUI
from ..utils import (
    create_styled_button, create_styled_label, show_info_message,
    show_error_message, select_file, select_directory, validate_dataframe,
    load_data_with_datamanager, GUIAnalysisError
)

# Configurar logging
try:
    from core.logger_config import setup_logger
    logger = setup_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class Step1LoadFrame(ttk.Frame):
    """
    Frame para el Paso 1: Cargar Datos
    
    Este módulo maneja la carga de archivos necesarios para el análisis:
    - Archivo de KPIs (CSV con métricas de estrategias)
    - Carpeta de estrategias (archivos .sqx)
    - Datos de mercado (opcional)
    """
    
    def __init__(self, parent, data_manager=None, on_data_loaded=None, on_next_step=None):
        """
        Inicializa el frame del Paso 1.
        
        Args:
            parent: Widget padre
            data_manager: Instancia del DataManager
            on_data_loaded: Callback cuando se cargan datos
            on_next_step: Callback para ir al siguiente paso
        """
        super().__init__(parent)
        
        self.data_manager = data_manager
        self.on_data_loaded = on_data_loaded
        self.on_next_step = on_next_step
        
        # Variables de archivos
        self.kpi_file_var = tk.StringVar()
        self.strategies_folder_var = tk.StringVar()
        self.market_file_var = tk.StringVar()
        self.destination_folder_var = tk.StringVar()
        
        # Estado de carga
        self.load_status = {
            'kpi_file': False,
            'strategies_folder': False,
            'market_file': False,
            'destination_folder': False
        }
        
        # Construir interfaz
        self._build_interface()
        
        logger.info("✅ Step1LoadFrame inicializado correctamente")
    
    def _build_interface(self):
        """Construye la interfaz del Paso 1."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título del paso
        self._build_title_section(main_frame)
        
        # Descripción del paso
        self._build_description_section(main_frame)
        
        # Frame de configuración de archivos
        self._build_files_section(main_frame)
        
        # Frame de estado
        self._build_status_section(main_frame)
        
        # Frame de navegación
        self._build_navigation_section(main_frame)
    
    def _build_title_section(self, parent):
        """Construye la sección del título."""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame, 
            text="📁 PASO 1: CARGAR DATOS", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(anchor="w")
    
    def _build_description_section(self, parent):
        """Construye la sección de descripción."""
        desc_frame = ttk.Frame(parent)
        desc_frame.pack(fill="x", pady=(0, 20))
        
        desc_label = ttk.Label(
            desc_frame, 
            text="En este paso cargarás los archivos necesarios para el análisis:", 
            font=("Arial", 10)
        )
        desc_label.pack(anchor="w")
        
        # Lista de archivos necesarios
        files_list = [
            "• Archivo de KPIs (CSV con métricas de estrategias)",
            "• Carpeta de estrategias (archivos .sqx)",
            "• Datos de mercado (opcional, para análisis avanzado)"
        ]
        
        for file_desc in files_list:
            file_label = ttk.Label(
                desc_frame, 
                text=file_desc, 
                font=("Arial", 9)
            )
            file_label.pack(anchor="w")
    
    def _build_files_section(self, parent):
        """Construye la sección de archivos."""
        files_frame = ttk.LabelFrame(
            parent, 
            text="📂 Archivos del Proyecto", 
            padding=15
        )
        files_frame.pack(fill="x", pady=(0, 20))
        
        # Configuración de archivos
        self._build_file_config(files_frame)
    
    def _build_file_config(self, parent):
        """Construye la configuración de archivos."""
        # Función auxiliar para agregar filas de archivo
        def add_file_row(label, var, row, is_file=True):
            # Frame para la fila
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill="x", pady=2)
            
            # Etiqueta
            label_widget = ttk.Label(row_frame, text=label, width=20)
            label_widget.pack(side="left")
            
            # Campo de entrada
            entry = ttk.Entry(row_frame, textvariable=var, state="readonly", width=50)
            entry.pack(side="left", padx=(10, 5))
            
            # Botón de selección
            if is_file:
                button = create_styled_button(
                    row_frame, 
                    "📁 Seleccionar", 
                    lambda v=var: self._select_file(v)
                )
            else:
                button = create_styled_button(
                    row_frame, 
                    "📁 Seleccionar", 
                    lambda v=var: self._select_folder(v)
                )
            button.pack(side="left")
            
            # Etiqueta de estado
            status_var = tk.StringVar(value="⏳ Pendiente")
            status_label = ttk.Label(row_frame, textvariable=status_var, font=("Arial", 8))
            status_label.pack(side="right")
            
            return status_var
        
        # Agregar filas de archivos
        self.kpi_status_var = add_file_row("📊 Archivo KPI:", self.kpi_file_var, 0, True)
        self.strategies_status_var = add_file_row("📁 Carpeta Estrategias:", self.strategies_folder_var, 1, False)
        self.market_status_var = add_file_row("📈 Datos Mercado:", self.market_file_var, 2, True)
        self.destination_status_var = add_file_row("🎯 Carpeta Destino:", self.destination_folder_var, 3, False)
    
    def _build_status_section(self, parent):
        """Construye la sección de estado."""
        status_frame = ttk.LabelFrame(
            parent, 
            text="📊 Estado de Carga", 
            padding=15
        )
        status_frame.pack(fill="x", pady=(0, 20))
        
        self.step1_status_label = ttk.Label(
            status_frame, 
            text="⏳ Pendiente de cargar archivos", 
            font=("Arial", 10, "bold")
        )
        self.step1_status_label.pack(anchor="w")
    
    def _build_navigation_section(self, parent):
        """Construye la sección de navegación."""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill="x", pady=(20, 0))
        
        # Botón anterior (deshabilitado en paso 1)
        prev_button = ttk.Button(
            nav_frame, 
            text="⬅️ Anterior", 
            state="disabled"
        )
        prev_button.pack(side="left")
        
        # Botón siguiente
        next_button = create_styled_button(
            nav_frame, 
            "Siguiente ➡️", 
            self._go_to_next_step
        )
        next_button.pack(side="right")
        
        # Botón de validación
        validate_button = create_styled_button(
            nav_frame, 
            "🔍 Validar Datos", 
            self._validate_data
        )
        validate_button.pack(side="right", padx=(0, 10))
    
    def _select_file(self, var):
        """Selecciona un archivo."""
        try:
            file_path = select_file(
                title="Seleccionar archivo",
                filetypes=[
                    ("Archivos CSV", "*.csv"),
                    ("Archivos Excel", "*.xlsx;*.xls"),
                    ("Todos los archivos", "*.*")
                ]
            )
            
            if file_path:
                var.set(file_path)
                self._update_file_status(var, file_path)
                logger.info(f"✅ Archivo seleccionado: {file_path}")
                
        except Exception as e:
            show_error_message("Error", f"Error seleccionando archivo: {str(e)}")
            logger.error(f"❌ Error seleccionando archivo: {e}")
    
    def _select_folder(self, var):
        """Selecciona una carpeta."""
        try:
            folder_path = select_directory(title="Seleccionar carpeta")
            
            if folder_path:
                var.set(folder_path)
                self._update_folder_status(var, folder_path)
                logger.info(f"✅ Carpeta seleccionada: {folder_path}")
                
        except Exception as e:
            show_error_message("Error", f"Error seleccionando carpeta: {str(e)}")
            logger.error(f"❌ Error seleccionando carpeta: {e}")
    
    def _update_file_status(self, var, file_path):
        """Actualiza el estado de un archivo."""
        try:
            # Verificar que el archivo existe
            if Path(file_path).exists():
                if var == self.kpi_file_var:
                    self.kpi_status_var.set("✅ Cargado")
                    self.load_status['kpi_file'] = True
                elif var == self.market_file_var:
                    self.market_status_var.set("✅ Cargado")
                    self.load_status['market_file'] = True
                
                self._update_overall_status()
            else:
                if var == self.kpi_file_var:
                    self.kpi_status_var.set("❌ No encontrado")
                elif var == self.market_file_var:
                    self.market_status_var.set("❌ No encontrado")
                    
        except Exception as e:
            logger.error(f"Error actualizando estado de archivo: {e}")
    
    def _update_folder_status(self, var, folder_path):
        """Actualiza el estado de una carpeta."""
        try:
            # Verificar que la carpeta existe
            if Path(folder_path).exists():
                if var == self.strategies_folder_var:
                    self.strategies_status_var.set("✅ Cargado")
                    self.load_status['strategies_folder'] = True
                elif var == self.destination_folder_var:
                    self.destination_status_var.set("✅ Cargado")
                    self.load_status['destination_folder'] = True
                
                self._update_overall_status()
            else:
                if var == self.strategies_folder_var:
                    self.strategies_status_var.set("❌ No encontrado")
                elif var == self.destination_folder_var:
                    self.destination_status_var.set("❌ No encontrado")
                    
        except Exception as e:
            logger.error(f"Error actualizando estado de carpeta: {e}")
    
    def _update_overall_status(self):
        """Actualiza el estado general del paso."""
        # Verificar si se han cargado los archivos mínimos necesarios
        kpi_loaded = self.load_status['kpi_file']
        strategies_loaded = self.load_status['strategies_folder']
        
        if kpi_loaded and strategies_loaded:
            self.getattr(step1_status_label, 'config', None)(
                text="✅ Datos cargados correctamente",
                foreground="green"
            )
            logger.info("✅ Paso 1: Datos cargados correctamente")
        elif kpi_loaded or strategies_loaded:
            self.getattr(step1_status_label, 'config', None)(
                text="⚠️ Cargados parcialmente - Falta archivo KPI o carpeta de estrategias",
                foreground="orange"
            )
        else:
            self.getattr(step1_status_label, 'config', None)(
                text="⏳ Pendiente de cargar archivos",
                foreground="black"
            )
    
    def _validate_data(self):
        """Valida los datos del paso 1."""
        try:
            # Verificar que se han cargado los archivos necesarios
            if self.load_status['kpi_file'] and self.load_status['strategies_folder']:
                
                # Intentar cargar y validar datos
                if self.data_manager:
                    kpi_file = self.kpi_file_var.get()
                    if kpi_file:
                        df = load_data_with_datamanager(kpi_file, self.data_manager)
                        is_valid, errors = validate_dataframe(df)
                        
                        if is_valid:
                            show_info_message(
                                "Validación Exitosa", 
                                "Los datos han sido validados correctamente."
                            )
                            self.getattr(step1_status_label, 'config', None)(
                                text="✅ Datos validados correctamente",
                                foreground="green"
                            )
                            
                            # Llamar callback si existe
                            if self.on_data_loaded:
                                self.on_data_loaded(df)
                                
                            logger.info("✅ Datos validados correctamente")
                        else:
                            show_error_message(
                                "Error de Validación", 
                                f"Los datos contienen errores:\n{'; '.join(errors)}"
                            )
                            self.getattr(step1_status_label, 'config', None)(
                                text="❌ Error: Datos inválidos",
                                foreground="red"
                            )
                            logger.error(f"❌ Error validando datos: {errors}")
                    else:
                        show_error_message(
                            "Error", 
                            "Por favor, selecciona un archivo KPI antes de validar."
                        )
                else:
                    show_info_message(
                        "Validación", 
                        "Los datos han sido validados correctamente."
                    )
                    self.getattr(step1_status_label, 'config', None)(
                        text="✅ Datos validados correctamente",
                        foreground="green"
                    )
            else:
                show_error_message(
                    "Error", 
                    "Por favor, carga los archivos necesarios antes de continuar."
                )
                self.getattr(step1_status_label, 'config', None)(
                    text="❌ Error: Falta cargar archivos",
                    foreground="red"
                )
                
        except Exception as e:
            show_error_message("Error", f"Error validando datos: {str(e)}")
            self.getattr(step1_status_label, 'config', None)(
                text="❌ Error validando datos",
                foreground="red"
            )
            logger.error(f"❌ Error validando datos: {e}")
    
    def _go_to_next_step(self):
        """Va al siguiente paso del wizard."""
        try:
            # Verificar que se han cargado los datos mínimos
            if self.load_status['kpi_file'] and self.load_status['strategies_folder']:
                
                # Validar datos antes de continuar
                self._validate_data()
                
                # Llamar callback si existe
                if self.on_next_step:
                    self.on_next_step()
                else:
                    logger.info("✅ Paso 1 completado - Continuando al siguiente paso")
                    
            else:
                show_error_message(
                    "Error", 
                    "Por favor, carga al menos el archivo KPI y la carpeta de estrategias antes de continuar."
                )
                
        except Exception as e:
            show_error_message("Error", f"Error navegando al siguiente paso: {str(e)}")
            logger.error(f"❌ Error navegando al siguiente paso: {e}")
    
    def get_loaded_data(self) -> Dict[str, Any]:
        """Obtiene los datos cargados en este paso."""
        return {
            'kpi_file': self.kpi_file_var.get(),
            'strategies_folder': self.strategies_folder_var.get(),
            'market_file': self.market_file_var.get(),
            'destination_folder': self.destination_folder_var.get(),
            'load_status': self.load_status.copy()
        }
    
    def set_loaded_data(self, data: Dict[str, Any]):
        """Establece los datos cargados desde el exterior."""
        try:
            if 'kpi_file' in data:
                self.kpi_file_var.set(data['kpi_file'])
                if data['kpi_file']:
                    self._update_file_status(self.kpi_file_var, data['kpi_file'])
            
            if 'strategies_folder' in data:
                self.strategies_folder_var.set(data['strategies_folder'])
                if data['strategies_folder']:
                    self._update_folder_status(self.strategies_folder_var, data['strategies_folder'])
            
            if 'market_file' in data:
                self.market_file_var.set(data['market_file'])
                if data['market_file']:
                    self._update_file_status(self.market_file_var, data['market_file'])
            
            if 'destination_folder' in data:
                self.destination_folder_var.set(data['destination_folder'])
                if data['destination_folder']:
                    self._update_folder_status(self.destination_folder_var, data['destination_folder'])
            
            if 'load_status' in data:
                self.load_status.update(data['load_status'])
                self._update_overall_status()
                
            logger.info("✅ Datos establecidos en Step1LoadFrame")
            
        except Exception as e:
            logger.error(f"❌ Error estableciendo datos: {e}")
    
    def is_ready_for_next_step(self) -> bool:
        """Verifica si el paso está listo para continuar."""
        return self.load_status['kpi_file'] and self.load_status['strategies_folder']
    
    def reset_step(self):
        """Reinicia el paso."""
        try:
            # Limpiar variables
            self.kpi_file_var.set("")
            self.strategies_folder_var.set("")
            self.market_file_var.set("")
            self.destination_folder_var.set("")
            
            # Limpiar estados
            self.load_status = {
                'kpi_file': False,
                'strategies_folder': False,
                'market_file': False,
                'destination_folder': False
            }
            
            # Actualizar interfaz
            self.kpi_status_var.set("⏳ Pendiente")
            self.strategies_status_var.set("⏳ Pendiente")
            self.market_status_var.set("⏳ Pendiente")
            self.destination_status_var.set("⏳ Pendiente")
            self.getattr(step1_status_label, 'config', None)(
                text="⏳ Pendiente de cargar archivos",
                foreground="black"
            )
            
            logger.info("✅ Step1LoadFrame reiniciado")
            
        except Exception as e:
            logger.error(f"❌ Error reiniciando paso: {e}")


def create_step1_load_frame(parent, **kwargs):
    """
    Función factory para crear el frame del Paso 1.
    
    Args:
        parent: Widget padre
        **kwargs: Argumentos adicionales para Step1LoadFrame
        
    Returns:
        Step1LoadFrame: Instancia del frame del Paso 1
    """
    return Step1LoadFrame(parent, **kwargs) 