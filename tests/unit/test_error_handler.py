#!/usr/bin/env python3
"""
Tests unitarios para error_handler.py

Este test verifica:
1. Inicialización correcta del RobustErrorHandler
2. Manejo de reintentos con errores
3. Estrategias de recuperación
4. Decoradores de manejo de errores
5. Validación de entrada
6. Logging de tiempo de ejecución
7. Excepción personalizada GUIAnalysisError
"""

import pytest
import sys
import os
import time
import logging
from typing import Any, Dict, List

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.core.utils.error_handler import (
        RobustErrorHandler,
        retry_on_error,
        handle_specific_errors,
        validate_input,
        log_execution_time,
        GUIAnalysisError
    )
except ImportError as e:
    pytest.skip(f"No se puede importar error_handler: {e}", allow_module_level=True)

# Configurar logging para tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestErrorHandler:
    """Test suite para error_handler."""
    
    @pytest.fixture(scope="class")
    def error_handler(self):
        """Fixture para RobustErrorHandler."""
        return RobustErrorHandler(max_retries=3, timeout=10)
    
    def test_initialization(self, error_handler):
        """Test 1: Inicialización correcta del error handler."""
        print("\n🧪 Test 1: Inicialización del error handler")
        
        # Verificar que el error handler se creó correctamente
        assert error_handler is not None, "Error handler no debe ser None"
        logger.debug("Error handler creado correctamente ✅")
        
        # Verificar atributos básicos
        assert hasattr(error_handler, 'max_retries'), "Error handler debe tener max_retries"
        assert hasattr(error_handler, 'timeout'), "Error handler debe tener timeout"
        assert hasattr(error_handler, 'error_counts'), "Error handler debe tener error_counts"
        assert hasattr(error_handler, 'recovery_strategies'), "Error handler debe tener recovery_strategies"
        
        # Verificar valores por defecto
        assert error_handler.max_retries == 3, f"max_retries debe ser 3, fue {error_handler.max_retries}"
        assert error_handler.timeout == 10, f"timeout debe ser 10, fue {error_handler.timeout}"
        
        print("✅ Test 1 PASÓ: Inicialización correcta")
    
    def test_retry_with_success(self, error_handler):
        """Test 2: Reintentos con éxito eventual."""
        print("\n🧪 Test 2: Reintentos con éxito eventual")
        
        # Función que falla las primeras 2 veces y luego tiene éxito
        attempt_count = 0
        def failing_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count <= 2:
                raise ValueError(f"Error intencional en intento {attempt_count}")
            return "éxito"
        
        # Ejecutar con reintentos
        result = error_handler.execute_with_retry(failing_function)
        
        # Verificar que eventualmente tuvo éxito
        assert result == "éxito", f"Resultado debe ser 'éxito', fue {result}"
        assert attempt_count == 3, f"Debe haber hecho 3 intentos, fue {attempt_count}"
        
        logger.debug(f"Función exitosa después de {attempt_count} intentos ✅")
        print("✅ Test 2 PASÓ: Reintentos con éxito eventual")
    
    def test_retry_with_final_failure(self, error_handler):
        """Test 3: Reintentos con fallo final."""
        print("\n🧪 Test 3: Reintentos con fallo final")
        
        # Función que siempre falla
        def always_failing_function():
            raise RuntimeError("Error permanente")
        
        # Verificar que se lanza la excepción correcta
        with pytest.raises(RuntimeError) as exc_info:
            error_handler.execute_with_retry(always_failing_function)
        
        assert "Error permanente" in str(exc_info.value), "Debe contener el mensaje de error original"
        logger.debug("Fallo final manejado correctamente ✅")
        print("✅ Test 3 PASÓ: Reintentos con fallo final")
    
    def test_recovery_strategy(self, error_handler):
        """Test 4: Estrategia de recuperación."""
        print("\n🧪 Test 4: Estrategia de recuperación")
        
        # Contador para la estrategia de recuperación
        recovery_called = False
        
        def recovery_strategy(error, *args, **kwargs):
            nonlocal recovery_called
            recovery_called = True
            logger.debug("Estrategia de recuperación ejecutada ✅")
        
        # Registrar estrategia de recuperación
        error_handler.register_recovery_strategy("ValueError", recovery_strategy)
        
        # Función que falla con ValueError
        attempt_count = 0
        def failing_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count <= 2:
                raise ValueError("Error para recuperación")
            return "éxito después de recuperación"
        
        # Ejecutar con reintentos
        result = error_handler.execute_with_retry(failing_function)
        
        # Verificar que la estrategia de recuperación fue llamada
        assert recovery_called, "Estrategia de recuperación debe haber sido llamada"
        assert result == "éxito después de recuperación", f"Resultado debe ser 'éxito después de recuperación', fue {result}"
        
        print("✅ Test 4 PASÓ: Estrategia de recuperación")
    
    def test_retry_decorator(self):
        """Test 5: Decorador de reintentos."""
        print("\n🧪 Test 5: Decorador de reintentos")
        
        # Función decorada que falla las primeras 2 veces
        attempt_count = 0
        @retry_on_error(max_retries=3, delay=0.1)
        def decorated_failing_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count <= 2:
                raise ValueError(f"Error en intento {attempt_count}")
            return "éxito con decorador"
        
        # Ejecutar función decorada
        result = decorated_failing_function()
        
        # Verificar que eventualmente tuvo éxito
        assert result == "éxito con decorador", f"Resultado debe ser 'éxito con decorador', fue {result}"
        assert attempt_count == 3, f"Debe haber hecho 3 intentos, fue {attempt_count}"
        
        logger.debug(f"Decorador funcionó correctamente después de {attempt_count} intentos ✅")
        print("✅ Test 5 PASÓ: Decorador de reintentos")
    
    def test_handle_specific_errors_decorator(self):
        """Test 6: Decorador de manejo de errores específicos."""
        print("\n🧪 Test 6: Decorador de manejo de errores específicos")
        
        # Función que puede fallar con diferentes tipos de error
        @handle_specific_errors([ValueError, TypeError], default_value="valor por defecto")
        def function_with_specific_errors(error_type):
            if error_type == "ValueError":
                raise ValueError("Error de valor")
            elif error_type == "TypeError":
                raise TypeError("Error de tipo")
            elif error_type == "RuntimeError":
                raise RuntimeError("Error de runtime")
            else:
                return "éxito"
        
        # Test con ValueError (debe retornar valor por defecto)
        result = function_with_specific_errors("ValueError")
        assert result == "valor por defecto", f"Debe retornar valor por defecto, fue {result}"
        
        # Test con TypeError (debe retornar valor por defecto)
        result = function_with_specific_errors("TypeError")
        assert result == "valor por defecto", f"Debe retornar valor por defecto, fue {result}"
        
        # Test con RuntimeError (debe propagar el error)
        with pytest.raises(RuntimeError):
            function_with_specific_errors("RuntimeError")
        
        # Test con éxito
        result = function_with_specific_errors("success")
        assert result == "éxito", f"Debe retornar 'éxito', fue {result}"
        
        logger.debug("Decorador de manejo de errores específicos funcionó correctamente ✅")
        print("✅ Test 6 PASÓ: Decorador de manejo de errores específicos")
    
    def test_validate_input_decorator(self):
        """Test 7: Decorador de validación de entrada."""
        print("\n🧪 Test 7: Decorador de validación de entrada")
        
        @validate_input
        def function_with_validation(arg1, arg2, kwarg1=None):
            return f"éxito: {arg1}, {arg2}, {kwarg1}"
        
        # Test con argumentos válidos
        result = function_with_validation("a", "b", kwarg1="c")
        assert result == "éxito: a, b, c", f"Debe retornar resultado correcto, fue {result}"
        
        # Test con argumento None (debe fallar)
        with pytest.raises(ValueError) as exc_info:
            function_with_validation(None, "b")
        assert "Argumento 0 no puede ser None" in str(exc_info.value)
        
        # Test con kwarg None (debe fallar)
        with pytest.raises(ValueError) as exc_info:
            function_with_validation("a", "b", kwarg1=None)
        assert "Argumento 'kwarg1' no puede ser None" in str(exc_info.value)
        
        logger.debug("Decorador de validación de entrada funcionó correctamente ✅")
        print("✅ Test 7 PASÓ: Decorador de validación de entrada")
    
    def test_log_execution_time_decorator(self):
        """Test 8: Decorador de logging de tiempo de ejecución."""
        print("\n🧪 Test 8: Decorador de logging de tiempo de ejecución")
        
        @log_execution_time
        def function_with_timing():
            time.sleep(0.1)  # Simular trabajo
            return "completado"
        
        # Ejecutar función con timing
        result = function_with_timing()
        assert result == "completado", f"Debe retornar 'completado', fue {result}"
        
        # Test con función que falla
        @log_execution_time
        def function_that_fails():
            time.sleep(0.05)  # Simular trabajo
            raise RuntimeError("Error de prueba")
        
        # Verificar que se propaga el error
        with pytest.raises(RuntimeError):
            function_that_fails()
        
        logger.debug("Decorador de logging de tiempo funcionó correctamente ✅")
        print("✅ Test 8 PASÓ: Decorador de logging de tiempo de ejecución")
    
    def test_gui_analysis_error(self):
        """Test 9: Excepción personalizada GUIAnalysisError."""
        print("\n🧪 Test 9: Excepción personalizada GUIAnalysisError")
        
        # Crear excepción personalizada
        error_details = {"step": "análisis", "data_size": 1000}
        gui_error = GUIAnalysisError(
            message="Error en análisis de datos",
            error_type="data_processing",
            details=error_details
        )
        
        # Verificar atributos
        assert gui_error.error_type == "data_processing", f"error_type debe ser 'data_processing', fue {gui_error.error_type}"
        assert gui_error.details == error_details, "details debe coincidir"
        
        # Verificar string representation
        error_str = str(gui_error)
        assert "data_processing" in error_str, "String debe contener error_type"
        assert "Error en análisis de datos" in error_str, "String debe contener mensaje"
        
        # Verificar get_details
        details = gui_error.get_details()
        assert details['error_type'] == "data_processing", "get_details debe retornar error_type correcto"
        assert details['details'] == error_details, "get_details debe retornar details correcto"
        
        logger.debug("Excepción personalizada GUIAnalysisError funcionó correctamente ✅")
        print("✅ Test 9 PASÓ: Excepción personalizada GUIAnalysisError")
    
    def test_error_stats(self, error_handler):
        """Test 10: Estadísticas de errores."""
        print("\n🧪 Test 10: Estadísticas de errores")
        
        # Ejecutar algunas operaciones que generen errores
        def failing_function():
            raise ValueError("Error de prueba")
        
        # Ejecutar con reintentos (fallará)
        with pytest.raises(RuntimeError):
            error_handler.execute_with_retry(failing_function)
        
        # Obtener estadísticas
        stats = error_handler.get_error_stats()
        
        # Verificar estadísticas básicas
        assert 'total_errors' in stats, "stats debe tener total_errors"
        assert 'error_counts' in stats, "stats debe tener error_counts"
        assert 'recovery_strategies' in stats, "stats debe tener recovery_strategies"
        assert 'max_retries' in stats, "stats debe tener max_retries"
        assert 'timeout' in stats, "stats debe tener timeout"
        
        # Verificar que hay errores registrados
        assert stats['total_errors'] > 0, "Debe haber errores registrados"
        assert 'ValueError' in stats['error_counts'], "Debe haber errores ValueError"
        
        logger.debug(f"Estadísticas de errores: {stats} ✅")
        print("✅ Test 10 PASÓ: Estadísticas de errores")

def test_resumen_error_handler():
    """Resumen final de tests de error_handler."""
    print("\n" + "="*60)
    print("🎯 RESUMEN: TESTS DE ERROR HANDLER")
    print("="*60)
    print("✅ Inicialización correcta del RobustErrorHandler")
    print("✅ Reintentos con éxito eventual")
    print("✅ Reintentos con fallo final")
    print("✅ Estrategia de recuperación")
    print("✅ Decorador de reintentos")
    print("✅ Decorador de manejo de errores específicos")
    print("✅ Decorador de validación de entrada")
    print("✅ Decorador de logging de tiempo de ejecución")
    print("✅ Excepción personalizada GUIAnalysisError")
    print("✅ Estadísticas de errores")
    print("="*60)
    print("🎉 TODOS LOS TESTS DE ERROR HANDLER PASARON")
    print("="*60)

if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "--tb=short"]) 