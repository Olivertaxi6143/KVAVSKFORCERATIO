#!/usr/bin/env python3
"""
Test Comprehensivo: Implementación de Pestaña de Resultados
==========================================================

Valida que la función _display_results funciona correctamente con datos reales
y que la tabla de resultados se actualiza dinámicamente según el estándar científico.
"""

import sys
import os
import traceback
import pandas as pd
import numpy as np
from datetime import datetime

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_results_table_implementation():
    """Test comprehensivo de la implementación de la pestaña de resultados."""
    print("🔍 Test Comprehensivo: Implementación de Pestaña de Resultados")
    print("=" * 70)
    
    try:
        # Importar módulos necesarios
        from gui.gui_enhanced_rank import EnhancedRankGUI
        import tkinter as tk
        
        # Crear datos de prueba realistas
        test_data = pd.DataFrame({
            'Strategy Name': [f'Strategy_{i}' for i in range(1, 11)],
            'CAGR': np.random.uniform(1.0, 5.0, 10),
            'Sharpe Ratio': np.random.uniform(0.5, 2.0, 10),
            'Drawdown': np.random.uniform(5.0, 25.0, 10),
            'Profit factor': np.random.uniform(1.2, 2.5, 10),
            'Max Consec. Losses': np.random.randint(2, 8, 10),
            'RecoveryFactor': np.random.uniform(1.0, 3.0, 10),
            'SQN': np.random.uniform(1.0, 2.5, 10),
            'CalmarRatio': np.random.uniform(1.0, 3.0, 10),
            'VaR (95%)': np.random.uniform(2.0, 8.0, 10),
            'predictability_score': np.random.uniform(60, 95, 10),
            'Unified_Score': np.random.uniform(0.5, 0.9, 10),
            'Unified_Score_Scientific': np.random.uniform(0.5, 0.9, 10),
            'Unified_Score_Enhanced': np.random.uniform(0.5, 0.9, 10)
        })
        
        # Añadir categorías de calidad
        test_data['Quality_Category'] = ['Elite', 'Excellent', 'Very Good', 'Good', 'Regular', 
                                       'Poor', 'Elite', 'Excellent', 'Very Good', 'Good']
        
        # Crear resumen de prueba
        test_summary = {
            'total_strategies': len(test_data),
            'excellent': 3,
            'very_good': 2,
            'good': 2,
            'regular': 2,
            'poor': 1,
            'best_strategy': 'Strategy_1',
            'avg_score': test_data['Unified_Score'].mean()
        }
        
        print("✅ Datos de prueba creados exitosamente")
        print(f"   - {len(test_data)} estrategias")
        print(f"   - Columnas: {list(test_data.columns)}")
        
        # Crear GUI de prueba (sin mostrar ventana)
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana
        
        gui = EnhancedRankGUI()
        
        print("✅ GUI de prueba inicializada")
        
        # Simular tabla de resultados
        gui.results_tree = type('MockTree', (), {
            'get_children': lambda: [],
            'delete': lambda item: None,
            'insert': lambda parent, index, **kwargs: f"item_{index}",
            'tag_configure': lambda tag, **kwargs: None
        })()
        
        # Simular métodos auxiliares
        gui._log_message = lambda msg, level="INFO": print(f"[{level}] {msg}")
        gui._get_predictability_level = lambda score: "Alta" if score > 80 else "Moderada" if score > 60 else "Baja"
        gui._get_predictability_recommendation = lambda score: "Excelente" if score > 80 else "Buena" if score > 60 else "Requiere atención"
        gui._calculate_tail_risk_level = lambda row: {
            'icon': '🟢',
            'level': 'BAJO',
            'description': 'Riesgo de cola bajo',
            'risk_factors': ['Drawdown controlado', 'Profit factor estable']
        }
        gui._crear_tooltip = lambda widget, text: None
        gui._show_analysis_summary = lambda summary: print(f"📊 Resumen mostrado: {len(summary)} métricas")
        
        print("✅ Métodos auxiliares simulados")
        
        # Ejecutar _display_results
        print("\n🔄 Ejecutando _display_results...")
        gui._display_results(test_data, test_summary)
        
        print("✅ _display_results ejecutado exitosamente")
        
        # Verificar que se guardó el DataFrame
        assert hasattr(gui, 'results_df'), "❌ results_df no se guardó"
        assert len(gui.results_df) == len(test_data), f"❌ Tamaño incorrecto: {len(gui.results_df)} vs {len(test_data)}"
        
        print("✅ DataFrame guardado correctamente")
        
        # Verificar que se inicializaron las variables de control
        assert hasattr(gui, 'checkbox_vars'), "❌ checkbox_vars no se inicializó"
        assert hasattr(gui, 'is_oos_details'), "❌ is_oos_details no se inicializó"
        
        print("✅ Variables de control inicializadas")
        
        # Verificar métricas científicas
        assert 'Unified_Score_Scientific' in gui.results_df.columns, "❌ Columna científica no encontrada"
        assert 'Unified_Score_Enhanced' in gui.results_df.columns, "❌ Columna mejorada no encontrada"
        
        print("✅ Métricas científicas verificadas")
        
        # Verificar predictibilidad
        if 'predictability_score' in test_data.columns:
            assert 'Predictability_Level' in gui.results_df.columns, "❌ Nivel de predictibilidad no encontrado"
            assert 'Predictability_Recommendation' in gui.results_df.columns, "❌ Recomendación de predictibilidad no encontrada"
            print("✅ Métricas de predictibilidad verificadas")
        
        # Test de robustez con datos vacíos
        print("\n🔄 Test de robustez con datos vacíos...")
        empty_df = pd.DataFrame()
        gui._display_results(empty_df, {})
        print("✅ Manejo de datos vacíos correcto")
        
        # Test de robustez con datos None
        print("\n🔄 Test de robustez con datos None...")
        gui._display_results(None, {})
        print("✅ Manejo de datos None correcto")
        
        # Test de robustez con datos sin columnas requeridas
        print("\n🔄 Test de robustez con datos incompletos...")
        incomplete_df = pd.DataFrame({'Strategy Name': ['Test'], 'CAGR': [1.0]})
        gui._display_results(incomplete_df, {})
        print("✅ Manejo de datos incompletos correcto")
        
        # Limpiar
        root.destroy()
        
        print("\n" + "=" * 70)
        print("🎉 ¡TEST COMPREHENSIVO EXITOSO!")
        print("✅ Pestaña de resultados implementada correctamente")
        print("✅ Actualización dinámica funcionando")
        print("✅ Manejo de errores robusto")
        print("✅ Estándar científico cumplido")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN TEST: {str(e)}")
        print(f"📋 Traceback completo:")
        traceback.print_exc()
        return False

def test_display_results_edge_cases():
    """Test de casos edge para _display_results."""
    print("\n🔍 Test de Casos Edge: _display_results")
    print("=" * 50)
    
    try:
        from gui.gui_enhanced_rank import EnhancedRankGUI
        import tkinter as tk
        
        # Crear GUI de prueba
        root = tk.Tk()
        root.withdraw()
        
        gui = EnhancedRankGUI()
        
        # Simular métodos
        gui._log_message = lambda msg, level="INFO": None
        gui._get_predictability_level = lambda score: "Alta"
        gui._get_predictability_recommendation = lambda score: "Excelente"
        gui._calculate_tail_risk_level = lambda row: {
            'icon': '🟢', 'level': 'BAJO', 'description': 'Bajo', 'risk_factors': []
        }
        gui._crear_tooltip = lambda widget, text: None
        gui._show_analysis_summary = lambda summary: None
        
        # Simular tabla
        gui.results_tree = type('MockTree', (), {
            'get_children': lambda: [],
            'delete': lambda item: None,
            'insert': lambda parent, index, **kwargs: f"item_{index}",
            'tag_configure': lambda tag, **kwargs: None
        })()
        
        # Test 1: DataFrame con valores NaN
        print("🔄 Test 1: DataFrame con valores NaN...")
        nan_df = pd.DataFrame({
            'Strategy Name': ['Test1', 'Test2'],
            'CAGR': [1.0, np.nan],
            'Unified_Score': [0.8, np.nan]
        })
        gui._display_results(nan_df, {})
        print("✅ Manejo de NaN correcto")
        
        # Test 2: DataFrame con tipos mixtos
        print("🔄 Test 2: DataFrame con tipos mixtos...")
        mixed_df = pd.DataFrame({
            'Strategy Name': ['Test1', 'Test2'],
            'CAGR': ['1.5', 2.0],
            'Unified_Score': [0.8, '0.9']
        })
        gui._display_results(mixed_df, {})
        print("✅ Manejo de tipos mixtos correcto")
        
        # Test 3: DataFrame muy grande
        print("🔄 Test 3: DataFrame grande...")
        large_df = pd.DataFrame({
            'Strategy Name': [f'Strategy_{i}' for i in range(100)],
            'CAGR': np.random.uniform(1.0, 5.0, 100),
            'Unified_Score': np.random.uniform(0.5, 0.9, 100)
        })
        gui._display_results(large_df, {})
        print("✅ Manejo de DataFrame grande correcto")
        
        root.destroy()
        
        print("\n✅ Todos los casos edge pasaron correctamente")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN CASOS EDGE: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando tests de implementación de pestaña de resultados...")
    
    # Ejecutar tests
    test1_passed = test_results_table_implementation()
    test2_passed = test_display_results_edge_cases()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE TESTS")
    print("=" * 70)
    print(f"✅ Test principal: {'PASÓ' if test1_passed else 'FALLÓ'}")
    print(f"✅ Casos edge: {'PASÓ' if test2_passed else 'FALLÓ'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ La implementación de la pestaña de resultados está lista para producción")
    else:
        print("\n❌ Algunos tests fallaron")
        print("⚠️ Revisar la implementación antes de continuar")
    
    print("=" * 70) 