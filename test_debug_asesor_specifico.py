#!/usr/bin/env python3
"""
TEST_DEBUG_ASESOR_ESPECIFICO.py - Debug específico del asesor financiero
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

def test_debug_asesor_especifico():
    """Test específico para debuggear el asesor financiero."""
    print("🔍 DEBUG ESPECÍFICO DEL ASESOR FINANCIERO")
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
        
        # 1. Ejecutar análisis principal (NO TOCAR)
        print("🔧 Paso 1: Ejecutando análisis principal...")
        resultados = run_complete_analysis_with_gui_integration(
            file_path='DatabankExport_M1.csv',
            config=config
        )
        
        if len(resultados) != 2:
            print("❌ Error: No se obtuvieron resultados correctos")
            return
        
        df_analisis = resultados[0]
        print(f"✅ Análisis principal completado: {len(df_analisis)} estrategias")
        
        # 2. Simular filtrado por percentil (como hace la GUI)
        print("\n🎯 Paso 2: Simulando filtrado por percentil 90%...")
        if 'Unified_Score' in df_analisis.columns:
            threshold = df_analisis['Unified_Score'].quantile(0.9)
            df_filtrado = df_analisis[df_analisis['Unified_Score'] >= threshold]
        else:
            print("⚠️ No se encontró columna Unified_Score, usando todas las estrategias")
            df_filtrado = df_analisis.copy()
        
        print(f"📊 Estrategias filtradas: {len(df_filtrado)}")
        
        # 3. DEBUG: Verificar columnas del DataFrame filtrado
        print(f"\n📋 Paso 3: Analizando columnas del DataFrame filtrado...")
        print(f"📋 TODAS LAS COLUMNAS:")
        for i, col in enumerate(df_filtrado.columns, 1):
            print(f"  {i:2d}. '{col}' (tipo: {df_filtrado[col].dtype})")
        
        # 4. DEBUG: KPIs numéricos en DataFrame filtrado
        print(f"\n🔢 Paso 4: Analizando KPIs numéricos...")
        kpis_numericos = [
            col for col in df_filtrado.columns
            if pd.api.types.is_numeric_dtype(df_filtrado[col])
        ]
        print(f"🔢 KPIs numéricos encontrados: {len(kpis_numericos)}")
        for i, kpi in enumerate(kpis_numericos, 1):
            print(f"  {i:2d}. '{kpi}'")
        
        # 5. DEBUG: Excluir identificadores (lógica actual del asesor)
        print(f"\n🎯 Paso 5: Aplicando filtro de identificadores...")
        columnas_excluir = [
            'Strategy_Name', 'Quality_Category', 'Unified_Score', 'Explicación',
            'Filters_result', 'TimeFrame', 'Total_Data_Months', '#_of_trades'
        ]
        kpis_relevantes = [
            col for col in kpis_numericos
            if col not in columnas_excluir
        ]
        print(f"🎯 KPIs relevantes después de excluir identificadores: {len(kpis_relevantes)}")
        for i, kpi in enumerate(kpis_relevantes, 1):
            print(f"  {i:2d}. '{kpi}'")
        
        # 6. DEBUG: Probar normalización actual
        print(f"\n🔄 Paso 6: Probando normalización actual...")
        from src.gui_enhanced_rank import normalizar_columnas_y_kpis
        
        df_normalizado, kpis_normalizados = normalizar_columnas_y_kpis(df_filtrado.copy())
        print(f"🔢 KPIs después de normalización: {len(kpis_normalizados)}")
        for i, kpi in enumerate(kpis_normalizados, 1):
            print(f"  {i:2d}. '{kpi}'")
        
        # 7. DEBUG: Comparar con lógica actual del asesor
        print(f"\n🔍 Paso 7: Comparando con lógica actual del asesor...")
        
        # Simular exactamente lo que hace el asesor actualmente
        estrategias_filtradas = df_filtrado.copy()
        
        # Lógica actual del asesor (líneas 2180-2185 en gui_enhanced_rank.py)
        kpis_disponibles = [col for col in estrategias_filtradas.columns 
                          if col not in ['Strategy_Name', 'Quality_Category', 'Unified_Score', 'Explicación']]
        
        kpis_numericos_asesor = []
        for kpi in kpis_disponibles:
            if pd.api.types.is_numeric_dtype(estrategias_filtradas[kpi]):
                kpis_numericos_asesor.append(kpi)
        
        print(f"🔢 KPIs que encuentra el asesor actualmente: {len(kpis_numericos_asesor)}")
        for i, kpi in enumerate(kpis_numericos_asesor, 1):
            print(f"  {i:2d}. '{kpi}'")
        
        # 8. DEBUG: Identificar el problema
        print(f"\n❌ Paso 8: Identificando el problema...")
        
        if len(kpis_numericos_asesor) <= 1:
            print(f"❌ PROBLEMA DETECTADO: Solo {len(kpis_numericos_asesor)} KPIs encontrados")
            print(f"🔍 Posibles causas:")
            
            # Verificar si las columnas tienen nombres diferentes
            columnas_asesor = estrategias_filtradas.columns.tolist()
            print(f"  • Columnas en DataFrame: {columnas_asesor}")
            
            # Verificar si hay columnas con espacios vs guiones bajos
            columnas_con_espacios = [col for col in columnas_asesor if ' ' in col]
            columnas_con_guiones = [col for col in columnas_asesor if '_' in col]
            
            print(f"  • Columnas con espacios: {len(columnas_con_espacios)}")
            print(f"  • Columnas con guiones bajos: {len(columnas_con_guiones)}")
            
            if columnas_con_espacios:
                print(f"  • Ejemplos con espacios: {columnas_con_espacios[:5]}")
            if columnas_con_guiones:
                print(f"  • Ejemplos con guiones: {columnas_con_guiones[:5]}")
        
        # 9. DEBUG: Probar solución
        print(f"\n🔧 Paso 9: Probando solución...")
        
        # Usar la función de normalización que corregimos
        df_solucion, kpis_solucion = normalizar_columnas_y_kpis(df_filtrado.copy())
        
        print(f"✅ KPIs después de la solución: {len(kpis_solucion)}")
        if len(kpis_solucion) >= 5:
            print(f"✅ SOLUCIÓN FUNCIONA: {len(kpis_solucion)} KPIs disponibles")
            
            # Probar asesor financiero con la solución
            try:
                asesor = AsesorFinancieroInteligente(df_solucion, kpis_solucion)
                print("✅ Asesor financiero inicializado correctamente")
                
                resultados_asesor = asesor.generar_consejos_completos()
                print(f"✅ Análisis completado: {len(resultados_asesor.get('consejos_completos', []))} consejos")
                
            except Exception as e:
                print(f"❌ Error en asesor financiero: {e}")
        else:
            print(f"❌ SOLUCIÓN NO FUNCIONA: Solo {len(kpis_solucion)} KPIs")
        
        print("\n" + "=" * 60)
        print("✅ Debug específico completado")
        
    except Exception as e:
        print(f"❌ Error en debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug_asesor_especifico() 