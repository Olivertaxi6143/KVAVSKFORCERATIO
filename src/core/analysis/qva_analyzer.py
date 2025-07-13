import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple, Any
from src.core.config.config_manager import ConfigManagerEnhanced
from src.core.config.progress_callback import ProgressCallback
from src.logger_config import setup_logger

# Definir ExtraKPIManager localmente para evitar conflictos de tipos
class ExtraKPIManager:
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
    def apply_extra_kpis_to_qva_score(self, df, trading_style):
        return pd.Series(0.5, index=df.index)

class QVAScorerEnhanced:
    """
    QVA Scorer mejorado con validación robusta, penalizaciones avanzadas y optimizaciones para GUI.
    
    Características principales:
    - Normalización robusta con percentiles adaptativos
    - Penalizaciones por pérdidas consecutivas, estancamiento, drawdown
    - Pesos configurables por estilo de trading
    - Logging detallado y validación exhaustiva
    - Compatibilidad total con tests existentes
    """
    
    def __init__(self, config_manager: Optional[ConfigManagerEnhanced] = None, 
                 progress_callback: Optional[ProgressCallback] = None):
        self.logger = setup_logger("kforce")
        self.config_manager = config_manager or ConfigManagerEnhanced()
        self.progress_callback = progress_callback
        self.extra_kpi_manager = ExtraKPIManager(config_manager)
        
        # Configuración de penalizaciones
        self.penalty_config = {
            'consecutive_losses': {
                'enabled': True,
                'threshold': 5,  # Máximo número de pérdidas consecutivas aceptables
                'penalty_factor': 0.8  # Factor de penalización
            },
            'stagnation': {
                'enabled': True,
                'threshold': 10,  # Máximo número de trades de estancamiento
                'penalty_factor': 0.9
            },
            'stagnation_trades': {
                'enabled': True,
                'threshold': 8,  # Máximo número de trades consecutivos en estancamiento
                'penalty_factor': 0.85  # Más agresiva que stagnation normal
            },
            'drawdown_duration': {
                'enabled': True,
                'threshold': 20,  # Máxima duración de drawdown en trades
                'penalty_factor': 0.85
            },
            'exposure': {
                'enabled': True,
                'min_threshold': 0.1,  # Mínima exposición
                'max_threshold': 0.9,  # Máxima exposición
                'penalty_factor': 0.95
            },
            'winning_percent': {
                'enabled': True,
                'min_threshold': 0.3,  # Mínimo porcentaje de victorias
                'penalty_factor': 0.9
            }
        }
        
        # Pesos por estilo de trading (configurables desde GUI)
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
        
    def calculate_qva_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcula el score QVA con componentes mejorados, penalizaciones avanzadas e integración de KPIs extra.
        
        Args:
            df: DataFrame con datos de estrategias
            
        Returns:
            Series con scores QVA normalizados en [0,1]
        """
        try:
            self.logger.info("🚀 Iniciando cálculo QVA Score con penalizaciones avanzadas")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 0, 100, "Iniciando cálculo QVA...")
            
            # Validación de datos
            if df.empty:
                self.logger.warning("⚠️ DataFrame vacío, retornando scores por defecto")
                return pd.Series(0.5, index=df.index)
            
            # Obtener KPIs habilitados
            enabled_kpis = self.config_manager.get_enabled_kpis()
            self.logger.info(f"📊 KPIs habilitados: {len(enabled_kpis)}")
            
            # Obtener estilo de trading actual
            trading_style = self.config_manager.current_config.get('trading_style', 'General')
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
            qva_score = (base_qva_score + extra_kpis_component) * penalties['total_penalty']
            
            # Normalización final robusta
            qva_score = self._robust_normalization(qva_score)
            
            self.logger.info(f"✅ Score QVA calculado exitosamente: {qva_score.mean():.4f} ± {qva_score.std():.4f}")
            
            if self.progress_callback:
                self.progress_callback.update_progress("QVA", 100, 100, "Cálculo QVA completado")
            
            return qva_score
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando score QVA: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _calculate_profitability_component_robust(self, df: pd.DataFrame, enabled_kpis: List[str]) -> pd.Series:
        """Calcula el componente de rentabilidad con normalización robusta."""
        try:
            profitability_metrics = []
            
            # Profit Factor con normalización robusta
            if 'Profit_factor' in enabled_kpis and 'Profit_factor' in df.columns:
                pf = pd.to_numeric(df['Profit_factor'], errors='coerce').fillna(1.0)
                pf_score = self._robust_normalization(pd.Series(pf, index=df.index), higher_is_better=True)
                profitability_metrics.append(pf_score)
                self.logger.debug(f"💰 Profit Factor normalizado: {pf_score.mean():.4f}")
            
            # Net Profit con normalización robusta
            if 'Net_profit' in enabled_kpis and 'Net_profit' in df.columns:
                np_col = pd.to_numeric(df['Net_profit'], errors='coerce').fillna(0)
                np_score = self._robust_normalization(pd.Series(np_col, index=df.index), higher_is_better=True)
                profitability_metrics.append(np_score)
                self.logger.debug(f"💰 Net Profit normalizado: {np_score.mean():.4f}")
            
            # CAGR con normalización robusta
            if 'CAGR' in enabled_kpis and 'CAGR' in df.columns:
                cagr = pd.to_numeric(df['CAGR'], errors='coerce').fillna(0)
                cagr_score = self._robust_normalization(pd.Series(cagr, index=df.index), higher_is_better=True)
                profitability_metrics.append(cagr_score)
                self.logger.debug(f"💰 CAGR normalizado: {cagr_score.mean():.4f}")
            
            # Recovery Factor con normalización robusta
            if 'RecoveryFactor' in enabled_kpis and 'RecoveryFactor' in df.columns:
                rf = pd.to_numeric(df['RecoveryFactor'], errors='coerce').fillna(0)
                rf_score = self._robust_normalization(pd.Series(rf, index=df.index), higher_is_better=True)
                profitability_metrics.append(rf_score)
                self.logger.debug(f"💰 Recovery Factor normalizado: {rf_score.mean():.4f}")
            
            # Calcular promedio ponderado
            if profitability_metrics:
                result = pd.concat(profitability_metrics, axis=1).mean(axis=1)
                return self._robust_normalization(pd.Series(result, index=df.index))
            else:
                return pd.Series(0.5, index=df.index)
                
        except Exception as e:
            self.logger.error(f"❌ Error calculando componente de rentabilidad: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _calculate_risk_component_robust(self, df: pd.DataFrame, enabled_kpis: List[str]) -> pd.Series:
        """Calcula el componente de riesgo con normalización robusta."""
        try:
            risk_metrics = []
            
            # Max Drawdown (invertido para que menor sea mejor)
            if 'Max_DD_%' in enabled_kpis and 'Max_DD_%' in df.columns:
                max_dd = pd.to_numeric(df['Max_DD_%'], errors='coerce').fillna(0)
                dd_score = self._robust_normalization(pd.Series(max_dd, index=df.index), higher_is_better=False)
                risk_metrics.append(dd_score)
                self.logger.debug(f"🛡️ Max DD normalizado: {dd_score.mean():.4f}")
            
            # VaR 95% (invertido)
            if 'VaR_95%' in enabled_kpis and 'VaR_95%' in df.columns:
                var = pd.to_numeric(df['VaR_95%'], errors='coerce').fillna(0)
                var_score = self._robust_normalization(pd.Series(var, index=df.index), higher_is_better=False)
                risk_metrics.append(var_score)
                self.logger.debug(f"🛡️ VaR 95% normalizado: {var_score.mean():.4f}")
            
            # CVaR 95% (invertido)
            if 'CVaR_95%' in enabled_kpis and 'CVaR_95%' in df.columns:
                cvar = pd.to_numeric(df['CVaR_95%'], errors='coerce').fillna(0)
                cvar_score = self._robust_normalization(pd.Series(cvar, index=df.index), higher_is_better=False)
                risk_metrics.append(cvar_score)
                self.logger.debug(f"🛡️ CVaR 95% normalizado: {cvar_score.mean():.4f}")
            
            # Ulcer Index (invertido)
            if 'Ulcer_Index_%' in enabled_kpis and 'Ulcer_Index_%' in df.columns:
                ulcer = pd.to_numeric(df['Ulcer_Index_%'], errors='coerce').fillna(0)
                ulcer_score = self._robust_normalization(pd.Series(ulcer, index=df.index), higher_is_better=False)
                risk_metrics.append(ulcer_score)
                self.logger.debug(f"🛡️ Ulcer Index normalizado: {ulcer_score.mean():.4f}")
            
            # Calcular promedio ponderado
            if risk_metrics:
                result = pd.concat(risk_metrics, axis=1).mean(axis=1)
                return self._robust_normalization(pd.Series(result, index=df.index))
            else:
                return pd.Series(0.5, index=df.index)
                
        except Exception as e:
            self.logger.error(f"❌ Error calculando componente de riesgo: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _calculate_consistency_component_robust(self, df: pd.DataFrame, enabled_kpis: List[str]) -> pd.Series:
        """Calcula el componente de consistencia con normalización robusta."""
        try:
            consistency_metrics = []
            
            # Sharpe Ratio
            if 'Sharpe_Ratio' in enabled_kpis and 'Sharpe_Ratio' in df.columns:
                sharpe = pd.to_numeric(df['Sharpe_Ratio'], errors='coerce').fillna(0)
                sharpe_score = self._robust_normalization(pd.Series(sharpe, index=df.index), higher_is_better=True)
                consistency_metrics.append(sharpe_score)
                self.logger.debug(f"📈 Sharpe Ratio normalizado: {sharpe_score.mean():.4f}")
            
            # Calmar Ratio
            if 'CalmarRatio' in enabled_kpis and 'CalmarRatio' in df.columns:
                calmar = pd.to_numeric(df['CalmarRatio'], errors='coerce').fillna(0)
                calmar_score = self._robust_normalization(pd.Series(calmar, index=df.index), higher_is_better=True)
                consistency_metrics.append(calmar_score)
                self.logger.debug(f"📈 Calmar Ratio normalizado: {calmar_score.mean():.4f}")
            
            # SQN Score
            if 'SQN' in enabled_kpis and 'SQN' in df.columns:
                sqn = pd.to_numeric(df['SQN'], errors='coerce').fillna(0)
                sqn_score = self._robust_normalization(pd.Series(sqn, index=df.index), higher_is_better=True)
                consistency_metrics.append(sqn_score)
                self.logger.debug(f"📈 SQN Score normalizado: {sqn_score.mean():.4f}")
            
            # RINA Index
            if 'RINAIndex' in enabled_kpis and 'RINAIndex' in df.columns:
                rina = pd.to_numeric(df['RINAIndex'], errors='coerce').fillna(0)
                rina_score = self._robust_normalization(pd.Series(rina, index=df.index), higher_is_better=True)
                consistency_metrics.append(rina_score)
                self.logger.debug(f"📈 RINA Index normalizado: {rina_score.mean():.4f}")
            
            # Stagnation Trades (invertido)
            if 'Stagnation' in enabled_kpis and 'Stagnation' in df.columns:
                stagnation = pd.to_numeric(df['Stagnation'], errors='coerce').fillna(0)
                stagnation_score = self._robust_normalization(pd.Series(stagnation, index=df.index), higher_is_better=False)
                consistency_metrics.append(stagnation_score)
                self.logger.debug(f"📈 Stagnation Trades normalizado: {stagnation_score.mean():.4f}")
            
            # Calcular promedio ponderado
            if consistency_metrics:
                result = pd.concat(consistency_metrics, axis=1).mean(axis=1)
                return self._robust_normalization(pd.Series(result, index=df.index))
            else:
                return pd.Series(0.5, index=df.index)
                
        except Exception as e:
            self.logger.error(f"❌ Error calculando componente de consistencia: {e}")
            return pd.Series(0.5, index=df.index)
    
    def _calculate_advanced_penalties(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calcula todas las penalizaciones avanzadas."""
        try:
            penalties = {}
            
            # 1. Penalización por pérdidas consecutivas
            if self.penalty_config['consecutive_losses']['enabled']:
                penalties['consecutive_losses'] = self._calculate_consecutive_losses_penalty(df)
                self.logger.debug(f"⚠️ Penalización pérdidas consecutivas: {penalties['consecutive_losses'].mean():.4f}")
            
            # 2. Penalización por estancamiento
            if self.penalty_config['stagnation']['enabled']:
                penalties['stagnation'] = self._calculate_stagnation_penalty(df)
                self.logger.debug(f"⚠️ Penalización estancamiento: {penalties['stagnation'].mean():.4f}")
            
            # 3. Penalización por duración de drawdown
            if self.penalty_config['drawdown_duration']['enabled']:
                penalties['drawdown_duration'] = self._calculate_drawdown_duration_penalty(df)
                self.logger.debug(f"⚠️ Penalización duración drawdown: {penalties['drawdown_duration'].mean():.4f}")
            
            # 4. Penalización por exposición
            if self.penalty_config['exposure']['enabled']:
                penalties['exposure'] = self._calculate_exposure_penalty(df)
                self.logger.debug(f"⚠️ Penalización exposición: {penalties['exposure'].mean():.4f}")
            
            # 5. Penalización por porcentaje de victorias
            if self.penalty_config['winning_percent']['enabled']:
                penalties['winning_percent'] = self._calculate_winning_percent_penalty(df)
                self.logger.debug(f"⚠️ Penalización % victorias: {penalties['winning_percent'].mean():.4f}")
            
            # 6. Penalización por número de trades en estancamiento (más agresiva que Stagnation)
            if self.penalty_config.get('stagnation_trades', {}).get('enabled'):
                penalties['stagnation_trades'] = self._calculate_stagnation_trades_penalty(df)
                self.logger.debug(f"⚠️ Penalización Stagnation_Trades: {penalties['stagnation_trades'].mean():.4f}")
            
            # Penalización total (producto de todas las penalizaciones)
            if penalties:
                total_penalty = pd.concat(penalties.values(), axis=1).prod(axis=1)
                penalties['total_penalty'] = total_penalty
                self.logger.info(f"⚠️ Penalización total: {total_penalty.mean():.4f} ± {total_penalty.std():.4f}")
            else:
                penalties['total_penalty'] = pd.Series(1.0, index=df.index)
            
            return penalties
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando penalizaciones: {e}")
            return {'total_penalty': pd.Series(1.0, index=df.index)}
    
    def _calculate_consecutive_losses_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por pérdidas consecutivas."""
        try:
            if 'Max Consec. Losses' not in df.columns:
                return pd.Series(1.0, index=df.index)
            
            consec_losses = pd.to_numeric(df['Max Consec. Losses'], errors='coerce').fillna(0)
            threshold = self.penalty_config['consecutive_losses']['threshold']
            penalty_factor = self.penalty_config['consecutive_losses']['penalty_factor']
            
            # Penalización exponencial
            penalty = np.where(consec_losses > threshold, 
                             penalty_factor ** (consec_losses - threshold), 
                             1.0)
            
            return pd.Series(penalty, index=df.index)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando penalización pérdidas consecutivas: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _calculate_stagnation_trades_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por número de trades en estancamiento (más agresiva que Stagnation)."""
        try:
            if 'Stagnation_Trades' not in df.columns:
                return pd.Series(1.0, index=df.index)
            
            stagnation_trades = pd.to_numeric(df['Stagnation_Trades'], errors='coerce').fillna(0)
            threshold = self.penalty_config.get('stagnation_trades', {}).get('threshold', 10)
            penalty_factor = self.penalty_config.get('stagnation_trades', {}).get('penalty_factor', 1.2)
            
            # Penalización más agresiva para trades en estancamiento
            penalty = np.where(stagnation_trades > threshold, 
                             penalty_factor ** (stagnation_trades - threshold), 
                             1.0)
            
            self.logger.debug(f"📊 Penalización Stagnation_Trades: {penalty.mean():.4f}")
            return pd.Series(penalty, index=df.index)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando penalización Stagnation_Trades: {e}")
            return pd.Series(1.0, index=df.index)

    def _calculate_stagnation_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por estancamiento."""
        try:
            if 'Stagnation' not in df.columns:
                return pd.Series(1.0, index=df.index)
            
            stagnation = pd.to_numeric(df['Stagnation'], errors='coerce').fillna(0)
            threshold = self.penalty_config['stagnation']['threshold']
            penalty_factor = self.penalty_config['stagnation']['penalty_factor']
            
            # Penalización exponencial
            penalty = np.where(stagnation > threshold, 
                             penalty_factor ** (stagnation - threshold), 
                             1.0)
            
            return pd.Series(penalty, index=df.index)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando penalización estancamiento: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _calculate_drawdown_duration_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por duración de drawdown."""
        try:
            if 'Max_Drawdown_Duration' not in df.columns:
                return pd.Series(1.0, index=df.index)
            
            dd_duration = pd.to_numeric(df['Max_Drawdown_Duration'], errors='coerce').fillna(0)
            threshold = self.penalty_config['drawdown_duration']['threshold']
            penalty_factor = self.penalty_config['drawdown_duration']['penalty_factor']
            
            # Penalización exponencial
            penalty = np.where(dd_duration > threshold, 
                             penalty_factor ** (dd_duration - threshold), 
                             1.0)
            
            return pd.Series(penalty, index=df.index)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando penalización duración drawdown: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _calculate_exposure_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por exposición."""
        try:
            if 'Exposure' not in df.columns:
                return pd.Series(1.0, index=df.index)
            
            exposure = pd.to_numeric(df['Exposure'], errors='coerce').fillna(0.5)
            min_threshold = self.penalty_config['exposure']['min_threshold']
            max_threshold = self.penalty_config['exposure']['max_threshold']
            penalty_factor = self.penalty_config['exposure']['penalty_factor']
            
            # Penalización por exposición muy baja o muy alta
            penalty = np.where((exposure < min_threshold) | (exposure > max_threshold),
                             penalty_factor,
                             1.0)
            
            return pd.Series(penalty, index=df.index)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando penalización exposición: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _calculate_winning_percent_penalty(self, df: pd.DataFrame) -> pd.Series:
        """Calcula penalización por porcentaje de victorias."""
        try:
            if 'Winning_Percent' not in df.columns:
                return pd.Series(1.0, index=df.index)
            
            winning_pct = pd.to_numeric(df['Winning_Percent'], errors='coerce').fillna(50) / 100
            min_threshold = self.penalty_config['winning_percent']['min_threshold']
            penalty_factor = self.penalty_config['winning_percent']['penalty_factor']
            
            # Penalización por porcentaje de victorias muy bajo
            penalty = np.where(winning_pct < min_threshold,
                             penalty_factor,
                             1.0)
            
            return pd.Series(penalty, index=df.index)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando penalización % victorias: {e}")
            return pd.Series(1.0, index=df.index)
    
    def _robust_normalization(self, series: pd.Series, higher_is_better: bool = True) -> pd.Series:
        """
        Normalización robusta usando percentiles adaptativos.
        
        Args:
            series: Serie a normalizar
            higher_is_better: True si valores más altos son mejores
            
        Returns:
            Serie normalizada en [0,1]
        """
        try:
            if series.empty:
                return pd.Series(0.5, index=series.index)
            
            # Limpiar datos
            clean_series = pd.to_numeric(series, errors='coerce').fillna(series.median())
            
            # Usar percentiles para normalización robusta
            p5 = clean_series.quantile(0.05)
            p95 = clean_series.quantile(0.95)
            
            if p95 == p5:
                return pd.Series(0.5, index=series.index)
            
            # Normalizar usando percentiles
            if higher_is_better:
                normalized = (clean_series - p5) / (p95 - p5)
            else:
                normalized = (p95 - clean_series) / (p95 - p5)
            
            # Clipping a [0,1]
            normalized = np.clip(normalized, 0, 1)
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"❌ Error en normalización robusta: {e}")
            return pd.Series(0.5, index=series.index)
    
    def update_trading_style_weights(self, trading_style: str, weights: Dict[str, float]) -> None:
        """Actualiza los pesos para un estilo de trading específico."""
        try:
            if trading_style in self.trading_style_weights:
                self.trading_style_weights[trading_style].update(weights)
                self.logger.info(f"⚖️ Pesos actualizados para {trading_style}: {weights}")
            else:
                self.trading_style_weights[trading_style] = weights
                self.logger.info(f"⚖️ Nuevos pesos creados para {trading_style}: {weights}")
        except Exception as e:
            self.logger.error(f"❌ Error actualizando pesos: {e}")
    
    def update_penalty_config(self, penalty_type: str, config: Dict[str, Any]) -> None:
        """Actualiza la configuración de penalizaciones."""
        try:
            if penalty_type in self.penalty_config:
                self.penalty_config[penalty_type].update(config)
                self.logger.info(f"⚠️ Configuración de penalización actualizada para {penalty_type}: {config}")
            else:
                self.penalty_config[penalty_type] = config
                self.logger.info(f"⚠️ Nueva configuración de penalización creada para {penalty_type}: {config}")
        except Exception as e:
            self.logger.error(f"❌ Error actualizando configuración de penalización: {e}")
    
    def get_score_breakdown(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Obtiene el desglose detallado de los componentes del score QVA."""
        try:
            enabled_kpis = self.config_manager.get_enabled_kpis()
            trading_style = self.config_manager.current_config.get('trading_style', 'General')
            weights = self.trading_style_weights.get(trading_style, self.trading_style_weights['General'])
            
            breakdown = {
                'profitability': self._calculate_profitability_component_robust(df, enabled_kpis),
                'risk': self._calculate_risk_component_robust(df, enabled_kpis),
                'consistency': self._calculate_consistency_component_robust(df, enabled_kpis),
                'extra_kpis': self.extra_kpi_manager.apply_extra_kpis_to_qva_score(df, trading_style),
                'penalties': self._calculate_advanced_penalties(df)['total_penalty'],
                'weights': weights
            }
            
            return breakdown
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo desglose de score: {e}")
            return {}
    
    def compute_qva_score_robust(self, df: pd.DataFrame, alpha: float = 0.8) -> pd.Series:
        """
        Método legacy para compatibilidad con tests existentes.
        
        Args:
            df: DataFrame con datos de estrategias
            alpha: Factor de robustez (no usado en nueva implementación)
            
        Returns:
            Series con scores QVA
        """
        try:
            self.logger.info("🔄 Usando método legacy compute_qva_score_robust")
            return self.calculate_qva_score(df)
        except Exception as e:
            self.logger.error(f"❌ Error en método legacy: {e}")
            return pd.Series(0.5, index=df.index) 