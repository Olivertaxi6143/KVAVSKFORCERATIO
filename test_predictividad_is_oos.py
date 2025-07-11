#!/usr/bin/env python3
"""
Test específico para verificar la función predictividad_is_oos_empirica.
"""

import sys
import os
import pandas as pd
import numpy as np

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def test_predictividad_is_oos():
    """Test específico de la función predictividad_is_oos_empirica."""
    
    print("🔍 TEST ESPECÍFICO: predictividad_is_oos_empirica")
    print("=" * 60)
    
    # Cargar datos de prueba
    kpi_file = "DatabankExport_M1.csv"
    df = pd.read_csv(kpi_file, sep=';', decimal=',')
    
    print(f"📊 Datos originales: {len(df)} filas, {len(df.columns)} columnas")
    print(f"📋 Columnas originales: {list(df.columns)[:10]}...")
    
    # Importar la función
    from src.core_engine_enhanced import predictividad_is_oos_empirica
    
    try:
        # Aplicar la función
        print("\n🔄 Aplicando predictividad_is_oos_empirica...")
        df_result = predictividad_is_oos_empirica(df, is_oos_split=0.75)
        
        print(f"✅ Resultado: {len(df_result)} filas, {len(df_result.columns)} columnas")
        
        if df_result.empty:
            print("❌ PROBLEMA ENCONTRADO: predictividad_is_oos_empirica devolvió DataFrame vacío")
            return False
        else:
            print("✅ predictividad_is_oos_empirica funcionó correctamente")
            
            # Verificar columnas nuevas
            nuevas_columnas = [col for col in df_result.columns if col not in df.columns]
            print(f"📋 Columnas nuevas agregadas: {nuevas_columnas}")
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR en predictividad_is_oos_empirica: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unified_evaluator():
    """Test específico del UnifiedEvaluatorEnhanced."""
    
    print("\n🔍 TEST ESPECÍFICO: UnifiedEvaluatorEnhanced")
    print("=" * 60)
    
    # Cargar datos de prueba
    kpi_file = "DatabankExport_M1.csv"
    df = pd.read_csv(kpi_file, sep=';', decimal=',')
    
    print(f"📊 Datos originales: {len(df)} filas, {len(df.columns)} columnas")
    
    # Importar el evaluador
    from src.core_engine_enhanced import UnifiedEvaluatorEnhanced
    
    try:
        # Crear evaluador
        evaluator = UnifiedEvaluatorEnhanced()
        
        # Evaluar estrategias
        print("\n🔄 Evaluando estrategias con UnifiedEvaluator...")
        df_result = evaluator.evaluate_strategies_unified(df)
        
        print(f"✅ Resultado: {len(df_result)} filas, {len(df_result.columns)} columnas")
        
        if df_result.empty:
            print("❌ PROBLEMA ENCONTRADO: UnifiedEvaluator devolvió DataFrame vacío")
            return False
        else:
            print("✅ UnifiedEvaluator funcionó correctamente")
            
            # Verificar columnas de score
            score_columns = [col for col in df_result.columns if 'Score' in col or 'Unified' in col]
            print(f"📊 Columnas de score: {score_columns}")
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR en UnifiedEvaluator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_factor_k_enhanced():
    """Test específico del FactorKElite96Enhanced."""
    
    print("\n🔍 TEST ESPECÍFICO: FactorKElite96Enhanced")
    print("=" * 60)
    
    # Cargar datos de prueba
    kpi_file = "DatabankExport_M1.csv"
    df = pd.read_csv(kpi_file, sep=';', decimal=',')
    
    print(f"📊 Datos originales: {len(df)} filas, {len(df.columns)} columnas")
    
    # Importar el evaluador
    from src.core_engine_enhanced import FactorKElite96Enhanced
    
    try:
        # Crear evaluador
        config = {
            "trading_style": "General",
            "alpha": 0.8,
            "min_trades_monthly": 10,
            "percentil": 80,
            "scientific_improvements": True,
            "is_oos_split": 0.75
        }
        
        factor_k = FactorKElite96Enhanced(config)
        factor_k.enable_scientific_improvements()
        
        # Evaluar estrategias
        print("\n🔄 Evaluando estrategias con FactorKElite96Enhanced...")
        df_result = factor_k.evaluate_strategies(df)
        
        print(f"✅ Resultado: {len(df_result)} filas, {len(df_result.columns)} columnas")
        
        if df_result.empty:
            print("❌ PROBLEMA ENCONTRADO: FactorKElite96Enhanced devolvió DataFrame vacío")
            return False
        else:
            print("✅ FactorKElite96Enhanced funcionó correctamente")
            
            # Verificar columnas de score
            score_columns = [col for col in df_result.columns if 'Score' in col or 'FK96' in col]
            print(f"📊 Columnas de score: {score_columns}")
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR en FactorKElite96Enhanced: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS ESPECÍFICOS")
    print("=" * 80)
    
    tests = [
        ("predictividad_is_oos_empirica", test_predictividad_is_oos),
        ("UnifiedEvaluatorEnhanced", test_unified_evaluator),
        ("FactorKElite96Enhanced", test_factor_k_enhanced)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASÓ")
            else:
                print(f"❌ {test_name}: FALLÓ")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    print("\n📊 RESUMEN DE TESTS ESPECÍFICOS")
    print("-" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("✅ TODOS LOS TESTS ESPECÍFICOS PASARON")
    else:
        print("❌ ALGUNOS TESTS ESPECÍFICOS FALLARON - IDENTIFICADO EL PROBLEMA") 