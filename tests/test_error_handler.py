"""
Tests para el módulo de Gestión de Errores Intuitiva

Este módulo contiene tests para validar:
- Creación y manejo de errores
- Destacados visuales en la interfaz
- Navegación inteligente
- Validaciones preventivas
- Mensajes de error específicos
"""

import pytest
import tkinter as tk
from tkinter import ttk
import sys
import os
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

# Importar el módulo a testear
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.gui.error_handler import (
    IntuitiveErrorHandler
)


class TestErrorHandler:
    """Tests para la clase IntuitiveErrorHandler."""
    
    @pytest.fixture
    def mock_main_window(self):
        """Fixture para crear una ventana principal mock."""
        # Usar Mock en lugar de tk.Tk para evitar problemas de Tkinter
        mock_window = Mock()
        mock_window.tk = Mock()
        mock_window._last_child_ids = {}
        yield mock_window
    
    @pytest.fixture
    def error_handler(self, mock_main_window):
        """Fixture para crear un IntuitiveErrorHandler."""
        return IntuitiveErrorHandler(mock_main_window)
    
    def test_error_handler_initialization(self, error_handler):
        """Test: Inicialización correcta del IntuitiveErrorHandler."""
        log.info("Test: Inicialización del IntuitiveErrorHandler")
        
        assert error_handler.parent is not None
        assert error_handler.error_window is None
        assert len(error_handler.error_history) == 0
        assert len(error_handler.error_counts) == 0
        assert len(error_handler.error_categories) == 6  # data_loading, data_validation, analysis, export, system, ui
        assert len(error_handler.error_solutions) == 5  # data_loading, data_validation, analysis, export, system (ui no tiene soluciones)
        
        log.debug("IntuitiveErrorHandler inicializado correctamente")
    
    def test_error_categories(self, error_handler):
        """Test: Categorías de error configuradas correctamente."""
        log.info("Test: Categorías de error")
        
        expected_categories = ["data_loading", "data_validation", "analysis", "export", "system", "ui"]
        for category in expected_categories:
            assert category in error_handler.error_categories
            assert "title" in error_handler.error_categories[category]
            assert "icon" in error_handler.error_categories[category]
            assert "color" in error_handler.error_categories[category]
        
        log.debug("Categorías de error configuradas correctamente")
    
    def test_error_solutions(self, error_handler):
        """Test: Soluciones de error configuradas correctamente."""
        log.info("Test: Soluciones de error")
        
        # Verificar que cada categoría tiene soluciones
        for category in error_handler.error_solutions:
            assert len(error_handler.error_solutions[category]) > 0
            for solution_key, solution_data in error_handler.error_solutions[category].items():
                assert "message" in solution_data
                assert "solutions" in solution_data
                assert "action" in solution_data
        
        log.debug("Soluciones de error configuradas correctamente")
    
    def test_handle_error_basic(self, error_handler):
        """Test: Manejo básico de errores."""
        log.info("Test: Manejo básico de errores")
        
        # Simular un error
        test_error = Exception("Test error message")
        error_info = error_handler.handle_error(
            test_error,
            context="test",
            category="data_loading",
            show_dialog=False
        )
        
        # Verificar que se procesó el error
        assert isinstance(error_info, dict)
        assert "type" in error_info
        assert "message" in error_info
        assert "context" in error_info
        assert "category" in error_info
        assert "specific_category" in error_info
        
        log.debug("Error manejado correctamente")
    
    def test_determine_specific_category(self, error_handler):
        """Test: Determinación de categoría específica."""
        log.info("Test: Determinación de categoría específica")
        
        # Test file_not_found
        specific_category = error_handler._determine_specific_category(
            "FileNotFoundError", "file not found", "data_loading"
        )
        assert specific_category == "file_not_found"
        
        # Test invalid_format
        specific_category = error_handler._determine_specific_category(
            "ValueError", "format delimiter", "data_loading"
        )
        assert specific_category == "invalid_format"
        
        # Test unknown error
        specific_category = error_handler._determine_specific_category(
            "UnknownError", "unknown message", "unknown"
        )
        assert specific_category == "unknown_error"
        
        log.debug("Categorías específicas determinadas correctamente")
    
    def test_get_error_solution(self, error_handler):
        """Test: Obtención de soluciones de error."""
        log.info("Test: Obtención de soluciones de error")
        
        # Test solución conocida
        solution = error_handler._get_error_solution("file_not_found", "FileNotFoundError", "file not found")
        assert isinstance(solution, dict)
        assert "message" in solution
        assert "solutions" in solution
        assert "action" in solution
        
        # Test solución genérica
        solution = error_handler._get_error_solution("unknown_error", "UnknownError", "unknown")
        assert isinstance(solution, dict)
        assert "message" in solution
        assert "solutions" in solution
        
        log.debug("Soluciones de error obtenidas correctamente")
    
    def test_create_user_friendly_message(self, error_handler):
        """Test: Creación de mensajes amigables."""
        log.info("Test: Creación de mensajes amigables")
        
        solution = {
            "message": "Test error message",
            "solutions": ["Solution 1", "Solution 2"],
            "action": "test_action"
        }
        
        friendly_message = error_handler._create_user_friendly_message(
            "TestError", "Test error", solution
        )
        
        assert isinstance(friendly_message, str)
        assert "❌" in friendly_message
        assert "Test error message" in friendly_message
        assert "🔧" in friendly_message
        assert "Solution 1" in friendly_message
        assert "Solution 2" in friendly_message
        
        log.debug("Mensaje amigable creado correctamente")
    
    def test_get_recommended_actions(self, error_handler):
        """Test: Obtención de acciones recomendadas."""
        log.info("Test: Obtención de acciones recomendadas")
        
        actions = error_handler._get_recommended_actions("file_not_found", "FileNotFoundError")
        
        assert isinstance(actions, list)
        assert len(actions) > 0
        
        # Verificar que cada acción tiene los campos requeridos
        for action in actions:
            assert "text" in action
            assert "action" in action
            assert "icon" in action
        
        log.debug("Acciones recomendadas obtenidas correctamente")
    
    def test_log_error(self, error_handler):
        """Test: Logging de errores."""
        log.info("Test: Logging de errores")
        
        error_info = {
            "type": "TestError",
            "message": "Test error message",
            "context": "test",
            "category": "data_loading",
            "specific_category": "file_not_found",
            "timestamp": "2025-01-27 10:00:00",  # Usar string en lugar de Timestamp
            "stack_trace": "Test stack trace"
        }
        
        # Log del error
        error_handler._log_error(error_info)
        
        # Verificar que se agregó al historial
        assert len(error_handler.error_history) == 1
        logged_error = error_handler.error_history[0]
        
        # Verificar campos principales (sin comparar timestamp exacto)
        assert logged_error["type"] == "TestError"
        assert logged_error["message"] == "Test error message"
        assert logged_error["context"] == "test"
        assert logged_error["category"] == "data_loading"
        assert logged_error["specific_category"] == "file_not_found"
        assert "timestamp" in logged_error  # Solo verificar que existe
        
        log.debug("Error loggeado correctamente")
    
    def test_get_error_statistics(self, error_handler):
        """Test: Estadísticas de errores."""
        log.info("Test: Estadísticas de errores")
        
        # Agregar algunos errores
        error_info1 = {
            "type": "TestError1",
            "message": "Test error 1",
            "category": "data_loading",
            "timestamp": "2025-01-27 10:00:00",
            "stack_trace": "Test stack trace 1"
        }
        error_info2 = {
            "type": "TestError2", 
            "message": "Test error 2",
            "category": "analysis",
            "timestamp": "2025-01-27 10:01:00",
            "stack_trace": "Test stack trace 2"
        }
        
        error_handler.error_history = [error_info1, error_info2]
        
        stats = error_handler.get_error_statistics()
        
        assert isinstance(stats, dict)
        assert "total_errors" in stats
        assert "errors_by_category" in stats
        assert "errors_by_type" in stats
        assert stats["total_errors"] == 2
        
        # Verificar que las categorías están presentes
        assert "data_loading" in stats["errors_by_category"]
        assert "analysis" in stats["errors_by_category"]
        assert "TestError1" in stats["errors_by_type"]
        assert "TestError2" in stats["errors_by_type"]
        
        log.debug("Estadísticas de errores obtenidas correctamente")
    
    def test_clear_error_history(self, error_handler):
        """Test: Limpieza del historial de errores."""
        log.info("Test: Limpieza del historial de errores")
        
        # Agregar errores
        error_handler.error_history = [{"type": "TestError", "message": "Test"}]
        error_handler.error_counts = {"TestError": 1}
        
        # Limpiar historial
        error_handler.clear_error_history()
        
        assert len(error_handler.error_history) == 0
        assert len(error_handler.error_counts) == 0
        
        log.debug("Historial de errores limpiado correctamente")


# Configurar logging para tests
import logging
log = logging.getLogger(__name__)


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ejecutar tests
    pytest.main([__file__, "-v"]) 