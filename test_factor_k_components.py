"""
Test específico para verificar el cálculo correcto de los componentes del Factor K
"""

import pandas as pd
import numpy as np
import pytest
import logging
from src.core.analysis.factor_k_analyzer import FactorKElite96Enhanced


class TestFactorKComponents:
    """Test para verificar el cálculo correcto de componentes del Factor K."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔧 Configurando test de componentes Factor K")
        
        # Crear datos de prueba con métricas reales
        self.sample_data = pd.DataFrame({
            'Strategy_Name': [f'Strategy_{i}' for i in range(5)],
            'CAGR': [0.15, 0.25, 0.10, 0.30, 0.20],
            'Sharpe_Ratio': [1.5, 2.0, 1.0, 2.5, 1.8],
            'Max_DD_%': [0.05, 0.10, 0.15, 0.08, 0.12],
            'Profit_factor': [1.8, 2.2, 1.5, 2.8, 2.0],
            'Total_Trades': [200, 350, 150, 400, 300],
            'Win_Rate_%': [60, 65, 55, 70, 62],
            'CalmarRatio': [2.5, 3.0, 1.8, 3.5, 2.8],
            'VaR_95%': [0.02, 0.03, 0.04, 0.025, 0.035],
            'CVaR_95%': [0.025, 0.035, 0.045, 0.03, 0.04],
            'Sortino_Ratio': [2.0, 2.5, 1.8, 3.0, 2.3],
            'Max_Consec_Losses': [3, 2, 5, 2, 4],
            'Stagnation': [10, 5, 15, 3, 8]
        })
        
        self.logger.info(f"📊 Datos de prueba creados: {self.sample_data.shape}")
    
    def test_stability_component_calculation(self):
        """Test del cálculo del componente de estabilidad."""
        self.logger.info("🧪 Testando cálculo del componente de estabilidad")
        
        try:
            # Crear instancia
            factor_k = FactorKElite96Enhanced()
            
            # Calcular componente de estabilidad
            result_df = factor_k._calculate_stability_component(self.sample_data.copy())
            
            # Verificar que se calculó correctamente
            assert 'FK96_Stability_Enhanced' in result_df.columns
            assert not bool(result_df['FK96_Stability_Enhanced'].isna().any())
            assert bool((result_df['FK96_Stability_Enhanced'] >= 0).all())
            assert bool((result_df['FK96_Stability_Enhanced'] <= 1).all())
            
            # Verificar que los valores son razonables
            stability_scores = result_df['FK96_Stability_Enhanced']
            self.logger.info(f"📊 Stability scores: {stability_scores.values}")
            
            # La estrategia con mejor Sharpe y menor drawdown debería tener mejor score
            best_strategy_idx = 3  # Strategy_3 tiene mejor Sharpe (2.5) y menor DD (0.08)
            worst_strategy_idx = 2  # Strategy_2 tiene peor Sharpe (1.0) y mayor DD (0.15)
            
            assert stability_scores.iloc[best_strategy_idx] > stability_scores.iloc[worst_strategy_idx]
            
            self.logger.info("✅ Componente de estabilidad calculado correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error en cálculo de estabilidad: {e}")
            raise
    
    def test_growth_component_calculation(self):
        """Test del cálculo del componente de crecimiento."""
        self.logger.info("🧪 Testando cálculo del componente de crecimiento")
        
        try:
            # Crear instancia
            factor_k = FactorKElite96Enhanced()
            
            # Calcular componente de crecimiento
            result_df = factor_k._calculate_growth_component(self.sample_data.copy())
            
            # Verificar que se calculó correctamente
            assert 'FK96_Growth_Enhanced' in result_df.columns
            assert not bool(result_df['FK96_Growth_Enhanced'].isna().any())
            assert bool((result_df['FK96_Growth_Enhanced'] >= 0).all())
            assert bool((result_df['FK96_Growth_Enhanced'] <= 1).all())
            
            # Verificar que los valores son razonables
            growth_scores = result_df['FK96_Growth_Enhanced']
            self.logger.info(f"📊 Growth scores: {growth_scores.values}")
            
            # La estrategia con mejor CAGR debería tener mejor score
            best_strategy_idx = 3  # Strategy_3 tiene mejor CAGR (0.30)
            worst_strategy_idx = 2  # Strategy_2 tiene peor CAGR (0.10)
            
            assert growth_scores.iloc[best_strategy_idx] > growth_scores.iloc[worst_strategy_idx]
            
            self.logger.info("✅ Componente de crecimiento calculado correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error en cálculo de crecimiento: {e}")
            raise
    
    def test_efficiency_component_calculation(self):
        """Test del cálculo del componente de eficiencia."""
        self.logger.info("🧪 Testando cálculo del componente de eficiencia")
        
        try:
            # Crear instancia
            factor_k = FactorKElite96Enhanced()
            
            # Calcular componente de eficiencia
            result_df = factor_k._calculate_efficiency_component(self.sample_data.copy())
            
            # Verificar que se calculó correctamente
            assert 'FK96_Efficiency_Enhanced' in result_df.columns
            assert not bool(result_df['FK96_Efficiency_Enhanced'].isna().any())
            assert bool((result_df['FK96_Efficiency_Enhanced'] >= 0).all())
            assert bool((result_df['FK96_Efficiency_Enhanced'] <= 1).all())
            
            # Verificar que los valores son razonables
            efficiency_scores = result_df['FK96_Efficiency_Enhanced']
            self.logger.info(f"📊 Efficiency scores: {efficiency_scores.values}")
            
            # La estrategia con mejor Profit Factor debería tener mejor score
            best_strategy_idx = 3  # Strategy_3 tiene mejor Profit Factor (2.8)
            worst_strategy_idx = 2  # Strategy_2 tiene peor Profit Factor (1.5)
            
            assert efficiency_scores.iloc[best_strategy_idx] > efficiency_scores.iloc[worst_strategy_idx]
            
            self.logger.info("✅ Componente de eficiencia calculado correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error en cálculo de eficiencia: {e}")
            raise
    
    def test_consistency_component_calculation(self):
        """Test del cálculo del componente de consistencia."""
        self.logger.info("🧪 Testando cálculo del componente de consistencia")
        
        try:
            # Crear instancia
            factor_k = FactorKElite96Enhanced()
            
            # Calcular componente de consistencia
            result_df = factor_k._calculate_consistency_component(self.sample_data.copy())
            
            # Verificar que se calculó correctamente
            assert 'FK96_Consistency_Enhanced' in result_df.columns
            assert not bool(result_df['FK96_Consistency_Enhanced'].isna().any())
            assert bool((result_df['FK96_Consistency_Enhanced'] >= 0).all())
            assert bool((result_df['FK96_Consistency_Enhanced'] <= 1).all())
            
            # Verificar que los valores son razonables
            consistency_scores = result_df['FK96_Consistency_Enhanced']
            self.logger.info(f"📊 Consistency scores: {consistency_scores.values}")
            
            # La estrategia con más trades y menos stagnation debería tener mejor score
            best_strategy_idx = 3  # Strategy_3 tiene más trades (400) y menos stagnation (3)
            worst_strategy_idx = 2  # Strategy_2 tiene menos trades (150) y más stagnation (15)
            
            assert consistency_scores.iloc[best_strategy_idx] > consistency_scores.iloc[worst_strategy_idx]
            
            self.logger.info("✅ Componente de consistencia calculado correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error en cálculo de consistencia: {e}")
            raise
    
    def test_risk_component_calculation(self):
        """Test del cálculo del componente de riesgo."""
        self.logger.info("🧪 Testando cálculo del componente de riesgo")
        
        try:
            # Crear instancia
            factor_k = FactorKElite96Enhanced()
            
            # Calcular componente de riesgo
            result_df = factor_k._calculate_risk_component(self.sample_data.copy())
            
            # Verificar que se calculó correctamente
            assert 'FK96_Risk_Enhanced' in result_df.columns
            assert not bool(result_df['FK96_Risk_Enhanced'].isna().any())
            assert bool((result_df['FK96_Risk_Enhanced'] >= 0).all())
            assert bool((result_df['FK96_Risk_Enhanced'] <= 1).all())
            
            # Verificar que los valores son razonables
            risk_scores = result_df['FK96_Risk_Enhanced']
            self.logger.info(f"📊 Risk scores: {risk_scores.values}")
            
            # La estrategia con menor VaR y mejor Sortino debería tener mejor score
            best_strategy_idx = 0  # Strategy_0 tiene menor VaR (0.02) y mejor Sortino (2.0)
            worst_strategy_idx = 2  # Strategy_2 tiene mayor VaR (0.04) y peor Sortino (1.8)
            
            assert risk_scores.iloc[best_strategy_idx] > risk_scores.iloc[worst_strategy_idx]
            
            self.logger.info("✅ Componente de riesgo calculado correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error en cálculo de riesgo: {e}")
            raise
    
    def test_complete_factor_k_calculation(self):
        """Test del cálculo completo del Factor K Elite."""
        self.logger.info("🧪 Testando cálculo completo del Factor K Elite")
        
        try:
            # Crear instancia
            factor_k = FactorKElite96Enhanced()
            
            # Calcular Factor K completo
            result_df = factor_k._calculate_factor_k_elite(self.sample_data.copy())
            
            # Verificar que se calculó correctamente
            assert 'FK96_Elite_Enhanced' in result_df.columns
            assert not bool(result_df['FK96_Elite_Enhanced'].isna().any())
            
            # Verificar que todos los componentes están presentes
            component_columns = [
                'FK96_Stability_Enhanced',
                'FK96_Growth_Enhanced', 
                'FK96_Efficiency_Enhanced',
                'FK96_Consistency_Enhanced',
                'FK96_Risk_Enhanced'
            ]
            
            for col in component_columns:
                assert col in result_df.columns
                assert not bool(result_df[col].isna().any())
            
            # Verificar que el Factor K es una combinación ponderada de componentes
            fk_scores = result_df['FK96_Elite_Enhanced']
            self.logger.info(f"📊 Factor K scores: {fk_scores.values}")
            
            # Verificar que los scores están en rango razonable
            assert bool((fk_scores >= 0).all())
            assert bool((fk_scores <= 1).all())
            
            # La mejor estrategia debería tener el mejor Factor K
            best_strategy_idx = 3  # Strategy_3 tiene mejores métricas en general
            worst_strategy_idx = 2  # Strategy_2 tiene peores métricas en general
            
            assert fk_scores.iloc[best_strategy_idx] > fk_scores.iloc[worst_strategy_idx]
            
            self.logger.info("✅ Factor K Elite calculado correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error en cálculo completo del Factor K: {e}")
            raise


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Ejecutar tests
    pytest.main([__file__, "-v"]) 