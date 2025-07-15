#!/usr/bin/env python3
"""
Test muy simple para identificar exactamente dónde se pierden los datos.
"""

import sys
import os
import pandas as pd

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def main():
    print("🔍 DIAGNÓSTICO ESPECÍFICO DEL PROBLEMA")
    print("=" * 60)
    
    # PASO 1: Verificar archivo
    print("\n1️⃣ Verificando archivo de entrada...")
    kpi_file = "DatabankExport_M1.csv"
    
    if not os.path.exists(kpi_file):
        print(f"❌ Archivo {kpi_file} no encontrado")
        return
    
    # Leer archivo directamente
    try:
        df_directo = pd.read_csv(kpi_file, sep=';', decimal=',')
        print(f"✅ Archivo leído: {len(df_directo)} filas, {len(df_directo.columns)} columnas")
        print(f"📋 Primeras columnas: {list(df_directo.columns)[:5]}")
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return
    
    # PASO 2: Test DataManager
    print("\n2️⃣ Probando DataManager...")
    try:
        from src.data.data_manager import DataManager
        
        dm = DataManager()
        success = dm.load_kpis_data(kpi_file)
        
        print(f"DataManager.load_kpis_data(): {success}")
        
        if success and dm.kpis_data is not None:
            print(f"✅ DataManager: {len(dm.kpis_data)} filas, {len(dm.kpis_data.columns)} columnas")
        else:
            print("❌ DataManager falló")
            return
    except Exception as e:
        print(f"❌ Error en DataManager: {e}")
        return
    
    # PASO 3: Test Core Engine
    print("\n3️⃣ Probando Core Engine...")
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
        
        print("Llamando a run_complete_analysis_with_gui_integration...")
        results, summary = run_complete_analysis_with_gui_integration(
            df_directo,
            config=config,
            progress_callback=None
        )
        
        print(f"✅ Core Engine: {len(results)} filas, {len(results.columns)} columnas")
        
        if results.empty:
            print("❌ PROBLEMA ENCONTRADO: Core Engine devolvió DataFrame vacío")
            print("📋 Columnas del resultado:", list(results.columns))
        else:
            print("✅ Core Engine funcionó correctamente")
            
    except Exception as e:
        print(f"❌ Error en Core Engine: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎯 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    main() 