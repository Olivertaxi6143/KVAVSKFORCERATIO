#!/usr/bin/env python3
"""
Script de testing para la función de predicción avanzada con Random Forest.
Valida la implementación completa sin afectar el flujo principal.
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

def test_prediction_workflow():
    """Test completo del flujo de predicción."""
    try:
        logger.info("🚀 Iniciando test de predicción avanzada")
        
        # 1. Cargar datos de prueba
        logger.info("📊 Cargando datos de prueba...")
        dm = DataManager()
        
        # Usar archivos de prueba estándar
        kpis_file = "DatabankExport_M1.csv"
        market_file = "DATOSMQL5.csv"
        
        if not os.path.exists(kpis_file):
            logger.error(f"❌ Archivo {kpis_file} no encontrado")
            return False
            
        dm.load_kpis_data(kpis_file)
        dm.load_market_data(market_file)
        
        logger.info(f"✅ Datos cargados: {len(dm.kpis_data)} estrategias")
        
        # 2. Simular selección de KPIs (KPIs más relevantes)
        selected_kpis = [
            'Profit_Factor', 
            'Sharpe_Ratio', 
            'Max_Drawdown', 
            'Win_Rate',
            'Total_Net_Profit',
            'Recovery_Factor'
        ]
        
        # Verificar que los KPIs existen
        available_kpis = [kpi for kpi in selected_kpis if kpi in dm.kpis_data.columns]
        if len(available_kpis) < 2:
            logger.error("❌ No hay suficientes KPIs disponibles para predicción")
            return False
            
        logger.info(f"✅ KPIs seleccionados: {available_kpis}")
        
        # 3. Ejecutar predicción
        logger.info("🔮 Ejecutando predicción con Random Forest...")
        results = predict_score_with_rf(
            data=dm.kpis_data,
            selected_kpis=available_kpis,
            target_score='QVA_Score'
        )
        
        # 4. Validar métricas básicas
        metrics = results['metrics']
        logger.info(f"📈 Métricas obtenidas:")
        logger.info(f"   - R²: {metrics['R2']:.4f}")
        logger.info(f"   - MAE: {metrics['MAE']:.4f}")
        logger.info(f"   - RMSE: {metrics['RMSE']:.4f}")
        logger.info(f"   - MAPE: {metrics['MAPE']:.2f}%")
        logger.info(f"   - CV R²: {metrics['CV_R2_mean']:.4f}")
        
        # 5. Validaciones críticas
        assert metrics['R2'] > 0.3, f"R² ({metrics['R2']:.4f}) debe ser > 0.3"
        assert metrics['CV_R2_mean'] > 0.2, f"CV R² ({metrics['CV_R2_mean']:.4f}) debe ser > 0.2"
        assert len(results['predictions']) == len(dm.kpis_data), "Número de predicciones incorrecto"
        
        # 6. Test de visualización
        logger.info("🎨 Probando visualización...")
        viz_results = visualize_prediction_results(results, dm.kpis_data)
        
        assert len(viz_results) == len(dm.kpis_data), "Visualización incorrecta"
        assert 'Quality_Label' in viz_results.columns, "Columna de calidad faltante"
        
        # 7. Test de validación de calidad
        logger.info("🔍 Validando calidad del modelo...")
        validation = validate_prediction_quality(results)
        
        logger.info(f"✅ Validaciones: {validation}")
        
        # 8. Test de importancia de características
        importance_df = get_feature_importance_summary(results)
        
        assert len(importance_df) == len(available_kpis), "Importancia de características incorrecta"
        logger.info("📊 Importancia de características:")
        for _, row in importance_df.iterrows():
            logger.info(f"   - {row['KPI']}: {row['SHAP_Importance']:.4f}")
        
        logger.info("✅ Test de predicción completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de predicción: {str(e)}")
        return False

def test_integration_with_gui():
    """Test de integración con la GUI (simulado)."""
    try:
        logger.info("🖥️ Probando integración con GUI...")
        
        # Simular datos que vendrían de la GUI
        dm = DataManager()
        dm.load_kpis_data("DatabankExport_M1.csv")
        
        # Simular KPIs seleccionados por usuario
        selected_kpis = ['Profit_Factor', 'Sharpe_Ratio', 'Max_Drawdown']
        
        # Simular ejecución desde GUI
        results = predict_score_with_rf(
            data=dm.kpis_data,
            selected_kpis=selected_kpis
        )
        
        # Simular display en GUI
        output = f"""
=== RESULTADOS PREDICCIÓN RANDOM FOREST ===

MÉTRICAS DE EVALUACIÓN:
- R² Score: {results['metrics']['R2']:.4f}
- MAE: {results['metrics']['MAE']:.4f}
- RMSE: {results['metrics']['RMSE']:.4f}
- MAPE: {results['metrics']['MAPE']:.2f}%
- CV R² (Media): {results['metrics']['CV_R2_mean']:.4f}
- CV R² (Std): {results['metrics']['CV_R2_std']:.4f}

MEJORES HIPERPARÁMETROS:
{results['metrics']['best_params']}

IMPORTANCIA DE VARIABLES (SHAP):
"""
        
        # Añadir importancia de variables
        importance_df = get_feature_importance_summary(results)
        for _, row in importance_df.iterrows():
            output += f"- {row['KPI']}: {row['SHAP_Importance']:.4f}\n"
        
        logger.info("✅ Integración con GUI simulada exitosamente")
        logger.info(f"📝 Output generado: {len(output)} caracteres")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en integración GUI: {str(e)}")
        return False

def test_error_handling():
    """Test de manejo de errores."""
    try:
        logger.info("🛡️ Probando manejo de errores...")
        
        # Test con datos insuficientes
        empty_data = pd.DataFrame({'KPI1': [], 'QVA_Score': []})
        
        try:
            predict_score_with_rf(empty_data, ['KPI1'])
            logger.error("❌ Debería haber fallado con datos vacíos")
            return False
        except Exception:
            logger.info("✅ Correctamente falló con datos vacíos")
        
        # Test con KPIs inexistentes
        dm = DataManager()
        dm.load_kpis_data("DatabankExport_M1.csv")
        
        try:
            predict_score_with_rf(dm.kpis_data, ['KPI_INEXISTENTE'])
            logger.error("❌ Debería haber fallado con KPIs inexistentes")
            return False
        except Exception:
            logger.info("✅ Correctamente falló con KPIs inexistentes")
        
        logger.info("✅ Manejo de errores correcto")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de manejo de errores: {str(e)}")
        return False

def main():
    """Función principal de testing."""
    logger.info("🧪 INICIANDO SUITE DE TESTING DE PREDICCIÓN AVANZADA")
    
    tests = [
        ("Test de flujo de predicción", test_prediction_workflow),
        ("Test de integración GUI", test_integration_with_gui),
        ("Test de manejo de errores", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Ejecutando: {test_name}")
        logger.info(f"{'='*50}")
        
        if test_func():
            logger.info(f"✅ {test_name}: PASÓ")
            passed += 1
        else:
            logger.error(f"❌ {test_name}: FALLÓ")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"RESUMEN: {passed}/{total} tests pasaron")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 TODOS LOS TESTS PASARON - IMPLEMENTACIÓN LISTA")
        return True
    else:
        logger.error("💥 ALGUNOS TESTS FALLARON - REVISAR IMPLEMENTACIÓN")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 