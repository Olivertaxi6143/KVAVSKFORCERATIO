"""
Test para validar el módulo FactorKElite96Enhanced extraído.

Este test verifica que la clase se puede importar, construir y ejecutar evaluate_strategies
con un DataFrame de ejemplo.
"""

import pandas as pd
import numpy as np
import pytest
from src.core.analysis.factor_k_analyzer import FactorKElite96Enhanced

def test_factor_kelite96_construction():
    # Debe poder construirse sin error
    analyzer = FactorKElite96Enhanced()
    assert isinstance(analyzer, FactorKElite96Enhanced)

def test_factor_kelite96_evaluate_strategies():
    analyzer = FactorKElite96Enhanced()
    # DataFrame de ejemplo con columnas mínimas requeridas
    df = pd.DataFrame({
        'Strategy_Name': [f"strat{i}" for i in range(10)],
        'Sharpe_Ratio': np.random.normal(1, 0.5, 10),
        'CAGR': np.random.normal(0.2, 0.05, 10),
        'Max_DD_%': np.random.uniform(5, 20, 10),
        'Profit_factor': np.random.uniform(1.2, 2.0, 10),
        'FK96_Stability_Enhanced': np.random.uniform(7, 10, 10),
        'FK96_Growth_Enhanced': np.random.uniform(7, 10, 10),
        'FK96_Efficiency_Enhanced': np.random.uniform(7, 10, 10),
        'FK96_Consistency_Enhanced': np.random.uniform(7, 10, 10),
        'FK96_Risk_Enhanced': np.random.uniform(7, 10, 10)
    })
    # Debe ejecutarse sin error y devolver un DataFrame con Unified_Score
    result = analyzer.evaluate_strategies(df)
    assert isinstance(result, pd.DataFrame)
    assert 'Unified_Score' in result.columns
    assert len(result) == len(df)

if __name__ == "__main__":
    test_factor_kelite96_construction()
    test_factor_kelite96_evaluate_strategies()
    print("Test de FactorKElite96Enhanced completado correctamente.") 