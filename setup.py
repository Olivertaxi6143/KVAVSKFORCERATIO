#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SETUP.PY - Script de instalación automática para KFORCEVSQVARATIOS

Este script automatiza la instalación y configuración del proyecto:
- Instalación de dependencias
- Creación de estructura de directorios
- Configuración inicial
- Verificación de instalación
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Verifica que la versión de Python sea compatible."""
    if sys.version_info < (3, 8):
        logger.error("Se requiere Python 3.8 o superior")
        return False
    logger.info(f"Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def install_dependencies():
    """Instala las dependencias del proyecto."""
    try:
        logger.info("Instalando dependencias...")
        
        # Verificar si pip está disponible
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            logger.error("pip no está disponible")
            return False
        
        # Instalar dependencias
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Dependencias instaladas correctamente")
            return True
        else:
            logger.error(f"Error instalando dependencias: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error en instalación de dependencias: {e}")
        return False

def create_project_structure():
    """Crea la estructura de directorios del proyecto."""
    directories = [
        'config',
        'cache',
        'cache/scientific',
        'output',
        'logs',
        'data',
        'reports',
        'temp'
    ]
    
    try:
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"Directorio creado/verificado: {directory}")
        return True
    except Exception as e:
        logger.error(f"Error creando estructura de directorios: {e}")
        return False

def create_default_config():
    """Crea la configuración por defecto."""
    try:
        config = {
            "trading_style": "General",
            "selected_kpis": {
                "Strategy_Name": {"enabled": True, "weight": 1.0, "description": "Nombre de la Estrategia"},
                "Profit_factor": {"enabled": True, "weight": 1.0, "description": "Factor de Beneficio"},
                "Sharpe_Ratio": {"enabled": True, "weight": 1.0, "description": "Ratio de Sharpe"},
                "CalmarRatio": {"enabled": True, "weight": 1.0, "description": "Ratio de Calmar"},
                "Max_DD_%": {"enabled": True, "weight": 1.0, "description": "Máximo Drawdown (%)"},
                "Winning_Percent": {"enabled": True, "weight": 1.0, "description": "Porcentaje de Operaciones Ganadoras"},
                "Net_profit": {"enabled": True, "weight": 1.0, "description": "Beneficio Neto"},
                "Sharpe_Ratio_IS": {"enabled": True, "weight": 1.0, "description": "Ratio de Sharpe (IS)"},
                "Profit_Factor_IS": {"enabled": True, "weight": 1.0, "description": "Factor de Beneficio (IS)"},
                "Sharpe_Ratio_OOS": {"enabled": True, "weight": 1.0, "description": "Ratio de Sharpe (OOS)"},
                "Profit_Factor_OOS": {"enabled": True, "weight": 1.0, "description": "Factor de Beneficio (OOS)"}
            },
            "trading_styles": {
                "General": {
                    "description": "Estilo general de trading",
                    "kpi_weights": {},
                    "component_weights": {
                        "stability": 0.25,
                        "growth": 0.25,
                        "efficiency": 0.25,
                        "consistency": 0.25
                    },
                    "priority_kpis": ["Sharpe_Ratio", "Profit_factor", "Max_DD_%"]
                }
            },
            "performance": {
                "chunk_size": 10000,
                "max_workers": 4,
                "cache_size": 128,
                "gui_update_interval": 0.1
            },
            "validation": {
                "strict_validation": True,
                "imputation_method": "regime_based",
                "outlier_detection": "isolation_forest",
                "outlier_threshold": 0.1
            },
            "cache": {
                "enable_cache": True,
                "cache_duration_hours": 24,
                "cache_dir": "cache"
            }
        }
        
        config_file = Path("config/trading_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info("Configuración por defecto creada")
        return True
        
    except Exception as e:
        logger.error(f"Error creando configuración: {e}")
        return False

def create_sample_data():
    """Crea datos de ejemplo si no existen."""
    try:
        if not os.path.exists('DatabankExport_M1.csv'):
            logger.info("Creando datos de ejemplo...")
            
            import pandas as pd
            import numpy as np
            
            # Crear datos de ejemplo para DatabankExport_M1.csv
            sample_kpis = pd.DataFrame({
                'Strategy_Name': [f'Strategy_{i}' for i in range(1, 21)],
                'Profit_factor': np.random.uniform(1.0, 3.0, 20),
                'Sharpe_Ratio': np.random.uniform(0.5, 2.5, 20),
                'CalmarRatio': np.random.uniform(0.3, 2.0, 20),
                'Max_DD_%': np.random.uniform(5.0, 25.0, 20),
                'Winning_Percent': np.random.uniform(40.0, 70.0, 20),
                'Net_profit': np.random.uniform(10000, 100000, 20),
                'Sharpe_Ratio_IS': np.random.uniform(0.5, 2.5, 20),
                'Profit_Factor_IS': np.random.uniform(1.0, 3.0, 20),
                'Sharpe_Ratio_OOS': np.random.uniform(0.5, 2.5, 20),
                'Profit_Factor_OOS': np.random.uniform(1.0, 3.0, 20)
            })
            
            sample_kpis.to_csv('DatabankExport_M1.csv', index=False, sep=';', decimal=',')
            logger.info("Datos de ejemplo creados: DatabankExport_M1.csv")
        
        if not os.path.exists('DATOSMQL5.csv'):
            logger.info("Creando datos de mercado de ejemplo...")
            
            # Crear datos de mercado de ejemplo
            dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
            market_data = pd.DataFrame({
                'Date': dates,
                'Open': np.random.uniform(100, 200, len(dates)),
                'High': np.random.uniform(200, 300, len(dates)),
                'Low': np.random.uniform(50, 150, len(dates)),
                'Close': np.random.uniform(100, 200, len(dates)),
                'Volume': np.random.randint(1000000, 10000000, len(dates))
            })
            
            market_data.to_csv('DATOSMQL5.csv', index=False)
            logger.info("Datos de mercado de ejemplo creados: DATOSMQL5.csv")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creando datos de ejemplo: {e}")
        return False

def test_imports():
    """Prueba que se pueden importar todos los módulos."""
    modules = [
        'src.core_engine_enhanced',
        'src.data_utils',
        'src.gui_enhanced',
        'src.research_docs'
    ]
    
    failed_imports = []
    
    for module in modules:
        try:
            __import__(module)
            logger.info(f"✓ {module} importado correctamente")
        except ImportError as e:
            logger.error(f"✗ Error importando {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        logger.error(f"Módulos con errores de importación: {failed_imports}")
        return False
    
    return True

def run_basic_tests():
    """Ejecuta pruebas básicas del sistema."""
    try:
        logger.info("Ejecutando pruebas básicas...")
        
        # Importar módulos principales
        from core_engine_enhanced import ConfigManagerEnhanced
        
        # Probar ConfigManager
        config_manager = ConfigManagerEnhanced()
        logger.info("✓ ConfigManager funcionando")
        
        return True
        
    except Exception as e:
        logger.error(f"Error en pruebas básicas: {e}")
        return False

def create_batch_files():
    """Crea archivos batch para Windows."""
    try:
        # Crear archivo batch para ejecutar pruebas
        with open('run_tests.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('echo Ejecutando pruebas del proyecto...\n')
            f.write('python test_project.py\n')
            f.write('pause\n')
        
        # Crear archivo batch para ejecutar GUI
        with open('run_gui.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('echo Iniciando interfaz gráfica...\n')
            f.write('python gui_enhanced.py\n')
            f.write('pause\n')
        
        # Crear archivo batch para ejecutar main
        with open('run_main.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('echo Ejecutando programa principal...\n')
            f.write('python main.py\n')
            f.write('pause\n')
        
        logger.info("Archivos batch creados para Windows")
        return True
        
    except Exception as e:
        logger.error(f"Error creando archivos batch: {e}")
        return False

def create_shell_scripts():
    """Crea scripts shell para Linux/Mac."""
    try:
        # Crear script para ejecutar pruebas
        with open('run_tests.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Ejecutando pruebas del proyecto..."\n')
            f.write('python3 test_project.py\n')
        
        # Crear script para ejecutar GUI
        with open('run_gui.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Iniciando interfaz gráfica..."\n')
            f.write('python3 gui_enhanced.py\n')
        
        # Crear script para ejecutar main
        with open('run_main.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Ejecutando programa principal..."\n')
            f.write('python3 main.py\n')
        
        # Hacer ejecutables los scripts
        os.chmod('run_tests.sh', 0o755)
        os.chmod('run_gui.sh', 0o755)
        os.chmod('run_main.sh', 0o755)
        
        logger.info("Scripts shell creados para Linux/Mac")
        return True
        
    except Exception as e:
        logger.error(f"Error creando scripts shell: {e}")
        return False

def main():
    """Función principal de instalación."""
    print("="*60)
    print("INSTALADOR DE KFORCEVSQVARATIOS")
    print("="*60)
    
    steps = [
        ("Verificando versión de Python", check_python_version),
        ("Instalando dependencias", install_dependencies),
        ("Creando estructura del proyecto", create_project_structure),
        ("Creando configuración por defecto", create_default_config),
        ("Creando datos de ejemplo", create_sample_data),
        ("Probando importaciones", test_imports),
        ("Ejecutando pruebas básicas", run_basic_tests),
        ("Creando archivos batch (Windows)", create_batch_files),
        ("Creando scripts shell (Linux/Mac)", create_shell_scripts)
    ]
    
    results = {}
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        try:
            results[step_name] = step_func()
            if results[step_name]:
                print(f"✓ {step_name} completado")
            else:
                print(f"✗ {step_name} falló")
        except Exception as e:
            print(f"✗ {step_name} falló con error: {e}")
            results[step_name] = False
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("RESUMEN DE INSTALACIÓN")
    print("="*60)
    
    successful_steps = sum(results.values())
    total_steps = len(results)
    
    for step_name, result in results.items():
        status = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{step_name}: {status}")
    
    print(f"\nTotal: {successful_steps}/{total_steps} pasos completados exitosamente")
    
    if successful_steps == total_steps:
        print("\n🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
        print("\nPara usar el sistema:")
        print("- Windows: Ejecutar run_main.bat, run_gui.bat o run_tests.bat")
        print("- Linux/Mac: Ejecutar ./run_main.sh, ./run_gui.sh o ./run_tests.sh")
        print("- O usar directamente: python main.py, python gui_enhanced.py, python test_project.py")
    else:
        print("\n⚠️  INSTALACIÓN COMPLETADA CON ERRORES")
        print("Revisar los errores anteriores y ejecutar manualmente los pasos fallidos")
    
    return successful_steps == total_steps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 