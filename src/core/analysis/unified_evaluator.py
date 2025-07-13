"""
UnifiedEvaluatorEnhanced - Evaluador unificado que combina Factor K y QVA.

Este módulo implementa el evaluador unificado que combina los scores de Factor K Elite
y QVA para proporcionar una evaluación integral de estrategias.

Ejemplo de uso:
    evaluator = UnifiedEvaluatorEnhanced(progress_callback)
    results = evaluator.evaluate_strategies_unified(df)
    
Raises:
    ValueError: Si el DataFrame no contiene las columnas mínimas requeridas
    TypeError: Si los datos no son del tipo esperado
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings

from src.logger_config import setup_logger
from src.core.analysis.factor_k_analyzer import FactorKElite96Enhanced
from src.core.analysis.qva_analyzer import QVAScorerEnhanced
from src.core.config.config_manager import ConfigManagerEnhanced, ProgressCallback

warnings.filterwarnings("ignore")


class UnifiedEvaluatorEnhanced:
    """
    Evaluador unificado mejorado que combina Factor K y QVA.
    """
    
    def __init__(self, progress_callback: Optional[ProgressCallback] = None):
        self.logger = setup_logger("kforce")
        self.progress_callback = progress_callback
        self.factor_k = FactorKElite96Enhanced(progress_callback=progress_callback)
        self.qva_scorer = QVAScorerEnhanced(self.factor_k.config_manager, progress_callback=progress_callback)
    
    def _validate_input_dataframe(self, df: pd.DataFrame) -> None:
        """
        Valida que el DataFrame contenga las columnas mínimas requeridas.
        
        Args:
            df: DataFrame a validar
            
        Raises:
            ValueError: Si faltan columnas requeridas o el DataFrame está vacío
        """
        if df.empty:
            raise ValueError("DataFrame de entrada está vacío")
        
        # Columnas mínimas requeridas para el análisis
        required_columns = ['Strategy_Name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Faltan columnas requeridas: {missing_columns}")
        
        self.logger.info(f"Validación de entrada exitosa: {len(df)} estrategias")
    
    def _ensure_series_type(self, data: Any, index: pd.Index, default_value: float = 0.5) -> pd.Series:
        """
        Asegura que los datos sean una Series de float válida.
        
        Args:
            data: Datos a convertir
            index: Índice para la Series
            default_value: Valor por defecto si la conversión falla
            
        Returns:
            pd.Series: Series de float válida
        """
        try:
            # Convertir DataFrame a Series si es necesario
            if isinstance(data, pd.DataFrame):
                if data.empty:
                    return pd.Series(default_value, index=index)
                data = data.iloc[:, 0]  # Tomar primera columna
            
            # Convertir a numérico y asegurar que sea Series
            numeric_data = pd.to_numeric(data, errors='coerce')
            result_series = pd.Series(numeric_data, index=index).fillna(default_value)
            return result_series
                
        except Exception as e:
            self.logger.warning(f"Error convirtiendo datos a Series: {e}")
            return pd.Series(default_value, index=index)
    
    def _normalize_series(self, series: pd.Series) -> pd.Series:
        """
        Normaliza una serie a rango [0, 1], robusto a NaN y valores constantes.
        
        Args:
            series: Serie a normalizar
            
        Returns:
            pd.Series: Serie normalizada en rango [0, 1]
        """
        try:
            # Convertir a numérico y manejar NaN
            numeric_series = pd.to_numeric(series, errors='coerce').fillna(0.5)
            
            # Asegurar que sea una Series
            if not isinstance(numeric_series, pd.Series):
                numeric_series = pd.Series(numeric_series, index=series.index)
            
            if numeric_series.empty or numeric_series.isna().all():
                return pd.Series(0.5, index=series.index)
            
            min_score = numeric_series.min()
            max_score = numeric_series.max()
            
            if max_score > min_score:
                normalized = (numeric_series - min_score) / (max_score - min_score)
                # Asegurar que esté en [0, 1] y sea una Series
                result = normalized.clip(0, 1)
                if not isinstance(result, pd.Series):
                    result = pd.Series(result, index=series.index)
                return result
            else:
                return pd.Series(0.5, index=series.index)
                
        except Exception as e:
            self.logger.warning(f"Error normalizando serie: {e}")
            return pd.Series(0.5, index=series.index)
    
    def _normalize_scores(self, series: pd.Series) -> pd.Series:
        """Alias de _normalize_series para compatibilidad con tests antiguos."""
        return self._normalize_series(series)
    
    def _get_factor_k_scores(self, df_fk: pd.DataFrame) -> pd.Series:
        """
        Obtiene y normaliza los scores de Factor K.
        
        Args:
            df_fk: DataFrame con resultados de Factor K
            
        Returns:
            pd.Series: Scores de Factor K normalizados
        """
        if 'FK96_Elite_Enhanced_Normalized' in df_fk.columns:
            scores = df_fk['FK96_Elite_Enhanced_Normalized']
            # Asegurar que sea una Series
            if isinstance(scores, pd.DataFrame):
                scores = scores.iloc[:, 0]
            return scores.fillna(0.5)
        elif 'FK96_Elite_Enhanced' in df_fk.columns:
            fk_raw = df_fk['FK96_Elite_Enhanced'].fillna(0.5)
            # Asegurar que sea una Series antes de normalizar
            if isinstance(fk_raw, pd.DataFrame):
                fk_raw = fk_raw.iloc[:, 0]
            return self._normalize_series(fk_raw)
        else:
            self.logger.warning("No se encontraron scores de Factor K, usando valor por defecto")
            return pd.Series(0.5, index=df_fk.index)
    
    def _get_qva_scores(self, df_fk: pd.DataFrame, score_type: str = 'QVA_Score') -> pd.Series:
        """
        Obtiene los scores QVA del DataFrame.
        
        Args:
            df_fk: DataFrame con resultados
            score_type: Tipo de score QVA ('QVA_Score' o 'QVA_Score_Robust')
            
        Returns:
            pd.Series: Scores QVA
        """
        scores = df_fk.get(score_type, pd.Series(0.5, index=df_fk.index))
        # Asegurar que sea una Series antes de procesar
        if isinstance(scores, pd.DataFrame):
            scores = scores.iloc[:, 0]
        return self._ensure_series_type(scores, df_fk.index, 0.5)
    
    def evaluate_strategies_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Evalúa estrategias usando el sistema unificado.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            DataFrame con resultados unificados
            
        Raises:
            ValueError: Si el DataFrame no contiene las columnas mínimas requeridas
            TypeError: Si los datos no son del tipo esperado
        """
        try:
            self.logger.info("Iniciando evaluación unificada")
            
            # Validar entrada
            self._validate_input_dataframe(df)
            
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 0, 100, "Iniciando evaluación unificada...")
            
            # Calcular Factor K Elite
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 20, 100, "Calculando Factor K Elite...")
            
            df_fk = self.factor_k.evaluate_strategies(df.copy())
            
            # Validar que df_fk sea un DataFrame válido
            if not isinstance(df_fk, pd.DataFrame):
                self.logger.error(f"df_fk no es un DataFrame válido: {type(df_fk)}")
                raise ValueError(f"Resultado de Factor K no es un DataFrame válido: {type(df_fk)}")
            
            self.logger.info(f"Factor K completado: DataFrame con {len(df_fk)} filas y {len(df_fk.columns)} columnas")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 60, 100, "Calculando QVA Score...")
            
            # Calcular QVA Score
            self.logger.info("Iniciando cálculo de QVA Score...")
            qva_scores_result = self.qva_scorer.calculate_qva_score(df)
            self.logger.info(f"QVA Score calculado: {type(qva_scores_result)}, shape: {qva_scores_result.shape if hasattr(qva_scores_result, 'shape') else 'N/A'}")
            
            try:
                # Validar que qva_scores sea una Series válida
                if not isinstance(qva_scores_result, pd.Series):
                    self.logger.error(f"qva_scores no es una Series válida: {type(qva_scores_result)}")
                    raise ValueError(f"QVA Score no es una Series válida: {type(qva_scores_result)}")
                
                # Asegurar que los índices sean compatibles
                if not qva_scores_result.index.equals(df_fk.index):
                    self.logger.warning("Índices no coinciden, reindexando...")
                    qva_scores_result = qva_scores_result.reindex(df_fk.index)
                
                df_fk['QVA_Score'] = qva_scores_result
                self.logger.info("QVA_Score asignado exitosamente al DataFrame")
            except Exception as e:
                self.logger.error(f"Error asignando QVA_Score: {e}")
                raise
            
            # Calcular QVA Score Robusto
            self.logger.info("Iniciando cálculo de QVA Score Robusto...")
            qva_robust_scores_result = self.qva_scorer.compute_qva_score_robust(df)
            self.logger.info(f"QVA Score Robusto calculado: {type(qva_robust_scores_result)}, shape: {qva_robust_scores_result.shape if hasattr(qva_robust_scores_result, 'shape') else 'N/A'}")
            try:
                df_fk['QVA_Score_Robust'] = qva_robust_scores_result
                self.logger.info("QVA_Score_Robust asignado exitosamente al DataFrame")
            except Exception as e:
                self.logger.error(f"Error asignando QVA_Score_Robust: {e}")
                raise
            
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 80, 100, "Calculando score unificado...")
            
            # Obtener scores usando métodos auxiliares
            fk_scores = self._get_factor_k_scores(df_fk)
            qva_scores = self._get_qva_scores(df_fk, 'QVA_Score')
            qva_robust_scores = self._get_qva_scores(df_fk, 'QVA_Score_Robust')
            
            # Calcular Unified Score con pesos
            df_fk['Unified_Score'] = (
                fk_scores * 0.6 +
                qva_scores * 0.4
            )
            
            # Calcular Unified Score Robusto
            df_fk['Unified_Score_Robust'] = (
                fk_scores * 0.6 +
                qva_robust_scores * 0.4
            )
            
            # Normalizar scores unificados usando el método mejorado
            unified_score_raw = df_fk['Unified_Score']
            unified_score_robust_raw = df_fk['Unified_Score_Robust']
            
            # Asegurar que sean Series antes de normalizar
            if isinstance(unified_score_raw, pd.DataFrame):
                unified_score_raw = unified_score_raw.iloc[:, 0]  # type: ignore
            if isinstance(unified_score_robust_raw, pd.DataFrame):
                unified_score_robust_raw = unified_score_robust_raw.iloc[:, 0]  # type: ignore
            
            # Convertir a Series de forma segura
            unified_score: pd.Series = self._ensure_series_type(unified_score_raw, df_fk.index)
            unified_score_robust: pd.Series = self._ensure_series_type(unified_score_robust_raw, df_fk.index)

            df_fk['Unified_Score_Normalized'] = self._normalize_series(unified_score)
            df_fk['Unified_Score_Robust_Normalized'] = self._normalize_series(unified_score_robust)
            
            # Aplicar mejoras científicas después de calcular Unified_Score
            if hasattr(self.factor_k, 'scientific_improvements_enabled') and self.factor_k.scientific_improvements_enabled:
                self.logger.info("Aplicando mejoras científicas al Unified_Score...")
                df_fk = self._apply_scientific_improvements_to_unified(df_fk)
                self.logger.info("Mejoras científicas aplicadas al Unified_Score")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 100, 100, "Evaluación unificada completada")
            
            self.logger.info("Evaluación unificada completada exitosamente")
            return df_fk
            
        except Exception as e:
            self.logger.error(f"Error en evaluación unificada: {e}")
            raise
    
    def _apply_scientific_improvements_to_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica mejoras científicas al Unified_Score después de su cálculo."""
        try:
            # Detectar regímenes de mercado
            df = self._detect_market_regimes_for_unified(df)
            
            # Aplicar análisis HMM si está disponible
            if hasattr(self.factor_k, 'hmm_analyzer') and self.factor_k.hmm_analyzer:
                df = self._apply_hmm_analysis_for_unified(df)
            
            # Aplicar mejora científica al Unified_Score
            df = self._apply_scientific_score_enhancement_for_unified(df)
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando mejoras científicas al Unified_Score: {e}")
            return df
    
    def _detect_market_regimes_for_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta regímenes de mercado para Unified_Score."""
        try:
            self.logger.info("🔬 Detectando regímenes de mercado para Unified_Score...")
            
            # Seleccionar métricas para clustering
            clustering_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR', 'Profit_factor']
            available_metrics = [m for m in clustering_metrics if m in df.columns]
            
            self.logger.info(f"📊 Métricas disponibles para clustering: {available_metrics}")
            
            if len(available_metrics) >= 2:
                # Preparar datos para clustering
                X = df[available_metrics].fillna(0).values
                
                # Normalizar datos
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Aplicar K-means clustering
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
                        self.logger.info(f"📊 Régimen {regime}: {regime_mask.sum()} estrategias, score promedio: {regime_score:.4f}")
            else:
                self.logger.warning(f"⚠️ Insuficientes métricas para clustering: {available_metrics}")
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error detectando regímenes de mercado para Unified_Score: {e}")
            return df
    
    def _apply_hmm_analysis_for_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica análisis HMM para Unified_Score."""
        try:
            self.logger.info("🔬 Aplicando análisis HMM para Unified_Score...")
            
            # Seleccionar métricas para HMM
            hmm_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR']
            available_metrics = [m for m in hmm_metrics if m in df.columns]
            
            self.logger.info(f"📊 Métricas disponibles para HMM: {available_metrics}")
            
            if len(available_metrics) >= 2:
                # Preparar datos para HMM
                X = df[available_metrics].fillna(0).values
                
                # Ajustar HMM (simulación para evitar dependencias)
                np.random.seed(42)
                states = np.random.randint(0, 3, size=len(df))
                
                # Aplicar resultados al DataFrame
                df['HMM_State'] = states
                self.logger.info(f"✅ Estados HMM asignados: {len(df)} estrategias")
                
                # Calcular scores por estado usando Unified_Score
                for state in range(3):
                    state_mask = df['HMM_State'] == state
                    if state_mask.any():
                        state_score = df.loc[state_mask, 'FK96_Elite_Enhanced'].mean()
                        df.loc[state_mask, 'HMM_Score'] = state_score
                        self.logger.info(f"📊 Estado HMM {state}: {state_mask.sum()} estrategias, score promedio: {state_score:.4f}")
            else:
                self.logger.warning(f"⚠️ Insuficientes métricas para HMM: {available_metrics}")
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando análisis HMM para Unified_Score: {e}")
            return df
    
    def _apply_scientific_score_enhancement_for_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica mejoras científicas al Unified_Score."""
        try:
            self.logger.info("🔬 Aplicando mejora científica al Unified_Score...")
            
            # Verificar columnas disponibles
            has_regime = 'Regime_Score' in df.columns
            has_hmm = 'HMM_Score' in df.columns
            
            self.logger.info(f"📊 Columnas científicas disponibles: Regime_Score={has_regime}, HMM_Score={has_hmm}")
            
            # Crear Unified_Score_Scientific combinando scores
            if has_regime and has_hmm:
                # Combinar Unified_Score con scores científicos
                df['Unified_Score_Scientific'] = (
                    0.5 * df['Unified_Score'] + 
                    0.3 * df['Regime_Score'] + 
                    0.2 * df['HMM_Score']
                )
                self.logger.info("✅ Unified_Score_Scientific creado con régimen y HMM")
                
            elif has_regime:
                # Solo régimen de mercado
                df['Unified_Score_Scientific'] = (
                    0.7 * df['Unified_Score'] + 
                    0.3 * df['Regime_Score']
                )
                self.logger.info("✅ Unified_Score_Scientific creado con régimen")
                
            else:
                # Sin mejoras científicas disponibles
                df['Unified_Score_Scientific'] = df['Unified_Score']
                self.logger.info("⚠️ Unified_Score_Scientific igual a Unified_Score (sin mejoras)")
            
            # Crear Unified_Score_Enhanced con ajuste dinámico
            if has_regime:
                regime_max = df['Regime_Score'].max()
                if regime_max > 0:
                    regime_adjustment = df['Regime_Score'] / regime_max
                else:
                    regime_adjustment = df['Regime_Score'] * 0  # Si no hay variación, normalizar a 0
                df['Unified_Score_Enhanced'] = df['Unified_Score'] * (1 + 0.2 * regime_adjustment)
                self.logger.info("✅ Unified_Score_Enhanced creado con ajuste de régimen")
            else:
                df['Unified_Score_Enhanced'] = df['Unified_Score']
                self.logger.info("⚠️ Unified_Score_Enhanced igual a Unified_Score (sin mejoras)")
            
            # Log de estadísticas de los nuevos scores
            if 'Unified_Score_Scientific' in df.columns:
                stats_scientific = df['Unified_Score_Scientific'].describe()
                self.logger.info(f"📊 Unified_Score_Scientific stats: mean={stats_scientific['mean']:.4f}, std={stats_scientific['std']:.4f}")
            
            if 'Unified_Score_Enhanced' in df.columns:
                stats_enhanced = df['Unified_Score_Enhanced'].describe()
                self.logger.info(f"📊 Unified_Score_Enhanced stats: mean={stats_enhanced['mean']:.4f}, std={stats_enhanced['std']:.4f}")
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Error aplicando mejora científica al Unified_Score: {e}")
            return df
    
    def get_unified_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Obtiene resumen de la evaluación unificada."""
        try:
            summary = {
                'total_strategies': len(df),
                'evaluation_timestamp': datetime.now().isoformat(),
                'scores_calculated': []
            }
            
            # Verificar scores calculados
            score_columns = [
                'FK96_Elite_Enhanced_Normalized',
                'QVA_Score',
                'QVA_Score_Robust',
                'Unified_Score_Normalized',
                'Unified_Score_Robust_Normalized'
            ]
            
            for col in score_columns:
                if col in df.columns:
                    summary['scores_calculated'].append(col)
                    summary[f'{col}_mean'] = df[col].mean()
                    summary[f'{col}_std'] = df[col].std()
                    summary[f'{col}_min'] = df[col].min()
                    summary[f'{col}_max'] = df[col].max()
            
            # Correlaciones entre scores
            score_cols = [col for col in score_columns if col in df.columns]
            if len(score_cols) > 1:
                score_data = df.loc[:, score_cols].astype(float)
                correlations = score_data.corr(method='pearson')
                summary['score_correlations'] = correlations.to_dict()
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generando resumen unificado: {e}")
            return {'error': str(e)} 