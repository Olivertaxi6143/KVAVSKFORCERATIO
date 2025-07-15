#!/usr/bin/env python3
"""
TEST_KPIS_INICIALES.py - Test para verificar que los KPIs se cargan correctamente al iniciar la GUI
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath('src'))

def test_kpis_iniciales():
    """Test para verificar que los KPIs se cargan correctamente al iniciar la GUI."""
    print("🔍 TEST: Verificación de KPIs iniciales")
    print("=" * 50)
    
    try:
        # Importar la GUI
        from gui_enhanced_rank import EnhancedRankGUI
        print("✅ Módulo GUI importado correctamente")
        
        # Crear instancia de la GUI
        print("🚀 Creando instancia de la GUI...")
        app = EnhancedRankGUI()
        print("✅ GUI creada exitosamente")
        
        # Verificar el estilo inicial
        estilo_inicial = app.var_style.get()
        print(f"📊 Estilo inicial: {estilo_inicial}")
        
        # Verificar KPIs activos
        kpis_activos = [key for key, var in app.metric_vars.items() if var.get()]
        print(f"📋 KPIs activos al iniciar: {len(kpis_activos)}")
        
        # Mostrar los KPIs activos
        if kpis_activos:
            print("✅ KPIs activos:")
            for i, kpi in enumerate(kpis_activos, 1):
                print(f"  {i}. {kpi}")
        else:
            print("❌ No hay KPIs activos al iniciar")
            assert False
        
        # Verificar que el número de KPIs es correcto según el estilo
        kpis_esperados_por_estilo = {
            'Intradía': 8,
            'Swing': 8,
            'Tendencial': 8,
            'Reversión a la media': 8,
            'Breakout': 8
        }
        
        kpis_esperados = kpis_esperados_por_estilo.get(estilo_inicial, 8)
        
        if len(kpis_activos) == kpis_esperados:
            print(f"✅ Número correcto de KPIs activos: {len(kpis_activos)}/{kpis_esperados}")
        else:
            print(f"❌ Número incorrecto de KPIs activos: {len(kpis_activos)}/{kpis_esperados}")
            assert False
        
        # Verificar que los KPIs son los correctos para el estilo
        kpis_correctos_por_estilo = {
            'Intradía': [
                'Winning Percent', 'Avg. Bars in Trade', 'Exposure', 'SQN', 'Sortino Ratio',
                'Max Consec. Losses', 'Drawdown', 'RecoveryFactor'
            ],
            'Swing': [
                'Profit factor', 'Max Drawdown Duration', 'RecoveryFactor', 'Exposure', 'VaR (95%)',
                'CVaR (95%)', 'Ulcer Index %', 'CalmarRatio'
            ],
            'Tendencial': [
                'Profit factor', 'Max Drawdown Duration', 'RecoveryFactor', 'CAGR', 'Sharpe Ratio',
                'Profit factor', 'Sortino Ratio', 'Stagnation'
            ],
            'Reversión a la media': [
                'Expectancy', 'Avg. Bars in Trade', 'Winning Percent', 'Sortino Ratio', 'Max Drawdown Duration',
                'Drawdown', 'Payout ratio', 'Ulcer Index %'
            ],
            'Breakout': [
                'Sortino Ratio', 'RecoveryFactor', 'Exposure', 'Stagnation',
                'Stagnation', 'Drawdown', 'RINAIndex', 'VaR (95%)'
            ],
        }
        
        kpis_correctos = kpis_correctos_por_estilo.get(estilo_inicial, [])
        kpis_faltantes = [kpi for kpi in kpis_correctos if kpi not in kpis_activos]
        kpis_extra = [kpi for kpi in kpis_activos if kpi not in kpis_correctos]
        
        if not kpis_faltantes and not kpis_extra:
            print("✅ KPIs correctos para el estilo inicial")
        else:
            print("❌ KPIs incorrectos para el estilo inicial:")
            if kpis_faltantes:
                print(f"  Faltantes: {kpis_faltantes}")
            if kpis_extra:
                print(f"  Extra: {kpis_extra}")
            assert False
        
        # Verificar que la información de KPIs se actualiza correctamente
        if hasattr(app, 'kpi_info_label'):
            texto_label = app.kpi_info_label.cget("text")
            print(f"📊 Label de KPIs: {texto_label}")
            
            # Verificar que el color es verde (KPIs activos)
            color_label = app.kpi_info_label.cget("foreground")
            if color_label == "green":
                print("✅ Color del label correcto (verde)")
            else:
                print(f"⚠️ Color del label: {color_label}")
        
        print("\n" + "=" * 50)
        print("✅ TEST COMPLETADO: Los KPIs se cargan correctamente al iniciar")
        
        # Cerrar la GUI después del test
        app.destroy()
        
        assert True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        assert False

if __name__ == "__main__":
    test_kpis_iniciales() 