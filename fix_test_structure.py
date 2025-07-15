#!/usr/bin/env python3
"""
Script para corregir la estructura de tests y crear archivos de prueba

Este script:
1. Crea archivos de datos de prueba en INPUTTEST/
2. Corrige los tests que referencian módulos inexistentes
3. Actualiza la lista de módulos disponibles
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import shutil

def create_test_data():
    """Crea archivos de datos de prueba en INPUTTEST/."""
    print("📊 Creando archivos de datos de prueba...")
    
    # Crear directorio INPUTTEST si no existe
    inputtest_dir = Path("INPUTTEST")
    inputtest_dir.mkdir(exist_ok=True)
    
    # Crear DatabankExport_M1.csv
    strategies_data = {
        'Strategy_Name': [f'Strategy_{i}' for i in range(1, 21)],
        'Profit_factor': np.random.uniform(1.0, 3.0, 20),
        'Sharpe_Ratio': np.random.uniform(0.5, 2.5, 20),
        'CalmarRatio': np.random.uniform(0.3, 2.0, 20),
        'Max_Drawdown': np.random.uniform(5.0, 25.0, 20),
        'Total_Trades': np.random.randint(50, 500, 20),
        'Win_Rate': np.random.uniform(0.4, 0.8, 20),
        'CAGR': np.random.uniform(5.0, 30.0, 20),
        'Net_Profit': np.random.uniform(1000, 50000, 20),
        'Recovery_Factor': np.random.uniform(1.0, 5.0, 20),
        'Risk_Reward_Ratio': np.random.uniform(1.5, 4.0, 20),
        'Profit_Factor': np.random.uniform(1.2, 3.5, 20),
        'Sharpe_Ratio_IS': np.random.uniform(0.5, 2.5, 20),
        'Sharpe_Ratio_OOS': np.random.uniform(0.3, 2.0, 20),
        'CAGR_IS': np.random.uniform(5.0, 30.0, 20),
        'CAGR_OOS': np.random.uniform(3.0, 25.0, 20)
    }
    
    df_strategies = pd.DataFrame(strategies_data)
    df_strategies.to_csv(inputtest_dir / "DatabankExport_M1.csv", index=False)
    print("✅ DatabankExport_M1.csv creado")
    
    # Crear DATOSMQL5.csv
    mql5_data = {
        'Strategy_Name': [f'MQL5_Strategy_{i}' for i in range(1, 16)],
        'Profit_factor': np.random.uniform(1.1, 2.8, 15),
        'Sharpe_Ratio': np.random.uniform(0.6, 2.2, 15),
        'CalmarRatio': np.random.uniform(0.4, 1.8, 15),
        'Max_Drawdown': np.random.uniform(8.0, 20.0, 15),
        'Total_Trades': np.random.randint(30, 300, 15),
        'Win_Rate': np.random.uniform(0.45, 0.75, 15),
        'CAGR': np.random.uniform(8.0, 25.0, 15),
        'Net_Profit': np.random.uniform(2000, 40000, 15),
        'Recovery_Factor': np.random.uniform(1.2, 4.5, 15),
        'Risk_Reward_Ratio': np.random.uniform(1.8, 3.5, 15),
        'Profit_Factor': np.random.uniform(1.3, 3.0, 15)
    }
    
    df_mql5 = pd.DataFrame(mql5_data)
    df_mql5.to_csv(inputtest_dir / "DATOSMQL5.csv", index=False)
    print("✅ DATOSMQL5.csv creado")

def fix_test_imports():
    """Corrige los imports en los tests que referencian módulos inexistentes."""
    print("🔧 Corrigiendo imports en tests...")
    
    # Archivos a corregir
    test_files = [
        "tests/unit/test_gui_workflow.py",
        "tests/unit/test_analisis_kpis_core.py"
    ]
    
    replacements = [
        # Módulos que no existen
        ("src.analysis.research_docs", "# src.analysis.research_docs - MÓDULO ELIMINADO"),
        ("src.data.data_processing", "# src.data.data_processing - MÓDULO ELIMINADO"),
        ("src.validation.advanced_temporal_validation", "# src.validation.advanced_temporal_validation - MÓDULO ELIMINADO"),
        
        # Rutas de archivos
        ("'src/data/data_processing.py'", "# 'src/data/data_processing.py' - ARCHIVO ELIMINADO"),
        ("'src/analysis/research_docs.py'", "# 'src/analysis/research_docs.py' - ARCHIVO ELIMINADO"),
        ("'src/validation/advanced_temporal_validation.py'", "# 'src/validation/advanced_temporal_validation.py' - ARCHIVO ELIMINADO"),
        
        # Imports específicos
        ("from src.analysis.research_docs import", "# from src.analysis.research_docs import - MÓDULO ELIMINADO"),
        ("from src.data.data_processing import", "# from src.data.data_processing import - MÓDULO ELIMINADO"),
        ("from src.validation.advanced_temporal_validation import", "# from src.validation.advanced_temporal_validation import - MÓDULO ELIMINADO"),
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                for old_import, new_import in replacements:
                    content = content.replace(old_import, new_import)
                
                if content != original_content:
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Corregido: {test_file}")
                else:
                    print(f"ℹ️ Sin cambios: {test_file}")
                    
            except Exception as e:
                print(f"❌ Error procesando {test_file}: {e}")

def update_module_list():
    """Actualiza la lista de módulos disponibles en los tests."""
    print("📋 Actualizando lista de módulos disponibles...")
    
    # Módulos que realmente existen
    available_modules = [
        'src.logger_config',
        'src.analysis.advanced_analysis_enhanced',
        'src.analysis.asesor_financiero_inteligente',
        'src.analysis.axi_select_analysis',
        'src.analysis.darwinex_pipeline',
        'src.analysis.scientific_analysis',
        'src.analysis.tail_risk_metrics',
        'src.analysis.predictability_metrics',
        'src.core.compliance_audit',
        'src.core.integration_layer',
        'src.core.logger_config',
        'src.data.column_mapping',
        'src.data.data_manager',
        'src.data.data_utils',
        'src.data.visualization',
        'src.gui.main_window',
        'src.gui.scientific_gui_tab',
        'src.gui.utils',
        'src.ml.advanced_ml_validation'
    ]
    
    # Actualizar test_gui_workflow.py
    test_file = "tests/unit/test_gui_workflow.py"
    if Path(test_file).exists():
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Reemplazar la lista de módulos
            old_list_start = content.find("all_py_modules = [")
            if old_list_start != -1:
                old_list_end = content.find("]", old_list_start) + 1
                new_list = "all_py_modules = [\n            " + ",\n            ".join([f"'{module}'" for module in available_modules]) + "\n        ]"
                content = content[:old_list_start] + new_list + content[old_list_end:]
                
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Lista de módulos actualizada en {test_file}")
            else:
                print(f"⚠️ No se encontró la lista de módulos en {test_file}")
                
        except Exception as e:
            print(f"❌ Error actualizando {test_file}: {e}")

def create_missing_files():
    """Crea archivos faltantes que son referenciados en los tests."""
    print("📄 Creando archivos faltantes...")
    
    # Crear archivos de configuración si no existen
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Crear trading_config.json básico
    config_file = config_dir / "trading_config.json"
    if not config_file.exists():
        config_content = '''{
    "trading_styles": {
        "Scalping": {
            "profitability_weight": 0.35,
            "risk_weight": 0.40,
            "consistency_weight": 0.25
        },
        "Day_Trading": {
            "profitability_weight": 0.40,
            "risk_weight": 0.35,
            "consistency_weight": 0.25
        },
        "Swing_Trading": {
            "profitability_weight": 0.45,
            "risk_weight": 0.30,
            "consistency_weight": 0.25
        },
        "Position_Trading": {
            "profitability_weight": 0.50,
            "risk_weight": 0.25,
            "consistency_weight": 0.25
        }
    },
    "analysis_settings": {
        "alpha": 0.8,
        "percentile": 80,
        "top_n": 20
    }
}'''
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ trading_config.json creado")

def main():
    """Función principal del script."""
    print("🔧 Iniciando corrección de estructura de tests...")
    
    # Crear datos de prueba
    create_test_data()
    
    # Corregir imports
    fix_test_imports()
    
    # Actualizar lista de módulos
    update_module_list()
    
    # Crear archivos faltantes
    create_missing_files()
    
    print("\n✅ Corrección de estructura completada")
    print("📊 Archivos creados:")
    print("  - INPUTTEST/DatabankExport_M1.csv")
    print("  - INPUTTEST/DATOSMQL5.csv")
    print("  - config/trading_config.json")
    print("\n🔧 Tests corregidos para usar módulos disponibles")

if __name__ == "__main__":
    main() 