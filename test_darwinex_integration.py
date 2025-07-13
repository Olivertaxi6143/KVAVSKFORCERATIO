#!/usr/bin/env python3
"""
Test de integración para DarwinEXPipeline en la GUI
==================================================

Valida que la integración de DarwinEXPipeline funcione correctamente
en la GUI con todas sus funcionalidades.
"""

import sys
import os
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading
import time

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.gui_enhanced_rank import EnhancedRankGUI
from src.analysis.darwinex_pipeline import DarwinEXPipeline, PipelineResult

class TestDarwinEXIntegration:
    """Test de integración para DarwinEXPipeline."""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.gui = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'total': 0
        }
    
    def _setup_logger(self):
        """Configura el logger para los tests."""
        import logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Registra el resultado de un test."""
        self.test_results['total'] += 1
        if passed:
            self.test_results['passed'] += 1
            self.logger.info(f"✅ {test_name}: PASSED - {message}")
        else:
            self.test_results['failed'] += 1
            self.logger.error(f"❌ {test_name}: FAILED - {message}")
    
    def create_test_data(self):
        """Crea datos de prueba para DarwinEX."""
        np.random.seed(42)
        
        # Crear estrategias de ejemplo
        n_strategies = 20
        
        data = {
            'Strategy_Name': [f'Strategy_{i+1}' for i in range(n_strategies)],
            'D_Score': np.random.uniform(50, 90, n_strategies),
            'Years_Running': np.random.uniform(0.5, 5.0, n_strategies),
            'LEA': np.random.uniform(-0.1, 0.3, n_strategies),
            'OS': np.random.uniform(-0.1, 0.3, n_strategies),
            'Correlation_6m': np.random.uniform(0.1, 0.4, n_strategies),
            'Frequency_Stability': np.random.uniform(0.2, 0.8, n_strategies),
            'DD_Correlation': np.random.uniform(0.3, 0.7, n_strategies),
            'Max_Drawdown': np.random.uniform(5, 25, n_strategies),
            'Unified_Score': np.random.uniform(0.3, 0.9, n_strategies),
            'CAGR': np.random.uniform(5, 50, n_strategies),
            'Sharpe_Ratio': np.random.uniform(0.5, 3.0, n_strategies),
            'Profit_factor': np.random.uniform(1.1, 3.0, n_strategies),
            'Drawdown': np.random.uniform(5, 25, n_strategies)
        }
        
        return pd.DataFrame(data)
    
    def test_1_darwinex_pipeline_import(self):
        """Test 1: Importación de DarwinEXPipeline."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 1: IMPORTACIÓN DE DARWINEX PIPELINE")
        self.logger.info("=" * 60)
        
        try:
            # Verificar que se puede importar
            from src.analysis.darwinex_pipeline import DarwinEXPipeline, PipelineResult
            self.log_test("Importación DarwinEXPipeline", True, "Módulo importado correctamente")
            
            # Verificar que se puede crear instancia
            pipeline = DarwinEXPipeline()
            self.log_test("Creación de instancia", True, "Pipeline creado exitosamente")
            
            # Verificar configuración
            config = pipeline.config
            self.log_test("Configuración disponible", bool(config), f"Configuración con {len(config)} secciones")
            
        except Exception as e:
            self.log_test("Importación DarwinEXPipeline", False, f"Error: {str(e)}")
    
    def test_2_darwinex_pipeline_execution(self):
        """Test 2: Ejecución del pipeline DarwinEX."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 2: EJECUCIÓN DEL PIPELINE DARWINEX")
        self.logger.info("=" * 60)
        
        try:
            # Crear datos de prueba
            test_data = self.create_test_data()
            self.log_test("Creación datos de prueba", True, f"{len(test_data)} estrategias creadas")
            
            # Crear pipeline
            pipeline = DarwinEXPipeline()
            
            # Ejecutar pipeline
            results = pipeline.run_pipeline(test_data)
            self.log_test("Ejecución pipeline", True, f"{len(results)} resultados generados")
            
            # Verificar estructura de resultados
            if results:
                first_result = results[0]
                required_attrs = ['strategy_name', 'passed_filters', 'failed_filters', 
                                'final_score', 'ticket_size', 'category']
                
                all_attrs_present = all(hasattr(first_result, attr) for attr in required_attrs)
                self.log_test("Estructura de resultados", all_attrs_present, 
                             f"Atributos requeridos: {required_attrs}")
                
                # Verificar tipos de datos
                score_valid = isinstance(first_result.final_score, (int, float))
                ticket_valid = isinstance(first_result.ticket_size, (int, float))
                self.log_test("Tipos de datos", score_valid and ticket_valid, 
                             f"Score: {type(first_result.final_score)}, Ticket: {type(first_result.ticket_size)}")
            
        except Exception as e:
            self.log_test("Ejecución pipeline", False, f"Error: {str(e)}")
    
    def test_3_darwinex_gui_integration(self):
        """Test 3: Integración en la GUI."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 3: INTEGRACIÓN EN LA GUI")
        self.logger.info("=" * 60)
        
        try:
            # Crear GUI
            self.gui = EnhancedRankGUI()
            self.log_test("Creación GUI", True, "GUI creada exitosamente")
            
            # Verificar que existe la pestaña DarwinEX
            has_darwinex_tab = hasattr(self.gui, 'tab_darwinex')
            self.log_test("Pestaña DarwinEX creada", has_darwinex_tab, 
                         "Pestaña DarwinEX presente en GUI")
            
            # Verificar métodos de DarwinEX
            required_methods = [
                '_build_darwinex_tab',
                '_run_darwinex_pipeline',
                '_show_darwinex_results_in_gui',
                '_show_darwinex_error',
                '_show_darwinex_results',
                '_build_approved_strategies_tab',
                '_build_rejected_strategies_tab',
                '_build_metrics_tab',
                '_export_darwinex_report',
                '_clear_darwinex_results'
            ]
            
            methods_present = all(hasattr(self.gui, method) for method in required_methods)
            self.log_test("Métodos DarwinEX", methods_present, 
                         f"Métodos requeridos: {len(required_methods)}")
            
            # Verificar variables de DarwinEX
            has_darwinex_vars = hasattr(self.gui, 'darwinex_text') and hasattr(self.gui, 'darwinex_results_frame')
            self.log_test("Variables DarwinEX", has_darwinex_vars, "Variables de interfaz presentes")
            
        except Exception as e:
            self.log_test("Integración GUI", False, f"Error: {str(e)}")
        finally:
            if self.gui:
                self.gui.destroy()
    
    def test_4_darwinex_pipeline_report(self):
        """Test 4: Generación de reportes del pipeline."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 4: GENERACIÓN DE REPORTES")
        self.logger.info("=" * 60)
        
        try:
            # Crear datos y pipeline
            test_data = self.create_test_data()
            pipeline = DarwinEXPipeline()
            results = pipeline.run_pipeline(test_data)
            
            # Generar reporte
            report = pipeline.generate_pipeline_report(results)
            self.log_test("Generación de reporte", bool(report), "Reporte generado exitosamente")
            
            # Verificar estructura del reporte
            if report:
                required_sections = ['summary', 'ticket_categories', 'top_strategies', 
                                   'risk_alerts', 'recommendations']
                
                sections_present = all(section in report for section in required_sections)
                self.log_test("Estructura del reporte", sections_present, 
                             f"Secciones requeridas: {required_sections}")
                
                # Verificar contenido del resumen
                if 'summary' in report:
                    summary = report['summary']
                    has_total = 'total_strategies' in summary
                    has_passed = 'passed_strategies' in summary
                    has_rejected = 'rejected_strategies' in summary
                    
                    self.log_test("Contenido del resumen", has_total and has_passed and has_rejected,
                                 f"Total: {has_total}, Passed: {has_passed}, Rejected: {has_rejected}")
            
        except Exception as e:
            self.log_test("Generación de reporte", False, f"Error: {str(e)}")
    
    def test_5_darwinex_pipeline_filters(self):
        """Test 5: Validación de filtros del pipeline."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 5: VALIDACIÓN DE FILTROS")
        self.logger.info("=" * 60)
        
        try:
            # Crear pipeline
            pipeline = DarwinEXPipeline()
            
            # Verificar configuración de filtros
            config = pipeline.config
            filters_config = config.get('filters', {})
            
            required_filters = [
                'gold_access', 'track_record', 'lea_os_positive',
                'correlation_6m', 'discipline', 'dd_correlation'
            ]
            
            filters_present = all(filter_name in filters_config for filter_name in required_filters)
            self.log_test("Configuración de filtros", filters_present,
                         f"Filtros requeridos: {required_filters}")
            
            # Verificar configuración de scoring
            scoring_config = config.get('scoring', {})
            weights = scoring_config.get('weights', {})
            thresholds = scoring_config.get('thresholds', {})
            
            has_weights = len(weights) > 0
            has_thresholds = len(thresholds) > 0
            
            self.log_test("Configuración de scoring", has_weights and has_thresholds,
                         f"Weights: {len(weights)}, Thresholds: {len(thresholds)}")
            
        except Exception as e:
            self.log_test("Validación de filtros", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Ejecuta todos los tests de integración."""
        self.logger.info("🚀 INICIANDO TESTS DE INTEGRACIÓN DARWINEX")
        self.logger.info("=" * 60)
        
        # Ejecutar tests
        self.test_1_darwinex_pipeline_import()
        self.test_2_darwinex_pipeline_execution()
        self.test_3_darwinex_gui_integration()
        self.test_4_darwinex_pipeline_report()
        self.test_5_darwinex_pipeline_filters()
        
        # Mostrar resumen
        self.logger.info("=" * 60)
        self.logger.info("📊 RESUMEN DE TESTS DARWINEX")
        self.logger.info("=" * 60)
        self.logger.info(f"Total de tests: {self.test_results['total']}")
        self.logger.info(f"Tests pasados: {self.test_results['passed']}")
        self.logger.info(f"Tests fallidos: {self.test_results['failed']}")
        
        success_rate = (self.test_results['passed'] / self.test_results['total']) * 100
        self.logger.info(f"Tasa de éxito: {success_rate:.1f}%")
        
        if self.test_results['failed'] == 0:
            self.logger.info("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        else:
            self.logger.warning(f"⚠️ {self.test_results['failed']} tests fallaron")
        
        return self.test_results['failed'] == 0

def main():
    """Función principal para ejecutar los tests."""
    tester = TestDarwinEXIntegration()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ INTEGRACIÓN DARWINEX VALIDADA EXITOSAMENTE")
        return 0
    else:
        print("\n❌ HAY ERRORES EN LA INTEGRACIÓN DARWINEX")
        return 1

if __name__ == "__main__":
    exit(main()) 