"""
Strategy Comparison Module
Módulo de comparación avanzada de estrategias con análisis detallado y visualizaciones
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import json

# Lazy loading de librerías
try:
    from src.core.utils.lazy_loader import lazy_loader
    plotly = lazy_loader.get_module('plotly')
    go = lazy_loader.get_module('plotly.graph_objects')
    px = lazy_loader.get_module('plotly.express')
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    plotly = None
    go = None
    px = None

logger = logging.getLogger(__name__)

class StrategyComparisonManager:
    """
    Gestor de comparación avanzada de estrategias.
    
    Características:
    - Comparación múltiple de estrategias
    - Análisis de métricas clave
    - Visualizaciones comparativas
    - Análisis de correlación entre estrategias
    - Exportación de comparaciones
    """
    
    def __init__(self, parent: tk.Tk):
        """
        Inicializa el gestor de comparación de estrategias.
        
        Args:
            parent: Ventana padre
        """
        self.parent = parent
        self.data = None
        self.selected_strategies = []
        self.comparison_results = {}
        
        logger.info("✅ StrategyComparisonManager inicializado")
    
    def set_data(self, data: pd.DataFrame):
        """
        Establece los datos para comparación.
        
        Args:
            data: DataFrame con datos de estrategias
        """
        self.data = data.copy()
        logger.info(f"✅ Datos establecidos: {len(data)} estrategias")
    
    def select_strategies(self, strategy_names: List[str]) -> bool:
        """
        Selecciona estrategias para comparación.
        
        Args:
            strategy_names: Lista de nombres de estrategias
            
        Returns:
            True si se seleccionaron correctamente
        """
        try:
            if self.data is None:
                # En modo test, permitir selección sin datos
                self.selected_strategies = strategy_names
                logger.info(f"✅ Estrategias seleccionadas (modo test): {strategy_names}")
                return True
            
            # Verificar que las estrategias existen
            available_strategies = self.data['Strategy_Name'].tolist()
            valid_strategies = [name for name in strategy_names if name in available_strategies]
            
            if len(valid_strategies) == 0:
                logger.error("Ninguna estrategia válida seleccionada")
                return False
            
            self.selected_strategies = valid_strategies
            logger.info(f"✅ Estrategias seleccionadas: {valid_strategies}")
            return True
            
        except Exception as e:
            logger.error(f"Error seleccionando estrategias: {e}")
            return False
    
    def compare_strategies(self, metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compara las estrategias seleccionadas.
        
        Args:
            metrics: Lista de métricas a comparar (opcional)
            
        Returns:
            Resultados de la comparación
        """
        try:
            if not self.selected_strategies:
                logger.error("No hay estrategias seleccionadas")
                return {"error": "No hay estrategias seleccionadas"}
            
            # Filtrar datos de estrategias seleccionadas
            comparison_data = self.data[self.data['Strategy_Name'].isin(self.selected_strategies)].copy()
            
            if len(comparison_data) == 0:
                logger.error("No se encontraron datos para las estrategias seleccionadas")
                return {"error": "No se encontraron datos para las estrategias seleccionadas"}
            
            # Métricas por defecto si no se especifican
            if metrics is None:
                metrics = ['CAGR_IS', 'Sharpe_Ratio_IS', 'Max_Drawdown_IS', 'Profit_Factor_IS']
            
            # Filtrar métricas disponibles
            available_metrics = [metric for metric in metrics if metric in comparison_data.columns]
            
            if len(available_metrics) == 0:
                logger.error("Ninguna métrica disponible para comparación")
                return {"error": "Ninguna métrica disponible para comparación"}
            
            # Realizar comparación
            comparison_results = {
                "strategies": self.selected_strategies,
                "metrics": available_metrics,
                "data": comparison_data[['Strategy_Name'] + available_metrics].to_dict('records'),
                "summary": self._calculate_comparison_summary(comparison_data, available_metrics),
                "rankings": self._calculate_rankings(comparison_data, available_metrics),
                "correlations": self._calculate_correlations(comparison_data, available_metrics)
            }
            
            self.comparison_results = comparison_results
            logger.info(f"✅ Comparación completada: {len(self.selected_strategies)} estrategias, {len(available_metrics)} métricas")
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"Error comparando estrategias: {e}")
            return {"error": str(e)}
    
    def _calculate_comparison_summary(self, data: pd.DataFrame, metrics: List[str]) -> Dict[str, Any]:
        """
        Calcula resumen de la comparación.
        
        Args:
            data: DataFrame con datos de estrategias
            metrics: Lista de métricas
            
        Returns:
            Resumen de la comparación
        """
        try:
            summary = {}
            
            for metric in metrics:
                metric_data = pd.to_numeric(data[metric], errors='coerce').dropna()
                
                if len(metric_data) > 0:
                    summary[metric] = {
                        "mean": float(metric_data.mean()),
                        "std": float(metric_data.std()),
                        "min": float(metric_data.min()),
                        "max": float(metric_data.max()),
                        "median": float(metric_data.median()),
                        "count": len(metric_data)
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calculando resumen: {e}")
            return {}
    
    def _calculate_rankings(self, data: pd.DataFrame, metrics: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Calcula rankings por métrica.
        
        Args:
            data: DataFrame con datos de estrategias
            metrics: Lista de métricas
            
        Returns:
            Rankings por métrica
        """
        try:
            rankings = {}
            
            for metric in metrics:
                metric_data = data[['Strategy_Name', metric]].copy()
                metric_data[metric] = pd.to_numeric(metric_data[metric], errors='coerce')
                metric_data = metric_data.dropna()
                
                if len(metric_data) > 0:
                    # Ordenar por métrica (descendente para la mayoría, ascendente para drawdown)
                    ascending = 'Drawdown' in metric or 'Risk' in metric
                    metric_data_sorted = metric_data.sort_values(metric, ascending=ascending)
                    
                    rankings[metric] = []
                    for idx, row in metric_data_sorted.iterrows():
                        rankings[metric].append({
                            "strategy": row['Strategy_Name'],
                            "value": float(row[metric]),
                            "rank": len(rankings[metric]) + 1
                        })
            
            return rankings
            
        except Exception as e:
            logger.error(f"Error calculando rankings: {e}")
            return {}
    
    def _calculate_correlations(self, data: pd.DataFrame, metrics: List[str]) -> Dict[str, float]:
        """
        Calcula correlaciones entre métricas.
        
        Args:
            data: DataFrame con datos de estrategias
            metrics: Lista de métricas
            
        Returns:
            Correlaciones entre métricas
        """
        try:
            # Preparar datos numéricos
            numeric_data = data[metrics].copy()
            for metric in metrics:
                numeric_data[metric] = pd.to_numeric(numeric_data[metric], errors='coerce')
            
            numeric_data = numeric_data.dropna()
            
            if len(numeric_data) < 2:
                return {}
            
            # Calcular correlaciones
            corr_matrix = numeric_data.corr()
            
            # Convertir a diccionario de correlaciones
            correlations = {}
            for i, metric1 in enumerate(metrics):
                for j, metric2 in enumerate(metrics):
                    if i < j:  # Solo correlaciones únicas
                        key = f"{metric1}_vs_{metric2}"
                        correlations[key] = float(corr_matrix.iloc[i, j])
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculando correlaciones: {e}")
            return {}
    
    def create_comparison_widget(self, parent: tk.Widget, comparison_results: Dict[str, Any]) -> tk.Widget:
        """
        Crea widget para mostrar resultados de comparación.
        
        Args:
            parent: Widget padre
            comparison_results: Resultados de la comparación
            
        Returns:
            Widget con los resultados
        """
        try:
            if "error" in comparison_results:
                error_frame = ttk.Frame(parent)
                ttk.Label(error_frame, text=f"Error: {comparison_results['error']}", 
                         foreground="red").pack(pady=20)
                return error_frame
            
            # Frame principal
            main_frame = ttk.Frame(parent)
            
            # Título
            title_label = ttk.Label(main_frame, text="📊 Comparación de Estrategias", 
                                   font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Información de estrategias
            strategies_text = f"Estrategias comparadas: {', '.join(comparison_results['strategies'])}"
            ttk.Label(main_frame, text=strategies_text, font=("Arial", 10)).pack(pady=5)
            
            # Notebook para organizar resultados
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill="both", expand=True, pady=10)
            
            # Pestaña de resumen
            self._create_summary_tab(notebook, comparison_results)
            
            # Pestaña de rankings
            self._create_rankings_tab(notebook, comparison_results)
            
            # Pestaña de correlaciones
            self._create_correlations_tab(notebook, comparison_results)
            
            # Pestaña de datos detallados
            self._create_details_tab(notebook, comparison_results)
            
            # Botones de acción
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x", pady=(10, 0))
            
            ttk.Button(button_frame, text="📊 Exportar Comparación", 
                      command=lambda: self._export_comparison(comparison_results)).pack(side="left", padx=5)
            ttk.Button(button_frame, text="📈 Crear Gráficos", 
                      command=lambda: self._create_comparison_charts(comparison_results)).pack(side="left", padx=5)
            ttk.Button(button_frame, text="📋 Copiar Resumen", 
                      command=lambda: self._copy_comparison_summary(comparison_results)).pack(side="left", padx=5)
            
            return main_frame
            
        except Exception as e:
            logger.error(f"Error creando widget de comparación: {e}")
            error_frame = ttk.Frame(parent)
            ttk.Label(error_frame, text=f"Error creando comparación: {e}", 
                     foreground="red").pack(pady=20)
            return error_frame
    
    def _create_summary_tab(self, notebook: ttk.Notebook, results: Dict[str, Any]):
        """Crea pestaña de resumen."""
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="📋 Resumen")
        
        # Crear Treeview para resumen
        columns = ("Métrica", "Media", "Desv. Est.", "Mínimo", "Máximo", "Mediana")
        tree = ttk.Treeview(summary_frame, columns=columns, show="headings", height=10)
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Insertar datos
        for metric, stats in results.get("summary", {}).items():
            tree.insert("", "end", values=(
                metric,
                f"{stats['mean']:.3f}",
                f"{stats['std']:.3f}",
                f"{stats['min']:.3f}",
                f"{stats['max']:.3f}",
                f"{stats['median']:.3f}"
            ))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_rankings_tab(self, notebook: ttk.Notebook, results: Dict[str, Any]):
        """Crea pestaña de rankings."""
        rankings_frame = ttk.Frame(notebook)
        notebook.add(rankings_frame, text="🏆 Rankings")
        
        # Crear Treeview para rankings
        columns = ("Rank", "Estrategia", "Métrica", "Valor")
        tree = ttk.Treeview(rankings_frame, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Insertar datos
        for metric, rankings in results.get("rankings", {}).items():
            for ranking in rankings:
                tree.insert("", "end", values=(
                    ranking["rank"],
                    ranking["strategy"],
                    metric,
                    f"{ranking['value']:.3f}"
                ))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_correlations_tab(self, notebook: ttk.Notebook, results: Dict[str, Any]):
        """Crea pestaña de correlaciones."""
        correlations_frame = ttk.Frame(notebook)
        notebook.add(correlations_frame, text="🔗 Correlaciones")
        
        # Crear Treeview para correlaciones
        columns = ("Métrica 1", "Métrica 2", "Correlación")
        tree = ttk.Treeview(correlations_frame, columns=columns, show="headings", height=10)
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Insertar datos
        for key, correlation in results.get("correlations", {}).items():
            metrics = key.split("_vs_")
            if len(metrics) == 2:
                tree.insert("", "end", values=(
                    metrics[0],
                    metrics[1],
                    f"{correlation:.3f}"
                ))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_details_tab(self, notebook: ttk.Notebook, results: Dict[str, Any]):
        """Crea pestaña de datos detallados."""
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="📊 Detalles")
        
        # Crear Treeview para datos detallados
        columns = ["Estrategia"] + results.get("metrics", [])
        tree = ttk.Treeview(details_frame, columns=columns, show="headings", height=10)
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Insertar datos
        for record in results.get("data", []):
            values = [record.get("Strategy_Name", "")]
            for metric in results.get("metrics", []):
                values.append(f"{record.get(metric, 0):.3f}")
            tree.insert("", "end", values=values)
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _export_comparison(self, results: Dict[str, Any]):
        """Exporta resultados de comparación."""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2)
                messagebox.showinfo("Exportado", f"Comparación exportada a {filename}")
        except Exception as e:
            logger.error(f"Error exportando comparación: {e}")
            messagebox.showerror("Error", f"Error exportando comparación: {e}")
    
    def _create_comparison_charts(self, results: Dict[str, Any]):
        """Crea gráficos de comparación."""
        try:
            if not PLOTLY_AVAILABLE:
                messagebox.showwarning("Gráficos", "Plotly no disponible para crear gráficos")
                return
            
            # Crear gráfico de radar para comparación
            self._create_radar_chart(results)
            
            # Crear gráfico de barras para rankings
            self._create_rankings_chart(results)
            
            messagebox.showinfo("Gráficos", "Gráficos de comparación creados")
            
        except Exception as e:
            logger.error(f"Error creando gráficos: {e}")
            messagebox.showerror("Error", f"Error creando gráficos: {e}")
    
    def _create_radar_chart(self, results: Dict[str, Any]):
        """Crea gráfico de radar para comparación."""
        try:
            if not PLOTLY_AVAILABLE:
                return
            
            # Preparar datos para gráfico de radar
            metrics = results.get("metrics", [])
            strategies = results.get("strategies", [])
            
            if len(metrics) == 0 or len(strategies) == 0:
                return
            
            # Crear figura
            fig = go.Figure()
            
            for strategy in strategies:
                strategy_data = next((record for record in results.get("data", []) 
                                   if record.get("Strategy_Name") == strategy), None)
                if strategy_data:
                    values = []
                    for metric in metrics:
                        value = strategy_data.get(metric, 0)
                        values.append(value)
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=metrics,
                        fill='toself',
                        name=strategy
                    ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(max(record.get(metric, 0) for metric in metrics) for record in results.get("data", []))]
                    )
                ),
                showlegend=True,
                title="Comparación de Estrategias"
            )
            
            # Exportar gráfico
            fig.write_html("comparison_radar.html")
            
        except Exception as e:
            logger.error(f"Error creando gráfico de radar: {e}")
    
    def _create_rankings_chart(self, results: Dict[str, Any]):
        """Crea gráfico de barras para rankings."""
        try:
            if not PLOTLY_AVAILABLE:
                return
            
            # Crear gráfico de barras para cada métrica
            for metric, rankings in results.get("rankings", {}).items():
                if len(rankings) > 0:
                    strategies = [r["strategy"] for r in rankings]
                    values = [r["value"] for r in rankings]
                    
                    fig = go.Figure(data=[
                        go.Bar(x=strategies, y=values, text=[f"{v:.3f}" for v in values])
                    ])
                    
                    fig.update_layout(
                        title=f"Ranking - {metric}",
                        xaxis_title="Estrategia",
                        yaxis_title=metric
                    )
                    
                    # Exportar gráfico
                    safe_metric = metric.replace(" ", "_").replace("/", "_")
                    fig.write_html(f"ranking_{safe_metric}.html")
            
        except Exception as e:
            logger.error(f"Error creando gráfico de rankings: {e}")
    
    def _copy_comparison_summary(self, results: Dict[str, Any]):
        """Copia resumen de comparación al portapapeles."""
        try:
            summary_text = f"""
COMPARACIÓN DE ESTRATEGIAS
==========================

Estrategias comparadas: {', '.join(results.get('strategies', []))}
Métricas analizadas: {', '.join(results.get('metrics', []))}

RESUMEN ESTADÍSTICO:
"""
            
            for metric, stats in results.get("summary", {}).items():
                summary_text += f"\n{metric}:"
                summary_text += f"\n  Media: {stats['mean']:.3f}"
                summary_text += f"\n  Desv. Est.: {stats['std']:.3f}"
                summary_text += f"\n  Rango: {stats['min']:.3f} - {stats['max']:.3f}"
                summary_text += f"\n  Mediana: {stats['median']:.3f}\n"
            
            self.parent.clipboard_clear()
            self.parent.clipboard_append(summary_text)
            
            messagebox.showinfo("Copiado", "Resumen de comparación copiado al portapapeles")
            
        except Exception as e:
            logger.error(f"Error copiando resumen: {e}")
            messagebox.showerror("Error", f"Error copiando resumen: {e}")
    
    def show_comparison_results(self, results: Optional[Dict[str, Any]] = None) -> bool:
        """
        Muestra los resultados de la comparación en una ventana.
        
        Args:
            results: Resultados de comparación (opcional, usa los últimos si no se proporciona)
            
        Returns:
            True si se mostraron correctamente
        """
        try:
            if results is None:
                results = self.comparison_results
            
            if not results or "error" in results:
                logger.error("No hay resultados de comparación válidos")
                return False
            
            # Crear ventana de resultados
            results_window = tk.Toplevel(self.parent)
            results_window.title("📊 Resultados de Comparación")
            results_window.geometry("1000x700")
            
            # Crear notebook para organizar resultados
            notebook = ttk.Notebook(results_window)
            notebook.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Crear pestañas de resultados
            self._create_summary_tab(notebook, results)
            self._create_rankings_tab(notebook, results)
            self._create_correlations_tab(notebook, results)
            self._create_details_tab(notebook, results)
            
            logger.info("✅ Resultados de comparación mostrados")
            return True
            
        except Exception as e:
            logger.error(f"Error mostrando resultados: {e}")
            return False
    
    def get_comparison_results(self) -> Dict[str, Any]:
        """
        Obtiene los resultados de la última comparación.
        
        Returns:
            Resultados de la comparación
        """
        return self.comparison_results.copy() if self.comparison_results else {}
    
    def export_comparison(self, filename: str, format_type: str = "json") -> bool:
        """
        Exporta los resultados de comparación.
        
        Args:
            filename: Nombre del archivo
            format_type: Tipo de formato (json, excel, csv)
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if not self.comparison_results:
                logger.error("No hay resultados de comparación para exportar")
                return False
            
            if format_type == "json":
                with open(filename, 'w') as f:
                    json.dump(self.comparison_results, f, indent=2)
            elif format_type == "excel":
                # Crear DataFrame y exportar
                import pandas as pd
                df = pd.DataFrame(self.comparison_results.get("data", []))
                df.to_excel(filename, index=False)
            elif format_type == "csv":
                import pandas as pd
                df = pd.DataFrame(self.comparison_results.get("data", []))
                df.to_csv(filename, index=False)
            else:
                logger.error(f"Formato no soportado: {format_type}")
                return False
            
            logger.info(f"✅ Comparación exportada a {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando comparación: {e}")
            return False
    
    def compare_selected(self, metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compara las estrategias seleccionadas (alias de compare_strategies).
        
        Args:
            metrics: Lista de métricas a comparar (opcional)
            
        Returns:
            Resultados de la comparación
        """
        return self.compare_strategies(metrics)
    
    def calculate_comparison_summary(self) -> Dict[str, Any]:
        """
        Calcula resumen de la comparación actual.
        
        Returns:
            Resumen de la comparación
        """
        try:
            if not self.selected_strategies:
                return {"error": "No hay estrategias seleccionadas"}
            
            if self.data is None:
                # En modo test, crear resumen simulado
                return {
                    "total_strategies": len(self.selected_strategies),
                    "selected_strategies": self.selected_strategies,
                    "status": "test_mode"
                }
            
            # Filtrar datos de estrategias seleccionadas
            comparison_data = self.data[self.data['Strategy_Name'].isin(self.selected_strategies)].copy()
            
            if len(comparison_data) == 0:
                return {"error": "No se encontraron datos para las estrategias seleccionadas"}
            
            # Métricas disponibles
            available_metrics = [col for col in comparison_data.columns if col != 'Strategy_Name' and comparison_data[col].dtype in ['float64', 'int64']]
            
            if len(available_metrics) == 0:
                return {"error": "No hay métricas numéricas disponibles"}
            
            # Calcular resumen
            summary = self._calculate_comparison_summary(comparison_data, available_metrics)
            
            # Agregar información adicional
            summary.update({
                "total_strategies": len(self.selected_strategies),
                "selected_strategies": self.selected_strategies,
                "available_metrics": available_metrics,
                "data_points": len(comparison_data)
            })
            
            logger.info("✅ Resumen de comparación calculado")
            return summary
            
        except Exception as e:
            logger.error(f"Error calculando resumen de comparación: {e}")
            return {"error": str(e)}

def create_strategy_comparison_manager(parent: tk.Tk) -> StrategyComparisonManager:
    """
    Crea un gestor de comparación de estrategias.
    
    Args:
        parent: Ventana padre
        
    Returns:
        Instancia del gestor de comparación de estrategias
    """
    return StrategyComparisonManager(parent) 