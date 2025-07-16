"""
Advanced Filters Popup
Popup avanzado con filtros dinámicos para análisis detallado de estrategias
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class AdvancedFiltersPopup:
    """
    Popup avanzado con filtros dinámicos para análisis detallado de estrategias.
    
    Características:
    - Filtros por rangos numéricos con sliders
    - Filtros por categorías con checkboxes
    - Filtros por regímenes de mercado
    - Búsqueda por texto
    - Filtros combinados
    - Exportación de filtros
    """
    
    def __init__(self, parent: tk.Tk, data: pd.DataFrame, on_filter_changed: Optional[Callable] = None):
        """
        Inicializa el popup de filtros avanzados.
        
        Args:
            parent: Ventana padre
            data: DataFrame con datos de estrategias
            on_filter_changed: Callback cuando cambian los filtros
        """
        self.parent = parent
        self.data = data.copy()
        self.on_filter_changed = on_filter_changed
        self.filtered_data = data.copy()
        
        # Configurar ventana popup
        self.popup = tk.Toplevel(parent)
        self.popup.title("🔍 Filtros Avanzados")
        self.popup.geometry("800x600")
        self.popup.resizable(True, True)
        
        # Centrar ventana
        self.popup.transient(parent)
        self.popup.grab_set()
        
        # Variables de filtros
        self.filter_vars = {}
        self.range_vars = {}
        self.category_vars = {}
        
        # Construir interfaz
        self._build_interface()
        # self._setup_filters()  # Eliminado: método inexistente
        
        logger.info("✅ AdvancedFiltersPopup inicializado")
    
    def _build_interface(self):
        """Construye la interfaz del popup."""
        # Frame principal
        main_frame = ttk.Frame(self.popup)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔍 Filtros Avanzados", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Notebook para organizar filtros
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Crear pestañas de filtros
        self._create_numeric_filters_tab()
        self._create_category_filters_tab()
        self._create_text_search_tab()
        self._create_combined_filters_tab()
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Botones de acción
        ttk.Button(button_frame, text="🔄 Aplicar Filtros", 
                  command=self._apply_filters).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🗑️ Limpiar Filtros", 
                  command=self._clear_filters).pack(side="left", padx=5)
        ttk.Button(button_frame, text="💾 Guardar Filtros", 
                  command=self._save_filters).pack(side="left", padx=5)
        ttk.Button(button_frame, text="📊 Estadísticas", 
                  command=self._show_statistics).pack(side="left", padx=5)
        ttk.Button(button_frame, text="❌ Cerrar", 
                  command=self.popup.destroy).pack(side="right", padx=5)
    
    def _create_numeric_filters_tab(self):
        """Crea pestaña de filtros numéricos."""
        numeric_frame = ttk.Frame(self.notebook)
        self.notebook.add(numeric_frame, text="📊 Numéricos")
        
        # Scrollable frame
        canvas = tk.Canvas(numeric_frame)
        scrollbar = ttk.Scrollbar(numeric_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Filtros numéricos
        numeric_columns = self._get_numeric_columns()
        
        for col in numeric_columns:
            self._create_numeric_filter(scrollable_frame, col)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_category_filters_tab(self):
        """Crea pestaña de filtros por categorías."""
        category_frame = ttk.Frame(self.notebook)
        self.notebook.add(category_frame, text="🏷️ Categorías")
        
        # Scrollable frame
        canvas = tk.Canvas(category_frame)
        scrollbar = ttk.Scrollbar(category_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Filtros por categorías
        category_columns = self._get_category_columns()
        
        for col in category_columns:
            self._create_category_filter(scrollable_frame, col)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_text_search_tab(self):
        """Crea pestaña de búsqueda por texto."""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="🔍 Búsqueda")
        
        # Búsqueda por nombre de estrategia
        ttk.Label(search_frame, text="Buscar por nombre de estrategia:").pack(pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.pack(pady=5)
        
        # Búsqueda por palabras clave
        ttk.Label(search_frame, text="Palabras clave (separadas por comas):").pack(pady=5)
        
        self.keywords_var = tk.StringVar()
        keywords_entry = ttk.Entry(search_frame, textvariable=self.keywords_var, width=50)
        keywords_entry.pack(pady=5)
        
        # Opciones de búsqueda
        search_options_frame = ttk.Frame(search_frame)
        search_options_frame.pack(pady=10)
        
        self.case_sensitive_var = tk.BooleanVar()
        ttk.Checkbutton(search_options_frame, text="Sensible a mayúsculas", 
                       variable=self.case_sensitive_var).pack(side="left", padx=5)
        
        self.exact_match_var = tk.BooleanVar()
        ttk.Checkbutton(search_options_frame, text="Coincidencia exacta", 
                       variable=self.exact_match_var).pack(side="left", padx=5)
    
    def _create_combined_filters_tab(self):
        """Crea pestaña de filtros combinados."""
        combined_frame = ttk.Frame(self.notebook)
        self.notebook.add(combined_frame, text="🔗 Combinados")
        
        # Filtros predefinidos
        ttk.Label(combined_frame, text="Filtros predefinidos:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Elite strategies
        self.elite_var = tk.BooleanVar()
        ttk.Checkbutton(combined_frame, text="🏆 Solo estrategias Elite (Factor K ≥ 9.2)", 
                       variable=self.elite_var).pack(pady=2)
        
        # High Sharpe
        self.high_sharpe_var = tk.BooleanVar()
        ttk.Checkbutton(combined_frame, text="📈 Alto Sharpe (≥ 1.5)", 
                       variable=self.high_sharpe_var).pack(pady=2)
        
        # Low Drawdown
        self.low_dd_var = tk.BooleanVar()
        ttk.Checkbutton(combined_frame, text="🛡️ Bajo Drawdown (≤ 15%)", 
                       variable=self.low_dd_var).pack(pady=2)
        
        # Consistent performance
        self.consistent_var = tk.BooleanVar()
        ttk.Checkbutton(combined_frame, text="📊 Rendimiento consistente (IS/OOS ratio ≥ 0.8)", 
                       variable=self.consistent_var).pack(pady=2)
        
        # Separador
        ttk.Separator(combined_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # Filtros personalizados
        ttk.Label(combined_frame, text="Filtros personalizados:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Frame para filtros personalizados
        custom_frame = ttk.Frame(combined_frame)
        custom_frame.pack(fill="both", expand=True)
        
        # Botón para agregar filtro personalizado
        ttk.Button(custom_frame, text="➕ Agregar Filtro Personalizado", 
                  command=self._add_custom_filter).pack(pady=5)
    
    def _get_numeric_columns(self) -> List[str]:
        """Obtiene columnas numéricas del DataFrame."""
        numeric_cols = []
        for col in self.data.columns:
            if pd.api.types.is_numeric_dtype(self.data[col]):
                numeric_cols.append(col)
        return numeric_cols[:10]  # Limitar a 10 columnas para no sobrecargar
    
    def _get_category_columns(self) -> List[str]:
        """Obtiene columnas categóricas del DataFrame."""
        category_cols = []
        for col in self.data.columns:
            if self.data[col].dtype == 'object' or self.data[col].dtype.name == 'category':
                if self.data[col].nunique() <= 20:  # Solo columnas con pocos valores únicos
                    category_cols.append(col)
        return category_cols[:10]  # Limitar a 10 columnas
    
    def _create_numeric_filter(self, parent: ttk.Frame, column: str):
        """Crea filtro numérico para una columna."""
        try:
            # Frame para el filtro
            filter_frame = ttk.LabelFrame(parent, text=f"📊 {column}")
            filter_frame.pack(fill="x", padx=5, pady=5)
            
            # Estadísticas de la columna
            col_data = pd.to_numeric(self.data[column], errors='coerce')
            if isinstance(col_data, pd.Series):
                col_data = col_data.dropna()
            else:
                col_data = pd.Series(dtype=float)
            
            if len(col_data) == 0:
                ttk.Label(filter_frame, text="No hay datos numéricos válidos").pack()
                return
            
            min_val = float(col_data.min())
            max_val = float(col_data.mean() + 2 * col_data.std())  # Usar mean + 2*std como max
            
            # Variables para el filtro
            min_var = tk.DoubleVar(value=min_val)
            max_var = tk.DoubleVar(value=max_val)
            enabled_var = tk.BooleanVar(value=False)
            
            # Guardar variables
            self.range_vars[column] = {
                'min': min_var,
                'max': max_var,
                'enabled': enabled_var
            }
            
            # Checkbox para habilitar filtro
            ttk.Checkbutton(filter_frame, text=f"Habilitar filtro para {column}", 
                           variable=enabled_var).pack(anchor="w")
            
            # Sliders
            slider_frame = ttk.Frame(filter_frame)
            slider_frame.pack(fill="x", padx=10, pady=5)
            
            # Slider mínimo
            ttk.Label(slider_frame, text=f"Mínimo: {min_val:.2f}").pack(anchor="w")
            min_slider = ttk.Scale(slider_frame, from_=min_val, to=max_val, 
                                  variable=min_var, orient="horizontal")
            min_slider.pack(fill="x", pady=2)
            
            # Slider máximo
            ttk.Label(slider_frame, text=f"Máximo: {max_val:.2f}").pack(anchor="w")
            max_slider = ttk.Scale(slider_frame, from_=min_val, to=max_val, 
                                  variable=max_var, orient="horizontal")
            max_slider.pack(fill="x", pady=2)
            
            # Labels con valores actuales
            values_frame = ttk.Frame(filter_frame)
            values_frame.pack(fill="x", pady=5)
            
            min_label = ttk.Label(values_frame, text=f"Min: {min_var.get():.2f}")
            min_label.pack(side="left", padx=5)
            
            max_label = ttk.Label(values_frame, text=f"Max: {max_var.get():.2f}")
            max_label.pack(side="right", padx=5)
            
            # Actualizar labels cuando cambien los sliders
            def update_labels(*args):
                min_label.config(text=f"Min: {min_var.get():.2f}")
                max_label.config(text=f"Max: {max_var.get():.2f}")
            
            min_var.trace("w", update_labels)
            max_var.trace("w", update_labels)
            
        except Exception as e:
            logger.warning(f"Error creando filtro numérico para {column}: {e}")
    
    def _create_category_filter(self, parent: ttk.Frame, column: str):
        """Crea filtro por categorías para una columna."""
        try:
            # Frame para el filtro
            filter_frame = ttk.LabelFrame(parent, text=f"🏷️ {column}")
            filter_frame.pack(fill="x", padx=5, pady=5)
            
            # Obtener valores únicos
            unique_values = self.data[column].dropna().unique()
            if len(unique_values) > 20:
                unique_values = unique_values[:20]  # Limitar a 20 valores
            
            # Variables para checkboxes
            category_vars = {}
            for value in unique_values:
                var = tk.BooleanVar(value=True)  # Por defecto seleccionado
                category_vars[str(value)] = var
            
            self.category_vars[column] = category_vars
            
            # Crear checkboxes
            for value in unique_values:
                ttk.Checkbutton(filter_frame, text=str(value), 
                               variable=category_vars[str(value)]).pack(anchor="w", padx=10)
            
        except Exception as e:
            logger.warning(f"Error creando filtro de categoría para {column}: {e}")
    
    def _apply_filters(self):
        """Aplica todos los filtros configurados."""
        try:
            # Comenzar con todos los datos
            filtered_data = self.data.copy()
            if not isinstance(filtered_data, pd.DataFrame):
                filtered_data = pd.DataFrame(filtered_data)
            
            # Aplicar filtros numéricos
            for column, vars_dict in self.range_vars.items():
                if vars_dict['enabled'].get():
                    min_val = vars_dict['min'].get()
                    max_val = vars_dict['max'].get()
                    
                    # Convertir columna a numérico
                    col_data = pd.to_numeric(filtered_data[column], errors='coerce')
                    mask = (col_data >= min_val) & (col_data <= max_val)
                    filtered_data = filtered_data[mask]
                    if not isinstance(filtered_data, pd.DataFrame):
                        filtered_data = pd.DataFrame(filtered_data)
            
            # Aplicar filtros de categorías
            for column, category_vars in self.category_vars.items():
                selected_values = [value for value, var in category_vars.items() if var.get()]
                if selected_values:
                    if not isinstance(filtered_data, pd.DataFrame):
                        filtered_data = pd.DataFrame(filtered_data)
                    mask = filtered_data[column].isin(selected_values)
                    filtered_data = filtered_data[mask]
            
            # Aplicar búsqueda por texto
            if hasattr(self, 'search_var') and self.search_var.get().strip():
                search_term = self.search_var.get().strip()
                if not self.case_sensitive_var.get():
                    search_term = search_term.lower()
                
                def search_filter(row):
                    strategy_name = str(row.get('Strategy_Name', row.get('Strategy Name', '')))
                    if not self.case_sensitive_var.get():
                        strategy_name = strategy_name.lower()
                    
                    if self.exact_match_var.get():
                        return search_term == strategy_name
                    else:
                        return search_term in strategy_name
                if not isinstance(filtered_data, pd.DataFrame):
                    filtered_data = pd.DataFrame(filtered_data)
                mask = filtered_data.apply(search_filter, axis=1)
                filtered_data = filtered_data[mask]
            
            # Aplicar filtros combinados
            if hasattr(self, 'elite_var') and self.elite_var.get():
                # Filtrar estrategias Elite
                if isinstance(filtered_data, pd.DataFrame) and 'Factor_K' in filtered_data.columns:
                    mask = filtered_data['Factor_K'] >= 9.2
                    filtered_data = filtered_data[mask]
            
            if hasattr(self, 'high_sharpe_var') and self.high_sharpe_var.get():
                # Filtrar alto Sharpe
                sharpe_col = next((col for col in filtered_data.columns if 'Sharpe' in col), None) if isinstance(filtered_data, pd.DataFrame) else None
                if sharpe_col:
                    mask = filtered_data[sharpe_col] >= 1.5
                    filtered_data = filtered_data[mask]
            
            if hasattr(self, 'low_dd_var') and self.low_dd_var.get():
                # Filtrar bajo drawdown
                dd_col = next((col for col in filtered_data.columns if 'Drawdown' in col), None) if isinstance(filtered_data, pd.DataFrame) else None
                if dd_col:
                    mask = filtered_data[dd_col] <= 0.15
                    filtered_data = filtered_data[mask]
            
            # Actualizar datos filtrados
            self.filtered_data = filtered_data
            
            # Mostrar resultados
            messagebox.showinfo("Filtros Aplicados", 
                              f"Se encontraron {len(filtered_data)} estrategias que cumplen los criterios.")
            
            # Llamar callback si existe
            if self.on_filter_changed:
                self.on_filter_changed(filtered_data)
            
            logger.info(f"✅ Filtros aplicados: {len(filtered_data)} estrategias")
            
        except Exception as e:
            logger.error(f"Error aplicando filtros: {e}")
            messagebox.showerror("Error", f"Error aplicando filtros: {e}")
    
    def _clear_filters(self):
        """Limpia todos los filtros."""
        try:
            # Resetear variables de filtros numéricos
            for vars_dict in self.range_vars.values():
                vars_dict['enabled'].set(False)
            
            # Resetear variables de categorías
            for category_vars in self.category_vars.values():
                for var in category_vars.values():
                    var.set(True)
            
            # Resetear búsqueda
            if hasattr(self, 'search_var'):
                self.search_var.set("")
            if hasattr(self, 'keywords_var'):
                self.keywords_var.set("")
            
            # Resetear filtros combinados
            if hasattr(self, 'elite_var'):
                self.elite_var.set(False)
            if hasattr(self, 'high_sharpe_var'):
                self.high_sharpe_var.set(False)
            if hasattr(self, 'low_dd_var'):
                self.low_dd_var.set(False)
            if hasattr(self, 'consistent_var'):
                self.consistent_var.set(False)
            
            # Resetear datos filtrados
            self.filtered_data = self.data.copy()
            
            messagebox.showinfo("Filtros Limpiados", "Todos los filtros han sido limpiados.")
            
            # Llamar callback si existe
            if self.on_filter_changed:
                self.on_filter_changed(self.data.copy())
            
            logger.info("✅ Filtros limpiados")
            
        except Exception as e:
            logger.error(f"Error limpiando filtros: {e}")
            messagebox.showerror("Error", f"Error limpiando filtros: {e}")
    
    def _save_filters(self):
        """Guarda la configuración actual de filtros."""
        try:
            # Crear diccionario con configuración de filtros
            filter_config = {
                'numeric_filters': {},
                'category_filters': {},
                'search_filters': {},
                'combined_filters': {}
            }
            
            # Guardar filtros numéricos
            for column, vars_dict in self.range_vars.items():
                if vars_dict['enabled'].get():
                    filter_config['numeric_filters'][column] = {
                        'min': vars_dict['min'].get(),
                        'max': vars_dict['max'].get(),
                        'enabled': True
                    }
            
            # Guardar filtros de categorías
            for column, category_vars in self.category_vars.items():
                selected_values = [value for value, var in category_vars.items() if var.get()]
                if selected_values:
                    filter_config['category_filters'][column] = selected_values
            
            # Guardar filtros de búsqueda
            if hasattr(self, 'search_var'):
                filter_config['search_filters'] = {
                    'search_term': self.search_var.get(),
                    'case_sensitive': self.case_sensitive_var.get(),
                    'exact_match': self.exact_match_var.get()
                }
            
            # Guardar filtros combinados
            if hasattr(self, 'elite_var'):
                filter_config['combined_filters'] = {
                    'elite_only': self.elite_var.get(),
                    'high_sharpe': self.high_sharpe_var.get(),
                    'low_drawdown': self.low_dd_var.get(),
                    'consistent_performance': self.consistent_var.get()
                }
            
            # Guardar en archivo
            import json
            from pathlib import Path
            
            config_file = Path("filter_config.json")
            with open(config_file, 'w') as f:
                json.dump(filter_config, f, indent=2)
            
            messagebox.showinfo("Filtros Guardados", 
                              f"Configuración de filtros guardada en {config_file}")
            
            logger.info(f"✅ Filtros guardados en {config_file}")
            
        except Exception as e:
            logger.error(f"Error guardando filtros: {e}")
            messagebox.showerror("Error", f"Error guardando filtros: {e}")
    
    def _show_statistics(self):
        """Muestra estadísticas de los datos filtrados."""
        try:
            stats_text = f"""
📊 ESTADÍSTICAS DE FILTROS

📈 Datos Originales:
   - Total de estrategias: {len(self.data)}
   - Columnas disponibles: {len(self.data.columns)}

🔍 Datos Filtrados:
   - Estrategias que cumplen criterios: {len(self.filtered_data)}
   - Porcentaje retenido: {(len(self.filtered_data) / len(self.data) * 100):.1f}%

📋 Filtros Activos:
   - Filtros numéricos: {sum(1 for v in self.range_vars.values() if v['enabled'].get())}
   - Filtros de categorías: {sum(1 for v in self.category_vars.values() if any(var.get() for var in v.values()))}
   - Búsqueda por texto: {'Sí' if hasattr(self, 'search_var') and self.search_var.get().strip() else 'No'}
   - Filtros combinados: {sum(1 for attr in ['elite_var', 'high_sharpe_var', 'low_dd_var', 'consistent_var'] if hasattr(self, attr) and getattr(self, attr).get())}
"""
            
            # Crear ventana de estadísticas
            stats_window = tk.Toplevel(self.popup)
            stats_window.title("📊 Estadísticas de Filtros")
            stats_window.geometry("500x400")
            
            text_widget = tk.Text(stats_window, wrap="word", padx=10, pady=10)
            text_widget.pack(fill="both", expand=True)
            text_widget.insert("1.0", stats_text)
            text_widget.config(state="disabled")
            
        except Exception as e:
            logger.error(f"Error mostrando estadísticas: {e}")
            messagebox.showerror("Error", f"Error mostrando estadísticas: {e}")
    
    def _add_custom_filter(self):
        """Agrega un filtro personalizado."""
        # TODO: Implementar filtros personalizados
        messagebox.showinfo("Filtros Personalizados", 
                          "Funcionalidad de filtros personalizados en desarrollo.")
    
    def get_filtered_data(self) -> pd.DataFrame:
        """Devuelve el DataFrame filtrado actual."""
        if not isinstance(self.filtered_data, pd.DataFrame):
            return pd.DataFrame(self.filtered_data)
        return self.filtered_data
    
    def apply_filters(self) -> pd.DataFrame:
        """
        Aplica los filtros configurados y retorna los datos filtrados.
        
        Returns:
            DataFrame con datos filtrados
        """
        try:
            self._apply_filters()
            logger.info("✅ Filtros aplicados correctamente")
            return self.filtered_data
        except Exception as e:
            logger.error(f"Error aplicando filtros: {e}")
            return self.data.copy()
    
    def set_filter_config(self, config: Dict[str, Any]) -> bool:
        """
        Establece la configuración de filtros.
        
        Args:
            config: Configuración de filtros
            
        Returns:
            True si se configuró correctamente
        """
        try:
            # Configurar filtros numéricos
            if 'numeric_filters' in config:
                for column, range_config in config['numeric_filters'].items():
                    if column in self.range_vars:
                        min_val = range_config.get('min', 0)
                        max_val = range_config.get('max', 100)
                        self.range_vars[column]['min'].set(min_val)
                        self.range_vars[column]['max'].set(max_val)
            
            # Configurar filtros de categorías
            if 'category_filters' in config:
                for column, values in config['category_filters'].items():
                    if column in self.category_vars:
                        for value, checked in values.items():
                            if value in self.category_vars[column]:
                                self.category_vars[column][value].set(checked)
            
            # Configurar búsqueda de texto
            if 'text_search' in config:
                search_config = config['text_search']
                if 'search_text' in search_config:
                    self.search_var.set(search_config['search_text'])
                if 'keywords' in search_config:
                    self.keywords_var.set(search_config['keywords'])
                if 'case_sensitive' in search_config:
                    self.case_sensitive_var.set(search_config['case_sensitive'])
                if 'exact_match' in search_config:
                    self.exact_match_var.set(search_config['exact_match'])
            
            logger.info("✅ Configuración de filtros establecida")
            return True
            
        except Exception as e:
            logger.error(f"Error configurando filtros: {e}")
            return False
    
    def reset_filters(self) -> bool:
        """
        Resetea todos los filtros a su estado inicial.
        
        Returns:
            True si se reseteó correctamente
        """
        try:
            self._clear_filters()
            logger.info("✅ Filtros reseteados correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error reseteando filtros: {e}")
            return False
    
    def get_filter_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración actual de filtros.
        
        Returns:
            Configuración actual de filtros
        """
        try:
            config = {
                'numeric_filters': {},
                'category_filters': {},
                'text_search': {},
                'combined_filters': {}
            }
            
            # Obtener filtros numéricos
            for column, vars_dict in self.range_vars.items():
                if vars_dict['enabled'].get():
                    config['numeric_filters'][column] = {
                        'min': vars_dict['min'].get(),
                        'max': vars_dict['max'].get(),
                        'enabled': True
                    }
            
            # Obtener filtros de categorías
            for column, category_vars in self.category_vars.items():
                selected_values = [value for value, var in category_vars.items() if var.get()]
                if selected_values:
                    config['category_filters'][column] = selected_values
            
            # Obtener filtros de búsqueda
            if hasattr(self, 'search_var'):
                config['text_search'] = {
                    'search_text': self.search_var.get(),
                    'keywords': self.keywords_var.get() if hasattr(self, 'keywords_var') else "",
                    'case_sensitive': self.case_sensitive_var.get() if hasattr(self, 'case_sensitive_var') else False,
                    'exact_match': self.exact_match_var.get() if hasattr(self, 'exact_match_var') else False
                }
            
            # Obtener filtros combinados
            if hasattr(self, 'elite_var'):
                config['combined_filters'] = {
                    'elite_only': self.elite_var.get(),
                    'high_sharpe': self.high_sharpe_var.get() if hasattr(self, 'high_sharpe_var') else False,
                    'low_drawdown': self.low_dd_var.get() if hasattr(self, 'low_dd_var') else False,
                    'consistent_performance': self.consistent_var.get() if hasattr(self, 'consistent_var') else False
                }
            
            logger.info("✅ Configuración de filtros obtenida")
            return config
            
        except Exception as e:
            logger.error(f"Error obteniendo configuración de filtros: {e}")
            return {}
    
    def show(self):
        """Muestra el popup."""
        self.popup.wait_window()
        return self.filtered_data

def create_advanced_filters_popup(parent: tk.Tk, data: pd.DataFrame, 
                                 on_filter_changed: Optional[Callable] = None) -> AdvancedFiltersPopup:
    """
    Crea y muestra un popup de filtros avanzados.
    
    Args:
        parent: Ventana padre
        data: DataFrame con datos de estrategias
        on_filter_changed: Callback cuando cambian los filtros
        
    Returns:
        Instancia del popup de filtros avanzados
    """
    return AdvancedFiltersPopup(parent, data, on_filter_changed) 