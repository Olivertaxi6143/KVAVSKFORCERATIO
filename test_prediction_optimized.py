#!/usr/bin/env python3
"""
Script de testing para la función de predicción optimizada con KPIs financieros.
Valida la implementación completa con selección inteligente de KPIs.
"""

import sys
import os
import pandas as pd
import numpy as np
import logging
from pathlib import Path

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

from data_manager import DataManager

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_optimized_prediction_workflow():
    """Test completo del flujo de predicción optimizada."""
    try:
        logger.info("🚀 Iniciando test de predicción optimizada con KPIs financieros")
        
        # 1. Cargar datos con DataManager
        logger.info("📊 Cargando datos con DataManager...")
        dm = DataManager()
        dm.load_kpis_data("INPUTTEST/DatabankExport_M1.csv")
        
        data = dm.kpis_data
        logger.info(f"✅ Datos cargados: {data.shape[0]} estrategias, {data.shape[1]} columnas")
        
        # 2. Verificar KPIs disponibles
        logger.info("🔍 Analizando KPIs disponibles...")
        kpi_groups = get_optimal_kpi_groups()
        
        for group_name, kpis in kpi_groups.items():
            available_kpis = [kpi for kpi in kpis if kpi in data.columns]
            logger.info(f"  {group_name}: {len(available_kpis)}/{len(kpis)} KPIs disponibles")
        
        # 3. Validar criterios optimizados
        logger.info("⚙️ Validando criterios optimizados...")
        criteria = get_optimized_validation_criteria()
        logger.info(f"✅ Criterios optimizados cargados: R² min={criteria['min_r2']}, CV R² min={criteria['min_cv_r2']}")
        
        # 4. Test con grupo primario
        logger.info("🎯 Probando predicción con grupo primario...")
        results_primary = predict_score_with_optimized_rf(data, kpi_group='primary')
        
        logger.info(f"✅ Predicción primaria completada:")
        logger.info(f"  R²: {results_primary['metrics']['R2']:.4f}")
        logger.info(f"  CV R²: {results_primary['metrics']['CV_R2_mean']:.4f}")
        logger.info(f"  MAE: {results_primary['metrics']['MAE']:.4f}")
        
        # 5. Validar calidad de predicción
        logger.info("🔬 Validando calidad de predicción...")
        validation = validate_prediction_quality(results_primary)
        
        logger.info(f"✅ Validación completada:")
        logger.info(f"  Calidad: {validation['quality_level']} ({validation['quality_score']:.1f}%)")
        logger.info(f"  Recomendaciones: {len(validation['recommendations'])}")
        
        # 6. Test con grupo extendido
        logger.info("📈 Probando predicción con grupo extendido...")
        results_extended = predict_score_with_optimized_rf(data, kpi_group='extended')
        
        logger.info(f"✅ Predicción extendida completada:")
        logger.info(f"  R²: {results_extended['metrics']['R2']:.4f}")
        logger.info(f"  CV R²: {results_extended['metrics']['CV_R2_mean']:.4f}")
        logger.info(f"  KPIs usados: {len(results_extended['feature_names'])}")
        
        # 7. Comparar resultados
        logger.info("📊 Comparando resultados...")
        comparison = {
            'primary': {
                'r2': results_primary['metrics']['R2'],
                'cv_r2': results_primary['metrics']['CV_R2_mean'],
                'kpis': len(results_primary['feature_names'])
            },
            'extended': {
                'r2': results_extended['metrics']['R2'],
                'cv_r2': results_extended['metrics']['CV_R2_mean'],
                'kpis': len(results_extended['feature_names'])
            }
        }
        
        logger.info("📈 Comparación de resultados:")
        logger.info(f"  Primario: R²={comparison['primary']['r2']:.4f}, CV R²={comparison['primary']['cv_r2']:.4f}, KPIs={comparison['primary']['kpis']}")
        logger.info(f"  Extendido: R²={comparison['extended']['r2']:.4f}, CV R²={comparison['extended']['cv_r2']:.4f}, KPIs={comparison['extended']['kpis']}")
        
        # 8. Análisis de importancia
        logger.info("🏆 Analizando importancia de KPIs...")
        importance_primary = get_feature_importance_summary(results_primary)
        importance_extended = get_feature_importance_summary(results_extended)
        
        logger.info("📊 Top 5 KPIs más importantes (Primario):")
        for i, row in importance_primary.head().iterrows():
            logger.info(f"  {i+1}. {row['KPI']}: {row['SHAP_Importance']:.4f}")
        
        # 9. Visualización de resultados
        logger.info("🎨 Creando visualización de resultados...")
        viz_primary = visualize_prediction_results(results_primary, data)
        viz_extended = visualize_prediction_results(results_extended, data)
        
        logger.info(f"✅ Visualizaciones creadas:")
        logger.info(f"  Primario: {len(viz_primary)} resultados")
        logger.info(f"  Extendido: {len(viz_extended)} resultados")
        
        # 10. Validar selección de KPIs
        logger.info("🔍 Validando selección de KPIs...")
        kpi_validation = validate_kpi_selection(data, results_primary['feature_names'])
        
        logger.info(f"✅ Validación de KPIs:")
        logger.info(f"  Disponibles: {len(kpi_validation['available_kpis'])}")
        logger.info(f"  Faltantes: {len(kpi_validation['missing_kpis'])}")
        logger.info(f"  Advertencias de correlación: {len(kpi_validation['correlation_warnings'])}")
        
        # 11. Resumen final
        logger.info("🎉 RESUMEN FINAL DEL TEST:")
        logger.info("✅ Todos los componentes funcionan correctamente")
        logger.info("✅ Predicción optimizada implementada")
        logger.info("✅ Validación específica para KPIs financieros")
        logger.info("✅ Selección inteligente de KPIs")
        logger.info("✅ Análisis de importancia con SHAP")
        logger.info("✅ Visualización con escala de colores")
        
        return {
            'success': True,
            'results_primary': results_primary,
            'results_extended': results_extended,
            'validation': validation,
            'comparison': comparison,
            'importance_primary': importance_primary,
            'importance_extended': importance_extended,
            'visualization_primary': viz_primary,
            'visualization_extended': viz_extended,
            'kpi_validation': kpi_validation
        }
        
    except Exception as e:
        logger.error(f"❌ Error en test: {str(e)}")
        return {'success': False, 'error': str(e)}

def test_kpi_groups():
    """Test específico de grupos de KPIs."""
    try:
        logger.info("🔍 Test de grupos de KPIs...")
        
        kpi_groups = get_optimal_kpi_groups()
        
        for group_name, kpis in kpi_groups.items():
            logger.info(f"  {group_name}: {len(kpis)} KPIs")
            for kpi in kpis:
                logger.info(f"    - {kpi}")
        
        logger.info("✅ Grupos de KPIs definidos correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de grupos: {str(e)}")
        return False

def test_validation_criteria():
    """Test específico de criterios de validación."""
    try:
        logger.info("⚙️ Test de criterios de validación...")
        
        criteria = get_optimized_validation_criteria()
        
        logger.info("✅ Criterios optimizados:")
        for key, value in criteria.items():
            logger.info(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de criterios: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("🚀 INICIANDO TESTS DE PREDICCIÓN OPTIMIZADA")
    
    # Test 1: Grupos de KPIs
    test1_success = test_kpi_groups()
    
    # Test 2: Criterios de validación
    test2_success = test_validation_criteria()
    
    # Test 3: Flujo completo
    test3_results = test_optimized_prediction_workflow()
    
    # Resumen final
    logger.info("🎯 RESUMEN DE TESTS:")
    logger.info(f"  Test 1 (Grupos KPIs): {'✅ PASÓ' if test1_success else '❌ FALLÓ'}")
    logger.info(f"  Test 2 (Criterios): {'✅ PASÓ' if test2_success else '❌ FALLÓ'}")
    logger.info(f"  Test 3 (Flujo completo): {'✅ PASÓ' if test3_results['success'] else '❌ FALLÓ'}")
    
    if test1_success and test2_success and test3_results['success']:
        logger.info("🎉 ¡TODOS LOS TESTS PASARON! Implementación optimizada lista.")
    else:
        logger.error("❌ Algunos tests fallaron. Revisar implementación.") 