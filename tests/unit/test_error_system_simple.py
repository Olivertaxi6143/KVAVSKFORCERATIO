#!/usr/bin/env python3
"""
Test simple del sistema de mensajes de error en pantalla.
"""

import sys
import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_error_display_manager():
    """Test simple del ErrorDisplayManager."""
    try:
        logger.info("🧪 Test simple del sistema de errores")
        
        # Crear ventana principal
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        
        # Importar después de configurar tkinter
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
        from src.gui.gui_enhanced_rank import ErrorDisplayManager
        
        # Crear un mock parent con el método _log_message
        class MockParent:
            def _log_message(self, message, level="INFO"):
                logger.info(f"[GUI] {message}")
        
        mock_parent = MockParent()
        error_manager = ErrorDisplayManager(mock_parent)
        logger.info("✅ ErrorDisplayManager creado correctamente")
        
        # Test error básico
        error_manager.show_error(
            "Test Error",
            "Este es un mensaje de error de prueba para validar el sistema.",
            "ERROR",
            True,
            "Detalles técnicos del error de prueba"
        )
        
        logger.info("✅ Ventana de error mostrada correctamente")
        
        # Test warning
        error_manager.show_warning(
            "Test Warning",
            "Este es un mensaje de advertencia de prueba.",
            True,
            "Detalles de la advertencia"
        )
        
        logger.info("✅ Ventana de warning mostrada correctamente")
        
        # Test error de validación
        error_manager.show_validation_error(
            "Campo de Prueba",
            "El campo tiene un formato inválido",
            ["Sugerencia 1: Verificar formato", "Sugerencia 2: Comprobar datos"]
        )
        
        logger.info("✅ Ventana de error de validación mostrada correctamente")
        
        # Test error de datos
        error_manager.show_data_error(
            "Carga de Archivo",
            "No se pudo cargar el archivo de datos",
            "/ruta/ejemplo/archivo.csv"
        )
        
        logger.info("✅ Ventana de error de datos mostrada correctamente")
        
        # Test error de análisis
        error_manager.show_analysis_error(
            "Factor K Analysis",
            "Error durante el cálculo del Factor K",
            {"analysis_type": "Factor K", "alpha": 0.8}
        )
        
        logger.info("✅ Ventana de error de análisis mostrada correctamente")
        
        # Cerrar ventanas si existen
        if error_manager.error_window:
            error_manager.error_window.destroy()
        
        logger.info("🎉 TODOS LOS TESTS DEL SISTEMA DE ERRORES PASARON")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

def main():
    """Función principal."""
    logger.info("🔧 INICIANDO TEST SIMPLE DEL SISTEMA DE ERRORES")
    
    success = test_error_display_manager()
    
    if success:
        logger.info("✅ TEST EXITOSO: Sistema de errores funcionando correctamente")
        return 0
    else:
        logger.error("❌ TEST FALLIDO: Problemas con el sistema de errores")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 