#!/usr/bin/env python3
"""
Test del CLI Runner
Valida la funcionalidad del sistema desde línea de comandos
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import json
import traceback
from datetime import datetime
from pathlib import Path

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
    logger = setup_logger("test_cli")
except ImportError:
    # Fallback si no está disponible
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("test_cli")
    
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

def test_cli_imports():
    """Prueba la importación del CLI."""
    try:
        import cli_runner
        assert True
    except ImportError as e:
        assert False, f"Error importando CLI: {e}"

def test_cli_configuration():
    """Prueba la configuración del CLI."""
    try:
        import cli_runner
        
        # Verificar que el CLI tiene las funciones necesarias
        assert hasattr(cli_runner, 'main'), "CLI no tiene función main"
        
        # Verificar que existe la clase CLIRunner
        from cli_runner import CLIRunner
        runner = CLIRunner()
        assert runner is not None, "No se pudo crear CLIRunner"
        
        # Verificar configuración por defecto
        assert hasattr(runner, 'default_config'), "CLIRunner no tiene configuración por defecto"
        assert runner.default_config is not None, "Configuración por defecto es None"
        
        assert True
    except Exception as e:
        assert False, f"Error en configuración CLI: {e}"

def test_cli_execution():
    """Prueba la ejecución del CLI."""
    try:
        import cli_runner
        
        # Verificar que se puede crear el runner
        from cli_runner import CLIRunner
        runner = CLIRunner()
        
        # Verificar que tiene métodos de ejecución
        assert hasattr(runner, 'run_analysis'), "CLIRunner no tiene método run_analysis"
        assert hasattr(runner, 'load_data'), "CLIRunner no tiene método load_data"
        
        assert True
    except Exception as e:
        assert False, f"Error en ejecución CLI: {e}"

def test_cli_output():
    """Prueba la salida del CLI."""
    try:
        import cli_runner
        
        # Verificar que se puede crear el runner
        from cli_runner import CLIRunner
        runner = CLIRunner()
        
        # Verificar métodos de salida
        assert hasattr(runner, 'display_results'), "CLIRunner no tiene método display_results"
        assert hasattr(runner, 'show_summary'), "CLIRunner no tiene método show_summary"
        
        assert True
    except Exception as e:
        assert False, f"Error en salida CLI: {e}"

def test_cli_error_handling():
    """Prueba el manejo de errores del CLI."""
    try:
        import cli_runner
        
        # Verificar que se puede crear el runner
        from cli_runner import CLIRunner
        runner = CLIRunner()
        
        # Verificar manejo de errores
        assert hasattr(runner, 'error_handler'), "CLIRunner no tiene error_handler"
        assert hasattr(runner, 'error_context'), "CLIRunner no tiene error_context"
        
        assert True
    except Exception as e:
        assert False, f"Error en manejo de errores CLI: {e}"

def run_all_tests():
    """Ejecutar todos los tests CLI"""
    tests = [
        ("Imports CLI", test_cli_imports),
        ("Configuración CLI", test_cli_configuration),
        ("Ejecución CLI", test_cli_execution),
        ("Salida CLI", test_cli_output),
        ("Manejo de Errores CLI", test_cli_error_handling)
    ]
    
    results = []
    passed = 0
    total = len(tests)
    
    safe_print("INICIANDO PRUEBAS DEL CLI RUNNER")
    safe_print("=" * 50)
    
    for test_name, test_func in tests:
        try:
            start_time = time.time()
            test_func()
            execution_time = time.time() - start_time
            
            status = "PASS"
            icon = "✅"
            passed += 1
            
            result = {
                'test_name': test_name,
                'status': status,
                'message': "Test completado exitosamente",
                'execution_time': execution_time
            }
            results.append(result)
            
            safe_print(f"{icon} {test_name}: {status} ({execution_time:.2f}s)")
            
        except AssertionError as e:
            result = {
                'test_name': test_name,
                'status': 'FAIL',
                'message': f"AssertionError: {str(e)}",
                'execution_time': 0
            }
            results.append(result)
            safe_print(f"❌ {test_name}: FAIL")
            safe_print(f"   {str(e)}")
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
    safe_print(f"RESUMEN CLI: {passed}/{total} tests pasaron")
    
    if passed == total:
        safe_print("🎉 TODOS LOS TESTS CLI PASARON")
    elif passed >= total * 0.8:
        safe_print("⚠️ LA MAYORÍA DE TESTS CLI PASARON")
    else:
        safe_print("❌ MUCHOS TESTS CLI FALLARON")
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_cli_results_{timestamp}.json"
    
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'total_tests': total,
                'passed_tests': passed,
                'results': results
            }, f, indent=2, ensure_ascii=False)
        safe_print(f"📄 Resultados CLI guardados en: {results_file}")
    except Exception as e:
        safe_print(f"⚠️ No se pudieron guardar los resultados CLI: {e}")

def main():
    """Función principal"""
    try:
        run_all_tests()
        return 0
    except Exception as e:
        safe_print(f"❌ Error fatal en test CLI: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 