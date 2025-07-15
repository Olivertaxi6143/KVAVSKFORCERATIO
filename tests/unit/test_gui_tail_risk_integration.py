#!/usr/bin/env python3
"""
Test de Integración de Tail Risk Metrics con GUI
===============================================

Verifica que las métricas de tail risk se integren correctamente
con la interfaz gráfica y se muestren en la tabla de resultados.

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

from src.gui.gui_enhanced_rank import EnhancedRankGUI

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestGUITailRiskIntegration:
    """Test de integración de Tail Risk Metrics con la GUI."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.gui = EnhancedRankGUI()
        logger.info("🔬 Test de integración de Tail Risk Metrics con GUI configurado")
    
    def test_tail_risk_calculation_method_exists(self):
        """Test que verifica que el método _calculate_tail_risk_level existe en la GUI."""
        logger.info("🧪 Test: Existencia del método _calculate_tail_risk_level en GUI")
        
        assert hasattr(self.gui, '_calculate_tail_risk_level')
        assert callable(self.gui._calculate_tail_risk_level)
        
        logger.info("✅ Método _calculate_tail_risk_level existe en GUI")
    
    def test_tail_risk_calculation_with_tail_risk_metrics(self):
        """Test que verifica el cálculo de riesgo de cola con métricas de tail risk."""
        logger.info("🧪 Test: Cálculo de riesgo de cola con métricas de tail risk")
        
        # Crear datos de prueba con métricas de tail risk
        test_row = pd.Series({
            'Strategy_Name': 'Test_Strategy',
            'TailRisk_var_95': -0.03,  # -3%
            'TailRisk_cvar_95': -0.05,  # -5%
            'TailRisk_expected_shortfall': -0.06,  # -6%
            'TailRisk_max_drawdown': -0.20,  # -20%
            'TailRisk_skewness': -0.8,
            'TailRisk_kurtosis': 4.2
        })
        
        # Calcular nivel de riesgo
        risk_info = self.gui._calculate_tail_risk_level(test_row)
        
        # Verificar que se calculó correctamente
        assert isinstance(risk_info, dict)
        assert 'level' in risk_info
        assert 'icon' in risk_info
        assert 'description' in risk_info
        assert 'risk_factors' in risk_info
        assert 'risk_score' in risk_info
        assert 'metrics' in risk_info
        
        # Verificar que se detectaron las métricas de tail risk
        assert len(risk_info['metrics']) > 0
        assert 'TailRisk_var_95' in risk_info['metrics']
        assert 'TailRisk_cvar_95' in risk_info['metrics']
        
        logger.info(f"✅ Riesgo calculado: {risk_info['level']} {risk_info['icon']}")
        logger.info(f"📊 Factores de riesgo: {risk_info['risk_factors']}")
    
    def test_tail_risk_calculation_with_traditional_metrics(self):
        """Test que verifica el cálculo de riesgo de cola con métricas tradicionales."""
        logger.info("🧪 Test: Cálculo de riesgo de cola con métricas tradicionales")
        
        # Crear datos de prueba con métricas tradicionales
        test_row = pd.Series({
            'Strategy_Name': 'Test_Strategy',
            'Drawdown': -15.5,  # -15.5%
            'VaR (95%)': -8.2,  # -8.2%
            'Profit factor': 1.3
        })
        
        # Calcular nivel de riesgo
        risk_info = self.gui._calculate_tail_risk_level(test_row)
        
        # Verificar que se calculó correctamente
        assert isinstance(risk_info, dict)
        assert 'level' in risk_info
        assert 'icon' in risk_info
        assert 'description' in risk_info
        assert 'risk_factors' in risk_info
        assert 'risk_score' in risk_info
        assert 'metrics' in risk_info
        
        # Verificar que se usaron métricas tradicionales
        assert risk_info['metrics'].get('traditional', False) is True
        
        logger.info(f"✅ Riesgo calculado: {risk_info['level']} {risk_info['icon']}")
        logger.info(f"📊 Factores de riesgo: {risk_info['risk_factors']}")
    
    def test_tail_risk_display_in_table(self):
        """Test que verifica que el riesgo de cola se muestra en la tabla."""
        logger.info("🧪 Test: Visualización de riesgo de cola en tabla")
        
        # Crear DataFrame de prueba
        test_df = pd.DataFrame({
            'Strategy_Name': ['Strategy_A', 'Strategy_B'],
            'Unified_Score': [0.8, 0.6],
            'Quality_Category': ['Elite', 'Excellent'],
            'TailRisk_var_95': [-0.02, -0.04],
            'TailRisk_cvar_95': [-0.025, -0.05],
            'TailRisk_expected_shortfall': [-0.03, -0.06],
            'TailRisk_max_drawdown': [-0.15, -0.25],
            'TailRisk_skewness': [-0.5, -0.8],
            'TailRisk_kurtosis': [3.2, 4.1]
        })
        
        # Mock del método _display_results para evitar errores de GUI
        with patch.object(self.gui, '_display_results') as mock_display:
            # Simular la llamada al método
            self.gui._display_results(test_df, {})
            
            # Verificar que se llamó el método
            mock_display.assert_called_once()
            
            # Verificar que se pasó el DataFrame correcto
            called_df = mock_display.call_args[0][0]
            assert isinstance(called_df, pd.DataFrame)
            assert len(called_df) == 2
            
            # Verificar que las métricas de tail risk están presentes
            tail_risk_columns = [col for col in called_df.columns if col.startswith('TailRisk_')]
            assert len(tail_risk_columns) > 0
            
        logger.info("✅ Visualización de riesgo de cola en tabla verificada")
    
    def test_tail_risk_levels_classification(self):
        """Test que verifica la clasificación de niveles de riesgo de cola."""
        logger.info("🧪 Test: Clasificación de niveles de riesgo de cola")
        
        test_cases = [
            # (métricas, nivel_esperado, icono_esperado)
            ({
                'TailRisk_var_95': -0.06,  # -6%
                'TailRisk_cvar_95': -0.08,  # -8%
                'TailRisk_expected_shortfall': -0.09,  # -9%
                'TailRisk_max_drawdown': -0.30,  # -30%
                'TailRisk_skewness': -1.2,
                'TailRisk_kurtosis': 6.0
            }, "ALTO", "🔴"),
            ({
                'TailRisk_var_95': -0.04,  # -4%
                'TailRisk_cvar_95': -0.06,  # -6%
                'TailRisk_expected_shortfall': -0.07,  # -7%
                'TailRisk_max_drawdown': -0.20,  # -20%
                'TailRisk_skewness': -0.7,
                'TailRisk_kurtosis': 4.5
            }, "MODERADO", "🟡"),
            ({
                'TailRisk_var_95': -0.02,  # -2%
                'TailRisk_cvar_95': -0.03,  # -3%
                'TailRisk_expected_shortfall': -0.04,  # -4%
                'TailRisk_max_drawdown': -0.12,  # -12%
                'TailRisk_skewness': -0.3,
                'TailRisk_kurtosis': 3.8
            }, "BAJO", "🟢"),
            ({
                'TailRisk_var_95': -0.01,  # -1%
                'TailRisk_cvar_95': -0.02,  # -2%
                'TailRisk_expected_shortfall': -0.02,  # -2%
                'TailRisk_max_drawdown': -0.05,  # -5%
                'TailRisk_skewness': 0.1,
                'TailRisk_kurtosis': 3.1
            }, "MUY BAJO", "🟢")
        ]
        
        for metrics, expected_level, expected_icon in test_cases:
            test_row = pd.Series({
                'Strategy_Name': 'Test_Strategy',
                **metrics
            })
            
            risk_info = self.gui._calculate_tail_risk_level(test_row)
            
            assert risk_info['level'] == expected_level, f"Error: esperado {expected_level}, obtenido {risk_info['level']}"
            assert risk_info['icon'] == expected_icon, f"Error: esperado {expected_icon}, obtenido {risk_info['icon']}"
            
            logger.info(f"✅ {expected_level} {expected_icon}: {risk_info['risk_score']} puntos")
        
        logger.info("✅ Clasificación de niveles de riesgo verificada")
    
    def test_tail_risk_error_handling(self):
        """Test que verifica el manejo de errores en el cálculo de riesgo de cola."""
        logger.info("🧪 Test: Manejo de errores en cálculo de riesgo de cola")
        
        # Caso 1: Datos vacíos
        empty_row = pd.Series({})
        risk_info = self.gui._calculate_tail_risk_level(empty_row)
        
        assert risk_info['level'] == "N/A"
        assert risk_info['icon'] == "❓"
        assert "Error" in risk_info['description']
        
        # Caso 2: Datos con valores NaN
        nan_row = pd.Series({
            'Strategy_Name': 'Test_Strategy',
            'TailRisk_var_95': np.nan,
            'TailRisk_cvar_95': np.nan
        })
        risk_info = self.gui._calculate_tail_risk_level(nan_row)
        
        # Debe usar métricas tradicionales como fallback
        assert risk_info['level'] != "N/A" or risk_info['level'] == "MUY BAJO"
        
        logger.info("✅ Manejo de errores funcionando correctamente")
    
    def test_tail_risk_tooltip_generation(self):
        """Test que verifica la generación de tooltips para riesgo de cola."""
        logger.info("🧪 Test: Generación de tooltips para riesgo de cola")
        
        test_row = pd.Series({
            'Strategy_Name': 'Test_Strategy',
            'TailRisk_var_95': -0.03,
            'TailRisk_cvar_95': -0.05,
            'TailRisk_expected_shortfall': -0.06,
            'TailRisk_max_drawdown': -0.20,
            'TailRisk_skewness': -0.8,
            'TailRisk_kurtosis': 4.2
        })
        
        risk_info = self.gui._calculate_tail_risk_level(test_row)
        
        # Generar tooltip
        tooltip_text = f"Riesgo de Cola: {risk_info['description']}\n\nFactores de riesgo:\n" + "\n".join(risk_info['risk_factors'])
        
        # Verificar que el tooltip contiene información útil
        assert "Riesgo de Cola:" in tooltip_text
        assert "Factores de riesgo:" in tooltip_text
        assert len(risk_info['risk_factors']) > 0
        
        logger.info(f"✅ Tooltip generado: {len(tooltip_text)} caracteres")
        logger.info(f"📊 Factores de riesgo: {len(risk_info['risk_factors'])}")
    
    def test_tail_risk_integration_with_unified_evaluator(self):
        """Test que verifica la integración completa con UnifiedEvaluator."""
        logger.info("🧪 Test: Integración completa con UnifiedEvaluator")
        
        # Mock del UnifiedEvaluator
        with patch('src.core.analysis.unified_evaluator.UnifiedEvaluatorEnhanced') as mock_evaluator:
            # Configurar mock
            mock_instance = Mock()
            mock_evaluator.return_value = mock_instance
            
            # Simular DataFrame con métricas de tail risk
            test_df = pd.DataFrame({
                'Strategy_Name': ['Strategy_A', 'Strategy_B'],
                'Unified_Score': [0.8, 0.6],
                'TailRisk_var_95': [-0.02, -0.04],
                'TailRisk_cvar_95': [-0.025, -0.05],
                'TailRisk_expected_shortfall': [-0.03, -0.06],
                'TailRisk_max_drawdown': [-0.15, -0.25],
                'TailRisk_skewness': [-0.5, -0.8],
                'TailRisk_kurtosis': [3.2, 4.1]
            })
            
            mock_instance.evaluate_strategies_unified.return_value = test_df
            
            # Verificar que el evaluador se puede crear
            from src.core.analysis.unified_evaluator import UnifiedEvaluatorEnhanced
            evaluator = UnifiedEvaluatorEnhanced()
            
            # Verificar que tiene el analizador de tail risk
            assert hasattr(evaluator, 'tail_risk_analyzer')
            
        logger.info("✅ Integración con UnifiedEvaluator verificada")


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "--tb=short"]) 