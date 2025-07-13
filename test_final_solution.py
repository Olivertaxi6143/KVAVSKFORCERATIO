#!/usr/bin/env python3
"""
Test final para verificar la solución del error de asignación de string.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import pandas as pd
from src.data_manager import DataManager
from src.core.integration_layer import UnifiedEvaluatorEnhanced

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_final_solution():
    """Test final de la solución."""
    try:
        print("=== TEST FINAL - SOLUCIÓN ERROR ASIGNACIÓN ===")
        
        # 1. Cargar datos
        print("1. Cargando datos...")
        dm = DataManager()
        success = dm.load_kpis_data('DatabankExport_M1.csv')
        if not success or dm.kpis_data is None:
            print("❌ Error cargando datos")
            return False
            
        df = dm.kpis_data
        print(f"   ✅ Datos cargados: {len(df)} filas")
        
        # 2. Crear evaluador unificado
        print("2. Creando evaluador unificado...")
        evaluator = UnifiedEvaluatorEnhanced()
        print("   ✅ Evaluador creado")
        
        # 3. Ejecutar evaluación unificada
        print("3. Ejecutando evaluación unificada...")
        result = evaluator.evaluate_strategies_unified(df)
        print(f"   ✅ Evaluación completada: {len(result)} filas")
        
        # 4. Verificar columnas de score
        print("4. Verificando columnas de score...")
        score_columns = [col for col in result.columns if 'Score' in col]
        print(f"   ✅ Columnas de score: {score_columns}")
        
        # 5. Verificar que no hay errores
        print("5. Verificando integridad de datos...")
        for col in score_columns:
            if col in result.columns:
                print(f"   ✅ {col}: {result[col].dtype}")
        
        print("🎉 TEST FINAL EXITOSO - ERROR RESUELTO")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_final_solution()
    sys.exit(0 if success else 1) 