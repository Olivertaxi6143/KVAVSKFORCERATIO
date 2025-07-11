#!/usr/bin/env python3
"""
Script de prueba simple para aislar el error en el análisis unificado.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import pandas as pd
from src.data_manager import DataManager
from src.core_engine_enhanced import run_unified_analysis_enhanced

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_analysis():
    """Prueba simple del análisis unificado."""
    try:
        print("=== PRUEBA DE ANÁLISIS UNIFICADO ===")
        
        # Cargar datos usando DataManager
        print("1. Cargando datos con DataManager...")
        dm = DataManager()
        success = dm.load_kpis_data('DatabankExport_M1.csv')
        if not success or dm.kpis_data is None:
            print("❌ Error cargando datos con DataManager")
            return False
            
        df = dm.kpis_data
        print(f"   Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
        print(f"   Columnas de estrategia: {[col for col in df.columns if 'strategy' in col.lower() or 'name' in col.lower()]}")
        
        # Ejecutar análisis
        print("2. Ejecutando análisis unificado...")
        result, summary = run_unified_analysis_enhanced(df)
        print(f"   Análisis completado: {len(result)} filas en resultado")
        
        # Verificar columnas del resultado
        print("3. Verificando columnas del resultado...")
        score_columns = [col for col in result.columns if 'Score' in col]
        print(f"   Columnas de score encontradas: {score_columns}")
        
        print("✅ PRUEBA EXITOSA")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analysis()
    sys.exit(0 if success else 1) 