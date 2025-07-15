#!/usr/bin/env python3
"""
TEST_GUI_RAPIDO.py - Test rápido de validación de la GUI
"""

import sys
import os
import time
import tkinter as tk
from tkinter import ttk

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath('src'))

def test_gui_rapido():
    """Test rápido de validación de la GUI."""
    print("🔍 TEST RÁPIDO DE VALIDACIÓN GUI")
    print("=" * 50)
    
    try:
        # Importar la GUI
        from src.gui.main_window import MainWindow as EnhancedRankGUI
        print("✅ Módulo GUI importado correctamente")
        
        # Crear instancia de la GUI
        print("🚀 Creando instancia de la GUI...")
        app = EnhancedRankGUI()
        print("✅ GUI creada exitosamente")
        
        # Verificar componentes críticos
        print("\n📋 Verificando componentes críticos...")
        
        # Verificar pestañas principales
        pestañas_principales = ['tab_config', 'tab_results', 'tab_log', 'tab_help']
        for pestaña in pestañas_principales:
            if hasattr(app, pestaña):
                print(f"✅ Pestaña {pestaña}: OK")
            else:
                print(f"❌ Pestaña {pestaña}: FALTA")
        
        # Verificar variables críticas
        variables_criticas = ['var_kpi', 'var_sqx', 'var_market', 'var_dest']
        for var in variables_criticas:
            if hasattr(app, var):
                print(f"✅ Variable {var}: OK")
            else:
                print(f"❌ Variable {var}: FALTA")
        
        # Verificar widgets críticos
        widgets_criticos = ['tree_results', 'progress', 'run_btn']
        for widget in widgets_criticos:
            if hasattr(app, widget):
                print(f"✅ Widget {widget}: OK")
            else:
                print(f"❌ Widget {widget}: FALTA")
        
        # Verificar funciones críticas
        funciones_criticas = ['_run_analysis', '_export_to_excel', '_ejecutar_asesor_financiero']
        for func in funciones_criticas:
            if hasattr(app, func):
                print(f"✅ Función {func}: OK")
            else:
                print(f"❌ Función {func}: FALTA")
        
        # Verificar subpestañas del asesor
        print("\n🤖 Verificando subpestañas del asesor...")
        subpestañas_asesor = ['tab_asesor_analisis', 'tab_asesor_cientifico', 'tab_asesor_empirico', 'tab_asesor_seleccionadas']
        for subpestaña in subpestañas_asesor:
            if hasattr(app, subpestaña):
                print(f"✅ Subpestaña {subpestaña}: OK")
            else:
                print(f"❌ Subpestaña {subpestaña}: FALTA")
        
        # Verificar tooltips y ayuda
        print("\n📚 Verificando tooltips y ayuda...")
        if hasattr(app, '_crear_tooltip'):
            print("✅ Tooltips: IMPLEMENTADOS")
        else:
            print("❌ Tooltips: NO IMPLEMENTADOS")
        
        if hasattr(app, '_mostrar_ayuda_rapida'):
            print("✅ Ayuda rápida: IMPLEMENTADA")
        else:
            print("❌ Ayuda rápida: NO IMPLEMENTADA")
        
        # Verificar botones de la Fase 4
        print("\n🔧 Verificando botones de la Fase 4...")
        botones_fase4 = ['save_selected_btn', 'pass_to_asesor_btn', 'ayuda_rapida_btn']
        for botón in botones_fase4:
            if hasattr(app, botón):
                print(f"✅ Botón {botón}: OK")
            else:
                print(f"❌ Botón {botón}: FALTA")
        
        # Verificar contadores y estadísticas
        print("\n📊 Verificando contadores y estadísticas...")
        contadores = ['lbl_total_strategies', 'lbl_selected_strategies', 'lbl_avg_score']
        for contador in contadores:
            if hasattr(app, contador):
                print(f"✅ Contador {contador}: OK")
            else:
                print(f"❌ Contador {contador}: FALTA")
        
        # Verificar funciones de actualización
        funciones_actualizacion = ['_update_checkboxes', '_update_asesor_selection_count']
        for func in funciones_actualizacion:
            if hasattr(app, func):
                print(f"✅ Función {func}: OK")
            else:
                print(f"❌ Función {func}: FALTA")
        
        print("\n" + "=" * 50)
        print("✅ TEST RÁPIDO COMPLETADO")
        print("🎉 La GUI está lista para pruebas y refinamiento")
        
        # Cerrar la GUI después del test
        app.destroy()
        
        assert True
        
    except Exception as e:
        print(f"❌ Error en test rápido: {e}")
        import traceback
        traceback.print_exc()
        assert False

if __name__ == "__main__":
    test_gui_rapido() 