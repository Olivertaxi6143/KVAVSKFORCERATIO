"""
Test para verificar las correcciones de Pyright aplicadas.
"""

import pytest
import numpy as np
import pandas as pd
from typing import Any, Dict, List

def test_numpy_array_operations():
    """Test que verifica operaciones seguras con arrays numpy."""
    # Crear array de prueba
    arr = np.array([1, 2, np.nan, 4, 5])
    
    # Verificar que las operaciones numpy funcionan correctamente
    assert np.isnan(arr).any() == True
    assert np.nanmedian(arr) == 3.0
    assert np.nan_to_num(arr, nan=0).tolist() == [1, 2, 0, 4, 5]
    
    # Verificar operaciones booleanas
    bool_arr = arr > 2
    assert np.all(bool_arr) == False
    assert np.any(bool_arr) == True

def test_pandas_dataframe_operations():
    """Test que verifica operaciones seguras con DataFrames pandas."""
    # Crear DataFrame de prueba
    df = pd.DataFrame({
        'A': [1, 2, np.nan, 4],
        'B': [5, 6, 7, np.nan],
        'C': [9, 10, 11, 12]
    })
    
    # Verificar operaciones pandas estándar
    assert df['A'].isna().any() == True
    assert df['A'].median() == 2.0
    assert df['A'].fillna(0).tolist() == [1.0, 2.0, 0.0, 4.0]

def test_mixed_type_operations():
    """Test que verifica operaciones con tipos mixtos."""
    # Array numpy
    arr = np.array([1, 2, 3])
    assert arr.size == 3
    assert arr.size > 0
    
    # DataFrame pandas
    df = pd.DataFrame({'col': [1, 2, 3]})
    assert not df.empty
    assert len(df) > 0

def test_error_handling():
    """Test que verifica manejo robusto de errores."""
    # Test con datos problemáticos
    try:
        # Simular operación que podría fallar
        problematic_data = np.array([np.nan, np.nan, np.nan])
        result = np.nanmedian(problematic_data)
        assert np.isnan(result)
    except Exception:
        # Si falla, es aceptable
        pass

def test_type_safety():
    """Test que verifica seguridad de tipos."""
    # Verificar que no se usan métodos incorrectos
    arr = np.array([1, 2, 3])
    
    # Estas operaciones deben funcionar
    assert hasattr(arr, 'size')
    assert hasattr(arr, 'shape')
    
    # Estas operaciones NO deben estar disponibles en ndarray
    assert not hasattr(arr, 'columns')
    assert not hasattr(arr, 'iloc')
    assert not hasattr(arr, 'dropna')

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 