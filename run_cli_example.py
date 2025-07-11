#!/usr/bin/env python3
"""
RUN_CLI_EXAMPLE.py - Script de ejemplo para probar el CLI mejorado

Este script demuestra todas las funcionalidades del CLI Runner:
- Testing automatizado
- Análisis completo
- Validación de datos
- Exportación de resultados
- Manejo robusto de errores

Uso:
    python run_cli_example.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"📝 Comando: {command}")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        execution_time = time.time() - start_time
        
        print(f"⏱️ Tiempo de ejecución: {execution_time:.2f} segundos")
        print(f"📊 Código de salida: {result.returncode}")
        
        if result.stdout:
            print("\n📤 SALIDA:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ ERRORES:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Comando ejecutado exitosamente")
        else:
            print("❌ Comando falló")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

def main():
    """Función principal del script de ejemplo."""
    print("🎯 SCRIPT DE EJEMPLO - CLI RUNNER MEJORADO")
    print("="*60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("cli_runner.py"):
        print("❌ Error: cli_runner.py no encontrado")
        print("💡 Asegúrate de ejecutar este script desde el directorio raíz del proyecto")
        return False
    
    # Verificar archivos de datos
    required_files = [
        "DatabankExport_M1.csv",
        "DATOSMQL5.csv",
        "INPUTTEST/M1_NDX_UP_MQL4_136_STOP"
    ]
    
    print("\n🔍 Verificando archivos de datos...")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NO ENCONTRADO")
    
    # Crear carpeta de salida si no existe
    output_folder = "INPUTTEST/TOP"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Carpeta creada: {output_folder}")
    
    # Ejecutar pruebas en orden
    tests = [
        {
            "command": "python cli_runner.py --help",
            "description": "Mostrar ayuda del CLI"
        },
        {
            "command": "python cli_runner.py --validate",
            "description": "Validar archivos de entrada"
        },
        {
            "command": "python cli_runner.py --test",
            "description": "Ejecutar pruebas automatizadas completas"
        },
        {
            "command": "python cli_runner.py --auto --top-n 10 --percentil 90",
            "description": "Ejecutar análisis automático con parámetros específicos"
        },
        {
            "command": "python cli_runner.py --run --scientific",
            "description": "Ejecutar análisis con mejoras científicas"
        }
    ]
    
    print(f"\n🧪 Ejecutando {len(tests)} pruebas...")
    
    passed_tests = 0
    for i, test in enumerate(tests, 1):
        print(f"\n📋 Prueba {i}/{len(tests)}")
        if run_command(test["command"], test["description"]):
            passed_tests += 1
    
    # Mostrar resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"✅ Pruebas pasadas: {passed_tests}/{len(tests)}")
    print(f"📈 Tasa de éxito: {(passed_tests/len(tests)*100):.1f}%")
    
    if passed_tests == len(tests):
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("\n💡 El CLI está funcionando correctamente y listo para usar.")
        print("📝 Puedes usar los siguientes comandos:")
        print("   - python cli_runner.py --help")
        print("   - python cli_runner.py --auto")
        print("   - python cli_runner.py --test")
        print("   - python cli_runner.py --run")
    else:
        print("⚠️ Algunas pruebas fallaron")
        print("🔧 Revisa los logs para más detalles")
    
    # Mostrar archivos generados
    print(f"\n📁 Archivos generados en: {output_folder}")
    if os.path.exists(output_folder):
        files = os.listdir(output_folder)
        for file in files:
            file_path = os.path.join(output_folder, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  📄 {file} ({size} bytes)")
    
    return passed_tests == len(tests)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Script cancelado por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        sys.exit(1) 