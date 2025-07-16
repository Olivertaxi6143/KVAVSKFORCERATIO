from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class KPIConfig:
    """Configuración de un KPI específico con validación."""
    name: str
    enabled: bool
    weight: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""
    
    def validate(self) -> bool:
        """Valida la configuración del KPI."""
        if not self.name or self.name.strip() == "":
            return False
        if self.weight < 0:
            return False
        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                return False
        return True

@dataclass
class TradingStyleConfig:
    """Configuración para un estilo de trading específico."""
    name: str
    description: str
    kpi_weights: Dict[str, float]
    component_weights: Dict[str, float]
    priority_kpis: List[str]
    
    def validate(self) -> bool:
        """Valida la configuración del estilo de trading."""
        if not self.name or self.name.strip() == "":
            return False
        if not self.kpi_weights:
            return False
        if not self.component_weights:
            return False
        # Validar que los pesos sumen aproximadamente 1
        total_weight = sum(self.component_weights.values())
        if abs(total_weight - 1.0) > 0.1:
            return False
        return True 