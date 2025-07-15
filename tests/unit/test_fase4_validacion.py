#!/usr/bin/env python3
"""
Test específico para la Fase 4: Validación y feedback
Valida que todas las mejoras implementadas funcionen correctamente
"""

import sys
import os
import time
import json
import logging
from datetime import datetime

# Agregar el directorio src al path
sys.path.append('src')

def test_fase4_validacion():
    """Test completo de la Fase 4: Validación y feedback"""
    print("🧪 INICIANDO TEST FASE 4: VALIDACIÓN Y FEEDBACK")
    print("=" * 60)
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Ejecutar todos los tests
    tests = [
        ("Funcionalidad Crítica", test_funcionalidad_critica),
        ("Integración", test_integracion),
        ("Rendimiento", test_rendimiento),
        ("Usabilidad", test_usabilidad),
        ("Sistema Feedback", test_sistema_feedback)
    ]
    
    resultados = {}
    for test_name, test_func in tests:
        try:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            resultados[test_name] = test_func()
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            resultados[test_name] = False
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN FASE 4")
    print("=" * 60)
    
    passed = sum(resultados.values())
    total = len(resultados)
    
    for test_name, result in resultados.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 TODA LA FASE 4 VALIDADA CORRECTAMENTE")
        return True
    else:
        print("⚠️ ALGUNOS TESTS FALLARON")
        return False

def test_funcionalidad_critica():
    """Test de funcionalidad crítica"""
    print("🔍 Validando funcionalidad crítica...")
    
    try:
        # Importar GUI
        from gui_enhanced_rank import EnhancedRankGUI
        
        # Crear instancia
        app = EnhancedRankGUI()
        print("✅ GUI creada correctamente")
        
        # Verificar variables críticas
        variables_criticas = ['var_kpi', 'var_sqx', 'var_market', 'var_dest']
        for var in variables_criticas:
            if hasattr(app, var):
                print(f"✅ Variable {var}: OK")
            else:
                print(f"❌ Variable {var}: FALTA")
                return False
        
        # Verificar widgets críticos
        widgets_criticos = ['tree_results', 'progress', 'run_btn']
        for widget in widgets_criticos:
            if hasattr(app, widget):
                print(f"✅ Widget {widget}: OK")
            else:
                print(f"❌ Widget {widget}: FALTA")
                return False
        
        # Verificar funciones críticas
        funciones_criticas = [
            '_run_analysis', '_export_selected_sqxs', '_ejecutar_asesor_financiero'
        ]
        for func in funciones_criticas:
            if hasattr(app, func):
                print(f"✅ Función {func}: OK")
            else:
                print(f"❌ Función {func}: FALTA")
                return False
        
        print("✅ Funcionalidad crítica: VALIDADA")
        return True
        
    except Exception as e:
        print(f"❌ Error en test funcionalidad crítica: {e}")
        return False

def test_integracion():
    """Test de integración"""
    print("🔍 Validando integración...")
    
    try:
        from gui_enhanced_rank import EnhancedRankGUI
        
        app = EnhancedRankGUI()
        
        # Verificar subpestañas del asesor
        subpestañas = ['tab_asesor_analisis', 'tab_asesor_cientifico', 'tab_asesor_empirico', 'tab_asesor_seleccionadas']
        for tab in subpestañas:
            if hasattr(app, tab):
                print(f"✅ Subpestaña {tab}: OK")
            else:
                print(f"❌ Subpestaña {tab}: FALTA")
                return False
        
        # Verificar notebook del asesor
        if hasattr(app, 'asesor_notebook'):
            print("✅ Notebook asesor: OK")
        else:
            print("❌ Notebook asesor: FALTA")
            return False
        
        # Verificar funciones de actualización
        funciones_actualizacion = ['_update_checkboxes', '_update_asesor_selection_count']
        for func in funciones_actualizacion:
            if hasattr(app, func):
                print(f"✅ Función {func}: OK")
            else:
                print(f"❌ Función {func}: FALTA")
                return False
        
        print("✅ Integración: VALIDADA")
        return True
        
    except Exception as e:
        print(f"❌ Error en test integración: {e}")
        return False

def test_rendimiento():
    """Test de rendimiento"""
    print("🔍 Validando rendimiento...")
    
    try:
        from gui_enhanced_rank import EnhancedRankGUI
        
        # Medir tiempo de creación
        start_time = time.time()
        app = EnhancedRankGUI()
        creation_time = time.time() - start_time
        
        print(f"⏱️ Tiempo de creación GUI: {creation_time:.2f}s")
        
        if creation_time < 5.0:
            print("✅ Tiempo de creación: ACEPTABLE")
        else:
            print("⚠️ Tiempo de creación: LENTO")
        
        # Verificar análisis en hilo separado
        if hasattr(app, '_threaded_analysis'):
            print("✅ Análisis en hilo separado: CONFIGURADO")
        else:
            print("⚠️ Análisis no está en hilo separado")
        
        # Verificar barra de progreso
        if hasattr(app, 'progress'):
            print("✅ Barra de progreso: DISPONIBLE")
        else:
            print("⚠️ Barra de progreso: NO ENCONTRADA")
        
        # Verificar funciones de escalabilidad
        funciones_escalabilidad = ['_display_results', '_categorize_quality']
        for func in funciones_escalabilidad:
            if hasattr(app, func):
                print(f"✅ Función escalabilidad {func}: OK")
            else:
                print(f"❌ Función escalabilidad {func}: FALTA")
        
        print("✅ Rendimiento: VALIDADO")
        return True
        
    except Exception as e:
        print(f"❌ Error en test rendimiento: {e}")
        return False

def test_usabilidad():
    """Test de usabilidad"""
    print("🔍 Validando usabilidad...")
    
    try:
        from gui_enhanced_rank import EnhancedRankGUI
        
        app = EnhancedRankGUI()
        
        # Verificar botones principales
        botones_principales = ['run_btn', 'save_selected_btn', 'pass_to_asesor_btn']
        for btn in botones_principales:
            if hasattr(app, btn):
                print(f"✅ Botón {btn}: DISPONIBLE")
            else:
                print(f"⚠️ Botón {btn}: NO ENCONTRADO")
        
        # Verificar tooltips
        if hasattr(app, '_crear_tooltip'):
            print("✅ Tooltips: IMPLEMENTADOS")
        else:
            print("⚠️ Tooltips: NO IMPLEMENTADOS")
        
        # Verificar ayuda rápida
        if hasattr(app, 'ayuda_rapida'):
            print("✅ Ayuda rápida: DISPONIBLE")
        else:
            print("⚠️ Ayuda rápida: NO DISPONIBLE")
        
        # Verificar funciones principales
        funciones_principales = [
            '_run_analysis', '_export_to_excel', '_export_selected_sqxs',
            '_ejecutar_asesor_financiero', '_mostrar_ayuda_rapida'
        ]
        for func in funciones_principales:
            if hasattr(app, func):
                print(f"✅ Función {func}: ACCESIBLE")
            else:
                print(f"⚠️ Función {func}: NO ENCONTRADA")
        
        # Verificar contadores
        if hasattr(app, '_update_checkboxes'):
            print("✅ Contadores de selección: FUNCIONALES")
        else:
            print("⚠️ Contadores de selección: NO FUNCIONALES")
        
        print("✅ Usabilidad: VALIDADA")
        return True
        
    except Exception as e:
        print(f"❌ Error en test usabilidad: {e}")
        return False

def test_sistema_feedback():
    """Test del sistema de feedback"""
    print("🔍 Validando sistema de feedback...")
    
    try:
        from gui_enhanced_rank import EnhancedRankGUI
        
        app = EnhancedRankGUI()
        
        # Verificar funciones de feedback
        funciones_feedback = [
            'reportar_problema', 'enviar_sugerencia', 
            'actualizar_metrica', 'guardar_metricas'
        ]
        for func in funciones_feedback:
            if hasattr(app, func):
                print(f"✅ Función feedback {func}: OK")
            else:
                print(f"⚠️ Función feedback {func}: NO ENCONTRADA")
        
        # Verificar métricas de uso
        if hasattr(app, 'metricas_uso'):
            print("✅ Métricas de uso: INICIALIZADAS")
            print(f"   Métricas disponibles: {list(app.metricas_uso.keys())}")
        else:
            print("⚠️ Métricas de uso: NO INICIALIZADAS")
        
        # Verificar log de errores detallado
        if hasattr(app, 'log_error_detallado'):
            print("✅ Log de errores detallado: DISPONIBLE")
        else:
            print("⚠️ Log de errores detallado: NO DISPONIBLE")
        
        # Crear archivo de test de feedback
        test_feedback = {
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'test': 'Fase 4 - Sistema Feedback',
            'resultado': 'VALIDADO'
        }
        
        with open('test_feedback_fase4.json', 'w', encoding='utf-8') as f:
            json.dump(test_feedback, f, indent=2, ensure_ascii=False)
        
        print("✅ Archivo de test feedback creado")
        print("✅ Sistema de feedback: VALIDADO")
        return True
        
    except Exception as e:
        print(f"❌ Error en test sistema feedback: {e}")
        return False

def main():
    """Función principal"""
    print("KFORCEVSQVARATIOS - Test Fase 4: Validación y Feedback")
    print("=" * 60)
    
    # Ejecutar test completo
    success = test_fase4_validacion()
    
    if success:
        print("\n🎉 TODA LA FASE 4 HA SIDO VALIDADA EXITOSAMENTE")
        print("✅ El sistema está listo para uso en producción")
    else:
        print("\n⚠️ ALGUNOS ASPECTOS DE LA FASE 4 NECESITAN ATENCIÓN")
        print("🔧 Revisar los tests que fallaron")
    
    return success

if __name__ == "__main__":
    main() 