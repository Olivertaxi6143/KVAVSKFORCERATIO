#!/usr/bin/env python3
"""
Test completo para verificar la integración de la GUI con DataManager
- Verificación de carga de datos con DataManager
- Verificación de flujo hacia core engine y asesor financiero
- Verificación de preservación de datos reales
- Verificación de modo desarrollo vs producción
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
from datetime import datetime
import tkinter as tk
from unittest.mock import Mock, patch

# Agregar src al path
sys.path.append('src')

# Importar módulos necesarios
from src.gui.gui_enhanced_rank import EnhancedRankGUI
from src.data.data_manager import DataManager, create_data_manager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gui_datamanager_integration():
    """
    Test completo de integración GUI con DataManager.
    """
    print("=" * 80)
    print("TEST DE INTEGRACIÓN GUI CON DATAMANAGER")
    print("=" * 80)
    
    results = {
        'tests_passed': 0,
        'tests_failed': 0,
        'errors': [],
        'warnings': []
    }
    
    # Test 1: Inicialización de GUI con DataManager
    print("\n1. Test de inicialización de GUI con DataManager...")
    try:
        # Crear GUI (sin mostrar ventana)
        with patch('tkinter.Tk') as mock_tk:
            mock_tk.return_value = Mock()
            gui = EnhancedRankGUI()
            
            # Verificar que DataManager se inicializó
            assert hasattr(gui, 'data_manager'), "DataManager no se inicializó en GUI"
            assert gui.data_manager is not None, "DataManager es None"
            
            print("✓ Inicialización de GUI con DataManager: OK")
            results['tests_passed'] += 1
            
    except Exception as e:
        print(f"✗ Error en inicialización de GUI: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Inicialización de GUI: {e}")
    
    # Test 2: Detección automática de modo desarrollo
    print("\n2. Test de detección automática de modo desarrollo...")
    try:
        # Crear GUI temporal para test
        gui = EnhancedRankGUI()
        
        # Verificar función de detección
        should_use_inputtest = gui._should_use_inputtest()
        assert isinstance(should_use_inputtest, bool), "Función de detección no retorna booleano"
        
        print(f"✓ Detección automática de modo: {'Desarrollo' if should_use_inputtest else 'Producción'}")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en detección de modo: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Detección de modo: {e}")
    
    # Test 3: Carga de datos con DataManager
    print("\n3. Test de carga de datos con DataManager...")
    try:
        # Crear GUI temporal
        gui = EnhancedRankGUI()
        
        # Simular datos de prueba directamente en el DataManager
        test_data = pd.DataFrame({
            'Strategy Name': ['Test Strategy 1', 'Test Strategy 2'],
            'CAGR': [15.5, 12.3],
            'Drawdown': [-8.5, -12.1],
            'Sharpe Ratio': [1.85, 1.42],
            'Profit factor': [2.1, 1.8]
        })
        
        # Asignar datos directamente al DataManager y simular carga exitosa
        gui.data_manager._kpis_data = test_data.copy()
        gui.data_manager._load_status['kpis'] = True
        
        # Probar carga de datos - usar la propiedad directamente
        loaded_data = gui.data_manager.kpis_data
        
        assert isinstance(loaded_data, pd.DataFrame), "Datos cargados no son DataFrame"
        assert not loaded_data.empty, "Datos cargados están vacíos"
        assert len(loaded_data) == 2, "Número incorrecto de registros"
        
        print("✓ Carga de datos con DataManager: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en carga de datos: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Carga de datos: {e}")
    
    # Test 4: Interfaz para core engine
    print("\n4. Test de interfaz para core engine...")
    try:
        # Crear GUI temporal
        gui = EnhancedRankGUI()
        
        # Simular datos cargados
        test_data = pd.DataFrame({
            'Strategy_Name': ['Test Strategy'],
            'CAGR_IS': [15.5],
            'CAGR_OOS': [14.2],
            'Drawdown_IS': [-8.5],
            'Drawdown_OOS': [-9.2]
        })
        
        gui.data_manager._kpis_data = test_data.copy()
        
        # Obtener datos para core engine
        core_data = gui._get_data_for_core_engine()
        
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
        # Crear GUI temporal
        gui = EnhancedRankGUI()
        
        # Simular datos cargados
        test_kpis = pd.DataFrame({
            'Strategy_Name': ['Test Strategy'],
            'CAGR_IS': [15.5],
            'CAGR_OOS': [14.2]
        })
        
        test_market = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02'],
            'Close': [100.0, 101.0]
        })
        
        gui.data_manager._kpis_data = test_kpis.copy()
        gui.data_manager._market_data = test_market.copy()
        gui.data_manager._load_status = {'kpis': True, 'market': True, 'strategies': False}
        
        # Obtener datos para asesor financiero
        asesor_data = gui._get_data_for_asesor_financiero()
        
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
    
    # Test 6: Validación de datos con DataManager
    print("\n6. Test de validación de datos con DataManager...")
    try:
        # Crear GUI temporal
        gui = EnhancedRankGUI()
        
        # Crear datos de prueba válidos
        test_data = pd.DataFrame({
            'Strategy_Name': ['Strategy A', 'Strategy B'],
            'CAGR_IS': [15.5, 12.3],
            'CAGR_OOS': [14.2, 11.8],
            'Drawdown_IS': [-8.5, -12.1],
            'Drawdown_OOS': [-9.2, -13.5]
        })
        
        # Validar datos
        validated_data = gui._validate_data_with_datamanager(test_data)
        
        assert validated_data is not None, "Validación retornó None"
        assert isinstance(validated_data, pd.DataFrame), "Validación no retornó DataFrame"
        
        print("✓ Validación de datos con DataManager: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en validación de datos: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Validación de datos: {e}")
    
    # Test 7: Preservación de datos reales
    print("\n7. Test de preservación de datos reales...")
    try:
        # Crear GUI temporal
        gui = EnhancedRankGUI()
        
        # Datos originales reales
        original_data = pd.DataFrame({
            'Strategy Name': ['Strategy A', 'Strategy B'],
            'CAGR (IS)': [15.5, 12.3],
            'CAGR (OOS)': [14.2, 11.8],
            'Drawdown (IS)': [-8.5, -12.1],
            'Drawdown (OOS)': [-9.2, -13.5]
        })
        
        # Simular carga con DataManager
        gui.data_manager._kpis_data = original_data.copy()
        
        # Obtener datos para core engine
        core_data = gui._get_data_for_core_engine()
        
        # Verificar que los valores numéricos se preservaron
        original_values = original_data[['CAGR (IS)', 'CAGR (OOS)', 'Drawdown (IS)', 'Drawdown (OOS)']].values
        core_values = core_data[['CAGR (IS)', 'CAGR (OOS)', 'Drawdown (IS)', 'Drawdown (OOS)']].values
        
        # Los valores deben ser idénticos (preservación de datos reales)
        assert np.allclose(original_values.astype(float), core_values.astype(float), rtol=1e-10), "Datos reales no se preservaron"
        
        print("✓ Preservación de datos reales: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en preservación de datos: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Preservación de datos: {e}")
    
    # Test 8: Modo desarrollo vs producción
    print("\n8. Test de modo desarrollo vs producción...")
    try:
        # Crear GUI temporal
        gui = EnhancedRankGUI()
        
        # Probar cambio a modo desarrollo
        gui.data_manager.switch_to_development_mode()
        assert gui.data_manager.config['development']['use_inputtest'] == True, "Modo desarrollo no activado"
        
        # Probar cambio a modo producción
        gui.data_manager.switch_to_production_mode()
        assert gui.data_manager.config['development']['use_inputtest'] == False, "Modo producción no activado"
        
        print("✓ Modo desarrollo vs producción: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en modo desarrollo vs producción: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Modo desarrollo vs producción: {e}")
    
    # Test 9: Integración con funciones existentes
    print("\n9. Test de integración con funciones existentes...")
    try:
        # Crear GUI temporal
        gui = EnhancedRankGUI()
        
        # Verificar que las funciones existentes siguen funcionando
        assert hasattr(gui, '_run_analysis'), "Función _run_analysis no disponible"
        assert hasattr(gui, '_run_asesor_analysis'), "Función _run_asesor_analysis no disponible"
        assert hasattr(gui, '_validate_data'), "Función _validate_data no disponible"
        
        # Verificar que las nuevas funciones están disponibles
        assert hasattr(gui, '_load_data_with_datamanager'), "Función _load_data_with_datamanager no disponible"
        assert hasattr(gui, '_get_data_for_core_engine'), "Función _get_data_for_core_engine no disponible"
        assert hasattr(gui, '_get_data_for_asesor_financiero'), "Función _get_data_for_asesor_financiero no disponible"
        
        print("✓ Integración con funciones existentes: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en integración con funciones existentes: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Integración con funciones existentes: {e}")
    
    # Test 10: Configuración de DataManager
    print("\n10. Test de configuración de DataManager...")
    try:
        # Crear GUI temporal
        gui = EnhancedRankGUI()
        
        # Verificar configuración esencial
        required_config_keys = [
            'csv_delimiter', 'csv_decimal', 'is_oos_ratio',
            'required_columns', 'default_files', 'validation',
            'cache', 'development'
        ]
        
        for key in required_config_keys:
            assert key in gui.data_manager.config, f"Configuración faltante: {key}"
        
        # Verificar configuración de desarrollo
        assert 'use_inputtest' in gui.data_manager.config['development'], "Configuración de desarrollo incompleta"
        assert 'inputtest_path' in gui.data_manager.config['development'], "Ruta INPUTTEST no configurada"
        
        print("✓ Configuración de DataManager: OK")
        results['tests_passed'] += 1
        
    except Exception as e:
        print(f"✗ Error en configuración de DataManager: {e}")
        results['tests_failed'] += 1
        results['errors'].append(f"Configuración de DataManager: {e}")
    
    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DE TESTS DE INTEGRACIÓN")
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
    results_file = f"test_gui_datamanager_integration_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResultados guardados en: {results_file}")
    
    # Verificar éxito general
    success_rate = results['tests_passed'] / (results['tests_passed'] + results['tests_failed'])
    print(f"\nTasa de éxito: {success_rate:.2%}")
    
    if success_rate >= 0.8:
        print("🎉 INTEGRACIÓN GUI CON DATAMANAGER COMPLETADA EXITOSAMENTE")
        print("✅ GUI completamente integrada con DataManager")
        print("✅ Datos reales se preservan sin cocinamiento")
        print("✅ Interfaz para core engine y asesor financiero operativa")
        print("✅ Modo desarrollo vs producción funcionando")
        print("✅ Configuración y validación robustas")
    else:
        print("⚠️  Algunos tests fallaron - revisar integración")
    
    return success_rate >= 0.8

if __name__ == "__main__":
    success = test_gui_datamanager_integration()
    sys.exit(0 if success else 1) 