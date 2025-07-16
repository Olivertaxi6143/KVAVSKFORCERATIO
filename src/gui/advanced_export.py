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
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import BarChart, LineChart, ScatterChart, Reference
from openpyxl.chart.series import DataPoint
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
import webbrowser
import os
import time
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Para evitar problemas con GUI
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from PIL import Image as PILImage

logger = logging.getLogger(__name__)

class AdvancedExportManager:
    """
    Gestor de exportación avanzada con múltiples formatos.
    
    Características:
    - Exportación a Excel con múltiples hojas y gráficos
    - Dashboard HTML interactivo con Plotly
    - Reportes PDF profesionales
    - Exportación por lotes y selección de columnas
    - Filtros de exportación avanzados
    - Formateo automático y personalizable
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
        self.charts_data = {}
        
        logger.info("✅ AdvancedExportManager inicializado")
    
    def set_data(self, data: pd.DataFrame):
        """
        Establece los datos para exportación.
        
        Args:
            data: DataFrame con datos a exportar
        """
        self.data = data.copy()
        logger.info(f"✅ Datos establecidos para exportación: {len(data)} filas")
    
    def set_charts_data(self, charts_data: Dict[str, Any]):
        """
        Establece datos de gráficos para exportación.
        
        Args:
            charts_data: Diccionario con datos de gráficos
        """
        self.charts_data = charts_data
        logger.info(f"✅ Datos de gráficos establecidos: {len(charts_data)} gráficos")
    
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
            
            # Configuración por defecto con 7 hojas según especificación
            if sheets_config is None:
                sheets_config = {
                    "ranking": {
                        "columns": ["Strategy_Name", "Factor_K", "Categoria", "CAGR_IS", "Sharpe_Ratio_IS", "Max_Drawdown_IS", "Trades_IS"],
                        "title": "Ranking de Estrategias",
                        "sort_by": "Factor_K",
                        "sort_ascending": False,
                        "add_chart": True
                    },
                    "por_regimen": {
                        "columns": ["Strategy_Name", "Factor_K", "Bull_Score", "Bear_Score", "Sideways_Score", "Crisis_Score"],
                        "title": "Análisis por Régimen de Mercado",
                        "sort_by": "Factor_K",
                        "sort_ascending": False,
                        "add_chart": True
                    },
                    "componentes_fk96": {
                        "columns": ["Strategy_Name", "Factor_K", "S_Score", "G_Score", "E_Score", "C_Score", "ML_Score", "T_Score", "P_Score"],
                        "title": "Componentes Factor K 9.6",
                        "sort_by": "Factor_K",
                        "sort_ascending": False,
                        "add_chart": True
                    },
                    "metricas_derivadas": {
                        "columns": ["Strategy_Name", "Calmar_Ratio", "Profit_Factor", "Recovery_Factor", "Risk_Reward_Ratio"],
                        "title": "Métricas Derivadas",
                        "sort_by": "Calmar_Ratio",
                        "sort_ascending": False,
                        "add_chart": True
                    },
                    "is_oos": {
                        "columns": ["Strategy_Name", "CAGR_IS", "CAGR_OOS", "Sharpe_IS", "Sharpe_OOS", "Drawdown_IS", "Drawdown_OOS"],
                        "title": "Análisis IS/OOS",
                        "sort_by": "CAGR_IS",
                        "sort_ascending": False,
                        "add_chart": True
                    },
                    "categorias": {
                        "columns": ["Strategy_Name", "Categoria", "Factor_K", "Predictibilidad", "Recomendacion"],
                        "title": "Categorización y Recomendaciones",
                        "sort_by": "Factor_K",
                        "sort_ascending": False,
                        "add_chart": True
                    },
                    "datos_completos": {
                        "columns": None,  # Todas las columnas
                        "title": "Datos Completos",
                        "sort_by": None,
                        "add_chart": False
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
        Crea una hoja de Excel con formateo avanzado y gráficos.
        
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
            self._format_excel_headers(worksheet)
            
            # Ajustar ancho de columnas
            self._adjust_excel_column_widths(worksheet)
            
            # Agregar filtros
            worksheet.auto_filter.ref = worksheet.dimensions
            
            # Agregar gráfico si se especifica
            if config.get("add_chart", False):
                self._add_excel_chart(worksheet, data, sheet_name)
            
            # Agregar bordes y formato adicional
            self._add_excel_borders(worksheet)
            
        except Exception as e:
            logger.error(f"Error creando hoja Excel {sheet_name}: {e}")
    
    def _format_excel_headers(self, worksheet):
        """Formatea los encabezados de Excel."""
        header_font = Font(bold=True, color="FFFFFF", size=12)
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
    
    def _adjust_excel_column_widths(self, worksheet):
        """Ajusta el ancho de las columnas de Excel."""
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
    
    def _add_excel_chart(self, worksheet, data: pd.DataFrame, sheet_name: str):
        """Añade gráficos a la hoja de Excel."""
        try:
            if len(data) == 0:
                return
            
            # Crear gráfico de barras para las primeras 10 filas
            chart = BarChart()
            chart.title = f"Top 10 - {sheet_name.replace('_', ' ').title()}"
            chart.style = 10
            chart.x_axis.title = "Estrategia"
            chart.y_axis.title = "Valor"
            
            # Seleccionar datos para el gráfico
            if "Factor_K" in data.columns:
                top_data = data.head(10)
                data_ref = Reference(worksheet, min_col=2, min_row=2, max_row=11, max_col=2)
                categories_ref = Reference(worksheet, min_col=1, min_row=2, max_row=11)
                
                chart.add_data(data_ref, titles_from_data=True)
                chart.set_categories(categories_ref)
                
                # Insertar gráfico
                worksheet.add_chart(chart, "H2")
                
        except Exception as e:
            logger.warning(f"No se pudo añadir gráfico a {sheet_name}: {e}")
    
    def _add_excel_borders(self, worksheet):
        """Añade bordes a la hoja de Excel."""
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        for row in worksheet.iter_rows():
            for cell in row:
                cell.border = thin_border
    
    def export_to_html_dashboard(self, filename: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exporta datos a dashboard HTML interactivo con Plotly.
        
        Args:
            filename: Nombre del archivo
            config: Configuración del dashboard (opcional)
            
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
                    "title": "Dashboard de Análisis de Estrategias",
                    "theme": "plotly_white",
                    "include_charts": True,
                    "include_filters": True,
                    "include_summary": True
                }
            
            # Crear dashboard HTML
            html_content = self._generate_html_dashboard(config)
            
            # Guardar archivo
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ Dashboard HTML exportado: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando dashboard HTML: {e}")
            return False
    
    def _generate_html_dashboard(self, config: Dict[str, Any]) -> str:
        """Genera el contenido HTML del dashboard."""
        try:
            # Crear gráficos con Plotly
            charts_html = self._create_plotly_charts()
            
            # Crear tabla interactiva
            table_html = self._create_interactive_table()
            
            # Crear filtros
            filters_html = self._create_html_filters()
            
            # Crear resumen
            summary_html = self._create_html_summary()
            
            # Template HTML completo
            html_template = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{config.get('title', 'Dashboard de Estrategias')}</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
                    .chart-container {{ margin: 20px 0; }}
                    .filter-section {{ background-color: #f8f9fa; padding: 15px; margin: 10px 0; }}
                    .summary-card {{ background-color: #e3f2fd; padding: 15px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container-fluid">
                    <h1 class="text-center mb-4">{config.get('title', 'Dashboard de Estrategias')}</h1>
                    
                    {filters_html if config.get('include_filters', True) else ''}
                    
                    {summary_html if config.get('include_summary', True) else ''}
                    
                    {charts_html if config.get('include_charts', True) else ''}
                    
                    {table_html}
                </div>
                
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            </body>
            </html>
            """
            
            return html_template
            
        except Exception as e:
            logger.error(f"Error generando dashboard HTML: {e}")
            return f"<html><body><h1>Error generando dashboard: {e}</h1></body></html>"
    
    def _create_plotly_charts(self) -> str:
        """Crea gráficos interactivos con Plotly."""
        try:
            charts_html = ""
            
            # Gráfico 1: Factor K por estrategia (Top 10)
            if "Factor_K" in self.data.columns:
                fig1 = go.Figure(data=[
                    go.Bar(
                        x=self.data.head(10)["Strategy_Name"],
                        y=self.data.head(10)["Factor_K"],
                        marker_color='rgb(55, 83, 109)'
                    )
                ])
                fig1.update_layout(
                    title="Top 10 Estrategias por Factor K",
                    xaxis_title="Estrategia",
                    yaxis_title="Factor K",
                    height=400
                )
                charts_html += f'<div class="chart-container">{fig1.to_html(full_html=False)}</div>'
            
            # Gráfico 2: Scatter CAGR vs Sharpe
            if "CAGR_IS" in self.data.columns and "Sharpe_Ratio_IS" in self.data.columns:
                fig2 = go.Figure(data=[
                    go.Scatter(
                        x=self.data["CAGR_IS"],
                        y=self.data["Sharpe_Ratio_IS"],
                        mode='markers',
                        marker=dict(
                            size=8,
                            color=self.data.get("Factor_K", [0]*len(self.data)),
                            colorscale='Viridis',
                            showscale=True
                        ),
                        text=self.data["Strategy_Name"],
                        hovertemplate='<b>%{text}</b><br>CAGR: %{x}<br>Sharpe: %{y}<extra></extra>'
                    )
                ])
                fig2.update_layout(
                    title="CAGR vs Sharpe Ratio",
                    xaxis_title="CAGR (%)",
                    yaxis_title="Sharpe Ratio",
                    height=400
                )
                charts_html += f'<div class="chart-container">{fig2.to_html(full_html=False)}</div>'
            
            # Gráfico 3: Distribución por categoría
            if "Categoria" in self.data.columns:
                category_counts = self.data["Categoria"].value_counts()
                fig3 = go.Figure(data=[
                    go.Pie(
                        labels=category_counts.index,
                        values=category_counts.values,
                        hole=0.3
                    )
                ])
                fig3.update_layout(
                    title="Distribución por Categoría",
                    height=400
                )
                charts_html += f'<div class="chart-container">{fig3.to_html(full_html=False)}</div>'
            
            return charts_html
            
        except Exception as e:
            logger.error(f"Error creando gráficos Plotly: {e}")
            return f'<div class="alert alert-warning">Error creando gráficos: {e}</div>'
    
    def _create_interactive_table(self) -> str:
        """Crea tabla interactiva HTML."""
        try:
            # Preparar datos para tabla
            table_data = self.data.head(50)  # Mostrar solo las primeras 50 filas
            
            # Crear tabla HTML
            table_html = """
            <div class="table-responsive">
                <table class="table table-striped table-hover">
                    <thead class="table-dark">
                        <tr>
            """
            
            # Encabezados
            for col in table_data.columns:
                table_html += f'<th>{col}</th>'
            
            table_html += """
                        </tr>
                    </thead>
                    <tbody>
            """
            
            # Filas de datos
            for _, row in table_data.iterrows():
                table_html += '<tr>'
                for value in row:
                    if pd.isna(value):
                        table_html += '<td>-</td>'
                    else:
                        table_html += f'<td>{value}</td>'
                table_html += '</tr>'
            
            table_html += """
                    </tbody>
                </table>
            </div>
            """
            
            return table_html
            
        except Exception as e:
            logger.error(f"Error creando tabla interactiva: {e}")
            return f'<div class="alert alert-warning">Error creando tabla: {e}</div>'
    
    def _create_html_filters(self) -> str:
        """Crea filtros HTML interactivos."""
        try:
            filters_html = """
            <div class="filter-section">
                <h4>Filtros</h4>
                <div class="row">
                    <div class="col-md-3">
                        <label for="minFactorK">Factor K Mínimo:</label>
                        <input type="number" id="minFactorK" class="form-control" min="0" max="10" step="0.1">
                    </div>
                    <div class="col-md-3">
                        <label for="minCAGR">CAGR Mínimo (%):</label>
                        <input type="number" id="minCAGR" class="form-control" min="-100" max="1000" step="0.1">
                    </div>
                    <div class="col-md-3">
                        <label for="maxDrawdown">Drawdown Máximo (%):</label>
                        <input type="number" id="maxDrawdown" class="form-control" min="0" max="100" step="0.1">
                    </div>
                    <div class="col-md-3">
                        <label for="categoryFilter">Categoría:</label>
                        <select id="categoryFilter" class="form-control">
                            <option value="">Todas</option>
                        </select>
                    </div>
                </div>
                <button class="btn btn-primary mt-2" onclick="applyFilters()">Aplicar Filtros</button>
            </div>
            """
            
            return filters_html
            
        except Exception as e:
            logger.error(f"Error creando filtros HTML: {e}")
            return f'<div class="alert alert-warning">Error creando filtros: {e}</div>'
    
    def _create_html_summary(self) -> str:
        """Crea resumen HTML."""
        try:
            total_strategies = len(self.data)
            avg_factor_k = self.data.get("Factor_K", pd.Series([0])).mean()
            avg_cagr = self.data.get("CAGR_IS", pd.Series([0])).mean()
            avg_sharpe = self.data.get("Sharpe_Ratio_IS", pd.Series([0])).mean()
            
            summary_html = f"""
            <div class="summary-card">
                <h4>Resumen</h4>
                <div class="row">
                    <div class="col-md-3">
                        <strong>Total Estrategias:</strong> {total_strategies}
                    </div>
                    <div class="col-md-3">
                        <strong>Factor K Promedio:</strong> {avg_factor_k:.2f}
                    </div>
                    <div class="col-md-3">
                        <strong>CAGR Promedio:</strong> {avg_cagr:.2f}%
                    </div>
                    <div class="col-md-3">
                        <strong>Sharpe Promedio:</strong> {avg_sharpe:.2f}
                    </div>
                </div>
            </div>
            """
            
            return summary_html
            
        except Exception as e:
            logger.error(f"Error creando resumen HTML: {e}")
            return f'<div class="alert alert-warning">Error creando resumen: {e}</div>'
    
    def export_to_pdf_report(self, filename: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exporta datos a reporte PDF profesional.
        
        Args:
            filename: Nombre del archivo
            config: Configuración del reporte (opcional)
            
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
                    "title": "Reporte de Análisis de Estrategias",
                    "author": "QVA Strategy Studio",
                    "include_charts": True,
                    "include_summary": True,
                    "include_details": True
                }
            
            # Crear documento PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Título
            story.append(Paragraph(config.get("title", "Reporte de Análisis"), title_style))
            story.append(Spacer(1, 20))
            
            # Resumen
            if config.get("include_summary", True):
                story.extend(self._create_pdf_summary(styles))
            
            # Tabla de datos
            if config.get("include_details", True):
                story.extend(self._create_pdf_table(styles))
            
            # Gráficos
            if config.get("include_charts", True):
                story.extend(self._create_pdf_charts())
            
            # Construir PDF
            doc.build(story)
            
            logger.info(f"✅ Reporte PDF exportado: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando PDF: {e}")
            return False
    
    def _create_pdf_summary(self, styles) -> List:
        """Crea sección de resumen para PDF."""
        elements = []
        
        # Título de sección
        elements.append(Paragraph("Resumen Ejecutivo", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Estadísticas básicas
        total_strategies = len(self.data)
        avg_factor_k = self.data.get("Factor_K", pd.Series([0])).mean()
        avg_cagr = self.data.get("CAGR_IS", pd.Series([0])).mean()
        
        summary_text = f"""
        <b>Total de Estrategias Analizadas:</b> {total_strategies}<br/>
        <b>Factor K Promedio:</b> {avg_factor_k:.2f}<br/>
        <b>CAGR Promedio:</b> {avg_cagr:.2f}%<br/>
        """
        
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_pdf_table(self, styles) -> List:
        """Crea tabla de datos para PDF."""
        elements = []
        
        # Título de sección
        elements.append(Paragraph("Top 20 Estrategias", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Preparar datos para tabla
        top_data = self.data.head(20)
        columns_to_show = ["Strategy_Name", "Factor_K", "CAGR_IS", "Sharpe_Ratio_IS", "Max_Drawdown_IS"]
        available_columns = [col for col in columns_to_show if col in top_data.columns]
        
        if available_columns:
            # Crear tabla
            table_data = [available_columns]  # Encabezados
            
            for _, row in top_data.iterrows():
                table_row = []
                for col in available_columns:
                    value = row[col]
                    if pd.isna(value):
                        table_row.append("-")
                    else:
                        table_row.append(str(value))
                table_data.append(table_row)
            
            # Crear tabla con estilo
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_pdf_charts(self) -> List:
        """Crea gráficos para PDF."""
        elements = []
        
        try:
            # Título de sección
            elements.append(Paragraph("Gráficos de Análisis", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            # Crear gráfico de barras
            if "Factor_K" in self.data.columns:
                fig, ax = plt.subplots(figsize=(10, 6))
                top_data = self.data.head(10)
                ax.bar(range(len(top_data)), top_data["Factor_K"])
                ax.set_title("Top 10 Estrategias por Factor K")
                ax.set_xlabel("Estrategia")
                ax.set_ylabel("Factor K")
                ax.set_xticks(range(len(top_data)))
                ax.set_xticklabels(top_data["Strategy_Name"], rotation=45, ha='right')
                
                # Guardar gráfico en buffer
                img_buffer = io.BytesIO()
                plt.tight_layout()
                plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                img_buffer.seek(0)
                
                # Añadir imagen al PDF
                img = Image(img_buffer)
                img.drawHeight = 4*inch
                img.drawWidth = 6*inch
                elements.append(img)
                elements.append(Spacer(1, 20))
                
                plt.close()
            
        except Exception as e:
            logger.error(f"Error creando gráficos PDF: {e}")
            elements.append(Paragraph(f"Error creando gráficos: {e}", styles['Normal']))
        
        return elements
    
    def export_batch(self, output_dir: str, formats: List[str] = None) -> bool:
        """
        Exporta datos en múltiples formatos por lotes.
        
        Args:
            output_dir: Directorio de salida
            formats: Lista de formatos a exportar
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if self.data is None or len(self.data) == 0:
                logger.error("No hay datos para exportar")
                return False
            
            # Formatos por defecto
            if formats is None:
                formats = ["excel", "html", "pdf", "csv", "json"]
            
            # Crear directorio si no existe
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Timestamp para nombres de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            success_count = 0
            
            for format_type in formats:
                try:
                    if format_type == "excel":
                        filename = os.path.join(output_dir, f"estrategias_analisis_{timestamp}.xlsx")
                        if self.export_to_excel_advanced(filename):
                            success_count += 1
                    
                    elif format_type == "html":
                        filename = os.path.join(output_dir, f"dashboard_estrategias_{timestamp}.html")
                        if self.export_to_html_dashboard(filename):
                            success_count += 1
                    
                    elif format_type == "pdf":
                        filename = os.path.join(output_dir, f"reporte_estrategias_{timestamp}.pdf")
                        if self.export_to_pdf_report(filename):
                            success_count += 1
                    
                    elif format_type == "csv":
                        filename = os.path.join(output_dir, f"estrategias_{timestamp}.csv")
                        if self.export_to_csv_advanced(filename):
                            success_count += 1
                    
                    elif format_type == "json":
                        filename = os.path.join(output_dir, f"estrategias_{timestamp}.json")
                        if self.export_to_json_advanced(filename):
                            success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error exportando {format_type}: {e}")
            
            logger.info(f"✅ Exportación por lotes completada: {success_count}/{len(formats)} formatos exitosos")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error en exportación por lotes: {e}")
            return False
    
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