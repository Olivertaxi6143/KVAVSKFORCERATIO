"""
UnifiedEvaluatorEnhanced - Evaluador unificado que combina Factor K y QVA.

ADVERTENCIA PROFESIONAL:
------------------------------------------------------------
Toda carga, validación y manipulación de archivos de estrategias (.sqx, .csv, .xlsx, etc.)
debe hacerse exclusivamente usando los módulos y utilidades de la carpeta data
(DataManager, data_utils, data_processing, etc.).
NO duplicar lógica de validación ni manipulación de datos aquí.
Este módulo solo debe recibir DataFrames ya validados y preparados desde data_manager
u otras funciones centralizadas.
------------------------------------------------------------

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
from src.analysis.tail_risk_metrics import TailRiskAnalyzer

warnings.filterwarnings("ignore")


class UnifiedEvaluatorEnhanced:
    """
    Evaluador unificado mejorado que combina Factor K, QVA y Tail Risk Metrics.

    ADVERTENCIA PROFESIONAL:
    ------------------------------------------------------------
    Este módulo SOLO debe recibir DataFrames ya validados y preparados por DataManager
    u otras funciones centralizadas de la capa data. No realizar validación, carga ni
    manipulación local de datos aquí. Toda gestión de datos debe estar centralizada.
    ------------------------------------------------------------
    """
    
    def __init__(self, progress_callback: Optional[ProgressCallback] = None):
        self.logger = setup_logger("kforce")
        self.progress_callback = progress_callback
        self.factor_k = FactorKElite96Enhanced(progress_callback=progress_callback)
        self.qva_scorer = QVAScorerEnhanced(self.factor_k.config_manager, progress_callback=progress_callback)
        self.tail_risk_analyzer = TailRiskAnalyzer()
    
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
    
    def _apply_tail_risk_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica análisis de tail risk metrics al DataFrame.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            pd.DataFrame: DataFrame con métricas de tail risk añadidas
        """
        try:
            self.logger.info("🔬 Aplicando análisis de Tail Risk Metrics...")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Tail Risk", 0, 100, "Iniciando análisis de tail risk...")
            
            # Verificar si hay datos de retornos disponibles
            required_columns = ['Strategy_Name']
            if not all(col in df.columns for col in required_columns):
                self.logger.warning("Columnas requeridas no disponibles para tail risk analysis")
                return df
            
            # Intentar encontrar columnas de retornos o métricas de riesgo
            risk_columns = [col for col in df.columns if any(keyword in col.lower() 
                           for keyword in ['return', 'profit', 'loss', 'drawdown', 'sharpe', 'var'])]
            
            if not risk_columns:
                self.logger.warning("No se encontraron columnas de riesgo para tail risk analysis")
                return df
            
            self.logger.info(f"Columnas de riesgo encontradas: {risk_columns}")
            
            # Aplicar análisis de tail risk
            tail_risk_results = self.tail_risk_analyzer.analyze_strategies(df)
            
            if isinstance(tail_risk_results, dict):
                # Si el resultado es un diccionario, extraer métricas principales
                for strategy_name, metrics in tail_risk_results.items():
                    if strategy_name in df.index or strategy_name in df['Strategy_Name'].values:
                        # Encontrar el índice correspondiente
                        if strategy_name in df.index:
                            idx = strategy_name
                        else:
                            idx = df[df['Strategy_Name'] == strategy_name].index[0]
                        
                        # Añadir métricas principales al DataFrame
                        for metric_name, value in metrics.items():
                            if isinstance(value, (int, float)) and not pd.isna(value):
                                col_name = f"TailRisk_{metric_name}"
                                df.loc[idx, col_name] = value
                
                self.logger.info("✅ Métricas de tail risk añadidas al DataFrame")
            else:
                self.logger.warning("Resultado de tail risk analysis no es un diccionario válido")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Tail Risk", 100, 100, "Análisis de tail risk completado")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error aplicando análisis de tail risk: {e}")
            return df
    
    def evaluate_strategies_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recibe un DataFrame ya validado y preparado por DataManager.
        No realizar validación ni carga local aquí.
        """
        self.logger.debug("[INICIO] evaluate_strategies_unified - Entrada recibida (datos validados por DataManager)")
        try:
            self.logger.info("Iniciando evaluación unificada (datos ya preparados por DataManager)")
            
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 0, 100, "Iniciando evaluación unificada...")
            
            # Calcular Factor K Elite
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 15, 100, "Calculando Factor K Elite...")
            
            df_fk = self.factor_k.evaluate_strategies(df.copy())
            
            # Validar que df_fk sea un DataFrame válido
            if not isinstance(df_fk, pd.DataFrame):
                self.logger.error(f"df_fk no es un DataFrame válido: {type(df_fk)}")
                raise ValueError(f"Resultado de Factor K no es un DataFrame válido: {type(df_fk)}")
            
            self.logger.info(f"Factor K completado: DataFrame con {len(df_fk)} filas y {len(df_fk.columns)} columnas")
            
            # Aplicar análisis de Tail Risk Metrics
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 30, 100, "Aplicando análisis de Tail Risk...")
            
            df_fk = self._apply_tail_risk_analysis(df_fk)
            
            # Calcular QVA Score
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 45, 100, "Calculando QVA Score...")
            
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
            if self.progress_callback:
                self.progress_callback.update_progress("Unificado", 60, 100, "Calculando QVA Score Robusto...")
            
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
                self.progress_callback.update_progress("Unificado", 75, 100, "Calculando score unificado...")
            
            # Obtener scores usando métodos auxiliares
            fk_scores = self._get_factor_k_scores(df_fk)
            qva_scores = self._get_qva_scores(df_fk, 'QVA_Score')
            qva_robust_scores = self._get_qva_scores(df_fk, 'QVA_Score_Robust')

            # Pesos de combinación (por defecto, no expuestos al usuario)
            weight_fk = 0.6
            weight_qva = 0.4

            # Calcular Unified Score con pesos
            df_fk['Unified_Score'] = (
                fk_scores * weight_fk +
                qva_scores * weight_qva
            )
            
            # Calcular Unified Score Robusto
            df_fk['Unified_Score_Robust'] = (
                fk_scores * weight_fk +
                qva_robust_scores * weight_qva
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
            self.logger.debug("[FIN] evaluate_strategies_unified - Evaluación completada")
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
        """Detecta regímenes de mercado para Unified_Score (n_clusters parametrizable)."""
        try:
            self.logger.info("🔬 Detectando regímenes de mercado para Unified_Score...")
            # Parametrización interna (fácil de cambiar):
            n_clusters = 3  # Cambiar aquí si se desea otro número de clusters
            # Seleccionar métricas para clustering
            clustering_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR', 'Profit_factor']
            available_metrics = [m for m in clustering_metrics if m in df.columns]
            self.logger.info(f"📊 Métricas disponibles para clustering: {available_metrics}")
            if len(available_metrics) >= 2:
                X = df[available_metrics].fillna(0).values
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
                cluster_labels = kmeans.fit_predict(X_scaled)
                df['Market_Regime'] = cluster_labels
                # Logging detallado de clusters
                for regime in range(n_clusters):
                    regime_mask = df['Market_Regime'] == regime
                    # Refuerzo: aseguro que regime_mask es un array booleano y nunca se usa como condicional directo
                    if hasattr(regime_mask, 'any') and callable(regime_mask.any):
                        if regime_mask.any():
                            regime_score = df.loc[regime_mask, 'FK96_Elite_Enhanced'].mean()
                            size = int(regime_mask.sum())
                            sharpe_mean = df.loc[regime_mask, 'Sharpe_Ratio'].mean() if 'Sharpe_Ratio' in df.columns else None
                            self.logger.info(f"📊 Régimen {regime}: {size} estrategias, score promedio: {regime_score:.4f}, Sharpe medio: {sharpe_mean}")
                            df.loc[regime_mask, 'Regime_Score'] = regime_score
            else:
                self.logger.warning(f"⚠️ Insuficientes métricas para clustering: {available_metrics}")
            return df
        except Exception as e:
            self.logger.warning(f"Error detectando regímenes de mercado para Unified_Score: {e}")
            return df

    def _apply_hmm_analysis_for_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica análisis HMM para Unified_Score solo si hay datos secuenciales reales."""
        try:
            self.logger.info("🔬 Aplicando análisis HMM para Unified_Score...")
            # Comprobar si el analizador HMM es real y hay datos secuenciales
            hmm_analyzer = getattr(self.factor_k, 'hmm_analyzer', None)
            if hmm_analyzer is None or getattr(hmm_analyzer, 'is_simulation', True):
                self.logger.info("⚠️ HMM no ejecutado: no hay analizador real o datos secuenciales.")
                return df
            # Seleccionar métricas para HMM
            hmm_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR']
            available_metrics = [m for m in hmm_metrics if m in df.columns]
            self.logger.info(f"📊 Métricas disponibles para HMM: {available_metrics}")
            if len(available_metrics) >= 2:
                X = df[available_metrics].fillna(0).values
                # Aquí se llamaría al analizador HMM real
                states = hmm_analyzer.predict_states(X)
                df['HMM_State'] = states
                self.logger.info(f"✅ Estados HMM asignados: {len(df)} estrategias")
                for state in np.unique(states):
                    state_mask = df['HMM_State'] == state
                    # Refuerzo: aseguro que state_mask es un array booleano y nunca se usa como condicional directo
                    if hasattr(state_mask, 'any') and callable(state_mask.any):
                        if state_mask.any():
                            state_score = df.loc[state_mask, 'FK96_Elite_Enhanced'].mean()
                            size = int(state_mask.sum())
                            self.logger.info(f"📊 Estado HMM {state}: {size} estrategias, score promedio: {state_score:.4f}")
                            df.loc[state_mask, 'HMM_Score'] = state_score
            else:
                self.logger.warning(f"⚠️ Insuficientes métricas para HMM: {available_metrics}")
            return df
        except Exception as e:
            self.logger.warning(f"Error aplicando análisis HMM para Unified_Score: {e}")
            return df
    
    def _apply_scientific_score_enhancement_for_unified(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica mejoras científicas al Unified_Score.
        Justificación de pesos:
        - Unified_Score_Scientific: 0.5 Unified + 0.3 Regime + 0.2 HMM (si ambos disponibles)
        - Si solo hay régimen: 0.7 Unified + 0.3 Regime
        - Si no hay mejoras: solo Unified
        Estos pesos son heurísticos y pueden calibrarse en el futuro.
        Se evita redundancia: Regime_Score y HMM_Score solo se usan si aportan información adicional.
        Preparado para integrar predictibilidad/robustez si está disponible (ver TODO).
        """
        try:
            self.logger.info("🔬 Aplicando mejora científica al Unified_Score...")
            # Verificar columnas disponibles
            has_regime = 'Regime_Score' in df.columns
            has_hmm = 'HMM_Score' in df.columns
            # TODO: Integrar predictibilidad/robustez si está disponible en df (ej: 'Predictability_Score', 'Robustness_Score')
            self.logger.info(f"📊 Columnas científicas disponibles: Regime_Score={has_regime}, HMM_Score={has_hmm}")
            # Crear Unified_Score_Scientific combinando scores
            if has_regime and has_hmm:
                df['Unified_Score_Scientific'] = (
                    0.5 * df['Unified_Score'] + 
                    0.3 * df['Regime_Score'] + 
                    0.2 * df['HMM_Score']
                )
                self.logger.info("✅ Unified_Score_Scientific creado con régimen y HMM (pesos 0.5/0.3/0.2)")
            elif has_regime:
                df['Unified_Score_Scientific'] = (
                    0.7 * df['Unified_Score'] + 
                    0.3 * df['Regime_Score']
                )
                self.logger.info("✅ Unified_Score_Scientific creado con régimen (pesos 0.7/0.3)")
            else:
                df['Unified_Score_Scientific'] = df['Unified_Score']
                self.logger.info("⚠️ Unified_Score_Scientific igual a Unified_Score (sin mejoras científicas)")
            # Crear Unified_Score_Enhanced con ajuste dinámico
            if has_regime:
                regime_max = df['Regime_Score'].max()
                if regime_max > 0:
                    regime_adjustment = df['Regime_Score'] / regime_max
                else:
                    regime_adjustment = df['Regime_Score'] * 0  # Si no hay variación, normalizar a 0
                df['Unified_Score_Enhanced'] = df['Unified_Score'] * (1 + 0.2 * regime_adjustment)
                self.logger.info("✅ Unified_Score_Enhanced creado con ajuste de régimen (factor 0.2)")
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
        """Obtiene resumen de la evaluación unificada.
        Incluye top 5 estrategias por Unified_Score_Scientific (si existe), tamaños de clusters/regímenes,
        métricas de tail risk, y advertencia si hay columnas temporales. Nomenclatura consistente en scores.
        TODO: Limpiar columnas temporales (Market_Regime, HMM_State) si no se requieren en la salida final.
        """
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
                'Unified_Score_Robust_Normalized',
                'Unified_Score_Scientific',
                'Unified_Score_Enhanced'
            ]
            for col in score_columns:
                if col in df.columns:
                    summary['scores_calculated'].append(col)
                    summary[f'{col}_mean'] = df[col].mean()
                    summary[f'{col}_std'] = df[col].std()
                    summary[f'{col}_min'] = df[col].min()
                    summary[f'{col}_max'] = df[col].max()
            
            # Verificar métricas de tail risk calculadas
            tail_risk_columns = [col for col in df.columns if col.startswith('TailRisk_')]
            if tail_risk_columns:
                summary['tail_risk_metrics_calculated'] = tail_risk_columns
                summary['tail_risk_metrics_count'] = len(tail_risk_columns)
                
                # Estadísticas de métricas de tail risk
                for col in tail_risk_columns:
                    if col in df.columns and df[col].dtype in ['float64', 'int64']:
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
            
            # Top 5 estrategias por Unified_Score_Scientific (si existe)
            if 'Unified_Score_Scientific' in df.columns:
                top5 = df.sort_values('Unified_Score_Scientific', ascending=False).head(5)
                if isinstance(top5, pd.Series):
                    top5 = top5.to_frame().T
                if 'Strategy_Name' in df.columns:
                    summary['top5_strategies'] = top5[['Strategy_Name', 'Unified_Score_Scientific']].reset_index(drop=True).to_dict(orient='records')  # type: ignore[reportCallIssue]  # pandas acepta orient='records'
                else:
                    summary['top5_strategies'] = top5.reset_index().to_dict(orient='records')  # type: ignore[reportCallIssue]
            
            # Tamaños de clusters/regímenes
            if 'Market_Regime' in df.columns:
                regime_counts = df['Market_Regime'].value_counts().to_dict()
                summary['market_regime_counts'] = regime_counts
            if 'HMM_State' in df.columns:
                hmm_counts = df['HMM_State'].value_counts().to_dict()
                summary['hmm_state_counts'] = hmm_counts
            
            # Información de tail risk por estrategia
            if tail_risk_columns and 'Strategy_Name' in df.columns:
                tail_risk_summary = {}
                for _, row in df.iterrows():
                    strategy_name = row.get('Strategy_Name', 'Unknown')
                    strategy_metrics = {}
                    for col in tail_risk_columns:
                        if col in row and pd.notna(row[col]):
                            strategy_metrics[col] = row[col]
                    if len(strategy_metrics) > 0:
                        tail_risk_summary[strategy_name] = strategy_metrics
                
                if len(tail_risk_summary) > 0:
                    summary['tail_risk_by_strategy'] = tail_risk_summary
            
            # Advertencia si hay columnas temporales
            temp_cols = [col for col in ['Market_Regime', 'HMM_State'] if col in df.columns]
            if temp_cols:
                summary['warning'] = f"Columnas temporales presentes: {temp_cols}. Considera limpiarlas si no son necesarias en la salida final."
            
            # TODO: Limpiar columnas temporales si no se requieren (decisión de negocio)
            return summary
        except Exception as e:
            self.logger.error(f"Error generando resumen unificado: {e}")
            return {'error': str(e)} 