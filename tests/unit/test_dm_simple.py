#!/usr/bin/env python3
"""
Test simple y directo del DataManager
"""
import sys
import os
import pandas as pd

# Añadir src/ al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.data_manager import DataManager

def main():
    print("=== TEST SIMPLE DATAMANAGER ===")
    
    # Crear DataManager
    dm = DataManager()
    print("✅ DataManager creado")
    
    # Cargar datos
    df = dm.load_and_prepare_data_pipeline("INPUTTEST/DatabankExport_M1.csv")
    print(f"✅ Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
    
    # Mostrar columnas estándar
    standard_columns = [
        'strategy_name', 'cagr_is', 'cagr_oos', 'sharpe_ratio_is', 
        'sharpe_ratio_oos', 'profit_factor_is', 'profit_factor_oos',
        'max_dd_percent', 'number_of_trades', 'winning_percent_is', 
        'winning_percent_oos'
    ]
    
    print("\n=== COLUMNAS ESTÁNDAR ===")
    for col in standard_columns:
        if col in df.columns:
            if df[col].isnull().all():
                first_value = 'N/A'
            else:
                first_value = str(df[col].iloc[0])
            print(f"✅ {col}: {first_value}")
        else:
            print(f"❌ {col}: NO ENCONTRADA")
    
    # Mostrar primeras filas
    print("\n=== PRIMERAS 3 FILAS ===")
    print(df.head(3).to_string())
    
    print("\n✅ TEST COMPLETADO")

if __name__ == "__main__":
    main() 