import pandas as pd
import numpy as np
import gc
from pathlib import Path
from typing import Optional, Dict
from src.core.config.config_manager import ConfigManagerEnhanced
from src.core.config.progress_callback import ProgressCallback
from src.data.data_manager import DataManager
from src.logger_config import setup_logger
# Importar analizadores científicos si están disponibles
try:
    from src.core.market_regime_analyzer import HiddenMarkovModelAnalyzer
    from src.core.robustness_analyzer import StressTestGenerator
    from src.core.integration_layer import DataDriftDetector, TemporalValidation
except ImportError:
    HiddenMarkovModelAnalyzer = None
    StressTestGenerator = None
    DataDriftDetector = None
    TemporalValidation = None

CHUNK_SIZE = 10000
MAX_WORKERS = 4

class FactorKElite96Enhanced:
    """
    Motor principal mejorado con procesamiento en hilos y optimizaciones para GUI.
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
        
        # Cache para optimización
        self._calculation_cache = {}
        
        if config:
            self.config_manager.current_config.update(config)
        
        # SIEMPRE ACTIVAR MEJORAS CIENTÍFICAS POR DEFECTO
        self.enable_scientific_improvements()
    
    def enable_scientific_improvements(self, cache_dir: str = "cache/scientific"):
        """
        Habilita las mejoras científicas opcionales.
        """
        try:
            self.scientific_improvements_enabled = True
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            if HiddenMarkovModelAnalyzer:
                self.hmm_analyzer = HiddenMarkovModelAnalyzer()
            if StressTestGenerator:
                self.stress_tester = StressTestGenerator()
            if DataDriftDetector:
                self.drift_detector = DataDriftDetector()
            if TemporalValidation:
                self.temporal_validator = TemporalValidation()
            self.logger.info("Mejoras científicas habilitadas")
        except Exception as e:
            self.logger.error(f"Error habilitando mejoras científicas: {e}")
            self.scientific_improvements_enabled = False
    
    def load_and_prepare_data(self, file_path: str) -> pd.DataFrame:
        """
        Carga y prepara datos usando el cargador mejorado.
        """
        try:
            return self.data_manager.load_and_prepare_data_pipeline(file_path)
        except Exception as e:
            self.logger.error(f"Error en load_and_prepare_data: {e}")
            raise
    
    def evaluate_strategies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Evalúa estrategias con procesamiento optimizado y callbacks de progreso.
        """
        try:
            self.logger.info("Iniciando evaluación de estrategias")
            if self.progress_callback:
                self.progress_callback.update_progress("Evaluación", 0, 100, "Iniciando evaluación...")
            df = self._validate_input_data(df)
            if self.progress_callback:
                self.progress_callback.update_progress("Evaluación", 10, 100, "Datos validados, calculando componentes...")
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
            gc.collect()
            return df
        except Exception as e:
            self.logger.error(f"Error en evaluate_strategies: {str(e)}")
            if self.progress_callback:
                self.progress_callback.update_progress("Evaluación", 0, 100, f"Error: {str(e)}")
            raise ValueError(f"Error en el análisis: {str(e)}")
    
    def _validate_input_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valida los datos de entrada con validaciones mejoradas."""
        try:
            if df is None or df.empty:
                raise ValueError("DataFrame vacío o None")
            
            # Verificar columnas mínimas requeridas
            required_columns = ['Strategy_Name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas requeridas faltantes: {missing_columns}")
            
            # Verificar que hay suficientes datos
            if len(df) < 5:
                raise ValueError("Insuficientes datos para análisis (mínimo 5 estrategias)")
            
            # Verificar que hay columnas numéricas
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) < 3:
                raise ValueError("Insuficientes columnas numéricas para análisis")
            
            # Limpiar datos extremos
            df = self._clean_extreme_values(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error validando datos de entrada: {e}")
            raise
    
    def _clean_extreme_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia valores extremos en columnas numéricas."""
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_columns:
                if col in df.columns:
                    # Calcular percentiles para detectar outliers
                    q1 = float(df[col].quantile(0.01))
                    q3 = float(df[col].quantile(0.99))
                    iqr = q3 - q1
                    
                    # Definir límites
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    # Reemplazar outliers con límites
                    df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error limpiando valores extremos: {e}")
            return df
    
    def _calculate_factor_k_elite(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula el Factor K Elite con procesamiento optimizado."""
        try:
            # Calcular componentes principales
            df = self._calculate_stability_component(df)
            df = self._calculate_growth_component(df)
            df = self._calculate_efficiency_component(df)
            df = self._calculate_consistency_component(df)
            df = self._calculate_risk_component(df)
            
            # Calcular Factor K Elite
            df['FK96_Elite_Enhanced'] = (
                df['FK96_Stability_Enhanced'] * 0.25 +
                df['FK96_Growth_Enhanced'] * 0.25 +
                df['FK96_Efficiency_Enhanced'] * 0.20 +
                df['FK96_Consistency_Enhanced'] * 0.15 +
                df['FK96_Risk_Enhanced'] * 0.15
            )
            
            # Aplicar penalizaciones dinámicas
            df = self._apply_dynamic_penalties(df)
            
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
                trades = pd.to_numeric(df['#_of_trades'], errors='coerce').fillna(0)
                consistency_metrics.append(np.minimum(trades / 100, 1))  # Normalizar a [0,1]
            
            # Stagnation Trades
            if 'Stagnation' in df.columns:
                stagnation = pd.to_numeric(df['Stagnation'], errors='coerce').fillna(0)
                consistency_metrics.append(1 / (1 + stagnation))  # Menor es mejor
            
            # Max Consecutive Losses
            if 'Max_Consec_Losses' in df.columns:
                consec_losses = pd.to_numeric(df['Max_Consec_Losses'], errors='coerce').fillna(0)
                consistency_metrics.append(1 / (1 + consec_losses))  # Menor es mejor
            
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
                trades = pd.to_numeric(df['Total_Trades'], errors='coerce').fillna(0)
                trade_penalty = np.where(trades < 50, 0.1, 0)
                df['FK96_Elite_Enhanced'] *= (1 - trade_penalty)
            
            # Penalización por alto drawdown
            if 'Max_DD_%' in df.columns:
                max_dd = df['Max_DD_%'].fillna(0)
                dd_penalty = np.where(max_dd > 0.3, 0.15, 0)
                df['FK96_Elite_Enhanced'] *= (1 - dd_penalty)
            
            # Penalización por bajo Sharpe
            if 'Sharpe_Ratio' in df.columns:
                sharpe = df['Sharpe_Ratio'].fillna(0)
                sharpe_penalty = np.where(sharpe < 0.5, 0.1, 0)
                df['FK96_Elite_Enhanced'] *= (1 - sharpe_penalty)
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando penalizaciones dinámicas: {e}")
            return df
    
    def _apply_scientific_improvements(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica mejoras científicas si están habilitadas."""
        try:
            if not self.scientific_improvements_enabled:
                return df
            
            # Detectar regímenes de mercado
            df = self._detect_market_regimes(df)
            
            # Aplicar análisis HMM si está disponible
            if self.hmm_analyzer:
                df = self._apply_hmm_analysis(df)
            
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
                
                # Aplicar K-means clustering
                from sklearn.cluster import KMeans
                from sklearn.preprocessing import StandardScaler
                
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
                cluster_labels = kmeans.fit_predict(X_scaled)
                
                # Asignar regímenes
                df['Market_Regime'] = cluster_labels
                
                # Calcular scores por régimen
                for regime in range(3):
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
                df['FK96_Elite_Enhanced_Scientific'] = df['FK96_Elite_Enhanced']
            
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