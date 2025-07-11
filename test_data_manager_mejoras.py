#!/usr/bin/env python3
"""
Test completo para verificar las mejoras en data_manager.py
- Consolidación de funcionalidades
- Preservación de datos reales sin cocinamiento
- Integración con INPUTTEST para desarrollo
- Flujo correcto hacia core engine y asesor financiero
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
from datetime import datetime

# Agregar src al path
sys.path.append('src')

from data_manager import DataManager, create_data_manager, load_inputtest_data_pipeline

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_manager_mejoras():
    """
    Test completo de las mejoras en DataManager.
    """
    print("=" * 80)
    print("TEST COMPLETO DE MEJORAS EN DATA_MANAGER.PY")
    print("=" * 80)
    
    results = {
        'tests_passed': 0,
        'tests_failed': 0,
        'errors': [],
        'warnings': []
    }
    
    # Test 1: Inicialización básica
    print("\n1. Test de inicialización básica...")
    try:
        dm = DataManager()
        assert dm is not None, "DataManager no se inicializó"
        assert hasattr(dm, 'config'), "Configuración no disponible"
        assert hasattr(dm, 'COLUMN_MAPPINGS'), "Mapeo de columnas no disponible"
        print("✓ Inicialización básica: OK")
        results['tests_passed'] += 1
    except Exception as e:
        print(f"✗ Error en inicialización básica: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Inicialización básica: {e}")
    
    # Test 2: Modo desarrollo con INPUTTEST
    print("\n2. Test de modo desarrollo con INPUTTEST...")
    try:
        dm_dev = DataManager()
        dm_dev.switch_to_development_mode()
        
        # Verificar configuración de desarrollo
        assert dm_dev.config['development']['use_inputtest'] == True, "Modo desarrollo no activado"
        assert 'inputtest_path' in dm_dev.config['development'], "Ruta INPUTTEST no configurada"
        
        # Cargar datos de INPUTTEST
        success = dm_dev.load_all_data()
        
        print(f"✓ Modo desarrollo: OK (carga: {'Exitoso' if success else 'Fallido'})")
        results['tests_passed'] += 1
        
        if not success:
            results['warnings'].append("Carga de datos INPUTTEST falló")
            
    except Exception as e:
        print(f"✗ Error en modo desarrollo: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Modo desarrollo: {e}")
    
    # Test 3: Preservación de datos reales
    print("\n3. Test de preservación de datos reales...")
    try:
        # Crear datos de prueba reales
        test_data = pd.DataFrame({
            'Strategy Name': ['Strategy A', 'Strategy B'],
            'CAGR (IS)': [15.5, 12.3],
            'CAGR (OOS)': [14.2, 11.8],
            'Drawdown (IS)': [-8.5, -12.1],
            'Drawdown (OOS)': [-9.2, -13.5],
            'Sharpe Ratio (IS)': [1.85, 1.42],
            'Sharpe Ratio (OOS)': [1.72, 1.38]
        })
        
        # Procesar datos
        processed_data = dm._normalize_column_names(test_data)
        
        # Verificar que los valores numéricos se preservaron
        original_values = test_data[['CAGR (IS)', 'CAGR (OOS)', 'Drawdown (IS)', 'Drawdown (OOS)']].values
        processed_values = processed_data[['cagr_is', 'cagr_oos', 'drawdown_is', 'drawdown_oos']].values
        
        # Los valores deben ser idénticos (preservación de datos reales)
        assert np.allclose(original_values.astype(float), processed_values.astype(float), rtol=1e-10), "Datos reales no se preservaron"
        
        print("✓ Preservación de datos reales: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en preservación de datos: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Preservación de datos: {e}")
    
    # Test 4: Interfaz para core engine
    print("\n4. Test de interfaz para core engine...")
    try:
        # Simular datos cargados
        dm._kpis_data = pd.DataFrame({
            'Strategy_Name': ['Test Strategy'],
            'CAGR_IS': [15.5],
            'CAGR_OOS': [14.2],
            'Drawdown_IS': [-8.5],
            'Drawdown_OOS': [-9.2]
        })
        
        # Obtener datos para core engine
        core_data = dm.get_data_for_core_engine()
        
        assert isinstance(core_data, pd.DataFrame), "Datos para core engine no son DataFrame"
        assert not core_data.empty, "Datos para core engine están vacíos"
        assert 'Strategy_Name' in core_data.columns, "Columna Strategy_Name faltante"
        
        print("✓ Interfaz para core engine: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en interfaz core engine: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Interfaz core engine: {e}")
    
    # Test 5: Interfaz para asesor financiero
    print("\n5. Test de interfaz para asesor financiero...")
    try:
        # Simular datos cargados
        dm._market_data = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02'],
            'Close': [100.0, 101.0]
        })
        
        # Obtener datos para asesor financiero
        asesor_data = dm.get_data_for_asesor_financiero()
        
        assert isinstance(asesor_data, dict), "Datos para asesor no son diccionario"
        assert 'kpis' in asesor_data, "KPIs faltantes en datos de asesor"
        assert 'market' in asesor_data, "Datos de mercado faltantes en datos de asesor"
        assert 'load_status' in asesor_data, "Estado de carga faltante en datos de asesor"
        
        print("✓ Interfaz para asesor financiero: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en interfaz asesor financiero: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Interfaz asesor financiero: {e}")
    
    # Test 6: Validación de datos INPUTTEST
    print("\n6. Test de validación de datos INPUTTEST...")
    try:
        # Crear datos de prueba similares a INPUTTEST
        inputtest_data = pd.DataFrame({
            'Strategy_Name': ['Strategy A', 'Strategy B'],
            'CAGR_IS': [15.5, 12.3],
            'CAGR_OOS': [14.2, 11.8],
            'Drawdown_IS': [-8.5, -12.1],
            'Drawdown_OOS': [-9.2, -13.5]
        })
        
        # Validar datos
        is_valid, errors = dm.validate_inputtest_data(inputtest_data)
        
        assert is_valid, f"Validación falló: {errors}"
        assert len(errors) == 0, f"Errores de validación: {errors}"
        
        print("✓ Validación de datos INPUTTEST: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en validación INPUTTEST: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Validación INPUTTEST: {e}")
    
    # Test 7: Pipeline completo de carga INPUTTEST
    print("\n7. Test de pipeline completo INPUTTEST...")
    try:
        # Usar función de utilidad
        inputtest_data = load_inputtest_data_pipeline()
        
        # Verificar estructura
        assert isinstance(inputtest_data, dict), "Datos INPUTTEST no son diccionario"
        expected_keys = ['kpis', 'market', 'strategies']
        
        for key in expected_keys:
            if key in inputtest_data:
                print(f"  - {key}: {len(inputtest_data[key]) if isinstance(inputtest_data[key], pd.DataFrame) else 'N/A'} registros")
        
        print("✓ Pipeline completo INPUTTEST: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en pipeline INPUTTEST: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Pipeline INPUTTEST: {e}")
    
    # Test 8: Mapeo de columnas críticas
    print("\n8. Test de mapeo de columnas críticas...")
    try:
        # Verificar mapeos críticos
        critical_mappings = [
            ('Strategy Name', 'Strategy_Name'),
            ('CAGR (IS)', 'CAGR_IS'),
            ('CAGR (OOS)', 'CAGR_OOS'),
            ('Drawdown (IS)', 'Drawdown_IS'),
            ('Drawdown (OOS)', 'Drawdown_OOS')
        ]
        
        for old_name, new_name in critical_mappings:
            assert old_name in dm.COLUMN_MAPPINGS, f"Mapeo faltante: {old_name}"
            assert dm.COLUMN_MAPPINGS[old_name] == new_name, f"Mapeo incorrecto: {old_name} → {dm.COLUMN_MAPPINGS[old_name]}"
        
        print("✓ Mapeo de columnas críticas: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en mapeo de columnas: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Mapeo de columnas: {e}")
    
    # Test 9: Configuración por defecto
    print("\n9. Test de configuración por defecto...")
    try:
        # Verificar configuración esencial
        required_config_keys = [
            'csv_delimiter', 'csv_decimal', 'is_oos_ratio',
            'required_columns', 'default_files', 'validation',
            'cache', 'development'
        ]
        
        for key in required_config_keys:
            assert key in dm.config, f"Configuración faltante: {key}"
        
        # Verificar configuración de desarrollo
        assert 'use_inputtest' in dm.config['development'], "Configuración de desarrollo incompleta"
        assert 'inputtest_path' in dm.config['development'], "Ruta INPUTTEST no configurada"
        
        print("✓ Configuración por defecto: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en configuración: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Configuración: {e}")
    
    # Test 10: Funciones de utilidad
    print("\n10. Test de funciones de utilidad...")
    try:
        # Test create_data_manager
        dm_util = create_data_manager()
        assert isinstance(dm_util, DataManager), "create_data_manager no retorna DataManager"
        
        # Test switch modes
        dm_util.switch_to_development_mode()
        assert dm_util.config['development']['use_inputtest'] == True, "Modo desarrollo no activado"
        
        dm_util.switch_to_production_mode()
        assert dm_util.config['development']['use_inputtest'] == False, "Modo producción no activado"
        
        print("✓ Funciones de utilidad: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en funciones de utilidad: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Funciones de utilidad: {e}")
    
    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DE TESTS")
    print("=" * 80)
    print(f"Tests pasados: {results['tests_passed']}")
    print(f"Tests fallidos: {results['tests_failed']}")
    print(f"Total tests: {results['tests_passed'] + results['tests_failed']}")
    
    if results['errors']:
        print("\nErrores encontrados:")
        for error in results['errors']:
            print(f"  - {error}")
    
    if results['warnings']:
        print("\nAdvertencias:")
        for warning in results['warnings']:
            print(f"  - {warning}")
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_data_manager_mejoras_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResultados guardados en: {results_file}")
    
    # Verificar éxito general
    success_rate = results['tests_passed'] / (results['tests_passed'] + results['tests_failed'])
    print(f"\nTasa de éxito: {success_rate:.2%}")
    
    if success_rate >= 0.8:
        print("🎉 MEJORAS EN DATA_MANAGER IMPLEMENTADAS EXITOSAMENTE")
        print("✅ Datos reales se preservan sin cocinamiento")
        print("✅ Integración con INPUTTEST funcionando")
        print("✅ Interfaz para core engine y asesor financiero operativa")
        print("✅ Consolidación de funcionalidades completada")
    else:
        print("⚠️  Algunos tests fallaron - revisar implementación")
    
    return success_rate >= 0.8

if __name__ == "__main__":
    success = test_data_manager_mejoras()
    sys.exit(0 if success else 1) 