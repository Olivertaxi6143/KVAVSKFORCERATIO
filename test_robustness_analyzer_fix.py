"""
Test específico para verificar las correcciones de Pyright en robustness_analyzer.py.
"""

import pytest
import numpy as np
import pandas as pd
from src.core.robustness_analyzer import RobustnessAnalyzer

def test_robustness_analyzer_initialization():
    """Test que verifica la inicialización del RobustnessAnalyzer."""
    analyzer = RobustnessAnalyzer()
    assert analyzer is not None
    assert hasattr(analyzer, 'analyze_stability_metrics')
    assert hasattr(analyzer, 'detect_outliers')

def test_numpy_operations_in_robustness():
    """Test que verifica operaciones numpy seguras en robustness_analyzer."""
    # Crear datos de prueba
    df = pd.DataFrame({
        'Sharpe_Ratio': [1.2, 1.5, np.nan, 0.8, 2.1],
        'Drawdown': [0.05, 0.12, 0.08, np.nan, 0.15],
        'CAGR': [0.15, 0.22, 0.18, 0.25, np.nan],
        'Profit_factor': [1.8, 2.1, 1.9, 2.3, 1.7]
    })
    
    analyzer = RobustnessAnalyzer()
    
    # Test que las operaciones numpy funcionan correctamente
    try:
        # Estas operaciones deben funcionar sin errores de Pyright
        stability_metrics = analyzer.analyze_stability_metrics(df)
        assert isinstance(stability_metrics, dict)
        
        outlier_info = analyzer.detect_outliers(df)
        assert isinstance(outlier_info, dict)
        
        distribution_analysis = analyzer.analyze_distribution_robustness(df)
        assert isinstance(distribution_analysis, dict)
        
        overall_robustness = analyzer.calculate_overall_robustness(df)
        assert isinstance(overall_robustness, dict)
        
    except Exception as e:
        pytest.fail(f"Error en operaciones de robustness_analyzer: {e}")

def test_safe_numpy_operations():
    """Test que verifica operaciones numpy seguras."""
    # Test operaciones numpy que reemplazaron métodos pandas problemáticos
    arr = np.array([1, 2, np.nan, 4, 5])
    
    # Verificar que las operaciones numpy funcionan
    assert np.isnan(arr).any() == True
    # El percentil 25 de [1, 2, nan, 4, 5] es 1.75 (ignorando nan)
    assert np.nanpercentile(arr, 25) == 1.75
    assert np.nanpercentile(arr, 75) == 4.25
    
    # Verificar operaciones de comparación
    clean_arr = arr[~np.isnan(arr)]
    assert len(clean_arr) == 4
    assert np.all(clean_arr > 0)

def test_pandas_safe_operations():
    """Test que verifica operaciones pandas seguras."""
    df = pd.DataFrame({
        'A': [1, 2, np.nan, 4],
        'B': [5, 6, 7, np.nan]
    })
    
    # Verificar operaciones pandas estándar
    assert df['A'].isna().any() == True
    assert df['A'].median() == 2.0
    assert df['A'].fillna(0).tolist() == [1.0, 2.0, 0.0, 4.0]

def test_mixed_type_handling():
    """Test que verifica manejo de tipos mixtos."""
    # Test con diferentes tipos de datos
    mixed_data = {
        'numeric': [1, 2, 3],
        'with_nan': [1, np.nan, 3],
        'empty': []
    }
    
    # Verificar que las operaciones son robustas
    for key, data in mixed_data.items():
        arr = np.array(data)
        if len(arr) > 0:
            # Estas operaciones deben funcionar sin errores
            has_nan = np.isnan(arr).any()
            if has_nan:
                clean_arr = arr[~np.isnan(arr)]
                assert len(clean_arr) < len(arr)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 