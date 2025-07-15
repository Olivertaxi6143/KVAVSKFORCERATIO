#!/usr/bin/env python3
"""
Test exhaustivo para validar las mejoras científicas de la Fase 3 del roadmap.
Valida: scoring adaptativo, optimización de portfolio, stress testing y validación de datos.
"""

import sys
import os
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List

# Añadir el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.predictability_analyzer import PredictabilityAnalyzer
from core.logger_config import setup_logger

# Configurar logging
logger = setup_logger('test_mejoras_cientificas_fase3')

class TestMejorasCientificasFase3:
    """Test exhaustivo para las mejoras científicas de la Fase 3."""
    
    def __init__(self):
        """Inicializar el test."""
        self.predictability_analyzer = PredictabilityAnalyzer()
        self.test_results = {}
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Ejecutar todos los tests de la Fase 3."""
        logger.info("🚀 INICIANDO TESTS DE MEJORAS CIENTÍFICAS - FASE 3")
        
        try:
            # Test 1: Scoring adaptativo por régimen
            logger.info("📊 Test 1: Scoring adaptativo por régimen")
            self.test_regime_adaptive_scoring()
            
            # Test 2: Optimización de portfolio
            logger.info("📈 Test 2: Optimización de portfolio")
            self.test_portfolio_optimization()
            
            # Test 3: Stress testing
            logger.info("🛡️ Test 3: Stress testing")
            self.test_stress_testing()
            
            # Test 4: Validación de datos
            logger.info("🔍 Test 4: Validación de datos")
            self.test_data_validation()
            
            # Test 5: Bootstrap CI
            logger.info("📊 Test 5: Bootstrap CI")
            self.test_bootstrap_ci()
            
            # Test 6: Tail risk
            logger.info("⚠️ Test 6: Tail risk")
            self.test_tail_risk()
            
            # Test 7: Compliance score
            logger.info("✅ Test 7: Compliance score")
            self.test_compliance_score()
            
            # Resumen final
            self.generate_final_report()
            
            return self.test_results
            
        except Exception as e:
            logger.error(f"Error en tests de Fase 3: {str(e)}")
            return {'error': str(e)}
    
    def create_test_data(self) -> pd.DataFrame:
        """Crear datos de prueba realistas."""
        logger.debug("Creando datos de prueba...")
        
        # Crear estrategias de prueba
        np.random.seed(42)
        n_strategies = 20
        
        strategies_data = {
            'Strategy Name': [f'Strategy_{i}' for i in range(n_strategies)],
            'CAGR': np.random.normal(0.15, 0.08, n_strategies),
            'Sharpe Ratio': np.random.normal(1.2, 0.5, n_strategies),
            'Profit factor': np.random.normal(1.8, 0.6, n_strategies),
            'Drawdown': np.random.normal(8.0, 3.0, n_strategies),
            'Total trades': np.random.randint(100, 1000, n_strategies),
            'Win rate': np.random.normal(0.55, 0.1, n_strategies),
            'Exposure': np.random.normal(0.6, 0.2, n_strategies)
        }
        
        strategies_df = pd.DataFrame(strategies_data)
        strategies_df.set_index('Strategy Name', inplace=True)
        
        # Asegurar valores positivos para métricas clave
        strategies_df['CAGR'] = np.abs(strategies_df['CAGR'])
        strategies_df['Sharpe Ratio'] = np.abs(strategies_df['Sharpe Ratio'])
        strategies_df['Profit factor'] = np.maximum(strategies_df['Profit factor'], 0.5)
        strategies_df['Win rate'] = np.clip(strategies_df['Win rate'], 0.3, 0.8)
        
        logger.debug(f"Datos de prueba creados: {strategies_df.shape}")
        return strategies_df
    
    def create_market_data(self) -> pd.DataFrame:
        """Crear datos de mercado para testing."""
        logger.debug("Creando datos de mercado...")
        
        # Simular datos de mercado
        np.random.seed(42)
        n_days = 252 * 2  # 2 años de datos
        
        market_data = pd.DataFrame({
            'date': pd.date_range('2022-01-01', periods=n_days, freq='D'),
            'returns': np.random.normal(0.0005, 0.015, n_days),
            'volatility': np.random.normal(0.015, 0.005, n_days)
        })
        
        market_data.set_index('date', inplace=True)
        logger.debug(f"Datos de mercado creados: {market_data.shape}")
        return market_data
    
    def test_regime_adaptive_scoring(self):
        """Test del scoring adaptativo por régimen."""
        try:
            logger.info("Ejecutando test de scoring adaptativo...")
            
            # Crear datos de prueba
            strategies = self.create_test_data()
            market_data = self.create_market_data()
            
            # Ejecutar scoring adaptativo
            weights = self.predictability_analyzer.regime_adaptive_scoring(market_data, strategies)
            
            # Validaciones
            assert isinstance(weights, dict), "weights debe ser un diccionario"
            assert len(weights) > 0, "weights no debe estar vacío"
            assert all(isinstance(v, float) for v in weights.values()), "Todos los valores deben ser float"
            assert abs(sum(weights.values()) - 1.0) < 0.01, "Los pesos deben sumar 1.0"
            
            # Verificar que los pesos están en rangos razonables
            for weight in weights.values():
                assert 0.0 <= weight <= 1.0, f"Peso fuera de rango: {weight}"
            
            self.test_results['regime_adaptive_scoring'] = {
                'status': 'PASSED',
                'weights': weights,
                'message': f"Scoring adaptativo exitoso con {len(weights)} estrategias"
            }
            
            logger.info("✅ Test de scoring adaptativo: PASADO")
            
        except Exception as e:
            logger.error(f"❌ Test de scoring adaptativo: FALLIDO - {str(e)}")
            self.test_results['regime_adaptive_scoring'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_portfolio_optimization(self):
        """Test de optimización de portfolio."""
        try:
            logger.info("Ejecutando test de optimización de portfolio...")
            
            # Crear datos de prueba
            strategies = self.create_test_data()
            
            # Ejecutar optimización
            allocation = self.predictability_analyzer.optimize_portfolio_allocation(
                strategies, max_position_size=0.15, max_volatility=0.12
            )
            
            # Validaciones
            assert isinstance(allocation, dict), "allocation debe ser un diccionario"
            if len(allocation) > 0:
                assert all(isinstance(v, float) for v in allocation.values()), "Todos los valores deben ser float"
                assert all(0.0 <= v <= 1.0 for v in allocation.values()), "Pesos fuera de rango"
            
            self.test_results['portfolio_optimization'] = {
                'status': 'PASSED',
                'allocation': allocation,
                'message': f"Optimización exitosa con {len(allocation)} estrategias"
            }
            
            logger.info("✅ Test de optimización de portfolio: PASADO")
            
        except Exception as e:
            logger.error(f"❌ Test de optimización de portfolio: FALLIDO - {str(e)}")
            self.test_results['portfolio_optimization'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_stress_testing(self):
        """Test de stress testing."""
        try:
            logger.info("Ejecutando test de stress testing...")
            
            # Crear datos de prueba
            strategies = self.create_test_data()
            allocation = {'Strategy_0': 0.3, 'Strategy_1': 0.3, 'Strategy_2': 0.4}
            
            # Ejecutar stress testing
            stress_results = self.predictability_analyzer.stress_test_portfolio(strategies, allocation)
            
            # Validaciones
            assert isinstance(stress_results, dict), "stress_results debe ser un diccionario"
            assert 'error' not in stress_results, f"Error en stress testing: {stress_results.get('error')}"
            
            # Verificar que hay resultados de escenarios
            scenario_count = len([k for k in stress_results.keys() if k != 'aggregate'])
            assert scenario_count > 0, "Debe haber al menos un escenario de stress"
            
            # Verificar métricas agregadas
            if 'aggregate' in stress_results:
                aggregate = stress_results['aggregate']
                assert 'error' not in aggregate, f"Error en agregados: {aggregate.get('error')}"
                if 'error' not in aggregate:
                    assert 'scenarios_tested' in aggregate, "Debe incluir número de escenarios"
            
            self.test_results['stress_testing'] = {
                'status': 'PASSED',
                'scenarios_tested': scenario_count,
                'message': f"Stress testing exitoso con {scenario_count} escenarios"
            }
            
            logger.info("✅ Test de stress testing: PASADO")
            
        except Exception as e:
            logger.error(f"❌ Test de stress testing: FALLIDO - {str(e)}")
            self.test_results['stress_testing'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_data_validation(self):
        """Test de validación de datos."""
        try:
            logger.info("Ejecutando test de validación de datos...")
            
            # Crear datos de prueba
            strategies = self.create_test_data()
            
            # Ejecutar validación
            validation_results = self.predictability_analyzer.validate_data_quality(strategies)
            
            # Validaciones
            assert isinstance(validation_results, dict), "validation_results debe ser un diccionario"
            required_keys = ['drift_detected', 'temporal_quality', 'outliers', 'is_valid', 'overall_score']
            for key in required_keys:
                assert key in validation_results, f"Falta clave requerida: {key}"
            
            # Verificar tipos de datos
            assert isinstance(validation_results['drift_detected'], bool), "drift_detected debe ser bool"
            assert isinstance(validation_results['is_valid'], bool), "is_valid debe ser bool"
            assert isinstance(validation_results['overall_score'], float), "overall_score debe ser float"
            assert 0.0 <= validation_results['overall_score'] <= 1.0, "overall_score fuera de rango"
            
            self.test_results['data_validation'] = {
                'status': 'PASSED',
                'overall_score': validation_results['overall_score'],
                'is_valid': validation_results['is_valid'],
                'message': f"Validación exitosa con score {validation_results['overall_score']:.3f}"
            }
            
            logger.info("✅ Test de validación de datos: PASADO")
            
        except Exception as e:
            logger.error(f"❌ Test de validación de datos: FALLIDO - {str(e)}")
            self.test_results['data_validation'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_bootstrap_ci(self):
        """Test de intervalos de confianza bootstrap."""
        try:
            logger.info("Ejecutando test de bootstrap CI...")
            
            # Crear datos de prueba
            data = pd.Series(np.random.normal(0.1, 0.05, 100))
            
            # Función de métrica de prueba
            def test_metric(x):
                return float(x.mean())
            
            # Ejecutar bootstrap CI
            lower, upper, original = self.predictability_analyzer.bootstrap_ci(data, test_metric)
            
            # Validaciones
            assert isinstance(lower, float), "lower debe ser float"
            assert isinstance(upper, float), "upper debe ser float"
            assert isinstance(original, float), "original debe ser float"
            assert lower <= upper, "lower debe ser <= upper"
            assert lower <= original <= upper, "original debe estar en el intervalo"
            
            self.test_results['bootstrap_ci'] = {
                'status': 'PASSED',
                'interval': [lower, upper],
                'original': original,
                'message': f"Bootstrap CI exitoso: [{lower:.4f}, {upper:.4f}]"
            }
            
            logger.info("✅ Test de bootstrap CI: PASADO")
            
        except Exception as e:
            logger.error(f"❌ Test de bootstrap CI: FALLIDO - {str(e)}")
            self.test_results['bootstrap_ci'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_tail_risk(self):
        """Test de métricas de tail risk."""
        try:
            logger.info("Ejecutando test de tail risk...")
            
            # Crear datos de prueba
            strategy_data = pd.Series(np.random.normal(0.001, 0.02, 500))
            
            # Ejecutar cálculo de tail risk
            tail_risk_score = self.predictability_analyzer.calculate_tail_risk(strategy_data)
            
            # Validaciones
            assert isinstance(tail_risk_score, float), "tail_risk_score debe ser float"
            assert 0.0 <= tail_risk_score <= 1.0, "tail_risk_score fuera de rango [0,1]"
            
            self.test_results['tail_risk'] = {
                'status': 'PASSED',
                'score': tail_risk_score,
                'message': f"Tail risk calculado: {tail_risk_score:.4f}"
            }
            
            logger.info("✅ Test de tail risk: PASADO")
            
        except Exception as e:
            logger.error(f"❌ Test de tail risk: FALLIDO - {str(e)}")
            self.test_results['tail_risk'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_compliance_score(self):
        """Test de compliance score."""
        try:
            logger.info("Ejecutando test de compliance score...")
            
            # Crear datos de prueba
            strategies = self.create_test_data()
            allocation = {'Strategy_0': 0.25, 'Strategy_1': 0.25, 'Strategy_2': 0.25, 'Strategy_3': 0.25}
            
            # Ejecutar cálculo de compliance score
            compliance_score = self.predictability_analyzer.calculate_compliance_score(strategies, allocation)
            
            # Validaciones
            assert isinstance(compliance_score, float), "compliance_score debe ser float"
            assert 0.0 <= compliance_score <= 100.0, "compliance_score fuera de rango [0,100]"
            
            self.test_results['compliance_score'] = {
                'status': 'PASSED',
                'score': compliance_score,
                'message': f"Compliance score: {compliance_score:.1f}/100"
            }
            
            logger.info("✅ Test de compliance score: PASADO")
            
        except Exception as e:
            logger.error(f"❌ Test de compliance score: FALLIDO - {str(e)}")
            self.test_results['compliance_score'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    
    def generate_final_report(self):
        """Generar reporte final de la Fase 3."""
        logger.info("📋 GENERANDO REPORTE FINAL - FASE 3")
        
        # Contar resultados
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get('status') == 'PASSED'])
        failed_tests = total_tests - passed_tests
        
        # Calcular score general
        overall_score = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Generar resumen
        summary = {
            'fase': 'Fase 3 - Mejoras Funcionales',
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'overall_score': overall_score,
            'status': 'PASSED' if failed_tests == 0 else 'PARTIAL' if passed_tests > 0 else 'FAILED',
            'details': self.test_results
        }
        
        # Log del resumen
        logger.info(f"🎯 RESUMEN FASE 3:")
        logger.info(f"   Total tests: {total_tests}")
        logger.info(f"   Tests pasados: {passed_tests}")
        logger.info(f"   Tests fallidos: {failed_tests}")
        logger.info(f"   Score general: {overall_score:.1f}%")
        logger.info(f"   Estado: {summary['status']}")
        
        # Log de detalles
        for test_name, result in self.test_results.items():
            status_emoji = "✅" if result.get('status') == 'PASSED' else "❌"
            logger.info(f"   {status_emoji} {test_name}: {result.get('message', result.get('error', 'Sin mensaje'))}")
        
        self.test_results['summary'] = summary
        
        if failed_tests == 0:
            logger.info("🎉 ¡TODOS LOS TESTS DE LA FASE 3 PASARON!")
        else:
            logger.warning(f"⚠️ {failed_tests} tests fallaron en la Fase 3")

def main():
    """Función principal para ejecutar los tests."""
    try:
        # Crear y ejecutar tests
        tester = TestMejorasCientificasFase3()
        results = tester.run_all_tests()
        
        # Retornar resultados
        return results
        
    except Exception as e:
        logger.error(f"Error en ejecución de tests: {str(e)}")
        return {'error': str(e)}

if __name__ == "__main__":
    results = main()
    print(f"\n🎯 RESULTADOS FINALES FASE 3:")
    print(f"Estado: {results.get('summary', {}).get('status', 'UNKNOWN')}")
    print(f"Score: {results.get('summary', {}).get('overall_score', 0):.1f}%") 