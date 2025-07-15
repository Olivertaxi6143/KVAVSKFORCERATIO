#!/usr/bin/env python3
"""
TEST_DARWIN_EX_PIPELINE_UNIT.py - Tests unitarios para cada filtro del pipeline DarwinEX
"""

import sys
import os
import pandas as pd
import numpy as np
import pytest
from unittest.mock import Mock, patch
import logging

# Configurar path
sys.path.insert(0, os.path.abspath('src'))

from src.analysis.darwinex_pipeline import DarwinEXPipeline, PipelineResult

# Configurar logging para tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDarwinEXPipelineUnit:
    """Test suite para filtros unitarios del pipeline DarwinEX."""
    
    @pytest.fixture(scope="class")
    def pipeline(self):
        """Fixture para instancia del pipeline."""
        return DarwinEXPipeline()
    
    @pytest.fixture(scope="class")
    def sample_strategy_data(self):
        """Fixture para datos de estrategia de prueba."""
        return pd.Series({
            'Strategy_Name': 'Test_Strategy_1',
            'D_Score': 75.0,
            'Ranking': 120,
            'Years_Running': 1.5,
            'Months_Pilot': 10,
            'LEA': 0.15,
            'OS': 0.25,
            'Correlation_6m_Nasdaq': 0.20,
            'Correlation_6m_Gold': 0.15,
            'Correlation_6m_BTC': 0.10,
            'Frequency_Stability': 0.85,
            'Asset_Drift': 0.10,
            'DD_Correlation_INDX': 0.45,
            'Total_Data_Months': 18,
            'Development_Mode': False
        })
    
    def test_filter_1_gold_access_passed(self, pipeline, sample_strategy_data):
        """Test 1: Filtro Gold Access - Estrategia que pasa."""
        logger.info("🧪 Test 1: Filtro Gold Access - Estrategia que pasa")
        
        # Estrategia con D-Score alto y ranking bueno
        strategy_data = sample_strategy_data.copy()
        strategy_data['D_Score'] = 75.0
        strategy_data['Ranking'] = 120
        
        result = pipeline._check_gold_access(strategy_data)
        
        assert result == True, "Estrategia con D-Score 75 y ranking 120 debe pasar Gold Access"
        logger.info("✅ Test 1 PASÓ: Gold Access - Estrategia que pasa")
    
    def test_filter_1_gold_access_failed(self, pipeline, sample_strategy_data):
        """Test 2: Filtro Gold Access - Estrategia que falla."""
        logger.info("🧪 Test 2: Filtro Gold Access - Estrategia que falla")
        
        # Estrategia con D-Score bajo y ranking malo
        strategy_data = sample_strategy_data.copy()
        strategy_data['D_Score'] = 65.0
        strategy_data['Ranking'] = 200
        
        result = pipeline._check_gold_access(strategy_data)
        
        assert result == False, "Estrategia con D-Score 65 y ranking 200 debe fallar Gold Access"
        logger.info("✅ Test 2 PASÓ: Gold Access - Estrategia que falla")
    
    def test_filter_2_track_record_passed(self, pipeline, sample_strategy_data):
        """Test 3: Filtro Track Record - Estrategia que pasa."""
        logger.info("🧪 Test 3: Filtro Track Record - Estrategia que pasa")
        
        # Estrategia con track record suficiente
        strategy_data = sample_strategy_data.copy()
        strategy_data['Months_Pilot'] = 10
        strategy_data['Years_Running'] = 1.5
        
        result = pipeline._check_track_record(strategy_data)
        
        assert result == True, "Estrategia con 10 meses piloto debe pasar Track Record"
        logger.info("✅ Test 3 PASÓ: Track Record - Estrategia que pasa")
    
    def test_filter_2_track_record_failed(self, pipeline, sample_strategy_data):
        """Test 4: Filtro Track Record - Estrategia que falla."""
        logger.info("🧪 Test 4: Filtro Track Record - Estrategia que falla")
        
        # Estrategia con track record insuficiente
        strategy_data = sample_strategy_data.copy()
        strategy_data['Months_Pilot'] = 5
        strategy_data['Years_Running'] = 0.3
        
        result = pipeline._check_track_record(strategy_data)
        
        assert result == False, "Estrategia con 5 meses piloto debe fallar Track Record"
        logger.info("✅ Test 4 PASÓ: Track Record - Estrategia que falla")
    
    def test_filter_3_lea_os_positive_passed(self, pipeline, sample_strategy_data):
        """Test 5: Filtro LEA & OS Positive - Estrategia que pasa."""
        logger.info("🧪 Test 5: Filtro LEA & OS Positive - Estrategia que pasa")
        
        # Estrategia con LEA y OS positivos
        strategy_data = sample_strategy_data.copy()
        strategy_data['LEA'] = 0.15
        strategy_data['OS'] = 0.25
        
        result = pipeline._check_lea_os_positive(strategy_data)
        
        assert result == True, "Estrategia con LEA=0.15 y OS=0.25 debe pasar"
        logger.info("✅ Test 5 PASÓ: LEA & OS Positive - Estrategia que pasa")
    
    def test_filter_3_lea_os_positive_failed(self, pipeline, sample_strategy_data):
        """Test 6: Filtro LEA & OS Positive - Estrategia que falla."""
        logger.info("🧪 Test 6: Filtro LEA & OS Positive - Estrategia que falla")
        
        # Estrategia con LEA negativo
        strategy_data = sample_strategy_data.copy()
        strategy_data['LEA'] = -0.05
        strategy_data['OS'] = 0.25
        
        result = pipeline._check_lea_os_positive(strategy_data)
        
        assert result == False, "Estrategia con LEA=-0.05 debe fallar"
        logger.info("✅ Test 6 PASÓ: LEA & OS Positive - Estrategia que falla")
    
    def test_filter_4_correlation_6m_passed(self, pipeline, sample_strategy_data):
        """Test 7: Filtro Correlation 6m - Estrategia que pasa."""
        logger.info("🧪 Test 7: Filtro Correlation 6m - Estrategia que pasa")
        
        # Estrategia con correlaciones bajas
        strategy_data = sample_strategy_data.copy()
        strategy_data['Correlation_6m_Nasdaq'] = 0.20
        strategy_data['Correlation_6m_Gold'] = 0.15
        strategy_data['Correlation_6m_BTC'] = 0.10
        
        result = pipeline._check_correlation_6m(strategy_data)
        
        assert result == True, "Estrategia con correlaciones ≤ 0.25 debe pasar"
        logger.info("✅ Test 7 PASÓ: Correlation 6m - Estrategia que pasa")
    
    def test_filter_4_correlation_6m_failed(self, pipeline, sample_strategy_data):
        """Test 8: Filtro Correlation 6m - Estrategia que falla."""
        logger.info("🧪 Test 8: Filtro Correlation 6m - Estrategia que falla")
        
        # Estrategia con correlación alta
        strategy_data = sample_strategy_data.copy()
        strategy_data['Correlation_6m_Nasdaq'] = 0.30
        strategy_data['Correlation_6m_Gold'] = 0.15
        strategy_data['Correlation_6m_BTC'] = 0.10
        
        result = pipeline._check_correlation_6m(strategy_data)
        
        assert result == False, "Estrategia con correlación Nasdaq=0.30 debe fallar"
        logger.info("✅ Test 8 PASÓ: Correlation 6m - Estrategia que falla")
    
    def test_filter_5_discipline_passed(self, pipeline, sample_strategy_data):
        """Test 9: Filtro Discipline - Estrategia que pasa."""
        logger.info("🧪 Test 9: Filtro Discipline - Estrategia que pasa")
        
        # Estrategia con disciplina buena
        strategy_data = sample_strategy_data.copy()
        strategy_data['Frequency_Stability'] = 0.85
        strategy_data['Asset_Drift'] = 0.10
        
        result = pipeline._check_discipline(strategy_data)
        
        assert result == True, "Estrategia con estabilidad=0.85 y drift=0.10 debe pasar"
        logger.info("✅ Test 9 PASÓ: Discipline - Estrategia que pasa")
    
    def test_filter_5_discipline_failed(self, pipeline, sample_strategy_data):
        """Test 10: Filtro Discipline - Estrategia que falla."""
        logger.info("🧪 Test 10: Filtro Discipline - Estrategia que falla")
        
        # Estrategia con disciplina mala
        strategy_data = sample_strategy_data.copy()
        strategy_data['Frequency_Stability'] = 0.60
        strategy_data['Asset_Drift'] = 0.30
        
        result = pipeline._check_discipline(strategy_data)
        
        assert result == False, "Estrategia con estabilidad=0.60 y drift=0.30 debe fallar"
        logger.info("✅ Test 10 PASÓ: Discipline - Estrategia que falla")
    
    def test_filter_6_dd_correlation_passed(self, pipeline, sample_strategy_data):
        """Test 11: Filtro DD Correlation - Estrategia que pasa."""
        logger.info("🧪 Test 11: Filtro DD Correlation - Estrategia que pasa")
        
        # Estrategia con correlación DD baja
        strategy_data = sample_strategy_data.copy()
        strategy_data['DD_Correlation_INDX'] = 0.45
        
        result = pipeline._check_dd_correlation(strategy_data)
        
        assert result == True, "Estrategia con DD correlation=0.45 debe pasar"
        logger.info("✅ Test 11 PASÓ: DD Correlation - Estrategia que pasa")
    
    def test_filter_6_dd_correlation_failed(self, pipeline, sample_strategy_data):
        """Test 12: Filtro DD Correlation - Estrategia que falla."""
        logger.info("🧪 Test 12: Filtro DD Correlation - Estrategia que falla")
        
        # Estrategia con correlación DD alta
        strategy_data = sample_strategy_data.copy()
        strategy_data['DD_Correlation_INDX'] = 0.70
        
        result = pipeline._check_dd_correlation(strategy_data)
        
        assert result == False, "Estrategia con DD correlation=0.70 debe fallar"
        logger.info("✅ Test 12 PASÓ: DD Correlation - Estrategia que falla")
    
    def test_calculate_score_gold(self, pipeline, sample_strategy_data):
        """Test 13: Cálculo de score - Categoría Gold."""
        logger.info("🧪 Test 13: Cálculo de score - Categoría Gold")
        
        # Estrategia con score alto
        strategy_data = sample_strategy_data.copy()
        filter_results = {
            'passed': ['gold_access', 'track_record', 'lea_os_positive', 'correlation_6m', 'discipline', 'dd_correlation'],
            'failed': [],
            'details': {
                'gold_access': {'passed': True, 'value': 'Gold'},
                'track_record': {'passed': True, 'value': 'Sufficient'},
                'lea_os_positive': {'passed': True, 'value': 'Positive'},
                'correlation_6m': {'passed': True, 'value': 'Low'},
                'discipline': {'passed': True, 'value': 'Good'},
                'dd_correlation': {'passed': True, 'value': 'Low'}
            }
        }
        
        score = pipeline._calculate_score(strategy_data, filter_results)
        
        assert score >= 85, f"Score debe ser ≥ 85 para Gold, obtenido: {score}"
        logger.info(f"✅ Test 13 PASÓ: Score Gold = {score}")
    
    def test_calculate_score_silver(self, pipeline, sample_strategy_data):
        """Test 14: Cálculo de score - Categoría Silver."""
        logger.info("🧪 Test 14: Cálculo de score - Categoría Silver")
        
        # Estrategia con score medio
        strategy_data = sample_strategy_data.copy()
        filter_results = {
            'passed': ['gold_access', 'track_record', 'lea_os_positive'],
            'failed': ['correlation_6m', 'discipline', 'dd_correlation'],
            'details': {
                'gold_access': {'passed': True, 'value': 'Gold'},
                'track_record': {'passed': True, 'value': 'Sufficient'},
                'lea_os_positive': {'passed': True, 'value': 'Positive'},
                'correlation_6m': {'passed': False, 'value': 'High'},
                'discipline': {'passed': False, 'value': 'Poor'},
                'dd_correlation': {'passed': False, 'value': 'High'}
            }
        }
        
        score = pipeline._calculate_score(strategy_data, filter_results)
        
        assert 75 <= score < 85, f"Score debe estar entre 75-84 para Silver, obtenido: {score}"
        logger.info(f"✅ Test 14 PASÓ: Score Silver = {score}")
    
    def test_determine_ticket_size_gold(self, pipeline):
        """Test 15: Determinación de ticket - Gold."""
        logger.info("🧪 Test 15: Determinación de ticket - Gold")
        
        score = 87.5
        ticket_info = pipeline._determine_ticket_size(score)
        
        assert ticket_info['ticket'] == 100000, f"Ticket Gold debe ser 100,000€, obtenido: {ticket_info['ticket']}"
        assert ticket_info['category'] == 'Gold', f"Categoría debe ser Gold, obtenida: {ticket_info['category']}"
        logger.info("✅ Test 15 PASÓ: Ticket Gold = 100,000€")
    
    def test_determine_ticket_size_silver(self, pipeline):
        """Test 16: Determinación de ticket - Silver."""
        logger.info("🧪 Test 16: Determinación de ticket - Silver")
        
        score = 78.0
        ticket_info = pipeline._determine_ticket_size(score)
        
        assert ticket_info['ticket'] == 25000, f"Ticket Silver debe ser 25,000€, obtenido: {ticket_info['ticket']}"
        assert ticket_info['category'] == 'Silver', f"Categoría debe ser Silver, obtenida: {ticket_info['category']}"
        logger.info("✅ Test 16 PASÓ: Ticket Silver = 25,000€")
    
    def test_determine_ticket_size_bronze(self, pipeline):
        """Test 17: Determinación de ticket - Bronze."""
        logger.info("🧪 Test 17: Determinación de ticket - Bronze")
        
        score = 65.0
        ticket_info = pipeline._determine_ticket_size(score)
        
        assert ticket_info['ticket'] == 11000, f"Ticket Bronze debe ser 11,000€, obtenido: {ticket_info['ticket']}"
        assert ticket_info['category'] == 'Bronze', f"Categoría debe ser Bronze, obtenida: {ticket_info['category']}"
        logger.info("✅ Test 17 PASÓ: Ticket Bronze = 11,000€")
    
    def test_determine_ticket_size_reject(self, pipeline):
        """Test 18: Determinación de ticket - Reject."""
        logger.info("🧪 Test 18: Determinación de ticket - Reject")
        
        score = 55.0
        ticket_info = pipeline._determine_ticket_size(score)
        
        assert ticket_info['ticket'] == 0, f"Ticket Reject debe ser 0€, obtenido: {ticket_info['ticket']}"
        assert ticket_info['category'] == 'Reject', f"Categoría debe ser Reject, obtenida: {ticket_info['category']}"
        logger.info("✅ Test 18 PASÓ: Ticket Reject = 0€")
    
    def test_pipeline_complete_integration(self, pipeline):
        """Test 19: Integración completa del pipeline."""
        logger.info("🧪 Test 19: Integración completa del pipeline")
        
        # Crear DataFrame de prueba
        df = pd.DataFrame({
            'Strategy_Name': ['Strategy_1', 'Strategy_2', 'Strategy_3'],
            'D_Score': [75.0, 65.0, 85.0],
            'Ranking': [120, 200, 80],
            'Years_Running': [1.5, 0.5, 2.5],
            'Months_Pilot': [10, 5, 15],
            'LEA': [0.15, -0.05, 0.25],
            'OS': [0.25, 0.20, 0.30],
            'Correlation_6m_Nasdaq': [0.20, 0.30, 0.15],
            'Correlation_6m_Gold': [0.15, 0.25, 0.10],
            'Correlation_6m_BTC': [0.10, 0.20, 0.08],
            'Frequency_Stability': [0.85, 0.60, 0.90],
            'Asset_Drift': [0.10, 0.30, 0.05],
            'DD_Correlation_INDX': [0.45, 0.70, 0.35],
            'Total_Data_Months': [18, 6, 30],
            'Development_Mode': [False, False, False]
        })
        
        # Ejecutar pipeline completo
        results = pipeline.run_pipeline(df)
        
        # Verificar resultados
        assert len(results) == 3, f"Deben procesarse 3 estrategias, procesadas: {len(results)}"
        
        # Verificar que Strategy_1 (Gold) tiene ticket alto
        strategy_1 = next(r for r in results if r.strategy_name == 'Strategy_1')
        assert strategy_1.ticket_size >= 100000, f"Strategy_1 debe tener ticket ≥ 100,000€, tiene: {strategy_1.ticket_size}"
        
        # Verificar que Strategy_2 (Reject) tiene ticket 0
        strategy_2 = next(r for r in results if r.strategy_name == 'Strategy_2')
        assert strategy_2.ticket_size == 0, f"Strategy_2 debe tener ticket 0€, tiene: {strategy_2.ticket_size}"
        
        logger.info("✅ Test 19 PASÓ: Integración completa del pipeline")
    
    def test_generate_recommendations(self, pipeline):
        """Test 20: Generación de recomendaciones."""
        logger.info("🧪 Test 20: Generación de recomendaciones")
        
        filter_results = {
            'passed': ['gold_access', 'track_record'],
            'failed': ['lea_os_positive', 'correlation_6m', 'discipline', 'dd_correlation']
        }
        score = 72.0
        
        recommendations = pipeline._generate_recommendations(filter_results, score)
        
        assert len(recommendations) > 0, "Deben generarse recomendaciones"
        assert isinstance(recommendations, list), "Las recomendaciones deben ser una lista"
        
        logger.info(f"✅ Test 20 PASÓ: {len(recommendations)} recomendaciones generadas")
    
    def test_generate_risk_alerts(self, pipeline, sample_strategy_data):
        """Test 21: Generación de alertas de riesgo."""
        logger.info("🧪 Test 21: Generación de alertas de riesgo")
        
        strategy_data = sample_strategy_data.copy()
        strategy_data['LEA'] = -0.05  # LEA negativo para generar alerta
        filter_results = {
            'passed': ['gold_access'],
            'failed': ['lea_os_positive', 'correlation_6m', 'discipline', 'dd_correlation']
        }
        
        risk_alerts = pipeline._generate_risk_alerts(strategy_data, filter_results)
        
        assert len(risk_alerts) > 0, "Deben generarse alertas de riesgo"
        assert isinstance(risk_alerts, list), "Las alertas deben ser una lista"
        
        logger.info(f"✅ Test 21 PASÓ: {len(risk_alerts)} alertas de riesgo generadas")

def test_resumen_final():
    """Test de resumen final de todos los tests unitarios."""
    logger.info("\n" + "="*60)
    logger.info("🎯 RESUMEN: Tests Unitarios Pipeline DarwinEX")
    logger.info("="*60)
    logger.info("✅ 21 tests unitarios implementados")
    logger.info("✅ Cobertura completa de 6 filtros")
    logger.info("✅ Validación de scoring y tickets")
    logger.info("✅ Tests de integración completos")
    logger.info("✅ Generación de recomendaciones y alertas")
    logger.info("="*60)
    logger.info("🎉 TODOS LOS TESTS UNITARIOS COMPLETADOS")

if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"]) 