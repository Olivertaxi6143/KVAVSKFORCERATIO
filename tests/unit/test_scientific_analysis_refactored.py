#!/usr/bin/env python3
"""
Test para validar la refactorización del módulo scientific_analysis.py

Valida que:
1. Los stubs han sido eliminados
2. Se usan implementaciones reales del core
3. La funcionalidad básica funciona correctamente
4. No hay errores de importación
"""

import pandas as pd
import numpy as np
import pytest
import logging
from unittest.mock import Mock, patch
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analysis.scientific_analysis import (
    ScientificAnalysisFilter,
    ScientificVisualizationManager,
    AnalysisType,
    ScientificAnalysisResult,
    create_scientific_analysis_filter,
    create_scientific_visualization_manager,
    run_scientific_analysis_complete
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestScientificAnalysisRefactored:
    """Test suite para validar la refactorización del módulo scientific_analysis.py"""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        # Crear datos de prueba
        self.test_data = pd.DataFrame({
            'Strategy Name': ['Strategy_1', 'Strategy_2', 'Strategy_3'],
            'CAGR (IS)': [15.5, 12.3, 18.7],
            'CAGR (OOS)': [14.2, 11.8, 17.9],
            'Sharpe Ratio (IS)': [1.8, 1.5, 2.1],
            'Sharpe Ratio (OOS)': [1.7, 1.4, 2.0],
            'Drawdown (IS)': [-8.5, -12.3, -6.8],
            'Drawdown (OOS)': [-9.2, -13.1, -7.5],
            'Profit factor (IS)': [2.1, 1.8, 2.5],
            'Profit factor (OOS)': [2.0, 1.7, 2.4],
            'Total Trades': [150, 120, 200],
            'Total Months': [24, 18, 30]
        })
        
        logger.info("✅ Datos de prueba creados")
    
    def test_imports_successful(self):
        """Test que valida que todas las importaciones funcionan correctamente."""
        try:
            # Verificar que no hay stubs
            from src.analysis.scientific_analysis import ScientificAnalysisFilter
            from src.core.predictability_analyzer import PredictabilityAnalyzer as CorePredictabilityAnalyzer
            from src.core.robustness_analyzer import RobustnessAnalyzer as CoreRobustnessAnalyzer
            from src.analysis.predictability_metrics import PredictabilityAnalyzer as EmpiricalPredictabilityAnalyzer
            
            logger.info("✅ Todas las importaciones exitosas")
            assert True
            
        except ImportError as e:
            logger.error(f"❌ Error de importación: {e}")
            assert False, f"Error de importación: {e}"
    
    def test_analysis_types_enum(self):
        """Test que valida el enum AnalysisType."""
        analysis_types = [at.value for at in AnalysisType]
        expected_types = [
            "predictability",
            "empirical_predictability", 
            "market_regimes",
            "robustness",
            "walk_forward",
            "null_simulation",
            "tail_risk",
            "comprehensive"
        ]
        
        logger.info(f"✅ AnalysisType enum: {analysis_types}")
        assert set(analysis_types) == set(expected_types)
    
    def test_scientific_analysis_filter_initialization(self):
        """Test que valida la inicialización del filtro de análisis científico."""
        try:
            filter_instance = ScientificAnalysisFilter(self.test_data)
            
            # Verificar que se inicializaron los analizadores reales
            assert hasattr(filter_instance, 'core_predictability_analyzer')
            assert hasattr(filter_instance, 'empirical_predictability_analyzer')
            assert hasattr(filter_instance, 'robustness_analyzer')
            assert hasattr(filter_instance, 'walk_forward_analyzer')
            assert hasattr(filter_instance, 'null_simulation_analyzer')
            assert hasattr(filter_instance, 'tail_risk_analyzer')
            
            # Verificar que no hay stubs
            assert not hasattr(filter_instance, 'error_handler')
            assert not hasattr(filter_instance, 'config_manager')
            
            logger.info("✅ ScientificAnalysisFilter inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando ScientificAnalysisFilter: {e}")
            assert False, f"Error de inicialización: {e}"
    
    def test_get_available_analyses(self):
        """Test que valida la obtención de análisis disponibles."""
        filter_instance = ScientificAnalysisFilter(self.test_data)
        available_analyses = filter_instance.get_available_analyses()
        
        expected_analyses = [
            "predictability",
            "empirical_predictability",
            "market_regimes", 
            "robustness",
            "walk_forward",
            "null_simulation",
            "tail_risk",
            "comprehensive"
        ]
        
        logger.info(f"✅ Análisis disponibles: {available_analyses}")
        assert set(available_analyses) == set(expected_analyses)
    
    def test_get_filtered_strategies_info(self):
        """Test que valida la información de estrategias filtradas."""
        filter_instance = ScientificAnalysisFilter(self.test_data)
        info = filter_instance.get_filtered_strategies_info()
        
        assert "count" in info
        assert "columns" in info
        assert "memory_usage" in info
        assert "has_data" in info
        assert info["count"] == 3
        assert info["has_data"] == True
        
        logger.info(f"✅ Información de estrategias: {info}")
    
    def test_apply_scientific_analysis_structure(self):
        """Test que valida la estructura del resultado de análisis científico."""
        filter_instance = ScientificAnalysisFilter(self.test_data)
        
        # Mock de los analizadores para evitar errores de datos
        with patch.object(filter_instance.core_predictability_analyzer, 'analyze_is_oos_correlations') as mock_core:
            mock_core.return_value = {"correlations": {"test": 0.5}, "predictability_score": 0.7}
            
            result = filter_instance.apply_scientific_analysis("predictability")
            
            # Verificar estructura del resultado
            assert isinstance(result, ScientificAnalysisResult)
            assert result.analysis_type == "predictability"
            assert result.filtered_strategies_count == 3
            assert result.success == True
            assert result.timestamp > 0
            assert isinstance(result.results, dict)
            
            logger.info("✅ Estructura de resultado correcta")
    
    def test_empirical_predictability_analysis(self):
        """Test que valida el análisis de predictibilidad empírica."""
        filter_instance = ScientificAnalysisFilter(self.test_data)
        
        # Mock del analizador empírico
        with patch.object(filter_instance.empirical_predictability_analyzer, 'calculate_overall_predictability') as mock_empirical:
            # Crear mock de PredictabilityMetrics
            mock_metrics = Mock()
            mock_metrics.is_oos_consistency = 85.0
            mock_metrics.temporal_robustness = 78.0
            mock_metrics.overfitting_detection = 92.0
            mock_metrics.stability_score = 88.0
            mock_metrics.overall_predictability = 85.75
            mock_empirical.return_value = mock_metrics
            
            result = filter_instance.apply_scientific_analysis("empirical_predictability")
            
            assert result.success == True
            assert result.analysis_type == "empirical_predictability"
            assert "strategies_analyzed" in result.results
            assert "average_overall_predictability" in result.results
            
            logger.info("✅ Análisis empírico funcionando")
    
    def test_visualization_manager_initialization(self):
        """Test que valida la inicialización del gestor de visualizaciones."""
        try:
            viz_manager = ScientificVisualizationManager(self.test_data)
            
            assert hasattr(viz_manager, 'filtered_strategies')
            assert len(viz_manager.filtered_strategies) == 3
            
            logger.info("✅ ScientificVisualizationManager inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando ScientificVisualizationManager: {e}")
            assert False, f"Error de inicialización: {e}"
    
    def test_factory_functions(self):
        """Test que valida las funciones de fábrica."""
        try:
            # Test create_scientific_analysis_filter
            filter_instance = create_scientific_analysis_filter(self.test_data)
            assert isinstance(filter_instance, ScientificAnalysisFilter)
            
            # Test create_scientific_visualization_manager
            viz_manager = create_scientific_visualization_manager(self.test_data)
            assert isinstance(viz_manager, ScientificVisualizationManager)
            
            logger.info("✅ Funciones de fábrica funcionando correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en funciones de fábrica: {e}")
            assert False, f"Error en funciones de fábrica: {e}"
    
    def test_run_scientific_analysis_complete(self):
        """Test que valida la función de análisis completo."""
        try:
            # Mock de los analizadores
            with patch('src.analysis.scientific_analysis.CorePredictabilityAnalyzer') as mock_core:
                mock_instance = Mock()
                mock_instance.analyze_is_oos_correlations.return_value = {"test": 0.5}
                mock_core.return_value = mock_instance
                
                results = run_scientific_analysis_complete(
                    self.test_data, 
                    analysis_types=["predictability"]
                )
                
                assert isinstance(results, dict)
                assert "predictability" in results
                assert "metadata" in results
                
                logger.info("✅ Análisis completo funcionando")
                
        except Exception as e:
            logger.error(f"❌ Error en análisis completo: {e}")
            assert False, f"Error en análisis completo: {e}"
    
    def test_error_handling(self):
        """Test que valida el manejo de errores."""
        filter_instance = ScientificAnalysisFilter(self.test_data)
        
        # Test con tipo de análisis inválido
        result = filter_instance.apply_scientific_analysis("invalid_analysis")
        
        assert result.success == False
        assert result.error_message is not None
        assert "invalid_analysis" in result.error_message
        
        logger.info("✅ Manejo de errores funcionando")
    
    def test_empty_dataframe_handling(self):
        """Test que valida el manejo de DataFrames vacíos."""
        empty_df = pd.DataFrame()
        filter_instance = ScientificAnalysisFilter(empty_df)
        
        result = filter_instance.apply_scientific_analysis("predictability")
        
        assert result.success == False
        assert result.filtered_strategies_count == 0
        assert "No hay estrategias filtradas" in result.error_message
        
        logger.info("✅ Manejo de DataFrame vacío funcionando")

def test_integration_with_real_data():
    """Test de integración con datos reales del proyecto."""
    try:
        # Crear datos más realistas
        real_data = pd.DataFrame({
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
        
        # Crear instancia y probar funcionalidad básica
        filter_instance = ScientificAnalysisFilter(real_data)
        
        # Verificar que se puede obtener información
        info = filter_instance.get_filtered_strategies_info()
        assert info["count"] == 3
        assert info["has_data"] == True
        
        # Verificar que se pueden obtener análisis disponibles
        analyses = filter_instance.get_available_analyses()
        assert len(analyses) > 0
        
        logger.info("✅ Integración con datos reales exitosa")
        
    except Exception as e:
        logger.error(f"❌ Error en integración con datos reales: {e}")
        assert False, f"Error en integración: {e}"

if __name__ == "__main__":
    # Ejecutar tests
    logger.info("🚀 Iniciando tests de refactorización de scientific_analysis.py")
    
    test_instance = TestScientificAnalysisRefactored()
    
    # Ejecutar tests en orden
    test_instance.setup_method()
    test_instance.test_imports_successful()
    test_instance.test_analysis_types_enum()
    test_instance.test_scientific_analysis_filter_initialization()
    test_instance.test_get_available_analyses()
    test_instance.test_get_filtered_strategies_info()
    test_instance.test_apply_scientific_analysis_structure()
    test_instance.test_empirical_predictability_analysis()
    test_instance.test_visualization_manager_initialization()
    test_instance.test_factory_functions()
    test_instance.test_run_scientific_analysis_complete()
    test_instance.test_error_handling()
    test_instance.test_empty_dataframe_handling()
    
    # Test de integración
    test_integration_with_real_data()
    
    logger.info("✅ Todos los tests de refactorización completados exitosamente") 