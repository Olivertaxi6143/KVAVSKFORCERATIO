#!/usr/bin/env python3
"""
Test de diagnóstico simple para identificar el problema del DataFrame vacío.
"""

import sys
import os
import pandas as pd
import traceback

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def test_archivo_entrada():
    """Test básico del archivo de entrada."""
    print("🔍 TEST 1: Verificando archivo de entrada")
    print("-" * 50)
    
    kpi_file = "DatabankExport_M1.csv"
    
    if not os.path.exists(kpi_file):
        print(f"❌ ERROR: Archivo {kpi_file} no encontrado")
        return False
    
    try:
        df = pd.read_csv(kpi_file, sep=';', decimal=',')
        print(f"✅ Archivo leído: {len(df)} filas, {len(df.columns)} columnas")
        print(f"📋 Columnas: {df.columns.tolist()}")
        
        if df.empty:
            print("❌ ERROR: DataFrame está vacío")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR leyendo archivo: {e}")
        traceback.print_exc()
        return False

def test_data_manager():
    """Test básico del DataManager."""
    print("\n🔍 TEST 2: Verificando DataManager")
    print("-" * 50)
    
    try:
        from src.data_manager import DataManager
        
        dm = DataManager()
        success = dm.load_kpis_data("DatabankExport_M1.csv")
        
        print(f"DataManager.load_kpis_data(): {success}")
        
        if success and dm.kpis_data is not None:
            print(f"✅ DataManager: {len(dm.kpis_data)} filas, {len(dm.kpis_data.columns)} columnas")
            return True
        else:
            print("❌ ERROR: DataManager no pudo cargar los datos")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en DataManager: {e}")
        traceback.print_exc()
        return False

def test_core_engine():
    """Test básico del core engine."""
    print("\n🔍 TEST 3: Verificando Core Engine")
    print("-" * 50)
    
    try:
        from src.core.integration_layer import run_complete_analysis_with_gui_integration
        
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
        
        results, summary = run_complete_analysis_with_gui_integration(
            "DatabankExport_M1.csv",
            config=config,
            analysis_type="unified"
        )
        
        print(f"✅ Core Engine: {len(results)} filas, {len(results.columns)} columnas")
        
        if results.empty:
            print("❌ ERROR: Core Engine devolvió DataFrame vacío")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en Core Engine: {e}")
        traceback.print_exc()
        return False

def test_gui_integration():
    """Test básico de la integración GUI."""
    print("\n🔍 TEST 4: Verificando integración GUI")
    print("-" * 50)
    
    try:
        from src.gui_enhanced_rank import read_and_prepare
        
        df = read_and_prepare("DatabankExport_M1.csv")
        print(f"✅ GUI read_and_prepare: {len(df)} filas, {len(df.columns)} columnas")
        
        if df.empty:
            print("❌ ERROR: GUI read_and_prepare devolvió DataFrame vacío")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en GUI integration: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE DIAGNÓSTICO SIMPLE")
    print("=" * 80)
    
    tests = [
        ("Archivo de entrada", test_archivo_entrada),
        ("DataManager", test_data_manager),
        ("Core Engine", test_core_engine),
        ("GUI Integration", test_gui_integration)
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
    
    print("\n📊 RESUMEN DE TESTS")
    print("-" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("✅ TODOS LOS TESTS PASARON - EL FLUJO FUNCIONA CORRECTAMENTE")
    else:
        print("❌ ALGUNOS TESTS FALLARON - REVISAR LOGS PARA DETALLES") 