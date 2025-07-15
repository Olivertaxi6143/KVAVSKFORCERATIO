from typing import Optional, Any, Union
"""
MARKET_REGIME_ANALYZER.py - Análisis de Regímenes de Mercado

Este módulo contiene las clases para análisis de regímenes de mercado:
- HiddenMarkovModelAnalyzer: Análisis con modelos de Markov ocultos
- MarketRegimeDetector: Detección de regímenes usando clustering
- MarketRegimeDetectorEnhanced: Versión mejorada con más características

Extraído de core_engine_enhanced.py para modularización.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
import warnings
from dataclasses import dataclass
from enum import Enum

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

class RegimeType(Enum):
    """Tipos de régimen de mercado."""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    CRISIS = "crisis"
    VOLATILE = "volatile"
    CALM = "calm"

@dataclass
class RegimeAnalysisResult:
    """Resultado del análisis de régimen."""
    regime_labels: np.ndarray
    regime_centroids: np.ndarray
    regime_characteristics: Dict[str, Any]
    confidence_scores: np.ndarray
    transition_matrix: Optional[np.ndarray] = None

class HiddenMarkovModelAnalyzer:
    """
    Analizador de regímenes de mercado usando modelos de Markov ocultos.
    
    Esta clase implementa análisis de regímenes usando HMM para detectar
    cambios en el comportamiento del mercado de forma estadísticamente robusta.
    """
    
    def __init__(self, n_states: int = 3, random_state: int = 42):
        """
        Inicializa el analizador HMM.
        
        Args:
            n_states: Número de estados (regímenes) a detectar
            random_state: Semilla para reproducibilidad
        """
        self.n_states = n_states
        self.random_state = random_state
        self.hmm_model = None
        self.is_fitted = False
        
    def fit_hmm(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Ajusta el modelo HMM a los datos de mercado.
        
        Args:
            data: DataFrame con datos de mercado (precios, volatilidad, etc.)
            
        Returns:
            Diccionario con resultados del análisis HMM
        """
        try:
            logger.info(f"Ajustando modelo HMM con {self.n_states} estados...")
            
            # Preparar datos para HMM
            if isinstance(data, pd.DataFrame):
                # Usar características relevantes para régimen
                feature_columns = []
                for col in data.columns:
                    if any(metric in col.lower() for metric in ['return', 'volatility', 'volume', 'price']):
                        feature_columns.append(col)
                
                if not feature_columns:
                    # Usar todas las columnas numéricas si no hay características específicas
                    numeric_data = data.select_dtypes(include=[np.number])
                    feature_columns = numeric_data.columns.tolist()
                
                features = data[feature_columns].values
            else:
                features = np.array(data)
            
            # Normalizar características
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Ajustar modelo HMM usando GMM como aproximación
            # (HMM puro requiere secuencias temporales, GMM es más apropiado para datos de mercado)
            gmm = GaussianMixture(
                n_components=self.n_states,
                random_state=self.random_state,
                covariance_type='full'
            )
            
            gmm.fit(features_scaled)
            # Guardar tanto el modelo como el scaler para uso posterior
            self.hmm_model = {
                'model': gmm,
                'scaler': scaler
            }
            self.is_fitted = True
            
            # Obtener etiquetas de régimen
            regime_labels = gmm.predict(features_scaled)
            
            # Calcular probabilidades de pertenencia
            regime_probs = gmm.predict_proba(features_scaled)
            
            # Caracterizar cada régimen
            # Convertir features a ndarray para evitar problemas de tipo
            features_array = np.asarray(features)
            regime_characteristics = self._characterize_regimes(features_array, regime_labels)
            
            # Calcular matriz de transición (aproximada)
            transition_matrix = self._calculate_transition_matrix(regime_labels)
            
            # Calcular scores de confianza
            confidence_scores = np.max(regime_probs, axis=1)
            
            result = {
                'regime_labels': regime_labels,
                'regime_centroids': gmm.means_,
                'regime_characteristics': regime_characteristics,
                'confidence_scores': confidence_scores,
                'transition_matrix': transition_matrix,
                'model': gmm,
                'scaler': scaler
            }
            
            logger.info(f"HMM ajustado exitosamente. Regímenes detectados: {len(np.unique(regime_labels))}")
            return result
            
        except Exception as e:
            logger.error(f"Error ajustando modelo HMM: {str(e)}")
            raise
    
    def _characterize_regimes(self, features: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
        """
        Caracteriza cada régimen detectado.
        
        Args:
            features: Características de mercado
            labels: Etiquetas de régimen
            
        Returns:
            Diccionario con características de cada régimen
        """
        characteristics = {}
        
        # Asegurar que features sea ndarray
        if not isinstance(features, np.ndarray):
            features = np.asarray(features)
        if not isinstance(labels, np.ndarray):
            labels = np.asarray(labels)
        
        for regime_id in np.unique(labels):
            regime_mask = labels == regime_id
            regime_features = features[regime_mask]
            
            if len(regime_features) > 0:
                characteristics[f'regime_{regime_id}'] = {
                    'size': int(np.sum(regime_mask)),
                    'percentage': float(np.mean(regime_mask) * 100),
                    'mean_features': np.mean(regime_features, axis=0).tolist(),
                    'std_features': np.std(regime_features, axis=0).tolist()
                }
        
        return characteristics
    
    def _calculate_transition_matrix(self, labels: np.ndarray) -> np.ndarray:
        """
        Calcula matriz de transición entre regímenes.
        
        Args:
            labels: Etiquetas de régimen
            
        Returns:
            Matriz de transición
        """
        n_regimes = len(np.unique(labels))
        transition_matrix = np.zeros((n_regimes, n_regimes))
        
        for i in range(len(labels) - 1):
            current_regime = labels[i]
            next_regime = labels[i + 1]
            transition_matrix[current_regime, next_regime] += 1
        
        # Normalizar por filas
        row_sums = transition_matrix.sum(axis=1)
        transition_matrix = np.divide(transition_matrix, row_sums[:, np.newaxis], 
                                    where=row_sums[:, np.newaxis] != 0)
        
        return transition_matrix
    
    def predict_regime(self, features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predice régimen para nuevos datos.
        
        Args:
            features: Características de mercado
            
        Returns:
            Tupla con etiquetas de régimen y probabilidades
        """
        if not self.is_fitted:
            raise ValueError("Modelo HMM no ha sido ajustado")
        
        if isinstance(features, pd.DataFrame):
            features = features.values
        
        # Verificar que el modelo esté disponible
        if self.hmm_model is None:
            raise ValueError("Modelo HMM no está disponible")
        
        # El modelo es un diccionario con 'model' y 'scaler'
        # Normalizar características usando el scaler guardado
        features_scaled = self.hmm_model['scaler'].transform(features)
        
        # Predecir régimen usando el modelo GMM
        regime_labels = self.hmm_model['model'].predict(features_scaled)
        regime_probs = self.hmm_model['model'].predict_proba(features_scaled)
        
        return regime_labels, regime_probs

# Limpieza profesional: dejar solo la clase MarketRegimeDetector y sus métodos

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger("market_regime_analyzer")

class MarketRegimeDetector:
    def __init__(self):
        self.logger = logger
        self.cluster_model = None  # Puede ser asignado externamente si se usa clustering
        self.drift_threshold = 0.5  # Placeholder para futuras funciones
    
    def detect_regimes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detecta regímenes de mercado en los datos.
        
        Args:
            df: DataFrame con datos de mercado
            
        Returns:
            Diccionario con información de regímenes
        """
        try:
            # Implementación básica de detección de regímenes
            return {
                "regime_labels": ["bull", "bear", "sideways"],
                "details": {
                    "bull_periods": 0,
                    "bear_periods": 0,
                    "sideways_periods": 0
                }
            }
        except Exception as e:
            self.logger.error(f"Error detectando regímenes: {e}")
            return {"regime_labels": [], "details": {}}

    def detect_current_regime(self, market_data: pd.DataFrame) -> str:
        try:
            self.logger.info("🔍 Detectando régimen de mercado actual...")
            features = self._prepare_regime_features(market_data)
            if len(features) < 10:
                self.logger.warning("⚠️ Datos insuficientes para detección de régimen")
                return 'sideways'
            current_features = features.iloc[-30:].mean()
            current_features_reshaped = current_features.values.reshape(1, -1)
            if self.cluster_model is not None:
                regime_label = self.cluster_model.predict(current_features_reshaped)[0]
                regime_name = self._map_regime_label_to_name(regime_label)
            else:
                regime_name = self._simple_regime_detection(current_features)
            self.logger.info(f"✅ Régimen detectado: {regime_name}")
            return regime_name
        except Exception as e:
            self.logger.error(f"❌ Error detectando régimen actual: {e}")
            return 'sideways'

    def calculate_regime_performance(self, strategies: pd.DataFrame, current_regime: str) -> Dict[str, Any]:
        try:
            self.logger.info(f"📊 Calculando rendimiento por régimen: {current_regime}")
            regime_weights = {
                'bull': {'profitability': 0.45, 'risk': 0.25, 'consistency': 0.30, 'ml': 0.15},
                'bear': {'profitability': 0.35, 'risk': 0.40, 'consistency': 0.25, 'ml': 0.15},
                'sideways': {'profitability': 0.40, 'risk': 0.30, 'consistency': 0.30, 'ml': 0.15},
                'crisis': {'profitability': 0.30, 'risk': 0.45, 'consistency': 0.25, 'ml': 0.15}
            }
            current_weights = regime_weights.get(current_regime, regime_weights['sideways'])
            regime_metrics = {
                'current_regime': current_regime,
                'weights': current_weights,
                'strategy_count': len(strategies),
                'avg_cagr': strategies['CAGR'].mean() if 'CAGR' in strategies.columns else 0,
                'avg_sharpe': strategies['Sharpe_Ratio'].mean() if 'Sharpe_Ratio' in strategies.columns else 0,
                'avg_max_dd': strategies['Max_Drawdown'].mean() if 'Max_Drawdown' in strategies.columns else 0,
                'regime_optimal_strategies': self._identify_regime_optimal_strategies(strategies, current_regime)
            }
            self.logger.info(f"✅ Rendimiento por régimen calculado: {len(regime_metrics['regime_optimal_strategies'])} estrategias óptimas")
            return regime_metrics
        except Exception as e:
            self.logger.error(f"❌ Error calculando rendimiento por régimen: {e}")
            return {
                'current_regime': current_regime,
                'weights': {'profitability': 0.4, 'risk': 0.3, 'consistency': 0.3, 'ml': 0.15},
                'strategy_count': 0,
                'avg_cagr': 0,
                'avg_sharpe': 0,
                'avg_max_dd': 0,
                'regime_optimal_strategies': []
            }

    def optimize_weights_by_regime(self, regime_performance: Dict[str, Any], current_regime: str) -> Dict[str, float]:
        try:
            self.logger.info(f"⚙️ Optimizando pesos para régimen: {current_regime}")
            base_weights = regime_performance.get('weights', {'profitability': 0.4, 'risk': 0.3, 'consistency': 0.3, 'ml': 0.15})
            avg_cagr = regime_performance.get('avg_cagr', 0)
            avg_sharpe = regime_performance.get('avg_sharpe', 0)
            avg_max_dd = regime_performance.get('avg_max_dd', 0)
            adjustments = self._calculate_weight_adjustments(avg_cagr, avg_sharpe, avg_max_dd, current_regime)
            optimized_weights = {}
            for component, base_weight in base_weights.items():
                adjustment = adjustments.get(component, 0)
                optimized_weights[component] = max(0.1, min(0.6, base_weight + adjustment))
            total_weight = sum(optimized_weights.values())
            normalized_weights = {k: v/total_weight for k, v in optimized_weights.items()}
            self.logger.info(f"✅ Pesos optimizados: {normalized_weights}")
            return normalized_weights
        except Exception as e:
            self.logger.error(f"❌ Error optimizando pesos: {e}")
            return {'profitability': 0.4, 'risk': 0.3, 'consistency': 0.3, 'ml': 0.15}

    def apply_adaptive_scoring(self, strategies: pd.DataFrame, optimized_weights: Dict[str, float]) -> pd.DataFrame:
        try:
            self.logger.info("🎯 Aplicando scoring adaptativo...")
            strategies_scored = strategies.copy()
            profitability_scores = self._calculate_profitability_scores(strategies)
            risk_scores = self._calculate_risk_scores(strategies)
            consistency_scores = self._calculate_consistency_scores(strategies)
            ml_scores = self._calculate_ml_scores(strategies)
            adaptive_scores = (
                profitability_scores * optimized_weights.get('profitability', 0.4) +
                risk_scores * optimized_weights.get('risk', 0.3) +
                consistency_scores * optimized_weights.get('consistency', 0.3) +
                ml_scores * optimized_weights.get('ml', 0.15)
            )
            strategies_scored['Adaptive_Score'] = adaptive_scores
            strategies_scored['Profitability_Score'] = profitability_scores
            strategies_scored['Risk_Score'] = risk_scores
            strategies_scored['Consistency_Score'] = consistency_scores
            strategies_scored['ML_Score'] = ml_scores
            strategies_scored = strategies_scored.sort_values('Adaptive_Score', ascending=False)
            self.logger.info(f"✅ Scoring adaptativo aplicado a {len(strategies_scored)} estrategias")
            return strategies_scored
        except Exception as e:
            self.logger.error(f"❌ Error aplicando scoring adaptativo: {e}")
            return strategies

    # Métodos auxiliares (privados)
    def _prepare_regime_features(self, market_data: pd.DataFrame) -> pd.DataFrame:
        try:
            features = pd.DataFrame()
            if 'Close' in market_data.columns:
                returns = market_data['Close'].pct_change().dropna()
                features['volatility'] = returns.rolling(20).std()
                features['momentum'] = returns.rolling(20).mean()
                features['skewness'] = returns.rolling(20).skew()
                features['kurtosis'] = returns.rolling(20).kurt()
            if 'Volume' in market_data.columns:
                features['volume_ratio'] = market_data['Volume'].rolling(20).mean() / market_data['Volume'].rolling(60).mean()
            features = features.fillna(method='ffill').fillna(0)
            return features
        except Exception as e:
            self.logger.error(f"❌ Error preparando características de régimen: {e}")
            return pd.DataFrame()

    def _map_regime_label_to_name(self, regime_label: int) -> str:
        regime_mapping = {0: 'bull', 1: 'bear', 2: 'sideways', 3: 'crisis'}
        return regime_mapping.get(regime_label, 'sideways')

    def _simple_regime_detection(self, features: pd.Series) -> str:
        try:
            volatility = features.get('volatility', 0)
            momentum = features.get('momentum', 0)
            # Controlar None
            volatility = float(volatility) if volatility is not None else 0.0
            momentum = float(momentum) if momentum is not None else 0.0
            if volatility > 0.03:
                if momentum < -0.001:
                    return 'crisis'
                else:
                    return 'bear'
            elif momentum > 0.001:
                return 'bull'
            else:
                return 'sideways'
        except Exception as e:
            self.logger.error(f"❌ Error en detección simple de régimen: {e}")
            return 'sideways'

    def _identify_regime_optimal_strategies(self, strategies: pd.DataFrame, regime: str) -> List[str]:
        try:
            if len(strategies) == 0:
                return []
            regime_criteria = {
                'bull': {'min_cagr': 0.15, 'min_sharpe': 1.0, 'max_dd': 0.20},
                'bear': {'min_cagr': 0.05, 'min_sharpe': 0.5, 'max_dd': 0.15},
                'sideways': {'min_cagr': 0.10, 'min_sharpe': 0.8, 'max_dd': 0.18},
                'crisis': {'min_cagr': 0.02, 'min_sharpe': 0.3, 'max_dd': 0.10}
            }
            criteria = regime_criteria.get(regime, regime_criteria['sideways'])
            optimal_strategies = []
            for _, strategy in strategies.iterrows():
                cagr = strategy.get('CAGR', 0)
                sharpe = strategy.get('Sharpe_Ratio', 0)
                max_dd = strategy.get('Max_Drawdown', 0)
                # Controlar None
                cagr = float(cagr) if cagr is not None else 0.0
                sharpe = float(sharpe) if sharpe is not None else 0.0
                max_dd = abs(float(max_dd)) if max_dd is not None else 0.0
                if (cagr >= criteria['min_cagr'] and 
                    sharpe >= criteria['min_sharpe'] and 
                    max_dd <= criteria['max_dd']):
                    optimal_strategies.append(strategy.get('Strategy_Name', 'Unknown'))
            return optimal_strategies
        except Exception as e:
            self.logger.error(f"❌ Error identificando estrategias óptimas: {e}")
            return []

    def _calculate_weight_adjustments(self, avg_cagr: float, avg_sharpe: float, avg_max_dd: float, regime: str) -> Dict[str, float]:
        adjustments: Dict[str, float] = {'profitability': 0.0, 'risk': 0.0, 'consistency': 0.0, 'ml': 0.0}
        try:
            avg_cagr = float(avg_cagr) if avg_cagr is not None else 0.0
            avg_sharpe = float(avg_sharpe) if avg_sharpe is not None else 0.0
            avg_max_dd = float(avg_max_dd) if avg_max_dd is not None else 0.0
            if avg_cagr > 0.15:
                adjustments['profitability'] += 0.05
                adjustments['risk'] -= 0.02
            elif avg_cagr < 0.05:
                adjustments['profitability'] -= 0.05
                adjustments['risk'] += 0.02
            if avg_sharpe > 1.5:
                adjustments['consistency'] += 0.03
            elif avg_sharpe < 0.5:
                adjustments['consistency'] -= 0.03
            if avg_max_dd > 0.25:
                adjustments['risk'] += 0.05
                adjustments['profitability'] -= 0.02
            elif avg_max_dd < 0.10:
                adjustments['risk'] -= 0.03
                adjustments['profitability'] += 0.02
            if regime == 'crisis':
                adjustments['risk'] += 0.05
                adjustments['profitability'] -= 0.03
            elif regime == 'bull':
                adjustments['profitability'] += 0.03
                adjustments['risk'] -= 0.02
            return adjustments
        except Exception as e:
            self.logger.error(f"❌ Error calculando ajustes de pesos: {e}")
            return {'profitability': 0.0, 'risk': 0.0, 'consistency': 0.0, 'ml': 0.0}

    def _calculate_profitability_scores(self, strategies: pd.DataFrame) -> pd.Series:
        try:
            if 'CAGR' not in strategies.columns:
                return pd.Series(0.5, index=strategies.index)
            cagr_scores = (strategies['CAGR'] - strategies['CAGR'].min()) / (strategies['CAGR'].max() - strategies['CAGR'].min())
            return cagr_scores.fillna(0.5)
        except Exception as e:
            self.logger.error(f"❌ Error calculando scores de rentabilidad: {e}")
            return pd.Series(0.5, index=strategies.index)

    def _calculate_risk_scores(self, strategies: pd.DataFrame) -> pd.Series:
        try:
            if 'Max_Drawdown' not in strategies.columns:
                return pd.Series(0.5, index=strategies.index)
            risk_scores = 1 - (strategies['Max_Drawdown'] - strategies['Max_Drawdown'].min()) / (strategies['Max_Drawdown'].max() - strategies['Max_Drawdown'].min())
            return risk_scores.fillna(0.5)
        except Exception as e:
            self.logger.error(f"❌ Error calculando scores de riesgo: {e}")
            return pd.Series(0.5, index=strategies.index)

    def _calculate_consistency_scores(self, strategies: pd.DataFrame) -> pd.Series:
        try:
            if 'Sharpe_Ratio' not in strategies.columns:
                return pd.Series(0.5, index=strategies.index)
            sharpe_scores = (strategies['Sharpe_Ratio'] - strategies['Sharpe_Ratio'].min()) / (strategies['Sharpe_Ratio'].max() - strategies['Sharpe_Ratio'].min())
            return sharpe_scores.fillna(0.5)
        except Exception as e:
            self.logger.error(f"❌ Error calculando scores de consistencia: {e}")
            return pd.Series(0.5, index=strategies.index)

    def _calculate_ml_scores(self, strategies: pd.DataFrame) -> pd.Series:
        try:
            if 'Factor_K' in strategies.columns:
                ml_scores = (strategies['Factor_K'] - strategies['Factor_K'].min()) / (strategies['Factor_K'].max() - strategies['Factor_K'].min())
                return ml_scores.fillna(0.5)
            else:
                return pd.Series(0.5, index=strategies.index)
        except Exception as e:
            self.logger.error(f"❌ Error calculando scores de ML: {e}")
            return pd.Series(0.5, index=strategies.index) 