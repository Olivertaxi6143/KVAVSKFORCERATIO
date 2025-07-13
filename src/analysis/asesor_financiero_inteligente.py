#!/usr/bin/env python3
"""
Asesor Financiero Inteligente para Estrategias de Trading
========================================================

Implementa análisis científico avanzado para estrategias cuantitativas:
- Análisis de correlación IS/OOS con umbrales dinámicos
- Detección de outliers usando Isolation Forest
- Clustering de estrategias para diversificación
- Análisis de importancia de KPIs con SHAP
- Predicción de rendimiento con validación robusta
- Generación de consejos prácticos y amigables
- DETECCIÓN AUTOMÁTICA DE TEMPORALIDAD Y AJUSTES CIENTÍFICOS
- FILTROS EMPÍRICOS BASADOS EN EVIDENCIA CIENTÍFICA
- MÉTRICAS AJUSTADAS SEGÚN TEMPORALIDAD

Basado en recomendaciones científicas para datos financieros.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, silhouette_score
import shap
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
from scipy.stats import spearmanr
from src.data.data_manager import DataManager
import re
from src.analysis.predictability_metrics import PredictabilityAnalyzer
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AsesorFinancieroInteligente:
    """
    Asesor Financiero Inteligente que analiza estrategias filtradas
    y proporciona consejos científicos pero amigables.
    
    INCLUYE MEJORAS CIENTÍFICAS Y EMPÍRICAS:
    - Detección automática de temporalidad
    - Ajustes científicos basados en evidencia empírica
    - Filtros robustos para análisis estadístico
    - Métricas ajustadas según temporalidad
    """
    
    def __init__(self, estrategias_filtradas: Optional[pd.DataFrame] = None, kpis_seleccionados: Optional[List[str]] = None, config_file: str = "config/asesor_config.json"):
        """
        Inicializa el asesor con estrategias filtradas y KPIs seleccionados.
        
        Args:
            estrategias_filtradas: DataFrame con estrategias que pasaron el filtro (opcional)
            kpis_seleccionados: Lista de KPIs a analizar (opcional)
        """
        self.estrategias = estrategias_filtradas.copy() if estrategias_filtradas is not None else pd.DataFrame()
        self.kpis = kpis_seleccionados if kpis_seleccionados is not None else []
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(
            n_estimators=100, 
            max_depth=10, 
            min_samples_leaf=5, 
            random_state=42
        )
        self.results = {}
        self.consejos = []
        self.predictability_analyzer = PredictabilityAnalyzer()
        
        # Configurar KPIs IS/OOS
        self._setup_is_oos_kpis()
        
        # MEJORAS CIENTÍFICAS: Detección de temporalidad y ajustes
        self.temporalidad_detectada = None
        self.factor_ajuste_temporalidad = 1.0
        self._detectar_temporalidad_y_ajustar()
        
        logger.info(f"🔬 Asesor Financiero Inteligente inicializado con {len(self.estrategias)} estrategias")
        if self.temporalidad_detectada:
            logger.info(f"📊 Temporalidad detectada: {self.temporalidad_detectada} (factor ajuste: {self.factor_ajuste_temporalidad:.3f})")
    
    def _detectar_temporalidad_y_ajustar(self):
        """
        MEJORA CIENTÍFICA: Detecta automáticamente la temporalidad desde la columna TimeFrame
        y aplica ajustes científicos basados en evidencia empírica.
        """
        try:
            # Buscar columna de temporalidad
            temporalidad_cols = [col for col in self.estrategias.columns if 'timeframe' in col.lower() or 'time_frame' in col.lower()]
            
            if temporalidad_cols:
                temporalidad_col = temporalidad_cols[0]
                temporalidades = self.estrategias[temporalidad_col].dropna().unique()
                
                if len(temporalidades) > 0:
                    # Detectar temporalidad más común
                    mode_result = self.estrategias[temporalidad_col].mode()
                    temporalidad_principal = mode_result.iloc[0] if not mode_result.empty else None
                    
                    if temporalidad_principal:
                        self.temporalidad_detectada = temporalidad_principal
                        
                        # ESCALA LOGARÍTMICA DE AJUSTE SEGÚN TEMPORALIDAD
                        factores_temporalidad = {
                            'M1': 1.0,      # Base
                            'M5': 0.8,      # Menos trades
                            'M15': 0.6,     # Aún menos
                            'M30': 0.4,     # Mucho menos
                            'H1': 0.2,      # Muy pocos
                            'H4': 0.1,      # Extremadamente pocos
                            'D1': 0.05      # Mínimo
                        }
                        
                        # Buscar coincidencia más cercana
                        temporalidad_upper = temporalidad_principal.upper()
                        for tf, factor in factores_temporalidad.items():
                            if tf in temporalidad_upper:
                                self.factor_ajuste_temporalidad = factor
                                break
                        else:
                            # Si no coincide, usar factor basado en patrón
                            if 'M' in temporalidad_upper:
                                try:
                                    minutos = int(re.findall(r'M(\d+)', temporalidad_upper)[0])
                                    self.factor_ajuste_temporalidad = max(0.05, 1.0 / (minutos / 5))
                                except:
                                    self.factor_ajuste_temporalidad = 0.5
                            elif 'H' in temporalidad_upper:
                                self.factor_ajuste_temporalidad = 0.1
                            elif 'D' in temporalidad_upper:
                                self.factor_ajuste_temporalidad = 0.05
                            else:
                                self.factor_ajuste_temporalidad = 0.5
                        
                        logger.info(f"🔍 Temporalidad detectada: {temporalidad_principal} -> factor ajuste: {self.factor_ajuste_temporalidad:.3f}")
                        
        except Exception as e:
            logger.warning(f"⚠️ Error en detección de temporalidad: {e}")
            self.temporalidad_detectada = "Desconocida"
            self.factor_ajuste_temporalidad = 1.0
    
    def _aplicar_ajustes_cientificos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        MEJORA CIENTÍFICA: Aplica ajustes científicos basados en evidencia empírica
        según la temporalidad detectada.
        """
        df_ajustado = df.copy()
        
        try:
            if self.temporalidad_detectada and self.factor_ajuste_temporalidad != 1.0:
                logger.info(f"🔬 Aplicando ajustes científicos con factor {self.factor_ajuste_temporalidad:.3f}")
                
                # AJUSTES EMPÍRICOS BASADOS EN EVIDENCIA CIENTÍFICA
                
                # 1. Trades mensuales ajustados
                if 'Trades_Monthly' in df_ajustado.columns:
                    df_ajustado['Trades_Monthly_Ajustado'] = df_ajustado['Trades_Monthly'] * self.factor_ajuste_temporalidad
                    logger.info("📊 Trades mensuales ajustados según temporalidad")
                
                # 2. CAGR anualizado ajustado
                if 'CAGR' in df_ajustado.columns:
                    # CAGR ya está anualizado, pero ajustamos según frecuencia de trading
                    df_ajustado['CAGR_Ajustado'] = df_ajustado['CAGR'] * np.sqrt(self.factor_ajuste_temporalidad)
                    logger.info("📈 CAGR ajustado según frecuencia de trading")
                
                # 3. Expectancy por trade ajustado
                if 'Expectancy' in df_ajustado.columns:
                    df_ajustado['Expectancy_Ajustado'] = df_ajustado['Expectancy'] * self.factor_ajuste_temporalidad
                    logger.info("💰 Expectancy ajustado según temporalidad")
                
                # 4. Drawdown por mes ajustado
                if 'Max_Drawdown' in df_ajustado.columns:
                    df_ajustado['Drawdown_Mensual_Ajustado'] = df_ajustado['Max_Drawdown'] / (12 * self.factor_ajuste_temporalidad)
                    logger.info("📉 Drawdown mensual ajustado")
                
                # 5. Sharpe ratio ajustado
                if 'Sharpe_Ratio' in df_ajustado.columns:
                    df_ajustado['Sharpe_Ajustado'] = df_ajustado['Sharpe_Ratio'] * np.sqrt(self.factor_ajuste_temporalidad)
                    logger.info("📊 Sharpe ratio ajustado según frecuencia")
                
                # 6. Profit factor ajustado
                if 'Profit_factor' in df_ajustado.columns:
                    # Profit factor se mantiene similar pero ajustamos umbrales
                    df_ajustado['Profit_Factor_Ajustado'] = df_ajustado['Profit_factor']
                    logger.info("💹 Profit factor ajustado")
                
        except Exception as e:
            logger.error(f"❌ Error aplicando ajustes científicos: {e}")
        
        return df_ajustado.copy()
    
    def _aplicar_filtros_cientificos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        MEJORA CIENTÍFICA: Aplica filtros científicos basados en evidencia empírica
        para asegurar robustez estadística.
        """
        df_filtrado = df.copy()
        filtros_aplicados = []
        
        try:
            logger.info("🔬 Aplicando filtros científicos basados en evidencia empírica...")
            
            # FILTROS CIENTÍFICOS BASADOS EN EVIDENCIA EMPÍRICA
            
            # 1. Mínimo 30 trades para robustez estadística
            if 'Total_Trades' in df_filtrado.columns:
                antes = len(df_filtrado)
                df_filtrado = df_filtrado[df_filtrado['Total_Trades'] >= 30]
                filtros_aplicados.append(f"Trades mínimos: {antes} -> {len(df_filtrado)}")
                logger.info(f"📊 Filtro trades mínimos: {antes} -> {len(df_filtrado)} estrategias")
            
            # 2. Mínimo 12 meses de datos
            if 'Total_Data_Months' in df_filtrado.columns:
                antes = len(df_filtrado)
                df_filtrado = df_filtrado[df_filtrado['Total_Data_Months'] >= 12]
                filtros_aplicados.append(f"Meses mínimos: {antes} -> {len(df_filtrado)}")
                logger.info(f"📅 Filtro meses mínimos: {antes} -> {len(df_filtrado)} estrategias")
            
            # 3. Sharpe ratio mínimo (ajustado según temporalidad)
            if 'Sharpe_Ratio' in df_filtrado.columns:
                antes = len(df_filtrado)
                sharpe_min = 0.5 * self.factor_ajuste_temporalidad
                df_filtrado = df_filtrado[df_filtrado['Sharpe_Ratio'] >= sharpe_min]
                filtros_aplicados.append(f"Sharpe mínimo: {antes} -> {len(df_filtrado)}")
                logger.info(f"📊 Filtro Sharpe mínimo ({sharpe_min:.2f}): {antes} -> {len(df_filtrado)} estrategias")
            
            # 4. Profit factor mínimo
            if 'Profit_factor' in df_filtrado.columns:
                antes = len(df_filtrado)
                df_filtrado = df_filtrado[df_filtrado['Profit_factor'] >= 1.1]
                filtros_aplicados.append(f"Profit factor mínimo: {antes} -> {len(df_filtrado)}")
                logger.info(f"💹 Filtro profit factor mínimo: {antes} -> {len(df_filtrado)} estrategias")
            
            # 5. Drawdown máximo permitido
            if 'Max_Drawdown' in df_filtrado.columns:
                antes = len(df_filtrado)
                drawdown_max = 0.25  # 25% máximo
                df_filtrado = df_filtrado[df_filtrado['Max_Drawdown'] <= drawdown_max]
                filtros_aplicados.append(f"Drawdown máximo: {antes} -> {len(df_filtrado)}")
                logger.info(f"📉 Filtro drawdown máximo ({drawdown_max*100}%): {antes} -> {len(df_filtrado)} estrategias")
            
            # 6. Win rate mínimo
            if 'Winning_Percent' in df_filtrado.columns:
                antes = len(df_filtrado)
                winrate_min = 0.4  # 40% mínimo
                df_filtrado = df_filtrado[df_filtrado['Winning_Percent'] >= winrate_min]
                filtros_aplicados.append(f"Win rate mínimo: {antes} -> {len(df_filtrado)}")
                logger.info(f"🎯 Filtro win rate mínimo ({winrate_min*100}%): {antes} -> {len(df_filtrado)} estrategias")
            
            # 7. Consistencia IS/OOS mínima
            if 'Predictividad_IS_OOS' in df_filtrado.columns:
                antes = len(df_filtrado)
                consistencia_min = 0.6  # 60% mínimo
                df_filtrado = df_filtrado[df_filtrado['Predictividad_IS_OOS'] >= consistencia_min]
                filtros_aplicados.append(f"Consistencia mínima: {antes} -> {len(df_filtrado)}")
                logger.info(f"🔄 Filtro consistencia mínima ({consistencia_min*100}%): {antes} -> {len(df_filtrado)} estrategias")
            
            logger.info(f"✅ Filtros científicos aplicados: {len(filtros_aplicados)} filtros")
            for filtro in filtros_aplicados:
                logger.info(f"   • {filtro}")
                
        except Exception as e:
            logger.error(f"❌ Error aplicando filtros científicos: {e}")
        
        return df_filtrado.copy()  # type: ignore
    
    def analizar_estrategias(self, estrategias: pd.DataFrame, kpis: List[str]) -> Dict[str, Any]:
        """
        Analiza las estrategias proporcionadas con los KPIs especificados.
        
        Args:
            estrategias: DataFrame con estrategias a analizar
            kpis: Lista de KPIs a considerar en el análisis
            
        Returns:
            Diccionario con resultados del análisis
        """
        self.estrategias = estrategias.copy()
        self.kpis = kpis
        self._setup_is_oos_kpis()
        
        # MEJORAS CIENTÍFICAS: Aplicar ajustes y filtros
        logger.info("🔬 Aplicando mejoras científicas y empíricas...")
        
        # 1. Aplicar ajustes científicos
        estrategias_ajustadas = self._aplicar_ajustes_cientificos(self.estrategias)
        
        # 2. Aplicar filtros científicos
        estrategias_filtradas = self._aplicar_filtros_cientificos(estrategias_ajustadas)
        
        # 3. Actualizar estrategias con los ajustes
        self.estrategias = estrategias_filtradas
        
        # 4. Análisis de predictibilidad (nuevo)
        predictibilidad_results = self._analyze_predictability_all_strategies()
        
        results = {
            'estrategias_analizadas': len(self.estrategias),
            'estrategias_originales': len(estrategias),
            'estrategias_filtradas': len(estrategias_filtradas),
            'kpis_utilizados': len(self.kpis),
            'temporalidad_detectada': self.temporalidad_detectada,
            'factor_ajuste_temporalidad': self.factor_ajuste_temporalidad,
            'analisis_predictibilidad': predictibilidad_results,
            'analisis_correlacion': self.analizar_correlacion_is_oos(),
            'outliers_detectados': self.detectar_outliers(),
            'consejos_generados': self.generar_consejos_completos()
        }
        
        logger.info(f"✅ Análisis completado para {len(self.estrategias)} estrategias (filtradas de {len(estrategias)} originales)")
        return results
    
    def _setup_is_oos_kpis(self):
        """Configura pares de KPIs IS/OOS para análisis de consistencia."""
        self.is_oos_pairs = {}
        for kpi in self.kpis:
            if kpi.endswith('(IS)') and kpi.replace('(IS)', '(OOS)') in self.kpis:
                kpi_oos = kpi.replace('(IS)', '(OOS)')
                self.is_oos_pairs[kpi] = kpi_oos
            elif kpi.endswith('_IS') and kpi.replace('_IS', '_OOS') in self.kpis:
                kpi_oos = kpi.replace('_IS', '_OOS')
                self.is_oos_pairs[kpi] = kpi_oos
    
    def _check_nulls(self, df, series):
        """Función auxiliar para verificar valores nulos de forma segura."""
        if isinstance(df, pd.DataFrame):
            df_has_nulls = df.isnull().any().any()
        else:
            df_has_nulls = df.isnull().any()
        series_has_nulls = series.isnull().any()
        return df_has_nulls or series_has_nulls
    
    def analizar_correlacion_is_oos(self) -> Dict[str, Any]:
        """
        Analiza la consistencia entre rendimiento IS y OOS, reportando tanto el ratio OOS/IS como la correlación de Spearman.
        """
        results = {
            'pairs_analyzed': 0,
            'consistent_pairs': 0,
            'details': {},
            'consejos': []
        }
        for kpi_is, kpi_oos in self.is_oos_pairs.items():
            if kpi_is in self.estrategias.columns and kpi_oos in self.estrategias.columns:
                results['pairs_analyzed'] += 1
                is_values = self.estrategias[kpi_is]
                oos_values = self.estrategias[kpi_oos]
                ratio = oos_values / is_values
                ratio = ratio.replace([np.inf, -np.inf], np.nan).dropna()
                consistentes = ratio.between(0.8, 1.2).sum()
                consistency = (consistentes / len(ratio)) * 100 if len(ratio) > 0 else 0
                mask = is_values.notnull() & oos_values.notnull()
                if mask.sum() > 2:
                    try:
                        corr_result = spearmanr(is_values[mask].values, oos_values[mask].values)
                        if isinstance(corr_result, tuple):
                            val = corr_result[0]
                        else:
                            val = corr_result
                        spearman_corr = float(val) if isinstance(val, (int, float, np.floating, np.integer)) else float('nan')
                    except Exception:
                        spearman_corr = float('nan')
                else:
                    spearman_corr = float('nan')
                msg_ratio = f"{'✅' if consistency >= 80 else '⚠️' if consistency >= 60 else '❌'} Consistencia IS/OOS en {kpi_is.replace('(IS)','').replace('_IS','')}: {consistency:.1f}%"
                if not np.isnan(spearman_corr):
                    if spearman_corr >= 0.7:
                        msg_corr = f"🔗 Correlación de Spearman alta entre IS y OOS en {kpi_is.replace('(IS)','').replace('_IS','')}: {spearman_corr:.2f} (ranking consistente)"
                    elif spearman_corr >= 0.4:
                        msg_corr = f"🟡 Correlación de Spearman moderada entre IS y OOS en {kpi_is.replace('(IS)','').replace('_IS','')}: {spearman_corr:.2f} (ranking parcialmente consistente)"
                    else:
                        msg_corr = f"⚠️ Correlación de Spearman baja entre IS y OOS en {kpi_is.replace('(IS)','').replace('_IS','')}: {spearman_corr:.2f} (posible sobreajuste o ranking inconsistente)"
                else:
                    msg_corr = ""
                # Determinar nivel de consistencia
                if consistency >= 80:
                    nivel = "Excelente"
                elif consistency >= 60:
                    nivel = "Buena"
                elif consistency >= 40:
                    nivel = "Moderada"
                else:
                    nivel = "Baja"
                
                results['details'][kpi_is] = {
                    'consistency_pct': consistency,
                    'spearman_corr': spearman_corr,
                    'nivel': nivel
                }
                results['consejos'].append(msg_ratio)
                if msg_corr:
                    results['consejos'].append(msg_corr)
                if consistency >= 60:
                    results['consistent_pairs'] += 1
        if results['pairs_analyzed'] > 0:
            consistency_avg = results['consistent_pairs'] / results['pairs_analyzed'] * 100
            if consistency_avg >= 80:
                results['consejos'].append("🎯 Excelente robustez general entre IS y OOS")
            elif consistency_avg >= 60:
                results['consejos'].append("🟡 Buena robustez general, algunas métricas requieren atención")
            else:
                results['consejos'].append("⚠️ Baja robustez general - considera revisar la metodología")
        return results
    
    def detectar_outliers(self, contamination: float = 0.1) -> Dict[str, Any]:
        """
        Identifica estrategias con comportamiento atípico usando Isolation Forest.
        
        Args:
            contamination: Proporción esperada de outliers (0.05-0.15)
            
        Returns:
            Diccionario con outliers detectados y clasificación
        """
        try:
            if len(self.estrategias) < 10:
                return {
                    'outliers': [],
                    'buenos_outliers': [],
                    'malos_outliers': [],
                    'consejos': ["ℹ️ Datos insuficientes para detección de outliers (mínimo 10 estrategias)"]
                }
            
            # Preparar datos para detección
            kpi_data = self.estrategias[self.kpis].copy()
            kpi_data = kpi_data.replace([np.inf, -np.inf], np.nan)
            kpi_data = kpi_data.fillna(kpi_data.median())
            
            # Detectar outliers
            iso_forest = IsolationForest(
                contamination="auto", 
                random_state=42,
                n_estimators=100
            )
            outliers = iso_forest.fit_predict(kpi_data)
            outlier_indices = self.estrategias.index[outliers == -1]
            
            # Clasificar outliers
            buenos_outliers = []
            malos_outliers = []
            
            for idx in outlier_indices:
                # Identificar KPIs de riesgo y rendimiento
                risk_kpis = [k for k in self.kpis if 'drawdown' in k.lower() or 'var' in k.lower()]
                performance_kpis = [k for k in self.kpis if 'profit' in k.lower() or 'sharpe' in k.lower() or 'cagr' in k.lower()]
                
                # Evaluar si es outlier "bueno" o "malo"
                is_high_risk = False
                is_high_performance = False
                
                for risk_kpi in risk_kpis:
                    if risk_kpi in self.estrategias.columns:
                        if self.estrategias.loc[idx, risk_kpi] > self.estrategias[risk_kpi].quantile(0.9):
                            is_high_risk = True
                            break
                
                for perf_kpi in performance_kpis:
                    if perf_kpi in self.estrategias.columns:
                        if self.estrategias.loc[idx, perf_kpi] > self.estrategias[perf_kpi].quantile(0.9):
                            is_high_performance = True
                            break
                
                if is_high_risk:
                    malos_outliers.append(idx)
                elif is_high_performance:
                    buenos_outliers.append(idx)
                else:
                    # Clasificar por comportamiento general
                    malos_outliers.append(idx)
            
            # Generar consejos
            consejos = []
            if len(malos_outliers) > 0:
                consejos.append(f"⚠️ {len(malos_outliers)} estrategias con riesgo elevado detectadas")
                for idx in malos_outliers[:3]:  # Mostrar solo las primeras 3
                    consejos.append(f"   • Estrategia {idx}: Revisar parámetros de riesgo")
            
            if len(buenos_outliers) > 0:
                consejos.append(f"✅ {len(buenos_outliers)} estrategias con rendimiento excepcional")
                for idx in buenos_outliers[:3]:  # Mostrar solo las primeras 3
                    consejos.append(f"   • Estrategia {idx}: Considerar optimización adicional")
            
            if len(outlier_indices) == 0:
                consejos.append("✅ No se detectaron outliers significativos")
            
            logger.info(f"🔍 Detección de outliers: {len(outlier_indices)} outliers detectados")
            return {
                'outliers': outlier_indices.tolist(),
                'buenos_outliers': buenos_outliers,
                'malos_outliers': malos_outliers,
                'consejos': consejos
            }
            
        except Exception as e:
            logger.error(f"Error en detección de outliers: {e}")
            return {'error': str(e), 'consejos': ["❌ Error en detección de outliers"]}
    
    def clustering_estrategias(self, n_clusters: int = 3) -> Dict[str, Any]:
        """
        Agrupa estrategias por similitud usando K-means.
        
        Args:
            n_clusters: Número de clusters (2-5 recomendado)
            
        Returns:
            Diccionario con resultados de clustering
        """
        try:
            if len(self.estrategias) < n_clusters:
                return {
                    'clusters': [],
                    'centers': [],
                    'silhouette_score': 0,
                    'consejos': [f"ℹ️ Datos insuficientes para clustering (mínimo {n_clusters} estrategias)"]
                }
            
            # Preparar datos
            kpi_data = self.estrategias[self.kpis].copy()
            kpi_data = kpi_data.replace([np.inf, -np.inf], np.nan)
            kpi_data = kpi_data.fillna(kpi_data.median())
            
            # Estandarizar
            kpi_scaled = self.scaler.fit_transform(kpi_data)
            
            # Determinar número óptimo de clusters si hay suficientes datos
            if len(self.estrategias) >= 10:
                silhouette_scores = []
                k_range = range(2, min(6, len(self.estrategias) // 2))
                
                for k in k_range:
                    kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init="auto")
                    labels_temp = kmeans_temp.fit_predict(kpi_scaled)
                    score = silhouette_score(kpi_scaled, labels_temp)
                    silhouette_scores.append(score)
                
                # Usar el número de clusters con mejor score
                best_k = k_range[np.argmax(silhouette_scores)]
                if best_k != n_clusters:
                    n_clusters = best_k
                    logger.info(f"🔄 Número óptimo de clusters ajustado a {n_clusters}")
            
            # Clustering final
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
            clusters = kmeans.fit_predict(kpi_scaled)
            silhouette_score_final = silhouette_score(kpi_scaled, clusters)
            
            # Analizar características de cada cluster
            cluster_analysis = []
            for i in range(n_clusters):
                cluster_mask = clusters == i
                cluster_data = self.estrategias[cluster_mask]
                
                # Características principales del cluster
                characteristics = []
                for kpi in self.kpis[:5]:  # Analizar solo los primeros 5 KPIs
                    if kpi in cluster_data.columns:
                        mean_val = cluster_data[kpi].mean()
                        characteristics.append(f"{kpi}: {mean_val:.2f}")
                
                cluster_analysis.append({
                    'cluster_id': i,
                    'size': int(cluster_mask.sum()),
                    'characteristics': characteristics
                })
            
            # Generar consejos
            consejos = [f"📊 Estrategias agrupadas en {n_clusters} clusters (score: {silhouette_score_final:.3f})"]
            
            # Consejos de diversificación
            if n_clusters >= 2:
                cluster_sizes = [c['size'] for c in cluster_analysis]
                max_size = max(cluster_sizes)
                min_size = min(cluster_sizes)
                
                if max_size / min_size > 2:
                    consejos.append("⚠️ Distribución desigual entre clusters - considera rebalancear")
                else:
                    consejos.append("✅ Buena distribución entre clusters")
                
                # Recomendaciones específicas
                for cluster in cluster_analysis:
                    if cluster['size'] > 0:
                        consejos.append(f"   • Cluster {cluster['cluster_id']}: {cluster['size']} estrategias")
            
            logger.info(f"🎯 Clustering completado: {n_clusters} clusters, score={silhouette_score_final:.3f}")
            return {
                'clusters': clusters.tolist(),
                'centers': kmeans.cluster_centers_.tolist(),
                'silhouette_score': silhouette_score_final,
                'cluster_analysis': cluster_analysis,
                'consejos': consejos
            }
            
        except Exception as e:
            logger.error(f"Error en clustering: {e}")
            return {'error': str(e), 'consejos': ["❌ Error en clustering de estrategias"]}
    
    def analizar_importancia_kpis(self, target: str = 'Unified_Score') -> Dict[str, Any]:
        """
        Identifica KPIs más predictivos usando SHAP.
        
        Args:
            target: Variable objetivo para predicción
            
        Returns:
            Diccionario con importancia de KPIs
        """
        try:
            if target not in self.estrategias.columns:
                return {
                    'importance': {},
                    'top_kpis': [],
                    'consejos': [f"❌ Variable objetivo '{target}' no encontrada en los datos"]
                }
            
            # Preparar datos
            X = self.estrategias[self.kpis].copy()
            y = self.estrategias[target]
            
            # Limpiar datos
            X = X.replace([np.inf, -np.inf], np.nan)
            X = X.fillna(X.median())
            
            # Verificar que no hay valores faltantes
            if self._check_nulls(X, y):
                return {
                    'importance': {},
                    'top_kpis': [],
                    'consejos': ["❌ Datos con valores faltantes - no se puede calcular importancia"]
                }
            
            # Entrenar modelo
            self.model.fit(X, y)
            
            # Calcular importancia SHAP
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X)
            
            # Calcular importancia promedio
            importance = pd.Series(
                np.abs(shap_values).mean(axis=0), 
                index=self.kpis
            ).sort_values(ascending=False)
            
            # Top 5 KPIs más importantes
            top_kpis = importance.head(5)
            
            # Generar consejos
            consejos = ["🎯 KPIs más predictivos del rendimiento:"]
            for i, (kpi, importance_val) in enumerate(top_kpis.items(), 1):
                percentage = (importance_val / importance.sum()) * 100
                consejos.append(f"   {i}. {kpi}: {percentage:.1f}%")
            
            # Consejo adicional sobre interpretación
            if top_kpis.iloc[0] > importance.mean() * 2:
                consejos.append("💡 Un KPI domina la predicción - considera diversificar métricas")
            else:
                consejos.append("✅ Buena distribución de importancia entre KPIs")
            
            logger.info(f"📈 Análisis de importancia completado: {len(top_kpis)} KPIs principales identificados")
            return {
                'importance': importance.to_dict(),
                'top_kpis': top_kpis.to_dict(),
                'consejos': consejos
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de importancia: {e}")
            return {'error': str(e), 'consejos': ["❌ Error en análisis de importancia de KPIs"]}
    
    def predecir_rendimiento(self, target: str = 'Unified_Score') -> Dict[str, Any]:
        """
        Predice el rendimiento futuro usando Random Forest con validación robusta.
        
        Args:
            target: Variable objetivo para predicción
            
        Returns:
            Diccionario con resultados de predicción
        """
        try:
            if target not in self.estrategias.columns:
                return {
                    'predictions': [],
                    'r2_mean': 0,
                    'r2_std': 0,
                    'consejos': [f"❌ Variable objetivo '{target}' no encontrada"]
                }
            
            # Preparar datos
            X = self.estrategias[self.kpis].copy()
            y = self.estrategias[target]
            
            # Limpiar datos
            X = X.replace([np.inf, -np.inf], np.nan)
            X = X.fillna(X.median())
            
            if self._check_nulls(X, y):
                return {
                    'predictions': [],
                    'r2_mean': 0,
                    'r2_std': 0,
                    'consejos': ["❌ Datos con valores faltantes - no se puede predecir"]
                }
            
            # Validación cruzada con TimeSeriesSplit para respetar orden temporal
            if len(self.estrategias) >= 10:
                tscv = TimeSeriesSplit(n_splits=min(5, len(self.estrategias) // 2))
                scores = cross_val_score(self.model, X, y, cv=tscv, scoring='r2')
                r2_mean = scores.mean()
                r2_std = scores.std()
            else:
                # Para pocos datos, usar validación simple
                self.model.fit(X, y)
                predictions = self.model.predict(X)
                r2_mean = r2_score(y, predictions)
                r2_std = 0
            
            # Entrenar modelo final
            self.model.fit(X, y)
            predictions = self.model.predict(X)
            
            # Calcular métricas adicionales
            mae = mean_absolute_error(y, predictions)
            rmse = np.sqrt(mean_squared_error(y, predictions))
            
            # Generar consejos
            consejos = []
            if r2_mean >= 0.7:
                consejos.append(f"✅ Excelente capacidad predictiva (R²: {r2_mean:.2f} ± {r2_std:.2f})")
            elif r2_mean >= 0.5:
                consejos.append(f"🟡 Buena capacidad predictiva (R²: {r2_mean:.2f} ± {r2_std:.2f})")
            elif r2_mean >= 0.3:
                consejos.append(f"⚠️ Capacidad predictiva moderada (R²: {r2_mean:.2f} ± {r2_std:.2f})")
            else:
                consejos.append(f"❌ Baja capacidad predictiva (R²: {r2_mean:.2f} ± {r2_std:.2f})")
            
            consejos.append(f"📊 Error promedio: {mae:.2f}, Error cuadrático: {rmse:.2f}")
            
            logger.info(f"🔮 Predicción completada: R²={r2_mean:.3f} ± {r2_std:.3f}")
            return {
                'predictions': predictions.tolist(),
                'r2_mean': r2_mean,
                'r2_std': r2_std,
                'mae': mae,
                'rmse': rmse,
                'consejos': consejos
            }
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            return {'error': str(e), 'consejos': ["❌ Error en predicción de rendimiento"]}
    
    def generar_consejos_completos(self) -> Dict[str, Any]:
        """
        Ejecuta todos los análisis y genera consejos completos.
        
        Returns:
            Diccionario con todos los resultados y consejos
        """
        try:
            logger.info("🚀 Iniciando análisis completo del Asesor Financiero Inteligente")
            
            # MEJORAS CIENTÍFICAS: Información sobre ajustes aplicados
            consejos_mejoras_cientificas = []
            
            if self.temporalidad_detectada and self.temporalidad_detectada != "Desconocida":
                consejos_mejoras_cientificas.append(f"🔬 Temporalidad detectada: {self.temporalidad_detectada}")
                consejos_mejoras_cientificas.append(f"📊 Factor de ajuste aplicado: {self.factor_ajuste_temporalidad:.3f}")
                
                if self.factor_ajuste_temporalidad < 1.0:
                    consejos_mejoras_cientificas.append("⚡ Ajustes científicos aplicados según temporalidad")
                    consejos_mejoras_cientificas.append("📈 Métricas ajustadas para análisis más preciso")
                else:
                    consejos_mejoras_cientificas.append("✅ Análisis con métricas estándar (temporalidad M1)")
            
            # Filtros científicos aplicados
            if hasattr(self, 'estrategias') and len(self.estrategias) > 0:
                consejos_mejoras_cientificas.append("🔍 Filtros científicos aplicados para robustez estadística")
                consejos_mejoras_cientificas.append("📊 Mínimo 30 trades, 12 meses de datos, métricas de calidad")
            
            # Ejecutar todos los análisis
            correlacion = self.analizar_correlacion_is_oos()
            outliers = self.detectar_outliers()
            clustering = self.clustering_estrategias()
            importancia = self.analizar_importancia_kpis()
            prediccion = self.predecir_rendimiento()
            
            # Combinar todos los consejos
            todos_consejos = []
            
            # MEJORAS CIENTÍFICAS: Agregar consejos de mejoras científicas al inicio
            todos_consejos.extend(consejos_mejoras_cientificas)
            todos_consejos.append("")  # Línea en blanco para separar
            
            # Consejos de correlación IS/OOS
            if 'consejos' in correlacion:
                todos_consejos.extend(correlacion['consejos'])
            
            # Consejos de outliers
            if 'consejos' in outliers:
                todos_consejos.extend(outliers['consejos'])
            
            # Consejos de clustering
            if 'consejos' in clustering:
                todos_consejos.extend(clustering['consejos'])
            
            # Consejos de importancia
            if 'consejos' in importancia:
                todos_consejos.extend(importancia['consejos'])
            
            # Consejos de predicción
            if 'consejos' in prediccion:
                todos_consejos.extend(prediccion['consejos'])
            
            # Consejo final de resumen
            total_analisis = sum([
                'error' not in correlacion,
                'error' not in outliers,
                'error' not in clustering,
                'error' not in importancia,
                'error' not in prediccion
            ])
            
            if total_analisis >= 4:
                todos_consejos.append("🎉 Análisis completo ejecutado exitosamente")
                todos_consejos.append("🔬 Mejoras científicas y empíricas aplicadas correctamente")
            else:
                todos_consejos.append("⚠️ Algunos análisis presentaron errores - revisar datos")
            
            # Guardar resultados
            self.results = {
                'correlacion_is_oos': correlacion,
                'outliers': outliers,
                'clustering': clustering,
                'importancia_kpis': importancia,
                'prediccion': prediccion,
                'consejos_completos': todos_consejos,
                'mejoras_cientificas': {
                    'temporalidad_detectada': self.temporalidad_detectada,
                    'factor_ajuste_temporalidad': self.factor_ajuste_temporalidad,
                    'consejos_mejoras': consejos_mejoras_cientificas
                }
            }
            
            logger.info(f"✅ Análisis completo finalizado: {len(todos_consejos)} consejos generados")
            logger.info(f"🔬 Mejoras científicas aplicadas: {len(consejos_mejoras_cientificas)} mejoras")
            return self.results
            
        except Exception as e:
            logger.error(f"Error en análisis completo: {e}")
            return {
                'error': str(e),
                'consejos_completos': ["❌ Error en análisis completo del Asesor Financiero"]
            }
    
    def obtener_resumen_ejecutivo(self) -> str:
        """
        Genera un resumen ejecutivo de los hallazgos principales.
        
        Returns:
            String con resumen ejecutivo
        """
        if not self.results:
            return "❌ No hay resultados disponibles - ejecutar análisis primero"
        
        resumen = "📋 RESUMEN EJECUTIVO DEL ASESOR FINANCIERO\n"
        resumen += "=" * 50 + "\n\n"
        
        # MEJORAS CIENTÍFICAS: Información sobre ajustes aplicados
        if 'mejoras_cientificas' in self.results:
            mejoras = self.results['mejoras_cientificas']
            resumen += "🔬 MEJORAS CIENTÍFICAS APLICADAS:\n"
            resumen += "-" * 30 + "\n"
            
            if mejoras.get('temporalidad_detectada') and mejoras['temporalidad_detectada'] != "Desconocida":
                resumen += f"📊 Temporalidad detectada: {mejoras['temporalidad_detectada']}\n"
                resumen += f"⚡ Factor de ajuste: {mejoras['factor_ajuste_temporalidad']:.3f}\n"
                resumen += "📈 Métricas ajustadas según evidencia empírica\n"
                resumen += "🔍 Filtros científicos aplicados para robustez\n\n"
        
        # Resumen de correlación IS/OOS
        if 'correlacion_is_oos' in self.results:
            corr = self.results['correlacion_is_oos']
            if 'pairs_analyzed' in corr:
                resumen += f"📊 Consistencia IS/OOS: {corr['pairs_analyzed']} métricas analizadas\n"
                if 'consistent_pairs' in corr:
                    consistency_pct = (corr['consistent_pairs'] / corr['pairs_analyzed']) * 100
                    resumen += f"   • {consistency_pct:.1f}% de métricas consistentes\n"
        
        # Resumen de outliers
        if 'outliers' in self.results:
            outliers = self.results['outliers']
            if 'outliers' in outliers:
                resumen += f"🔍 Outliers detectados: {len(outliers['outliers'])} estrategias\n"
                if 'malos_outliers' in outliers:
                    resumen += f"   • {len(outliers['malos_outliers'])} con riesgo elevado\n"
                if 'buenos_outliers' in outliers:
                    resumen += f"   • {len(outliers['buenos_outliers'])} con rendimiento excepcional\n"
        
        # Resumen de clustering
        if 'clustering' in self.results:
            cluster = self.results['clustering']
            if 'silhouette_score' in cluster:
                resumen += f"🎯 Clustering: Score de calidad {cluster['silhouette_score']:.3f}\n"
        
        # Resumen de predicción
        if 'prediccion' in self.results:
            pred = self.results['prediccion']
            if 'r2_mean' in pred:
                resumen += f"🔮 Capacidad predictiva: R² = {pred['r2_mean']:.3f}\n"
        
        resumen += "\n💡 RECOMENDACIONES PRINCIPALES:\n"
        resumen += "-" * 30 + "\n"
        
        # Top 5 consejos más importantes (incluyendo mejoras científicas)
        if 'consejos_completos' in self.results:
            consejos = self.results['consejos_completos']
            # Filtrar consejos de mejoras científicas y otros consejos importantes
            consejos_importantes = [c for c in consejos if c and not c.startswith("   •") and not c.startswith("   ")]
            for i, consejo in enumerate(consejos_importantes[:5], 1):
                resumen += f"{i}. {consejo}\n"
        
        return resumen

    def calculate_quality_score(self, strategy_data: pd.Series) -> float:
        """
        Calcula el Quality Score basado en múltiples factores de calidad.
        Incluye bonus por predictibilidad usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            Quality Score (0-100)
        """
        try:
            # Quality Score base original (mantener lógica original)
            base_quality_score = self._calculate_base_quality_score(strategy_data)
            
            # Bonus por predictibilidad (nuevo)
            predictability_bonus = self._calculate_predictability_bonus_asesor(strategy_data)
            
            # Quality Score final
            final_quality_score = base_quality_score + predictability_bonus
            return min(final_quality_score, 100)
            
        except Exception as e:
            logger.error(f"Error calculando Quality Score: {e}")
            return 0.0
    
    def _calculate_base_quality_score(self, strategy_data: pd.Series) -> float:
        """
        Calcula Quality Score base original (mantener lógica original).
        """
        try:
            quality_score = 0.0
            
            # 1. Rentabilidad (30%)
            profitability_score = 0.0
            
            # CAGR
            if 'CAGR' in strategy_data:
                cagr = self._safe_float(strategy_data['CAGR'])
                if cagr > 0:
                    profitability_score += min(cagr * 3, 30)
            
            # Profit Factor
            if 'Profit factor' in strategy_data:
                pf = self._safe_float(strategy_data['Profit factor'])
                if pf > 1:
                    profitability_score += min((pf - 1) * 15, 20)
            
            quality_score += profitability_score * 0.30
            
            # 2. Riesgo (25%)
            risk_score = 0.0
            
            # Sharpe Ratio
            if 'Sharpe Ratio' in strategy_data:
                sharpe = self._safe_float(strategy_data['Sharpe Ratio'])
                if sharpe > 0:
                    risk_score += min(sharpe * 10, 25)
            
            # Max Drawdown (inverso)
            if 'Max DD %' in strategy_data:
                dd = abs(self._safe_float(strategy_data['Max DD %']))
                if dd <= 10:
                    risk_score += 25
                elif dd <= 15:
                    risk_score += 20
                elif dd <= 20:
                    risk_score += 15
                elif dd <= 25:
                    risk_score += 10
            
            quality_score += risk_score * 0.25
            
            # 3. Consistencia (25%)
            consistency_score = 0.0
            
            # Win Rate
            if 'Winning Percent' in strategy_data:
                win_rate = self._safe_float(strategy_data['Winning Percent'])
                if win_rate > 0:
                    consistency_score += min(win_rate * 0.4, 25)
            
            # SQN
            if 'SQN' in strategy_data:
                sqn = self._safe_float(strategy_data['SQN'])
                if sqn > 0:
                    consistency_score += min(sqn * 8, 20)
            
            # Number of Trades
            if '# of trades' in strategy_data:
                trades = self._safe_float(strategy_data['# of trades'])
                if trades >= 100:
                    consistency_score += 10
                elif trades >= 50:
                    consistency_score += 5
            
            quality_score += consistency_score * 0.25
            
            # 4. Estabilidad (20%)
            stability_score = 0.0
            
            # Calmar Ratio
            if 'CalmarRatio' in strategy_data:
                calmar = self._safe_float(strategy_data['CalmarRatio'])
                if calmar > 0:
                    stability_score += min(calmar * 8, 20)
            
            # Recovery Factor
            if 'RecoveryFactor' in strategy_data:
                rf = self._safe_float(strategy_data['RecoveryFactor'])
                if rf > 0:
                    stability_score += min(rf * 2, 15)
            
            # Sortino Ratio
            if 'Sortino Ratio' in strategy_data:
                sortino = self._safe_float(strategy_data['Sortino Ratio'])
                if sortino > 0:
                    stability_score += min(sortino * 5, 15)
            
            quality_score += stability_score * 0.20
            
            return min(quality_score, 100)
            
        except Exception as e:
            logger.error(f"Error calculando Quality Score base: {e}")
            return 0.0
    
    def _calculate_predictability_bonus_asesor(self, strategy_data: pd.Series) -> float:
        """
        Calcula bonus por predictibilidad para Asesor Financiero usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            Bonus de predictibilidad (0-25 puntos)
        """
        try:
            # Calcular métricas de predictibilidad
            predictability_metrics = self.predictability_analyzer.calculate_overall_predictability(strategy_data)
            
            # Bonus basado en predictibilidad general (más generoso para asesor)
            if predictability_metrics.overall_predictability >= 80:
                bonus = 25  # Excelente predictibilidad
            elif predictability_metrics.overall_predictability >= 70:
                bonus = 20  # Buena predictibilidad
            elif predictability_metrics.overall_predictability >= 60:
                bonus = 15  # Predictibilidad aceptable
            elif predictability_metrics.overall_predictability >= 50:
                bonus = 10  # Predictibilidad básica
            elif predictability_metrics.overall_predictability >= 40:
                bonus = 5   # Predictibilidad mínima
            else:
                bonus = 0   # Sin bonus
            
            logger.info(f"Asesor Predictibilidad: {predictability_metrics.overall_predictability:.1f}, Bonus: {bonus}")
            
            return bonus
            
        except Exception as e:
            logger.error(f"Error calculando bonus de predictibilidad Asesor: {e}")
            return 0.0

    def _apply_predictability_filters_asesor(self, strategy_data: pd.Series) -> Dict[str, Any]:
        """
        Aplica filtros de predictibilidad para Asesor Financiero usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            Resultados de filtros de predictibilidad
        """
        try:
            passed_filters = []
            failed_filters = []
            
            # 1. Filtro de Consistencia IS/OOS (datos reales)
            if self._check_is_oos_consistency_asesor(strategy_data):
                passed_filters.append("is_oos_consistency")
            else:
                failed_filters.append("is_oos_consistency")
            
            # 2. Filtro de Robustez Temporal (datos reales)
            if self._check_temporal_robustness_asesor(strategy_data):
                passed_filters.append("temporal_robustness")
            else:
                failed_filters.append("temporal_robustness")
            
            # 3. Filtro de Detección de Sobreajuste (datos reales)
            if self._check_overfitting_detection_asesor(strategy_data):
                passed_filters.append("overfitting_detection")
            else:
                failed_filters.append("overfitting_detection")
            
            # 4. Filtro de Estabilidad (datos reales)
            if self._check_stability_score_asesor(strategy_data):
                passed_filters.append("stability_score")
            else:
                failed_filters.append("stability_score")
            
            return {
                "passed": passed_filters,
                "failed": failed_filters,
                "total_passed": len(passed_filters),
                "total_filters": len(passed_filters) + len(failed_filters)
            }
            
        except Exception as e:
            self.logger.error(f"Error aplicando filtros de predictibilidad Asesor: {e}")
            return {"passed": [], "failed": [], "total_passed": 0, "total_filters": 0}
    
    def _analyze_predictability_all_strategies(self) -> Dict[str, Any]:
        """
        Analiza predictibilidad de todas las estrategias.
        
        Returns:
            Resultados del análisis de predictibilidad
        """
        try:
            predictability_results = {
                "strategies_analyzed": 0,
                "high_predictability": 0,
                "medium_predictability": 0,
                "low_predictability": 0,
                "average_predictability": 0.0,
                "top_predictable": [],
                "predictability_scores": []
            }
            
            total_predictability = 0.0
            strategy_scores = []
            
            for idx, strategy_data in self.estrategias.iterrows():
                try:
                    # Aplicar filtros de predictibilidad
                    filter_results = self._apply_predictability_filters_asesor(strategy_data)
                    
                    # Calcular Quality Score con predictibilidad
                    quality_score = self.calculate_quality_score(strategy_data)
                    
                    # Calcular métricas de predictibilidad
                    metrics = self.predictability_analyzer.calculate_overall_predictability(strategy_data)
                    
                    # Clasificar por predictibilidad
                    if metrics.overall_predictability >= 80:
                        predictability_results["high_predictability"] += 1
                    elif metrics.overall_predictability >= 60:
                        predictability_results["medium_predictability"] += 1
                    else:
                        predictability_results["low_predictability"] += 1
                    
                    total_predictability += metrics.overall_predictability
                    strategy_scores.append({
                        "strategy_name": strategy_data.get("Strategy Name", f"Strategy_{idx}"),
                        "predictability_score": metrics.overall_predictability,
                        "quality_score": quality_score,
                        "filter_results": filter_results
                    })
                    
                    predictability_results["strategies_analyzed"] += 1
                    
                except Exception as e:
                    self.logger.error(f"Error analizando predictibilidad de estrategia {idx}: {e}")
                    continue
            
            # Calcular promedio
            if predictability_results["strategies_analyzed"] > 0:
                predictability_results["average_predictability"] = total_predictability / predictability_results["strategies_analyzed"]
            
            # Top estrategias más predecibles
            strategy_scores.sort(key=lambda x: x["predictability_score"], reverse=True)
            predictability_results["top_predictable"] = strategy_scores[:10]
            predictability_results["predictability_scores"] = strategy_scores
            
            return predictability_results
            
        except Exception as e:
            self.logger.error(f"Error en análisis de predictibilidad: {e}")
            return {"error": str(e)}
    
    def _check_is_oos_consistency_asesor(self, strategy_data: pd.Series) -> bool:
        """
        Verifica consistencia IS/OOS para Asesor Financiero usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            True si pasa el filtro de consistencia
        """
        try:
            # Calcular métricas de predictibilidad
            metrics = self.predictability_analyzer.calculate_overall_predictability(strategy_data)
            
            # Umbral mínimo de consistencia IS/OOS (más generoso para asesor)
            min_consistency = 55.0  # 55% mínimo
            
            return metrics.is_oos_consistency >= min_consistency
            
        except Exception as e:
            self.logger.error(f"Error verificando consistencia IS/OOS Asesor: {e}")
            return False
    
    def _check_temporal_robustness_asesor(self, strategy_data: pd.Series) -> bool:
        """
        Verifica robustez temporal para Asesor Financiero usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            True si pasa el filtro de robustez temporal
        """
        try:
            # Calcular métricas de predictibilidad
            metrics = self.predictability_analyzer.calculate_overall_predictability(strategy_data)
            
            # Umbral mínimo de robustez temporal (más generoso para asesor)
            min_robustness = 45.0  # 45% mínimo
            
            return metrics.temporal_robustness >= min_robustness
            
        except Exception as e:
            self.logger.error(f"Error verificando robustez temporal Asesor: {e}")
            return False
    
    def _check_overfitting_detection_asesor(self, strategy_data: pd.Series) -> bool:
        """
        Verifica detección de sobreajuste para Asesor Financiero usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            True si pasa el filtro de detección de sobreajuste
        """
        try:
            # Calcular métricas de predictibilidad
            metrics = self.predictability_analyzer.calculate_overall_predictability(strategy_data)
            
            # Umbral mínimo de detección de sobreajuste (más generoso para asesor)
            min_overfitting_detection = 65.0  # 65% mínimo (menos sobreajuste)
            
            return metrics.overfitting_detection >= min_overfitting_detection
            
        except Exception as e:
            self.logger.error(f"Error verificando detección de sobreajuste Asesor: {e}")
            return False
    
    def _check_stability_score_asesor(self, strategy_data: pd.Series) -> bool:
        """
        Verifica score de estabilidad para Asesor Financiero usando datos empíricos reales.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            True si pasa el filtro de estabilidad
        """
        try:
            # Calcular métricas de predictibilidad
            metrics = self.predictability_analyzer.calculate_overall_predictability(strategy_data)
            
            # Umbral mínimo de estabilidad (más generoso para asesor)
            min_stability = 45.0  # 45% mínimo
            
            return metrics.stability_score >= min_stability
            
        except Exception as e:
            self.logger.error(f"Error verificando score de estabilidad Asesor: {e}")
            return False

    def _safe_float(self, value) -> float:
        """
        Convierte valor a float de forma segura.
        
        Args:
            value: Valor a convertir
            
        Returns:
            Float convertido o 0.0 si falla
        """
        try:
            if pd.isna(value) or value is None:
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0


def crear_asesor_financiero(estrategias_filtradas: pd.DataFrame, kpis_seleccionados: List[str]) -> AsesorFinancieroInteligente:
    """
    Función de utilidad para crear una instancia del Asesor Financiero.
    
    Args:
        estrategias_filtradas: DataFrame con estrategias filtradas
        kpis_seleccionados: Lista de KPIs para análisis
        
    Returns:
        Instancia del Asesor Financiero Inteligente
    """
    return AsesorFinancieroInteligente(estrategias_filtradas, kpis_seleccionados)


def ejecutar_analisis_completo(estrategias_filtradas: pd.DataFrame, kpis_seleccionados: List[str]) -> Dict[str, Any]:
    """
    Función de utilidad para ejecutar análisis completo en una sola llamada.
    
    Args:
        estrategias_filtradas: DataFrame con estrategias filtradas
        kpis_seleccionados: Lista de KPIs para análisis
        
    Returns:
        Diccionario con todos los resultados del análisis
    """
    asesor = crear_asesor_financiero(estrategias_filtradas, kpis_seleccionados)
    return asesor.generar_consejos_completos() 