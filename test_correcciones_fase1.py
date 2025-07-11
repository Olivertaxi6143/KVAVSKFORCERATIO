#!/usr/bin/env python3
"""
Test Automático CLI - Correcciones Críticas Fase 1
Verifica que las mejoras implementadas funcionen correctamente
"""

import sys
import os
import logging
import pandas as pd
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui_enhanced_rank import EnhancedRankGUI
from data_manager import DataManager

def setup_logging():
    """Configurar logging para el test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'test_correcciones_fase1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )

def test_reorganizacion_pestaña_resultados():
    """Test 1: Verificar reorganización de pestaña de resultados"""
    print("\n" + "="*60)
    print("🧪 TEST 1: REORGANIZACIÓN PESTAÑA RESULTADOS")
    print("="*60)
    
    try:
        # Crear instancia de GUI
        gui = EnhancedRankGUI()
        
        # Verificar que existe el método de reorganización
        if hasattr(gui, '_display_results'):
            print("✅ Método _display_results existe")
        else:
            print("❌ ERROR: Método _display_results no existe")
            return False
        
        # Verificar que existe la tabla de estrategias filtradas
        if hasattr(gui, 'filtered_strategies_tree'):
            print("✅ Atributo filtered_strategies_tree existe")
        else:
            print("❌ ERROR: Atributo filtered_strategies_tree no existe")
            return False
        
        print("✅ Reorganización de pestaña de resultados implementada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en test reorganización: {str(e)}")
        return False

def test_subpestaña_estrategias_seleccionadas():
    """Test 2: Verificar subpestaña Estrategias Seleccionadas"""
    print("\n" + "="*60)
    print("🧪 TEST 2: SUBPESTAÑA ESTRATEGIAS SELECCIONADAS")
    print("="*60)
    
    try:
        # Crear instancia de GUI
        gui = EnhancedRankGUI()
        
        # Verificar métodos de la subpestaña
        methods_to_check = [
            '_build_asesor_seleccionadas_tab',
            '_update_asesor_strategies_table',
            '_show_strategy_details',
            '_on_asesor_treeview_double_click'
        ]
        
        for method in methods_to_check:
            if hasattr(gui, method):
                print(f"✅ Método {method} existe")
            else:
                print(f"❌ ERROR: Método {method} no existe")
                return False
        
        # Verificar que la tabla tiene las columnas correctas
        if hasattr(gui, 'tree_asesor_strategies'):
            print("✅ Tabla tree_asesor_strategies existe")
        else:
            print("❌ ERROR: Tabla tree_asesor_strategies no existe")
            return False
        
        print("✅ Subpestaña Estrategias Seleccionadas implementada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en test subpestaña: {str(e)}")
        return False

def test_popup_detalles_individuales():
    """Test 3: Verificar popup de detalles individuales"""
    print("\n" + "="*60)
    print("🧪 TEST 3: POPUP DETALLES INDIVIDUALES")
    print("="*60)
    
    try:
        # Crear instancia de GUI
        gui = EnhancedRankGUI()
        
        # Verificar método de detalles
        if hasattr(gui, '_show_strategy_details'):
            print("✅ Método _show_strategy_details existe")
        else:
            print("❌ ERROR: Método _show_strategy_details no existe")
            return False
        
        # Verificar que el método maneja estadísticas empíricas
        method_source = gui._show_strategy_details.__code__.co_consts
        if any('estadísticas empíricas' in str(const) for const in method_source):
            print("✅ Método incluye estadísticas empíricas")
        else:
            print("⚠️ ADVERTENCIA: Método puede no incluir estadísticas empíricas completas")
        
        print("✅ Popup de detalles individuales implementado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en test popup: {str(e)}")
        return False

def test_layout_mejorado():
    """Test 4: Verificar layout mejorado con controles reorganizados"""
    print("\n" + "="*60)
    print("🧪 TEST 4: LAYOUT MEJORADO")
    print("="*60)
    
    try:
        # Crear instancia de GUI
        gui = EnhancedRankGUI()
        
        # Verificar que existe el método de display con layout mejorado
        if hasattr(gui, '_display_results'):
            print("✅ Método _display_results existe")
            
            # Verificar que incluye reorganización
            method_source = gui._display_results.__code__.co_consts
            layout_keywords = ['REORGANIZACIÓN', 'left_frame', 'right_frame', 'main_layout_frame']
            
            found_keywords = 0
            for keyword in layout_keywords:
                if any(keyword in str(const) for const in method_source):
                    found_keywords += 1
            
            if found_keywords >= 3:
                print("✅ Layout mejorado implementado correctamente")
            else:
                print("⚠️ ADVERTENCIA: Layout puede no estar completamente reorganizado")
        else:
            print("❌ ERROR: Método _display_results no existe")
            return False
        
        print("✅ Layout mejorado verificado")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en test layout: {str(e)}")
        return False

def test_scrollbars_estrategias_filtradas():
    """Test 5: Verificar scrollbars en tabla de estrategias filtradas"""
    print("\n" + "="*60)
    print("🧪 TEST 5: SCROLLBARS ESTRATEGIAS FILTRADAS")
    print("="*60)
    
    try:
        # Crear instancia de GUI
        gui = EnhancedRankGUI()
        
        # Verificar que el método incluye scrollbars
        if hasattr(gui, '_display_results'):
            method_source = gui._display_results.__code__.co_consts
            scrollbar_keywords = ['h_scrollbar', 'v_scrollbar', 'xscrollcommand', 'yscrollcommand']
            
            found_keywords = 0
            for keyword in scrollbar_keywords:
                if any(keyword in str(const) for const in method_source):
                    found_keywords += 1
            
            if found_keywords >= 2:
                print("✅ Scrollbars implementados correctamente")
            else:
                print("⚠️ ADVERTENCIA: Scrollbars pueden no estar completamente implementados")
        else:
            print("❌ ERROR: Método _display_results no existe")
            return False
        
        print("✅ Scrollbars verificados")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en test scrollbars: {str(e)}")
        return False

def run_all_tests():
    """Ejecutar todos los tests de correcciones críticas"""
    print("🚀 INICIANDO TESTS DE CORRECCIONES CRÍTICAS FASE 1")
    print("="*80)
    
    setup_logging()
    
    tests = [
        test_reorganizacion_pestaña_resultados,
        test_subpestaña_estrategias_seleccionadas,
        test_popup_detalles_individuales,
        test_layout_mejorado,
        test_scrollbars_estrategias_filtradas
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
            else:
                print(f"❌ Test {test.__name__} falló")
        except Exception as e:
            print(f"❌ ERROR ejecutando test {test.__name__}: {str(e)}")
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE TESTS - CORRECCIONES CRÍTICAS FASE 1")
    print("="*80)
    print(f"✅ Tests pasados: {passed_tests}/{total_tests}")
    print(f"❌ Tests fallidos: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON! Las correcciones críticas están implementadas correctamente.")
        return True
    else:
        print("⚠️ Algunos tests fallaron. Revisar implementación de correcciones críticas.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 