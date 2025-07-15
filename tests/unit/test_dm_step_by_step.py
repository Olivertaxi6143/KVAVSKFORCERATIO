#!/usr/bin/env python3
"""
Test paso a paso del DataManager sin duplicaciones
"""
import sys
import os
import pandas as pd

# Añadir src/ al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.data_manager import DataManager

def main():
    print("=== TEST PASO A PASO DATAMANAGER ===")
    
    # Paso 1: Crear DataManager
    print("\n1. Creando DataManager...")
    dm = DataManager()
    print("✅ DataManager creado")
    
    # Paso 2: Cargar datos UNA SOLA VEZ
    print("\n2. Cargando datos UNA SOLA VEZ...")
    df = dm.load_and_prepare_data_pipeline("INPUTTEST/DatabankExport_M1.csv")
    print(f"✅ Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
    
    # Paso 3: Mostrar columnas finales
    print("\n3. Columnas finales:")
    for i, col in enumerate(df.columns):
        print(f"   {i+1:2d}. {col}")
    
    # Paso 4: Verificar columnas estándar
    print("\n4. Verificando columnas estándar:")
    standard_columns = [
        'strategy_name', 'cagr_is', 'cagr_oos', 'sharpe_ratio_is', 
        'sharpe_ratio_oos', 'profit_factor_is', 'profit_factor_oos',
        'max_dd_percent', 'number_of_trades', 'winning_percent_is', 
        'winning_percent_oos'
    ]
    
    found_standard = []
    missing_standard = []
    
    for col in standard_columns:
        if col in df.columns:
            found_standard.append(col)
            print(f"   ✅ {col}")
        else:
            missing_standard.append(col)
            print(f"   ❌ {col}")
    
    print(f"\n✅ Encontradas: {len(found_standard)} columnas estándar")
    print(f"❌ Faltantes: {len(missing_standard)} columnas estándar")
    
    print("\n✅ TEST COMPLETADO")

if __name__ == "__main__":
    main() 