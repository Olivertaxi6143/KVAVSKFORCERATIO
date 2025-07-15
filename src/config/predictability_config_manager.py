"""
Gestor de configuración para predictibilidad con capacidades de IA.
Integrado con ConfigManagerEnhanced y con ajuste automático de umbrales.
"""

import json
import os
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

# Importar ConfigManagerEnhanced para integración
from src.core.config.config_manager import ConfigManagerEnhanced

logger = logging.getLogger(__name__)

@dataclass
class PredictabilityThresholds:
    """Umbrales de predictibilidad con validación dinámica."""
    consistency: Dict[str, float]
    temporal_robustness: Dict[str, float]
    overfitting_detection: Dict[str, float]
    stability: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "consistency": self.consistency,
            "temporal_robustness": self.temporal_robustness,
            "overfitting_detection": self.overfitting_detection,
            "stability": self.stability
        }

class PredictabilityConfigManager:
    """
    Gestor de configuración para parámetros de predictibilidad con IA.
    Integrado con ConfigManagerEnhanced y capacidades de auto-tuning.
    """
    
    def __init__(self, config_path: Optional[str] = None, 
                 main_config_manager: Optional[ConfigManagerEnhanced] = None):
        """
        Inicializa el gestor de configuración.
        
        Args:
            config_path: Ruta al archivo de configuración JSON
            main_config_manager: Instancia del ConfigManagerEnhanced principal
        """
        self.config_path = config_path or self._get_default_config_path()
        self.main_config_manager = main_config_manager or ConfigManagerEnhanced()
        self.config = self._load_config()
        self._validate_config()
        
        # Capacidades de IA
        self.ai_enabled = self.config.get("ai_settings", {}).get("enable_ai", True)
        self.auto_tuning_enabled = self.config.get("ai_settings", {}).get("enable_auto_tuning", True)
        self.clustering_enabled = self.config.get("ai_settings", {}).get("enable_clustering", True)
        
        # Historial de rendimiento para ajuste dinámico
        self.performance_history = []
        self.threshold_adjustments = []
        
        # Modelos de IA
        self._scaler = StandardScaler()
        self._outlier_detector = None
        self._clustering_model = None
        
        if self.ai_enabled:
            self._initialize_ai_models()
    
    def _get_default_config_path(self) -> str:
        """Obtiene la ruta por defecto del archivo de configuración."""
        current_dir = Path(__file__).parent
        return str(current_dir / "predictability_config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carga la configuración desde archivo JSON o ConfigManagerEnhanced.
        
        Returns:
            Diccionario con la configuración
        """
        try:
            # Intentar cargar desde archivo específico
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Configuración de predictibilidad cargada desde: {self.config_path}")
            else:
                # Cargar desde ConfigManagerEnhanced
                main_config = self.main_config_manager.get_config()
                config = self._extract_predictability_config(main_config)
                logger.info("Configuración de predictibilidad cargada desde ConfigManagerEnhanced")
            
            return config
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return self._get_default_config()
    
    def _extract_predictability_config(self, main_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae configuración de predictibilidad del config principal."""
        # Buscar sección de predictibilidad en config principal
        if "predictability" in main_config:
            return main_config["predictability"]
        
        # Si no existe, crear configuración por defecto
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuración por defecto mejorada con IA."""
        return {
            "predictability_thresholds": {
                "consistency": {
                    "min_is_oos_ratio": 0.7,
                    "max_is_oos_ratio": 1.3,
                    "excellent_threshold": 0.8,
                    "good_threshold": 0.5,
                    "adaptive_adjustment": True
                },
                "temporal_robustness": {
                    "min_total_months": 12,
                    "min_trades": 50,
                    "preferred_months": 24,
                    "preferred_trades": 200,
                    "min_months_basic": 6,
                    "min_trades_basic": 25,
                    "adaptive_adjustment": True
                },
                "overfitting_detection": {
                    "max_dd_threshold": 20.0,
                    "min_recovery_factor": 1.0,
                    "max_profit_factor_is": 3.0,
                    "oos_degradation_threshold": 0.7,
                    "sharpe_degradation_threshold": 0.6,
                    "dd_multiplier_threshold": 1.5,
                    "adaptive_adjustment": True
                },
                "stability": {
                    "min_calmar_ratio": 1.0,
                    "min_sqn": 1.0,
                    "min_sortino": 1.0,
                    "var_threshold_low": 0.05,
                    "var_threshold_medium": 0.10,
                    "cvar_threshold_low": 0.10,
                    "cvar_threshold_medium": 0.20,
                    "adaptive_adjustment": True
                }
            },
            "scoring_weights": {
                "is_oos_consistency": 0.30,
                "temporal_robustness": 0.25,
                "overfitting_detection": 0.25,
                "stability_score": 0.20
            },
            "ai_settings": {
                "enable_ai": True,
                "enable_auto_tuning": True,
                "enable_clustering": True,
                "enable_outlier_detection": True,
                "min_data_points_for_ai": 50,
                "auto_tuning_frequency": 100,  # Ajustar cada 100 estrategias
                "clustering_n_clusters": 3,
                "outlier_contamination": 0.1
            },
            "validation": {
                "enable_cache": True,
                "max_cache_size": 1000,
                "enable_numeric_validation": True,
                "enable_outlier_detection": True,
                "outlier_threshold": 3.0
            },
            "logging": {
                "level": "INFO",
                "enable_debug": False,
                "log_cache_hits": True,
                "log_ai_adjustments": True
            }
        }
    
    def _initialize_ai_models(self):
        """Inicializa modelos de IA para análisis avanzado."""
        try:
            if self.clustering_enabled:
                self._clustering_model = KMeans(
                    n_clusters=self.config["ai_settings"]["clustering_n_clusters"],
                    random_state=42
                )
            
            if self.config["ai_settings"]["enable_outlier_detection"]:
                contamination = self.config["ai_settings"]["outlier_contamination"]
                self._outlier_detector = IsolationForest(
                    contamination=contamination,
                    random_state=42
                )
            
            logger.info("✅ Modelos de IA inicializados correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando modelos de IA: {e}")
            self.ai_enabled = False
    
    def _validate_config(self):
        """Valida la configuración cargada."""
        required_sections = [
            "predictability_thresholds",
            "scoring_weights", 
            "validation",
            "logging"
        ]
        
        for section in required_sections:
            if section not in self.config:
                logger.warning(f"Sección faltante en configuración: {section}")
                self.config[section] = self._get_default_config()[section]
        
        # Validar pesos de scoring sumen 1.0
        weights = self.config.get("scoring_weights", {})
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Pesos de scoring no suman 1.0: {total_weight}")
            # Normalizar pesos
            for key in weights:
                weights[key] /= total_weight
    
    def get_thresholds(self, section: str) -> Dict[str, Any]:
        """
        Obtiene umbrales de una sección específica con ajuste dinámico.
        
        Args:
            section: Nombre de la sección (consistency, temporal_robustness, etc.)
            
        Returns:
            Diccionario con umbrales de la sección
        """
        thresholds = self.config.get("predictability_thresholds", {})
        section_thresholds = thresholds.get(section, {})
        
        # Aplicar ajustes dinámicos si están habilitados
        if self.ai_enabled and section_thresholds.get("adaptive_adjustment", False):
            section_thresholds = self._apply_dynamic_adjustments(section, section_thresholds)
        
        return section_thresholds
    
    def _apply_dynamic_adjustments(self, section: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica ajustes dinámicos basados en datos históricos."""
        if len(self.performance_history) < self.config["ai_settings"]["min_data_points_for_ai"]:
            return thresholds
        
        try:
            # Extraer métricas relevantes del historial
            relevant_metrics = self._extract_section_metrics(section)
            
            if len(relevant_metrics) < 10:  # Mínimo de datos para ajuste
                return thresholds
            
            # Calcular estadísticas de los datos históricos
            metrics_array = np.array(relevant_metrics)
            mean_val = np.mean(metrics_array)
            std_val = np.std(metrics_array)
            
            # Ajustar umbrales basándose en la distribución histórica
            adjusted_thresholds = thresholds.copy()
            
            if section == "consistency":
                # Ajustar ratios IS/OOS basándose en la media histórica
                if "min_is_oos_ratio" in thresholds and "max_is_oos_ratio" in thresholds:
                    current_range = thresholds["max_is_oos_ratio"] - thresholds["min_is_oos_ratio"]
                    new_center = max(0.5, min(1.5, float(mean_val)))  # Limitar entre 0.5 y 1.5
                    new_range = max(0.2, min(0.8, float(current_range)))  # Limitar rango
                    
                    adjusted_thresholds["min_is_oos_ratio"] = max(0.3, new_center - new_range/2)
                    adjusted_thresholds["max_is_oos_ratio"] = min(2.0, new_center + new_range/2)
            
            elif section == "temporal_robustness":
                # Ajustar umbrales de tiempo basándose en la distribución
                if "min_total_months" in thresholds:
                    adjusted_thresholds["min_total_months"] = max(3, int(mean_val * 0.8))
                if "min_trades" in thresholds:
                    adjusted_thresholds["min_trades"] = max(10, int(mean_val * 0.8))
            
            elif section == "overfitting_detection":
                # Ajustar umbrales de overfitting basándose en outliers
                if self._outlier_detector is not None:
                    outlier_scores = self._outlier_detector.fit_predict(metrics_array.reshape(-1, 1))
                    outlier_ratio = np.sum(outlier_scores == -1) / len(outlier_scores)
                    
                    if outlier_ratio > 0.2:  # Muchos outliers
                        adjusted_thresholds["max_dd_threshold"] *= 0.9  # Más estricto
                        adjusted_thresholds["oos_degradation_threshold"] *= 0.9
            
            elif section == "stability":
                # Ajustar umbrales de estabilidad basándose en la volatilidad histórica
                if std_val > 0.5:  # Alta volatilidad
                    adjusted_thresholds["min_calmar_ratio"] *= 0.8
                    adjusted_thresholds["min_sqn"] *= 0.8
            
            # Registrar ajuste
            if self.config["logging"]["log_ai_adjustments"]:
                logger.info(f"🔧 Ajuste dinámico aplicado a {section}: {len(relevant_metrics)} datos históricos")
            
            return adjusted_thresholds
            
        except Exception as e:
            logger.error(f"Error aplicando ajustes dinámicos a {section}: {e}")
            return thresholds
    
    def _extract_section_metrics(self, section: str) -> List[float]:
        """Extrae métricas relevantes para una sección del historial de rendimiento."""
        relevant_metrics = []
        
        for performance in self.performance_history:
            if section == "consistency":
                if "is_oos_ratio" in performance:
                    relevant_metrics.append(performance["is_oos_ratio"])
            elif section == "temporal_robustness":
                if "total_months" in performance:
                    relevant_metrics.append(performance["total_months"])
                if "total_trades" in performance:
                    relevant_metrics.append(performance["total_trades"])
            elif section == "overfitting_detection":
                if "max_dd" in performance:
                    relevant_metrics.append(performance["max_dd"])
            elif section == "stability":
                if "calmar_ratio" in performance:
                    relevant_metrics.append(performance["calmar_ratio"])
        
        return relevant_metrics
    
    def update_performance_history(self, strategy_performance: Dict[str, Any]):
        """
        Actualiza el historial de rendimiento para ajuste dinámico.
        
        Args:
            strategy_performance: Diccionario con métricas de rendimiento de una estrategia
        """
        if not self.ai_enabled:
            return
        
        try:
            self.performance_history.append(strategy_performance)
            
            # Verificar si es momento de ajustar umbrales
            if len(self.performance_history) % self.config["ai_settings"]["auto_tuning_frequency"] == 0:
                self._perform_auto_tuning()
                
        except Exception as e:
            logger.error(f"Error actualizando historial de rendimiento: {e}")
    
    def _perform_auto_tuning(self):
        """Realiza ajuste automático de umbrales basado en datos históricos."""
        if len(self.performance_history) < self.config["ai_settings"]["min_data_points_for_ai"]:
            return
        
        try:
            logger.info(f"🤖 Iniciando auto-tuning con {len(self.performance_history)} datos históricos")
            
            # Extraer características para clustering
            features = self._extract_features_for_clustering()
            
            if len(features) < 10:
                return
            
            # Aplicar clustering para identificar patrones
            if self._clustering_model is not None:
                cluster_labels = self._clustering_model.fit_predict(features)
                
                # Analizar clusters para sugerir ajustes
                suggestions = self._analyze_clusters_for_suggestions(features, cluster_labels)
                
                # Aplicar sugerencias si son válidas
                if suggestions:
                    self._apply_ai_suggestions(suggestions)
            
            logger.info("✅ Auto-tuning completado")
            
        except Exception as e:
            logger.error(f"Error en auto-tuning: {e}")
    
    def _extract_features_for_clustering(self) -> np.ndarray:
        """Extrae características para clustering de predictibilidad."""
        features = []
        
        for performance in self.performance_history:
            feature_vector = []
            
            # Consistencia IS/OOS
            feature_vector.append(performance.get("is_oos_ratio", 1.0))
            
            # Robustez temporal
            feature_vector.append(performance.get("total_months", 12))
            feature_vector.append(performance.get("total_trades", 50))
            
            # Detección de overfitting
            feature_vector.append(performance.get("max_dd", 20.0))
            feature_vector.append(performance.get("oos_degradation", 0.7))
            
            # Estabilidad
            feature_vector.append(performance.get("calmar_ratio", 1.0))
            feature_vector.append(performance.get("sqn", 1.0))
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def _analyze_clusters_for_suggestions(self, features: np.ndarray, cluster_labels: np.ndarray) -> Dict[str, Any]:
        """Analiza clusters para generar sugerencias de ajuste."""
        suggestions = {}
        
        try:
            n_clusters = len(np.unique(cluster_labels))
            
            for cluster_id in range(n_clusters):
                cluster_mask = cluster_labels == cluster_id
                cluster_features = features[cluster_mask]
                
                if len(cluster_features) < 5:  # Cluster muy pequeño
                    continue
                
                # Analizar características del cluster
                cluster_mean = np.mean(cluster_features, axis=0)
                cluster_std = np.std(cluster_features, axis=0)
                
                # Generar sugerencias basadas en el análisis del cluster
                cluster_suggestions = self._generate_cluster_suggestions(cluster_id, cluster_mean, cluster_std)
                
                if cluster_suggestions:
                    suggestions[f"cluster_{cluster_id}"] = cluster_suggestions
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error analizando clusters: {e}")
            return {}
    
    def _generate_cluster_suggestions(self, cluster_id: int, cluster_mean: np.ndarray, cluster_std: np.ndarray) -> Dict[str, Any]:
        """Genera sugerencias específicas basadas en el análisis de un cluster."""
        suggestions = {}
        
        try:
            # Interpretar características del cluster
            is_oos_ratio = cluster_mean[0]
            total_months = cluster_mean[1]
            total_trades = cluster_mean[2]
            max_dd = cluster_mean[3]
            oos_degradation = cluster_mean[4]
            calmar_ratio = cluster_mean[5]
            sqn = cluster_mean[6]
            
            # Generar sugerencias basadas en patrones detectados
            if is_oos_ratio < 0.6:
                suggestions["consistency"] = {
                    "action": "tighten_thresholds",
                    "reason": f"Cluster {cluster_id} muestra baja consistencia IS/OOS ({is_oos_ratio:.2f})",
                    "suggested_adjustment": "Reducir umbrales de consistencia"
                }
            
            if total_months < 8 or total_trades < 30:
                suggestions["temporal_robustness"] = {
                    "action": "increase_minimums",
                    "reason": f"Cluster {cluster_id} muestra poca robustez temporal",
                    "suggested_adjustment": "Aumentar umbrales mínimos de tiempo/trades"
                }
            
            if max_dd > 25 or oos_degradation < 0.6:
                suggestions["overfitting_detection"] = {
                    "action": "tighten_overfitting_thresholds",
                    "reason": f"Cluster {cluster_id} muestra signos de overfitting",
                    "suggested_adjustment": "Hacer más estrictos los umbrales de overfitting"
                }
            
            if calmar_ratio < 0.8 or sqn < 0.8:
                suggestions["stability"] = {
                    "action": "adjust_stability_thresholds",
                    "reason": f"Cluster {cluster_id} muestra baja estabilidad",
                    "suggested_adjustment": "Ajustar umbrales de estabilidad"
                }
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generando sugerencias para cluster {cluster_id}: {e}")
            return {}
    
    def _apply_ai_suggestions(self, suggestions: Dict[str, Any]):
        """Aplica sugerencias de IA a la configuración."""
        try:
            for cluster_id, cluster_suggestions in suggestions.items():
                for section, suggestion in cluster_suggestions.items():
                    if suggestion["action"] == "tighten_thresholds":
                        self._tighten_thresholds(section)
                    elif suggestion["action"] == "increase_minimums":
                        self._increase_minimums(section)
                    elif suggestion["action"] == "tighten_overfitting_thresholds":
                        self._tighten_overfitting_thresholds(section)
                    elif suggestion["action"] == "adjust_stability_thresholds":
                        self._adjust_stability_thresholds(section)
                    
                    logger.info(f"🤖 Sugerencia aplicada: {suggestion['reason']}")
            
        except Exception as e:
            logger.error(f"Error aplicando sugerencias de IA: {e}")
    
    def _tighten_thresholds(self, section: str):
        """Hace más estrictos los umbrales de una sección."""
        thresholds = self.config["predictability_thresholds"][section]
        
        if section == "consistency":
            thresholds["min_is_oos_ratio"] = max(0.5, thresholds["min_is_oos_ratio"] * 1.1)
            thresholds["max_is_oos_ratio"] = min(1.5, thresholds["max_is_oos_ratio"] * 0.9)
    
    def _increase_minimums(self, section: str):
        """Aumenta los mínimos de una sección."""
        thresholds = self.config["predictability_thresholds"][section]
        
        if section == "temporal_robustness":
            thresholds["min_total_months"] = int(thresholds["min_total_months"] * 1.2)
            thresholds["min_trades"] = int(thresholds["min_trades"] * 1.2)
    
    def _tighten_overfitting_thresholds(self, section: str):
        """Hace más estrictos los umbrales de overfitting."""
        thresholds = self.config["predictability_thresholds"][section]
        
        if section == "overfitting_detection":
            thresholds["max_dd_threshold"] *= 0.9
            thresholds["oos_degradation_threshold"] *= 0.9
    
    def _adjust_stability_thresholds(self, section: str):
        """Ajusta los umbrales de estabilidad."""
        thresholds = self.config["predictability_thresholds"][section]
        
        if section == "stability":
            thresholds["min_calmar_ratio"] *= 0.9
            thresholds["min_sqn"] *= 0.9
    
    def get_scoring_weights(self) -> Dict[str, float]:
        """
        Obtiene pesos de scoring.
        
        Returns:
            Diccionario con pesos de scoring
        """
        return self.config.get("scoring_weights", {})
    
    def get_validation_settings(self) -> Dict[str, Any]:
        """
        Obtiene configuración de validación.
        
        Returns:
            Diccionario con configuración de validación
        """
        return self.config.get("validation", {})
    
    def get_logging_settings(self) -> Dict[str, Any]:
        """
        Obtiene configuración de logging.
        
        Returns:
            Diccionario con configuración de logging
        """
        return self.config.get("logging", {})
    
    def get_ai_settings(self) -> Dict[str, Any]:
        """
        Obtiene configuración de IA.
        
        Returns:
            Diccionario con configuración de IA
        """
        return self.config.get("ai_settings", {})
    
    def update_config(self, updates: Dict[str, Any]):
        """
        Actualiza configuración con nuevos valores.
        
        Args:
            updates: Diccionario con actualizaciones
        """
        def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        
        self.config = deep_update(self.config, updates)
        self._validate_config()
        logger.info("Configuración actualizada")
    
    def save_config(self, path: Optional[str] = None):
        """
        Guarda la configuración actual en archivo JSON.
        
        Args:
            path: Ruta donde guardar (opcional)
        """
        save_path = path or self.config_path
        
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Configuración guardada en: {save_path}")
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        Obtiene toda la configuración.
        
        Returns:
            Diccionario completo con la configuración
        """
        return self.config.copy()
    
    def get_ai_insights(self) -> Dict[str, Any]:
        """
        Obtiene insights de IA basados en datos históricos.
        
        Returns:
            Diccionario con insights y recomendaciones
        """
        if not self.ai_enabled or len(self.performance_history) < 10:
            return {"message": "Insuficientes datos para análisis de IA"}
        
        try:
            insights = {
                "total_strategies_analyzed": len(self.performance_history),
                "ai_enabled": self.ai_enabled,
                "auto_tuning_enabled": self.auto_tuning_enabled,
                "clustering_enabled": self.clustering_enabled,
                "recommendations": []
            }
            
            # Generar recomendaciones basadas en patrones detectados
            if self._clustering_model is not None:
                features = self._extract_features_for_clustering()
                if len(features) >= 10:
                    cluster_labels = self._clustering_model.fit_predict(features)
                    insights["clusters_detected"] = len(np.unique(cluster_labels))
                    
                    # Analizar cada cluster
                    for cluster_id in np.unique(cluster_labels):
                        cluster_mask = cluster_labels == cluster_id
                        cluster_size = np.sum(cluster_mask)
                        cluster_percentage = cluster_size / len(cluster_labels) * 100
                        
                        if cluster_percentage > 30:  # Cluster significativo
                            insights["recommendations"].append({
                                "type": "cluster_analysis",
                                "cluster_id": int(cluster_id),
                                "size": cluster_size,
                                "percentage": cluster_percentage,
                                "description": f"Cluster {cluster_id} representa {cluster_percentage:.1f}% de las estrategias"
                            })
            
            # Detectar outliers
            if self._outlier_detector is not None:
                features = self._extract_features_for_clustering()
                if len(features) >= 10:
                    outlier_scores = self._outlier_detector.fit_predict(features)
                    outlier_count = np.sum(outlier_scores == -1)
                    outlier_percentage = outlier_count / len(outlier_scores) * 100
                    
                    if outlier_percentage > 10:
                        insights["recommendations"].append({
                            "type": "outlier_detection",
                            "outlier_count": outlier_count,
                            "outlier_percentage": outlier_percentage,
                            "description": f"Se detectaron {outlier_count} estrategias atípicas ({outlier_percentage:.1f}%)"
                        })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generando insights de IA: {e}")
            return {"error": str(e)}
    
    def reset_ai_models(self):
        """Reinicia los modelos de IA."""
        try:
            self.performance_history.clear()
            self.threshold_adjustments.clear()
            
            if self._clustering_model is not None:
                self._clustering_model = KMeans(
                    n_clusters=self.config["ai_settings"]["clustering_n_clusters"],
                    random_state=42
                )
            
            if self._outlier_detector is not None:
                contamination = self.config["ai_settings"]["outlier_contamination"]
                self._outlier_detector = IsolationForest(
                    contamination=contamination,
                    random_state=42
                )
            
            logger.info("✅ Modelos de IA reiniciados")
            
        except Exception as e:
            logger.error(f"Error reiniciando modelos de IA: {e}") 