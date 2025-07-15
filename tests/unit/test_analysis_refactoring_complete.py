#!/usr/bin/env python3
"""
Test Completo de Refactorización de la Carpeta Analysis
======================================================

Valida que toda la refactorización de la carpeta analysis funciona correctamente:
1. Eliminación de stubs
2. Integración con implementaciones reales
3. Funcionalidad de utilidades compartidas
4. Compatibilidad con módulos existentes

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

import pandas as pd
import numpy as np
import pytest
import logging
import sys
import os
from unittest.mock import Mock, patch
import warnings

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

class TestAnalysisRefactoringComplete:
    """Test suite completo para validar la refactorización de analysis"""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        # Crear datos de prueba realistas
        self.test_data = pd.DataFrame({
            'Strategy Name': ['EURUSD_M1_Strategy', 'GBPUSD_H1_Strategy', 'USDJPY_D1_Strategy'],
            'CAGR (IS)': [18.5, 15.2, 22.1],
            'CAGR (OOS)': [17.8, 14.9, 21.5],
            'Sharpe Ratio (IS)': [2.1, 1.8, 2.5],
            'Sharpe Ratio (OOS)': [2.0, 1.7, 2.4],
            'Drawdown (IS)': [-6.8, -9.2, -5.5],
            'Drawdown (OOS)': [-7.5, -10.1, -6.2],
            'Profit factor (IS)': [2.3, 2.0, 2.8],
            'Profit factor (OOS)': [2.2, 1.9, 2.7],
            'Total Trades': [180, 150, 220],
            'Total Months': [30, 24, 36],
            'Factor K': [8.5, 7.8, 9.2],
            'QVA Score': [85.2, 78.5, 91.3]
        })
        
        logger.info("✅ Datos de prueba creados")
    
    def test_scientific_analysis_refactored(self):
        """Test que valida la refactorización de scientific_analysis.py."""
        try:
            from src.analysis.scientific_analysis import (
                ScientificAnalysisFilter,
                AnalysisType,
                ScientificAnalysisResult
            )
            
            # Crear instancia del filtro
            filter_instance = ScientificAnalysisFilter(self.test_data)
            
            # Verificar que no hay stubs
            assert hasattr(filter_instance, 'core_predictability_analyzer')
            assert hasattr(filter_instance, 'empirical_predictability_analyzer')
            assert hasattr(filter_instance, 'robustness_analyzer')
            assert hasattr(filter_instance, 'walk_forward_analyzer')
            assert hasattr(filter_instance, 'null_simulation_analyzer')
            assert hasattr(filter_instance, 'tail_risk_analyzer')
            
            # Verificar que se pueden obtener análisis disponibles
            available_analyses = filter_instance.get_available_analyses()
            expected_analyses = [
                "predictability", "empirical_predictability", "market_regimes",
                "robustness", "walk_forward", "null_simulation", "tail_risk", "comprehensive"
            ]
            assert set(available_analyses) == set(expected_analyses)
            
            logger.info("✅ Scientific analysis refactorizado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en scientific analysis: {e}")
            assert False, f"Error en scientific analysis: {e}"
    
    def test_utils_module_creation(self):
        """Test que valida la creación del módulo de utilidades."""
        try:
            from src.analysis.utils import (
                clean_numeric_data,
                validate_dataframe,
                extract_numeric_columns,
                handle_missing_values,
                normalize_metrics
            )
            
            # Test de funciones de utilidades
            # 1. Validar DataFrame
            validation_result = validate_dataframe(self.test_data)
            assert validation_result["is_valid"] == True
            assert validation_result["total_rows"] == 3
            assert validation_result["total_columns"] == 13
            
            # 2. Extraer columnas numéricas
            numeric_cols = extract_numeric_columns(self.test_data)
            assert len(numeric_cols) > 0
            assert all(col in self.test_data.columns for col in numeric_cols)
            
            # 3. Limpiar datos numéricos
            cleaned_data = clean_numeric_data(self.test_data)
            assert len(cleaned_data) == len(self.test_data)
            
            # 4. Manejar valores faltantes
            processed_data = handle_missing_values(self.test_data, strategy="fill")
            assert len(processed_data) == len(self.test_data)
            
            # 5. Normalizar métricas
            normalized_data = normalize_metrics(self.test_data, method="standard")
            assert len(normalized_data) == len(self.test_data)
            
            logger.info("✅ Módulo de utilidades funcionando correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en módulo de utilidades: {e}")
            assert False, f"Error en módulo de utilidades: {e}"
    
    def test_predictability_metrics_integration(self):
        """Test que valida la integración con predictability_metrics.py."""
        try:
            from src.analysis.predictability_metrics import PredictabilityAnalyzer
            
            # Crear analizador
            analyzer = PredictabilityAnalyzer()
            
            # Test con una estrategia
            strategy_data = self.test_data.iloc[0]
            metrics = analyzer.calculate_overall_predictability(strategy_data)
            
            # Verificar que se calculan métricas
            assert hasattr(metrics, 'is_oos_consistency')
            assert hasattr(metrics, 'temporal_robustness')
            assert hasattr(metrics, 'overfitting_detection')
            assert hasattr(metrics, 'stability_score')
            assert hasattr(metrics, 'overall_predictability')
            
            logger.info("✅ Predictability metrics integrado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en predictability metrics: {e}")
            assert False, f"Error en predictability metrics: {e}"
    
    def test_tail_risk_metrics_integration(self):
        """Test que valida la integración con tail_risk_metrics.py."""
        try:
            from src.analysis.tail_risk_metrics import TailRiskAnalyzer
            
            # Crear analizador
            analyzer = TailRiskAnalyzer()
            
            # Crear datos de retornos simulados
            returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.025, -0.03, 0.02, -0.015])
            
            # Calcular métricas de tail risk
            metrics = analyzer.calculate_tail_risk_metrics(returns, "Test_Strategy")
            
            # Verificar que se calculan métricas
            assert hasattr(metrics, 'var_90')
            assert hasattr(metrics, 'var_95')
            assert hasattr(metrics, 'var_99')
            assert hasattr(metrics, 'cvar_90')
            assert hasattr(metrics, 'cvar_95')
            assert hasattr(metrics, 'cvar_99')
            
            logger.info("✅ Tail risk metrics integrado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en tail risk metrics: {e}")
            assert False, f"Error en tail risk metrics: {e}"
    
    def test_asesor_financiero_integration(self):
        """Test que valida la integración con asesor_financiero_inteligente.py."""
        try:
            from src.analysis.asesor_financiero_inteligente import AsesorFinancieroInteligente
            
            # Crear asesor
            asesor = AsesorFinancieroInteligente(self.test_data)
            
            # Test de análisis básico
            kpis = ['CAGR (IS)', 'Sharpe Ratio (IS)', 'Drawdown (IS)']
            results = asesor.analizar_estrategias(self.test_data, kpis)
            
            # Verificar resultados
            assert 'estrategias_analizadas' in results
            assert 'kpis_utilizados' in results
            assert 'temporalidad_detectada' in results
            assert 'factor_ajuste_temporalidad' in results
            
            logger.info("✅ Asesor financiero integrado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en asesor financiero: {e}")
            assert False, f"Error en asesor financiero: {e}"
    
    def test_advanced_analysis_integration(self):
        """Test que valida la integración con advanced_analysis_enhanced.py."""
        try:
            from src.analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
            
            # Crear analizador avanzado
            analyzer = AdvancedAnalysisEnhanced(self.test_data)
            
            # Test de análisis básico
            results = analyzer.run_complete_enhanced_analysis(['dynamic_correlation'])
            
            # Verificar que se ejecuta sin errores
            assert isinstance(results, dict)
            assert 'dynamic_correlation' in results
            
            logger.info("✅ Advanced analysis integrado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en advanced analysis: {e}")
            assert False, f"Error en advanced analysis: {e}"
    
    def test_complete_workflow(self):
        """Test que valida el flujo completo de análisis."""
        try:
            from src.analysis.scientific_analysis import run_scientific_analysis_complete
            from src.analysis.utils import validate_dataframe, clean_numeric_data
            
            # 1. Validar datos de entrada
            validation = validate_dataframe(self.test_data)
            assert validation["is_valid"] == True
            
            # 2. Limpiar datos
            cleaned_data = clean_numeric_data(self.test_data)
            assert len(cleaned_data) == len(self.test_data)
            
            # 3. Ejecutar análisis científico completo
            results = run_scientific_analysis_complete(
                cleaned_data,
                analysis_types=["predictability", "robustness"]
            )
            
            # 4. Verificar resultados
            assert isinstance(results, dict)
            assert "metadata" in results
            assert "predictability" in results
            assert "robustness" in results
            
            logger.info("✅ Flujo completo funcionando correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en flujo completo: {e}")
            assert False, f"Error en flujo completo: {e}"
    
    def test_no_stubs_remaining(self):
        """Test que verifica que no quedan stubs en el código."""
        try:
            # Verificar que no hay clases stub en scientific_analysis.py
            with open('src/analysis/scientific_analysis.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar que no hay stubs vacíos
            stub_indicators = [
                'return {"correlations": {}, "predictability_score": 0.5}',
                'return {"stability_score": 0.5, "metrics": {}}',
                'return {"walk_forward_results": {}, "validation_score": 0.5}',
                'return {"null_simulation_results": {}, "p_value": 0.05}'
            ]
            
            for indicator in stub_indicators:
                assert indicator not in content, f"Stub encontrado: {indicator}"
            
            # Verificar que se importan implementaciones reales
            real_imports = [
                'from src.core.predictability_analyzer import',
                'from src.core.robustness_analyzer import',
                'from src.analysis.predictability_metrics import',
                'from src.analysis.tail_risk_metrics import'
            ]
            
            for import_statement in real_imports:
                assert import_statement in content, f"Import real faltante: {import_statement}"
            
            logger.info("✅ No se encontraron stubs en el código")
            
        except Exception as e:
            logger.error(f"❌ Error verificando stubs: {e}")
            assert False, f"Error verificando stubs: {e}"
    
    def test_performance_validation(self):
        """Test que valida el rendimiento de la refactorización."""
        try:
            import time
            from src.analysis.scientific_analysis import ScientificAnalysisFilter
            
            # Crear instancia
            start_time = time.time()
            filter_instance = ScientificAnalysisFilter(self.test_data)
            init_time = time.time() - start_time
            
            # Verificar que la inicialización es rápida (< 1 segundo)
            assert init_time < 1.0, f"Inicialización muy lenta: {init_time:.2f}s"
            
            # Test de análisis rápido
            start_time = time.time()
            result = filter_instance.apply_scientific_analysis("predictability")
            analysis_time = time.time() - start_time
            
            # Verificar que el análisis es razonablemente rápido (< 5 segundos)
            assert analysis_time < 5.0, f"Análisis muy lento: {analysis_time:.2f}s"
            
            logger.info(f"✅ Rendimiento validado: init={init_time:.2f}s, analysis={analysis_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Error en validación de rendimiento: {e}")
            assert False, f"Error en validación de rendimiento: {e}"

def test_integration_with_gui():
    """Test que valida la integración con la GUI existente."""
    try:
        # Simular importación de módulos de GUI
        from src.gui.gui_enhanced_rank import QVAStrategyRankerGUI
        
        # Verificar que la GUI puede importar módulos de analysis
        from src.analysis.scientific_analysis import ScientificAnalysisFilter
        from src.analysis.predictability_metrics import PredictabilityAnalyzer
        from src.analysis.tail_risk_metrics import TailRiskAnalyzer
        
        logger.info("✅ Integración con GUI validada")
        
    except ImportError as e:
        logger.warning(f"⚠️ GUI no disponible para test: {e}")
        # No fallar el test si la GUI no está disponible
    except Exception as e:
        logger.error(f"❌ Error en integración con GUI: {e}")
        assert False, f"Error en integración con GUI: {e}"

if __name__ == "__main__":
    # Ejecutar tests completos
    logger.info("🚀 Iniciando tests completos de refactorización de analysis")
    
    test_instance = TestAnalysisRefactoringComplete()
    
    # Ejecutar tests en orden
    test_instance.setup_method()
    test_instance.test_scientific_analysis_refactored()
    test_instance.test_utils_module_creation()
    test_instance.test_predictability_metrics_integration()
    test_instance.test_tail_risk_metrics_integration()
    test_instance.test_asesor_financiero_integration()
    test_instance.test_advanced_analysis_integration()
    test_instance.test_complete_workflow()
    test_instance.test_no_stubs_remaining()
    test_instance.test_performance_validation()
    
    # Test de integración con GUI
    test_integration_with_gui()
    
    logger.info("✅ Todos los tests de refactorización completados exitosamente")
    logger.info("🎉 Refactorización de la carpeta analysis completada con éxito") 