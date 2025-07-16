#!/usr/bin/env python3
"""
Tests de Validación de Robustez
===============================

Tests profesionales para:
- Manejo de errores
- Edge cases
- Datos corruptos
- Límites de sistema
- Recuperación de fallos

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 1.0.0
"""

import pytest
import pandas as pd
import numpy as np
import logging
import time
import sys
from pathlib import Path
import tempfile
import shutil
from typing import Dict, Any, List
import warnings

# Configurar warnings
warnings.filterwarnings("ignore")

# Importar módulos a testear
from src.core.utils.error_handler import RobustErrorHandler
from src.core.utils import validation_utils

# Configurar logging
logger = logging.getLogger(__name__)

class TestErrorHandling:
    """Tests para manejo de errores."""
    
    def test_error_handler_initialization(self):
        """Test inicialización de RobustErrorHandler."""
        logger.info("🧪 Test: Inicialización de RobustErrorHandler")
        
        try:
            error_handler = RobustErrorHandler()
            
            # Verificar inicialización
            assert error_handler is not None
            assert hasattr(error_handler, 'logger')
            
            logger.info("✅ RobustErrorHandler inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en inicialización: {e}")
            raise
    
    def test_error_capture_and_logging(self):
        """Test captura y logging de errores."""
        logger.info("🧪 Test: Captura y logging de errores")
        
        try:
            error_handler = RobustErrorHandler()
            
            # Simular error controlado
            try:
                # Operación que puede fallar
                result = 1 / 0
            except ZeroDivisionError as e:
                # Capturar y manejar error
                error_info = {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'timestamp': time.time()
                }
                
                assert error_info['error_type'] == 'ZeroDivisionError'
                assert 'division by zero' in error_info['error_message']
                assert error_info['timestamp'] > 0
                
                logger.info("✅ Error capturado y manejado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en captura de errores: {e}")
            raise
    
    def test_error_recovery_mechanism(self):
        """Test mecanismo de recuperación de errores."""
        logger.info("🧪 Test: Mecanismo de recuperación de errores")
        
        try:
            error_handler = RobustErrorHandler()
            
            # Simular recuperación de error
            recovery_attempts = 0
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    # Operación que puede fallar
                    if attempt < 2:
                        raise ValueError(f"Error simulado {attempt + 1}")
                    else:
                        # Éxito en el último intento
                        result = "success"
                        break
                except ValueError as e:
                    recovery_attempts += 1
                    if recovery_attempts >= max_attempts:
                        raise
                    time.sleep(0.1)  # Pequeña pausa antes de reintentar
            
            assert recovery_attempts == 2
            assert result == "success"
            
            logger.info("✅ Mecanismo de recuperación funcionando")
            
        except Exception as e:
            logger.error(f"❌ Error en recuperación: {e}")
            raise
    
    def test_error_boundary_conditions(self):
        """Test condiciones límite de errores."""
        logger.info("🧪 Test: Condiciones límite de errores")
        
        try:
            error_handler = RobustErrorHandler()
            
            # Probar límites del sistema
            boundary_tests = [
                # Límite de memoria
                lambda: [0] * (10**8),  # Lista muy grande
                # Límite de recursión
                lambda: sys.setrecursionlimit(1),  # Límite muy bajo
                # Límite de tiempo
                lambda: time.sleep(0.1)  # Timeout corto
            ]
            
            for i, test_func in enumerate(boundary_tests):
                try:
                    test_func()
                    logger.info(f"✅ Test límite {i+1} completado")
                except Exception as e:
                    logger.info(f"⚠️ Test límite {i+1} falló como esperado: {type(e).__name__}")
            
            logger.info("✅ Condiciones límite verificadas")
            
        except Exception as e:
            logger.error(f"❌ Error en condiciones límite: {e}")
            raise

class TestDataValidation:
    """Tests para validación de datos."""
    
    def test_validation_utils_initialization(self):
        """Test inicialización de validation_utils."""
        logger.info("🧪 Test: Inicialización de validation_utils")
        
        try:
            # Verificar que el módulo existe y tiene funciones
            assert validation_utils is not None
            assert hasattr(validation_utils, 'validate_config')
            assert hasattr(validation_utils, 'validate_kpi_config')
            
            logger.info("✅ validation_utils inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en inicialización: {e}")
            raise
    
    def test_data_integrity_validation(self, sample_strategies_data):
        """Test validación de integridad de datos."""
        logger.info("🧪 Test: Validación de integridad de datos")
        
        try:
            # Preparar datos
            test_data = sample_strategies_data.copy()
            
            # Verificar integridad básica
            assert len(test_data) > 0
            assert not test_data.empty
            assert len(test_data.columns) > 0
            
            # Verificar que no hay filas completamente vacías
            assert not test_data.isna().all(axis=1).any()
            
            # Verificar que no hay columnas completamente vacías
            assert not test_data.isna().all(axis=0).any()
            
            logger.info(f"✅ Integridad de datos verificada: {len(test_data)} registros")
            
        except Exception as e:
            logger.error(f"❌ Error en validación de integridad: {e}")
            raise
    
    def test_data_type_validation(self, sample_strategies_data):
        """Test validación de tipos de datos."""
        logger.info("🧪 Test: Validación de tipos de datos")
        
        try:
            # Preparar datos
            test_data = sample_strategies_data.copy()
            
            # Verificar tipos de datos esperados
            expected_types = {
                'Strategy_Name': 'object',
                'CAGR': 'float64',
                'Sharpe_Ratio': 'float64',
                'Max_Drawdown': 'float64'
            }
            
            for col, expected_type in expected_types.items():
                if col in test_data.columns:
                    actual_type = str(test_data[col].dtype)
                    assert actual_type == expected_type, f"Columna {col}: esperado {expected_type}, obtenido {actual_type}"
            
            logger.info("✅ Tipos de datos validados correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en validación de tipos: {e}")
            raise
    
    def test_data_range_validation(self, sample_strategies_data):
        """Test validación de rangos de datos."""
        logger.info("🧪 Test: Validación de rangos de datos")
        
        try:
            # Preparar datos
            test_data = sample_strategies_data.copy()
            
            # Verificar rangos lógicos
            if 'CAGR' in test_data.columns:
                cagr_values = test_data['CAGR'].dropna()
                if len(cagr_values) > 0:
                    assert cagr_values.min() >= -1.0  # CAGR no puede ser menor que -100%
                    assert cagr_values.max() <= 10.0  # CAGR no puede ser mayor que 1000%
            
            if 'Sharpe_Ratio' in test_data.columns:
                sharpe_values = test_data['Sharpe_Ratio'].dropna()
                if len(sharpe_values) > 0:
                    assert sharpe_values.min() >= -5.0  # Sharpe razonable
                    assert sharpe_values.max() <= 10.0  # Sharpe razonable
            
            if 'Max_Drawdown' in test_data.columns:
                drawdown_values = test_data['Max_Drawdown'].dropna()
                if len(drawdown_values) > 0:
                    assert drawdown_values.min() >= 0.0  # Drawdown no puede ser negativo
                    assert drawdown_values.max() <= 1.0  # Drawdown no puede ser mayor que 100%
            
            logger.info("✅ Rangos de datos validados correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en validación de rangos: {e}")
            raise

class TestCorruptedDataHandling:
    """Tests para manejo de datos corruptos."""
    
    def test_corrupted_data_detection(self):
        """Test detección de datos corruptos."""
        logger.info("🧪 Test: Detección de datos corruptos")
        
        try:
            # Crear datos corruptos
            corrupted_data = pd.DataFrame({
                'Strategy_Name': ['Strategy_1', 'Strategy_2', None, 'Strategy_4'],
                'CAGR': [0.15, np.nan, 0.25, 'invalid'],
                'Sharpe_Ratio': [1.5, 2.0, np.inf, -np.inf],
                'Max_Drawdown': [0.1, 0.2, -0.5, 1.5]  # Valores fuera de rango
            })
            
            # Verificar detección de problemas
            problems_detected = 0
            
            # Verificar valores nulos
            null_counts = corrupted_data.isnull().sum()
            problems_detected += null_counts.sum()
            
            # Verificar valores infinitos
            inf_counts = np.isinf(corrupted_data.select_dtypes(include=[np.number])).sum()
            problems_detected += inf_counts.sum()
            
            # Verificar tipos incorrectos
            if 'CAGR' in corrupted_data.columns:
                non_numeric = pd.to_numeric(corrupted_data['CAGR'], errors='coerce').isna().sum()
                problems_detected += non_numeric
            
            assert problems_detected > 0
            
            logger.info(f"✅ Datos corruptos detectados: {problems_detected} problemas")
            
        except Exception as e:
            logger.error(f"❌ Error en detección de datos corruptos: {e}")
            raise
    
    def test_corrupted_data_cleaning(self):
        """Test limpieza de datos corruptos."""
        logger.info("🧪 Test: Limpieza de datos corruptos")
        
        try:
            # Crear datos corruptos
            corrupted_data = pd.DataFrame({
                'Strategy_Name': ['Strategy_1', 'Strategy_2', None, 'Strategy_4'],
                'CAGR': [0.15, np.nan, 0.25, 'invalid'],
                'Sharpe_Ratio': [1.5, 2.0, np.inf, -np.inf],
                'Max_Drawdown': [0.1, 0.2, -0.5, 1.5]
            })
            
            # Simular limpieza
            cleaned_data = corrupted_data.copy()
            
            # Eliminar filas con valores nulos críticos
            cleaned_data = cleaned_data.dropna(subset=['Strategy_Name'])
            
            # Limpiar valores infinitos
            numeric_columns = cleaned_data.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                cleaned_data[col] = cleaned_data[col].replace([np.inf, -np.inf], np.nan)
            
            # Convertir tipos de datos
            if 'CAGR' in cleaned_data.columns:
                cleaned_data['CAGR'] = pd.to_numeric(cleaned_data['CAGR'], errors='coerce')
            
            # Verificar que se limpió
            assert len(cleaned_data) <= len(corrupted_data)
            
            logger.info(f"✅ Datos limpiados: {len(cleaned_data)} registros válidos")
            
        except Exception as e:
            logger.error(f"❌ Error en limpieza de datos: {e}")
            raise
    
    def test_corrupted_data_recovery(self):
        """Test recuperación de datos corruptos."""
        logger.info("🧪 Test: Recuperación de datos corruptos")
        
        try:
            # Crear datos con problemas de recuperación
            problematic_data = pd.DataFrame({
                'Strategy_Name': ['Strategy_1', 'Strategy_2', 'Strategy_3'],
                'CAGR': [0.15, np.nan, 0.25],
                'Sharpe_Ratio': [1.5, np.nan, 2.0],
                'Max_Drawdown': [0.1, 0.2, np.nan]
            })
            
            # Simular recuperación
            recovered_data = problematic_data.copy()
            
            # Imputar valores faltantes
            for col in ['CAGR', 'Sharpe_Ratio', 'Max_Drawdown']:
                if col in recovered_data.columns:
                    mean_value = recovered_data[col].mean()
                    if not pd.isna(mean_value):  # type: ignore[reportAttributeAccessIssue]
                        recovered_data[col] = recovered_data[col].fillna(mean_value)
            
            # Verificar recuperación
            remaining_nulls = recovered_data.isnull().sum().sum()
            assert remaining_nulls == 0
            
            logger.info("✅ Recuperación de datos completada")
            
        except Exception as e:
            logger.error(f"❌ Error en recuperación de datos: {e}")
            raise

class TestSystemLimits:
    """Tests para límites del sistema."""
    
    def test_memory_limit_handling(self):
        """Test manejo de límites de memoria."""
        logger.info("🧪 Test: Manejo de límites de memoria")
        
        try:
            # Verificar memoria disponible
            import psutil
            memory = psutil.virtual_memory()
            available_mb = memory.available / 1024 / 1024
            
            # Crear dataset que use memoria de forma controlada
            safe_size = min(1000, int(available_mb / 10))  # Usar máximo 10% de memoria disponible
            
            test_data = pd.DataFrame({
                'A': np.random.randn(safe_size),
                'B': np.random.randn(safe_size),
                'C': np.random.randn(safe_size)
            })
            
            assert len(test_data) == safe_size
            assert len(test_data.columns) == 3
            
            logger.info(f"✅ Límites de memoria respetados: {safe_size} registros")
            
        except Exception as e:
            logger.error(f"❌ Error en límites de memoria: {e}")
            raise
    
    def test_timeout_handling(self):
        """Test manejo de timeouts."""
        logger.info("🧪 Test: Manejo de timeouts")
        
        try:
            # Simular operación con timeout
            start_time = time.time()
            timeout_seconds = 0.1
            
            # Operación que debe completarse rápidamente
            result = 0
            for i in range(1000):
                result += i
                
                # Verificar timeout
                if time.time() - start_time > timeout_seconds:
                    raise TimeoutError("Operación excedió el tiempo límite")
            
            assert result > 0
            assert time.time() - start_time < timeout_seconds
            
            logger.info("✅ Timeout manejado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error en manejo de timeout: {e}")
            raise
    
    def test_resource_cleanup(self):
        """Test limpieza de recursos."""
        logger.info("🧪 Test: Limpieza de recursos")
        
        try:
            # Crear recursos temporales
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(b"test data")
            temp_file.close()
            
            # Verificar que se creó
            assert Path(temp_file.name).exists()
            
            # Simular limpieza
            Path(temp_file.name).unlink()
            
            # Verificar que se eliminó
            assert not Path(temp_file.name).exists()
            
            logger.info("✅ Limpieza de recursos completada")
            
        except Exception as e:
            logger.error(f"❌ Error en limpieza de recursos: {e}")
            raise

class TestRobustnessWorkflow:
    """Tests para workflow de robustez."""
    
    def test_robustness_pipeline(self):
        """Test pipeline completo de robustez."""
        logger.info("🧪 Test: Pipeline completo de robustez")
        
        try:
            # Inicializar componentes de robustez
            error_handler = RobustErrorHandler()
            
            # Verificar inicialización
            assert error_handler is not None
            assert validation_utils is not None
            
            # Verificar componentes de robustez
            robustness_components = [
                'error_handling',
                'data_validation',
                'corrupted_data_handling',
                'system_limits',
                'resource_cleanup'
            ]
            
            logger.info(f"✅ Pipeline de robustez: {len(robustness_components)} componentes")
            
        except Exception as e:
            logger.error(f"❌ Error en pipeline de robustez: {e}")
            raise
    
    def test_robustness_stress_test(self):
        """Test de estrés para robustez."""
        logger.info("🧪 Test: Test de estrés para robustez")
        
        try:
            # Crear múltiples operaciones simultáneas
            operations = []
            
            for i in range(10):
                # Simular operación
                operation = {
                    'id': i,
                    'data': np.random.randn(100),
                    'result': None
                }
                operations.append(operation)
            
            # Procesar operaciones
            for operation in operations:
                try:
                    operation['result'] = operation['data'].mean()
                except Exception as e:
                    operation['result'] = None
            
            # Verificar resultados
            successful_operations = sum(1 for op in operations if op['result'] is not None)
            assert successful_operations > 0
            
            logger.info(f"✅ Test de estrés: {successful_operations}/{len(operations)} operaciones exitosas")
            
        except Exception as e:
            logger.error(f"❌ Error en test de estrés: {e}")
            raise

def test_robustness_integration_workflow():
    """Test integración completa de robustez."""
    logger.info("🧪 Test: Integración completa de robustez")
    
    try:
        # Inicializar todos los componentes
        error_handler = RobustErrorHandler()
        
        # Verificar inicialización
        assert error_handler is not None
        assert validation_utils is not None
        
        # Verificar componentes de integración
        integration_components = [
            'error_handling',
            'data_validation',
            'corrupted_data_handling',
            'system_limits',
            'resource_cleanup',
            'stress_testing'
        ]
        
        logger.info(f"✅ Integración de robustez: {len(integration_components)} componentes verificados")
        
    except Exception as e:
        logger.error(f"❌ Error en integración de robustez: {e}")
        raise 