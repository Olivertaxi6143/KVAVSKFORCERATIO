#!/usr/bin/env python3
"""
TEST_DEBUG_FINAL.py - Debug final del DataFrame del asesor financiero
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

from src.data_manager import DataManager

def test_carga_inputtest():
    dm = DataManager()
    print('--- TEST CARGA INPUTTEST ---')
    kpis_ok = dm.load_kpis_data('INPUTTEST/DatabankExport_M1.csv')
    print('KPIs:', kpis_ok, '| Registros:', len(dm.kpis_data) if dm.kpis_data is not None else 0)
    mercado_ok = dm.load_market_data('INPUTTEST/DATOSMQL5.csv')
    print('Mercado:', mercado_ok, '| Registros:', len(dm.market_data) if dm.market_data is not None else 0)
    # Estrategias (solo cuenta archivos .sqx)
    import os
    sqx_count = len([f for f in os.listdir('INPUTTEST/M1_NDX_UP_MQL4_136_STOP') if f.endswith('.sqx')])
    print('Archivos .sqx:', sqx_count)

if __name__ == '__main__':
    test_carga_inputtest()

def test_debug_final():
    """Test final para debuggear el DataFrame del asesor financiero."""
    print("🔍 TEST FINAL: Debuggeando DataFrame del asesor financiero")
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
        
        # Ejecutar análisis principal
        print("🔧 Ejecutando análisis principal...")
        resultados = run_complete_analysis_with_gui_integration(
            file_path='DatabankExport_M1.csv',
            config=config
        )
        
        if len(resultados) != 2:
            print("❌ Error: No se obtuvieron resultados correctos")
            return
        
        df_analisis = resultados[0]
        print(f"✅ Análisis completado: {len(df_analisis)} estrategias")
        print(f"📋 TODAS LAS COLUMNAS DEL ANÁLISIS:")
        for i, col in enumerate(df_analisis.columns, 1):
            print(f"  {i:2d}. '{col}' (tipo: {df_analisis[col].dtype})")
        
        # Simular filtrado por percentil
        print(f"\n🎯 Simulando filtrado por percentil 90%...")
        if 'Unified_Score' in df_analisis.columns:
            threshold = df_analisis['Unified_Score'].quantile(0.9)
            df_filtrado = df_analisis[df_analisis['Unified_Score'] >= threshold]
        else:
            print("⚠️ No se encontró columna Unified_Score, usando todas las estrategias")
            df_filtrado = df_analisis.copy()
        
        print(f"📊 Estrategias filtradas: {len(df_filtrado)}")
        print(f"📋 COLUMNAS DEL DATAFRAME FILTRADO:")
        for i, col in enumerate(df_filtrado.columns, 1):
            print(f"  {i:2d}. '{col}' (tipo: {df_filtrado[col].dtype})")
        
        # Analizar KPIs numéricos
        print(f"\n🔢 ANALIZANDO KPIs NUMÉRICOS:")
        kpis_numericos = [
            col for col in df_filtrado.columns
            if pd.api.types.is_numeric_dtype(df_filtrado[col])
        ]
        print(f"🔢 KPIs numéricos encontrados: {len(kpis_numericos)}")
        for i, kpi in enumerate(kpis_numericos, 1):
            print(f"  {i:2d}. '{kpi}'")
        
        # Excluir identificadores
        columnas_excluir = [
            'Strategy_Name', 'Quality_Category', 'Unified_Score', 'Explicación',
            'Filters_result', 'TimeFrame', 'Total_Data_Months', '#_of_trades'
        ]
        kpis_relevantes = [
            col for col in kpis_numericos
            if col not in columnas_excluir
        ]
        print(f"\n🎯 KPIs relevantes para asesor: {len(kpis_relevantes)}")
        for i, kpi in enumerate(kpis_relevantes, 1):
            print(f"  {i:2d}. '{kpi}'")
        
        # Probar normalización
        print(f"\n🔄 PROBANDO NORMALIZACIÓN:")
        from src.gui_enhanced_rank import normalizar_columnas_y_kpis
        
        df_normalizado, kpis_normalizados = normalizar_columnas_y_kpis(df_filtrado.copy())
        print(f"🔢 KPIs después de normalización: {len(kpis_normalizados)}")
        for i, kpi in enumerate(kpis_normalizados, 1):
            print(f"  {i:2d}. '{kpi}'")
        
        # Probar asesor financiero
        if len(kpis_normalizados) >= 5:
            print(f"\n✅ KPIs suficientes ({len(kpis_normalizados)}), probando asesor financiero...")
            
            try:
                asesor = AsesorFinancieroInteligente(df_normalizado, kpis_normalizados)
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
            print(f"❌ KPIs insuficientes: {len(kpis_normalizados)} (se requieren al menos 5)")
        
        print("\n" + "=" * 60)
        print("✅ Test final completado")
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug_final() 