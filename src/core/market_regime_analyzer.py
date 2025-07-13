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
                    feature_columns = data.select_dtypes(include=[np.number]).columns.tolist()
                
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

class MarketRegimeDetector:
    """
    Detector de regímenes de mercado usando clustering.
    
    Esta clase implementa detección de regímenes usando técnicas de clustering
    para identificar patrones en el comportamiento del mercado.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el detector de regímenes.
        
        Args:
            config: Configuración opcional del detector
        """
        self.config = config or {}
        self.n_regimes = self.config.get('n_regimes', 4)
        self.random_state = self.config.get('random_state', 42)
        self.scaler = StandardScaler()
        self.cluster_model = None
        self.is_fitted = False
        
    def extract_market_features(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Extrae características relevantes para detección de regímenes.
        
        Args:
            market_data: DataFrame con datos de mercado
            
        Returns:
            DataFrame con características extraídas
        """
        try:
            logger.info("Extrayendo características de mercado para detección de regímenes...")
            
            features_df = pd.DataFrame()
            
            # Características básicas de precio
            if 'Close' in market_data.columns:
                prices = market_data['Close']
                
                # Asegurar que prices es una Series
                if isinstance(prices, pd.DataFrame):
                    prices = prices.iloc[:, 0]
                
                # Retornos
                features_df['returns'] = prices.pct_change().fillna(0)
                
                # Volatilidad móvil
                features_df['volatility_20'] = features_df['returns'].rolling(20).std().fillna(0)
                features_df['volatility_60'] = features_df['returns'].rolling(60).std().fillna(0)
                
                # Momentum
                features_df['momentum_5'] = prices.pct_change(5).fillna(0)
                features_df['momentum_20'] = prices.pct_change(20).fillna(0)
                features_df['momentum_60'] = prices.pct_change(60).fillna(0)
                
                # RSI
                features_df['rsi_14'] = self._calculate_rsi(prices, 14)
                
                # Bandas de Bollinger
                bb_upper, bb_lower = self._calculate_bollinger_bands(prices, 20, 2)
                features_df['bb_position'] = (prices - bb_lower) / (bb_upper - bb_lower)
                features_df['bb_width'] = (bb_upper - bb_lower) / prices
                
                # Drawdown
                features_df['drawdown'] = self._calculate_drawdown(prices)
                
            # Características de volumen si están disponibles
            if 'Volume' in market_data.columns:
                volume = market_data['Volume']
                features_df['volume_ma_ratio'] = volume / volume.rolling(20).mean()
                features_df['volume_trend'] = volume.pct_change(5).fillna(0)
            
            # Características de volatilidad
            if 'High' in market_data.columns and 'Low' in market_data.columns:
                high_low_range = (market_data['High'] - market_data['Low']) / market_data['Close']
                features_df['range_volatility'] = high_low_range.rolling(20).mean()
            
            # Limpiar características
            features_df = features_df.ffill().bfill().fillna(0)
            
            # Eliminar columnas con varianza cero
            features_df = features_df.loc[:, features_df.var() > 0]
            
            logger.info(f"Características extraídas: {features_df.shape[1]} columnas")
            return features_df
            
        except Exception as e:
            logger.error(f"Error extrayendo características de mercado: {str(e)}")
            raise
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcula el RSI (Relative Strength Index)."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series]:
        """Calcula las bandas de Bollinger."""
        ma = prices.rolling(period).mean()
        std = prices.rolling(period).std()
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        return upper_band, lower_band
    
    def _calculate_drawdown(self, prices: pd.Series) -> pd.Series:
        """Calcula el drawdown."""
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return drawdown
    
    def detect_regimes(self, df):
        """Detecta regímenes de mercado, robusto a tipos incorrectos."""
        import pandas as pd
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"detect_regimes espera un DataFrame, recibió: {type(df)}")
        try:
            logger.info(f"Detectando regímenes de mercado usando {self.n_regimes} clusters...")
            
            # Normalizar características
            features_scaled = self.scaler.fit_transform(df)
            
            # Aplicar clustering
            kmeans = KMeans(
                n_clusters=self.n_regimes,
                random_state=self.random_state,
                n_init="auto"
            )
            
            regime_labels = kmeans.fit_predict(features_scaled)
            self.cluster_model = kmeans
            self.is_fitted = True
            
            # Mapear clusters a regímenes
            feature_names_list = df.columns.tolist()
            regime_mapping = self._map_clusters_to_regimes(kmeans.cluster_centers_, feature_names_list)
            
            # Caracterizar regímenes
            regime_info = self._characterize_regimes(df, regime_labels, regime_mapping)
            
            logger.info(f"Regímenes detectados: {len(np.unique(regime_labels))}")
            return regime_labels, regime_info
            
        except Exception as e:
            logger.error(f"Error detectando regímenes: {str(e)}")
            raise
    
    def _map_clusters_to_regimes(self, centroids: np.ndarray, feature_names: List[str]) -> Dict[int, str]:
        """
        Mapea clusters a tipos de régimen basado en características.
        
        Args:
            centroids: Centroides de los clusters
            feature_names: Nombres de las características
            
        Returns:
            Mapeo de cluster_id a tipo de régimen
        """
        regime_mapping = {}
        
        for i, centroid in enumerate(centroids):
            # Analizar características del centroide para determinar tipo de régimen
            regime_type = self._classify_regime_by_centroid(centroid, feature_names)
            regime_mapping[i] = regime_type
        
        return regime_mapping
    
    def _classify_regime_by_centroid(self, centroid: np.ndarray, feature_names: List[str]) -> str:
        """
        Clasifica un régimen basado en su centroide.

        Args:
            centroid: Centroide del cluster
            feature_names: Nombres de las características

        Returns:
            Tipo de régimen
        """
        # Crear diccionario de características con validación de tipos
        features = {}
        for i, name in enumerate(feature_names):
            if isinstance(name, str):
                features[name] = centroid[i] if i < len(centroid) else 0.0
            else:
                # Si el nombre no es string, usar índice como clave
                features[str(i)] = centroid[i] if i < len(centroid) else 0.0
        
        # Clasificar basado en características clave
        volatility_score = 0
        momentum_score = 0
        volume_score = 0
        
        # Analizar volatilidad con validación de tipos
        for feature, value in features.items():
            if isinstance(feature, str):
                feature_lower = feature.lower()
                if 'volatility' in feature_lower:
                    volatility_score += abs(float(value))
                elif 'momentum' in feature_lower:
                    momentum_score += float(value)
                elif 'volume' in feature_lower:
                    volume_score += float(value)
        
        # Clasificar régimen
        if volatility_score > 0.5:
            if momentum_score > 0:
                return RegimeType.BULL.value
            else:
                return RegimeType.BEAR.value
        elif volume_score > 0.3:
            return RegimeType.VOLATILE.value
        elif volatility_score < 0.2:
            return RegimeType.CALM.value
        else:
            return RegimeType.SIDEWAYS.value
    
    def _characterize_regimes(self, features_df: pd.DataFrame, labels: np.ndarray, 
                            regime_mapping: Dict[int, str]) -> Dict[str, Any]:
        """
        Caracteriza cada régimen detectado.
        
        Args:
            features_df: DataFrame con características
            labels: Etiquetas de régimen
            regime_mapping: Mapeo de clusters a regímenes
            
        Returns:
            Información detallada de cada régimen
        """
        regime_info = {}
        
        for regime_id in np.unique(labels):
            regime_mask = labels == regime_id
            regime_features = features_df[regime_mask]
            
            if len(regime_features) > 0:
                regime_type = regime_mapping.get(regime_id, f"regime_{regime_id}")
                
                regime_info[regime_type] = {
                    'cluster_id': int(regime_id),
                    'size': int(np.sum(regime_mask)),
                    'percentage': float(np.mean(regime_mask) * 100),
                    'mean_features': regime_features.mean().to_dict(),
                    'characteristics': {
                        'volatility': float(regime_features.std().mean()),
                        'stability': float(1.0 / (1.0 + regime_features.std().mean())),
                        'momentum': float(regime_features.mean().mean())
                    }
                }
        
        return regime_info
    
    def analyze_strategy_performance_by_regime(self, strategies_df: pd.DataFrame, 
                                            regime_labels: np.ndarray) -> Dict[str, pd.DataFrame]:
        """
        Analiza el rendimiento de estrategias por régimen.
        
        Args:
            strategies_df: DataFrame con estrategias
            regime_labels: Etiquetas de régimen
            
        Returns:
            Diccionario con rendimiento por régimen
        """
        try:
            logger.info("Analizando rendimiento de estrategias por régimen...")
            
            performance_by_regime = {}
            
            # Agrupar estrategias por régimen
            for regime_id in np.unique(regime_labels):
                regime_mask = regime_labels == regime_id
                
                if np.sum(regime_mask) > 0:
                    # Filtrar estrategias que operaron en este régimen
                    regime_strategies = strategies_df[regime_mask]
                    
                    if not regime_strategies.empty:
                        # Asegurar que regime_strategies sea DataFrame
                        if isinstance(regime_strategies, pd.Series):
                            regime_strategies = regime_strategies.to_frame()
                        
                        # Calcular métricas de rendimiento para este régimen
                        regime_performance = self._calculate_regime_performance(regime_strategies)
                        performance_by_regime[f'regime_{regime_id}'] = regime_performance
            
            logger.info(f"Análisis por régimen completado: {len(performance_by_regime)} regímenes")
            return performance_by_regime
            
        except Exception as e:
            logger.error(f"Error analizando rendimiento por régimen: {str(e)}")
            raise
    
    def _calculate_regime_performance(self, regime_strategies: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula métricas de rendimiento para un régimen específico.
        
        Args:
            regime_strategies: Estrategias que operaron en el régimen
            
        Returns:
            DataFrame con métricas de rendimiento
        """
        performance_metrics = {}
        
        # Métricas de rendimiento
        if 'CAGR' in regime_strategies.columns:
            performance_metrics['avg_cagr'] = regime_strategies['CAGR'].mean()
            performance_metrics['std_cagr'] = regime_strategies['CAGR'].std()
        
        if 'Sharpe Ratio' in regime_strategies.columns:
            performance_metrics['avg_sharpe'] = regime_strategies['Sharpe Ratio'].mean()
            performance_metrics['std_sharpe'] = regime_strategies['Sharpe Ratio'].std()
        
        if 'Drawdown' in regime_strategies.columns:
            performance_metrics['avg_drawdown'] = regime_strategies['Drawdown'].mean()
            performance_metrics['max_drawdown'] = regime_strategies['Drawdown'].max()
        
        if 'Profit factor' in regime_strategies.columns:
            performance_metrics['avg_profit_factor'] = regime_strategies['Profit factor'].mean()
        
        # Métricas de riesgo
        if 'Ulcer Index %' in regime_strategies.columns:
            performance_metrics['avg_ulcer_index'] = regime_strategies['Ulcer Index %'].mean()
        
        # Número de estrategias
        performance_metrics['n_strategies'] = len(regime_strategies)
        
        return pd.DataFrame([performance_metrics])

class MarketRegimeDetectorEnhanced(MarketRegimeDetector):
    """
    Versión mejorada del detector de regímenes con características adicionales.
    
    Esta clase extiende MarketRegimeDetector con funcionalidades avanzadas
    como análisis de correlación entre regímenes y predicción de transiciones.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el detector mejorado.
        
        Args:
            config: Configuración opcional del detector
        """
        super().__init__(config)
        self.regime_history = []
        self.transition_probabilities = None
        
    def extract_market_features(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Extrae características mejoradas para detección de regímenes.
        
        Args:
            market_data: DataFrame con datos de mercado
            
        Returns:
            DataFrame con características extraídas
        """
        # Obtener características básicas
        features_df = super().extract_market_features(market_data)
        
        # Añadir características avanzadas
        if 'Close' in market_data.columns:
            prices = market_data['Close']
            
            # Asegurar que prices es una Series
            if isinstance(prices, pd.DataFrame):
                prices = prices.iloc[:, 0]
            
            # Características de tendencia
            features_df['trend_strength'] = self._calculate_trend_strength(prices)
            features_df['trend_duration'] = self._calculate_trend_duration(prices)
            
            # Características de volatilidad condicional
            features_df['conditional_volatility'] = self._calculate_conditional_volatility(prices)
            
            # Características de momentum
            features_df['momentum_divergence'] = self._calculate_momentum_divergence(prices)
            
            # Características de volumen (si está disponible)
            if 'Volume' in market_data.columns:
                volume = market_data['Volume']
                # Asegurar que volume es una Series
                if isinstance(volume, pd.DataFrame):
                    volume = volume.iloc[:, 0]
                features_df['volume_price_trend'] = self._calculate_volume_price_trend(prices, volume)
        
        return features_df
    
    def _calculate_trend_strength(self, prices: pd.Series) -> pd.Series:
        """Calcula la fuerza de la tendencia."""
        # Usar regresión lineal móvil para medir tendencia
        trend_strength = prices.rolling(20).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
        )
        return trend_strength.fillna(0)  # type: ignore
    
    def _calculate_trend_duration(self, prices: pd.Series) -> pd.Series:
        """Calcula la duración de la tendencia actual."""
        # Implementación simplificada
        trend_duration = prices.rolling(10).apply(
            lambda x: len([i for i in range(1, len(x)) if x.iloc[i] > x.iloc[i-1]])
        )
        return trend_duration.fillna(0)  # type: ignore
    
    def _calculate_conditional_volatility(self, prices: pd.Series) -> pd.Series:
        """Calcula volatilidad condicional."""
        returns = prices.pct_change().fillna(0)
        conditional_vol = returns.rolling(20).apply(
            lambda x: np.std(x[x < 0]) if len(x[x < 0]) > 0 else 0
        )
        return conditional_vol.fillna(0)  # type: ignore
    
    def _calculate_momentum_divergence(self, prices: pd.Series) -> pd.Series:
        """Calcula divergencia de momentum."""
        momentum_short = prices.pct_change(5)
        momentum_long = prices.pct_change(20)
        divergence = momentum_short - momentum_long
        return divergence.fillna(0)
    
    def _calculate_volume_price_trend(self, prices: pd.Series, volume: pd.Series) -> pd.Series:
        """Calcula tendencia de volumen-precio."""
        price_change = prices.pct_change().fillna(0)
        volume_change = volume.pct_change().fillna(0)
        vpt = (price_change * volume_change).rolling(10).sum()
        return vpt.fillna(0)
    
    def predict_regime_transitions(self, features_df: pd.DataFrame, 
                                 lookback_period: int = 20) -> Dict[str, Any]:
        """
        Predice transiciones entre regímenes.
        
        Args:
            features_df: DataFrame con características
            lookback_period: Período de lookback para predicción
            
        Returns:
            Diccionario con predicciones de transición
        """
        try:
            logger.info("Prediciendo transiciones entre regímenes...")
            
            if not self.is_fitted:
                raise ValueError("Modelo no ha sido ajustado")
            
            # Obtener etiquetas de régimen para datos históricos
            features_scaled = self.scaler.transform(features_df)
            
            if self.cluster_model is None:
                raise ValueError("Modelo no ha sido ajustado")
            
            regime_labels = self.cluster_model.predict(features_scaled)
            
            # Asegurar que regime_labels sea ndarray
            if not isinstance(regime_labels, np.ndarray):
                regime_labels = np.asarray(regime_labels)
            
            # Calcular probabilidades de transición
            transition_probs = self._calculate_transition_probabilities(regime_labels)
            
            # Predecir próximo régimen
            current_regime = regime_labels[-1]
            next_regime_probs = transition_probs[current_regime]
            
            # Encontrar régimen más probable
            most_likely_regime = np.argmax(next_regime_probs)
            confidence = next_regime_probs[most_likely_regime]
            
            prediction_result = {
                'current_regime': int(current_regime),
                'predicted_regime': int(most_likely_regime),
                'confidence': float(confidence),
                'transition_probabilities': next_regime_probs.tolist(),
                'regime_stability': self._calculate_regime_stability(regime_labels)
            }
            
            logger.info(f"Predicción completada: régimen actual {current_regime}, "
                       f"predicción {most_likely_regime} (confianza: {confidence:.2f})")
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Error prediciendo transiciones: {str(e)}")
            raise
    
    def _calculate_transition_probabilities(self, regime_labels: np.ndarray) -> np.ndarray:
        """Calcula matriz de probabilidades de transición."""
        n_regimes = len(np.unique(regime_labels))
        transition_matrix = np.zeros((n_regimes, n_regimes))
        
        for i in range(len(regime_labels) - 1):
            current = regime_labels[i]
            next_regime = regime_labels[i + 1]
            transition_matrix[current, next_regime] += 1
        
        # Normalizar
        row_sums = transition_matrix.sum(axis=1)
        transition_matrix = np.divide(transition_matrix, row_sums[:, np.newaxis], 
                                    where=row_sums[:, np.newaxis] != 0)
        
        return transition_matrix
    
    def _calculate_regime_stability(self, regime_labels: np.ndarray) -> float:
        """Calcula la estabilidad del régimen actual."""
        if len(regime_labels) < 10:
            return 0.5
        
        # Calcular frecuencia del régimen actual en los últimos períodos
        current_regime = regime_labels[-1]
        recent_regimes = regime_labels[-10:]
        stability = np.mean(recent_regimes == current_regime)
        
        return float(stability) 