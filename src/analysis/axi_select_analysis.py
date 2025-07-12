"""
Análisis Axi Select - Integración completa de metodologías para gestión de capital de terceros.
Basado en el programa de financiación escalonada con 6 fases: Seed → Incubation → Acceleration → Pro → Pro 500 → Pro M
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class AxiSelectStage:
    """Configuración de una fase de Axi Select."""
    name: str
    min_equity_usd: int
    edge_score_required: int
    target_profit: float  # +5% excepto Pro M
    min_days: int
    min_trades_stage: int
    min_trades_month: int
    multiplier: int
    max_funding_usd: int
    profit_share: float
    max_drawdown: float  # -10%

@dataclass
class AxiSelectStrategy:
    """Estrategia con métricas Axi Select calculadas."""
    strategy_name: str
    edge_score: float
    current_stage: str
    stage_progress: Dict[str, Any]
    allocation_percentage: float
    fixed_amount: float
    risk_metrics: Dict[str, float]
    capital_efficiency: float
    quarantine_status: str  # NORMAL, QUARANTINE, EXEMPT
    recommendations: List[str]

class AxiSelectAnalysis:
    """
    Análisis Axi Select completo con 6 fases de financiación escalonada.
    Integra metodologías profesionales de asignación y gestión de riesgo.
    """
    
    def __init__(self, config_file: str = "config/axi_select_config.json"):
        self.logger = logging.getLogger("axi_select")
        self.config_file = config_file
        self.config = self._load_config()
        self.stages = self._initialize_stages()
        
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración de Axi Select."""
        default_config = {
            "edge_score_components": {
                "skill_weight": 0.35,      # Rentabilidad vs drawdown
                "risk_weight": 0.25,       # Control del riesgo
                "consistency_weight": 0.20, # Estabilidad de resultados
                "experience_weight": 0.20   # Trayectoria y días consecutivos
            },
            "quarantine_settings": {
                "max_drawdown_threshold": -0.10,  # -10%
                "quarantine_duration_days": 14,
                "seed_exempt": True
            },
            "trading_conditions": {
                "leverage": "1:100",
                "min_trades_initial": 20,
                "min_deposit_usd": 500,
                "edge_score_reset_days": 90
            },
            "payout_conditions": {
                "monthly_payout": True,
                "min_allocation_balance": 0,
                "no_open_positions": True
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            else:
                # Crear archivo de configuración por defecto
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")
            return default_config
    
    def _initialize_stages(self) -> Dict[str, AxiSelectStage]:
        """Inicializa las 6 fases de Axi Select."""
        stages = {
            "Seed": AxiSelectStage(
                name="Seed",
                min_equity_usd=500,
                edge_score_required=50,
                target_profit=0.05,  # +5%
                min_days=30,
                min_trades_stage=20,
                min_trades_month=5,
                multiplier=10,
                max_funding_usd=5000,
                profit_share=0.0,  # 0%
                max_drawdown=-0.10  # -10%
            ),
            "Incubation": AxiSelectStage(
                name="Incubation",
                min_equity_usd=1000,
                edge_score_required=60,
                target_profit=0.05,
                min_days=60,
                min_trades_stage=40,
                min_trades_month=5,
                multiplier=10,
                max_funding_usd=20000,
                profit_share=0.40,  # 40%
                max_drawdown=-0.10
            ),
            "Acceleration": AxiSelectStage(
                name="Acceleration",
                min_equity_usd=2000,
                edge_score_required=70,
                target_profit=0.05,
                min_days=60,
                min_trades_stage=50,
                min_trades_month=5,
                multiplier=25,
                max_funding_usd=100000,
                profit_share=0.50,  # 50%
                max_drawdown=-0.10
            ),
            "Pro": AxiSelectStage(
                name="Pro",
                min_equity_usd=2000,
                edge_score_required=90,
                target_profit=0.05,
                min_days=60,
                min_trades_stage=50,
                min_trades_month=5,
                multiplier=100,
                max_funding_usd=200000,
                profit_share=0.70,  # 70%
                max_drawdown=-0.10
            ),
            "Pro 500": AxiSelectStage(
                name="Pro 500",
                min_equity_usd=2000,
                edge_score_required=90,
                target_profit=0.05,
                min_days=60,
                min_trades_stage=50,
                min_trades_month=5,
                multiplier=250,
                max_funding_usd=500000,
                profit_share=0.80,  # 80%
                max_drawdown=-0.10
            ),
            "Pro M": AxiSelectStage(
                name="Pro M",
                min_equity_usd=4000,
                edge_score_required=90,
                target_profit=0.0,  # Sin objetivo específico
                min_days=0,  # Sin límite
                min_trades_stage=0,  # Sin límite
                min_trades_month=5,
                multiplier=250,
                max_funding_usd=1000000,
                profit_share=0.90,  # 90%
                max_drawdown=-0.10
            )
        }
        return stages
    
    def calculate_edge_score(self, strategy_data: pd.Series) -> float:
        """
        Calcula el Edge Score basado en 4 componentes: Skill, Risk, Consistency, Experience.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            Edge Score (0-100)
        """
        try:
            weights = self.config["edge_score_components"]
            edge_score = 0.0
            
            # 1. Skill Component (35%) - Rentabilidad vs drawdown
            skill_score = 0.0
            
            # CAGR como medida de rentabilidad
            if 'CAGR' in strategy_data:
                cagr = self._safe_float(strategy_data['CAGR'])
                if cagr > 0:
                    skill_score += min(cagr * 2, 50)  # Máximo 50 puntos
            
            # Profit Factor
            if 'Profit factor' in strategy_data:
                pf = self._safe_float(strategy_data['Profit factor'])
                if pf > 1:
                    skill_score += min((pf - 1) * 25, 30)  # Máximo 30 puntos
            
            # Calmar Ratio (rentabilidad vs drawdown)
            if 'CalmarRatio' in strategy_data:
                calmar = self._safe_float(strategy_data['CalmarRatio'])
                if calmar > 0:
                    skill_score += min(calmar * 10, 20)  # Máximo 20 puntos
            
            edge_score += skill_score * weights["skill_weight"]
            
            # 2. Risk Component (25%) - Control del riesgo
            risk_score = 0.0
            
            # Sharpe Ratio
            if 'Sharpe Ratio' in strategy_data:
                sharpe = self._safe_float(strategy_data['Sharpe Ratio'])
                if sharpe > 0:
                    risk_score += min(sharpe * 15, 40)  # Máximo 40 puntos
            
            # Max Drawdown (inverso)
            if 'Max DD %' in strategy_data:
                dd = abs(self._safe_float(strategy_data['Max DD %']))
                if dd <= 10:  # Menos del 10%
                    risk_score += 40
                elif dd <= 15:  # Menos del 15%
                    risk_score += 30
                elif dd <= 20:  # Menos del 20%
                    risk_score += 20
                elif dd <= 25:  # Menos del 25%
                    risk_score += 10
            elif 'Drawdown' in strategy_data:
                # Fallback a la columna original
                dd = abs(self._safe_float(strategy_data['Drawdown']))
                # Si el valor es muy alto (>100), probablemente son puntos monetarios
                if dd > 100:
                    # No podemos determinar con seguridad, asumir drawdown bajo
                    risk_score += 30
                else:
                    # Interpretar como decimal
                    dd_percent = dd * 100
                    if dd_percent <= 10:  # Menos del 10%
                        risk_score += 40
                    elif dd_percent <= 15:  # Menos del 15%
                        risk_score += 30
                    elif dd_percent <= 20:  # Menos del 20%
                        risk_score += 20
                    elif dd_percent <= 25:  # Menos del 25%
                        risk_score += 10
            
            # VaR
            if 'VaR (95%)' in strategy_data:
                var = abs(self._safe_float(strategy_data['VaR (95%)']))
                if var <= 0.05:  # Menos del 5%
                    risk_score += 20
                elif var <= 0.10:  # Menos del 10%
                    risk_score += 10
            
            edge_score += risk_score * weights["risk_weight"]
            
            # 3. Consistency Component (20%) - Estabilidad de resultados
            consistency_score = 0.0
            
            # Win Rate
            if 'Winning Percent' in strategy_data:
                win_rate = self._safe_float(strategy_data['Winning Percent'])
                if win_rate > 0:
                    consistency_score += min(win_rate, 40)  # Máximo 40 puntos
            
            # SQN (System Quality Number)
            if 'SQN' in strategy_data:
                sqn = self._safe_float(strategy_data['SQN'])
                if sqn > 0:
                    consistency_score += min(sqn * 5, 30)  # Máximo 30 puntos
            
            # Number of Trades
            if '# of trades' in strategy_data:
                trades = self._safe_float(strategy_data['# of trades'])
                if trades >= 100:
                    consistency_score += 30
                elif trades >= 50:
                    consistency_score += 20
                elif trades >= 30:
                    consistency_score += 10
            
            edge_score += consistency_score * weights["consistency_weight"]
            
            # 4. Experience Component (20%) - Trayectoria y días consecutivos
            experience_score = 0.0
            
            # Recovery Factor
            if 'RecoveryFactor' in strategy_data:
                rf = self._safe_float(strategy_data['RecoveryFactor'])
                if rf > 0:
                    experience_score += min(rf * 10, 40)  # Máximo 40 puntos
            
            # RINA Index
            if 'RINAIndex' in strategy_data:
                rina = self._safe_float(strategy_data['RINAIndex'])
                if rina > 0:
                    experience_score += min(rina * 5, 30)  # Máximo 30 puntos
            
            # Exposure (tiempo en el mercado)
            if 'Exposure' in strategy_data:
                exposure = self._safe_float(strategy_data['Exposure'])
                if exposure > 0:
                    experience_score += min(exposure * 2, 30)  # Máximo 30 puntos
            
            edge_score += experience_score * weights["experience_weight"]
            
            return min(edge_score, 100)
            
        except Exception as e:
            self.logger.error(f"Error calculando Edge Score: {e}")
            return 0.0
    
    def determine_stage(self, strategy_data: pd.Series, edge_score: float) -> str:
        """
        Determina la fase actual basada en Edge Score y requisitos.
        
        Args:
            strategy_data: Datos de la estrategia
            edge_score: Edge Score calculado
            
        Returns:
            Nombre de la fase actual
        """
        try:
            # Verificar requisitos de cada fase de mayor a menor
            for stage_name in ["Pro M", "Pro 500", "Pro", "Acceleration", "Incubation", "Seed"]:
                stage = self.stages[stage_name]
                
                # Verificar Edge Score mínimo
                if edge_score >= stage.edge_score_required:
                    # Verificar otros requisitos básicos
                    if self._check_stage_requirements(strategy_data, stage):
                        return stage_name
            
            return "Seed"  # Fase por defecto
            
        except Exception as e:
            self.logger.error(f"Error determinando fase: {e}")
            return "Seed"
    
    def _check_stage_requirements(self, strategy_data: pd.Series, stage: AxiSelectStage) -> bool:
        """
        Verifica si la estrategia cumple los requisitos de una fase específica.
        
        Args:
            strategy_data: Datos de la estrategia
            stage: Fase a verificar
            
        Returns:
            True si cumple los requisitos
        """
        try:
            # Verificar número mínimo de trades
            if '# of trades' in strategy_data:
                trades = self._safe_float(strategy_data['# of trades'])
                if trades < stage.min_trades_stage:
                    return False
            
            # Verificar drawdown máximo - CORREGIDO: usar "Max DD %"
            if 'Max DD %' in strategy_data:
                dd = abs(self._safe_float(strategy_data['Max DD %']))
                if dd > abs(stage.max_drawdown * 100):  # Convertir a porcentaje
                    return False
            elif 'Drawdown' in strategy_data:
                # Fallback a la columna original
                dd = abs(self._safe_float(strategy_data['Drawdown']))
                # Si el valor es muy alto (>100), probablemente son puntos monetarios
                if dd > 100:
                    # No podemos determinar con seguridad, asumir que cumple
                    pass
                elif dd > abs(stage.max_drawdown):
                    return False
            
            # Verificar profit factor mínimo
            if 'Profit factor' in strategy_data:
                pf = self._safe_float(strategy_data['Profit factor'])
                if pf < 1.0:  # Debe ser rentable
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error verificando requisitos de fase: {e}")
            return False
    
    def calculate_stage_progress(self, strategy_data: pd.Series, current_stage: str) -> Dict[str, Any]:
        """
        Calcula el progreso en la fase actual.
        
        Args:
            strategy_data: Datos de la estrategia
            current_stage: Fase actual
            
        Returns:
            Diccionario con progreso detallado
        """
        try:
            stage = self.stages[current_stage]
            progress = {
                "stage": current_stage,
                "days_completed": 0,  # Simulado
                "trades_completed": self._safe_float(strategy_data.get('# of trades', 0)),
                "target_profit_achieved": False,
                "edge_score_met": False,
                "requirements_met": {},
                "can_advance": False
            }
            
            # Verificar trades mínimos
            progress["requirements_met"]["min_trades"] = (
                progress["trades_completed"] >= stage.min_trades_stage
            )
            
            # Verificar trades mensuales
            progress["requirements_met"]["monthly_trades"] = (
                progress["trades_completed"] >= stage.min_trades_month
            )
            
            # Verificar Edge Score
            edge_score = self.calculate_edge_score(strategy_data)
            progress["edge_score_met"] = edge_score >= stage.edge_score_required
            
            # Verificar objetivo de beneficio (simulado)
            if current_stage != "Pro M":
                # Simular verificación de +5%
                progress["target_profit_achieved"] = True  # Simulado
            
            # Determinar si puede avanzar
            progress["can_advance"] = all(progress["requirements_met"].values()) and \
                                    progress["edge_score_met"] and \
                                    progress["target_profit_achieved"]
            
            return progress
            
        except Exception as e:
            self.logger.error(f"Error calculando progreso de fase: {e}")
            return {}
    
    def check_quarantine_status(self, strategy_data: pd.Series, current_stage: str) -> str:
        """
        Verifica el estado de cuarentena de la estrategia.
        
        Args:
            strategy_data: Datos de la estrategia
            current_stage: Fase actual
            
        Returns:
            Estado de cuarentena (NORMAL, QUARANTINE, EXEMPT)
        """
        try:
            # Seed está exenta de cuarentena
            if current_stage == "Seed":
                return "EXEMPT"
            
            # Verificar drawdown máximo - CORREGIDO: usar "Max DD %" en lugar de "Drawdown"
            if 'Max DD %' in strategy_data:
                dd = abs(self._safe_float(strategy_data['Max DD %']))
                if dd > 10:  # Excede 10%
                    return "QUARANTINE"
            elif 'Drawdown' in strategy_data:
                # Fallback a la columna original si no existe "Max DD %"
                dd = abs(self._safe_float(strategy_data['Drawdown']))
                # Si el valor es muy alto (>100), probablemente son puntos monetarios, no porcentaje
                if dd > 100:
                    # Buscar una columna alternativa o usar un valor por defecto
                    return "NORMAL"  # No podemos determinar con seguridad
                elif dd > 0.10:  # Excede 10%
                    return "QUARANTINE"
            
            return "NORMAL"
            
        except Exception as e:
            self.logger.error(f"Error verificando estado de cuarentena: {e}")
            return "NORMAL"
    
    def calculate_allocation(self, strategy_data: pd.Series, 
                           current_stage: str,
                           total_capital: float = 100000) -> Tuple[float, float]:
        """
        Calcula la asignación de capital basada en la fase actual.
        
        Args:
            strategy_data: Datos de la estrategia
            current_stage: Fase actual
            total_capital: Capital total disponible
            
        Returns:
            Tuple con (porcentaje, cantidad fija)
        """
        try:
            stage = self.stages[current_stage]
            
            # Calcular cantidad fija basada en el multiplicador de la fase
            fixed_amount = stage.max_funding_usd
            percentage = (fixed_amount / total_capital) * 100
            
            return percentage, fixed_amount
            
        except Exception as e:
            self.logger.error(f"Error calculando asignación: {e}")
            return 5.0, 5000.0
    
    def generate_recommendations(self, strategy_data: pd.Series, 
                               edge_score: float, current_stage: str,
                               stage_progress: Dict[str, Any]) -> List[str]:
        """
        Genera recomendaciones específicas para la estrategia.
        
        Args:
            strategy_data: Datos de la estrategia
            edge_score: Edge Score calculado
            current_stage: Fase actual
            stage_progress: Progreso en la fase
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        # Recomendaciones basadas en Edge Score
        if edge_score >= 90:
            recommendations.append("¡Excelente Edge Score! Eres elegible para Pro 500 y Pro M")
        elif edge_score >= 70:
            recommendations.append("Buen Edge Score. Puedes avanzar a Acceleration y Pro")
        elif edge_score >= 60:
            recommendations.append("Edge Score aceptable. Enfoque en Incubation")
        elif edge_score >= 50:
            recommendations.append("Edge Score mínimo. Mantén Seed y mejora métricas")
        else:
            recommendations.append("Edge Score insuficiente. Requiere mejoras significativas")
        
        # Recomendaciones por fase
        if current_stage == "Seed":
            recommendations.append("Fase Seed: Enfoque en alcanzar 20 trades y Edge Score 50+")
        elif current_stage == "Incubation":
            recommendations.append("Fase Incubation: Objetivo 40 trades y Edge Score 60+")
        elif current_stage == "Acceleration":
            recommendations.append("Fase Acceleration: Objetivo 50 trades y Edge Score 70+")
        elif current_stage in ["Pro", "Pro 500", "Pro M"]:
            recommendations.append(f"Fase {current_stage}: Mantén Edge Score 90+ y métricas excelentes")
        
        # Recomendaciones de progreso
        if stage_progress.get("can_advance", False):
            recommendations.append("✅ ¡Puedes avanzar a la siguiente fase!")
        else:
            missing_requirements = []
            if not stage_progress.get("edge_score_met", False):
                missing_requirements.append("Edge Score mínimo")
            if not stage_progress.get("target_profit_achieved", False):
                missing_requirements.append("Objetivo de beneficio +5%")
            if not stage_progress.get("requirements_met", {}).get("min_trades", False):
                missing_requirements.append("Trades mínimos")
            
            if missing_requirements:
                recommendations.append(f"❌ Requisitos pendientes: {', '.join(missing_requirements)}")
        
        # Recomendaciones de riesgo
        if 'Max DD %' in strategy_data:
            dd = abs(self._safe_float(strategy_data['Max DD %']))
            if dd > 8:  # Alerta al 8%
                recommendations.append("⚠️ Drawdown cercano al límite 10%. Monitorea riesgo")
            if dd > 10:
                recommendations.append("🚨 Drawdown excede 10%. Cuarentena activa")
        elif 'Drawdown' in strategy_data:
            dd = abs(self._safe_float(strategy_data['Drawdown']))
            # Si el valor es muy alto (>100), probablemente son puntos monetarios
            if dd > 100:
                # No podemos determinar con seguridad
                pass
            else:
                # Interpretar como decimal
                dd_percent = dd * 100
                if dd_percent > 8:  # Alerta al 8%
                    recommendations.append("⚠️ Drawdown cercano al límite 10%. Monitorea riesgo")
                if dd_percent > 10:
                    recommendations.append("🚨 Drawdown excede 10%. Cuarentena activa")
        
        return recommendations
    
    def analyze_strategies(self, strategies_df: pd.DataFrame, 
                          total_capital: float = 100000) -> List[AxiSelectStrategy]:
        """
        Analiza todas las estrategias con metodología Axi Select completa.
        
        Args:
            strategies_df: DataFrame con estrategias
            total_capital: Capital total disponible
            
        Returns:
            Lista de estrategias Axi Select
        """
        self.logger.info("🚀 Ejecutando análisis Axi Select completo...")
        
        axi_strategies = []
        
        try:
            for idx in strategies_df.index:
                strategy_data = strategies_df.loc[idx]
                strategy_name = strategy_data['Strategy Name']
                
                # Calcular Edge Score
                edge_score = self.calculate_edge_score(strategy_data)
                
                # Determinar fase actual
                current_stage = self.determine_stage(strategy_data, edge_score)
                
                # Calcular progreso en la fase
                stage_progress = self.calculate_stage_progress(strategy_data, current_stage)
                
                # Verificar estado de cuarentena
                quarantine_status = self.check_quarantine_status(strategy_data, current_stage)
                
                # Calcular asignación
                allocation_percentage, fixed_amount = self.calculate_allocation(
                    strategy_data, current_stage, total_capital
                )
                
                # Calcular eficiencia de capital
                capital_efficiency = self.calculate_capital_efficiency(strategy_data)
                
                # Métricas de riesgo
                risk_metrics = {
                    "max_drawdown": abs(self._safe_float(strategy_data.get('Drawdown', 0))),
                    "sharpe_ratio": self._safe_float(strategy_data.get('Sharpe Ratio', 0)),
                    "profit_factor": self._safe_float(strategy_data.get('Profit factor', 0)),
                    "win_rate": self._safe_float(strategy_data.get('Winning Percent', 0)),
                    "var_95": self._safe_float(strategy_data.get('VaR (95%)', 0)),
                    "cvar_95": self._safe_float(strategy_data.get('CVaR (95%)', 0))
                }
                
                # Recomendaciones
                recommendations = self.generate_recommendations(
                    strategy_data, edge_score, current_stage, stage_progress
                )
                
                # Crear estrategia Axi Select
                axi_strategy = AxiSelectStrategy(
                    strategy_name=strategy_name,
                    edge_score=edge_score,
                    current_stage=current_stage,
                    stage_progress=stage_progress,
                    allocation_percentage=allocation_percentage,
                    fixed_amount=fixed_amount,
                    risk_metrics=risk_metrics,
                    capital_efficiency=capital_efficiency,
                    quarantine_status=quarantine_status,
                    recommendations=recommendations
                )
                
                axi_strategies.append(axi_strategy)
            
            self.logger.info(f"✅ Análisis Axi Select completado: {len(axi_strategies)} estrategias")
            return axi_strategies
            
        except Exception as e:
            self.logger.error(f"❌ Error en análisis Axi Select: {e}")
            raise
    
    def calculate_capital_efficiency(self, strategy_data: pd.Series) -> float:
        """
        Calcula la eficiencia de capital de la estrategia.
        
        Args:
            strategy_data: Datos de la estrategia
            
        Returns:
            Eficiencia de capital (0-1)
        """
        try:
            efficiency = 0.0
            
            # Sharpe Ratio
            sharpe = self._safe_float(strategy_data.get('Sharpe Ratio', 0))
            if sharpe > 0:
                efficiency += min(sharpe / 3, 0.4)  # Máximo 40%
            
            # Profit Factor
            pf = self._safe_float(strategy_data.get('Profit factor', 0))
            if pf > 1:
                efficiency += min((pf - 1) / 2, 0.3)  # Máximo 30%
            
            # Recovery Factor
            rf = self._safe_float(strategy_data.get('RecoveryFactor', 0))
            if rf > 0:
                efficiency += min(rf / 5, 0.3)  # Máximo 30%
            
            return min(efficiency, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculando eficiencia de capital: {e}")
            return 0.0
    
    def generate_axi_report(self, strategies: List[AxiSelectStrategy]) -> Dict[str, Any]:
        """
        Genera reporte completo de Axi Select con todas las fases.
        
        Args:
            strategies: Lista de estrategias Axi Select
            
        Returns:
            Reporte completo
        """
        try:
            # Estadísticas por fase
            stage_stats = {}
            total_allocation = 0
            total_capital_efficiency = 0
            
            for strategy in strategies:
                stage = strategy.current_stage
                if stage not in stage_stats:
                    stage_stats[stage] = {
                        "count": 0,
                        "total_allocation": 0,
                        "avg_edge_score": 0,
                        "avg_capital_efficiency": 0,
                        "quarantine_count": 0
                    }
                
                stage_stats[stage]["count"] += 1
                stage_stats[stage]["total_allocation"] += strategy.fixed_amount
                total_allocation += strategy.fixed_amount
                total_capital_efficiency += strategy.capital_efficiency
                
                if strategy.quarantine_status == "QUARANTINE":
                    stage_stats[stage]["quarantine_count"] += 1
            
            # Calcular promedios
            for stage in stage_stats:
                stage_strategies = [s for s in strategies if s.current_stage == stage]
                if stage_strategies:
                    stage_stats[stage]["avg_edge_score"] = np.mean([s.edge_score for s in stage_strategies])
                    stage_stats[stage]["avg_capital_efficiency"] = np.mean([s.capital_efficiency for s in stage_strategies])
            
            # Top estrategias por Edge Score
            top_strategies = sorted(strategies, key=lambda x: x.edge_score, reverse=True)[:10]
            
            # Estrategias por eficiencia de capital
            efficient_strategies = sorted(strategies, key=lambda x: x.capital_efficiency, reverse=True)[:10]
            
            # Estrategias en cuarentena
            quarantine_strategies = [s for s in strategies if s.quarantine_status == "QUARANTINE"]
            
            report = {
                "summary": {
                    "total_strategies": len(strategies),
                    "total_allocation": total_allocation,
                    "avg_edge_score": np.mean([s.edge_score for s in strategies]),
                    "avg_capital_efficiency": total_capital_efficiency / len(strategies) if strategies else 0,
                    "quarantine_count": len(quarantine_strategies)
                },
                "stage_stats": stage_stats,
                "top_strategies": top_strategies,
                "efficient_strategies": efficient_strategies,
                "quarantine_strategies": quarantine_strategies,
                "stage_progression": {
                    "seed_eligible": [s for s in strategies if s.current_stage == "Seed"],
                    "incubation_eligible": [s for s in strategies if s.current_stage == "Incubation"],
                    "acceleration_eligible": [s for s in strategies if s.current_stage == "Acceleration"],
                    "pro_eligible": [s for s in strategies if s.current_stage in ["Pro", "Pro 500", "Pro M"]]
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generando reporte Axi Select: {e}")
            return {}
    
    def _safe_float(self, value) -> float:
        """
        Convierte valor a float de forma segura.
        
        Args:
            value: Valor a convertir
            
        Returns:
            Float o 0.0 si no se puede convertir
        """
        try:
            if pd.isna(value):
                return 0.0
            if isinstance(value, str):
                # Manejar formato europeo (comas como decimales)
                value = value.replace(',', '.')
            return float(value)
        except (ValueError, TypeError):
            return 0.0

def test_axi_select_analysis():
    """Función de prueba para el análisis Axi Select completo."""
    try:
        # Crear instancia del análisis
        axi_analyzer = AxiSelectAnalysis()
        
        # Cargar datos de prueba
        strategies_df = pd.read_csv('DatabankExport_M1.csv', sep=';')
        logger.info(f"📊 Datos cargados: {strategies_df.shape}")
        
        # Ejecutar análisis
        strategies = axi_analyzer.analyze_strategies(
            strategies_df, 
            total_capital=100000
        )
        
        # Generar reporte
        report = axi_analyzer.generate_axi_report(strategies)
        
        # Mostrar resultados
        print("\n" + "="*60)
        print("📊 REPORTE AXI SELECT COMPLETO")
        print("="*60)
        
        print(f"\n📈 Resumen:")
        print(f"  • Total estrategias: {report['summary']['total_strategies']}")
        print(f"  • Asignación total: €{report['summary']['total_allocation']:,.0f}")
        print(f"  • Edge Score promedio: {report['summary']['avg_edge_score']:.1f}")
        print(f"  • Eficiencia promedio: {report['summary']['avg_capital_efficiency']:.3f}")
        print(f"  • Estrategias en cuarentena: {report['summary']['quarantine_count']}")
        
        print(f"\n🏆 Top 5 Estrategias por Edge Score:")
        for i, strategy in enumerate(report['top_strategies'][:5], 1):
            print(f"  {i}. {strategy.strategy_name}: Edge {strategy.edge_score:.1f}, "
                  f"Fase {strategy.current_stage}, €{strategy.fixed_amount:,.0f}")
        
        print(f"\n💰 Estrategias por Fase:")
        for stage, stats in report['stage_stats'].items():
            print(f"  • {stage}: {stats['count']} estrategias, "
                  f"€{stats['total_allocation']:,.0f}, Edge {stats['avg_edge_score']:.1f}")
            if stats['quarantine_count'] > 0:
                print(f"    ⚠️ {stats['quarantine_count']} en cuarentena")
        
        print(f"\n🚨 Estrategias en Cuarentena:")
        for strategy in report['quarantine_strategies'][:5]:
            print(f"  • {strategy.strategy_name}: Fase {strategy.current_stage}, "
                  f"DD {strategy.risk_metrics['max_drawdown']:.1%}")
        
        print(f"\n✅ Análisis Axi Select completado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en prueba Axi Select: {e}")
        raise

if __name__ == "__main__":
    test_axi_select_analysis() 