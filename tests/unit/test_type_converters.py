"""
Tests para el módulo type_converters.py
"""

import pytest
import pandas as pd
import numpy as np
import logging
from src.data.data_utils import (
    safe_float, safe_int, safe_str, safe_bool, convert_types, convert_series_types, convert_dataframe_types, validate_types, infer_numeric_type, normalize_numeric_series, ensure_numeric_columns, convert_to_datetime, safe_convert_to_numeric, safe_replace_date, safe_str_arg
)

# Configurar logging para tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestTypeConverters:
    """Tests para las funciones de conversión de tipos."""
    
    def test_convert_types_basic(self):
        """Test conversión básica de tipos."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_convert_types_basic")
        
        # Test float
        result = convert_types("123.45", "float")
        assert isinstance(result, float)
        assert result == 123.45
        log.debug("assert passed: convert_types float funciona correctamente")
        
        # Test int
        result = convert_types("123", "int")
        assert isinstance(result, int)
        assert result == 123
        log.debug("assert passed: convert_types int funciona correctamente")
        
        # Test str
        result = convert_types(123, "str")
        assert isinstance(result, str)
        assert result == "123"
        log.debug("assert passed: convert_types str funciona correctamente")
        
        # Test bool
        result = convert_types("true", "bool")
        assert isinstance(result, bool)
        assert result is True
        log.debug("assert passed: convert_types bool funciona correctamente")
    
    def test_safe_float(self):
        """Test conversión segura a float."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_safe_float")
        
        # Test valores válidos
        assert safe_float("123.45") == 123.45
        assert safe_float("123,45") == 123.45  # Coma como separador decimal
        assert safe_float(123) == 123.0
        log.debug("assert passed: safe_float valores válidos")
        
        # Test valores inválidos
        assert safe_float("invalid") == 0.0
        assert safe_float(None) == 0.0
        log.debug("assert passed: safe_float valores inválidos")
    
    def test_safe_int(self):
        """Test conversión segura a int."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_safe_int")
        
        # Test valores válidos
        assert safe_int("123") == 123
        assert safe_int(123.45) == 123
        log.debug("assert passed: safe_int valores válidos")
        
        # Test valores inválidos
        assert safe_int("invalid") == 0
        assert safe_int(None) == 0
        log.debug("assert passed: safe_int valores inválidos")
    
    def test_convert_series_types(self):
        """Test conversión de tipos en Series."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_convert_series_types")
        
        # Crear serie de prueba
        series = pd.Series(["1", "2", "3"])
        
        # Test conversión a float
        result = convert_series_types(series, "float")
        assert isinstance(result, pd.Series)
        assert result.dtype == float
        assert result.iloc[0] == 1.0
        log.debug("assert passed: convert_series_types float")
        
        # Test conversión a int
        result = convert_series_types(series, "int")
        assert isinstance(result, pd.Series)
        assert result.dtype == int
        assert result.iloc[0] == 1
        log.debug("assert passed: convert_series_types int")
    
    def test_normalize_numeric_series(self):
        """Test normalización de series numéricas."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_normalize_numeric_series")
        
        # Serie con valores mixtos
        series = pd.Series(["1", "2.5", "inf", "-inf", "NaN", "3"])
        result = normalize_numeric_series(series)
        
        assert isinstance(result, pd.Series)
        assert result.dtype == float
        assert result.iloc[0] == 1.0
        assert result.iloc[1] == 2.5
        assert pd.isna(result.iloc[2])  # inf convertido a NaN
        assert pd.isna(result.iloc[3])  # -inf convertido a NaN
        assert pd.isna(result.iloc[4])  # NaN se mantiene
        assert result.iloc[5] == 3.0
        log.debug("assert passed: normalize_numeric_series maneja infinitos y NaN")
    
    def test_convert_to_datetime(self):
        """Test conversión a datetime."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_convert_to_datetime")
        
        # Serie con fechas
        series = pd.Series(["2023-01-01", "2023-01-02", "2023-01-03"])
        result = convert_to_datetime(series)
        
        assert isinstance(result, pd.Series)
        assert result.dtype == 'datetime64[ns]'
        assert result.iloc[0].year == 2023
        assert result.iloc[0].month == 1
        assert result.iloc[0].day == 1
        log.debug("assert passed: convert_to_datetime conversión básica")
        
        # Test con formato específico
        series_with_format = pd.Series(["01/01/2023", "02/01/2023"])
        result = convert_to_datetime(series_with_format, format="%d/%m/%Y")
        
        assert isinstance(result, pd.Series)
        assert result.dtype == 'datetime64[ns]'
        log.debug("assert passed: convert_to_datetime con formato específico")
    
    def test_safe_convert_to_numeric(self):
        """Test conversión segura a numérico."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_safe_convert_to_numeric")
        
        # Serie con valores mixtos
        series = pd.Series(["1", "2.5", "invalid", "3"])
        result = safe_convert_to_numeric(series)
        
        assert isinstance(result, pd.Series)
        assert result.dtype == float
        assert result.iloc[0] == 1.0
        assert result.iloc[1] == 2.5
        assert pd.isna(result.iloc[2])  # valor inválido
        assert result.iloc[3] == 3.0
        log.debug("assert passed: safe_convert_to_numeric maneja valores inválidos")
        
        # Test con downcast
        result = safe_convert_to_numeric(series, downcast="integer")
        assert isinstance(result, pd.Series)
        log.debug("assert passed: safe_convert_to_numeric con downcast")
    
    def test_ensure_numeric_columns(self):
        """Test asegurar columnas numéricas en DataFrame."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_ensure_numeric_columns")
        
        # DataFrame con columnas mixtas
        df = pd.DataFrame({
            'numeric': ['1', '2', '3'],
            'mixed': ['1', 'invalid', '3'],
            'text': ['a', 'b', 'c']
        })
        
        result = ensure_numeric_columns(df, ['numeric', 'mixed'])
        
        assert isinstance(result, pd.DataFrame)
        assert result['numeric'].dtype == float
        assert result['mixed'].dtype == float
        assert result['text'].dtype == object  # No se modifica
        log.debug("assert passed: ensure_numeric_columns procesa columnas específicas")
    
    def test_validate_types(self):
        """Test validación de tipos."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_validate_types")
        
        # Test tipos válidos
        assert validate_types(123, int) is True
        assert validate_types(123.45, float) is True
        assert validate_types("123", float) is True  # Conversión posible
        log.debug("assert passed: validate_types tipos válidos")
        
        # Test tipos inválidos
        assert validate_types("invalid", float) is False
        assert validate_types("abc", int) is False
        log.debug("assert passed: validate_types tipos inválidos")
    
    def test_infer_numeric_type(self):
        """Test inferencia de tipo numérico."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_infer_numeric_type")
        
        # Serie de enteros
        int_series = pd.Series([1, 2, 3])
        assert infer_numeric_type(int_series) == 'int'
        log.debug("assert passed: infer_numeric_type detecta enteros")
        
        # Serie de flotantes
        float_series = pd.Series([1.0, 2.5, 3.0])
        assert infer_numeric_type(float_series) == 'float'
        log.debug("assert passed: infer_numeric_type detecta flotantes")
        
        # Serie mixta
        mixed_series = pd.Series([1, 2.5, 3])
        assert infer_numeric_type(mixed_series) == 'float'
        log.debug("assert passed: infer_numeric_type detecta mixtos")
    
    def test_safe_replace_date(self):
        """Test reemplazo seguro de fechas."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_safe_replace_date")
        
        from datetime import datetime
        dt = datetime(2023, 1, 1)
        
        # Test reemplazo válido
        result = safe_replace_date(dt, year=2024, month=2)
        assert result.year == 2024
        assert result.month == 2
        log.debug("assert passed: safe_replace_date reemplazo válido")
        
        # Test con valores inválidos
        result = safe_replace_date(dt, year="invalid", month=[1, 2])
        assert result == dt  # No cambia
        log.debug("assert passed: safe_replace_date maneja valores inválidos")
    
    def test_safe_str_arg(self):
        """Test conversión segura de argumentos string."""
        log = logging.getLogger(__name__)
        log.info("Iniciando test_safe_str_arg")
        
        assert safe_str_arg("test") == "test"
        assert safe_str_arg(123) == "123"
        assert safe_str_arg(None) == ""
        log.debug("assert passed: safe_str_arg conversión segura")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 