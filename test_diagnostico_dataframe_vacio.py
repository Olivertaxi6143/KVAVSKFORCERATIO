#!/usr/bin/env python3
"""
Test de diagnóstico para identificar dónde se pierden los datos en el flujo de análisis.
Este test ejecuta cada paso del flujo de análisis de forma independiente para identificar
exactamente dónde se está vaciando el DataFrame.
"""

import sys
import os
import logging
import pandas as pd
import numpy as np
from pathlib import Path
import traceback

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.core_engine_enhanced import (
    FactorKElite96Enhanced,
    UnifiedEvaluatorEnhanced,
    DataLoaderEnhanced,
    run_complete_analysis_with_gui_integration
)
from src.data_manager import DataManager

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diagnostico_dataframe_vacio.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_diagnostico_completo():
    """Test completo de diagnóstico del flujo de datos."""
    
    print("🔍 INICIANDO DIAGNÓSTICO COMPLETO DEL FLUJO DE DATOS")
    print("=" * 80)
    
    # Configuración de prueba
    kpi_file = "DatabankExport_M1.csv"
    config = {
        "trading_style": "General",
        "alpha": 0.8,
        "min_trades_monthly": 10,
        "percentil": 80,
        "scientific_improvements": True,
        "is_oos_split": 0.75,
        "selected_kpis": {
            "CAGR": {"enabled": True, "weight": 1.0},
            "Sharpe_Ratio": {"enabled": True, "weight": 1.0},
            "Profit_factor": {"enabled": True, "weight": 1.0},
            "Drawdown": {"enabled": True, "weight": 1.0}
        },
        "enabled_kpi_names": ["CAGR", "Sharpe_Ratio", "Profit_factor", "Drawdown"],
        "extra_kpis_config": {},
        "enable_extra_kpis": True
    }
    
    try:
        # PASO 1: Verificar que el archivo existe y tiene datos
        print("\n📁 PASO 1: Verificando archivo de entrada")
        print("-" * 50)
        
        if not os.path.exists(kpi_file):
            print(f"❌ ERROR: Archivo {kpi_file} no encontrado")
            return False
        
        # Leer archivo directamente con pandas
        df_directo = pd.read_csv(kpi_file, sep=';', decimal=',')
        print(f"✅ Archivo leído directamente: {len(df_directo)} filas, {len(df_directo.columns)} columnas")
        print(f"📋 Columnas originales: {df_directo.columns.tolist()}")
        
        if df_directo.empty:
            print("❌ ERROR: Archivo está vacío")
            return False
        
        # PASO 2: Test DataManager
        print("\n📊 PASO 2: Test DataManager")
        print("-" * 50)
        
        dm = DataManager()
        success = dm.load_kpis_data(kpi_file)
        print(f"DataManager.load_kpis_data(): {success}")
        
        if success and dm.kpis_data is not None:
            print(f"✅ DataManager: {len(dm.kpis_data)} filas, {len(dm.kpis_data.columns)} columnas")
            print(f"📋 Columnas DataManager: {list(dm.kpis_data.columns)[:10]}...")
        else:
            print("❌ ERROR: DataManager no pudo cargar los datos")
            return False
        
        # PASO 3: Test DataLoaderEnhanced
        print("\n🔄 PASO 3: Test DataLoaderEnhanced")
        print("-" * 50)
        
        data_loader = DataLoaderEnhanced()
        df_loader = data_loader.load_and_prepare_data(kpi_file)
        
        print(f"✅ DataLoaderEnhanced: {len(df_loader)} filas, {len(df_loader.columns)} columnas")
        print(f"📋 Columnas DataLoader: {list(df_loader.columns)[:10]}...")
        
        if df_loader.empty:
            print("❌ ERROR: DataLoaderEnhanced devolvió DataFrame vacío")
            return False
        
        # PASO 4: Test FactorKElite96Enhanced
        print("\n⚙️ PASO 4: Test FactorKElite96Enhanced")
        print("-" * 50)
        
        factor_k = FactorKElite96Enhanced(config)
        factor_k.enable_scientific_improvements()
        
        # Test load_and_prepare_data
        df_factor_k_load = factor_k.load_and_prepare_data(kpi_file)
        print(f"✅ FactorK load_and_prepare_data: {len(df_factor_k_load)} filas, {len(df_factor_k_load.columns)} columnas")
        
        if df_factor_k_load.empty:
            print("❌ ERROR: FactorK load_and_prepare_data devolvió DataFrame vacío")
            return False
        
        # Test evaluate_strategies
        df_factor_k_eval = factor_k.evaluate_strategies(df_factor_k_load.copy())
        print(f"✅ FactorK evaluate_strategies: {len(df_factor_k_eval)} filas, {len(df_factor_k_eval.columns)} columnas")
        
        if df_factor_k_eval.empty:
            print("❌ ERROR: FactorK evaluate_strategies devolvió DataFrame vacío")
            return False
        
        # PASO 5: Test UnifiedEvaluatorEnhanced
        print("\n🔗 PASO 5: Test UnifiedEvaluatorEnhanced")
        print("-" * 50)
        
        evaluator = UnifiedEvaluatorEnhanced()
        df_unified = evaluator.evaluate_strategies_unified(df_factor_k_load.copy())
        
        print(f"✅ UnifiedEvaluator: {len(df_unified)} filas, {len(df_unified.columns)} columnas")
        
        if df_unified.empty:
            print("❌ ERROR: UnifiedEvaluator devolvió DataFrame vacío")
            return False
        
        # PASO 6: Test run_complete_analysis_with_gui_integration
        print("\n🎯 PASO 6: Test run_complete_analysis_with_gui_integration")
        print("-" * 50)
        
        results, summary = run_complete_analysis_with_gui_integration(
            kpi_file,
            config=config,
            analysis_type="unified"
        )
        
        print(f"✅ run_complete_analysis_with_gui_integration: {len(results)} filas, {len(results.columns)} columnas")
        
        if results.empty:
            print("❌ ERROR: run_complete_analysis_with_gui_integration devolvió DataFrame vacío")
            return False
        
        # PASO 7: Verificar columnas de score
        print("\n📈 PASO 7: Verificando columnas de score")
        print("-" * 50)
        
        score_columns = [col for col in results.columns if 'Score' in col or 'QVA' in col or 'Unified' in col]
        print(f"📊 Columnas de score encontradas: {score_columns}")
        
        if score_columns:
            for col in score_columns:
                if col in results.columns:
                    stats = results[col].describe()
                    print(f"📈 {col}: min={stats['min']:.4f}, max={stats['max']:.4f}, mean={stats['mean']:.4f}")
        
        # PASO 8: Resumen final
        print("\n🎉 RESUMEN FINAL")
        print("-" * 50)
        print(f"✅ Archivo original: {len(df_directo)} filas")
        print(f"✅ DataManager: {len(dm.kpis_data)} filas")
        print(f"✅ DataLoaderEnhanced: {len(df_loader)} filas")
        print(f"✅ FactorK load: {len(df_factor_k_load)} filas")
        print(f"✅ FactorK eval: {len(df_factor_k_eval)} filas")
        print(f"✅ UnifiedEvaluator: {len(df_unified)} filas")
        print(f"✅ Análisis completo: {len(results)} filas")
        
        print("\n✅ DIAGNÓSTICO COMPLETADO: Todos los pasos funcionan correctamente")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN DIAGNÓSTICO: {str(e)}")
        print(f"📋 Traceback completo:")
        traceback.print_exc()
        return False

def test_diagnostico_especifico():
    """Test de diagnóstico específico para identificar el punto exacto donde se pierden los datos."""
    
    print("\n🔍 DIAGNÓSTICO ESPECÍFICO - PUNTO EXACTO DE PÉRDIDA DE DATOS")
    print("=" * 80)
    
    kpi_file = "DatabankExport_M1.csv"
    
    try:
        # Cargar datos originales
        df_original = pd.read_csv(kpi_file, sep=';', decimal=',')
        print(f"📊 Datos originales: {len(df_original)} filas, {len(df_original.columns)} columnas")
        
        # Test cada paso individualmente
        steps = [
            ("DataManager", lambda: DataManager().load_kpis_data(kpi_file)),
            ("DataLoaderEnhanced", lambda: DataLoaderEnhanced().load_and_prepare_data(kpi_file)),
            ("FactorK load", lambda: FactorKElite96Enhanced().load_and_prepare_data(kpi_file)),
            ("FactorK eval", lambda: FactorKElite96Enhanced().evaluate_strategies(pd.read_csv(kpi_file, sep=';', decimal=','))),
            ("UnifiedEvaluator", lambda: UnifiedEvaluatorEnhanced().evaluate_strategies_unified(pd.read_csv(kpi_file, sep=';', decimal=','))),
        ]
        
        for step_name, step_func in steps:
            try:
                print(f"\n🔄 Probando: {step_name}")
                result = step_func()
                
                if hasattr(result, '__len__'):
                    print(f"✅ {step_name}: {len(result)} filas")
                else:
                    print(f"✅ {step_name}: {result}")
                    
            except Exception as e:
                print(f"❌ {step_name}: ERROR - {str(e)}")
                print(f"📋 Traceback para {step_name}:")
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ ERROR EN DIAGNÓSTICO ESPECÍFICO: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE DIAGNÓSTICO")
    print("=" * 80)
    
    # Test completo
    success_completo = test_diagnostico_completo()
    
    # Test específico
    test_diagnostico_especifico()
    
    if success_completo:
        print("\n✅ TODOS LOS TESTS PASARON - EL FLUJO FUNCIONA CORRECTAMENTE")
    else:
        print("\n❌ ALGUNOS TESTS FALLARON - REVISAR LOGS PARA DETALLES")
    
    print("\n📋 Revisar archivo 'diagnostico_dataframe_vacio.log' para detalles completos") 