import pandas as pd
import numpy as np
import gc
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
import warnings
from typing import Optional, Any, Union
warnings.filterwarnings('ignore')

# Importar hmmlearn para HMM real
try:
    from hmmlearn import hmm
    HMM_AVAILABLE = True
except ImportError:
    HMM_AVAILABLE = False
    print("⚠️ hmmlearn no disponible. HMM será simulado.")

from src.core.config.config_manager import ConfigManagerEnhanced
from src.core.config.progress_callback import ProgressCallback
from src.data.data_manager import DataManager
from src.logger_config import setup_logger

# Importar analizadores científicos si están disponibles
try:
    from src.core.market_regime_analyzer import HiddenMarkovModelAnalyzer
    from src.core.robustness_analyzer import StressTestGenerator
    # DataDriftDetector y TemporalValidation no están disponibles en integration_layer
    # Se implementan en otros módulos del proyecto
except ImportError:
    HiddenMarkovModelAnalyzer = None
    StressTestGenerator = None

# Variables para compatibilidad (no disponibles en integration_layer)
DataDriftDetector = None
TemporalValidation = None

CHUNK_SIZE = 10000
MAX_WORKERS = 4

class FactorKElite96Enhanced:
    """
    Motor principal mejorado con IA avanzada: HMM real, clustering optimizado,
    detección de anomalías, componentes temporal y predictivo.

    ADVERTENCIA PROFESIONAL:
    ------------------------------------------------------------
    Este módulo SOLO debe recibir DataFrames ya validados y preparados por DataManager
    u otras funciones centralizadas de la capa data. No realizar validación, carga ni
    manipulación local de datos aquí. Toda gestión de datos debe estar centralizada.
    ------------------------------------------------------------
    """
    
    def __init__(self, config: Optional[Dict] = None, progress_callback: Optional[ProgressCallback] = None):
        self.logger = setup_logger("kforce")
        self.config_manager = ConfigManagerEnhanced()
        self.data_manager = DataManager()
        self.progress_callback = progress_callback
        
        # Configuración de rendimiento
        self.chunk_size = CHUNK_SIZE
        self.max_workers = MAX_WORKERS
        self.scientific_improvements_enabled = False
        self.cache_dir = None
        
        # Componentes científicos (opcionales)
        self.hmm_analyzer = None
        self.stress_tester = None
        self.drift_detector = None
        self.temporal_validator = None
        
        # Modelos de IA
        self.hmm_model = None
        self.isolation_forest = None
        self.ml_scorer = None
        self.optimized_weights = None
        
        # Cache para optimización
        self._calculation_cache = {}
        
        if config:
            self.config_manager.current_config.update(config)
        
        # SIEMPRE ACTIVAR MEJORAS CIENTÍFICAS POR DEFECTO
        self.enable_scientific_improvements()
    
    def enable_scientific_improvements(self, cache_dir: str = "cache/scientific"):
        """
        Habilita las mejoras científicas con IA avanzada.
        """
        try:
            self.scientific_improvements_enabled = True
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Inicializar modelos de IA
            self._initialize_ai_models()
            
            if HiddenMarkovModelAnalyzer:
                self.hmm_analyzer = HiddenMarkovModelAnalyzer()
            if StressTestGenerator:
                self.stress_tester = StressTestGenerator()
            if DataDriftDetector:
                self.drift_detector = DataDriftDetector()
            if TemporalValidation:
                self.temporal_validator = TemporalValidation()
                
            self.logger.info("Mejoras científicas con IA avanzada habilitadas")
        except Exception as e:
            self.logger.error(f"Error habilitando mejoras científicas: {e}")
            self.scientific_improvements_enabled = False
    
    def _initialize_ai_models(self):
        """Inicializa modelos de IA avanzada."""
        try:
            # Isolation Forest para detección de anomalías
            self.isolation_forest = IsolationForest(
                contamination="auto",  # Cambiar de float a str
                random_state=42,
                n_estimators=100
            )
            
            # Modelo de ML para scoring predictivo
            self.ml_scorer = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            
            # HMM real si está disponible
            if HMM_AVAILABLE:
                self.hmm_model = hmm.GaussianHMM(
                    n_components=3,
                    covariance_type="full",
                    random_state=42
                )
            
            self.logger.info("Modelos de IA inicializados correctamente")
            
        except Exception as e:
            self.logger.warning(f"Error inicializando modelos de IA: {e}")
            # Inicializar con valores por defecto si falla
            self.isolation_forest = None
            self.ml_scorer = None
    
    def _optimize_clustering(self, X: np.ndarray) -> Tuple[int, np.ndarray]:
        """
        Optimiza el número de clusters usando silhouette score y elbow method.
        
        Args:
            X: Datos para clustering
            
        Returns:
            Tuple con número óptimo de clusters y labels
        """
        try:
            if not isinstance(X, np.ndarray):
                X = np.array(X)
            
            # Probar diferentes números de clusters
            n_clusters_range = range(2, min(8, len(X) // 10 + 1))
            silhouette_scores = []
            inertias = []
            
            for n_clusters in n_clusters_range:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
                cluster_labels = kmeans.fit_predict(X)
                
                # Calcular silhouette score
                if len(np.unique(cluster_labels)) > 1:
                    silhouette_avg = silhouette_score(X, cluster_labels)
                    silhouette_scores.append(silhouette_avg)
                    inertias.append(kmeans.inertia_)
                else:
                    silhouette_scores.append(0)
                    inertias.append(float('inf'))
            
            # Encontrar número óptimo de clusters
            if silhouette_scores:
                optimal_n_clusters = n_clusters_range[np.argmax(silhouette_scores)]
            else:
                optimal_n_clusters = 3
            
            # Aplicar clustering óptimo
            kmeans_optimal = KMeans(n_clusters=optimal_n_clusters, random_state=42, n_init='auto')
            optimal_labels = kmeans_optimal.fit_predict(X)
            
            self.logger.info(f"Clustering optimizado: {optimal_n_clusters} clusters (silhouette: {max(silhouette_scores):.3f})")
            
            return optimal_n_clusters, optimal_labels
            
        except Exception as e:
            self.logger.warning(f"Error optimizando clustering: {e}")
            # Fallback a 3 clusters
            kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
            return 3, kmeans.fit_predict(X)
    
    def _detect_anomalies_multivariate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta anomalías multivariadas usando Isolation Forest.
        
        Args:
            df: DataFrame con métricas
            
        Returns:
            DataFrame con columna de anomalías
        """
        try:
            anomaly_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR', 'Profit_factor', 'Total_Trades']
            available_metrics = [m for m in anomaly_metrics if m in df.columns]
            
            if len(available_metrics) >= 2:
                X = df[available_metrics].fillna(0).values
                if self.isolation_forest is not None:
                    anomaly_labels = self.isolation_forest.fit_predict(X)
                else:
                    self.logger.warning("IsolationForest no inicializado, asignando normalidad por defecto")
                    anomaly_labels = np.ones(len(df))
                df['Anomaly_Score'] = anomaly_labels
                df['Is_Anomaly'] = (anomaly_labels == -1).astype(int)
                anomaly_penalty = np.where(df['Is_Anomaly'] == 1, 0.2, 0)
                if 'FK96_Elite_Enhanced' in df.columns:
                    df['FK96_Elite_Enhanced'] *= (1 - anomaly_penalty)
                self.logger.info(f"Detección de anomalías: {df['Is_Anomaly'].sum()} estrategias anómalas")
            return df
        except Exception as e:
            self.logger.warning(f"Error detectando anomalías: {e}")
            return df
    
    def _calculate_temporal_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula componente temporal basado en robustez estadística (trades/mes y trades/año) según temporalidad.
        Penaliza solo si la estrategia tiene menos del mínimo para su temporalidad.
        
        Args:
            df: DataFrame con estrategias
            
        Returns:
            DataFrame con componente temporal
        """
        try:
            # Inicializar score temporal
            temporal_scores = np.full(len(df), 0.8)  # Score normal por defecto
            
            # Definir umbrales por temporalidad
            temporalidad_minimos = {
                'M1':  (2, 24),
                'M5':  (2, 24),
                'M15': (2, 24),
                'M30': (2, 24),
                'H1':  (1.5, 18),
                'H4':  (1, 12),
                'D1':  (0.5, 6),
                'W1':  (0.25, 3)
            }
            
            # Buscar columnas relevantes
            tf_col = None
            months_col = None
            trades_col = None
            for col in df.columns:
                if col.strip().lower() in ["timeframe", "temporalidad"]:
                    tf_col = col
                if col.strip().lower() in ["total data months", "total_data_months", "months", "total_months"]:
                    months_col = col
                if col.strip().lower() in ["# of trades", "total_trades", "trades", "#_of_trades"]:
                    trades_col = col
            
            if tf_col and months_col and trades_col:
                timeframes = df[tf_col].astype(str).str.upper().str.strip()
                # Convertir a Series y manejar NaN de forma segura
                total_months = pd.to_numeric(df[months_col], errors='coerce')
                total_months = pd.Series(total_months).replace([np.nan, None], 1.0)
                total_trades = pd.to_numeric(df[trades_col], errors='coerce')
                total_trades = pd.Series(total_trades).replace([np.nan, None], 0.0)
                trades_per_month = total_trades / total_months
                trades_per_year = total_trades / (total_months / 12.0)
                
                for idx, tf in enumerate(timeframes):
                    min_mes, min_ano = temporalidad_minimos.get(tf, (2, 24))  # Default mínimo intradía
                    if trades_per_month.iloc[idx] < min_mes or trades_per_year.iloc[idx] < min_ano:
                        temporal_scores[idx] = 0.2  # Penalización fuerte
            else:
                # Si faltan columnas, score neutral
                temporal_scores[:] = 0.5
            
            df['FK96_Temporal_Component'] = temporal_scores
            return df
        except Exception as e:
            self.logger.warning(f"Error calculando componente temporal: {e}")
            df['FK96_Temporal_Component'] = 0.5
            return df
    
    def _calculate_new_strategy_temporal_score(self, df_new: pd.DataFrame) -> np.ndarray:
        """
        Calcula score temporal específico para estrategias nuevas.
        
        Args:
            df_new: DataFrame con solo estrategias nuevas
            
        Returns:
            Array con scores temporales para estrategias nuevas
        """
        try:
            # Métricas de calidad para estrategias nuevas
            quality_metrics = []
            
            # Sharpe Ratio (indicador de calidad)
            if 'Sharpe_Ratio' in df_new.columns:
                sharpe = pd.to_numeric(df_new['Sharpe_Ratio'], errors='coerce')
                sharpe = pd.Series(sharpe).replace([np.nan, None], 0.0)
                quality_metrics.append((sharpe + 3.0) / 6.0)  # Normalizar a [0,1]
            
            # Profit Factor (eficiencia)
            if 'Profit_factor' in df_new.columns:
                pf = pd.to_numeric(df_new['Profit_factor'], errors='coerce')
                pf = pd.Series(pf).replace([np.nan, None], 1.0)
                quality_metrics.append((pf - 1.0) / 2.0)  # Normalizar a [0,1]
            
            # Max Drawdown (riesgo controlado)
            if 'Max_DD_%' in df_new.columns:
                dd = pd.to_numeric(df_new['Max_DD_%'], errors='coerce')
                dd = pd.Series(dd).replace([np.nan, None], 0.0)
                quality_metrics.append(1.0 - (dd / 100.0))  # Menor DD = mejor
            
            # CAGR (crecimiento)
            if 'CAGR' in df_new.columns:
                cagr = pd.to_numeric(df_new['CAGR'], errors='coerce')
                cagr = pd.Series(cagr).replace([np.nan, None], 0.0)
                quality_metrics.append((cagr + 50.0) / 100.0)  # Normalizar a [0,1]
            
            # Calcular score temporal para estrategias nuevas
            if quality_metrics:
                # Promedio de métricas de calidad
                temporal_score = np.mean(quality_metrics, axis=0)
                
                # Aplicar factor de "novedad" (estrategias nuevas tienen potencial pero incertidumbre)
                novelty_factor = 0.8  # Reducir score por incertidumbre temporal
                temporal_score *= novelty_factor
                
                return temporal_score
            else:
                # Score por defecto para estrategias nuevas
                return np.full(len(df_new), 0.4)  # Score moderado por incertidumbre
                
        except Exception as e:
            self.logger.warning(f"Error calculando score temporal para estrategias nuevas: {e}")
            return np.full(len(df_new), 0.4)
    
    def _calculate_predictive_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula componente predictivo usando ML para predecir éxito futuro.
        
        Args:
            df: DataFrame con estrategias
            
        Returns:
            DataFrame con componente predictivo
        """
        try:
            # Métricas para predicción
            predictive_features = []
            feature_names = []
            
            # Métricas de calidad
            if 'Sharpe_Ratio' in df.columns:
                sharpe = pd.to_numeric(df['Sharpe_Ratio'], errors='coerce')
                sharpe = pd.Series(sharpe).replace([np.nan, None], 0.0)
                predictive_features.append(sharpe)
                feature_names.append('Sharpe_Ratio')
            
            if 'Profit_factor' in df.columns:
                pf = pd.to_numeric(df['Profit_factor'], errors='coerce')
                pf = pd.Series(pf).replace([np.nan, None], 1.0)
                predictive_features.append(pf)
                feature_names.append('Profit_factor')
            
            if 'Max_DD_%' in df.columns:
                dd = pd.to_numeric(df['Max_DD_%'], errors='coerce')
                dd = pd.Series(dd).replace([np.nan, None], 0.0)
                predictive_features.append(-dd)  # Negativo porque menor es mejor
                feature_names.append('Max_DD_%')
            
            if 'CAGR' in df.columns:
                cagr = pd.to_numeric(df['CAGR'], errors='coerce')
                cagr = pd.Series(cagr).replace([np.nan, None], 0.0)
                predictive_features.append(cagr)
                feature_names.append('CAGR')
            
            if len(predictive_features) >= 2:
                # Crear matriz de características
                X = np.column_stack(predictive_features)
                
                # Crear target sintético basado en score actual
                if 'FK96_Elite_Enhanced' in df.columns:
                    target = df['FK96_Elite_Enhanced'].values
                else:
                    # Target basado en combinación de métricas
                    target = np.mean(X, axis=1)
                
                # Entrenar modelo predictivo
                try:
                    if self.ml_scorer is not None:
                        self.ml_scorer.fit(X, target)
                        predictions = self.ml_scorer.predict(X)
                        
                        # Normalizar predicciones
                        min_pred = predictions.min()
                        max_pred = predictions.max()
                        if max_pred > min_pred:
                            df['FK96_Predictive_Component'] = (predictions - min_pred) / (max_pred - min_pred)
                        else:
                            df['FK96_Predictive_Component'] = 0.5
                        
                        self.logger.info(f"Componente predictivo calculado usando {len(feature_names)} características")
                        
                    else:
                        self.logger.warning("ml_scorer no inicializado, asignando valor por defecto")
                        df['FK96_Predictive_Component'] = 0.5
                except Exception as e:
                    self.logger.warning(f"Error entrenando modelo predictivo: {e}")
                    df['FK96_Predictive_Component'] = 0.5
            else:
                df['FK96_Predictive_Component'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error calculando componente predictivo: {e}")
            df['FK96_Predictive_Component'] = 0.5
            return df
    
    def _apply_real_hmm_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica análisis HMM real usando hmmlearn.
        
        Args:
            df: DataFrame con estrategias
            
        Returns:
            DataFrame con análisis HMM
        """
        try:
            if not HMM_AVAILABLE or not hasattr(self, 'hmm_model') or self.hmm_model is None:
                return self._apply_hmm_analysis(df)
            
            # Seleccionar métricas para HMM
            hmm_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR']
            available_metrics = [m for m in hmm_metrics if m in df.columns]
            
            if len(available_metrics) >= 2:
                # Preparar datos
                X = df[available_metrics].fillna(0).values
                
                # Entrenar HMM
                self.hmm_model.fit(X)
                
                # Predecir estados
                states = self.hmm_model.predict(X)
                
                # Calcular scores por estado
                df['HMM_State'] = states
                
                for state in range(self.hmm_model.n_components):
                    state_mask = df['HMM_State'] == state
                    if state_mask.any():
                        state_score = df.loc[state_mask, 'FK96_Elite_Enhanced'].mean()
                        df.loc[state_mask, 'HMM_Score'] = state_score
                
                # Calcular probabilidades de estado
                state_probs = self.hmm_model.predict_proba(X)
                df['HMM_State_Probability'] = np.max(state_probs, axis=1)
                
                self.logger.info(f"HMM real aplicado: {self.hmm_model.n_components} estados detectados")
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando HMM real: {e}")
            return self._apply_hmm_analysis(df)
    
    def _optimize_weights_evolutionary(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Optimiza pesos de componentes usando algoritmo evolutivo.
        
        Args:
            df: DataFrame con estrategias
            
        Returns:
            Diccionario con pesos optimizados
        """
        try:
            # Componentes disponibles
            components = []
            component_names = []
            
            if 'FK96_Stability_Enhanced' in df.columns:
                components.append(df['FK96_Stability_Enhanced'].values)
                component_names.append('Stability')
            
            if 'FK96_Growth_Enhanced' in df.columns:
                components.append(df['FK96_Growth_Enhanced'].values)
                component_names.append('Growth')
            
            if 'FK96_Efficiency_Enhanced' in df.columns:
                components.append(df['FK96_Efficiency_Enhanced'].values)
                component_names.append('Efficiency')
            
            if 'FK96_Consistency_Enhanced' in df.columns:
                components.append(df['FK96_Consistency_Enhanced'].values)
                component_names.append('Consistency')
            
            if 'FK96_Risk_Enhanced' in df.columns:
                components.append(df['FK96_Risk_Enhanced'].values)
                component_names.append('Risk')
            
            if 'FK96_Temporal_Component' in df.columns:
                components.append(df['FK96_Temporal_Component'].values)
                component_names.append('Temporal')
            
            if 'FK96_Predictive_Component' in df.columns:
                components.append(df['FK96_Predictive_Component'].values)
                component_names.append('Predictive')
            
            if len(components) >= 2:
                # Crear matriz de componentes
                X = np.column_stack(components)
                
                # Función objetivo: maximizar varianza explicada
                def objective_function(weights):
                    weights = np.array(weights)
                    weights = weights / np.sum(weights)  # Normalizar
                    combined_score = np.dot(X, weights)
                    return np.var(combined_score)  # Maximizar varianza
                
                # Optimización simple (podría extenderse a algoritmos genéticos)
                from scipy.optimize import minimize
                
                n_components = len(components)
                initial_weights = np.ones(n_components) / n_components
                
                # Restricciones: pesos suman 1
                constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
                
                # Límites: pesos entre 0 y 1
                bounds = [(0, 1)] * n_components
                
                result = minimize(
                    lambda x: -objective_function(x),  # Minimizar negativo = maximizar
                    initial_weights,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints
                )
                
                if result.success:
                    optimized_weights = result.x / np.sum(result.x)
                    self.optimized_weights = dict(zip(component_names, optimized_weights))
                    
                    self.logger.info(f"Pesos optimizados: {self.optimized_weights}")
                    return self.optimized_weights
                else:
                    self.logger.warning("Optimización de pesos falló, usando pesos por defecto")
            
            # Pesos por defecto
            default_weights = {
                'Stability': 0.25,
                'Growth': 0.25,
                'Efficiency': 0.20,
                'Consistency': 0.15,
                'Risk': 0.15
            }
            
            return default_weights
            
        except Exception as e:
            self.logger.warning(f"Error optimizando pesos: {e}")
            return {
                'Stability': 0.25,
                'Growth': 0.25,
                'Efficiency': 0.20,
                'Consistency': 0.15,
                'Risk': 0.15
            }
    
    def evaluate_strategies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recibe un DataFrame ya validado y preparado por DataManager.
        No realizar validación ni carga local aquí.
        """
        self.logger.debug("[INICIO] evaluate_strategies - Entrada recibida (datos validados por DataManager)")
        self.logger.info("Evaluando estrategias (datos ya preparados por DataManager)")
        if self.progress_callback:
            self.progress_callback.update_progress("Evaluación", 0, 100, "Iniciando evaluación...")
        df = self._calculate_factor_k_elite(df)
        if self.progress_callback:
            self.progress_callback.update_progress("Evaluación", 60, 100, "Componentes calculados, aplicando mejoras...")
        if self.scientific_improvements_enabled:
            df = self._apply_scientific_improvements(df)
        if self.progress_callback:
            self.progress_callback.update_progress("Evaluación", 80, 100, "Finalizando evaluación...")
        df = self._apply_final_normalization(df)
        df = self._assign_quality_categories(df)
        if self.progress_callback:
            self.progress_callback.update_progress("Evaluación", 100, 100, "Evaluación completada")
        self.logger.debug("[FIN] evaluate_strategies - Evaluación completada")
        gc.collect()
        return df
    
    def load_and_prepare_data(self, file_path: str) -> pd.DataFrame:
        """
        Carga y prepara datos usando el pipeline centralizado de DataManager.
        Cumple con la arquitectura profesional: toda gestión de datos debe estar centralizada.
        """
        self.logger.debug(f"[FactorKElite96Enhanced] Llamando a DataManager.load_and_prepare_data_pipeline para {file_path}")
        return self.data_manager.load_and_prepare_data_pipeline(file_path)
    
    def _calculate_factor_k_elite(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el Factor K Elite con IA avanzada."""
        try:
            # Calcular componentes principales
            df = self._calculate_stability_component(df)
            df = self._calculate_growth_component(df)
            df = self._calculate_efficiency_component(df)
            df = self._calculate_consistency_component(df)
            df = self._calculate_risk_component(df)
            
            # Calcular componentes de IA avanzada
            df = self._calculate_temporal_component(df)
            df = self._calculate_predictive_component(df)
            
            # Detectar anomalías multivariadas
            df = self._detect_anomalies_multivariate(df)
            
            # Optimizar pesos de componentes
            optimized_weights = self._optimize_weights_evolutionary(df)
            
            # Calcular Factor K Elite con pesos optimizados
            df['FK96_Elite_Enhanced'] = 0.0
            
            # Aplicar pesos optimizados
            if 'FK96_Stability_Enhanced' in df.columns:
                df['FK96_Elite_Enhanced'] += df['FK96_Stability_Enhanced'] * optimized_weights.get('Stability', 0.25)
            
            if 'FK96_Growth_Enhanced' in df.columns:
                df['FK96_Elite_Enhanced'] += df['FK96_Growth_Enhanced'] * optimized_weights.get('Growth', 0.25)
            
            if 'FK96_Efficiency_Enhanced' in df.columns:
                df['FK96_Elite_Enhanced'] += df['FK96_Efficiency_Enhanced'] * optimized_weights.get('Efficiency', 0.20)
            
            if 'FK96_Consistency_Enhanced' in df.columns:
                df['FK96_Elite_Enhanced'] += df['FK96_Consistency_Enhanced'] * optimized_weights.get('Consistency', 0.15)
            
            if 'FK96_Risk_Enhanced' in df.columns:
                df['FK96_Elite_Enhanced'] += df['FK96_Risk_Enhanced'] * optimized_weights.get('Risk', 0.15)
            
            # Añadir componentes de IA si están disponibles
            if 'FK96_Temporal_Component' in df.columns:
                temporal_weight = optimized_weights.get('Temporal', 0.1)
                df['FK96_Elite_Enhanced'] += df['FK96_Temporal_Component'] * temporal_weight
            
            if 'FK96_Predictive_Component' in df.columns:
                predictive_weight = optimized_weights.get('Predictive', 0.1)
                df['FK96_Elite_Enhanced'] += df['FK96_Predictive_Component'] * predictive_weight
            
            # Aplicar penalizaciones dinámicas
            df = self._apply_dynamic_penalties(df)
            
            # Crear versión científica con componentes de IA
            df['FK96_Elite_Enhanced_Scientific'] = df['FK96_Elite_Enhanced'].copy()
            
            # Añadir información de anomalías al score científico
            if 'Is_Anomaly' in df.columns:
                anomaly_penalty = np.where(df['Is_Anomaly'] == 1, 0.3, 0)
                df['FK96_Elite_Enhanced_Scientific'] *= (1 - anomaly_penalty)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando Factor K Elite: {e}")
            raise
    
    def _calculate_stability_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el componente de estabilidad."""
        try:
            # Métricas de estabilidad
            stability_metrics = []
            
            # Max Drawdown (invertido para que menor sea mejor)
            if 'Max_DD_%' in df.columns:
                max_dd = df['Max_DD_%'].fillna(0)
                stability_metrics.append(1 / (1 + abs(max_dd)))
            
            # Sharpe Ratio
            if 'Sharpe_Ratio' in df.columns:
                sharpe = df['Sharpe_Ratio'].fillna(0)
                stability_metrics.append((sharpe + 3) / 6)  # Normalizar a [0,1]
            
            # Calmar Ratio
            if 'CalmarRatio' in df.columns:
                calmar = df['CalmarRatio'].fillna(0)
                stability_metrics.append((calmar + 2) / 4)  # Normalizar a [0,1]
            
            # Ulcer Index
            if 'Ulcer_Index_%' in df.columns:
                ulcer = df['Ulcer_Index_%'].fillna(0)
                stability_metrics.append(1 / (1 + ulcer))
            
            # Calcular componente de estabilidad
            if stability_metrics:
                # Crear DataFrame con las métricas
                metrics_df = pd.concat(stability_metrics, axis=1)
                # Calcular promedio por fila
                df['FK96_Stability_Enhanced'] = metrics_df.mean(axis=1)
                # Asegurar que esté en rango [0, 1]
                df['FK96_Stability_Enhanced'] = df['FK96_Stability_Enhanced'].clip(0, 1)
            else:
                df['FK96_Stability_Enhanced'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando componente de estabilidad: {e}")
            df['FK96_Stability_Enhanced'] = 0.5
            return df
    
    def _calculate_growth_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el componente de crecimiento."""
        try:
            # Métricas de crecimiento
            growth_metrics = []
            
            # CAGR
            if 'CAGR' in df.columns:
                cagr = df['CAGR'].fillna(0)
                growth_metrics.append((cagr + 50) / 100)  # Normalizar a [0,1]
            
            # Net Profit
            if 'Net_profit' in df.columns:
                net_profit = df['Net_profit'].fillna(0)
                growth_metrics.append((net_profit + 10000) / 20000)  # Normalizar a [0,1]
            
            # Recovery Factor
            if 'RecoveryFactor' in df.columns:
                recovery = df['RecoveryFactor'].fillna(0)
                growth_metrics.append((recovery + 5) / 10)  # Normalizar a [0,1]
            
            # Calcular componente de crecimiento
            if growth_metrics:
                # Crear DataFrame con las métricas
                metrics_df = pd.concat(growth_metrics, axis=1)
                # Calcular promedio por fila
                df['FK96_Growth_Enhanced'] = metrics_df.mean(axis=1)
                # Asegurar que esté en rango [0, 1]
                df['FK96_Growth_Enhanced'] = df['FK96_Growth_Enhanced'].clip(0, 1)
            else:
                df['FK96_Growth_Enhanced'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando componente de crecimiento: {e}")
            df['FK96_Growth_Enhanced'] = 0.5
            return df
    
    def _calculate_efficiency_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el componente de eficiencia."""
        try:
            # Métricas de eficiencia
            efficiency_metrics = []
            
            # Profit Factor
            if 'Profit_factor' in df.columns:
                profit_factor = df['Profit_factor'].fillna(1)
                efficiency_metrics.append((profit_factor - 1) / 2)  # Normalizar a [0,1]
            
            # Expectancy
            if 'Expectancy' in df.columns:
                expectancy = df['Expectancy'].fillna(0)
                efficiency_metrics.append((expectancy + 100) / 200)  # Normalizar a [0,1]
            
            # Winning Percent
            if 'Winning_Percent' in df.columns:
                winning_pct = df['Winning_Percent'].fillna(50)
                efficiency_metrics.append(winning_pct / 100)  # Ya está en [0,1]
            
            # Calcular componente de eficiencia
            if efficiency_metrics:
                # Crear DataFrame con las métricas
                metrics_df = pd.concat(efficiency_metrics, axis=1)
                # Calcular promedio por fila
                df['FK96_Efficiency_Enhanced'] = metrics_df.mean(axis=1)
                # Asegurar que esté en rango [0, 1]
                df['FK96_Efficiency_Enhanced'] = df['FK96_Efficiency_Enhanced'].clip(0, 1)
            else:
                df['FK96_Efficiency_Enhanced'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando componente de eficiencia: {e}")
            df['FK96_Efficiency_Enhanced'] = 0.5
            return df
    
    def _calculate_consistency_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el componente de consistencia."""
        try:
            # Métricas de consistencia
            consistency_metrics = []
            
            # Number of Trades
            if '#_of_trades' in df.columns:
                trades = pd.to_numeric(df['#_of_trades'], errors='coerce')
                trades = pd.Series(trades).replace([np.nan, None], 0.0)
                consistency_metrics.append(np.minimum(trades / 100.0, 1.0))  # Normalizar a [0,1]
            
            # Stagnation Trades
            if 'Stagnation' in df.columns:
                stagnation = pd.to_numeric(df['Stagnation'], errors='coerce')
                stagnation = pd.Series(stagnation).replace([np.nan, None], 0.0)
                consistency_metrics.append(1.0 / (1.0 + stagnation))  # Menor es mejor
            
            # Max Consecutive Losses
            if 'Max_Consec_Losses' in df.columns:
                consec_losses = pd.to_numeric(df['Max_Consec_Losses'], errors='coerce')
                consec_losses = pd.Series(consec_losses).replace([np.nan, None], 0.0)
                consistency_metrics.append(1.0 / (1.0 + consec_losses))  # Menor es mejor
            
            # Calcular componente de consistencia
            if consistency_metrics:
                # Crear DataFrame con las métricas
                metrics_df = pd.concat(consistency_metrics, axis=1)
                # Calcular promedio por fila
                df['FK96_Consistency_Enhanced'] = metrics_df.mean(axis=1)
                # Asegurar que esté en rango [0, 1]
                df['FK96_Consistency_Enhanced'] = df['FK96_Consistency_Enhanced'].clip(0, 1)
            else:
                df['FK96_Consistency_Enhanced'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando componente de consistencia: {e}")
            df['FK96_Consistency_Enhanced'] = 0.5
            return df
    
    def _calculate_risk_component(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el componente de riesgo."""
        try:
            # Métricas de riesgo (invertidas para que menor sea mejor)
            risk_metrics = []
            
            # VaR 95%
            if 'VaR_95%' in df.columns:
                var = df['VaR_95%'].fillna(0)
                risk_metrics.append(1 / (1 + abs(var)))
            
            # CVaR 95%
            if 'CVaR_95%' in df.columns:
                cvar = df['CVaR_95%'].fillna(0)
                risk_metrics.append(1 / (1 + abs(cvar)))
            
            # Sortino Ratio
            if 'Sortino_Ratio' in df.columns:
                sortino = df['Sortino_Ratio'].fillna(0)
                risk_metrics.append((sortino + 2) / 4)  # Normalizar a [0,1]
            
            # Calcular componente de riesgo
            if risk_metrics:
                # Crear DataFrame con las métricas
                metrics_df = pd.concat(risk_metrics, axis=1)
                # Calcular promedio por fila
                df['FK96_Risk_Enhanced'] = metrics_df.mean(axis=1)
                # Asegurar que esté en rango [0, 1]
                df['FK96_Risk_Enhanced'] = df['FK96_Risk_Enhanced'].clip(0, 1)
            else:
                df['FK96_Risk_Enhanced'] = 0.5
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculando componente de riesgo: {e}")
            df['FK96_Risk_Enhanced'] = 0.5
            return df
    
    def _apply_dynamic_penalties(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica penalizaciones dinámicas basadas en métricas de calidad."""
        try:
            # Penalización por bajo número de trades
            if 'Total_Trades' in df.columns:
                trades = pd.to_numeric(df['Total_Trades'], errors='coerce')
                trades = pd.Series(trades).replace([np.nan, None], 0.0)
                trade_penalty = np.where(trades < 50.0, 0.1, 0.0)
                df['FK96_Elite_Enhanced'] *= (1.0 - trade_penalty)
            
            # Penalización por alto drawdown
            if 'Max_DD_%' in df.columns:
                max_dd = df['Max_DD_%'].replace([np.nan, None], 0.0)
                dd_penalty = np.where(max_dd > 0.3, 0.15, 0.0)
                df['FK96_Elite_Enhanced'] *= (1.0 - dd_penalty)
            
            # Penalización por bajo Sharpe
            if 'Sharpe_Ratio' in df.columns:
                sharpe = df['Sharpe_Ratio'].replace([np.nan, None], 0.0)
                sharpe_penalty = np.where(sharpe < 0.5, 0.1, 0.0)
                df['FK96_Elite_Enhanced'] *= (1.0 - sharpe_penalty)
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando penalizaciones dinámicas: {e}")
            return df
    
    def _apply_scientific_improvements(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica mejoras científicas con IA avanzada."""
        try:
            if not self.scientific_improvements_enabled:
                return df
            
            # Detectar regímenes de mercado optimizados
            df = self._detect_market_regimes(df)
            
            # Aplicar análisis HMM real
            df = self._apply_real_hmm_analysis(df)
            
            # Aplicar mejora científica al score
            df = self._apply_scientific_score_enhancement(df)
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando mejoras científicas: {e}")
            return df
    
    def _detect_market_regimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta regímenes de mercado usando clustering."""
        try:
            # Seleccionar métricas para clustering
            clustering_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR', 'Profit_factor']
            available_metrics = [m for m in clustering_metrics if m in df.columns]
            
            if len(available_metrics) >= 2:
                # Preparar datos para clustering
                X = df[available_metrics].fillna(0).values
                # Asegurar que X sea un np.ndarray
                if not isinstance(X, np.ndarray):
                    X = np.array(X)
                
                # Aplicar K-means clustering
                optimal_n_clusters, cluster_labels = self._optimize_clustering(X)
                
                # Asignar regímenes
                df['Market_Regime'] = cluster_labels
                
                # Calcular scores por régimen
                for regime in range(optimal_n_clusters):
                    regime_mask = df['Market_Regime'] == regime
                    if regime_mask.any():
                        regime_score = df.loc[regime_mask, 'FK96_Elite_Enhanced'].mean()
                        df.loc[regime_mask, 'Regime_Score'] = regime_score
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error detectando regímenes de mercado: {e}")
            return df
    
    def _apply_hmm_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica análisis HMM si está disponible."""
        try:
            if not self.hmm_analyzer:
                return df
            
            # Seleccionar métricas para HMM
            hmm_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR']
            available_metrics = [m for m in hmm_metrics if m in df.columns]
            
            if len(available_metrics) >= 2:
                # Simular análisis HMM (placeholder)
                np.random.seed(42)
                states = np.random.randint(0, 3, size=len(df))
                
                # Aplicar resultados al DataFrame
                df['HMM_State'] = states
                
                # Calcular scores por estado
                for state in range(3):
                    state_mask = df['HMM_State'] == state
                    if state_mask.any():
                        state_score = df.loc[state_mask, 'FK96_Elite_Enhanced'].mean()
                        df.loc[state_mask, 'HMM_Score'] = state_score
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando análisis HMM: {e}")
            return df
    
    def _apply_scientific_score_enhancement(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica mejora científica al score."""
        try:
            # Verificar columnas disponibles
            has_regime = 'Regime_Score' in df.columns
            has_hmm = 'HMM_Score' in df.columns
            
            # Crear score científico combinando scores
            if has_regime and has_hmm:
                df['FK96_Elite_Enhanced_Scientific'] = (
                    0.5 * df['FK96_Elite_Enhanced'] + 
                    0.3 * df['Regime_Score'] + 
                    0.2 * df['HMM_Score']
                )
            elif has_regime:
                df['FK96_Elite_Enhanced_Scientific'] = (
                    0.7 * df['FK96_Elite_Enhanced'] + 
                    0.3 * df['Regime_Score']
                )
            else:
                df['FK96_Elite_Enhanced_Scientific'] = df['FK96_Elite_Enhanced'].copy()
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando mejora científica: {e}")
            return df
    
    def _apply_final_normalization(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica normalización final al score."""
        try:
            # Normalizar FK96_Elite_Enhanced a [0, 1]
            score_col = 'FK96_Elite_Enhanced'
            if score_col in df.columns:
                score = df[score_col]
                min_score = score.min()
                max_score = score.max()
                
                if max_score > min_score:
                    df['FK96_Elite_Enhanced_Normalized'] = (score - min_score) / (max_score - min_score)
                else:
                    df['FK96_Elite_Enhanced_Normalized'] = 0.5
            
            # Normalizar versión científica si existe
            scientific_col = 'FK96_Elite_Enhanced_Scientific'
            if scientific_col in df.columns:
                score = df[scientific_col]
                min_score = score.min()
                max_score = score.max()
                
                if max_score > min_score:
                    df['FK96_Elite_Enhanced_Scientific_Normalized'] = (score - min_score) / (max_score - min_score)
                else:
                    df['FK96_Elite_Enhanced_Scientific_Normalized'] = 0.5
            
            # Añadir columna 'Unified_Score' como alias de 'FK96_Elite_Enhanced_Normalized' si existe
            if 'FK96_Elite_Enhanced_Normalized' in df.columns:
                df['Unified_Score'] = df['FK96_Elite_Enhanced_Normalized']
            elif 'FK96_Elite_Enhanced' in df.columns:
                df['Unified_Score'] = df['FK96_Elite_Enhanced']
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando normalización final: {e}")
            return df
    
    def _assign_quality_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Asigna categorías de calidad basadas en el score."""
        try:
            score_col = 'FK96_Elite_Enhanced_Normalized'
            if score_col not in df.columns:
                score_col = 'FK96_Elite_Enhanced'
            
            if score_col in df.columns:
                score = df[score_col]
                
                # Definir categorías
                def categorize_score(val):
                    if val >= 0.9:
                        return 'Elite'
                    elif val >= 0.8:
                        return 'Excellent'
                    elif val >= 0.7:
                        return 'Very Good'
                    elif val >= 0.6:
                        return 'Good'
                    elif val >= 0.5:
                        return 'Average'
                    elif val >= 0.4:
                        return 'Below Average'
                    else:
                        return 'Poor'
                
                df['Quality_Category'] = score.apply(categorize_score)
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error asignando categorías de calidad: {e}")
            return df
    
    def get_analysis_summary(self, df: pd.DataFrame) -> Dict:
        """Obtiene resumen del análisis."""
        try:
            summary = {
                'total_strategies': len(df),
                'analysis_timestamp': pd.Timestamp.now().isoformat(),
                'scores_calculated': []
            }
            
            # Verificar scores calculados
            score_columns = [
                'FK96_Elite_Enhanced',
                'FK96_Elite_Enhanced_Normalized',
                'FK96_Elite_Enhanced_Scientific',
                'FK96_Elite_Enhanced_Scientific_Normalized'
            ]
            
            for col in score_columns:
                if col in df.columns:
                    summary['scores_calculated'].append(col)
                    summary[f'{col}_mean'] = df[col].mean()
                    summary[f'{col}_std'] = df[col].std()
                    summary[f'{col}_min'] = df[col].min()
                    summary[f'{col}_max'] = df[col].max()
            
            # Categorías de calidad
            if 'Quality_Category' in df.columns:
                category_counts = df['Quality_Category'].value_counts().to_dict()
                summary['quality_categories'] = category_counts
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generando resumen: {e}")
            return {'error': str(e)} 