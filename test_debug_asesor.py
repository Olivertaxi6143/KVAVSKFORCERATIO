#!/usr/bin/env python3
"""
TEST_DEBUG_ASESOR.py - Debuggear columnas que llegan al asesor financiero
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath('src'))

try:
    from src.core.integration_layer import run_complete_analysis_with_gui_integration
    from src.data.data_manager import DataManager
    from src.analysis.asesor_financiero_inteligente import AsesorFinancieroInteligente
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

def test_debug_asesor():
    """Test para debuggear qué columnas llegan al asesor financiero."""
    print("🔍 TEST: Debuggeando columnas del asesor financiero")
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
        
        df_filtrado = resultados[0]  # El DataFrame es el primer elemento
        print(f"✅ Análisis completado: {len(df_filtrado)} estrategias filtradas")
        
        # Debug: mostrar todas las columnas
        print(f"\n📋 TODAS LAS COLUMNAS DEL DATAFRAME FILTRADO:")
        for i, col in enumerate(df_filtrado.columns, 1):
            print(f"  {i:2d}. '{col}' (tipo: {df_filtrado[col].dtype})")
        
        # Simular la lógica exacta del asesor financiero
        print(f"\n🔍 SIMULANDO LÓGICA DEL ASESOR FINANCIERO:")
        
        estrategias_filtradas = df_filtrado.copy()
        
        # Seleccionar KPIs relevantes (excluyendo columnas especiales)
        kpis_disponibles = [col for col in estrategias_filtradas.columns 
                          if col not in ['Strategy_Name', 'Quality_Category', 'Unified_Score', 'Explicación']]
        
        print(f"🔍 KPIs disponibles (excluyendo columnas especiales): {len(kpis_disponibles)}")
        for i, kpi in enumerate(kpis_disponibles, 1):
            print(f"  {i:2d}. '{kpi}'")
        
        # Filtrar KPIs numéricos
        kpis_numericos = []
        for kpi in kpis_disponibles:
            if pd.api.types.is_numeric_dtype(estrategias_filtradas[kpi]):
                kpis_numericos.append(kpi)
        
        print(f"\n🔢 KPIs numéricos encontrados: {len(kpis_numericos)}")
        for i, kpi in enumerate(kpis_numericos, 1):
            print(f"  {i:2d}. '{kpi}'")
        
        # Verificar si hay suficientes KPIs
        if len(kpis_numericos) < 5:
            print(f"\n⚠️ Solo {len(kpis_numericos)} KPIs disponibles, usando todos los numéricos")
            # Usar todos los KPIs numéricos disponibles
            kpis_numericos = [col for col in estrategias_filtradas.columns 
                            if pd.api.types.is_numeric_dtype(estrategias_filtradas[col]) 
                            and col not in ['Strategy_Name', 'Quality_Category', 'Unified_Score', 'Explicación']]
            print(f"✅ KPIs numéricos finales: {len(kpis_numericos)}")
        
        # Probar el asesor financiero
        if len(kpis_numericos) >= 5:
            print(f"\n✅ KPIs suficientes encontrados ({len(kpis_numericos)}), probando asesor financiero...")
            
            try:
                asesor = AsesorFinancieroInteligente(estrategias_filtradas, kpis_numericos)
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
            print(f"❌ KPIs insuficientes: {len(kpis_numericos)} (se requieren al menos 5)")
        
        print("\n" + "=" * 60)
        print("✅ Test completado")
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug_asesor() 