"""
Interactive Charts Module
Módulo de gráficos interactivos para análisis científico con Plotly embebido
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
import json
from pathlib import Path

# Lazy loading de Plotly
try:
    from src.core.utils.lazy_loader import lazy_loader
    plotly = lazy_loader.get_module('plotly')
    go = lazy_loader.get_module('plotly.graph_objects')
    px = lazy_loader.get_module('plotly.express')
    make_subplots = lazy_loader.get_module('plotly.subplots').make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    plotly = None
    go = None
    px = None
    make_subplots = None

logger = logging.getLogger(__name__)

class InteractiveChartManager:
    """
    Gestor de gráficos interactivos para análisis científico.
    
    Características:
    - Gráficos interactivos con Plotly
    - Múltiples tipos de visualización
    - Exportación de gráficos
    - Filtros dinámicos
    - Análisis estadístico integrado
    """
    
    def __init__(self, parent: tk.Tk):
        """
        Inicializa el gestor de gráficos interactivos.
        
        Args:
            parent: Ventana padre
        """
        self.parent = parent
        self.current_data = None
        self.chart_widgets = {}
        self.chart_configs = {}
        
        if not PLOTLY_AVAILABLE:
            logger.warning("⚠️ Plotly no disponible, gráficos interactivos deshabilitados")
        
        logger.info("✅ InteractiveChartManager inicializado")
    
    def create_correlation_matrix_chart(self, data: pd.DataFrame, title: str = "Matriz de Correlación") -> Dict[str, Any]:
        """
        Crea gráfico de matriz de correlación interactiva.
        
        Args:
            data: DataFrame con datos numéricos
            title: Título del gráfico
            
        Returns:
            Configuración del gráfico
        """
        try:
            if not PLOTLY_AVAILABLE:
                return {"error": "Plotly no disponible"}
            
            # Seleccionar columnas numéricas
            numeric_data = data.select_dtypes(include=[np.number])
            
            if len(numeric_data.columns) < 2:
                return {"error": "Se necesitan al menos 2 columnas numéricas"}
            
            # Calcular correlación
            corr_matrix = numeric_data.corr()
            
            # Crear heatmap
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.round(2).values,
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title=title,
                width=600,
                height=500,
                xaxis_title="Variables",
                yaxis_title="Variables"
            )
            
            return {
                "type": "correlation_matrix",
                "figure": fig,
                "data": corr_matrix.to_dict(),
                "title": title
            }
            
        except Exception as e:
            logger.error(f"Error creando matriz de correlación: {e}")
            return {"error": str(e)}
    
    def create_scatter_plot(self, data: pd.DataFrame, x_col: str, y_col: str, 
                           color_col: Optional[str] = None, size_col: Optional[str] = None,
                           title: str = "Gráfico de Dispersión") -> Dict[str, Any]:
        """
        Crea gráfico de dispersión interactivo.
        
        Args:
            data: DataFrame con datos
            x_col: Columna para eje X
            y_col: Columna para eje Y
            color_col: Columna para color (opcional)
            size_col: Columna para tamaño (opcional)
            title: Título del gráfico
            
        Returns:
            Configuración del gráfico
        """
        try:
            if not PLOTLY_AVAILABLE:
                return {"error": "Plotly no disponible"}
            
            if x_col not in data.columns or y_col not in data.columns:
                return {"error": f"Columnas {x_col} o {y_col} no encontradas"}
            
            # Crear gráfico de dispersión
            fig = px.scatter(
                data,
                x=x_col,
                y=y_col,
                color=color_col,
                size=size_col,
                title=title,
                hover_data=data.columns.tolist()[:5]  # Mostrar primeras 5 columnas en hover
            )
            
            fig.update_layout(
                width=700,
                height=500,
                showlegend=True
            )
            
            return {
                "type": "scatter_plot",
                "figure": fig,
                "x_column": x_col,
                "y_column": y_col,
                "color_column": color_col,
                "size_column": size_col,
                "title": title
            }
            
        except Exception as e:
            logger.error(f"Error creando gráfico de dispersión: {e}")
            return {"error": str(e)}
    
    def create_histogram_chart(self, data: pd.DataFrame, column: str, 
                              bins: int = 30, title: str = "Histograma") -> Dict[str, Any]:
        """
        Crea histograma interactivo.
        
        Args:
            data: DataFrame con datos
            column: Columna para el histograma
            bins: Número de bins
            title: Título del gráfico
            
        Returns:
            Configuración del gráfico
        """
        try:
            if not PLOTLY_AVAILABLE:
                return {"error": "Plotly no disponible"}
            
            if column not in data.columns:
                return {"error": f"Columna {column} no encontrada"}
            
            # Crear histograma
            fig = px.histogram(
                data,
                x=column,
                nbins=bins,
                title=title,
                marginal="box"  # Agregar box plot marginal
            )
            
            fig.update_layout(
                width=600,
                height=400,
                showlegend=False
            )
            
            # Agregar estadísticas
            col_data = pd.to_numeric(data[column], errors='coerce').dropna()
            if len(col_data) > 0:
                mean_val = col_data.mean()
                std_val = col_data.std()
                median_val = col_data.median()
                
                fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                             annotation_text=f"Media: {mean_val:.2f}")
                fig.add_vline(x=median_val, line_dash="dash", line_color="green", 
                             annotation_text=f"Mediana: {median_val:.2f}")
            
            return {
                "type": "histogram",
                "figure": fig,
                "column": column,
                "bins": bins,
                "title": title,
                "statistics": {
                    "mean": mean_val if len(col_data) > 0 else None,
                    "std": std_val if len(col_data) > 0 else None,
                    "median": median_val if len(col_data) > 0 else None,
                    "count": len(col_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Error creando histograma: {e}")
            return {"error": str(e)}
    
    def create_box_plot(self, data: pd.DataFrame, column: str, 
                       group_by: Optional[str] = None, title: str = "Box Plot") -> Dict[str, Any]:
        """
        Crea box plot interactivo.
        
        Args:
            data: DataFrame con datos
            column: Columna para el box plot
            group_by: Columna para agrupar (opcional)
            title: Título del gráfico
            
        Returns:
            Configuración del gráfico
        """
        try:
            if not PLOTLY_AVAILABLE:
                return {"error": "Plotly no disponible"}
            
            if column not in data.columns:
                return {"error": f"Columna {column} no encontrada"}
            
            # Crear box plot
            if group_by and group_by in data.columns:
                fig = px.box(data, x=group_by, y=column, title=title)
            else:
                fig = px.box(data, y=column, title=title)
            
            fig.update_layout(
                width=600,
                height=400,
                showlegend=False
            )
            
            return {
                "type": "box_plot",
                "figure": fig,
                "column": column,
                "group_by": group_by,
                "title": title
            }
            
        except Exception as e:
            logger.error(f"Error creando box plot: {e}")
            return {"error": str(e)}
    
    def create_time_series_chart(self, data: pd.DataFrame, date_column: str, value_column: str,
                                group_by: Optional[str] = None, title: str = "Serie Temporal") -> Dict[str, Any]:
        """
        Crea gráfico de serie temporal interactivo.
        
        Args:
            data: DataFrame con datos
            date_column: Columna con fechas
            value_column: Columna con valores
            group_by: Columna para agrupar (opcional)
            title: Título del gráfico
            
        Returns:
            Configuración del gráfico
        """
        try:
            if not PLOTLY_AVAILABLE:
                return {"error": "Plotly no disponible"}
            
            if date_column not in data.columns or value_column not in data.columns:
                return {"error": f"Columnas {date_column} o {value_column} no encontradas"}
            
            # Convertir columna de fecha
            data_copy = data.copy()
            data_copy[date_column] = pd.to_datetime(data_copy[date_column], errors='coerce')
            data_copy = data_copy.dropna(subset=[date_column])
            
            if len(data_copy) == 0:
                return {"error": "No hay datos válidos de fecha"}
            
            # Crear gráfico de línea
            if group_by and group_by in data_copy.columns:
                fig = px.line(data_copy, x=date_column, y=value_column, color=group_by, title=title)
            else:
                fig = px.line(data_copy, x=date_column, y=value_column, title=title)
            
            fig.update_layout(
                width=800,
                height=500,
                xaxis_title="Fecha",
                yaxis_title=value_column
            )
            
            return {
                "type": "time_series",
                "figure": fig,
                "date_column": date_column,
                "value_column": value_column,
                "group_by": group_by,
                "title": title
            }
            
        except Exception as e:
            logger.error(f"Error creando serie temporal: {e}")
            return {"error": str(e)}
    
    def create_3d_scatter_plot(self, data: pd.DataFrame, x_col: str, y_col: str, z_col: str,
                               color_col: Optional[str] = None, title: str = "Gráfico 3D") -> Dict[str, Any]:
        """
        Crea gráfico de dispersión 3D interactivo.
        
        Args:
            data: DataFrame con datos
            x_col: Columna para eje X
            y_col: Columna para eje Y
            z_col: Columna para eje Z
            color_col: Columna para color (opcional)
            title: Título del gráfico
            
        Returns:
            Configuración del gráfico
        """
        try:
            if not PLOTLY_AVAILABLE:
                return {"error": "Plotly no disponible"}
            
            required_cols = [x_col, y_col, z_col]
            if not all(col in data.columns for col in required_cols):
                return {"error": f"Columnas {x_col}, {y_col} o {z_col} no encontradas"}
            
            # Crear gráfico 3D
            fig = px.scatter_3d(
                data,
                x=x_col,
                y=y_col,
                z=z_col,
                color=color_col,
                title=title,
                hover_data=data.columns.tolist()[:3]
            )
            
            fig.update_layout(
                width=800,
                height=600,
                scene=dict(
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    zaxis_title=z_col
                )
            )
            
            return {
                "type": "3d_scatter",
                "figure": fig,
                "x_column": x_col,
                "y_column": y_col,
                "z_column": z_col,
                "color_column": color_col,
                "title": title
            }
            
        except Exception as e:
            logger.error(f"Error creando gráfico 3D: {e}")
            return {"error": str(e)}
    
    def export_chart_to_html(self, chart_config: Dict[str, Any], filename: str) -> bool:
        """
        Exporta gráfico a archivo HTML.
        
        Args:
            chart_config: Configuración del gráfico
            filename: Nombre del archivo
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if "figure" not in chart_config:
                logger.error("No hay figura para exportar")
                return False
            
            fig = chart_config["figure"]
            fig.write_html(filename)
            
            logger.info(f"✅ Gráfico exportado a {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando gráfico: {e}")
            return False
    
    def export_chart_to_image(self, chart_config: Dict[str, Any], filename: str, 
                             format: str = "png", width: int = 800, height: int = 600) -> bool:
        """
        Exporta gráfico a imagen.
        
        Args:
            chart_config: Configuración del gráfico
            filename: Nombre del archivo
            format: Formato de imagen (png, jpg, svg, pdf)
            width: Ancho de la imagen
            height: Alto de la imagen
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if "figure" not in chart_config:
                logger.error("No hay figura para exportar")
                return False
            
            fig = chart_config["figure"]
            fig.write_image(filename, width=width, height=height)
            
            logger.info(f"✅ Gráfico exportado a {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando gráfico: {e}")
            return False
    
    def create_chart_widget(self, parent: tk.Widget, chart_config: Dict[str, Any]) -> tk.Widget:
        """
        Crea widget para mostrar gráfico interactivo.
        
        Args:
            parent: Widget padre
            chart_config: Configuración del gráfico
            
        Returns:
            Widget con el gráfico
        """
        try:
            if "error" in chart_config:
                # Mostrar error
                error_frame = ttk.Frame(parent)
                ttk.Label(error_frame, text=f"Error: {chart_config['error']}", 
                         foreground="red").pack(pady=20)
                return error_frame
            
            if not PLOTLY_AVAILABLE:
                error_frame = ttk.Frame(parent)
                ttk.Label(error_frame, text="Plotly no disponible para gráficos interactivos", 
                         foreground="orange").pack(pady=20)
                return error_frame
            
            # Crear frame para el gráfico
            chart_frame = ttk.Frame(parent)
            
            # Título del gráfico
            if "title" in chart_config:
                title_label = ttk.Label(chart_frame, text=chart_config["title"], 
                                      font=("Arial", 12, "bold"))
                title_label.pack(pady=(0, 10))
            
            # Botones de exportación
            button_frame = ttk.Frame(chart_frame)
            button_frame.pack(fill="x", pady=(0, 10))
            
            ttk.Button(button_frame, text="📊 Exportar HTML", 
                      command=lambda: self._export_chart_html(chart_config)).pack(side="left", padx=5)
            ttk.Button(button_frame, text="🖼️ Exportar PNG", 
                      command=lambda: self._export_chart_png(chart_config)).pack(side="left", padx=5)
            ttk.Button(button_frame, text="📋 Copiar Datos", 
                      command=lambda: self._copy_chart_data(chart_config)).pack(side="left", padx=5)
            
            # Aquí se integraría el widget de Plotly
            # Por ahora, mostrar información del gráfico
            info_frame = ttk.Frame(chart_frame)
            info_frame.pack(fill="both", expand=True)
            
            info_text = f"""
Tipo de gráfico: {chart_config.get('type', 'Desconocido')}
Columnas utilizadas: {', '.join([k for k, v in chart_config.items() if k.endswith('_column') and v])}
Título: {chart_config.get('title', 'Sin título')}
"""
            
            text_widget = tk.Text(info_frame, wrap="word", height=10)
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)
            text_widget.insert("1.0", info_text)
            text_widget.config(state="disabled")
            
            return chart_frame
            
        except Exception as e:
            logger.error(f"Error creando widget de gráfico: {e}")
            error_frame = ttk.Frame(parent)
            ttk.Label(error_frame, text=f"Error creando gráfico: {e}", 
                     foreground="red").pack(pady=20)
            return error_frame
    
    def _export_chart_html(self, chart_config: Dict[str, Any]):
        """Exporta gráfico a HTML."""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
            )
            if filename:
                self.export_chart_to_html(chart_config, filename)
                messagebox.showinfo("Exportado", f"Gráfico exportado a {filename}")
        except Exception as e:
            logger.error(f"Error exportando a HTML: {e}")
            messagebox.showerror("Error", f"Error exportando gráfico: {e}")
    
    def _export_chart_png(self, chart_config: Dict[str, Any]):
        """Exporta gráfico a PNG."""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            if filename:
                self.export_chart_to_image(chart_config, filename, "png")
                messagebox.showinfo("Exportado", f"Gráfico exportado a {filename}")
        except Exception as e:
            logger.error(f"Error exportando a PNG: {e}")
            messagebox.showerror("Error", f"Error exportando gráfico: {e}")
    
    def _copy_chart_data(self, chart_config: Dict[str, Any]):
        """Copia datos del gráfico al portapapeles."""
        try:
            import json
            data_to_copy = {
                "type": chart_config.get("type"),
                "title": chart_config.get("title"),
                "columns": {k: v for k, v in chart_config.items() if k.endswith('_column') and v}
            }
            
            self.parent.clipboard_clear()
            self.parent.clipboard_append(json.dumps(data_to_copy, indent=2))
            
            messagebox.showinfo("Copiado", "Datos del gráfico copiados al portapapeles")
        except Exception as e:
            logger.error(f"Error copiando datos: {e}")
            messagebox.showerror("Error", f"Error copiando datos: {e}")

    def create_factor_k_chart(self, *args, **kwargs):
        logger.debug("Llamada a create_factor_k_chart (stub)")
    def create_sharpe_chart(self, *args, **kwargs):
        logger.debug("Llamada a create_sharpe_chart (stub)")
    def create_drawdown_chart(self, *args, **kwargs):
        logger.debug("Llamada a create_drawdown_chart (stub)")
    def create_performance_chart(self, *args, **kwargs):
        logger.debug("Llamada a create_performance_chart (stub)")
    def create_correlation_chart(self, *args, **kwargs):
        logger.debug("Llamada a create_correlation_chart (stub)")
    def update_data(self, *args, **kwargs):
        logger.debug("Llamada a update_data (stub)")
    def refresh_charts(self, *args, **kwargs):
        logger.debug("Llamada a refresh_charts (stub)")
    def set_data(self, *args, **kwargs):
        logger.debug("Llamada a set_data (stub)")
    
    def create_histogram(self, *args, **kwargs):
        """Alias para create_histogram_chart."""
        return self.create_histogram_chart(*args, **kwargs)

def create_interactive_chart_manager(parent: tk.Tk) -> InteractiveChartManager:
    """
    Crea un gestor de gráficos interactivos.
    
    Args:
        parent: Ventana padre
        
    Returns:
        Instancia del gestor de gráficos interactivos
    """
    return InteractiveChartManager(parent) 