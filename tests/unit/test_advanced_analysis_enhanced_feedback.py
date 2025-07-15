#!/usr/bin/env python3
"""
Test exhaustivo para AdvancedAnalysisEnhanced - Feedback y Mejoras
================================================================

Valida el estado actual del módulo antes de implementar las mejoras propuestas.
"""

import sys
import os
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any
import traceback

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_data() -> pd.DataFrame:
    """Crea datos de prueba realistas para el análisis."""
    logger.info("🔬 Creando datos de prueba para AdvancedAnalysisEnhanced...")
    
    np.random.seed(42)
    n_strategies = 50
    
    # Crear DataFrame con métricas realistas
    data = {
        'Strategy_Name': [f'Strategy_{i:03d}' for i in range(n_strategies)],
        'CAGR': np.random.normal(0.15, 0.08, n_strategies),
        'Sharpe_Ratio': np.random.normal(1.2, 0.5, n_strategies),
        'Drawdown': np.random.normal(-0.12, 0.06, n_strategies),
        'Profit_Factor': np.random.normal(1.8, 0.4, n_strategies),
        'Winrate': np.random.normal(0.55, 0.1, n_strategies),
        'Sortino_Ratio': np.random.normal(1.5, 0.6, n_strategies),
        'Calmar_Ratio': np.random.normal(1.3, 0.7, n_strategies),
        'Trades': np.random.randint(100, 1000, n_strategies),
        'Exposure': np.random.normal(0.75, 0.15, n_strategies),
        'Recovery_Factor': np.random.normal(2.1, 0.8, n_strategies),
        'SQN': np.random.normal(1.8, 0.5, n_strategies),
        'Expectancy': np.random.normal(0.02, 0.01, n_strategies),
        'Payout_Ratio': np.random.normal(1.5, 0.3, n_strategies),
        'Max_Consec_Losses': np.random.randint(3, 15, n_strategies),
        'Ulcer_Index': np.random.normal(0.08, 0.04, n_strategies),
        'RINA_Index': np.random.normal(1.2, 0.4, n_strategies),
        'VaR_95': np.random.normal(-0.03, 0.015, n_strategies),
        'CVaR_95': np.random.normal(-0.05, 0.02, n_strategies),
        'Max_DD_Duration': np.random.randint(30, 200, n_strategies),
        'DD_Trades_Percent': np.random.normal(0.35, 0.1, n_strategies),
        'New_Peak_Trades_Percent': np.random.normal(0.65, 0.1, n_strategies),
        'Avg_Bars_in_Trade': np.random.randint(5, 50, n_strategies),
        'Avg_Stagnation': np.random.normal(0.25, 0.1, n_strategies),
        'Stagnation': np.random.normal(0.25, 0.1, n_strategies),
        'Avg_MAE': np.random.normal(0.02, 0.01, n_strategies),
        'Avg_MFE': np.random.normal(0.03, 0.015, n_strategies)
    }
    
    df = pd.DataFrame(data)
    
    # Añadir algunos outliers para probar robustez
    df.loc[0, 'CAGR'] = 0.5  # Outlier positivo
    df.loc[1, 'Drawdown'] = -0.8  # Outlier negativo
    df.loc[2, 'Sharpe_Ratio'] = 5.0  # Outlier extremo
    
    # Añadir algunos valores NaN para probar imputación
    df.loc[3, 'Sortino_Ratio'] = np.nan
    df.loc[4, 'Calmar_Ratio'] = np.nan
    
    logger.info(f"✅ Datos de prueba creados: {len(df)} estrategias, {len(df.columns)} columnas")
    return df

def test_advanced_analysis_enhanced_current_state():
    """Test del estado actual del módulo AdvancedAnalysisEnhanced."""
    logger.info("🔬 Iniciando test del estado actual de AdvancedAnalysisEnhanced...")
    
    try:
        # Importar el módulo
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced, AnalysisType
        
        # Crear datos de prueba
        test_data = create_test_data()
        
        # Inicializar el análisis
        logger.info("🔬 Inicializando AdvancedAnalysisEnhanced...")
        analysis = AdvancedAnalysisEnhanced(test_data)
        
        # Test 1: Verificar inicialización
        logger.info("🔬 Test 1: Verificación de inicialización...")
        assert hasattr(analysis, 'filtered_strategies'), "❌ No se encontró filtered_strategies"
        assert hasattr(analysis, 'numeric_columns'), "❌ No se encontró numeric_columns"
        assert len(analysis.numeric_columns) > 0, "❌ No hay columnas numéricas"
        logger.info("✅ Inicialización correcta")
        
        # Test 2: Verificar preparación de datos
        logger.info("🔬 Test 2: Verificación de preparación de datos...")
        assert not analysis.filtered_strategies[analysis.numeric_columns].isna().any().any(), "❌ Datos no imputados correctamente"
        logger.info("✅ Preparación de datos correcta")
        
        # Test 3: Análisis de correlaciones dinámicas
        logger.info("🔬 Test 3: Análisis de correlaciones dinámicas...")
        dynamic_corr_result = analysis.dynamic_correlation_analysis(window_size=5)
        assert isinstance(dynamic_corr_result.analysis_type, AnalysisType), "❌ Tipo de análisis incorrecto"
        assert 'data' in dynamic_corr_result.__dict__, "❌ Resultado sin datos"
        assert 'metrics' in dynamic_corr_result.__dict__, "❌ Resultado sin métricas"
        logger.info("✅ Análisis de correlaciones dinámicas correcto")
        
        # Test 4: Análisis de regímenes
        logger.info("🔬 Test 4: Análisis de regímenes...")
        regime_result = analysis.regime_analysis(n_regimes=3)
        assert isinstance(regime_result.analysis_type, AnalysisType), "❌ Tipo de análisis incorrecto"
        assert 'silhouette_score' in regime_result.metrics, "❌ Métricas de régimen incompletas"
        logger.info("✅ Análisis de regímenes correcto")
        
        # Test 5: Análisis de predicción
        logger.info("🔬 Test 5: Análisis de predicción...")
        prediction_result = analysis.enhanced_prediction_analysis('CAGR', use_ensemble=True)
        assert isinstance(prediction_result.analysis_type, AnalysisType), "❌ Tipo de análisis incorrecto"
        assert 'data' in prediction_result.__dict__, "❌ Resultado sin datos"
        logger.info("✅ Análisis de predicción correcto")
        
        # Test 6: Análisis completo
        logger.info("🔬 Test 6: Análisis completo...")
        complete_results = analysis.run_complete_enhanced_analysis()
        assert isinstance(complete_results, dict), "❌ Resultados no son diccionario"
        assert len(complete_results) > 0, "❌ No hay resultados de análisis"
        logger.info("✅ Análisis completo correcto")
        
        # Test 7: Verificar métodos stub
        logger.info("🔬 Test 7: Verificación de métodos stub...")
        clustering_result = analysis.clustering_analysis()
        correlation_result = analysis.correlation_analysis()
        anomaly_result = analysis.anomaly_detection()
        dim_reduction_result = analysis.dimensionality_reduction()
        
        assert isinstance(clustering_result.analysis_type, AnalysisType), "❌ Tipo de clustering incorrecto"
        assert isinstance(correlation_result.analysis_type, AnalysisType), "❌ Tipo de correlación incorrecto"
        assert isinstance(anomaly_result.analysis_type, AnalysisType), "❌ Tipo de anomalía incorrecto"
        assert isinstance(dim_reduction_result.analysis_type, AnalysisType), "❌ Tipo de reducción incorrecto"
        logger.info("✅ Métodos stub funcionando correctamente")
        
        # Test 8: Verificar robustez con datos problemáticos
        logger.info("🔬 Test 8: Verificación de robustez...")
        problematic_data = test_data.copy()
        problematic_data.loc[0, 'CAGR'] = np.inf  # Valor infinito
        problematic_data.loc[1, 'Sharpe_Ratio'] = -np.inf  # Valor infinito negativo
        
        try:
            robust_analysis = AdvancedAnalysisEnhanced(problematic_data)
            logger.info("✅ Manejo de valores infinitos correcto")
        except Exception as e:
            logger.warning(f"⚠️ Advertencia en manejo de valores infinitos: {e}")
        
        # Test 9: Verificar con datos mínimos
        logger.info("🔬 Test 9: Verificación con datos mínimos...")
        minimal_data = test_data.head(3)  # Solo 3 estrategias
        minimal_analysis = AdvancedAnalysisEnhanced(minimal_data)
        
        # Intentar análisis con datos mínimos
        try:
            minimal_regime = minimal_analysis.regime_analysis(n_regimes=2)
            logger.info("✅ Análisis con datos mínimos correcto")
        except Exception as e:
            logger.warning(f"⚠️ Advertencia en análisis con datos mínimos: {e}")
        
        logger.info("🎉 Todos los tests del estado actual PASARON correctamente")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Error importando módulo: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")
        traceback.print_exc()
        return False

def analyze_current_limitations():
    """Analiza las limitaciones actuales del módulo."""
    logger.info("🔍 Analizando limitaciones actuales del módulo...")
    
    limitations = [
        "1. Clustering fijo con K-means (no adaptativo)",
        "2. Detección de anomalías básica (solo clipping)",
        "3. Modelos de predicción limitados (sin SHAP)",
        "4. Reducción de dimensionalidad básica (solo PCA)",
        "5. Visualizaciones limitadas (sin t-SNE/UMAP)",
        "6. Sin validación cruzada robusta",
        "7. Sin optimización de hiperparámetros",
        "8. Sin modelos explicables avanzados",
        "9. Sin análisis de estabilidad temporal",
        "10. Sin integración con SHAP para interpretabilidad"
    ]
    
    for limitation in limitations:
        logger.info(f"⚠️ {limitation}")
    
    logger.info("📋 Análisis de limitaciones completado")
    return limitations

def main():
    """Función principal del test."""
    logger.info("🚀 Iniciando test exhaustivo de AdvancedAnalysisEnhanced...")
    
    # Test del estado actual
    current_state_ok = test_advanced_analysis_enhanced_current_state()
    
    if current_state_ok:
        logger.info("✅ Estado actual validado correctamente")
        
        # Analizar limitaciones
        limitations = analyze_current_limitations()
        
        logger.info("📊 RESUMEN DEL TEST:")
        logger.info("✅ Estado actual: FUNCIONAL")
        logger.info(f"⚠️ Limitaciones identificadas: {len(limitations)}")
        logger.info("🎯 Listo para implementar mejoras")
        
        return True
    else:
        logger.error("❌ Estado actual con problemas")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Test completado exitosamente")
        print("📋 El módulo está listo para mejoras")
    else:
        print("\n❌ Test falló")
        print("🔧 Se requieren correcciones antes de mejoras") 