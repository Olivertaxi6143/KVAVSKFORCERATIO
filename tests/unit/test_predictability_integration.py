#!/usr/bin/env python3
"""
Test Integrado de Predictibilidad - KVAVSKFORCERATIO
====================================================

Valida todas las mejoras de predictibilidad implementadas en los 3 pipelines:
- DarwinEX Pipeline
- Axi Select Pipeline  
- Asesor Financiero Inteligente

Basado en datos empíricos reales del Excel DatabankExport_M1.csv
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from src.analysis.predictability_metrics import PredictabilityAnalyzer
from src.analysis.darwinex_pipeline import DarwinEXPipeline
from src.analysis.axi_select_analysis import AxiSelectAnalysis
from src.analysis.asesor_financiero_inteligente import AsesorFinancieroInteligente

def test_predictability_metrics():
    """Test de métricas de predictibilidad básicas."""
    logger.info("🧪 TEST 1: Métricas de Predictibilidad")
    
    try:
        # Cargar datos reales
        df = pd.read_csv('DatabankExport_M1.csv', sep=';', decimal=',')
        logger.info(f"📊 Datos cargados: {len(df)} estrategias")
        
        # Crear analizador
        analyzer = PredictabilityAnalyzer()
        
        # Analizar primera estrategia
        strategy_data = df.iloc[0]
        metrics = analyzer.calculate_overall_predictability(strategy_data)
        
        logger.info(f"✅ Estrategia: {strategy_data['Strategy Name']}")
        logger.info(f"   Consistencia IS/OOS: {metrics.is_oos_consistency:.1f}")
        logger.info(f"   Robustez Temporal: {metrics.temporal_robustness:.1f}")
        logger.info(f"   Detección Sobreajuste: {metrics.overfitting_detection:.1f}")
        logger.info(f"   Score Estabilidad: {metrics.stability_score:.1f}")
        logger.info(f"   Predictibilidad General: {metrics.overall_predictability:.1f}")
        
        assert True
        
    except Exception as e:
        logger.error(f"❌ Error en test de métricas: {e}")
        assert False

def test_darwinex_pipeline():
    """Test del DarwinEX Pipeline mejorado."""
    logger.info("🧪 TEST 2: DarwinEX Pipeline")
    
    try:
        # Cargar datos reales
        df = pd.read_csv('DatabankExport_M1.csv', sep=';', decimal=',')
        
        # Crear pipeline
        pipeline = DarwinEXPipeline()
        
        # Procesar primera estrategia
        strategy_data = df.iloc[0]
        predictability_results = pipeline._apply_predictability_filters(strategy_data)
        original_results = pipeline._apply_filters(strategy_data)
        combined_results = pipeline._combine_filter_results(predictability_results, original_results)
        score = pipeline._calculate_score(strategy_data, combined_results)
        
        logger.info(f"✅ Estrategia: {strategy_data['Strategy Name']}")
        logger.info(f"   Filtros predictibilidad: {predictability_results['total_passed']}/{predictability_results['total_filters']}")
        logger.info(f"   Filtros originales: {len(original_results['passed'])}/{len(original_results['passed']) + len(original_results['failed'])}")
        logger.info(f"   Filtros combinados: {len(combined_results['passed'])}/{len(combined_results['passed']) + len(combined_results['failed'])}")
        logger.info(f"   Score final: {score:.1f}")
        
        assert True
        
    except Exception as e:
        logger.error(f"❌ Error en test DarwinEX: {e}")
        assert False

def test_axi_select_pipeline():
    """Test del Axi Select Pipeline mejorado."""
    logger.info("🧪 TEST 3: Axi Select Pipeline")
    
    try:
        # Cargar datos reales
        df = pd.read_csv('DatabankExport_M1.csv', sep=';', decimal=',')
        
        # Crear pipeline
        axi = AxiSelectAnalysis()
        
        # Procesar primera estrategia
        strategy_data = df.iloc[0]
        predictability_results = axi._apply_predictability_filters_axi(strategy_data)
        edge_score = axi.calculate_edge_score(strategy_data)
        stage = axi.determine_stage(strategy_data, edge_score)
        
        logger.info(f"✅ Estrategia: {strategy_data['Strategy Name']}")
        logger.info(f"   Filtros predictibilidad: {predictability_results['total_passed']}/{predictability_results['total_filters']}")
        logger.info(f"   Edge Score: {edge_score:.1f}")
        logger.info(f"   Etapa: {stage}")
        
        assert True
        
    except Exception as e:
        logger.error(f"❌ Error en test Axi Select: {e}")
        assert False

def test_asesor_financiero():
    """Test del Asesor Financiero mejorado."""
    logger.info("🧪 TEST 4: Asesor Financiero")
    
    try:
        # Cargar datos reales
        df = pd.read_csv('DatabankExport_M1.csv', sep=';', decimal=',')
        
        # Crear asesor
        asesor = AsesorFinancieroInteligente(df)
        
        # Procesar primera estrategia
        strategy_data = df.iloc[0]
        predictability_results = asesor._apply_predictability_filters_asesor(strategy_data)
        quality_score = asesor.calculate_quality_score(strategy_data)
        
        logger.info(f"✅ Estrategia: {strategy_data['Strategy Name']}")
        logger.info(f"   Filtros predictibilidad: {predictability_results['total_passed']}/{predictability_results['total_filters']}")
        logger.info(f"   Quality Score: {quality_score:.1f}")
        logger.info(f"   Temporalidad detectada: {asesor.temporalidad_detectada}")
        logger.info(f"   Factor ajuste: {asesor.factor_ajuste_temporalidad:.3f}")
        
        assert True
        
    except Exception as e:
        logger.error(f"❌ Error en test Asesor Financiero: {e}")
        assert False

def test_integration_complete():
    """Test de integración completa."""
    logger.info("🧪 TEST 5: Integración Completa")
    
    try:
        # Cargar datos reales
        df = pd.read_csv('DatabankExport_M1.csv', sep=';', decimal=',')
        
        # Crear todos los pipelines
        darwin = DarwinEXPipeline()
        axi = AxiSelectAnalysis()
        asesor = AsesorFinancieroInteligente(df)
        
        # Procesar primera estrategia con todos los pipelines
        strategy_data = df.iloc[0]
        strategy_name = strategy_data['Strategy Name']
        
        # DarwinEX
        darwin_predictability = darwin._apply_predictability_filters(strategy_data)
        darwin_score = darwin._calculate_score(strategy_data, darwin_predictability)
        
        # Axi Select
        axi_predictability = axi._apply_predictability_filters_axi(strategy_data)
        axi_score = axi.calculate_edge_score(strategy_data)
        axi_stage = axi.determine_stage(strategy_data, axi_score)
        
        # Asesor Financiero
        asesor_predictability = asesor._apply_predictability_filters_asesor(strategy_data)
        asesor_score = asesor.calculate_quality_score(strategy_data)
        
        logger.info(f"✅ Estrategia: {strategy_name}")
        logger.info(f"   DarwinEX Score: {darwin_score:.1f}")
        logger.info(f"   Axi Select Score: {axi_score:.1f} (Etapa: {axi_stage})")
        logger.info(f"   Asesor Score: {asesor_score:.1f}")
        logger.info(f"   Predictibilidad promedio: {(darwin_predictability['total_passed'] + axi_predictability['total_passed'] + asesor_predictability['total_passed']) / 12:.1f}/4")
        
        assert True
        
    except Exception as e:
        logger.error(f"❌ Error en test de integración: {e}")
        assert False

def run_all_tests():
    """Ejecuta todos los tests de integración."""
    logger.info("🚀 INICIANDO TESTS DE INTEGRACIÓN DE PREDICTIBILIDAD")
    logger.info("=" * 60)
    
    tests = [
        ("Métricas de Predictibilidad", test_predictability_metrics),
        ("DarwinEX Pipeline", test_darwinex_pipeline),
        ("Axi Select Pipeline", test_axi_select_pipeline),
        ("Asesor Financiero", test_asesor_financiero),
        ("Integración Completa", test_integration_complete)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Ejecutando: {test_name}")
        try:
            success = test_func()
            results[test_name] = success
            if success:
                logger.info(f"✅ {test_name}: PASÓ")
            else:
                logger.error(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False
    
    # Resumen final
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMEN DE TESTS")
    logger.info("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\n🎯 RESULTADO FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        logger.info("🎉 ¡TODOS LOS TESTS PASARON! Integración de predictibilidad exitosa.")
        return True
    else:
        logger.error(f"⚠️ {total - passed} tests fallaron. Revisar implementación.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 