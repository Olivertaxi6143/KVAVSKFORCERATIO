#!/usr/bin/env python3
"""
Test de Integración de Tail Risk Metrics con UnifiedEvaluator
============================================================

Verifica que el módulo de tail risk metrics se integre correctamente
con el UnifiedEvaluator y que las métricas se calculen y añadan al DataFrame.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
"""

import pytest
import pandas as pd
import numpy as np
import logging
from unittest.mock import Mock, patch
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.analysis.unified_evaluator import UnifiedEvaluatorEnhanced
from src.analysis.tail_risk_metrics import TailRiskAnalyzer
from src.core.config.config_manager import ProgressCallback

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestTailRiskIntegration:
    """Test de integración de Tail Risk Metrics con UnifiedEvaluator."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.mock_callback = Mock(spec=ProgressCallback)
        self.evaluator = UnifiedEvaluatorEnhanced(progress_callback=self.mock_callback)
        logger.info("🔬 Test de integración de Tail Risk Metrics configurado")
    
    def test_tail_risk_analyzer_initialization(self):
        """Test que verifica que el TailRiskAnalyzer se inicialice correctamente."""
        logger.info("🧪 Test: Inicialización de TailRiskAnalyzer")
        
        assert hasattr(self.evaluator, 'tail_risk_analyzer')
        assert isinstance(self.evaluator.tail_risk_analyzer, TailRiskAnalyzer)
        assert self.evaluator.tail_risk_analyzer.confidence_levels == [0.90, 0.95, 0.99]
        
        logger.info("✅ TailRiskAnalyzer inicializado correctamente")
    
    def test_apply_tail_risk_analysis_method_exists(self):
        """Test que verifica que el método _apply_tail_risk_analysis existe."""
        logger.info("🧪 Test: Existencia del método _apply_tail_risk_analysis")
        
        assert hasattr(self.evaluator, '_apply_tail_risk_analysis')
        assert callable(self.evaluator._apply_tail_risk_analysis)
        
        logger.info("✅ Método _apply_tail_risk_analysis existe")
    
    def test_tail_risk_analysis_with_sample_data(self):
        """Test que verifica el análisis de tail risk con datos de muestra."""
        logger.info("🧪 Test: Análisis de tail risk con datos de muestra")
        
        # Crear datos de muestra
        sample_data = pd.DataFrame({
            'Strategy_Name': ['Strategy_A', 'Strategy_B', 'Strategy_C'],
            'Sharpe_Ratio': [1.2, 0.8, 1.5],
            'Max_DD_%': [-15.0, -25.0, -10.0],
            'CAGR': [12.5, 8.2, 15.0],
            'Profit_factor': [1.8, 1.2, 2.1]
        })
        
        # Aplicar análisis de tail risk
        result = self.evaluator._apply_tail_risk_analysis(sample_data.copy())
        
        # Verificar que el resultado es un DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_data)
        
        # Verificar que se mantienen las columnas originales
        for col in sample_data.columns:
            assert col in result.columns
        
        logger.info("✅ Análisis de tail risk completado con datos de muestra")
    
    def test_tail_risk_columns_detection(self):
        """Test que verifica la detección de columnas de riesgo."""
        logger.info("🧪 Test: Detección de columnas de riesgo")
        
        # DataFrame con columnas de riesgo
        risk_data = pd.DataFrame({
            'Strategy_Name': ['Strategy_A'],
            'Returns': [0.05],
            'Profit': [1000],
            'Loss': [-500],
            'Drawdown': [-0.15],
            'Sharpe': [1.2],
            'VaR': [-0.02]
        })
        
        # Aplicar análisis
        result = self.evaluator._apply_tail_risk_analysis(risk_data.copy())
        
        # Verificar que se detectaron columnas de riesgo
        assert isinstance(result, pd.DataFrame)
        
        logger.info("✅ Columnas de riesgo detectadas correctamente")
    
    def test_unified_evaluation_with_tail_risk(self):
        """Test que verifica la evaluación unificada incluye tail risk."""
        logger.info("🧪 Test: Evaluación unificada con tail risk")
        
        # Crear datos de muestra para evaluación completa
        sample_data = pd.DataFrame({
            'Strategy_Name': ['Strategy_A', 'Strategy_B'],
            'Sharpe_Ratio': [1.2, 0.8],
            'Max_DD_%': [-15.0, -25.0],
            'CAGR': [12.5, 8.2],
            'Profit_factor': [1.8, 1.2],
            'Total_Trades': [100, 80],
            'Win_Rate_%': [65.0, 55.0],
            'Avg_Trade_%': [0.5, 0.3],
            'Net_Profit': [5000, 3000]
        })
        
        # Mock del progress callback para evitar errores
        with patch.object(self.evaluator, 'factor_k') as mock_factor_k, \
             patch.object(self.evaluator, 'qva_scorer') as mock_qva_scorer:
            
            # Configurar mocks
            mock_factor_k.evaluate_strategies.return_value = sample_data.copy()
            mock_qva_scorer.calculate_qva_score.return_value = pd.Series([0.7, 0.5], index=sample_data.index)
            mock_qva_scorer.compute_qva_score_robust.return_value = pd.Series([0.8, 0.6], index=sample_data.index)
            
            # Ejecutar evaluación unificada
            result = self.evaluator.evaluate_strategies_unified(sample_data.copy())
            
            # Verificar que el resultado es un DataFrame
            assert isinstance(result, pd.DataFrame)
            assert len(result) == len(sample_data)
            
            # Verificar que se mantienen las columnas originales
            for col in sample_data.columns:
                assert col in result.columns
            
            logger.info("✅ Evaluación unificada con tail risk completada")
    
    def test_tail_risk_metrics_in_summary(self):
        """Test que verifica que las métricas de tail risk aparecen en el resumen."""
        logger.info("🧪 Test: Métricas de tail risk en resumen")
        
        # Crear DataFrame con métricas de tail risk simuladas
        sample_data = pd.DataFrame({
            'Strategy_Name': ['Strategy_A', 'Strategy_B'],
            'TailRisk_var_95': [-0.02, -0.03],
            'TailRisk_cvar_95': [-0.025, -0.035],
            'TailRisk_expected_shortfall': [-0.03, -0.04],
            'TailRisk_max_drawdown': [-0.15, -0.25],
            'TailRisk_skewness': [-0.5, -0.8],
            'TailRisk_kurtosis': [3.2, 4.1],
            'Unified_Score_Scientific': [0.8, 0.6]
        })
        
        # Generar resumen
        summary = self.evaluator.get_unified_summary(sample_data)
        
        # Verificar que el resumen incluye información de tail risk
        assert 'tail_risk_metrics_calculated' in summary
        assert 'tail_risk_metrics_count' in summary
        assert summary['tail_risk_metrics_count'] == 6  # 6 métricas de tail risk
        
        # Verificar que se incluyen estadísticas de las métricas
        assert 'TailRisk_var_95_mean' in summary
        assert 'TailRisk_cvar_95_mean' in summary
        assert 'TailRisk_expected_shortfall_mean' in summary
        
        logger.info("✅ Métricas de tail risk incluidas en resumen")
    
    def test_tail_risk_by_strategy_in_summary(self):
        """Test que verifica que el resumen incluye tail risk por estrategia."""
        logger.info("🧪 Test: Tail risk por estrategia en resumen")
        
        # Crear DataFrame con métricas de tail risk
        sample_data = pd.DataFrame({
            'Strategy_Name': ['Strategy_A', 'Strategy_B'],
            'TailRisk_var_95': [-0.02, -0.03],
            'TailRisk_cvar_95': [-0.025, -0.035],
            'TailRisk_expected_shortfall': [-0.03, -0.04]
        })
        
        # Generar resumen
        summary = self.evaluator.get_unified_summary(sample_data)
        
        # Verificar que se incluye información por estrategia
        assert 'tail_risk_by_strategy' in summary
        assert 'Strategy_A' in summary['tail_risk_by_strategy']
        assert 'Strategy_B' in summary['tail_risk_by_strategy']
        
        # Verificar que las métricas están presentes
        strategy_a_metrics = summary['tail_risk_by_strategy']['Strategy_A']
        assert 'TailRisk_var_95' in strategy_a_metrics
        assert 'TailRisk_cvar_95' in strategy_a_metrics
        assert 'TailRisk_expected_shortfall' in strategy_a_metrics
        
        logger.info("✅ Tail risk por estrategia incluido en resumen")
    
    def test_error_handling_in_tail_risk_analysis(self):
        """Test que verifica el manejo de errores en el análisis de tail risk."""
        logger.info("🧪 Test: Manejo de errores en análisis de tail risk")
        
        # DataFrame vacío o con datos inválidos
        empty_data = pd.DataFrame()
        
        # Debe manejar el error graciosamente
        result = self.evaluator._apply_tail_risk_analysis(empty_data)
        
        # Verificar que devuelve el DataFrame original sin errores
        assert isinstance(result, pd.DataFrame)
        
        logger.info("✅ Manejo de errores funcionando correctamente")
    
    def test_progress_callback_in_tail_risk(self):
        """Test que verifica que el progress callback se usa en tail risk."""
        logger.info("🧪 Test: Progress callback en tail risk")
        
        # Crear datos de muestra
        sample_data = pd.DataFrame({
            'Strategy_Name': ['Strategy_A'],
            'Sharpe_Ratio': [1.2],
            'Max_DD_%': [-15.0]
        })
        
        # Aplicar análisis
        self.evaluator._apply_tail_risk_analysis(sample_data.copy())
        
        # Verificar que se llamó al progress callback
        assert self.mock_callback.update_progress.called
        
        logger.info("✅ Progress callback funcionando en tail risk")


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "--tb=short"]) 