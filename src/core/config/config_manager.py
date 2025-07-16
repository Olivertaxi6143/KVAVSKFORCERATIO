import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.core.config.kpi_config import KPIConfig, TradingStyleConfig
from src.core.config.progress_callback import ProgressCallback
from src.logger_config import setup_logger
import numpy as np
import pandas as pd
from typing import Optional, Any, Union
import warnings

class ConfigManagerEnhanced:
    """
    Gestor de configuración mejorado con validación robusta y manejo de errores.
    """
    
    def __init__(self, config_file: str = "config/trading_config.json"):
        self.logger = setup_logger("kforce")
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configuración por defecto mejorada
        self.default_config = self._create_default_config()
        self.current_config = self.load_config()
        self.validation_errors = []
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Crea la configuración por defecto con todos los KPIs disponibles y estilos de trading con KPIs extra."""
        return {
            "trading_style": "Swing",
            "selected_kpis": {
                "Sharpe_Ratio": {"enabled": True, "weight": 1.0, "description": "Ratio de Sharpe"},
                "Profit factor": {"enabled": True, "weight": 1.0, "description": "Factor de Beneficio"},
                "Max_DD_%": {"enabled": True, "weight": 1.0, "description": "Máximo Drawdown"},
                "CAGR": {"enabled": True, "weight": 1.0, "description": "CAGR"},
                "RecoveryFactor": {"enabled": True, "weight": 1.0, "description": "Factor de Recuperación"},
                "VaR (95%)": {"enabled": True, "weight": 1.0, "description": "Value at Risk 95%"},
                "CVaR (95%)": {"enabled": True, "weight": 1.0, "description": "Conditional VaR 95%"},
                "Ulcer Index %": {"enabled": True, "weight": 1.0, "description": "Índice de Úlcera"},
                "CalmarRatio": {"enabled": True, "weight": 1.0, "description": "Ratio de Calmar"},
                "SQN": {"enabled": True, "weight": 1.0, "description": "SQN Score"},
                "RINAIndex": {"enabled": True, "weight": 1.0, "description": "RINA Index"},
                "Stagnation": {"enabled": True, "weight": 1.0, "description": "Estancamiento"},
                "Net profit": {"enabled": True, "weight": 1.0, "description": "Beneficio Neto"},
                "Winning Percent": {"enabled": True, "weight": 1.0, "description": "Porcentaje de Victorias"},
                "Avg. Bars in Trade": {"enabled": True, "weight": 1.0, "description": "Barras promedio en trade"},
                "Max Consec. Losses": {"enabled": True, "weight": 1.0, "description": "Máximas pérdidas consecutivas"},
                "Drawdown": {"enabled": True, "weight": 1.0, "description": "Drawdown"},
                "Max Drawdown Duration": {"enabled": True, "weight": 1.0, "description": "Duración máxima de drawdown"},
                "Exposure": {"enabled": True, "weight": 1.0, "description": "Exposición"},
                "Sortino Ratio": {"enabled": True, "weight": 1.0, "description": "Ratio de Sortino"},
                "Payout ratio": {"enabled": True, "weight": 1.0, "description": "Ratio de payout"},
                "Expectancy": {"enabled": True, "weight": 1.0, "description": "Expectativa"}
            },
            "component_weights": {
                "profitability": 0.4,
                "risk": 0.35,
                "consistency": 0.25
            },
            "trading_styles": {
                "Intradía": {
                    "description": "KPIs optimizados para trading de alta frecuencia",
                    "extra_kpis": ['Winning Percent', 'Avg. Bars in Trade', 'Exposure', 'SQN', 'Sortino Ratio', 'Max Consec. Losses', 'Drawdown', 'RecoveryFactor']
                },
                "Swing": {
                    "description": "KPIs para operaciones de medio plazo",
                    "extra_kpis": ['Profit factor', 'Max Drawdown Duration', 'RecoveryFactor', 'Exposure', 'VaR (95%)', 'CVaR (95%)', 'Ulcer Index %', 'CalmarRatio']
                },
                "Tendencial": {
                    "description": "KPIs para estrategias de seguimiento de tendencias",
                    "extra_kpis": ['Profit factor', 'Max Drawdown Duration', 'RecoveryFactor', 'CAGR', 'Sharpe Ratio', 'Profit factor', 'Sortino Ratio', 'Stagnation']
                },
                "Reversión a la media": {
                    "description": "KPIs para estrategias de reversión",
                    "extra_kpis": ['Expectancy', 'Avg. Bars in Trade', 'Winning Percent', 'Sortino Ratio', 'Max Drawdown Duration', 'Drawdown', 'Payout ratio', 'Ulcer Index %']
                },
                "Breakout": {
                    "description": "KPIs para estrategias de breakout",
                    "extra_kpis": ['Sortino Ratio', 'RecoveryFactor', 'Exposure', 'Stagnation', 'Stagnation', 'Drawdown', 'RINAIndex', 'VaR (95%)']
                }
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde archivo o usa la por defecto."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"Configuración cargada de {self.config_file}")
                return config
            except Exception as e:
                self.logger.error(f"Error cargando configuración: {e}")
        self.logger.warning("Usando configuración por defecto")
        return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Guarda la configuración en archivo."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuración guardada en {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Valida la configuración actual."""
        errors = []
        if "selected_kpis" not in config:
            errors.append("Falta 'selected_kpis' en la configuración")
        if "component_weights" not in config:
            errors.append("Falta 'component_weights' en la configuración")
        if "trading_styles" not in config:
            errors.append("Falta 'trading_styles' en la configuración")
        return len(errors) == 0, errors
    
    def get_enabled_kpis(self) -> List[str]:
        """
        Obtiene la lista de KPIs habilitados en la configuración actual.
        
        Returns:
            Lista de nombres de KPIs habilitados
        """
        try:
            enabled_kpis = []
            if 'selected_kpis' in self.current_config:
                for kpi_name, kpi_config in self.current_config['selected_kpis'].items():
                    if isinstance(kpi_config, dict) and kpi_config.get('enabled', False):
                        enabled_kpis.append(kpi_name)
                    elif isinstance(kpi_config, bool) and kpi_config:
                        enabled_kpis.append(kpi_name)
            
            # Si no hay KPIs habilitados, usar todos los disponibles
            if not enabled_kpis:
                enabled_kpis = list(self.current_config.get('selected_kpis', {}).keys())
            
            self.logger.info(f"📊 KPIs habilitados encontrados: {len(enabled_kpis)}")
            return enabled_kpis
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo KPIs habilitados: {e}")
            # Retornar KPIs por defecto si hay error
            return ["Sharpe_Ratio", "Profit_factor", "Max_DD_%", "CAGR"]
    
    def update_kpi_config(self, kpi_name: str, enabled: bool, weight: float = 1.0) -> bool:
        """
        Actualiza la configuración de un KPI específico.
        
        Args:
            kpi_name: Nombre del KPI
            enabled: Si está habilitado
            weight: Peso del KPI
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            if 'selected_kpis' not in self.current_config:
                self.current_config['selected_kpis'] = {}
            
            self.current_config['selected_kpis'][kpi_name] = {
                'enabled': enabled,
                'weight': weight,
                'description': f"KPI {kpi_name}"
            }
            
            self.logger.info(f"⚙️ KPI {kpi_name} actualizado: enabled={enabled}, weight={weight}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error actualizando KPI {kpi_name}: {e}")
            return False
    
    def get_trading_style_config(self, style_name: str) -> Dict[str, Any]:
        """
        Obtiene la configuración para un estilo de trading específico.
        
        Args:
            style_name: Nombre del estilo de trading
            
        Returns:
            Configuración del estilo de trading
        """
        try:
            trading_styles = self.current_config.get('trading_styles', {})
            if style_name in trading_styles:
                return trading_styles[style_name]
            else:
                # Retornar configuración por defecto
                return {
                    'description': f"Estilo {style_name}",
                    'kpi_weights': {},
                    'component_weights': {'profitability': 0.4, 'risk': 0.35, 'consistency': 0.25},
                    'priority_kpis': []
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo configuración de estilo {style_name}: {e}")
            return {} 

    def get_kpi_weights(self) -> dict:
        # Retorna los pesos de los KPIs actuales
        if 'selected_kpis' in self.current_config:
            return {k: v.get('weight', 1.0) if isinstance(v, dict) else 1.0 for k, v in self.current_config['selected_kpis'].items()}
        return {}

    def get_trading_style(self, style_name: Optional[str] = None) -> Any:
        # Si no se pasa argumento, retorna un string para compatibilidad con el test
        if style_name is None:
            style_name = "Swing"
        style = self.get_trading_style_config(style_name)
        if not style or not isinstance(style, dict):
            return {
                'description': f"Estilo {style_name}",
                'kpi_weights': {},
                'component_weights': {'profitability': 0.4, 'risk': 0.35, 'consistency': 0.25},
                'priority_kpis': []
            }
        return style

    def get_config(self) -> Dict[str, Any]:
        """Alias de load_config para compatibilidad con tests antiguos."""
        return self.load_config()
    
    def update_trading_style(self, trading_style: str) -> bool:
        """
        Actualiza el estilo de trading en la configuración actual.
        
        Args:
            trading_style: Nombre del estilo de trading
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            # Actualizar el estilo de trading en la configuración
            self.current_config['trading_style'] = trading_style
            
            # Guardar en archivo
            success = self.save_config(self.current_config)
            
            if success:
                self.logger.info(f"🎯 Estilo de trading actualizado: {trading_style}")
            else:
                self.logger.warning(f"Estilo de trading actualizado en memoria pero no se pudo guardar en archivo: {trading_style}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error actualizando estilo de trading {trading_style}: {e}")
            return False
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """
        Actualiza la configuración actual con nuevos valores.
        
        Args:
            config: Nueva configuración a aplicar
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            # Actualizar configuración actual
            self.current_config.update(config)
            
            # Guardar en archivo
            success = self.save_config(self.current_config)
            
            if success:
                self.logger.info("Configuración actualizada exitosamente")
            else:
                self.logger.warning("Configuración actualizada en memoria pero no se pudo guardar en archivo")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error actualizando configuración: {e}")
            return False

def test_get_trading_style():
    cm = ConfigManagerEnhanced()
    # Estilo existente
    style = cm.get_trading_style("Swing")
    assert isinstance(style, dict)
    assert "description" in style
    # Estilo inexistente
    style2 = cm.get_trading_style("NoExiste")
    assert isinstance(style2, dict)
    assert "component_weights" in style2
    print("✅ get_trading_style retorna estructura válida para cualquier estilo") 