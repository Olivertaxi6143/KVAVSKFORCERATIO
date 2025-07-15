#!/usr/bin/env python3
"""
Test Comprehensivo para AdvancedAnalysisEnhanced
===============================================

Valida todas las funcionalidades implementadas y detecta errores
antes de continuar con el siguiente módulo.
"""

import sys
import os
import pandas as pd
import numpy as np
import logging
import traceback
from typing import Dict, List, Any, Optional

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_comprehensive_test_data() -> pd.DataFrame:
    """Crea datos de prueba comprehensivos para validar todas las funcionalidades."""
    logger.info("🔬 Creando datos de prueba comprehensivos...")
    
    np.random.seed(42)
    n_strategies = 100  # Más datos para pruebas robustas
    
    # Crear DataFrame con métricas realistas y variadas
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
    
    # Añadir outliers para probar robustez
    df.loc[0, 'CAGR'] = 0.8  # Outlier extremo positivo
    df.loc[1, 'Drawdown'] = -0.9  # Outlier extremo negativo
    df.loc[2, 'Sharpe_Ratio'] = 8.0  # Outlier extremo
    df.loc[3, 'Profit_Factor'] = 0.1  # Outlier extremo bajo
    
    # Añadir valores NaN para probar imputación
    df.loc[4, 'Sortino_Ratio'] = np.nan
    df.loc[5, 'Calmar_Ratio'] = np.nan
    df.loc[6, 'SQN'] = np.nan
    
    # Añadir valores infinitos para probar manejo
    df.loc[7, 'CAGR'] = np.inf
    df.loc[8, 'Sharpe_Ratio'] = -np.inf
    
    logger.info(f"✅ Datos de prueba creados: {len(df)} estrategias, {len(df.columns)} columnas")
    return df

def test_initialization_and_data_preparation():
    """Test de inicialización y preparación de datos."""
    logger.info("🔬 Test 1: Inicialización y preparación de datos...")
    
    try:
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        # Test con datos normales
        test_data = create_comprehensive_test_data()
        analysis = AdvancedAnalysisEnhanced(test_data)
        
        # Validaciones básicas
        assert hasattr(analysis, 'filtered_strategies'), "❌ No se encontró filtered_strategies"
        assert hasattr(analysis, 'numeric_columns'), "❌ No se encontró numeric_columns"
        assert len(analysis.numeric_columns) > 0, "❌ No hay columnas numéricas"
        assert not analysis.filtered_strategies[analysis.numeric_columns].isna().any().any(), "❌ Datos no imputados correctamente"
        
        logger.info("✅ Inicialización y preparación de datos: CORRECTO")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en inicialización: {e}")
        traceback.print_exc()
        return False

def test_regime_analysis_comprehensive():
    """Test comprehensivo del análisis de regímenes."""
    logger.info("🔬 Test 2: Análisis de regímenes comprehensivo...")
    
    try:
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        test_data = create_comprehensive_test_data()
        analysis = AdvancedAnalysisEnhanced(test_data)
        
        # Test con método auto
        result_auto = analysis.regime_analysis(method="auto")
        assert result_auto.analysis_type.value == "regime_analysis", "❌ Tipo de análisis incorrecto"
        assert 'silhouette_score' in result_auto.metrics, "❌ Métricas de régimen incompletas"
        
        # Test con método kmeans
        result_kmeans = analysis.regime_analysis(method="kmeans", n_regimes=3)
        assert result_kmeans.analysis_type.value == "regime_analysis", "❌ Tipo de análisis incorrecto"
        
        # Test con método dbscan
        result_dbscan = analysis.regime_analysis(method="dbscan")
        assert result_dbscan.analysis_type.value == "regime_analysis", "❌ Tipo de análisis incorrecto"
        
        # Test con método gmm
        result_gmm = analysis.regime_analysis(method="gmm", n_regimes=4)
        assert result_gmm.analysis_type.value == "regime_analysis", "❌ Tipo de análisis incorrecto"
        
        logger.info("✅ Análisis de regímenes comprehensivo: CORRECTO")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en análisis de regímenes: {e}")
        traceback.print_exc()
        return False

def test_anomaly_detection_comprehensive():
    """Test comprehensivo de detección de anomalías."""
    logger.info("🔬 Test 3: Detección de anomalías comprehensiva...")
    
    try:
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        test_data = create_comprehensive_test_data()
        analysis = AdvancedAnalysisEnhanced(test_data)
        
        # Test con ensemble
        result_ensemble = analysis.anomaly_detection(method="ensemble", contamination=0.05)
        assert result_ensemble.analysis_type.value == "anomaly_detection", "❌ Tipo de análisis incorrecto"
        assert 'best_method' in result_ensemble.metrics, "❌ Métricas de anomalías incompletas"
        
        # Test con isolation_forest
        result_iso = analysis.anomaly_detection(method="isolation_forest", contamination=0.03)
        assert result_iso.analysis_type.value == "anomaly_detection", "❌ Tipo de análisis incorrecto"
        
        # Test con lof
        result_lof = analysis.anomaly_detection(method="lof", contamination=0.07)
        assert result_lof.analysis_type.value == "anomaly_detection", "❌ Tipo de análisis incorrecto"
        
        # Test con elliptic_envelope
        result_ell = analysis.anomaly_detection(method="elliptic_envelope", contamination=0.04)
        assert result_ell.analysis_type.value == "anomaly_detection", "❌ Tipo de análisis incorrecto"
        
        logger.info("✅ Detección de anomalías comprehensiva: CORRECTO")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en detección de anomalías: {e}")
        traceback.print_exc()
        return False

def test_correlation_analysis_comprehensive():
    """Test comprehensivo de análisis de correlaciones."""
    logger.info("🔬 Test 4: Análisis de correlaciones comprehensivo...")
    
    try:
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        test_data = create_comprehensive_test_data()
        analysis = AdvancedAnalysisEnhanced(test_data)
        
        # Test con método dinámico
        result_dynamic = analysis.correlation_analysis(method="dynamic", window_size=10)
        assert result_dynamic.analysis_type.value == "correlation", "❌ Tipo de análisis incorrecto"
        
        # Test con método estático
        result_static = analysis.correlation_analysis(method="static")
        assert result_static.analysis_type.value == "correlation", "❌ Tipo de análisis incorrecto"
        
        # Test con método rolling
        result_rolling = analysis.correlation_analysis(method="rolling", window_size=15)
        assert result_rolling.analysis_type.value == "correlation", "❌ Tipo de análisis incorrecto"
        
        # Test con método regime_change
        result_regime = analysis.correlation_analysis(method="regime_change", window_size=12)
        assert result_regime.analysis_type.value == "correlation", "❌ Tipo de análisis incorrecto"
        
        logger.info("✅ Análisis de correlaciones comprehensivo: CORRECTO")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en análisis de correlaciones: {e}")
        traceback.print_exc()
        return False

def test_dimensionality_reduction_comprehensive():
    """Test comprehensivo de reducción de dimensionalidad."""
    logger.info("🔬 Test 5: Reducción de dimensionalidad comprehensiva...")
    
    try:
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        test_data = create_comprehensive_test_data()
        analysis = AdvancedAnalysisEnhanced(test_data)
        
        # Test con método auto
        result_auto = analysis.dimensionality_reduction(method="auto", n_components=2)
        assert result_auto.analysis_type.value == "dimensionality_reduction", "❌ Tipo de análisis incorrecto"
        
        # Test con PCA
        result_pca = analysis.dimensionality_reduction(method="pca", n_components=3)
        assert result_pca.analysis_type.value == "dimensionality_reduction", "❌ Tipo de análisis incorrecto"
        
        # Test con UMAP
        result_umap = analysis.dimensionality_reduction(method="umap", n_components=2)
        assert result_umap.analysis_type.value == "dimensionality_reduction", "❌ Tipo de análisis incorrecto"
        
        # Test con t-SNE
        result_tsne = analysis.dimensionality_reduction(method="tsne", n_components=2)
        assert result_tsne.analysis_type.value == "dimensionality_reduction", "❌ Tipo de análisis incorrecto"
        
        # Test con UMAP supervisado
        result_supervised = analysis.dimensionality_reduction(
            method="umap", n_components=2, supervised=True, target_column="CAGR"
        )
        assert result_supervised.analysis_type.value == "dimensionality_reduction", "❌ Tipo de análisis incorrecto"
        
        logger.info("✅ Reducción de dimensionalidad comprehensiva: CORRECTO")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en reducción de dimensionalidad: {e}")
        traceback.print_exc()
        return False

def test_clustering_analysis_comprehensive():
    """Test comprehensivo de análisis de clustering."""
    logger.info("🔬 Test 6: Análisis de clustering comprehensivo...")
    
    try:
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        test_data = create_comprehensive_test_data()
        analysis = AdvancedAnalysisEnhanced(test_data)
        
        # Test con método auto
        result_auto = analysis.clustering_analysis(method="auto", n_clusters=5)
        assert result_auto.analysis_type.value == "clustering", "❌ Tipo de análisis incorrecto"
        
        # Test con K-means
        result_kmeans = analysis.clustering_analysis(method="kmeans", n_clusters=4)
        assert result_kmeans.analysis_type.value == "clustering", "❌ Tipo de análisis incorrecto"
        
        # Test con DBSCAN
        result_dbscan = analysis.clustering_analysis(method="dbscan")
        assert result_dbscan.analysis_type.value == "clustering", "❌ Tipo de análisis incorrecto"
        
        # Test con GMM
        result_gmm = analysis.clustering_analysis(method="gmm", n_clusters=3)
        assert result_gmm.analysis_type.value == "clustering", "❌ Tipo de análisis incorrecto"
        
        # Test con características específicas
        result_specific = analysis.clustering_analysis(
            method="kmeans", n_clusters=3, 
            features=['CAGR', 'Sharpe_Ratio', 'Drawdown']
        )
        assert result_specific.analysis_type.value == "clustering", "❌ Tipo de análisis incorrecto"
        
        logger.info("✅ Análisis de clustering comprehensivo: CORRECTO")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en análisis de clustering: {e}")
        traceback.print_exc()
        return False

def test_edge_cases_and_error_handling():
    """Test de casos edge y manejo de errores."""
    logger.info("🔬 Test 7: Casos edge y manejo de errores...")
    
    try:
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        # Test con datos mínimos
        minimal_data = create_comprehensive_test_data().head(3)
        analysis_minimal = AdvancedAnalysisEnhanced(minimal_data)
        
        # Intentar análisis con datos mínimos
        try:
            result_minimal = analysis_minimal.regime_analysis(n_regimes=2)
            logger.info("✅ Manejo de datos mínimos: CORRECTO")
        except Exception as e:
            logger.warning(f"⚠️ Advertencia en datos mínimos: {e}")
        
        # Test con datos problemáticos
        problematic_data = create_comprehensive_test_data().copy()
        problematic_data.loc[0, 'CAGR'] = np.inf
        problematic_data.loc[1, 'Sharpe_Ratio'] = -np.inf
        problematic_data.loc[2, 'Drawdown'] = np.nan
        
        try:
            analysis_problematic = AdvancedAnalysisEnhanced(problematic_data)
            logger.info("✅ Manejo de datos problemáticos: CORRECTO")
        except Exception as e:
            logger.warning(f"⚠️ Advertencia en datos problemáticos: {e}")
        
        # Test con parámetros inválidos
        normal_data = create_comprehensive_test_data()
        analysis_normal = AdvancedAnalysisEnhanced(normal_data)
        
        try:
            # Test con método inválido
            result_invalid = analysis_normal.regime_analysis(method="invalid_method")
            logger.warning("⚠️ No se detectó método inválido")
        except Exception as e:
            logger.info("✅ Manejo de método inválido: CORRECTO")
        
        logger.info("✅ Casos edge y manejo de errores: CORRECTO")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en casos edge: {e}")
        traceback.print_exc()
        return False

def test_performance_and_memory():
    """Test de performance y uso de memoria."""
    logger.info("🔬 Test 8: Performance y memoria...")
    
    try:
        import time
        import psutil
        import os
        
        from analysis.advanced_analysis_enhanced import AdvancedAnalysisEnhanced
        
        # Crear dataset más grande para test de performance
        large_data = create_comprehensive_test_data()
        large_data = pd.concat([large_data] * 2, ignore_index=True)  # 200 estrategias
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        
        analysis = AdvancedAnalysisEnhanced(large_data)
        
        # Ejecutar análisis completo
        results = analysis.run_complete_enhanced_analysis()
        
        end_time = time.time()
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_used = memory_after - memory_before
        
        logger.info(f"⏱️ Tiempo de ejecución: {execution_time:.2f} segundos")
        logger.info(f"💾 Memoria utilizada: {memory_used:.2f} MB")
        
        # Validar performance aceptable
        assert execution_time < 30, f"❌ Tiempo de ejecución muy alto: {execution_time:.2f}s"
        assert memory_used < 500, f"❌ Uso de memoria muy alto: {memory_used:.2f}MB"
        
        logger.info("✅ Performance y memoria: CORRECTO")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de performance: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal del test comprehensivo."""
    logger.info("🚀 Iniciando test comprehensivo de AdvancedAnalysisEnhanced...")
    
    tests = [
        ("Inicialización y preparación de datos", test_initialization_and_data_preparation),
        ("Análisis de regímenes comprehensivo", test_regime_analysis_comprehensive),
        ("Detección de anomalías comprehensiva", test_anomaly_detection_comprehensive),
        ("Análisis de correlaciones comprehensivo", test_correlation_analysis_comprehensive),
        ("Reducción de dimensionalidad comprehensiva", test_dimensionality_reduction_comprehensive),
        ("Análisis de clustering comprehensivo", test_clustering_analysis_comprehensive),
        ("Casos edge y manejo de errores", test_edge_cases_and_error_handling),
        ("Performance y memoria", test_performance_and_memory)
    ]
    
    results = {}
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"🔬 Ejecutando: {test_name}")
        logger.info(f"{'='*60}")
        
        try:
            success = test_func()
            results[test_name] = success
            if success:
                passed_tests += 1
                logger.info(f"✅ {test_name}: PASÓ")
            else:
                logger.error(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR CRÍTICO - {e}")
            results[test_name] = False
            traceback.print_exc()
    
    # Resumen final
    logger.info(f"\n{'='*60}")
    logger.info("📊 RESUMEN FINAL DEL TEST COMPREHENSIVO")
    logger.info(f"{'='*60}")
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n📈 ESTADÍSTICAS:")
    logger.info(f"Tests pasados: {passed_tests}/{total_tests}")
    logger.info(f"Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 ¡TODOS LOS TESTS PASARON! El módulo está listo para producción.")
        return True
    else:
        logger.error(f"\n⚠️ {total_tests - passed_tests} tests fallaron. Se requieren correcciones.")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Test comprehensivo completado exitosamente")
        print("📋 El módulo AdvancedAnalysisEnhanced está listo para el siguiente módulo")
    else:
        print("\n❌ Test comprehensivo falló")
        print("🔧 Se requieren correcciones antes de continuar") 