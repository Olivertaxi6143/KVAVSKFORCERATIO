"""
Test para validar los módulos de utilidades extraídos.

Este test verifica que todas las funciones de utilidades funcionen correctamente
después de la extracción modular.
"""

import pandas as pd
import numpy as np
import pytest
import logging
from typing import Dict, Any

# Importar módulos de utilidades
from src.gui.utils import (
    safe_sum, safe_values, improve_missing_data_handling,
    validate_dataframe, clean_extreme_values, normalize_series, calculate_percentiles
)
from src.core.utils.error_handler import (
    RobustErrorHandler, retry_on_error, handle_specific_errors,
    validate_input, log_execution_time, GUIAnalysisError
)
from src.data.data_utils import (
    safe_float, safe_int, safe_str, safe_bool, convert_types, convert_series_types, convert_dataframe_types, validate_types, infer_numeric_type, normalize_numeric_series, ensure_numeric_columns, convert_to_datetime, safe_convert_to_numeric, safe_replace_date, safe_str_arg
)
from src.core.utils.validation_utils import (
    validate_config, validate_kpi_config, validate_trading_style_config,
    validate_file_path, validate_numeric_range, validate_percentage,
    validate_probability, validate_series_quality, validate_correlation_matrix,
    validate_analysis_results
)
from src.data.data_utils import (
    safe_float, extract_float_from_tuple, validate_numeric_column, calculate_basic_stats, detect_outliers_iqr
)

# Configurar logging para tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestDataUtils:
    """Tests para utilidades de datos."""
    
    def test_safe_sum(self):
        """Test para safe_sum con diferentes tipos de entrada."""
        logger.info("Testing safe_sum function")
        
        # Test con Series
        series = pd.Series([True, False, True, True])
        assert safe_sum(series) == 3
        
        # Test con DataFrame
        df = pd.DataFrame({'A': [True, False], 'B': [True, True]})
        assert safe_sum(df) == 3
        
        # Test con ndarray
        arr = np.array([True, False, True])
        assert safe_sum(arr) == 2
        
        # Test con escalar
        assert safe_sum(True) == 1
        assert safe_sum(False) == 0
        
        logger.info("safe_sum tests passed")
    
    def test_safe_values(self):
        """Test para safe_values."""
        logger.info("Testing safe_values function")
        
        # Test con Series
        series = pd.Series([1, 2, 3])
        values = safe_values(series)
        assert isinstance(values, np.ndarray)
        assert np.array_equal(values, np.array([1, 2, 3]))
        
        # Test con DataFrame
        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        values = safe_values(df)
        assert isinstance(values, np.ndarray)
        
        # Test con escalar
        assert safe_values(5) == 5
        
        logger.info("safe_values tests passed")
    
    def test_safe_float(self):
        """Test para safe_float."""
        logger.info("Testing safe_float function")
        
        assert safe_float("123.45") == 123.45
        assert safe_float("123,45") == 123.45  # Coma decimal
        assert safe_float(" 123.45 ") == 123.45  # Espacios
        assert safe_float(123) == 123.0
        assert safe_float("invalid") == 0.0  # Valor inválido
        assert safe_float(None) == 0.0  # None
        
        logger.info("safe_float tests passed")
    
    def test_improve_missing_data_handling(self):
        """Test para improve_missing_data_handling."""
        logger.info("Testing improve_missing_data_handling function")
        
        # Crear DataFrame con datos faltantes
        df = pd.DataFrame({
            'cagr': [1.5, np.nan, 2.1, np.nan],
            'drawdown': [0.1, 0.2, np.nan, 0.3],
            'category': ['A', 'B', np.nan, 'C']
        })
        
        df_improved = improve_missing_data_handling(df)
        
        # Verificar que no hay NaN
        assert not df_improved.isna().any().any()
        assert len(df_improved) == len(df)
        
        logger.info("improve_missing_data_handling tests passed")
    
    def test_validate_dataframe(self):
        """Test para validate_dataframe."""
        logger.info("Testing validate_dataframe function")
        
        # DataFrame válido
        df_valid = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })
        is_valid, errors = validate_dataframe(df_valid)
        assert is_valid
        assert len(errors) == 0
        
        # DataFrame vacío
        df_empty = pd.DataFrame()
        is_valid, errors = validate_dataframe(df_empty)
        assert not is_valid
        assert "DataFrame está vacío" in errors[0]
        
        # DataFrame sin columnas numéricas
        df_no_numeric = pd.DataFrame({
            'A': ['a', 'b', 'c'],
            'B': ['d', 'e', 'f']
        })
        is_valid, errors = validate_dataframe(df_no_numeric)
        assert not is_valid
        assert "No hay columnas numéricas" in errors[0]
        
        logger.info("validate_dataframe tests passed")
    
    def test_clean_extreme_values(self):
        """Test para clean_extreme_values."""
        logger.info("Testing clean_extreme_values function")
        
        # Crear DataFrame con outliers
        df = pd.DataFrame({
            'A': [1, 2, 3, 100, 4, 5, -50],
            'B': [10, 20, 30, 40, 50, 60, 70]
        })
        
        df_cleaned = clean_extreme_values(df, method='iqr')
        
        # Verificar que los outliers fueron limpiados
        assert len(df_cleaned) == len(df)
        assert df_cleaned['A'].max() < 100
        assert df_cleaned['A'].min() > -50
        
        logger.info("clean_extreme_values tests passed")
    
    def test_normalize_series(self):
        """Test para normalize_series."""
        logger.info("Testing normalize_series function")
        
        series = pd.Series([1, 2, 3, 4, 5])
        
        # Test minmax
        normalized = normalize_series(series, method='minmax')
        assert normalized.min() == 0
        assert normalized.max() == 1
        
        # Test zscore
        normalized = normalize_series(series, method='zscore')
        assert abs(normalized.mean()) < 1e-10  # Cerca de 0
        assert abs(normalized.std() - 1) < 1e-10  # Cerca de 1
        
        logger.info("normalize_series tests passed")


class TestErrorHandler:
    """Tests para el manejador de errores."""
    
    def test_robust_error_handler(self):
        """Test para RobustErrorHandler."""
        logger.info("Testing RobustErrorHandler")
        
        handler = RobustErrorHandler(max_retries=2)
        
        # Función que falla
        def failing_func():
            raise ValueError("Test error")
        
        # Test que la función falla después de reintentos
        with pytest.raises(ValueError):
            handler.execute_with_retry(failing_func)
        
        # Verificar estadísticas
        stats = handler.get_error_stats()
        assert stats['total_errors'] > 0
        assert 'ValueError' in stats['error_counts']
        
        logger.info("RobustErrorHandler tests passed")
    
    def test_retry_decorator(self):
        """Test para el decorador retry_on_error."""
        logger.info("Testing retry_on_error decorator")
        
        call_count = 0
        
        @retry_on_error(max_retries=2)
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Test error")
        
        # Test que la función falla después de reintentos
        with pytest.raises(RuntimeError):
            failing_function()
        
        assert call_count == 2
        
        logger.info("retry_on_error tests passed")
    
    def test_handle_specific_errors(self):
        """Test para el decorador handle_specific_errors."""
        logger.info("Testing handle_specific_errors decorator")
        
        @handle_specific_errors([ValueError], default_value=42)
        def function_that_raises_value_error():
            raise ValueError("Test error")
        
        result = function_that_raises_value_error()
        assert result == 42
        
        logger.info("handle_specific_errors tests passed")
    
    def test_validate_input(self):
        """Test para el decorador validate_input."""
        logger.info("Testing validate_input decorator")
        
        @validate_input
        def test_function(a, b, c=None):
            return a + b
        
        # Test con argumentos válidos
        assert test_function(1, 2) == 3
        
        # Test con argumento None
        with pytest.raises(ValueError):
            test_function(1, None)
        
        logger.info("validate_input tests passed")
    
    def test_gui_analysis_error(self):
        """Test para GUIAnalysisError."""
        logger.info("Testing GUIAnalysisError")
        
        error = GUIAnalysisError("Test error", "test_type", {"detail": "test"})
        
        assert str(error) == "test_type: Test error"
        assert error.error_type == "test_type"
        assert error.details == {"detail": "test"}
        
        details = error.get_details()
        assert details['message'] == "test_type: Test error"
        assert details['error_type'] == "test_type"
        
        logger.info("GUIAnalysisError tests passed")


class TestTypeConverters:
    """Tests para conversores de tipos."""
    
    def test_convert_types(self):
        """Test para convert_types."""
        logger.info("Testing convert_types function")
        
        assert convert_types("123.45", "float") == 123.45
        assert convert_types("123", "int") == 123
        assert convert_types(123, "str") == "123"
        assert convert_types("true", "bool") is True
        
        logger.info("convert_types tests passed")
    
    def test_safe_conversions(self):
        """Test para conversiones seguras."""
        logger.info("Testing safe conversions")
        
        assert safe_int("123") == 123
        assert safe_int("invalid") == 0
        
        assert safe_str(123) == "123"
        assert safe_str(None) == "None"
        
        assert safe_bool("true") is True
        assert safe_bool("false") is False
        assert safe_bool(1) is True
        assert safe_bool(0) is False
        
        logger.info("safe conversions tests passed")
    
    def test_convert_series_types(self):
        """Test para convert_series_types."""
        logger.info("Testing convert_series_types function")
        
        series = pd.Series(["1", "2", "3"])
        converted = convert_series_types(series, "int")
        
        assert converted.dtype == 'int64'
        assert converted.iloc[0] == 1
        
        logger.info("convert_series_types tests passed")
    
    def test_validate_types(self):
        """Test para validate_types."""
        logger.info("Testing validate_types function")
        
        assert validate_types(123, int) is True
        assert validate_types("123", int) is True
        assert validate_types("abc", int) is False
        
        assert validate_types(123.45, float) is True
        assert validate_types("123.45", float) is True
        
        logger.info("validate_types tests passed")


class TestValidationUtils:
    """Tests para utilidades de validación."""
    
    def test_validate_config(self):
        """Test para validate_config."""
        logger.info("Testing validate_config function")
        
        # Configuración válida
        config = {
            'feature_enabled': True,
            'weight': 0.5,
            'threshold': 0.1
        }
        is_valid, errors = validate_config(config)
        assert is_valid
        assert len(errors) == 0
        
        # Configuración inválida
        config_invalid = {
            'feature_enabled': "not_bool",
            'weight': "not_numeric"
        }
        is_valid, errors = validate_config(config_invalid)
        assert not is_valid
        assert len(errors) > 0
        
        logger.info("validate_config tests passed")
    
    def test_validate_kpi_config(self):
        """Test para validate_kpi_config."""
        logger.info("Testing validate_kpi_config function")
        
        # Configuración válida
        kpi_config = {
            'sharpe_ratio': {
                'enabled': True,
                'weight': 0.3
            }
        }
        is_valid, errors = validate_kpi_config(kpi_config)
        assert is_valid
        assert len(errors) == 0
        
        # Configuración inválida
        kpi_config_invalid = {
            'sharpe_ratio': {
                'enabled': "not_bool",
                'weight': -0.5  # Peso negativo
            }
        }
        is_valid, errors = validate_kpi_config(kpi_config_invalid)
        assert not is_valid
        assert len(errors) > 0
        
        logger.info("validate_kpi_config tests passed")
    
    def test_validate_numeric_range(self):
        """Test para validate_numeric_range."""
        logger.info("Testing validate_numeric_range function")
        
        # Valor válido
        is_valid, errors = validate_numeric_range(5, 0, 10, "test_value")
        assert is_valid
        assert len(errors) == 0
        
        # Valor fuera de rango
        is_valid, errors = validate_numeric_range(15, 0, 10, "test_value")
        assert not is_valid
        assert len(errors) > 0
        
        logger.info("validate_numeric_range tests passed")
    
    def test_validate_percentage(self):
        """Test para validate_percentage."""
        logger.info("Testing validate_percentage function")
        
        # Porcentaje válido
        is_valid, errors = validate_percentage(50.0)
        assert is_valid
        assert len(errors) == 0
        
        # Porcentaje inválido
        is_valid, errors = validate_percentage(150.0)
        assert not is_valid
        assert len(errors) > 0
        
        logger.info("validate_percentage tests passed")
    
    def test_validate_probability(self):
        """Test para validate_probability."""
        logger.info("Testing validate_probability function")
        
        # Probabilidad válida
        is_valid, errors = validate_probability(0.5)
        assert is_valid
        assert len(errors) == 0
        
        # Probabilidad inválida
        is_valid, errors = validate_probability(1.5)
        assert not is_valid
        assert len(errors) > 0
        
        logger.info("validate_probability tests passed")
    
    def test_validate_series_quality(self):
        """Test para validate_series_quality."""
        logger.info("Testing validate_series_quality function")
        
        # Serie válida
        series = pd.Series([1, 2, 3, 4, 5])
        is_valid, errors = validate_series_quality(series)
        assert is_valid
        assert len(errors) == 0
        
        # Serie con muchos NaN
        series_with_nan = pd.Series([1, np.nan, 3, np.nan, 5, np.nan, 7, np.nan, 9, np.nan])
        is_valid, errors = validate_series_quality(series_with_nan, min_non_null=0.6)
        assert not is_valid
        assert len(errors) > 0
        
        logger.info("validate_series_quality tests passed")


class TestDataUtilsData:
    """Tests para funciones de data_utils.py migradas de research_docs.py."""
    def test_safe_float(self):
        assert safe_float("12.5") == 12.5
        assert safe_float("invalid") == 0.0
        assert safe_float(None) == 0.0
        assert safe_float(7) == 7.0
        assert safe_float(3.14) == 3.14

    def test_extract_float_from_tuple(self):
        assert extract_float_from_tuple((1.5, 2.5), 1) == 2.5
        assert extract_float_from_tuple(("3.2",), 0) == 3.2
        assert extract_float_from_tuple(("bad",), 0, default=9.9) == 9.9
        assert extract_float_from_tuple(5.5) == 5.5
        assert extract_float_from_tuple(None, 0, default=-1) == -1

    def test_validate_numeric_column(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        assert validate_numeric_column(df, "a")
        assert not validate_numeric_column(df, "b")
        assert not validate_numeric_column(df, "c")
        df_nan = pd.DataFrame({"a": [np.nan, np.nan]})
        assert not validate_numeric_column(df_nan, "a")

    def test_calculate_basic_stats(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
        stats = calculate_basic_stats(df, "x")
        assert stats["mean"] == 3.0
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["count"] == 5.0
        # Columna inválida
        assert calculate_basic_stats(df, "y") == {}

    def test_detect_outliers_iqr(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 100]})
        result = detect_outliers_iqr(df, "x")
        assert result["count"] == 1
        assert 100 in result["outliers"]
        # Columna inválida
        assert detect_outliers_iqr(df, "y")["count"] == 0
        # Sin outliers
        df2 = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
        assert detect_outliers_iqr(df2, "x")["count"] == 0


def test_all_utils_integration():
    """Test de integración de todas las utilidades."""
    logger.info("Testing all utilities integration")
    
    # Crear datos de prueba
    df = pd.DataFrame({
        'A': [1, 2, 3, np.nan, 5],
        'B': [10, 20, 30, 40, 50],
        'C': ['a', 'b', 'c', 'd', 'e']
    })
    
    # Probar flujo completo
    try:
        # 1. Validar DataFrame
        is_valid, errors = validate_dataframe(df)
        assert is_valid
        
        # 2. Mejorar manejo de datos faltantes
        df_improved = improve_missing_data_handling(df)
        assert not df_improved.isna().any().any()
        
        # 3. Limpiar valores extremos
        df_cleaned = clean_extreme_values(df_improved)
        assert len(df_cleaned) == len(df_improved)
        
        # 4. Normalizar serie
        series_b = df_cleaned['B'].astype(float)
        if isinstance(series_b, pd.Series):
            normalized = normalize_series(series_b)
            assert normalized.min() == 0
            assert normalized.max() == 1
        
        # 5. Convertir tipos
        df_converted = convert_dataframe_types(df_cleaned, {'A': 'float', 'B': 'int'})
        assert df_converted['A'].dtype == 'float64'
        assert df_converted['B'].dtype == 'int64'
        
        logger.info("All utilities integration test passed")
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        raise


if __name__ == "__main__":
    # Ejecutar todos los tests
    logger.info("Starting utils modular tests...")
    
    # Tests de DataUtils
    test_data_utils = TestDataUtils()
    test_data_utils.test_safe_sum()
    test_data_utils.test_safe_values()
    test_data_utils.test_safe_float()
    test_data_utils.test_improve_missing_data_handling()
    test_data_utils.test_validate_dataframe()
    test_data_utils.test_clean_extreme_values()
    test_data_utils.test_normalize_series()
    
    # Tests de ErrorHandler
    test_error_handler = TestErrorHandler()
    test_error_handler.test_robust_error_handler()
    test_error_handler.test_retry_decorator()
    test_error_handler.test_handle_specific_errors()
    test_error_handler.test_validate_input()
    test_error_handler.test_gui_analysis_error()
    
    # Tests de TypeConverters
    test_type_converters = TestTypeConverters()
    test_type_converters.test_convert_types()
    test_type_converters.test_safe_conversions()
    test_type_converters.test_convert_series_types()
    test_type_converters.test_validate_types()
    
    # Tests de ValidationUtils
    test_validation_utils = TestValidationUtils()
    test_validation_utils.test_validate_config()
    test_validation_utils.test_validate_kpi_config()
    test_validation_utils.test_validate_numeric_range()
    test_validation_utils.test_validate_percentage()
    test_validation_utils.test_validate_probability()
    test_validation_utils.test_validate_series_quality()
    
    # Test de integración
    test_all_utils_integration()
    
    # Tests de DataUtilsData
    test_data_utils_data = TestDataUtilsData()
    test_data_utils_data.test_safe_float()
    test_data_utils_data.test_extract_float_from_tuple()
    test_data_utils_data.test_validate_numeric_column()
    test_data_utils_data.test_calculate_basic_stats()
    test_data_utils_data.test_detect_outliers_iqr()
    
    logger.info("All utils modular tests completed successfully!") 