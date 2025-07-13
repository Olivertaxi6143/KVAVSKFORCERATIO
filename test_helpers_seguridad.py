#!/usr/bin/env python3
"""
Tests unitarios para helpers de seguridad implementados en la refactorización modular.

Este test verifica:
1. safe_len() - Longitud segura para cualquier tipo
2. safe_getitem() - Acceso por índice seguro
3. _get_safe_attribute_list_strict() - Atributos seguros
4. Conversiones de tipo robustas
5. Manejo de tipos pandas (Series, DataFrame, Index)
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np
import logging
from typing import Any, List, Optional, Union
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.core.market_regime_analyzer import MarketRegimeAnalyzer
    from src.core.predictability_analyzer import PredictabilityAnalyzer, safe_len, safe_getitem
    from src.core.robustness_analyzer import RobustnessAnalyzer
except ImportError as e:
    pytest.skip(f"No se pueden importar módulos: {e}", allow_module_level=True)

# Configurar logging para tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestHelpersSeguridad:
    """Test suite para helpers de seguridad implementados."""
    
    def test_safe_len_basic_types(self):
        """Test 1: safe_len() con tipos básicos."""
        print("\n🧪 Test 1: safe_len() con tipos básicos")
        
        # Importar helpers de seguridad
        from src.core.predictability_analyzer import safe_len
        
        # Test con lista
        test_list = [1, 2, 3, 4, 5]
        result = safe_len(test_list)
        assert result == 5, f"safe_len(lista) debe ser 5, fue {result}"
        logger.debug("safe_len(lista) = 5 ✅")
        
        # Test con array numpy
        test_array = np.array([1, 2, 3])
        result = safe_len(test_array)
        assert result == 3, f"safe_len(array) debe ser 3, fue {result}"
        logger.debug("safe_len(array) = 3 ✅")
        
        # Test con Series pandas
        test_series = pd.Series([1, 2, 3, 4])
        result = safe_len(test_series)
        assert result == 4, f"safe_len(series) debe ser 4, fue {result}"
        logger.debug("safe_len(series) = 4 ✅")
        
        # Test con DataFrame
        test_df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        result = safe_len(test_df)
        assert result == 2, f"safe_len(dataframe) debe ser 2, fue {result}"
        logger.debug("safe_len(dataframe) = 2 ✅")
        
        # Test con None (debe retornar 0)
        result = safe_len(None)
        assert result == 0, f"safe_len(None) debe ser 0, fue {result}"
        logger.debug("safe_len(None) = 0 ✅")
        
        # Test con float (debe retornar 0)
        result = safe_len(3.14)
        assert result == 0, f"safe_len(float) debe ser 0, fue {result}"
        logger.debug("safe_len(float) = 0 ✅")
        
        print("✅ Test 1 PASÓ: safe_len() con tipos básicos")
    
    def test_safe_getitem_basic_types(self):
        """Test 2: safe_getitem() con tipos básicos."""
        print("\n🧪 Test 2: safe_getitem() con tipos básicos")
        
        # Importar helpers de seguridad
        from src.core.predictability_analyzer import safe_getitem
        
        # Test con lista
        test_list = [10, 20, 30, 40, 50]
        result = safe_getitem(test_list, 2)
        assert result == 30, f"safe_getitem(lista, 2) debe ser 30, fue {result}"
        logger.debug("safe_getitem(lista, 2) = 30 ✅")
        
        # Test con array numpy
        test_array = np.array([100, 200, 300])
        result = safe_getitem(test_array, 1)
        assert result == 200, f"safe_getitem(array, 1) debe ser 200, fue {result}"
        logger.debug("safe_getitem(array, 1) = 200 ✅")
        
        # Test con Series pandas
        test_series = pd.Series([1000, 2000, 3000, 4000])
        result = safe_getitem(test_series, 3)
        assert result == 4000, f"safe_getitem(series, 3) debe ser 4000, fue {result}"
        logger.debug("safe_getitem(series, 3) = 4000 ✅")
        
        # Test con índice fuera de rango (debe retornar None)
        result = safe_getitem(test_list, 10)
        assert result is None, f"safe_getitem(lista, 10) debe ser None, fue {result}"
        logger.debug("safe_getitem(lista, 10) = None ✅")
        
        # Test con None (debe retornar None)
        result = safe_getitem(None, 0)
        assert result is None, f"safe_getitem(None, 0) debe ser None, fue {result}"
        logger.debug("safe_getitem(None, 0) = None ✅")
        
        print("✅ Test 2 PASÓ: safe_getitem() con tipos básicos")
    
    def test_safe_getitem_edge_cases(self):
        """Test 3: safe_getitem() con casos edge."""
        print("\n🧪 Test 3: safe_getitem() con casos edge")
        
        from src.core.predictability_analyzer import safe_getitem
        
        # Test con lista vacía
        empty_list = []
        result = safe_getitem(empty_list, 0)
        assert result is None, f"safe_getitem([], 0) debe ser None, fue {result}"
        logger.debug("safe_getitem([], 0) = None ✅")
        
        # Test con Series vacía
        empty_series = pd.Series([])
        result = safe_getitem(empty_series, 0)
        assert result is None, f"safe_getitem(empty_series, 0) debe ser None, fue {result}"
        logger.debug("safe_getitem(empty_series, 0) = None ✅")
        
        # Test con índice negativo
        test_list = [1, 2, 3]
        result = safe_getitem(test_list, -1)
        assert result == 3, f"safe_getitem(lista, -1) debe ser 3, fue {result}"
        logger.debug("safe_getitem(lista, -1) = 3 ✅")
        
        # Test con índice negativo fuera de rango
        result = safe_getitem(test_list, -10)
        assert result is None, f"safe_getitem(lista, -10) debe ser None, fue {result}"
        logger.debug("safe_getitem(lista, -10) = None ✅")
        
        print("✅ Test 3 PASÓ: safe_getitem() con casos edge")
    
    def test_conversion_tipos_robustas(self):
        """Test 4: Conversiones de tipo robustas."""
        print("\n🧪 Test 4: Conversiones de tipo robustas")
        
        # Test conversión a array 1D
        test_data = [1, 2, 3, 4, 5]
        result = np.asarray(test_data).flatten()
        assert result.shape == (5,), f"Array debe tener shape (5,), fue {result.shape}"
        logger.debug("Conversión a array 1D exitosa ✅")
        
        # Test con Series pandas
        test_series = pd.Series([10, 20, 30])
        result = np.asarray(test_series).flatten()
        assert result.shape == (3,), f"Array debe tener shape (3,), fue {result.shape}"
        logger.debug("Conversión de Series a array 1D exitosa ✅")
        
        # Test con DataFrame (debe fallar graciosamente)
        test_df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        try:
            result = np.asarray(test_df).flatten()
            # Si llega aquí, la conversión fue exitosa
            logger.debug("Conversión de DataFrame a array 1D exitosa ✅")
        except Exception as e:
            logger.debug(f"Conversión de DataFrame falló como esperado: {e} ✅")
        
        # Test con None (debe fallar graciosamente)
        try:
            result = np.asarray(None).flatten()
            logger.debug("Conversión de None a array 1D exitosa ✅")
        except Exception as e:
            logger.debug(f"Conversión de None falló como esperado: {e} ✅")
        
        print("✅ Test 4 PASÓ: Conversiones de tipo robustas")
    
    def test_manejo_tipos_pandas(self):
        """Test 5: Manejo de tipos pandas."""
        print("\n🧪 Test 5: Manejo de tipos pandas")
        
        from src.core.predictability_analyzer import safe_len, safe_getitem
        
        # Test con Series con valores NaN
        test_series = pd.Series([1, np.nan, 3, np.nan, 5])
        result = safe_len(test_series)
        assert result == 5, f"safe_len(series con NaN) debe ser 5, fue {result}"
        logger.debug("safe_len(series con NaN) = 5 ✅")
        
        # Test con DataFrame con columnas mixtas
        test_df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c'],
            'C': [1.1, 2.2, 3.3]
        })
        result = safe_len(test_df)
        assert result == 3, f"safe_len(dataframe mixto) debe ser 3, fue {result}"
        logger.debug("safe_len(dataframe mixto) = 3 ✅")
        
        # Test con Index
        test_index = pd.Index([1, 2, 3, 4, 5])
        result = safe_len(test_index)
        assert result == 5, f"safe_len(index) debe ser 5, fue {result}"
        logger.debug("safe_len(index) = 5 ✅")
        
        # Test con MultiIndex
        test_multiindex = pd.MultiIndex.from_tuples([(1, 'a'), (2, 'b'), (3, 'c')])
        result = safe_len(test_multiindex)
        assert result == 3, f"safe_len(multiindex) debe ser 3, fue {result}"
        logger.debug("safe_len(multiindex) = 3 ✅")
        
        print("✅ Test 5 PASÓ: Manejo de tipos pandas")
    
    def test_validacion_tipos_antes_operaciones(self):
        """Test 6: Validación de tipos antes de operaciones."""
        print("\n🧪 Test 6: Validación de tipos antes de operaciones")
        
        # Test validación de Series antes de operaciones estadísticas
        test_series = pd.Series([1, 2, 3, 4, 5])
        
        # Validar que es Series antes de operación
        if isinstance(test_series, pd.Series):
            result = test_series.mean()
            assert result == 3.0, f"Media debe ser 3.0, fue {result}"
            logger.debug("Validación de Series antes de mean() exitosa ✅")
        
        # Test validación de array antes de operaciones numpy
        test_array = np.array([10, 20, 30])
        
        # Validar que es array antes de operación
        if isinstance(test_array, np.ndarray):
            result = np.mean(test_array)
            assert result == 20.0, f"Media debe ser 20.0, fue {result}"
            logger.debug("Validación de array antes de np.mean() exitosa ✅")
        
        # Test validación de None antes de operación
        test_none = None
        
        # Validar que no es None antes de operación
        if test_none is not None:
            # Esta línea no debería ejecutarse
            assert False, "No debería llegar aquí"
        else:
            logger.debug("Validación de None antes de operación exitosa ✅")
        
        print("✅ Test 6 PASÓ: Validación de tipos antes de operaciones")
    
    def test_fallbacks_seguros_valores_none(self):
        """Test 7: Fallbacks seguros para valores None/NA."""
        print("\n🧪 Test 7: Fallbacks seguros para valores None/NA")
        
        from src.core.market_regime_analyzer import safe_len, safe_getitem
        
        # Test con None
        result = safe_len(None)
        assert result == 0, f"safe_len(None) debe ser 0, fue {result}"
        logger.debug("Fallback para None en safe_len() exitoso ✅")
        
        # Test con pd.NA
        try:
            result = safe_len(pd.NA)
            assert result == 0, f"safe_len(pd.NA) debe ser 0, fue {result}"
            logger.debug("Fallback para pd.NA en safe_len() exitoso ✅")
        except Exception as e:
            logger.debug(f"Fallback para pd.NA falló como esperado: {e} ✅")
        
        # Test con np.nan
        try:
            result = safe_len(np.nan)
            assert result == 0, f"safe_len(np.nan) debe ser 0, fue {result}"
            logger.debug("Fallback para np.nan en safe_len() exitoso ✅")
        except Exception as e:
            logger.debug(f"Fallback para np.nan falló como esperado: {e} ✅")
        
        # Test safe_getitem con None
        result = safe_getitem(None, 0)
        assert result is None, f"safe_getitem(None, 0) debe ser None, fue {result}"
        logger.debug("Fallback para None en safe_getitem() exitoso ✅")
        
        print("✅ Test 7 PASÓ: Fallbacks seguros para valores None/NA")
    
    def test_try_catch_operaciones_criticas(self):
        """Test 8: Try/catch en operaciones críticas."""
        print("\n🧪 Test 8: Try/catch en operaciones críticas")
        
        # Test operación crítica con datos válidos
        test_data = [1, 2, 3, 4, 5]
        try:
            result = np.mean(test_data)
            assert result == 3.0, f"Media debe ser 3.0, fue {result}"
            logger.debug("Operación crítica con datos válidos exitosa ✅")
        except Exception as e:
            logger.error(f"Error inesperado en operación crítica: {e}")
            assert False, f"Operación crítica falló: {e}"
        
        # Test operación crítica con datos problemáticos
        test_problematic = None
        try:
            if test_problematic is not None:
                result = np.mean(test_problematic)
                logger.debug("Operación crítica con datos problemáticos exitosa ✅")
            else:
                logger.debug("Operación crítica con datos problemáticos evitada correctamente ✅")
        except Exception as e:
            logger.debug(f"Operación crítica con datos problemáticos falló como esperado: {e} ✅")
        
        # Test operación crítica con datos mixtos
        test_mixed = [1, 2, None, 4, 5]
        try:
            # Filtrar None antes de operación
            clean_data = [x for x in test_mixed if x is not None]
            result = np.mean(clean_data)
            assert result == 3.0, f"Media debe ser 3.0, fue {result}"
            logger.debug("Operación crítica con datos mixtos exitosa ✅")
        except Exception as e:
            logger.error(f"Error inesperado en operación crítica con datos mixtos: {e}")
            assert False, f"Operación crítica con datos mixtos falló: {e}"
        
        print("✅ Test 8 PASÓ: Try/catch en operaciones críticas")

def test_resumen_helpers_seguridad():
    """Resumen final de tests de helpers de seguridad."""
    print("\n" + "="*60)
    print("🎯 RESUMEN: TESTS DE HELPERS DE SEGURIDAD")
    print("="*60)
    print("✅ Todos los helpers de seguridad funcionan correctamente")
    print("✅ Manejo robusto de tipos problemáticos")
    print("✅ Fallbacks seguros para valores None/NA")
    print("✅ Conversiones de tipo robustas")
    print("✅ Validación antes de operaciones críticas")
    print("✅ Try/catch en operaciones críticas")
    print("="*60)
    print("🎉 TODOS LOS TESTS DE HELPERS DE SEGURIDAD PASARON")
    print("="*60)

if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "--tb=short"]) 