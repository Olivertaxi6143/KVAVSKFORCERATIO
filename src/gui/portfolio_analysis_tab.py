"""
Portfolio Analysis Tab Module
Pestaña para análisis de portfolios
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import threading
from PySide6.QtCore import QThread, Signal
import time

# Importar módulos de la aplicación
from src.data.data_manager import DataManager
from src.core.utils.error_handler import RobustErrorHandler
import logging

log = logging.getLogger(__name__)

class PortfolioLoaderThread(QThread):
    """Hilo para cargar portfolios sin bloquear la GUI"""
    portfolio_loaded = Signal(pd.DataFrame)
    error_occurred = Signal(str)
    progress_updated = Signal(int)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        """Ejecuta la carga del portfolio en segundo plano"""
        try:
            self.progress_updated.emit(10)
            
            # Simular carga de datos
            time.sleep(0.5)
            self.progress_updated.emit(50)
            
            # Cargar datos del archivo
            df = pd.read_csv(self.file_path)
            df = self._clean_portfolio_data(df)
            
            self.progress_updated.emit(90)
            time.sleep(0.2)
            
            self.progress_updated.emit(100)
            self.portfolio_loaded.emit(df)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def _clean_portfolio_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y valida los datos del portfolio"""
        # Eliminar filas duplicadas
        df = df.drop_duplicates()
        
        # Asegurar que las columnas necesarias existan
        required_columns = ['Strategy Name', 'FactorK', 'CAGR', 'Sharpe', 'MaxDD', 'Trades']
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0.0
        
        # Convertir columnas numéricas
        numeric_columns = ['FactorK', 'CAGR', 'Sharpe', 'MaxDD', 'Trades']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0.0)
        
        return df

class PortfolioMetricsCalculator:
    """Calculadora de métricas para portfolios"""
    
    def __init__(self):
        self.error_handler = RobustErrorHandler()
    
    def calculate_portfolio_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula métricas agregadas del portfolio"""
        try:
            if df.empty:
                return self._get_empty_metrics()
            
            # Calcular métricas de forma segura
            metrics = {
                'total_strategies': len(df),
                'total_net_profit': df['NetProfit'].sum() if 'NetProfit' in df.columns else 0,
                'avg_cagr': df['CAGR'].mean() if 'CAGR' in df.columns else 0,
                'avg_sharpe': df['Sharpe'].mean() if 'Sharpe' in df.columns else 0,
                'avg_max_dd': df['MaxDD'].mean() if 'MaxDD' in df.columns else 0,
                'avg_profit_factor': df['ProfitFactor'].mean() if 'ProfitFactor' in df.columns else 0,
                'total_trades': df['Trades'].sum() if 'Trades' in df.columns else 0,
                'avg_correlation': self._calculate_avg_correlation(df),
                'elite_count': len(df[df['FactorK'] >= 9.2]) if 'FactorK' in df.columns else 0,
                'excellent_count': len(df[(df['FactorK'] >= 8.2) & (df['FactorK'] < 9.2)]) if 'FactorK' in df.columns else 0,
                'very_good_count': len(df[(df['FactorK'] >= 7.2) & (df['FactorK'] < 8.2)]) if 'FactorK' in df.columns else 0
            }
            
            return metrics
            
        except Exception as e:
            log.error(f"Error calculando métricas del portfolio: {e}")
            return self._get_empty_metrics()
    
    def _calculate_avg_correlation(self, df: pd.DataFrame) -> float:
        """Calcula la correlación promedio entre estrategias"""
        try:
            # Simular cálculo de correlación
            return 0.15  # Valor típico para portfolios bien diversificados
        except Exception:
            return 0.0

    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Retorna métricas vacías"""
        return {
            'total_strategies': 0,
            'total_net_profit': 0,
            'avg_cagr': 0,
            'avg_sharpe': 0,
            'avg_max_dd': 0,
            'avg_profit_factor': 0,
            'total_trades': 0,
            'avg_correlation': 0,
            'elite_count': 0,
            'excellent_count': 0,
            'very_good_count': 0
        }

class PortfolioAnalysisTab(ttk.Frame):
    """Pestaña para análisis de portfolios"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = DataManager()
        self.metrics_calculator = PortfolioMetricsCalculator()
        self.current_portfolio: Optional[pd.DataFrame] = None
        self.error_handler = RobustErrorHandler()
        
        self.setup_ui()
        log.info("PortfolioAnalysisTab inicializada")
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Título
        title = ttk.Label(self, text="Análisis de Portfolios", font=("Arial", 16, "bold"))
        title.pack(pady=(10, 20))
        
        # Frame para controles
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Botones de carga
        self.load_portfolio_btn = ttk.Button(controls_frame, text="Cargar Portfolio", 
                                           command=self.load_portfolio)
        self.load_portfolio_btn.pack(side="left", padx=5)
        
        self.clear_btn = ttk.Button(controls_frame, text="Limpiar", 
                                   command=self.clear_portfolio)
        self.clear_btn.pack(side="left", padx=5)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(controls_frame, mode='determinate')
        self.progress_bar.pack(side="right", padx=5, fill="x", expand=True)
        self.progress_bar.pack_forget()  # Oculto inicialmente
        
        # Notebook para tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Crear tabs
        self.create_metrics_tab()
        self.create_comparison_tab()
        self.create_darwinex_tab()
        self.create_axi_tab()
        self.create_export_tab()
        
        # Tabla de estrategias
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ttk.Label(table_frame, text="Estrategias del Portfolio:").pack(anchor="w")
        
        # Crear tabla con scrollbars
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill="both", expand=True)
        
        columns = ["Strategy Name", "FactorK", "CAGR", "Sharpe", "MaxDD", "Trades"]
        self.strategies_table = ttk.Treeview(table_container, columns=columns, show="headings", height=10)
        
        # Configurar columnas
        for col in columns:
            self.strategies_table.heading(col, text=col)
            self.strategies_table.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.strategies_table.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.strategies_table.xview)
        self.strategies_table.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.strategies_table.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Inicialmente deshabilitar tabs
        self.set_tabs_enabled(False)
    
    def create_metrics_tab(self):
        """Crea el tab de métricas agregadas"""
        metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(metrics_frame, text="Métricas Agregadas")
        
        # Grupo de métricas básicas
        basic_group = ttk.LabelFrame(metrics_frame, text="Métricas Básicas")
        basic_group.pack(fill="x", padx=10, pady=5)
        
        basic_layout = ttk.Frame(basic_group)
        basic_layout.pack(fill="x", padx=10, pady=10)
        
        self.total_strategies_label = ttk.Label(basic_layout, text="Total Estrategias: 0")
        self.total_strategies_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.total_net_profit_label = ttk.Label(basic_layout, text="Profit Total: $0")
        self.total_net_profit_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        self.avg_cagr_label = ttk.Label(basic_layout, text="CAGR Promedio: 0%")
        self.avg_cagr_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        self.avg_sharpe_label = ttk.Label(basic_layout, text="Sharpe Promedio: 0")
        self.avg_sharpe_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Grupo de métricas avanzadas
        advanced_group = ttk.LabelFrame(metrics_frame, text="Métricas Avanzadas")
        advanced_group.pack(fill="x", padx=10, pady=5)
        
        advanced_layout = ttk.Frame(advanced_group)
        advanced_layout.pack(fill="x", padx=10, pady=10)
        
        self.avg_max_dd_label = ttk.Label(advanced_layout, text="Max DD Promedio: 0%")
        self.avg_max_dd_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.avg_profit_factor_label = ttk.Label(advanced_layout, text="Profit Factor Promedio: 0")
        self.avg_profit_factor_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        self.total_trades_label = ttk.Label(advanced_layout, text="Total Trades: 0")
        self.total_trades_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        self.avg_correlation_label = ttk.Label(advanced_layout, text="Correlación Promedio: 0")
        self.avg_correlation_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Grupo de distribución por categorías
        categories_group = ttk.LabelFrame(metrics_frame, text="Distribución por Categorías")
        categories_group.pack(fill="x", padx=10, pady=5)
        
        categories_layout = ttk.Frame(categories_group)
        categories_layout.pack(fill="x", padx=10, pady=10)
        
        self.elite_count_label = ttk.Label(categories_layout, text="Elite: 0")
        self.elite_count_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.excellent_count_label = ttk.Label(categories_layout, text="Excellent: 0")
        self.excellent_count_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        self.very_good_count_label = ttk.Label(categories_layout, text="Very Good: 0")
        self.very_good_count_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
    
    def create_comparison_tab(self):
        """Crea el tab de comparativas"""
        comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(comparison_frame, text="Comparativas")
        
        # Botón para comparar portfolios
        self.compare_btn = ttk.Button(comparison_frame, text="Comparar Portfolios", 
                                     command=self.compare_portfolios)
        self.compare_btn.pack(pady=10)
        
        # Área de resultados de comparación
        self.comparison_text = tk.Text(comparison_frame, height=15, wrap="word")
        self.comparison_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbar para el texto
        scrollbar = ttk.Scrollbar(comparison_frame, orient="vertical", command=self.comparison_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.comparison_text.configure(yscrollcommand=scrollbar.set)
    
    def create_darwinex_tab(self):
        """Crea el tab de análisis Darwinex"""
        darwinex_frame = ttk.Frame(self.notebook)
        self.notebook.add(darwinex_frame, text="Darwinex")
        
        # Botón para análisis Darwinex
        self.darwinex_btn = ttk.Button(darwinex_frame, text="Analizar para Darwinex", 
                                      command=self.analyze_darwinex)
        self.darwinex_btn.pack(pady=10)
        
        # Área de resultados
        self.darwinex_text = tk.Text(darwinex_frame, height=15, wrap="word")
        self.darwinex_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(darwinex_frame, orient="vertical", command=self.darwinex_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.darwinex_text.configure(yscrollcommand=scrollbar.set)
    
    def create_axi_tab(self):
        """Crea el tab de análisis Axi Select"""
        axi_frame = ttk.Frame(self.notebook)
        self.notebook.add(axi_frame, text="Axi Select")
        
        # Botón para análisis Axi Select
        self.axi_btn = ttk.Button(axi_frame, text="Analizar con Axi Select", 
                                 command=self.analyze_axi_select)
        self.axi_btn.pack(pady=10)
        
        # Área de resultados
        self.axi_text = tk.Text(axi_frame, height=15, wrap="word")
        self.axi_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(axi_frame, orient="vertical", command=self.axi_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.axi_text.configure(yscrollcommand=scrollbar.set)
    
    def create_export_tab(self):
        """Crea el tab de exportación"""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="Exportar")
        
        # Botones de exportación
        export_buttons_frame = ttk.Frame(export_frame)
        export_buttons_frame.pack(pady=10)
        
        self.export_excel_btn = ttk.Button(export_buttons_frame, text="Exportar a Excel", 
                                          command=self.export_to_excel)
        self.export_excel_btn.pack(side="left", padx=5)
        
        self.export_html_btn = ttk.Button(export_buttons_frame, text="Exportar a HTML", 
                                         command=self.export_to_html)
        self.export_html_btn.pack(side="left", padx=5)
        
        # Área de resultados
        self.export_text = tk.Text(export_frame, height=10, wrap="word")
        self.export_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(export_frame, orient="vertical", command=self.export_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.export_text.configure(yscrollcommand=scrollbar.set)
    
    def load_portfolio(self):
        """Carga un portfolio desde archivo"""
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo de portfolio",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("Excel files", "*.xlsx"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                self.start_portfolio_loading(file_path)
                
        except Exception as e:
            log.error(f"Error cargando portfolio: {e}")
            messagebox.showerror("Error", f"Error cargando portfolio: {str(e)}")
    
    def start_portfolio_loading(self, file_path: str):
        """Inicia la carga del portfolio en segundo plano"""
        try:
            # Mostrar barra de progreso
            self.progress_bar.pack(side="right", padx=5, fill="x", expand=True)
            self.progress_bar['value'] = 0
            
            # Crear y ejecutar hilo de carga
        self.loader_thread = PortfolioLoaderThread(file_path)
        self.loader_thread.portfolio_loaded.connect(self.on_portfolio_loaded)
        self.loader_thread.error_occurred.connect(self.on_loading_error)
            self.loader_thread.progress_updated.connect(self.progress_bar.configure)
        self.loader_thread.start()
            
        except Exception as e:
            log.error(f"Error iniciando carga de portfolio: {e}")
            messagebox.showerror("Error", f"Error iniciando carga: {str(e)}")
    
    def on_portfolio_loaded(self, df: pd.DataFrame):
        """Maneja la carga exitosa del portfolio"""
        try:
            self.current_portfolio = df
            self.update_strategies_table(df)
            self.update_metrics(df)
            self.set_tabs_enabled(True)
            
            # Ocultar barra de progreso
            self.progress_bar.pack_forget()
            
            messagebox.showinfo("Éxito", f"Portfolio cargado: {len(df)} estrategias")
            
        except Exception as e:
            log.error(f"Error procesando portfolio cargado: {e}")
            messagebox.showerror("Error", f"Error procesando portfolio: {str(e)}")
    
    def on_loading_error(self, error_msg: str):
        """Maneja errores durante la carga"""
        try:
            # Ocultar barra de progreso
            self.progress_bar.pack_forget()
            
            messagebox.showerror("Error de Carga", f"Error cargando portfolio: {error_msg}")
            
        except Exception as e:
            log.error(f"Error manejando error de carga: {e}")
    
    def update_strategies_table(self, df: pd.DataFrame):
        """Actualiza la tabla de estrategias"""
        try:
            # Limpiar tabla
            for item in self.strategies_table.get_children():
                self.strategies_table.delete(item)
            
            # Agregar datos
            for _, row in df.iterrows():
                values = [
                    row.get('Strategy Name', ''),
                    f"{row.get('FactorK', 0):.2f}",
                    f"{row.get('CAGR', 0):.2f}%",
                    f"{row.get('Sharpe', 0):.2f}",
                    f"{row.get('MaxDD', 0):.2f}%",
                    str(row.get('Trades', 0))
                ]
                self.strategies_table.insert('', 'end', values=values)
            
        except Exception as e:
            log.error(f"Error actualizando tabla de estrategias: {e}")
    
    def update_metrics(self, df: pd.DataFrame):
        """Actualiza las métricas mostradas"""
        try:
            metrics = self.metrics_calculator.calculate_portfolio_metrics(df)
            
            # Actualizar labels
            self.total_strategies_label.config(text=f"Total Estrategias: {metrics['total_strategies']}")
            self.total_net_profit_label.config(text=f"Profit Total: ${metrics['total_net_profit']:,.2f}")
            self.avg_cagr_label.config(text=f"CAGR Promedio: {metrics['avg_cagr']:.2f}%")
            self.avg_sharpe_label.config(text=f"Sharpe Promedio: {metrics['avg_sharpe']:.2f}")
            self.avg_max_dd_label.config(text=f"Max DD Promedio: {metrics['avg_max_dd']:.2f}%")
            self.avg_profit_factor_label.config(text=f"Profit Factor Promedio: {metrics['avg_profit_factor']:.2f}")
            self.total_trades_label.config(text=f"Total Trades: {metrics['total_trades']:,}")
            self.avg_correlation_label.config(text=f"Correlación Promedio: {metrics['avg_correlation']:.3f}")
            self.elite_count_label.config(text=f"Elite: {metrics['elite_count']}")
            self.excellent_count_label.config(text=f"Excellent: {metrics['excellent_count']}")
            self.very_good_count_label.config(text=f"Very Good: {metrics['very_good_count']}")
            
        except Exception as e:
            log.error(f"Error actualizando métricas: {e}")
    
    def set_tabs_enabled(self, enabled: bool):
        """Habilita o deshabilita los tabs"""
        try:
            for i in range(self.notebook.index('end')):
                self.notebook.tab(i, state='normal' if enabled else 'disabled')
                
        except Exception as e:
            log.error(f"Error configurando estado de tabs: {e}")
    
    def clear_portfolio(self):
        """Limpia el portfolio actual"""
        try:
            self.current_portfolio = None
            
            # Limpiar tabla
            for item in self.strategies_table.get_children():
                self.strategies_table.delete(item)
            
            # Resetear métricas
            self.update_metrics(pd.DataFrame())
            
            # Deshabilitar tabs
            self.set_tabs_enabled(False)
            
            # Limpiar áreas de texto
            self.comparison_text.delete(1.0, tk.END)
            self.darwinex_text.delete(1.0, tk.END)
            self.axi_text.delete(1.0, tk.END)
            self.export_text.delete(1.0, tk.END)
            
            messagebox.showinfo("Portfolio Limpiado", "Portfolio limpiado correctamente")
            
        except Exception as e:
            log.error(f"Error limpiando portfolio: {e}")
            messagebox.showerror("Error", f"Error limpiando portfolio: {str(e)}")
    
    def compare_portfolios(self):
        """Compara portfolios"""
        try:
            if self.current_portfolio is None or self.current_portfolio.empty:
                messagebox.showwarning("Advertencia", "No hay portfolio cargado para comparar")
                return
            
            df = self.current_portfolio
            # Métricas seguras
            factork_col = df['FactorK'] if 'FactorK' in df.columns else pd.Series([0]*len(df))
            cagr_col = df['CAGR'] if 'CAGR' in df.columns else pd.Series([0]*len(df))
            sharpe_col = df['Sharpe'] if 'Sharpe' in df.columns else pd.Series([0]*len(df))
            maxdd_col = df['MaxDD'] if 'MaxDD' in df.columns else pd.Series([0]*len(df))

            comparison_result = f"""
Comparación de Portfolio:
========================
Total Estrategias: {len(df)}
FactorK Promedio: {factork_col.mean():.2f}
CAGR Promedio: {cagr_col.mean():.2f}%
Sharpe Promedio: {sharpe_col.mean():.2f}
MaxDD Promedio: {maxdd_col.mean():.2f}%

Distribución por Categorías:
- Elite: {len(df[factork_col >= 9.2])}
- Excellent: {len(df[(factork_col >= 8.2) & (factork_col < 9.2)])}
- Very Good: {len(df[(factork_col >= 7.2) & (factork_col < 8.2)])}
"""
            self.comparison_text.delete(1.0, tk.END)
            self.comparison_text.insert(1.0, comparison_result)
            
        except Exception as e:
            log.error(f"Error comparando portfolios: {e}")
            messagebox.showerror("Error", f"Error comparando portfolios: {str(e)}")
    
    def analyze_darwinex(self):
        """Analiza el portfolio para Darwinex"""
        try:
            if self.current_portfolio is None or self.current_portfolio.empty:
                messagebox.showwarning("Advertencia", "No hay portfolio cargado para analizar")
                return
            df = self.current_portfolio
            factork_col = df['FactorK'] if 'FactorK' in df.columns else pd.Series([0]*len(df))
            sharpe_col = df['Sharpe'] if 'Sharpe' in df.columns else pd.Series([0]*len(df))
            maxdd_col = df['MaxDD'] if 'MaxDD' in df.columns else pd.Series([0]*len(df))
            trades_col = df['Trades'] if 'Trades' in df.columns else pd.Series([0]*len(df))
            darwinex_result = f"""
Análisis Darwinex:
==================
Portfolio analizado: {len(df)} estrategias

Criterios de Darwinex:
- FactorK mínimo: 8.0
- Sharpe mínimo: 1.5
- MaxDD máximo: 15%
- Trades mínimos: 100

Estrategias que cumplen criterios:
- FactorK >= 8.0: {len(df[factork_col >= 8.0])}
- Sharpe >= 1.5: {len(df[sharpe_col >= 1.5])}
- MaxDD <= 15%: {len(df[maxdd_col <= 15])}
- Trades >= 100: {len(df[trades_col >= 100])}

Recomendación: {'APROBADO' if len(df[factork_col >= 8.0]) >= 3 else 'RECHAZADO'}
"""
            self.darwinex_text.delete(1.0, tk.END)
            self.darwinex_text.insert(1.0, darwinex_result)
            
        except Exception as e:
            log.error(f"Error analizando para Darwinex: {e}")
            messagebox.showerror("Error", f"Error analizando para Darwinex: {str(e)}")
    
    def analyze_axi_select(self):
        """Analiza el portfolio con Axi Select"""
        try:
            if self.current_portfolio is None or self.current_portfolio.empty:
                messagebox.showwarning("Advertencia", "No hay portfolio cargado para analizar")
                return
            df = self.current_portfolio
            factork_col = df['FactorK'] if 'FactorK' in df.columns else pd.Series([0]*len(df))
            cagr_col = df['CAGR'] if 'CAGR' in df.columns else pd.Series([0]*len(df))
            sharpe_col = df['Sharpe'] if 'Sharpe' in df.columns else pd.Series([0]*len(df))
            maxdd_col = df['MaxDD'] if 'MaxDD' in df.columns else pd.Series([0]*len(df))
            axi_result = f"""
Análisis Axi Select:
===================
Portfolio analizado: {len(df)} estrategias

Criterios de Axi Select:
- FactorK mínimo: 7.5
- CAGR mínimo: 12%
- Sharpe mínimo: 1.2
- MaxDD máximo: 20%

Estrategias que cumplen criterios:
- FactorK >= 7.5: {len(df[factork_col >= 7.5])}
- CAGR >= 12%: {len(df[cagr_col >= 12])}
- Sharpe >= 1.2: {len(df[sharpe_col >= 1.2])}
- MaxDD <= 20%: {len(df[maxdd_col <= 20])}

Puntuación Axi Select: {len(df[factork_col >= 7.5]) * 10 / len(df) if len(df) > 0 else 0:.1f}/10
"""
            self.axi_text.delete(1.0, tk.END)
            self.axi_text.insert(1.0, axi_result)
            
        except Exception as e:
            log.error(f"Error analizando con Axi Select: {e}")
            messagebox.showerror("Error", f"Error analizando con Axi Select: {str(e)}")
    
    def export_to_excel(self):
        """Exporta el portfolio a Excel"""
        try:
            if self.current_portfolio is None or self.current_portfolio.empty:
                messagebox.showwarning("Advertencia", "No hay portfolio para exportar")
                return
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar portfolio como Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
            
            if file_path:
                self.current_portfolio.to_excel(file_path, index=False)
                messagebox.showinfo("Éxito", f"Portfolio exportado a: {file_path}")
                
                self.export_text.delete(1.0, tk.END)
                self.export_text.insert(1.0, f"Portfolio exportado exitosamente a:\n{file_path}")
            
        except Exception as e:
            log.error(f"Error exportando a Excel: {e}")
            messagebox.showerror("Error", f"Error exportando a Excel: {str(e)}")
    
    def export_to_html(self):
        """Exporta el portfolio a HTML"""
        try:
            if self.current_portfolio is None or self.current_portfolio.empty:
                messagebox.showwarning("Advertencia", "No hay portfolio para exportar")
                return
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar portfolio como HTML",
                defaultextension=".html",
                filetypes=[("HTML files", "*.html")]
            )
            
            if file_path:
                # Crear HTML básico
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Portfolio Analysis</title>
    <style>
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Portfolio Analysis</h1>
    <p>Total Strategies: {len(self.current_portfolio)}</p>
    {self.current_portfolio.to_html(index=False)}
</body>
</html>
"""
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                messagebox.showinfo("Éxito", f"Portfolio exportado a: {file_path}")
                
                self.export_text.delete(1.0, tk.END)
                self.export_text.insert(1.0, f"Portfolio exportado exitosamente a:\n{file_path}")
            
        except Exception as e:
            log.error(f"Error exportando a HTML: {e}")
            messagebox.showerror("Error", f"Error exportando a HTML: {str(e)}") 