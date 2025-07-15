#!/usr/bin/env python3
"""
Test específico para verificar la función predictividad_is_oos_empirica.
"""

import sys
import os
import pandas as pd
import numpy as np
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

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
    from src.core.integration_layer import predictividad_is_oos_empirica
    
    try:
        # Aplicar la función
        print("\n🔄 Aplicando predictividad_is_oos_empirica...")
        df_result = predictividad_is_oos_empirica(df, is_oos_split=0.75)
        
        print(f"✅ Resultado: {len(df_result)} filas, {len(df_result.columns)} columnas")
        
        # Usar assert en lugar de return False
        assert not df_result.empty, "predictividad_is_oos_empirica devolvió DataFrame vacío"
        logger.debug("assert passed: DataFrame no está vacío")
        
        print("✅ predictividad_is_oos_empirica funcionó correctamente")
        
        # Verificar columnas nuevas
        nuevas_columnas = [col for col in df_result.columns if col not in df.columns]
        print(f"📋 Columnas nuevas agregadas: {nuevas_columnas}")
        
        # Verificar que se añadieron columnas de predictibilidad
        assert 'predictability_score' in df_result.columns, "Falta columna predictability_score"
        logger.debug("assert passed: columna predictability_score presente")
        
        assert True
        
    except Exception as e:
        print(f"❌ ERROR en predictividad_is_oos_empirica: {e}")
        import traceback
        traceback.print_exc()
        raise

def test_unified_evaluator():
    """Test específico del UnifiedEvaluatorEnhanced."""
    
    print("\n🔍 TEST ESPECÍFICO: UnifiedEvaluatorEnhanced")
    print("=" * 60)
    
    # Cargar datos de prueba
    kpi_file = "DatabankExport_M1.csv"
    df = pd.read_csv(kpi_file, sep=';', decimal=',')
    
    print(f"📊 Datos originales: {len(df)} filas, {len(df.columns)} columnas")
    
    # Importar el evaluador
    from src.core.integration_layer import UnifiedEvaluatorEnhanced
    
    try:
        # Crear evaluador
        evaluator = UnifiedEvaluatorEnhanced()
        
        # Evaluar estrategias
        print("\n🔄 Evaluando estrategias con UnifiedEvaluator...")
        df_result = evaluator.evaluate_strategies_unified(df)
        
        print(f"✅ Resultado: {len(df_result)} filas, {len(df_result.columns)} columnas")
        
        # Usar assert en lugar de return False
        assert not df_result.empty, "UnifiedEvaluator devolvió DataFrame vacío"
        logger.debug("assert passed: DataFrame no está vacío")
        
        print("✅ UnifiedEvaluator funcionó correctamente")
        
        # Verificar columnas de score
        score_columns = [col for col in df_result.columns if 'Score' in col or 'Unified' in col]
        print(f"📊 Columnas de score: {score_columns}")
        
        # Verificar que hay al menos una columna de score
        assert len(score_columns) > 0, "No se encontraron columnas de score"
        logger.debug("assert passed: columnas de score presentes")
        
        assert True
        
    except Exception as e:
        print(f"❌ ERROR en UnifiedEvaluator: {e}")
        import traceback
        traceback.print_exc()
        raise

def test_factor_k_enhanced():
    """Test específico del FactorKElite96Enhanced."""
    
    print("\n🔍 TEST ESPECÍFICO: FactorKElite96Enhanced")
    print("=" * 60)
    
    # Cargar datos de prueba
    kpi_file = "DatabankExport_M1.csv"
    df = pd.read_csv(kpi_file, sep=';', decimal=',')
    
    print(f"📊 Datos originales: {len(df)} filas, {len(df.columns)} columnas")
    
    # Importar el evaluador
    from src.core.integration_layer import FactorKElite96Enhanced
    
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
        
        # Evaluar estrategias
        print("\n🔄 Evaluando estrategias con FactorKElite96Enhanced...")
        df_result = factor_k.run_complete_analysis(df)
        
        print(f"✅ Resultado: {len(df_result)} filas, {len(df_result.columns)} columnas")
        
        # Usar assert en lugar de return False
        assert not df_result.empty, "FactorKElite96Enhanced devolvió DataFrame vacío"
        logger.debug("assert passed: DataFrame no está vacío")
        
        print("✅ FactorKElite96Enhanced funcionó correctamente")
        
        # Verificar columnas de score
        score_columns = [col for col in df_result.columns if 'Score' in col or 'Factor_K' in col]
        print(f"📊 Columnas de score: {score_columns}")
        
        # Verificar que hay al menos una columna de score
        assert len(score_columns) > 0, "No se encontraron columnas de score"
        logger.debug("assert passed: columnas de score presentes")
        
        assert True
        
    except Exception as e:
        print(f"❌ ERROR en FactorKElite96Enhanced: {e}")
        import traceback
        traceback.print_exc()
        raise

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