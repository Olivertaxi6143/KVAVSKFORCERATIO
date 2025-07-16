#!/usr/bin/env python3
"""
Integración GUI con Base de Datos ISA
=====================================

Integración completa de la GUI con la base de datos ISA:
- Conectar GUI con base de datos
- Implementar persistencia de análisis
- Crear dashboard de métricas de entrenamiento
- Implementar exportación de datos de entrenamiento
- Crear sistema de monitoreo de modelos

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import warnings

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QTableWidget, QTableWidgetItem, QPushButton, 
                               QLabel, QProgressBar, QComboBox, QSpinBox,
                               QTextEdit, QGroupBox, QGridLayout, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject
from PySide6.QtGui import QFont, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.data.isa_database import ISADatabase
from src.ml.isa_training_enhanced import ISAModelTrainer, ModelConfig
from src.logger_config import setup_logger

logger = setup_logger(__name__)
warnings.filterwarnings('ignore')

class ISAMonitoringWorker(QObject):
    """Worker para monitoreo de modelos en segundo plano."""
    
    model_updated = Signal(dict)
    training_progress = Signal(int)
    error_occurred = Signal(str)
    
    def __init__(self, isa_database: ISADatabase, model_trainer: ISAModelTrainer):
        super().__init__()
        self.isa_database = isa_database
        self.model_trainer = model_trainer
        self.running = False
    
    def start_monitoring(self):
        """Inicia el monitoreo de modelos."""
        self.running = True
        logger.info("🔍 Monitoreo de modelos iniciado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo de modelos."""
        self.running = False
        logger.info("⏹️ Monitoreo de modelos detenido")
    
    def check_model_performance(self):
        """Verifica el rendimiento de los modelos."""
        try:
            # Obtener estadísticas de la base de datos
            stats = self.isa_database.get_database_stats()
            
            # Verificar modelos activos
            models_info = self._get_active_models_info()
            
            # Emitir señal con información actualizada
            monitoring_data = {
                'database_stats': stats,
                'active_models': models_info,
                'timestamp': datetime.now().isoformat()
            }
            
            self.model_updated.emit(monitoring_data)
            
        except Exception as e:
            self.error_occurred.emit(f"Error en monitoreo: {e}")
    
    def _get_active_models_info(self) -> List[Dict[str, Any]]:
        """Obtiene información de modelos activos."""
        try:
            models_dir = Path("models")
            if not models_dir.exists():
                return []
            
            models_info = []
            for model_file in models_dir.glob("*.pkl"):
                model_info = {
                    'name': model_file.stem,
                    'path': str(model_file),
                    'size_mb': model_file.stat().st_size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(model_file.stat().st_mtime).isoformat()
                }
                models_info.append(model_info)
            
            return models_info
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo información de modelos: {e}")
            return []

class ISADashboardWidget(QWidget):
    """
    Dashboard de métricas de entrenamiento ISA.
    
    Funcionalidades:
    - Dashboard de métricas de entrenamiento
    - Visualización de rendimiento de modelos
    - Estadísticas de la base de datos
    - Monitoreo en tiempo real
    """
    
    def __init__(self, isa_database: ISADatabase, model_trainer: ISAModelTrainer):
        super().__init__()
        self.isa_database = isa_database
        self.model_trainer = model_trainer
        
        # Configurar worker de monitoreo
        self.monitoring_worker = ISAMonitoringWorker(isa_database, model_trainer)
        self.monitoring_thread = QThread()
        self.monitoring_worker.moveToThread(self.monitoring_thread)
        
        # Conectar señales
        self.monitoring_worker.model_updated.connect(self.update_dashboard)
        self.monitoring_worker.error_occurred.connect(self.handle_monitoring_error)
        
        # Configurar timer para actualizaciones
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.monitoring_worker.check_model_performance)
        
        self._setup_ui()
        self._start_monitoring()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("📊 Dashboard ISA - Métricas de Entrenamiento")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Tabs
        self.tab_widget = QTabWidget()
        
        # Tab de estadísticas generales
        self.stats_tab = self._create_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "📈 Estadísticas Generales")
        
        # Tab de modelos
        self.models_tab = self._create_models_tab()
        self.tab_widget.addTab(self.models_tab, "🤖 Modelos ML")
        
        # Tab de monitoreo
        self.monitoring_tab = self._create_monitoring_tab()
        self.tab_widget.addTab(self.monitoring_tab, "🔍 Monitoreo")
        
        layout.addWidget(self.tab_widget)
        
        # Botones de control
        control_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.clicked.connect(self.refresh_dashboard)
        control_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("📤 Exportar Datos")
        self.export_btn.clicked.connect(self.export_training_data)
        control_layout.addWidget(self.export_btn)
        
        self.backup_btn = QPushButton("💾 Crear Backup")
        self.backup_btn.clicked.connect(self.create_database_backup)
        control_layout.addWidget(self.backup_btn)
        
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
    
    def _create_stats_tab(self) -> QWidget:
        """Crea el tab de estadísticas generales."""
        widget = QWidget()
        layout = QGridLayout()
        
        # Estadísticas de la base de datos
        stats_group = QGroupBox("📊 Estadísticas de Base de Datos")
        stats_layout = QGridLayout()
        
        self.stats_labels = {}
        stats_fields = [
            'strategies_count', 'analysis_results_count', 'portfolios_count',
            'system_logs_count', 'performance_metrics_count', 'ml_models_count'
        ]
        
        for i, field in enumerate(stats_fields):
            label = QLabel(f"{field.replace('_', ' ').title()}:")
            value = QLabel("0")
            value.setStyleSheet("font-weight: bold; color: #2E86AB;")
            
            stats_layout.addWidget(label, i // 2, (i % 2) * 2)
            stats_layout.addWidget(value, i // 2, (i % 2) * 2 + 1)
            
            self.stats_labels[field] = value
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group, 0, 0, 1, 2)
        
        # Gráfico de actividad
        self.activity_figure = Figure(figsize=(8, 4))
        self.activity_canvas = FigureCanvas(self.activity_figure)
        layout.addWidget(self.activity_canvas, 1, 0, 1, 2)
        
        widget.setLayout(layout)
        return widget
    
    def _create_models_tab(self) -> QWidget:
        """Crea el tab de modelos ML."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tabla de modelos
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(5)
        self.models_table.setHorizontalHeaderLabels([
            "Modelo", "Tipo", "Tamaño (MB)", "Última Modificación", "Estado"
        ])
        layout.addWidget(self.models_table)
        
        # Controles de modelos
        controls_layout = QHBoxLayout()
        
        self.train_btn = QPushButton("🚀 Entrenar Nuevo Modelo")
        self.train_btn.clicked.connect(self.train_new_model)
        controls_layout.addWidget(self.train_btn)
        
        self.evaluate_btn = QPushButton("📊 Evaluar Modelo")
        self.evaluate_btn.clicked.connect(self.evaluate_selected_model)
        controls_layout.addWidget(self.evaluate_btn)
        
        layout.addLayout(controls_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _create_monitoring_tab(self) -> QWidget:
        """Crea el tab de monitoreo."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Estado del monitoreo
        status_group = QGroupBox("🔍 Estado del Monitoreo")
        status_layout = QVBoxLayout()
        
        self.monitoring_status = QLabel("🟢 Monitoreo Activo")
        self.monitoring_status.setStyleSheet("font-weight: bold; color: green;")
        status_layout.addWidget(self.monitoring_status)
        
        self.last_update = QLabel("Última actualización: Nunca")
        status_layout.addWidget(self.last_update)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Log de eventos
        log_group = QGroupBox("📝 Log de Eventos")
        log_layout = QVBoxLayout()
        
        self.event_log = QTextEdit()
        self.event_log.setMaximumHeight(200)
        self.event_log.setReadOnly(True)
        log_layout.addWidget(self.event_log)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Controles de monitoreo
        monitoring_controls = QHBoxLayout()
        
        self.start_monitoring_btn = QPushButton("▶️ Iniciar Monitoreo")
        self.start_monitoring_btn.clicked.connect(self.start_monitoring)
        monitoring_controls.addWidget(self.start_monitoring_btn)
        
        self.stop_monitoring_btn = QPushButton("⏹️ Detener Monitoreo")
        self.stop_monitoring_btn.clicked.connect(self.stop_monitoring)
        self.stop_monitoring_btn.setEnabled(False)
        monitoring_controls.addWidget(self.stop_monitoring_btn)
        
        layout.addLayout(monitoring_controls)
        
        widget.setLayout(layout)
        return widget
    
    def _start_monitoring(self):
        """Inicia el monitoreo."""
        try:
            self.monitoring_thread.start()
            self.monitoring_worker.start_monitoring()
            self.update_timer.start(30000)  # Actualizar cada 30 segundos
            
            self.start_monitoring_btn.setEnabled(False)
            self.stop_monitoring_btn.setEnabled(True)
            self.monitoring_status.setText("🟢 Monitoreo Activo")
            self.monitoring_status.setStyleSheet("font-weight: bold; color: green;")
            
            self.log_event("Monitoreo iniciado")
            
        except Exception as e:
            self.log_event(f"Error iniciando monitoreo: {e}")
    
    def stop_monitoring(self):
        """Detiene el monitoreo."""
        try:
            self.monitoring_worker.stop_monitoring()
            self.update_timer.stop()
            
            self.start_monitoring_btn.setEnabled(True)
            self.stop_monitoring_btn.setEnabled(False)
            self.monitoring_status.setText("🔴 Monitoreo Detenido")
            self.monitoring_status.setStyleSheet("font-weight: bold; color: red;")
            
            self.log_event("Monitoreo detenido")
            
        except Exception as e:
            self.log_event(f"Error deteniendo monitoreo: {e}")
    
    def update_dashboard(self, data: Dict[str, Any]):
        """Actualiza el dashboard con nuevos datos."""
        try:
            # Actualizar estadísticas
            stats = data.get('database_stats', {})
            for field, label in self.stats_labels.items():
                value = stats.get(field, 0)
                label.setText(str(value))
            
            # Actualizar tabla de modelos
            self._update_models_table(data.get('active_models', []))
            
            # Actualizar gráfico de actividad
            self._update_activity_chart(stats)
            
            # Actualizar timestamp
            timestamp = data.get('timestamp', '')
            if timestamp:
                self.last_update.setText(f"Última actualización: {timestamp}")
            
            self.log_event("Dashboard actualizado")
            
        except Exception as e:
            self.log_event(f"Error actualizando dashboard: {e}")
    
    def _update_models_table(self, models_info: List[Dict[str, Any]]):
        """Actualiza la tabla de modelos."""
        try:
            self.models_table.setRowCount(len(models_info))
            
            for i, model_info in enumerate(models_info):
                self.models_table.setItem(i, 0, QTableWidgetItem(model_info.get('name', '')))
                self.models_table.setItem(i, 1, QTableWidgetItem('ML Model'))
                self.models_table.setItem(i, 2, QTableWidgetItem(f"{model_info.get('size_mb', 0):.2f}"))
                self.models_table.setItem(i, 3, QTableWidgetItem(model_info.get('modified', '')))
                self.models_table.setItem(i, 4, QTableWidgetItem('🟢 Activo'))
            
        except Exception as e:
            logger.error(f"❌ Error actualizando tabla de modelos: {e}")
    
    def _update_activity_chart(self, stats: Dict[str, Any]):
        """Actualiza el gráfico de actividad."""
        try:
            self.activity_figure.clear()
            ax = self.activity_figure.add_subplot(111)
            
            # Datos para el gráfico
            categories = ['Strategies', 'Analysis', 'Portfolios', 'Logs', 'Metrics', 'Models']
            values = [
                stats.get('strategies_count', 0),
                stats.get('analysis_results_count', 0),
                stats.get('portfolios_count', 0),
                stats.get('system_logs_count', 0),
                stats.get('performance_metrics_count', 0),
                stats.get('ml_models_count', 0)
            ]
            
            # Crear gráfico de barras
            bars = ax.bar(categories, values, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4749'])
            ax.set_title('Actividad de Base de Datos ISA')
            ax.set_ylabel('Cantidad')
            
            # Rotar etiquetas
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Añadir valores en las barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
            
            self.activity_figure.tight_layout()
            self.activity_canvas.draw()
            
        except Exception as e:
            logger.error(f"❌ Error actualizando gráfico: {e}")
    
    def refresh_dashboard(self):
        """Actualiza manualmente el dashboard."""
        try:
            self.monitoring_worker.check_model_performance()
            self.log_event("Dashboard actualizado manualmente")
            
        except Exception as e:
            self.log_event(f"Error actualizando dashboard: {e}")
    
    def export_training_data(self):
        """Exporta datos de entrenamiento."""
        try:
            # Recolectar datos de entrenamiento
            training_data = self.model_trainer.collect_training_data()
            
            if training_data is not None:
                # Guardar como CSV
                output_path = f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                training_data.to_csv(output_path, index=False)
                
                self.log_event(f"Datos de entrenamiento exportados: {output_path}")
                QMessageBox.information(self, "Exportación Exitosa", 
                                      f"Datos exportados a: {output_path}")
            else:
                QMessageBox.warning(self, "Sin Datos", 
                                  "No hay datos de entrenamiento disponibles")
                
        except Exception as e:
            self.log_event(f"Error exportando datos: {e}")
            QMessageBox.critical(self, "Error", f"Error exportando datos: {e}")
    
    def create_database_backup(self):
        """Crea un backup de la base de datos."""
        try:
            success = self.isa_database.create_backup()
            
            if success:
                self.log_event("Backup de base de datos creado exitosamente")
                QMessageBox.information(self, "Backup Exitoso", 
                                      "Backup de base de datos creado exitosamente")
            else:
                QMessageBox.warning(self, "Error en Backup", 
                                  "Error creando backup de base de datos")
                
        except Exception as e:
            self.log_event(f"Error creando backup: {e}")
            QMessageBox.critical(self, "Error", f"Error creando backup: {e}")
    
    def train_new_model(self):
        """Entrena un nuevo modelo."""
        try:
            # Recolectar datos de entrenamiento
            training_data = self.model_trainer.collect_training_data()
            
            if training_data is None:
                QMessageBox.warning(self, "Sin Datos", 
                                  "No hay datos de entrenamiento disponibles")
                return
            
            # Preparar datos
            X = training_data.drop(columns=['strategy_id', 'Unified_Score'])
            y = training_data['Unified_Score']
            
            # Entrenar modelo
            config = ModelConfig(model_type='random_forest')
            result = self.model_trainer.train_model(X, y, config)
            
            if result:
                self.log_event(f"Nuevo modelo entrenado: {result.model_name}")
                QMessageBox.information(self, "Entrenamiento Exitoso", 
                                      f"Modelo entrenado: {result.model_name}\nR²: {result.train_score:.4f}")
                
                # Actualizar dashboard
                self.refresh_dashboard()
            else:
                QMessageBox.warning(self, "Error en Entrenamiento", 
                                  "Error entrenando el modelo")
                
        except Exception as e:
            self.log_event(f"Error entrenando modelo: {e}")
            QMessageBox.critical(self, "Error", f"Error entrenando modelo: {e}")
    
    def evaluate_selected_model(self):
        """Evalúa el modelo seleccionado."""
        try:
            current_row = self.models_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Sin Selección", 
                                  "Por favor selecciona un modelo para evaluar")
                return
            
            model_name = self.models_table.item(current_row, 0).text()
            model_path = f"models/{model_name}.pkl"
            
            # Recolectar datos de prueba
            training_data = self.model_trainer.collect_training_data()
            if training_data is None:
                QMessageBox.warning(self, "Sin Datos", 
                                  "No hay datos disponibles para evaluación")
                return
            
            # Preparar datos
            X = training_data.drop(columns=['strategy_id', 'Unified_Score'])
            y = training_data['Unified_Score']
            
            # Evaluar modelo
            metrics = self.model_trainer.evaluate_model(model_path, X, y)
            
            if metrics:
                metrics_text = "\n".join([f"{k}: {v:.4f}" for k, v in metrics.items()])
                QMessageBox.information(self, "Evaluación del Modelo", 
                                      f"Resultados de evaluación:\n\n{metrics_text}")
                self.log_event(f"Modelo evaluado: {model_name}")
            else:
                QMessageBox.warning(self, "Error en Evaluación", 
                                  "Error evaluando el modelo")
                
        except Exception as e:
            self.log_event(f"Error evaluando modelo: {e}")
            QMessageBox.critical(self, "Error", f"Error evaluando modelo: {e}")
    
    def handle_monitoring_error(self, error_msg: str):
        """Maneja errores del monitoreo."""
        self.log_event(f"Error de monitoreo: {error_msg}")
    
    def log_event(self, message: str):
        """Registra un evento en el log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {message}")
    
    def closeEvent(self, event):
        """Maneja el cierre del widget."""
        self.stop_monitoring()
        if self.monitoring_thread.isRunning():
            self.monitoring_thread.quit()
            self.monitoring_thread.wait()
        event.accept() 