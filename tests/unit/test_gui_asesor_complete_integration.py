#!/usr/bin/env python3
"""
Test comprehensivo de la integración GUI-Asesor Financiero.

Este test valida:
1. Sistema de mensajes de error en pantalla
2. Popup de detalles avanzados de estrategias
3. Pestañas del asesor con datos reales
4. Integración completa GUI-Asesor
5. Funcionalidad de copiar/exportar
6. Robustez y manejo de errores
"""

import sys
import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_error_display_system():
    """Test del sistema de mensajes de error en pantalla."""
    try:
        logger.info("🧪 Test del sistema de mensajes de error")
        
        # Crear ventana principal
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        
        # Importar después de configurar tkinter
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
        from src.gui.utils import GUIAnalysisError as ErrorDisplayManager
        
        # Crear un mock parent con el método _log_message
        class MockParent:
            def _log_message(self, message, level="INFO"):
                logger.info(f"[GUI] {message}")
        
        mock_parent = MockParent()
        error_manager = ErrorDisplayManager(mock_parent)
        logger.info("✅ ErrorDisplayManager creado correctamente")
        
        # Test diferentes tipos de errores
        error_manager.show_error("Test Error", "Este es un error de prueba", "ERROR", True, "Detalles del error")
        logger.info("✅ Error básico mostrado")
        
        error_manager.show_warning("Test Warning", "Esta es una advertencia", True, "Detalles de la advertencia")
        logger.info("✅ Warning mostrado")
        
        error_manager.show_info("Test Info", "Esta es información")
        logger.info("✅ Info mostrado")
        
        error_manager.show_validation_error("Campo Test", "Error de validación", ["Sugerencia 1", "Sugerencia 2"])
        logger.info("✅ Error de validación mostrado")
        
        error_manager.show_data_error("Operación Test", "Error de datos", "/ruta/archivo.csv")
        logger.info("✅ Error de datos mostrado")
        
        error_manager.show_analysis_error("Análisis Test", "Error de análisis", {"tipo": "test", "config": "test"})
        logger.info("✅ Error de análisis mostrado")
        
        root.destroy()
        logger.info("✅ Test del sistema de errores completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test del sistema de errores: {e}")
        return False

def test_popup_details():
    """Test del popup de detalles avanzados."""
    try:
        logger.info("🧪 Test del popup de detalles avanzados")
        
        # Crear ventana principal
        root = tk.Tk()
        root.withdraw()
        
        # Importar GUI
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
        from src.gui.main_window import MainWindow as EnhancedRankGUI
        
        # Crear datos de prueba
        test_data = pd.DataFrame({
            'Strategy_Name': ['Test Strategy 1', 'Test Strategy 2'],
            'CAGR': [15.5, 12.3],
            'Sharpe Ratio': [1.8, 1.5],
            'Max DD %': [8.2, 12.1],
            'Profit factor': [2.1, 1.8],
            'CalmarRatio': [1.89, 1.02],
            'Unified_Score': [0.85, 0.72],
            'Quality_Category': ['Elite', 'Excellent'],
            'Explicación': ['Excelente consistencia', 'Buena estrategia'],
            '# of trades': [150, 120],
            'Winning Percent': [65.2, 58.7],
            'Avg. Bars in Trade': [45.3, 52.1],
            'Exposure': [0.85, 0.78],
            'Max Consec. Losses': [3, 5],
            'Stagnation': [0.12, 0.18],
            'Ulcer Index %': [2.1, 3.5],
            'VaR (95%)': [1.8, 2.4]
        })
        
        # Crear instancia de GUI
        gui = EnhancedRankGUI()
        gui.filtered_results_df = test_data
        
        # Test mostrar detalles
        strategy_data = test_data.iloc[0]
        gui._show_advanced_strategy_details(strategy_data)
        logger.info("✅ Popup de detalles mostrado correctamente")
        
        # Test copiar detalles
        gui._copy_strategy_details_to_clipboard(strategy_data)
        logger.info("✅ Detalles copiados al portapapeles")
        
        root.destroy()
        logger.info("✅ Test del popup de detalles completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test del popup de detalles: {e}")
        return False

def test_asesor_tabs_integration():
    """Test de la integración de pestañas del asesor."""
    try:
        logger.info("🧪 Test de integración de pestañas del asesor")
        
        # Crear ventana principal
        root = tk.Tk()
        root.withdraw()
        
        # Importar GUI
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
        from src.gui.main_window import MainWindow as EnhancedRankGUI
        
        # Crear datos de prueba más completos
        test_data = pd.DataFrame({
            'Strategy_Name': [f'Strategy_{i}' for i in range(1, 21)],
            'CAGR': np.random.uniform(5, 25, 20),
            'Sharpe Ratio': np.random.uniform(0.5, 2.5, 20),
            'Max DD %': np.random.uniform(5, 20, 20),
            'Profit factor': np.random.uniform(1.2, 3.0, 20),
            'CalmarRatio': np.random.uniform(0.5, 2.0, 20),
            'Unified_Score': np.random.uniform(0.3, 0.95, 20),
            'Quality_Category': np.random.choice(['Elite', 'Excellent', 'Very Good', 'Good'], 20),
            'Explicación': [f'Explicación para estrategia {i}' for i in range(1, 21)],
            '# of trades': np.random.randint(50, 300, 20),
            'Winning Percent': np.random.uniform(45, 75, 20),
            'Avg. Bars in Trade': np.random.uniform(20, 80, 20),
            'Exposure': np.random.uniform(0.6, 0.95, 20),
            'Max Consec. Losses': np.random.randint(2, 8, 20),
            'Stagnation': np.random.uniform(0.05, 0.25, 20),
            'Ulcer Index %': np.random.uniform(1.0, 5.0, 20),
            'VaR (95%)': np.random.uniform(1.0, 4.0, 20),
            'CAGR_IS': np.random.uniform(5, 25, 20),
            'CAGR_OOS': np.random.uniform(3, 22, 20),
            'Sharpe_IS': np.random.uniform(0.5, 2.5, 20),
            'Sharpe_OOS': np.random.uniform(0.3, 2.2, 20)
        })
        
        # Crear instancia de GUI
        gui = EnhancedRankGUI()
        gui.filtered_results_df = test_data
        
        # Test análisis científico
        gui._actualizar_analisis_cientifico()
        logger.info("✅ Análisis científico actualizado")
        
        # Test análisis empírico
        gui._actualizar_analisis_empirico()
        logger.info("✅ Análisis empírico actualizado")
        
        # Test copiar contenido científico
        gui._copiar_cientifico_asesor()
        logger.info("✅ Contenido científico copiado")
        
        # Test copiar contenido empírico
        gui._copiar_empirico_asesor()
        logger.info("✅ Contenido empírico copiado")
        
        # Test exportar contenido científico
        gui._exportar_cientifico_asesor()
        logger.info("✅ Contenido científico exportado")
        
        # Test exportar contenido empírico
        gui._exportar_empirico_asesor()
        logger.info("✅ Contenido empírico exportado")
        
        root.destroy()
        logger.info("✅ Test de integración de pestañas del asesor completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de integración de pestañas del asesor: {e}")
        return False

def test_complete_gui_asesor_integration():
    """Test de integración completa GUI-Asesor."""
    try:
        logger.info("🧪 Test de integración completa GUI-Asesor")
        
        # Crear ventana principal
        root = tk.Tk()
        root.withdraw()
        
        # Importar GUI y asesor
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
        from src.gui.main_window import MainWindow as EnhancedRankGUI
        from src.analysis.asesor_financiero_inteligente import AsesorFinancieroInteligente
        
        # Crear datos de prueba
        test_data = pd.DataFrame({
            'Strategy_Name': [f'Strategy_{i}' for i in range(1, 31)],
            'CAGR': np.random.uniform(5, 25, 30),
            'Sharpe Ratio': np.random.uniform(0.5, 2.5, 30),
            'Max DD %': np.random.uniform(5, 20, 30),
            'Profit factor': np.random.uniform(1.2, 3.0, 30),
            'CalmarRatio': np.random.uniform(0.5, 2.0, 30),
            'Unified_Score': np.random.uniform(0.3, 0.95, 30),
            'Quality_Category': np.random.choice(['Elite', 'Excellent', 'Very Good', 'Good'], 30),
            'Explicación': [f'Explicación para estrategia {i}' for i in range(1, 31)],
            '# of trades': np.random.randint(50, 300, 30),
            'Winning Percent': np.random.uniform(45, 75, 30),
            'Avg. Bars in Trade': np.random.uniform(20, 80, 30),
            'Exposure': np.random.uniform(0.6, 0.95, 30),
            'Max Consec. Losses': np.random.randint(2, 8, 30),
            'Stagnation': np.random.uniform(0.05, 0.25, 30),
            'Ulcer Index %': np.random.uniform(1.0, 5.0, 30),
            'VaR (95%)': np.random.uniform(1.0, 4.0, 30)
        })
        
        # Crear instancia de GUI
        gui = EnhancedRankGUI()
        gui.filtered_results_df = test_data
        
        # Test ejecutar asesor financiero
        kpis_numericos = ['CAGR', 'Sharpe Ratio', 'Max DD %', 'Profit factor', 'CalmarRatio']
        
        # Simular ejecución del asesor
        asesor = AsesorFinancieroInteligente(test_data, kpis_numericos)
        resultados = asesor.generar_consejos_completos()
        
        # Test mostrar resultados del asesor
        gui._mostrar_resultados_asesor(resultados, asesor, test_data)
        logger.info("✅ Resultados del asesor mostrados correctamente")
        
        # Test limpiar asesor
        gui._limpiar_asesor_financiero()
        logger.info("✅ Asesor limpiado correctamente")
        
        # Test manejo de errores del asesor
        gui._mostrar_error_asesor("Error de prueba del asesor")
        logger.info("✅ Error del asesor manejado correctamente")
        
        root.destroy()
        logger.info("✅ Test de integración completa GUI-Asesor completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de integración completa GUI-Asesor: {e}")
        return False

def main():
    """Función principal del test."""
    logger.info("🚀 Iniciando tests comprehensivos de integración GUI-Asesor")
    
    tests = [
        ("Sistema de Mensajes de Error", test_error_display_system),
        ("Popup de Detalles Avanzados", test_popup_details),
        ("Integración de Pestañas del Asesor", test_asesor_tabs_integration),
        ("Integración Completa GUI-Asesor", test_complete_gui_asesor_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 Ejecutando: {test_name}")
        logger.info(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASÓ")
            else:
                logger.error(f"❌ {test_name}: FALLÓ")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    logger.info(f"\n{'='*60}")
    logger.info("📊 RESUMEN DE TESTS")
    logger.info(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n🎯 RESULTADO FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        logger.info("🎉 ¡TODOS LOS TESTS PASARON! Sistema GUI-Asesor completamente funcional.")
    else:
        logger.warning(f"⚠️ {total - passed} tests fallaron. Revisar implementación.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 