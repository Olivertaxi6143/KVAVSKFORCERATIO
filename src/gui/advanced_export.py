"""
Advanced Export Module
Módulo de exportación avanzada con múltiples formatos y opciones de personalización
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import json
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

logger = logging.getLogger(__name__)

class AdvancedExportManager:
    """
    Gestor de exportación avanzada con múltiples formatos.
    
    Características:
    - Exportación a Excel con múltiples hojas
    - Exportación a CSV con opciones avanzadas
    - Exportación a JSON con estructura personalizada
    - Exportación a HTML con estilos
    - Exportación a PDF con gráficos
    - Filtros de exportación
    - Formateo automático
    """
    
    def __init__(self, parent: tk.Tk):
        """
        Inicializa el gestor de exportación avanzada.
        
        Args:
            parent: Ventana padre
        """
        self.parent = parent
        self.data = None
        self.export_config = {}
        
        logger.info("✅ AdvancedExportManager inicializado")
    
    def set_data(self, data: pd.DataFrame):
        """
        Establece los datos para exportación.
        
        Args:
            data: DataFrame con datos a exportar
        """
        self.data = data.copy()
        logger.info(f"✅ Datos establecidos para exportación: {len(data)} filas")
    
    def export_to_excel_advanced(self, filename: str, sheets_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exporta datos a Excel con múltiples hojas y formateo avanzado.
        
        Args:
            filename: Nombre del archivo
            sheets_config: Configuración de hojas (opcional)
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if self.data is None or len(self.data) == 0:
                logger.error("No hay datos para exportar")
                return False
            
            # Configuración por defecto
            if sheets_config is None:
                sheets_config = {
                    "ranking": {
                        "columns": ["Strategy_Name", "Factor_K", "CAGR_IS", "Sharpe_Ratio_IS", "Max_Drawdown_IS"],
                        "title": "Ranking de Estrategias",
                        "sort_by": "Factor_K",
                        "sort_ascending": False
                    },
                    "detailed_analysis": {
                        "columns": None,  # Todas las columnas
                        "title": "Análisis Detallado",
                        "sort_by": None
                    },
                    "summary_stats": {
                        "columns": ["Strategy_Name", "CAGR_IS", "Sharpe_Ratio_IS", "Max_Drawdown_IS", "Profit_Factor_IS"],
                        "title": "Estadísticas Resumidas",
                        "sort_by": "CAGR_IS",
                        "sort_ascending": False
                    }
                }
            
            # Crear workbook
            workbook = openpyxl.Workbook()
            
            # Eliminar hoja por defecto
            workbook.remove(workbook.active)
            
            # Crear hojas según configuración
            for sheet_name, config in sheets_config.items():
                self._create_excel_sheet(workbook, sheet_name, config)
            
            # Guardar archivo
            workbook.save(filename)
            logger.info(f"✅ Datos exportados a Excel: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando a Excel: {e}")
            return False
    
    def _create_excel_sheet(self, workbook: openpyxl.Workbook, sheet_name: str, config: Dict[str, Any]):
        """
        Crea una hoja de Excel con formateo.
        
        Args:
            workbook: Workbook de Excel
            sheet_name: Nombre de la hoja
            config: Configuración de la hoja
        """
        try:
            # Crear hoja
            worksheet = workbook.create_sheet(title=config.get("title", sheet_name))
            
            # Preparar datos
            data = self.data.copy()
            
            # Filtrar columnas si se especifica
            columns = config.get("columns")
            if columns:
                available_columns = [col for col in columns if col in data.columns]
                data = data[available_columns]
            
            # Ordenar datos si se especifica
            sort_by = config.get("sort_by")
            if sort_by and sort_by in data.columns:
                ascending = config.get("sort_ascending", True)
                data = data.sort_values(sort_by, ascending=ascending)
            
            # Escribir datos
            for r in dataframe_to_rows(data, index=False, header=True):
                worksheet.append(r)
            
            # Formatear encabezados
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
            
            # Ajustar ancho de columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Agregar filtros
            worksheet.auto_filter.ref = worksheet.dimensions
            
        except Exception as e:
            logger.error(f"Error creando hoja Excel {sheet_name}: {e}")
    
    def export_to_csv_advanced(self, filename: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exporta datos a CSV con opciones avanzadas.
        
        Args:
            filename: Nombre del archivo
            config: Configuración de exportación (opcional)
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if self.data is None or len(self.data) == 0:
                logger.error("No hay datos para exportar")
                return False
            
            # Configuración por defecto
            if config is None:
                config = {
                    "columns": None,  # Todas las columnas
                    "index": False,
                    "encoding": "utf-8",
                    "separator": ",",
                    "decimal": ".",
                    "date_format": "%Y-%m-%d",
                    "float_format": "%.3f"
                }
            
            # Preparar datos
            data = self.data.copy()
            
            # Filtrar columnas si se especifica
            columns = config.get("columns")
            if columns:
                available_columns = [col for col in columns if col in data.columns]
                data = data[available_columns]
            
            # Ordenar datos si se especifica
            sort_by = config.get("sort_by")
            if sort_by and sort_by in data.columns:
                ascending = config.get("sort_ascending", True)
                data = data.sort_values(sort_by, ascending=ascending)
            
            # Exportar a CSV
            data.to_csv(
                filename,
                index=config.get("index", False),
                encoding=config.get("encoding", "utf-8"),
                sep=config.get("separator", ","),
                decimal=config.get("decimal", "."),
                float_format=config.get("float_format", "%.3f")
            )
            
            logger.info(f"✅ Datos exportados a CSV: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando a CSV: {e}")
            return False
    
    def export_to_json_advanced(self, filename: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exporta datos a JSON con estructura personalizada.
        
        Args:
            filename: Nombre del archivo
            config: Configuración de exportación (opcional)
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if self.data is None or len(self.data) == 0:
                logger.error("No hay datos para exportar")
                return False
            
            # Configuración por defecto
            if config is None:
                config = {
                    "orient": "records",
                    "columns": None,
                    "include_index": False,
                    "date_format": "iso",
                    "indent": 2,
                    "sort_by": None,
                    "group_by": None
                }
            
            # Preparar datos
            data = self.data.copy()
            
            # Filtrar columnas si se especifica
            columns = config.get("columns")
            if columns:
                available_columns = [col for col in columns if col in data.columns]
                data = data[available_columns]
            
            # Ordenar datos si se especifica
            sort_by = config.get("sort_by")
            if sort_by and sort_by in data.columns:
                ascending = config.get("sort_ascending", True)
                data = data.sort_values(sort_by, ascending=ascending)
            
            # Agrupar datos si se especifica
            group_by = config.get("group_by")
            if group_by and group_by in data.columns:
                grouped_data = {}
                for name, group in data.groupby(group_by):
                    grouped_data[str(name)] = group.to_dict(config.get("orient", "records"))
                
                export_data = {
                    "metadata": {
                        "total_records": len(data),
                        "grouped_by": group_by,
                        "groups": list(grouped_data.keys())
                    },
                    "data": grouped_data
                }
            else:
                export_data = {
                    "metadata": {
                        "total_records": len(data),
                        "columns": list(data.columns)
                    },
                    "data": data.to_dict(config.get("orient", "records"))
                }
            
            # Exportar a JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=config.get("indent", 2), 
                         default=str, ensure_ascii=False)
            
            logger.info(f"✅ Datos exportados a JSON: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando a JSON: {e}")
            return False
    
    def export_to_html_advanced(self, filename: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exporta datos a HTML con estilos personalizados.
        
        Args:
            filename: Nombre del archivo
            config: Configuración de exportación (opcional)
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if self.data is None or len(self.data) == 0:
                logger.error("No hay datos para exportar")
                return False
            
            # Configuración por defecto
            if config is None:
                config = {
                    "columns": None,
                    "sort_by": "Factor_K",
                    "sort_ascending": False,
                    "include_styles": True,
                    "responsive": True,
                    "table_id": "strategies-table"
                }
            
            # Preparar datos
            data = self.data.copy()
            
            # Filtrar columnas si se especifica
            columns = config.get("columns")
            if columns:
                available_columns = [col for col in columns if col in data.columns]
                data = data[available_columns]
            
            # Ordenar datos si se especifica
            sort_by = config.get("sort_by")
            if sort_by and sort_by in data.columns:
                ascending = config.get("sort_ascending", True)
                data = data.sort_values(sort_by, ascending=ascending)
            
            # Generar HTML
            html_content = self._generate_html_content(data, config)
            
            # Guardar archivo
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ Datos exportados a HTML: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando a HTML: {e}")
            return False
    
    def _generate_html_content(self, data: pd.DataFrame, config: Dict[str, Any]) -> str:
        """
        Genera contenido HTML con estilos.
        
        Args:
            data: DataFrame con datos
            config: Configuración de exportación
            
        Returns:
            Contenido HTML
        """
        # CSS styles
        css_styles = """
        <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
        th { background-color: #366092; color: white; font-weight: bold; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        tr:hover { background-color: #ddd; }
        .factor-k-high { background-color: #d4edda !important; }
        .factor-k-medium { background-color: #fff3cd !important; }
        .factor-k-low { background-color: #f8d7da !important; }
        @media (max-width: 768px) {
            table { font-size: 12px; }
            th, td { padding: 4px; }
        }
        </style>
        """
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Análisis de Estrategias</title>
            {css_styles if config.get("include_styles", True) else ""}
        </head>
        <body>
            <div class="container">
                <h1>📊 Análisis de Estrategias</h1>
                <p>Total de estrategias: {len(data)}</p>
                <table id="{config.get('table_id', 'strategies-table')}">
                    <thead>
                        <tr>
                            {''.join(f'<th>{col}</th>' for col in data.columns)}
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Generar filas de datos
        for idx, row in data.iterrows():
            # Determinar clase CSS basada en Factor K
            css_class = ""
            if "Factor_K" in data.columns:
                factor_k = row.get("Factor_K", 0)
                if isinstance(factor_k, (int, float)):
                    if factor_k >= 9.2:
                        css_class = "factor-k-high"
                    elif factor_k >= 7.2:
                        css_class = "factor-k-medium"
                    else:
                        css_class = "factor-k-low"
            
            html_content += f'<tr class="{css_class}">'
            for col in data.columns:
                value = row[col]
                if isinstance(value, float):
                    formatted_value = f"{value:.3f}"
                else:
                    formatted_value = str(value)
                html_content += f'<td>{formatted_value}</td>'
            html_content += '</tr>'
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def create_export_dialog(self, parent: tk.Widget) -> tk.Widget:
        """
        Crea diálogo de exportación avanzada.
        
        Args:
            parent: Widget padre
            
        Returns:
            Widget del diálogo de exportación
        """
        try:
            # Frame principal
            dialog_frame = ttk.Frame(parent)
            
            # Título
            title_label = ttk.Label(dialog_frame, text="📤 Exportación Avanzada", 
                                   font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Frame para opciones
            options_frame = ttk.LabelFrame(dialog_frame, text="Opciones de Exportación")
            options_frame.pack(fill="x", padx=10, pady=5)
            
            # Formato de exportación
            format_frame = ttk.Frame(options_frame)
            format_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(format_frame, text="Formato:").pack(side="left")
            format_var = tk.StringVar(value="excel")
            format_combo = ttk.Combobox(format_frame, textvariable=format_var, 
                                       values=["Excel", "CSV", "JSON", "HTML"], state="readonly")
            format_combo.pack(side="left", padx=5)
            
            # Columnas a exportar
            columns_frame = ttk.Frame(options_frame)
            columns_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(columns_frame, text="Columnas:").pack(side="left")
            columns_var = tk.StringVar(value="all")
            columns_combo = ttk.Combobox(columns_frame, textvariable=columns_var, 
                                        values=["Todas", "Solo numéricas", "Personalizadas"], state="readonly")
            columns_combo.pack(side="left", padx=5)
            
            # Ordenamiento
            sort_frame = ttk.Frame(options_frame)
            sort_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(sort_frame, text="Ordenar por:").pack(side="left")
            sort_var = tk.StringVar(value="Factor_K")
            if self.data is not None:
                sort_combo = ttk.Combobox(sort_frame, textvariable=sort_var, 
                                         values=list(self.data.columns), state="readonly")
                sort_combo.pack(side="left", padx=5)
            
            # Opciones adicionales
            options_check_frame = ttk.Frame(options_frame)
            options_check_frame.pack(fill="x", padx=10, pady=5)
            
            include_index_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(options_check_frame, text="Incluir índice", 
                           variable=include_index_var).pack(side="left", padx=5)
            
            include_styles_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(options_check_frame, text="Incluir estilos (HTML)", 
                           variable=include_styles_var).pack(side="left", padx=5)
            
            # Botones de acción
            button_frame = ttk.Frame(dialog_frame)
            button_frame.pack(fill="x", pady=10)
            
            ttk.Button(button_frame, text="📁 Seleccionar Archivo", 
                      command=lambda: self._select_export_file(format_var.get())).pack(side="left", padx=5)
            ttk.Button(button_frame, text="📊 Vista Previa", 
                      command=lambda: self._preview_export()).pack(side="left", padx=5)
            ttk.Button(button_frame, text="❌ Cancelar", 
                      command=lambda: dialog_frame.destroy()).pack(side="right", padx=5)
            
            return dialog_frame
            
        except Exception as e:
            logger.error(f"Error creando diálogo de exportación: {e}")
            error_frame = ttk.Frame(parent)
            ttk.Label(error_frame, text=f"Error creando diálogo: {e}", 
                     foreground="red").pack(pady=20)
            return error_frame
    
    def _select_export_file(self, format_type: str):
        """Selecciona archivo para exportación."""
        try:
            filetypes = {
                "Excel": [("Excel files", "*.xlsx"), ("All files", "*.*")],
                "CSV": [("CSV files", "*.csv"), ("All files", "*.*")],
                "JSON": [("JSON files", "*.json"), ("All files", "*.*")],
                "HTML": [("HTML files", "*.html"), ("All files", "*.*")]
            }
            
            filename = filedialog.asksaveasfilename(
                title="Guardar archivo de exportación",
                filetypes=filetypes.get(format_type, [("All files", "*.*")]),
                defaultextension=filetypes.get(format_type, [("", "")])[0][1]
            )
            
            if filename:
                success = self._perform_export(filename, format_type)
                if success:
                    messagebox.showinfo("Exportación", f"Archivo exportado correctamente a {filename}")
                else:
                    messagebox.showerror("Error", "Error durante la exportación")
                    
        except Exception as e:
            logger.error(f"Error seleccionando archivo: {e}")
            messagebox.showerror("Error", f"Error seleccionando archivo: {e}")
    
    def _perform_export(self, filename: str, format_type: str) -> bool:
        """Realiza la exportación según el formato."""
        try:
            if format_type == "Excel":
                return self.export_to_excel_advanced(filename)
            elif format_type == "CSV":
                return self.export_to_csv_advanced(filename)
            elif format_type == "JSON":
                return self.export_to_json_advanced(filename)
            elif format_type == "HTML":
                return self.export_to_html_advanced(filename)
            else:
                logger.error(f"Formato no soportado: {format_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error realizando exportación: {e}")
            return False
    
    def _preview_export(self):
        """Muestra vista previa de la exportación."""
        try:
            if self.data is None:
                messagebox.showwarning("Vista Previa", "No hay datos para mostrar")
                return
            
            # Crear ventana de vista previa
            preview_window = tk.Toplevel(self.parent)
            preview_window.title("Vista Previa de Exportación")
            preview_window.geometry("800x600")
            
            # Mostrar datos
            preview_frame = ttk.Frame(preview_window)
            preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Crear Treeview
            columns = list(self.data.columns)
            tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=20)
            
            # Configurar columnas
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            # Insertar datos (limitado a 100 filas para vista previa)
            for idx, row in self.data.head(100).iterrows():
                values = [str(row[col]) for col in columns]
                tree.insert("", "end", values=values)
            
            tree.pack(fill="both", expand=True)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scrollbar.set)
            
        except Exception as e:
            logger.error(f"Error mostrando vista previa: {e}")
            messagebox.showerror("Error", f"Error mostrando vista previa: {e}")
    
    def export_to_excel(self, filename: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exporta datos a Excel con configuración básica.
        
        Args:
            filename: Nombre del archivo
            config: Configuración de exportación (opcional)
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if self.data is None or len(self.data) == 0:
                logger.error("No hay datos para exportar")
                return False
            
            # Configuración por defecto
            if config is None:
                config = {
                    "sheets": {
                        "ranking": {
                            "columns": ["Strategy_Name", "Factor_K", "CAGR_IS", "Sharpe_Ratio_IS", "Max_Drawdown_IS"],
                            "title": "Ranking de Estrategias"
                        }
                    }
                }
            
            return self.export_to_excel_advanced(filename, config.get("sheets"))
            
        except Exception as e:
            logger.error(f"Error exportando a Excel: {e}")
            return False
    
    def set_export_config(self, config: Dict[str, Any]) -> bool:
        """
        Establece la configuración de exportación.
        
        Args:
            config: Configuración de exportación
            
        Returns:
            True si se configuró correctamente
        """
        try:
            self.export_config = config.copy()
            logger.info("✅ Configuración de exportación establecida")
            return True
            
        except Exception as e:
            logger.error(f"Error configurando exportación: {e}")
            return False
    
    def configure_export(self, export_type: str, options: Dict[str, Any]) -> bool:
        """
        Configura opciones específicas de exportación.
        
        Args:
            export_type: Tipo de exportación (excel, csv, json, html)
            options: Opciones de configuración
            
        Returns:
            True si se configuró correctamente
        """
        try:
            if export_type not in self.export_config:
                self.export_config[export_type] = {}
            
            self.export_config[export_type].update(options)
            logger.info(f"✅ Configuración de exportación {export_type} actualizada")
            return True
            
        except Exception as e:
            logger.error(f"Error configurando exportación {export_type}: {e}")
            return False
    
    def export_to_csv(self, filename: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exporta datos a CSV.
        
        Args:
            filename: Nombre del archivo
            config: Configuración de exportación (opcional)
            
        Returns:
            True si se exportó correctamente
        """
        return self.export_to_csv_advanced(filename, config)
    
    def export_to_html(self, filename: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exporta datos a HTML.
        
        Args:
            filename: Nombre del archivo
            config: Configuración de exportación (opcional)
            
        Returns:
            True si se exportó correctamente
        """
        return self.export_to_html_advanced(filename, config)
    
    def export_to_pdf(self, filename: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exporta datos a PDF.
        
        Args:
            filename: Nombre del archivo
            config: Configuración de exportación (opcional)
            
        Returns:
            True si se exportó correctamente
        """
        try:
            # TODO: Implementar exportación a PDF
            logger.warning("Exportación a PDF no implementada aún")
            return False
            
        except Exception as e:
            logger.error(f"Error exportando a PDF: {e}")
            return False
    
    def export_charts(self, filename: str, chart_type: str = "all") -> bool:
        """
        Exporta gráficos generados.
        
        Args:
            filename: Nombre del archivo
            chart_type: Tipo de gráfico a exportar
            
        Returns:
            True si se exportó correctamente
        """
        try:
            # TODO: Implementar exportación de gráficos
            logger.warning("Exportación de gráficos no implementada aún")
            return False
            
        except Exception as e:
            logger.error(f"Error exportando gráficos: {e}")
            return False
    
    def export_comparison(self, filename: str, comparison_data: Dict[str, Any]) -> bool:
        """
        Exporta datos de comparación.
        
        Args:
            filename: Nombre del archivo
            comparison_data: Datos de comparación
            
        Returns:
            True si se exportó correctamente
        """
        try:
            # Crear DataFrame con datos de comparación
            import pandas as pd
            df = pd.DataFrame(comparison_data.get("data", []))
            df.to_excel(filename, index=False)
            
            logger.info(f"✅ Comparación exportada a {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando comparación: {e}")
            return False

def create_advanced_export_manager(parent: tk.Tk) -> AdvancedExportManager:
    """
    Crea un gestor de exportación avanzada.
    
    Args:
        parent: Ventana padre
        
    Returns:
        Instancia del gestor de exportación avanzada
    """
    return AdvancedExportManager(parent) 