#!/usr/bin/env python3
"""
Test comprehensivo del sistema de mensajes de error en pantalla.

Este test valida:
1. Creación y funcionamiento del ErrorDisplayManager
2. Diferentes tipos de errores (ERROR, WARNING, INFO)
3. Manejo de errores de validación
4. Manejo de errores de datos
5. Manejo de errores de análisis
6. Funcionalidad de copiar al portapapeles
7. Robustez y manejo de excepciones
"""

import sys
import os
import logging
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Importar la GUI y el sistema de errores
from src.gui.main_window import MainWindow as EnhancedRankGUI, ErrorDisplayManager

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestErrorDisplaySystem:
    """Test comprehensivo del sistema de errores."""
    
    def __init__(self):
        """Inicializar el test."""
        self.gui = None
        self.error_manager = None
        self.test_results = []
        
    def setup_gui(self):
        """Configurar GUI para testing."""
        try:
            logger.info("🔧 Configurando GUI para testing...")
            
            # Crear GUI en modo testing
            self.gui = EnhancedRankGUI()
            self.error_manager = self.gui.error_manager
            
            logger.info("✅ GUI configurada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando GUI: {e}")
            return False
    
    def test_error_display_manager_creation(self):
        """Test 1: Creación del ErrorDisplayManager."""
        try:
            logger.info("🧪 Test 1: Creación del ErrorDisplayManager")
            
            # Verificar que el error manager existe
            assert self.error_manager is not None, "ErrorDisplayManager no creado"
            assert isinstance(self.error_manager, ErrorDisplayManager), "Tipo incorrecto de ErrorDisplayManager"
            
            # Verificar atributos básicos
            assert hasattr(self.error_manager, 'parent'), "Falta atributo 'parent'"
            assert hasattr(self.error_manager, 'error_window'), "Falta atributo 'error_window'"
            assert hasattr(self.error_manager, 'error_queue'), "Falta atributo 'error_queue'"
            
            logger.info("✅ Test 1 PASADO: ErrorDisplayManager creado correctamente")
            self.test_results.append(("ErrorDisplayManager Creation", True, "OK"))
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 1 FALLIDO: {e}")
            self.test_results.append(("ErrorDisplayManager Creation", False, str(e)))
            return False
    
    def test_basic_error_display(self):
        """Test 2: Visualización básica de errores."""
        try:
            logger.info("🧪 Test 2: Visualización básica de errores")
            
            # Test error básico
            self.error_manager.show_error(
                "Test Error",
                "Este es un mensaje de error de prueba para validar el sistema.",
                "ERROR",
                True,
                "Detalles técnicos del error de prueba"
            )
            
            # Verificar que la ventana se creó
            assert self.error_manager.error_window is not None, "Ventana de error no creada"
            
            # Cerrar ventana
            if self.error_manager.error_window:
                self.error_manager.error_window.destroy()
                self.error_manager.error_window = None
            
            logger.info("✅ Test 2 PASADO: Visualización básica de errores")
            self.test_results.append(("Basic Error Display", True, "OK"))
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 2 FALLIDO: {e}")
            self.test_results.append(("Basic Error Display", False, str(e)))
            return False
    
    def test_warning_display(self):
        """Test 3: Visualización de advertencias."""
        try:
            logger.info("🧪 Test 3: Visualización de advertencias")
            
            # Test warning
            self.error_manager.show_warning(
                "Test Warning",
                "Este es un mensaje de advertencia de prueba.",
                True,
                "Detalles de la advertencia"
            )
            
            # Verificar que la ventana se creó
            assert self.error_manager.error_window is not None, "Ventana de warning no creada"
            
            # Cerrar ventana
            if self.error_manager.error_window:
                self.error_manager.error_window.destroy()
                self.error_manager.error_window = None
            
            logger.info("✅ Test 3 PASADO: Visualización de advertencias")
            self.test_results.append(("Warning Display", True, "OK"))
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 3 FALLIDO: {e}")
            self.test_results.append(("Warning Display", False, str(e)))
            return False
    
    def test_validation_error_display(self):
        """Test 4: Errores de validación específicos."""
        try:
            logger.info("🧪 Test 4: Errores de validación específicos")
            
            # Test error de validación
            self.error_manager.show_validation_error(
                "Campo de Prueba",
                "El campo tiene un formato inválido",
                ["Sugerencia 1: Verificar formato", "Sugerencia 2: Comprobar datos", "Sugerencia 3: Validar entrada"]
            )
            
            # Verificar que la ventana se creó
            assert self.error_manager.error_window is not None, "Ventana de validación no creada"
            
            # Cerrar ventana
            if self.error_manager.error_window:
                self.error_manager.error_window.destroy()
                self.error_manager.error_window = None
            
            logger.info("✅ Test 4 PASADO: Errores de validación específicos")
            self.test_results.append(("Validation Error Display", True, "OK"))
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 4 FALLIDO: {e}")
            self.test_results.append(("Validation Error Display", False, str(e)))
            return False
    
    def test_data_error_display(self):
        """Test 5: Errores relacionados con datos."""
        try:
            logger.info("🧪 Test 5: Errores relacionados con datos")
            
            # Test error de datos
            self.error_manager.show_data_error(
                "Carga de Archivo",
                "No se pudo cargar el archivo de datos",
                "/ruta/ejemplo/archivo.csv"
            )
            
            # Verificar que la ventana se creó
            assert self.error_manager.error_window is not None, "Ventana de error de datos no creada"
            
            # Cerrar ventana
            if self.error_manager.error_window:
                self.error_manager.error_window.destroy()
                self.error_manager.error_window = None
            
            logger.info("✅ Test 5 PASADO: Errores relacionados con datos")
            self.test_results.append(("Data Error Display", True, "OK"))
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 5 FALLIDO: {e}")
            self.test_results.append(("Data Error Display", False, str(e)))
            return False
    
    def test_analysis_error_display(self):
        """Test 6: Errores de análisis."""
        try:
            logger.info("🧪 Test 6: Errores de análisis")
            
            # Test error de análisis
            config = {
                "analysis_type": "Factor K",
                "alpha": 0.8,
                "percentile": 90,
                "timestamp": datetime.now().isoformat()
            }
            
            self.error_manager.show_analysis_error(
                "Factor K Analysis",
                "Error durante el cálculo del Factor K",
                config
            )
            
            # Verificar que la ventana se creó
            assert self.error_manager.error_window is not None, "Ventana de error de análisis no creada"
            
            # Cerrar ventana
            if self.error_manager.error_window:
                self.error_manager.error_window.destroy()
                self.error_manager.error_window = None
            
            logger.info("✅ Test 6 PASADO: Errores de análisis")
            self.test_results.append(("Analysis Error Display", True, "OK"))
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 6 FALLIDO: {e}")
            self.test_results.append(("Analysis Error Display", False, str(e)))
            return False
    
    def test_clipboard_functionality(self):
        """Test 7: Funcionalidad de copiar al portapapeles."""
        try:
            logger.info("🧪 Test 7: Funcionalidad de copiar al portapapeles")
            
            # Test copiar error al portapapeles
            test_title = "Test Clipboard"
            test_message = "Mensaje de prueba para portapapeles"
            test_details = "Detalles técnicos de prueba"
            
            # Simular copia al portapapeles
            self.error_manager._copy_error_to_clipboard(test_title, test_message, test_details)
            
            # Verificar que no hay errores en la función
            logger.info("✅ Función de copia ejecutada sin errores")
            
            logger.info("✅ Test 7 PASADO: Funcionalidad de copiar al portapapeles")
            self.test_results.append(("Clipboard Functionality", True, "OK"))
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 7 FALLIDO: {e}")
            self.test_results.append(("Clipboard Functionality", False, str(e)))
            return False
    
    def test_error_robustness(self):
        """Test 8: Robustez del sistema de errores."""
        try:
            logger.info("🧪 Test 8: Robustez del sistema de errores")
            
            # Test con parámetros extremos
            self.error_manager.show_error(
                "",  # título vacío
                "Mensaje de prueba con parámetros extremos",
                "ERROR",
                True,
                None  # detalles None
            )
            
            # Verificar que no falla con parámetros extremos
            assert self.error_manager.error_window is not None, "Sistema no robusto con parámetros extremos"
            
            # Cerrar ventana
            if self.error_manager.error_window:
                self.error_manager.error_window.destroy()
                self.error_manager.error_window = None
            
            logger.info("✅ Test 8 PASADO: Robustez del sistema de errores")
            self.test_results.append(("Error Robustness", True, "OK"))
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 8 FALLIDO: {e}")
            self.test_results.append(("Error Robustness", False, str(e)))
            return False
    
    def test_gui_error_integration(self):
        """Test 9: Integración con el sistema de errores de la GUI."""
        try:
            logger.info("🧪 Test 9: Integración con el sistema de errores de la GUI")
            
            # Test error de análisis de la GUI
            test_error = ValueError("Error de prueba para GUI")
            self.gui._handle_analysis_error(test_error)
            
            # Verificar que se usó el error manager
            assert self.error_manager.error_window is not None, "GUI no usa ErrorDisplayManager"
            
            # Cerrar ventana
            if self.error_manager.error_window:
                self.error_manager.error_window.destroy()
                self.error_manager.error_window = None
            
            logger.info("✅ Test 9 PASADO: Integración con el sistema de errores de la GUI")
            self.test_results.append(("GUI Error Integration", True, "OK"))
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 9 FALLIDO: {e}")
            self.test_results.append(("GUI Error Integration", False, str(e)))
            return False
    
    def test_error_with_real_data(self):
        """Test 10: Errores con datos reales simulados."""
        try:
            logger.info("🧪 Test 10: Errores con datos reales simulados")
            
            # Simular error con datos reales
            self.error_manager.show_data_error(
                "Validación de DataFrame",
                "El DataFrame contiene valores NaN en columnas críticas",
                "data/strategies_kpis.csv"
            )
            
            # Verificar que la ventana se creó
            assert self.error_manager.error_window is not None, "Ventana de error con datos reales no creada"
            
            # Cerrar ventana
            if self.error_manager.error_window:
                self.error_manager.error_window.destroy()
                self.error_manager.error_window = None
            
            logger.info("✅ Test 10 PASADO: Errores con datos reales simulados")
            self.test_results.append(("Real Data Error", True, "OK"))
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 10 FALLIDO: {e}")
            self.test_results.append(("Real Data Error", False, str(e)))
            return False
    
    def run_all_tests(self):
        """Ejecutar todos los tests."""
        logger.info("🚀 INICIANDO TESTS DEL SISTEMA DE ERRORES")
        logger.info("=" * 60)
        
        # Configurar GUI
        if not self.setup_gui():
            logger.error("❌ No se pudo configurar la GUI. Abortando tests.")
            return False
        
        # Ejecutar tests
        tests = [
            self.test_error_display_manager_creation,
            self.test_basic_error_display,
            self.test_warning_display,
            self.test_validation_error_display,
            self.test_data_error_display,
            self.test_analysis_error_display,
            self.test_clipboard_functionality,
            self.test_error_robustness,
            self.test_gui_error_integration,
            self.test_error_with_real_data
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for i, test_func in enumerate(tests, 1):
            logger.info(f"\n📋 Ejecutando test {i}/{total_tests}: {test_func.__name__}")
            try:
                if test_func():
                    passed_tests += 1
                else:
                    logger.warning(f"⚠️ Test {i} falló")
            except Exception as e:
                logger.error(f"❌ Error ejecutando test {i}: {e}")
        
        # Mostrar resultados
        self.show_test_results(passed_tests, total_tests)
        
        # Limpiar
        if self.gui:
            self.gui.destroy()
        
        return passed_tests == total_tests
    
    def show_test_results(self, passed: int, total: int):
        """Mostrar resultados de los tests."""
        logger.info("\n" + "=" * 60)
        logger.info("📊 RESULTADOS DE LOS TESTS")
        logger.info("=" * 60)
        
        # Resumen general
        success_rate = (passed / total) * 100 if total > 0 else 0
        logger.info(f"✅ Tests pasados: {passed}/{total} ({success_rate:.1f}%)")
        
        if passed == total:
            logger.info("🎉 ¡TODOS LOS TESTS PASARON!")
        else:
            logger.info(f"⚠️ {total - passed} tests fallaron")
        
        # Detalles por test
        logger.info("\n📋 DETALLES POR TEST:")
        for test_name, passed, details in self.test_results:
            status = "✅ PASÓ" if passed else "❌ FALLÓ"
            logger.info(f"  {test_name}: {status} - {details}")
        
        logger.info("=" * 60)

def main():
    """Función principal del test."""
    logger.info("🔧 INICIANDO TEST DEL SISTEMA DE MENSAJES DE ERROR")
    
    # Crear y ejecutar tests
    tester = TestErrorDisplaySystem()
    success = tester.run_all_tests()
    
    if success:
        logger.info("🎉 TODOS LOS TESTS DEL SISTEMA DE ERRORES PASARON")
        return 0
    else:
        logger.error("❌ ALGUNOS TESTS DEL SISTEMA DE ERRORES FALLARON")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 