#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KFORCEVSQVARATIOS - Sistema de Análisis Cuantitativo v2.0
Sistema principal para análisis robusto de estrategias de trading.

Archivos principales:
- integration_layer.py
- gui_enhanced_rank.py
- data_manager.py
- data_processing.py
- data_utils.py
- research_docs.py
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def ensure_dir(path):
    """Asegura que el directorio existe."""
    os.makedirs(path, exist_ok=True)

def get_sqx_files(folder):
    """Obtiene lista de archivos .sqx de una carpeta."""
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if f.lower().endswith('.sqx')]

def setup_project_structure():
    """Configura la estructura del proyecto."""
    logger.info("Configurando estructura del proyecto...")
    
    directories = [
        'data',
        'output',
        'reports',
        'logs',
        'cache',
        'config'
    ]
    
    for directory in directories:
        ensure_dir(directory)
        logger.info(f"Directorio creado/verificado: {directory}")
    
    logger.info("Estructura del proyecto configurada")

def create_sample_data():
    """Crea datos de ejemplo para testing."""
    logger.info("Creando datos de ejemplo...")
    
    # Crear DataFrame de ejemplo
    np.random.seed(42)
    n_strategies = 50
    
    sample_data = {
        'Strategy_Name': [f'Strategy_{i:03d}' for i in range(1, n_strategies + 1)],
        'CAGR': np.random.normal(15, 8, n_strategies),
        'Sharpe_Ratio': np.random.normal(1.2, 0.5, n_strategies),
        'Profit_factor': np.random.normal(1.5, 0.3, n_strategies),
        'Max_DD_%': np.random.normal(-12, 5, n_strategies),
        'Winning_Percent': np.random.normal(55, 10, n_strategies),
        'Expectancy': np.random.normal(0.8, 0.4, n_strategies),
        'CalmarRatio': np.random.normal(1.8, 0.8, n_strategies),
        'RecoveryFactor': np.random.normal(2.5, 1.2, n_strategies),
        'SQN': np.random.normal(2.1, 0.9, n_strategies),
        'Total_Trades': np.random.randint(100, 1000, n_strategies),
        'Avg_Bars_in_Trade': np.random.randint(20, 200, n_strategies),
        'Max_Consec_Losses': np.random.randint(3, 15, n_strategies),
        'Stagnation': np.random.randint(0, 50, n_strategies),
        'Net_profit': np.random.normal(50000, 25000, n_strategies),
        'Exposure': np.random.normal(85, 10, n_strategies),
        'VaR_95%': np.random.normal(-2.5, 1.0, n_strategies),
        'CVaR_95%': np.random.normal(-3.8, 1.5, n_strategies),
        'Ulcer_Index_%': np.random.normal(8, 3, n_strategies),
        'Ulcer_Performance_Index': np.random.normal(1.9, 0.8, n_strategies),
        'RINAIndex': np.random.normal(0.65, 0.15, n_strategies),
        'Sortino_Ratio': np.random.normal(1.8, 0.6, n_strategies),
        'Payout_ratio': np.random.normal(1.4, 0.3, n_strategies),
        'New_Peak_Trades_%': np.random.normal(25, 8, n_strategies),
        'Drawdown_Trades_%': np.random.normal(15, 6, n_strategies),
        'Avg_MAE_Profit_loss': np.random.normal(600, 200, n_strategies),
        'Avg_MFE_Profit_loss': np.random.normal(800, 250, n_strategies),
        'Max_Drawdown_Duration': np.random.randint(30, 180, n_strategies)
    }
    
    df = pd.DataFrame(sample_data)
    
    # Asegurar valores positivos donde corresponde
    df['Profit_factor'] = df['Profit_factor'].abs()
    df['Winning_Percent'] = df['Winning_Percent'].clip(0, 100)
    df['Exposure'] = df['Exposure'].clip(0, 100)
    df['Total_Trades'] = df['Total_Trades'].abs()
    df['Avg_Bars_in_Trade'] = df['Avg_Bars_in_Trade'].abs()
    df['Max_Consec_Losses'] = df['Max_Consec_Losses'].abs()
    df['Stagnation'] = df['Stagnation'].abs()
    df['Max_Drawdown_Duration'] = df['Max_Drawdown_Duration'].abs()
    
    # Asegurar valores negativos donde corresponde
    df['Max_DD_%'] = df['Max_DD_%'].clip(-100, 0)
    df['VaR_95%'] = df['VaR_95%'].clip(-10, 0)
    df['CVaR_95%'] = df['CVaR_95%'].clip(-15, 0)
    
    # Guardar datos de ejemplo
    df.to_csv('DatabankExport_M1.csv', sep=';', decimal=',', index=False)
    logger.info(f"Datos de ejemplo creados: {len(df)} estrategias")
    
    return df

def test_core_engine():
    """Prueba el motor principal de análisis."""
    try:
        logger.info("=== Probando Core Engine ===")
        
        from src.core.integration_layer import (
            FactorKElite96Enhanced,
            UnifiedEvaluatorEnhanced,
            run_complete_analysis_with_gui_integration
        )
        
        # Crear motor
        engine = FactorKElite96Enhanced()
        logger.info("Motor FactorKElite96Enhanced creado correctamente")
        
        # Crear evaluador unificado
        evaluator = UnifiedEvaluatorEnhanced()
        logger.info("Evaluador unificado creado correctamente")
        
        # Verificar que se puede importar la función de análisis
        logger.info("Función de análisis integrado importada correctamente")
        
        return True
        
    except Exception as e:
        logger.error(f"Error en test_core_engine: {e}")
        return False

def test_data_manager():
    """Prueba el gestor de datos."""
    try:
        logger.info("=== Probando Data Manager ===")
        
        from src.data.data_manager import DataManager
        
        # Crear gestor de datos
        dm = DataManager()
        logger.info("DataManager creado correctamente")
        
        # Verificar configuración
        config = dm.config
        logger.info(f"Configuración cargada: {len(config)} parámetros")
        
        return True
        
    except Exception as e:
        logger.error(f"Error en test_data_manager: {e}")
        return False

def test_data_processing():
    """Prueba el procesamiento de datos usando SOLO DataManager."""
    try:
        logger.info("=== Probando DataManager ===")
        from src.data.data_manager import DataManager
        processor = DataManager()
        logger.info("DataManager creado correctamente")
        return True
    except Exception as e:
        logger.error(f"Error en test_data_processing: {e}")
        return False

def test_research_docs():
    """Prueba las funciones de investigación y validación científica integradas en DataManager."""
    try:
        logger.info("=== Probando funciones de investigación en DataManager ===")
        
        from src.data.data_manager import DataManager
        
        # Crear DataManager
        dm = DataManager()
        
        # Probar funciones básicas
        if os.path.exists('DatabankExport_M1.csv'):
            df = pd.read_csv('DatabankExport_M1.csv', sep=';', decimal=',')
            
            # Probar validación de columna numérica
            is_valid = dm.validate_numeric_column(df, 'CAGR')
            logger.info(f"Columna CAGR válida: {is_valid}")
            
            # Probar cálculo de estadísticas básicas
            stats = dm.calculate_basic_stats(df, 'Sharpe_Ratio')
            logger.info(f"Estadísticas calculadas: {len(stats)} métricas")
            
            # Probar detección de outliers
            outliers = dm.detect_outliers_iqr(df, 'CAGR')
            logger.info(f"Outliers detectados: {outliers['count']} valores")
            
            # Probar análisis completo de calidad
            quality_analysis = dm.analyze_data_quality(df)
            logger.info(f"Análisis de calidad completado: {quality_analysis['total_rows']} filas, {quality_analysis['numeric_columns']} columnas numéricas")
            
            return True
        else:
            logger.error("Archivo DatabankExport_M1.csv no encontrado")
            return False
            
    except Exception as e:
        logger.error(f"Error en test_research_docs: {e}")
        return False

def test_gui():
    """Prueba la interfaz gráfica."""
    try:
        logger.info("=== Probando GUI Enhanced Rank ===")
        
        # Importar GUI
        from src.gui.gui_enhanced_rank import EnhancedRankGUI
        
        # Verificar que se puede importar sin errores
        logger.info("GUI EnhancedRankGUI importada correctamente")
        
        # Nota: La GUI se ejecutará en modo interactivo
        print("\n" + "="*50)
        print("GUI ENHANCED RANK - Para ejecutar la interfaz gráfica:")
        print("python src/gui_enhanced_rank.py")
        print("="*50 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Error en test_gui: {e}")
        return False

def run_complete_test():
    """Ejecuta todas las pruebas del proyecto."""
    logger.info("Iniciando pruebas completas del proyecto KFORCEVSQVARATIOS")
    
    # Configurar estructura del proyecto
    setup_project_structure()
    
    # Crear datos de ejemplo si no existen
    if not os.path.exists('DatabankExport_M1.csv'):
        create_sample_data()
    
    # Ejecutar pruebas
    tests = [
        ("Core Engine", test_core_engine),
        ("Data Manager", test_data_manager),
        ("Data Processing", test_data_processing),
        ("Research Docs", test_research_docs),
        ("GUI", test_gui)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            logger.info(f"\n{'='*20} {test_name} {'='*20}")
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Error en {test_name}: {e}")
            results[test_name] = False
    
    # Mostrar resumen
    logger.info("\n" + "="*50)
    logger.info("RESUMEN DE PRUEBAS")
    logger.info("="*50)
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        logger.info(f"{test_name}: {'PASO' if result else 'FALLO'}")
    
    passed = sum(results.values())
    total = len(results)
    logger.info(f"\nTotal: {passed}/{total} pruebas pasaron")
    
    return results

def main():
    """Función principal."""
    print("KFORCEVSQVARATIOS - Sistema de Análisis Cuantitativo")
    print("="*60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            run_complete_test()
        elif command == "gui":
            print("Para ejecutar la GUI:")
            print("python src/gui_enhanced_rank.py")
        elif command == "data":
            create_sample_data()
        elif command == "help":
            print_help()
        else:
            print(f"Comando desconocido: {command}")
            print_help()
    else:
        # Ejecutar pruebas por defecto
        run_complete_test()

def print_help():
    """Muestra la ayuda del programa."""
    print("\nUso: python main.py [comando]")
    print("\nComandos disponibles:")
    print("  test    - Ejecutar todas las pruebas del proyecto")
    print("  gui     - Mostrar instrucciones para ejecutar la GUI")
    print("  data    - Crear datos de ejemplo")
    print("  help    - Mostrar esta ayuda")
    print("\nEjemplos:")
    print("  python main.py test")
    print("  python main.py gui")
    print("  python main.py data")

if __name__ == "__main__":
    main() 