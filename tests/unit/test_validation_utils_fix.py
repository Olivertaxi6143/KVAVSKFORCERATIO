"""
Tests unitarios para validar las correcciones de tipado en validation_utils.py.

Este módulo verifica que las funciones de validación manejen correctamente
los valores None y tipos opcionales.
"""

import pytest
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import tempfile
import os

# Importar las funciones de validación
from src.core.utils.validation_utils import (
    validate_config,
    validate_kpi_config,
    validate_trading_style_config,
    validate_file_path,
    validate_numeric_range,
    validate_percentage,
    validate_probability,
    validate_series_quality,
    validate_correlation_matrix,
    validate_analysis_results
)
from src.gui.utils import validate_dataframe

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestValidationUtilsFix:
    """Tests para validar las correcciones de tipado en validation_utils.py."""
    
    def test_validate_dataframe_with_none_parameters(self):
        """Test que valida el manejo correcto de parámetros None en validate_dataframe."""
        logger.debug("Iniciando test_validate_dataframe_with_none_parameters")
        
        # Crear DataFrame de prueba
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })
        
        # Test con required_columns=None
        is_valid, errors = validate_dataframe(df, required_columns=None)
        logger.debug(f"validate_dataframe con required_columns=None: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        # Test con max_rows=None
        is_valid, errors = validate_dataframe(df, max_rows=None)
        logger.debug(f"validate_dataframe con max_rows=None: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        # Test con ambos parámetros None
        is_valid, errors = validate_dataframe(df, required_columns=None, max_rows=None)
        logger.debug(f"validate_dataframe con ambos None: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        logger.debug("test_validate_dataframe_with_none_parameters completado exitosamente")
    
    def test_validate_config_with_none_parameters(self):
        """Test que valida el manejo correcto de parámetros None en validate_config."""
        logger.debug("Iniciando test_validate_config_with_none_parameters")
        
        config = {
            'feature_enabled': True,
            'weight_value': 0.5,
            'threshold_value': 0.1
        }
        
        # Test con required_keys=None
        is_valid, errors = validate_config(config, required_keys=None)
        logger.debug(f"validate_config con required_keys=None: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        # Test con configuración inválida
        invalid_config = "no es un dict"
        is_valid, errors = validate_config(invalid_config, required_keys=None)
        logger.debug(f"validate_config con config inválida: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        logger.debug("test_validate_config_with_none_parameters completado exitosamente")
    
    def test_validate_file_path_with_none_parameters(self):
        """Test que valida el manejo correcto de parámetros None en validate_file_path."""
        logger.debug("Iniciando test_validate_file_path_with_none_parameters")
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Test con file_type=None
            is_valid, errors = validate_file_path(tmp_path, file_type=None)
            logger.debug(f"validate_file_path con file_type=None: válido={is_valid}, errores={errors}")
            assert is_valid
            assert len(errors) == 0
            
            # Test con archivo inexistente
            is_valid, errors = validate_file_path("/ruta/inexistente/archivo.txt", file_type=None)
            logger.debug(f"validate_file_path con archivo inexistente: válido={is_valid}, errores={errors}")
            assert not is_valid
            assert len(errors) > 0
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        logger.debug("test_validate_file_path_with_none_parameters completado exitosamente")
    
    def test_validate_numeric_range_with_none_parameters(self):
        """Test que valida el manejo correcto de parámetros None en validate_numeric_range."""
        logger.debug("Iniciando test_validate_numeric_range_with_none_parameters")
        
        # Test con min_val=None y max_val=None
        is_valid, errors = validate_numeric_range(5.0, min_val=None, max_val=None)
        logger.debug(f"validate_numeric_range con ambos None: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        # Test con min_val=None
        is_valid, errors = validate_numeric_range(5.0, min_val=None, max_val=10.0)
        logger.debug(f"validate_numeric_range con min_val=None: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        # Test con max_val=None
        is_valid, errors = validate_numeric_range(5.0, min_val=0.0, max_val=None)
        logger.debug(f"validate_numeric_range con max_val=None: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        # Test con valor fuera de rango
        is_valid, errors = validate_numeric_range(15.0, min_val=0.0, max_val=10.0)
        logger.debug(f"validate_numeric_range con valor fuera de rango: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        logger.debug("test_validate_numeric_range_with_none_parameters completado exitosamente")
    
    def test_validate_percentage_and_probability(self):
        """Test que valida las funciones de validación de porcentajes y probabilidades."""
        logger.debug("Iniciando test_validate_percentage_and_probability")
        
        # Test porcentaje válido
        is_valid, errors = validate_percentage(50.0)
        logger.debug(f"validate_percentage con 50.0: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        # Test porcentaje inválido
        is_valid, errors = validate_percentage(150.0)
        logger.debug(f"validate_percentage con 150.0: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        # Test probabilidad válida
        is_valid, errors = validate_probability(0.5)
        logger.debug(f"validate_probability con 0.5: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        # Test probabilidad inválida
        is_valid, errors = validate_probability(1.5)
        logger.debug(f"validate_probability con 1.5: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        logger.debug("test_validate_percentage_and_probability completado exitosamente")
    
    def test_validate_series_quality(self):
        """Test que valida la función de validación de calidad de series."""
        logger.debug("Iniciando test_validate_series_quality")
        
        # Serie válida
        series = pd.Series([1, 2, 3, 4, 5])
        is_valid, errors = validate_series_quality(series)
        logger.debug(f"validate_series_quality con serie válida: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        # Serie vacía
        empty_series = pd.Series([])
        is_valid, errors = validate_series_quality(empty_series)
        logger.debug(f"validate_series_quality con serie vacía: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        # Serie con valores infinitos
        inf_series = pd.Series([1, 2, np.inf, 4])
        is_valid, errors = validate_series_quality(inf_series)
        logger.debug(f"validate_series_quality con valores infinitos: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        logger.debug("test_validate_series_quality completado exitosamente")
    
    def test_validate_correlation_matrix(self):
        """Test que valida la función de validación de matrices de correlación."""
        logger.debug("Iniciando test_validate_correlation_matrix")
        
        # Matriz de correlación válida
        corr_matrix = pd.DataFrame([
            [1.0, 0.5, 0.3],
            [0.5, 1.0, 0.7],
            [0.3, 0.7, 1.0]
        ])
        is_valid, errors = validate_correlation_matrix(corr_matrix)
        logger.debug(f"validate_correlation_matrix con matriz válida: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        # Matriz vacía
        empty_matrix = pd.DataFrame()
        is_valid, errors = validate_correlation_matrix(empty_matrix)
        logger.debug(f"validate_correlation_matrix con matriz vacía: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        # Matriz no cuadrada
        non_square_matrix = pd.DataFrame([
            [1.0, 0.5],
            [0.5, 1.0],
            [0.3, 0.7]
        ])
        is_valid, errors = validate_correlation_matrix(non_square_matrix)
        logger.debug(f"validate_correlation_matrix con matriz no cuadrada: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        logger.debug("test_validate_correlation_matrix completado exitosamente")
    
    def test_validate_analysis_results(self):
        """Test que valida la función de validación de resultados de análisis."""
        logger.debug("Iniciando test_validate_analysis_results")
        
        # Resultados válidos
        results = {
            'success': True,
            'data': pd.DataFrame({'A': [1, 2, 3]})
        }
        is_valid, errors = validate_analysis_results(results)
        logger.debug(f"validate_analysis_results con resultados válidos: válido={is_valid}, errores={errors}")
        assert is_valid
        assert len(errors) == 0
        
        # Resultados inválidos (no es dict)
        invalid_results = "no es un dict"
        is_valid, errors = validate_analysis_results(invalid_results)
        logger.debug(f"validate_analysis_results con resultados inválidos: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        # Resultados con campo faltante
        incomplete_results = {'success': True}
        is_valid, errors = validate_analysis_results(incomplete_results)
        logger.debug(f"validate_analysis_results con campo faltante: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        logger.debug("test_validate_analysis_results completado exitosamente")
    
    def test_edge_cases_and_error_handling(self):
        """Test que valida casos extremos y manejo de errores."""
        logger.debug("Iniciando test_edge_cases_and_error_handling")
        
        # DataFrame con valores duplicados en índice
        df_with_duplicates = pd.DataFrame({'A': [1, 2, 3]}, index=[0, 0, 1])
        is_valid, errors = validate_dataframe(df_with_duplicates)
        logger.debug(f"validate_dataframe con índices duplicados: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        # DataFrame sin columnas numéricas
        df_no_numeric = pd.DataFrame({'A': ['a', 'b', 'c']})
        is_valid, errors = validate_dataframe(df_no_numeric)
        logger.debug(f"validate_dataframe sin columnas numéricas: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        # Configuración con tipos incorrectos
        invalid_config = {
            'feature_enabled': "no es bool",
            'weight_value': "no es numérico"
        }
        is_valid, errors = validate_config(invalid_config)
        logger.debug(f"validate_config con tipos incorrectos: válido={is_valid}, errores={errors}")
        assert not is_valid
        assert len(errors) > 0
        
        logger.debug("test_edge_cases_and_error_handling completado exitosamente")


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "--tb=short"]) 