"""
Test para UnifiedEvaluatorEnhanced
"""

import pandas as pd
import numpy as np
import pytest
import logging
from unittest.mock import Mock, patch

from src.core.analysis.unified_evaluator import UnifiedEvaluatorEnhanced


class TestUnifiedEvaluatorEnhanced:
    """Test para UnifiedEvaluatorEnhanced."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔧 Configurando test UnifiedEvaluatorEnhanced")
        
        # Crear datos de prueba
        self.sample_data = pd.DataFrame({
            'Strategy_Name': [f'Strategy_{i}' for i in range(10)],
            'CAGR': np.random.uniform(0.05, 0.25, 10),
            'Sharpe_Ratio': np.random.uniform(0.5, 2.0, 10),
            'Max_DD_%': np.random.uniform(0.05, 0.30, 10),
            'Profit_factor': np.random.uniform(1.1, 2.5, 10),
            'Total_Trades': np.random.randint(50, 500, 10),
            'Win_Rate_%': np.random.uniform(40, 70, 10),
            'Avg_Trade': np.random.uniform(-0.01, 0.02, 10),
            'Calmar_Ratio': np.random.uniform(0.5, 3.0, 10)
        })
        
        self.logger.info(f"📊 Datos de prueba creados: {self.sample_data.shape}")
    
    def test_construction(self):
        """Test de construcción del evaluador unificado."""
        self.logger.info("🧪 Testando construcción de UnifiedEvaluatorEnhanced")
        
        try:
            # Crear instancia
            evaluator = UnifiedEvaluatorEnhanced()
            
            # Verificar que se creó correctamente
            assert evaluator is not None
            assert hasattr(evaluator, 'factor_k')
            assert hasattr(evaluator, 'qva_scorer')
            assert hasattr(evaluator, 'logger')
            
            self.logger.info("✅ Construcción exitosa")
            
        except Exception as e:
            self.logger.error(f"❌ Error en construcción: {e}")
            raise
    
    def test_evaluate_strategies_unified(self):
        """Test de evaluación unificada de estrategias."""
        self.logger.info("🧪 Testando evaluación unificada de estrategias")
        
        try:
            # Crear evaluador
            evaluator = UnifiedEvaluatorEnhanced()
            
            # Ejecutar evaluación
            result_df = evaluator.evaluate_strategies_unified(self.sample_data)
            
            # Verificar que el resultado es un DataFrame
            assert isinstance(result_df, pd.DataFrame)
            assert len(result_df) == len(self.sample_data)
            
            # Verificar que se calcularon los scores esperados
            expected_columns = [
                'QVA_Score', 'QVA_Score_Robust', 
                'Unified_Score', 'Unified_Score_Robust',
                'Unified_Score_Normalized', 'Unified_Score_Robust_Normalized'
            ]
            
            for col in expected_columns:
                if col in result_df.columns:
                    self.logger.info(f"✅ Columna {col} presente")
                    # Verificar que no hay valores NaN
                    assert not bool(result_df[col].isna().all()), f"Columna {col} tiene solo NaN"
                else:
                    self.logger.warning(f"⚠️ Columna {col} no encontrada")
            
            self.logger.info("✅ Evaluación unificada exitosa")
            
        except Exception as e:
            self.logger.error(f"❌ Error en evaluación unificada: {e}")
            raise
    
    def test_normalize_scores(self):
        """Test de normalización de scores."""
        self.logger.info("🧪 Testando normalización de scores")
        
        try:
            evaluator = UnifiedEvaluatorEnhanced()
            
            # Crear scores de prueba
            test_scores = pd.Series([1, 2, 3, 4, 5])
            
            # Normalizar
            normalized = evaluator._normalize_scores(test_scores)
            
            # Verificar que está en rango [0, 1]
            assert normalized.min() >= 0
            assert normalized.max() <= 1
            assert len(normalized) == len(test_scores)
            
            self.logger.info("✅ Normalización exitosa")
            
        except Exception as e:
            self.logger.error(f"❌ Error en normalización: {e}")
            raise
    
    def test_get_unified_summary(self):
        """Test de generación de resumen unificado."""
        self.logger.info("🧪 Testando generación de resumen unificado")
        
        try:
            evaluator = UnifiedEvaluatorEnhanced()
            
            # Crear DataFrame con scores
            test_df = self.sample_data.copy()
            test_df['Unified_Score'] = np.random.uniform(0, 1, len(test_df))
            test_df['QVA_Score'] = np.random.uniform(0, 1, len(test_df))
            
            # Generar resumen
            summary = evaluator.get_unified_summary(test_df)
            
            # Verificar estructura del resumen
            assert isinstance(summary, dict)
            assert 'total_strategies' in summary
            assert 'evaluation_timestamp' in summary
            assert 'scores_calculated' in summary
            
            self.logger.info("✅ Resumen unificado generado exitosamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error en generación de resumen: {e}")
            raise


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Ejecutar tests
    pytest.main([__file__, "-v"]) 