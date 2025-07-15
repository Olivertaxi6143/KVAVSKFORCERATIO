#!/usr/bin/env python3
"""
Test comprehensivo de la integración AXI SELECT con KVAVSKFORCERATIO.

Este test valida:
1. Integración no intrusiva con el flujo actual
2. Análisis de estrategias para AXI SELECT
3. Generación de reportes
4. Integración con la GUI
5. Generación de recomendaciones
6. Manejo de errores y casos edge
"""

import sys
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_integration_initialization():
    """Test de inicialización de la integración."""
    try:
        logger.info("🧪 Test de inicialización de integración AXI SELECT")
        
        # Importar integración
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
        from src.ml.axi_select_integration import AxiSelectIntegration
        
        # Test inicialización básica
        integration = AxiSelectIntegration()
        assert integration is not None, "Integración no se inicializó correctamente"
        assert hasattr(integration, 'predictor'), "Integración no tiene predictor"
        assert hasattr(integration, 'is_loaded'), "Integración no tiene flag de carga"
        
        logger.info("✅ Test de inicialización completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de inicialización: {e}")
        return False

def test_basic_analysis():
    """Test de análisis básico de estrategias."""
    try:
        logger.info("🧪 Test de análisis básico de estrategias")
        
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
        from src.ml.axi_select_integration import AxiSelectIntegration
        
        integration = AxiSelectIntegration()
        
        # Crear datos de prueba
        test_data = pd.DataFrame({
            'Strategy_Name': [f'Strategy_{i}' for i in range(1, 11)],
            'CAGR': np.random.uniform(5, 25, 10),
            'Sharpe Ratio': np.random.uniform(0.5, 2.5, 10),
            'Max DD %': np.random.uniform(5, 20, 10),
            'Profit factor': np.random.uniform(1.2, 3.0, 10),
            'CalmarRatio': np.random.uniform(0.5, 2.0, 10),
            'Winning Percent': np.random.uniform(45, 75, 10),
            '# of trades': np.random.randint(50, 300, 10),
            'Avg. Bars in Trade': np.random.uniform(20, 80, 10),
            'Exposure': np.random.uniform(0.6, 0.95, 10),
            'Max Consec. Losses': np.random.randint(2, 8, 10),
            'Stagnation': np.random.uniform(0.05, 0.25, 10),
            'Ulcer Index %': np.random.uniform(1.0, 5.0, 10),
            'VaR (95%)': np.random.uniform(1.0, 4.0, 10),
            'Recovery Factor': np.random.uniform(0.5, 2.5, 10),
            'System Quality Number': np.random.uniform(0.5, 3.0, 10),
            'RINA Index': np.random.uniform(0.3, 0.9, 10),
            'Unified_Score': np.random.uniform(0.3, 0.95, 10),
            'Predictability_Score': np.random.uniform(0.4, 0.9, 10),
            'Robustness_Score': np.random.uniform(0.3, 0.85, 10)
        })
        
        # Realizar análisis
        analysis_results = integration.analyze_strategies_for_axi_select(test_data)
        
        # Validar estructura de resultados
        assert 'analysis_timestamp' in analysis_results, "Falta timestamp en resultados"
        assert 'total_strategies' in analysis_results, "Falta total de estrategias"
        assert 'strategies_analysis' in analysis_results, "Falta análisis de estrategias"
        assert 'phase_distribution' in analysis_results, "Falta distribución de fases"
        assert 'quarantine_status' in analysis_results, "Falta estado de cuarentena"
        
        # Validar datos específicos
        assert analysis_results['total_strategies'] == 10, "Número incorrecto de estrategias"
        assert len(analysis_results['strategies_analysis']) == 10, "Análisis incompleto"
        
        # Validar que cada estrategia tiene análisis
        for strategy_analysis in analysis_results['strategies_analysis']:
            assert 'strategy_name' in strategy_analysis, "Falta nombre de estrategia"
            assert 'current_phase' in strategy_analysis, "Falta fase actual"
            assert 'edge_score' in strategy_analysis, "Falta Edge Score"
            assert 'quarantine_status' in strategy_analysis, "Falta estado de cuarentena"
        
        logger.info("✅ Test de análisis básico completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de análisis básico: {e}")
        return False

def test_report_generation():
    """Test de generación de reportes."""
    try:
        logger.info("🧪 Test de generación de reportes")
        
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
        from src.ml.axi_select_integration import AxiSelectIntegration
        
        integration = AxiSelectIntegration()
        
        # Crear datos de prueba
        test_data = pd.DataFrame({
            'Strategy_Name': [f'Strategy_{i}' for i in range(1, 6)],
            'CAGR': [15.5, 12.0, 18.2, 22.1, 8.5],
            'Sharpe Ratio': [1.9, 1.2, 1.8, 2.2, 0.8],
            'Max DD %': [8.2, 9.5, 8.0, 7.5, 12.0],
            'Profit factor': [2.1, 1.6, 2.0, 2.5, 1.3],
            'CalmarRatio': [1.8, 1.2, 1.6, 2.1, 0.8],
            'Winning Percent': [65.2, 62.0, 68.0, 72.0, 55.0],
            '# of trades': [150, 45, 60, 80, 25],
            'Avg. Bars in Trade': [45, 35, 50, 60, 30],
            'Exposure': [0.85, 0.80, 0.85, 0.90, 0.75],
            'Max Consec. Losses': [3, 4, 3, 2, 5],
            'Stagnation': [0.12, 0.15, 0.10, 0.08, 0.20],
            'Ulcer Index %': [2.1, 2.8, 2.2, 1.8, 3.5],
            'VaR (95%)': [2.1, 2.8, 2.2, 1.8, 3.5],
            'Recovery Factor': [1.8, 1.3, 1.7, 2.1, 0.9],
            'System Quality Number': [2.1, 1.5, 1.9, 2.4, 1.0],
            'RINA Index': [0.87, 0.65, 0.78, 0.92, 0.45],
            'Unified_Score': [0.87, 0.65, 0.78, 0.92, 0.45],
            'Predictability_Score': [0.82, 0.70, 0.75, 0.88, 0.60],
            'Robustness_Score': [0.78, 0.65, 0.72, 0.85, 0.55]
        })
        
        # Realizar análisis
        analysis_results = integration.analyze_strategies_for_axi_select(test_data)
        
        # Generar reporte
        report = integration.generate_axi_select_report(analysis_results)
        
        # Validar reporte
        assert report is not None, "Reporte es None"
        assert len(report) > 0, "Reporte está vacío"
        assert "REPORTE AXI SELECT" in report, "Falta título del reporte"
        assert "ESTADÍSTICAS DE EDGE SCORE" in report, "Faltan estadísticas de Edge Score"
        assert "DISTRIBUCIÓN POR FASES" in report, "Falta distribución de fases"
        assert "ESTADO DE CUARENTENA" in report, "Falta estado de cuarentena"
        
        # Verificar que el reporte contiene datos reales
        assert "5 estrategias" in report or "5 estrategias analizadas" in report, "Falta información de estrategias"
        
        logger.info(f"✅ Reporte generado exitosamente: {len(report.split(chr(10)))} líneas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de generación de reportes: {e}")
        return False

def test_gui_integration():
    """Test de integración con la GUI."""
    try:
        logger.info("🧪 Test de integración con GUI")
        
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
        from src.ml.axi_select_integration import AxiSelectIntegration
        
        integration = AxiSelectIntegration()
        
        # Crear datos de prueba
        test_data = pd.DataFrame({
            'Strategy_Name': [f'Strategy_{i}' for i in range(1, 8)],
            'CAGR': [15.5, 12.0, 18.2, 22.1, 8.5, 25.0, 10.2],
            'Sharpe Ratio': [1.9, 1.2, 1.8, 2.2, 0.8, 2.5, 1.1],
            'Max DD %': [8.2, 9.5, 8.0, 7.5, 12.0, 6.0, 11.5],
            'Profit factor': [2.1, 1.6, 2.0, 2.5, 1.3, 2.8, 1.4],
            'CalmarRatio': [1.8, 1.2, 1.6, 2.1, 0.8, 2.3, 1.0],
            'Winning Percent': [65.2, 62.0, 68.0, 72.0, 55.0, 75.0, 58.0],
            '# of trades': [150, 45, 60, 80, 25, 100, 35],
            'Avg. Bars in Trade': [45, 35, 50, 60, 30, 55, 40],
            'Exposure': [0.85, 0.80, 0.85, 0.90, 0.75, 0.92, 0.78],
            'Max Consec. Losses': [3, 4, 3, 2, 5, 2, 4],
            'Stagnation': [0.12, 0.15, 0.10, 0.08, 0.20, 0.06, 0.18],
            'Ulcer Index %': [2.1, 2.8, 2.2, 1.8, 3.5, 1.5, 3.2],
            'VaR (95%)': [2.1, 2.8, 2.2, 1.8, 3.5, 1.5, 3.2],
            'Recovery Factor': [1.8, 1.3, 1.7, 2.1, 0.9, 2.4, 1.1],
            'System Quality Number': [2.1, 1.5, 1.9, 2.4, 1.0, 2.6, 1.2],
            'RINA Index': [0.87, 0.65, 0.78, 0.92, 0.45, 0.95, 0.52],
            'Unified_Score': [0.87, 0.65, 0.78, 0.92, 0.45, 0.95, 0.52],
            'Predictability_Score': [0.82, 0.70, 0.75, 0.88, 0.60, 0.90, 0.65],
            'Robustness_Score': [0.78, 0.65, 0.72, 0.85, 0.55, 0.88, 0.58]
        })
        
        # Integrar con GUI
        gui_data = integration.integrate_with_gui(test_data)
        
        # Validar estructura de datos para GUI
        assert 'axi_analysis' in gui_data, "Falta análisis AXI en datos GUI"
        assert 'gui_summary' in gui_data, "Falta resumen GUI"
        assert 'strategies_details' in gui_data, "Faltan detalles de estrategias"
        assert 'recommendations' in gui_data, "Faltan recomendaciones"
        
        # Validar resumen GUI
        gui_summary = gui_data['gui_summary']
        assert 'total_strategies' in gui_summary, "Falta total de estrategias en resumen"
        assert 'phase_distribution' in gui_summary, "Falta distribución de fases en resumen"
        assert 'quarantine_status' in gui_summary, "Falta estado de cuarentena en resumen"
        assert 'advancement_rate' in gui_summary, "Falta tasa de avance en resumen"
        assert 'average_edge_score' in gui_summary, "Falta Edge Score promedio en resumen"
        
        # Validar detalles de estrategias
        strategies_details = gui_data['strategies_details']
        assert len(strategies_details) == 7, "Número incorrecto de detalles de estrategias"
        
        for detail in strategies_details:
            assert 'name' in detail, "Falta nombre en detalle"
            assert 'phase' in detail, "Falta fase en detalle"
            assert 'edge_score' in detail, "Falta Edge Score en detalle"
            assert 'can_advance' in detail, "Falta flag de avance en detalle"
            assert 'quarantine_status' in detail, "Falta estado de cuarentena en detalle"
        
        # Validar recomendaciones
        recommendations = gui_data['recommendations']
        assert isinstance(recommendations, list), "Recomendaciones no es una lista"
        assert len(recommendations) > 0, "No hay recomendaciones"
        
        logger.info(f"✅ Integración con GUI completada: {len(strategies_details)} estrategias, {len(recommendations)} recomendaciones")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de integración con GUI: {e}")
        return False

def test_edge_cases():
    """Test de casos edge y manejo de errores."""
    try:
        logger.info("🧪 Test de casos edge y manejo de errores")
        
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
        from src.ml.axi_select_integration import AxiSelectIntegration
        
        integration = AxiSelectIntegration()
        
        # Test 1: DataFrame vacío
        logger.info("📊 Test con DataFrame vacío...")
        empty_df = pd.DataFrame()
        analysis_empty = integration.analyze_strategies_for_axi_select(empty_df)
        assert 'total_strategies' in analysis_empty, "Falta total de estrategias en análisis vacío"
        assert analysis_empty['total_strategies'] == 0, "Total de estrategias incorrecto para DataFrame vacío"
        
        # Test 2: DataFrame con datos faltantes
        logger.info("📊 Test con datos faltantes...")
        incomplete_df = pd.DataFrame({
            'Strategy_Name': ['Strategy_1', 'Strategy_2'],
            'CAGR': [15.5, np.nan],
            'Sharpe Ratio': [1.9, 1.2],
            'Max DD %': [np.nan, 9.5],
            'Profit factor': [2.1, 1.6]
        })
        analysis_incomplete = integration.analyze_strategies_for_axi_select(incomplete_df)
        assert len(analysis_incomplete['strategies_analysis']) == 2, "Análisis incompleto para datos faltantes"
        
        # Test 3: DataFrame con una sola estrategia
        logger.info("📊 Test con una sola estrategia...")
        single_df = pd.DataFrame({
            'Strategy_Name': ['Single_Strategy'],
            'CAGR': [20.0],
            'Sharpe Ratio': [2.0],
            'Max DD %': [7.0],
            'Profit factor': [2.5],
            'CalmarRatio': [2.0],
            'Winning Percent': [70.0],
            '# of trades': [100],
            'Avg. Bars in Trade': [50],
            'Exposure': [0.85],
            'Max Consec. Losses': [3],
            'Stagnation': [0.10],
            'Ulcer Index %': [2.0],
            'VaR (95%)': [2.0],
            'Recovery Factor': [2.0],
            'System Quality Number': [2.0],
            'RINA Index': [0.85],
            'Unified_Score': [0.85],
            'Predictability_Score': [0.80],
            'Robustness_Score': [0.75]
        })
        analysis_single = integration.analyze_strategies_for_axi_select(single_df)
        assert len(analysis_single['strategies_analysis']) == 1, "Análisis incorrecto para estrategia única"
        
        # Test 4: DataFrame con valores extremos
        logger.info("📊 Test con valores extremos...")
        extreme_df = pd.DataFrame({
            'Strategy_Name': ['Extreme_Strategy'],
            'CAGR': [100.0],  # Valor extremo
            'Sharpe Ratio': [5.0],  # Valor extremo
            'Max DD %': [50.0],  # Valor extremo
            'Profit factor': [10.0],  # Valor extremo
            'CalmarRatio': [10.0],  # Valor extremo
            'Winning Percent': [95.0],  # Valor extremo
            '# of trades': [1000],  # Valor extremo
            'Avg. Bars in Trade': [200],  # Valor extremo
            'Exposure': [0.99],  # Valor extremo
            'Max Consec. Losses': [20],  # Valor extremo
            'Stagnation': [0.01],  # Valor extremo
            'Ulcer Index %': [0.1],  # Valor extremo
            'VaR (95%)': [0.1],  # Valor extremo
            'Recovery Factor': [10.0],  # Valor extremo
            'System Quality Number': [10.0],  # Valor extremo
            'RINA Index': [0.99],  # Valor extremo
            'Unified_Score': [0.99],  # Valor extremo
            'Predictability_Score': [0.99],  # Valor extremo
            'Robustness_Score': [0.99]  # Valor extremo
        })
        analysis_extreme = integration.analyze_strategies_for_axi_select(extreme_df)
        assert len(analysis_extreme['strategies_analysis']) == 1, "Análisis incorrecto para valores extremos"
        
        logger.info("✅ Test de casos edge completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de casos edge: {e}")
        return False

def test_recommendations_generation():
    """Test de generación de recomendaciones."""
    try:
        logger.info("🧪 Test de generación de recomendaciones")
        
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
        from src.ml.axi_select_integration import AxiSelectIntegration
        
        integration = AxiSelectIntegration()
        
        # Crear diferentes escenarios de datos para probar recomendaciones
        scenarios = [
            # Escenario 1: Estrategias con bajo Edge Score
            {
                'name': 'Bajo Edge Score',
                'data': pd.DataFrame({
                    'Strategy_Name': [f'Low_Score_{i}' for i in range(1, 6)],
                    'CAGR': [5.0, 6.0, 4.0, 7.0, 5.5],
                    'Sharpe Ratio': [0.3, 0.4, 0.2, 0.5, 0.3],
                    'Max DD %': [15.0, 18.0, 20.0, 16.0, 17.0],
                    'Profit factor': [1.1, 1.2, 1.0, 1.3, 1.1],
                    'CalmarRatio': [0.3, 0.4, 0.2, 0.4, 0.3],
                    'Winning Percent': [45.0, 48.0, 42.0, 50.0, 46.0],
                    '# of trades': [30, 35, 25, 40, 32],
                    'Avg. Bars in Trade': [30, 35, 25, 40, 32],
                    'Exposure': [0.70, 0.75, 0.65, 0.80, 0.72],
                    'Max Consec. Losses': [5, 6, 7, 4, 5],
                    'Stagnation': [0.25, 0.30, 0.35, 0.20, 0.28],
                    'Ulcer Index %': [4.0, 5.0, 6.0, 3.5, 4.5],
                    'VaR (95%)': [3.5, 4.0, 4.5, 3.0, 3.8],
                    'Recovery Factor': [0.3, 0.4, 0.2, 0.4, 0.3],
                    'System Quality Number': [0.3, 0.4, 0.2, 0.4, 0.3],
                    'RINA Index': [0.25, 0.30, 0.20, 0.35, 0.28],
                    'Unified_Score': [0.25, 0.30, 0.20, 0.35, 0.28],
                    'Predictability_Score': [0.30, 0.35, 0.25, 0.40, 0.32],
                    'Robustness_Score': [0.25, 0.30, 0.20, 0.35, 0.28]
                })
            },
            # Escenario 2: Estrategias en cuarentena
            {
                'name': 'En Cuarentena',
                'data': pd.DataFrame({
                    'Strategy_Name': [f'Quarantine_{i}' for i in range(1, 4)],
                    'CAGR': [12.0, 15.0, 18.0],
                    'Sharpe Ratio': [1.5, 1.8, 2.0],
                    'Max DD %': [12.0, 15.0, 18.0],  # Drawdown alto
                    'Profit factor': [1.8, 2.0, 2.2],
                    'CalmarRatio': [1.2, 1.4, 1.6],
                    'Winning Percent': [65.0, 68.0, 70.0],
                    '# of trades': [80, 100, 120],
                    'Avg. Bars in Trade': [50, 60, 70],
                    'Exposure': [0.85, 0.88, 0.90],
                    'Max Consec. Losses': [3, 4, 3],
                    'Stagnation': [0.10, 0.08, 0.06],
                    'Ulcer Index %': [2.0, 1.8, 1.5],
                    'VaR (95%)': [2.0, 1.8, 1.5],
                    'Recovery Factor': [1.5, 1.7, 1.9],
                    'System Quality Number': [1.8, 2.0, 2.2],
                    'RINA Index': [0.75, 0.80, 0.85],
                    'Unified_Score': [0.75, 0.80, 0.85],
                    'Predictability_Score': [0.70, 0.75, 0.80],
                    'Robustness_Score': [0.65, 0.70, 0.75]
                })
            },
            # Escenario 3: Estrategias excelentes
            {
                'name': 'Excelentes',
                'data': pd.DataFrame({
                    'Strategy_Name': [f'Excellent_{i}' for i in range(1, 4)],
                    'CAGR': [25.0, 28.0, 30.0],
                    'Sharpe Ratio': [2.5, 2.8, 3.0],
                    'Max DD %': [6.0, 5.5, 5.0],
                    'Profit factor': [2.8, 3.0, 3.2],
                    'CalmarRatio': [2.5, 2.8, 3.0],
                    'Winning Percent': [75.0, 78.0, 80.0],
                    '# of trades': [150, 180, 200],
                    'Avg. Bars in Trade': [60, 70, 80],
                    'Exposure': [0.90, 0.92, 0.95],
                    'Max Consec. Losses': [2, 2, 1],
                    'Stagnation': [0.05, 0.04, 0.03],
                    'Ulcer Index %': [1.5, 1.2, 1.0],
                    'VaR (95%)': [1.5, 1.2, 1.0],
                    'Recovery Factor': [2.5, 2.8, 3.0],
                    'System Quality Number': [2.8, 3.0, 3.2],
                    'RINA Index': [0.90, 0.92, 0.95],
                    'Unified_Score': [0.90, 0.92, 0.95],
                    'Predictability_Score': [0.85, 0.88, 0.90],
                    'Robustness_Score': [0.80, 0.85, 0.88]
                })
            }
        ]
        
        for scenario in scenarios:
            logger.info(f"📊 Probando escenario: {scenario['name']}")
            
            # Analizar estrategias
            analysis_results = integration.analyze_strategies_for_axi_select(scenario['data'])
            
            # Generar recomendaciones
            recommendations = integration._generate_recommendations(analysis_results)
            
            # Validar recomendaciones
            assert isinstance(recommendations, list), f"Recomendaciones no es lista para {scenario['name']}"
            assert len(recommendations) > 0, f"No hay recomendaciones para {scenario['name']}"
            
            logger.info(f"✅ {scenario['name']}: {len(recommendations)} recomendaciones generadas")
        
        logger.info("✅ Test de generación de recomendaciones completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de recomendaciones: {e}")
        return False

def main():
    """Función principal del test comprehensivo de integración."""
    logger.info("🚀 Iniciando test comprehensivo de integración AXI SELECT")
    
    tests = [
        ("Inicialización de Integración", test_integration_initialization),
        ("Análisis Básico", test_basic_analysis),
        ("Generación de Reportes", test_report_generation),
        ("Integración con GUI", test_gui_integration),
        ("Casos Edge", test_edge_cases),
        ("Generación de Recomendaciones", test_recommendations_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 Ejecutando: {test_name}")
        logger.info(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASÓ")
            else:
                logger.error(f"❌ {test_name}: FALLÓ")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    logger.info(f"\n{'='*60}")
    logger.info("📊 RESUMEN DE TESTS DE INTEGRACIÓN AXI SELECT")
    logger.info(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n🎯 RESULTADO FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        logger.info("🎉 ¡TODOS LOS TESTS PASARON! Integración AXI SELECT completamente funcional.")
    else:
        logger.warning(f"⚠️ {total - passed} tests fallaron. Revisar implementación.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 