#!/usr/bin/env python3
"""
Script de debug para diagnosticar problemas con PredictabilityAnalyzer
"""

import pandas as pd
import numpy as np
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_predictability_analyzer():
    """Test específico para PredictabilityAnalyzer"""
    try:
        from src.core.predictability_analyzer import PredictabilityAnalyzer
        
        # Crear DataFrame con columnas numéricas
        df = pd.DataFrame({
            0: [0.287967, 0.000000, 0.530213, 0.038884, 1.000000],
            1: [1.2, 1.1, 1.3, 1.0, 1.4],
            2: [0.15, 0.14, 0.16, 0.13, 0.17]
        })
        
        print(f"DataFrame creado: {df.shape}")
        print(f"Columnas: {df.columns.tolist()}")
        print(f"Tipos de columnas: {[type(col) for col in df.columns]}")
        
        analyzer = PredictabilityAnalyzer()
        
        # Test _identify_is_oos_pairs
        pairs = analyzer._identify_is_oos_pairs(df)
        print(f"Pares IS/OOS encontrados: {pairs}")
        
        # Test analyze_is_oos_correlations
        results = analyzer.analyze_is_oos_correlations(df)
        print(f"Resultados de análisis: {results}")
        
        print("✅ PredictabilityAnalyzer funciona correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en PredictabilityAnalyzer: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_market_regime_analyzer():
    """Test específico para MarketRegimeAnalyzer"""
    try:
        from src.core.market_regime_analyzer import MarketRegimeDetector
        
        # Crear datos de prueba
        df = pd.DataFrame({
            0: np.random.randn(100),
            1: np.random.randn(100),
            2: np.random.randn(100)
        })
        
        print(f"DataFrame de mercado creado: {df.shape}")
        print(f"Columnas: {df.columns.tolist()}")
        
        detector = MarketRegimeDetector()
        
        # Test extract_market_features
        features = detector.extract_market_features(df)
        print(f"Características extraídas: {features.shape}")
        
        print("✅ MarketRegimeDetector funciona correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en MarketRegimeDetector: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_layer():
    """Test específico para IntegrationLayer"""
    try:
        from src.core.integration_layer import run_complete_analysis_with_gui_integration
        
        # Crear DataFrame de prueba
        df = pd.DataFrame({
            'Strategy_Name': [f"strat{i}" for i in range(5)],
            'Sharpe_Ratio': [1.2, 1.1, 1.3, 1.0, 1.4],
            'CAGR': [0.15, 0.14, 0.16, 0.13, 0.17],
            'Max_DD_%': [10, 12, 9, 11, 8],
            'Profit_factor': [1.5, 1.6, 1.4, 1.7, 1.8]
        })
        
        print(f"DataFrame de integración creado: {df.shape}")
        
        result, info = run_complete_analysis_with_gui_integration(df)
        print(f"Resultado de integración: {result.shape}")
        print(f"Columnas en resultado: {list(result.columns)}")
        
        print("✅ IntegrationLayer funciona correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en IntegrationLayer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Iniciando diagnóstico de problemas...")
    
    test1 = test_predictability_analyzer()
    test2 = test_market_regime_analyzer()
    test3 = test_integration_layer()
    
    print("\n📊 Resumen de diagnóstico:")
    print(f"PredictabilityAnalyzer: {'✅' if test1 else '❌'}")
    print(f"MarketRegimeDetector: {'✅' if test2 else '❌'}")
    print(f"IntegrationLayer: {'✅' if test3 else '❌'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 Todos los componentes funcionan correctamente")
    else:
        print("\n⚠️ Algunos componentes necesitan corrección") 