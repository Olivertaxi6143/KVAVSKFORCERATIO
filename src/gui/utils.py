"""
GUI Utils - Utilidades para la interfaz gráfica

Este módulo contiene funciones auxiliares, constantes y clases de soporte
para la interfaz gráfica del sistema de análisis cuantitativo.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import os
from datetime import datetime

# Configurar logging
try:
    from core.logger_config import setup_logger
    logger = setup_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class TkinterLogHandler(logging.Handler):
    """Handler de logging para widgets Tkinter."""
    
    def __init__(self, text_widget: tk.Text):
        super().__init__()
        self.text_widget = text_widget
        
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()


class GUIAnalysisError(Exception):
    """Excepción personalizada para errores de la GUI."""
    pass


def validate_input(func):
    """Decorador para validar inputs en la GUI."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error en {func.__name__}: {e}")
            messagebox.showerror("Error", f"Error en {func.__name__}: {str(e)}")
            raise GUIAnalysisError(f"Error en {func.__name__}: {str(e)}")
    return wrapper


def log_execution_time(func):
    """Decorador para medir tiempo de ejecución."""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            logger.info(f"{func.__name__} ejecutado en {execution_time:.2f} segundos")
            return result
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            logger.error(f"{func.__name__} falló después de {execution_time:.2f} segundos: {e}")
            raise
    return wrapper


# Constantes de mapeo de columnas
QVA_COL_MAP = {
    'Strategy Name': 'Strategy_Name',
    'CAGR (IS)': 'CAGR_IS',
    'CAGR (OOS)': 'CAGR_OOS',
    'Drawdown (IS)': 'Drawdown_IS',
    'Drawdown (OOS)': 'Drawdown_OOS',
    'Sharpe Ratio (IS)': 'Sharpe_Ratio_IS',
    'Sharpe Ratio (OOS)': 'Sharpe_Ratio_OOS',
    'Profit factor (IS)': 'Profit_factor_IS',
    'Profit factor (OOS)': 'Profit_factor_OOS',
    'Winning Percent (IS)': 'Winning_Percent_IS',
    'Winning Percent (OOS)': 'Winning_Percent_OOS',
    'Net profit (IS)': 'Net_profit_IS',
    'Net profit (OOS)': 'Net_profit_OOS',
    'CalmarRatio (IS)': 'CalmarRatio_IS',
    'CalmarRatio (OOS)': 'CalmarRatio_OOS',
    'SQN Score (IS)': 'SQN_Score_IS',
    'SQN Score (OOS)': 'SQN_Score_OOS',
    'R Expectancy (IS)': 'R_Expectancy_IS',
    'R Expectancy (OOS)': 'R_Expectancy_OOS',
    'Winning Percent': 'Winning_Percent',
    'Max DD %': 'Max_DD_pct',
    'Avg. MAE - Profit/loss': 'Avg_MAE_Profit_loss',
    'Avg. MFE - Profit/loss': 'Avg_MFE_Profit_loss',
    'Max Consec. Losses': 'Max_Consec_Losses',
    'Payout ratio': 'Payout_ratio',
    'Ulcer Index %': 'Ulcer_Index_pct',
    'Ulcer Performance Index': 'Ulcer_Performance_Index',
    'Max Drawdown Duration': 'Max_Drawdown_Duration',
    'Avg. Bars in Trade': 'Avg_Bars_in_Trade',
    'VaR (95%)': 'VaR_95pct',
    'CVaR (95%)': 'CVaR_95pct',
    'Sortino Ratio': 'Sortino_Ratio',
    'RecoveryFactor': 'RecoveryFactor',
    'Stagnation (Trades)': 'Stagnation',
    'Max Stagnation Trades': 'Stagnation_Trades',
    'Stagnation_Trades': 'Stagnation_Trades',
    'New Peak Trades %': 'New_Peak_Trades_pct',
    'Drawdown Trades %': 'Drawdown_Trades_pct',
    'Date': 'Date',
    'Open': 'Open',
    'High': 'High',
    'Low': 'Low',
    'Close': 'Close',
    'Volume': 'Volume'
}

# Configuraciones por defecto
DEFAULT_CONFIG = {
    'csv_delimiter': ';',
    'csv_decimal': ',',
    'is_oos_ratio': 0.7,
    'required_columns': [
        'Net_Profit_IS', 'Net_Profit_OOS',
        'Sharpe_Ratio_IS', 'Sharpe_Ratio_OOS',
        'Max_Drawdown_IS', 'Max_Drawdown_OOS',
        'Profit_Factor_IS', 'Profit_Factor_OOS',
        'CAGR_IS', 'CAGR_OOS'
    ],
    'validation': {
        'strict_validation': True,
        'imputation_method': 'regime_based',
        'outlier_detection': 'isolation_forest',
        'outlier_threshold': 0.1
    }
}

# Colores para categorías
CATEGORY_COLORS = {
    'Elite': '#FFD700',      # Oro
    'Excellent': '#C0C0C0',  # Plata
    'Very Good': '#CD7F32',  # Bronce
    'Good': '#90EE90',       # Verde claro
    'Average': '#FFB6C1',    # Rosa claro
    'Poor': '#FF6347',       # Tomate
    'Very Poor': '#DC143C'   # Carmesí
}

# Estilos de widgets
WIDGET_STYLES = {
    'title_font': ('Arial', 12, 'bold'),
    'header_font': ('Arial', 10, 'bold'),
    'normal_font': ('Arial', 9),
    'button_bg': '#4CAF50',
    'button_fg': 'white',
    'error_bg': '#FF6B6B',
    'success_bg': '#4ECDC4'
}


def create_styled_button(parent, text, command, **kwargs):
    """Crea un botón con estilo consistente."""
    return ttk.Button(
        parent, 
        text=text, 
        command=command,
        style='Accent.TButton',
        **kwargs
    )


def create_styled_label(parent, text, **kwargs):
    """Crea una etiqueta con estilo consistente."""
    return ttk.Label(
        parent,
        text=text,
        font=WIDGET_STYLES['normal_font'],
        **kwargs
    )


def create_styled_entry(parent, **kwargs):
    """Crea un campo de entrada con estilo consistente."""
    return ttk.Entry(
        parent,
        font=WIDGET_STYLES['normal_font'],
        **kwargs
    )


def show_info_message(title, message):
    """Muestra un mensaje informativo."""
    messagebox.showinfo(title, message)


def show_error_message(title, message):
    """Muestra un mensaje de error."""
    messagebox.showerror(title, message)


def show_warning_message(title, message):
    """Muestra un mensaje de advertencia."""
    messagebox.showwarning(title, message)


def ask_yes_no_question(title, message):
    """Hace una pregunta sí/no."""
    return messagebox.askyesno(title, message)


def select_file(title="Seleccionar archivo", filetypes=None):
    """Abre diálogo para seleccionar archivo."""
    if filetypes is None:
        filetypes = [
            ("Archivos CSV", "*.csv"),
            ("Archivos Excel", "*.xlsx;*.xls"),
            ("Todos los archivos", "*.*")
        ]
    
    return filedialog.askopenfilename(
        title=title,
        filetypes=filetypes
    )


def select_directory(title="Seleccionar carpeta"):
    """Abre diálogo para seleccionar carpeta."""
    return filedialog.askdirectory(title=title)


def save_file(title="Guardar archivo", filetypes=None):
    """Abre diálogo para guardar archivo."""
    if filetypes is None:
        filetypes = [
            ("Archivos Excel", "*.xlsx"),
            ("Archivos CSV", "*.csv"),
            ("Archivos JSON", "*.json"),
            ("Todos los archivos", "*.*")
        ]
    
    return filedialog.asksaveasfilename(
        title=title,
        filetypes=filetypes
    )


def validate_dataframe(df: pd.DataFrame, required_columns: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
    """Valida un DataFrame para uso en la GUI."""
    errors = []
    
    if df is None or df.empty:
        errors.append("DataFrame está vacío o es None")
        return False, errors
    
    if required_columns:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Columnas faltantes: {missing_columns}")
    
    # Verificar que hay columnas numéricas
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_columns) < 3:
        errors.append("Insuficientes columnas numéricas para análisis")
    
    return len(errors) == 0, errors


def load_data_with_datamanager(file_path: str, data_manager=None):
    """Carga datos usando el DataManager."""
    try:
        if data_manager is None:
            from data.data_manager import DataManager
            data_manager = DataManager()
        
        # Cargar datos según el tipo de archivo
        if file_path.endswith('.csv'):
            df = data_manager.load_and_prepare_data_pipeline(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Formato de archivo no soportado: {file_path}")
        
        # Validar datos
        is_valid, errors = validate_dataframe(df)
        if not is_valid:
            raise GUIAnalysisError(f"Error validando datos: {'; '.join(errors)}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        raise GUIAnalysisError(f"Error cargando datos: {str(e)}")


def format_number(value, decimals=2):
    """Formatea un número para mostrar en la GUI."""
    if pd.isna(value) or value is None:
        return "N/A"
    
    try:
        if isinstance(value, (int, float)):
            return f"{value:.{decimals}f}"
        else:
            return str(value)
    except:
        return str(value)


def format_percentage(value, decimals=1):
    """Formatea un porcentaje para mostrar en la GUI."""
    if pd.isna(value) or value is None:
        return "N/A"
    
    try:
        if isinstance(value, (int, float)):
            return f"{value:.{decimals}f}%"
        else:
            return str(value)
    except:
        return str(value)


def create_progress_bar(parent, **kwargs):
    """Crea una barra de progreso con estilo."""
    return ttk.Progressbar(
        parent,
        mode='determinate',
        **kwargs
    )


def update_progress_bar(progress_bar, value, maximum=100):
    """Actualiza una barra de progreso."""
    progress_bar['value'] = value
    progress_bar['maximum'] = maximum
    progress_bar.update_idletasks()


def create_treeview(parent, columns, **kwargs):
    """Crea un Treeview con columnas predefinidas."""
    tree = ttk.Treeview(parent, columns=columns, show='headings', **kwargs)
    
    # Configurar columnas
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, minwidth=50)
    
    return tree


def populate_treeview(tree, data, key_column=None):
    """Puebla un Treeview con datos."""
    # Limpiar datos existentes
    for item in tree.get_children():
        tree.delete(item)
    
    # Insertar nuevos datos
    for index, row in data.iterrows():
        values = [row.get(col, '') for col in tree['columns']]
        item_id = row.get(key_column, index) if key_column else index
        tree.insert('', 'end', iid=item_id, values=values)


def create_scrolled_frame(parent):
    """Crea un frame con scroll."""
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    return scrollable_frame, canvas, scrollbar


def setup_logging_to_widget(text_widget):
    """Configura logging para un widget de texto."""
    handler = TkinterLogHandler(text_widget)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Agregar handler al logger raíz
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    return handler


def clear_log_widget(text_widget):
    """Limpia un widget de texto de log."""
    text_widget.delete(1.0, tk.END)


def export_results_to_excel(data, file_path, sheet_name="Resultados"):
    """Exporta resultados a Excel."""
    try:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)
        return True
    except Exception as e:
        logger.error(f"Error exportando a Excel: {e}")
        return False


def export_results_to_csv(data, file_path):
    """Exporta resultados a CSV."""
    try:
        data.to_csv(file_path, index=False, sep=';', decimal=',')
        return True
    except Exception as e:
        logger.error(f"Error exportando a CSV: {e}")
        return False


def create_tooltip(widget, text):
    """Crea un tooltip para un widget."""
    def show_tooltip(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(tooltip, text=text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        label.pack()
        
        def hide_tooltip():
            tooltip.destroy()
        
        widget.tooltip = tooltip
        widget.bind('<Leave>', lambda e: hide_tooltip())
        tooltip.bind('<Leave>', lambda e: hide_tooltip())
    
    widget.bind('<Enter>', show_tooltip)


def create_help_button(parent, help_text, **kwargs):
    """Crea un botón de ayuda con tooltip."""
    help_button = ttk.Button(parent, text="?", width=3, **kwargs)
    create_tooltip(help_button, help_text)
    return help_button


def create_status_bar(parent):
    """Crea una barra de estado."""
    status_frame = ttk.Frame(parent)
    status_label = ttk.Label(status_frame, text="Listo", relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    return status_frame, status_label


def update_status(status_label, message):
    """Actualiza el mensaje de la barra de estado."""
    status_label.config(text=message)
    status_label.update_idletasks()


def create_menu_bar(parent):
    """Crea una barra de menú básica."""
    menubar = tk.Menu(parent)
    parent.config(menu=menubar)
    
    # Menú Archivo
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Archivo", menu=file_menu)
    file_menu.add_command(label="Cargar Datos", command=lambda: None)
    file_menu.add_command(label="Guardar Resultados", command=lambda: None)
    file_menu.add_separator()
    file_menu.add_command(label="Salir", command=parent.quit)
    
    # Menú Ayuda
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Ayuda", menu=help_menu)
    help_menu.add_command(label="Acerca de", command=lambda: None)
    
    return menubar


def center_window(window, width=None, height=None):
    """Centra una ventana en la pantalla."""
    window.update_idletasks()
    
    if width is None:
        width = window.winfo_reqwidth()
    if height is None:
        height = window.winfo_reqheight()
    
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    
    window.geometry(f'{width}x{height}+{x}+{y}')


def create_loading_dialog(parent, title="Cargando..."):
    """Crea un diálogo de carga."""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    
    # Centrar diálogo
    dialog.geometry("300x100")
    center_window(dialog, 300, 100)
    
    # Contenido
    label = ttk.Label(dialog, text="Procesando datos...", font=WIDGET_STYLES['normal_font'])
    label.pack(pady=20)
    
    progress = ttk.Progressbar(dialog, mode='indeterminate')
    progress.pack(pady=10, padx=20, fill=tk.X)
    progress.start()
    
    return dialog, progress


def close_loading_dialog(dialog, progress):
    """Cierra un diálogo de carga."""
    progress.stop()
    dialog.destroy()


def create_error_dialog(parent, title, message):
    """Crea un diálogo de error."""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    
    # Centrar diálogo
    dialog.geometry("400x200")
    center_window(dialog, 400, 200)
    
    # Contenido
    label = ttk.Label(dialog, text=message, wraplength=350, font=WIDGET_STYLES['normal_font'])
    label.pack(pady=20)
    
    button = ttk.Button(dialog, text="Aceptar", command=dialog.destroy)
    button.pack(pady=10)
    
    return dialog


def create_confirm_dialog(parent, title, message):
    """Crea un diálogo de confirmación."""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    
    # Centrar diálogo
    dialog.geometry("400x200")
    center_window(dialog, 400, 200)
    
    # Contenido
    label = ttk.Label(dialog, text=message, wraplength=350, font=WIDGET_STYLES['normal_font'])
    label.pack(pady=20)
    
    # Botones
    button_frame = ttk.Frame(dialog)
    button_frame.pack(pady=10)
    
    result = {'confirmed': False}
    
    def on_confirm():
        result['confirmed'] = True
        dialog.destroy()
    
    def on_cancel():
        dialog.destroy()
    
    ttk.Button(button_frame, text="Confirmar", command=on_confirm).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Cancelar", command=on_cancel).pack(side=tk.LEFT, padx=5)
    
    return dialog, result


def create_info_dialog(parent, title, message):
    """Crea un diálogo informativo."""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    
    # Centrar diálogo
    dialog.geometry("400x200")
    center_window(dialog, 400, 200)
    
    # Contenido
    label = ttk.Label(dialog, text=message, wraplength=350, font=WIDGET_STYLES['normal_font'])
    label.pack(pady=20)
    
    button = ttk.Button(dialog, text="Aceptar", command=dialog.destroy)
    button.pack(pady=10)
    
    return dialog


def create_wizard_navigation(parent, current_step, total_steps, on_previous=None, on_next=None):
    """Crea navegación de wizard."""
    nav_frame = ttk.Frame(parent)
    
    # Información de progreso
    progress_label = ttk.Label(nav_frame, text=f"Paso {current_step} de {total_steps}")
    progress_label.pack(side=tk.LEFT, padx=10)
    
    # Barra de progreso
    progress_bar = ttk.Progressbar(nav_frame, mode='determinate', length=200)
    progress_bar['value'] = (current_step / total_steps) * 100
    progress_bar.pack(side=tk.LEFT, padx=10)
    
    # Botones de navegación
    button_frame = ttk.Frame(nav_frame)
    button_frame.pack(side=tk.RIGHT, padx=10)
    
    if current_step > 1 and on_previous:
        prev_button = ttk.Button(button_frame, text="← Anterior", command=on_previous)
        prev_button.pack(side=tk.LEFT, padx=5)
    
    if current_step < total_steps and on_next:
        next_button = ttk.Button(button_frame, text="Siguiente →", command=on_next)
        next_button.pack(side=tk.LEFT, padx=5)
    
    return nav_frame, progress_bar, progress_label


def create_filter_panel(parent, filters, on_filter_change=None):
    """Crea un panel de filtros."""
    filter_frame = ttk.LabelFrame(parent, text="Filtros")
    
    filter_vars = {}
    
    for filter_name, filter_config in filters.items():
        row_frame = ttk.Frame(filter_frame)
        row_frame.pack(fill=tk.X, padx=5, pady=2)
        
        label = ttk.Label(row_frame, text=filter_config['label'])
        label.pack(side=tk.LEFT)
        
        if filter_config['type'] == 'range':
            min_var = tk.DoubleVar(value=filter_config.get('min', 0))
            max_var = tk.DoubleVar(value=filter_config.get('max', 100))
            
            min_entry = ttk.Entry(row_frame, textvariable=min_var, width=10)
            min_entry.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(row_frame, text="a").pack(side=tk.LEFT)
            
            max_entry = ttk.Entry(row_frame, textvariable=max_var, width=10)
            max_entry.pack(side=tk.LEFT, padx=5)
            
            filter_vars[filter_name] = {'min': min_var, 'max': max_var}
            
        elif filter_config['type'] == 'combo':
            var = tk.StringVar(value=filter_config.get('default', ''))
            combo = ttk.Combobox(row_frame, textvariable=var, values=filter_config['options'])
            combo.pack(side=tk.LEFT, padx=5)
            filter_vars[filter_name] = var
    
    # Botón aplicar filtros
    if on_filter_change:
        apply_button = ttk.Button(filter_frame, text="Aplicar Filtros", 
                                command=lambda: on_filter_change(filter_vars))
        apply_button.pack(pady=5)
    
    return filter_frame, filter_vars


def create_results_table(parent, columns, data=None):
    """Crea una tabla de resultados."""
    # Frame para la tabla
    table_frame = ttk.Frame(parent)
    
    # Crear Treeview
    tree = create_treeview(table_frame, columns)
    
    # Scrollbars
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    # Layout
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    
    # Poblar datos si se proporcionan
    if data is not None:
        populate_treeview(tree, data)
    
    return table_frame, tree


def create_chart_frame(parent):
    """Crea un frame para gráficos."""
    chart_frame = ttk.LabelFrame(parent, text="Gráficos")
    
    # Aquí se pueden agregar widgets para gráficos (matplotlib, plotly, etc.)
    # Por ahora es un placeholder
    
    return chart_frame


def create_summary_panel(parent):
    """Crea un panel de resumen."""
    summary_frame = ttk.LabelFrame(parent, text="Resumen")
    
    # Variables para el resumen
    summary_vars = {
        'total_strategies': tk.StringVar(value="0"),
        'elite_count': tk.StringVar(value="0"),
        'excellent_count': tk.StringVar(value="0"),
        'very_good_count': tk.StringVar(value="0"),
        'good_count': tk.StringVar(value="0"),
        'average_count': tk.StringVar(value="0"),
        'poor_count': tk.StringVar(value="0"),
        'very_poor_count': tk.StringVar(value="0")
    }
    
    # Crear etiquetas de resumen
    row = 0
    for label_text, var in summary_vars.items():
        label = ttk.Label(summary_frame, text=label_text.replace('_', ' ').title() + ":")
        label.grid(row=row, column=0, sticky="w", padx=5, pady=2)
        
        value_label = ttk.Label(summary_frame, textvariable=var, font=WIDGET_STYLES['header_font'])
        value_label.grid(row=row, column=1, sticky="w", padx=5, pady=2)
        
        row += 1
    
    return summary_frame, summary_vars


def update_summary_panel(summary_vars, data):
    """Actualiza el panel de resumen con nuevos datos."""
    if data is None or data.empty:
        return
    
    # Contar estrategias por categoría
    if 'Category' in data.columns:
        category_counts = data['Category'].value_counts()
        
        summary_vars['total_strategies'].set(str(len(data)))
        summary_vars['elite_count'].set(str(category_counts.get('Elite', 0)))
        summary_vars['excellent_count'].set(str(category_counts.get('Excellent', 0)))
        summary_vars['very_good_count'].set(str(category_counts.get('Very Good', 0)))
        summary_vars['good_count'].set(str(category_counts.get('Good', 0)))
        summary_vars['average_count'].set(str(category_counts.get('Average', 0)))
        summary_vars['poor_count'].set(str(category_counts.get('Poor', 0)))
        summary_vars['very_poor_count'].set(str(category_counts.get('Very Poor', 0)))


def create_export_panel(parent, on_export_excel=None, on_export_csv=None, on_export_json=None):
    """Crea un panel de exportación."""
    export_frame = ttk.LabelFrame(parent, text="Exportar Resultados")
    
    button_frame = ttk.Frame(export_frame)
    button_frame.pack(pady=10)
    
    if on_export_excel:
        excel_button = ttk.Button(button_frame, text="📊 Excel", command=on_export_excel)
        excel_button.pack(side=tk.LEFT, padx=5)
    
    if on_export_csv:
        csv_button = ttk.Button(button_frame, text="📄 CSV", command=on_export_csv)
        csv_button.pack(side=tk.LEFT, padx=5)
    
    if on_export_json:
        json_button = ttk.Button(button_frame, text="📋 JSON", command=on_export_json)
        json_button.pack(side=tk.LEFT, padx=5)
    
    return export_frame


def create_help_panel(parent):
    """Crea un panel de ayuda."""
    help_frame = ttk.LabelFrame(parent, text="Ayuda")
    
    help_text = """
    Guía de Uso:
    
    1. Cargar Datos: Selecciona archivos CSV o Excel con datos de estrategias
    2. Configurar Análisis: Ajusta parámetros y KPIs para el análisis
    3. Ejecutar Análisis: Procesa los datos y genera resultados
    4. Resultados: Visualiza y filtra los resultados del análisis
    5. Asesor: Obtén recomendaciones inteligentes sobre las estrategias
    6. Exportar: Guarda los resultados en diferentes formatos
    
    Para más información, consulta la documentación del proyecto.
    """
    
    text_widget = tk.Text(help_frame, wrap=tk.WORD, height=15, width=60)
    text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    text_widget.insert(tk.END, help_text)
    text_widget.config(state=tk.DISABLED)
    
    return help_frame


def create_about_dialog(parent):
    """Crea un diálogo 'Acerca de'."""
    dialog = tk.Toplevel(parent)
    dialog.title("Acerca de")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Centrar diálogo
    dialog.geometry("400x300")
    center_window(dialog, 400, 300)
    
    # Contenido
    title_label = ttk.Label(dialog, text="QVA Strategy Studio", font=WIDGET_STYLES['title_font'])
    title_label.pack(pady=20)
    
    version_label = ttk.Label(dialog, text="Versión 2.1", font=WIDGET_STYLES['normal_font'])
    version_label.pack(pady=5)
    
    description = """
    Sistema de análisis cuantitativo para estrategias de trading.
    
    Características:
    • Análisis Factor K Elite 9.6
    • Validación temporal avanzada
    • Asesor financiero inteligente
    • Exportación de resultados
    
    Desarrollado con Python y Tkinter.
    """
    
    desc_label = ttk.Label(dialog, text=description, justify=tk.CENTER, wraplength=350)
    desc_label.pack(pady=20)
    
    button = ttk.Button(dialog, text="Aceptar", command=dialog.destroy)
    button.pack(pady=10)
    
    return dialog


# Función para inicializar estilos de widgets
def setup_widget_styles():
    """Configura estilos personalizados para widgets."""
    style = ttk.Style()
    
    # Configurar estilo para botones de acento
    style.configure('Accent.TButton',
                   background=WIDGET_STYLES['button_bg'],
                   foreground=WIDGET_STYLES['button_fg'])
    
    # Configurar estilo para etiquetas de título
    style.configure('Title.TLabel',
                   font=WIDGET_STYLES['title_font'])
    
    # Configurar estilo para etiquetas de encabezado
    style.configure('Header.TLabel',
                   font=WIDGET_STYLES['header_font'])
    
    # Configurar estilo para frames de grupo
    style.configure('Group.TLabelframe',
                   font=WIDGET_STYLES['header_font'])


# Inicializar estilos al importar el módulo
setup_widget_styles() 