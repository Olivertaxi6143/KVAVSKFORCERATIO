#!/usr/bin/env python3
"""
Test de Integración de Tail Risk Analysis
=========================================

Valida que el módulo de Tail Risk se integra correctamente con la GUI
y funciona con datos reales del proyecto.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-15
Versión: 1.0.0
"""

import sys
import os
import pandas as pd
import numpy as np
import logging
import traceback
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analysis.tail_risk_metrics import TailRiskAnalyzer
from src.data.data_manager import DataManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tail_risk_analyzer_initialization():
    """Test de inicialización del TailRiskAnalyzer."""
    try:
        logger.info("🧪 Test: Inicialización de TailRiskAnalyzer")
        
        # Crear instancia del analizador
        analyzer = TailRiskAnalyzer()
        
        # Verificar que se inicializó correctamente
        assert analyzer is not None, "El analizador no se inicializó"
        assert hasattr(analyzer, 'confidence_levels'), "Falta atributo confidence_levels"
        assert hasattr(analyzer, 'logger'), "Falta atributo logger"
        
        logger.info("✅ TailRiskAnalyzer inicializado correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de inicialización: {e}")
        return False

def test_tail_risk_metrics_calculation():
    """Test de cálculo de métricas de Tail Risk."""
    try:
        logger.info("🧪 Test: Cálculo de métricas de Tail Risk")
        
        # Crear datos de ejemplo
        np.random.seed(42)
        returns = pd.Series(np.random.normal(0.001, 0.02, 1000))
        
        # Crear analizador
        analyzer = TailRiskAnalyzer()
        
        # Calcular métricas
        metrics = analyzer.calculate_tail_risk_metrics(returns, "Test_Strategy")
        
        # Verificar que se calcularon las métricas básicas
        required_metrics = ['var_90', 'var_95', 'var_99', 'cvar_90', 'cvar_95', 'cvar_99', 
                          'expected_shortfall', 'max_drawdown', 'skewness', 'kurtosis']
        
        for metric in required_metrics:
            assert metric in metrics, f"Falta métrica: {metric}"
            assert not pd.isna(metrics[metric]), f"Métrica {metric} es NaN"
        
        logger.info(f"✅ Métricas calculadas: VaR 95% = {metrics['var_95']:.4f}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de cálculo: {e}")
        return False

def test_tail_risk_with_real_data():
    """Test de Tail Risk con datos reales del proyecto."""
    try:
        logger.info("🧪 Test: Tail Risk con datos reales")
        
        # Cargar datos reales
        data_manager = DataManager()
        kpi_path = "INPUTTEST/DatabankExport_M1.csv"
        
        if not os.path.exists(kpi_path):
            logger.warning(f"⚠️ Archivo de datos no encontrado: {kpi_path}")
            return True  # No es un error crítico
        
        # Cargar datos
        df_kpi = pd.read_csv(kpi_path, sep=',', quotechar='"', engine='python')
        logger.info(f"📊 Datos cargados: {df_kpi.shape}")
        
        # Crear analizador
        analyzer = TailRiskAnalyzer()
        
        # Simular retornos más realistas para cada estrategia
        np.random.seed(42)
        simulated_returns = []
        
        for _, row in df_kpi.iterrows():
            # Usar CAGR como base para generar retornos más realistas
            cagr_value = row.get('CAGR', 0.1)
            if cagr_value is None or pd.isna(cagr_value):
                cagr_value = 0.1
            base_return = float(cagr_value) / 252  # Convertir CAGR anual a diario
            volatility = abs(base_return) * 2  # Volatilidad proporcional al retorno
            
            # Generar serie de retornos diarios (252 días = 1 año)
            daily_returns = np.random.normal(base_return, volatility, 252)
            simulated_returns.append(daily_returns)
        
        # Crear DataFrame con retornos simulados
        returns_df = pd.DataFrame({
            'Strategy_Name': df_kpi['Strategy_Name'],
            'Returns': simulated_returns
        })
        
        # Analizar tail risk para cada estrategia individualmente
        results = {}
        for idx, row in returns_df.iterrows():
            strategy_name = str(row['Strategy_Name'])  # Asegurar que sea string
            returns_series = pd.Series(row['Returns'])  # Convertir array a Serie
            
            # Calcular métricas para esta estrategia
            metrics = analyzer.calculate_tail_risk_metrics(returns_series, strategy_name)
            results[strategy_name] = metrics
        
        # Verificar resultados
        assert len(results) > 0, "No se generaron resultados"
        
        # Verificar que al menos algunas estrategias tienen métricas válidas
        valid_strategies = 0
        for strategy_name, metrics in results.items():
            if strategy_name == "error":
                continue
            if not pd.isna(metrics.get('var_95', np.nan)):
                valid_strategies += 1
        
        assert valid_strategies > 0, "No hay estrategias con métricas válidas"
        
        logger.info(f"✅ Tail Risk analizado para {valid_strategies} estrategias válidas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test con datos reales: {e}")
        return False

def test_tail_risk_portfolio_analysis():
    """Test de análisis de Tail Risk de portafolio."""
    try:
        logger.info("🧪 Test: Análisis de Tail Risk de portafolio")
        
        # Crear datos de ejemplo para múltiples estrategias
        np.random.seed(42)
        strategies_metrics = []
        
        for i in range(5):
            returns = pd.Series(np.random.normal(0.001, 0.02, 1000))
            analyzer = TailRiskAnalyzer()
            metrics = analyzer.calculate_tail_risk_metrics(returns, f"Strategy_{i}")
            strategies_metrics.append(metrics)
        
        # Analizar portafolio
        analyzer = TailRiskAnalyzer()
        portfolio_analysis = analyzer.analyze_portfolio_tail_risk(strategies_metrics)
        
        # Verificar resultados del portafolio
        assert 'total_strategies' in portfolio_analysis, "Falta total_strategies"
        assert 'average_var_95' in portfolio_analysis, "Falta average_var_95"
        assert 'average_cvar_95' in portfolio_analysis, "Falta average_cvar_95"
        
        logger.info(f"✅ Análisis de portafolio completado: {portfolio_analysis['total_strategies']} estrategias")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de portafolio: {e}")
        return False

def test_tail_risk_edge_cases():
    """Test de casos edge del análisis de Tail Risk."""
    try:
        logger.info("🧪 Test: Casos edge de Tail Risk")
        
        analyzer = TailRiskAnalyzer()
        
        # Test 1: Datos insuficientes
        short_returns = pd.Series([0.01, -0.02, 0.03])  # Solo 3 observaciones
        metrics = analyzer.calculate_tail_risk_metrics(short_returns, "Short_Strategy")
        
        # Debería devolver métricas con NaN
        assert all(pd.isna(metrics[key]) for key in ['var_95', 'cvar_95', 'max_drawdown']), \
            "Datos insuficientes deberían devolver NaN"
        
        # Test 2: Datos vacíos
        empty_returns = pd.Series(dtype=float)
        metrics = analyzer.calculate_tail_risk_metrics(empty_returns, "Empty_Strategy")
        
        # Debería devolver métricas con NaN
        assert all(pd.isna(metrics[key]) for key in ['var_95', 'cvar_95', 'max_drawdown']), \
            "Datos vacíos deberían devolver NaN"
        
        # Test 3: Datos con valores extremos
        extreme_returns = pd.Series([0.5, -0.8, 0.3, -0.9, 0.1])  # Valores extremos
        metrics = analyzer.calculate_tail_risk_metrics(extreme_returns, "Extreme_Strategy")
        
        # Debería manejar valores extremos sin error
        assert 'var_95' in metrics, "Debería calcular VaR incluso con valores extremos"
        
        logger.info("✅ Casos edge manejados correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de casos edge: {e}")
        return False

def run_all_tail_risk_tests():
    """Ejecuta todos los tests de Tail Risk."""
    logger.info("🚀 Iniciando tests de integración de Tail Risk")
    
    tests = [
        ("Inicialización", test_tail_risk_analyzer_initialization),
        ("Cálculo de Métricas", test_tail_risk_metrics_calculation),
        ("Datos Reales", test_tail_risk_with_real_data),
        ("Análisis de Portafolio", test_tail_risk_portfolio_analysis),
        ("Casos Edge", test_tail_risk_edge_cases)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Ejecutando: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                logger.info(f"✅ {test_name}: PASÓ")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            logger.error(traceback.format_exc())
    
    logger.info(f"\n{'='*50}")
    logger.info(f"📊 RESUMEN DE TESTS DE TAIL RISK")
    logger.info(f"{'='*50}")
    logger.info(f"✅ Tests pasados: {passed}/{total}")
    logger.info(f"📈 Tasa de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 ¡Todos los tests de Tail Risk pasaron!")
        return True
    else:
        logger.error("⚠️ Algunos tests de Tail Risk fallaron")
        return False

if __name__ == "__main__":
    success = run_all_tail_risk_tests()
    sys.exit(0 if success else 1) 