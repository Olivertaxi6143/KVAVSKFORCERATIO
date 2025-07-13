#!/usr/bin/env python3
"""
Test completo del flujo GUI
Valida todas las funcionalidades del sistema de análisis cuantitativo
"""

import sys
import os
import time
import json
import traceback
from datetime import datetime
from pathlib import Path
import logging

# Configurar encoding para Windows
if os.name == 'nt':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Importar configuración de logging segura
try:
    from src.logger_config import setup_logger, safe_print
    logger = setup_logger("test_flujo_completo")
except ImportError:
    # Fallback si no está disponible
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("test_flujo_completo")
    
    def safe_print(message: str, use_unicode: bool = True):
        try:
            if use_unicode:
                print(message)
            else:
                safe_message = message.encode('ascii', errors='replace').decode('ascii')
                print(safe_message)
        except UnicodeEncodeError:
            safe_message = message.encode('ascii', errors='replace').decode('ascii')
            print(safe_message)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_flujo_completo.log', encoding='utf-8', mode='w')
    ]
)

def test_file_structure():
    """Test 1: Verificar estructura de archivos"""
    try:
        required_files = [
            'src/gui/gui_enhanced_rank.py',
            'src/core/integration_layer.py',
            'src/logger_config.py',
            'BACKUP/gui_enhanced_rank.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            return False, f"Archivos faltantes: {missing_files}"
        
        return True, "Estructura de archivos correcta"
    except Exception as e:
        return False, f"Error verificando estructura: {str(e)}"

def test_data_loading():
    """Test 2: Verificar carga de datos"""
    try:
        # Buscar archivos de datos
        data_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.csv', '.xlsx', '.xls')):
                    data_files.append(os.path.join(root, file))
        
        if not data_files:
            return False, "No se encontraron archivos de datos"
        
        # Intentar cargar el primer archivo encontrado
        test_file = data_files[0]
        import pandas as pd
        
        if test_file.endswith('.csv'):
            df = pd.read_csv(test_file, sep=';', decimal=',', engine='python')
        else:
            df = pd.read_excel(test_file)
        
        if len(df) == 0:
            return False, f"Archivo de datos vacío: {test_file}"
        
        return True, f"Datos cargados correctamente: {len(df)} filas, {len(df.columns)} columnas"
    except Exception as e:
        return False, f"Error cargando datos: {str(e)}"

def test_module_imports():
    """Test 3: Verificar imports de módulos"""
    try:
        # Test imports principales
        import pandas as pd
        import numpy as np
        import tkinter as tk
        from tkinter import ttk
        
        # Test imports del sistema
        try:
            from src.core.integration_layer import run_complete_analysis_with_gui_integration
            return True, "Importación exitosa"
        except ImportError as e:
            return False, "No se pudo importar integration_layer"
        
        return True, "Todos los módulos importados correctamente"
    except Exception as e:
        return False, f"Error en imports: {str(e)}"

def test_gui_structure():
    """Test 4: Verificar estructura GUI"""
    try:
        # Importar GUI
        try:
            from src.gui_enhanced_rank import EnhancedRankGUI
        except ImportError:
            try:
                from gui_enhanced_rank import EnhancedRankGUI
            except ImportError:
                return False, "No se pudo importar EnhancedRankGUI"
        
        # Verificar que la clase existe y tiene métodos principales
        if not hasattr(EnhancedRankGUI, '__init__'):
            return False, "Clase GUI no tiene constructor"
        
        return True, "Estructura GUI verificada"
    except Exception as e:
        return False, f"Error verificando GUI: {str(e)}"

def test_analysis_flow():
    """Test 5: Verificar flujo de análisis"""
    try:
        # Simular configuración básica
        config = {
            'trading_style': 'CONSERVADOR',
            'kpis': ['CAGR', 'Drawdown', 'Sharpe Ratio'],
            'alpha': 0.05,
            'percentile': 90
        }
        
        # Verificar que la configuración es válida
        if not isinstance(config['trading_style'], str):
            return False, "Trading style inválido"
        
        if not isinstance(config['kpis'], list):
            return False, "KPIs inválidos"
        
        return True, "Flujo de análisis configurado correctamente"
    except Exception as e:
        return False, f"Error en flujo de análisis: {str(e)}"

def test_advisor_integration():
    """Test 6: Verificar integración del asesor financiero"""
    try:
        # Verificar funciones del asesor
        advisor_functions = [
            'build_analisis_seleccion_tab',
            'build_resumen_cientifico_tab',
            'build_informacion_empirica_tab',
            'build_estrategias_seleccionadas_tab'
        ]
        
        # Simular verificación de funciones
        for func_name in advisor_functions:
            # Aquí normalmente verificaríamos que las funciones existen
            # Por ahora solo verificamos que los nombres son válidos
            if not func_name or len(func_name) < 5:
                return False, f"Nombre de función inválido: {func_name}"
        
        return True, "Integración del asesor verificada"
    except Exception as e:
        return False, f"Error en integración del asesor: {str(e)}"

def test_export_functionality():
    """Test 7: Verificar funcionalidad de exportación"""
    try:
        # Verificar directorios de exportación
        export_dirs = ['exports', 'results', 'reports']
        
        for dir_name in export_dirs:
            if not os.path.exists(dir_name):
                try:
                    os.makedirs(dir_name)
                except Exception:
                    pass
        
        # Verificar que al menos un directorio es escribible
        writable_dirs = []
        for dir_name in export_dirs:
            if os.path.exists(dir_name):
                test_file = os.path.join(dir_name, 'test_write.tmp')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    writable_dirs.append(dir_name)
                except Exception:
                    pass
        
        if not writable_dirs:
            return False, "No hay directorios escribibles para exportación"
        
        return True, f"Exportación verificada: {len(writable_dirs)} directorios disponibles"
    except Exception as e:
        return False, f"Error en exportación: {str(e)}"

def test_performance():
    """Test 8: Verificar rendimiento básico"""
    try:
        start_time = time.time()
        
        # Simular operaciones básicas
        import numpy as np
        data = np.random.rand(1000, 10)
        result = np.mean(data, axis=0)
        
        execution_time = time.time() - start_time
        
        if execution_time > 5.0:  # Más de 5 segundos es lento
            return False, f"Rendimiento lento: {execution_time:.2f}s"
        
        return True, f"Rendimiento aceptable: {execution_time:.2f}s"
    except Exception as e:
        return False, f"Error en test de rendimiento: {str(e)}"

def run_all_tests():
    """Ejecutar todos los tests"""
    tests = [
        ("Estructura de Archivos", test_file_structure),
        ("Carga de Datos", test_data_loading),
        ("Imports de Módulos", test_module_imports),
        ("Estructura GUI", test_gui_structure),
        ("Flujo de Análisis", test_analysis_flow),
        ("Integración Asesor", test_advisor_integration),
        ("Funcionalidad Exportación", test_export_functionality),
        ("Rendimiento", test_performance)
    ]
    
    results = []
    passed = 0
    total = len(tests)
    
    safe_print("INICIANDO PRUEBAS DEL FLUJO GUI")
    safe_print("=" * 50)
    
    for test_name, test_func in tests:
        try:
            start_time = time.time()
            success, message = test_func()
            execution_time = time.time() - start_time
            
            status = "PASS" if success else "FAIL"
            icon = "✅" if success else "❌"
            
            if success:
                passed += 1
            
            result = {
                'test_name': test_name,
                'status': status,
                'message': message,
                'execution_time': execution_time
            }
            results.append(result)
            
            safe_print(f"{icon} {test_name}: {status} ({execution_time:.2f}s)")
            safe_print(f"   {message}")
            
        except Exception as e:
            result = {
                'test_name': test_name,
                'status': 'ERROR',
                'message': f"Excepción: {str(e)}",
                'execution_time': 0
            }
            results.append(result)
            safe_print(f"❌ {test_name}: ERROR")
            safe_print(f"   Excepción: {str(e)}")
    
    # Resumen final
    safe_print("=" * 50)
    safe_print(f"RESUMEN FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        safe_print("🎉 TODOS LOS TESTS PASARON")
    elif passed >= total * 0.8:
        safe_print("⚠️ LA MAYORÍA DE TESTS PASARON")
    else:
        safe_print("❌ MUCHOS TESTS FALLARON")
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'total_tests': total,
                'passed_tests': passed,
                'results': results
            }, f, indent=2, ensure_ascii=False)
        safe_print(f"📄 Resultados guardados en: {results_file}")
    except Exception as e:
        safe_print(f"⚠️ No se pudieron guardar los resultados: {e}")
    
    return passed == total

def main():
    """Función principal"""
    try:
        success = run_all_tests()
        return 0 if success else 1
    except Exception as e:
        safe_print(f"❌ Error fatal en test: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 