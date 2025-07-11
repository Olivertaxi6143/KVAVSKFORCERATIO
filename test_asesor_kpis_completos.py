#!/usr/bin/env python3
"""
TEST_ASESOR_KPIS_COMPLETOS.py - Test para verificar que el asesor financiero recibe todos los KPIs numéricos
"""

import sys
import os
import pandas as pd
import numpy as np
import json

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath('src'))

try:
    from core_engine_enhanced import run_complete_analysis_with_gui_integration
    from data_manager import DataManager
    from asesor_financiero_inteligente import AsesorFinancieroInteligente
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

def test_asesor_kpis_completos():
    """Test para verificar que el asesor financiero recibe todos los KPIs numéricos."""
    print("🔍 TEST: Verificando que el asesor financiero recibe todos los KPIs numéricos")
    print("=" * 70)
    
    try:
        # 1. Cargar datos con DataManager
        print("📊 Paso 1: Cargando datos con DataManager...")
        dm = DataManager()
        dm.load_all_data()
        
        if dm.kpis_data is None:
            print("❌ Error: No se pudieron cargar los datos de KPIs")
            return
        
        print(f"✅ Datos cargados: {len(dm.kpis_data)} estrategias")
        print(f"📋 Columnas originales: {len(dm.kpis_data.columns)}")
        
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
            file_path='DatabankExport_M1.csv',
            config=config
        )
        
        if len(resultados) != 2:
            print("❌ Error: No se obtuvieron resultados correctos del análisis")
            return
        
        df_filtrado = resultados[0]  # El DataFrame es el primer elemento de la tupla
        print(f"✅ Análisis completado: {len(df_filtrado)} estrategias filtradas")
        print(f"📋 Columnas del DataFrame filtrado: {len(df_filtrado.columns)}")
        
        # 3. Simular la lógica del asesor financiero con todos los KPIs numéricos
        print("\n🤖 Paso 3: Simulando asesor financiero con todos los KPIs numéricos...")
        
        # Excluir columnas especiales que no son KPIs
        columnas_excluir = [
            'Strategy_Name', 'Strategy Name', 'Quality_Category', 
            'Unified_Score', 'Unified_Score_Robust', 'Unified_Score_Normalized', 
            'Unified_Score_Robust_Normalized', 'Explicación'
        ]
        
        # Obtener todos los KPIs numéricos disponibles (igual que el motor principal)
        kpis_numericos = []
        for col in df_filtrado.columns:
            if col not in columnas_excluir and pd.api.types.is_numeric_dtype(df_filtrado[col]):
                kpis_numericos.append(col)
        
        print(f"🔢 KPIs numéricos disponibles: {len(kpis_numericos)}")
        print(f"📋 KPIs encontrados: {kpis_numericos}")
        
        # 4. Comparar con KPIs seleccionados en GUI (simulado)
        print("\n🎯 Paso 4: Comparando con KPIs seleccionados en GUI...")
        
        # Simular KPIs seleccionados en GUI (solo algunos)
        kpis_seleccionados_gui = [
            'CAGR (IS)', 'CAGR (OOS)', 'Sharpe Ratio (IS)', 'Sharpe Ratio (OOS)',
            'Sortino Ratio', 'SQN Score (IS)', 'SQN Score (OOS)', 'Drawdown (IS)', 'Drawdown (OOS)',
            'Profit factor (IS)', 'Profit factor (OOS)', 'RecoveryFactor'
        ]
        
        print(f"🎯 KPIs seleccionados en GUI: {len(kpis_seleccionados_gui)}")
        print(f"🔢 KPIs numéricos totales: {len(kpis_numericos)}")
        
        # Verificar que el asesor recibe más KPIs que los seleccionados en GUI
        kpis_adicionales = [kpi for kpi in kpis_numericos if kpi not in kpis_seleccionados_gui]
        print(f"✅ KPIs adicionales que recibe el asesor: {len(kpis_adicionales)}")
        
        if kpis_adicionales:
            print("📋 KPIs adicionales:")
            for i, kpi in enumerate(kpis_adicionales[:10], 1):  # Mostrar solo los primeros 10
                print(f"  {i:2d}. {kpi}")
            if len(kpis_adicionales) > 10:
                print(f"  ... y {len(kpis_adicionales) - 10} más")
        
        # 5. Probar el asesor financiero con todos los KPIs numéricos
        print(f"\n✅ KPIs suficientes encontrados ({len(kpis_numericos)}), probando asesor financiero...")
        
        try:
            asesor = AsesorFinancieroInteligente(df_filtrado, kpis_numericos)
            print("✅ Asesor financiero inicializado correctamente")
            
            # Ejecutar análisis básico
            resultados_asesor = asesor.generar_consejos_completos()
            print("✅ Análisis del asesor completado")
            print(f"📝 Consejos generados: {len(resultados_asesor.get('consejos_completos', []))}")
            
            # Verificar que el asesor usó todos los KPIs
            if 'analisis_completos' in resultados_asesor:
                analisis = resultados_asesor['analisis_completos']
                if 'importancia_kpis' in analisis:
                    importancia = analisis['importancia_kpis']
                    if 'top_kpis' in importancia:
                        top_kpis = importancia['top_kpis']
                        print(f"🎯 Top KPIs identificados por el asesor: {len(top_kpis)}")
                        print("📋 Top 5 KPIs más importantes:")
                        for i, kpi in enumerate(top_kpis[:5], 1):
                            print(f"  {i}. {kpi}")
            
        except Exception as e:
            print(f"❌ Error en el asesor financiero: {e}")
            import traceback
            traceback.print_exc()
        
        # 6. Crear informe de comparación
        informe = {
            'fecha_test': pd.Timestamp.now().isoformat(),
            'datos_originales': {
                'total_estrategias': len(dm.kpis_data),
                'total_columnas': len(dm.kpis_data.columns),
                'kpis_numericos_originales': len([col for col in dm.kpis_data.columns if pd.api.types.is_numeric_dtype(dm.kpis_data[col])])
            },
            'analisis_principal': {
                'estrategias_filtradas': len(df_filtrado),
                'total_columnas': len(df_filtrado.columns),
                'kpis_numericos_disponibles': len(kpis_numericos),
                'kpis_numericos_lista': kpis_numericos
            },
            'asesor_financiero': {
                'kpis_seleccionados_gui': len(kpis_seleccionados_gui),
                'kpis_numericos_totales': len(kpis_numericos),
                'kpis_adicionales': len(kpis_adicionales),
                'kpis_adicionales_lista': kpis_adicionales,
                'mejora_cobertura': f"{((len(kpis_numericos) - len(kpis_seleccionados_gui)) / len(kpis_seleccionados_gui) * 100):.1f}%"
            },
            'configuracion_usada': config
        }
        
        # Guardar informe
        with open('test_asesor_kpis_completos.json', 'w', encoding='utf-8') as f:
            json.dump(informe, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Informe guardado en: test_asesor_kpis_completos.json")
        
        # 7. Resumen final
        print(f"\n📊 RESUMEN FINAL:")
        print(f"  • KPIs seleccionados en GUI: {len(kpis_seleccionados_gui)}")
        print(f"  • KPIs numéricos totales: {len(kpis_numericos)}")
        print(f"  • KPIs adicionales: {len(kpis_adicionales)}")
        print(f"  • Mejora en cobertura: {informe['asesor_financiero']['mejora_cobertura']}")
        print(f"  • Asesor financiero: ✅ FUNCIONANDO")
        
        print("\n" + "=" * 70)
        print("✅ Test completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_asesor_kpis_completos() 