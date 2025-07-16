#!/usr/bin/env python3
"""
Módulo de Inteligencia ML/IA Complementario para Core Engine
============================================================

Integra funcionalidades ML/IA que complementan el análisis existente sin duplicar:
- Performance Predictor: Predice rendimiento OOS basado en métricas IS
- Strategy Quality Classifier: Clasifica calidad de estrategias con ML
- Risk Profile Analyzer: Análisis de perfil de riesgo con clustering
- Consistency Validator: Valida consistencia temporal con ML
- Adaptive Threshold Optimizer: Optimiza umbrales dinámicamente

⚠️ COMPLEMENTA, NO DUPLICA: Usa las funcionalidades existentes como base
y agrega inteligencia adicional.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import warnings
from pathlib import Path
import json
from datetime import datetime

# ML Libraries
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import shap

# Core imports
from src.core.logger_config import setup_logger
from src.core.utils.error_handler import RobustErrorHandler

warnings.filterwarnings('ignore')

logger = setup_logger(__name__)


class MLIntelligenceType(Enum):
    """Tipos de inteligencia ML disponibles."""
    PERFORMANCE_PREDICTOR = "performance_predictor"
    QUALITY_CLASSIFIER = "quality_classifier"
    RISK_PROFILE_ANALYZER = "risk_profile_analyzer"
    CONSISTENCY_VALIDATOR = "consistency_validator"
    ADAPTIVE_THRESHOLD_OPTIMIZER = "adaptive_threshold_optimizer"


@dataclass
class MLIntelligenceResult:
    """Resultado de análisis de inteligencia ML."""
    analysis_type: MLIntelligenceType
    predictions: Optional[pd.Series] = None
    classifications: Optional[pd.Series] = None
    risk_profiles: Optional[Dict[str, Any]] = None
    consistency_scores: Optional[pd.Series] = None
    optimized_thresholds: Optional[Dict[str, float]] = None
    model_performance: Optional[Dict[str, float]] = None
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    confidence_scores: Optional[pd.Series] = None


class MLIntelligenceEnhancer:
    """
    Enhancer de inteligencia ML que complementa el core engine existente.
    
    Funcionalidades complementarias:
    - Performance Predictor: Predice rendimiento OOS
    - Quality Classifier: Clasifica calidad de estrategias
    - Risk Profile Analyzer: Análisis de perfiles de riesgo
    - Consistency Validator: Valida consistencia temporal
    - Adaptive Threshold Optimizer: Optimiza umbrales
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 enable_shap: bool = True,
                 enable_confidence_scores: bool = True):
        """
        Inicializa el enhancer de inteligencia ML.
        
        Args:
            config: Configuración opcional
            enable_shap: Si habilitar análisis SHAP
            enable_confidence_scores: Si calcular scores de confianza
        """
        self.config = config or {}
        self.enable_shap = enable_shap
        self.enable_confidence_scores = enable_confidence_scores
        self.logger = setup_logger(__name__)
        
        # Modelos ML
        self.performance_predictor = None
        self.quality_classifier = None
        self.risk_analyzer = None
        self.consistency_validator = None
        
        # Escaladores
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Resultados cache
        self.cached_results = {}
        
        logger.info("🔬 MLIntelligenceEnhancer inicializado")
    
    def enhance_analysis(self, 
                        df: pd.DataFrame,
                        analysis_types: Optional[List[MLIntelligenceType]] = None) -> Dict[str, MLIntelligenceResult]:
        """
        Ejecuta análisis de inteligencia ML complementario.
        
        Args:
            df: DataFrame con estrategias y métricas
            analysis_types: Tipos de análisis a ejecutar (None = todos)
            
        Returns:
            Diccionario con resultados de cada tipo de análisis
        """
        try:
            if analysis_types is None:
                analysis_types = list(MLIntelligenceType)
            
            results = {}
            
            for analysis_type in analysis_types:
                logger.info(f"🔍 Ejecutando {analysis_type.value}...")
                
                if analysis_type == MLIntelligenceType.PERFORMANCE_PREDICTOR:
                    results[analysis_type.value] = self._predict_performance(df)
                
                elif analysis_type == MLIntelligenceType.QUALITY_CLASSIFIER:
                    results[analysis_type.value] = self._classify_quality(df)
                
                elif analysis_type == MLIntelligenceType.RISK_PROFILE_ANALYZER:
                    results[analysis_type.value] = self._analyze_risk_profiles(df)
                
                elif analysis_type == MLIntelligenceType.CONSISTENCY_VALIDATOR:
                    results[analysis_type.value] = self._validate_consistency(df)
                
                elif analysis_type == MLIntelligenceType.ADAPTIVE_THRESHOLD_OPTIMIZER:
                    results[analysis_type.value] = self._optimize_thresholds(df)
            
            # Cache resultados
            self.cached_results.update(results)
            
            logger.info(f"✅ Análisis de inteligencia ML completado: {len(results)} tipos")
            return results
            
        except Exception as e:
            self.logger.error(f"Error en enhance_analysis: {e}")
            return {}
    
    def _predict_performance(self, df: pd.DataFrame) -> MLIntelligenceResult:
        """
        Predice rendimiento OOS basado en métricas IS.
        
        Args:
            df: DataFrame con métricas IS/OOS
            
        Returns:
            MLIntelligenceResult con predicciones
        """
        try:
            # Identificar métricas IS/OOS
            is_metrics = [col for col in df.columns if '_IS' in col or '(IS)' in col]
            oos_metrics = [col for col in df.columns if '_OOS' in col or '(OOS)' in col]
            
            if not is_metrics or not oos_metrics:
                return MLIntelligenceResult(
                    analysis_type=MLIntelligenceType.PERFORMANCE_PREDICTOR,
                    insights=["No se encontraron métricas IS/OOS para predicción"],
                    recommendations=["Asegurar que los datos incluyan métricas IS/OOS"]
                )
            
            # Usar la primera métrica OOS disponible como target
            target_metric = oos_metrics[0]
            target_col = target_metric.replace('_OOS', '_IS').replace('(OOS)', '(IS)')
            
            if target_col not in is_metrics:
                target_col = is_metrics[0]  # Fallback
            
            # Preparar datos
            X = df[is_metrics].copy()
            y = df[target_metric]
            
            # Limpiar datos
            X = X.replace([np.inf, -np.inf], np.nan)
            X = X.fillna(X.median())
            y = y.replace([np.inf, -np.inf], np.nan)
            y = y.fillna(y.median())
            
            if len(X.dropna()) < 10:
                return MLIntelligenceResult(
                    analysis_type=MLIntelligenceType.PERFORMANCE_PREDICTOR,
                    insights=["Datos insuficientes para predicción"],
                    recommendations=["Se necesitan al menos 10 estrategias con datos completos"]
                )
            
            # Entrenar modelo
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Validación temporal
            tscv = TimeSeriesSplit(n_splits=3)
            cv_scores = cross_val_score(model, X, y, cv=tscv, scoring='r2')
            
            # Entrenar modelo final
            model.fit(X, y)
            predictions = model.predict(X)
            
            # Calcular métricas
            r2 = r2_score(y, predictions)
            mae = mean_absolute_error(y, predictions)
            
            # Análisis SHAP si está habilitado
            shap_values = None
            if self.enable_shap:
                try:
                    explainer = shap.TreeExplainer(model)
                    shap_values = explainer.shap_values(X)
                except Exception as e:
                    logger.warning(f"Error en análisis SHAP: {e}")
            
            # Generar insights
            insights = [
                f"Modelo de predicción entrenado con {len(X)} estrategias",
                f"R² score: {r2:.3f}",
                f"MAE: {mae:.3f}",
                f"Target: {target_metric}",
                f"Features: {len(is_metrics)} métricas IS"
            ]
            
            if r2 > 0.7:
                insights.append("✅ Predicción confiable")
            elif r2 > 0.5:
                insights.append("🟡 Predicción moderadamente confiable")
            else:
                insights.append("⚠️ Predicción poco confiable")
            
            recommendations = [
                "Usar predicciones solo como indicador complementario",
                "Validar con walk-forward analysis",
                "Considerar múltiples métricas objetivo"
            ]
            
            return MLIntelligenceResult(
                analysis_type=MLIntelligenceType.PERFORMANCE_PREDICTOR,
                predictions=pd.Series(predictions, index=df.index),
                model_performance={'r2': r2, 'mae': mae, 'cv_mean': cv_scores.mean()},
                insights=insights,
                recommendations=recommendations,
                confidence_scores=pd.Series(cv_scores, index=df.index) if self.enable_confidence_scores else None
            )
            
        except Exception as e:
            self.logger.error(f"Error en _predict_performance: {e}")
            return MLIntelligenceResult(
                analysis_type=MLIntelligenceType.PERFORMANCE_PREDICTOR,
                insights=[f"Error en predicción: {e}"],
                recommendations=["Revisar datos de entrada"]
            )
    
    def _classify_quality(self, df: pd.DataFrame) -> MLIntelligenceResult:
        """
        Clasifica calidad de estrategias usando ML.
        
        Args:
            df: DataFrame con estrategias
            
        Returns:
            MLIntelligenceResult con clasificaciones
        """
        try:
            # Identificar métricas de calidad
            quality_metrics = [
                'Profit_factor', 'Sharpe_Ratio', 'Max_DD_%', 
                'Win_Rate_%', 'Total_Trades', 'CAGR'
            ]
            
            available_metrics = [col for col in quality_metrics if col in df.columns]
            
            if len(available_metrics) < 3:
                return MLIntelligenceResult(
                    analysis_type=MLIntelligenceType.QUALITY_CLASSIFIER,
                    insights=["Métricas insuficientes para clasificación"],
                    recommendations=["Se necesitan al menos 3 métricas de calidad"]
                )
            
            # Preparar datos
            X = df[available_metrics].copy()
            X = X.replace([np.inf, -np.inf], np.nan)
            X = X.fillna(X.median())
            
            if len(X.dropna()) < 10:
                return MLIntelligenceResult(
                    analysis_type=MLIntelligenceType.QUALITY_CLASSIFIER,
                    insights=["Datos insuficientes para clasificación"],
                    recommendations=["Se necesitan al menos 10 estrategias"]
                )
            
            # Crear etiquetas de calidad basadas en percentiles
            quality_scores = []
            for idx, row in X.iterrows():
                score = 0
                if 'Profit_factor' in available_metrics and row['Profit_factor'] > 1.5:
                    score += 1
                if 'Sharpe_Ratio' in available_metrics and row['Sharpe_Ratio'] > 1.0:
                    score += 1
                if 'Max_DD_%' in available_metrics and abs(row['Max_DD_%']) < 20:
                    score += 1
                if 'Win_Rate_%' in available_metrics and row['Win_Rate_%'] > 50:
                    score += 1
                quality_scores.append(score)
            
            # Clasificar en 3 categorías
            quality_labels = []
            for score in quality_scores:
                if score >= 3:
                    quality_labels.append('High')
                elif score >= 2:
                    quality_labels.append('Medium')
                else:
                    quality_labels.append('Low')
            
            # Entrenar clasificador
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            # Validación cruzada
            cv_scores = cross_val_score(model, X, quality_labels, cv=3, scoring='accuracy')
            
            # Entrenar modelo final
            model.fit(X, quality_labels)
            predictions = model.predict(X)
            
            # Calcular métricas
            accuracy = cv_scores.mean()
            
            # Generar insights
            quality_dist = pd.Series(quality_labels).value_counts()
            insights = [
                f"Clasificación de calidad completada",
                f"Accuracy: {accuracy:.3f}",
                f"Distribución: {dict(quality_dist)}",
                f"Features: {len(available_metrics)} métricas"
            ]
            
            recommendations = [
                "Usar clasificación como filtro complementario",
                "Validar con análisis manual de casos extremos",
                "Considerar métricas específicas del mercado"
            ]
            
            return MLIntelligenceResult(
                analysis_type=MLIntelligenceType.QUALITY_CLASSIFIER,
                classifications=pd.Series(predictions, index=df.index),
                model_performance={'accuracy': accuracy},
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error en _classify_quality: {e}")
            return MLIntelligenceResult(
                analysis_type=MLIntelligenceType.QUALITY_CLASSIFIER,
                insights=[f"Error en clasificación: {e}"],
                recommendations=["Revisar métricas de calidad"]
            )
    
    def _analyze_risk_profiles(self, df: pd.DataFrame) -> MLIntelligenceResult:
        """
        Analiza perfiles de riesgo usando clustering.
        
        Args:
            df: DataFrame con estrategias
            
        Returns:
            MLIntelligenceResult con perfiles de riesgo
        """
        try:
            # Métricas de riesgo
            risk_metrics = ['Max_DD_%', 'VaR_95%', 'CVaR_95%', 'Ulcer_Index_%']
            available_risk_metrics = [col for col in risk_metrics if col in df.columns]
            
            if len(available_risk_metrics) < 2:
                return MLIntelligenceResult(
                    analysis_type=MLIntelligenceType.RISK_PROFILE_ANALYZER,
                    insights=["Métricas de riesgo insuficientes"],
                    recommendations=["Se necesitan al menos 2 métricas de riesgo"]
                )
            
            # Preparar datos
            X = df[available_risk_metrics].copy()
            X = X.replace([np.inf, -np.inf], np.nan)
            X = X.fillna(X.median())
            
            if len(X.dropna()) < 10:
                return MLIntelligenceResult(
                    analysis_type=MLIntelligenceType.RISK_PROFILE_ANALYZER,
                    insights=["Datos insuficientes para análisis de riesgo"],
                    recommendations=["Se necesitan al menos 10 estrategias"]
                )
            
            # Normalizar datos
            X_scaled = self.scaler.fit_transform(X)
            
            # Clustering de perfiles de riesgo
            n_clusters = min(3, len(X_scaled) // 3)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            risk_labels = kmeans.fit_predict(X_scaled)
            
            # Analizar características de cada cluster
            risk_profiles = {}
            for i in range(n_clusters):
                cluster_mask = risk_labels == i
                cluster_data = X[cluster_mask]
                
                profile = {
                    'size': int(cluster_mask.sum()),
                    'avg_metrics': cluster_data.mean().to_dict(),
                    'risk_level': self._determine_risk_level(cluster_data)
                }
                risk_profiles[f'profile_{i}'] = profile
            
            # Generar insights
            insights = [
                f"Análisis de perfiles de riesgo completado",
                f"Clusters identificados: {n_clusters}",
                f"Métricas analizadas: {len(available_risk_metrics)}"
            ]
            
            for profile_name, profile in risk_profiles.items():
                insights.append(f"{profile_name}: {profile['size']} estrategias - {profile['risk_level']}")
            
            recommendations = [
                "Usar perfiles para diversificación de riesgo",
                "Considerar correlación entre perfiles",
                "Validar estabilidad temporal de perfiles"
            ]
            
            return MLIntelligenceResult(
                analysis_type=MLIntelligenceType.RISK_PROFILE_ANALYZER,
                risk_profiles=risk_profiles,
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error en _analyze_risk_profiles: {e}")
            return MLIntelligenceResult(
                analysis_type=MLIntelligenceType.RISK_PROFILE_ANALYZER,
                insights=[f"Error en análisis de riesgo: {e}"],
                recommendations=["Revisar métricas de riesgo"]
            )
    
    def _validate_consistency(self, df: pd.DataFrame) -> MLIntelligenceResult:
        """
        Valida consistencia temporal usando ML.
        
        Args:
            df: DataFrame con estrategias
            
        Returns:
            MLIntelligenceResult con scores de consistencia
        """
        try:
            # Identificar métricas IS/OOS
            is_metrics = [col for col in df.columns if '_IS' in col or '(IS)' in col]
            oos_metrics = [col for col in df.columns if '_OOS' in col or '(OOS)' in col]
            
            if not is_metrics or not oos_metrics:
                return MLIntelligenceResult(
                    analysis_type=MLIntelligenceType.CONSISTENCY_VALIDATOR,
                    insights=["No se encontraron métricas IS/OOS"],
                    recommendations=["Asegurar datos IS/OOS para validación"]
                )
            
            # Calcular scores de consistencia
            consistency_scores = []
            for idx, row in df.iterrows():
                score = 0
                valid_pairs = 0
                
                for is_metric in is_metrics:
                    oos_metric = is_metric.replace('_IS', '_OOS').replace('(IS)', '(OOS)')
                    if oos_metric in oos_metrics:
                        is_val = row[is_metric]
                        oos_val = row[oos_metric]
                        
                        if pd.notna(is_val) and pd.notna(oos_val):
                            # Calcular correlación de ranking
                            if is_val > 0 and oos_val > 0:
                                consistency = min(is_val, oos_val) / max(is_val, oos_val)
                                score += consistency
                                valid_pairs += 1
                
                if valid_pairs > 0:
                    consistency_scores.append(score / valid_pairs)
                else:
                    consistency_scores.append(np.nan)
            
            consistency_series = pd.Series(consistency_scores, index=df.index)
            
            # Clasificar consistencia
            high_consistency = consistency_series > 0.8
            medium_consistency = (consistency_series > 0.6) & (consistency_series <= 0.8)
            low_consistency = consistency_series <= 0.6
            
            # Generar insights
            insights = [
                f"Validación de consistencia completada",
                f"Estrategias con alta consistencia: {high_consistency.sum()}",
                f"Estrategias con consistencia media: {medium_consistency.sum()}",
                f"Estrategias con baja consistencia: {low_consistency.sum()}",
                f"Consistencia promedio: {consistency_series.mean():.3f}"
            ]
            
            recommendations = [
                "Priorizar estrategias con alta consistencia",
                "Investigar causas de baja consistencia",
                "Considerar walk-forward analysis para validación"
            ]
            
            return MLIntelligenceResult(
                analysis_type=MLIntelligenceType.CONSISTENCY_VALIDATOR,
                consistency_scores=consistency_series,
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error en _validate_consistency: {e}")
            return MLIntelligenceResult(
                analysis_type=MLIntelligenceType.CONSISTENCY_VALIDATOR,
                insights=[f"Error en validación de consistencia: {e}"],
                recommendations=["Revisar datos IS/OOS"]
            )
    
    def _optimize_thresholds(self, df: pd.DataFrame) -> MLIntelligenceResult:
        """
        Optimiza umbrales dinámicamente usando ML.
        
        Args:
            df: DataFrame con estrategias
            
        Returns:
            MLIntelligenceResult con umbrales optimizados
        """
        try:
            # Métricas clave para optimización
            key_metrics = ['Profit_factor', 'Sharpe_Ratio', 'Max_DD_%', 'Win_Rate_%']
            available_metrics = [col for col in key_metrics if col in df.columns]
            
            if len(available_metrics) < 2:
                return MLIntelligenceResult(
                    analysis_type=MLIntelligenceType.ADAPTIVE_THRESHOLD_OPTIMIZER,
                    insights=["Métricas insuficientes para optimización"],
                    recommendations=["Se necesitan al menos 2 métricas clave"]
                )
            
            # Calcular umbrales optimizados basados en percentiles
            optimized_thresholds = {}
            
            for metric in available_metrics:
                values = df[metric].dropna()
                if len(values) > 0:
                    # Umbral basado en percentil 75 para métricas positivas
                    if metric in ['Profit_factor', 'Sharpe_Ratio', 'Win_Rate_%']:
                        threshold = values.quantile(0.75)
                    # Umbral basado en percentil 25 para métricas de riesgo
                    elif metric in ['Max_DD_%']:
                        threshold = values.quantile(0.25)
                    else:
                        threshold = values.median()
                    
                    optimized_thresholds[metric] = float(threshold)
            
            # Generar insights
            insights = [
                f"Optimización de umbrales completada",
                f"Umbrales optimizados: {len(optimized_thresholds)}"
            ]
            
            for metric, threshold in optimized_thresholds.items():
                insights.append(f"{metric}: {threshold:.3f}")
            
            recommendations = [
                "Usar umbrales optimizados como filtros dinámicos",
                "Validar umbrales con datos históricos",
                "Ajustar según condiciones de mercado"
            ]
            
            return MLIntelligenceResult(
                analysis_type=MLIntelligenceType.ADAPTIVE_THRESHOLD_OPTIMIZER,
                optimized_thresholds=optimized_thresholds,
                insights=insights,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error en _optimize_thresholds: {e}")
            return MLIntelligenceResult(
                analysis_type=MLIntelligenceType.ADAPTIVE_THRESHOLD_OPTIMIZER,
                insights=[f"Error en optimización de umbrales: {e}"],
                recommendations=["Revisar métricas disponibles"]
            )
    
    def _determine_risk_level(self, cluster_data: pd.DataFrame) -> str:
        """Determina el nivel de riesgo de un cluster."""
        try:
            # Calcular score de riesgo promedio
            risk_score = 0
            
            if 'Max_DD_%' in cluster_data.columns:
                avg_mdd = abs(cluster_data['Max_DD_%'].mean())
                if avg_mdd > 20:
                    risk_score += 2
                elif avg_mdd > 10:
                    risk_score += 1
            
            if 'VaR_95%' in cluster_data.columns:
                avg_var = abs(cluster_data['VaR_95%'].mean())
                if avg_var > 15:
                    risk_score += 2
                elif avg_var > 8:
                    risk_score += 1
            
            if risk_score >= 3:
                return "Alto"
            elif risk_score >= 1:
                return "Medio"
            else:
                return "Bajo"
                
        except Exception:
            return "Desconocido"
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de todos los análisis ejecutados."""
        try:
            summary = {
                'total_analyses': len(self.cached_results),
                'analysis_types': list(self.cached_results.keys()),
                'timestamp': datetime.now().isoformat()
            }
            
            for analysis_type, result in self.cached_results.items():
                if hasattr(result, 'model_performance') and result.model_performance:
                    summary[f'{analysis_type}_performance'] = result.model_performance
                
                if hasattr(result, 'insights') and result.insights:
                    summary[f'{analysis_type}_insights'] = result.insights[:3]  # Top 3
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error en get_summary: {e}")
            return {'error': str(e)}


# Función de conveniencia para integración con core engine
def enhance_core_analysis_with_ml(df: pd.DataFrame, 
                                 analysis_types: Optional[List[MLIntelligenceType]] = None,
                                 config: Optional[Dict[str, Any]] = None) -> Dict[str, MLIntelligenceResult]:
    """
    Función de conveniencia para integrar ML con el core engine.
    
    Args:
        df: DataFrame con estrategias
        analysis_types: Tipos de análisis a ejecutar
        config: Configuración opcional
        
    Returns:
        Diccionario con resultados de inteligencia ML
    """
    enhancer = MLIntelligenceEnhancer(config=config)
    return enhancer.enhance_analysis(df, analysis_types) 