#!/usr/bin/env python3
"""
TEST_KPIS_DISPONIBLES.py - Verificar KPIs disponibles en el asesor financiero
"""

import sys
import os
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

def test_kpis_disponibles():
    """Test para verificar qué KPIs están disponibles."""
    print("🔍 TEST: Verificando KPIs disponibles en el asesor financiero")
    print("=" * 60)
    
    try:
        # 1. Cargar datos con DataManager
        print("📊 Paso 1: Cargando datos con DataManager...")
        dm = DataManager()
        dm.load_all_data()
        
        if dm.kpis_data is None:
            print("❌ Error: No se pudieron cargar los datos de KPIs")
            return
        
        print(f"✅ Datos cargados: {len(dm.kpis_data)} estrategias")
        print(f"📋 Columnas originales: {dm.kpis_data.columns.tolist()}")
        
        # 2. Simular análisis principal
        print("\n🔧 Paso 2: Simulando análisis principal...")
        
        # Configuración de prueba
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
        resultados = run_complete_analysis_with_gui_integration(
            kpis_file='DatabankExport_M1.csv',
            market_file='DATOSMQL5.csv',
            strategies_folder='INPUTTEST/M1_NDX_UP_MQL4_136_STOP',
            output_folder='INPUTTEST/TOP',
            config=config
        )
        
        if 'filtered_df' not in resultados:
            print("❌ Error: No se obtuvieron resultados filtrados del análisis")
            return
        
        df_filtrado = resultados['filtered_df']
        print(f"✅ Análisis completado: {len(df_filtrado)} estrategias filtradas")
        print(f"📋 Columnas del DataFrame filtrado: {df_filtrado.columns.tolist()}")
        
        # 3. Verificar KPIs para el asesor financiero
        print("\n🤖 Paso 3: Verificando KPIs para el asesor financiero...")
        
        # Simular la lógica del asesor financiero
        estrategias_filtradas = df_filtrado.copy()
        
        # Seleccionar KPIs relevantes
        kpis_disponibles = [col for col in estrategias_filtradas.columns 
                          if col not in ['Strategy_Name', 'Quality_Category', 'Unified_Score', 'Explicación']]
        
        print(f"🔍 KPIs disponibles (excluyendo columnas especiales): {kpis_disponibles}")
        
        # Filtrar KPIs numéricos
        kpis_numericos = []
        for kpi in kpis_disponibles:
            if pd.api.types.is_numeric_dtype(estrategias_filtradas[kpi]):
                kpis_numericos.append(kpi)
        
        print(f"🔢 KPIs numéricos encontrados: {kpis_numericos}")
        print(f"📊 Total KPIs numéricos: {len(kpis_numericos)}")
        
        # 4. Probar el asesor financiero
        if len(kpis_numericos) >= 5:
            print("\n✅ KPIs suficientes encontrados, probando asesor financiero...")
            
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
    test_kpis_disponibles() 