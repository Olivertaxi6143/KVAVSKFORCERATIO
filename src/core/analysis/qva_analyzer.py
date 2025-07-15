from typing import Optional, Any, Union
#!/usr/bin/env python3
"""
QVAScorerEnhanced - Análisis QVA Unificado y Mejorado

Integra funcionalidades básicas y avanzadas en un solo módulo:
- Scoring QVA robusto con penalizaciones avanzadas
- Integración con ExtraKPIManager para KPIs extra por estilo de trading
- Componentes de ML opcionales (predicción OOS, detección overfitting)
- Explicabilidad con SHAP (opcional)
- Optimización automática de pesos y penalizaciones (opcional)
- Pesos dinámicos según régimen de mercado (opcional)

Características principales:
- Compatibilidad total con GUI y tests existentes
- Funcionalidades avanzadas opcionales (no rompen flujo actual)
- Integración completa con DataManager
- Validación robusta y logging detallado
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple, Any
import logging
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Importar DataManager y utilidades
from src.data.data_manager import DataManager, create_data_manager
from src.data.data_utils import read_and_prepare
from src.gui.utils import validate_dataframe
from src.getattr(core, 'config', None).config_manager import ConfigManagerEnhanced
from src.getattr(core, 'config', None).progress_callback import ProgressCallback
from src.logger_config import setup_logger

# Importar ExtraKPIManager desde el módulo dedicado
from src.core.analysis.extra_kpi_manager import ExtraKPIManager

# Importar librerías de ML para funcionalidades avanzadas (opcionales)
try:
    from sklearn.ensemble import RandomForestRegressor, IsolationForest
    from getattr(sklearn, 'model', None)_selection import cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    import shap
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ Librerías de ML no disponibles. Funcionalidades básicas únicamente.")

def ensure_series(obj: Any, index: Any = None) -> pd.Series:
    """
    Convierte cualquier objeto a pd.Series de forma robusta.
    """
    if isinstance(obj, pd.DataFrame):
        if obj.shape[1] == 1:
            return obj.iloc[:, 0]
        else:
            squeezed = obj.squeeze()
            if isinstance(squeezed, pd.Series):
                return squeezed
            elif isinstance(squeezed, pd.DataFrame) and squeezed.shape[1] == 1:
                return squeezed.iloc[:, 0]
            else:
                return pd.Series(squeezed.values.flatten() if hasattr(squeezed, 'values') else squeezed, index=index)
    elif isinstance(obj, pd.Series):
        return obj
    elif isinstance(obj, (float, int)):
        if index is not None:
            return pd.Series(obj, index=index)
        return pd.Series([obj])
    elif hasattr(obj, '__len__') and len(obj) == 1:
        return pd.Series(obj, index=index)
    else:
        return pd.Series(obj, index=index)

class QVAScorerEnhanced:
    """
    QVA Scorer unificado con funcionalidades básicas y avanzadas.

    ADVERTENCIA PROFESIONAL:
    ------------------------------------------------------------
    Este módulo SOLO debe recibir DataFrames ya validados y preparados por DataManager
    u otras funciones centralizadas de la capa data. No realizar validación, carga ni
    manipulación local de datos aquí. Toda gestión de datos debe estar centralizada.
    ------------------------------------------------------------
    """
    
    def __init__(self, config_manager: Optional[ConfigManagerEnhanced] = None, 
                 progress_callback: Optional[ProgressCallback] = None,
                 data_manager: Optional[DataManager] = None,
                 enable_advanced_features: bool = False):
        """
        Inicializa el QVA Scorer unificado.
        
        Args:
            config_manager: Configuración del sistema
            progress_callback: Callback para progreso
            data_manager: Instancia de DataManager (opcional)
            enable_advanced_features: Activar funcionalidades avanzadas (ML, explicabilidad, etc.)
        """
        self.logger = setup_logger("qva_unified")
        getattr(self, 'config', None)_manager = config_manager or ConfigManagerEnhanced()
        self.progress_callback = progress_callback
        self.extra_kpi_manager = ExtraKPIManager(config_manager)
        
        # Integración con DataManager
        self.data_manager = data_manager or create_data_manager()
        
        # Configuración de funcionalidades avanzadas
        self.enable_advanced_features = enable_advanced_features
        
        # Componentes de IA (si están disponibles y habilitados)
        self.ml_components = {}
        if ML_AVAILABLE and enable_advanced_features:
            self._initialize_ml_components()
        
        # Configuración de penalizaciones mejorada
        self.penalty_config = {
            'consecutive_losses': {
                'enabled': True,
                'threshold': 5,
                'penalty_factor': 0.8
            },
            'stagnation': {
                'enabled': True,
                'threshold': 10,
                'penalty_factor': 0.9
            },
            'stagnation_trades': {
                'enabled': True,
                'threshold': 8,
                'penalty_factor': 0.85
            },
            'drawdown_duration': {
                'enabled': True,
                'threshold': 20,
                'penalty_factor': 0.85
            },
            'exposure': {
                'enabled': True,
                'min_threshold': 0.1,
                'max_threshold': 0.9,
                'penalty_factor': 0.95
            },
            'winning_percent': {
                'enabled': True,
                'min_threshold': 0.3,
                'penalty_factor': 0.9
            },
            'oos_robustness': {
                'enabled': enable_advanced_features,
                'min_correlation': 0.5,
                'penalty_factor': 0.7
            },
            'overfitting': {
                'enabled': enable_advanced_features,
                'contamination': 0.1,
                'penalty_factor': 0.6
            }
        }
        
        # Pesos por estilo de trading (configurables)
        self.trading_style_weights = {
            'Scalping': {
                'profitability': 0.35,
                'risk': 0.40,
                'consistency': 0.25,
                'extra_kpis': 0.15
            },
            'Day Trading': {
                'profitability': 0.40,
                'risk': 0.35,
                'consistency': 0.25,
                'extra_kpis': 0.15
            },
            'Swing Trading': {
                'profitability': 0.45,
                'risk': 0.30,
                'consistency': 0.25,
                'extra_kpis': 0.15
            },
            'Position Trading': {
                'profitability': 0.50,
                'risk': 0.25,
                'consistency': 0.25,
                'extra_kpis': 0.15
            },
            'Breakout': {
                'profitability': 0.40,
                'risk': 0.35,
                'consistency': 0.25,
                'extra_kpis': 0.15
            },
            'General': {
                'profitability': 0.40,
                'risk': 0.35,
                'consistency': 0.25,
                'extra_kpis': 0.15
            }
        }
        
        self.logger.info("✅ QVAScorerEnhanced unificado inicializado correctamente")
        if enable_advanced_features:
            self.logger.info("🔬 Funcionalidades avanzadas habilitadas")
    
    def _initialize_ml_components(self):
        """Inicializa componentes de ML si están disponibles."""
        try:
            self.ml_components = {
                'oos_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
                'overfitting_detector': IsolationForest(contamination=0.1, random_state=42),  # type: ignore[reportArgumentType]
                'market_regime_cluster': KMeans(n_clusters=3, random_state=42),
                'scaler': StandardScaler()
            }
            self.logger.info("✅ Componentes de ML inicializados")
        except Exception as e:
            self.logger.warning(f"⚠️ Error inicializando ML: {e}")
    
    def _get_data_from_manager(self) -> pd.DataFrame:
        """Obtiene datos del DataManager."""
        try:
            if self.data_manager:
                return self.data_manager.get_kpis_data()
            else:
                self.logger.warning("⚠️ DataManager no disponible")
                return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo datos del DataManager: {e}")
            return pd.DataFrame()
    
    def calculate_qva_score(self, df: Optional[pd.DataFrame] = None) -> pd.Series:
        """
        Recibe un DataFrame ya validado y preparado por DataManager.
        No realizar validación ni carga local aquí.
        """
        self.logger.debug("[INICIO] calculate_qva_score - Entrada recibida (datos validados por DataManager)")
        try:
            
            # Obtener datos del DataManager si no se proporcionan
            if df is None:
                df = self._get_data_from_manager()
                if df.empty:
                    self.logger.error("❌ No hay datos disponibles")
                    return pd.Series()
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 0, 100, "Iniciando cálculo QVA...")
            
            # Validación de datos
            if df.empty:
                self.logger.warning("⚠️ DataFrame vacío, retornando scores por defecto")
                return pd.Series(0.5, index=df.index)
            
            # Obtener KPIs habilitados
            enabled_kpis = getattr(self, 'config', None)_manager.get_enabled_kpis()
            self.logger.info(f"📊 KPIs habilitados: {len(enabled_kpis)}")
            
            # Obtener estilo de trading actual
            trading_style = getattr(self, 'config', None)_manager.current_config.get('trading_style', 'General')
            self.logger.info(f"🎯 Estilo de trading: {trading_style}")
            
            # Obtener pesos para el estilo de trading
            weights = self.trading_style_weights.get(trading_style, self.trading_style_weights['General'])
            self.logger.info(f"⚖️ Pesos aplicados: {weights}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 15, 100, "Calculando componente de rentabilidad...")
            
            # Calcular componente de rentabilidad con normalización robusta
            profitability_score = self._calculate_profitability_component_robust(df, enabled_kpis)
            self.logger.info(f"💰 Componente de rentabilidad calculado: {profitability_score.mean():.4f}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 30, 100, "Calculando componente de riesgo...")
            
            # Calcular componente de riesgo con normalización robusta
            risk_score = self._calculate_risk_component_robust(df, enabled_kpis)
            self.logger.info(f"🛡️ Componente de riesgo calculado: {risk_score.mean():.4f}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 45, 100, "Calculando componente de consistencia...")
            
            # Calcular componente de consistencia con normalización robusta
            consistency_score = self._calculate_consistency_component_robust(df, enabled_kpis)
            self.logger.info(f"📈 Componente de consistencia calculado: {consistency_score.mean():.4f}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 60, 100, "Aplicando KPIs extra...")
            
            # Calcular componente de KPIs extra según el estilo de trading
            extra_kpis_score = self.extra_kpi_manager.apply_extra_kpis_to_qva_score(df, trading_style)
            self.logger.info(f"🔧 Componente de KPIs extra calculado: {extra_kpis_score.mean():.4f}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 75, 100, "Aplicando penalizaciones avanzadas...")
            
            # Calcular penalizaciones avanzadas
            penalties = self._calculate_advanced_penalties(df)
            self.logger.info(f"⚠️ Penalizaciones calculadas: {len(penalties)} tipos")
            
            # Calcular score QVA final con pesos configurables
            self.logger.info("🎯 Calculando score QVA final con pesos configurables...")
            
            # Componente base del QVA Score con pesos por estilo
            base_qva_score = (
                profitability_score * weights['profitability'] +
                risk_score * weights['risk'] +
                consistency_score * weights['consistency']
            )
            
            # Integrar KPIs extra
            extra_kpis_component = extra_kpis_score * weights['extra_kpis']
            
            # QVA Score final con penalizaciones
            if isinstance(base_qva_score, (float, int)):
                base_qva_score = pd.Series(base_qva_score, index=df.index)
            if isinstance(extra_kpis_component, (float, int)):
                extra_kpis_component = pd.Series(extra_kpis_component, index=df.index)
            if isinstance(penalties['total_penalty'], (float, int)):
                penalties['total_penalty'] = pd.Series(penalties['total_penalty'], index=df.index)
            qva_score = (base_qva_score + extra_kpis_component) * penalties['total_penalty']
            if not isinstance(qva_score, pd.Series):
                qva_score = pd.Series(qva_score, index=df.index)
            # Normalización final robusta
            qva_score = self._robust_normalization(ensure_series(qva_score, index=df.index))
            
            self.logger.info(f"✅ Score QVA calculado exitosamente: {qva_score.mean():.4f} ± {qva_score.std():.4f}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 100, 100, "Cálculo QVA completado")
            self.logger.debug("[FIN] calculate_qva_score - Score calculado")
            
            return qva_score
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando QVA Score: {e}")
            return pd.Series(0.5, index=df.index if df is not None else pd.Index([]))
    
    def _calculate_profitability_component_robust(self, df: pd.DataFrame, enabled_kpis: List[str]) -> pd.Series:
        """
        Calcula el componente de rentabilidad con normalización robusta.
        
        Args:
            df: DataFrame con datos
            enabled_kpis: Lista de KPIs habilitados
            
        Returns:
            Series con scores de rentabilidad normalizados
        """
        try:
            profitability_kpis = ['Profit_factor', 'CAGR', 'Net_profit', 'Winning_Percent']
            available_kpis = [kpi for kpi in profitability_kpis if kpi in df.columns]
            
            if not available_kpis:
                self.logger.warning("⚠️ No hay KPIs de rentabilidad disponibles")
                return pd.Series(0.5, index=df.index)
            
            # Calcular scores individuales
            scores = []
            for kpi in available_kpis:
                try:
                    values = df[kpi].fillna(0)
                    normalized = self._robust_normalization(ensure_series(values, index=df.index), higher_is_better=True)
                    scores.append(normalized)
                except Exception as e:
                    self.logger.warning(f"⚠️ Error procesando KPI {kpi}: {e}")
                    scores.append(pd.Series(0.5, index=df.index))
            
            # Combinar scores
            if scores:
                combined_score = pd.concat(scores, axis=1).mean(axis=1)
                combined_score = pd.Series(combined_score, index=df.index).astype(float)
                return self._robust_normalization(ensure_series(combined_score, index=df.index))
            else:
                return pd.Series(0.5, index=df.index)
                
        except Exception as e:
            self.logger.error(f"❌ Error calculando componente de rentabilidad: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _calculate_risk_component_robust(self, df: pd.DataFrame, enabled_kpis: List[str]) -> pd.Series:
        """
        Calcula el componente de riesgo con normalización robusta.
        
        Args:
            df: DataFrame con datos
            enabled_kpis: Lista de KPIs habilitados
            
        Returns:
            Series con scores de riesgo normalizados
        """
        try:
            risk_kpis = ['Max_DD_%', 'CalmarRatio', 'Sortino_Ratio', 'Sharpe_Ratio']
            available_kpis = [kpi for kpi in risk_kpis if kpi in df.columns]
            
            if not available_kpis:
                self.logger.warning("⚠️ No hay KPIs de riesgo disponibles")
                return pd.Series(0.5, index=df.index)
            
            # Calcular scores individuales
            scores = []
            for kpi in available_kpis:
                try:
                    values = df[kpi].fillna(0)
                    # Para Max_DD_%, valores más bajos son mejores
                    higher_is_better = kpi != 'Max_DD_%'
                    normalized = self._robust_normalization(ensure_series(values, index=df.index), higher_is_better=higher_is_better)
                    scores.append(normalized)
                except Exception as e:
                    self.logger.warning(f"⚠️ Error procesando KPI {kpi}: {e}")
                    scores.append(pd.Series(0.5, index=df.index))
            
            # Combinar scores
            if scores:
                combined_score = pd.concat(scores, axis=1).mean(axis=1)
                combined_score = pd.Series(combined_score, index=df.index).astype(float)
                return self._robust_normalization(ensure_series(combined_score, index=df.index))
            else:
                return pd.Series(0.5, index=df.index)
                
        except Exception as e:
            self.logger.error(f"❌ Error calculando componente de riesgo: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _calculate_consistency_component_robust(self, df: pd.DataFrame, enabled_kpis: List[str]) -> pd.Series:
        """
        Calcula el componente de consistencia con normalización robusta.
        
        Args:
            df: DataFrame con datos
            enabled_kpis: Lista de KPIs habilitados
            
        Returns:
            Series con scores de consistencia normalizados
        """
        try:
            consistency_kpis = ['RecoveryFactor', 'SQN', 'Expectancy', '#_of_trades']
            available_kpis = [kpi for kpi in consistency_kpis if kpi in df.columns]
            
            if not available_kpis:
                self.logger.warning("⚠️ No hay KPIs de consistencia disponibles")
                return pd.Series(0.5, index=df.index)
            
            # Calcular scores individuales
            scores = []
            for kpi in available_kpis:
                try:
                    values = df[kpi].fillna(0)
                    normalized = self._robust_normalization(ensure_series(values, index=df.index), higher_is_better=True)
                    scores.append(normalized)
                except Exception as e:
                    self.logger.warning(f"⚠️ Error procesando KPI {kpi}: {e}")
                    scores.append(pd.Series(0.5, index=df.index))
            
            # Combinar scores
            if scores:
                combined_score = pd.concat(scores, axis=1).mean(axis=1)
                combined_score = pd.Series(combined_score, index=df.index).astype(float)
                return self._robust_normalization(ensure_series(combined_score, index=df.index))
            else:
                return pd.Series(0.5, index=df.index)
                
        except Exception as e:
            self.logger.error(f"❌ Error calculando componente de consistencia: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _calculate_advanced_penalties(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calcula penalizaciones avanzadas.
        
        Args:
            df: DataFrame con datos
            
        Returns:
            Diccionario con penalizaciones calculadas
        """
        try:
            penalties = {}
            
            # Penalización por pérdidas consecutivas
            if self.penalty_config['consecutive_losses']['enabled']:
                penalties['consecutive_losses'] = self._calculate_consecutive_losses_penalty(df)
            
            # Penalización por estancamiento
            if self.penalty_config['stagnation']['enabled']:
                penalties['stagnation'] = self._calculate_stagnation_penalty(df)
            
            # Penalización por trades de estancamiento
            if self.penalty_config['stagnation_trades']['enabled']:
                penalties['stagnation_trades'] = self._calculate_stagnation_trades_penalty(df)
            
            # Penalización por duración de drawdown
            if self.penalty_config['drawdown_duration']['enabled']:
                penalties['drawdown_duration'] = self._calculate_drawdown_duration_penalty(df)
            
            # Penalización por exposición
            if self.penalty_config['exposure']['enabled']:
                penalties['exposure'] = self._calculate_exposure_penalty(df)
            
            # Penalización por porcentaje de victorias
            if self.penalty_config['winning_percent']['enabled']:
                penalties['winning_percent'] = self._calculate_winning_percent_penalty(df)
            
            # Penalizaciones avanzadas (solo si están habilitadas)
            if self.enable_advanced_features:
                if self.penalty_config['oos_robustness']['enabled']:
                    penalties['oos_robustness'] = self._calculate_oos_robustness_penalty(df)
                
                if self.penalty_config['overfitting']['enabled']:
                    penalties['overfitting'] = self._calculate_overfitting_penalty(df)
            
            # Calcular penalización total
            if penalties:
                total_penalty = pd.concat(list(penalties.values()), axis=1).mean(axis=1)
                total_penalty = pd.Series(total_penalty, index=df.index).astype(float)
                penalties['total_penalty'] = self._robust_normalization(ensure_series(total_penalty, index=df.index))
            else:
                penalties['total_penalty'] = pd.Series(1.0, index=df.index)
            
            return penalties
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando penalizaciones: {e}")
            return {'total_penalty': pd.Series(1.0, index=df.index)}
    
    def _calculate_consecutive_losses_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por pérdidas consecutivas."""
        try:
            if 'Max_Consec._Losses' in df.columns:
                max_losses = df['Max_Consec._Losses'].fillna(0)
                threshold = self.penalty_config['consecutive_losses']['threshold']
                penalty_factor = self.penalty_config['consecutive_losses']['penalty_factor']
                
                penalty = np.where(max_losses > threshold, penalty_factor, 1.0)
                return pd.Series(penalty, index=df.index)
            else:
                return pd.Series(1.0, index=df.index)
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando penalización por pérdidas consecutivas: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _calculate_stagnation_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por estancamiento."""
        try:
            if 'Stagnation' in df.columns:
                stagnation = df['Stagnation'].fillna(0)
                threshold = self.penalty_config['stagnation']['threshold']
                penalty_factor = self.penalty_config['stagnation']['penalty_factor']
                
                penalty = np.where(stagnation > threshold, penalty_factor, 1.0)
                return pd.Series(penalty, index=df.index)
            else:
                return pd.Series(1.0, index=df.index)
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando penalización por estancamiento: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _calculate_stagnation_trades_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por trades de estancamiento."""
        try:
            if 'Stagnation_trades' in df.columns:
                stagnation_trades = df['Stagnation_trades'].fillna(0)
                threshold = self.penalty_config['stagnation_trades']['threshold']
                penalty_factor = self.penalty_config['stagnation_trades']['penalty_factor']
                
                penalty = np.where(stagnation_trades > threshold, penalty_factor, 1.0)
                return pd.Series(penalty, index=df.index)
            else:
                return pd.Series(1.0, index=df.index)
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando penalización por trades de estancamiento: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _calculate_drawdown_duration_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por duración de drawdown."""
        try:
            if 'Max_Drawdown_Duration' in df.columns:
                duration = df['Max_Drawdown_Duration'].fillna(0)
                threshold = self.penalty_config['drawdown_duration']['threshold']
                penalty_factor = self.penalty_config['drawdown_duration']['penalty_factor']
                
                penalty = np.where(duration > threshold, penalty_factor, 1.0)
                return pd.Series(penalty, index=df.index)
            else:
                return pd.Series(1.0, index=df.index)
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando penalización por duración de drawdown: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _calculate_exposure_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por exposición."""
        try:
            if 'Exposure' in df.columns:
                exposure = df['Exposure'].fillna(0.5)
                min_threshold = self.penalty_config['exposure']['min_threshold']
                max_threshold = self.penalty_config['exposure']['max_threshold']
                penalty_factor = self.penalty_config['exposure']['penalty_factor']
                
                penalty = np.where((exposure < min_threshold) | (exposure > max_threshold), 
                                 penalty_factor, 1.0)
                return pd.Series(penalty, index=df.index)
            else:
                return pd.Series(1.0, index=df.index)
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando penalización por exposición: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _calculate_winning_percent_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por porcentaje de victorias."""
        try:
            if 'Winning_Percent' in df.columns:
                winning_percent = df['Winning_Percent'].fillna(50) / 100
                min_threshold = self.penalty_config['winning_percent']['min_threshold']
                penalty_factor = self.penalty_config['winning_percent']['penalty_factor']
                
                penalty = np.where(winning_percent < min_threshold, penalty_factor, 1.0)
                return pd.Series(penalty, index=df.index)
            else:
                return pd.Series(1.0, index=df.index)
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando penalización por porcentaje de victorias: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _calculate_oos_robustness_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por robustez OOS (funcionalidad avanzada)."""
        if not self.enable_advanced_features or not ML_AVAILABLE:
            return pd.Series(1.0, index=df.index)
        
        try:
            # Implementar predicción de robustez OOS con ML
            oos_scores = self._predict_oos_robustness(df)
            min_correlation = self.penalty_config['oos_robustness']['min_correlation']
            penalty_factor = self.penalty_config['oos_robustness']['penalty_factor']
            
            penalty = np.where(oos_scores < min_correlation, penalty_factor, 1.0)
            return pd.Series(penalty, index=df.index)
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando penalización por robustez OOS: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _calculate_overfitting_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por sobreajuste (funcionalidad avanzada)."""
        if not self.enable_advanced_features or not ML_AVAILABLE:
            return pd.Series(1.0, index=df.index)
        
        try:
            # Implementar detección de sobreajuste con ML
            overfitting_scores = self._detect_overfitting(df)
            penalty_factor = self.penalty_config['overfitting']['penalty_factor']
            
            penalty = np.where(overfitting_scores > 0.5, penalty_factor, 1.0)
            return pd.Series(penalty, index=df.index)
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando penalización por sobreajuste: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _predict_oos_robustness(self, df: pd.DataFrame) -> pd.Series:
        """Predice robustez OOS usando ML (funcionalidad avanzada)."""
        if not self.enable_advanced_features or not ML_AVAILABLE:
            return pd.Series(0.5, index=df.index)
        
        try:
            # Implementar predicción de robustez OOS
            # Por ahora, retornar valores por defecto
            return pd.Series(0.7, index=df.index)
        except Exception as e:
            self.logger.warning(f"⚠️ Error prediciendo robustez OOS: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _detect_overfitting(self, df: pd.DataFrame) -> pd.Series:
        """Detecta sobreajuste usando ML (funcionalidad avanzada)."""
        if not self.enable_advanced_features or not ML_AVAILABLE:
            return pd.Series(0.3, index=df.index)
        
        try:
            # Implementar detección de sobreajuste
            # Por ahora, retornar valores por defecto
            return pd.Series(0.3, index=df.index)
        except Exception as e:
            self.logger.warning(f"⚠️ Error detectando sobreajuste: {e}")
            return pd.Series(0.3, index=df.index)
    
    def _robust_normalization(self, series: pd.Series, higher_is_better: bool = True) -> pd.Series:
        """
        Aplica normalización robusta a una serie.
        
        Args:
            series: Serie a normalizar
            higher_is_better: Si valores más altos son mejores
            
        Returns:
            Serie normalizada en [0,1]
        """
        try:
            if not isinstance(series, pd.Series) or series.empty:
                return pd.Series(0.5, index=series.index if hasattr(series, 'index') else None)
            # Manejar valores extremos
            series = series.replace([np.inf, -np.inf], np.nan)
            series = series.fillna(series.median())
            mean_val = series.mean()
            std_val = series.std()
            if std_val == 0:
                return pd.Series(0.5, index=series.index)
            normalized = 1 / (1 + np.exp(-(series - mean_val) / (std_val + 1e-8)))
            if not higher_is_better:
                normalized = 1 - normalized
            return pd.Series(normalized, index=series.index)
        except Exception as e:
            self.logger.warning(f"⚠️ Error en normalización robusta: {e}")
            return pd.Series(0.5, index=series.index if hasattr(series, 'index') else None)
    
    def get_score_breakdown(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Obtiene el desglose detallado de scores.
        
        Args:
            df: DataFrame con datos
            
        Returns:
            Diccionario con componentes del score
        """
        try:
            enabled_kpis = getattr(self, 'config', None)_manager.get_enabled_kpis()
            trading_style = getattr(self, 'config', None)_manager.current_config.get('trading_style', 'General')
            
            breakdown = {
                'profitability': self._calculate_profitability_component_robust(df, enabled_kpis),
                'risk': self._calculate_risk_component_robust(df, enabled_kpis),
                'consistency': self._calculate_consistency_component_robust(df, enabled_kpis),
                'extra_kpis': self.extra_kpi_manager.apply_extra_kpis_to_qva_score(df, trading_style),
                'penalties': self._calculate_advanced_penalties(df)['total_penalty'],
                'weights': self.trading_style_weights.get(trading_style, self.trading_style_weights['General'])
            }
            
            return breakdown
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo desglose de scores: {e}")
            return {}
    
    def update_trading_style_weights(self, trading_style: str, weights: Dict[str, float]) -> None:
        """
        Actualiza los pesos para un estilo de trading específico.
        
        Args:
            trading_style: Estilo de trading
            weights: Nuevos pesos
        """
        try:
            self.trading_style_weights[trading_style] = weights
            self.logger.info(f"⚖️ Pesos actualizados para {trading_style}: {weights}")
        except Exception as e:
            self.logger.error(f"❌ Error actualizando pesos: {e}")
    
    def update_penalty_config(self, penalty_type: str, config: Dict[str, Any]) -> None:
        """
        Actualiza la configuración de penalizaciones.
        
        Args:
            penalty_type: Tipo de penalización
            config: Nueva configuración
        """
        try:
            self.penalty_config[penalty_type] = config
            self.logger.info(f"⚙️ Configuración de penalización actualizada para {penalty_type}")
        except Exception as e:
            self.logger.error(f"❌ Error actualizando configuración de penalización: {e}")
    
    def compute_qva_score_robust(self, df: pd.DataFrame, alpha: float = 0.8) -> pd.Series:
        """
        Recibe un DataFrame ya validado y preparado por DataManager.
        No realizar validación ni carga local aquí.
        """
        self.logger.info("Calculando QVA Score Robusto (datos ya preparados por DataManager)")
        try:
            # Calcular score QVA normal
            qva_score = self.calculate_qva_score(df)
            if not isinstance(qva_score, pd.Series):
                qva_score = pd.Series(qva_score, index=df.index)
            
            # Aplicar factor de robustez
            robust_score = qva_score * alpha + (1 - alpha) * 0.5
            
            return pd.Series(robust_score, index=df.index)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando score QVA robusto: {e}")
            return pd.Series(0.5, index=df.index)
    
    # ============================================================================
    # FUNCIONALIDADES AVANZADAS (OPCIONALES)
    # ============================================================================
    
    def explain_score(self, df: pd.DataFrame, strategy_idx: int) -> Dict[str, float]:
        """
        Explica el score de una estrategia específica (funcionalidad avanzada).
        """
        if not self.enable_advanced_features:
            return {"explanation": 0.0}
        try:
            breakdown = self.get_score_breakdown(df)
            explanation = {}
            for component, scores in breakdown.items():
                if len(scores) > strategy_idx:
                    explanation[component] = float(scores.iloc[strategy_idx])
            return explanation
        except Exception as e:
            self.logger.error(f"❌ Error explicando score: {e}")
            return {"error": 0.0}

    def _calculate_ml_enhancement_component(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcula el componente de mejora ML (funcionalidad avanzada).
        
        Args:
            df: DataFrame con datos
            
        Returns:
            Series con scores de mejora ML
        """
        if not self.enable_advanced_features or not ML_AVAILABLE:
            return pd.Series(0.5, index=df.index)
        
        try:
            # Predicción de robustez OOS
            oos_scores = self._predict_oos_robustness(df)
            
            # Detección de sobreajuste
            overfitting_scores = self._detect_overfitting(df)
            
            # Análisis de régimen de mercado
            regime_scores = self._analyze_market_regime(df)
            
            # Combinar componentes ML
            ml_components = [oos_scores, overfitting_scores, regime_scores]
            combined_ml = pd.concat(ml_components, axis=1).mean(axis=1)
            
            return self._robust_normalization(ensure_series(combined_ml, index=df.index))
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando componente ML: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _analyze_market_regime(self, df: pd.DataFrame) -> pd.Series:
        """
        Analiza régimen de mercado usando clustering (funcionalidad avanzada).
        
        Args:
            df: DataFrame con datos
            
        Returns:
            Series con scores de régimen de mercado
        """
        if not self.enable_advanced_features or not ML_AVAILABLE:
            return pd.Series(0.5, index=df.index)
        
        try:
            # Seleccionar métricas para clustering
            regime_metrics = ['Sharpe_Ratio', 'Max_DD_%', 'CAGR', 'Profit_factor']
            available_metrics = [col for col in regime_metrics if col in df.columns]
            
            if len(available_metrics) < 2:
                return pd.Series(0.5, index=df.index)
            
            # Preparar datos para clustering
            X = df[available_metrics].fillna(0)
            X_scaled = self.ml_components['scaler'].fit_transform(X)
            
            # Aplicar clustering
            clusters = self.ml_components['market_regime_cluster'].fit_predict(X_scaled)
            
            # Calcular scores por régimen
            regime_scores = pd.Series(clusters, index=df.index)
            
            # Normalizar scores de régimen
            return self._robust_normalization(ensure_series(regime_scores, index=df.index))
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error analizando régimen de mercado: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _get_trading_style_characteristics(self, trading_style: str) -> Dict[str, Any]:
        """
        Obtiene características específicas del estilo de trading.
        
        Args:
            trading_style: Estilo de trading
            
        Returns:
            Diccionario con características del estilo
        """
        characteristics = {
            'Scalping': {
                'timeframe': 'M1-M5',
                'avg_trades_per_month': 200,
                'risk_tolerance': 'high',
                'profit_target': 'small_consistent',
                'max_drawdown_tolerance': 0.15,
                'sharpe_minimum': 1.5,
                'profit_factor_minimum': 1.2
            },
            'Day Trading': {
                'timeframe': 'M5-H1',
                'avg_trades_per_month': 50,
                'risk_tolerance': 'medium_high',
                'profit_target': 'moderate_consistent',
                'max_drawdown_tolerance': 0.20,
                'sharpe_minimum': 1.3,
                'profit_factor_minimum': 1.4
            },
            'Swing Trading': {
                'timeframe': 'H1-D1',
                'avg_trades_per_month': 15,
                'risk_tolerance': 'medium',
                'profit_target': 'moderate_swing',
                'max_drawdown_tolerance': 0.25,
                'sharpe_minimum': 1.1,
                'profit_factor_minimum': 1.6
            },
            'Position Trading': {
                'timeframe': 'D1-W1',
                'avg_trades_per_month': 5,
                'risk_tolerance': 'low_medium',
                'profit_target': 'large_swing',
                'max_drawdown_tolerance': 0.30,
                'sharpe_minimum': 0.9,
                'profit_factor_minimum': 1.8
            },
            'Breakout': {
                'timeframe': 'H1-D1',
                'avg_trades_per_month': 20,
                'risk_tolerance': 'medium_high',
                'profit_target': 'breakout_moves',
                'max_drawdown_tolerance': 0.25,
                'sharpe_minimum': 1.2,
                'profit_factor_minimum': 1.5
            },
            'General': {
                'timeframe': 'H1',
                'avg_trades_per_month': 25,
                'risk_tolerance': 'medium',
                'profit_target': 'balanced',
                'max_drawdown_tolerance': 0.25,
                'sharpe_minimum': 1.0,
                'profit_factor_minimum': 1.5
            }
        }
        
        return characteristics.get(trading_style, characteristics['General'])
    
    def _calculate_optimal_weights(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcula pesos óptimos basados en características del estilo de trading.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Diccionario con pesos optimizados
        """
        try:
            # Analizar distribuciones de métricas
            metric_importance = self._analyze_metric_distributions(df, style_characteristics)
            
            # Calcular importancia de cada componente
            profitability_importance = self._calculate_profitability_importance(df, style_characteristics)
            risk_importance = self._calculate_risk_importance(df, style_characteristics)
            consistency_importance = self._calculate_consistency_importance(df, style_characteristics)
            ml_importance = self._calculate_ml_importance(df, style_characteristics)
            
            # Combinar importancias
            weights = {
                'profitability': profitability_importance,
                'risk': risk_importance,
                'consistency': consistency_importance,
                'extra_kpis': 0.15,  # Fijo para KPIs extra
                'ml_enhancement': ml_importance if self.enable_advanced_features else 0.0
            }
            
            # Normalizar pesos
            return self._normalize_weights(weights)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando pesos óptimos: {e}")
            return self.trading_style_weights.get('General', self.trading_style_weights['General'])
    
    def _analyze_metric_distributions(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> Dict[str, float]:
        """
        Analiza distribuciones de métricas para optimización.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Diccionario con importancia de métricas
        """
        try:
            metric_importance = {}
            
            # Analizar métricas clave
            key_metrics = ['Sharpe_Ratio', 'Profit_factor', 'Max_DD_%', 'CAGR', 'Win_Rate']
            
            for metric in key_metrics:
                if metric in df.columns:
                    values = df[metric].fillna(0)
                    
                    # Calcular estadísticas
                    mean_val = values.mean()
                    std_val = values.std()
                    skew_val = values.skew()
                    
                    # Calcular importancia basada en distribución
                    if std_val > 0:
                        # Mayor variabilidad = mayor importancia para optimización
                        importance = min(1.0, (std_val / abs(mean_val)) if mean_val != 0 else 0.5)
                        metric_importance[metric] = importance
                    else:
                        metric_importance[metric] = 0.5
            
            return metric_importance
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error analizando distribuciones: {e}")
            return {}
    
    def _calculate_profitability_importance(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> float:
        """
        Calcula importancia del componente de rentabilidad.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Importancia del componente de rentabilidad
        """
        try:
            # Factores base según estilo
            base_importance = {
                'Scalping': 0.35,
                'Day Trading': 0.40,
                'Swing Trading': 0.45,
                'Position Trading': 0.50,
                'Breakout': 0.40,
                'General': 0.40
            }
            
            style = style_characteristics.get('timeframe', 'General')
            base = base_importance.get(style, 0.40)
            
            # Ajustar según métricas de rentabilidad disponibles
            profitability_metrics = ['Profit_factor', 'CAGR', 'Net_profit']
            available_metrics = [m for m in profitability_metrics if m in df.columns]
            
            if available_metrics:
                # Calcular calidad de datos de rentabilidad
                quality_score = 0
                for metric in available_metrics:
                    values = df[metric].fillna(0)
                    if values.std() > 0:
                        quality_score += 1
                
                quality_factor = quality_score / len(available_metrics)
                adjusted_importance = base * (0.8 + 0.4 * quality_factor)
            else:
                adjusted_importance = base * 0.8
            
            return min(1.0, max(0.1, adjusted_importance))
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando importancia de rentabilidad: {e}")
            return 0.40
    
    def _calculate_risk_importance(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> float:
        """
        Calcula importancia del componente de riesgo.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Importancia del componente de riesgo
        """
        try:
            # Factores base según tolerancia al riesgo
            risk_tolerance = style_characteristics.get('risk_tolerance', 'medium')
            base_importance = {
                'high': 0.40,
                'medium_high': 0.35,
                'medium': 0.30,
                'low_medium': 0.25,
                'low': 0.20
            }
            
            base = base_importance.get(risk_tolerance, 0.30)
            
            # Ajustar según métricas de riesgo disponibles
            risk_metrics = ['Max_DD_%', 'Sharpe_Ratio', 'Sortino_Ratio', 'CalmarRatio']
            available_metrics = [m for m in risk_metrics if m in df.columns]
            
            if available_metrics:
                # Calcular calidad de datos de riesgo
                quality_score = 0
                for metric in available_metrics:
                    values = df[metric].fillna(0)
                    if values.std() > 0:
                        quality_score += 1
                
                quality_factor = quality_score / len(available_metrics)
                adjusted_importance = base * (0.8 + 0.4 * quality_factor)
            else:
                adjusted_importance = base * 0.8
            
            return min(1.0, max(0.1, adjusted_importance))
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando importancia de riesgo: {e}")
            return 0.35
    
    def _calculate_consistency_importance(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> float:
        """
        Calcula importancia del componente de consistencia.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Importancia del componente de consistencia
        """
        try:
            # Factores base según frecuencia de trading
            avg_trades = style_characteristics.get('avg_trades_per_month', 25)
            
            if avg_trades > 100:  # Scalping
                base = 0.25
            elif avg_trades > 30:  # Day Trading
                base = 0.25
            elif avg_trades > 10:  # Swing Trading
                base = 0.30
            else:  # Position Trading
                base = 0.35
            
            # Ajustar según métricas de consistencia disponibles
            consistency_metrics = ['Win_Rate', 'RecoveryFactor', 'SQN', 'Expectancy']
            available_metrics = [m for m in consistency_metrics if m in df.columns]
            
            if available_metrics:
                # Calcular calidad de datos de consistencia
                quality_score = 0
                for metric in available_metrics:
                    values = df[metric].fillna(0)
                    if values.std() > 0:
                        quality_score += 1
                
                quality_factor = quality_score / len(available_metrics)
                adjusted_importance = base * (0.8 + 0.4 * quality_factor)
            else:
                adjusted_importance = base * 0.8
            
            return min(1.0, max(0.1, adjusted_importance))
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando importancia de consistencia: {e}")
            return 0.25
    
    def _calculate_ml_importance(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> float:
        """
        Calcula importancia del componente ML.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Importancia del componente ML
        """
        if not self.enable_advanced_features:
            return 0.0
        
        try:
            # Base según complejidad del estilo
            complexity_factors = {
                'Scalping': 0.20,  # Alta complejidad
                'Day Trading': 0.18,
                'Swing Trading': 0.15,
                'Position Trading': 0.12,
                'Breakout': 0.16,
                'General': 0.15
            }
            
            style = style_characteristics.get('timeframe', 'General')
            base = complexity_factors.get(style, 0.15)
            
            # Ajustar según disponibilidad de datos para ML
            ml_metrics = ['Sharpe_Ratio', 'Profit_factor', 'Max_DD_%', 'CAGR']
            available_ml_metrics = [m for m in ml_metrics if m in df.columns]
            
            if len(available_ml_metrics) >= 3:
                quality_factor = 1.0
            elif len(available_ml_metrics) >= 2:
                quality_factor = 0.8
            else:
                quality_factor = 0.6
            
            adjusted_importance = base * quality_factor
            return min(0.25, max(0.0, adjusted_importance))
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculando importancia ML: {e}")
            return 0.15
    
    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Normaliza pesos para que sumen 1.0.
        
        Args:
            weights: Diccionario con pesos
            
        Returns:
            Diccionario con pesos normalizados
        """
        try:
            total_weight = sum(weights.values())
            
            if total_weight > 0:
                normalized_weights = {k: v / total_weight for k, v in weights.items()}
            else:
                # Pesos por defecto si la suma es 0
                normalized_weights = {
                    'profitability': 0.40,
                    'risk': 0.35,
                    'consistency': 0.25,
                    'extra_kpis': 0.15,
                    'ml_enhancement': 0.0
                }
                # Renormalizar
                total = sum(normalized_weights.values())
                normalized_weights = {k: v / total for k, v in normalized_weights.items()}
            
            return normalized_weights
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error normalizando pesos: {e}")
            return {
                'profitability': 0.40,
                'risk': 0.35,
                'consistency': 0.25,
                'extra_kpis': 0.15,
                'ml_enhancement': 0.0
            }
    
    def auto_optimize_weights_by_trading_style(self, trading_style: str, df: pd.DataFrame) -> Dict[str, float]:
        """
        Optimiza automáticamente los pesos según el estilo de trading.
        
        Args:
            trading_style: Estilo de trading
            df: DataFrame con datos
            
        Returns:
            Diccionario con pesos optimizados
        """
        if not self.enable_advanced_features:
            return self.trading_style_weights.get(trading_style, self.trading_style_weights['General'])
        
        try:
            # Obtener características del estilo
            style_characteristics = self._get_trading_style_characteristics(trading_style)
            
            # Calcular pesos óptimos
            optimal_weights = self._calculate_optimal_weights(df, style_characteristics)
            
            # Actualizar pesos en la configuración
            self.trading_style_weights[trading_style] = optimal_weights
            
            self.logger.info(f"⚖️ Pesos optimizados para {trading_style}: {optimal_weights}")
            
            return optimal_weights
            
        except Exception as e:
            self.logger.error(f"❌ Error optimizando pesos: {e}")
            return self.trading_style_weights.get(trading_style, self.trading_style_weights['General'])
    
    def auto_optimize_penalties_by_trading_style(self, trading_style: str, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Optimiza automáticamente las penalizaciones según el estilo de trading.
        
        Args:
            trading_style: Estilo de trading
            df: DataFrame con datos
            
        Returns:
            Diccionario con penalizaciones optimizadas
        """
        if not self.enable_advanced_features:
            return self.penalty_config
        
        try:
            # Obtener características del estilo
            style_characteristics = self._get_trading_style_characteristics(trading_style)
            
            # Optimizar cada tipo de penalización
            optimized_penalties = {}
            
            # Penalización por pérdidas consecutivas
            optimized_penalties['consecutive_losses'] = self._optimize_consecutive_losses_penalty(df, style_characteristics)
            
            # Penalización por estancamiento
            optimized_penalties['stagnation'] = self._optimize_stagnation_penalty(df, style_characteristics)
            
            # Penalización por duración de drawdown
            optimized_penalties['drawdown_duration'] = self._optimize_drawdown_duration_penalty(df, style_characteristics)
            
            # Penalización por exposición
            optimized_penalties['exposure'] = self._optimize_exposure_penalty(df, style_characteristics)
            
            # Penalización por porcentaje de victorias
            optimized_penalties['winning_percent'] = self._optimize_winning_percent_penalty(df, style_characteristics)
            
            # Penalizaciones avanzadas
            if self.enable_advanced_features:
                optimized_penalties['oos_robustness'] = self._optimize_oos_robustness_penalty(df, style_characteristics)
                optimized_penalties['overfitting'] = self._optimize_overfitting_penalty(df, style_characteristics)
            
            # Actualizar configuración
            self.penalty_config.update(optimized_penalties)
            
            self.logger.info(f"⚙️ Penalizaciones optimizadas para {trading_style}")
            
            return optimized_penalties
            
        except Exception as e:
            self.logger.error(f"❌ Error optimizando penalizaciones: {e}")
            return self.penalty_config
    
    def _optimize_consecutive_losses_penalty(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza penalización por pérdidas consecutivas.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Configuración optimizada
        """
        try:
            if 'Max_Consec._Losses' not in df.columns:
                return self.penalty_config['consecutive_losses']
            
            values = df['Max_Consec._Losses'].fillna(0)
            
            # Calcular umbral óptimo basado en percentiles
            threshold = values.quantile(0.75)  # 75% de las estrategias
            penalty_factor = 0.8
            
            # Ajustar según tolerancia al riesgo
            risk_tolerance = style_characteristics.get('risk_tolerance', 'medium')
            if risk_tolerance == 'high':
                threshold *= 1.2  # Más tolerante
                penalty_factor *= 0.9
            elif risk_tolerance == 'low':
                threshold *= 0.8  # Menos tolerante
                penalty_factor *= 1.1
            
            return {
                'enabled': True,
                'threshold': max(3, int(threshold) if threshold is not None else 0 if threshold is not None else 0),
                'penalty_factor': max(0.5, min(1.0, penalty_factor))
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error optimizando penalización por pérdidas consecutivas: {e}")
            return self.penalty_config['consecutive_losses']
    
    def _optimize_stagnation_penalty(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza penalización por estancamiento.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Configuración optimizada
        """
        try:
            if 'Stagnation' not in df.columns:
                return self.penalty_config['stagnation']
            
            values = df['Stagnation'].fillna(0)
            
            # Calcular umbral óptimo
            threshold = values.quantile(0.8)
            penalty_factor = 0.9
            
            # Ajustar según frecuencia de trading
            avg_trades = style_characteristics.get('avg_trades_per_month', 25)
            if avg_trades > 50:  # Alta frecuencia
                threshold *= 1.5  # Más tolerante
                penalty_factor *= 0.95
            elif avg_trades < 10:  # Baja frecuencia
                threshold *= 0.7  # Menos tolerante
                penalty_factor *= 1.05
            
            return {
                'enabled': True,
                'threshold': max(5, int(threshold) if threshold is not None else 0 if threshold is not None else 0),
                'penalty_factor': max(0.7, min(1.0, penalty_factor))
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error optimizando penalización por estancamiento: {e}")
            return self.penalty_config['stagnation']
    
    def _optimize_drawdown_duration_penalty(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza penalización por duración de drawdown.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Configuración optimizada
        """
        try:
            if 'Max_Drawdown_Duration' not in df.columns:
                return self.penalty_config['drawdown_duration']
            
            values = df['Max_Drawdown_Duration'].fillna(0)
            
            # Calcular umbral óptimo
            threshold = values.quantile(0.8)
            penalty_factor = 0.85
            
            # Ajustar según tolerancia al riesgo
            risk_tolerance = style_characteristics.get('risk_tolerance', 'medium')
            if risk_tolerance == 'high':
                threshold *= 1.3
                penalty_factor *= 0.9
            elif risk_tolerance == 'low':
                threshold *= 0.7
                penalty_factor *= 1.1
            
            return {
                'enabled': True,
                'threshold': max(10, int(threshold) if threshold is not None else 0 if threshold is not None else 0),
                'penalty_factor': max(0.6, min(1.0, penalty_factor))
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error optimizando penalización por duración de drawdown: {e}")
            return self.penalty_config['drawdown_duration']
    
    def _optimize_exposure_penalty(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza penalización por exposición.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Configuración optimizada
        """
        try:
            if 'Exposure' not in df.columns:
                return self.penalty_config['exposure']
            
            values = df['Exposure'].fillna(0.5)
            
            # Calcular rangos óptimos
            min_threshold = values.quantile(0.1)
            max_threshold = values.quantile(0.9)
            penalty_factor = 0.95
            
            # Ajustar según estilo de trading
            timeframe = style_characteristics.get('timeframe', 'H1')
            if 'M1' in timeframe or 'M5' in timeframe:  # Scalping
                min_threshold = max(0.05, min_threshold * 0.8)
                max_threshold = min(0.95, max_threshold * 1.2)
            elif 'D1' in timeframe or 'W1' in timeframe:  # Position Trading
                min_threshold = max(0.1, min_threshold * 1.2)
                max_threshold = min(0.9, max_threshold * 0.8)
            
            return {
                'enabled': True,
                'min_threshold': max(0.05, min(0.4, min_threshold)),
                'max_threshold': min(0.95, max(0.6, max_threshold)),
                'penalty_factor': max(0.8, min(1.0, penalty_factor))
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error optimizando penalización por exposición: {e}")
            return self.penalty_config['exposure']
    
    def _optimize_winning_percent_penalty(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza penalización por porcentaje de victorias.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Configuración optimizada
        """
        try:
            if 'Winning_Percent' not in df.columns:
                return self.penalty_config['winning_percent']
            
            values = df['Winning_Percent'].fillna(50) / 100
            
            # Calcular umbral óptimo
            min_threshold = values.quantile(0.2)  # 20% inferior
            penalty_factor = 0.9
            
            # Ajustar según estilo de trading
            timeframe = style_characteristics.get('timeframe', 'H1')
            if 'M1' in timeframe or 'M5' in timeframe:  # Scalping
                min_threshold = max(0.2, min_threshold * 0.8)  # Más tolerante
                penalty_factor *= 0.95
            elif 'D1' in timeframe or 'W1' in timeframe:  # Position Trading
                min_threshold = max(0.3, min_threshold * 1.2)  # Menos tolerante
                penalty_factor *= 1.05
            
            return {
                'enabled': True,
                'min_threshold': max(0.2, min(0.5, min_threshold)),
                'penalty_factor': max(0.7, min(1.0, penalty_factor))
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error optimizando penalización por porcentaje de victorias: {e}")
            return self.penalty_config['winning_percent']
    
    def _optimize_oos_robustness_penalty(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza penalización por robustez OOS.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Configuración optimizada
        """
        try:
            # Calcular correlación IS/OOS si está disponible
            is_oos_columns = [col for col in df.columns if '(IS)' in col and '(OOS)' in col.replace('(IS)', '')]
            
            min_correlation = 0.5  # Valor por defecto
            if is_oos_columns:
                # Calcular correlaciones promedio
                correlations = []
                for col in is_oos_columns:
                    is_col = col
                    oos_col = col.replace('(IS)', '(OOS)')
                    if oos_col in df.columns:
                        corr = ensure_series(is_col).corr(ensure_series(oos_col))
                        if not pd.isna(corr):
                            correlations.append(corr)
                
                if correlations:
                    avg_correlation = np.mean(correlations)
                    min_correlation = max(0.3, min(0.7, float(avg_correlation * 0.8)))

            penalty_factor = 0.7
            
            # Ajustar según complejidad del estilo
            timeframe = style_characteristics.get('timeframe', 'H1')
            if 'M1' in timeframe or 'M5' in timeframe:  # Alta complejidad
                min_correlation *= 0.9  # Más tolerante
                penalty_factor *= 0.95
            
            return {
                'enabled': True,
                'min_correlation': max(0.3, min(0.7, min_correlation)),
                'penalty_factor': max(0.5, min(1.0, penalty_factor))
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error optimizando penalización por robustez OOS: {e}")
            return self.penalty_config['oos_robustness']
    
    def _optimize_overfitting_penalty(self, df: pd.DataFrame, style_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza penalización por sobreajuste.
        
        Args:
            df: DataFrame con datos
            style_characteristics: Características del estilo de trading
            
        Returns:
            Configuración optimizada
        """
        try:
            # Calcular contaminación basada en complejidad del estilo
            timeframe = style_characteristics.get('timeframe', 'H1')
            
            if 'M1' in timeframe or 'M5' in timeframe:  # Alta complejidad
                contamination = 0.15
            elif 'H1' in timeframe:  # Complejidad media
                contamination = 0.10
            else:  # Baja complejidad
                contamination = 0.05
            
            penalty_factor = 0.6
            
            # Ajustar según tolerancia al riesgo
            risk_tolerance = style_characteristics.get('risk_tolerance', 'medium')
            if risk_tolerance == 'high':
                contamination *= 1.2  # Más tolerante
                penalty_factor *= 0.9
            elif risk_tolerance == 'low':
                contamination *= 0.8  # Menos tolerante
                penalty_factor *= 1.1
            
            return {
                'enabled': True,
                'contamination': max(0.05, min(0.2, contamination)),
                'penalty_factor': max(0.4, min(1.0, penalty_factor))
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error optimizando penalización por sobreajuste: {e}")
            return self.penalty_config['overfitting']
    
    def update_trading_style_from_gui(self, trading_style: str, df: pd.DataFrame) -> None:
        """
        Actualiza configuración desde la GUI.
        
        Args:
            trading_style: Estilo de trading seleccionado
            df: DataFrame con datos
        """
        try:
            # Actualizar configuración
            getattr(self, 'config', None)_manager.current_config['trading_style'] = trading_style
            
            # Optimizar pesos automáticamente
            optimized_weights = self.auto_optimize_weights_by_trading_style(trading_style, df)
            
            # Optimizar penalizaciones automáticamente
            optimized_penalties = self.auto_optimize_penalties_by_trading_style(trading_style, df)
            
            self.logger.info(f"🔄 Configuración actualizada desde GUI para {trading_style}")
            
        except Exception as e:
            self.logger.error(f"❌ Error actualizando configuración desde GUI: {e}")
    
    def get_optimization_report(self, trading_style: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Genera reporte completo de optimización.
        
        Args:
            trading_style: Estilo de trading
            df: DataFrame con datos
            
        Returns:
            Diccionario con reporte de optimización
        """
        if not self.enable_advanced_features:
            return {
                'status': 'Funcionalidad avanzada no habilitada',
                'trading_style': trading_style,
                'data_shape': df.shape,
                'optimization_status': 'disabled'
            }
        
        try:
            # Obtener características del estilo
            style_characteristics = self._get_trading_style_characteristics(trading_style)
            
            # Optimizar pesos
            optimized_weights = self.auto_optimize_weights_by_trading_style(trading_style, df)
            
            # Optimizar penalizaciones
            optimized_penalties = self.auto_optimize_penalties_by_trading_style(trading_style, df)
            
            # Generar reporte
            report = {
                'trading_style': trading_style,
                'data_shape': df.shape,
                'optimization_status': 'completed',
                'style_characteristics': style_characteristics,
                'optimized_weights': optimized_weights,
                'optimized_penalties': optimized_penalties,
                'timestamp': pd.Timestamp.now().isoformat(),
                'ml_components_available': ML_AVAILABLE,
                'advanced_features_enabled': self.enable_advanced_features
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generando reporte de optimización: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'trading_style': trading_style,
                'data_shape': df.shape,
                'optimization_status': 'failed'
            } 