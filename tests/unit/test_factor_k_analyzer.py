"""
Test para validar el módulo FactorKElite96Enhanced extraído.

Este test verifica que la clase se puede importar, construir y ejecutar evaluate_strategies
con un DataFrame de ejemplo.
"""

import pytest
import pandas as pd
import numpy as np
from src.core.analysis.factor_k_analyzer import FactorKElite96Enhanced

def test_factor_kelite96_construction():
    """Test de construcción del analizador."""
    analyzer = FactorKElite96Enhanced()
    assert analyzer is not None
    assert analyzer.scientific_improvements_enabled == True

def test_factor_kelite96_evaluate_strategies():
    """Test de evaluación de estrategias."""
    analyzer = FactorKElite96Enhanced()
    
    # Crear datos de prueba (mínimo 5 estrategias)
    data = {
        'Strategy_Name': ['Strategy1', 'Strategy2', 'Strategy3', 'Strategy4', 'Strategy5'],
        'Sharpe_Ratio': [1.5, 2.0, 0.8, 1.1, 1.7],
        'Max_DD_%': [15.0, 10.0, 25.0, 18.0, 12.0],
        'CAGR': [12.0, 18.0, 8.0, 10.0, 14.0],
        'Profit_factor': [1.8, 2.2, 1.3, 1.5, 1.9],
        'Total_Trades': [150, 200, 80, 120, 160]
    }
    
    df = pd.DataFrame(data)
    result = analyzer.evaluate_strategies(df)
    
    assert len(result) == 5
    assert 'FK96_Elite_Enhanced' in result.columns
    assert 'Quality_Category' in result.columns

def test_temporal_component_new_strategies():
    """Test específico para el componente temporal con estrategias con pocos trades (deberían ser penalizadas)."""
    analyzer = FactorKElite96Enhanced()
    data = {
        'Strategy_Name': ['New1', 'New2', 'Proven1', 'Proven2', 'Proven3'],
        'Sharpe_Ratio': [1.2, 1.8, 1.5, 2.0, 1.6],
        'Max_DD_%': [20.0, 15.0, 12.0, 8.0, 10.0],
        'CAGR': [10.0, 15.0, 12.0, 18.0, 13.0],
        'Profit_factor': [1.5, 1.8, 1.6, 2.1, 1.7],
        'TimeFrame': ['M1', 'M1', 'M1', 'M1', 'M1'],
        'Total Data Months': [12, 12, 12, 12, 12],
        '# of trades': [10, 15, 30, 40, 28],  # New1 y New2 penalizadas
    }
    df = pd.DataFrame(data)
    result = analyzer.evaluate_strategies(df)
    penalizadas = result['FK96_Temporal_Component'] == 0.2
    no_penalizadas = result['FK96_Temporal_Component'] == 0.8
    assert penalizadas.sum() == 2  # Dos estrategias penalizadas
    assert no_penalizadas.sum() == 3  # Tres no penalizadas
    print(f"✅ Test temporal component: penalizadas={penalizadas.sum()}, no penalizadas={no_penalizadas.sum()}")

def test_temporal_component_edge_cases():
    """Test de casos extremos para el componente temporal."""
    analyzer = FactorKElite96Enhanced()
    # Caso 1: Todas penalizadas
    data_new_only = {
        'Strategy_Name': ['New1', 'New2', 'New3', 'New4', 'New5'],
        'Sharpe_Ratio': [1.0, 1.5, 2.0, 1.3, 1.7],
        'Max_DD_%': [25.0, 20.0, 15.0, 22.0, 18.0],
        'CAGR': [8.0, 12.0, 16.0, 10.0, 14.0],
        'Profit_factor': [1.2, 1.6, 2.0, 1.4, 1.8],
        'TimeFrame': ['H1']*5,
        'Total Data Months': [12]*5,
        '# of trades': [10, 12, 14, 13, 11],  # Todas penalizadas (mínimo H1=18/año)
    }
    df_new_only = pd.DataFrame(data_new_only)
    result_new_only = analyzer.evaluate_strategies(df_new_only)
    assert (result_new_only['FK96_Temporal_Component'] == 0.2).all()
    # Caso 2: Todas robustas
    data_proven_only = {
        'Strategy_Name': ['Proven1', 'Proven2', 'Proven3', 'Proven4', 'Proven5'],
        'Sharpe_Ratio': [1.5, 2.0, 2.5, 1.8, 2.2],
        'Max_DD_%': [10.0, 8.0, 5.0, 12.0, 9.0],
        'CAGR': [15.0, 18.0, 22.0, 14.0, 19.0],
        'Profit_factor': [1.8, 2.2, 2.6, 1.9, 2.3],
        'TimeFrame': ['D1']*5,
        'Total Data Months': [24]*5,
        '# of trades': [20, 18, 25, 22, 30],  # Todas robustas (mínimo D1=6/año)
    }
    df_proven_only = pd.DataFrame(data_proven_only)
    result_proven_only = analyzer.evaluate_strategies(df_proven_only)
    assert (result_proven_only['FK96_Temporal_Component'] == 0.8).all()
    print("✅ Test edge cases: penalización temporal aplicada correctamente")

def test_temporal_component_integration_real_file():
    """Test de integración: componente temporal usando datos reales de INPUTTEST/DatabankExport_M1.csv."""
    analyzer = FactorKElite96Enhanced()
    file_path = "INPUTTEST/DatabankExport_M1.csv"
    df = analyzer.load_and_prepare_data(file_path)
    if 'Strategy Name' in df.columns and 'Strategy_Name' not in df.columns:
        df = df.rename(columns={'Strategy Name': 'Strategy_Name'})
    result = analyzer.evaluate_strategies(df)
    assert 'FK96_Temporal_Component' in result.columns
    assert result['FK96_Temporal_Component'].between(0, 1).all()

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 