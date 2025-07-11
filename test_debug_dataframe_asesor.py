#!/usr/bin/env python3
"""
TEST_DEBUG_DATAFRAME_ASESOR.py - Debuggear DataFrame del asesor financiero
"""

import sys
import os
import pandas as pd
import numpy as np

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath('src'))

try:
    from core_engine_enhanced import run_complete_analysis_with_gui_integration
    from data_manager import DataManager
    from asesor_financiero_inteligente import AsesorFinancieroInteligente
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

def test_debug_dataframe_asesor():
    """Test para debuggear el DataFrame del asesor financiero."""
    print("🔍 TEST: Debuggeando DataFrame del asesor financiero")
    print("=" * 60)
    
    try:
        # Configuración simple
        config = {
            'trading_style': 'balanced',
            'alpha': 0.7,
            'percentil': 90,
            'kpis_seleccionados': [
                'CAGR (IS)', 'CAGR (OOS)', 'Sharpe Ratio (IS)', 'Sharpe Ratio (OOS)',
                'Sortino Ratio', 'SQN Score (IS)', 'SQN Score (OOS)', 'Drawdown (IS)', 'Drawdown (OOS)',
                'Profit factor (IS)', 'Profit factor (OOS)', 'RecoveryFactor'
            ]
        }
        
        # 1. Cargar datos originales
        print("📊 Paso 1: Cargando datos originales...")
        dm = DataManager()
        dm.load_all_data()
        
        if dm.kpis_data is None:
            print("❌ Error: No se pudieron cargar los datos de KPIs")
            return
        
        print(f"✅ Datos originales cargados: {len(dm.kpis_data)} estrategias")
        print(f"📋 Columnas originales: {dm.kpis_data.columns.tolist()}")
        
        # 2. Ejecutar análisis principal
        print("\n🔧 Paso 2: Ejecutando análisis principal...")
        resultados = run_complete_analysis_with_gui_integration(
            file_path='DatabankExport_M1.csv',
            config=config
        )
        
        if len(resultados) != 2:
            print("❌ Error: No se obtuvieron resultados correctos")
            return
        
        df_analisis_principal = resultados[0]
        print(f"✅ Análisis principal completado: {len(df_analisis_principal)} estrategias")
        print(f"📋 Columnas del análisis principal: {df_analisis_principal.columns.tolist()}")
        
        # 3. Simular filtrado por percentil
        print("\n🎯 Paso 3: Simulando filtrado por percentil...")
        percentil = 90
        if 'Unified_Score' in df_analisis_principal.columns:
            threshold = df_analisis_principal['Unified_Score'].quantile(percentil / 100)
            df_filtrado = df_analisis_principal[df_analisis_principal['Unified_Score'] >= threshold]
        else:
            print("⚠️ No se encontró columna Unified_Score, usando todas las estrategias")
            df_filtrado = df_analisis_principal.copy()
        
        print(f"📊 Estrategias filtradas: {len(df_filtrado)}")
        print(f"📋 Columnas del DataFrame filtrado: {df_filtrado.columns.tolist()}")
        
        # 4. Debuggear KPIs numéricos
        print("\n🔢 Paso 4: Analizando KPIs numéricos...")
        
        # KPIs numéricos en DataFrame filtrado
        kpis_numericos_filtrado = [
            col for col in df_filtrado.columns
            if pd.api.types.is_numeric_dtype(df_filtrado[col])
        ]
        print(f"🔢 KPIs numéricos en DataFrame filtrado: {len(kpis_numericos_filtrado)}")
        for i, kpi in enumerate(kpis_numericos_filtrado, 1):
            print(f"  {i:2d}. '{kpi}'")
        
        # KPIs numéricos excluyendo identificadores
        columnas_excluir = [
            'Strategy_Name', 'Quality_Category', 'Unified_Score', 'Explicación',
            'Filters_result', 'TimeFrame', 'Total_Data_Months', '#_of_trades'
        ]
        kpis_relevantes = [
            col for col in kpis_numericos_filtrado
            if col not in columnas_excluir
        ]
        print(f"\n🎯 KPIs relevantes para asesor: {len(kpis_relevantes)}")
        for i, kpi in enumerate(kpis_relevantes, 1):
            print(f"  {i:2d}. '{kpi}'")
        
        # 5. Comparar con datos originales
        print("\n📊 Paso 5: Comparando con datos originales...")
        kpis_originales = [
            col for col in dm.kpis_data.columns
            if pd.api.types.is_numeric_dtype(dm.kpis_data[col])
        ]
        print(f"🔢 KPIs numéricos en datos originales: {len(kpis_originales)}")
        
        # KPIs perdidos
        kpis_perdidos = [kpi for kpi in kpis_originales if kpi not in kpis_numericos_filtrado]
        if kpis_perdidos:
            print(f"❌ KPIs perdidos en el proceso: {len(kpis_perdidos)}")
            for kpi in kpis_perdidos:
                print(f"  • '{kpi}'")
        else:
            print("✅ No se perdieron KPIs en el proceso")
        
        # 6. Probar asesor financiero
        if len(kpis_relevantes) >= 5:
            print(f"\n✅ KPIs suficientes ({len(kpis_relevantes)}), probando asesor financiero...")
            
            try:
                asesor = AsesorFinancieroInteligente(df_filtrado, kpis_relevantes)
                print("✅ Asesor financiero inicializado correctamente")
                
                # Ejecutar análisis básico
                resultados_asesor = asesor.generar_consejos_completos()
                print("✅ Análisis del asesor completado")
                print(f"📝 Consejos generados: {len(resultados_asesor.get('consejos_completos', []))}")
                
            except Exception as e:
                print(f"❌ Error en el asesor financiero: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ KPIs insuficientes: {len(kpis_relevantes)} (se requieren al menos 5)")
        
        print("\n" + "=" * 60)
        print("✅ Test completado")
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug_dataframe_asesor() 