#!/usr/bin/env python3
"""
TEST_ANALISIS_KPIS_CORE.py - Analizar KPIs usados en el core engine
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
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

def analizar_kpis_core():
    """Analizar qué KPIs usa el core engine en sus cálculos."""
    print("🔍 ANÁLISIS: KPIs usados en el core engine")
    print("=" * 60)
    
    try:
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
        
        # 1. Cargar datos originales
        print("📊 Paso 1: Cargando datos originales...")
        dm = DataManager()
        dm.load_all_data()
        
        if dm.kpis_data is None:
            print("❌ Error: No se pudieron cargar los datos de KPIs")
            return
        
        df_original = dm.kpis_data
        print(f"✅ Datos originales: {len(df_original)} estrategias, {len(df_original.columns)} columnas")
        
        # 2. Analizar KPIs originales
        print("\n📋 Paso 2: Analizando KPIs originales...")
        kpis_originales = [
            col for col in df_original.columns
            if pd.api.types.is_numeric_dtype(df_original[col])
        ]
        print(f"🔢 KPIs numéricos originales: {len(kpis_originales)}")
        
        # Categorizar KPIs
        kpis_categorizados = {
            'Rendimiento': [],
            'Riesgo': [],
            'Consistencia': [],
            'Otros': []
        }
        
        for kpi in kpis_originales:
            kpi_lower = kpi.lower()
            if any(term in kpi_lower for term in ['cagr', 'profit', 'return', 'net']):
                kpis_categorizados['Rendimiento'].append(kpi)
            elif any(term in kpi_lower for term in ['drawdown', 'risk', 'var', 'cvar', 'ulcer']):
                kpis_categorizados['Riesgo'].append(kpi)
            elif any(term in kpi_lower for term in ['sharpe', 'sortino', 'sqn', 'calmar', 'consistency']):
                kpis_categorizados['Consistencia'].append(kpi)
            else:
                kpis_categorizados['Otros'].append(kpi)
        
        # Mostrar KPIs categorizados
        for categoria, kpis in kpis_categorizados.items():
            print(f"\n📊 {categoria}: {len(kpis)} KPIs")
            for kpi in kpis:
                print(f"  • {kpi}")
        
        # 3. Ejecutar análisis principal
        print("\n🔧 Paso 3: Ejecutando análisis principal...")
        resultados = run_complete_analysis_with_gui_integration(
            file_path='DatabankExport_M1.csv',
            config=config
        )
        
        if len(resultados) != 2:
            print("❌ Error: No se obtuvieron resultados correctos")
            return
        
        df_analisis = resultados[0]
        print(f"✅ Análisis completado: {len(df_analisis)} estrategias, {len(df_analisis.columns)} columnas")
        
        # 4. Analizar KPIs en resultado del análisis
        print("\n📋 Paso 4: Analizando KPIs en resultado del análisis...")
        kpis_analisis = [
            col for col in df_analisis.columns
            if pd.api.types.is_numeric_dtype(df_analisis[col])
        ]
        print(f"🔢 KPIs numéricos en análisis: {len(kpis_analisis)}")
        
        # KPIs perdidos
        kpis_perdidos = [kpi for kpi in kpis_originales if kpi not in kpis_analisis]
        kpis_nuevos = [kpi for kpi in kpis_analisis if kpi not in kpis_originales]
        
        print(f"\n📊 Resumen de cambios:")
        print(f"  • KPIs originales: {len(kpis_originales)}")
        print(f"  • KPIs en análisis: {len(kpis_analisis)}")
        print(f"  • KPIs perdidos: {len(kpis_perdidos)}")
        print(f"  • KPIs nuevos: {len(kpis_nuevos)}")
        
        if kpis_perdidos:
            print(f"\n❌ KPIs perdidos en el análisis:")
            for kpi in kpis_perdidos:
                print(f"  • {kpi}")
        
        if kpis_nuevos:
            print(f"\n✅ KPIs nuevos en el análisis:")
            for kpi in kpis_nuevos:
                print(f"  • {kpi}")
        
        # 5. Crear informe detallado
        informe = {
            'fecha_analisis': pd.Timestamp.now().isoformat(),
            'datos_originales': {
                'total_estrategias': len(df_original),
                'total_columnas': len(df_original.columns),
                'kpis_numericos': len(kpis_originales),
                'kpis_categorizados': kpis_categorizados
            },
            'analisis_principal': {
                'total_estrategias': len(df_analisis),
                'total_columnas': len(df_analisis.columns),
                'kpis_numericos': len(kpis_analisis),
                'kpis_perdidos': kpis_perdidos,
                'kpis_nuevos': kpis_nuevos
            },
            'configuracion_usada': config
        }
        
        # Guardar informe
        with open('informe_kpis_core_engine.json', 'w', encoding='utf-8') as f:
            json.dump(informe, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Informe guardado en: informe_kpis_core_engine.json")
        
        # 6. Resumen ejecutivo
        print(f"\n📊 RESUMEN EJECUTIVO:")
        print(f"  • El core engine procesa {len(kpis_originales)} KPIs originales")
        print(f"  • Genera {len(kpis_analisis)} KPIs en el resultado")
        print(f"  • {'✅' if len(kpis_perdidos) == 0 else '❌'} KPIs perdidos: {len(kpis_perdidos)}")
        print(f"  • {'✅' if len(kpis_nuevos) > 0 else '❌'} KPIs nuevos: {len(kpis_nuevos)}")
        
        print("\n" + "=" * 60)
        print("✅ Análisis completado")
        
    except Exception as e:
        print(f"❌ Error en el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analizar_kpis_core() 