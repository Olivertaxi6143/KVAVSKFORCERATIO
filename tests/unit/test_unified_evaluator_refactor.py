"""
Tests de regresión para el refactor de UnifiedEvaluatorEnhanced.
"""

import pytest
import pandas as pd
import numpy as np
import logging
from unittest.mock import Mock, patch
from src.core.analysis.unified_evaluator import UnifiedEvaluatorEnhanced

# Configurar logging para tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestUnifiedEvaluatorRefactor:
    """Tests de regresión para el refactor de UnifiedEvaluatorEnhanced."""
    
    def setup_method(self):
        """Configuración para cada test."""
        self.mock_progress_callback = Mock()
        self.evaluator = UnifiedEvaluatorEnhanced(progress_callback=self.mock_progress_callback)
        
        # DataFrame de prueba básico
        self.df_basic = pd.DataFrame({
            'Strategy_Name': ['Strategy_1', 'Strategy_2', 'Strategy_3'],
            'Sharpe_Ratio': [1.5, 2.0, 1.8],
            'CAGR': [0.15, 0.20, 0.18],
            'Max_DD_%': [-0.10, -0.08, -0.12],
            'Profit_factor': [1.8, 2.2, 1.9]
        })
    
    def test_validate_input_dataframe_success(self):
        """Test validación exitosa de DataFrame de entrada."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_validate_input_dataframe_success")
        
        # Test con DataFrame válido
        self.evaluator._validate_input_dataframe(self.df_basic)
        log.debug("assert passed: validación exitosa con DataFrame válido")
    
    def test_validate_input_dataframe_empty(self):
        """Test validación con DataFrame vacío."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_validate_input_dataframe_empty")
        
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="DataFrame de entrada está vacío"):
            self.evaluator._validate_input_dataframe(empty_df)
        log.debug("assert passed: ValueError lanzado para DataFrame vacío")
    
    def test_validate_input_dataframe_missing_columns(self):
        """Test validación con columnas faltantes."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_validate_input_dataframe_missing_columns")
        
        df_missing = pd.DataFrame({
            'Other_Column': [1, 2, 3]
        })
        
        with pytest.raises(ValueError, match="Faltan columnas requeridas"):
            self.evaluator._validate_input_dataframe(df_missing)
        log.debug("assert passed: ValueError lanzado para columnas faltantes")
    
    def test_ensure_series_type_with_series(self):
        """Test conversión de Series a Series de float."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_ensure_series_type_with_series")
        
        input_series = pd.Series(['1.5', '2.0', '1.8'], index=[0, 1, 2])
        result = self.evaluator._ensure_series_type(input_series, input_series.index)
        
        assert isinstance(result, pd.Series)
        assert result.dtype == float
        assert result.iloc[0] == 1.5
        log.debug("assert passed: conversión de Series exitosa")
    
    def test_ensure_series_type_with_dataframe(self):
        """Test conversión de DataFrame a Series de float."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_ensure_series_type_with_dataframe")
        
        input_df = pd.DataFrame({'col': [1.5, 2.0, 1.8]})
        result = self.evaluator._ensure_series_type(input_df, input_df.index)
        
        assert isinstance(result, pd.Series)
        assert result.dtype == float
        assert result.iloc[0] == 1.5
        log.debug("assert passed: conversión de DataFrame exitosa")
    
    def test_ensure_series_type_with_invalid_data(self):
        """Test conversión con datos inválidos."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_ensure_series_type_with_invalid_data")
        
        invalid_data = "not_a_series"
        result = self.evaluator._ensure_series_type(invalid_data, pd.Index([0, 1, 2]))
        
        assert isinstance(result, pd.Series)
        assert result.dtype == float
        assert all(result == 0.5)  # Valor por defecto
        log.debug("assert passed: manejo de datos inválidos")
    
    def test_normalize_series_basic(self):
        """Test normalización básica de series."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_normalize_series_basic")
        
        input_series = pd.Series([1, 2, 3, 4, 5])
        result = self.evaluator._normalize_series(input_series)
        
        assert isinstance(result, pd.Series)
        assert result.min() == 0.0
        assert result.max() == 1.0
        assert result.iloc[0] == 0.0  # valor mínimo
        assert result.iloc[4] == 1.0  # valor máximo
        log.debug("assert passed: normalización básica exitosa")
    
    def test_normalize_series_with_nan(self):
        """Test normalización con valores NaN."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_normalize_series_with_nan")
        
        input_series = pd.Series([1, np.nan, 3, 4, 5])
        result = self.evaluator._normalize_series(input_series)
        
        assert isinstance(result, pd.Series)
        assert not result.isna().any()  # No debe haber NaN
        assert result.min() >= 0.0
        assert result.max() <= 1.0
        log.debug("assert passed: normalización con NaN exitosa")
    
    def test_normalize_series_constant_values(self):
        """Test normalización con valores constantes."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_normalize_series_constant_values")
        
        input_series = pd.Series([5, 5, 5, 5, 5])
        result = self.evaluator._normalize_series(input_series)
        
        assert isinstance(result, pd.Series)
        assert all(result == 0.5)  # Valor por defecto para valores constantes
        log.debug("assert passed: normalización con valores constantes")
    
    def test_normalize_series_empty(self):
        """Test normalización con serie vacía."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_normalize_series_empty")
        
        input_series = pd.Series([])
        result = self.evaluator._normalize_series(input_series)
        
        assert isinstance(result, pd.Series)
        assert all(result == 0.5)  # Valor por defecto
        log.debug("assert passed: normalización con serie vacía")
    
    def test_get_factor_k_scores_with_normalized(self):
        """Test obtención de scores FK con columna normalizada."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_get_factor_k_scores_with_normalized")
        
        df_fk = pd.DataFrame({
            'FK96_Elite_Enhanced_Normalized': [0.8, 0.9, 0.7],
            'Other_Column': [1, 2, 3]
        })
        
        result = self.evaluator._get_factor_k_scores(df_fk)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert result.iloc[0] == 0.8
        log.debug("assert passed: obtención de scores FK normalizados")
    
    def test_get_factor_k_scores_with_raw(self):
        """Test obtención de scores FK con columna raw."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_get_factor_k_scores_with_raw")
        
        df_fk = pd.DataFrame({
            'FK96_Elite_Enhanced': [8.5, 9.2, 7.8],
            'Other_Column': [1, 2, 3]
        })
        
        result = self.evaluator._get_factor_k_scores(df_fk)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert result.min() >= 0.0
        assert result.max() <= 1.0
        log.debug("assert passed: obtención y normalización de scores FK raw")
    
    def test_get_factor_k_scores_missing(self):
        """Test obtención de scores FK cuando faltan columnas."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_get_factor_k_scores_missing")
        
        df_fk = pd.DataFrame({
            'Other_Column': [1, 2, 3]
        })
        
        result = self.evaluator._get_factor_k_scores(df_fk)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert all(result == 0.5)  # Valor por defecto
        log.debug("assert passed: manejo de columnas FK faltantes")
    
    def test_get_qva_scores_basic(self):
        """Test obtención de scores QVA básicos."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_get_qva_scores_basic")
        
        df_fk = pd.DataFrame({
            'QVA_Score': [0.7, 0.8, 0.6],
            'Other_Column': [1, 2, 3]
        })
        
        result = self.evaluator._get_qva_scores(df_fk, 'QVA_Score')
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert result.iloc[0] == 0.7
        log.debug("assert passed: obtención de scores QVA básicos")
    
    def test_get_qva_scores_missing(self):
        """Test obtención de scores QVA cuando faltan."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_get_qva_scores_missing")
        
        df_fk = pd.DataFrame({
            'Other_Column': [1, 2, 3]
        })
        
        result = self.evaluator._get_qva_scores(df_fk, 'QVA_Score')
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        assert all(result == 0.5)  # Valor por defecto
        log.debug("assert passed: manejo de scores QVA faltantes")
    
    @patch('src.core.analysis.unified_evaluator.FactorKElite96Enhanced')
    @patch('src.core.analysis.unified_evaluator.QVAScorerEnhanced')
    def test_evaluate_strategies_unified_integration(self, mock_qva, mock_factor_k):
        """Test integración completa del método principal."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_evaluate_strategies_unified_integration")
        
        # Mock Factor K
        mock_factor_k_instance = Mock()
        mock_factor_k_instance.evaluate_strategies.return_value = pd.DataFrame({
            'FK96_Elite_Enhanced': [8.5, 9.2, 7.8],
            'Strategy_Name': ['Strategy_1', 'Strategy_2', 'Strategy_3']
        })
        mock_factor_k.return_value = mock_factor_k_instance
        
        # Mock QVA
        mock_qva_instance = Mock()
        mock_qva_instance.calculate_qva_score.return_value = pd.Series([0.7, 0.8, 0.6])
        mock_qva_instance.compute_qva_score_robust.return_value = pd.Series([0.75, 0.85, 0.65])
        mock_qva_instance.config_manager = Mock()
        mock_qva.return_value = mock_qva_instance
        
        # Crear evaluador con mocks
        evaluator = UnifiedEvaluatorEnhanced(progress_callback=self.mock_progress_callback)
        evaluator.factor_k = mock_factor_k_instance
        evaluator.qva_scorer = mock_qva_instance
        
        # Ejecutar evaluación
        result = evaluator.evaluate_strategies_unified(self.df_basic)
        
        # Verificar resultado
        assert isinstance(result, pd.DataFrame)
        assert 'Unified_Score' in result.columns
        assert 'Unified_Score_Normalized' in result.columns
        assert 'Unified_Score_Robust' in result.columns
        assert 'Unified_Score_Robust_Normalized' in result.columns
        assert len(result) == 3
        log.debug("assert passed: integración completa exitosa")
    
    def test_evaluate_strategies_unified_empty_input(self):
        """Test evaluación con entrada vacía."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_evaluate_strategies_unified_empty_input")
        
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="DataFrame de entrada está vacío"):
            self.evaluator.evaluate_strategies_unified(empty_df)
        log.debug("assert passed: ValueError para entrada vacía")
    
    def test_evaluate_strategies_unified_missing_columns(self):
        """Test evaluación con columnas faltantes."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_evaluate_strategies_unified_missing_columns")
        
        df_missing = pd.DataFrame({
            'Other_Column': [1, 2, 3]
        })
        
        with pytest.raises(ValueError, match="Faltan columnas requeridas"):
            self.evaluator.evaluate_strategies_unified(df_missing)
        log.debug("assert passed: ValueError para columnas faltantes")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 