"""
Test de Modularización de GUI

Este test verifica que la modularización de la interfaz gráfica
funciona correctamente y que todos los módulos se importan sin errores.
"""

import sys
import os
import unittest
import tkinter as tk
from tkinter import ttk
import logging

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar logging para tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestGUIModularization(unittest.TestCase):
    """Test para verificar la modularización de la GUI."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        logger.info("🔧 Configurando test de modularización GUI")
        
        # Crear ventana de prueba
        self.root = tk.Tk()
        self.root.withdraw()  # Ocultar ventana durante tests
        
    def tearDown(self):
        """Limpieza después de cada test."""
        logger.info("🧹 Limpiando test de modularización GUI")
        
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_import_gui_utils(self):
        """Test: Importar módulo de utilidades GUI."""
        try:
            from src.gui.utils import (
                TkinterLogHandler,
                GUIAnalysisError,
                create_styled_button,
                show_info_message,
                QVA_COL_MAP,
                DEFAULT_CONFIG
            )
            
            # Verificar que las clases y funciones existen
            self.assertIsNotNone(TkinterLogHandler)
            self.assertIsNotNone(GUIAnalysisError)
            self.assertIsNotNone(create_styled_button)
            self.assertIsNotNone(show_info_message)
            self.assertIsNotNone(QVA_COL_MAP)
            self.assertIsNotNone(DEFAULT_CONFIG)
            
            logger.info("✅ Test import_gui_utils: PASÓ")
            
        except Exception as e:
            logger.error(f"❌ Test import_gui_utils: FALLÓ - {e}")
            self.fail(f"Error importando utilidades GUI: {e}")
    
    def test_import_step1_load(self):
        """Test: Importar módulo del Paso 1."""
        try:
            from src.gui.steps.step1_load import Step1LoadFrame, create_step1_load_frame
            
            # Verificar que las clases existen
            self.assertIsNotNone(Step1LoadFrame)
            self.assertIsNotNone(create_step1_load_frame)
            
            logger.info("✅ Test import_step1_load: PASÓ")
            
        except Exception as e:
            logger.error(f"❌ Test import_step1_load: FALLÓ - {e}")
            self.fail(f"Error importando Paso 1: {e}")
    
    def test_import_step2_configure(self):
        """Test: Importar módulo del Paso 2."""
        try:
            from src.gui.steps.step2_configure import Step2ConfigureFrame, create_step2_configure_frame
            
            # Verificar que las clases existen
            self.assertIsNotNone(Step2ConfigureFrame)
            self.assertIsNotNone(create_step2_configure_frame)
            
            logger.info("✅ Test import_step2_configure: PASÓ")
            
        except Exception as e:
            logger.error(f"❌ Test import_step2_configure: FALLÓ - {e}")
            self.fail(f"Error importando Paso 2: {e}")
    
    def test_import_main_window(self):
        """Test: Importar ventana principal."""
        try:
            from src.gui.main_window import MainWindow, create_main_window
            
            # Verificar que las clases existen
            self.assertIsNotNone(MainWindow)
            self.assertIsNotNone(create_main_window)
            
            logger.info("✅ Test import_main_window: PASÓ")
            
        except Exception as e:
            logger.error(f"❌ Test import_main_window: FALLÓ - {e}")
            self.fail(f"Error importando ventana principal: {e}")
    
    def test_create_step1_frame(self):
        """Test: Crear frame del Paso 1."""
        try:
            from src.gui.steps.step1_load import Step1LoadFrame
            
            # Crear frame
            frame = Step1LoadFrame(self.root)
            
            # Verificar que se creó correctamente
            self.assertIsNotNone(frame)
            self.assertIsInstance(frame, ttk.Frame)
            
            logger.info("✅ Test create_step1_frame: PASÓ")
            
        except Exception as e:
            logger.error(f"❌ Test create_step1_frame: FALLÓ - {e}")
            self.fail(f"Error creando frame del Paso 1: {e}")
    
    def test_create_step2_frame(self):
        """Test: Crear frame del Paso 2."""
        try:
            from src.gui.steps.step2_configure import Step2ConfigureFrame
            
            # Crear frame
            frame = Step2ConfigureFrame(self.root)
            
            # Verificar que se creó correctamente
            self.assertIsNotNone(frame)
            self.assertIsInstance(frame, ttk.Frame)
            
            logger.info("✅ Test create_step2_frame: PASÓ")
            
        except Exception as e:
            logger.error(f"❌ Test create_step2_frame: FALLÓ - {e}")
            self.fail(f"Error creando frame del Paso 2: {e}")
    
    def test_gui_utils_functions(self):
        """Test: Funciones de utilidades GUI."""
        try:
            from src.gui.utils import (
                create_styled_button,
                create_styled_label,
                show_info_message,
                show_error_message,
                format_number,
                format_percentage
            )
            
            # Test crear botón estilizado
            button = create_styled_button(self.root, "Test", lambda: None)
            self.assertIsNotNone(button)
            self.assertIsInstance(button, ttk.Button)
            
            # Test crear etiqueta estilizada
            label = create_styled_label(self.root, "Test")
            self.assertIsNotNone(label)
            self.assertIsInstance(label, ttk.Label)
            
            # Test funciones de formato
            formatted_number = format_number(123.456, 2)
            self.assertEqual(formatted_number, "123.46")
            
            formatted_percentage = format_percentage(85.5, 1)
            self.assertEqual(formatted_percentage, "85.5%")
            
            logger.info("✅ Test gui_utils_functions: PASÓ")
            
        except Exception as e:
            logger.error(f"❌ Test gui_utils_functions: FALLÓ - {e}")
            self.fail(f"Error probando funciones de utilidades GUI: {e}")
    
    def test_step1_functionality(self):
        """Test: Funcionalidad básica del Paso 1."""
        try:
            from src.gui.steps.step1_load import Step1LoadFrame
            
            # Crear frame
            frame = Step1LoadFrame(self.root)
            
            # Verificar que tiene los métodos esperados
            self.assertTrue(hasattr(frame, 'get_loaded_data'))
            self.assertTrue(hasattr(frame, 'set_loaded_data'))
            self.assertTrue(hasattr(frame, 'is_ready_for_next_step'))
            self.assertTrue(hasattr(frame, 'reset_step'))
            
            # Verificar estado inicial
            self.assertFalse(frame.is_ready_for_next_step())
            
            # Test obtener datos cargados
            data = frame.get_loaded_data()
            self.assertIsInstance(data, dict)
            self.assertIn('kpi_file', data)
            self.assertIn('strategies_folder', data)
            self.assertIn('load_status', data)
            
            logger.info("✅ Test step1_functionality: PASÓ")
            
        except Exception as e:
            logger.error(f"❌ Test step1_functionality: FALLÓ - {e}")
            self.fail(f"Error probando funcionalidad del Paso 1: {e}")
    
    def test_step2_functionality(self):
        """Test: Funcionalidad básica del Paso 2."""
        try:
            from src.gui.steps.step2_configure import Step2ConfigureFrame
            
            # Crear frame
            frame = Step2ConfigureFrame(self.root)
            
            # Verificar que tiene los métodos esperados
            self.assertTrue(hasattr(frame, 'get_configuration'))
            self.assertTrue(hasattr(frame, 'set_configuration'))
            self.assertTrue(hasattr(frame, 'is_ready_for_next_step'))
            self.assertTrue(hasattr(frame, 'reset_step'))
            
            # Verificar estado inicial
            self.assertFalse(frame.is_ready_for_next_step())
            
            # Test obtener configuración
            config = frame.get_configuration()
            self.assertIsInstance(config, dict)
            self.assertIn('trading_style', config)
            self.assertIn('alpha', config)
            self.assertIn('percentile', config)
            self.assertIn('top_n', config)
            self.assertIn('selected_kpis', config)
            
            logger.info("✅ Test step2_functionality: PASÓ")
            
        except Exception as e:
            logger.error(f"❌ Test step2_functionality: FALLÓ - {e}")
            self.fail(f"Error probando funcionalidad del Paso 2: {e}")
    
    def test_package_structure(self):
        """Test: Verificar estructura del paquete GUI."""
        try:
            import src.gui
            import src.gui.steps
            import src.gui.advisor
            
            # Verificar que los paquetes existen
            self.assertIsNotNone(src.gui)
            self.assertIsNotNone(src.gui.steps)
            self.assertIsNotNone(src.gui.advisor)
            
            # Verificar que tienen __all__ definido
            self.assertTrue(hasattr(src.gui, '__all__'))
            self.assertTrue(hasattr(src.gui.steps, '__all__'))
            self.assertTrue(hasattr(src.gui.advisor, '__all__'))
            
            logger.info("✅ Test package_structure: PASÓ")
            
        except Exception as e:
            logger.error(f"❌ Test package_structure: FALLÓ - {e}")
            self.fail(f"Error verificando estructura del paquete: {e}")
    
    def test_import_all_gui_modules(self):
        """Test: Importar todos los módulos GUI desde el paquete principal."""
        try:
            from src.gui import (
                MainWindow,
                create_main_window,
                Step1LoadFrame,
                Step2ConfigureFrame,
                create_styled_button,
                show_info_message,
                QVA_COL_MAP,
                DEFAULT_CONFIG
            )
            
            # Verificar que todos los módulos se importan correctamente
            self.assertIsNotNone(MainWindow)
            self.assertIsNotNone(create_main_window)
            self.assertIsNotNone(Step1LoadFrame)
            self.assertIsNotNone(Step2ConfigureFrame)
            self.assertIsNotNone(create_styled_button)
            self.assertIsNotNone(show_info_message)
            self.assertIsNotNone(QVA_COL_MAP)
            self.assertIsNotNone(DEFAULT_CONFIG)
            
            logger.info("✅ Test import_all_gui_modules: PASÓ")
            
        except Exception as e:
            logger.error(f"❌ Test import_all_gui_modules: FALLÓ - {e}")
            self.fail(f"Error importando todos los módulos GUI: {e}")


def run_gui_modularization_tests():
    """Ejecuta todos los tests de modularización de GUI."""
    logger.info("🚀 Iniciando tests de modularización de GUI")
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGUIModularization)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    logger.info(f"📊 Resultados de tests:")
    logger.info(f"   - Tests ejecutados: {result.testsRun}")
    logger.info(f"   - Tests exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
    logger.info(f"   - Tests fallidos: {len(result.failures)}")
    logger.info(f"   - Tests con errores: {len(result.errors)}")
    
    if result.wasSuccessful():
        logger.info("✅ Todos los tests de modularización GUI PASARON")
        return True
    else:
        logger.error("❌ Algunos tests de modularización GUI FALLARON")
        return False


if __name__ == "__main__":
    # Ejecutar tests
    success = run_gui_modularization_tests()
    
    # Salir con código apropiado
    sys.exit(0 if success else 1) 