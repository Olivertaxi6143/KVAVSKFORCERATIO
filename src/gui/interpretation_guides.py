"""
Guías de Interpretación Integradas
Proporciona guías de interpretación para métricas y resultados de la GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class InterpretationGuides:
    """
    Guías de interpretación integradas para la GUI.
    
    Características:
    - Interpretación automática de métricas
    - Recomendaciones contextuales
    - Guías visuales de interpretación
    - Alertas inteligentes
    """
    
    def __init__(self):
        """Inicializa las guías de interpretación."""
        self.interpretation_rules = self._initialize_interpretation_rules()
        self.recommendation_templates = self._initialize_recommendation_templates()
        
        logger.info("✅ InterpretationGuides inicializado")
    
    def _initialize_interpretation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa las reglas de interpretación."""
        return {
            "factor_k": {
                "excellent": {"min": 9.2, "max": 10.0, "color": "#FFD700", "badge": "🥇", "description": "Estrategia Elite - Calidad excepcional"},
                "very_good": {"min": 8.2, "max": 9.19, "color": "#C0C0C0", "badge": "🥈", "description": "Estrategia Excellent - Muy alta calidad"},
                "good": {"min": 7.2, "max": 8.19, "color": "#CD7F32", "badge": "🥉", "description": "Estrategia Very Good - Buena calidad"},
                "acceptable": {"min": 6.2, "max": 7.19, "color": "#FFFF00", "badge": "⭐", "description": "Estrategia Good - Calidad aceptable"},
                "poor": {"min": 3.1, "max": 6.19, "color": "#FFA500", "badge": "⚠️", "description": "Estrategia Poor - Calidad baja"},
                "very_poor": {"min": 0.0, "max": 3.09, "color": "#FF0000", "badge": "❌", "description": "Estrategia Very Poor - No recomendada"}
            },
            "predictability": {
                "excellent": {"min": 85.0, "max": 100.0, "color": "#00FF00", "emoji": "🎯", "description": "Predictibilidad Excelente - Alta confiabilidad"},
                "good": {"min": 70.0, "max": 84.9, "color": "#90EE90", "emoji": "🎯", "description": "Predictibilidad Buena - Buena estabilidad"},
                "acceptable": {"min": 60.0, "max": 69.9, "color": "#FFFF00", "emoji": "🎯", "description": "Predictibilidad Aceptable - Estabilidad moderada"},
                "low": {"min": 0.0, "max": 59.9, "color": "#FF0000", "emoji": "🎯", "description": "Predictibilidad Baja - Alto riesgo"}
            },
            "sharpe_ratio": {
                "excellent": {"min": 2.0, "max": 10.0, "color": "#00FF00", "description": "Sharpe Excelente - Rendimiento superior"},
                "very_good": {"min": 1.5, "max": 1.99, "color": "#90EE90", "description": "Sharpe Muy Bueno - Buen rendimiento"},
                "good": {"min": 1.0, "max": 1.49, "color": "#FFFF00", "description": "Sharpe Bueno - Rendimiento aceptable"},
                "acceptable": {"min": 0.5, "max": 0.99, "color": "#FFA500", "description": "Sharpe Aceptable - Rendimiento moderado"},
                "poor": {"min": 0.0, "max": 0.49, "color": "#FF0000", "description": "Sharpe Pobre - Rendimiento bajo"}
            },
            "max_drawdown": {
                "excellent": {"min": 0.0, "max": 10.0, "color": "#00FF00", "description": "Drawdown Excelente - Bajo riesgo"},
                "good": {"min": 10.1, "max": 20.0, "color": "#90EE90", "description": "Drawdown Bueno - Riesgo moderado"},
                "acceptable": {"min": 20.1, "max": 30.0, "color": "#FFFF00", "description": "Drawdown Aceptable - Riesgo alto"},
                "high": {"min": 30.1, "max": 50.0, "color": "#FFA500", "description": "Drawdown Alto - Riesgo muy alto"},
                "very_high": {"min": 50.1, "max": 100.0, "color": "#FF0000", "description": "Drawdown Muy Alto - Riesgo extremo"}
            },
            "cagr": {
                "excellent": {"min": 20.0, "max": 100.0, "color": "#00FF00", "description": "CAGR Excelente - Crecimiento excepcional"},
                "very_good": {"min": 15.0, "max": 19.9, "color": "#90EE90", "description": "CAGR Muy Bueno - Buen crecimiento"},
                "good": {"min": 10.0, "max": 14.9, "color": "#FFFF00", "description": "CAGR Bueno - Crecimiento aceptable"},
                "moderate": {"min": 5.0, "max": 9.9, "color": "#FFA500", "description": "CAGR Moderado - Crecimiento bajo"},
                "low": {"min": 0.0, "max": 4.9, "color": "#FF0000", "description": "CAGR Bajo - Crecimiento mínimo"}
            }
        }
    
    def _initialize_recommendation_templates(self) -> Dict[str, str]:
        """Inicializa las plantillas de recomendaciones."""
        return {
            "factor_k_excellent": "🏆 ESTRATEGIA ELITE: Esta estrategia muestra calidad excepcional. Recomendada para portafolios de alto rendimiento.",
            "factor_k_very_good": "🥈 ESTRATEGIA EXCELLENT: Muy alta calidad con buen potencial. Ideal para diversificación.",
            "factor_k_good": "🥉 ESTRATEGIA VERY GOOD: Buena calidad con potencial de mejora. Considerar para portafolios equilibrados.",
            "factor_k_acceptable": "⭐ ESTRATEGIA GOOD: Calidad aceptable. Revisar otros factores antes de decidir.",
            "factor_k_poor": "⚠️ ESTRATEGIA POOR: Calidad baja. No recomendada sin análisis adicional.",
            "factor_k_very_poor": "❌ ESTRATEGIA VERY POOR: No recomendada. Evitar en portafolios.",
            
            "predictability_excellent": "🎯 PREDICTIBILIDAD EXCELENTE: Alta confiabilidad para datos futuros. Estrategia muy estable.",
            "predictability_good": "🎯 PREDICTIBILIDAD BUENA: Buena estabilidad. Confiable para el futuro.",
            "predictability_acceptable": "🎯 PREDICTIBILIDAD ACEPTABLE: Estabilidad moderada. Monitorear cambios.",
            "predictability_low": "🎯 PREDICTIBILIDAD BAJA: Alto riesgo de inestabilidad. Cautela requerida.",
            
            "sharpe_excellent": "📈 SHARPE EXCELENTE: Rendimiento superior ajustado por riesgo. Estrategia muy eficiente.",
            "sharpe_very_good": "📈 SHARPE MUY BUENO: Buen rendimiento por unidad de riesgo.",
            "sharpe_good": "📈 SHARPE BUENO: Rendimiento aceptable. Considerar para diversificación.",
            "sharpe_acceptable": "📈 SHARPE ACEPTABLE: Rendimiento moderado. Revisar otros factores.",
            "sharpe_poor": "📈 SHARPE POBRE: Rendimiento bajo. No recomendado.",
            
            "drawdown_excellent": "📉 DRAWDOWN EXCELENTE: Riesgo muy bajo. Estrategia muy segura.",
            "drawdown_good": "📉 DRAWDOWN BUENO: Riesgo moderado. Aceptable para la mayoría de portafolios.",
            "drawdown_acceptable": "📉 DRAWDOWN ACEPTABLE: Riesgo alto. Considerar con cautela.",
            "drawdown_high": "📉 DRAWDOWN ALTO: Riesgo muy alto. Solo para inversores experimentados.",
            "drawdown_very_high": "📉 DRAWDOWN MUY ALTO: Riesgo extremo. No recomendado.",
            
            "cagr_excellent": "📊 CAGR EXCELENTE: Crecimiento excepcional. Estrategia de alto potencial.",
            "cagr_very_good": "📊 CAGR MUY BUENO: Buen crecimiento. Estrategia prometedora.",
            "cagr_good": "📊 CAGR BUENO: Crecimiento aceptable. Considerar para diversificación.",
            "cagr_moderate": "📊 CAGR MODERADO: Crecimiento bajo. Revisar otros factores.",
            "cagr_low": "📊 CAGR BAJO: Crecimiento mínimo. No recomendado."
        }
    
    def interpret_factor_k(self, factor_k: float) -> Dict[str, Any]:
        """Interpreta el Factor K y retorna información de categorización."""
        try:
            for category, rules in self.interpretation_rules["factor_k"].items():
                if rules["min"] <= factor_k <= rules["max"]:
                    return {
                        "category": category,
                        "badge": rules["badge"],
                        "color": rules["color"],
                        "description": rules["description"],
                        "recommendation": self.recommendation_templates[f"factor_k_{category}"],
                        "value": factor_k
                    }
            
            # Fallback para valores fuera de rango
            return {
                "category": "unknown",
                "badge": "❓",
                "color": "#808080",
                "description": "Factor K fuera de rango",
                "recommendation": "Valor de Factor K no reconocido. Revisar datos.",
                "value": factor_k
            }
            
        except Exception as e:
            logger.error(f"Error interpretando Factor K {factor_k}: {e}")
            return {
                "category": "error",
                "badge": "❌",
                "color": "#FF0000",
                "description": "Error en interpretación",
                "recommendation": "Error procesando Factor K. Revisar datos.",
                "value": factor_k
            }
    
    def interpret_predictability(self, predictability: float) -> Dict[str, Any]:
        """Interpreta la predictibilidad y retorna información de categorización."""
        try:
            for category, rules in self.interpretation_rules["predictability"].items():
                if rules["min"] <= predictability <= rules["max"]:
                    return {
                        "category": category,
                        "emoji": rules["emoji"],
                        "color": rules["color"],
                        "description": rules["description"],
                        "recommendation": self.recommendation_templates[f"predictability_{category}"],
                        "value": predictability
                    }
            
            # Fallback para valores fuera de rango
            return {
                "category": "unknown",
                "emoji": "❓",
                "color": "#808080",
                "description": "Predictibilidad fuera de rango",
                "recommendation": "Valor de predictibilidad no reconocido. Revisar datos.",
                "value": predictability
            }
            
        except Exception as e:
            logger.error(f"Error interpretando predictibilidad {predictability}: {e}")
            return {
                "category": "error",
                "emoji": "❌",
                "color": "#FF0000",
                "description": "Error en interpretación",
                "recommendation": "Error procesando predictibilidad. Revisar datos.",
                "value": predictability
            }
    
    def interpret_sharpe_ratio(self, sharpe: float) -> Dict[str, Any]:
        """Interpreta el Sharpe Ratio y retorna información de categorización."""
        try:
            for category, rules in self.interpretation_rules["sharpe_ratio"].items():
                if rules["min"] <= sharpe <= rules["max"]:
                    return {
                        "category": category,
                        "color": rules["color"],
                        "description": rules["description"],
                        "recommendation": self.recommendation_templates[f"sharpe_{category}"],
                        "value": sharpe
                    }
            
            # Fallback para valores fuera de rango
            return {
                "category": "unknown",
                "color": "#808080",
                "description": "Sharpe Ratio fuera de rango",
                "recommendation": "Valor de Sharpe Ratio no reconocido. Revisar datos.",
                "value": sharpe
            }
            
        except Exception as e:
            logger.error(f"Error interpretando Sharpe Ratio {sharpe}: {e}")
            return {
                "category": "error",
                "color": "#FF0000",
                "description": "Error en interpretación",
                "recommendation": "Error procesando Sharpe Ratio. Revisar datos.",
                "value": sharpe
            }
    
    def interpret_max_drawdown(self, drawdown: float) -> Dict[str, Any]:
        """Interpreta el Máximo Drawdown y retorna información de categorización."""
        try:
            for category, rules in self.interpretation_rules["max_drawdown"].items():
                if rules["min"] <= drawdown <= rules["max"]:
                    return {
                        "category": category,
                        "color": rules["color"],
                        "description": rules["description"],
                        "recommendation": self.recommendation_templates[f"drawdown_{category}"],
                        "value": drawdown
                    }
            
            # Fallback para valores fuera de rango
            return {
                "category": "unknown",
                "color": "#808080",
                "description": "Máximo Drawdown fuera de rango",
                "recommendation": "Valor de Máximo Drawdown no reconocido. Revisar datos.",
                "value": drawdown
            }
            
        except Exception as e:
            logger.error(f"Error interpretando Máximo Drawdown {drawdown}: {e}")
            return {
                "category": "error",
                "color": "#FF0000",
                "description": "Error en interpretación",
                "recommendation": "Error procesando Máximo Drawdown. Revisar datos.",
                "value": drawdown
            }
    
    def interpret_cagr(self, cagr: float) -> Dict[str, Any]:
        """Interpreta el CAGR y retorna información de categorización."""
        try:
            for category, rules in self.interpretation_rules["cagr"].items():
                if rules["min"] <= cagr <= rules["max"]:
                    return {
                        "category": category,
                        "color": rules["color"],
                        "description": rules["description"],
                        "recommendation": self.recommendation_templates[f"cagr_{category}"],
                        "value": cagr
                    }
            
            # Fallback para valores fuera de rango
            return {
                "category": "unknown",
                "color": "#808080",
                "description": "CAGR fuera de rango",
                "recommendation": "Valor de CAGR no reconocido. Revisar datos.",
                "value": cagr
            }
            
        except Exception as e:
            logger.error(f"Error interpretando CAGR {cagr}: {e}")
            return {
                "category": "error",
                "color": "#FF0000",
                "description": "Error en interpretación",
                "recommendation": "Error procesando CAGR. Revisar datos.",
                "value": cagr
            }
    
    def get_comprehensive_interpretation(self, strategy_data: Dict[str, float]) -> Dict[str, Any]:
        """Obtiene interpretación completa de una estrategia."""
        try:
            interpretations = {}
            
            # Interpretar cada métrica
            if "Factor_K" in strategy_data:
                interpretations["factor_k"] = self.interpret_factor_k(strategy_data["Factor_K"])
            
            if "Predictability" in strategy_data:
                interpretations["predictability"] = self.interpret_predictability(strategy_data["Predictability"])
            
            if "Sharpe_Ratio_IS" in strategy_data:
                interpretations["sharpe"] = self.interpret_sharpe_ratio(strategy_data["Sharpe_Ratio_IS"])
            
            if "Max_Drawdown_IS" in strategy_data:
                interpretations["drawdown"] = self.interpret_max_drawdown(strategy_data["Max_Drawdown_IS"])
            
            if "CAGR_IS" in strategy_data:
                interpretations["cagr"] = self.interpret_cagr(strategy_data["CAGR_IS"])
            
            # Calcular score general
            overall_score = self._calculate_overall_score(interpretations)
            
            # Generar recomendación general
            overall_recommendation = self._generate_overall_recommendation(interpretations)
            
            return {
                "interpretations": interpretations,
                "overall_score": overall_score,
                "overall_recommendation": overall_recommendation,
                "strategy_name": strategy_data.get("Strategy_Name", "Desconocida")
            }
            
        except Exception as e:
            logger.error(f"Error en interpretación completa: {e}")
            return {
                "interpretations": {},
                "overall_score": 0,
                "overall_recommendation": "Error en interpretación. Revisar datos.",
                "strategy_name": strategy_data.get("Strategy_Name", "Desconocida")
            }
    
    def _calculate_overall_score(self, interpretations: Dict[str, Any]) -> float:
        """Calcula un score general basado en todas las interpretaciones."""
        try:
            if not interpretations:
                return 0.0
            
            # Pesos para cada métrica
            weights = {
                "factor_k": 0.35,
                "predictability": 0.25,
                "sharpe": 0.20,
                "drawdown": 0.15,
                "cagr": 0.05
            }
            
            total_score = 0.0
            total_weight = 0.0
            
            for metric, interpretation in interpretations.items():
                if metric in weights:
                    # Convertir categoría a score (0-100)
                    category_score = self._category_to_score(interpretation["category"])
                    total_score += category_score * weights[metric]
                    total_weight += weights[metric]
            
            return total_score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculando score general: {e}")
            return 0.0
    
    def _category_to_score(self, category: str) -> float:
        """Convierte una categoría a un score numérico."""
        score_mapping = {
            "excellent": 95.0,
            "very_good": 85.0,
            "good": 75.0,
            "acceptable": 60.0,
            "poor": 40.0,
            "very_poor": 20.0,
            "high": 30.0,
            "moderate": 50.0,
            "low": 70.0
        }
        
        return score_mapping.get(category, 50.0)
    
    def _generate_overall_recommendation(self, interpretations: Dict[str, Any]) -> str:
        """Genera una recomendación general basada en todas las interpretaciones."""
        try:
            if not interpretations:
                return "No hay datos suficientes para generar recomendación."
            
            # Contar categorías excelentes y buenas
            excellent_count = 0
            good_count = 0
            poor_count = 0
            
            for interpretation in interpretations.values():
                category = interpretation.get("category", "")
                if category in ["excellent", "very_good"]:
                    excellent_count += 1
                elif category in ["good", "acceptable"]:
                    good_count += 1
                elif category in ["poor", "very_poor", "high"]:
                    poor_count += 1
            
            # Generar recomendación basada en la mayoría
            if excellent_count >= 3:
                return "🏆 ESTRATEGIA EXCEPCIONAL: Múltiples métricas excelentes. Altamente recomendada."
            elif excellent_count >= 2 and good_count >= 1:
                return "🥈 ESTRATEGIA MUY BUENA: Mayoría de métricas excelentes o buenas. Recomendada."
            elif excellent_count >= 1 and good_count >= 2:
                return "🥉 ESTRATEGIA BUENA: Buen balance de métricas. Considerar para portafolio."
            elif good_count >= 2:
                return "⭐ ESTRATEGIA ACEPTABLE: Métricas moderadas. Revisar otros factores."
            elif poor_count >= 2:
                return "⚠️ ESTRATEGIA CON RIESGO: Múltiples métricas pobres. No recomendada."
            else:
                return "❓ ESTRATEGIA MIXTA: Métricas variadas. Análisis adicional requerido."
                
        except Exception as e:
            logger.error(f"Error generando recomendación general: {e}")
            return "Error generando recomendación general."

def create_interpretation_guides() -> InterpretationGuides:
    """Crea una instancia de las guías de interpretación."""
    return InterpretationGuides() 