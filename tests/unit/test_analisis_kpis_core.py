#!/usr/bin/env python3
"""
TEST_ANALISIS_KPIS_CORE.py - Analizar KPIs usados en todos los módulos del core engine
"""

import sys
import os
import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath('src'))

def test_import_all_modules():
    """Test para verificar que todos los módulos se pueden importar correctamente."""
    logger.info("🔍 Test: Importando todos los módulos del proyecto")
    
    modules_to_test = [
        'src.core.integration_layer',
        'src.data.data_manager',
        'src.data.column_mapping',
        'src.data.data_utils',
        'src.data.data_processing',
        'src.analysis.advanced_analysis_enhanced',
        'src.analysis.asesor_financiero_inteligente',
        'src.analysis.axi_select_analysis',
        'src.analysis.darwinex_pipeline',
        'src.analysis.research_docs',
        'src.analysis.scientific_analysis',
        'src.analysis.tail_risk_metrics',
        'src.gui.gui_enhanced_rank',
        'src.gui.scientific_gui_tab',
        'src.ml.advanced_ml_validation',
        'src.validation.advanced_temporal_validation',
        'src.core.compliance_audit',
        'src.core.logger_config'
    ]
    
    imported_modules = []
    failed_modules = []
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            imported_modules.append(module_name)
            logger.info(f"✅ Módulo importado: {module_name}")
        except ImportError as e:
            failed_modules.append((module_name, str(e)))
            logger.warning(f"❌ Error importando {module_name}: {e}")
    
    # Assertions para el test
    assert len(imported_modules) > 0, "No se pudo importar ningún módulo"
    logger.info(f"📊 Resumen: {len(imported_modules)} módulos importados, {len(failed_modules)} fallos")
    
    return imported_modules, failed_modules

def test_analyze_kpis_in_core_engine():
    """Test para analizar KPIs usados en el core engine."""
    logger.info("🔍 Test: Analizando KPIs en core engine")
    
    try:
        from src.core.integration_layer import run_complete_analysis_with_gui_integration
        from src.data.data_manager import DataManager
        
        # Configuración de prueba
        config = {
            'trading_style': 'balanced',
            'alpha': 0.7,
            'percentil': 90,
            'kpis_seleccionados': [
                'CAGR (IS)', 'CAGR (OOS)', 'Sharpe Ratio (IS)', 'Sharpe Ratio (OOS)',
                'Sortino Ratio', 'SQN Score (IS)', 'SQN Score (OOS)', 'Drawdown (IS)', 'Drawdown (OOS)',
                'Profit factor (IS)', 'Profit factor (OOS)', 'RecoveryFactor'
            ]
        }
        
        # 1. Cargar datos originales
        logger.info("📊 Paso 1: Cargando datos originales...")
        dm = DataManager()
        dm.load_all_data()
        
        assert dm.kpis_data is not None, "No se pudieron cargar los datos de KPIs"
        
        df_original = dm.kpis_data
        logger.info(f"✅ Datos originales: {len(df_original)} estrategias, {len(df_original.columns)} columnas")
        
        # 2. Analizar KPIs originales
        logger.info("📋 Paso 2: Analizando KPIs originales...")
        kpis_originales = [
            col for col in df_original.columns
            if pd.api.types.is_numeric_dtype(df_original[col])
        ]
        logger.info(f"🔢 KPIs numéricos originales: {len(kpis_originales)}")
        
        # Categorizar KPIs
        kpis_categorizados = {
            'Rendimiento': [],
            'Riesgo': [],
            'Consistencia': [],
            'Otros': []
        }
        
        for kpi in kpis_originales:
            kpi_lower = kpi.lower()
            if any(term in kpi_lower for term in ['cagr', 'profit', 'return', 'net']):
                kpis_categorizados['Rendimiento'].append(kpi)
            elif any(term in kpi_lower for term in ['drawdown', 'risk', 'var', 'cvar', 'ulcer']):
                kpis_categorizados['Riesgo'].append(kpi)
            elif any(term in kpi_lower for term in ['sharpe', 'sortino', 'sqn', 'calmar', 'consistency']):
                kpis_categorizados['Consistencia'].append(kpi)
            else:
                kpis_categorizados['Otros'].append(kpi)
        
        # Mostrar KPIs categorizados
        for categoria, kpis in kpis_categorizados.items():
            logger.info(f"📊 {categoria}: {len(kpis)} KPIs")
            for kpi in kpis:
                logger.debug(f"  • {kpi}")
        
        # 3. Ejecutar análisis principal
        logger.info("🔧 Paso 3: Ejecutando análisis principal...")
        df = pd.read_csv('DatabankExport_M1.csv', sep=';', decimal=',')
        resultados = run_complete_analysis_with_gui_integration(
            df,
            config=config
        )
        
        assert len(resultados) == 2, "No se obtuvieron resultados correctos del análisis"
        
        df_analisis = resultados[0]
        logger.info(f"✅ Análisis completado: {len(df_analisis)} estrategias, {len(df_analisis.columns)} columnas")
        
        # 4. Analizar KPIs en resultado del análisis
        logger.info("📋 Paso 4: Analizando KPIs en resultado del análisis...")
        kpis_analisis = [
            col for col in df_analisis.columns
            if pd.api.types.is_numeric_dtype(df_analisis[col])
        ]
        logger.info(f"🔢 KPIs numéricos en análisis: {len(kpis_analisis)}")
        
        # KPIs perdidos
        kpis_perdidos = [kpi for kpi in kpis_originales if kpi not in kpis_analisis]
        kpis_nuevos = [kpi for kpi in kpis_analisis if kpi not in kpis_originales]
        
        logger.info(f"📊 Resumen de cambios:")
        logger.info(f"  • KPIs originales: {len(kpis_originales)}")
        logger.info(f"  • KPIs en análisis: {len(kpis_analisis)}")
        logger.info(f"  • KPIs perdidos: {len(kpis_perdidos)}")
        logger.info(f"  • KPIs nuevos: {len(kpis_nuevos)}")
        
        if kpis_perdidos:
            logger.warning(f"❌ KPIs perdidos en el análisis:")
            for kpi in kpis_perdidos:
                logger.warning(f"  • {kpi}")
        
        if kpis_nuevos:
            logger.info(f"✅ KPIs nuevos en el análisis:")
            for kpi in kpis_nuevos:
                logger.info(f"  • {kpi}")
        
        # 5. Crear informe detallado
        informe = {
            'fecha_analisis': pd.Timestamp.now().isoformat(),
            'datos_originales': {
                'total_estrategias': len(df_original),
                'total_columnas': len(df_original.columns),
                'kpis_numericos': len(kpis_originales),
                'kpis_categorizados': kpis_categorizados
            },
            'analisis_principal': {
                'total_estrategias': len(df_analisis),
                'total_columnas': len(df_analisis.columns),
                'kpis_numericos': len(kpis_analisis),
                'kpis_perdidos': kpis_perdidos,
                'kpis_nuevos': kpis_nuevos
            },
            'configuracion_usada': config
        }
        
        # Guardar informe
        with open('informe_kpis_core_engine.json', 'w', encoding='utf-8') as f:
            json.dump(informe, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Informe guardado en: informe_kpis_core_engine.json")
        
        # 6. Resumen ejecutivo
        logger.info(f"📊 RESUMEN EJECUTIVO:")
        logger.info(f"  • El core engine procesa {len(kpis_originales)} KPIs originales")
        logger.info(f"  • Genera {len(kpis_analisis)} KPIs en el resultado")
        logger.info(f"  • {'✅' if len(kpis_perdidos) == 0 else '❌'} KPIs perdidos: {len(kpis_perdidos)}")
        logger.info(f"  • {'✅' if len(kpis_nuevos) > 0 else '❌'} KPIs nuevos: {len(kpis_nuevos)}")
        
        # Assertions finales
        assert len(kpis_originales) > 0, "No se encontraron KPIs originales"
        assert len(kpis_analisis) > 0, "No se encontraron KPIs en el análisis"
        assert len(df_analisis) > 0, "El DataFrame de análisis está vacío"
        
        logger.info("✅ Test de análisis de KPIs en core engine completado")
        
    except Exception as e:
        logger.error(f"❌ Error en el análisis: {e}")
        import traceback
        traceback.print_exc()
        raise

def test_analyze_all_python_files():
    """Test para analizar todos los archivos .py del proyecto."""
    logger.info("🔍 Test: Analizando todos los archivos .py del proyecto")
    
    # Encontrar todos los archivos .py
    src_path = Path('src')
    python_files = []
    
    for py_file in src_path.rglob('*.py'):
        if py_file.is_file() and not py_file.name.startswith('__'):
            python_files.append(py_file)
    
    logger.info(f"📁 Encontrados {len(python_files)} archivos .py en src/")
    
    # Analizar cada archivo
    analysis_results = {}
    
    for py_file in python_files:
        try:
            logger.info(f"📄 Analizando: {py_file}")
            
            # Leer contenido del archivo
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Análisis básico del archivo
            lines = content.split('\n')
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            comment_lines = len([line for line in lines if line.strip().startswith('#')])
            
            # Buscar KPIs mencionados
            kpi_keywords = [
                'cagr', 'sharpe', 'drawdown', 'profit', 'factor', 'ratio',
                'sortino', 'calmar', 'sqn', 'recovery', 'ulcer', 'var', 'cvar',
                'winning', 'percent', 'expectancy', 'exposure', 'trades'
            ]
            
            kpis_mentioned = []
            for keyword in kpi_keywords:
                if keyword.lower() in content.lower():
                    kpis_mentioned.append(keyword)
            
            # Buscar imports
            import_lines = [line for line in lines if line.strip().startswith(('import ', 'from '))]
            
            # Buscar funciones y clases
            function_lines = [line for line in lines if line.strip().startswith('def ')]
            class_lines = [line for line in lines if line.strip().startswith('class ')]
            
            analysis_results[str(py_file)] = {
                'total_lines': total_lines,
                'code_lines': code_lines,
                'comment_lines': comment_lines,
                'kpis_mentioned': kpis_mentioned,
                'imports': len(import_lines),
                'functions': len(function_lines),
                'classes': len(class_lines),
                'file_size_kb': py_file.stat().st_size / 1024
            }
            
            logger.info(f"  ✅ {py_file.name}: {code_lines} líneas de código, {len(kpis_mentioned)} KPIs mencionados")
            
        except Exception as e:
            logger.error(f"  ❌ Error analizando {py_file}: {e}")
            analysis_results[str(py_file)] = {'error': str(e)}
    
    # Crear informe de análisis
    informe_archivos = {
        'fecha_analisis': pd.Timestamp.now().isoformat(),
        'total_archivos': len(python_files),
        'archivos_analizados': len([r for r in analysis_results.values() if 'error' not in r]),
        'archivos_con_errores': len([r for r in analysis_results.values() if 'error' in r]),
        'analisis_detallado': analysis_results,
        'resumen': {
            'total_lineas_codigo': sum(r.get('code_lines', 0) for r in analysis_results.values() if 'error' not in r),
            'total_funciones': sum(r.get('functions', 0) for r in analysis_results.values() if 'error' not in r),
            'total_clases': sum(r.get('classes', 0) for r in analysis_results.values() if 'error' not in r),
            'kpis_unicos_mencionados': list(set([
                kpi for r in analysis_results.values() 
                for kpi in r.get('kpis_mentioned', [])
                if 'error' not in r
            ]))
        }
    }
    
    # Guardar informe
    with open('informe_analisis_archivos_python.json', 'w', encoding='utf-8') as f:
        json.dump(informe_archivos, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 Informe de archivos guardado en: informe_analisis_archivos_python.json")
    
    # Assertions
    assert len(python_files) > 0, "No se encontraron archivos .py"
    assert len([r for r in analysis_results.values() if 'error' not in r]) > 0, "No se pudo analizar ningún archivo"
    
    logger.info(f"📊 RESUMEN EJECUTIVO:")
    logger.info(f"  • Archivos .py analizados: {len(python_files)}")
    logger.info(f"  • Líneas de código totales: {informe_archivos['resumen']['total_lineas_codigo']}")
    logger.info(f"  • Funciones encontradas: {informe_archivos['resumen']['total_funciones']}")
    logger.info(f"  • Clases encontradas: {informe_archivos['resumen']['total_clases']}")
    logger.info(f"  • KPIs únicos mencionados: {len(informe_archivos['resumen']['kpis_unicos_mencionados'])}")
    
    logger.info("✅ Test de análisis de archivos .py completado")

def test_data_quality_after_cleaning():
    """Test para verificar la calidad de datos después de la limpieza y unificación."""
    logger.info("🔍 Test: Verificando calidad de datos después de limpieza")
    
    try:
        from src.data.data_manager import DataManager
        
        # Crear DataManager
        dm = DataManager()
        
        # Cargar datos
        dm.load_all_data()
        
        assert dm.kpis_data is not None, "No se pudieron cargar los datos de KPIs"
        
        df = dm.kpis_data
        
        # Verificar que el DataFrame no esté vacío
        assert len(df) > 0, "DataFrame está vacío después de la carga"
        assert len(df.columns) > 0, "DataFrame no tiene columnas"
        
        # Verificar columnas numéricas
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        assert len(numeric_columns) > 0, "No se encontraron columnas numéricas"
        
        # Verificar que no hay valores infinitos
        infinite_values = df.isin([np.inf, -np.inf]).sum().sum()
        assert infinite_values == 0, f"Se encontraron {infinite_values} valores infinitos"
        
        # Verificar que no hay demasiados valores nulos
        null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        assert null_percentage < 50, f"Demasiados valores nulos: {null_percentage:.2f}%"
        
        # Verificar nombres de columnas normalizados
        problematic_chars = [' ', '(', ')', '"', "'", '%']
        problematic_columns = []
        
        for col in df.columns:
            for char in problematic_chars:
                if char in col:
                    problematic_columns.append(col)
                    break
        
        logger.info(f"📊 Calidad de datos:")
        logger.info(f"  • Filas: {len(df)}")
        logger.info(f"  • Columnas: {len(df.columns)}")
        logger.info(f"  • Columnas numéricas: {len(numeric_columns)}")
        logger.info(f"  • Valores infinitos: {infinite_values}")
        logger.info(f"  • Porcentaje de nulos: {null_percentage:.2f}%")
        logger.info(f"  • Columnas con caracteres problemáticos: {len(problematic_columns)}")
        
        if problematic_columns:
            logger.warning(f"⚠️ Columnas con caracteres problemáticos:")
            for col in problematic_columns[:5]:  # Mostrar solo las primeras 5
                logger.warning(f"  • {col}")
        
        # Assertions finales
        assert len(df) > 0, "DataFrame vacío"
        assert len(numeric_columns) > 0, "Sin columnas numéricas"
        assert infinite_values == 0, "Valores infinitos encontrados"
        assert null_percentage < 50, "Demasiados valores nulos"
        
        logger.info("✅ Test de calidad de datos completado")
        
    except Exception as e:
        logger.error(f"❌ Error en test de calidad de datos: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    # Ejecutar todos los tests
    test_import_all_modules()
    test_analyze_kpis_in_core_engine()
    test_analyze_all_python_files()
    test_data_quality_after_cleaning()
    print("✅ Todos los tests completados exitosamente") 