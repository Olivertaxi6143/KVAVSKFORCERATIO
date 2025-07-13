"""
Test para validar el módulo QVAScorerEnhanced extraído.

Este test verifica que la clase se puede importar, construir y ejecutar calculate_qva_score
con un DataFrame de ejemplo.
"""

import pytest
import pandas as pd
import numpy as np
from src.core.analysis.qva_analyzer import QVAScorerEnhanced
from src.core.config.config_manager import ConfigManagerEnhanced
from src.logger_config import setup_logger

# Configurar logger para tests
logger = setup_logger("test_qva")

class TestQVAScorerEnhanced:
    """Tests exhaustivos para QVAScorerEnhanced mejorado."""
    
    @pytest.fixture
    def sample_data(self):
        """Datos de prueba con todas las métricas necesarias, incluyendo KPIs extra por estilo de trading."""
        np.random.seed(42)
        n_strategies = 20
        
        data = {
            'Strategy_Name': [f'Strategy_{i}' for i in range(n_strategies)],
            'Profit factor': np.random.uniform(1.0, 3.0, n_strategies),
            'Net profit': np.random.uniform(-5000, 15000, n_strategies),
            'CAGR': np.random.uniform(-20, 80, n_strategies),
            'RecoveryFactor': np.random.uniform(0.5, 5.0, n_strategies),
            'Max_DD_%': np.random.uniform(5, 30, n_strategies),
            'VaR (95%)': np.random.uniform(-0.05, -0.01, n_strategies),
            'CVaR (95%)': np.random.uniform(-0.08, -0.02, n_strategies),
            'Ulcer Index %': np.random.uniform(5, 25, n_strategies),
            'Sharpe Ratio': np.random.uniform(0.5, 2.5, n_strategies),
            'CalmarRatio': np.random.uniform(0.5, 3.0, n_strategies),
            'SQN': np.random.uniform(0.5, 2.0, n_strategies),
            'RINAIndex': np.random.uniform(3, 12, n_strategies),
            'Stagnation': np.random.randint(0, 20, n_strategies),
            'Winning Percent': np.random.uniform(30, 70, n_strategies),
            'Avg. Bars in Trade': np.random.uniform(5, 50, n_strategies),
            'Max Consec. Losses': np.random.randint(2, 12, n_strategies),
            'Drawdown': np.random.uniform(5, 30, n_strategies),
            'Max Drawdown Duration': np.random.randint(5, 50, n_strategies),
            'Exposure': np.random.uniform(0.1, 0.9, n_strategies),
            'Sortino Ratio': np.random.uniform(0.5, 2.5, n_strategies),
            'Payout ratio': np.random.uniform(0.5, 2.0, n_strategies),
            'Expectancy': np.random.uniform(-1, 2, n_strategies)
        }
        df = pd.DataFrame(data)
        logger.info(f"📊 Datos de prueba creados: {df.shape}")
        return df
    
    @pytest.fixture
    def qva_scorer(self):
        """Instancia de QVAScorerEnhanced para testing."""
        config_manager = ConfigManagerEnhanced()
        scorer = QVAScorerEnhanced(config_manager)
        logger.info("🔧 QVAScorerEnhanced inicializado para testing")
        return scorer
    
    def test_initialization(self, qva_scorer):
        """Test de inicialización correcta."""
        logger.info("🧪 Test: Inicialización correcta")

        assert qva_scorer is not None
        assert hasattr(qva_scorer, 'penalty_config')
        assert hasattr(qva_scorer, 'trading_style_weights')
        assert len(qva_scorer.penalty_config) == 6  # 6 tipos de penalizaciones (añadimos stagnation_trades)
        assert 'stagnation_trades' in qva_scorer.penalty_config  # Verificar que existe la nueva penalización
        assert qva_scorer.penalty_config['stagnation_trades']['enabled'] == True
        assert qva_scorer.penalty_config['stagnation_trades']['threshold'] == 8
        assert qva_scorer.penalty_config['stagnation_trades']['penalty_factor'] == 0.85
        assert len(qva_scorer.trading_style_weights) == 6  # 6 estilos de trading
        
        logger.info("✅ Inicialización correcta verificada")
    
    def test_robust_normalization(self, qva_scorer):
        """Test de normalización robusta."""
        logger.info("🧪 Test: Normalización robusta")
        
        # Test con datos normales
        test_series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        normalized = qva_scorer._robust_normalization(test_series, higher_is_better=True)
        
        assert len(normalized) == len(test_series)
        assert normalized.min() >= 0
        assert normalized.max() <= 1
        assert not normalized.isna().any()
        
        # Test con datos invertidos
        normalized_inv = qva_scorer._robust_normalization(test_series, higher_is_better=False)
        assert len(normalized_inv) == len(test_series)
        assert normalized_inv.min() >= 0
        assert normalized_inv.max() <= 1
        
        # Test con datos constantes
        constant_series = pd.Series([5, 5, 5, 5, 5])
        normalized_const = qva_scorer._robust_normalization(constant_series)
        assert normalized_const.mean() == 0.5  # Valor por defecto para datos constantes
        
        logger.info("✅ Normalización robusta verificada")
    
    def test_profitability_component(self, qva_scorer, sample_data):
        """Test del componente de rentabilidad."""
        logger.info("🧪 Test: Componente de rentabilidad")
        
        enabled_kpis = ['Profit_factor', 'Net_profit', 'CAGR', 'RecoveryFactor']
        profitability_score = qva_scorer._calculate_profitability_component_robust(sample_data, enabled_kpis)
        
        assert len(profitability_score) == len(sample_data)
        assert profitability_score.min() >= 0
        assert profitability_score.max() <= 1
        assert not profitability_score.isna().any()
        
        logger.info(f"💰 Componente rentabilidad: {profitability_score.mean():.4f} ± {profitability_score.std():.4f}")
        logger.info("✅ Componente de rentabilidad verificado")
    
    def test_risk_component(self, qva_scorer, sample_data):
        """Test del componente de riesgo."""
        logger.info("🧪 Test: Componente de riesgo")
        
        enabled_kpis = ['Max_DD_%', 'VaR_95%', 'CVaR_95%', 'Ulcer_Index_%']
        risk_score = qva_scorer._calculate_risk_component_robust(sample_data, enabled_kpis)
        
        assert len(risk_score) == len(sample_data)
        assert risk_score.min() >= 0
        assert risk_score.max() <= 1
        assert not risk_score.isna().any()
        
        logger.info(f"🛡️ Componente riesgo: {risk_score.mean():.4f} ± {risk_score.std():.4f}")
        logger.info("✅ Componente de riesgo verificado")
    
    def test_consistency_component(self, qva_scorer, sample_data):
        """Test del componente de consistencia."""
        logger.info("🧪 Test: Componente de consistencia")
        
        enabled_kpis = ['Sharpe_Ratio', 'CalmarRatio', 'SQN', 'RINAIndex', 'Stagnation']
        consistency_score = qva_scorer._calculate_consistency_component_robust(sample_data, enabled_kpis)
        
        assert len(consistency_score) == len(sample_data)
        assert consistency_score.min() >= 0
        assert consistency_score.max() <= 1
        assert not consistency_score.isna().any()
        
        logger.info(f"📈 Componente consistencia: {consistency_score.mean():.4f} ± {consistency_score.std():.4f}")
        logger.info("✅ Componente de consistencia verificado")
    
    def test_consecutive_losses_penalty(self, qva_scorer, sample_data):
        """Test de penalización por pérdidas consecutivas."""
        logger.info("🧪 Test: Penalización pérdidas consecutivas")
        
        penalty = qva_scorer._calculate_consecutive_losses_penalty(sample_data)
        
        assert len(penalty) == len(sample_data)
        assert penalty.min() >= 0
        assert penalty.max() <= 1
        assert not penalty.isna().any()
        
        # Verificar que estrategias con más pérdidas consecutivas tienen mayor penalización
        high_losses = sample_data['Max Consec. Losses'] > 8
        low_losses = sample_data['Max Consec. Losses'] <= 4
        
        if high_losses.any() and low_losses.any():
            avg_high_penalty = penalty[high_losses].mean()
            avg_low_penalty = penalty[low_losses].mean()
            assert avg_high_penalty <= avg_low_penalty  # Mayor penalización para más pérdidas
        
        logger.info(f"⚠️ Penalización pérdidas consecutivas: {penalty.mean():.4f}")
        logger.info("✅ Penalización pérdidas consecutivas verificada")
    
    def test_stagnation_trades_penalty(self, qva_scorer, sample_data):
        """Test de penalización por Stagnation_Trades."""
        logger.info("🧪 Test: Penalización Stagnation_Trades")
        
        # Crear una columna de longitud igual al DataFrame, alternando valores bajos y altos
        n = len(sample_data)
        values = [5 if i % 2 == 0 else 15 for i in range(n)]
        sample_data['Stagnation_Trades'] = values
        
        penalty = qva_scorer._calculate_stagnation_trades_penalty(sample_data)
        
        assert penalty is not None
        assert len(penalty) == len(sample_data)
        assert penalty.dtype == 'float64'
        
        # Verificar que las penalizaciones son más altas para valores más altos de Stagnation_Trades
        high_stagnation = sample_data['Stagnation_Trades'] > 8  # threshold
        low_stagnation = sample_data['Stagnation_Trades'] <= 8
        
        if high_stagnation.any() and low_stagnation.any():
            avg_high_penalty = penalty[high_stagnation].mean()
            avg_low_penalty = penalty[low_stagnation].mean()
            assert avg_high_penalty <= avg_low_penalty  # Mayor penalización para valores altos
        
        logger.info(f"✅ Penalización Stagnation_Trades: {penalty.mean():.4f}")

    def test_stagnation_penalty(self, qva_scorer, sample_data):
        """Test de penalización por estancamiento."""
        logger.info("🧪 Test: Penalización estancamiento")
        
        penalty = qva_scorer._calculate_stagnation_penalty(sample_data)
        
        assert len(penalty) == len(sample_data)
        assert penalty.min() >= 0
        assert penalty.max() <= 1
        assert not penalty.isna().any()
        
        # Verificar que estrategias con más estancamiento tienen mayor penalización
        high_stagnation = sample_data['Stagnation'] > 15
        low_stagnation = sample_data['Stagnation'] <= 5
        
        if high_stagnation.any() and low_stagnation.any():
            avg_high_penalty = penalty[high_stagnation].mean()
            avg_low_penalty = penalty[low_stagnation].mean()
            assert avg_high_penalty <= avg_low_penalty  # Mayor penalización para más estancamiento
        
        logger.info(f"⚠️ Penalización estancamiento: {penalty.mean():.4f}")
        logger.info("✅ Penalización estancamiento verificada")
    
    def test_drawdown_duration_penalty(self, qva_scorer, sample_data):
        """Test de penalización por duración de drawdown."""
        logger.info("🧪 Test: Penalización duración drawdown")
        
        penalty = qva_scorer._calculate_drawdown_duration_penalty(sample_data)
        
        assert len(penalty) == len(sample_data)
        assert penalty.min() >= 0
        assert penalty.max() <= 1
        assert not penalty.isna().any()
        
        logger.info(f"⚠️ Penalización duración drawdown: {penalty.mean():.4f}")
        logger.info("✅ Penalización duración drawdown verificada")
    
    def test_exposure_penalty(self, qva_scorer, sample_data):
        """Test de penalización por exposición."""
        logger.info("🧪 Test: Penalización exposición")
        
        penalty = qva_scorer._calculate_exposure_penalty(sample_data)
        
        assert len(penalty) == len(sample_data)
        assert penalty.min() >= 0
        assert penalty.max() <= 1
        assert not penalty.isna().any()
        
        # Verificar que exposiciones extremas tienen penalización
        extreme_exposure = (sample_data['Exposure'] < 0.2) | (sample_data['Exposure'] > 0.8)
        normal_exposure = (sample_data['Exposure'] >= 0.3) & (sample_data['Exposure'] <= 0.7)
        
        if extreme_exposure.any() and normal_exposure.any():
            avg_extreme_penalty = penalty[extreme_exposure].mean()
            avg_normal_penalty = penalty[normal_exposure].mean()
            assert avg_extreme_penalty <= avg_normal_penalty  # Mayor penalización para exposiciones extremas
        
        logger.info(f"⚠️ Penalización exposición: {penalty.mean():.4f}")
        logger.info("✅ Penalización exposición verificada")
    
    def test_winning_percent_penalty(self, qva_scorer, sample_data):
        """Test de penalización por porcentaje de victorias."""
        logger.info("🧪 Test: Penalización % victorias")
        
        penalty = qva_scorer._calculate_winning_percent_penalty(sample_data)
        
        assert len(penalty) == len(sample_data)
        assert penalty.min() >= 0
        assert penalty.max() <= 1
        assert not penalty.isna().any()
        
        # Verificar que la penalización funciona correctamente
        # Como no tenemos Winning_Percent en los datos de prueba, solo verificamos que la función funciona
        logger.info("ℹ️ Columna Winning_Percent no disponible en datos de prueba")
        
        logger.info(f"⚠️ Penalización % victorias: {penalty.mean():.4f}")
        logger.info("✅ Penalización % victorias verificada")
    
    def test_advanced_penalties(self, qva_scorer, sample_data):
        """Test de todas las penalizaciones avanzadas."""
        logger.info("🧪 Test: Penalizaciones avanzadas")
        
        penalties = qva_scorer._calculate_advanced_penalties(sample_data)
        
        assert 'total_penalty' in penalties
        assert len(penalties['total_penalty']) == len(sample_data)
        assert penalties['total_penalty'].min() >= 0
        assert penalties['total_penalty'].max() <= 1
        assert not penalties['total_penalty'].isna().any()
        
        logger.info(f"⚠️ Penalización total: {penalties['total_penalty'].mean():.4f}")
        logger.info("✅ Penalizaciones avanzadas verificadas")
    
    def test_trading_style_weights(self, qva_scorer):
        """Test de pesos por estilo de trading."""
        logger.info("🧪 Test: Pesos por estilo de trading")
        
        # Test actualización de pesos
        new_weights = {'profitability': 0.5, 'risk': 0.3, 'consistency': 0.2, 'extra_kpis': 0.1}
        qva_scorer.update_trading_style_weights('Test_Style', new_weights)
        
        assert 'Test_Style' in qva_scorer.trading_style_weights
        assert qva_scorer.trading_style_weights['Test_Style'] == new_weights
        
        logger.info("✅ Pesos por estilo de trading verificados")
    
    def test_penalty_config_update(self, qva_scorer):
        """Test de actualización de configuración de penalizaciones."""
        logger.info("🧪 Test: Actualización configuración penalizaciones")
        
        new_config = {'threshold': 8, 'penalty_factor': 0.7}
        qva_scorer.update_penalty_config('consecutive_losses', new_config)
        
        assert qva_scorer.penalty_config['consecutive_losses']['threshold'] == 8
        assert qva_scorer.penalty_config['consecutive_losses']['penalty_factor'] == 0.7
        
        logger.info("✅ Actualización configuración penalizaciones verificada")
    
    def test_score_breakdown(self, qva_scorer, sample_data):
        """Test del desglose detallado del score."""
        logger.info("🧪 Test: Desglose detallado del score")
        
        breakdown = qva_scorer.get_score_breakdown(sample_data)
        
        assert 'profitability' in breakdown
        assert 'risk' in breakdown
        assert 'consistency' in breakdown
        assert 'extra_kpis' in breakdown
        assert 'penalties' in breakdown
        assert 'weights' in breakdown
        
        for component in ['profitability', 'risk', 'consistency', 'extra_kpis', 'penalties']:
            assert len(breakdown[component]) == len(sample_data)
            assert breakdown[component].min() >= 0
            assert breakdown[component].max() <= 1
        
        logger.info("✅ Desglose detallado del score verificado")
    
    def test_full_qva_score_calculation(self, qva_scorer, sample_data):
        """Test del cálculo completo del score QVA."""
        logger.info("🧪 Test: Cálculo completo QVA Score")
        
        qva_score = qva_scorer.calculate_qva_score(sample_data)
        
        assert len(qva_score) == len(sample_data)
        assert qva_score.min() >= 0
        assert qva_score.max() <= 1
        assert not qva_score.isna().any()
        
        logger.info(f"🎯 QVA Score final: {qva_score.mean():.4f} ± {qva_score.std():.4f}")
        logger.info("✅ Cálculo completo QVA Score verificado")
    
    def test_legacy_compatibility(self, qva_scorer, sample_data):
        """Test de compatibilidad con método legacy."""
        logger.info("🧪 Test: Compatibilidad método legacy")
        
        legacy_score = qva_scorer.compute_qva_score_robust(sample_data, alpha=0.8)
        new_score = qva_scorer.calculate_qva_score(sample_data)
        
        # Los scores deberían ser similares (mismo método interno)
        assert len(legacy_score) == len(new_score)
        assert legacy_score.min() >= 0
        assert legacy_score.max() <= 1
        
        logger.info("✅ Compatibilidad método legacy verificada")
    
    def test_empty_dataframe(self, qva_scorer):
        """Test con DataFrame vacío."""
        logger.info("🧪 Test: DataFrame vacío")
        
        empty_df = pd.DataFrame()
        qva_score = qva_scorer.calculate_qva_score(empty_df)
        
        assert len(qva_score) == 0
        assert qva_score.dtype == 'float64'
        
        logger.info("✅ Manejo DataFrame vacío verificado")
    
    def test_missing_columns(self, qva_scorer, sample_data):
        """Test con columnas faltantes."""
        logger.info("🧪 Test: Columnas faltantes")
        
        # Remover algunas columnas importantes (usar columnas que existen)
        columns_to_drop = []
        for col in ['Profit factor', 'Max_DD_%', 'Sortino Ratio']:
            if col in sample_data.columns:
                columns_to_drop.append(col)
        
        if columns_to_drop:
            test_data = sample_data.drop(columns=columns_to_drop)
        else:
            test_data = sample_data.copy()
        qva_score = qva_scorer.calculate_qva_score(test_data)
        
        assert len(qva_score) == len(test_data)
        assert qva_score.min() >= 0
        assert qva_score.max() <= 1
        assert not qva_score.isna().any()
        
        logger.info("✅ Manejo columnas faltantes verificado")
    
    def test_extreme_values(self, qva_scorer):
        """Test con valores extremos."""
        logger.info("🧪 Test: Valores extremos")
        
        extreme_data = pd.DataFrame({
            'Strategy_Name': ['Extreme_1', 'Extreme_2', 'Extreme_3'],
            'Profit_factor': [0.1, 10.0, 1.0],  # Valores extremos
            'Max_DD_%': [50.0, 1.0, 25.0],  # Drawdown extremo
            'Sharpe_Ratio': [-2.0, 5.0, 1.0],  # Sharpe extremo
            'Max Consec. Losses': [20, 1, 5],  # Pérdidas consecutivas extremas
            'Stagnation': [50, 0, 10],  # Estancamiento extremo
            'Exposure': [0.01, 0.99, 0.5],  # Exposición extrema
            'Winning_Percent': [10, 90, 50]  # % victorias extremo
        })
        
        qva_score = qva_scorer.calculate_qva_score(extreme_data)
        
        assert len(qva_score) == len(extreme_data)
        assert qva_score.min() >= 0
        assert qva_score.max() <= 1
        assert not qva_score.isna().any()
        
        logger.info(f"🎯 QVA Score con valores extremos: {qva_score.mean():.4f}")
        logger.info("✅ Manejo valores extremos verificado")
    
    def test_performance_metrics(self, qva_scorer, sample_data):
        """Test de métricas de rendimiento."""
        logger.info("🧪 Test: Métricas de rendimiento")
        
        import time
        
        start_time = time.time()
        qva_score = qva_scorer.calculate_qva_score(sample_data)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"⏱️ Tiempo de ejecución: {execution_time:.4f} segundos")
        
        # Debería ejecutarse en menos de 1 segundo para 20 estrategias
        assert execution_time < 1.0
        
        logger.info("✅ Métricas de rendimiento verificadas")

if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "-s"]) 