#!/usr/bin/env python3
"""
Test para verificar las correcciones en data_manager.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from src.data.data_manager import DataManager

def test_data_manager_corrections():
    """Test básico para verificar que las correcciones funcionan"""
    print("🧪 Iniciando test de correcciones en DataManager...")
    
    try:
        # 1. Crear instancia de DataManager
        dm = DataManager()
        print("✅ DataManager creado correctamente")
        
        # 2. Crear DataFrame de prueba
        test_data = pd.DataFrame({
            'Strategy_Name': ['Test1', 'Test2'],
            'CAGR_IS': [10.5, 15.2],
            'CAGR_OOS': [8.3, 12.1],
            'Sharpe_Ratio_IS': [1.2, 1.8],
            'Max_DD_pct': [5.2, 3.8]
        })
        print("✅ DataFrame de prueba creado")
        
        # 3. Probar normalización de columnas
        normalized_df = dm._normalize_column_names(test_data)
        print(f"✅ Normalización completada: {len(normalized_df.columns)} columnas")
        
        # 4. Probar validación de DataFrame
        is_valid, errors = dm._validate_dataframe(normalized_df)
        print(f"✅ Validación completada: válido={is_valid}, errores={len(errors)}")
        
        # 5. Probar limpieza básica
        cleaned_df = dm._clean_data_basic(normalized_df)
        print(f"✅ Limpieza completada: {len(cleaned_df)} registros")
        
        # 6. Probar normalización numérica
        numeric_df = dm._normalize_numeric_columns(cleaned_df)
        print(f"✅ Normalización numérica completada: {len(numeric_df)} registros")
        
        print("🎉 Todas las correcciones funcionan correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False

if __name__ == "__main__":
    success = test_data_manager_corrections()
    sys.exit(0 if success else 1) 