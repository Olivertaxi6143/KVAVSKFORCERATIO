import logging
import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QGroupBox, QGridLayout, QProgressBar, QTextEdit, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPalette, QColor

from src.data.data_manager import DataManager
from src.core.utils.error_handler import RobustErrorHandler

log = logging.getLogger(__name__)

class PortfolioLoaderThread(QThread):
    """Hilo para cargar portfolios sin bloquear la GUI"""
    portfolio_loaded = Signal(pd.DataFrame)
    error_occurred = Signal(str)
    progress_updated = Signal(int)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.error_handler = RobustErrorHandler()
    
    def run(self):
        try:
            log.info(f"Iniciando carga de portfolio desde: {self.file_path}")
            self.progress_updated.emit(10)
            
            # Cargar datos según extensión
            if self.file_path.endswith('.csv'):
                df = pd.read_csv(self.file_path, delimiter=';', decimal=',')
            elif self.file_path.endswith('.xlsx'):
                df = pd.read_excel(self.file_path)
            else:
                raise ValueError("Formato de archivo no soportado")
            
            self.progress_updated.emit(50)
            
            # Validar y limpiar datos
            df = self._clean_portfolio_data(df)
            self.progress_updated.emit(80)
            
            # Validar estructura básica
            required_columns = ['Strategy', 'Net_Profit', 'CAGR', 'Sharpe_Ratio']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas requeridas faltantes: {missing_columns}")
            self.progress_updated.emit(100)
            
            log.info(f"Portfolio cargado exitosamente: {len(df)} estrategias")
            self.portfolio_loaded.emit(df)
            
        except Exception as e:
            error_msg = f"Error cargando portfolio: {str(e)}"
            log.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
    
    def _clean_portfolio_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y normaliza datos del portfolio"""
        # Eliminar filas vacías
        df = df.dropna(subset=['Strategy'])
        
        # Convertir columnas numéricas
        numeric_columns = ['Net_Profit', 'CAGR', 'Sharpe_Ratio', 'Max_DD', 'Profit_Factor', 'Total_Trades']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Normalizar nombres de columnas
        df.columns = [col.replace(' ', '_').replace('-', '_') for col in df.columns]
        
        return df

class PortfolioMetricsCalculator:
    """Calculadora de métricas agregadas para portfolios"""
    
    def __init__(self):
        self.error_handler = RobustErrorHandler()
    
    def calculate_portfolio_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula métricas agregadas del portfolio"""
        try:
            log.info("Calculando métricas agregadas del portfolio")
            
            metrics = {
                'total_strategies': len(df),
                'total_net_profit': df['Net_Profit'].sum() if 'Net_Profit' in df.columns else 0,
                'avg_cagr': df['CAGR'].mean() if 'CAGR' in df.columns else 0,
                'avg_sharpe': df['Sharpe_Ratio'].mean() if 'Sharpe_Ratio' in df.columns else 0,
                'avg_max_dd': df['Max_DD'].mean() if 'Max_DD' in df.columns else 0,
                'avg_profit_factor': df['Profit_Factor'].mean() if 'Profit_Factor' in df.columns else 0,
                'total_trades': df['Total_Trades'].sum() if 'Total_Trades' in df.columns else 0,
                'elite_count': len(df[df['Factor_K'] >= 9.2]) if 'Factor_K' in df.columns else 0,
                'excellent_count': len(df[(df['Factor_K'] >= 8.2) & (df['Factor_K'] < 9.2)]) if 'Factor_K' in df.columns else 0,
                'very_good_count': len(df[(df['Factor_K'] >= 7.2) & (df['Factor_K'] < 8.2)]) if 'Factor_K' in df.columns else 0
            }
            
            # Calcular correlaciones si hay suficientes datos
            if len(df) > 1:
                metrics['avg_correlation'] = self._calculate_avg_correlation(df)
            
            log.info(f"Métricas calculadas: {len(metrics)} indicadores")
            return metrics
            
        except Exception as e:
            log.error(f"Error calculando métricas: {e}", exc_info=True)
            self.error_handler.handle_error(e, "Error en cálculo de métricas")
            return {}
    
    def _calculate_avg_correlation(self, df: pd.DataFrame) -> float:
        """Calcula correlación promedio entre estrategias"""
        try:
            # Usar CAGR para correlación si está disponible
            if 'CAGR' in df.columns:
                returns = df['CAGR'].values
                if len(returns) > 1:
                    corr_matrix = np.corrcoef(returns)
                    # Promedio de correlaciones (excluyendo diagonal)
                    avg_corr = (corr_matrix.sum() - len(corr_matrix)) / (len(corr_matrix) ** 2 - len(corr_matrix))
                    return float(avg_corr)
            return 0.0
        except Exception as e:
            log.warning(f"No se pudo calcular correlación: {e}")
            return 0.0

class PortfolioAnalysisTab(QWidget):
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
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Análisis de Portfolios")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Botones de carga
        load_layout = QHBoxLayout()
        self.load_portfolio_btn = QPushButton("Cargar Portfolio")
        self.load_portfolio_btn.clicked.connect(self.load_portfolio)
        self.load_portfolio_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        load_layout.addWidget(self.load_portfolio_btn)
        
        self.clear_btn = QPushButton("Limpiar")
        self.clear_btn.clicked.connect(self.clear_portfolio)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        load_layout.addWidget(self.clear_btn)
        layout.addLayout(load_layout)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Tabs para diferentes análisis
        self.tabs = QTabWidget()
        
        # Tab de métricas agregadas
        self.metrics_tab = self.create_metrics_tab()
        self.tabs.addTab(self.metrics_tab, "Métricas Agregadas")
        
        # Tab de comparativas
        self.comparison_tab = self.create_comparison_tab()
        self.tabs.addTab(self.comparison_tab, "Comparativas")
        
        # Tab de Darwinex
        self.darwinex_tab = self.create_darwinex_tab()
        self.tabs.addTab(self.darwinex_tab, "Darwinex")
        
        # Tab de Axi Select
        self.axi_tab = self.create_axi_tab()
        self.tabs.addTab(self.axi_tab, "Axi Select")
        
        # Tab de exportación
        self.export_tab = self.create_export_tab()
        self.tabs.addTab(self.export_tab, "Exportar")
        
        layout.addWidget(self.tabs)
        
        # Tabla de estrategias
        self.strategies_table = QTableWidget()
        self.strategies_table.setAlternatingRowColors(True)
        layout.addWidget(QLabel("Estrategias del Portfolio:"))
        layout.addWidget(self.strategies_table)
        
        self.setLayout(layout)
        
        # Inicialmente deshabilitar tabs
        self.set_tabs_enabled(False)
    
    def create_metrics_tab(self) -> QWidget:
        """Crea el tab de métricas agregadas"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Grupo de métricas básicas
        basic_group = QGroupBox("Métricas Básicas")
        basic_layout = QGridLayout()
        
        self.total_strategies_label = QLabel("Total Estrategias: 0")
        self.total_net_profit_label = QLabel("Profit Total: $0")
        self.avg_cagr_label = QLabel("CAGR Promedio: 0%")
        self.avg_sharpe_label = QLabel("Sharpe Promedio: 0")
        
        basic_layout.addWidget(self.total_strategies_label, 0, 0)
        basic_layout.addWidget(self.total_net_profit_label, 0, 1)
        basic_layout.addWidget(self.avg_cagr_label, 1, 0)
        basic_layout.addWidget(self.avg_sharpe_label, 1, 1)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Grupo de métricas avanzadas
        advanced_group = QGroupBox("Métricas Avanzadas")
        advanced_layout = QGridLayout()
        
        self.avg_max_dd_label = QLabel("Max DD Promedio: 0%")
        self.avg_profit_factor_label = QLabel("Profit Factor Promedio: 0")
        self.total_trades_label = QLabel("Total Trades: 0")
        self.avg_correlation_label = QLabel("Correlación Promedio: 0")
        
        advanced_layout.addWidget(self.avg_max_dd_label, 0, 0)
        advanced_layout.addWidget(self.avg_profit_factor_label, 0, 1)
        advanced_layout.addWidget(self.total_trades_label, 1, 0)
        advanced_layout.addWidget(self.avg_correlation_label, 1, 1)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # Grupo de distribución por categorías
        categories_group = QGroupBox("Distribución por Categorías")
        categories_layout = QGridLayout()
        
        self.elite_count_label = QLabel("Elite: 0")
        self.excellent_count_label = QLabel("Excellent: 0")
        self.very_good_count_label = QLabel("Very Good: 0")
        
        categories_layout.addWidget(self.elite_count_label, 0, 0)
        categories_layout.addWidget(self.excellent_count_label, 0, 1)
        categories_layout.addWidget(self.very_good_count_label, 1, 0)
        
        categories_group.setLayout(categories_layout)
        layout.addWidget(categories_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_comparison_tab(self) -> QWidget:
        """Crea el tab de comparativas"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Botón para comparar portfolios
        self.compare_btn = QPushButton("Comparar Portfolios")
        self.compare_btn.clicked.connect(self.compare_portfolios)
        self.compare_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(self.compare_btn)
        
        # Área de resultados de comparación
        self.comparison_text = QTextEdit()
        self.comparison_text.setReadOnly(True)
        self.comparison_text.setPlaceholderText("Los resultados de comparación aparecerán aquí...")
        layout.addWidget(self.comparison_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_darwinex_tab(self) -> QWidget:
        """Crea el tab de análisis Darwinex"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Botón para análisis Darwinex
        self.darwinex_btn = QPushButton("Analizar para Darwinex")
        self.darwinex_btn.clicked.connect(self.analyze_darwinex)
        self.darwinex_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        layout.addWidget(self.darwinex_btn)
        
        # Área de resultados Darwinex
        self.darwinex_text = QTextEdit()
        self.darwinex_text.setReadOnly(True)
        self.darwinex_text.setPlaceholderText("Análisis Darwinex aparecerá aquí...")
        layout.addWidget(self.darwinex_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_axi_tab(self) -> QWidget:
        """Crea el tab de análisis Axi Select"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Botón para análisis Axi Select
        self.axi_btn = QPushButton("Analizar para Axi Select")
        self.axi_btn.clicked.connect(self.analyze_axi_select)
        self.axi_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        layout.addWidget(self.axi_btn)
        
        # Área de resultados Axi Select
        self.axi_text = QTextEdit()
        self.axi_text.setReadOnly(True)
        self.axi_text.setPlaceholderText("Análisis Axi Select aparecerá aquí...")
        layout.addWidget(self.axi_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_export_tab(self) -> QWidget:
        """Crea el tab de exportación"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Botones de exportación
        export_layout = QHBoxLayout()
        
        self.export_excel_btn = QPushButton("Exportar a Excel")
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        self.export_excel_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        export_layout.addWidget(self.export_excel_btn)
        
        self.export_html_btn = QPushButton("Exportar a HTML")
        self.export_html_btn.clicked.connect(self.export_to_html)
        self.export_html_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        export_layout.addWidget(self.export_html_btn)
        
        layout.addLayout(export_layout)
        
        # Área de estado de exportación
        self.export_text = QTextEdit()
        self.export_text.setReadOnly(True)
        self.export_text.setPlaceholderText("Estado de exportación aparecerá aquí...")
        layout.addWidget(self.export_text)
        
        widget.setLayout(layout)
        return widget
    
    def load_portfolio(self):
        """Carga un portfolio desde archivo"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Cargar Portfolio", "", 
                "Archivos CSV (*.csv);;Archivos Excel (*.xlsx);;Todos los archivos (*)"
            )
            
            if file_path:
                log.info(f"Seleccionado archivo: {file_path}")
                self.start_portfolio_loading(file_path)
                
        except Exception as e:
            log.error(f"Error en diálogo de carga: {e}", exc_info=True)
            self.error_handler.handle_error(e, "Error cargando portfolio")
    
    def start_portfolio_loading(self, file_path: str):
        """Inicia el proceso de carga en hilo separado"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.load_portfolio_btn.setEnabled(False)
        
        self.loader_thread = PortfolioLoaderThread(file_path)
        self.loader_thread.portfolio_loaded.connect(self.on_portfolio_loaded)
        self.loader_thread.error_occurred.connect(self.on_loading_error)
        self.loader_thread.progress_updated.connect(self.progress_bar.setValue)
        self.loader_thread.start()
    
    def on_portfolio_loaded(self, df: pd.DataFrame):
        """Maneja la carga exitosa del portfolio"""
        try:
            log.info(f"Portfolio cargado: {len(df)} estrategias")
            self.current_portfolio = df
            
            # Actualizar tabla
            self.update_strategies_table(df)
            
            # Calcular y mostrar métricas
            self.update_metrics(df)
            
            # Habilitar tabs
            self.set_tabs_enabled(True)
            
            # Limpiar UI
            self.progress_bar.setVisible(False)
            self.load_portfolio_btn.setEnabled(True)
            
            QMessageBox.information(self, "Éxito", f"Portfolio cargado: {len(df)} estrategias")
            
        except Exception as e:
            log.error(f"Error procesando portfolio cargado: {e}", exc_info=True)
            self.error_handler.handle_error(e, "Error procesando portfolio")
    
    def on_loading_error(self, error_msg: str):
        """Maneja errores de carga"""
        log.error(f"Error cargando portfolio: {error_msg}")
        self.progress_bar.setVisible(False)
        self.load_portfolio_btn.setEnabled(True)
        
        QMessageBox.critical(self, "Error", f"Error cargando portfolio:\n{error_msg}")
    
    def update_strategies_table(self, df: pd.DataFrame):
        """Actualiza la tabla de estrategias"""
        try:
            self.strategies_table.setRowCount(len(df))
            self.strategies_table.setColumnCount(len(df.columns))
            self.strategies_table.setHorizontalHeaderLabels(df.columns)
            
            for i, (_, row) in enumerate(df.iterrows()):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.strategies_table.setItem(i, j, item)
            
            log.info(f"Tabla actualizada con {len(df)} filas")
            
        except Exception as e:
            log.error(f"Error actualizando tabla: {e}", exc_info=True)
            self.error_handler.handle_error(e, "Error actualizando tabla")
    
    def update_metrics(self, df: pd.DataFrame):
        """Actualiza las métricas mostradas"""
        try:
            metrics = self.metrics_calculator.calculate_portfolio_metrics(df)
            
            # Actualizar labels de métricas básicas
            self.total_strategies_label.setText(f"Total Estrategias: {metrics.get('total_strategies', 0)}")
            self.total_net_profit_label.setText(f"Profit Total: ${metrics.get('total_net_profit', 0):,.2f}")
            self.avg_cagr_label.setText(f"CAGR Promedio: {metrics.get('avg_cagr', 0):.2f}%")
            self.avg_sharpe_label.setText(f"Sharpe Promedio: {metrics.get('avg_sharpe', 0):.2f}")
            
            # Actualizar labels de métricas avanzadas
            self.avg_max_dd_label.setText(f"Max DD Promedio: {metrics.get('avg_max_dd', 0):.2f}%")
            self.avg_profit_factor_label.setText(f"Profit Factor Promedio: {metrics.get('avg_profit_factor', 0):.2f}")
            self.total_trades_label.setText(f"Total Trades: {metrics.get('total_trades', 0):,}")
            self.avg_correlation_label.setText(f"Correlación Promedio: {metrics.get('avg_correlation', 0):.3f}")
            
            # Actualizar labels de categorías
            self.elite_count_label.setText(f"Elite: {metrics.get('elite_count', 0)}")
            self.excellent_count_label.setText(f"Excellent: {metrics.get('excellent_count', 0)}")
            self.very_good_count_label.setText(f"Very Good: {metrics.get('very_good_count', 0)}")
            
            log.info("Métricas actualizadas exitosamente")
            
        except Exception as e:
            log.error(f"Error actualizando métricas: {e}", exc_info=True)
            self.error_handler.handle_error(e, "Error actualizando métricas")
    
    def set_tabs_enabled(self, enabled: bool):
        """Habilita o deshabilita los tabs de análisis"""
        for i in range(self.tabs.count()):
            self.tabs.setTabEnabled(i, enabled)
    
    def clear_portfolio(self):
        """Limpia el portfolio actual"""
        try:
            self.current_portfolio = None
            self.strategies_table.setRowCount(0)
            self.strategies_table.setColumnCount(0)
            
            # Limpiar métricas
            self.total_strategies_label.setText("Total Estrategias: 0")
            self.total_net_profit_label.setText("Profit Total: $0")
            self.avg_cagr_label.setText("CAGR Promedio: 0%")
            self.avg_sharpe_label.setText("Sharpe Promedio: 0")
            self.avg_max_dd_label.setText("Max DD Promedio: 0%")
            self.avg_profit_factor_label.setText("Profit Factor Promedio: 0")
            self.total_trades_label.setText("Total Trades: 0")
            self.avg_correlation_label.setText("Correlación Promedio: 0")
            self.elite_count_label.setText("Elite: 0")
            self.excellent_count_label.setText("Excellent: 0")
            self.very_good_count_label.setText("Very Good: 0")
            
            # Deshabilitar tabs
            self.set_tabs_enabled(False)
            
            # Limpiar áreas de texto
            self.comparison_text.clear()
            self.darwinex_text.clear()
            self.axi_text.clear()
            self.export_text.clear()
            
            log.info("Portfolio limpiado")
            QMessageBox.information(self, "Limpiado", "Portfolio limpiado exitosamente")
            
        except Exception as e:
            log.error(f"Error limpiando portfolio: {e}", exc_info=True)
            self.error_handler.handle_error(e, "Error limpiando portfolio")
    
    def compare_portfolios(self):
        """Compara portfolios (placeholder)"""
        try:
            if self.current_portfolio is None:
                QMessageBox.warning(self, "Advertencia", "No hay portfolio cargado para comparar")
                return
            
            # Placeholder para comparación
            self.comparison_text.setText("Funcionalidad de comparación en desarrollo...")
            log.info("Iniciando comparación de portfolios")
            
        except Exception as e:
            log.error(f"Error en comparación: {e}", exc_info=True)
            self.error_handler.handle_error(e, "Error en comparación")
    
    def analyze_darwinex(self):
        """Analiza portfolio para Darwinex (placeholder)"""
        try:
            if self.current_portfolio is None:
                QMessageBox.warning(self, "Advertencia", "No hay portfolio cargado para analizar")
                return
            
            # Placeholder para análisis Darwinex
            self.darwinex_text.setText("Análisis Darwinex en desarrollo...")
            log.info("Iniciando análisis Darwinex")
            
        except Exception as e:
            log.error(f"Error en análisis Darwinex: {e}", exc_info=True)
            self.error_handler.handle_error(e, "Error en análisis Darwinex")
    
    def analyze_axi_select(self):
        """Analiza portfolio para Axi Select (placeholder)"""
        try:
            if self.current_portfolio is None:
                QMessageBox.warning(self, "Advertencia", "No hay portfolio cargado para analizar")
                return
            
            # Placeholder para análisis Axi Select
            self.axi_text.setText("Análisis Axi Select en desarrollo...")
            log.info("Iniciando análisis Axi Select")
            
        except Exception as e:
            log.error(f"Error en análisis Axi Select: {e}", exc_info=True)
            self.error_handler.handle_error(e, "Error en análisis Axi Select")
    
    def export_to_excel(self):
        """Exporta análisis a Excel (placeholder)"""
        try:
            if self.current_portfolio is None:
                QMessageBox.warning(self, "Advertencia", "No hay portfolio para exportar")
                return
            
            # Placeholder para exportación Excel
            self.export_text.setText("Exportación a Excel en desarrollo...")
            log.info("Iniciando exportación a Excel")
            
        except Exception as e:
            log.error(f"Error en exportación Excel: {e}", exc_info=True)
            self.error_handler.handle_error(e, "Error en exportación Excel")
    
    def export_to_html(self):
        """Exporta análisis a HTML (placeholder)"""
        try:
            if self.current_portfolio is None:
                QMessageBox.warning(self, "Advertencia", "No hay portfolio para exportar")
                return
            
            # Placeholder para exportación HTML
            self.export_text.setText("Exportación a HTML en desarrollo...")
            log.info("Iniciando exportación a HTML")
            
        except Exception as e:
            log.error(f"Error en exportación HTML: {e}", exc_info=True)
            self.error_handler.handle_error(e, "Error en exportación HTML") 